---
name: hang-doi-may
description: "Giao việc cho đội máy agy qua hàng đợi phiếu GitHub (nhánh hang-doi của linhx-engine): Claude ra đề, khoá test, agy trên các máy tự nhận, tự chia việc, Claude chấm cuối. Dùng khi Linh nói giao máy, giao agy, chạy trên máy cty, hàng đợi, hoặc dự án cần dựng/chạy/tìm kiếm nặng."
metadata:
  version: 0.1.0
---
# Hàng đợi máy agy

Claude cloud là não: nói chuyện với Linh, ra đề, khoá test, chấm cuối. Việc nặng (dựng, chạy, duyệt web, tải, render) giao agy trên máy qua phiếu. Claude chỉ đọc `KET-QUA.md` (≤ 2000 ký tự) nên tốn ít token.

## Máy (sửa bảng này khi đổi máy)
| Mã | Máy | Dùng cho |
|---|---|---|
| may-1 | DESKTOP-PVHR2CD, `D:\linhx\hang-doi` | Chrome đã đăng nhập tài khoản. RAM ít, ổ C: gần đầy, đang chạy thợ ENGINE |
| may-2 | DESKTOP-LNRQBEE, `C:\linhx\hang-doi` | Máy chính: dựng code, orchestration, chạy song song 3 phiếu |
| may-3 | (cài sau) | |
| may-4 | MSI (máy cá nhân) | Chỉ phiếu ghi đích danh may-4 (`-ChiDichDanh`) |

## Phiếu
File `hang-doi/moi/<id>.md` trên nhánh `hang-doi`, push là xong. Máy rảnh tự nhận (đổi sang `dang/`), làm xong ghi `xong/<id>/KET-QUA.md`.
```
may: may-2            # hoặc bat-ky
loai: code            # code | trinh-duyet | khac
tran_phut: 40         # trần, tối đa 40
theo_doi: C:\linhx\wt-du-an   # BẮT BUỘC khi agy làm ngoài thư mục phiếu (repo clone riêng)
phu_thuoc: id1; id2   # tuỳ chọn: chỉ nhận khi mọi id đã xong (trang_thai: xong); loi/dung thì bỏ qua
tu_sua: 2             # tuỳ chọn (0–3, mặc định 0): tự tạo <id>-sua-<k>.md khi loi/dung (trừ lỗi máy)

Việc, đầu vào, cấm đụng gì, cách kiểm, trả lời gì.
```
Mỗi phiếu: một repo clone riêng (`C:\linhx\wt-<du-an>`), không làm trong `hang-doi` (runner đang chạy). Hai phiếu chạy song song không dùng chung một clone.

## Quy trình một việc (đã chạy thử: landing Listening Vietnam 14/11)
1. **Đề** (Claude): `viec/<du-an>/DE-BAI.md`: mục tiêu, người dùng, khối/chức năng, ràng buộc, định nghĩa xong. Đính brand/tài liệu vào repo vì máy không đọc được thư mục chung cloud.
2. **Tiêu chuẩn + test khoá** (Claude): `viec/<du-an>/nghiem-thu/test_*.py` đo được (Playwright cho web: màn đầu, không tràn 360, form, console sạch, dung lượng). Thử test trên một trang giả trước khi khoá (đề phải khớp test). Ghi sha256 vào `.khoa`.
3. **Điều phối**: một phiếu `loai: dieu-phoi` cho may-2 (xem dưới), hoặc Claude tự viết vài phiếu nhỏ có thứ tự (tìm mẫu → dựng → chấm).
4. **Thợ** (agy): làm, tự chạy test khoá tới khi đạt, push nhánh việc.
5. **Chấm vòng 1** (máy): test khoá + Lighthouse + ảnh 360/1280 trong `bang-chung/`.
6. **Chấm vòng 2** (Claude): so sha256 test, chạy lại test trên cloud, xem 2 ảnh màn đầu, đối chiếu brand. Trượt thì phiếu sửa, tối đa 3 vòng.
7. **Giao Linh**: bản một file (nhúng css/js/svg) đính kèm, hoặc link demo.

## agy tự điều phối (orchestration)
Phiếu `loai: dieu-phoi` cho máy chính:
```
may: may-2
loai: dieu-phoi
tran_phut: 40
theo_doi: C:\linhx\wt-<du-an>

Đọc viec/<du-an>/DE-BAI.md. Clone nhánh hang-doi riêng vào C:\linhx\wt-hang-doi (có rồi thì git pull). Chia thành phiếu con ≤ 40 phút, ghi vào hang-doi/moi/<du-an>-<n>.md (đúng khuôn phiếu, có may:, theo_doi:, phụ thuộc ghi trong thân phiếu), push nhánh hang-doi.
Việc trình duyệt cần đăng nhập → may-1. Việc code → may-2 hoặc bat-ky.
Không tự làm phiếu con. Trả lời: danh sách phiếu con + thứ tự.
```
Claude duyệt danh sách phiếu con (đọc 1 file), xoá phiếu sai, rồi để máy chạy. Bên trong một phiếu, agy được tự sinh thợ con (background task): khi đó bắt buộc có `theo_doi:`.

## Bài học (14/11)
- agy chia thợ con làm ở thư mục khác → bộ canh không thấy tiến, dừng oan sau 10 phút. Sửa: dòng `theo_doi:`.
- Không chạy test ở chế độ nền rồi ngồi chờ; dặn "chạy ở tiền cảnh".
- Việc thử không đặt trong `giao-dien/` (cổng K1–K10 site BU chặn); dùng `viec/<du-an>/`.
- Mỗi lần mở agy tốn khoảng 13k token cố định, ảnh chụp màn hình tốn thêm nhiều: gom việc vào một phiếu, phiếu nhẹ (ping, kiểm) dùng model nhẹ.
- Sửa code runner thì Linh phải `git pull` trong thư mục `hang-doi` trên từng máy.
- Máy thiếu agy dòng lệnh hoặc không có ổ D: → truyền `-AgyCmd`, `-ThuMuc`.

## Cài máy mới
CMD trên máy (đổi `may-N`, ổ):
```
git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine D:\linhx\hang-doi
cd /d D:\linhx\hang-doi
powershell -ExecutionPolicy Bypass -Command "& .\runner\cai-may.ps1 -May may-N -AgyCmd (Get-Command agy).Source"
```
Thêm `-SoPhieu 3` cho máy mạnh, `-ChiDichDanh` cho máy cá nhân. Thử bằng phiếu `runner/phieu-mau/ping.md`.

## Đọc kết quả (Claude)
`git -C <clone hang-doi> pull origin hang-doi`, đọc `hang-doi/xong/<id>/KET-QUA.md`. `trang_thai: dung` = bộ canh dừng (đọc dòng lý do), `loi` = lỗi máy (thiếu agy, 429).
