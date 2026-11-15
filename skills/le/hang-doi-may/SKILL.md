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
khong_tien_phut: 25    # tuỳ chọn: nâng ngưỡng "không tiến" (mặc định 10) cho việc lâu như clone repo lớn, test dài; tối đa bằng tran_phut

Việc, đầu vào, cấm đụng gì, cách kiểm, trả lời gì.
```
Mỗi phiếu: một repo clone riêng (`C:\linhx\wt-<du-an>`), không làm trong `hang-doi` (runner đang chạy). Hai phiếu chạy song song không dùng chung một clone.
Khi chạy: cứ 3 phút runner ghi dòng `nhip: <giờ> <phút> <dòng cuối ≤120 ký tự>` vào cuối `dang/<id>.md`; gặp khối `CAN-LINH: <việc>; LENH: <lệnh>` thì ghi `can-linh/<id>.md` để hiện lên đầu bảng web; hồ sơ phần cứng/năng lực tự ghi ở `may/<ma-may>.json` (thêm `LINHX_VAI` trong `tho.env`).

## Quy trình một việc (đã chạy thử: landing Listening Vietnam 14/11)
1. **Đề** (Claude): `viec/<du-an>/DE-BAI.md`: mục tiêu, người dùng, khối/chức năng, ràng buộc, định nghĩa xong. Đính brand/tài liệu vào repo vì máy không đọc được thư mục chung cloud.
2. **Tiêu chuẩn + test khoá** (Claude): `viec/<du-an>/nghiem-thu/test_*.py` đo được (Playwright cho web: màn đầu, không tràn 360, form, console sạch, dung lượng). Thử test trên một trang giả trước khi khoá (đề phải khớp test). Ghi sha256 vào `.khoa`.
3. **Điều phối**: một phiếu `loai: dieu-phoi` cho may-2 (xem dưới), hoặc Claude tự viết vài phiếu nhỏ có thứ tự (tìm mẫu → dựng → chấm).
4. **Thợ** (agy): làm, tự chạy test khoá tới khi đạt, push nhánh việc.
5. **Chấm vòng 1** (máy): test khoá + Lighthouse + bộ `bang-chung/` thu bằng `runner/bang_chung.py` trên HTTP thật.
6. **Chấm vòng 2** (Claude): so sha256 test, chạy lại test trên cloud, xem 2 ảnh màn đầu, đối chiếu brand. Trượt thì phiếu sửa, tối đa 3 vòng.
7. **Giao Linh**: bản một file (nhúng css/js/svg) đính kèm, hoặc link demo.

## Bằng chứng
- Mọi phiếu giao diện/web bắt buộc chạy trên `http://` hoặc `https://` thật (cấm `file://`) và nộp thư mục bằng chứng sinh từ:
  `python runner/bang_chung.py --url <http://...> --kho iphone,kiosk,desktop --video --ra <thư mục>`
