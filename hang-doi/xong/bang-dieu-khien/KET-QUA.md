phieu: bang-dieu-khien
may: may-2
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 16.54
token: vao=203625 ra=60295

Đang chạy bộ kiểm thử tổng thể `python -m pytest runner -q` để xác nhận toàn bộ test đều đạt trước khi commit và push.
Đang hoàn tất kiểm thử sau rebase và push commit lên nhánh `claude/project-thread-jowxv1`.
Đã dựng và cài đặt thường trực bảng theo dõi web hàng đợi trên **may-2**:

- **Địa chỉ truy cập**: `http://192.168.1.136:8090` (cục bộ: `http://localhost:8090`, API JSON: `http://192.168.1.136:8090/api/trang-thai` — đều trả HTTP `200`).
- **Số test đạt**: **7/7** trong [test_bang.py](file:///C:/linhx/wt-bang/runner/bang/test_bang.py) (toàn bộ `python -m pytest runner -q`: **37/37** đạt).
- **Hash commit**: `aa52a58650c860d27d8029f97d5131850572f065` (`aa52a58`, nhánh `claude/project-thread-jowxv1`).

### Các tệp đã tạo trong `runner/bang/`
- [bang.py](file:///C:/linhx/wt-bang/runner/bang/bang.py): Máy chủ HTTP chỉ đọc (Python stdlib, cổng `8090`), tự động `git fetch` nhánh `hang-doi` mỗi 30 giây vào `C:\linhx\bang-hang-doi`, phục vụ `/` (tự làm mới 30s, 4 mục tiếng Việt, tô màu `xong`/`loi`/`dung` và tô đỏ máy quá 30 phút không hoạt động), `/phieu/<id>` xem `KET-QUA.md`, cùng `/api/trang-thai`.
- [chay-an-bang.vbs](file:///C:/linhx/wt-bang/runner/bang/chay-an-bang.vbs) & [cai-bang.ps1](file:///C:/linhx/wt-bang/runner/bang/cai-bang.ps1): Đã chạy trên `may-2`, đăng ký lịch `LINHX-Bang` chạy ẩn khi đăng nhập và mở cổng TCP `8090` trên tường lửa Windows cho mạng nội bộ (`Private`).
