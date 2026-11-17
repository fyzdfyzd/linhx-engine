may: may-3
loai: code
tran_phut: 40
theo_doi: D:\linhx\wt-dien-gia-v4

Phiếu DIỄN GIẢ v4 (chuyển các bản sửa dien-gia-v3 sang dòng ứng viên prod). Nhánh mo-test-17-11 trên origin có các commit dien-gia-v3 (vd 4699d55f bỏ logo VSM/CSMO -> avatar chữ cái đầu ở bộ chọn booth; db12fa2d khử trùng chức danh "Chủ tịch · Chủ tịch" Lê Quốc Vinh; và các commit tiêu điểm khuôn mặt nếu có). cherry-pick các commit đó (git log origin/mo-test-17-11 --oneline -15 để tìm) sang nhánh mới; giải xung đột giữ cả bản sửa tràn 47 diễn giả đã có trên lam-gap.
Làm nốt mục CHẶN còn thiếu: T2 tạp chí — MY FAVORITE SPEAKER mỗi mục "Tên · Đơn vị ngắn" 1 dòng kẹp, tối đa 3 diễn giả, đo chiều cao thực đẩy khối BA TỪ KHOÁ xuống; thêm test khoá MỚI: 3 diễn giả chức danh dài nhất (Đào Trung Thành, Đào Cẩm Thuỷ...) không chồng. Đếm số diễn giả có ảnh thật / 48 ghi vào KET-QUA.
CÁCH LÀM: git clone https://github.com/fyzdfyzd/ifagent D:\linhx\wt-dien-gia-v4 ; cd D:\linhx\wt-dien-gia-v4 ; git checkout -b dien-gia-v4-17-11 origin/lam-gap-17-11 (bản 3fd424b1 = ứng viên prod). Cài phụ thuộc theo README/package.json của apps/lab. MỌI LỆNH TIỀN CẢNH, không background task. Commit + PUSH sau mỗi mục (hết giờ không mất việc). Không sửa test khoá nghiem-thu-*; test khoá 10/11 phải xanh. KHÔNG deploy staging/prod (máy 2 gộp và deploy). Không in/đổi khoá. KET-QUA ≤2000 ký tự: SHA nhánh, test, còn thiếu.