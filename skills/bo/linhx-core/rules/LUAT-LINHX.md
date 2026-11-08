# Luật làm việc LINHX LAB

Áp dụng cho mọi phiên Claude Code và Antigravity trong thư mục LINHX. Đây là nguồn sự thật duy nhất; hook mở phiên và lệnh `agy-install` đều đọc file này.

1. **Một lab = một folder.** Mọi thứ của lab nằm trong folder đó: `OVERVIEW.md`, `LOG.md`, `PLAN.md`, `src/ data/ output/ refs/`. Tên `LAB0NN-TEN-NGAN` hoặc `EXP-YYYYMMDD-NN-ten-ngan`. Cập nhật `INDEX.md` khi mở hoặc đóng lab.
2. **Nghiên cứu nền là đọc code thật.** Trước khi đề xuất, clone và đọc code các repo cùng loại, kể cả repo Trung Quốc: pipeline, prompt, data model, license. Không đề xuất chỉ dựa trên bài tổng hợp hay README.
3. **Sản phẩm lab là skill hoặc plugin** cho Claude Code hay Antigravity (SKILL.md cộng script), không phải app hay web app riêng, trừ khi Linh yêu cầu.
4. **Luôn đưa 3–4 phương án**, mỗi phương án tách module rõ, có một khuyến nghị kèm lý do. Dùng skill `de-xuat-phuong-an`.
5. **Không đứng chờ.** Khi chờ Linh duyệt mà 10 phút không có tương tác, coi như duyệt theo khuyến nghị và làm tiếp. Ghi vào sổ quyết định trong `PLAN.md`. Ngoại lệ: việc không hoàn tác được (xoá, gửi ra ngoài, nộp hồ sơ, đăng bài, thanh toán) thì phải chờ Linh.
6. **Ghi ra đĩa, đừng tin trí nhớ.** Ngữ cảnh là RAM, file là ổ cứng. Kế hoạch ở `PLAN.md`, tiến độ ở `LOG.md`, phát hiện ở `refs/` hoặc `01-NGHIEN-CUU-NEN.md`. Dùng skill `ke-hoach-lab`.
7. **Báo xong phải có bằng chứng mới**: lệnh đã chạy và kết quả, file đã mở lại, link. Dùng skill `xac-minh-truoc-khi-bao-xong`.
8. **Viết tiếng Việt**, câu đầy đủ, dẫn đầu bằng kết luận. Không thay Linh nộp, đăng ký, gửi email hay đăng bài.
9. **Viết code theo chuẩn Karpathy:** nêu giả định trước khi code, tối giản (không thêm thứ chưa ai cần), sửa đúng chỗ (mỗi dòng đổi đều truy được về yêu cầu), mỗi bước có cách kiểm. Chi tiết trong skill `chuan-code`.
10. **Sửa có giới hạn, lỗi thành luật.** Một bước kiểm không đạt thì sửa lại riêng bước đó, tối đa 3 lần; quá 3 lần thì dừng, báo blocker kèm bằng chứng. Gặp cùng một lỗi lần thứ hai thì thêm một luật ngắn vào file này. Luật phải áp lần nào cũng như lần nào (format, lint, chặn đường dẫn) thì làm thành hook hoặc script trong `linhx-core`, không viết thành lời dặn.
