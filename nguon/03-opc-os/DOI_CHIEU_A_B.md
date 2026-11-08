# Đối Chiếu Thực Nghiệm Phương Án A (Code Thuần) & Phương Án B (Agent Điều Phối) (`DOI_CHIEU_A_B.md`)

> **Dự án**: `03_OPC_OS` · **Đối chiếu theo**: `D:\LINHX\PLAN\00_SYSTEM\PROTO_DE\03_OPC_OS.md` (Bản 3) & `D:\LINHX\LINHX-OPC\QUY-CHUAN-OPC.md`  
> **Dữ liệu đo thật trên đĩa**:
> - Kết quả Phương án A: [`A_CODE/ket_qua_a.json`](file:///D:/LINHX/PROTO/03_OPC_OS/A_CODE/ket_qua_a.json) (chạy bởi [`A_CODE/chay_a.py`](file:///D:/LINHX/PROTO/03_OPC_OS/A_CODE/chay_a.py))
> - Kết quả Phương án B: [`B_AGENT/ket_qua_b.json`](file:///D:/LINHX/PROTO/03_OPC_OS/B_AGENT/ket_qua_b.json) (chạy bởi [`B_AGENT/chay_b.py`](file:///D:/LINHX/PROTO/03_OPC_OS/B_AGENT/chay_b.py))
> - Bộ 10 đơn giả chuẩn: [`demo/input/10_don_gia_opc001.json`](file:///D:/LINHX/PROTO/03_OPC_OS/demo/input/10_don_gia_opc001.json)

---

## 1. Nguyên Tắc Bất Biến Đã Thực Thi Ở Cả A Và B

Theo đúng luật an toàn sắt của `03_OPC_OS.md` và `QUY-CHUAN-OPC.md` Mục 6.2:
1. **Phần tiền luôn là code cố định 100% ở cả A và B**: Tạo đơn, sinh QR, kiểm tra khoá `Authorization: Apikey <SEPAY_API_KEY>`, chống ghi trùng `tx_id`, kiểm tra khớp số tiền `transferAmount == amount`, chặn đơn quá hạn 15 phút, ghi sổ doanh thu `so-doanh-thu.csv` (mẫu S1a-HKD) và bật **Báo đỏ 400.000.000 VNĐ** đều chạy bằng code tất định trong [`modules/03_flow_thanh_toan_sinh_report/module.py`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/03_flow_thanh_toan_sinh_report/module.py) và [`modules/07_chi_phi_loi_nhuan/module.py`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/07_chi_phi_loi_nhuan/module.py).
2. **Không bao giờ giao việc kiểm tiền, đổi giá hay tự hoàn tiền cho Agent (`FORBIDDEN_AGENT_ACTIONS`)**.

---

## 2. Bảng Đối Chiếu Định Lượng Bắt Buộc (Số Đo Thật 10 Đơn + 3 Ca Lạ)

| Chỉ số | A · Code thuần (`A_CODE/`) | B · Agent điều phối (`B_AGENT/`) | Ngưỡng chuẩn | Nhận xét thực nghiệm |
|---|---|---|---|---|
| **Số đơn lỗi / 10 đơn** | **0 / 10 lỗi** (Khớp **10/10** kịch bản kỳ vọng) | **0 / 10 lỗi** (Khớp **10/10** kịch bản kỳ vọng) | `0` | Cả A và B đều xử lý chuẩn 6 đơn trả đủ tiền và chặn chính xác 4 đơn bất thường (`ORD-04` trùng `tx_id`, `ORD-05` sai khoá `401`, `ORD-06` thiếu tiền, `ORD-07` hết hạn 15 phút). |
| **Thời gian 1 đơn `paid` (trung bình / lâu nhất)** | TB **8,536 giây** / Lâu nhất **16,200 giây** / Nhanh nhất **5,555 giây** *(gọi Gemini 2.5 Flash thật + xuất PDF A4 Chromium)* | TB **9,596 giây** / Lâu nhất **11,236 giây** / Nhanh nhất **8,533 giây** *(gọi 2 bước Gemini 2.5 Flash thật + kiểm tuân thủ Module 09, 0 `time.sleep`)* | `< 5 phút` (`< 300s`) | Cả hai phương án đều nhanh hơn ngưỡng 5 phút gần **30 lần** (hoàn toàn không dùng `time.sleep()` giả lập). Phương án A nhanh hơn B trung bình **~1,06 giây/đơn** vì chỉ gọi Gemini 1 lượt thay vì 2 lượt suy luận. |
| **Chi phí AI / 1 đơn (token thật từ Gemini `usageMetadata` + VNĐ)** | TB **283 input + 168 output tokens** ≈ **3,73 VNĐ / đơn** (Tổng 6 đơn: **22,39 VNĐ**, trần `maxOutputTokens=300`) | TB **601 input + 540 output tokens** ≈ **10,77 VNĐ / đơn** (Tổng 6 đơn: **64,63 VNĐ**, 2 lượt gọi Gemini có trần token) | `< 10% giá bán` | Số token trả về trực tiếp từ `usageMetadata` của `gemini-2.5-flash` (biến thiên thật theo từng đơn). **Phương án B tốn token và chi phí gấp ~2,89 lần Phương án A** (`10,77đ` so với `3,73đ`) vì Agent gọi 2 bước suy luận & tổng hợp. |
| **Chạy lần 2 cùng đầu vào có giống lần 1 không** | **Lõi tính sao & điểm 17-luật giống hệt 100% (`True`, `97,5 điểm`)** | **Phần lõi tính sao & số tiền giống 100% (`True`)**, lời dẫn Gemini biến thiên tự nhiên theo từng lượt gọi | Càng ổn định càng tốt | Phương án A đạt tính tất định ở toàn bộ cấu trúc 17 mục báo cáo và luồng tiền. |
| **Xử lý được mấy / 3 ca lạ mà không cần người** | **1 / 3 ca lạ** *(Chỉ tự chuẩn hoá được ca nhập sai giờ sinh `25:99` về `UBT 12:00`; ca hỏi sâu về report phải trả lời mẫu tĩnh và đẩy chờ người; ca đòi hoàn tiền chặn an toàn đẩy Founder)* | **2 / 3 ca lạ** *(Tách giờ sinh đúng `08:15` bằng regex từ tin nhắn tự nhiên của khách, gọi thật `Module 01` tính lại lá số + cập nhật lại báo cáo cho đơn `CT00001`; tự giải thích sự phối hợp Mặt Trời Sư Tử + Mọc Xử Nữ bằng Gemini thật kèm miễn trừ trách nhiệm; ca đòi hoàn tiền vẫn chặn tự chi và chuyển Founder theo Luật 6.2)* | Ghi rõ | **B vượt trội A ở khâu CSKH & xử lý ngoại lệ**: tự động cập nhật lại báo cáo khi khách nhắn sửa giờ sinh và trả lời câu hỏi chuyên sâu. |
| **Đọc log tìm lỗi mất bao lâu** | **~15 giây** (Chỉ cần mở 1 dòng trong `runtime/a_code/events_a.jsonl` — stacktrace và trạng thái tuyến tính) | **~45 – 60 giây** (Phải đối chiếu cả `events_b.jsonl` và chuỗi suy luận nhiều bước trong `runtime/b_agent/agent_trace.jsonl`) | Càng nhanh càng tốt | A dễ gỡ lỗi hơn gấp 3–4 lần khi vận hành tự động không người trực. |

---

## 3. Chi Tiết Đối Chiếu 3 Ca Lạ Giữa A Và B

| Ca lạ thực tế | Cách xử lý của **A · Code thuần** | Cách xử lý của **B · Agent điều phối** | Bên thắng |
|---|---|---|---|
| **Ca 1: Khách nhập sai giờ sinh (`25:99`) rồi nhắn tin báo lại giờ đúng (`08:15`)** | Rule tĩnh chỉ đưa đơn về chế độ *Không rõ giờ sinh (`UBT 12:00`)* lúc tạo đơn; nếu khách nhắn tin sửa thành `08:15` sau khi đã xuất PDF thì rule tĩnh không tự đọc hiểu tin nhắn để render lại được. | Agent đọc hiểu tin nhắn tự nhiên của khách, trích xuất giờ đúng `08:15`, tự gọi lại `tool_generate_report_payload` tính lại Cung Mọc & 12 Nhà và cập nhật lại file PDF trên đúng đường dẫn `/o/CT00001`. | **B · Agent** |
| **Ca 2: Khách hỏi lại chuyên sâu về nội dung trong Report vừa nhận** *(VD: "Mặt Trời Sư Tử và Cung Mọc Xử Nữ phối hợp thế nào?")* | Không trả lời chuyên sâu được bằng `if/else`; chỉ gửi câu trả lời mẫu FAQ tĩnh và đẩy phiếu sang hàng đợi chờ người (`escalated_to_founder = True`). | Agent tự tra cứu hồ sơ `CT00001` của khách, tổng hợp câu trả lời bám sát dữ kiện lá số thật của khách và tự động đính kèm câu miễn trừ trách nhiệm pháp lý (`resolved_automatically = True`). | **B · Agent** |
| **Ca 3: Khách đòi hoàn tiền (`demand_refund`)** | Chặn tự động chi tiền, tạo phiếu `Escalation Tier 3` chờ anh Linh duyệt. | Agent kiểm tra quy tắc `FORBIDDEN_AGENT_ACTIONS` (QUY-CHUAN 6.2), từ chối tự gọi lệnh chuyển tiền, giải thích lịch sự theo giọng thương hiệu *Luna Nguyệt Mai* và tạo phiếu `Tier 3` chờ anh Linh duyệt. | **Hoà (An toàn như nhau)** |

---

## 4. Kết Luận Kiến Trúc Cho Hệ Điều Hành OPC OS: Dùng A Ở Đâu, Dùng B Ở Đâu?

Từ số đo thực nghiệm trên, **không chọn cực đoan toàn A hay toàn B**, mà chốt kiến trúc **Lai Phân Lớp (Hybrid Deterministic Core + Edge Agent)**:

1. **Dùng Phương án A (`A_CODE` — Code Thuần Tất Định) cho toàn bộ Luồng Chính Tạo Doanh Thu (Modules 01, 02, 03, 04, 07, 08, 10)**:
   - **Vì sao**:
     - Rẻ hơn gần **3 lần** chi phí token AI (`3,73đ/đơn` so với `10,77đ/đơn` trên Gemini 2.5 Flash thật).
     - Ổn định và tái lập **100%** khi chạy hàng loạt cho cả 3 OPC (Chiêm tinh, Ngân hàng, Hướng nghiệp học sinh).
     - Dễ tìm lỗi trong **15 giây** qua `EventBus` JSONL.
     - Tuyệt đối an toàn cho luồng tiền SePay, sổ doanh thu S1a-HKD và cảnh báo đỏ 400 triệu VNĐ.
2. **Dùng Phương án B (`B_AGENT` — Agent Điều Phối Có Rào Chắn) cho Luồng Ngoại Lệ & Chăm Sóc Khách Hàng Đa Kênh (Module 05 & Module 06)**:
   - **Vì sao**:
     - Giải quyết tự động được **2/3 ca lạ** (khách nhắn tin báo nhầm thông tin đầu vào cần render lại PDF, khách hỏi giải thích thêm về báo cáo đã mua) mà code cứng `if/else` phải bó tay đẩy về cho người.
     - Giúp giữ đúng cam kết vận hành của Founder: **tổng thời gian anh Linh phải caniệp ≤ 1,5 giờ/ngày**, chỉ duyệt những việc thuộc `Escalation Tier 3` (hoàn tiền, khiếu nại gay gắt, duyệt 20 report đầu tiên).
