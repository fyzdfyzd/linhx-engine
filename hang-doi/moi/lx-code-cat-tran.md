may: may-1
loai: code
tran_phut: 40
tu_sua: 0
theo_doi: D:\linhx\wt-cat-tran

Phiếu lx-code-cat-tran (runner LINHX). Chạy mọi lệnh ở TIỀN CẢNH, không dùng background task. Mỗi 5 phút có tệp mới hoặc commit.
1. Kho nguồn là TRẠM (không dùng GitHub): `git -c sendpack.sideband=false clone -b claude/project-thread-jowxv1 git://192.168.1.136/linhx-engine.git D:\linhx\wt-cat-tran` rồi `git -C D:\linhx\wt-cat-tran checkout -b lx-code-cat-tran`.
2. Lỗi cần vá: runner/linhx_runner.py hàm chay_agy chỉ dừng agy khi "không tiến" (tính cả CPU), nên agy chạy CPU mãi thì vượt tran_phut mà không bị cắt (vd phiếu bia-502-sua-1 chạy 330 phút / trần 40).
3. VIẾT TEST TRƯỚC, commit riêng ("test(cat-tran): ..."): pytest giả lập một tiến trình con ăn CPU liên tục (vòng lặp python) thay cho agy, đặt tran_phut rất nhỏ (vd 0.05) và chứng minh: quá trần thì CẢ CÂY tiến trình bị giết (kiểm PID con không còn), chay_agy trả trang_thai 'qua_tran' (hoặc 'dung' kèm lý do qua_tran), thời gian chạy ≤ trần + 15 giây. Chạy cho thấy ĐỎ.
4. Vá linhx_runner.py: quá tran_phut thì cắt cứng bất kể CPU/đầu ra, giết cả cây (Windows: taskkill /T /F), ghi lý do qua_tran vào KET-QUA, giữ nguyên commit đã có trong thư mục làm việc. Không đổi hành vi khác. Commit "fix(cat-tran): ...". Test vừa viết phải XANH, và `python -m pytest runner -q` không đỏ thêm so với trước (ghi số trước/sau).
5. Đẩy nhánh lên trạm: `git -C D:\linhx\wt-cat-tran -c sendpack.sideband=false push origin lx-code-cat-tran`.
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá.
Trả lời KET-QUA (ngắn): dòng đầu `dat: co|khong`; SHA đỉnh lx-code-cat-tran; pytest trước/sau; test mới đỏ→xanh.
