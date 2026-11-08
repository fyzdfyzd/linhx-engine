# Hợp đồng nghiệm thu LINHX ENGINE đợt 1 và 1b

Thư mục này là bộ nghiệm thu hộp đen, viết TRƯỚC khi làm. Thợ không sửa file nào ở đây và không sửa `features-dot1*.json.khoa`.
Repo riêng `fyzdfyzd/linhx-engine`: mọi đường dẫn dưới đây tính từ gốc repo. Chạy: `python -m pytest tests/nghiem-thu/test_<id>.py -q` (cwd = gốc repo).
Test không gọi mạng thật, không gọi SePay thật. Phần cần VM thật được kiểm qua file bằng chứng trong `bang-chung/<ID>/`,
ghi từ lần chạy thật trên VM `linhx-engine-1`; người canh đối chiếu lại trên VM trước khi chấm DAT.

| ID | Thợ phải tạo | Bằng chứng |
|---|---|---|
| N1 | workflow `.github/workflows/linhx-engine.yml` chạy trên push `tu-dong/*`, chạy `canh/cong_kiem.py` hoặc `tests/nghiem-thu` | `bang-chung/N1/ci.json` `{url, nhanh, ket_qua:"success"}` |
| N2 | `nguon/03-opc-os/`, `nguon/01-may-noi-dung/` (README.md + module.py gốc), `nguon/NGUON.md` (đường gốc + ngày YYYY-MM-DD). Không .env, khoá, .db/.xlsx/.sql, dữ liệu khách; < 50 MB; code trong apps/ không import nguon | – |
| N3 | app `apps/linhx_core/` (pyproject.toml, linhx_core/{__init__.py có __version__, hooks.py app_name, modules.txt có crm, pay}); DocType Single `LX Cau Hinh` có Check `bat_crm`, `bat_pay`; `linhx_core/co_module.py` thuần Python: `module_bat(ten, cau_hinh)`, `doctype_bi_an(doctype, cau_hinh)`; hooks nối co_module vào has_permission/permission_query_conditions | `bang-chung/N3/install-app.log` |
| N3 (bổ sung 8/11, Linh duyệt) | Cài và kiểm trên **Frappe bench WSL máy cty** (`canh/bench.ps1 gan -Tho <N>` chép app từ worktree vào ~/frappe-bench rồi install-app, migrate; `canh/bench.ps1 chay -- <lệnh>`; `canh/bench.ps1 serve` mở http://localhost:8000). KHÔNG cài vào container 0.1 trên linhx-engine-1. Chỉ dùng hook chính thống (`has_permission`, `permission_query_conditions` theo DocType, `doc_events`, `before_request`); không vá runtime frappe, không sửa lõi Frappe. Administrator được miễn chặn (Frappe vốn bỏ qua quyền với Administrator). Thiếu hoặc lỗi cờ thì coi là tắt. Không để hàm kiểm thử hay hàm xoá cấu hình trong code app | `bang-chung/N3/install-app.log` từ `bench.ps1` (có thời điểm, mã thoát) + `bang-chung/N3/an-api.log`: HTTP thật với user thường `kiem@test.local` trên site test của bench WSL, gọi `GET /api/resource/LX Nguoi` và `/api/method/frappe.client.get_list` khi cờ tắt và bật, ghi status code |
| N4 | `cli/linhx_cli` (`python -m linhx_cli tao-site <ten> --cau-hinh f.json --sites-dir D --chay-thu` in JSON `{"lenh":[...]}`, không chạy gì); site có sẵn thì không new-site/drop/reinstall/restore | `bang-chung/N4/tao-site.json` `{site, giay ≤ 600, lan_hai:{giay, ma_thoat:0, site_cu_ping:200}}` |
| N5 | `deploy/sites/linhx.json`, `deploy/sites/ifagent.json` `{"modules":{...}}` | `bang-chung/N5/ping.json` `{luc, may:"linhx-engine-1", sites:[{ten,url .../api/method/ping,status:200,db_name}]}` |
| N6 | `deploy/sao-luu.sh` (bench backup từng site), lịch hằng ngày trong deploy/ gọi nó; DocType `LX Nhat Ky Truy Cap`; không file .sql/.sql.gz/.tar.gz trong repo | `bang-chung/N6/sao-luu.json` `{luc_kiem, sites:[{ten,file,luc}], khoi_phuc_thu:{site_tam,tu_file,ping:200}}` |
| A1 | DocType module crm: `LX Don Vi`, `LX To Chuc`, `LX Nguoi` (dien_thoai, email, zalo, don_vi Link LX Don Vi); `linhx_core/crm/gop_trung.py`: `khoa_gop(nguoi)->set`, `gop(ds, moi)->list` (gộp theo SĐT chuẩn hoá 84…, email thường hoá, zalo; giữ trường cũ, bù trường trống); ghi `nguon/03-opc-os/<file có thật>`; `lx_nguoi.py` gọi gop_trung | – |
| B1 | DocType module pay: `LX Goi` (gia_san Currency), `LX Gia`, `LX Quyen Dung`; `linhx_core/pay/quyen_dung.py`: `gia_hop_le(so_tien, goi)`, `cap_quyen(don, goi)` (chỉ khi `trang_thai=="da_tra"` và đủ giá sàn); ghi `nguon/03-opc-os/<file có thật>` | – |
| C1 | `trang-bu/` Next.js, `npm run build` xuất tĩnh ra `trang-bu/out/`, đọc nội dung lúc dựng từ `NOI_DUNG_URL` (JSON `{tieu_de, mo_ta, muc:[{ten, mo_ta}]}`), thiếu thì `noi-dung.mau.json`; `npm ci` sẵn; trang không gọi ra ngoài (font tự host); 390 và 1280 không tràn ngang | – |

Module thuần Python (co_module, gop_trung, quyen_dung) không `import frappe` ở đầu file; phần nối Frappe để ở controller/hooks.
| C3 | (nghiệm thu viết sau) khuôn `trang-bu` phải dựng được theo `SITE_JSON=<sites/ten/site.json>` (nội dung ở khoá `noi_dung`, NOI_DUNG_URL vẫn ưu tiên); ifagent đặt ở `sites/ifagent/site.json`. C4 dựa vào đây | – |

## Đợt 1b (`features-dot1b.json`)

| ID | Thợ phải tạo | Bằng chứng |
|---|---|---|
| W1 | `apps/linhx_worker/linhx_worker/bang_tho.py` thuần Python: `COT`, `doc_phieu(p)`, `tong_hop(ds, dang_chay)`; nguồn là `.canh/phieu.tsv`, `.canh/dang-chay.json` do bộ điều phối ghi; `api.py` thêm `bang_tho` (chỉ điều hành); `front/index.html` #/engine vẽ `#bang-tho`, `#cham-tran` | ảnh `.canh-tho/anh/w1-*.png` lúc kiểm |
| Q1 | `pay/ban_bao_cao.py` (`goi_cong_khai`, `so_tien_don`), `pay/api_ban.py` (`goi`, `tao_don` allow_guest, gọi B2); `front/index.html` #/ có `[data-goi]`, `[data-tra-qr]`, `img[data-qr]`; không gửi giá từ client, không viết cứng giá | ảnh `.canh-tho/anh/q1-*.png` |
| C4 | chỉ `sites/unikon/site.json` (+ ảnh); dựng bằng `SITE_JSON`; commit `C4:` không đụng khuôn | ảnh `.canh-tho/anh/c4-*.png` |
| R1 | `apps/linhx_core/linhx_core/cts_adapter/hop_dong.py`: `tao_don(payload, danh_muc, kho)`, `nhan_webhook(payload, kho, authorization, khoa)` trả `(ma_http, than)` cùng dạng CTS; `cts_adapter/api.py` (`checkout`, `sepay_webhook`). 20 payload mẫu: `tests/nghiem-thu/du-lieu/cts/` | – |
| R2 | `cts_adapter/bong.py`: `bat`, `nhan_don_bong`, `nhan_bong`, `so_lech`; cờ `bat_bong` tắt mặc định; dùng lại luật `hop_dong`; không giao hàng | – |

Chi tiết từng hàm ghi ở đầu file `test_<id>.py`.

## Đợt 1 phần sau (viết 8/11, Linh duyệt "ok hết")

| ID | Thợ phải tạo (chi tiết ở đầu test_<id>.py) | Bằng chứng |
|---|---|---|
| A2 | DocType LX Quan He, LX Co Hoi (han_giao); `crm/co_hoi.py` `han_giao`, `giao`, `viec_cho`; lx_co_hoi.py gọi | – |
| A3 | DocType LX Dong Y (track_changes, chặn xoá); `crm/dong_y.py` `MUC_DICH`, `TuChoi`, `ghi`, `hieu_luc`, `kiem_chuyen_cheo` | – |
| A4 | `crm/quyen_don_vi.py` `co_quyen`, `dieu_kien`; hooks has_permission + permission_query_conditions cho LX Nguoi, LX Co Hoi | `bang-chung/A4/quyen.json` từ bench WSL |
| A5 | `crm/chuyen_lead.py` `goi_di`, `nhan`; `crm/api_lead.py` `nhan_lead` (không allow_guest), `gui_lead` | `bang-chung/A5/chuyen.json` từ VM |
| B2 | DocType LX Don; `pay/vietqr.py` `noi_dung_ck`, `qr_url`, `tao_don`; ghi nguồn PROTO | – |
| B3 | `pay/sepay.py` `xu_ly`; `pay/api_sepay.py` `webhook` (khoá từ site_config, for_update) | – |
| B4 | `pay/sau_tra.py` `viec_can_tao`, `link_bao_cao`; doc_events LX Don; LX Job thêm `don`, nguon "don" | – |
| B5 | DocType LX So S1a, Single LX Cau Hinh Pay; `pay/so_s1a.py`; `pay/api_thue.py` `canh_bao_thue`; ghi nguồn PROTO | – |
| C2 | `crm/form.py` `xu_ly`; `crm/api_form.py` `nhan_form` (allow_guest + giới hạn tần suất); trang-bu `form[data-lead]`, API_GOC lúc dựng | – |
| C3 | `sites/ifagent/site.json`; trang-bu đọc SITE_JSON; deploy/ phục vụ ifagent | `bang-chung/C3/chay.json` từ VM (URL là IP) |
| D1 | `sites/ifagent/kham.json`; trang `/kham` `[data-cau]`, `[data-tom-tat]`, chạy không mạng | – |
| D2 | `crm/t1.py` `ghi_ket_qua`; LX Nguoi thêm nguon, tang_pheu; `api_form.nhan_ket_qua_t1`; `form[data-nhan-ket-qua]`, `[data-ket-qua-day-du]` | – |
| D3 | `linhx_core/pheu.py` `TANG`, `dem`; `api_pheu.pheu`; #/engine `[data-tang]` | – |
| E1 | `linhx_core/ban.py` `tong_hop`; `api_ban_dieu_hanh.ban`; #/engine `#viec-cho`, `#lead-moi`, `#don-moi`, làm mới ≤ 60 giây | – |
| E2 | `linhx_worker/so_lieu.py` `phut`, `dong`; `bang` trả phut; bảng #viec cột Token vào, Token ra, Phút | – |
| T1 | `tests/e2e/test_hanh_trinh_lead.py` (URL, mật khẩu từ biến môi trường) | `bang-chung/T1/e2e.json` + `e2e.log` từ VM |
| T2 | `tests/e2e/test_don_bao_cao.py` (webhook giả lập, không gọi SePay thật) | `bang-chung/T2/e2e.json` + `e2e.log` từ VM |

Hàm dùng chung mới trong `_chung.py`: `dung_trang_bu`, `chan_ra_ngoai`, `trang_front_engine`, `ghi_nguon_proto`, `khong_import_frappe_dau_file`.

## Vùng (cổng K1)

Mỗi feature có trường `vung` (glob, `**` = nhiều cấp) trong `features-dot1*.json`. Người canh chạy `canh/rao.py`: file nào trong diff
của phiếu nằm ngoài `vung` thì CHUA_DAT máy, không cần đọc. Luôn được thêm: `bang-chung/<ID>/**` và hai trường `passes`, `bang_chung`
của chính feature đó. Luôn cấm: `tests/nghiem-thu/**`, `*.khoa`, `pytest.ini`, `canh/**`, `.canh/**`. Nhật ký agy (`.canh/log/<phieu>.jsonl`)
cũng được so: agy đã ghi file ngoài vùng rồi xoá trước commit vẫn tính là lỗi (K3).

## Kiểm thêm của canh (8/11, Linh duyệt "làm")

- K7 tích hợp bench: sau khi đạt hộp đen, B3, A4, C2 chạy thêm `tests/nghiem-thu/tich-hop/th_<id>.py` (HTTP thật trên site test của bench WSL, qua `canh/bench.ps1 th`). Trượt là CHUA_DAT. Hợp đồng thêm: B3 đọc khoá `sepay_khoa` trong site_config; A4 có vai trò `LX Nhan Vien` và đơn vị lấy từ User Permission.
- K8 đối chiếu VM: mỗi vòng tổng hợp, `canh/doi_chieu_vm.py` gọi lại URL trong bằng chứng N5, C3, T1, T2. Sai 2 lượt liền thì passes về false, thợ làm lại.
