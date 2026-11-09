---
name: chuan-code
description: "Chuẩn viết code của LINHX theo 4 nguyên tắc Karpathy: nghĩ trước khi code, tối giản, sửa đúng chỗ, làm theo mục tiêu kiểm được. Dùng khi viết, sửa, review hoặc refactor code, script, hook, plugin hay skill có script trong mọi lab."
---

# Chuẩn code LINHX

Dựa trên [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) (MIT, tác giả forrestchang), vốn đúc kết từ [nhận xét của Andrej Karpathy](https://x.com/karpathy/status/2015883857489522876) về các lỗi hay gặp khi LLM viết code. Bản gốc nằm ở `references/KARPATHY-GOC.md`; ví dụ đúng và sai bằng code thật ở `references/VI-DU-GOC.md`.

Chỉnh cho LINHX ở nguyên tắc 1: bản gốc dặn "không chắc thì hỏi". Ở LINHX, chỉ hỏi khi ngã rẽ làm đổi mục tiêu hoặc không hoàn tác được. Các trường hợp còn lại thì nêu rõ giả định, chọn mặc định hợp lý và đi tiếp (luật số 5).

Với việc vặt (sửa một dòng, đổi tên), dùng phán đoán, không cần làm đủ thủ tục.

## 1. Nghĩ trước khi code

**Không giả định ngầm. Không giấu chỗ chưa rõ. Nêu đánh đổi.**

- Viết giả định ra, ví dụ: "Giả định file CSV có dòng tiêu đề, mã hoá UTF-8".
- Yêu cầu hiểu được theo nhiều cách: liệt kê các cách hiểu, nói mình chọn cách nào và vì sao. Không chọn âm thầm.
- Có cách đơn giản hơn thì nói ra; cần thì phản biện yêu cầu.
- Chỗ chưa rõ mà ảnh hưởng mục tiêu: dừng, gọi tên chỗ đó, rồi hỏi Linh bằng câu trả lời được một từ.

## 2. Tối giản trước

**Ít code nhất mà giải quyết được việc. Không làm cho trường hợp tưởng tượng.**

- Không thêm tính năng ngoài yêu cầu.
- Không tạo lớp trừu tượng cho code chỉ dùng một lần.
- Không thêm "tuỳ biến" hay "cấu hình" khi chưa ai cần.
- Không bắt lỗi cho tình huống không thể xảy ra.
- Viết 200 dòng mà làm được bằng 50 dòng thì viết lại.
- Ưu tiên thư viện chuẩn (Node, Python) như các plugin linhx đang làm. Chỉ thêm phụ thuộc khi có lý do ghi trong PLAN.md.

Tự hỏi: "Một kỹ sư giỏi có thấy chỗ này rườm rà không?" Nếu có, rút gọn.

## 3. Sửa đúng chỗ

**Chỉ chạm vào chỗ phải sửa. Chỉ dọn rác do chính mình tạo ra.**

- Không "tiện tay" sửa code, comment hay định dạng ở chỗ bên cạnh.
- Không refactor thứ đang chạy tốt.
- Viết theo phong cách sẵn có của file, kể cả khi mình thích cách khác.
- Thấy code chết không liên quan thì ghi chú cho Linh, không tự xoá.
- Xoá import, biến, hàm mà **chính thay đổi của mình** làm thừa. Không xoá code chết có sẵn khi chưa được yêu cầu.

Phép thử: mỗi dòng thay đổi phải truy ngược được về yêu cầu của Linh.

## 4. Làm theo mục tiêu kiểm được

**Đặt tiêu chí thành công rồi lặp đến khi kiểm xong.**

Đổi việc thành mục tiêu kiểm được:

| Yêu cầu | Mục tiêu kiểm được |
|---|---|
| "Thêm kiểm tra dữ liệu" | Viết ca thử với dữ liệu sai, rồi sửa đến khi qua |
| "Sửa lỗi" | Viết ca thử tái hiện lỗi, rồi sửa đến khi qua |
| "Refactor X" | Ca thử qua cả trước và sau |
| "Script quét chạy được" | Chạy trên dữ liệu mẫu, ra đúng số dòng hoặc file mong đợi |

Việc nhiều bước thì viết kế hoạch ngắn, mỗi bước kèm cách kiểm (ghi vào PLAN.md nếu lab có):

```
1. <bước> → kiểm: <lệnh hoặc dấu hiệu>
2. <bước> → kiểm: <lệnh hoặc dấu hiệu>
```

Tiêu chí mạnh cho phép tự lặp mà không phải hỏi lại. Tiêu chí yếu như "làm cho chạy" thì lúc nào cũng phải hỏi. Trước khi báo xong, chạy skill `xac-minh-truoc-khi-bao-xong`.

## Dấu hiệu đang làm sai

| Nguyên tắc | Làm sai | Cách đúng |
|---|---|---|
| Nghĩ trước | Âm thầm đoán định dạng file, trường dữ liệu, phạm vi | Liệt kê giả định, nói đã chọn gì |
| Tối giản | Dựng cả "strategy pattern" cho một phép tính | Một hàm, đến khi thật sự cần thêm |
| Sửa đúng chỗ | Sửa lỗi xong tiện tay đổi dấu nháy, thêm type hint | Chỉ đổi các dòng sửa lỗi |
| Theo mục tiêu | "Để mình xem và cải thiện code" | "Viết ca thử cho lỗi X, sửa đến khi qua, kiểm không vỡ chỗ khác" |

Code tốt là code giải quyết việc hôm nay một cách đơn giản, không phải giải quyết sớm việc của ngày mai.

**Dấu hiệu chuẩn này đang có tác dụng:** diff ít thay đổi thừa, ít phải viết lại vì rườm rà, câu hỏi làm rõ xuất hiện trước khi code chứ không phải sau khi đã sai.
