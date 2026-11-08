---
name: office
description: Mở, tắt, xem trạng thái hoặc chạy demo văn phòng ảo LINHX (2D pixel / 3D) hiển thị Claude Code, subagent và worker Antigravity đang làm gì; cài hook cho Antigravity CLI.
argument-hint: "[open 2d|open 3d|start|stop|status|demo|install-agy|uninstall-agy]"
user_invocable: true
---

# /office

Văn phòng ảo LINHX: mỗi phiên Claude Code là một chú mèo áo cam ngồi ở "Bàn Claude", subagent áo tím đứng cạnh, worker Antigravity (`agy`) áo xanh ngồi ở "Bàn Antigravity". Đọc nhiều file thì ra thư viện, tra web thì ra sofa, giao việc thì ra bàn họp, xong lượt thì ra quầy cà phê, cần quyền thì giơ tay với bong bóng "!".

Hook của plugin tự gửi sự kiện tới server cục bộ `http://127.0.0.1:4848` và tự bật server khi mở phiên mới. Không có gì rời khỏi máy.

## Cách dùng

Mọi lệnh chạy qua script trong plugin. Đường dẫn script: `${CLAUDE_PLUGIN_ROOT}/scripts/office.js`.

Lấy lệnh con từ `$ARGUMENTS` (mặc định `open 2d`) rồi chạy đúng một lệnh:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/office.js" <lệnh con>
```

| Lệnh con | Việc |
|---|---|
| `open 2d` / `open 3d` | Bật server nếu chưa chạy và mở văn phòng trong trình duyệt |
| `start` / `stop` / `status` | Bật, tắt, xem trạng thái server và hook Antigravity |
| `demo` | Chạy kịch bản mẫu khoảng 40 giây (1 Claude, 1 subagent, 2 worker agy) để xem thử |
| `install-agy` | Ghi nhóm hook `linhx-office` vào `~/.gemini/config/hooks.json` (sao lưu file cũ thành `.bak-linhx-office`) |
| `uninstall-agy` | Gỡ nhóm hook đó |

Sau khi chạy, báo lại cho người dùng đúng dòng script in ra (URL hoặc trạng thái). Với `demo`, chạy ở nền (`run_in_background`) để không giữ lượt, và đưa người dùng link `/2d` và `/3d`.

## Ghi chú
- Đổi cổng: đặt biến môi trường `LINHX_OFFICE_PORT` cho cả Claude Code và agy.
- Không muốn hook tự bật server: `LINHX_OFFICE_AUTOSTART=0`.
- Worker agy được Claude gọi bằng `agy -p` sẽ được xếp làm "nhân viên" của phiên Claude đó (nhờ biến `CLAUDE_CODE_SESSION_ID`). Có thể ép bằng `LINHX_OFFICE_PARENT=<session id>`.
