# linhx-office · Văn phòng ảo xem agent làm việc

Plugin Claude Code (v0.1.0, MIT). Khi Claude Code chạy, mỗi agent hiện thành một chú mèo trong văn phòng 2D pixel hoặc 3D; worker Antigravity (`agy`) ngồi cùng phòng với Claude giao việc cho nó.

```
Claude Code ── hooks/hooks.json ──┐
                                  ├─ node hooks/send.js ── POST 127.0.0.1:4848/hook ── bridge/server.js ── SSE ── web/2d.html | web/3d.html
agy ── ~/.gemini/config/hooks.json┘
```

## Cài trên máy (Windows, macOS, Linux; cần Node 18+)

```bash
# 1. Thêm marketplace của lab (thư mục chứa .claude-plugin/marketplace.json)
claude plugin marketplace add "D:/LINHX/LAB/LAB021-VAN-PHONG-AO-AGENT/src"
# 2. Cài plugin
claude plugin install linhx-office@linhx-lab
# 3. Mở phiên Claude Code mới, gõ:
/office open 2d        # hoặc /office open 3d
# 4. (tuỳ chọn) nối Antigravity CLI
/office install-agy
```

Thử nhanh không cần cài: `claude --plugin-dir "<đường dẫn>/linhx-office"`, hoặc chạy thẳng `node scripts/office.js demo` rồi mở `http://127.0.0.1:4848/2d`.

## Thành phần

| Thư mục | Module | Ghi chú |
|---|---|---|
| `hooks/hooks.json`, `hooks/send.js` | M1 hook Claude, M2 hook agy | Node thuần, timeout ngắn, luôn exit 0; tự bật server khi `SessionStart` |
| `bridge/normalize.js` | M3 chuẩn hoá sự kiện | Claude + agy → `{agent, parent, source, state, detail…}` |
| `bridge/server.js` | M4 bridge | Không thư viện ngoài, chỉ nghe 127.0.0.1, SSE; cảnh báo 2 agent sửa cùng file, lệnh lỗi 3 lần liên tiếp |
| `web/office-core.js` | M5 phần chung | Bố trí phòng, luật đi lại, bảng bên, nhật ký |
| `web/2d.html` | M5 skin 2D | Canvas pixel, vẽ bằng code, không dùng asset có bản quyền |
| `web/3d.html` | M5 skin 3D | Three.js r128 (kèm sẵn `web/vendor/three.min.js`, MIT), chạy offline |
| `skills/office/SKILL.md`, `scripts/office.js` | M6 skill điều khiển | `/office open|start|stop|status|demo|install-agy|uninstall-agy` |

## Trạng thái → vị trí

| Trạng thái | Từ sự kiện | Ở đâu |
|---|---|---|
| Đang nghĩ | `UserPromptSubmit`, sau mỗi tool | Đứng yên chỗ đang làm |
| Đọc code | `Read/Grep/Glob`, agy `view_file/grep_search…` | Bàn; từ lần đọc thứ 2 liên tiếp ra thư viện |
| Tra cứu web | `WebFetch/WebSearch`, agy `search_web/read_url…` | Sofa |
| Viết file / Chạy lệnh | `Edit/Write`, `Bash`, agy `write_to_file/run_command` | Bàn, màn hình sáng |
| Giao việc | `Agent/Task` | Bàn họp |
| Cần bạn | `PermissionRequest`, `Notification` | Bàn, giơ tay, bong bóng "!" vàng |
| Xong | `Stop`, agy `PostInvocation/Stop` | Quầy cà phê |
| Rời đi | `SessionEnd`, `SubagentStop`, im lặng 30 phút | Ra cửa |

## Giới hạn đã biết
- Mới chạy thử trên Linux (container). Chưa thử trên Windows của Linh và chưa có `agy` thật để thử; định dạng sự kiện agy lấy từ code Clawd on Desk.
- Văn phòng chỉ xem, chưa duyệt quyền (M7) từ văn phòng.
- Tối đa 8 bàn Claude và 8 bàn agy; đông hơn thì ngồi chung bàn.
