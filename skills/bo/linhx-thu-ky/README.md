# linhx-thu-ky · Thư ký ảo điều phối Claude (LAB026, v0.1.0)

Plugin Claude Code. Mở một trang cục bộ có nhân vật video (bộ clip của Live Character / If Agent, mặc định Emily).
Linh nói hoặc gõ; thư ký kể tình hình dự án, hỏi hoặc giao việc cho Claude Code chạy trong đúng thư mục dự án, rồi tự báo lại khi xong.

```
Trình duyệt (index.html: video Emily + micro + loa)
   │  WebSocket /ws
   ▼
server/server.js  127.0.0.1:4850 ──── Gemini Live (giọng, hiểu câu nói, gọi tool)
   ├─ tools.js     danh_sach_du_an · tinh_hinh_du_an · agent_dang_chay · hoi_claude · giao_viec · ket_qua_viec · dung_viec
   ├─ projects.js  quét D:/LINHX/LAB, D:/LINHX/PRJ: OVERVIEW/README, cuối LOG.md, phiên Claude gần nhất (~/.claude/projects)
   ├─ jobs.js      claude -p (lời nhắn qua stdin) trong thư mục dự án; plan = chỉ đọc, acceptEdits = được sửa file
   └─ đọc văn phòng linhx-office (LAB021, cổng 4848) để biết phiên nào đang chạy
```

## Cài trên máy Windows (Node 22+)

```bash
claude plugin marketplace add "D:/LINHX/LAB/LAB026-NHAN-VAT-DIEU-PHOI/src"
claude plugin install linhx-thu-ky@linhx-lab-026
# mở phiên Claude Code mới rồi gõ:
/thu-ky setup      # dự án ở D:/LINHX/LAB + D:/LINHX/PRJ, nhân vật Emily, khoá Gemini lấy từ .env của Live Character
/thu-ky open       # mở http://127.0.0.1:4850/
```

Không cài cũng chạy được: `node scripts/thu-ky.js setup --linhx` rồi `node scripts/thu-ky.js open`.

Đổi nhân vật: `node scripts/thu-ky.js setup --character "D:/LINHX/PRJ/IFAGENT-LIVE-CHARACTER-DEMO/configs/tran-bao.json"`.
Mọi file nhân vật có `videoMatrix.clips` của Live Character đều dùng được; clip đọc thẳng từ thư mục `public/assets/characters/<id>/videos`, không chép.

## Nói gì với thư ký

| Câu | Thư ký làm |
|---|---|
| "Có những dự án nào?" | `danh_sach_du_an` |
| "LAB25 đang tới đâu rồi?" | `tinh_hinh_du_an`: tóm tắt, nhật ký, câu trả lời cuối của Claude ở thư mục đó |
| "Ai đang làm gì?" | `agent_dang_chay`: văn phòng linhx-office + việc đã giao |
| "Hỏi Claude ở LAB21 xem còn thiếu gì" | `hoi_claude` (chỉ đọc), báo lại khi xong |
| "Bảo LAB25 viết tiếp bài 8, tiếp phiên cũ" | `giao_viec` (`tiep_tuc` = tiếp phiên Claude gần nhất) |
| "Việc số 3 sao rồi?", "Dừng việc 3" | `ket_qua_viec`, `dung_viec` |

Chưa có khoá Gemini thì trang chạy chế độ gõ chữ với các mẫu câu: `dự án`, `tình hình LAB025`, `ai đang làm`, `hỏi LAB025: …`, `giao LAB025: …`, `kết quả 3`, `dừng 3`; giọng đọc là giọng máy của trình duyệt.

## An toàn
- Server chỉ nghe 127.0.0.1, chặn trang web lạ gọi vào; khoá Gemini chỉ ở server.
- Lời nói đi vào `claude -p` qua stdin, không ghép vào dòng lệnh. Mỗi lệnh có tiền tố `[Lệnh từ thư ký ảo LINHX …]` để Claude biết nguồn.
- Mặc định `acceptEdits`: Claude được sửa file trong thư mục dự án, lệnh shell cần quyền sẽ bị từ chối. Thư ký được dặn không giao việc xoá, đăng, gửi ra ngoài.
- Bỏ biến định danh phiên Claude cha khi chạy job, để job không ghi vào transcript của phiên đã bật thư ký.
- Tối đa 3 việc cùng lúc, mỗi việc 30 phút.

## Thử trong lab (container Linux, 13/10)
- Gemini Live giả (`test/fake-gemini.js`) + Claude giả: đủ vòng chào → tình hình LAB021 → giao việc LAB025 → báo cáo; `set_emotion` đổi clip (vẫy tay); micro mở được với thiết bị giả. Không lỗi trang.
- `claude -p` thật ở chế độ hỏi (plan): trả lời đúng nội dung OVERVIEW của LAB021 và báo lại qua thư ký.
- Clip Emily là H.264; Chromium trong container không phát được nên lúc thử đã chuyển sang webm. Chrome trên Windows phát mp4 bình thường.
- Chưa thử: Gemini Live thật (cần khoá), máy Windows, `agy`.

## Nguồn
- `web/vendor/avatar.js`, `clip-plan.js`, `audio.js`, `web/worklets/*`: chép nguyên từ dự án Live Character của Linh (`D:/LINHX/PRJ/IFAGENT-LIVE-CHARACTER-DEMO`, MIT).
- Bài học Gemini Live lấy từ `server/lib/live-proxy.js` và `gemini.js` của dự án đó: trả tool sau ~200 ms, kết quả là chuỗi, nhắc lại khi lượt trả lời rỗng, tên tool không bắt đầu bằng "search".
- Bộ tool đọc + một lệnh, gọi bằng tên dự án: theo LupusDei/adjutant và slopus/happy (xem `../../refs/`).
