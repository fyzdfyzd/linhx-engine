# Đề viết lại chữ cho deck keynote CSMO 19/11

## Bối cảnh
Diễn giả: Đinh Trần Tuấn Linh (CTO, If Agent). Keynote 20 phút + 5 phút hỏi đáp, 14:45 ngày 19/11/2026, VSMCamp & CSMO Summit 2026, Topic 07 "Trust in the Age of Agents". Người nghe: khoảng 300 giám đốc marketing, giám đốc thương hiệu Việt Nam. Tên bài: "Từ Brand Claim đến Verifiable Truth".

Một câu cho cả bài: khách hàng mới của thương hiệu là một cái máy chọn hộ người, và nó chỉ tin thứ kiểm được.
Khán giả phải mang về: (1) một con số về chính thương hiệu mình, đo ngay trong phòng; (2) một câu nói với sếp; (3) một việc làm trước thứ Hai.

## Bản hiện tại bị chê vì sao
Diễn giả chê bản v7 (đính kèm): chữ cụt, giọng AI rõ, cấu trúc khó hiểu. Cụ thể Claude soi được:
- Năm khung chạy song song: 4 chặng Người → Agent → Agent → Người, công thức nhân, 3 kiểu sai (mà deck chỉ có kiểu 1 và 3), 4 chỉ số, 5 bước, 5 lớp bằng chứng. Người nghe không biết mình đang ở đâu.
- Câu khẩu hiệu cụt: "Cửa sổ đang mở.", "Năm bước, năm chỗ rơi.", "Phép nhân, không phải phép cộng."
- Tiêu đề nhãn trơ: "Công thức", "Đo", "Kết", "30 ngày".
- Tiếng Anh để trần: "Verifiable Data", "Reputation".

## Việc của anh/chị
Viết lại toàn bộ chữ trên slide và lời nói đi kèm theo **phương án cấu trúc được giao** (dưới đây). Đọc kỹ `TIEU-CHUAN-TEXT.md`: bài sẽ được chấm đúng theo thước đó.

### PA-A · Bốn chặng (một khung duy nhất)
Cả bài đi theo 4 chặng Người giao quyền → Agent của khách hỏi và đối chiếu → Agent (máy) của thương hiệu trả lời → Người đứng sau chịu trách nhiệm. Mỗi chặng là một phần: một chuyện thật, chỗ gãy, việc sửa. 4 chỉ số đo và 5 lớp bằng chứng phải treo vào chặng phù hợp, không đứng riêng. Có thể bỏ "5 bước agent đọc".

### PA-B · Ba câu hỏi của một giám đốc marketing
Phần 1: AI đang nói gì về thương hiệu tôi? (đo, 4 chỉ số, kiểu sai). Phần 2: Vì sao nó nói vậy? (agent đọc và đối chiếu ra sao, chuyện thật). Phần 3: Tôi sửa gì trước thứ Hai? (claim sang bằng chứng, 30 ngày). Bốn chặng chỉ dùng một slide ở đầu làm bối cảnh.

### PA-C · Một công ty đi suốt bài
Nhân vật chính là công ty Việt "bị AI tả thành hãng dược bán kem bôi khớp" (đã ẩn danh). Theo họ đi qua: phát hiện → đo → tìm chỗ gãy → sửa → 30 ngày sau hỏi lại. Các chuyện quốc tế (OpenAI, Google–Walmart, Air Canada, Amex) chỉ làm bằng chứng phụ.

## Luật cứng
1. Chỉ dùng số và chuyện có trong kịch bản v5 và deck v7. Không thêm số mới. Chuyện CCTV đồng hồ giả chưa kiểm bản gốc: nếu dùng thì ghi [CHƯA KIỂM].
2. Không nêu tên thương hiệu riêng của diễn giả; ví dụ Việt Nam để ẩn danh.
3. 18–24 slide cho 20 phút. Giữ mở đầu "60 giây cầm điện thoại" và slide QR "Soi thương hiệu trong 10 phút".
4. Chữ hiển thị mỗi slide ≤ 30 chữ (slide bảng ≤ 60). Tiêu đề là một câu có nghĩa, ≤ 2 dòng.
5. Tiếng Việt tự nhiên như người nói, xưng "tôi", gọi khán giả "anh chị". Không theo danh sách cấm mục C.

