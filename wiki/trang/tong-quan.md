---
tieu_de: Bức tranh tổng thể LINHX
loai: tong-quan
trang_thai: dang-chay
cap_nhat: 2026-11-08
nguon: [nguon/2026-11-05-CHOT-KIEN-TRUC.md, nguon/2026-11-06-BAN-GIAO-QUY-HOACH-TUNG-UNIT.md, https://claude.ai/artifact/Wyeq3HaoB6pfgoeC11P2qY]
---
# Bức tranh tổng thể LINHX

**Một câu:** LINHX ENGINE là một lõi chung (trên Frappe) để launch sản phẩm, dịch vụ nhanh nhất mà vẫn nhận cập nhật lõi; mỗi unit, BU, OPC là một bản cài riêng cắm module; agy làm, Claude canh, Linh duyệt.

## Đọc tiếp theo thứ tự
1. [[dich-cuoi]]: vision, 5 thay đổi, từng đơn vị nay và khi đủ, đích 30/6/2027.
2. [[kien-truc]]: 6 tầng, module lõi, máy nền, template, tái dùng PROTO. Bản đang chạy: [[loi-engine]].
3. [[lo-trinh]]: 4 chặng, Chặng 0 chia làn, khuôn launch.
4. [[hop-nhat]]: dự án nào gộp vào đâu, khi nào, 5 luật cho dự án đang chạy song song.
5. [[danh-muc-he-thong]]: 63 dòng, mỗi dòng khách, nỗi đau, việc khách cần, người dùng thấy gì.

## Số đo chính
Thời gian từ ý tưởng tới đơn đầu tiên (Linh 6/11). Phụ: giờ Linh bỏ ra, tiền về.

## Ba vòng hệ thống (59 unit, danh sách h01–h63)
| Vòng | Gồm | Trang |
|---|---|---|
| Trong LINHX | EDU (Course OS, cungai, Sakedemy), Agent Force, Personal Brand (Expert OS), nền dùng chung | [[he-thong-linhx-edu]] [[he-thong-linhx-agent-force]] [[he-thong-linhx-personal-brand]] [[he-thong-nen-dung-chung]] |
| Giữa các BU | Unikon, ifAgent, TUVA, Sakedemy, URAH, thương hiệu khác | [[he-thong-unikon]] [[he-thong-ifagent]] [[he-thong-tuva]] [[he-thong-sakedemy]] [[he-thong-urah]] [[he-thong-thuong-hieu-khac]] |
| Dự án | 15 dự án (danh sách ở [[he-thong-du-an]]); đang chạy: Chiêm Tinh Số, Máy quét, OPC Live | [[du-an-chiem-tinh-so]] [[du-an-may-quet]] [[du-an-opc-live]] |

## Cách ghép (Linh chốt 6/11)
Theo cơ chế WordPress: chung code lõi, mỗi cụm (LINHX nội bộ, từng BU, mỗi OPC, Content hub) một bản cài + DB riêng, module là plugin, nối bằng `linhx_id` + API. Chi tiết: [[loi-engine]].

## Cách làm việc
- agy làm theo phiếu ≤ 40 phút, Claude canh và chấm, Linh duyệt: [[he-du-an-tu-chay]].
- Máy nào chạy gì: [[he-may-va-tai-khoan]].
- Artifact và doc đang dùng (giữ URL, không lập bản mới): [[danh-muc-artifact]].
- Đề bài, features, nghiệm thu: [[danh-muc-de-bai]].
- Quyết định đã chốt: [[quyet-dinh]]. Việc chờ Linh: [[cho-linh]].

## Đích gần
Đợt 1 engine: một lead đi trọn đường và một đơn báo cáo trả QR tự giao, trên hai bản cài `linhx` và `ifagent`.
