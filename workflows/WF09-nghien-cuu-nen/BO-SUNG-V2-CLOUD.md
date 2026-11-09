# WF09 · Bổ sung vòng 2 (cloud, 9/11/2026 12h–13h40)

Lấp các chỗ `NGHIEN-CUU.md` tự khai là mỏng. Không sửa `NGHIEN-CUU.md`. Mọi trích dưới đây đã đọc ở trang gốc trong phiên này. Nhãn: [đọc] là đã đọc trang hoặc code, [chạy] là đã chạy máy.

## Kết luận thêm
1. **Đã chạy thử máy đo trên một mẫu thật** (`LAB028 bao-cao-dao-tao-ai-vn`: 45 nguồn, 74 bằng chứng, bản này đã qua cổng 3). Có 61 trong 74 bằng chứng (82%) không lấy từ trang nguồn mà từ tệp ghi chú trung gian (`tep_nghien_cuu: 01_MARKET_DEMAND_VN_GLOBAL.md`…). Có trích còn dính bảng Markdown (`| | Tỷ lệ DN đã ứng dụng AI | 18% …`). Cổng 3 hiện tại cho qua hết. [chạy]
2. **Kiểm tay 6 bằng chứng ở trang gốc thì không câu nào khớp nguyên văn, dù 4 câu đúng ý.** Kết quả: 1 không vào được, 1 PARTIAL, 2 câu trích là bản dịch tiếng Việt của trang tiếng Anh, 2 câu là diễn giải. Vì vậy máy đo "trích là chuỗi con của trang" (tầng 1 của `NGHIEN-CUU.md`) sẽ đánh trượt cả chỗ đúng, **nếu không đổi khuôn sổ bằng chứng trước** (xem mục Sửa). [chạy]
3. **Cloud không tải được nguồn VN.** 45/45 URL bị proxy chặn (`Tunnel connection failed: 403`). Máy đo tầng 1 phải chạy trên **máy cty (DESKTOP-PVHR2CD)**. [chạy]
4. **Mốc ngưỡng đã có nguồn.** FACT cho thấy Gemini-2.5-Pro Deep Research chỉ đạt độ chính xác trích dẫn 81,44%. Nên ngưỡng VERIFIED ≥ 90% của `NGHIEN-CUU.md` là hợp lý, và kết quả Gemini DR bắt buộc phải qua cổng chứ không được nhận thẳng. [đọc]
5. Nghi vấn "NCT" ở mục Rủi ro đã rõ: NCT là **người cao tuổi** (LAB105, báo cáo cho Listening Vietnam). Lỗi gốc ghi ở `LAB105/QUY-CHUAN-4D.md` mục 8: 7 câu trích bịa, 10/17 link chết, "gộp" làm mất 241 số và sinh 89 số không nguồn, agy báo đã mở 11 link nhưng nhật ký không có lượt mở nào. [đọc]

## Chạy thử máy đo (`may-do/`)
| Script | Đo gì | Kết quả |
|---|---|---|
| `kiem_trich.py <thư mục>` | Tải từng URL bằng GET, lưu `tai/<mã>.txt` kèm băm và mã trạng thái. Chấm mỗi bằng chứng KHOP / GAN (≥ 80% cụm 3 từ) / KHONG / KHONG_TAI, và kiểm từng số trong `so` có trên trang | Trên LAB028 ở cloud: 45 FAILED (proxy), CHUA_DAT. Phải chạy lại trên máy cty |
| `kiem_mat_so.py truoc.md sau.md --bang-chung … --cho-doi …` | Dùng cho phiếu "chỉ vá": số bị mất ngoài danh sách được phép, số mới không có trong kho | Test bắt đúng trường hợp mất 11,9 và 1.234.567, sinh 37 không nguồn |
| `test_may_do.py` | 7 test, không gọi mạng | **7/7 đạt** |

Lệnh chạy trên **máy cty**, bên trong repo: `py -3.12 workflows\WF09-nghien-cuu-nen\may-do\kiem_trich.py <thư mục báo cáo>`. Riêng PDF, script ghi `PDF_CAN_TACH` và không tự đoán. Cần tách bằng `pdftotext` trước.

Kiểm tay 6 bằng chứng LAB028 (người đọc trang không biết gì về quá trình viết):

