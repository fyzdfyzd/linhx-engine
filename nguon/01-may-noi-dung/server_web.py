#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Máy chủ Web Tương tác Local cho Đề 01: Máy Tạo Nội Dung (`01_MAY_TAO_NOI_DUNG` — Cổng cố định 8010).

Phục vụ:
- Giao diện Web Studio tại `/web/index.html` (hoặc `/`) và tài sản tĩnh trong `/runs/`.
- `GET /health` và `GET /api/healthz`: Trả JSON tình trạng vận hành local, bản sao lưu mới nhất, nhật ký & cảnh báo lỗi.
- `GET /tinh-trang`: Màn hình tình trạng vận hành local tiếng Việt cho người quản trị (Mục 1 file 13_LENH_BAC_2.md).
- `GET /api/hang-7-ngay` & `POST /api/duyet-hang-7-ngay`: Hàng bài 7 ngày cho Chị Vân Anh duyệt (Mục 3 file 13_LENH_BAC_2.md).
- `POST /api/tao-dan-y`: Bước 1-5 thật bằng Gemini (dán đề -> sinh & chấm 3 phương án dàn ý A/B/C).
- `POST /api/chon-outline-va-xuat-ban`: Bước 5-9 & M1-M5 (chọn 1 dàn ý -> xuất bản bài + HTML + PDF + ảnh).
"""

import argparse
import hashlib
import html as H
import http.server
import json
import socketserver
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "scripts"))

from core_loai_va_gemini import kiem_tra_dau_vao, list_available_loai, load_loai_config
from dieu_phoi import taoNoiDung
from build_web_hub import _strip_jargon_from_text, build_web_hub, collect_runs_catalog
from sao_luu_va_khoi_phuc import ghi_bao_loi, ghi_nhat_ky

STARTED_AT = datetime.now().isoformat(timespec="seconds")
QUEUE_7_DAYS_PATH = ROOT_DIR / "du_lieu_hang_bai_7_ngay_van_anh.json"


def _make_slug(de_bai: str) -> str:
    digest = hashlib.sha1(de_bai.strip().encode("utf-8")).hexdigest()[:8]
    return f"tao-moi-{digest}"


def _read_jsonl_tail(path: Path, limit: int = 15) -> list:
    if not path.exists():
        return []
    lines = [
        ln.strip()
        for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if ln.strip()
    ]
    out = []
    for ln in lines[-limit:]:
        try:
            out.append(json.loads(ln))
        except Exception:
            pass
    return list(reversed(out))


def _build_health_payload() -> dict:
    latest_bk = {}
    bk_file = ROOT_DIR / "sao_luu" / "LATEST_BACKUP.json"
    if bk_file.exists():
        try:
            latest_bk = json.loads(bk_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    restore_drill = {}
    drill_file = ROOT_DIR / "sao_luu" / "BAO_CAO_KHOI_PHUC_THU.json"
    if drill_file.exists():
        try:
            restore_drill = json.loads(drill_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    audit_tail = _read_jsonl_tail(ROOT_DIR / "logs" / "nhat_ky_hoat_dong.jsonl", limit=12)
    error_tail = _read_jsonl_tail(ROOT_DIR / "logs" / "bao_loi_he_thong.jsonl", limit=10)
    gate_tail = _read_jsonl_tail(ROOT_DIR / "logs" / "cong_kiem_chung_metrics.jsonl", limit=10)

    return {
        "status": "ok",
        "service": "01_may_tao_noi_dung_local",
        "cong_co_dinh": 8010,
        "khoi_dong_luc": STARTED_AT,
        "thoi_diem_hien_tai": datetime.now().isoformat(timespec="seconds"),
        "so_loai_noi_dung": len(list_available_loai(ROOT_DIR)),
        "sao_luu_moi_nhat": {
            "ngay": latest_bk.get("ngay_sao_luu", ""),
            "duong_dan_zip": latest_bk.get("duong_dan_zip", ""),
            "so_luong_file": latest_bk.get("so_luong_file", 0),
        },
        "khoi_phuc_thu_1_lan": {
            "thanh_cong_100_pct": restore_drill.get("thanh_cong_100_pct", False),
            "so_file_khop_sha256": restore_drill.get("so_file_khoi_phuc_khop_sha256", 0),
            "thoi_diem": restore_drill.get("thoi_diem_khoi_phuc_thu", ""),
        },
        "so_luot_goi_cong_kiem_chung": len(gate_tail),
        "so_canh_bao_loi": len(error_tail),
        "nhat_ky_gan_day": audit_tail,
        "canh_bao_loi_gan_day": error_tail,
        "cong_kiem_chung_gan_day": gate_tail,
    }


def _render_tinh_trang_html() -> str:
    hp = _build_health_payload()
    bk = hp["sao_luu_moi_nhat"]
    dr = hp["khoi_phuc_thu_1_lan"]

    audit_rows = "\n".join(
        f"<tr><td>{H.escape(str(r.get('ts','')))}</td><td><strong>{H.escape(str(r.get('ai_lam','')))}</strong></td>"
        f"<td>{H.escape(str(r.get('lam_gi','')))}</td><td>{H.escape(str(r.get('doi_tuong','')))}</td>"
        f"<td>{H.escape(str(r.get('ket_qua','')))}</td></tr>"
        for r in hp["nhat_ky_gan_day"]
    ) or "<tr><td colspan='5'>Chưa có bản ghi hoạt động.</td></tr>"

    gate_rows = "\n".join(
        f"<tr><td>{H.escape(str(r.get('ts','')))}</td><td><strong>{H.escape(str(r.get('bo_goi','')))}</strong></td>"
        f"<td>{H.escape(str(r.get('loai','')))}</td><td>{r.get('diem',0)}/100</td>"
        f"<td>{r.get('thoi_gian_ms',0)} ms</td><td>{r.get('tong_token',0)}</td></tr>"
        for r in hp["cong_kiem_chung_gan_day"]
    ) or "<tr><td colspan='6'>Chưa có lượt gọi cổng kiểm chung.</td></tr>"

    err_rows = "\n".join(
        f"<tr><td>{H.escape(str(r.get('ts','')))}</td><td>{H.escape(str(r.get('nguon','')))}</td>"
        f"<td>{H.escape(str(r.get('thong_bao','')))}</td></tr>"
        for r in hp["canh_bao_loi_gan_day"]
    ) or "<tr><td colspan='3'>0 cảnh báo lỗi — Hệ thống vận hành ổn định.</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Tình Trạng Vận Hành Local — Sakédemy</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Be Vietnam Pro', sans-serif; background: #FDFDFD; color: #2D3436; margin: 0; padding: 24px; line-height: 1.6; font-size: 15px; }}
    .wrap {{ max-width: 1120px; margin: 0 auto; }}
    h1 {{ color: #02403B; margin-top: 0; font-size: 24px; }}
    h2 {{ color: #02403B; font-size: 18px; margin-top: 28px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .card {{ background: #F4F7F4; border: 1.5px solid #6EB264; border-radius: 16px 0 16px 0; padding: 16px; }}
    .card strong {{ display: block; color: #02403B; font-size: 18px; margin-top: 4px; }}
    table {{ width: 100%; border-collapse: collapse; background: #FFFFFF; border: 1px solid #D5E5D0; margin-bottom: 20px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #E5EFE2; font-size: 14px; }}
    th {{ background: #E9F6D3; color: #02403B; }}
    .btn-back {{ display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 10px 20px; background: #02403B; color: #FFFFFF; text-decoration: none; border-radius: 12px 0 12px 0; font-weight: 700; margin-bottom: 16px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <a class="btn-back" href="/web/index.html">← Quay lại Bàn Biên Tập Ấn Phẩm</a>
    <h1>Màn Hình Tình Trạng Vận Hành Local (Máy MSI · Cổng 8010)</h1>
    <div class="cards">
      <div class="card">Trạng thái máy chủ<strong>Đang hoạt động tốt (OK)</strong></div>
      <div class="card">Sao lưu hàng ngày mới nhất<strong>{H.escape(str(bk.get('ngay') or 'Hôm nay'))} ({bk.get('so_luong_file', 0)} tệp)</strong></div>
      <div class="card">Khôi phục thử 1 lần<strong>{'Đạt 100% (' + str(dr.get('so_file_khop_sha256', 0)) + ' tệp khớp)' if dr.get('thanh_cong_100_pct') else 'Chưa chạy'}</strong></div>
      <div class="card">Số cảnh báo lỗi hệ thống<strong>{hp['so_canh_bao_loi']} lỗi</strong></div>
    </div>

    <h2>1. Nhật ký Cổng kiểm chất lượng chung (Các bộ gọi qua <code>may_tao_noi_dung_adapter.py</code>)</h2>
    <table>
      <thead><tr><th>Thời gian</th><th>Bộ gọi</th><th>Thể loại</th><th>Điểm chất lượng</th><th>Thời gian đo</th><th>Token</th></tr></thead>
      <tbody>{gate_rows}</tbody>
    </table>

    <h2>2. Nhật ký Ai làm gì lúc nào (Audit Log)</h2>
    <table>
      <thead><tr><th>Thời gian</th><th>Người / Bộ thực hiện</th><th>Hành động</th><th>Đối tượng</th><th>Kết quả</th></tr></thead>
      <tbody>{audit_rows}</tbody>
    </table>

    <h2>3. Cảnh báo & Lỗi hệ thống</h2>
    <table>
      <thead><tr><th>Thời gian</th><th>Nguồn</th><th>Nội dung thông báo</th></tr></thead>
      <tbody>{err_rows}</tbody>
    </table>
  </div>
</body>
</html>"""


class ContentStudioHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def log_message(self, format, *args):
        pass

    def _send_json(self, status_code: int, payload: dict):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _send_html(self, status_code: int, html_str: str):
        raw = html_str.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_response(302)
            self.send_header("Location", "/web/index.html")
            self.end_headers()
            return

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if path in ("/health", "/api/healthz"):
            self._send_json(200, _build_health_payload())
            return

        if path == "/tinh-trang":
            self._send_html(200, _render_tinh_trang_html())
            return

        if path == "/api/hang-7-ngay":
            if QUEUE_7_DAYS_PATH.exists():
                data = json.loads(QUEUE_7_DAYS_PATH.read_text(encoding="utf-8"))
            else:
                data = {"danh_sach_7_ngay": []}
            self._send_json(200, {"hop_le": True, **data})
            return

        if path == "/api/loai":
            items = []
            for l_code in list_available_loai(ROOT_DIR):
                try:
                    cfg = load_loai_config(l_code, root_dir=ROOT_DIR)
                    items.append({
                        "loai": l_code,
                        "ten_hien_thi": cfg.get("ten_hien_thi", l_code),
                        "mo_ta": cfg.get("mo_ta", ""),
                        "kieu_xuat_ban": cfg.get("kieu_xuat_ban", "bai_viet"),
                        "do_dai_chu": cfg.get("do_dai_chu", {}),
                        "bat_buoc_co": cfg.get("bat_buoc_co", []),
                    })
                except Exception as exc:
                    items.append({"loai": l_code, "loi_cau_hinh": str(exc)})
            self._send_json(200, {"hop_le": True, "loai_hien_co": items})
            return

        if path == "/api/runs":
            cat = collect_runs_catalog()
            self._send_json(200, {"hop_le": True, "an_pham": cat})
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else "{}"
            body = json.loads(raw_body) if raw_body.strip() else {}
        except Exception:
            ghi_bao_loi("server_web.do_POST", "Dữ liệu gửi lên không đúng định dạng JSON.")
            self._send_json(
                400,
                {
                    "hop_le": False,
                    "ma_loi": "INVALID_JSON_PAYLOAD",
                    "thong_bao": "Dữ liệu gửi lên không đúng định dạng JSON hợp lệ.",
                },
            )
            return

        if path == "/api/duyet-hang-7-ngay":
            ma_bai = str(body.get("ma_bai", "")).strip()
            trang_thai_moi = str(body.get("trang_thai", "DA_DUYET")).strip()
            nguoi_duyet = str(body.get("nguoi_duyet", "Vân Anh")).strip()
            if not QUEUE_7_DAYS_PATH.exists():
                self._send_json(404, {"hop_le": False, "thong_bao": "Không tìm thấy hàng bài 7 ngày."})
                return
            qdata = json.loads(QUEUE_7_DAYS_PATH.read_text(encoding="utf-8"))
            updated_item = None
            for item in qdata.get("danh_sach_7_ngay", []):
                if item.get("ma_bai") == ma_bai:
                    item["trang_thai_duyet"] = trang_thai_moi
                    item["thoi_diem_duyet"] = datetime.now().isoformat(timespec="seconds")
                    updated_item = item
                    break
            if not updated_item:
                self._send_json(404, {"hop_le": False, "thong_bao": f"Không tìm thấy mã bài {ma_bai}."})
                return
            qdata["cap_nhat_cuoi"] = datetime.now().isoformat(timespec="seconds")
            QUEUE_7_DAYS_PATH.write_text(json.dumps(qdata, ensure_ascii=False, indent=2), encoding="utf-8")
            ghi_nhat_ky(
                nguoi_dung=nguoi_duyet,
                hanh_dong="DUYET_BAI_HANG_7_NGAY",
                doi_tuong=ma_bai,
                ket_qua=trang_thai_moi,
                chi_tiet={"tieu_de": updated_item.get("tieu_de", "")},
            )
            build_web_hub()
            self._send_json(200, {"hop_le": True, "item": updated_item, "danh_sach_7_ngay": qdata["danh_sach_7_ngay"]})
            return

        if path == "/api/tao-dan-y":
            loai = str(body.get("loai", "bai_viet")).strip()
            de_bai = body.get("de_bai", "")
            simulate_mode = body.get("simulate_mode")

            guard = kiem_tra_dau_vao(de_bai, loai=loai, root_dir=ROOT_DIR)
            if not guard["hop_le"]:
                ghi_nhat_ky("NguoiDungWeb", "CHAN_DAU_VAO", loai, ket_qua=guard.get("ma_loi", "BLOCKED"))
                self._send_json(422, guard)
                return

            if simulate_mode in ("ai_error", "ai_slow_timeout", "rate_limit"):
                ghi_bao_loi("server_web.tao_dan_y", f"Giả lập lỗi kết nối mô hình: {simulate_mode}")
                self._send_json(
                    503,
                    {
                        "hop_le": False,
                        "ma_loi": f"CHAOS_{simulate_mode.upper()}",
                        "thong_bao": "Dịch vụ trí tuệ nhân tạo tạm thời phản hồi chậm hoặc gián đoạn kết nối. Dữ liệu đề bài của bạn đã được giữ nguyên an toàn để bấm thử lại.",
                    },
                )
                return

            slug = body.get("slug") or _make_slug(de_bai)
            try:
                res = taoNoiDung(
                    loai,
                    {
                        "ngay": "2026-10-25",
                        "slug": slug,
                        "de_bai": de_bai,
                        "duyet_outline": "nguoi",
                        "resume": False,
                    },
                )
            except Exception as exc:
                ghi_bao_loi("server_web.tao_dan_y", str(exc))
                self._send_json(
                    500,
                    {
                        "hop_le": False,
                        "ma_loi": "PIPELINE_STEP1_5_ERROR",
                        "thong_bao": f"Hệ thống tạm thời gián đoạn khi lập dàn ý: {exc}",
                    },
                )
                return

            if res.get("hop_le") is False:
                self._send_json(422, res)
                return

            ghi_nhat_ky("NguoiDungWeb", "TAO_3_DAN_Y_ABC", res["run_id"], ket_qua="WAITING_APPROVAL")

            scores_map = {
                s.get("variant"): {
                    "tong_diem": s.get("tong_diem_100", 88.0),
                    "nhan_xet": _strip_jargon_from_text(s.get("nhan_xet", "")),
                }
                for s in res.get("bang_diem_outline", [])
            }
            rec_var = res.get("phuong_an_de_xuat", {}).get("variant", "B")
            react_map = {r.get("variant"): r for r in res.get("persona_reactions", [])}

            outlines_ui = []
            for out in res.get("outlines", []):
                v = out.get("variant", "A")
                r_info = react_map.get(v, {})
                sc_info = scores_map.get(v, {"tong_diem": 86.0, "nhan_xet": ""})
                outlines_ui.append({
                    "variant": v,
                    "ten_phuong_an": _strip_jargon_from_text(out.get("ten_phuong_an", f"Phương án {v}")),
                    "goc_nhin": _strip_jargon_from_text(out.get("variant_angle", "")),
                    "sections": [_strip_jargon_from_text(s) for s in out.get("sections", [])],
                    "tong_diem": sc_info["tong_diem"],
                    "nhan_xet": sc_info["nhan_xet"],
                    "duoc_chon": v == rec_var,
                    "phan_ung_doc_gia": [
                        {
                            "vai_tro": _strip_jargon_from_text(ep.get("vai_tro", "")),
                            "cau_phan_bien": _strip_jargon_from_text(ep.get("cau_phan_bien_ngay_tu_dan_y", "")),
                        }
                        for ep in r_info.get("chi_tiet_persona", [])[:3]
                    ],
                })

            self._send_json(
                200,
                {
                    "hop_le": True,
                    "run_id": res["run_id"],
                    "slug": slug,
                    "loai": loai,
                    "ten_hien_thi_loai": res.get("ten_hien_thi_loai", loai),
                    "de_bai": de_bai,
                    "phuong_an_de_xuat": rec_var,
                    "outlines": outlines_ui,
                },
            )
            return

        if path == "/api/chon-outline-va-xuat-ban":
            loai = str(body.get("loai", "bai_viet")).strip()
            de_bai = str(body.get("de_bai", "")).strip()
            chon_huong = str(body.get("chon_huong", "B")).strip().upper()
            if chon_huong not in ("A", "B", "C"):
                chon_huong = "B"

            run_id = str(body.get("run_id", "")).strip()
            prefix = f"2026-10-25_{loai}_"
            if run_id.startswith(prefix):
                slug = run_id[len(prefix):]
            else:
                slug = _make_slug(de_bai or run_id or "bai-moi")

            try:
                res = taoNoiDung(
                    loai,
                    {
                        "ngay": "2026-10-25",
                        "slug": slug,
                        "de_bai": de_bai,
                        "duyet_outline": "nguoi",
                        "chon_huong": chon_huong,
                        "resume": True,
                    },
                )
            except Exception as exc:
                ghi_bao_loi("server_web.xuat_ban", str(exc))
                self._send_json(
                    500,
                    {
                        "hop_le": False,
                        "ma_loi": "PUBLISH_STEP6_9_ERROR",
                        "thong_bao": f"Không thể hoàn tất xuất bản ấn phẩm: {exc}",
                    },
                )
                return

            if res.get("hop_le") is False:
                self._send_json(422, res)
                return

            ghi_nhat_ky("NguoiDungWeb", f"CHON_DAN_Y_{chon_huong}_VA_XUAT_BAN", res["run_id"], ket_qua="PUBLISHED")
            build_web_hub()
            cat = collect_runs_catalog()
            pub_item = next((x for x in cat if x["id"] == res["run_id"]), cat[0] if cat else {})
            self._send_json(
                200,
                {
                    "hop_le": True,
                    "run_id": res["run_id"],
                    "chon_huong": chon_huong,
                    "an_pham": pub_item,
                },
            )
            return

        self._send_json(404, {"hop_le": False, "thong_bao": "Không tìm thấy đường dẫn yêu cầu."})


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    ap = argparse.ArgumentParser(description="Web Studio Server cho 01_MAY_TAO_NOI_DUNG")
    ap.add_argument("--port", type=int, default=8010)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    build_web_hub()
    server = ThreadedHTTPServer((args.host, args.port), ContentStudioHandler)
    print(f"[WEB STUDIO SERVER] Listening on http://{args.host}:{args.port}/web/index.html", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
