# WF05 · Bổ sung vòng 2 (cloud, 9/11 12:10–13:30 giờ VN)

Lấp chỗ mỏng NGHIEN-CUU.md tự khai, và **thử máy đo thật** trên PDF ca thử LAB028 (`bao-cao-dao-tao-ai-vn`, 17 trang, tự chấm 4,08). Không sửa NGHIEN-CUU.md.

## Kết luận
1. **Điểm 4,08 là tự chấm thổi phồng.** Hai agent chấm mù (chỉ thấy ảnh trang + rubric) cho 3,44 và 3,66. Thợ tự chấm 0/17 trang dưới ngưỡng; cả hai người chấm mù cùng đánh trượt 7/17 trang (6, 8, 9, 12, 13, 15, 16). Ca thử LAB028 **chưa đạt** máy đo của WF05.
2. **Cổng script đã tốt:** cài 7 lỗi vào bản sao, script bắt 6/6 lỗi thuộc phần kiểm được bằng máy. Không cần viết lại, chỉ thêm 3 kiểm mới (mục "Sửa vào skill").
3. **"Kiểm số vẽ trên hình" phần lớn đã có:** cổng 4 so từng giá trị chuỗi trong `04-hinh.json` với BCxx, và hình do `hinh.py` vẽ từ đúng json đó. Lỗ hổng còn lại: hình là ảnh AI hoặc ảnh chép vào (không có json), và giá trị sai trùng một số khác có trong cùng BC.
4. **Ngưỡng "hai lần chấm lệch ≤1 điểm" quá lỏng:** 84/85 cặp tiêu chí lệch ≤1 nhưng hai người chấm chỉ đồng ý đạt/trượt ở 13/17 trang. Đề xuất thay bằng: **trang trượt nếu một trong hai lần chấm trượt** (lấy điểm thấp), và đo độ đồng ý đạt/trượt ≥80%.
5. Bản vàng tiếng Việt cùng chủ đề vòng 1 có: Decision Lab "The State of Consumer AI in Vietnam 2025". Cloud không tải được (proxy chặn); đề xem tận mắt ở `DR/DE-2.md`.

## Thử máy đo (chạy thật, Linux, Typst 0.13.1)
- Dựng lại từ nguồn: `report.py dung` ra lại đúng 17 trang, không cảnh báo. Plugin chạy được trên Linux, không chỉ Windows.
- Cổng 11 bản gốc: đạt trừ cảnh báo D07 (phủ chữ 0,38, mục tiêu 0,18–0,32). Tức cổng script cho qua một báo cáo mà mắt người chấm mù đánh trượt 7 trang: **script không thay được chấm mắt.**
- Lỗi vặt của cổng: chép thư mục bằng `cp` không giữ giờ sửa thì cổng 11 báo "PDF mới hơn bảng chấm". Nên so băm PDF thay vì giờ sửa tệp.

### Chấm mù hai lần (agent mới, không thấy lý do thợ, thứ tự xuôi và ngược)
| | Thợ tự chấm | Mù A | Mù B |
|---|---|---|---|
| Điểm TB | 4,08 | 3,44 | 3,66 |
| Trang dưới ngưỡng | 0 | 11 | 7 |

Lỗi người chấm mù thấy mà thợ và script đều bỏ sót (đã xem tận mắt trang 12 để xác nhận):
- **Lộ tên tệp nội bộ trong nguồn**: trang 8, 10, 15 ghi "R1 LINHX-EDU, 03_COMPETITORS_VIETNAM.csv", "03-bang-chung.jsonl" (đã grep PDF, đúng).
- **Tiêu đề rớt một chữ**: mục 4.1 trang 12 còn trơ "vi"; tiêu đề hình 9 trang 11 còn "khai.". D14 hiện chỉ bắt tiêu đề cuối trang.
- Nhãn chương lặp ("CHƯƠNG 4 · CHỖ TRỐNG" ở đầu trang và cạnh số 04); nhãn trục hình 10 dính nhau; 1/3 cuối trang trống ở trang 6, 9, 15; trang 8 và 16 chật kín; hai trang mở chương cùng một khuôn.

