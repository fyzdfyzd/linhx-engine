# Tiêu chuẩn chấm chữ trên slide (bản 1, 17/11/2026)

Dùng cho deck keynote CSMO 19/11 và mọi deck trình bày sau này.
Mỗi tiêu chí chấm 1–5. **Đạt khi mọi tiêu chí ≥ 4** theo trung vị của 3 người chấm (Claude, ChatGPT, Gemini; người viết không chấm bài mình). Điểm 3 = "sạch nhưng vội", chưa đạt.

## A. Cấp từng slide

| Mã | Tiêu chí | 5 điểm trông thế nào | Lỗi hay gặp (trừ điểm) |
|---|---|---|---|
| T1 | Hiểu ngay | Người lạ đọc 5 giây, không cần diễn giả, nói lại được slide muốn nói gì | Tiêu đề là nhãn ("Công thức", "Đo"), câu cần ngữ cảnh slide khác mới hiểu |
| T2 | Đủ ý, không cụt | Câu mang ý lớn có đủ chủ ngữ, vị ngữ và lý do | Câu kiểu khẩu hiệu 4–6 chữ gánh cả luận điểm; "Cửa sổ đang mở."; "Năm bước, năm chỗ rơi." |
| T3 | Giọng người Việt nói | Đọc to lên nghe như một người Việt đứng trên sân khấu nói với đồng nghiệp | Xem danh sách cấm mục C |
| T4 | Một slide một ý | Bỏ bất kỳ dòng nào thì slide mất nghĩa | Tiêu đề, phụ đề, chú thích nói lại cùng một ý; hai ý chen nhau |
| T5 | Đúng và gọi được tên | Số có nguồn, chủ thể có tên (hãng nào, nghiên cứu nào, năm nào); số nào cũng gánh luận điểm | "Một nghiên cứu", "các chuyên gia"; số để trang trí; ghi "cần kiểm bản gốc" mà vẫn chiếu |
| T6 | Vừa sân khấu | Chữ hiển thị ≤ 30 chữ (slide bảng ≤ 60); tiêu đề ≤ 2 dòng; phần dài để ở lời nói | Đoạn văn 3–4 câu trên slide chuyện |
| T7 | Hợp người nghe | CMO, CSMO Việt nghe là hiểu; tiếng Anh chỉ giữ chữ họ dùng hằng ngày (AI, agent, claim) | "Verifiable Data", "Reputation" để trần không dịch; ẩn dụ dịch từ tiếng Anh |

## B. Cấp cả deck

| Mã | Tiêu chí | 5 điểm trông thế nào |
|---|---|---|
| D1 | Xương sống một tầng | Chỉ một khung dẫn cả bài; mọi khung phụ (chỉ số, bước, lớp) treo vào khung chính, không đứng song song |
| D2 | Đọc tiêu đề liền là ra câu chuyện | Ghép tiêu đề 27 slide thành một bài văn đọc trơn, có mở, có thắt, có cởi |
| D3 | Lời hứa giữ được | Mở bài hứa gì, phần kết trả đúng cái đó; câu hỏi 60 giây được trả lời ở cuối |
| D4 | Ba thứ mang về | Khán giả nói lại được: một con số về mình, một câu nói với sếp, một việc trước thứ Hai |
| D5 | Không thiếu, không lặp | Không có "kiểu sai 1, kiểu sai 3" mà thiếu kiểu 2; một ý không nói ở hai slide |

## C. Danh sách cấm (giọng AI)

1. "Không còn là… mà là…", "không phải… mà là…" (trừ 1 lần cho câu chốt cả bài).
2. Câu đối hai vế liên tiếp ("X thì…, còn Y thì…"), quá 1 lần trong deck.
3. Câu ba nhịp liệt kê cho kêu ("Nhanh hơn. Rẻ hơn. Đúng hơn.").
4. Ẩn dụ dịch: "cửa sổ đang mở", "chìa khoá", "hành trình", "bức tranh", "cuộc chơi", "lời giải".
5. Láy cụm câu trước để mở câu sau.
6. "Nghĩa là…" mở câu để giảng lại câu trước.
7. Dấu gạch dài, dấu ngoặc kép trang trí, chữ in hoa cả câu để nhấn.
8. Tiêu đề là danh từ trơ ("Công thức", "Đo", "Kết").
9. Chủ thể chung chung: "nhiều doanh nghiệp", "người ta", "một nghiên cứu".

## D. Thang tham chiếu

- Giọng: 7 bài Linh đã đăng báo (LAB049, câu trung vị 27 chữ, xưng "tôi" tiết chế). Trên slide câu ngắn hơn bài báo nhưng không cụt.
- Linh chê v7: "cụt, giọng AI rõ, cấu trúc khó hiểu" → T2, T3, D1 là ba tiêu chí nặng nhất.

## E. Cách chấm

Người chấm trả JSON: `{"slide": n, "T1":..,"T7":.., "loi": ["câu nguyên văn → vì sao → gợi ý"]}` cho từng slide và `{"D1":..,"D5":.., "nhan_xet": ".."}` cho cả deck. Mỗi lỗi phải dẫn nguyên văn câu bị chê.