| BC | Nguồn | Nhãn | Vì sao |
|---|---|---|---|
| BC01 | thuvienphapluat.vn QĐ 1671 | INACCESSIBLE | Trang chặn máy đọc |
| BC06 | baodautu.vn | PARTIAL | Trang ghi "70% lao động có kỹ năng **sử dụng** AI cơ bản", trích bỏ mất chữ "sử dụng". Cụm "Mục tiêu dự thảo" không có trên trang. Con số 500.000 trên trang là của gộp hai nhóm ("nhân lực AI và nhân lực triển khai AI") |
| BC07 | en.vneconomy.vn | VERIFIED (ý), trượt nguyên văn | Trang tiếng Anh: "with 39% of workers classified as advanced AI users—more than double the global average of 16%"; trích là bản dịch tiếng Việt |
| BC09 | vietnamnews.vn | VERIFIED (ý), trượt nguyên văn | "81 per cent of users engage with AI tools and features daily, 83 per cent are participating in AI learning and upskilling". Đây là nguồn dẫn lại e-Conomy SEA, bản gốc chưa mở |
| BC10 | press.aboutamazon.com | VERIFIED | "18% of Vietnam's businesses have already adopted AI, up from 13% last year" (18/9/2025) |
| BC16 | unleash.ai (BCG AI at Work 2025) | VERIFIED, có bẫy | Số 36% xuất hiện hai lần trên trang với hai nghĩa: đào tạo "đủ" và mức tự tin của lao động tuyến đầu. Chỉ kiểm "số có trên trang" sẽ không phân biệt được |

Bài học rút ra: kiểm số theo kiểu "số có trong kho" (bài học 8 của NCT) vẫn thủng ngay cả khi số có trên trang gốc. Phải kèm **câu chứa số**, và người chấm mù phải chấm theo nghĩa (entailment).

## Quy trình đơn vị top (đã đọc)
- **Der Spiegel, phòng Dokumentation.** Theo Hauke Janssen, trưởng phòng, viết chương 10 của Verification Handbook: "It employs roughly 70 "documentation journalists."" · "Every verifiable piece of information will be underlined." · "The source of factual corrections and quotations must be given." · "A statement is considered verified only if confirmed by reliable sources or experts." · "Fact-checking starts with comparing a story draft with the research materials provided by the author." · "The fact-checker checks the corrections a second time". Nguồn: https://datajournalism.com/read/handbook/verification-2/10-organizing-the-newsroom-for-better-and-accurate-investigative-reporting [đọc]
- CJR 2010 viết về Spiegel: "checked twice—and not only [checked] by the author" · "it's more of an adversarial relationship" https://www.cjr.org/behind_the_news/inside_the_worlds_largest_fact.php (bài năm 2010, trước vụ Relotius) [đọc]
- Áp vào LINHX: (1) gạch chân **mọi** câu kiểm được, không lấy mẫu. (2) Bước đầu so bản viết với tài liệu của chính thợ là chưa đủ: phải mở trang gốc, vì vụ Relotius lọt qua đúng khâu này. Riêng điểm này chưa có nguồn đọc trực tiếp, báo cáo cuối của Spiegel đưa vào `DR/DE-2.md` để đọc. (3) Sửa xong thì kiểm lại lần hai.
- Pew `Our Methods`: không có câu nào nói cách Pew kiểm số trước khi đăng (đã đọc, **không tìm thấy**). Không dùng Pew làm mốc quy trình kiểm.

## Máy đo: mốc có nguồn
| Mốc | Số | Nguồn |
|---|---|---|
| FACT chấm thế nào | Tách cặp câu–URL, bỏ trùng, tải trang (Jina Reader), "a binary judgment ('support' or 'not support')", giám khảo Gemini-2.5-flash | arXiv 2506.11763v1, 13/6/2025 https://arxiv.org/abs/2506.11763 [đọc] |
| Độ chính xác trích dẫn (C. Acc.) / số trích dẫn hiệu quả (E. Cit.) | Gemini-2.5-Pro DR 81,44 / 111,21 · OpenAI DR 77,96 / 40,79 · Perplexity DR 90,24 / 31,26 · Claude-3.7-Sonnet w/Search 93,68 / 32,48 | như trên, Bảng 1 [đọc] |
| Độ tin của giám khảo | RACE đồng thuận cặp 71,33% so với 68,44% giữa chuyên gia người. **FACT không công bố độ khớp với người** | như trên, Bảng 2 [đọc] |
| AI tìm kiếm trích sai | "Collectively, they provided incorrect answers to more than 60 percent of queries" (1.600 truy vấn, 8 công cụ). "More than half of responses from Gemini and Grok 3 cited fabricated or broken URLs" | CJR Tow Center, 6/3/2025 https://www.cjr.org/tow_center/we-compared-eight-ai-search-engines-theyre-all-bad-at-citing-news.php [đọc] |
| Link chết theo thời gian | "A quarter of all webpages that existed at one point between 2013 and 2023 are no longer accessible" (tính tới 10/2023) | Pew, 17/5/2024 https://www.pewresearch.org/data-labs/2024/05/17/when-online-content-disappears/ [đọc] |

