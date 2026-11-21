---
name: hang-doi-may
description: "Giao việc cho đội máy agy qua hàng đợi phiếu GitHub (nhánh hang-doi của linhx-engine): Claude ra đề, khoá test, agy trên các máy tự nhận, tự chia việc, Claude chấm cuối. Dùng khi Linh nói giao máy, giao agy, chạy trên máy cty, hàng đợi, hoặc dự án cần dựng/chạy/tìm kiếm nặng."
metadata:
  version: 0.3.0
---
# Hàng đợi máy agy

Claude cloud là não: nói chuyện với Linh, ra đề, khoá test, chấm cuối. Việc nặng (dựng, chạy, duyệt web, tải, render) giao agy trên máy qua phiếu. Claude chỉ đọc `KET-QUA.md` (≤ 2000 ký tự) nên tốn ít token.

**Ngưỡng 10 dòng** (học từ codex-first, hạ từ 20 ngày 21/11 vì Neon sửa 7 lỗi trong ~5 phút máy, không tốn token Claude): Claude chỉ tự sửa khi thay đổi dưới 10 dòng, một chỗ, rõ ràng. Lớn hơn, hoặc rebase/gộp/xử lý xung đột/sửa CI, thì viết phiếu giao agy. Viết phiếu mà còn phải tự quyết thiết kế thì Claude chốt thiết kế trước, rồi mới giao.

## Máy (sửa bảng này khi đổi máy)
| Mã | Máy | Dùng cho |
|---|---|---|
| may-1 | DESKTOP-PVHR2CD, `D:\linhx\hang-doi` | Chrome đã đăng nhập tài khoản. RAM ít, ổ C: gần đầy, đang chạy thợ ENGINE |
| may-2 | DESKTOP-LNRQBEE, `C:\linhx\hang-doi` | Máy chính: dựng code, orchestration, 5 phiếu song song; có trình duyệt đăng nhập (15/11); deploy staging Yên Lam; trạm git |
| may-3 | DESKTOP-2AUT482, `C:\linhx\hang-doi` | Gemini Task, phiếu code; hạn mức Ultra riêng |
| may-4 | MSI (máy cá nhân) | Chỉ phiếu ghi đích danh may-4 (`-ChiDichDanh`) |

## Phiếu
File `hang-doi/moi/<du-an>-<loai>-<viec>.md` trên nhánh `hang-doi`, push là xong. Quy ước tên `<du-an>-<loai>-<viec>` để runner lấy đoạn thứ 2 (`<loai>`) tự chọn model theo `runner/model-theo-loai.json`. Máy rảnh tự nhận (đổi sang `dang/`), làm xong ghi `xong/<id>/KET-QUA.md` (dòng đầu luôn có `model: <id thật dùng>`).
```
may: may-2            # hoặc bat-ky
loai: code            # code | trinh-duyet | khac
model: gemini-pro-orchestrator  # tuỳ chọn: ghi đè model (--model <id>, chỉ chữ/số/-/./_)
tran_phut: 40         # trần, tối đa 40
theo_doi: C:\linhx\wt-du-an   # BẮT BUỘC khi agy làm ngoài thư mục phiếu (repo clone riêng)
phu_thuoc: id1; id2   # tuỳ chọn: chỉ nhận khi mọi id đã xong; cha loi/dung hết tu_sua → huy ("phụ thuộc trượt")
tu_sua: 2             # tuỳ chọn (0–3, mặc định 0): tự tạo <id>-sua-<k>.md khi loi/dung (trừ lỗi máy)
cham: 1               # tuỳ chọn: khi xong tự sinh moi/<id>-cham.md (loai: cham, mắt mới đọc đề gốc + diff, ngưỡng 9/10)
khong_tien_phut: 25    # tuỳ chọn: nâng ngưỡng "không tiến" (mặc định 20) cho việc lâu; tối đa bằng tran_phut
khoa: viec/du-an/nghiem-thu/test.py.khoa  # tuỳ chọn: file .khoa (tương đối theo_doi đầu tiên); lệch sha256 → loi "sửa test khoá"
lenh_kiem: python -m pytest viec/du-an/nghiem-thu -q  # tuỳ chọn: runner tự chạy sau agy (trần 15p), đạt mới xong; trượt → loi kèm 1500 ký tự cuối log
vung: runner/**; skills/le/hang-doi-may/**  # tuỳ chọn: glob phạm vi commit mới ở theo_doi đầu; ngoài vùng ("sửa ngoài vùng: <file>") hoặc lộ bí mật (<file>:<dòng>) → loi
cho_nen: co           # tuỳ chọn: đặt khi phiếu được phép chạy tác vụ nền / thợ con (mặc định tắt)

## Mục tiêu
Làm xong thì đúng cái gì (1–3 câu, đo được).
## File được sửa
Đường dẫn/glob cụ thể (khớp `vung:` nếu có).
## Cấm động
File/thư mục/việc không được chạm (test khoá, `.khoa`, prod, bí mật...). Gặp chặn: DỪNG, báo số liệu và chẩn đoán, không lách.
## Test bằng chứng
Lệnh kiểm chính xác (khớp `lenh_kiem:`) và kết quả phải thấy. Trả lời: file đã đổi + đầu ra test.
```
**Phiếu thiếu một trong 4 mục trên thì không đẩy.** Agy bắt đầu không có ngữ cảnh gì, chất lượng đề quyết định kết quả. Mỗi luật cấm phải kèm lối ra (dừng và báo); phiếu trả về báo cáo dừng vẫn tính là chạy đúng, đó là điểm Claude quyết.
**Chọn model theo phiếu** (cờ headless `--model <id>`, thứ tự ưu tiên): `model:` trong header phiếu → tiền tố `<loai>` ở đoạn thứ 2 của tên phiếu `<du-an>-<loai>-<viec>` → biến `LINHX_MODEL` trong `tho.env` → giữ `AGY_ARGS` mặc định như cũ. Model không có trong `agy models` thì runner ghi cảnh báo vào `KET-QUA.md` và chạy model mặc định (`mac-dinh`), không báo lỗi.

