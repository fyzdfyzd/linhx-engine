---
name: hieu-khach
description: Bước 1–4 của quy trình deck proposal - tiếp nhận và làm rõ đề bài, nghiên cứu nền có bảng bằng chứng, xác định người nghe và mục tiêu, pain–gain của khách. Dùng trong skill deck-proposal hoặc khi Linh nhờ "phân tích khách", "nghiên cứu nền cho đề xuất", "pain gain của khách".
---

# Hiểu khách (bước 1–4)

Script: `python "${CLAUDE_PLUGIN_ROOT}/scripts/deck.py"`.

## Bước 1. Đề bài → `01-de-bai.md`

- Đọc mọi thứ Linh đưa: email, Zalo, ghi âm đã gõ, brief, tệp cũ. Điền 12 mục theo mẫu. Trích nguyên văn lời khách ở mục 3.
- Chỗ chưa biết: `[CẦN LINH: câu hỏi cụ thể]`. Không đoán ngân sách, không đoán người ra quyết định.
- **Xung đột lợi ích (mục 13), bắt buộc:** tìm tên mọi BU của Linh (LINHX, Sakedemy, Unikon, URAH, TUVA, IF Agent, Chiêm Tinh Số, [DOANH NGHIỆP BÁN LẺ ĐÃ ẨN DANH], cùng tên viết tắt) trong tư liệu khách (`grep -ri` cả thư mục, đọc cả nhận xét, báo cáo đánh giá). Đọc cả tình hình BU ở `D:\LINHX\PLAN\20_BU\<BU>\` (công nợ, hợp đồng đang mở, kế hoạch quý: ca thử [DOANH NGHIỆP BÁN LẺ ĐÃ ẨN DANH] lộ ra URAH còn đang bị nợ một khoản và kế hoạch quý ghi không ký mới năm nay). BU nào đang là nhà cung cấp, đối tác hay bị khách chê thì ghi rõ; deck không được đề xuất việc trái với vị trí đó. Ca thử KGBG: nhà cung cấp QR bị chê chính là Unikon.
- **Riêng tư:** không chép tên người, số điện thoại, email, danh sách học viên/khách từ tư liệu vào bất kỳ tệp deck nào; nhắc người bằng vai.
- Tư liệu có nhiều bản (MASTER, FINAL, OLD…): lấy bản mới nhất theo ngày trong tên/nội dung làm số chính, ghi số cũ bị thay vào cột `vay_thi_sao` của BC.
- Gom các `[CẦN LINH]` thành **tối đa 5 câu hỏi** ở mục "Câu hỏi gửi Linh" (cổng 1 chặn quá 5), kèm phương án mặc định cho từng câu.
- Ba dòng **Chốt tối thiểu** (cụm cấm nói viết trong ngoặc kép để `kiem-deck` dò được trên slide; ghi 'không nêu giá' thì slide có số tiền bị chặn) (mục tiêu một câu, giá được phép nói, điều không được nói) phải có trước bước 10. Claude tự đề xuất thì ghi `(mặc định, chờ Linh xác nhận)` ở cuối dòng: cổng 10 cảnh báo, bản cuối (`kiem-deck --ban-cuoi`) chặn.
- `deck.py cong <dir> 1` tới khi báo **NỘI DUNG ĐẠT · CHỜ DUYỆT** (mã thoát 3). Gửi Linh câu hỏi ngắn có khuyến nghị và ghi giờ hỏi: `deck.py hoi <dir> 1 --cau "<câu hỏi + khuyến nghị>"`. Linh đồng ý: `deck.py duyet <dir> 1`. Linh im lặng đủ 10 phút: `deck.py duyet <dir> 1 --nguoi tu-dong-10-phut` (script từ chối nếu chưa đủ 10 phút hoặc nội dung chưa đạt).

## Bước 2. Nghiên cứu nền → `02-bang-chung.csv`, `02-nghien-cuu.md`

- Chia đề bài thành 3–6 câu hỏi nghiên cứu độc lập (khách, ngành, đối thủ, pháp lý, công nghệ). Câu nào cần đọc nhiều nguồn thì giao subagent chạy song song; mỗi subagent ghi một tệp nháp riêng, Claude gộp vào bảng.
- Mỗi dữ kiện một dòng CSV: `id` BC01…, `du_kien`, `so_lieu`, `loai` (`nguon` | `noi-bo` | `uoc-tinh` | `gia-thuyet`), `nguon_ten`, `nguon_url`, `ngay` (ngày đọc), `do_tin_cay` (cao/vua/thap), `trich_doan` (nguyên văn ngắn để kiểm lại), `vay_thi_sao` (ý nghĩa cho deck).
- Ưu tiên nguồn gốc (báo cáo, văn bản pháp luật, trang chính thức) hơn bài tổng hợp. Văn bản pháp luật: kiểm còn hiệu lực. Tên công cụ AI: kiểm còn đúng tới ngày trình bày.
- Tư liệu nội bộ của Linh (EDU, LAB, hồ sơ BU) dùng `loai=noi-bo`, `nguon_ten` = đường dẫn (script kiểm tệp có thật).
- Cột `duoc_len_slide`: `co` | `khong` (số nội bộ/nhạy cảm, chỉ để Claude hiểu) | `hoi-linh`. Slide trỏ BC `khong` bị chặn; `hoi-linh` bị chặn ở bản cuối.
- Số lấy lại từ tài liệu cũ của Linh: mở nguồn gốc ít nhất một lần, ghi lệch (nếu có) vào `vay_thi_sao`. Ca thử KGBG: "cầu vàng ~7 tấn" thực ra là cầu đầu tư.
- Trang web chặn (403, timeout): mở bằng Chrome của Linh hoặc bản lưu web.archive.org; không kiểm được nguyên văn thì `do_tin_cay=thap` và ghi "chưa kiểm nguyên văn" ở `trich_doan`.
- `02-nghien-cuu.md` viết 6 mục theo mẫu, mỗi khẳng định ghi (BCxx).
- Cổng 2 cần ít nhất 5 bằng chứng có nguồn, trong đó **ít nhất 2 nguồn công khai** (`loai=nguon`); mã BC nhắc trong 02-nghien-cuu.md phải có trong CSV.

## Bước 3. Người nghe → `03-nguoi-nghe.md`

Trả lời 5 câu (ai nghe, lập trường, quyết định ta muốn, thời gian, điều họ quan tâm/sợ) và câu 6 (sau buổi họ làm gì). Chọn trình tự:
- **Trực tiếp** (kết luận trước): người ủng hộ, lãnh đạo bận, deck gửi đọc.
- **Gián tiếp** (bối cảnh → vấn đề → giải pháp): người hoài nghi, hội đồng thẩm định.
Chọn mật độ: trình bày có người nói (ít chữ, nhiều ghi chú người nói) hay gửi đọc (đủ ý trên slide).

## Bước 4. Pain–gain → `04-pain-gain.json`

- `cong_viec`: việc khách đang cố làm xong (một câu, động từ + đối tượng + bối cảnh).
- Ít nhất 3 pain và 2 gain. Viết bằng lời của khách, không bằng lời của người bán.
- `diem` 1–10: độ đau/độ muốn. ≥7 nghĩa là khách đã nói ra hoặc có số chứng minh: ghi `trich` (nguyên văn) hoặc trỏ BC có `trich_doan`, không thì hạ nhãn `gia-thuyet` (cổng 4 chặn).
- Mỗi mục có `bang_chung` (BCxx) hoặc `nhan: "gia-thuyet"`. Pain điểm cao mà còn giả thuyết thì đưa vào danh sách câu hỏi xác nhận với khách.
