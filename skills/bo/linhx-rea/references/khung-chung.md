# Khung chung họ skill `linhx-rea`

Họ skill `linhx-rea` phục vụ phân tích ngược (Reverse Engineering Aesthetics & Structure) cho 5 loại tác phẩm: **video, sách, báo cáo, bài viết, ảnh**. Mọi skill con dùng chung kiến trúc 2 tầng, chu trình đọc kiểm soát, quy ước mốc bằng chứng và cấu trúc thư mục đầu ra dưới đây.

---

## 1. Kiến trúc 2 tầng

1. **Tầng 1 — Máy đo định lượng (`*_do.py`)**:
   - Chạy thuật toán xác định (deterministic) và mô hình cục bộ để đo các đại lượng khách quan (màu sắc, độ sáng, điểm hút mắt, bố cục hình học, độ sâu không gian, chữ OCR, nhịp cắt, độ dài câu/đoạn...).
   - Xuất kết quả máy đọc được (`do.json`) và bản trực quan (`do.png`).
   - **Nguyên tắc bất biến**: số đo ở `do.json` là bằng chứng nền, tầng đọc của agent không bao giờ ghi đè hay xoá trường trong `do.json`.
2. **Tầng 2 — Agent đọc theo từ vựng đóng, có mốc**:
   - Agent đa phương thức quan sát tư liệu gốc cùng `do.png`, trả lời bộ câu hỏi cố định trong `tu-vung/<loai>.yaml`.
   - Mỗi trục chỉ nhận nhãn trong danh sách đóng `gia_tri` để tránh văn phong tán dương mơ hồ, đồng thời buộc gắn **mốc vị trí (`moc`)** cho mọi nhận xét cục bộ.

---

## 2. Quy ước mốc (`moc`) theo loại đầu vào

Mọi nhận định gắn với chi tiết cụ thể phải chỉ được vị trí kiểm chứng:

| Loại | Định dạng mốc chuẩn | Ví dụ |
|---|---|---|
| **Ảnh (`rea-anh`)** | Toạ độ chuẩn hoá `[x, y]` hoặc vùng `[x1, y1, x2, y2]` với `x, y ∈ [0, 1]` (gốc `(0, 0)` trên-trái, `(1, 1)` dưới-phải), **hoặc** tên ô lưới 3×3 `A1..C3` | `[0.34, 0.36]`, `[0.15, 0.20, 0.55, 0.80]`, `"B2"`, `["A2", "B2"]` |
| **Video (`rea-video`)** | Khoảng thời gian `t0..t1` (giây) kèm mã `shot` | `"shot_012@14.20-16.80s"` |
| **Sách (`rea-sach`)** | Mã chương, trang, đoạn | `"ch03:p42:d2"` |
| **Báo cáo (`rea-bao-cao`)** | Mục, trang, bảng/hình | `"muc2.1:p08:hinh3"` |
| **Bài viết (`rea-bai`)** | Đoạn `P1..Pn` và câu `S1..Sm` | `"P4:S2"` |

### Sơ đồ ô lưới 3×3 của ảnh (`A1..C3`)

Chia khung ảnh thành 3 hàng (`A` trên, `B` giữa, `C` dưới) × 3 cột (`1` trái, `2` giữa, `3` phải):

| Hàng \ Cột | `1` (`x: 0.00..0.33`) | `2` (`x: 0.33..0.67`) | `3` (`x: 0.67..1.00`) |
|---|---|---|---|
| **`A`** (`y: 0.00..0.33`) | `A1` (trên-trái) | `A2` (trên-giữa) | `A3` (trên-phải) |
| **`B`** (`y: 0.33..0.67`) | `B1` (giữa-trái) | `B2` (tâm ảnh) | `B3` (giữa-phải) |
| **`C`** (`y: 0.67..1.00`) | `C1` (dưới-trái) | `C2` (dưới-giữa) | `C3` (dưới-phải) |