## Định dạng trả về
Bảng Markdown, mỗi slide một dòng:
| # | Tiêu đề (hiện trên slide) | Chữ phụ hiện trên slide | Hình/số gợi ý | Nguồn | Lời nói (≤ 80 chữ) |

Sau bảng: 3 dòng "Đọc tiêu đề liền" (ghép mọi tiêu đề thành đoạn văn) để tự kiểm D2.


---
# TIÊU CHUẨN CHẤM
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


---
# KỊCH BẢN v5 (nguồn số liệu và lời nói)
# Từ Brand Claim đến Verifiable Truth
**Khi khách nhờ AI chọn hộ, thương hiệu được tin bằng gì?**
VSMCamp & CSMO Summit 2026 · Topic 07 · 19/11, 14:45, Hồ Tây 2 · 20 phút + 5 phút hỏi đáp
Bản v5 (16/11). Nền: khung v4 ngày 13/10. Luật: không nêu tên thương hiệu của Linh trong bài; ví dụ để ẩn danh.

---

## 0. Một câu cho cả bài
Khách hàng mới của anh chị không còn đọc quảng cáo. Nó là một cái máy, và nó chỉ tin thứ kiểm được.

Khán giả ra khỏi phòng phải mang được 3 thứ:
1. Một con số về chính thương hiệu mình (vừa đo trong phòng).
2. Một câu để nói lại với sếp: "Visibility = Reputation × Verifiable Data, là phép nhân."
3. Một việc làm trước thứ Hai tuần sau.

---

## 1. Dẫn nhập: 3 phương án (khuyến nghị A)

### A. "60 giây cầm điện thoại" (khuyến nghị)
Linh bước ra, chưa chào, chưa giới thiệu.
> "Trước khi tôi nói gì, mời anh chị lấy điện thoại ra. Mở ChatGPT hoặc Gemini. Gõ đúng câu trên màn hình, thay chỗ trống bằng ngành của mình. Tôi bấm giờ 60 giây."

Màn hình: *"Tôi đang cần [sản phẩm/dịch vụ của bạn] ở Việt Nam. Giới thiệu giúp tôi 3 thương hiệu đáng chọn nhất và lý do."* Đồng hồ đếm ngược lớn.

Hết giờ:
> "Ai thấy tên thương hiệu mình trong 3 cái tên, giơ tay."
(Thường rất ít.) "Cảm ơn. Giữ tay. Trong số này, ai thấy nó nói về mình đúng hoàn toàn?" (Tay hạ thêm.)
> "Những người vừa hạ tay: tối qua khách hàng của anh chị cũng hỏi đúng câu đó. Và anh chị không có trong câu trả lời. Hôm nay mình nói về chuyện đó."

Vì sao chọn A: khán giả tự thấy vấn đề trên điện thoại mình, không phải nghe Linh kể. Cảm giác được đo ngay bằng số tay giơ.
Rủi ro: wifi yếu, nhiều người không mở app. Dự phòng: chuyển sang B sau 20 giây nếu ít người làm.

### B. "Hãng dược Singapore bán kem bôi khớp"
> "Tháng trước tôi hỏi AI về một công ty Việt Nam, khách hàng là mấy ngân hàng lớn nhất nước. AI trả lời rất tự tin: đây là một hãng dược Singapore, chuyên kem bôi xương khớp. Công ty đó làm marketing tử tế mười năm. Với cái máy, họ là người khác."
Ảnh chụp màn hình thật, che tên.

