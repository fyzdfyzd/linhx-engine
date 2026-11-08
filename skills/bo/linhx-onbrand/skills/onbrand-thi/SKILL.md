---
name: onbrand-thi
description: Đo năng lực bám chuẩn design của nhiều người hoặc nhiều AI trên cùng một brand: ra 5 đề chuẩn, thu bài, chấm onbrand từng bài, xếp hạng và chỉ ra điểm yếu theo mục. Dùng khi tuyển hoặc đánh giá designer, hoặc so công cụ AI tạo ảnh.
---

# Thi bám chuẩn design

## Bước
1. Ra đề: lấy `${CLAUDE_PLUGIN_ROOT}/data/de-thi.json`, thay nội dung chữ cho hợp brand nếu cần, xuất thành `brands/<brand-id>/07-bai-thi/DE-THI.md` kèm link guideline và thư mục logo. Cùng đề, cùng chữ cho mọi người để chỉ đo design.
2. Thu bài: `07-bai-thi/<ten-nguoi>/<ma-de>.<ext>`. Với AI (GPT Image, Gemini, Flow...), ghi prompt đã dùng vào `07-bai-thi/<ten-ai>/PROMPT.md`.
3. Chấm từng bài bằng skill onbrand-cham, lưu `08-ket-qua/<ten-nguoi>-<ma-de>.json`, thêm trường `"ten_bai": "<ten-nguoi> · <ma-de>"`.
4. Báo cáo: `onbrand.py bao-cao 08-ket-qua/*.json --ra 08-ket-qua/XEP-HANG.html`.
5. Hồ sơ năng lực mỗi người: điểm trung bình, mục yếu nhất (mục có tỉ lệ thấp nhất trung bình qua 5 đề), lỗi lặp lại ≥2 lần. Một người một đoạn ba câu.

## Lưu ý
- Đề D4 (avatar) và D5 (ảnh người) phân loại rõ nhất: AI tạo ảnh hay vẽ lại logo sai, designer hay quên vùng an toàn.
- Không công bố điểm từng người ra ngoài khi người dùng chưa đồng ý.
