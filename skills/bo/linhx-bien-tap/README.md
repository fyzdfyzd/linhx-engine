# linhx-bien-tap (v0.1, 19/10/2026)

Plugin biên tập bài tiếng Việt, nửa còn lại của plugin viết `linhx-viet-giong-viet`. Dựng từ: hai prompt biên tập gốc của Linh (CQS, APS) và checklist biên tập của Linh (LAB025), phản biện luồng OPC (`../../PHAN-BIEN-LUONG-OPC.md`), lượt chạy lại tuyến PA1 với ba vòng chấm từng câu (`../../bai/2026-10-19-opc-pa1-v3/`), và bảy bài Linh đã đăng báo làm mốc giọng.

## Cài
```
/plugin marketplace add <đường dẫn tới LAB049-VIET-NHU-NGUOI/src>
/plugin install linhx-bien-tap@linhx-lab049
```
Script Python chỉ dùng thư viện chuẩn. Xuất docx cần Node và `npm i docx` một lần.

## Dùng
- Biên tập một bài: "biên tập bài này" kèm file → skill `bien-tap-bai`.
- Chỉ chấm từng câu: skill `cham-tung-cau`.
- Đưa bản sửa của Vân Anh vào: đặt file vào `mau-sua/van-anh-<ngay>-<ten-bai>/`, rồi "học từ bản sửa của Vân Anh" → skill `hoc-tu-ban-sua`.

## Sáu lượt biên tập
| Lượt | Skill | Ai làm | Chặn khi |
|---|---|---|---|
| 0. Máy | script | `cham_cau.py`, `kiem_van_dich.py`, `kiem_van.py` | trượt ngưỡng giọng, câu số liệu thiếu mã nguồn, lỗi cũ quay lại |
| 1. Sự thật | `soat-su-that` | subagent | câu nói nhiều hơn nguồn, bịa, sai thuật ngữ luật |
| 2. Cấu trúc | `soat-cau-truc` | subagent | đoạn phải viết lại, lệch độ dài |
| 3. Ngôn ngữ | `soat-ngon-ngu` | 2 subagent chạy nguyên văn prompt CQS và APS của Linh | CQS < 85, APS > 30 |
| 4. Chấm từng câu | `cham-tung-cau` | 2 giám khảo + `tong_hop_cham.py` | GIỮ < 25%, có CẮT, SỬA > 10%, đoạn không có câu GIỮ |
| 5. Độc giả | `doc-gia-ao` | 2–3 subagent nhập vai | độc giả mang về điều khác luận điểm |

Ra một **phiếu biên tập** (`references/mau-phieu.md`): lỗi chặn, nặng, nhẹ, câu tác giả quyết, câu không được đụng, dòng mới cho sổ hồi quy.

## Học giống một biên tập viên cụ thể
`ho-so-bien-tap/<ten>/` chứa `LUAT.md` (luật rút từ bản sửa thật, mỗi luật ít nhất hai bằng chứng), `SO-DO.md`, `HIEU-CHUAN.md`.
- `linh/`: đang trống. Chỉ học từ bài Linh đã đăng báo; cần cặp bản nộp và bản đăng (hoặc bản Linh sửa trước khi gửi báo) của một bài đã đăng.
- `van-anh/`: 8 luật rút từ 20 comment của chị trên bản PA1 cũ (19/10), mã `HV AD FT CT CK DN` đã vào đề giám khảo. Hướng dẫn cho chị Vân Anh: `mau-sua/HUONG-DAN-VAN-ANH.md`; ba bài để chị sửa: `mau-sua/cho-van-anh/`.

## Script
| Script | Làm gì |
|---|---|
| `cham_cau.py` | tách câu, gắn cờ từng câu, so ngưỡng giọng; `--xuat-cau` cho giám khảo; `--sach` bỏ mã nguồn |
| `tong_hop_cham.py` | gộp bảng hai giám khảo, so ngưỡng, liệt kê câu lệch |
| `doc_ban_sua.py` | đọc Word Track Changes (kèm comment) hoặc cặp trước/sau, gióng câu, liệt kê từng chỗ sửa và kiểu sửa |
| `kiem_van_dich.py`, `kiem_van.py` | soát văn dịch, đo giọng theo mốc Linh (từ plugin viết) |
| `kiem_nhap.py` | so bài với nháp gạch đầu dòng của tác giả: gạch bị rơi, đoạn máy tự thêm, số lạ |
| `build_docx.js` | dàn docx một bài |

## Giới hạn đã biết
- Giám khảo, biên tập, độc giả đều là Claude (Sonnet). Lượt chạy thử cho thấy chúng tách được bản Linh và bản máy, nhưng chưa thay được người. Bước kế: một lượt bằng Gemini như `reviewer.py` gốc.
- Mốc giọng và ngưỡng máy đo trên 7 bài Linh đã đăng báo (Dân trí, VnExpress). Ngưỡng giám khảo (GIỮ ≥25%, CẮT 0, SỬA ≤10%) là tạm, chưa hiệu chuẩn lại trên bài đã đăng.
- Độ phủ (máy bắt được bao nhiêu phần chỗ người sửa) chưa đo được vì chưa có bài mẫu sửa.
