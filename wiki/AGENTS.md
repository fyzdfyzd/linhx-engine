# Wiki LINHX: luật chung cho mọi agent

Đây là **bộ nhớ chung** của LINHX ENGINE, các unit, BU và dự án. Claude (mọi thread, mọi máy), Antigravity (agy), Gemini, Copilot và người đều đọc ở đây trước khi làm, để không thread nào mù thông tin của thread khác.
Mô hình: LLM Wiki của Karpathy. `nguon/` là tài liệu gốc, `trang/` là trang biên soạn, `INDEX.md` là mục lục, `LOG.md` là nhật ký.
Viết tiếng Việt có dấu, câu ngắn, đủ ý.

## Đọc (mọi việc đều bắt đầu thế này)
1. Đọc `INDEX.md`. Không quét cả cây.
2. Mở `trang/tong-quan.md` nếu chưa biết bức tranh, rồi trang đúng việc.
3. Cần chi tiết hay bằng chứng thì theo link sang `nguon/` hoặc nguồn ngoài ghi ở cuối trang.
4. Xem 10 dòng cuối `LOG.md` để biết ai vừa đổi gì.

## Ghi (khi việc của bạn làm thay đổi sự thật)
Có quyết định mới, trạng thái mới, đường dẫn mới, đề bài mới, output mới thì ghi ngay trong lượt đó:
1. Sửa trang liên quan trong `trang/` (hoặc tạo trang mới từ khung dưới). Một trang một chủ đề.
2. Quyết định của Linh: thêm một dòng vào `trang/quyet-dinh.md` (ngày giờ, ai chốt, chốt gì, link).
3. Việc chờ Linh: thêm/xoá dòng ở `trang/cho-linh.md`.
4. Trang mới: thêm một dòng vào `INDEX.md`.
5. Thêm một dòng cuối `LOG.md`: `YYYY-MM-DD HH:MMZ | ai | nap/sua/ra | trang | một câu`.
6. Tài liệu gốc mới (bàn giao, đề, báo cáo): chép vào `nguon/` tên `YYYY-MM-DD-TEN-IN-HOA.md`. **Không sửa file trong `nguon/`** sau khi đã chép; bản mới là file mới.

## Cấm
- Không ghi bí mật: mật khẩu, token, khoá API, cookie, số tài khoản, dữ liệu khách. Chỉ ghi "nằm ở đâu".
- Không xoá trang. Hết hiệu lực thì đổi `trang_thai: cu` và ghi trang thay thế.
- Không chép nguyên văn dài vào `trang/`. Trang là bản tóm có link về nguồn.
- agy không tự sửa `trang/quyet-dinh.md`; agy ghi đề xuất vào `LOG.md` với loại `de-xuat`, Claude duyệt rồi mới ghi.

## Khung trang
```
---
tieu_de: <tên>
loai: tong-quan | loi | unit | du-an | he | danh-muc
trang_thai: dang-chay | cho-linh | tam-dung | xong | cu
cap_nhat: YYYY-MM-DD
nguon: [<link nguon/ hoặc URL>]
---
# <tên>
**Một câu:** là gì, đang ở đâu.
## Hiện trạng   (đúng tới ngày cap_nhat)
## Đã chốt      (link quyet-dinh)
## Chờ          (link cho-linh)
## Ở đâu        (repo, nhánh, thư mục máy, artifact)
## Liên quan    ([[trang-khac]])
```
Liên kết giữa trang dùng `[[ten-file-khong-duoi]]`, hai chiều khi có thể.

## Ba thao tác
| Lệnh | Làm |
|---|---|
| **nạp wiki: <nguồn>** | Chép nguồn vào `nguon/`, sửa mọi trang liên quan, cập nhật INDEX, quyet-dinh, cho-linh, LOG. |
| **hỏi wiki: <câu>** | INDEX → trang → nguồn, trả lời kèm link trang. Câu trả lời đáng giữ thì thành trang mới. |
| **rà wiki** | `python scripts/ra_wiki.py`: link gãy, trang mồ côi, trang thiếu khung, trang cũ hơn 14 ngày. Sửa rồi ghi LOG. |

## Bản chính và bản sao
Bản chính là thư mục `wiki/` trên nhánh `main` của repo `fyzdfyzd/linhx-engine`. Máy cty kéo bằng `git pull`. Bản ở thư mục chung dự án Claude, memory Claude hay D:\LINHX chỉ là bản sao; khi khác nhau, `main` thắng, và ai thấy khác thì sửa `main`.
