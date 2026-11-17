may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: D:\linhx\ifagent-wt\ev-video-luong-20
nhan: may-3 2026-11-17T23:38:41+0700

Lượt trước bị dừng vì chạy tác vụ nền rồi chờ. Lượt này mọi lệnh phải chạy tiền cảnh, đợi xong trong cùng lệnh.

Phiếu ev-video-luong-20 (song song máy 3): COMMIT + PUSH SAU MỖI Ý.
0. `$env:GIT_TERMINAL_PROMPT=0`. `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent-wt\ev-video-luong-20` (đã có thì fetch), `git checkout -b agy/ev-video-luong-20 origin/agy/ev-de-xuat-13b`. Trong apps/event: `npm ci`. Commit + push ngay khi có thay đổi đầu tiên.
1. Viết `apps/event/test/e2e/video-luong.test.js` (script `test:video`): Playwright quay video (recordVideo 1280×720 và một bản 390×844 mô phỏng điện thoại) 5 luồng thao tác thật bằng chuột/bàn phím, có chờ hợp lý giữa các bước để người xem theo kịp: (a) trang chủ → giải pháp → một demo; (b) /tao: điền form tạo sự kiện mẫu bằng dữ liệu mẫu có sẵn trong catalog, đến trang kết quả; (c) xưởng ý tưởng → mở đề xuất slide Trà Việt → lật 8 slide → tải PDF (kiểm tệp tải về 8 trang); (d) /thu?nguon=yen-lam&ma=<mã mẫu có sẵn>; (e) chuyển giao diện Đêm ↔ Sáng trên 3 trang. Mỗi luồng khẳng định trạng thái cuối đúng (ca test thật, không chỉ quay).
2. Lưu video webm vào bang-chung/ev-video-luong-20/<luong>-<co>.webm (mỗi tệp ≤ 15 MB, nếu lớn hơn thì giảm fps), kèm 1 ảnh khung cuối mỗi luồng .png. Lỗi luồng nào thì sửa trong apps/event (ghi rõ trong KET-QUA).
3. npm test sau cùng. KET-QUA: 5 luồng pass/fail, thời lượng mỗi video, lỗi đã sửa.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task, không dùng lệnh `status` chờ tác vụ; máy chủ khởi động và tắt BÊN TRONG chính script test. Chỉ sửa apps/event/ và bang-chung/ev-video-luong-20/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ (chỉ thêm ca mới), không sinh ảnh AI, không gọi AI thật, không viết chữ mới. KET-QUA ngắn: dat co/khong; SHA; test đỏ→xanh; pass/fail.

## Lần trước trượt vì:
model: mac-dinh
phieu: ev-video-luong-20
may: may-3
trang_thai: dung
ly_do: cho-tac-vu-nen
tep_doi: (khong)
drive: (khong)
phut: 0.75
token: vao=0 ra=0

dừng agy (cho-tac-vu-nen): waiting up to ... background task
warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the default mode.
root agent idle; waiting up to 40m0s for 1 background task(s)