Ngưỡng đề xuất, chỉnh lại so với `NGHIEN-CUU.md`:
1. Tầng 1 "trích khớp 100%" chỉ áp cho trường `trich_goc` (nguyên văn, giữ ngôn ngữ của trang). Bản dịch để ở trường `dich`, không đưa vào máy đo.
2. Một nguồn INACCESSIBLE thì không được đỡ khẳng định C1 (số, nhân quả, luật). Nếu là nguồn nhà nước bị chặn bot, Linh tải tay trên máy cty và lưu vào `tai/`.
3. Chấm mù: VERIFIED ≥ 90% (ngang Perplexity DR, cao hơn Gemini DR 81,44%), INACCURATE = 0. Vì FACT chưa có độ khớp với người, vòng 1 phải có Linh chấm lại 10 khẳng định để hiệu chỉnh giám khảo.

## Sửa vào skill (thêm vào danh sách của `NGHIEN-CUU.md`)
- `linhx-report` khuôn `03-bang-chung.jsonl`: thêm `trich_goc` (nguyên văn, ngôn ngữ gốc), `dich`, `tep_tai` (đường dẫn trong `tai/`), `dinh_vi` (trang, mục), `cau_chua_so`. **Cấm** dùng `tep_nghien_cuu` làm nguồn trích. Tệp trung gian chỉ được dùng để tìm đầu mối, đúng luật "Notes are routing aids, not authorities" của daymade.
- `report.py cong 3`: gọi `kiem_trich.py`. Có KHONG ở C1 thì báo lỗi, có GAN thì cảnh báo, KHONG_TAI thì C1 không được tính.
- `linhx-4d`: phiếu nào sửa tệp có sẵn thì chạy `kiem_mat_so.py` trước khi chấm (bài học 7 của NCT).
- `linhx_worker`: phiếu `tai-nguon` (máy cty, chỉ tải và lưu, không viết) tách khỏi phiếu viết. Phiếu `kiem-mu-trich-dan` như `NGHIEN-CUU.md` đã đề xuất.

## Nguồn ngoài thêm (skills.sh, NGOAI.md còn thiếu)
| Nguồn | Đã đọc | Lấy | Bỏ |
|---|---|---|---|
| boom5426/nature-paper-skills · `claim-source-verification` (MIT, 641 sao) https://github.com/boom5426/nature-paper-skills | SKILL.md [đọc code] | Hai vai: một bên đề xuất nguồn kèm "the sentence from the source that carries the claim, quoted verbatim", một bên hoài nghi chạy ở phiên mới. Ba luật: "The default verdict is reject", "No verbatim supporting sentence, no confirmation", "Spend more on verification than on research". Bốn kết quả CONFIRMED / PARTIAL / REJECTED / BLOCKED; PARTIAL thì "Do not apply. Do not remove the marker". Nguồn bị loại ghi lại làm cảnh báo cho lượt sau. Mốc: 139 nguồn, loại 55, trong đó 29 `does_not_support_claim`, và "None was fabricated" | Phân loại riêng cho bài báo khoa học (DOI, quần thể nghiên cứu) |
| deepcitation/skills · `verify` https://www.skills.sh/deepcitation/skills/verify | Trang đầu [chỉ thấy] | Báo cáo HTML có ảnh cắt bằng chứng ngay ở trang nguồn | Cần runtime DeepCitation; Snyk báo Fail |
| szoloth/skills · `fact-checker-investigator` https://skills.sh/szoloth/skills/fact-checker-investigator | Trang đầu [chỉ thấy] | Tách sự thật đã kiểm, giả định, diễn giải, bịa | Ít người dùng (5 lượt cài), không thấy cách kiểm |

Mốc của boom5426 giải thích đúng kết quả LAB028: nguồn có thật, đúng chủ đề, nhưng câu trích không phải câu của trang. Kiểm "link sống" và "số có trong kho" đều không bắt được loại lỗi này. Phải có câu nguyên văn của trang, và người chấm mặc định là loại.

## Rủi ro thêm
- Kiểm nguyên văn sẽ làm phiếu thu bằng chứng chậm hơn, vì thợ phải chép đúng ngôn ngữ gốc. Bù lại, phiếu viết không phải đoán.
- Trang báo VN đổi nội dung hoặc gỡ bài: phải lưu `tai/` ngay lúc thu. Kiểm lại sau này mà khác thì ghi DRIFT, không xoá.
