---
name: brand-check
description: Kiểm sức khoẻ thương hiệu trong thời đại AI agent theo chuẩn ABC (GEO, AEO, AI visibility, độ đúng, nhất quán, được đề xuất, truth signal, agent-readiness). Dùng khi được hỏi "AI nói gì về thương hiệu X", "ChatGPT có gợi ý mình không", audit GEO/AEO, brand health check, kiểm thương hiệu cho khách IF Agent, hay chuẩn bị báo cáo quét thương hiệu.
---

# Brand check chuẩn ABC (điều phối)

Chuẩn đầy đủ: `CHUAN-ABC-v1.md` trong LAB036. Luật: AI chỉ gán nhãn, code tính điểm; không đo thứ hạng; lặp để có sai số; tách Nhớ (không tra web) và Tìm (có tra web); không hiện con số nào không đếm được.

CLI: `python <plugin>/scripts/brandcheck.py <lệnh> -w <thư mục thương hiệu>`. Thư mục làm việc mặc định `D:\LINHX\BRAND-CHECK\<slug>` nếu người dùng không chỉ chỗ khác.

## Luồng (báo người dùng đang ở bước nào)
1. **Bảng sự thật** → skill `bang-su-that`. Không có bảng sự thật thì chỉ đo được Có mặt và Thị phần nhắc tên; nói rõ điều đó.
2. **Chọn gói và sinh câu hỏi**: `cau-hoi --goi N|C|S`. Nhanh 12 câu (demo, mồi lead), Chuẩn 25 câu (audit lần đầu), Sâu 40–60 câu (theo dõi, so đối thủ). Đọc lại danh sách câu với người dùng, sửa câu nào không giống khách thật hỏi (thêm vào `abc.cau_hoi_them` trong brand-facts.json).
3. **Hỏi AI** → skill `hoi-ai`. Báo trước số lần gọi. Mặc định: `claude-tim,claude-nho,agy` × 3 lượt, cộng `dan-tay:chatgpt` nếu người dùng chịu dán.
4. **Chấm** → skill `cham`.
5. **Kiểm tín hiệu** → skill `kiem-tin-hieu`.
6. **Báo cáo và sửa** → skill `bao-cao-va-sua`.

Một lệnh cho cả 3–6 khi đã có bảng sự thật và câu hỏi: `tat-ca --mo-hinh claude-tim,claude-nho,agy --luot 3 --giam-khao claude`.

## Khi nào dừng hỏi người dùng
- Trước khi gọi API tốn tiền (Gemini, OpenRouter): báo số lần gọi.
- Trước khi dùng báo cáo với khách: mọi dòng Sai/Bịa/Nhầm/Cũ phải có người xác nhận (mở file nguyên văn trong `tra-loi/`).
- Không chạy cho thương hiệu của chính Linh khi làm ví dụ công khai (luật bài nói CSMO: ẩn danh ví dụ).

## Tự kiểm
`python brandcheck.py tu-kiem` (không gọi mạng). Phải in XANH trước khi báo xong mọi sửa đổi code.