### C. "Chiếc ghế trống"
Một ghế trống trên sân khấu. "Hôm nay phòng này thiếu một vị khách quan trọng nhất của anh chị. Nó không xem TVC, không theo dõi KOL, không cảm động. Nó đọc, đối chiếu, rồi chọn hộ khách."
Dùng làm câu nối nếu chọn A.

---

## 2. Kịch bản lời nói theo phút

| Phút | Phần | Slide | Ý chính |
|---|---|---|---|
| 0:00–2:30 | Dẫn nhập A | 1–2 | 60 giây, giơ tay |
| 2:30–5:00 | Khách hàng mới là cái máy | 3–5 | Số liệu, công thức nhân |
| 5:00–9:00 | AI đang thấy anh chị thế nào | 6–9 | 3 kiểu sai, 4 chỉ số, đừng đo thứ hạng |
| 9:00–12:00 | Agent đọc thương hiệu qua 5 bước | 10–11 | Mỗi bước là một chỗ rơi |
| 12:00–16:30 | Từ claim sang bằng chứng | 12–15 | 5 lớp, ví dụ viết lại claim |
| 16:30–19:30 | Làm ngay | 16–18 | QR, 3 việc 7 ngày, kế hoạch 30 ngày |
| 19:30–20:00 | Chốt | 19 | Câu kết |

### 2:30–5:00 · Khách hàng mới là cái máy
> "87% người Việt mua sắm online đã dùng ít nhất một công cụ AI, trung bình mỗi người dùng hai cái."
> "Và đây là con số làm tôi mất ngủ: 57% người tiêu dùng nói họ sẵn sàng để AI đổi thương hiệu giúp họ nếu nó tìm được lựa chọn hời hơn. Lòng trung thành, thứ mình mua bằng mười năm quảng cáo, đang được giao cho một cái máy."
> "Tin tốt: người ta chưa tin hẳn. Ở Mỹ, chỉ 15% muốn để agent tự bấm mua. Nghĩa là cửa sổ đang mở. Ai chuẩn bị bây giờ sẽ có mặt khi cửa sổ đóng lại."

Slide 5, công thức:
**Agentic Visibility = Brand Reputation × Verifiable Data**
> "Phép nhân, không phải phép cộng. Được yêu mà không kiểm được thì nhân với 0. Dữ liệu đầy đủ mà không ai yêu cũng nhân với 0."

### 5:00–9:00 · AI đang thấy anh chị thế nào
Ba kiểu sai, mỗi kiểu một slide, một câu:
1. **Bị nhận nhầm.** Hãng dược Singapore (nếu chưa dùng ở dẫn nhập) hoặc: một khảo sát tháng 5/2026 thấy AI gán nhãn hiệu của một thương hiệu cho đối thủ trong 8,2% câu trả lời, dù 1.231 trang của đại lý đều ghi đúng.
2. **Bị bịa.** Một công ty đào tạo Việt bị AI bịa số học viên và giải thưởng. Một kiểm tra 182 doanh nghiệp được ChatGPT giới thiệu: cứ 9 doanh nghiệp có 1 doanh nghiệp mang ít nhất một thông tin sai.
3. **Không kiểm được.** Cũng nghiên cứu đó: claim về chứng nhận, giải thưởng chỉ 19% được xác nhận. "Chính thứ mình hay khoe nhất lại là thứ máy ít tin nhất."

> "Vậy đo thế nào? Đừng đo thứ hạng. ChatGPT thay 74% nguồn trích dẫn mỗi tuần. Hỏi hai lần, ra hai danh sách khác nhau. Đo thứ hạng trên AI giống đo chiều cao của sóng."

Slide 9, bốn chỉ số (hỏi nhiều AI, nhiều lần):
- **Có mặt:** hỏi chung về ngành, AI có tự nhắc tới mình không?
- **Đúng:** hỏi thẳng về mình, đúng bao nhiêu ý?
- **Được đề xuất:** AI có khuyên chọn mình, vì lý do đúng không?
- **Nhất quán:** các AI có nói giống nhau không?

