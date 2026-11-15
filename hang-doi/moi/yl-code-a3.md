may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\yl-code-a3
phu_thuoc: yl-khoa-t1

Phiếu A3 Yên Lam: sửa cách ly dữ liệu khách. Chạy mọi lệnh ở tiền cảnh, KHÔNG dùng background task, mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi. Được dùng thợ con nhưng tất cả làm trong thư mục theo_doi.
1. `git -C C:\linhx\ifagent fetch --all`. Nếu origin/agy/yl-test-t1 chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl-code-a3 -b agy/yl-code-a3 origin/agy/yl-test-t1`.
2. Chạy nhóm test cách ly (1) trong apps/lab/test/nghiem-thu-rc6/. Lập bảng route | file:dòng | đỏ/xanh.
3. Route nào đỏ thì sửa kiểm quyền sở hữu/vai ở route đó, mỗi route một commit "A3(route): ...". Không đụng code kiosk (A2 đang sửa song song), chỉ sửa tầng API/quyền.
4. Chạy nhóm (1) + test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js`, trước đó `npm i --no-save ws` trong packages/character), log thô vào bang-chung/yl-code-a3/ và commit.
5. Push `agy/yl-code-a3`.
CẤM: deploy, gửi mail, in khoá/mật khẩu, xoá dữ liệu, sửa test cũ, sửa bất kỳ file nào trong apps/lab/test/nghiem-thu-rc6/ (kiểm `sha256sum -c apps/lab/test/nghiem-thu-rc6/KHOA.sha256` trước khi push, lệch là tự trượt), sửa TIEU-CHUAN/CHUAN/KHUNG, tự sinh ảnh/video sản phẩm bằng AI, push nền qdzzr4. Màn chưa có khung duyệt thì không build, ghi CHUA_CO_KHUNG. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co` hoặc `dat: khong`; SHA đỉnh; bảng route | trước | sau; số pass/fail lab đủ; sha256sum -c OK/KHÔNG.
