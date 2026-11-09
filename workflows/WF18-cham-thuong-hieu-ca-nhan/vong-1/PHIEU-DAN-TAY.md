# Phiếu dán tay giao diện (agy, máy công ty DESKTOP-PVHR2CD), ≤ 40 phút mỗi nền tảng

Vì sao: API và giao diện chỉ trùng 6–32% (BO-SUNG-V2-CLOUD mục 3). Giao diện là cái khách thấy.

1. Lấy file: repo `fyzdfyzd/linhx-engine`, nhánh `claude/project-thread-l78gyp`, thư mục `workflows/WF18-cham-thuong-hieu-ca-nhan/vong-1/ws/lan/2026-11-09/tra-loi/`.
2. Bốn thư mục: `chatgpt-web`, `gemini-web`, `claude-web`, `perplexity-web`. Mỗi thư mục 26 file = 13 câu × 2 lượt (`P07__l1.md`, `P07__l2.md`…).
3. **Không dùng tài khoản của Linh** (AI sẽ thấy email, bộ nhớ, lịch sử và trả lời lệch; xem BAI-HOC L8). ChatGPT và Perplexity: đăng xuất, cửa sổ ẩn danh. Gemini và Claude: tài khoản phụ chưa từng chat về Linh, tắt bộ nhớ. Mỗi file: mở Chrome **máy công ty**, cửa sổ ẩn danh mới, dán nguyên câu trong file, chờ trả lời xong, chép **toàn bộ** câu trả lời kể cả link nguồn, thay dòng `(no response)`.
4. Lượt 2 phải là cửa sổ mới, không bấm "tạo lại".
5. Ghi đầu file: giờ hỏi, tên mô hình hiện trên giao diện (ví dụ GPT-5, Gemini 3 Pro), có bật tìm kiếm web không.
6. Không sửa câu hỏi, không thêm lời nhắc. Không dán thông tin đăng nhập.
7. Xong một nền tảng: commit `WF18 dán tay <nền tảng>` và push cùng nhánh.

Kiểm khi nhận: không còn file `(no response)`; mỗi file có giờ + tên mô hình.