| Tiền tố `<loai>` | Model (`runner/model-theo-loai.json`) | Dùng cho |
|---|---|---|
| `dp` | `gemini-pro-orchestrator-neon` | Điều phối, chia phiếu |
| `code` | `gemini-4-neon-high` | Dựng code, sửa lỗi, sửa kiến trúc |
| `test` | `gemini-4-neon-medium` | Viết / chạy kiểm thử |
| `trien` | `gemini-4-neon-medium` | Triển khai, cấu hình |
| `gop` | `gemini-4-hydrogen-high` | Gộp nhánh, xử lý xung đột |
| `do` | `gemini-4-hydrogen-high` | Đo đạc, benchmark, Lighthouse |
| `td` | `gemini-4-neon-medium` | Trình duyệt / tương tác (A/B 21/11 may-1: 0,9 phút, 38k/2k token, 3 bước; hydrogen-high 1,0 phút, 52k/4k, 6 bước; cùng kết quả đúng) |
| `kiem` | `gemini-4-hydrogen-low` | Kiểm nhanh, ping, rà nhẹ |

Việc rất khó (thiết kế lại, lỗi lặp 2 lần): ghi đè `model: gemini-4-neon-xhigh` (chưa đo). `gop`, `do` giữ Hydrogen (chưa đo). Đo lại bảng sau mỗi đợt: `python runner/so_model.py hang-doi/xong`.

Mỗi phiếu: một repo clone riêng (`C:\linhx\wt-<du-an>`), không làm trong `hang-doi` (runner đang chạy). Hai phiếu chạy song song không dùng chung một clone. Runner tự chèn vào cuối đề câu nhắc cho phép chạy tác vụ nền có timeout, ghi log vào `theo_doi`, tự kiểm/tắt và tắt server chạy mãi trước khi kết thúc (trừ khi `cho_nen: co`). Khi đọc luồng ra thấy `waiting up to .* background task` hoặc `root agent idle`, runner chuyển sang chế độ **CANH NỀN**: còn file mới/đổi trong `theo_doi` hoặc log tác vụ nền tăng dòng trong 5 phút gần nhất thì để chạy tiếp (bảng 8090 hiện nhãn `"đang chờ nền · log cuối N phút trước"`), im hoàn toàn đủ 5 phút (hoặc gặp `status ERROR` có `"chờ lệnh hoàn tất"`) thì dừng cả cây tiến trình (`trang_thai: dung`, `ly_do: cho-nen-im-lang`) và sinh phiếu `-sua-` nếu còn `tu_sua`. Khi phiếu kết thúc (`xong` hoặc `dung`), runner chép 60 bước cuối đã che bí mật vào `hang-doi/xong/<id>/NHAT-KY.md`. Bộ canh "không tiến" (mặc định 20 phút) tính là có tiến khi có file đổi đệ quy trong `theo_doi` hoặc tổng CPU cây tiến trình `agy` tăng trong 2 phút gần nhất.
Khi chạy: cứ 3 phút runner ghi dòng `nhip: <giờ> <phút> <dòng cuối ≤120 ký tự>` vào cuối `dang/<id>.md`; gặp khối `CAN-LINH: <việc>; LENH: <lệnh>` thì ghi `can-linh/<id>.md` để hiện lên đầu bảng web; hồ sơ phần cứng/năng lực tự ghi ở `may/<ma-may>.json` (thêm `LINHX_VAI` trong `tho.env`).

## Phiếu lệnh (không mở agy)
`loai: lenh` + `lenh: <ten>`: runner chạy `runner/lenh/<ten>.ps1` đã commit (không chạy lệnh tuỳ ý trong phiếu), không tốn token. Có sẵn: `suc-khoe` (RAM, ổ, agy, log cuối), `xem-viec` (thư mục wt-*: commit cuối, file đổi).