### Trang cài lỗi (đo cổng script)
| Lỗi cài | Script bắt? |
|---|---|
| Giá trị trên hình H01 sửa 83 → 58 | Có, cổng 4 (giá trị không có trong BC) |
| Tiêu đề hình bỏ dấu chấm | Có, V02 |
| Hình H02 bỏ nguồn | Có, D02 |
| Số trong văn 81% → 71% | Có, cổng 7 (số mồ côi) |
| Tiêu đề mục thành cụm danh từ | Có, V01 |
| Chèn gạch ngang dài | Có, V09 |
| Chèn đoạn chữ dài lặp ý (khối chữ đặc) | Không (chưa vượt 4.300 ký tự/trang), việc của chấm mắt |
Người chấm mù (agent mới) trên 5 trang cài lỗi bắt **6/7**: đủ 6 lỗi script bắt, thêm khối chữ lặp mà script bỏ sót. **Bỏ sót đúng lỗi số vẽ trên hình** (thanh 58 thay 83), còn báo nhầm là hình ghi 83 "khớp văn". Lý do: ảnh trang render 70 dpi (579×819 px), nhãn số trong biểu đồ SVG không có trong lớp chữ PDF. Hai lớp bù nhau: script bắt số trên hình, mắt bắt khối chữ và nhịp. Người chấm cũng nêu một nghi vấn nội dung thật ở Hình 4 bản gốc (thanh 4,7 triệu ghi "giá niêm yết" nhưng có thể là giá đăng ký sớm), chưa kiểm.

## Nguồn ngoài thêm (đọc code thật, chép ở scratchpad cloud, không chạy)
Bảng đầy đủ ở `GHI-CHEP-CLOUD.md`. Thêm vào NGOAI.md:
| Nguồn | Lấy | Bỏ |
|---|---|---|
| adobe/skills `whitepaper` [đọc repo gốc] | pandoc md → typst + template, Source Sans 3 | Chạy không hỏi, **xoá tệp nguồn sau khi ra PDF** (trái luật LINHX) |
| chesley-veko/book_skill (TQ) [đọc] | Phong cách cắm rút có prompt ảnh riêng; chương song song tự biên dịch 0 lỗi; ảnh AI hỏng thì DỪNG | |
| Mrpixelraf/whitepaper-forge (TQ) [đọc] | Thẻ "hỏi chủ" khi thiếu dữ liệu, cấm viết bừa; QC 21 mục; "không có ảnh chụp trang = chưa nghiệm thu" | Luật phủ trang ≥85% |
| vedangvatsa/consulting-report-framework [đọc] | `qa_check.py` từ sáo AI, câu dài; `fact_check.py` rút câu có số ra CSV | Kiểu thẻ dày đặc |
| Pysamlam/a4-report [đọc] | Kiểm số có tính lại (YoY, tổng) | Luật phủ 95% |
| clearsmog/claude-skills [đọc] | Mức lỗi Nghiêm trọng/Lớn/Nhỏ, nhiều agent chấm song song | Chỉ lấy mẫu 3 trang |
| lucifer1004/claude-skill-typst [đọc] | Bộ eval có lỗi gài sẵn để đo người chấm | |
| Perplexity "Designing, refining and maintaining agent skills" (1/5/2026) [đọc] | "Write some of the evals first."; "Gotchas are extremely high-value content. Start thin, grow as the agent fails."; "Self-generated Skills provide no benefit on average" | Cookbook agent-skills chỉ nói API, không về báo cáo [chỉ thấy] |

Nhận định: ngoài kia có hai trường phái, "tư vấn dày" (phủ 85–95% trang) và "tạp chí thoáng". LINHX đo từ 24 báo cáo thật nên giữ trường phái tạp chí; không lấy luật phủ trang.

## Sửa vào skill (đề xuất, chờ ≥2 bằng chứng ở vòng 1)
- `dan-trang` bước 11: **bỏ tự chấm**; chấm bằng 2 agent mắt mới (xuôi và ngược), trang trượt nếu một lần trượt. Bằng chứng: lệch 4,08 với 3,44/3,66.
- `report.py kiem-ban-in`: thêm (a) tiêu đề/tiêu đề hình có dòng cuối ≤2 tiếng; (b) chữ trong PDF khớp mẫu tên tệp nội bộ (`\.csv|\.jsonl|_[A-Z]{3,}|R\d LINHX`); (c) khoảng trống liền >30% chiều cao trang ở trang nội dung. Cả ba đo được bằng pymupdf.
- `viet-bao-cao` bước 7: hình không có json (ảnh AI, ảnh chép) phải có bảng giá trị đi kèm để kiểm.
- `report.py anh-trang` để chấm: nâng mặc định 70 → 150 dpi (ảnh 70 dpi làm người chấm đọc sai nhãn số).
- Bộ trang cài lỗi (thư mục `loi/` của lần thử này, 7 lỗi) làm **bài kiểm người chấm** trước mỗi vòng: người chấm phải bắt ≥80% lỗi nhìn thấy được.

## Rủi ro
- Hai người chấm mù cùng là một model; đồng ý nhau chưa chắc đúng với mắt Linh. Cần Linh chấm 3 trang để hiệu chuẩn.
- Bản vàng tiếng Việt chưa tải được trên cloud.
