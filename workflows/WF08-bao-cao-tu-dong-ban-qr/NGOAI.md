# Người ngoài đã làm: WF08

Bước 0, tìm sơ bộ 9/11 (GitHub, trang skill, blog, mạng). **Mới tìm thấy, chưa đọc code.** Vòng 1 phải đọc code/quy trình ít nhất 3 cái tốt nhất, ghi: lấy gì, bỏ gì, so với skill LINHX đang có.

| Nguồn | Link | Đọc để |
|---|---|---|
| Soulfync AI báo cáo chiêm tinh | https://contra.com/p/l67cvo7B-soulfync-ai-ai-powered-astrology-reports | sản phẩm cùng loại CTS |
| OpenFate AI | https://microlaunch.net/blog/why-openfate-ai-is-different-from-generic-horoscope-apps | định vị khác horoscope chung |
| Hệ giao sản phẩm số tự động | https://contra.com/p/ReQXmkXe-ai-automated-digital-product-fulfilment-system | trả tiền → giao |
| Indie hacker horoscope bridge | https://www.indiehackers.com/post/i-don-t-know-astrology-but-i-do-know-i-want-to-understand-my-wife-so-i-built-an-ai-powered-horoscope-bridge-72b5bd9173 | kể số thật |

## Còn phải tìm ở vòng 1
- GitHub theo tên skill + 'SKILL.md'; skills.sh, claudemarketplaces, openskillindex.
- Mạng: X, LinkedIn, Reddit, nhóm Facebook VN; tiếng Trung khi hợp.

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| [kerykeion](https://github.com/g-battaglia/kerykeion) `context/serializer.py` [đọc code] | Bộ tuần tự hoá model sang XML cho AI; đầu file ghi "strictly non-qualitative and non-interpretive" | Ý: đưa cho LLM dữ kiện thuần, không diễn giải; bỏ trường rỗng thay vì in trống | AGPL, không gộp code; không có kho diễn giải |
| [immanuel-python](https://github.com/theriftlab/immanuel-python) [đọc cấu trúc] | Thư mục `reports/` chỉ có aspect, dignity, pattern, weighting; không có lời diễn giải | Xác nhận: thư viện tính chỉ ra số, không ra văn; phần văn là việc của kho lời giải | Không dùng làm lõi |
| [branded-pdf-service](https://github.com/tsayles/branded-pdf-service) `app/renderer.py` [đọc code] | Pandoc → Typst → PDF; `_escape_typst` thoát các ký tự đặc biệt của Typst (dấu gạch chéo ngược, #, @, *, _, dấu nháy, <, >, ngoặc); `validate_brand_typ` thử biên dịch mẫu trước khi nhận; `typst compile` chạy đồng bộ | Thoát ký tự Typst với tên khách; thử biên dịch mẫu thương hiệu trước khi dùng; PDF đồng bộ không cần trình duyệt | GPL-3.0; dấu nước ReportLab (không cần) |
| [papermake](https://github.com/rkstgr/papermake) `README`, `CLAUDE.md` [đọc] | Mẫu Typst lưu theo băm SHA-256, mỗi lần dựng ghi băm đầu vào và đầu ra | Ý: ghi băm mẫu + băm dữ liệu cho mỗi báo cáo để truy vết khi khách khiếu nại | Cả hệ Rust + S3 + ClickHouse quá nặng cho OPC |
| [nava2](https://github.com/pvotio/nava2) `app/tasks.py` [đọc code] | Chuỗi Celery: kiểm → lấy dữ liệu → HTML → PDF → cập nhật trạng thái; có `handle_errors` đặt `FAILED` | Chuỗi bước tách riêng, lỗi ở bước nào ghi rõ bước đó, trạng thái đơn rõ | Celery/Redis/Postgres quá nặng; không có chống trùng |
| [natal-charts](https://github.com/jc4p/natal-charts) [chỉ thấy README] | API tính lá số trên flatlib | Không | Cũ (2025-02), chỉ là máy tính |
| [SePay: QR + form](https://developer.sepay.vn/en/sepay-webhooks/tao-qr-va-form-thanh-toan) [đọc] | Mã đơn duy nhất; UNIQUE trên `transaction_id`; chỉ xác nhận khi `transferAmount >= amount`; hỏi trạng thái 3 giây; hết hạn 15 phút; timeout 8 giây. Trích: "Only confirm payment when the transferred amount is ≥ the order amount." | Cả luồng | Không nêu retry và độ trễ: phải đọc thêm trang "Create Webhooks" |
| [Casso: webhook thủ công](https://developer.casso.vn/webhook/thiet-lap-webhook-thu-cong) [đọc] | 5 giây; gọi lại tối đa 17 lần trong 24 giờ; sau đó PAUSED, 7 ngày thì DISABLE; trích: "Mỗi giao dịch của Casso được định danh bởi một `id`." Không tách mã đơn, tự khớp theo `description` | Cảnh báo khi endpoint chết; tự đối soát | |
| [freeCodeCamp: Stripe + hàng đợi](https://www.freecodecamp.org/news/stripe-webhooks-background-jobs) [đọc qua công cụ tóm tắt] | Trích: "Your webhook handler should do exactly one thing: validate the incoming event and enqueue it for processing." Mỗi bước được lưu kết quả, lỗi bước 5 không chạy lại bước 1–4 | Nguyên tắc handler mỏng + bước có checkpoint | Inngest (dịch vụ ngoài) |
| [dev.to: Stripe giao hàng số](https://dev.to/joeytbuilds/the-exact-stripe-webhook-code-i-use-to-deliver-digital-products-automatically-3d6o) [đọc] | Giao sau ~4 giây (tác giả tự ước); không chống trùng; link tải công khai. Trích: "The download URL in this implementation is publicly accessible — anyone with the link can download." | Phản mẫu: bài học về những gì phải thêm (chống trùng, link có hạn) | Cách làm |
| [n8n 17213](https://n8n.io/workflows/17213-create-human-reviewed-personalized-pdfs-from-stripe-payments-using-openai/) [đọc mô tả] | Stripe → OpenAI → PDF → hàng duyệt tay (Slack) → Gmail; khớp đơn theo email | Hàng duyệt tay cho ca ngoại lệ | Khớp theo email (dễ nhầm khi mua nhiều đơn); không có kiểm số |
| [Bonnie Sorsby](https://bonniesorsby.com/astrology-reports-compared/) [đọc; người bán, thiên lệch] | 5 loại báo cáo; tiêu chí chất lượng. Trích: "The tell is whether anything was calculated." | 9 tiêu chí cho rubric M8 | Lời quảng cáo cho sản phẩm tác giả |
| [Proof-Carrying Numbers](https://arxiv.org/abs/2509.06902) [đọc abstract] | Kiểm số ở bộ dựng, không ở mô hình. Trích: "trust is earned only by proof, while the absence of a mark communicates uncertainty." | Mô hình cho luật Q18 | Phần chứng minh toán |
| [tianpan.co](https://tianpan.co/blog/2026/05/17/agent-narrated-a-number-it-should-have-computed) [chỉ thấy phần công khai] | Trích: "an unsourced number in agent output is a defect." | Cách gắn "biên nhận" cho mỗi số | Con số 83% nêu trong bài chưa kiểm nguồn gốc |
| [O*NET IP Manual](https://www.onetcenter.org/dl_files/IP_Manual.pdf) [đọc; Creative Commons] | Trích: "the goal is to direct a client to occupations that tend to have the same high and low interests (i.e., the same pattern)"; hệ số tương quan giữa hồ sơ khách và hồ sơ nghề | Cách nối RIASEC ra nghề (so hình dạng, không so mức) cho vòng 3 | Bản tiếng Anh, cần Việt hoá câu hỏi |
| [Truity mẫu](https://www.truity.com/sites/default/files/fillpdf/sample_big_five_personality_test_report.pdf), [Gallup mẫu](https://www.gallup.com/file/cliftonstrengths/en/260807/CliftonStrengths_34_Report.pdf) [đọc] | Bố cục báo cáo trả phí thật | Xem `vang/README.md` | Chữ (bản quyền) |

## Đã tìm nhưng chưa đọc được
- astro.com (chặn bot), 16personalities (403), bản đủ của Truity technical document và Gallup technical report (PDF nén, công cụ không trích chữ).
- Trang SePay "Create Webhooks" và "Reconciliation" (nêu retry chính thức): chưa đọc.
- Tiếng Trung: chưa tìm (không thấy cần cho đầu ra này).
- Nguồn tiếng Việt về báo cáo trả phí: tìm sơ bộ chỉ ra các trang thần số học bán lẻ, chưa đọc kỹ; giao cho `DR/DE-1.md`.