### 9:00–12:00 · Agent đọc thương hiệu qua 5 bước
> "Agent không cảm thương hiệu. Nó đọc và đối chiếu. Có 5 bước, mỗi bước là một chỗ anh chị có thể rơi."
1. Tìm: không có ở nguồn nó đọc thì vô hình.
2. Nhận diện: tên ngắn, trùng tên, viết tắt thì bị gán nhầm.
3. Đối chiếu: giá web một kiểu, sàn một kiểu, báo một kiểu thì nó bớt tin.
4. Lọc theo khách: không nói rõ mình dành cho ai thì không được ghép.
5. Đề xuất có lý do: lý do có nguồn thì khách tin; lý do bịa thì mình chịu tiếng.
> "Bốn chỉ số vừa rồi cho anh chị biết mình rơi ở bước nào. Không có mặt: bước 1. Sai, nhầm: bước 2 và 3. Không được đề xuất: bước 4 và 5."

### 12:00–16:30 · Từ claim sang bằng chứng
> "Claim là điều mình tự nói. Bằng chứng là điều máy kiểm được. Mỗi claim cần một bằng chứng."

Slide 13, ví dụ viết lại (slide đinh, để khán giả chụp):
| Claim | Bằng chứng máy đọc được |
|---|---|
| "Thương hiệu số 1 Việt Nam" | "Phục vụ 1.240 doanh nghiệp tính đến 11/2026, danh sách công khai tại [link]" |
| "Chất lượng hàng đầu" | "Đạt ISO 22000, số chứng nhận …, tra tại trang tổ chức cấp" |
| "Được khách hàng tin yêu" | "4,7/5 trên 3.100 đánh giá, 96% khiếu nại xử lý trong 48 giờ" |

Năm lớp bằng chứng (slide 14):
1. **Sự thật có cấu trúc:** một trang "Bảng sự thật": là ai, làm gì, cho ai, giá, chính sách, ngày cập nhật. Viết bằng chữ, không nhét trong ảnh.
2. **Nhất quán mọi kênh:** cùng một tên, giá, địa chỉ trên web, Google, fanpage, sàn, LinkedIn, trang đăng ký doanh nghiệp.
3. **Bên thứ ba xác nhận:** giải thưởng có link về trang ban tổ chức, chứng nhận có số hiệu, case khách hàng có tên đã xin phép.
4. **Người thật đứng tên:** nhà sáng lập, chuyên gia có hồ sơ công khai, ký tên dưới các claim quan trọng.
5. **Hành vi và phản hồi:** review, khiếu nại đã xử lý. Bán đúng người để phản hồi tốt; mỗi đơn bán sai người để lại một bằng chứng xấu mà agent đọc được.

> "Hai lớp đầu là Verifiable Data. Ba lớp sau là Reputation mà máy đọc được. Thiếu bên nào, phép nhân về 0."

### 16:30–19:30 · Làm ngay
Slide 16, QR lớn chiếm nửa màn hình, để 45 giây.
> "Tôi không bán gì trên sân khấu. Quét mã này, 10 phút tối nay anh chị tự đo thương hiệu mình theo 4 chỉ số, biết mình rơi ở bước nào, và nhận kế hoạch 30 ngày."

Slide 17, ba việc trước thứ Hai:
1. Hỏi 2 AI, mỗi AI 3 lần, 3 câu trong phiếu. Chụp lại câu trả lời.
2. Viết Bảng sự thật một trang. Đặt lên web bằng chữ.
3. Sửa chỗ lệch thông tin giữa web và Google Business Profile.

Slide 18, kế hoạch 30 ngày: tuần 1 sửa chỗ AI nói sai · tuần 2 Bảng sự thật · tuần 3 đồng bộ kênh · tuần 4 thêm bằng chứng bên thứ ba, đo lại.

