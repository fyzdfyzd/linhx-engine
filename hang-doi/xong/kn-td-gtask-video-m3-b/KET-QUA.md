model: gemini-4-hydrogen-high
phieu: kn-td-gtask-video-m3-b
may: may-3
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 1.54
token: vao=39596 ra=5296

# kn-td-gtask-video-m3-b — DESKTOP-2AUT482 (may-3)
KET_LUAN: HONG — browsentic: No MCP servers configured (agy mcp list); port 8765 connect failed

trinh_duyet: (chưa có MCP browsentic)
Tab: đã đóng 0/0
thoi_luong: 0 giây (chưa tạo được video do thiếu MCP Browsentic)
co_tieng: không
phut_that: 1
loi_gap: `agy mcp list` trả `No MCP servers configured.`; không có tool `browsentic_status`; `Test-NetConnection 127.0.0.1 -Port 8765` trả `WARNING: TCP connect to (127.0.0.1 : 8765) failed`

## Chi tiết kiểm tra
- Bước 0 `hostname`: `DESKTOP-2AUT482` (khớp `may-3` trong [kn-td-gtask-video-m3-b.md](file:///D:/linhx/.hang-doi-hang-doi/hang-doi/dang/kn-td-gtask-video-m3-b.md)).
- Luật 3 tại [DE-BAI.md](file:///D:/linhx/.hang-doi-hang-doi/viec/kn-thu/DE-BAI.md) bắt buộc việc cần đăng nhập CHỈ dùng MCP Browsentic, kiểm tra `browsentic_status` trước; hỏng thì dừng, không lùi sang `chrome-agy`.
- `agy mcp list` trả `No MCP servers configured.` ([mcp_config.json](file:///C:/Users/Admin/.gemini/config/mcp_config.json) và [mcp_config.json](file:///C:/Users/Admin/.gemini/antigravity/mcp_config.json) đều 0 byte).
- Cổng `127.0.0.1:8765` chưa mở (`TcpTestSucceeded : False`); không có lệnh `browsentic` trong PATH hay `npm list -g --depth=0`.
- Chrome `Profile 16` có thư mục extension `npmocgldfflonjjmdadmdefpnfagnjmp\0.9.2_0`, nhưng cầu nối MCP Browsentic chưa chạy và chưa cấu hình trong `agy`.

CAN-LINH: Bật cầu nối Browsentic cổng 8765 và cấu hình MCP Browsentic cho `agy` trên máy 3 (`DESKTOP-2AUT482`) rồi chạy lại phiếu; LENH: agy mcp add --transport http browsentic http://127.0.0.1:8765/mcp && agy mcp list
