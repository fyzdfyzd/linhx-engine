may: may-1
loai: khac
tran_phut: 30
nhan: may-1 2026-11-21T22:12:14+0700

Kiểm kê máy 1 (DESKTOP-PVHR2CD) làm nhà cho server Zalo, crawler và kho dữ liệu.
1. D:\linhx và D:\LINHX_CRAWLER: dung lượng thư mục cấp 1 (bỏ .venv/node_modules/.git) → kiem-ke-may1.csv.
2. Server đang chạy: cổng đang nghe (Get-NetTCPConnection -State Listen) kèm tên tiến trình; Task Scheduler có tên chứa LINHX, LAB, Zalo, Crawler, CTS: trạng thái, lần chạy cuối, kết quả cuối.
3. Zalo: bao nhiêu bộ nghe Zalo đang chạy (zalo-mcp listen, tra-loi-nhom, zalo-ifagent-bot 8188, bang_tho.py). Cần đúng 1 bộ nghe.
4. RAM trống, ổ C trống, Tailscale có chạy và tên máy trong Tailscale.
KET-QUA: bảng server (tên, cổng, sống/chết), lịch lỗi, đề xuất tắt gì để đỡ RAM.
Luật chung: CHỈ ĐỌC. Không xoá, không sửa, không cài, không deploy, không gửi tin/email/Zalo, không trả tiền, không in bí mật (.env, token, cookie) vào kết quả. Kết quả chính ghi KET-QUA.md ≤ 2000 ký tự, tiếng Việt, gạch đầu dòng; bảng dài ghi file CSV/MD cạnh KET-QUA và chỉ tóm tắt.
