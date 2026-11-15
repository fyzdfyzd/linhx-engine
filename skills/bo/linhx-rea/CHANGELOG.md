# Changelog

## [0.2.0] - 2026-11-11

### R5 — Tinh chỉnh ngưỡng ảnh phẳng, `sua-sai.jsonl` riêng từng bộ không ghi đè & tích hợp luật DoP
- **Ngưỡng ảnh phẳng & lọc cửa sổ lặp (`scripts/anh_do.py`)**:
  - Tách hàm thuần `quyet_dinh_phang(chi_so: dict) -> (bool, ly_do)` phục vụ kiểm thử độc lập; bổ sung điều kiện loại trừ cảnh 3D có dải độ sâu rộng (`dai_raw_p95_p5 >= 5.20` với `ti_le_mang_phang < 0.75`, hoặc `dai_norm_p95_p5 >= 0.75` kèm `ti_le_mang_phang < 0.48`) khỏi nhánh `phang_chu`.
  - Bổ sung bộ lọc `_loc_bo_thanh_phan_cua_so` trong `do_dac_trung_phang`: loại các thành phần hình hộp/khung chữ nhật lặp đều theo lưới 2 chiều hoặc các thành phần tỉ lệ gần vuông xếp thành nhiều hàng song song khỏi `so_ky_tu_ngang` (khắc phục lỗi nhận nhầm hàng cửa sổ nhà ở `sony24-01_pavy.jpg` thành chữ poster).
- **Sổ lỗi `<dir_ra>/sua-sai.jsonl` ghi nối không ghi đè (`scripts/rea_core.py`)**:
  - Đổi `rea_core.py sua <dir_ra>` sang ghi riêng tại `<dir_ra>/sua-sai.jsonl`, ghi nối và khử trùng theo `(anh, truc, mo_ta)` (hoặc `ma_loi` với lỗi hệ thống), không bao giờ xoá mục cũ; `--kiem-lai` cập nhật `trang_thai` tại chỗ và giữ nguyên toàn bộ mục.
  - Tự động di chuyển các bản ghi từ `linhx-rea/sua-sai.jsonl` cũ (nếu còn) về đúng `<dir_ra>/sua-sai.jsonl` theo tên ảnh/`dir_ra` rồi xoá file cũ.
- **Tích hợp bộ 52 luật DoP (`references/luat-dop.md`)**:
  - Thêm `references/luat-dop.md` gồm 52 luật viết lại theo 6 trục (`anh-sang`, `ong-kinh`, `bo-cuc`, `may-di`, `mau`, `nhip`) kèm nhãn đo được bằng máy, đối chiếu 8 trục ShotBench với `tu-vung/anh.yaml` và bảng nguồn tham chiếu.
  - Cập nhật `viec-doc` (`VIEC-DOC.md`, `viec_doc.json`, mẫu `dap_an.json`), `ap` (giữ `luat_khop` trong `doc.json`, in mục `Luật DoP khớp` trong `doc.md`), `ve_nguoc.py` (thêm dòng `Rules applied:` vào `prompt.md`) và `skills/rea-anh/SKILL.md`.
- Mở rộng bộ kiểm thử lên **10 pytest** tự sinh không skip (`tests/test_phang_dai_sau.py`, `tests/test_sua_khong_de.py`).

## [0.1.0] - 2026-11-11

Phát hành đầu tiên của plugin `linhx-rea` (skill `rea-anh`), tích hợp trọn vẹn kết quả từ 4 vòng phát triển R1–R4:

### R1 — Khung plugin & máy đo định lượng nền tảng
- Khởi tạo cấu trúc plugin `.claude-plugin/plugin.json`, `skills/rea-anh/SKILL.md` (≤ 120 dòng), lý thuyết `references/khung-chung.md` (khung 2 tầng Đo + Đọc, mốc bằng chứng, 7 thành phần thị giác *The Visual Story* của Bruce Block) và schema `references/the-thu-phap.schema.json`.
- Xây dựng `scripts/anh_do.py`: đo 6 màu chủ đạo K-means trên không gian Lab (`ti_le` cộng bằng `1.0`), histogram 16 mức sáng & kiểu tông (`high-key`, `low-key`, `tuong-phan-cao`, `trung-tinh`), khớp bố cục (`mot_phan_ba`, `cheo`, `doi_xung`), độ sâu ONNX Depth Anything V2 (`da2s.onnx`) và OCR tuỳ chọn.