---

## 3. Vòng `viec-doc` → `dap_an.json` → `ap`

Thiết kế tương tự chu trình review hai pha của `rea-video`, viết gọn cho mọi loại đầu vào trong `scripts/rea_core.py`:

1. **`rea_core.py viec-doc <dir_ra> --tu-vung <yaml>`**:
   - Quét các `do.json` trong `<dir_ra>`, kết hợp với file từ vựng `<yaml>` để sinh `<anh>/viec_doc.json` (danh sách trục câu hỏi + `goi_y_do` từ số đo), mẫu `<anh>/dap_an.json` (`"trang_thai": "chua_dien"` nếu chưa có) và trang tổng hợp `<dir_ra>/VIEC-DOC.md`.
2. **Agent điền `<anh>/dap_an.json`**:
   - Xem tư liệu gốc + hình đo (`do.png`, `hut_mat.png`), điền nhãn hợp lệ, `moc` (`{"x","y"}`, `{"vung"}`, `{"hop"}`), `ghi_chu` và `the_de_xuat`.
3. **`rea_core.py ap <dir_ra>`**:
   - Kiểm tra từng câu trả lời: trục `can_moc: true` thiếu mốc sẽ báo lỗi trực tiếp trục đó; nhãn ngoài danh sách ghi vào `canh_bao` nhưng vẫn giữ.
   - Hợp nhất phần đọc vào `<anh>/doc.json` và `<anh>/doc.md` trong khi giữ nguyên vẹn `do.json` (mọi khoá trùng số đo hoặc `duong_dan_mat` lệch vùng `hut_mat` ghi vào `xung_dot`).

---

## 4. Lệnh `tom` và vòng khép kín `sua → test`

- **`rea_core.py tom <dir_ra>`**: dựng trọn bộ hồ sơ tổng hợp (`cau-truc.md`, `nhip.md`, `nguyen-lieu.md`, `ve-dep.md`, `thu-phap/`, `ve-nguoc/README.md`) kèm trang đầu vào siêu gọn `<dir_ra>/tom.md` (**≤ 40 dòng**) có mục **Máy sai cần sửa** đếm lỗi theo nhóm để agent nắm toàn cục mà không tốn ngữ cảnh.
- **Quy trình `sua → test` (biến điểm máy đo sai thành kiểm thử hồi quy)**:
  1. **Phát hiện khi đọc (`MAY-SAI:`)**: trong lúc xem ảnh điền `dap_an.json`, nếu số đo máy lệch thực tế thị giác (hút mắt bỏ sót người/chủ thể chính, bản đồ độ sâu `lop.png` bị lừa bởi mảng sáng tối hoặc mặt phẳng 2D, khớp bố cục sai...), người đọc mở đầu `ghi_chu` bằng tiền tố `"MAY-SAI: ..."`.
  2. **Thu gom tự động (`rea_core.py sua <dir_ra>`)**: quét toàn bộ `dap_an.json`, trích các ghi chú `"MAY-SAI:"` vào `linhx-rea/sua-sai.jsonl` với cấu trúc `{anh, truc, loai_loi, mo_ta, trang_thai: "mo"}` (chống trùng theo `(anh, truc)`; cũng hỗ trợ `--mo-ta "..."` cho ca lỗi lẻ).
  3. **Chuyển hoá thành `pytest` bằng ảnh tự sinh**: với nhóm lỗi lặp lại nhiều lần ở trạng thái `"mo"`, lập trình viên cập nhật thuật toán đo trong `scripts/*_do.py`, đồng thời viết kiểm thử hồi quy dùng **ảnh tự sinh xác định (`numpy`/`cv2` trong `tmp_path`, không phụ thuộc ảnh thật hay mạng)** vào `linhx-rea/tests/` (ví dụ 2 lỗi R1→R2 đã gộp assert vào R3: độ sâu k-means 1D phụ thuộc ảnh với lớp gần sáng nhất, và hút mắt đa kênh ưu tiên điểm đỏ nổi bật + loại lề 4%). Sau khi `pytest` xanh, đổi bản ghi tương ứng sang `"trang_thai": "da_sua"`.

