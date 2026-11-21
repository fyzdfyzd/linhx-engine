may: may-1
loai: code
model: gemini-4-neon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\zalo-bang-tho
vung: **
nhan: may-1 2026-11-21T11:05:05+0700

## Mục tiêu
Nhóm Zalo "LINHX Thợ" (Linh vừa tạo, có nick Nụ) nói chuyện được với hàng đợi máy agy, KHÔNG gọi Claude/LLM:
1. Gõ `tt` → trả 1 tin ≤ 12 dòng: mỗi máy (may-1..4) RAM trống + giờ hồ sơ cuối; số phiếu moi/dang/can-linh; 3 phiếu xong gần nhất (mã + trạng thái).
2. Gõ `kẹt` (hoặc `ket`) → phiếu trong dang/ không có dòng `nhip:` 15 phút gần nhất.
3. Gõ `cần linh` (hoặc `can linh`) → danh sách can-linh/*.md: máy + 1 dòng việc.
4. Tự báo (mỗi 2 phút kiểm, gom 1 tin): phiếu mới vào xong/ (mã, trạng thái, phút) và phiếu mới vào can-linh/.
Dữ liệu đọc từ clone hàng đợi `D:\linhx\hang-doi` sau `git pull` (chỉ đọc, không commit vào đó).

## Chuẩn bị
Tìm bộ nghe Zalo đang có trên máy này (nick Nụ, zalo-mcp / zalo-agent-cli, LAB116-ZALO-HUB, LAB083, `runner/quet_cong_cu_may.py --loai zalo` giúp dò). Dùng lại cách nó nhận và gửi tin nhóm, không dựng bộ nghe thứ hai trùng nick. Lấy id nhóm "LINHX Thợ" từ danh sách nhóm của Nụ.

## File được sửa
Chỉ trong `D:\linhx\zalo-bang-tho\` (git init cục bộ): `bang_tho.py` (Python chuẩn + gọi CLI gửi tin sẵn có), `test_bang_tho.py`, `chay-an.vbs` (chạy ẩn), `README.md` (cách bật/tắt). Nếu bộ nghe sẵn có cần một móc nhỏ để chuyển tin nhóm này sang `bang_tho.py`: được sửa đúng chỗ đó, ghi rõ file:dòng trong KET-QUA, giữ bản sao `.bak`.
Đăng ký lịch Windows ẩn `LINHX-ZaloBangTho` (wscript chay-an.vbs), không mở cửa sổ console.

## Cấm động
- CHỈ gửi tin vào nhóm "LINHX Thợ". Tuyệt đối không gửi tin tới nhóm/người khác, không đổi trả lời của các nhóm khác.
- Chỉ trả lời tin của chủ nhóm (nick chính của Linh); người khác bỏ qua.
- Không in, không commit cookie/token/phiên Zalo. Không đăng xuất, không đăng nhập lại Nụ. Cần quét QR hoặc đăng nhập: DỪNG, trả `CAN-LINH: ...; LENH: ...`.
- Không sửa `D:\linhx\hang-doi`. Không chạy nền khi làm phiếu (chỉ lịch Windows ở bước cuối).

## Test bằng chứng
1. `python -m pytest D:\linhx\zalo-bang-tho -q` đạt (test bằng thư mục hàng đợi giả: tt, kẹt, cần linh, tự báo không báo trùng).
2. Gửi đúng 1 tin thử vào nhóm "LINHX Thợ": kết quả lệnh `tt` thật, mở đầu "Bảng thợ đã nối".
3. KET-QUA ≤ 15 dòng: bộ nghe dùng lại là gì, id nhóm (4 số cuối), file đã đổi, lệnh bật/tắt, đầu ra pytest, giờ gửi tin thử.
