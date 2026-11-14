"""Máy đo định lượng cho ảnh (`rea-anh`).

Cách gọi:
    python linhx-rea/scripts/anh_do.py <anh> -o <dir>

Sinh trong <dir>:
    - do.json     : 6 màu k-means, tông sáng, người/mặt (YuNet), điểm hút mắt, khớp bố cục, 3 lớp độ sâu (+phẳng), OCR.
    - do.png      : ảnh thu cạnh dài 1024, lưới 1/3, hộp mặt (nếu có), điểm hút mắt đánh số, dải 6 màu ở đáy.
    - hut_mat.png : bản đồ nhiệt (heatmap) hút mắt phủ lên ảnh kèm các đỉnh NMS.
    - depth.png   : bản đồ độ sâu chuẩn hoá 0..1 (Depth Anything V2 ra inverse depth: LỚN = GẦN / sáng).
    - lop.png     : bản phân 3 lớp độ sâu (gần = sáng nhất, xa = tối nhất, có chú giải nhỏ góc ảnh).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import onnxruntime as ort

PHIEN_BAN = "0.1.0"
GOC_REPO = Path(__file__).resolve().parents[2]
TEN_MODEL_YUNET = "face_detection_yunet_2023mar.onnx"

_ORT_SESS: ort.InferenceSession | None = None
_OCR_ENGINE: Any = False
_YUNET_CACHE: dict[str, Any] = {}


def _cau_hinh_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


# ---------------- Đọc / ghi ảnh an toàn Unicode trên Windows -----------------------------------------

def doc_anh_bgr(path: str | Path) -> np.ndarray:
    p = Path(path)
    raw = np.frombuffer(p.read_bytes(), dtype=np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Không đọc được ảnh: {p}")
    if img.dtype == np.uint16:
        img = (img.astype(np.float32) / np.float32(257.0)).round().clip(0, 255).astype(np.uint8)
    elif img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)

    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        alpha = img[:, :, 3:4].astype(np.float32) / np.float32(255.0)
        bgr = img[:, :, :3].astype(np.float32)
        img = (bgr * alpha + np.float32(255.0) * (np.float32(1.0) - alpha)).round().clip(0, 255).astype(np.uint8)
    elif img.shape[2] > 3:
        img = img[:, :, :3]
    return np.ascontiguousarray(img)


def ghi_anh(path: str | Path, img: np.ndarray) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    duoi = p.suffix.lower() or ".png"
    ok, buf = cv2.imencode(duoi, img)
    if not ok:
        raise RuntimeError(f"Không mã hoá được ảnh ra: {p}")
    p.write_bytes(buf.tobytes())


def thu_canh_dai(img: np.ndarray, canh_dai: int) -> np.ndarray:
    h, w = img.shape[:2]
    m = max(h, w)
    if m == canh_dai:
        return img
    ti_le = canh_dai / float(m)
    nw = max(1, int(round(w * ti_le)))
    nh = max(1, int(round(h * ti_le)))
    interp = cv2.INTER_AREA if ti_le < 1.0 else cv2.INTER_LINEAR
    return cv2.resize(img, (nw, nh), interpolation=interp)


def _chuan_hoa_01(arr: np.ndarray) -> np.ndarray:
    a_min, a_max = float(arr.min()), float(arr.max())
    if a_max - a_min <= 1e-8:
        return np.zeros_like(arr, dtype=np.float32)
    return ((arr - np.float32(a_min)) / np.float32(a_max - a_min)).astype(np.float32)


# ---------------- 1. Bảng 6 màu k-means --------------------------------------------------------------

def do_mau(img_bgr: np.ndarray, so_mau: int = 6) -> list[dict[str, Any]]:
    h, w = img_bgr.shape[:2]
    nho = thu_canh_dai(img_bgr, 256) if max(h, w) > 256 else img_bgr
    if nho.shape[0] * nho.shape[1] < so_mau:
        nho = cv2.resize(nho, (8, 8), interpolation=cv2.INTER_NEAREST)

    rgb = cv2.cvtColor(nho, cv2.COLOR_BGR2RGB)
    px_f32 = (rgb.reshape(-1, 1, 3).astype(np.float32) / np.float32(255.0)).astype(np.float32)
    lab = cv2.cvtColor(px_f32, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)

    cv2.setRNGSeed(0)
    tieu_chi = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    _, nhan, tam = cv2.kmeans(lab, so_mau, None, tieu_chi, 3, cv2.KMEANS_PP_CENTERS)

    tam = np.nan_to_num(tam, nan=0.0).astype(np.float32)
    dem = np.bincount(nhan.ravel(), minlength=so_mau)
    thu_tu = np.argsort(-dem)

    rgb_tam = (
        cv2.cvtColor(tam[thu_tu].reshape(-1, 1, 3), cv2.COLOR_LAB2RGB).reshape(-1, 3) * np.float32(255.0)
    ).round().clip(0, 255).astype(int)

    tong_px = float(dem.sum())
    ti_le = [round(float(dem[i] / tong_px), 4) for i in thu_tu]
    phan_bu = round(1.0 - sum(ti_le[1:]), 4)
    if len(ti_le) >= 2 and phan_bu >= ti_le[1]:
        ti_le[0] = phan_bu

    ket_qua = []
    for c, p in zip(rgb_tam, ti_le):
        ma_hex = f"#{int(c[0]):02x}{int(c[1]):02x}{int(c[2]):02x}"
        ket_qua.append({"hex": ma_hex, "ti_le": float(p)})
    return ket_qua


# ---------------- 2. Histogram độ sáng & kiểu tông ---------------------------------------------------

def do_tong(gray_u8: np.ndarray) -> dict[str, Any]:
    lum = gray_u8.astype(np.float32) / np.float32(255.0)
    dem, _ = np.histogram(gray_u8, bins=16, range=(0, 256))
    hist = [round(float(c / gray_u8.size), 4) for c in dem]

    tb = float(lum.mean())
    lech = float(lum.std())
    ti_le_toi = float((lum < 0.25).mean())
    ti_le_sang = float((lum > 0.75).mean())

    if (lech >= 0.28 and ti_le_toi >= 0.12 and ti_le_sang >= 0.12) or lech >= 0.34:
        kieu = "tuong-phan-cao"
    elif tb >= 0.62:
        kieu = "high-key"
    elif tb <= 0.38:
        kieu = "low-key"
    elif lech >= 0.26:
        kieu = "tuong-phan-cao"
    else:
        kieu = "trung-tinh"

    return {
        "histogram": hist,
        "trung_binh": round(tb, 4),
        "do_lech": round(lech, 4),
        "kieu": kieu,
    }


# ---------------- 3. Nhận diện mặt/người YuNet & trộn hút mắt -----------------------------------------

def tim_model_yunet() -> Path | None:
    """Tìm model YuNet theo đúng thứ tự: biến môi trường `REA_YUNET`, `<cwd>/models/`, `~/.cache/rea-video/models/`."""
    ung_vien: list[Path] = []
    env_val = os.environ.get("REA_YUNET", "").strip()
    if env_val:
        p_env = Path(env_val).expanduser()
        ung_vien.append((p_env / TEN_MODEL_YUNET) if p_env.is_dir() else p_env)

    p_cwd = Path.cwd() / "models" / TEN_MODEL_YUNET
    ung_vien.append(p_cwd)
    p_repo = GOC_REPO / "models" / TEN_MODEL_YUNET
    if p_repo != p_cwd:
        ung_vien.append(p_repo)
    ung_vien.append(Path.home() / ".cache" / "rea-video" / "models" / TEN_MODEL_YUNET)
    ung_vien.append(Path.home() / ".cache" / "linhx-rea" / "models" / TEN_MODEL_YUNET)

    for p in ung_vien:
        if p.is_file():
            return p
    return None


def _lay_bo_do_yunet() -> Any | None:
    if not hasattr(cv2, "FaceDetectorYN"):
        return None
    p_model = tim_model_yunet()
    if p_model is None:
        return None
    khoa = str(p_model.resolve())
    if khoa not in _YUNET_CACHE:
        try:
            _YUNET_CACHE[khoa] = cv2.FaceDetectorYN.create(str(p_model), "", (320, 320), 0.55, 0.3, 50)
        except Exception:
            _YUNET_CACHE[khoa] = None
    return _YUNET_CACHE[khoa]


def uoc_vung_than(hop_mat: list[float] | tuple[float, ...]) -> list[float]:
    """Ước vùng thân người từ hộp mặt `[x0, y0, x1, y1]`: rộng ≈ 3× mặt, cao ≈ 4× mặt xuống dưới, cắt trong [0, 1]."""
    x0, y0, x1, y1 = [float(v) for v in hop_mat[:4]]
    fw = max(1e-4, x1 - x0)
    fh = max(1e-4, y1 - y0)
    cx = 0.5 * (x0 + x1)

    tx0 = max(0.0, cx - 1.5 * fw)
    tx1 = min(1.0, cx + 1.5 * fw)
    ty0 = min(1.0, max(0.0, y1))
    ty1 = min(1.0, y1 + 4.0 * fh)
    if ty1 - ty0 < 1e-3:
        ty0 = max(0.0, 1.0 - min(0.15, fh))
        ty1 = 1.0
    return [round(tx0, 4), round(ty0, 4), round(tx1, 4), round(ty1, 4)]


def _iou_hop(a: list[float], b: list[float]) -> tuple[float, float]:
    ix0 = max(a[0], b[0])
    iy0 = max(a[1], b[1])
    ix1 = min(a[2], b[2])
    iy1 = min(a[3], b[3])
    iw = max(0.0, ix1 - ix0)
    ih = max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0, 0.0
    dt_a = max(1e-8, (a[2] - a[0]) * (a[3] - a[1]))
    dt_b = max(1e-8, (b[2] - b[0]) * (b[3] - b[1]))
    iou = inter / max(1e-8, dt_a + dt_b - inter)
    contain = inter / min(dt_a, dt_b)
    return iou, contain


def do_nguoi(img_bgr: np.ndarray) -> dict[str, Any]:
    """Phát hiện mặt bằng YuNet đa tỉ lệ và ước vùng thân tương ứng.
    Không có model -> `{"co_cong_cu": False}`.
    Có model -> `{"co_cong_cu": True, "mat": [...], "than": [...]}`.
    """
    det = _lay_bo_do_yunet()
    if det is None:
        return {"co_cong_cu": False}

    h, w = img_bgr.shape[:2]
    canh_max = max(h, w)
    cac_muc_thu: list[tuple[int, float]] = [(min(canh_max, 960), 0.58)]
    if canh_max > 520:
        cac_muc_thu.append((480, 0.58))
    if canh_max > 320:
        cac_muc_thu.append((256, 0.66))

    ung_vien_mat: list[dict[str, Any]] = []
    for canh_muc, nguong_diem in cac_muc_thu:
        anh_thu = thu_canh_dai(img_bgr, canh_muc) if canh_max != canh_muc else img_bgr
        sh, sw = anh_thu.shape[:2]
        if sw < 24 or sh < 24:
            continue
        det.setInputSize((sw, sh))
        _, raw_faces = det.detect(anh_thu)
        if raw_faces is None:
            continue

        for f in raw_faces:
            diem = float(f[14])
            if diem < nguong_diem:
                continue
            fx, fy, fw, fh = float(f[0]), float(f[1]), float(f[2]), float(f[3])
            x0 = float(np.clip(fx / sw, 0.0, 1.0))
            y0 = float(np.clip(fy / sh, 0.0, 1.0))
            x1 = float(np.clip((fx + fw) / sw, 0.0, 1.0))
            y1 = float(np.clip((fy + fh) / sh, 0.0, 1.0))
            dien_tich = (x1 - x0) * (y1 - y0)
            if x1 - x0 < 0.015 or y1 - y0 < 0.015 or dien_tich < 0.0008:
                continue

            # Thứ tự 5 landmark của OpenCV FaceDetectorYN:
            # 0: mắt phải nhân vật, 1: mắt trái nhân vật, 2: chóp mũi, 3: khoé miệng phải, 4: khoé miệng trái
            rx = float(np.clip(float(f[4]) / sw, 0.0, 1.0))
            ry = float(np.clip(float(f[5]) / sh, 0.0, 1.0))
            lx = float(np.clip(float(f[6]) / sw, 0.0, 1.0))
            ly = float(np.clip(float(f[7]) / sh, 0.0, 1.0))
            mr_x = float(np.clip(float(f[10]) / sw, 0.0, 1.0))
            mr_y = float(np.clip(float(f[11]) / sh, 0.0, 1.0))
            ml_x = float(np.clip(float(f[12]) / sw, 0.0, 1.0))
            ml_y = float(np.clip(float(f[13]) / sh, 0.0, 1.0))
            mx = 0.5 * (mr_x + ml_x)
            my = 0.5 * (mr_y + ml_y)

            ung_vien_mat.append({
                "hop": [round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)],
                "diem": round(diem, 4),
                "mat_trai": [round(lx, 4), round(ly, 4)],
                "mat_phai": [round(rx, 4), round(ry, 4)],
                "mieng": [round(mx, 4), round(my, 4)],
                "_dt": dien_tich,
            })

    # Gộp NMS xuyên tỉ lệ (ưu tiên điểm tin cậy cao hơn)
    ung_vien_mat.sort(key=lambda m: (-float(m["diem"]), -float(m["_dt"])))
    ds_mat: list[dict[str, Any]] = []
    for m in ung_vien_mat:
        trung = False
        for da_chon in ds_mat:
            iou, contain = _iou_hop(m["hop"], da_chon["hop"])
            if iou >= 0.35 or contain >= 0.65:
                trung = True
                break
        if not trung:
            ban_sach = {k: v for k, v in m.items() if k != "_dt"}
            ds_mat.append(ban_sach)

    # Sắp xếp mặt theo diện tích lớn -> nhỏ để thân tương ứng thứ tự mặt
    ds_mat.sort(key=lambda m: -((m["hop"][2] - m["hop"][0]) * (m["hop"][3] - m["hop"][1])))
    ds_than = [uoc_vung_than(m["hop"]) for m in ds_mat]
    return {
        "co_cong_cu": True,
        "mat": ds_mat,
        "than": ds_than,
    }


def tinh_saliency_r2(img_bgr: np.ndarray, le_mep: float = 0.04) -> np.ndarray:
    """Tính bản đồ saliency cơ sở R2 (SR Lab + Achanta 2009 + Bão hoà/Đỏ * Center Prior) ở kích thước gốc `(h, w)`."""
    h, w = img_bgr.shape[:2]
    nho_bgr = thu_canh_dai(img_bgr, 512) if max(h, w) > 512 else img_bgr
    hp, wp = nho_bgr.shape[:2]

    rgb_f32 = cv2.cvtColor(nho_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / np.float32(255.0)
    lab = cv2.cvtColor(rgb_f32, cv2.COLOR_RGB2LAB).astype(np.float32)

    # (a) Spectral Residual trên từng kênh L, a, b (đệm biên replicate để khử vệt nhảy biên FFT)
    sr_tong = np.zeros((hp, wp), dtype=np.float32)
    tong_w_sr = 0.0
    for idx_k in range(3):
        kenh = lab[:, :, idx_k]
        do_lech_k = float(kenh.std())
        trong_so_k = 1.0 if idx_k == 0 else min(1.0, do_lech_k / 2.0)
        if trong_so_k <= 0.02 or do_lech_k <= 1e-6:
            continue
        k64 = cv2.resize(kenh, (64, 64), interpolation=cv2.INTER_AREA).astype(np.float32)
        k_pad = cv2.copyMakeBorder(k64, 4, 4, 4, 4, cv2.BORDER_REPLICATE)
        fft = np.fft.fft2(k_pad)
        log_amp = np.log(np.abs(fft) + 1e-8).astype(np.float32)
        pha = np.angle(fft)
        residual = log_amp - cv2.blur(log_amp, (3, 3))
        sal_pad = (np.abs(np.fft.ifft2(np.exp(residual + 1j * pha))) ** 2).astype(np.float32)
        sal64 = cv2.GaussianBlur(sal_pad[4:-4, 4:-4], (9, 9), 2.5)
        sal_k = cv2.resize(sal64, (wp, hp), interpolation=cv2.INTER_LINEAR)
        sr_tong += np.float32(trong_so_k) * _chuan_hoa_01(sal_k)
        tong_w_sr += trong_so_k
    map_a = _chuan_hoa_01(sr_tong / np.float32(max(tong_w_sr, 1e-6)))

    # (b) Tương phản màu kiểu Achanta 2009: ưu tiên độ lệch màu (a*, b*) hơn bước nhảy trắng/đen thuần độ sáng (L*)
    lab_mo = cv2.GaussianBlur(lab, (5, 5), 0)
    lab_tb = lab.mean(axis=(0, 1), keepdims=True).astype(np.float32)
    hieu_lab = lab_mo - lab_tb
    achanta = np.sqrt(
        np.float32(0.35) * (hieu_lab[:, :, 0] ** 2)
        + (hieu_lab[:, :, 1] ** 2)
        + (hieu_lab[:, :, 2] ** 2)
    )
    map_b = _chuan_hoa_01(achanta)

    # (c) Độ bão hoà & độ đỏ nổi bật
    a_mo = lab_mo[:, :, 1]
    b_mo = lab_mo[:, :, 2]
    chroma = np.hypot(a_mo, b_mo)
    cong_mau = min(1.0, float(chroma.max()) / 8.0)

    v_chan = np.max(rgb_f32, axis=2)
    s_chan = (v_chan - np.min(rgb_f32, axis=2)) / np.maximum(v_chan, np.float32(1e-6))
    s_mo = cv2.GaussianBlur(s_chan, (5, 5), 0)
    v_mo = cv2.GaussianBlur(v_chan, (5, 5), 0)
    cong_sang_toi = np.clip((v_mo - np.float32(0.04)) / np.float32(0.07), np.float32(0.0), np.float32(1.0))
    sat_sach = s_mo * cong_sang_toi

    a_nen = max(0.0, float(a_mo.mean()))
    do_duong = np.maximum(np.float32(0.0), a_mo - np.float32(a_nen))
    r_vuot = np.maximum(np.float32(0.0), rgb_f32[:, :, 0] - np.maximum(rgb_f32[:, :, 1], rgb_f32[:, :, 2]))
    r_vuot_mo = cv2.GaussianBlur(r_vuot, (7, 7), 2.0) * cong_sang_toi
    do_noi = cv2.GaussianBlur(
        do_duong * (np.float32(1.0) + np.float32(0.25) * np.clip(b_mo / np.float32(30.0), np.float32(0.0), np.float32(1.0))),
        (7, 7),
        2.0,
    )
    cong_do = max(min(1.0, float(do_duong.max()) / 5.5), min(1.0, float(r_vuot_mo.max()) / 0.08))

    ket_hop_c = (
        np.float32(0.30 * cong_mau) * _chuan_hoa_01(chroma)
        + np.float32(0.25 * cong_mau) * _chuan_hoa_01(sat_sach)
        + np.float32(0.45 * cong_do) * _chuan_hoa_01(np.float32(0.6) * _chuan_hoa_01(do_noi) + np.float32(0.4) * _chuan_hoa_01(r_vuot_mo))
    )
    map_c = _chuan_hoa_01(ket_hop_c) * np.float32(max(cong_mau, cong_do))

    # Trung bình chuẩn hoá của (a), (b), (c) nhân center prior nhẹ (sigma=0.35 cạnh, trọng số 0.3)
    xs = (np.arange(wp, dtype=np.float32) + np.float32(0.5)) / np.float32(wp)
    ys = (np.arange(hp, dtype=np.float32) + np.float32(0.5)) / np.float32(hp)
    xx, yy = np.meshgrid(xs, ys)

    gauss_tam = np.exp(
        -(((xx - np.float32(0.5)) ** 2 + (yy - np.float32(0.5)) ** 2) / np.float32(2.0 * 0.35 * 0.35))
    ).astype(np.float32)
    center_prior = np.float32(0.7) + np.float32(0.3) * gauss_tam

    kc_mep = np.minimum(np.minimum(xx, np.float32(1.0) - xx), np.minimum(yy, np.float32(1.0) - yy))
    vanh_mep = np.clip((kc_mep - np.float32(le_mep * 0.5)) / np.float32(le_mep), np.float32(0.0), np.float32(1.0))

    sal_tb = (map_a + map_b + map_c) / np.float32(3.0)
    sal_nho = cv2.GaussianBlur(sal_tb * center_prior * vanh_mep, (5, 5), 1.2)
    if float(sal_nho.max() - sal_nho.min()) <= 1e-8:
        return np.zeros((h, w), dtype=np.float32)

    sal_nho = _chuan_hoa_01(sal_nho)
    return cv2.resize(sal_nho, (w, h), interpolation=cv2.INTER_LINEAR) if (wp != w or hp != h) else sal_nho.copy()


def tron_hut_mat_nguoi(
    sal_cu: np.ndarray,
    ds_mat: list[dict[str, Any] | list[float] | tuple[float, ...]],
    le_mep: float = 0.04,
) -> tuple[np.ndarray, list[list[float]]]:
    """Hàm trộn độc lập (không phụ thuộc YuNet, dùng trực tiếp cho unit test):
    - Nếu `ds_mat` rỗng: giữ nguyên `sal_cu` R2.
    - Nếu có mặt: ước vùng thân (rộng 3× mặt, cao 4× mặt xuống dưới), cộng trọng số vùng mặt (cao),
      vùng thân (vừa) và các điểm mắt/miệng từ landmark (nếu có) vào `sal_cu`, rồi chuẩn hoá về `[0, 1]`.
    Trả về `(sal_moi, ds_than)`.
    """
    if not ds_mat:
        return sal_cu.copy(), []

    h, w = sal_cu.shape[:2]
    nho_sal = thu_canh_dai(sal_cu, 512) if max(h, w) > 512 else sal_cu.astype(np.float32, copy=True)
    hp, wp = nho_sal.shape[:2]

    xs = (np.arange(wp, dtype=np.float32) + np.float32(0.5)) / np.float32(wp)
    ys = (np.arange(hp, dtype=np.float32) + np.float32(0.5)) / np.float32(hp)
    xx, yy = np.meshgrid(xs, ys)

    ban_do_mat = np.zeros((hp, wp), dtype=np.float32)
    ban_do_than = np.zeros((hp, wp), dtype=np.float32)
    ban_do_landmark = np.zeros((hp, wp), dtype=np.float32)
    ds_than: list[list[float]] = []

    for muc in ds_mat:
        if isinstance(muc, dict):
            hop = [float(v) for v in muc["hop"][:4]]
            diem = float(muc.get("diem", 1.0))
            pt_mt = muc.get("mat_trai")
            pt_mp = muc.get("mat_phai")
            pt_mi = muc.get("mieng")
        else:
            hop = [float(v) for v in muc[:4]]
            diem = 1.0
            pt_mt = pt_mp = pt_mi = None

        x0, y0, x1, y1 = hop
        fw = max(0.015, x1 - x0)
        fh = max(0.015, y1 - y0)
        cx, cy = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        w_conf = float(np.clip(diem, 0.55, 1.0))

        # Trọng số vùng mặt (cao): Gauss elip mượt phủ đúng hộp mặt (mở biên mềm 25% cạnh mặt)
        sx_m = np.float32(max(0.018, 0.48 * fw))
        sy_m = np.float32(max(0.018, 0.48 * fh))
        g_mat = np.exp(-(((xx - np.float32(cx)) / sx_m) ** 2 + ((yy - np.float32(cy)) / sy_m) ** 2) * np.float32(0.5))
        trong_hop_mat = (
            (xx >= x0 - 0.25 * fw) & (xx <= x1 + 0.25 * fw) & (yy >= y0 - 0.25 * fh) & (yy <= y1 + 0.25 * fh)
        )
        g_mat = np.where(trong_hop_mat, g_mat, g_mat * np.float32(0.25)).astype(np.float32)
        ban_do_mat = np.maximum(ban_do_mat, np.float32(0.95 * w_conf) * g_mat)

        # Trọng số vùng thân (vừa): rộng 3x mặt, cao 4x mặt xuống dưới
        hop_than = uoc_vung_than(hop)
        ds_than.append(hop_than)
        tx0, ty0, tx1, ty1 = hop_than
        tw = max(0.02, tx1 - tx0)
        th = max(0.02, ty1 - ty0)
        tcx = 0.5 * (tx0 + tx1)
        tcy = ty0 + 0.38 * th  # ưu tiên ngực/thân trên ngay dưới cổ
        sx_t = np.float32(max(0.025, 0.42 * tw))
        sy_t = np.float32(max(0.025, 0.45 * th))
        g_than = np.exp(-(((xx - np.float32(tcx)) / sx_t) ** 2 + ((yy - np.float32(tcy)) / sy_t) ** 2) * np.float32(0.5))
        trong_hop_than = (xx >= tx0) & (xx <= tx1) & (yy >= ty0) & (yy <= ty1)
        g_than = np.where(trong_hop_than, g_than, g_than * np.float32(0.15)).astype(np.float32)
        ban_do_than = np.maximum(ban_do_than, np.float32(0.30 * w_conf) * g_than)

        # Cộng thêm mắt trái, mắt phải và miệng từ landmark YuNet
        sigma_lm = np.float32(max(0.018, 0.16 * max(fw, fh)))
        for pt_lm, w_lm in ((pt_mt, 0.42), (pt_mp, 0.42), (pt_mi, 0.28)):
            if isinstance(pt_lm, (list, tuple)) and len(pt_lm) >= 2:
                lx, ly = float(pt_lm[0]), float(pt_lm[1])
                if 0.0 <= lx <= 1.0 and 0.0 <= ly <= 1.0:
                    g_lm = np.exp(
                        -(((xx - np.float32(lx)) ** 2 + (yy - np.float32(ly)) ** 2) / (np.float32(2.0) * sigma_lm * sigma_lm))
                    ).astype(np.float32)
                    ban_do_landmark = np.maximum(ban_do_landmark, np.float32(w_lm * w_conf) * g_lm)

    kc_mep = np.minimum(np.minimum(xx, np.float32(1.0) - xx), np.minimum(yy, np.float32(1.0) - yy))
    vanh_mep = np.clip((kc_mep - np.float32(le_mep * 0.5)) / np.float32(le_mep), np.float32(0.0), np.float32(1.0))

    ket_hop = (nho_sal + ban_do_mat + ban_do_than + ban_do_landmark) * vanh_mep
    ket_hop = cv2.GaussianBlur(ket_hop, (5, 5), 1.0)
    ket_hop_01 = _chuan_hoa_01(ket_hop)
    sal_moi = cv2.resize(ket_hop_01, (w, h), interpolation=cv2.INTER_LINEAR) if (wp != w or hp != h) else ket_hop_01
    return sal_moi, ds_than


def trich_dinh_hut_mat(
    sal: np.ndarray,
    toi_da: int = 3,
    kc_toi_thieu: float = 0.15,
    le_mep: float = 0.04,
) -> list[dict[str, float]]:
    """Loại điểm trong lề `le_mep` (4%) & chọn tối đa `toi_da` đỉnh bằng NMS bán kính `kc_toi_thieu` (0.15)."""
    h, w = sal.shape[:2]
    if float(sal.max() - sal.min()) <= 1e-8:
        return [{"x": 0.5, "y": 0.5, "diem": 0.0}]

    sal_nho = thu_canh_dai(sal, 512) if max(h, w) > 512 else sal.copy()
    sal_nho = _chuan_hoa_01(sal_nho)
    hp, wp = sal_nho.shape[:2]

    xs = (np.arange(wp, dtype=np.float32) + np.float32(0.5)) / np.float32(wp)
    ys = (np.arange(hp, dtype=np.float32) + np.float32(0.5)) / np.float32(hp)
    xx, yy = np.meshgrid(xs, ys)

    ban_sao = sal_nho.copy()
    ngoai_le = (xx < le_mep) | (xx > (1.0 - le_mep)) | (yy < le_mep) | (yy > (1.0 - le_mep))
    ban_sao[ngoai_le] = -1.0

    diem_hut: list[dict[str, float]] = []
    ban_kinh_chan = kc_toi_thieu + 0.006

    for _ in range(toi_da * 4):
        if len(diem_hut) >= toi_da:
            break
        vi_tri = int(np.argmax(ban_sao))
        iy, ix = divmod(vi_tri, wp)
        gia_tri = float(ban_sao[iy, ix])
        if gia_tri <= 0.0 or (diem_hut and gia_tri < 0.15):
            break

        rx = round(float(xs[ix]), 4)
        ry = round(float(ys[iy]), 4)
        if (le_mep <= rx <= 1.0 - le_mep) and (le_mep <= ry <= 1.0 - le_mep):
            if all(math.hypot(rx - d["x"], ry - d["y"]) >= kc_toi_thieu for d in diem_hut):
                diem_hut.append({"x": rx, "y": ry, "diem": round(gia_tri, 4)})
        ban_sao[(xx - rx) ** 2 + (yy - ry) ** 2 < ban_kinh_chan ** 2] = -1.0

    if not diem_hut:
        diem_hut.append({"x": 0.5, "y": 0.5, "diem": 1.0})
    return diem_hut


def do_hut_mat(
    img_bgr: np.ndarray,
    toi_da: int = 3,
    kc_toi_thieu: float = 0.15,
    le_mep: float = 0.04,
    ds_mat: list[dict[str, Any] | list[float] | tuple[float, ...]] | None = None,
) -> tuple[list[dict[str, float]], np.ndarray]:
    """Tính bản đồ hút mắt: saliency R2 + trọng số mặt/thân/landmark nếu có mặt; giữ nguyên R2 nếu không có mặt."""
    sal_r2 = tinh_saliency_r2(img_bgr, le_mep=le_mep)
    if float(sal_r2.max() - sal_r2.min()) <= 1e-8 and not ds_mat:
        return [{"x": 0.5, "y": 0.5, "diem": 0.0}], sal_r2
    if ds_mat:
        sal, _ = tron_hut_mat_nguoi(sal_r2, ds_mat, le_mep=le_mep)
    else:
        sal = sal_r2
    diem_hut = trich_dinh_hut_mat(sal, toi_da=toi_da, kc_toi_thieu=kc_toi_thieu, le_mep=le_mep)
    return diem_hut, sal


# ---------------- 4. Khớp bố cục (1/3, chéo, đối xứng) -----------------------------------------------

def do_bo_cuc(gray_u8: np.ndarray, hut_mat: list[dict[str, float]], sal: np.ndarray) -> dict[str, Any]:
    giao_1_3 = ((1.0 / 3.0, 1.0 / 3.0), (2.0 / 3.0, 1.0 / 3.0), (1.0 / 3.0, 2.0 / 3.0), (2.0 / 3.0, 2.0 / 3.0))
    can2 = math.sqrt(2.0)

    tong_w = sum(max(float(p["diem"]), 0.1) for p in hut_mat) or 1.0
    diem_1_3 = 0.0
    diem_cheo_pt = 0.0

    for p in hut_mat:
        px, py = float(p["x"]), float(p["y"])
        w = max(float(p["diem"]), 0.1)
        d_rot = min(math.hypot(px - gx, py - gy) for gx, gy in giao_1_3)
        diem_1_3 += w * math.exp(-((d_rot / 0.20) ** 2))

        d_diag = min(abs(px - py), abs(px + py - 1.0)) / can2
        diem_cheo_pt += w * math.exp(-((d_diag / 0.10) ** 2))

    mot_phan_ba = float(np.clip(diem_1_3 / tong_w, 0.0, 1.0))
    diem_cheo_pt /= tong_w

    sal64 = cv2.resize(sal, (64, 64), interpolation=cv2.INTER_AREA)
    u = (np.arange(64, dtype=np.float32) + 0.5) / 64.0
    uu, vv = np.meshgrid(u, u)
    kc_cheo = np.minimum(np.abs(uu - vv), np.abs(uu + vv - 1.0)) / np.float32(can2)
    trong_so_cheo = np.exp(-((kc_cheo / np.float32(0.10)) ** 2))
    cheo_map = float(np.sum(sal64 * trong_so_cheo) / (float(np.sum(sal64)) + 1e-8))
    cheo = float(np.clip(0.75 * diem_cheo_pt + 0.25 * cheo_map, 0.0, 1.0))

    g_sym = cv2.GaussianBlur(
        cv2.resize(gray_u8.astype(np.float32) / np.float32(255.0), (128, 128), interpolation=cv2.INTER_AREA),
        (5, 5),
        1.5,
    )
    g_lat = g_sym[:, ::-1]
    if float(g_sym.std()) < 0.015:
        doi_xung = float(np.clip(1.0 - float(np.mean(np.abs(g_sym - g_lat))), 0.0, 1.0))
    else:
        a = g_sym - float(g_sym.mean())
        b = g_lat - float(g_lat.mean())
        corr = float(np.sum(a * b) / (math.sqrt(float(np.sum(a * a) * np.sum(b * b))) + 1e-8))
        doi_xung = float(np.clip(max(0.0, corr), 0.0, 1.0))

    bang_diem = {
        "mot_phan_ba": round(mot_phan_ba, 4),
        "cheo": round(cheo, 4),
        "doi_xung": round(doi_xung, 4),
    }
    khop_nhat = max(("mot_phan_ba", "cheo", "doi_xung"), key=lambda k: bang_diem[k])
    return {**bang_diem, "khop_nhat": khop_nhat}


# ---------------- 5. Độ sâu 3 lớp & nhận diện ảnh phẳng ----------------------------------------------
# QUY ƯỚC BẤT BIẾN:
#   Mô hình Depth Anything V2 (`models/da2s.onnx`) xuất INVERSE DEPTH (độ sâu nghịch đảo tương đối):
#   -> Giá trị LỚN = GẦN (tiền cảnh), giá trị NHỎ = XA (hậu cảnh).
#   -> Trong cả `depth.png` và `lop.png`: GẦN = SÁNG NHẤT, XA = TỐI NHẤT.

def _lay_ort_session() -> ort.InferenceSession:
    global _ORT_SESS
    if _ORT_SESS is None:
        ung_vien = [Path(os.environ["REA_DEPTH"])] if os.environ.get("REA_DEPTH") else []
        ung_vien += [GOC_REPO / "models" / "da2s.onnx", Path.cwd() / "models" / "da2s.onnx",
                     Path.home() / ".cache" / "linhx-rea" / "models" / "da2s.onnx"]
        model_path = next((p for p in ung_vien if p.is_file()), ung_vien[0])
        if not model_path.is_file():
            raise FileNotFoundError(f"Không tìm thấy mô hình ONNX: {model_path}")
        _ORT_SESS = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    return _ORT_SESS


NGUONG_DAI_RAW_HEP = 0.35
NGUONG_DAI_NORM_HEP = 0.22
NGUONG_MANG_PHANG = 0.42
NGUONG_MANG_PHANG_RO = 0.48
NGUONG_DAI_RAW_RONG = 5.20
NGUONG_DAI_NORM_RONG = 0.75
NGUONG_KY_TU_NGANG = 50
NGUONG_DONG_CHU = 2


def quyet_dinh_phang(chi_so: dict[str, Any]) -> tuple[bool, str]:
    """Hàm thuần quyết định ảnh phẳng từ bộ chỉ số `chi_so_phang`:
    - `dai_hep`: depth thô hoặc chuẩn hoá có dải `p95 - p5` rất hẹp.
    - `dai_sau_rong`: cảnh 3D có dải độ sâu rộng (`dai_raw_p95_p5 >= 5.20` với `ti_le_mang_phang < 0.75`,
      hoặc `dai_norm_p95_p5 >= 0.75` kèm `ti_le_mang_phang < 0.48`) -> loại trừ khỏi nhánh `phang_chu`.
    - `phang_chu`: không thuộc `dai_sau_rong`, `ti_le_mang_phang >= 0.42`, `so_ky_tu_ngang >= 50`, `so_dong_chu >= 2`.
    """
    co_dai_raw = (chi_so.get("dai_raw_p95_p5") is not None) or (chi_so.get("dai_raw") is not None)
    dai_raw = float(chi_so.get("dai_raw_p95_p5", chi_so.get("dai_raw", 0.0)) or 0.0)
    dai_norm = float(chi_so.get("dai_norm_p95_p5", chi_so.get("dai_norm", 0.0)) or 0.0)
    ti_le_mang_phang = float(chi_so.get("ti_le_mang_phang", chi_so.get("mp", 0.0)) or 0.0)
    so_ky_tu_ngang = int(round(float(chi_so.get("so_ky_tu_ngang", chi_so.get("kt", 0.0)) or 0.0)))
    so_dong_chu = int(round(float(chi_so.get("so_dong_chu", chi_so.get("dong", 0.0)) or 0.0)))

    dai_hep = (co_dai_raw and dai_raw < NGUONG_DAI_RAW_HEP) or (
        dai_norm < NGUONG_DAI_NORM_HEP and ti_le_mang_phang >= NGUONG_MANG_PHANG
    )
    dai_sau_rong = (
        (co_dai_raw and dai_raw >= NGUONG_DAI_RAW_RONG and ti_le_mang_phang < 0.75)
        or (dai_norm >= NGUONG_DAI_NORM_RONG and ti_le_mang_phang < NGUONG_MANG_PHANG_RO)
    )
    phang_chu = (
        (not dai_sau_rong)
        and ti_le_mang_phang >= NGUONG_MANG_PHANG
        and so_ky_tu_ngang >= NGUONG_KY_TU_NGANG
        and so_dong_chu >= NGUONG_DONG_CHU
    )

    phang = bool(dai_hep or phang_chu)
    cac_ly_do: list[str] = []
    if dai_hep:
        cac_ly_do.append(f"depth_dai_hep(p95-p5_raw={dai_raw:.3f},norm={dai_norm:.3f})")
    if phang_chu:
        cac_ly_do.append(
            f"mang_phang_cao_nhieu_canh_chu(mang_phang={ti_le_mang_phang:.2f},ky_tu_ngang={so_ky_tu_ngang},dong_chu={so_dong_chu})"
        )
    return phang, "; ".join(cac_ly_do)


def _la_khung_chu_nhat_cua_so(comp_mask: np.ndarray, do_dac: float) -> bool:
    """Kiểm tra thành phần liên thông có hình dạng ô chữ nhật đặc hoặc khung chữ nhật 4 cạnh kiểu cửa sổ hay không
    (cả 4 dải biên ngoài của hộp giới hạn đều lấp đầy cao, khác hẳn nét chữ cái có cạnh hở hoặc góc bo).
    """
    h_c, w_c = comp_mask.shape[:2]
    if h_c < 5 or w_c < 5:
        return False
    ti_so = w_c / float(h_c)
    if not (0.48 <= ti_so <= 1.85):
        return False

    d_vien = max(1, min(w_c, h_c) // 5)
    b_tren = float(comp_mask[:d_vien, :].mean())
    b_duoi = float(comp_mask[-d_vien:, :].mean())
    b_trai = float(comp_mask[:, :d_vien].mean())
    b_phai = float(comp_mask[:, -d_vien:].mean())
    if min(b_tren, b_duoi, b_trai, b_phai) < 0.72:
        return False

    if do_dac >= 0.74:
        return True

    d_loi = min(max(1, d_vien * 2), (min(w_c, h_c) - 1) // 2)
    if h_c > 2 * d_loi and w_c > 2 * d_loi:
        loi = comp_mask[d_loi : h_c - d_loi, d_loi : w_c - d_loi]
        if float(loi.mean()) <= 0.42:
            return True
    return False


def _loc_bo_thanh_phan_cua_so(
    ds_ung_vien: list[tuple[str, float, float, float, float, float, bool, int]],
) -> list[tuple[float, float, float, float, int]]:
    """Loại bỏ các thành phần lặp đều kiểu cửa sổ khỏi danh sách ứng viên ký tự:
    1) Cùng cỡ, cách đều theo lưới 2 chiều (hàng × cột đều nhau).
    2) Tỉ lệ khung gần vuông (không có nét chữ hẹp hay cụm chữ dài) xếp thành nhiều hàng song song.
    """
    n = len(ds_ung_vien)
    if n == 0:
        return []

    loai_bo = [False] * n

    def _cung_co(w1: float, h1: float, w2: float, h2: float, sai_so: float = 0.25) -> bool:
        return abs(w1 - w2) <= max(2.0, sai_so * max(w1, w2)) and abs(h1 - h2) <= max(2.0, sai_so * max(h1, h2))

    def _cach_deu_1d(ds_kc_am: list[float], ds_kc_duong: list[float]) -> bool:
        am = sorted(ds_kc_am)
        duong = sorted(ds_kc_duong)
        if am and duong and abs(am[0] - duong[0]) <= 0.22 * max(am[0], duong[0]):
            return True
        if len(duong) >= 2 and abs(duong[1] - 2.0 * duong[0]) <= 0.22 * duong[1]:
            return True
        if len(am) >= 2 and abs(am[1] - 2.0 * am[0]) <= 0.22 * am[1]:
            return True
        return False

    # 1. Phát hiện lưới 2 chiều cùng cỡ, cách đều theo từng chế độ tương phản
    for che_do_chon in ("toi_tren_sang", "sang_tren_toi"):
        chi_muc = [i for i, u in enumerate(ds_ung_vien) if u[0] == che_do_chon]
        if len(chi_muc) < 4:
            continue

        cap_luoi_2x2: list[tuple[int, int, int, int]] = []
        co_2x2 = [False] * n
        co_deu_ngang = [False] * n
        co_deu_doc = [False] * n

        for i in chi_muc:
            _, cx1, cy1, w1, h1, _, _, _ = ds_ung_vien[i]
            ngang: list[int] = []
            doc: list[int] = []
            dxs_trai: list[float] = []
            dxs_phai: list[float] = []
            dys_tren: list[float] = []
            dys_duoi: list[float] = []

            for j in chi_muc:
                if j == i:
                    continue
                _, cx2, cy2, w2, h2, _, _, _ = ds_ung_vien[j]
                if not _cung_co(w1, h1, w2, h2):
                    continue
                khe_x = abs(cx2 - cx1) - 0.5 * (w1 + w2)
                khe_y = abs(cy2 - cy1) - 0.5 * (h1 + h2)
                if abs(cy2 - cy1) <= 0.30 * max(h1, h2) and 0.22 * w1 <= khe_x <= 5.5 * max(w1, w2):
                    ngang.append(j)
                    if cx2 < cx1:
                        dxs_trai.append(cx1 - cx2)
                    else:
                        dxs_phai.append(cx2 - cx1)
                if abs(cx2 - cx1) <= 0.30 * max(w1, w2) and 0.22 * h1 <= khe_y <= 5.5 * max(h1, h2):
                    doc.append(j)
                    if cy2 < cy1:
                        dys_tren.append(cy1 - cy2)
                    else:
                        dys_duoi.append(cy2 - cy1)

            co_deu_ngang[i] = _cach_deu_1d(dxs_trai, dxs_phai)
            co_deu_doc[i] = _cach_deu_1d(dys_tren, dys_duoi)

            for j in ngang:
                cx_j = ds_ung_vien[j][1]
                for k in doc:
                    cy_k = ds_ung_vien[k][2]
                    dung_sai = 0.30 * max(w1, h1)
                    for m in chi_muc:
                        if m in (i, j, k):
                            continue
                        _, cx_m, cy_m, w_m, h_m, _, _, _ = ds_ung_vien[m]
                        if (
                            _cung_co(w1, h1, w_m, h_m)
                            and abs(cx_m - cx_j) <= dung_sai
                            and abs(cy_m - cy_k) <= dung_sai
                        ):
                            co_2x2[i] = True
                            cap_luoi_2x2.append((i, j, k, m))
                            break

        hat_nhan_luoi = [False] * n
        for i in chi_muc:
            _, _, _, w1, h1, _, la_khung, _ = ds_ung_vien[i]
            ti_so = w1 / float(max(1.0, h1))
            if co_2x2[i] and (la_khung or ((0.48 <= ti_so <= 1.85) and (co_deu_ngang[i] or co_deu_doc[i]))):
                hat_nhan_luoi[i] = True

        for a, b, c, d in cap_luoi_2x2:
            if hat_nhan_luoi[a] or hat_nhan_luoi[b] or hat_nhan_luoi[c] or hat_nhan_luoi[d]:
                loai_bo[a] = loai_bo[b] = loai_bo[c] = loai_bo[d] = True
        for i in chi_muc:
            if hat_nhan_luoi[i]:
                loai_bo[i] = True

        # 2. Phát hiện nhiều hàng song song gồm các thành phần tỉ lệ gần vuông kiểu cửa sổ nhà
        da_tham = set()
        ds_hang_cua_so: list[list[int]] = []
        ds_hang_khung_ro: list[list[int]] = []

        for goc_i in chi_muc:
            if goc_i in da_tham:
                continue
            hang_doi = [goc_i]
            da_tham.add(goc_i)
            cum: list[int] = []
            while hang_doi:
                u = hang_doi.pop()
                cum.append(u)
                _, cx1, cy1, w1, h1, _, _, _ = ds_ung_vien[u]
                for v in chi_muc:
                    if v in da_tham:
                        continue
                    _, cx2, cy2, w2, h2, _, _, _ = ds_ung_vien[v]
                    h_tb = max(h1, h2)
                    kc_mep = max(0.0, abs(cx2 - cx1) - 0.5 * (w1 + w2))
                    if 0.45 <= (h2 / h1) <= 2.2 and abs(cy2 - cy1) <= 0.45 * h_tb and kc_mep <= 2.8 * h_tb:
                        da_tham.add(v)
                        hang_doi.append(v)

            if len(cum) < 2:
                continue
            cum.sort(key=lambda idx_c: ds_ung_vien[idx_c][1])
            ti_so_cum = [ds_ung_vien[idx_c][3] / float(max(1.0, ds_ung_vien[idx_c][4])) for idx_c in cum]
            co_net_hep = any(r < 0.45 for r in ti_so_cum)
            co_khoi_rong = any(r > 1.80 for r in ti_so_cum)
            if co_net_hep or co_khoi_rong:
                continue

            tl_gan_vuong = sum(1 for r in ti_so_cum if 0.50 <= r <= 1.65) / float(len(cum))
            if tl_gan_vuong < 0.80:
                continue

            tl_khung = sum(1 for idx_c in cum if ds_ung_vien[idx_c][6]) / float(len(cum))
            med_dac = float(np.median([ds_ung_vien[idx_c][5] for idx_c in cum]))

            ds_khe_w: list[float] = []
            for p_idx in range(len(cum) - 1):
                _, cx_a, _, w_a, _, _, _, _ = ds_ung_vien[cum[p_idx]]
                _, cx_b, _, w_b, _, _, _, _ = ds_ung_vien[cum[p_idx + 1]]
                if abs(cx_b - cx_a) < 0.30 * min(w_a, w_b):
                    continue
                khe = max(0.0, (cx_b - cx_a) - 0.5 * (w_a + w_b))
                ds_khe_w.append(khe / float(max(1.0, min(w_a, w_b))))

            min_khe_w = min(ds_khe_w) if ds_khe_w else 0.0
            med_khe_w = float(np.median(ds_khe_w)) if ds_khe_w else 0.0

            if tl_khung >= 0.75 and len(cum) >= 3 and min_khe_w >= 0.35:
                ds_hang_khung_ro.append(cum)
            if min_khe_w >= 0.32 and (
                (tl_khung >= 0.60 and med_khe_w >= 0.38)
                or (med_dac >= 0.60 and med_khe_w >= 0.42)
                or (len(cum) >= 3 and min_khe_w >= 0.45 and med_dac >= 0.52)
            ):
                ds_hang_cua_so.append(cum)

        for cum in ds_hang_khung_ro:
            for idx_c in cum:
                loai_bo[idx_c] = True

        # Đếm số cao độ dòng song song độc lập của các hàng cửa sổ gần vuông
        ys_hang_cs: list[tuple[float, float]] = []
        for cum in ds_hang_cua_so:
            cy_tb = float(np.mean([ds_ung_vien[idx_c][2] for idx_c in cum]))
            h_tb = float(np.mean([ds_ung_vien[idx_c][4] for idx_c in cum]))
            if all(abs(cy_tb - y0) > 0.70 * max(h_tb, h0) for y0, h0 in ys_hang_cs):
                ys_hang_cs.append((cy_tb, h_tb))

        if len(ys_hang_cs) >= 4:
            for cum in ds_hang_cua_so:
                for idx_c in cum:
                    loai_bo[idx_c] = True

    return [(u[1], u[2], u[3], u[4], u[7]) for i, u in enumerate(ds_ung_vien) if not loai_bo[i]]


def do_dac_trung_phang(img_bgr: np.ndarray, d_raw: np.ndarray, d_norm: np.ndarray) -> tuple[bool, str, dict[str, float]]:
    """Nhận diện ảnh phẳng (poster / thiết kế 2D / độ sâu dải hẹp):
    1) Depth chuẩn hoá thô có dải hẹp (`p95 - p5` của `d_raw` rất nhỏ, hoặc `p95 - p5` của `d_norm` hẹp kèm nền phẳng).
    2) Hoặc ảnh có dải độ sâu không quá rộng, tỉ lệ mảng màu phẳng cao KẾT HỢP nhiều cạnh chữ sắc nét xếp theo hàng ngang
       (đã lọc bỏ các thành phần lặp đều kiểu cửa sổ theo lưới 2 chiều hoặc khung gần vuông nhiều hàng song song).
    """
    dai_raw = float(np.percentile(d_raw, 95) - np.percentile(d_raw, 5))
    dai_norm = float(np.percentile(d_norm, 95) - np.percentile(d_norm, 5))

    # Tỉ lệ mảng màu phẳng trên ảnh thu cạnh dài 512:
    # Ô 8x8 có độ lệch chuẩn thấp (<= 4.2) VÀ không phải bóng tối kẹp đen của video (kênh sáng nhất >= 22)
    nho_512 = thu_canh_dai(img_bgr, 512) if max(img_bgr.shape[:2]) > 512 else img_bgr
    nh, nw = nho_512.shape[:2]
    b8_h, b8_w = max(1, nh // 8), max(1, nw // 8)
    cat_8 = nho_512[: b8_h * 8, : b8_w * 8].astype(np.float32)
    khoi_8 = cat_8.reshape(b8_h, 8, b8_w, 8, 3)
    std_8 = khoi_8.std(axis=(1, 3)).max(axis=2)
    max_kenh_8 = khoi_8.mean(axis=(1, 3)).max(axis=2)
    ti_le_mang_phang = float(((std_8 <= 4.2) & (max_kenh_8 >= 22.0)).mean())

    # Phát hiện mật độ ký tự / cạnh chữ trên nền phẳng (xét TÁCH RIÊNG chữ tối nền sáng & chữ sáng nền tối)
    anh_chu = thu_canh_dai(img_bgr, 1024) if max(img_bgr.shape[:2]) > 1024 else img_bgr
    gh, gw = anh_chu.shape[:2]
    gray = cv2.cvtColor(anh_chu, cv2.COLOR_BGR2GRAY)
    gx = np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3))
    gy = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))

    k_hat = cv2.getStructuringElement(cv2.MORPH_RECT, (29, 29))
    bhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, k_hat)  # chữ tối trên nền sáng
    that = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, k_hat)    # chữ sáng trên nền tối

    canh_lon = float(max(gh, gw))
    h_min = max(5, int(round(0.0045 * canh_lon)))
    h_max = max(h_min + 2, int(round(0.14 * canh_lon)))
    w_max = max(8, int(round(0.40 * canh_lon)))
    k3 = np.ones((3, 3), dtype=np.uint8)

    ds_ung_vien: list[tuple[str, float, float, float, float, float, bool, int]] = []
    for che_do, hat_map in (("toi_tren_sang", bhat), ("sang_tren_toi", that)):
        mask_net = (hat_map >= 48).astype(np.uint8)
        mask_loai = cv2.dilate((hat_map >= 24).astype(np.uint8), k3, iterations=1) > 0
        so_nhan, nhan_cc, thong_ke, tam_cc = cv2.connectedComponentsWithStats(mask_net, connectivity=8)

        for idx in range(1, so_nhan):
            x0 = int(thong_ke[idx, cv2.CC_STAT_LEFT])
            y0 = int(thong_ke[idx, cv2.CC_STAT_TOP])
            w_cc = int(thong_ke[idx, cv2.CC_STAT_WIDTH])
            h_cc = int(thong_ke[idx, cv2.CC_STAT_HEIGHT])
            dt_cc = int(thong_ke[idx, cv2.CC_STAT_AREA])
            if not (h_min <= h_cc <= h_max and 2 <= w_cc <= w_max and dt_cc >= 5):
                continue
            ti_so_wh = w_cc / float(h_cc)
            do_dac = dt_cc / float(max(1, w_cc * h_cc))
            if not (0.08 <= ti_so_wh <= 9.0 and 0.08 <= do_dac <= 0.88):
                continue

            # Vành nền ngay quanh ký tự phải phẳng và đúng chiều tương phản (loại bỏ khe giấy giữa các chữ)
            rx0, ry0 = max(0, x0 - 5), max(0, y0 - 5)
            rx1, ry1 = min(gw, x0 + w_cc + 5), min(gh, y0 + h_cc + 5)
            bg_px = gray[ry0:ry1, rx0:rx1][~mask_loai[ry0:ry1, rx0:rx1]]
            if bg_px.size < 8 or float(bg_px.std()) > 22.0:
                continue

            comp_mask = nhan_cc[y0 : y0 + h_cc, x0 : x0 + w_cc] == idx
            fg_px = gray[y0 : y0 + h_cc, x0 : x0 + w_cc][comp_mask]
            if fg_px.size == 0:
                continue
            tb_fg, tb_bg = float(fg_px.mean()), float(bg_px.mean())
            if che_do == "toi_tren_sang" and (tb_bg - tb_fg) < 42.0:
                continue
            if che_do == "sang_tren_toi" and (tb_fg - tb_bg) < 42.0:
                continue

            gx_max = float(gx[y0 : y0 + h_cc, x0 : x0 + w_cc].max())
            gy_max = float(gy[y0 : y0 + h_cc, x0 : x0 + w_cc].max())
            if ti_so_wh <= 0.35:
                if gx_max < 65.0:
                    continue
            elif gx_max < 55.0 or gy_max < 55.0:
                continue

            la_khung = _la_khung_chu_nhat_cua_so(comp_mask, do_dac)
            so_kt_uoc = max(1, min(6, int(round(w_cc / max(4.0, 0.75 * h_cc)))))
            ds_ung_vien.append(
                (che_do, float(tam_cc[idx, 0]), float(tam_cc[idx, 1]), float(w_cc), float(h_cc), float(do_dac), la_khung, so_kt_uoc)
            )

    ds_ky_tu = _loc_bo_thanh_phan_cua_so(ds_ung_vien)

    so_ky_tu_ngang = 0
    ys_dong: list[tuple[float, float]] = []
    for i, (cx1, cy1, w1, h1, uoc1) in enumerate(ds_ky_tu):
        cung_hang = uoc1 >= 3 and (w1 >= 1.8 * h1)
        if not cung_hang:
            for j, (cx2, cy2, w2, h2, _) in enumerate(ds_ky_tu):
                if i == j:
                    continue
                h_tb = max(h1, h2)
                khoang_cach_mep = max(0.0, abs(cx2 - cx1) - 0.5 * (w1 + w2))
                if 0.45 <= (h2 / h1) <= 2.2 and abs(cy2 - cy1) <= 0.45 * h_tb and khoang_cach_mep <= 2.8 * h_tb:
                    cung_hang = True
                    break
        if cung_hang:
            so_ky_tu_ngang += uoc1
            if all(abs(cy1 - y_d) > 0.70 * max(h1, h_d) for y_d, h_d in ys_dong):
                ys_dong.append((cy1, h1))

    so_dong_chu = len(ys_dong)
    chi_so = {
        "dai_raw_p95_p5": round(dai_raw, 4),
        "dai_norm_p95_p5": round(dai_norm, 4),
        "ti_le_mang_phang": round(ti_le_mang_phang, 4),
        "so_ky_tu_ngang": float(so_ky_tu_ngang),
        "so_dong_chu": float(so_dong_chu),
    }
    phang, ly_do_phang = quyet_dinh_phang(chi_so)
    return phang, ly_do_phang, chi_so


def ve_lop_png(lop: np.ndarray, ti_le: dict[str, float]) -> np.ndarray:
    """Vẽ `lop.png` theo đúng quy ước: gần (2) = sáng nhất (235), giữa (1) = 140, xa (0) = tối nhất (45),
    kèm chú giải nhỏ ở góc trên bên trái ảnh.
    """
    bang_xam = np.array([45, 140, 235], dtype=np.uint8)
    lop_u8 = bang_xam[lop]
    vis = cv2.cvtColor(lop_u8, cv2.COLOR_GRAY2BGR)
    vh, vw = vis.shape[:2]

    if vw < 140 or vh < 32:
        return vis

    co_chu = 0.42 if vw >= 520 else 0.32
    chu_giai = (
        f"gan(sang):{ti_le['gan']*100:.0f}%  "
        f"giua:{ti_le['giua']*100:.0f}%  "
        f"xa(toi):{ti_le['xa']*100:.0f}%"
    )
    (tw, th), _ = cv2.getTextSize(chu_giai, cv2.FONT_HERSHEY_SIMPLEX, co_chu, 1)
    hop_w = min(vw, tw + 62)
    hop_h = min(vh, th + 16)
    nen = vis[:hop_h, :hop_w].copy()
    vis[:hop_h, :hop_w] = (nen.astype(np.float32) * np.float32(0.22)).astype(np.uint8)

    y_o = max(2, (hop_h - 10) // 2)
    for idx_m, muc_xam in enumerate((235, 140, 45)):
        x0 = 6 + idx_m * 15
        if x0 + 11 < hop_w:
            vis[y_o : y_o + 10, x0 : x0 + 11] = (muc_xam, muc_xam, muc_xam)
            cv2.rectangle(vis, (x0, y_o), (x0 + 11, y_o + 10), (200, 200, 200), 1)

    cv2.putText(
        vis,
        chu_giai,
        (54, hop_h - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        co_chu,
        (245, 245, 245),
        1,
        cv2.LINE_AA,
    )
    return vis


def do_do_sau(img_bgr: np.ndarray) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    """Suy luận inverse depth (LỚN = GẦN), chuẩn hoá 0..1, phân 3 lớp k-means 1D và kiểm tra ảnh phẳng."""
    sess = _lay_ort_session()
    ten_in = sess.get_inputs()[0].name

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    rgb_518 = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), (518, 518), interpolation=cv2.INTER_CUBIC)
    x = (rgb_518.astype(np.float32) / np.float32(255.0) - mean) / std
    x = np.ascontiguousarray(x.transpose(2, 0, 1)[None], dtype=np.float32)

    d_raw = np.squeeze(sess.run(None, {ten_in: x})[0]).astype(np.float32)

    h, w = img_bgr.shape[:2]
    if max(h, w) > 1024:
        ti_le_kt = 1024.0 / float(max(h, w))
        target_w, target_h = max(1, int(round(w * ti_le_kt))), max(1, int(round(h * ti_le_kt)))
    else:
        target_w, target_h = w, h

    d = cv2.resize(d_raw, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
    d = cv2.GaussianBlur(d, (0, 0), 3)

    d_min, d_max = float(d.min()), float(d.max())
    if d_max - d_min < 1e-6:
        d_norm = np.full((target_h, target_w), 0.5, dtype=np.float32)
        t1, t2 = 0.3333, 0.6667
    else:
        d_norm = ((d - np.float32(d_min)) / np.float32(d_max - d_min)).astype(np.float32)
        d_nho = thu_canh_dai(d_norm, 256) if max(target_h, target_w) > 256 else d_norm
        mau_1d = d_nho.reshape(-1, 1).astype(np.float32)

        if np.unique(mau_1d).size < 3:
            t1, t2 = 0.3333, 0.6667
        else:
            cv2.setRNGSeed(0)
            tieu_chi = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 1e-4)
            _, _, tam = cv2.kmeans(mau_1d, 3, None, tieu_chi, 5, cv2.KMEANS_PP_CENTERS)
            c0, c1, c2 = sorted(float(v) for v in tam.ravel())
            t1 = float(np.clip(0.5 * (c0 + c1), 1e-4, 0.9998))
            t2 = float(np.clip(0.5 * (c1 + c2), t1 + 1e-4, 0.9999))

    lop = np.where(d_norm >= t2, 2, np.where(d_norm >= t1, 1, 0))
    gan = round(float((lop == 2).mean()), 4)
    giua = round(float((lop == 1).mean()), 4)
    xa = round(max(0.0, 1.0 - gan - giua), 4)
    ti_le_lop = {"gan": gan, "giua": giua, "xa": xa}

    ys_gan, xs_gan = np.nonzero(lop == 2)
    if xs_gan.size > 0:
        cx_gan = float((xs_gan.astype(np.float64) + 0.5).mean() / float(target_w))
        cy_gan = float((ys_gan.astype(np.float64) + 0.5).mean() / float(target_h))
    else:
        vi_tri_max = int(np.argmax(d_norm))
        iy_m, ix_m = divmod(vi_tri_max, target_w)
        cx_gan = (float(ix_m) + 0.5) / float(target_w)
        cy_gan = (float(iy_m) + 0.5) / float(target_h)

    phang, ly_do_phang, chi_so_phang = do_dac_trung_phang(img_bgr, d_raw, d_norm)

    depth_u8 = (d_norm * np.float32(255.0)).round().clip(0, 255).astype(np.uint8)
    lop_vis = ve_lop_png(lop, ti_le_lop)

    thong_so = {
        "quy_uoc": "inverse_depth_lon_la_gan",
        "nguong": [round(t1, 4), round(t2, 4)],
        "ti_le": ti_le_lop,
        "vung_gan_tam": {"x": round(cx_gan, 4), "y": round(cy_gan, 4)},
        "phang": phang,
        "ly_do_phang": ly_do_phang,
        "chi_so_phang": chi_so_phang,
    }
    return thong_so, depth_u8, lop_vis


# ---------------- 6. OCR (tuỳ chọn nếu có rapidocr_onnxruntime) --------------------------------------

def do_ocr(img_bgr: np.ndarray) -> dict[str, Any]:
    global _OCR_ENGINE
    if _OCR_ENGINE is None:
        return {"co_cong_cu": False, "chu": []}
    if _OCR_ENGINE is False:
        try:
            from rapidocr_onnxruntime import RapidOCR  # type: ignore

            _OCR_ENGINE = RapidOCR()
        except Exception:
            _OCR_ENGINE = None
            return {"co_cong_cu": False, "chu": []}

    try:
        kq, _ = _OCR_ENGINE(img_bgr)
        h, w = img_bgr.shape[:2]
        ds_chu = []
        for muc in kq or []:
            box, van_ban, diem = muc[0], str(muc[1]).strip(), float(muc[2])
            if not van_ban:
                continue
            xs = [pt[0] / float(w) for pt in box]
            ys = [pt[1] / float(h) for pt in box]
            ds_chu.append({
                "noi_dung": van_ban,
                "diem": round(diem, 3),
                "vung": [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)],
            })
        return {"co_cong_cu": True, "chu": ds_chu}
    except Exception:
        return {"co_cong_cu": False, "chu": []}


# ---------------- 7. Vẽ ảnh chú thích `do.png` & bản đồ nhiệt `hut_mat.png` --------------------------

def _hex_sang_bgr(ma_hex: str) -> tuple[int, int, int]:
    h = ma_hex.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b, g, r)


def ve_hut_mat_png(img_bgr: np.ndarray, sal: np.ndarray, hut_mat: list[dict[str, float]], co_mat: bool = False) -> np.ndarray:
    """Vẽ heatmap hút mắt phủ lên ảnh kèm các điểm đỉnh NMS đã chọn."""
    vis = thu_canh_dai(img_bgr, 1024).copy()
    vh, vw = vis.shape[:2]
    sal_vis = cv2.resize(sal, (vw, vh), interpolation=cv2.INTER_LINEAR) if sal.shape[:2] != (vh, vw) else sal
    sal_u8 = (np.clip(sal_vis, 0.0, 1.0) * np.float32(255.0)).round().astype(np.uint8)
    heat = cv2.applyColorMap(sal_u8, cv2.COLORMAP_JET)
    out = cv2.addWeighted(vis, 0.52, heat, 0.48, 0.0)

    for idx, pt in enumerate(hut_mat, start=1):
        px = int(round(float(pt["x"]) * (vw - 1)))
        py = int(round(float(pt["y"]) * (vh - 1)))
        cv2.circle(out, (px, py), 16, (10, 10, 10), 4, cv2.LINE_AA)
        cv2.circle(out, (px, py), 16, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.circle(out, (px, py), 3, (255, 255, 255), -1, cv2.LINE_AA)
        nhan = f"{idx}({pt['diem']:.2f})"
        tx = px + 18 if px + 88 < vw else max(6, px - 82)
        ty = py - 10 if py - 24 > 28 else min(vh - 10, py + 24)
        cv2.putText(out, nhan, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (10, 10, 10), 3, cv2.LINE_AA)
        cv2.putText(out, nhan, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 1, cv2.LINE_AA)

    if vw >= 220 and vh >= 32:
        chu = (
            "hut_mat: R2 + YuNet(mat+than+landmark)"
            if co_mat
            else "hut_mat: SR(Lab)+Achanta+Sat/Red * CenterPrior"
        )
        (tw, th), _ = cv2.getTextSize(chu, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        hop_w, hop_h = min(vw, tw + 16), min(vh, th + 12)
        out[:hop_h, :hop_w] = (out[:hop_h, :hop_w].astype(np.float32) * np.float32(0.28)).astype(np.uint8)
        cv2.putText(out, chu, (8, hop_h - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    return out


def ve_do_png(img_bgr: np.ndarray, ket_qua: dict[str, Any]) -> np.ndarray:
    vis = thu_canh_dai(img_bgr, 1024).copy()
    vh, vw = vis.shape[:2]
    cao_dai_mau = max(24, min(36, vh // 18))

    # 1. Vẽ lưới 1/3 có viền mờ để nổi trên cả nền sáng lẫn tối
    lop_luoi = vis.copy()
    x1, x2 = vw // 3, (2 * vw) // 3
    y1, y2 = vh // 3, (2 * vh) // 3
    for xv in (x1, x2):
        cv2.line(lop_luoi, (int(xv), 0), (int(xv), int(vh - cao_dai_mau)), (20, 20, 20), 2, cv2.LINE_AA)
        cv2.line(lop_luoi, (int(xv), 0), (int(xv), int(vh - cao_dai_mau)), (235, 235, 235), 1, cv2.LINE_AA)
    for yv in (y1, y2):
        cv2.line(lop_luoi, (0, int(yv)), (int(vw), int(yv)), (20, 20, 20), 2, cv2.LINE_AA)
        cv2.line(lop_luoi, (0, int(yv)), (int(vw), int(yv)), (235, 235, 235), 1, cv2.LINE_AA)
    for gx in (x1, x2):
        for gy in (y1, y2):
            cv2.circle(lop_luoi, (int(gx), int(gy)), 4, (0, 220, 255), -1, cv2.LINE_AA)
    vis = cv2.addWeighted(lop_luoi, 0.55, vis, 0.45, 0.0)

    # 2. Vẽ hộp mặt từ YuNet (nếu có)
    ds_mat = (ket_qua.get("nguoi") or {}).get("mat") or []
    for idx_m, m_info in enumerate(ds_mat, start=1):
        hop = m_info.get("hop") or []
        if len(hop) == 4:
            mx0 = int(round(float(hop[0]) * (vw - 1)))
            my0 = int(round(float(hop[1]) * (vh - 1)))
            mx1 = int(round(float(hop[2]) * (vw - 1)))
            my1 = int(round(float(hop[3]) * (vh - 1)))
            cv2.rectangle(vis, (mx0, my0), (mx1, my1), (15, 15, 15), 4, cv2.LINE_AA)
            cv2.rectangle(vis, (mx0, my0), (mx1, my1), (75, 240, 95), 2, cv2.LINE_AA)
            nhan_m = f"M{idx_m}:{float(m_info.get('diem', 0.0)):.2f}"
            ty_m = my0 - 6 if my0 > 44 else min(vh - cao_dai_mau - 8, my1 + 16)
            cv2.putText(vis, nhan_m, (max(4, mx0), ty_m), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (15, 15, 15), 3, cv2.LINE_AA)
            cv2.putText(vis, nhan_m, (max(4, mx0), ty_m), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (75, 240, 95), 1, cv2.LINE_AA)

    # 3. Đánh số các điểm hút mắt
    for idx, pt in enumerate(ket_qua.get("hut_mat") or [], start=1):
        px = int(round(float(pt["x"]) * (vw - 1)))
        py = int(round(float(pt["y"]) * (vh - 1)))
        cv2.circle(vis, (px, py), 18, (15, 15, 15), 4, cv2.LINE_AA)
        cv2.circle(vis, (px, py), 18, (0, 215, 255), 2, cv2.LINE_AA)
        cv2.circle(vis, (px, py), 3, (0, 80, 255), -1, cv2.LINE_AA)
        nhan = str(idx)
        tx = px + 20 if px + 36 < vw else max(6, px - 30)
        ty = py - 12 if py - 24 > 32 else min(vh - cao_dai_mau - 8, py + 26)
        cv2.putText(vis, nhan, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 0.7, (10, 10, 10), 4, cv2.LINE_AA)
        cv2.putText(vis, nhan, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 230, 255), 1, cv2.LINE_AA)

    # 4. Góc trên ghi kiểu tông + bố cục khớp nhất + số mặt / trạng thái phẳng
    tong = ket_qua["tong"]
    bc = ket_qua["bo_cuc"]
    kn = bc["khop_nhat"]
    phu_chu = f" | mat:{len(ds_mat)}" if ds_mat else ""
    if (ket_qua.get("do_sau") or {}).get("phang"):
        phu_chu += " | PHANG"
    chu_dau = f"tong: {tong['kieu']} (tb={tong['trung_binh']:.2f}) | bo cuc: {kn} ({bc[kn]:.2f}){phu_chu}"
    (tw, th), _ = cv2.getTextSize(chu_dau, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
    hop_w = min(vw, tw + 20)
    hop_h = min(vh, th + 16)
    nen_tren = vis[:hop_h, :hop_w].copy()
    vis[:hop_h, :hop_w] = (nen_tren.astype(np.float32) * 0.30).astype(np.uint8)
    cv2.putText(vis, chu_dau, (10, hop_h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)

    # 5. Dải 6 màu ở đáy ảnh (giữ nguyên cạnh dài 1024)
    y0 = vh - cao_dai_mau
    cv2.line(vis, (0, max(0, y0 - 1)), (vw, max(0, y0 - 1)), (30, 30, 30), 1)
    x_bat_dau = 0
    ds_mau = ket_qua.get("mau") or []
    for i, m in enumerate(ds_mau):
        bgr = _hex_sang_bgr(m["hex"])
        x_ket_thuc = vw if i == len(ds_mau) - 1 else min(vw, x_bat_dau + int(round(float(m["ti_le"]) * vw)))
        if x_ket_thuc > x_bat_dau:
            vis[y0:vh, x_bat_dau:x_ket_thuc] = bgr
            do_rong_o = x_ket_thuc - x_bat_dau
            if do_rong_o >= 78:
                do_sang_mau = 0.114 * bgr[0] + 0.587 * bgr[1] + 0.299 * bgr[2]
                mau_chu = (20, 20, 20) if do_sang_mau > 140 else (245, 245, 245)
                cv2.putText(
                    vis,
                    m["hex"],
                    (x_bat_dau + 6, y0 + (cao_dai_mau + 10) // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.40,
                    mau_chu,
                    1,
                    cv2.LINE_AA,
                )
        x_bat_dau = x_ket_thuc

    return vis


# ---------------- Điều phối đo 1 ảnh -----------------------------------------------------------------

def do_mot_anh(anh_path: str | Path, out_dir: str | Path) -> dict[str, Any]:
    p_anh = Path(anh_path)
    p_ra = Path(out_dir)
    p_ra.mkdir(parents=True, exist_ok=True)

    img_bgr = doc_anh_bgr(p_anh)
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    mau = do_mau(img_bgr, so_mau=6)
    tong = do_tong(gray)
    nguoi = do_nguoi(img_bgr)
    ds_mat = nguoi.get("mat") if nguoi.get("co_cong_cu") else None
    hut_mat, sal = do_hut_mat(img_bgr, toi_da=3, kc_toi_thieu=0.15, le_mep=0.04, ds_mat=ds_mat)
    bo_cuc = do_bo_cuc(gray, hut_mat, sal)
    do_sau, depth_u8, lop_vis = do_do_sau(img_bgr)
    ocr = do_ocr(img_bgr)

    ket_qua: dict[str, Any] = {
        "anh": p_anh.name,
        "kich_thuoc": [int(w), int(h)],
        "mau": mau,
        "tong": tong,
        "nguoi": nguoi,
        "hut_mat": hut_mat,
        "bo_cuc": bo_cuc,
        "do_sau": do_sau,
        "ocr": ocr,
        "phien_ban": PHIEN_BAN,
    }

    (p_ra / "do.json").write_text(json.dumps(ket_qua, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ghi_anh(p_ra / "depth.png", depth_u8)
    ghi_anh(p_ra / "lop.png", lop_vis)
    ghi_anh(p_ra / "hut_mat.png", ve_hut_mat_png(img_bgr, sal, hut_mat, co_mat=bool(ds_mat)))
    ghi_anh(p_ra / "do.png", ve_do_png(img_bgr, ket_qua))
    return ket_qua


def tao_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="anh_do.py", description="Máy đo định lượng ảnh cho rea-anh.")
    p.add_argument("anh", help="Đường dẫn file ảnh đầu vào.")
    p.add_argument(
        "-o",
        "--out",
        required=True,
        dest="out_dir",
        help="Thư mục ghi kết quả (do.json, do.png, hut_mat.png, depth.png, lop.png).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    _cau_hinh_utf8()
    args = tao_parser().parse_args(argv)
    do_mot_anh(args.anh, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
