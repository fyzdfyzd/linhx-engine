# QUY CHUẨN XÂY DỰNG VÀ VẬN HÀNH OPC CỦA LINHX

**Phiên bản:** 1.0 · **Hiệu lực:** 2026-10-09 · **Chủ sở hữu:** Đinh Trần Tuấn Linh
**Nguồn:** The 100 Task Playbook (Martin Bell, 2019) và 100 Tasks AI (2026); nghiên cứu LAB010; quy tắc tài chính trong `D:\LINHX\PLAN\00_BASELINE_LINHX_MASTER_PLAN.md`; bộ chuẩn dev LAB009.

Từ khoá: **PHẢI** là bắt buộc; **NÊN** là khuyến nghị mạnh, bỏ qua phải ghi lý do vào `QUYET-DINH.md`; **CÓ THỂ** là tuỳ chọn.

---

## 1. Định nghĩa và phạm vi
1.1. **OPC (One-Person Company)**: một sản phẩm hoặc doanh nghiệp do **một founder ra quyết định**, vận hành bằng **AI agent + code tất định + thuê ngoài theo việc**. Có thể có người bán thời gian ở giai đoạn Scale.
1.2. **LINHX-OPC** là **launchpad** (bệ phóng, theo nghĩa của Bell): nơi giữ quy chuẩn, template, tài nguyên dùng chung, và dựng các OPC nối tiếp nhau.
1.3. Quy chuẩn áp dụng cho mọi OPC trong `D:\LINHX\LINHX-OPC\`. Ý tưởng chưa kiểm chứng ở LAB/IDEA; chỉ vào LINHX-OPC khi founder quyết định chạy thật.

## 2. Mười nguyên tắc
1. **Nhân quả, có thứ tự**: SETUP → LAUNCH → SCALE; không qua cổng thì không sang bước sau.
2. **Kiểm chứng bằng tiền thật**: chỉ coi là "đã kiểm chứng" khi có đơn trả tiền từ người lạ.
3. **Chỉ làm việc bắt buộc cho ra mắt**; mọi hạng mục khác để sau go-live.
4. **Phân phối dựng trước sản phẩm**: kênh có khán giả phải chạy trước ngày ra mắt.
5. **Đo từ ngày đầu**: top 20 KPI, mỗi KPI một nguồn, một công thức, một chủ.
6. **Code làm phần phải đúng, AI làm phần cần viết và phân tích, founder quyết phần rủi ro.**
7. **Agent không bao giờ tự đụng tiền, giá, nội dung công khai.**
8. **Làm một lần, dùng nhiều lần**: mọi thứ dùng lại được phải nằm ở `_launchpad/`.
9. **Có lãi trước, lớn sau**: tự nuôi bằng doanh thu; không blitzscale.
10. **Mọi thứ là file mở**: Markdown/CSV để Claude, Codex, Antigravity, Obsidian và con người cùng đọc được.

## 3. Cấu trúc thư mục
```
D:\LINHX\LINHX-OPC\
├─ README.md            Giới thiệu, cách dùng
├─ QUY-CHUAN-OPC.md     File này
├─ INDEX.md             Danh sách mọi OPC và trạng thái
├─ _template\           Khung cho OPC mới (PLAYBOOK, TASKLIST, mẫu, AGENTS.md)
├─ _launchpad\          Dùng chung: agents, best-practice, legal, tool stack, benchmark, refs
├─ _archive\            OPC đã đóng (chuyển vào, không xoá)
└─ OPCNNN-TEN-VIET-TAT\
   ├─ README.md         Thẻ OPC
   ├─ AGENTS.md, CLAUDE.md
   ├─ LICH.md           Tuần 1–20 ra ngày thật
   ├─ PLAYBOOK.md, TASKLIST.csv
   ├─ QUYET-DINH.md     Sổ quyết định
   ├─ mau\              7 mẫu đã điền
   ├─ bao-cao\          Báo cáo tuần tuan-NN.md, tháng YYYY-MM.md
   ├─ src\              Code (repo riêng nếu lớn, theo LAB009)
   ├─ data\             Dữ liệu (không chứa khoá bí mật)
   └─ refs\             Tài liệu tham khảo