---

## 5. Cấu trúc thư mục đầu ra chung (`<dir_ra>/`)

Mọi skill trong họ `linhx-rea` hướng về cùng một cấu trúc đầu ra chuẩn:

```text
<dir_ra>/
├── cau-truc.md       # Bố cục, phân lớp không gian 3 lớp, chủ thể chính/phụ từng đơn vị
├── nhip.md           # Diễn tiến tông, độ sáng, màu chủ đạo theo thứ tự shot + chuyển biến
├── nguyen-lieu.md    # Đạo cụ, chất liệu bề mặt, thiết lập đèn, bảng 6 màu định lượng
├── ve-dep.md         # Ma trận tương phản / tương đồng 7 thành phần Bruce Block tổng hợp
├── thu-phap/         # thu-phap.jsonl (thẻ đạt schema), README.md (bảng tra nhanh), the-loi.jsonl (nếu có)
├── ve-nguoc/         # README.md chỉ mục trỏ tới <don-vi-con>/ve-nguoc/{khoi.png, khung.png, prompt.md}
├── tom.md            # Tóm tắt toàn cục ≤40 dòng + thống kê "Máy sai cần sửa"
└── <don-vi-con>/     # Thư mục từng ảnh: do.json, do.png, hut_mat.png, depth.png, lop.png,
                      #                   viec_doc.json, dap_an.json, doc.json, doc.md, ve-nguoc/
```

---

## 6. Cơ sở lý thuyết cho `rea-anh`

- **Kiểu tông sáng (`tong.kieu`)**: phân loại từ phân bố độ sáng chuẩn hoá `[0, 1]` thành 4 nhóm: `high-key` (sáng chủ đạo), `low-key` (tối chủ đạo), `tuong-phan-cao` (cực sáng và cực tối cùng mạnh, độ lệch chuẩn cao), `trung-tinh` (cân bằng vùng trung gian).
- **Điểm hút mắt & khớp bố cục**: bản đồ nổi bật là trung bình chuẩn hoá của (a) *Spectral Residual* (Hou & Zhang, CVPR 2007) trên từng kênh CIE Lab, (b) tương phản màu kiểu Achanta 2009 (`||Lab_tb - Lab_Gauss||`), (c) độ bão hoà & đỏ nổi bật, nhân center prior nhẹ (Gauss `sigma = 0.35`, trọng số `0.3`); loại lề `4%` mép và trích tối đa 3 cực đại bằng NMS bán kính `0.15` để chấm mức khớp `mot_phan_ba`, `cheo`, `doi_xung`.
- **3 lớp không gian (`do_sau`)**: suy luận từ *Depth Anything V2 Small* (`models/da2s.onnx`) xuất *inverse depth* (giá trị **LỚN = GẦN**, chuẩn hoá `0..1`), tách thành tiền cảnh (`gan` — sáng nhất trong `lop.png`), trung cảnh (`giua`), hậu cảnh (`xa` — tối nhất) bằng k-means 1 chiều (`cv2.kmeans` `k=3`), kèm trọng tâm lớp gần `vung_gan_tam`.
- **7 thành phần thị giác của Bruce Block (*The Visual Story*)**: `khong_gian` (sâu/phẳng), `duong_net`, `hinh_khoi`, `sac_do`, `mau`, `chuyen_dong` (hướng động thị giác), `nhip`. Mỗi thành phần được đánh giá theo nguyên lý **Tương phản (`tuong_phan`)** — tạo kịch tính, va đập thị giác — hoặc **Tương đồng (`tuong_dong`)** — tạo sự hài hoà, tĩnh tại.
