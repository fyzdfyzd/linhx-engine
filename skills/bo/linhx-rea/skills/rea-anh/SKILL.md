---
name: rea-anh
description: Phân tích ngược ảnh tĩnh, keyframe và poster/KV theo 7 bước cố định (đo định lượng, tạo việc đọc, điền đáp án có mốc, áp đáp án, vẽ ngược, rút thẻ thủ pháp, tóm tắt).
---

# rea-anh — Quy trình phân tích ngược ảnh

Thực hiện tuần tự đúng 7 bước dưới đây từ thư mục gốc workspace. Không bỏ bước, không ghi đè số máy đo. Lý thuyết và quy ước mốc xem tại `../../references/khung-chung.md`.

## Quy trình chuẩn: `do → viec-doc → dap_an.json → ap → ve-nguoc → the → tom`

### Bước 1 — Đo định lượng (`do`)

```bash
python linhx-rea/scripts/anh_do.py <anh> -o <dir_ra>/<ten-khong-duoi>
```

Sinh tại `<dir_ra>/<ten-khong-duoi>`: `do.json` (6 màu k-means, tông, người/mặt YuNet + ước vùng thân, điểm hút mắt bỏ lề 4% trộn mặt/thân/landmark, khớp bố cục, 3 lớp độ sâu k-means 1D kèm `vung_gan_tam` + tự nhận ảnh phẳng `phang`/`ly_do_phang`, OCR), `do.png` (vẽ cả hộp mặt), `hut_mat.png`, `depth.png`, `lop.png` (gần = sáng 235, giữa = 140, xa = tối 45).

### Bước 2 — Sinh việc đọc (`viec-doc`)

```bash
python linhx-rea/scripts/rea_core.py viec-doc <dir_ra> --tu-vung linhx-rea/tu-vung/anh.yaml
```

Sinh `<anh>/viec_doc.json` (17 trục câu hỏi + `goi_y_do`), mẫu `<anh>/dap_an.json` (nếu chưa có) và `<dir_ra>/VIEC-DOC.md`.

### Bước 3 — Agent xem ảnh và điền `<anh>/dap_an.json`

1. Mở ảnh gốc cùng `<anh>/do.png`, `<anh>/hut_mat.png` và `<anh>/lop.png`.
2. Đổi `"trang_thai"` thành `"da_dien"`, điền `"nguoi_doc"`, chọn nhãn trong `../../tu-vung/anh.yaml` cho `"tra_loi"`.
3. Trục `can_moc: true` bắt buộc có `"moc"` (`{"x","y"}`, `{"vung":"B2"}` hoặc `{"hop":[x0,y0,x1,y1]}`). Chỗ máy đo sai thì bắt đầu `"ghi_chu"` bằng `"MAY-SAI: ..."`.
4. Đối chiếu `../../references/luat-dop.md`: gắn mã luật khớp vào đầu `"ghi_chu"` (`"[AS-03] ..."`) và điền khoá gốc `"luat_khop"` (`[{"ma","vi_sao","moc"}]`, ≥3 luật mỗi ảnh).
5. Đề xuất ≥1 thẻ trong `"the_de_xuat"` theo `../../references/the-thu-phap.schema.json`.

### Bước 4 — Áp đáp án (`ap`)

```bash
python linhx-rea/scripts/rea_core.py ap <dir_ra>
```

Kiểm mốc bắt buộc, giữ `"luat_khop"`, bảo toàn nguyên vẹn `do.json` (mọi khoá trùng số đo hoặc lệch `duong_dan_mat` ghi vào `xung_dot`), xuất `<anh>/doc.json` và `<anh>/doc.md` (có mục `Luật DoP khớp`).

### Bước 5 — Vẽ ngược (`ve-nguoc`)

```bash
python linhx-rea/scripts/ve_nguoc.py <thu_muc_anh>
```

(Hoặc truyền `<dir_ra>` để chạy hàng loạt.) Sinh tại `<anh>/ve-nguoc/`:
- `khoi.png`: ảnh thường vẽ bản khối 3 lớp xám + viền Canny; ảnh phẳng (`do_sau.phang=true`) thay bằng bản khối bố cục lưới `24×N` (`chu` / `hinh` / `khoang_trong`) + chú giải và ghi thêm `bo_cuc.json`.
- `khung.png`: nền xám sáng + lưới 1/3 + 2 đường chéo mảnh + điểm hút mắt đánh số + mũi tên đường dẫn mắt ("máy" / "người đọc").
- `prompt.md`: prompt tiếng Anh + tóm tắt tiếng Việt đủ 7 mục, kéo chi tiết cụ thể + toạ độ từ `ghi_chu` (≤25 từ/trục, không cắt `"..."`, bỏ phần `"MAY-SAI:"`); ảnh phẳng ghi tỉ lệ `bo_cuc.json` thay cho lớp độ sâu.

### Bước 6 — Rút thẻ thủ pháp (`the`)

```bash
python linhx-rea/scripts/rea_core.py the <dir_ra>
```

Gom `the_de_xuat` từ `doc.json` mọi ảnh, kiểm theo `../../references/the-thu-phap.schema.json`:
- Thẻ đúng → `<dir_ra>/thu-phap/thu-phap.jsonl` và `<dir_ra>/thu-phap/README.md` (bảng `ten | loai | moc | khi_dung`).
- Thẻ sai schema → `the-loi.jsonl`. Báo lỗi nếu có ảnh đạt `<1` thẻ đúng schema.

### Bước 7 — Tóm tắt & dựng hồ sơ chung (`tom`)

```bash
python linhx-rea/scripts/rea_core.py tom <dir_ra>
```

Dựng trọn bộ đầu ra tại `<dir_ra>/`: `cau-truc.md`, `nhip.md` (chuyển biến theo thứ tự shot), `nguyen-lieu.md`, `ve-dep.md` (ma trận Bruce Block), `thu-phap/`, `ve-nguoc/README.md` (index từng ảnh), và `tom.md` (≤40 dòng, có mục `Máy sai cần sửa`).

## Ghi nhận sửa sai → kiểm thử (`sua`)

```bash
python linhx-rea/scripts/rea_core.py sua <dir_ra>
python linhx-rea/scripts/rea_core.py sua <dir_ra> --kiem-lai
```

Quét mọi ghi chú `"MAY-SAI:"` trong `dap_an.json` ghi nối + khử trùng theo `(anh, truc, mo_ta)` vào `<dir_ra>/sua-sai.jsonl` (không bao giờ xoá mục cũ); dùng `--kiem-lai` để kiểm tự động lại từng mục bằng `do.json` mới (`da_sua`, `mo`, `chua_kiem_duoc`) và in bảng tổng hợp.

## Tài liệu tham chiếu

- Khung 2 tầng, quy ước mốc, vòng `sua → test`, Bruce Block: `../../references/khung-chung.md`
- Luật & checklist DoP (52 luật + đối chiếu ShotBench): `../../references/luat-dop.md`
- Quy tắc & JSON Schema thẻ thủ pháp: `../../references/the-thu-phap.md`, `../../references/the-thu-phap.schema.json`
- Từ vựng 17 trục đọc ảnh: `../../tu-vung/anh.yaml`
