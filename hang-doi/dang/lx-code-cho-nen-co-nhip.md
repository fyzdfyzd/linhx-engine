may: may-2
loai: code
tran_phut: 30
khong_tien_phut: 20
tu_sua: 1
theo_doi: C:\linhx\wt\chan-cho-nen
phu_thuoc: lx-code-chan-cho-nen
nhan: may-2 2026-11-15T13:27:45+0700

Phiếu nối tiếp lx-code-chan-cho-nen. Linh 15/11: CHO PHÉP chạy nền nếu có log + nhịp. Chạy mọi lệnh tiền cảnh, mỗi 5 phút có file mới/commit. KHÔNG khởi động lại runner đang chạy.
1. Làm tiếp nhánh `agy/chan-cho-nen` (`git pull`).
2. Đổi luật dừng: gặp `waiting up to .* background task` / `root agent idle` thì vào chế độ CANH NỀN thay vì dừng ngay. Còn file mới/đổi trong theo_doi hoặc log tác vụ nền tăng dòng trong 5 phút gần nhất → để chạy. 5 phút im hoàn toàn → dừng cả cây, lý do `cho-nen-im-lang`, phiếu -sua- câu đầu: "Lượt trước chạy tác vụ nền không ghi log rồi chờ. Tác vụ nền phải có timeout, ghi log vào thư mục theo_doi; dev server/watch phải tắt khi xong."
3. Đổi câu runner tự chèn (CAU_NHAC_TIEN_CANH) thành: "Được chạy tác vụ nền nếu mỗi tác vụ có timeout, ghi log vào thư mục theo_doi, và bạn tự kiểm/tắt nó; server chạy mãi phải tắt trước khi kết thúc."
4. Bảng 8090: phiếu đang ở chế độ canh nền hiện nhãn "đang chờ nền · log cuối N phút trước".
5. Sửa test runner/test_chan_cho_nen.py: có log tăng → không dừng; im 5 phút → dừng đúng lý do. `python -m pytest runner -q` + `python -m pytest tests/nghiem-thu -q`. Push `agy/chan-cho-nen`.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co`/`dat: khong`; SHA; test pass/fail.

nhip: 13:30 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