### R2 — Sửa chuẩn độ sâu, hút mắt đa kênh, vòng đọc có mốc & kiểm thử pytest
- Chuẩn hoá quy ước `inverse_depth_lon_la_gan`: phân 3 lớp độ sâu bằng K-means 1 chiều động (`k=3`), `lop.png` gần sáng nhất (`235`), giữa (`140`), xa tối nhất (`45`) kèm chú giải và trọng tâm `do_sau.vung_gan_tam`.
- Nâng cấp bản đồ hút mắt R2: kết hợp Spectral Residual đa kênh Lab + tương phản màu Achanta 2009 + độ bão hoà/đỏ nổi bật nhân center prior nhẹ, loại bỏ điểm trong lề 4% mép và chọn đỉnh NMS bán kính `0.15`; xuất `hut_mat.png`.
- Xây dựng từ vựng 17 trục `tu-vung/anh.yaml` và các lệnh `rea_core.py viec-doc` / `ap` / `sua` bảo toàn tuyệt đối số đo máy (`do.json` không bao giờ bị ghi đè, ý kiến trái chiều đưa vào `xung_dot`) kèm 5 pytest cơ sở.

### R3 — Đọc thật 15 ảnh, vẽ ngược, rút thẻ thủ pháp & hồ sơ tổng hợp
- Hoàn thành đọc thật 15 ảnh (12 shot MV + 3 poster/KV) vào `dap_an.json` kèm mốc toạ độ/vùng/hộp và ghi nhận lỗi thật `MAY-SAI:` vào `linhx-rea/sua-sai.jsonl`.
- Xây dựng `scripts/ve_nguoc.py`: xuất `khoi.png`, `khung.png` (mũi tên máy & người đọc) cạnh dài `1024` và `prompt.md` tái tạo đủ 7 mục song ngữ Anh – Việt.
- Xây dựng `rea_core.py the` (kiểm và rút thẻ vào `thu-phap/thu-phap.jsonl` + `README.md`) và `rea_core.py tom` (`scripts/anh_tom.py`: dựng `cau-truc.md`, `nhip.md`, `nguyen-lieu.md`, `ve-dep.md`, `ve-nguoc/README.md`, `tom.md` ≤ 40 dòng).

### R4 — Hút mắt có người/mặt (YuNet), bố cục ảnh phẳng, chi tiết `prompt.md` & kiểm lại sửa sai
- Tích hợp `cv2.FaceDetectorYN` (YuNet đa tỉ lệ, tìm model theo thứ tự `REA_YUNET` → `<cwd>/models/` → `~/.cache/rea-video/models/`): ước vùng thân (`3×` rộng, `4×` cao mặt xuống dưới), tách hàm trộn `tron_hut_mat_nguoi` cộng trọng số vùng mặt + vùng thân + landmark mắt/miệng vào saliency R2, ghi `do.json.nguoi` và vẽ hộp mặt trên `do.png`.
- Tự động nhận diện ảnh phẳng (`do_sau.phang`, `do_sau.ly_do_phang`): với ảnh phẳng, `ve_nguoc.py` thay `khoi.png` bằng bản khối bố cục lưới `24×N` (`chu` / `hinh` / `khoang_trong` 3 sắc xám + viền + chú giải), xuất `ve-nguoc/bo_cuc.json` và đưa tỉ lệ bố cục phẳng vào `prompt.md`.
- Nâng cấp `prompt.md`: kéo cụm danh từ cụ thể + toạ độ từ `ghi_chu` của các trục vào `Subject`, `Lighting`, `Material/Texture`, `Style` (dịch sang tiếng Anh cho phần English, giữ chi tiết ở tóm tắt tiếng Việt, rút gọn ≤ 25 từ/trục không cắt `"..."`, lọc bỏ nhận xét lỗi máy `MAY-SAI:` nhưng giữ vật thể thật).
- Bổ sung `rea_core.py sua --kiem-lai` tự động đối chiếu lại 25 mục `sua-sai.jsonl` với `do.json` mới và mở rộng bộ kiểm thử lên 8 pytest tự sinh không skip.

### Model (không nằm trong kho)
- Depth Anything V2 Small `da2s.onnx`: biến `REA_DEPTH`, hoặc `models/` ở cwd, hoặc `~/.cache/linhx-rea/models/`.
- YuNet `face_detection_yunet_2023mar.onnx`: biến `REA_YUNET`, `models/` ở cwd, `~/.cache/rea-video/models/`, `~/.cache/linhx-rea/models/`. Thiếu YuNet thì bỏ qua bước nhận mặt.
