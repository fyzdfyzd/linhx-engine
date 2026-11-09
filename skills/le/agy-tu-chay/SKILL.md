---
name: agy-tu-chay
description: Cho Antigravity (agy) tự lập kế hoạch và tự chạy trọn một việc theo phiếu, tự kiểm, tự chấm chéo bằng phiên mới, ghi báo cáo một trang cho Claude và Linh. Dùng khi Linh hoặc Claude giao một việc lớn (chiến lược, báo cáo, slide...) để chạy trên máy công ty mà không tốn token Claude.
metadata:
  version: "0.1.0"
---

# agy-tu-chay

Bộ này chạy hoàn toàn trên agy. Claude chỉ ra lệnh lúc đầu và đọc `BAO-CAO-QUAN-TRI.md` theo lịch (skill `quan-tri-agy`). Luật chất lượng theo `linhx-chuan`, cách làm từng loại theo workflow tương ứng (ví dụ `chien-luoc`).

## Vai

| Vai | Ai | Làm gì |
|---|---|---|
| Người ra lệnh | Linh | Nói việc cho Claude; duyệt cổng D2 (chọn đúng vấn đề) và D4 (bản cuối) |
| Quản trị | Claude | Viết `LENH.md`, chọn loại, khởi tạo kế hoạch; đọc báo cáo định kỳ; mở cổng hoặc báo Linh |
| Lập kế hoạch | agy | Viết hoặc chỉnh `ke-hoach.json`, chạy `kiem` tới khi DAT |
| Thợ | agy | Làm một phiếu, phiên riêng |
| Người chấm | agy phiên MỚI, hoặc agy model khác (vai "gemini") | Chấm theo `linhx-chuan/cham.md`, không sửa bài |
| Máy kiểm | `kiem.py`, `ke_hoach.py` | Chặn trước khi tới người chấm |

## Lập kế hoạch (agy làm)

1. Đọc `LENH.md` (Claude viết: việc, loại, người xem, hạn, ràng buộc).
2. Có mẫu cho loại đó thì: `python scripts/ke_hoach.py moi <thu-muc> --loai <loai> --ten "<tên>"`. Hiện có mẫu `chien-luoc` (12 phiếu).
3. Chỉnh kế hoạch theo LENH: thêm, bớt, chia nhỏ phiếu. Chưa có mẫu thì tự viết `ke-hoach.json` theo khuôn dưới, đi theo 4 pha: tham chiếu và nghiên cứu → định nghĩa → phương án → giao và duyệt như khán giả.
4. `python scripts/ke_hoach.py kiem <thu-muc>` phải ra DAT. Máy chặn: thiếu trường, phiếu quá 40 phút, người chấm trùng thợ, giao Claude làm thợ, tiêu chí không đo được (phải có số, tên file, hoặc lệnh kiểm), phụ thuộc thiếu hoặc vòng lặp.

Khuôn một phiếu:
```json
{"ma": "P05", "viec": "...", "doc": ["chien-luoc/references/..."], "dau_ra": ["NC1_*.md"],
 "tieu_chi": ["3 file NC", "STATUS nhắc cả 3 file"],
 "lenh_kiem": "python {SKILLS}/linhx-chuan/scripts/kiem.py . --pha cuoi",
 "tho": "agy", "nguoi_cham": "agy-moi | gemini | linh", "tran_phut": 40,
 "phu_thuoc": ["P03"], "can_cong": "D2", "chi_va": false}
```
`can_cong` chặn phiếu tới khi cổng được mở. `chi_va: true` nghĩa là chỉ được vá mục nêu trong phiếu, không ghi lại cả file.

## Chạy

Trên máy công ty: `powershell -File scripts/chay-vong.ps1 -Viec <thu-muc>` (một lượt), hoặc `scripts/dang-ky-lich.ps1 -Viec <thu-muc>` (mỗi 20 phút). Mỗi lượt:
Mọi lệnh agy theo lịch chạy **ngầm hoàn toàn** qua `wscript chay-an.vbs` (Linh 2/11: console bật lên làm khó thao tác máy công ty). Chạy tay khi cần ngầm: `wscript //B chay-an.vbs chay-vong.ps1 -Viec <thu-muc>`. Mỗi thư mục việc một tên lịch riêng: `-Ten LINHX-<viec>`.

```
tiep → agy THỢ làm phiếu (.vong/PHIEU.md)
     → máy kiểm (lenh_kiem) ── trượt → ghi trượt, vòng +1
     → agy NGƯỜI CHẤM phiên mới (.vong/CHAM.md) → cham/<ma>.json
     → đạt: xong · trượt: ghi ≤3 lỗi, vòng +1 · 3 vòng: dừng, báo người quyết
     → bao-cao → BAO-CAO-QUAN-TRI.md
```

Chạy tay từng bước (khi không có PowerShell): `tiep`, làm phiếu, chạy lệnh kiểm, mở phiên mới chấm, rồi `xong <ma> --dat` hoặc `xong <ma> --truot "lý do"`.

## Luật cho agy

- Một phiếu một phiên. Không làm phiếu khác, không tự chấm mình.
- Thợ không được chấm, người chấm không được sửa bài.
- Không ghi đè file có sẵn nếu phiếu không nói. Vá thì chỉ vá đúng mục.
- Đọc đúng file trong `doc` của phiếu, không đoán tên file.
- Việc cần trình duyệt (Gemini Deep Research, Behance, ChatGPT) chạy trên Chrome máy công ty.
- Ý tưởng ngoài phạm vi: ghi một dòng vào `Y-TUONG.md`, không tự làm.
- Cổng D2, D4 không bao giờ tự mở. Chỉ `duyet` khi Linh (hoặc Claude ở chế độ `claude-quan-tri`) đã nói.

## Chế độ

- `claude-quan-tri` (mặc định): Claude đọc báo cáo, xem nhanh trước rồi chuyển Linh ở cổng.
- `agy-doc-lap`: khi Claude sắp hết quota hoặc vắng. Cổng đi thẳng tới Linh; mọi thứ khác chạy như cũ. Đổi bằng cách sửa `che_do` trong `ke-hoach.json`.
