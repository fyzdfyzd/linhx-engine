# Sổ Vấn Đề (.handoff/VAN-DE.md)

## OPEN

### [VD-003] Biến `$B` chưa expand trong đường dẫn đích của `T-G1-CUNGAI.md` — Trạng thái: RESOLVED
- **Thời gian & Phiên**: 2026-11-11 07:40 · `T-G1-CUNGAI` · Nhánh: `(no-git)`
- **Hiện tượng / Vấn đề**: Dòng 4 của `.handoff/tasks/T-G1-CUNGAI.md` ghi đường dẫn đích là `D:\LINHX\LAB\LAB122-BRAND-ID-4BU$B\01-tham-chieu\THAM-CHIEU.md` (lỗi escape biến `$B`), trong khi dòng 5 và dòng 7 chỉ định rõ `CUNGAI\01-tham-chieu\`.
- **File / Lệnh liên quan**: `.handoff/tasks/T-G1-CUNGAI.md:L4-L7`, thư mục có sẵn `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\`.
- **Đã thử / Cách xử lý tạm**: Xác định `$B = \CUNGAI`, ghi toàn bộ kết quả vào `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI\01-tham-chieu\THAM-CHIEU.md` và `CUNGAI\01-tham-chieu\anh\`, không tạo thư mục rác `LAB122-BRAND-ID-4BU$B`.
- **Cần Claude / Anh Linh**: Không cần thao tác thêm.

### [VD-002] Biến `$B` chưa expand trong đường dẫn đích của `T-G1-TUVA.md` — Trạng thái: RESOLVED
- **Thời gian & Phiên**: 2026-11-11 07:38 · `T-G1-TUVA` · Nhánh: `(no-git)`
- **Hiện tượng / Vấn đề**: Dòng 4 của `.handoff/tasks/T-G1-TUVA.md` ghi đường dẫn đích là `D:\LINHX\LAB\LAB122-BRAND-ID-4BU$B\01-tham-chieu\THAM-CHIEU.md` (cùng lỗi escape biến shell `$B` như `[VD-001]`), trong khi dòng 5 và dòng 7 ghi rõ `TUVA\01-tham-chieu\`.
- **File / Lệnh liên quan**: `.handoff/tasks/T-G1-TUVA.md:L4-L7`, thư mục có sẵn `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\TUVA\01-tham-chieu\`.
- **Đã thử / Cách xử lý tạm**: Xác định `$B = \TUVA` theo dòng 5, dòng 7 và thư mục `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\TUVA\01-tham-chieu\` có sẵn; ghi toàn bộ đầu ra vào `TUVA\01-tham-chieu\THAM-CHIEU.md` và `TUVA\01-tham-chieu\anh\`, không tạo thư mục rác `LAB122-BRAND-ID-4BU$B`.
- **Cần Claude / Anh Linh**: Không cần thao tác thêm.

### [VD-001] Biến `$B` chưa expand trong đường dẫn đích của `T-G1-UNIKON.md` — Trạng thái: RESOLVED
- **Thời gian & Phiên**: 2026-11-11 06:58 · `T-G1-UNIKON` · Nhánh: `(no-git)`
- **Hiện tượng / Vấn đề**: Dòng 4 của `.handoff/tasks/T-G1-UNIKON.md` ghi đường dẫn đích là `D:\LINHX\LAB\LAB122-BRAND-ID-4BU$B\01-tham-chieu\THAM-CHIEU.md` (lỗi escape biến shell `$B` khi tạo file đề).
- **File / Lệnh liên quan**: `.handoff/tasks/T-G1-UNIKON.md:L4`, thư mục có sẵn `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\`.
- **Đã thử / Cách xử lý tạm**: Đối chiếu cây thư mục workspace đã tạo sẵn `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\`, xác định `$B = \UNIKON` và xuất toàn bộ kết quả vào `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\THAM-CHIEU.md` cùng `D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON\01-tham-chieu\anh\`. Không tạo thư mục rác `LAB122-BRAND-ID-4BU$B`.
- **Cần Claude / Anh Linh**: Không cần thao tác thêm (ghi nhận để Claude biết khi đọc kết quả).
