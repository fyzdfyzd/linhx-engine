"""Logic thuần Python quản lý LX Pilot gắn Cơ hội: playbook 7 bước, hạn 14 ngày, báo trễ."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta
import json
import logging

SO_BUOC = 7
SO_NGAY_HAN = 14
DINH_DANG_TG = "%Y-%m-%d %H:%M:%S"
DINH_DANG_NGAY = "%Y-%m-%d"

TRANG_THAI_PILOT = ("dang_chay", "xong", "huy")
TRANG_THAI_BUOC = ("chua_lam", "xong")

PLAYBOOK_7_BUOC: tuple[dict[str, object], ...] = (
    {"so": 1, "ma": "khao_sat_bai_toan", "ten": "Khảo sát bài toán và chọn quy trình mục tiêu"},
    {"so": 2, "ma": "do_chi_so_nen", "ten": "Đo chỉ số nền (baseline) và chốt KPI nghiệm thu"},
    {"so": 3, "ma": "chuan_bi_du_lieu", "ten": "Thu thập, làm sạch dữ liệu mẫu và phân quyền"},
    {"so": 4, "ma": "cau_hinh_agent", "ten": "Cấu hình Agent và kịch bản xử lý chuẩn"},
    {"so": 5, "ma": "chay_thu_hat_nhan", "ten": "Chạy thử nghiệm với nhóm nhân sự hạt nhân"},
    {"so": 6, "ma": "do_luong_ket_qua", "ten": "Đo lường kết quả thực tế đối chiếu baseline"},
    {"so": 7, "ma": "nghiem_thu_mo_rong", "ten": "Nghiệm thu Pilot và đề xuất lộ trình mở rộng"},
)

logger = logging.getLogger(__name__)


def bay_gio() -> str:
    """Trả thời điểm hiện tại theo giờ hệ thống dạng 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.now().replace(microsecond=0).strftime(DINH_DANG_TG)


