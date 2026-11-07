# Hợp đồng nghiệm thu LINHX ENGINE đợt 1

Thư mục này là bộ nghiệm thu hộp đen, viết TRƯỚC khi làm. Thợ không sửa file nào ở đây và không sửa `features-dot1.json.khoa`.
Mọi đường dẫn dưới đây tính từ `linhx-engine/`. Chạy: `python -m pytest tests/nghiem-thu/test_<id>.py -q` (cwd = linhx-engine).
Test không gọi mạng thật, không gọi SePay thật. Phần cần VM thật được kiểm qua file bằng chứng trong `bang-chung/<ID>/`,
ghi từ lần chạy thật trên VM `linhx-engine-1`; người canh đối chiếu lại trên VM trước khi chấm DAT.

| ID | Thợ phải tạo | Bằng chứng |
|---|---|---|
| N1 | workflow `.github/workflows/linhx-engine.yml` (gốc repo) chạy trên push `tu-dong/*`, chạy `cong_kiem` hoặc `tests/nghiem-thu` của linhx-engine | `bang-chung/N1/ci.json` `{url, nhanh, ket_qua:"success"}` |
| N2 | `nguon/03-opc-os/`, `nguon/01-may-noi-dung/` (README.md + module.py gốc), `nguon/NGUON.md` (đường gốc + ngày YYYY-MM-DD). Không .env, khoá, .db/.xlsx/.sql, dữ liệu khách; < 50 MB; code trong apps/ không import nguon | – |
| N3 | app `apps/linhx_core/` (pyproject.toml, linhx_core/{__init__.py có __version__, hooks.py app_name, modules.txt có crm, pay}); DocType Single `LX Cau Hinh` có Check `bat_crm`, `bat_pay`; `linhx_core/co_module.py` thuần Python: `module_bat(ten, cau_hinh)`, `doctype_bi_an(doctype, cau_hinh)`; hooks nối co_module vào has_permission/permission_query_conditions | `bang-chung/N3/install-app.log` |
| N4 | `cli/linhx_cli` (`python -m linhx_cli tao-site <ten> --cau-hinh f.json --sites-dir D --chay-thu` in JSON `{"lenh":[...]}`, không chạy gì); site có sẵn thì không new-site/drop/reinstall/restore | `bang-chung/N4/tao-site.json` `{site, giay ≤ 600, lan_hai:{giay, ma_thoat:0, site_cu_ping:200}}` |
| N5 | `deploy/sites/linhx.json`, `deploy/sites/ifagent.json` `{"modules":{...}}` | `bang-chung/N5/ping.json` `{luc, may:"linhx-engine-1", sites:[{ten,url .../api/method/ping,status:200,db_name}]}` |
| N6 | `deploy/sao-luu.sh` (bench backup từng site), lịch hằng ngày trong deploy/ gọi nó; DocType `LX Nhat Ky Truy Cap`; không file .sql/.sql.gz/.tar.gz trong repo | `bang-chung/N6/sao-luu.json` `{luc_kiem, sites:[{ten,file,luc}], khoi_phuc_thu:{site_tam,tu_file,ping:200}}` |
| A1 | DocType module crm: `LX Don Vi`, `LX To Chuc`, `LX Nguoi` (dien_thoai, email, zalo, don_vi Link LX Don Vi); `linhx_core/crm/gop_trung.py`: `khoa_gop(nguoi)->set`, `gop(ds, moi)->list` (gộp theo SĐT chuẩn hoá 84…, email thường hoá, zalo; giữ trường cũ, bù trường trống); ghi `nguon/03-opc-os/<file có thật>`; `lx_nguoi.py` gọi gop_trung | – |
| B1 | DocType module pay: `LX Goi` (gia_san Currency), `LX Gia`, `LX Quyen Dung`; `linhx_core/pay/quyen_dung.py`: `gia_hop_le(so_tien, goi)`, `cap_quyen(don, goi)` (chỉ khi `trang_thai=="da_tra"` và đủ giá sàn); ghi `nguon/03-opc-os/<file có thật>` | – |
| C1 | `trang-bu/` Next.js, `npm run build` xuất tĩnh ra `trang-bu/out/`, đọc nội dung lúc dựng từ `NOI_DUNG_URL` (JSON `{tieu_de, mo_ta, muc:[{ten, mo_ta}]}`), thiếu thì `noi-dung.mau.json`; `npm ci` sẵn; trang không gọi ra ngoài (font tự host); 390 và 1280 không tràn ngang | – |

Module thuần Python (co_module, gop_trung, quyen_dung) không `import frappe` ở đầu file; phần nối Frappe để ở controller/hooks.
Các feature còn lại (A2–A5, B2–B5, C2–C3, D1–D3, E1–E2, T1–T2) viết nghiệm thu sau, chưa giao phiếu.
