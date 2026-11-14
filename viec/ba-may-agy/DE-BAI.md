# Đề agy: 3 máy công ty nhận việc qua hàng đợi GitHub

Linh chọn 14/11/2026. Claude (cloud) là não: viết phiếu, đọc kết quả, nói chuyện với Linh.
3 máy công ty chỉ chạy agy. Claude cloud không với tới engine.linhx.vn (proxy chặn), nên cầu nối là GitHub.

## Nguyên tắc
- Dùng lại `runner/linhx_runner.py` (hàm `chay_agy`, cờ `agy-settings.json`), chỉ thêm nguồn việc GitHub. Không viết runner mới.
- Hàng đợi nằm ở nhánh riêng `hang-doi` của repo này, không đụng `main`.
- Kết quả gửi lên phải NGẮN (Claude đọc tốn token): `KET-QUA.md` ≤ 2000 ký tự. Log đầy đủ để trên máy, không commit.
- File nặng (ảnh, video, PDF, zip) ghi vào `G:\My Drive\LINHX-VIEC\<id>\`, phiếu chỉ ghi đường dẫn.
- Không bí mật trong repo: `tho.env` không commit.

## Cấu trúc nhánh `hang-doi`
```
hang-doi/moi/<id>.md      phiếu chờ (đầu file: may: may-1|may-2|may-3|bat-ky; loai: code|trinh-duyet|khac)
hang-doi/dang/<id>.md     đã có máy nhận (thêm dòng nhan: <may> <giờ>)
hang-doi/xong/<id>/KET-QUA.md   trạng thái (xong|loi|dung), file đã đổi, đường dẫn Drive, phút, token
```
Giữ phiếu = commit đổi tên `moi/` → `dang/` rồi push; push bị từ chối (máy khác nhận trước) thì bỏ, kéo lại.

## Phiếu (mỗi phiếu ≤ 40 phút)

| ID | Việc | phu_thuoc |
|---|---|---|
| H1 | `runner/hang_doi_git.py`: kéo nhánh `hang-doi`, chọn phiếu của máy mình hoặc `bat-ky`, giữ phiếu bằng push, gọi `chay_agy`, ghi `KET-QUA.md`, push. Thêm `LINHX_NGUON=github` trong `tho.env` để `linhx_runner.py` chọn nguồn. Test bằng repo bare cục bộ, không gọi mạng. | |
| H2 | Rút gọn kết quả: cắt `KET-QUA.md` ≤ 2000 ký tự, chép file > 1 MB sang thư mục Drive, ghi log đủ vào `D:\linhx\linhx-runner\log\<id>.jsonl`. Test. | H1 |
| H3 | Định tuyến và an toàn: máy nào cũng nhận cả `code` lẫn `trinh-duyet`; mỗi máy tối đa 1 phiếu `trinh-duyet` một lúc (computer use chiếm chuột, bàn phím, màn hình) và tối đa `LINHX_SO_PHIEU` phiếu `code` chạy song song (mặc định 1); quá 40 phút hoặc 10 phút không tiến thì dừng agy (học cách dừng trong `canh/dieu-phoi-engine.ps1`); RAM trống < 1,5 GB thì không nhận. Test. | H1 |
| H4 | `runner/cai-may.ps1 -May may-N`: clone repo vào `D:\linhx\hang-doi` (thư mục riêng; KHÔNG dùng `D:\LINHX\LINHX-ENGINE` vì Windows không phân biệt hoa thường, trùng repo đang chạy thợ ENGINE), tạo `tho.env`, đăng ký Task Scheduler chạy MỖI PHÚT, CHỈ KHI USER ĐÃ ĐĂNG NHẬP (cần màn hình cho computer use), chạy ẩn qua `chay-an-tho.vbs`; agy để tự chạy lệnh, giới hạn trong `D:\linhx`. Kèm phiếu mẫu `ping` để thử. | H1 |

## Định nghĩa xong
- `pytest runner` xanh, không test skip, không gọi mạng thật.
- Hai runner giả cùng lúc tranh một phiếu `bat-ky`: đúng một bên nhận.
- Phiếu `ping` gửi từ cloud tới mỗi máy có `KET-QUA.md` trong ≤ 3 phút.

## Máy
Cả 3 máy (may-1 = DESKTOP-PVHR2CD, may-2, may-3) làm được cả code lẫn trình duyệt. Phiếu `bat-ky` thì máy rảnh nhận.
Chỉ chia khi cần tài khoản riêng: phiếu ghi `may:` nếu việc cần Chrome profile hoặc tài khoản chỉ đăng nhập trên một máy.