### 19:30–20:00 · Chốt
> "Mười năm qua, thương hiệu thắng là thương hiệu kể chuyện hay nhất. Mười năm tới, thương hiệu thắng là thương hiệu dễ kiểm chứng nhất. Ba mươi ngày nữa, anh chị hỏi lại AI đúng câu lúc nãy. Tôi mong lần đó anh chị là người giơ tay."
(Nối vòng về dẫn nhập.)

---

## 5. Nguồn số liệu (đọc trước khi nói)
| Số | Nguồn | Ghi chú |
|---|---|---|
| 87% người tiêu dùng online VN đã dùng ≥1 công cụ AI; trung bình 2 nền tảng | Decision Lab, Connected Consumer Q3/2025, qua VnEconomy 20/11/2025 | Số 2025, nói "năm ngoái" |
| 57% sẵn sàng để AI đổi thương hiệu nếu có lựa chọn hời hơn; 24% không bao giờ giao | Checkout.com, Agentic Commerce 2026, 9/6/2026, 6 thị trường | Cỡ mẫu không công bố |
| 15% người Mỹ muốn để agent tự mua | Forbes, Jordan McKee, 1/10/2026 | Không nêu cỡ mẫu, nói "khảo sát ở Mỹ" |
| 1/9 doanh nghiệp được ChatGPT giới thiệu mang thông tin sai; claim chứng nhận chỉ 19,2% xác nhận | Empirank AIV-009, 18/8/2026, 182 doanh nghiệp, qua PPC Land 24/8 | Doanh nghiệp địa phương, Mỹ |
| AI gán nhãn hiệu cho đối thủ trong 8,2% câu trả lời; 1.231 trang đại lý đều đúng | AIMCLEAR, 4/6/2026 | Audit 1 thương hiệu, không phải khảo sát |
| ChatGPT thay 74% nguồn trích dẫn mỗi tuần | SISTRIX 4/2026, qua PPC Land | Chưa đọc bản gốc, kiểm trước khi nói |
| Xác suất AI cho cùng danh sách 2 lần < 1/100 | SparkToro × Gumshoe, 1/2026 | Từ v4, đã kiểm |
Không dùng: Ipsos 46%/32 nước (không tìm thấy gốc); "72% thương hiệu bị AI nói sai" (Atlas Digital, không rõ phương pháp).

## 6. Hỏi đáp: 5 câu chắc chắn bị hỏi
1. *"Làm schema, llms.txt có giúp không?"* Schema giúp máy nhận diện, nên làm. llms.txt chưa có bằng chứng các AI lớn đọc; làm thì rẻ, nhưng đừng coi là việc chính.
2. *"Mua quảng cáo trong ChatGPT có thay được không?"* Quảng cáo mua được chỗ đứng, không mua được lý do. Agent vẫn đối chiếu.
3. *"Doanh nghiệp nhỏ làm gì trước?"* Bảng sự thật và Google Business Profile. Hai việc, một buổi chiều.
4. *"Ai trong công ty chịu trách nhiệm?"* Một người giữ sự thật, thường là brand hoặc PR, có quyền yêu cầu sửa web, sàn, fanpage.
5. *"Bao lâu thì AI cập nhật?"* AI có tìm web: vài ngày tới vài tuần. Trí nhớ của mô hình: theo kỳ huấn luyện, nên phải làm sớm.
Câu nối sang panel 16:15 cùng phòng: "Ai đặt luật chơi khi AI được trao quyền mua? Mời anh chị ở lại lúc 16:15, mình bàn tiếp."


---
# Chữ trên deck v7 (27 slide)

