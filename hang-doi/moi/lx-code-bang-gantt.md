may: may-2
loai: code
tran_phut: 30
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\wt\bang-du-an
phu_thuoc: lx-code-bang-du-an

Phiếu nối tiếp lx-code-bang-du-an: tab "Dự án" thành GANTT rút gọn theo giờ. Việc PHỤ, ưu tiên thấp, cùng luật cấm như phiếu trước (không khởi động lại bảng đang chạy, không đụng runner, tiền cảnh, KHÔNG background task, mỗi 5 phút có file mới/commit).
1. Làm tiếp trên nhánh `agy/bang-du-an` trong C:\linhx\wt\bang-du-an (`git pull`).
2. Mỗi bước trong hang-doi/du-an/*.json có `du_kien.bat_dau`/`du_kien.xong`. Mỗi bước một hàng: thanh mờ = dự kiến; thanh đậm = thực tế (giờ nhận phiếu đầu → giờ xong phiếu cuối; đang chạy thì kéo tới hiện tại); vạch dọc = giờ hiện tại; vạch đỏ = `han`. Bước trễ > 15 phút so với dự kiến tô cam, ghi "trễ N phút". Trên cùng 1 câu: "Dự kiến xong HH:MM (trễ/sớm N phút)" tính từ bước cuối.
3. 390px: danh sách dọc, mỗi bước "dự kiến 12:10–14:40 · thực tế 12:15–…" + chấm trạng thái. KHÔNG làm Kanban riêng (tab Phiếu đã có mới/đang/xong).
4. Test: thanh thực tế đúng giờ với dữ liệu giả; bước trễ tô cam; thiếu du_kien thì không vỡ. Chạy `python -m pytest runner -q` và `python -m pytest tests/nghiem-thu -q`.
5. Chụp lại ảnh du-an-*.png (390×844, 1440×900, sáng/tối), commit, push `agy/bang-du-an`.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co`/`dat: khong`; SHA; test pass/fail; đường dẫn ảnh.
