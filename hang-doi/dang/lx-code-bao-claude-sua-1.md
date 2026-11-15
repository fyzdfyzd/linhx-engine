may: may-2
loai: code
tran_phut: 30
khong_tien_phut: 20
tu_sua: 0
theo_doi: C:\linhx\wt\bao-claude
nhan: may-2 2026-11-15T13:48:10+0700

GẤP vừa. Chuông báo Claude: thay vì Claude đọc 30 phút/lần, runner BÁO NGAY khi phiếu cần Claude. Chạy mọi lệnh tiền cảnh, mỗi lệnh timeout ≤ 300 s, mỗi 5 phút có file mới/commit. KHÔNG khởi động lại runner đang chạy.
1. `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt\bao-claude` (có rồi thì fetch), `git checkout -b agy/bao-claude`.
2. Hàm mới `runner/bao_claude.py: bao(id, dat, may, phut)` đăng MỘT bình luận lên PR #36 repo fyzdfyzd/linhx-engine (PR nháp "Hộp thư Claude"), nội dung đúng một dòng: `XONG <id> dat=<co|khong|?> may=<may> phut=<n>`. Gửi bằng `gh pr comment 36 -R fyzdfyzd/linhx-engine -b "..."` nếu máy có gh đã đăng nhập; không có thì POST REST API `/repos/fyzdfyzd/linhx-engine/issues/36/comments` với token đọc từ biến LINHX_GH_TOKEN trong tho.env (KHÔNG in token, KHÔNG ghi token vào log). Lỗi mạng: thử lại 3 lần, rồi bỏ qua (không làm hỏng phiếu).
3. Gọi `bao` khi một phiếu kết thúc (xong/dung/loi) và thoả một trong: id bắt đầu `yl-`; header `bao: claude`; có phiếu khác trong moi/ đang `phu_thuoc` vào một id chưa có trong xong/ mà id đó bắt đầu `yl-khoa-` hoặc `yl-duyet-` (tức là Claude đang là cổng). Phiếu `-sua-` đang chạy lại thì không báo lượt dừng, chỉ báo lượt cuối. Chống lặp: mỗi id báo đúng 1 lần (ghi dấu vào xong/<id>/.da-bao).
4. Test runner/test_bao_claude.py (giả gh/HTTP): đúng nội dung một dòng; không báo phiếu lx- không có `bao: claude`; không báo 2 lần; token không xuất hiện trong log. `python -m pytest runner -q` + `python -m pytest tests/nghiem-thu -q`.
5. Kiểm trên máy 2: có `gh` không, `gh auth status` (chỉ ghi có/không đăng nhập, không in token). Nếu chưa có cả gh lẫn LINHX_GH_TOKEN thì ghi CAN-LINH: "Máy 2: chạy `gh auth login` một lần (tài khoản fyzdfyzd)".
6. Push `agy/bao-claude` (KHÔNG push vào claude/project-thread-jowxv1).
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co`/`dat: khong`; SHA; test pass/fail; máy 2 gửi được bằng gh hay token hay chưa được.

## Lần trước trượt vì:
model: gemini-pro-orchestrator
phieu: lx-code-bao-claude
may: may-2
trang_thai: dung
tep_doi: (khong)
drive: (khong)
phut: 30.03
token: vao=0 ra=0

dừng agy: quá trần 30 phút
warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the default mode.
root agent idle; waiting up to 40m0s for 1 background task(s)

nhip: 13:51 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