```

## 4. Đặt tên và trạng thái
4.1. Tên thư mục: `OPCNNN-TEN-VIET-TAT` (NNN là số tiếp theo, tính cả `_archive`; tên 1–3 từ, viết HOA, không dấu). Ví dụ `OPC001-CHIEMTINH-VN`.
4.2. Trạng thái trong `INDEX.md`:

| Mã | Ý nghĩa |
|---|---|
| `SETUP` | Đang ở giai đoạn Setup (tuần 1–4) |
| `LAUNCH` | Đã kiểm chứng, đang dựng và ra mắt |
| `SCALE` | Đã go-live, đang học từ dữ liệu và tối ưu |
| `INDEPENDENT` | Qua cổng Độc lập |
| `PAUSED` | Tạm gác (ghi lý do, ngày xem lại) |
| `CLOSED` | Đóng, đã chuyển vào `_archive` |

## 5. Vòng đời, 15 bước và các cổng
5.1. Mỗi OPC **PHẢI** dùng `PLAYBOOK.md` (80 việc, 15 bước) từ `_template`. Việc không áp dụng đánh `skip` kèm lý do.
5.2. Lịch chuẩn 20 tuần (Bell: 100 ngày). OPC **CÓ THỂ** nhanh hơn, không được bỏ cổng.

| Giai đoạn | 5 bước | Tuần |
|---|---|---|
| SETUP | Sứ mệnh · Đội agent · Thu ý tưởng · Kiểm chứng · Bộ khởi động | 1–4 |
| LAUNCH | Đội tạm · MVP · Chức năng tối giản · Data-First · Go Live | 4–9 |
| SCALE | Chuẩn hoá · Học từ dữ liệu · Tối ưu + vận hành AI · Best practice + nhân bản · Độc lập | 8–20 |

5.3. **Các cổng bắt buộc**:

| Cổng | Tiêu chí tối thiểu |
|---|---|
| Có chỉ tiêu tài chính | Doanh thu, biên gộp, hoà vốn, tiền mặt tối thiểu đã ghi |
| **Đã kiểm chứng** | ≥ 30 đơn trả tiền trước từ người lạ, hoặc mức founder đặt và ghi lý do |
| **Go live** | Không có điểm chết đơn lẻ; đóng 100% lỗi nghiêm trọng/cao, 60% trung bình, 20% thấp; báo cáo KPI ngày đã chạy; pháp lý đủ để nhận tiền |
| **Độc lập** | Founder ≤ 30–60 phút/ngày trong 4 tuần; có lãi 3 tháng liên tiếp; best practice đã ghi; PMF (Sean Ellis ≥ 40%) |

## 6. Quy chuẩn agent
6.1. Mỗi agent **PHẢI** có thẻ trong `mau/03-DOI-AGENT.md`: vai trò, việc, được làm, **không được làm**, trần token/tháng, KPI, người duyệt, lịch chạy.
6.2. Agent **KHÔNG ĐƯỢC** tự chi tiền, đổi giá, hoàn tiền, tạo mã giảm giá, đăng nội dung công khai, gửi tin cho khách thật lần đầu, deploy production, xoá dữ liệu.
6.3. Mỗi OPC **PHẢI** có một agent hoặc báo cáo tài chính kiểm soát chi tiêu và phát hiện bất thường (bài học Project Vend).
6.4. Agent chạy trong sandbox, tài khoản riêng; khoá bí mật không nằm trong file cấu hình hoặc repo; mọi hành động có nhật ký.
6.5. Không dùng skill, plugin, MCP chưa được duyệt.
6.6. Khi có ≥ 4 agent chạy hằng ngày, **NÊN** đưa vào Paperclip (org chart, ngân sách, phê duyệt).
6.7. Mỗi OPC **PHẢI** có `AGENTS.md` (và `CLAUDE.md` trỏ về đó).

## 7. Quy chuẩn kỹ thuật
7.1. Code **PHẢI** theo bộ chuẩn `D:\LINHX\LAB\LAB009-DEV-STANDARD`.
7.2. Phần phải đúng (tính toán nghiệp vụ, thanh toán, đối soát) **PHẢI** là code tất định có test; không giao cho LLM tự tính.
7.3. Một nguồn dữ liệu duy nhất (database) cho đơn, khách, KPI; sao lưu hằng ngày.
7.4. Ngưỡng sau go-live: uptime > 99%, tải trang < 3 giây.
7.5. Giấy phép thư viện bên thứ ba phải được kiểm (ví dụ AGPL).

## 8. Quy chuẩn dữ liệu và KPI
8.1. Top 20 KPI, trong đó 1–5 là KPI chính; mỗi KPI có nguồn, công thức, chủ, chỉ tiêu tháng/quý/năm.
8.2. Ngưỡng cảnh báo mặc định: ngày −50%, tuần −30%, tháng −15% so với kỳ trước.
8.3. Ngưỡng kinh tế đơn vị: CLV:CAC ≥ 3; churn < 3%/tháng; hoàn vốn CAC < 12 tháng.
8.4. Mỗi OPC đo **giờ founder/ngày** và **chi phí AI/doanh thu** (mục tiêu < 10%).

## 9. Nhịp vận hành
| Nhịp | Ai chuẩn bị | Founder làm | Thời lượng |
|---|---|---|---|
| Ngày (06:00) | Agent tài chính + CS | Đọc KPI ngày, xử lý ca chuyển lên, duyệt nội dung | 20–30 phút |
| Tuần (Chủ nhật) | Agent viết `bao-cao/tuan-NN.md` | Chọn **1** thử nghiệm, duyệt ngân sách tuần | 30–45 phút |
| Tháng (ngày 1) | Agent viết `bao-cao/YYYY-MM.md` | P&L, cohort, trần agent, giá | 1–2 giờ |
| Quý | Agent tổng kết | Chọn OKR quý (3 × 3) | Nửa ngày |

Báo cáo tuần **PHẢI** có: % tiến độ theo giai đoạn, 3 điểm tốt, 3 điểm xấu, KPI, chi phí agent, quyết định cần founder, 1 thử nghiệm tuần sau.

## 10. Quy chuẩn tài chính (theo luật tài chính LINHX)
10.1. **Không vay nợ** để chạy OPC.
10.2. **Trần đầu tư mỗi OPC: 200 triệu đồng** tính luỹ kế tới cổng Độc lập.
10.3. **3 tháng sau go-live không có lực kéo thì đóng** (lực kéo = đạt ≥ 50% chỉ tiêu doanh thu tháng 3).
10.4. Giữ **quỹ dự phòng 3 tháng** chi phí cố định của OPC.
10.5. **Tái đầu tư 20–30%** lợi nhuận vào OPC; phần còn lại về LINHX.
10.6. Chi tiêu > 5 triệu/lần hoặc quảng cáo > ngân sách tuần **PHẢI** có founder duyệt.
10.7. Gọi vốn ngoài là ngoại lệ, ghi vào `QUYET-DINH.md`; số vốn = thời gian tới mốc × burn × 1,5–2; pha loãng ≤ 20–25%.

## 11. Pháp lý và tuân thủ
11.1. Trước khi nhận tiền: pháp nhân thu tiền, mã số thuế, thông báo website TMĐT (online.gov.vn), điều khoản, chính sách quyền riêng tư (NĐ 13/2023), chính sách hoàn tiền.
11.2. Ngành nhạy cảm (tâm linh, sức khoẻ, tài chính) **PHẢI** được luật sư rà mô hình và nội dung trước go-live.
11.3. Không dùng dữ liệu, nội dung crawl của bên khác để bán; chỉ dùng tham chiếu nội bộ và viết lại.
11.4. Mỗi OPC có lịch tuân thủ trong `mau/06`.

## 12. Nội dung, thương hiệu, build in public
12.1. Nội dung công khai do agent soạn **PHẢI** được founder duyệt.
12.2. Không quảng cáo sai sự thật; không dùng người thật giả do AI tạo để chứng thực (bài học Medvi).
12.3. Build in public dưới thương hiệu DTTL **CÓ THỂ** làm; số liệu công khai **PHẢI** là số thật; dừng công khai khi lộ lợi thế cạnh tranh.

## 13. Đóng, gác, nhân bản
13.1. Đóng OPC khi: chạm điều 10.3, hoặc vượt trần 10.2, hoặc founder quyết. Ghi bài học vào `_launchpad/best-practice/`, chuyển thư mục vào `_archive/`, cập nhật `INDEX.md`.
13.2. Qua cổng Độc lập: ghi best practice theo chức năng vào `_launchpad/`, cập nhật benchmark giữa các OPC, viết blueprint nhân bản.
13.3. OPC thứ N+1 **PHẢI** bắt đầu từ `_template` + `_launchpad` mới nhất.

## 14. Sửa quy chuẩn
14.1. Mọi thay đổi ghi vào mục "Lịch sử" dưới đây, tăng phiên bản (1.0 → 1.1 khi thêm/sửa điều; 2.0 khi đổi cấu trúc).
14.2. Thay đổi `_template` **KHÔNG** tự áp vào OPC đang chạy; founder quyết định có áp hay không.

## Lịch sử
| Phiên bản | Ngày | Thay đổi |
|---|---|---|
| 1.0 | 2026-10-08 | Bản đầu, từ LAB010 |