- Khổ chuẩn: `iphone` (390×844, dpr 3), `kiosk` (1080×1920), `desktop` (1440×900). Công cụ chụp toàn trang mỗi khổ, quay video `.webm` 1 lượt cuộn và ghi `bang-chung.json` (`url`, `kho`, `sha256` từng file, `so_anh_trung = 0`, `loi_console`).
- File lớn (> 1 MB như video/ảnh khổ lớn) chép lên Drive (`<LINHX_DRIVE_DIR>/<id>/`), không đẩy vào nhánh `hang-doi`; trong `KET-QUA.md` chỉ ghi đường dẫn Drive và tóm tắt `bang-chung.json`.

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
``` Thợ con nền hay làm agy gốc ngồi chờ, thư mục không đổi → bị dừng oan: dặn "không chạy nền" hoặc nâng `khong_tien_phut`.
Claude duyệt danh sách phiếu con (đọc 1 file), xoá phiếu sai, rồi để máy chạy. Bên trong một phiếu, agy được tự sinh thợ con (background task): khi đó bắt buộc có `theo_doi:`.

## Phát hành
Học từ luật deploy thực chiến của `ifagent`: mọi dự án có server đi qua hàng đợi phải tách cứng Staging → Prod, không chạm dữ liệu sống và có đường lùi một lệnh.
- **Phiếu deploy chỉ được lên staging** (khuôn `runner/phieu-mau/deploy-staging.md`): chỉ chạy khi `verify` + `e2e` local đã xanh, cây git sạch, không rơi vào giờ sự kiện/lịch khoá, chỉ đẩy đúng app bị ảnh hưởng, giữ nguyên `data/` và lưu bản `:prev` (`.prev`).
- **Chạy cổng phát hành trước và sau** (chỉ dùng `GET`, chặn `--base` trùng `--prod`, chặn giờ VN `> 22h` hoặc `< 7h`):
  - Trước deploy (ghi nhận `BUILD_SHA` đang chạy làm mốc lùi): `python runner/cong_phat_hanh.py --base <url-staging> --truoc --prod <ds-ten-mien-prod>`
  - Sau deploy (bắt buộc `GET /healthz` trả `200` và khớp `<sha-moi>`): `python runner/cong_phat_hanh.py --base <url-staging> --sha <sha-moi> --prod <ds-ten-mien-prod>` — nếu lệch hoặc quá hạn phải chạy rollback ngay về `:prev`.
- **Ghi rõ lệnh rollback**: kết quả phiếu bắt buộc ghi lệnh rollback 1 dòng đã sẵn sàng (vd khôi phục image `:prev` / `rollback-app.sh <app>`).
- **Prod luôn là `CAN-LINH`** (cùng các việc xoá dữ liệu/lead, đổi DNS, tạo/sửa tài nguyên đám mây/khoá, đổi bí mật `.env`): agy tuyệt đối không tự deploy prod mà dừng và trả `CAN-LINH: Duyệt và chạy deploy prod <app> (<sha-moi>); LENH: <lệnh deploy prod> # Rollback: <lệnh rollback>` để Linh duyệt và tự chạy.

## Bài học (14/11)
- agy chia thợ con làm ở thư mục khác → bộ canh không thấy tiến, dừng oan sau 10 phút. Sửa: dòng `theo_doi:`.
- Không chạy test ở chế độ nền rồi ngồi chờ; dặn "chạy ở tiền cảnh".
- Việc thử không đặt trong `giao-dien/` (cổng K1–K10 site BU chặn); dùng `viec/<du-an>/`.
- Mỗi lần mở agy tốn khoảng 13k token cố định, ảnh chụp màn hình tốn thêm nhiều: gom việc vào một phiếu, phiếu nhẹ (ping, kiểm) dùng model nhẹ.
- Sửa code runner thì Linh phải `git pull` trong thư mục `hang-doi` trên từng máy.
- Máy thiếu agy dòng lệnh hoặc không có ổ D: → truyền `-AgyCmd`, `-ThuMuc`.
- Không chạy subagent hay background task rồi ngồi chờ (dễ kẹt 10 phút không đổi thư mục); dặn agy làm tuần tự và chạy mọi lệnh ở tiền cảnh.
- Khi gặp việc chỉ người làm được (đăng nhập, quyền Admin/UAC, captcha, cài phần mềm, duyệt), agy dừng ngay và trả `CAN-LINH: ...; LENH: ...` thay vì thử mù.
- Phát hành qua phiếu chỉ được chạm staging trong khung 07:00–22:00 giờ VN, chạy `runner/cong_phat_hanh.py` trước/sau để khoá `GET /healthz == BUILD_SHA` kèm lệnh rollback; lên prod luôn dừng ở `CAN-LINH`.
- Giao diện không mở `file://` tĩnh (dễ lọt lỗi CORS/CSP/đường dẫn và lặp ảnh); luôn dựng HTTP server cục bộ hoặc URL staging rồi chạy `runner/bang_chung.py`.

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