## Quy trình một việc (đã chạy thử: landing Listening Vietnam 14/11)
1. **Đề** (Claude): `viec/<du-an>/DE-BAI.md`: mục tiêu, người dùng, khối/chức năng, ràng buộc, định nghĩa xong. Đính brand/tài liệu vào repo vì máy không đọc được thư mục chung cloud.
2. **Tiêu chuẩn + test khoá** (Claude): `viec/<du-an>/nghiem-thu/test_*.py` đo được (Playwright cho web: màn đầu, không tràn 360, form, console sạch, dung lượng). Thử test trên một trang giả trước khi khoá (đề phải khớp test). Ghi sha256 vào `.khoa`.
3. **Điều phối**: một phiếu `loai: dieu-phoi` cho may-2 (xem dưới), hoặc Claude tự viết vài phiếu nhỏ có thứ tự (tìm mẫu → dựng → chấm).
4. **Thợ** (agy): làm, tự chạy test khoá tới khi đạt, push nhánh việc.
5. **Chấm vòng 1** (máy): test khoá + Lighthouse + bộ `bang-chung/` thu bằng `runner/bang_chung.py` trên HTTP thật.
6. **Soát chéo** (agy, mắt mới): phiếu code bắt buộc `cham: 1` → runner tự sinh `<id>-cham.md`, một phiên agy mới đọc đề gốc + diff, chấm theo 4 mục của phiếu, ngưỡng 9/10. Chưa qua soát chéo thì Claude chưa chấm; trượt thì phiếu sửa.
7. **Chấm vòng cuối** (Claude, quyết gộp): so sha256 test, chạy lại test trên cloud, xem 2 ảnh màn đầu, đối chiếu brand. Trượt thì phiếu sửa, tối đa 3 vòng.
8. **Giao Linh**: bản một file (nhúng css/js/svg) đính kèm, hoặc link demo.

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

## Neon (đo 21/11 trên may-2, `viec/neon-ab/`)
Gemini 4 Neon ra 18/11, có sẵn trong agy 1.5.13 (`gemini-4-neon-low|medium|high|xhigh`, `gemini-pro-orchestrator-neon`). Hai vòng, cùng đề, test khoá + 19 test ẩn chạy ở cloud:
| Model | Vòng 1 viết mới (phút, token vào/ra) | Vòng 2 sửa 7 lỗi | Test ẩn |
|---|---|---|---|
| gemini-pro-orchestrator (cũ của `code`) | | 8,5 · 141k/62k | 19/19 |
| gemini-pro-orchestrator-neon | | 6,9 · 121k/43k | 19/19 |
| gemini-4-neon-high | 4,0 · 60k/11k | 5,7 · 82k/28k | 19/19, 18/19* |
| gemini-4-argon-high (cũ của `test`) | 4,2 · 55k/9k | 4,3 · 66k/17k | 19/19 |
| gemini-4-neon-medium | 3,1 · 56k/7k | | 19/19 |
\* 29/2 được cho sang năm nhuận kế tiếp thay vì báo lỗi: hợp lý, nhưng làm quá đề.
Kết luận: lợi lớn nhất là bỏ orchestrator cho phiếu code (nhanh gấp 1,5, ít hơn nửa token ra), đơn tác tử còn tránh lỗi "chờ nền". Neon-high ngang argon-high ở việc nhỏ (không nhanh hơn); chọn Neon vì giá thấp hơn Carbon ~32% mỗi việc và điểm coding agent cao. Neon-medium đủ cho viết test/triển khai.
Luật mới: phiếu code quan trọng có thêm **test ẩn** giữ ở cloud (không đẩy lên phiếu), Claude chạy sau khi agy push nhánh; bắt được lỗi "chỉ cho qua test".
Lỗi đã gặp: 4 phiếu chạy cùng lúc trên may-2 thì một phiếu trả `backend returned an empty conversation id` sau 5 giây (lỗi máy, `tu_sua` không tự chạy lại lỗi máy; Claude thả lại phiếu đuôi `2` là đạt).

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
- Gắn `khoa:` + `lenh_kiem:` vào header phiếu để runner tự đối chiếu sha256 test khoá và chạy lệnh kiểm (trần 15 phút) ngoài tay agy trước khi công nhận `xong`.
- Gắn `vung: glob1; glob2` để runner đối chiếu diff các commit mới so với `HEAD` lúc nhận phiếu ở `theo_doi` đầu tiên, chặn sửa ngoài vùng và quét bí mật (chỉ báo `<file>:<dòng>`, không in giá trị, ghi 1 dòng JSON/phiếu vào log runner).
- Lúc nhận phiếu runner ghi `moc: <sha HEAD>` vào `dang/<id>.md` để lùi code khi cần; `cham: 1` tự sinh `<id>-cham.md` (`loai: cham`) chấm mắt mới trên diff; phụ thuộc trượt hết `tu_sua` tự chuyển `xong/<id>/KET-QUA.md` (`trang_thai: huy`, `"phụ thuộc trượt"`); `agy` trả `429`/hết hạn mức thì máy ghi cờ tạm nghỉ 30 phút không nhận phiếu mới.

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