def _parse_tg(gia_tri: object) -> datetime:
    if isinstance(gia_tri, bool) or gia_tri is None:
        raise ValueError("Thời gian không hợp lệ")
    if isinstance(gia_tri, datetime):
        if gia_tri.tzinfo is not None:
            gia_tri = gia_tri.astimezone().replace(tzinfo=None)
        return gia_tri.replace(microsecond=0)
    if not isinstance(gia_tri, str):
        raise ValueError("Thời gian phải là chuỗi hoặc datetime")
    chu = gia_tri.strip()
    if not chu:
        raise ValueError("Thời gian trống")
    try:
        dt = datetime.fromisoformat(chu.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone().replace(tzinfo=None)
        return dt.replace(microsecond=0)
    except ValueError:
        pass
    if "." in chu:
        chu = chu.split(".", 1)[0]
    if "T" in chu:
        chu = chu.replace("T", " ")
    if len(chu) == 10:
        return datetime.strptime(chu, DINH_DANG_NGAY)
    return datetime.strptime(chu, DINH_DANG_TG)


def chuan_hoa_tg(gia_tri: object) -> str:
    """Chuẩn hoá thời điểm về chuỗi 'YYYY-MM-DD HH:MM:SS'."""
    return _parse_tg(gia_tri).strftime(DINH_DANG_TG)


def tinh_han_hoan_thanh(bat_dau_luc: str | datetime) -> str:
    """Tính hạn hoàn thành pilot = bat_dau_luc + 14 ngày ('YYYY-MM-DD HH:MM:SS')."""
    dt = _parse_tg(bat_dau_luc) + timedelta(days=SO_NGAY_HAN)
    return dt.strftime(DINH_DANG_TG)


def tao_cac_buoc_mac_dinh() -> list[dict]:
    """Tạo danh sách 7 bước chuẩn của playbook ở trạng thái chua_lam."""
    return [
        {
            "so": int(b["so"]),
            "ma": str(b["ma"]),
            "ten": str(b["ten"]),
            "trang_thai": "chua_lam",
            "xong_luc": None,
        }
        for b in PLAYBOOK_7_BUOC
    ]


def doc_cac_buoc(cac_buoc: object) -> list[dict]:
    """Đọc và kiểm tra danh sách 7 bước từ list hoặc chuỗi JSON."""
    raw = cac_buoc
    if isinstance(raw, str):
        chu = raw.strip()
        if not chu:
            raise ValueError("Danh sách bước trống")
        try:
            raw = json.loads(chu)
        except Exception as exc:
            raise ValueError("cac_buoc không phải JSON hợp lệ") from exc
    if not isinstance(raw, (list, tuple)) or len(raw) != SO_BUOC:
        raise ValueError(f"Pilot bắt buộc có đúng {SO_BUOC} bước")

    ket_qua: list[dict] = []
    for idx, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Bước thứ {idx} phải là dict")
        so = item.get("so")
        if isinstance(so, bool) or not isinstance(so, int) or so != idx:
            raise ValueError(f"Thứ tự bước không hợp lệ tại vị trí {idx}: {so!r}")
        tt = item.get("trang_thai")
        if not isinstance(tt, str) or tt not in TRANG_THAI_BUOC:
            raise ValueError(f"Trạng thái bước {so} không hợp lệ: {tt!r}")
        mau = PLAYBOOK_7_BUOC[idx - 1]
        ma = str(item.get("ma") or mau["ma"]).strip()
        ten = str(item.get("ten") or mau["ten"]).strip()
        xong_luc = item.get("xong_luc")
        if tt == "xong":
            if xong_luc is not None and str(xong_luc).strip():
                xong_luc = chuan_hoa_tg(xong_luc)
        else:
            xong_luc = None
        ket_qua.append(
            {
                "so": so,
                "ma": ma,
                "ten": ten,
                "trang_thai": tt,
                "xong_luc": xong_luc,
            }
        )

    da_chua_lam = False
    for b in ket_qua:
        if b["trang_thai"] != "xong":
            da_chua_lam = True
        elif da_chua_lam:
            raise ValueError(
                f"Không được hoàn thành bước {b['so']} khi bước trước chưa xong"
            )
    return ket_qua


def tao_pilot(co_hoi: str, bat_dau_luc: str, phu_trach: str = "") -> dict:
    """Tạo pilot mới gắn với cơ hội, gồm đúng 7 bước và hạn hoàn thành 14 ngày."""
    if isinstance(co_hoi, bool) or not isinstance(co_hoi, str) or not co_hoi.strip():
        raise ValueError("Mã cơ hội không được để trống")
    if isinstance(phu_trach, bool) or (phu_trach is not None and not isinstance(phu_trach, str)):
        raise ValueError("Người phụ trách không hợp lệ")

    co_hoi_chuan = co_hoi.strip()
    phu_trach_chuan = (phu_trach or "").strip()
    bat_dau_chuan = chuan_hoa_tg(bat_dau_luc)
    han_hoan_thanh = tinh_han_hoan_thanh(bat_dau_chuan)

    return {
        "co_hoi": co_hoi_chuan,
        "phu_trach": phu_trach_chuan,
        "bat_dau_luc": bat_dau_chuan,
        "han_hoan_thanh": han_hoan_thanh,
        "trang_thai": "dang_chay",
        "cac_buoc": tao_cac_buoc_mac_dinh(),
    }


def hoan_thanh_buoc(pilot: dict, so_buoc: int, luc: str) -> dict:
    """Đánh dấu hoàn thành bước so_buoc (1..7); chặn nhảy bước khi bước trước chưa xong."""
    if not isinstance(pilot, dict):
        raise ValueError("Pilot phải là dict")
    if isinstance(so_buoc, bool) or not isinstance(so_buoc, int) or not (1 <= so_buoc <= SO_BUOC):
        raise ValueError(f"so_buoc phải trong khoảng 1..{SO_BUOC}")

    luc_chuan = chuan_hoa_tg(luc)
    trang_thai_pilot = pilot.get("trang_thai", "dang_chay")
    if trang_thai_pilot not in ("dang_chay", "xong"):
        raise ValueError(f"Không thể hoàn thành bước khi pilot ở trạng thái {trang_thai_pilot!r}")

    cac_buoc = doc_cac_buoc(pilot.get("cac_buoc"))
    for b in cac_buoc:
        if b["so"] < so_buoc and b["trang_thai"] != "xong":
            raise ValueError(
                f"Không được đi bước {so_buoc} khi bước {b['so']} chưa xong"
            )

    ket_qua = copy.deepcopy(pilot)
    cac_buoc_moi = copy.deepcopy(cac_buoc)
    buoc_hien_tai = cac_buoc_moi[so_buoc - 1]
    buoc_hien_tai["trang_thai"] = "xong"
    buoc_hien_tai["xong_luc"] = luc_chuan

    ket_qua["cac_buoc"] = cac_buoc_moi
    if so_buoc == SO_BUOC or all(b["trang_thai"] == "xong" for b in cac_buoc_moi):
        ket_qua["trang_thai"] = "xong"
    else:
        ket_qua["trang_thai"] = "dang_chay"
    return ket_qua


def kiem_pilot(pilot: dict) -> dict:
    """Kiểm tra tính hợp lệ toàn diện của dict Pilot và trả về bản chuẩn hoá."""
    if not isinstance(pilot, dict):
        raise ValueError("Pilot phải là dict")

    co_hoi = pilot.get("co_hoi")
    if isinstance(co_hoi, bool) or not isinstance(co_hoi, str) or not co_hoi.strip():
        raise ValueError("Pilot thiếu mã cơ hội (co_hoi)")

    bat_dau_chuan = chuan_hoa_tg(pilot.get("bat_dau_luc"))
    han_toi_da = tinh_han_hoan_thanh(bat_dau_chuan)

    han_raw = pilot.get("han_hoan_thanh")
    if han_raw is None or not str(han_raw).strip():
        han_chuan = han_toi_da
    else:
        dt_han = _parse_tg(han_raw)
        dt_bat_dau = _parse_tg(bat_dau_chuan)
        dt_toi_da = _parse_tg(han_toi_da)
        if dt_han < dt_bat_dau:
            raise ValueError("han_hoan_thanh không được nhỏ hơn bat_dau_luc")
        if dt_han > dt_toi_da:
            han_chuan = han_toi_da
        else:
            han_chuan = dt_han.strftime(DINH_DANG_TG)

    trang_thai = pilot.get("trang_thai") or "dang_chay"
    if not isinstance(trang_thai, str) or trang_thai not in TRANG_THAI_PILOT:
        raise ValueError(f"trang_thai không hợp lệ: {trang_thai!r}")

    cac_buoc = doc_cac_buoc(pilot.get("cac_buoc"))
    tat_ca_xong = all(b["trang_thai"] == "xong" for b in cac_buoc)
    if trang_thai == "xong" and not tat_ca_xong:
        raise ValueError("Chưa hoàn thành đủ 7 bước nên không thể đặt trạng thái xong")
    if trang_thai == "huy" and tat_ca_xong:
        raise ValueError("Đã hoàn thành đủ 7 bước nên không thể đặt trạng thái huỷ")
    if trang_thai == "dang_chay" and tat_ca_xong:
        trang_thai = "xong"

    ket_qua = dict(pilot)
    ket_qua["co_hoi"] = co_hoi.strip()
    ket_qua["phu_trach"] = str(pilot.get("phu_trach") or "").strip()
    ket_qua["bat_dau_luc"] = bat_dau_chuan
    ket_qua["han_hoan_thanh"] = han_chuan
    ket_qua["trang_thai"] = trang_thai
    ket_qua["cac_buoc"] = cac_buoc
    return ket_qua


def viec_cho(ds_pilot: list[dict], luc: str | datetime) -> list[dict]:
    """Trả danh sách các pilot đang chạy đã quá hạn 14 ngày (luc > han_hoan_thanh), xếp han_hoan_thanh tăng dần."""
    moc = _parse_tg(luc)
    ket_qua: list[tuple[tuple[int, str, int], dict]] = []

    for idx, p in enumerate(ds_pilot or []):
        if not isinstance(p, dict):
            continue
        if p.get("trang_thai") != "dang_chay":
            continue
        cac_buoc_raw = p.get("cac_buoc")
        if isinstance(cac_buoc_raw, (list, tuple)) and len(cac_buoc_raw) == SO_BUOC:
            if all(isinstance(b, dict) and b.get("trang_thai") == "xong" for b in cac_buoc_raw):
                continue

        han_str = str(p.get("han_hoan_thanh") or "").strip()
        bat_dau_str = str(p.get("bat_dau_luc") or "").strip()
        dt_han = None
        if han_str:
            try:
                dt_han = _parse_tg(han_str)
            except ValueError:
                logger.warning("LX Pilot %s có han_hoan_thanh sai định dạng: %r", p.get("name") or p.get("co_hoi"), han_str)
        if bat_dau_str:
            try:
                dt_han_tu_bd = _parse_tg(bat_dau_str) + timedelta(days=SO_NGAY_HAN)
                dt_han = min(dt_han, dt_han_tu_bd) if dt_han is not None else dt_han_tu_bd
            except ValueError:
                logger.warning("LX Pilot %s có bat_dau_luc sai định dạng: %r", p.get("name") or p.get("co_hoi"), bat_dau_str)

        if dt_han is None:
            continue

        if moc > dt_han:
            ban = copy.deepcopy(p)
            ban["qua_han"] = True
            khoa_xep = (0, dt_han.strftime(DINH_DANG_TG), idx)
            ket_qua.append((khoa_xep, ban))

    ket_qua.sort(key=lambda item: item[0])
    return [ban for _, ban in ket_qua]
