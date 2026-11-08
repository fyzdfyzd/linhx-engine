---
name: vong-ads
description: Một vòng tối ưu quảng cáo Meta/TikTok/Google kiểu Fastlane - đọc kết quả mẫu quảng cáo (CSV xuất từ Ads Manager hoặc qua MCP), chấm thắng/thua có xác suất, đề xuất dời ngân sách và brief biến thể mới. Dùng khi Linh nói "chạy vòng ads", "tối ưu ads", "mẫu nào thắng".
---
# Vòng ads (1 vòng = 1 ngày hoặc 1 tuần)

Agent KHÔNG tự tiêu tiền. Mọi lệnh ghi (tạo ad, đổi ngân sách, tắt ad) xuất ra `actions.json` để người duyệt; khi có MCP thì tạo ad ở trạng thái PAUSED.

## B1. Lấy số
- Có Meta Ads connector chính chủ hoặc pipeboard meta-ads-mcp: gọi `get_insights` mức ad, 7 ngày, cột spend, impressions, clicks, purchases (hoặc leads/tin nhắn), revenue.
- Không có: Linh xuất CSV từ Ads Manager. Cột bắt buộc: `ad_id,ten,spend,impressions,clicks,conv,revenue`. TikTok/Google đổi tên cột về đúng các cột này.

## B2. Chấm
`python scripts/vong.py ket-qua.csv --muc-tieu conv --ngan-sach-ngay 2000000 --ra out/`
Script tính CTR, CVR, CPA, ROAS và xác suất mỗi ad tốt hơn trung bình tài khoản (Beta-Binomial, Monte Carlo). Phân loại:
- TĂNG: P ≥ 0,9 và đủ 1.000 lượt hiển thị → +20% ngân sách (không quá 20%/lần để khỏi reset learning).
- TẮT: P ≤ 0,1 và đã tiêu ≥ 2 lần CPA mục tiêu (hoặc ≥ 2 lần CPA trung bình).
- CHƯA ĐỦ: chưa đủ dữ liệu, giữ nguyên.
- GIỮ: còn lại.

## B3. Đọc ngách (tùy chọn, ghép LAB077)
Lấy 10-20 mẫu đang chạy lâu của đối thủ trong Meta Ad Library (ad chạy > 30 ngày coi là đang lời). Bóc hook, định dạng, lời hứa, CTA bằng skill `tai-tao-flow`.

## B4. Brief biến thể
Với mỗi ad TĂNG: viết 3 biến thể chỉ đổi MỘT yếu tố (hook 3 giây đầu / ảnh bìa / CTA), giữ phần còn lại. Ghi vào `brief-bien-the.md`. Ảnh/video dựng bằng LAB059 (phim code) hoặc Gemini; không để GPT vẽ cả mẫu chữ Việt.

## B5. Kiểm tuân thủ trước khi đẩy
Kiểm từng biến thể: không hứa chữa bệnh, không "cam kết 100%", không trước/sau cơ thể, sản phẩm thuộc nhóm phải xin xác nhận nội dung quảng cáo (thực phẩm chức năng, mỹ phẩm, y tế, giáo dục có cấp bằng) thì đánh dấu CHỜ GIẤY.

## B6. Gói cho người duyệt
Đưa `DE-XUAT.md` (bảng thắng/thua, dời ngân sách, brief) và `actions.json`. Linh duyệt rồi mới gọi MCP ghi. Ghi kết quả vòng vào `lich-su.csv` để vòng sau so.
