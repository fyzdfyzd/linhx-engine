---
name: chien-luoc
description: Xây chiến lược theo chuẩn cao kiểu Trân Bảo / Kim Gia Bảo Gift / BTMH IPO - nghiên cứu tới đâu lưu tới đó, đào sâu khách hàng mục tiêu và định vị đối thủ, tìm khoảng trống thị trường, quyết định sản phẩm hoặc thông điệp. Dùng khi Linh hoặc khách cần chiến lược, PMF, GTM, định vị, kế hoạch thương hiệu.
---

# chien-luoc

Đọc `linhx-chuan` trước. Skill này chỉ thêm phần riêng của chiến lược.

Mọi khuôn mẫu nằm trong `references/`, đọc file của bước đang làm:

| Bước | Đọc |
|---|---|
| 1 | `references/01-cau-truc-du-an.md` (cây thư mục, STATUS, ANCHOR, DATA_GAPS) |
| 2 | `references/07-nghien-cuu-nen-va-ipo.md` (danh mục NC), `linhx-chuan/references/cong-cu.md`, `linhx-chuan/references/nguon-tham-chieu.md` |
| 3 | `references/02-phan-khuc-omc-11-lop.md` |
| 4 | `references/03-doi-thu-dinh-vi.md` |
| 5 | `references/04-khoang-trong.md` |
| 6 | `references/05-quyet-dinh-pmf.md` (PMF, CVP/USP/UVP, 12 tiêu chí so phương án, Go/No-Go) |
| 7 | `references/06-chung-thuc.md` |
| cuối | `references/08-bai-hoc.md` (đọc trước khi bắt đầu, ghi thêm khi xong) |

Thang chấm: `linhx-chuan/cham.md`, nguồn thang: `linhx-chuan/references/high-standard.md`. Các khuôn rút từ dự án Trân Bảo, Kim Gia Bảo Gift và BTMH IPO (chị Quỳnh Hương, 2026), đã bỏ số liệu mật.

## Thư mục việc

```
<DU-AN>/
  BRIEF.md  ANCHOR.md  STATUS.md  DATA_GAPS.md  HANH-TRINH-NGUOI-XEM.md  THAM-CHIEU.md
  NC1_<chu-de>_<ngay>.md  NC2_...  (mỗi nghiên cứu một file, không ghi đè; bản mới là NC2_V2_...)
  PHAN-KHUC_<ngay>.md  DOI-THU_<ngay>.md  KHOANG-TRONG_<ngay>.md  QUYET-DINH_<ngay>.md
  CHUNG-THUC_<ngay>.md  bang-chung/INDEX.md  DUYET-E2E.md  BAI-HOC.md
```

## 7 bước

Mỗi bước xong thì lưu file, sửa `STATUS.md`, ghi chỗ thiếu vào `DATA_GAPS.md`, rồi mới sang bước sau. Bước 1, 5 và 7 cần Linh hoặc khách duyệt.

1. **Brief và anchor.** Mục tiêu có số, khách là ai, ràng buộc. `ANCHOR.md` ghi dự án là gì và không phải là gì (xem mẫu Trân Bảo: "không phải luxury niche, không copy Hanoia"). Điền hành trình người xem: thường là ban lãnh đạo đọc tóm tắt điều hành trên giấy hoặc màn hình họp, nên trang đầu phải tự đứng được.
2. **Nghiên cứu nền, đánh số NC.** Mỗi câu hỏi một NC: thị trường tách lớp, xu hướng, case nước ngoài, diễn ngôn khách hàng trên mạng xã hội, kênh, giá. Dùng skill `nghien-cuu` (Gemini Deep Research Ultra trước, crawler sau). Mỗi số gắn `[BC-xxx]`.
3. **Phân khúc siêu chi tiết** (`PHAN-KHUC`). Mô hình nhiều lớp kiểu OMC, đặt các nhóm lên **ma trận 2 trục** (ví dụ giá trị × khả năng thắng) rồi mới chọn. Mỗi chân dung theo khung cố định: ai, job (Khi… tôi muốn… để…), nỗi đau, rào cản, kênh, **trích lời thật**, quy mô. Có cả B2C và B2B nếu có.
4. **Đối thủ và định vị** (`DOI-THU`). Ít nhất 4 đối thủ có tên và có số (doanh thu, cửa hàng, giá, kênh, thông điệp). SWOT của mình. Canvas định vị và canvas đại dương xanh: yếu tố nào giảm, bỏ, tăng, tạo mới.
5. **Khoảng trống** (`KHOANG-TRONG`). Chồng ma trận phân khúc lên bản đồ đối thủ: ô nào khách có nhu cầu chưa được đáp ứng mà đối thủ bỏ trống hoặc làm kém. Mỗi khoảng trống có bằng chứng và cỡ thị trường. Linh duyệt chọn khoảng trống (cổng D2).
6. **Quyết định** (`QUYET-DINH`). Mở bằng tóm tắt điều hành. 2–3 phương án sản phẩm hoặc thông điệp khác nhau thật; nếu khách có phương án riêng thì đặt ngang hàng (mẫu `DANH_GIA_2_PHUONG_AN_PMF.md`: AI và chị Hương, chấm 12 tiêu chí, rồi tìm phương án lai). Thông điệp theo tầng: ý lớn, trụ cột, bằng chứng. Mỗi phương án có cổng Go/No-Go: thời điểm, chỉ số, việc làm khi trượt.
7. **Chứng thực và duyệt như khán giả** (`CHUNG-THUC`). Bảng mỗi luận điểm → nguồn nội bộ → nguồn ngoài (mẫu `Chung_Thuc_Du_Lieu_NC7_V4`). Mở 5 số ngẫu nhiên đối chiếu. Rồi đọc trọn bản cuối như người xem trong hành trình, ghi `DUYET-E2E.md` có ảnh.

## Chấm

3 người chấm khác thợ (agy, Gemini model khác đóng vai đối thủ khó tính, Claude máy công ty), theo `linhx-chuan/cham.md` cộng 3 tiêu chí riêng:
- **Độ sâu khách hàng:** chân dung đủ khung, có trích lời thật, có job.
- **Định vị đối thủ:** có tên, có số, có canvas.
- **Từ khoảng trống tới quyết định:** đọc được một mạch từ dữ liệu → khoảng trống → phương án, không nhảy cóc.

Tối đa 3 vòng sửa, vòng tệ hơn thì hoàn tác (`linhx-chuan` luật 7).

## Kiểm máy

```
python ../linhx-chuan/scripts/kiem.py <DU-AN> --pha dau
python ../linhx-chuan/scripts/kiem.py <DU-AN> --pha cuoi --loai chien-luoc
```

## Xuất

Bản chính là `.md`. Khách cần thì xuất `.docx` (skill docx hoặc pandoc), hoặc slide qua workflow `slide`.

Skill này cần `linhx-chuan` cài cùng chỗ (thư mục anh em trong `.agents/skills/` hoặc `.claude/skills/`).
