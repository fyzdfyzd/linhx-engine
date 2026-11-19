May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-sua-7
nhan: may-2 2026-11-19T07:49:22+0700

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Push mỗi bước. KHÔNG gọi AI thật, trừ bước 3 (đúng 3 câu Grok, ≤ 0,05 USD).
Nhánh agy/bhc-sua-7 từ agy/bhc-sua-6 (ead66ac). Claude soi báo cáo CSMO v2 2026-11-19-csmo-90481a4a, chấm 8,8. Sửa 3 lỗi:
1. Nhãn trường lọt vào câu: "Sự thật: Công ty / người đứng sau: Câu lạc bộ …" (landing chương 1, PDF trang 2, hộp Điều cần lưu ý nhất). Câu sự thật phải là câu tự nhiên, bỏ nhãn trường bảng sự thật (vd "Sự thật: CSMO là Câu lạc bộ … do VACD thành lập." hoặc tối thiểu chỉ phần giá trị). Test khoá: chữ hiển thị không chứa nhãn trường của FACT_FIELDS ("Công ty / người đứng sau:", "Năm thành lập:" …). Kicker "Lời khuyên thẳng thắn của AI" chỉ dùng khi câu trích là lời khuyên; câu sai sự thật dùng "AI đang nói sai về <tên>".
2. Quản trị chi tiết lượt ghi "Quét lúc 19/11/2026 · 00:07" là giờ UTC; phải theo giờ Việt Nam (07:07). Kiểm mọi chỗ hiện giờ (quản trị, landing, PDF, mail). Test khoá với TZ=UTC.
3. Làn Grok quá thời gian 34/42 (trần 20 s). Đặt mặc định thời gian chờ riêng cho grok-tim 60 s (giống cách Claude nhân đôi), thử thật 3 câu CSMO bằng x-ai/grok-4.7 đo thời gian; nếu > 45 s/câu thì thử bản nhanh cùng họ (vd x-ai/grok-4.7-fast hoặc bản mới nhất có chữ fast trong /api/v1/models) và chọn bản nhanh làm mặc định. Ghi thời gian + chi phí vào KET-QUA.
4. npm test + node scripts/lint.js xanh, golden VNM/IFA không đổi. Dựng lại PDF + landing CSMO v2 từ JSON (không quét lại) trên máy, chụp lại 06d chương 01–02 (1280, 360) và PDF trang 1–3 vào bang-chung/bhc-mau-csmo-v2-sua/ trên nhánh agy/bhc-sua-7. KHÔNG deploy staging.
CẤM: deploy, in khoá. KET-QUA: dat, SHA, số test, câu trước/sau mục 1, model Grok chọn + thời gian.

nhip: 08:01 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
