---
name: thu-ky
description: Bật, mở, tắt hoặc cấu hình thư ký ảo LINHX (nhân vật video nói chuyện bằng giọng, kể tình hình các dự án và giao việc cho Claude Code ở từng thư mục). Dùng khi Linh gõ /thu-ky hoặc nhắc tới thư ký ảo, phòng chỉ huy, nhân vật điều phối.
---

# Thư ký ảo LINHX

Chạy script điều khiển bằng Node (đường dẫn plugin có sẵn trong biến `${CLAUDE_PLUGIN_ROOT}`):

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/thu-ky.js" <lệnh>
```

| Linh gõ | Lệnh |
|---|---|
| `/thu-ky` hoặc `/thu-ky open` | `open`: bật server nếu chưa chạy rồi mở trình duyệt ở http://127.0.0.1:4850/ |
| `/thu-ky setup` | `setup --linhx` (máy của Linh: dự án ở D:/LINHX/LAB và D:/LINHX/PRJ, nhân vật Emily của Live Character, khoá Gemini đọc từ .env của Live Character) |
| `/thu-ky setup <tham số>` | `setup --roots "D:/A;D:/B" --character <file nhân vật .json> --videos <thư mục clip> --env <file .env> --permission acceptEdits` |
| `/thu-ky status` | `status` |
| `/thu-ky stop` | `stop` |

Sau khi chạy, báo lại đúng dòng script in ra (đường dẫn, có Gemini hay chưa, nhân vật nào). Nếu chưa có khoá Gemini, nói rằng trang vẫn dùng được ở chế độ gõ chữ, và Linh có thể thêm `GEMINI_API_KEY` vào file .env đã khai báo.

Không tự đọc hay in nội dung file .env. Không sửa `permissionMode` sang chế độ bỏ qua quyền.

## Thư ký làm được gì
- Kể danh sách dự án, tình hình một dự án (OVERVIEW, cuối LOG, phiên Claude Code gần nhất ở thư mục đó).
- Xem ai đang làm (đọc văn phòng linhx-office nếu đang bật ở cổng 4848) và các việc đã giao.
- `hoi_claude`: hỏi Claude trong thư mục dự án, chỉ đọc (`--permission-mode plan`).
- `giao_viec`: giao việc cho Claude trong thư mục dự án (`--permission-mode acceptEdits` mặc định); kết quả tự báo lại bằng giọng.
