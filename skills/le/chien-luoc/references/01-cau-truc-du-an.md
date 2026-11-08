# 01 · Cấu trúc dự án và sổ "làm tới đâu lưu tới đó"

Rút từ dự án Trân Bảo (BTMH, chủ dự án chị Quỳnh Hương, 4/2026). Đây là cách làm đã được khách duyệt: tài liệu chia đề bài và nghiên cứu đánh số, mỗi cái một file, có tracker, có kim chỉ nam, có sổ khoảng trống dữ liệu.

## 1. Cây thư mục

```
<DU-AN>/
├── BRIEF.md                  brief gốc của khách + tổng hợp brief
├── ANCHOR.md                 kim chỉ nam, chỉ đổi khi khách góp ý
├── STATUS.md                 tracker, sửa sau MỖI file
├── DATA_GAPS.md              số còn thiếu, hỏi ai
├── QUYET-DINH-KHACH_<ngày>.md  biên bản mỗi lần khách/lãnh đạo chốt
├── STEP1_ONBOARDING/         đề bài 1..n (khung quản trị, phân khúc, kiến trúc SP, GTM, đối tác, PMF)
├── STEP2_WINNING_MODEL/      mô hình thắng (case nước ngoài)
├── STEP3_DIAGNOSIS/          chẩn đoán hiện trạng khách
├── STEP4_STRATEGY/           định vị, phương án, GTM chia phần
├── STEP5_EXECUTION/          lịch triển khai, ngân sách, KPI
├── RESEARCH/                 NC1_..., NC2_..., NC7_V4_... + CHUNG-THUC
├── PRODUCT_MARKET_FIT_TEMPLATE/  tài liệu mẫu high standard dùng làm thước
├── bang-chung/               nguyên văn nguồn, INDEX.md
└── OUTPUT/                   bản xuất docx, pdf, pptx gửi khách
```

Dự án nhỏ thì gộp phẳng như trong `SKILL.md` (BRIEF, ANCHOR, NC*, PHAN-KHUC, DOI-THU, KHOANG-TRONG, QUYET-DINH, CHUNG-THUC). Dự án lớn nhiều đợt thì dùng cây STEP1–5.

## 2. Đặt tên và phiên bản

- Nghiên cứu: `NC<số>_<CHU_DE_VIET_HOA>_<ddmmyyyy>.md`. Bản sửa lớn: `NC7_V2_...`, `NC7_V3_...`. **Không ghi đè bản cũ.** Khách có thể chọn lại bản cũ (chị Hương 31/10: bản đầu đẹp hơn bản sửa).
- Đề bài: `DE_BAI_<số>_<TEN>.md`. Mỗi file mở đầu bằng khối:

```
> **Dự án**: ...
> **Đơn vị**: ...
> **Phân loại**: Tài liệu chiến lược nội bộ, trình Ban Lãnh đạo
> **Phiên bản**: 3.0 | Ngày: 10/04/2026
> **Nền tảng**: lọc chéo từ NC2, NC5, NC7 (ghi rõ dựa trên nghiên cứu nào)
```
và kết thúc bằng `*Phiên bản: x | Ngày: ... | Lập: ...*`.

## 3. STATUS.md (mẫu đã dùng)

```
# TIẾN ĐỘ DỰ ÁN <TÊN>
> Cập nhật: 11/04/2026 05:30 · Chủ dự án: <khách>

## Đầu ra
| # | Đầu ra | Trạng thái | File | DOCX |
| 1 | Khung quản trị | ✅ V1.0 | STEP1_ONBOARDING/DE_BAI_1_... | ✅ |
| 3 | Kiến trúc sản phẩm | 🟡 Khung | ... | |

## Nghiên cứu
| # | Chủ đề | Trạng thái | File | DOCX |
| NC1 | Công nghiệp văn hoá và thuận thế (Trung Quốc) | ✅ | RESEARCH/NC1_... | ✅ |

## Thay đổi V2.0 (ngày)
- Đề bài 4 xong 6/6 phần: ... (mỗi phần một dòng, nêu cái mới)
```

Luật: tạo hoặc sửa xong một file thì sửa STATUS ngay trong cùng lượt. Máy kiểm `kiem.py --pha cuoi` báo lỗi nếu có file nội dung mà STATUS chưa nhắc.

## 4. ANCHOR.md (mẫu đã dùng)

Mở bằng: "Kim chỉ nam chiến lược. Mọi nghiên cứu, đầu ra, đề xuất PHẢI nhất quán với file này. Chỉ cập nhật khi có góp ý mới từ Ban dự án hoặc Ban lãnh đạo."

Các mục đã có trong ANCHOR Trân Bảo, dùng làm khung:
1. **Dự án là gì** (một câu định nghĩa).
2. **Dự án KHÔNG PHẢI là gì** (liệt kê ❌, ví dụ: không phải thương hiệu xa xỉ ngách, không chỉ cho người giàu, không copy đối thủ X).
3. **Dự án LÀ** (liệt kê ✅, ví dụ: hệ sinh thái phủ mọi phân khúc, hai nhánh chiến lược).
4. **Các nhánh chiến lược** và tiểu nhóm trong mỗi nhánh.
5. **Điều khách đã bác** (ví dụ: không đi theo xa xỉ ngách).
6. **Sự thật về năng lực** (ví dụ: công nghệ đã phổ thông, ai cũng có, không phải lợi thế; khách không có đội thợ thủ công lớn nên phải thuê ngoài).
7. **Khác biệt so với 2 đối thủ chính** (bảng DNA, phạm vi, di sản).
8. **Bài toán khó còn mở** (ví dụ chiến lược giá; định kiến "đeo vàng là trọc phú" phải giải bằng trào lưu chứ không bằng lý lẽ), mỗi bài toán thành một đề nghiên cứu riêng.
9. **Lộ trình và mốc năm cơ sở.**
10. **Lịch sử góp ý** (ngày, ai, đổi mục nào).

Vì sao cần: AI hay tự "sáng tạo" lệch hướng khách đã chốt. Anchor là thứ người chấm mở đầu tiên để bắt lệch.

## 5. DATA_GAPS.md (mẫu đã dùng)

```
| # | Dữ liệu thiếu | Nguồn cần hỏi | Mức độ | Ngày phát hiện |
| 1 | Danh sách vùng ưu tiên thí điểm | Ban lãnh đạo | 🔴 Chặn | 07/04/2026 |
| 3 | Chiến lược giá bán lẻ và bán sỉ | Tài chính | 🟡 Cao | 07/04/2026 |
| 7 | Doanh số theo vùng hiện tại | Phòng dữ liệu | 🔵 Vừa | 07/04/2026 |
```
Luật: thiếu số thì ghi vào đây và viết "[CHỜ SỐ: gap #3]" trong bài. Không ước bừa, không lấy số nước ngoài thay số Việt Nam mà không ghi rõ.

## 6. Biên bản quyết định

Mỗi lần khách hoặc chủ tịch chốt điều gì (ví dụ `CHAIRMAN_DECISION_0205.md`), ghi một file: ngày, ai chốt, chốt gì, mục nào trong ANCHOR phải sửa. Sau đó sửa ANCHOR và ghi vào lịch sử góp ý.
