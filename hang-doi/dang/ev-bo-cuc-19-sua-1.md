may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: D:\linhx\ifagent-wt\ev-bo-cuc-19
nhan: may-3 2026-11-17T22:34:11+0700

Lượt trước bị dừng vì chạy tác vụ nền rồi chờ. Lượt này mọi lệnh phải chạy tiền cảnh, đợi xong trong cùng lệnh.

Phiếu ev-bo-cuc-19 (song song máy 3): COMMIT + PUSH SAU MỖI Ý.
0. `$env:GIT_TERMINAL_PROMPT=0`. `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent-wt\ev-bo-cuc-19` (đã có thì fetch), `git checkout -b agy/ev-bo-cuc-19 origin/agy/ev-de-xuat-13b`. Trong apps/event: `npm ci`. Commit + push ngay khi có thay đổi đầu tiên.
1. Thêm test khoá `apps/event/test/e2e/bo-cuc-4-co.test.js` (script `test:bo-cuc`): 18 trang (danh sách như test chụp) × 4 cỡ (360, 768, 1280, 1920) × 2 giao diện (Đêm, Sáng). Bắt: chữ/nút chồng lên nhau (giao nhau hộp bao giữa các phần tử chữ, nút, ảnh cùng cấp > 4 px), chữ bị cắt (scrollWidth > clientWidth trên phần tử chữ không cuộn), vùng bấm < 44×44 px ở 360 và 768, cỡ chữ thân < 14 px ở 360. Thông báo: "<trang> @<cỡ> <giao diện>: <lỗi> ở <selector> — <cách sửa>".
2. Chạy (đỏ → bang-chung/ev-bo-cuc-19/do.log), sửa CSS trong apps/event cho tới xanh, không đổi bố cục nhìn thấy ở 1280 ngoài các chỗ lỗi. Chụp ảnh trước/sau các trang có lỗi vào bang-chung/ev-bo-cuc-19/.
3. Chạy tiền cảnh: test:bo-cuc, khong-tran-ngang, giao-dien-sang; npm test sau cùng. KET-QUA: số lỗi theo loại trước/sau, danh sách trang đã sửa.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task, không dùng lệnh `status` chờ tác vụ; máy chủ khởi động và tắt BÊN TRONG chính script test. Chỉ sửa apps/event/ và bang-chung/ev-bo-cuc-19/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ (chỉ thêm ca mới), không sinh ảnh AI, không gọi AI thật, không viết chữ mới. KET-QUA ngắn: dat co/khong; SHA; test đỏ→xanh; pass/fail.

## Lần trước trượt vì:
model: mac-dinh
phieu: ev-bo-cuc-19
may: may-3
trang_thai: dung
ly_do: cho-tac-vu-nen
tep_doi: (khong)
drive: (khong)
phut: 0.80
token: vao=0 ra=0

dừng agy (cho-tac-vu-nen): waiting up to ... background task
warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the default mode.
root agent idle; waiting up to 40m0s for 1 background task(s)

nhip: 22:40 6p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
