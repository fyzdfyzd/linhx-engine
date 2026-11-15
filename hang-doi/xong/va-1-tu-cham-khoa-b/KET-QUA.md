model: mac-dinh
phieu: va-1-tu-cham-khoa-b
may: may-2
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 24.80
token: vao=265263 ra=37124

Đang chạy toàn bộ bộ kiểm thử `python -m pytest runner -q` trong [wt-va1](file:///C:/linhx/wt-va1) và chờ kết quả hoàn tất để commit, rebase và push.
Đã hoàn thành Vá 1 trên nhánh `claude/project-thread-jowxv1`:

- **Làm gì**:
  - [hang_doi_git.py](file:///C:/linhx/wt-va1/runner/hang_doi_git.py): hỗ trợ header `khoa:` và `lenh_kiem:` (tương đối thư mục `theo_doi` đầu tiên, giữ qua `tu_sua`). Sau khi `agy` báo xong, runner kiểm sha256 file test khớp `.khoa` (định dạng 1 dòng hex, `sha256sum`, `features.json.khoa`, CRLF↔LF, chặn sửa đè `.khoa` và hook `conftest.py`/`sitecustomize.py`/`.pth`; lệch → `loi` `"sửa test khoá"`), rồi chạy `lenh_kiem` tiền cảnh (`PYTHONSAFEPATH=1`, trần 15 phút; mã thoát `!= 0` hoặc quá trần → `loi` kèm 1500 ký tự cuối log vào `KET-QUA.md`); đạt mới `xong`. Không có header thì giữ như cũ.
  - [test_tu_cham_khoa.py](file:///C:/linhx/wt-va1/runner/test_tu_cham_khoa.py): thêm bộ test cục bộ (không `conftest.py`, không mạng).
  - [SKILL.md](file:///C:/linhx/wt-va1/skills/le/hang-doi-may/SKILL.md): cập nhật ngắn mục `Phiếu` và `Bài học`.
- **Số test**: `python -m pytest runner -q` đạt **101 passed, 1 skipped** (`test_tu_cham_khoa.py`: **4 passed**).
- **Hash**: `37629fb` (`37629fb93ec613a65127e5805c56cbbf0c3bddd2`, nối tiếp `ffb6581`).
