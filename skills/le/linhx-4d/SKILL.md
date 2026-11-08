---
name: linhx-4d
description: Giao việc theo quy chuẩn 4D (Double Diamond x 100 Tasks x phòng Tam Quốc) cho mọi dự án - giáo trình, phần mềm OPC, ứng dụng, slide, kế hoạch. Dùng khi Linh nói "giao việc 4D", "mở chiến dịch", "theo quy chuẩn 4D".
---

# linhx-4d (LAB105, bản 0.1)

Đọc `../../QUY-CHUAN-4D.md` trước khi dùng.

## Các bước
1. Linh đưa ý định 4 câu: làm gì, cho ai, xong là khi nào, ngân sách.
2. Khổng Minh (Claude) chạy `python scripts/qc4d.py moi <loai> <thu_muc> "<tên>"`.
   - `loai` là một trong: giao-trinh, phan-mem-opc, ung-dung, slide, ke-hoach.
3. Sửa phiếu cho khớp việc thật, rồi chạy `qc4d.py kiem <thu_muc>`. Phải ra DAT mới được giao.
4. Giao từng phiếu cho tướng ghi trong phiếu. Mỗi phiếu một phiên mới, tối đa 40 phút.
   - Nghiên cứu sâu thì gửi Gemini Deep Research.
   - Quét thì dùng LINHX crawler.
   - Ảnh thì dùng Gemini Ultra hoặc ChatGPT Plus trên Chrome máy cty.
5. Cuối pha chạy `qc4d.py cong <thu_muc> <PHA>`.
   - DAT thì Bàng Thống chấm theo thang high standard.
   - CHUA_DAT thì giao Hoa Đà hoặc thợ sửa, tối đa 3 vòng.
6. Ở cổng DEFINE và DELIVER, gửi Linh duyệt kèm một trang tóm tắt và ảnh bằng chứng.

## Luật
- Claude không làm thợ. Script chặn phiếu giao Claude các việc lam, viet, nghien-cuu, quet, anh.
- Không có ảnh thì coi như chưa test. Mỗi TH-xxx ở pha DEFINE phải có dòng DAT kèm ảnh ở pha DELIVER.
- Script chỉ đo, không phán. Kết luận cuối do người chấm đưa ra.