S1: VSMCAMP & CSMO SUMMIT 2026 · TOPIC 07 · TRUST IN THE AGE OF AGENTS | 01 | Từ Brand Claim / đến Verifiable Truth | Khi khách nhờ AI chọn hộ, thương hiệu được tin bằng gì? | Đinh Trần Tuấn Linh   ·   19.11.2026   ·   Hồ Tây 2
S2: TRƯỚC KHI BẮT ĐẦU | 02 | 60 | GIÂY | HỎI ChatGPT HOẶC GEMINI | Tôi đang cần [sản phẩm của bạn] ở Việt Nam. Giới thiệu giúp tôi 3 thương hiệu đáng chọn nhất và lý do. | Ai thấy tên thương hiệu mình, giơ tay.
Hết giờ: Ai thấy tên thương hiệu mình trong 3 cái tên, giơ tay. Giữ tay. Ai thấy nó nói về mình đúng hoàn toàn? Những người vừa hạ tay: tối qua khách hàng của anh chị cũng hỏi đúng câu đó. Và anh chị không có trong câu trả lời.
Dự phòng nếu ít người làm sau 20 giây: kể chuyện hãng dược Singapore bán kem bôi khớp.
S3: PHẦN 1 | 03 | 01 | Một lần mua hàng giờ đi qua bốn chặng. | Hai chặng giữa là máy nói chuyện với máy.
S4: NGƯỜI → AGENT → AGENT → NGƯỜI | 04 | Niềm tin phải đi qua bốn chặng. Gãy một chặng là mất khách. | giao quyền | hỏi và đối chiếu | trả lời, cam kết | N | Người | khách hàng | A | Agent | của khách | A | Agent | của thương hiệu | N | Người | đứng sau thương hiệu | Thương hiệu không còn nói thẳng với khách. Nó nói qua hai cái máy.
S5: CHẶNG 1 · NGƯỜI GIAO QUYỀN | 05 | 87% | người Việt mua sắm online đã dùng ít nhất một công cụ AI. | Trung bình mỗi người dùng hai cái. | NGUỒN   Decision Lab, The Connected Consumer Q3/2025
S6: CHẶNG 1 · NGƯỜI GIAO QUYỀN | 06 | 57% | sẵn sàng để AI đổi thương hiệu giúp họ, nếu nó tìm được lựa chọn hời hơn. | Nhưng chỉ 15% người Mỹ muốn để agent tự bấm mua. Cửa sổ đang mở. | NGUỒN   Checkout.com, Agentic Commerce 2026 · 06/2026; Forbes, J. McKee · 10/2026
S7: CÂU CHUYỆN 1 | KHÁCH → AGENT CỦA KHÁCH | 29.09.2025 · MỸ | Nút “Mua” xuất hiện ngay trong khung chat. | Khách mua hàng của người bán trên Etsy mà không cần mở website. OpenAI nói kết quả không có tài trợ, xếp theo mức phù hợp với người hỏi. Nghĩa là chỗ đứng trong câu trả lời không mua được bằng tiền. | NGUỒN   TechCrunch, 29/9/2025 · OpenAI Instant Checkout, Agentic Commerce Protocol cùng Stripe
S8: CÂU CHUYỆN 2 | AGENT CỦA KHÁCH → AGENT CỦA THƯƠNG HIỆU | 01.2026 | Agent của khách nói chuyện thẳng với máy của cửa hàng. | Google công bố giao thức thương mại cho agent, Walmart nằm trong nhóm đầu tiên. Không còn ai đọc trang sản phẩm đẹp của anh chị. Hai cái máy đọc dữ liệu của nhau. | NGUỒN   Google Developers Blog, CNBC, Axios · 11/01/2026 (Universal Commerce Protocol)
S9: CÂU CHUYỆN 3 | AGENT CỦA KHÁCH → AGENT CỦA THƯƠNG HIỆU | 15.03.2026 · TRUNG QUỐC | Chiếc đồng hồ không có thật, được AI giới thiệu sau vài giờ. | Phóng viên CCTV dựng một mẫu đồng hồ không tồn tại, trả 39,9 tệ cho dịch vụ “tối ưu cho AI”. Vài giờ sau, trợ lý AI đã giới thiệu nó. Agent đọc nhanh hơn người, và bị lừa cũng nhanh hơn. | NGUỒN   CCTV 3.15 (3/2026), qua tổng hợp của Ballerine (11/2026) · cần kiểm bản gốc
S10: CÔNG THỨC | 10 | AGENTIC VISIBILITY  = | Reputation | × | Verifiable / Data | Con người yêu mến | Máy xác thực được | Phép nhân, không phải phép cộng. Thiếu một bên, kết quả về 0.
S11: PHẦN 2 | 11 | 02 | AI đang thấy anh chị thế nào? | Ba kiểu sai, và cách đo.
S12: KIỂU SAI 1 · BỊ NHẬN NHẦM | 12 | 8,2% | câu trả lời AI gán nhãn hiệu của một thương hiệu cho đối thủ. | Trong khi 1.231 trang của đại lý đều ghi đúng. | NGUỒN   AIMCLEAR · 06/2026 · audit một thương hiệu tiêu dùng trên 5 hệ AI
S13: CÂU CHUYỆN 4 · VIỆT NAM | AGENT CỦA KHÁCH | 2026 · HÀ NỘI | Phục vụ các ngân hàng lớn. AI tả họ là hãng dược bán kem bôi khớp. | Mười năm làm thương hiệu tử tế. Với cái máy, họ là người khác. Khi được hỏi chung về ngành, không AI nào nhắc tên họ. | NGUỒN   Kết quả đo của diễn giả, đã ẩn danh
S14: KIỂU SAI 3 · KHÔNG KIỂM ĐƯỢC | 14 | 19% | claim về chứng nhận, giải thưởng được AI xác nhận. | Thứ mình hay khoe nhất là thứ máy ít tin nhất. | NGUỒN   Empirank AIV-009 · 08/2026 · 26 claim chứng nhận
S15: ĐO | 15 | Đừng đo thứ hạng. Đo bốn điều. | 01 | Có mặt | Hỏi chung về ngành, AI có tự nhắc tới mình không? | 02 | Đúng | Hỏi thẳng về mình, đúng bao nhiêu ý? | 03 | Được đề xuất | AI có khuyên chọn mình, vì lý do đúng không? | 04 | Nhất quán | Các AI có nói giống nhau về mình không? | NGUỒN   Hỏi 2 lần, AI cho cùng danh sách dưới 1/100 lần · SparkToro × Gumshoe · 01/2026
S16: PHẦN 3 | 16 | 03 | Agent không cảm thương hiệu. Nó đọc và đối chiếu. | Năm bước, mỗi bước là một chỗ có thể rơi.
S17: AGENT ĐỌC THƯƠNG HIỆU QUA 5 BƯỚC | 17 | Năm bước, năm chỗ rơi. | 1 | Tìm | Không có ở nguồn nó đọc thì vô hình. | CÓ MẶT | 2 | Nhận diện | Tên ngắn, trùng tên thì bị gán nhầm. | ĐÚNG | 3 | Đối chiếu | Web, sàn, báo nói khác nhau thì bớt tin. | ĐÚNG · NHẤT QUÁN | 4 | Lọc theo khách | Không nói rõ dành cho ai thì không được ghép. | ĐƯỢC ĐỀ XUẤT | 5 | Đề xuất | Lý do có nguồn thì khách tin. | ĐƯỢC ĐỀ XUẤT | Chỉ số yếu cho biết anh chị đang rơi ở bước nào.
S18: CÂU CHUYỆN 5 | AGENT CỦA THƯƠNG HIỆU → NGƯỜI CỦA THƯƠNG HIỆU | 2022 → 02.2024 · CANADA | Chatbot hứa hoàn tiền vé tang. Hãng nói chatbot tự chịu. Toà nói không. | Một hành khách mất bà, hỏi chatbot của Air Canada và được bảo có thể xin giá vé tang sau khi bay. Chính sách thật không cho phép. Toà buộc hãng bồi thường. Agent nói thay anh chị, anh chị chịu thay agent. | NGUỒN   Global News, 15/2/2024 · Civil Resolution Tribunal, British Columbia
S19: PHẦN 4 | 19 | 04 | Claim là điều mình tự nói. Bằng chứng là điều máy kiểm được.
S20: VIẾT LẠI CLAIM · VÍ DỤ MINH HOẠ | 20 | Mỗi claim một bằng chứng. | CLAIM | BẰNG CHỨNG MÁY ĐỌC ĐƯỢC | Thương hiệu số 1 Việt Nam | ✓ | Phục vụ 1.240 doanh nghiệp tính đến 11/2026. Danh sách công khai tại [link]. | Chất lượng hàng đầu | ✓ | Đạt ISO 22000, số chứng nhận …, tra tại trang tổ chức cấp. | Được khách hàng tin yêu | ✓ | 4,7/5 trên 3.100 đánh giá. 96% khiếu nại xử lý trong 48 giờ. | NGUỒN   Ví dụ minh hoạ, số liệu giả định
S21: NĂM LỚP BẰNG CHỨNG | 21 | Năm lớp bằng chứng máy đọc được. | 01 | Sự thật có cấu trúc | Một trang: là ai, làm gì, cho ai, giá, chính sách, ngày cập nhật. Viết bằng chữ. | 02 | Nhất quán mọi kênh | Cùng tên, giá, địa chỉ trên web, Google, fanpage, sàn. | 03 | Bên thứ ba xác nhận | Giải thưởng có link, chứng nhận có số hiệu, case có tên. | 04 | Người thật đứng tên | Nhà sáng lập, chuyên gia ký dưới claim quan trọng. | 05 | Phản hồi đã xử lý | Review, khiếu nại, đổi trả. Bán đúng người. | Verifiable / Data | Reputation / máy đọc được
S22: CÂU CHUYỆN 6 | NGƯỜI CỦA THƯƠNG HIỆU | 2026 · AMERICAN EXPRESS | Hãng thẻ cam kết bồi hoàn khi agent đã đăng ký mua nhầm. | Agent được cấp danh tính, chủ thẻ được xác thực trước khi agent được mua. Niềm tin giữa hai cái máy cuối cùng vẫn cần một người đứng tên chịu trách nhiệm. | NGUỒN   The Financial Brand, 1/5/2026 (bình luận của Riskified)
S23: BÁN ĐÚNG NGƯỜI | 23 | “ | Mỗi đơn bán sai người để lại một bằng chứng xấu mà agent đọc được. | Agent đọc review, khiếu nại, đổi trả.
S24: PHẦN 05 · LÀM NGAY | 24 | Soi thương hiệu / trong 10 phút. | 01   Tự đo 4 chỉ số. | 02   Biết mình rơi ở bước nào. | 03   Nhận kế hoạch 30 ngày. | Miễn phí. Không cần đăng nhập. Không bán gì trên sân khấu. | QR | [đường dẫn]
S25: TRƯỚC THỨ HAI | 25 | Ba việc trước thứ Hai. | Hỏi | 2 AI, mỗi AI 3 lần, 3 câu trong phiếu. Chụp lại câu trả lời. | Viết | Bảng sự thật một trang. Đặt lên web bằng chữ. | Sửa | Chỗ lệch giữa web và Google Business Profile.
S26: 30 NGÀY | 26 | Ba mươi ngày. | TUẦN 1 | Sửa chỗ AI đang nói sai. | TUẦN 2 | Viết Bảng sự thật. | TUẦN 3 | Đồng bộ thông tin mọi kênh. | TUẦN 4 | Thêm bằng chứng bên thứ ba. Đo lại. | Ngày 30: hỏi lại AI đúng câu lúc nãy.
S27: KẾT | 27 | Mười năm tới, thương hiệu thắng là thương hiệu đi qua cả bốn chặng mà không bị bóp méo. | giao quyền | hỏi và đối chiếu | trả lời, cam kết | N | Người | khách hàng | A | Agent | của khách | A | Agent | của thương hiệu | N | Người | đứng sau thương hiệu | Dễ kiểm chứng nhất, không phải kể hay nhất. | Đinh Trần Tuấn Linh   ·   Mời ở lại panel 16:15, Hồ Tây 2
