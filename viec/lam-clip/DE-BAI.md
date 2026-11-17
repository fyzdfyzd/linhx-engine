# Clip chuyển động Lam qua Google Flow (đêm 17/11)

Nguồn đề: `/mnt/project-files/YEN-LAM/RA-SOAT/CHUYEN-DONG-LAM.md` (bản chép mục cần ở dưới). Claude ra đề và chấm cuối; agy làm trên máy.

## Luật chung (mọi phiếu lam-clip-*)
1. BƯỚC 0 `hostname`, sai máy thì dừng (`SAI_MAY`). Luật trình duyệt, đăng nhập, tab, bí mật: như `viec/kn-thu/DE-BAI.md` mục 3, 4, 6, 7, 8. Không trả phí, không nâng gói.
2. Chrome đang phát YouTube/âm thanh: TẠM DỪNG tab đó (không đóng), rồi mở Flow ở tab mới và giữ tab Flow active suốt phiên. Lần trước hỏng vì việc này.
3. Thư mục làm việc: `<o>\linhx\lam-clip` (o = D: nếu trống > 3 GB, không thì C:). Clone `https://github.com/fyzdfyzd/ifagent` vào `<o>\linhx\lam-clip\ifagent`, nhánh mới `clip-lam-t147` từ `origin/lam-gap-17-11` (đã có thì `git pull`). KHÔNG đụng nhánh khác, KHÔNG deploy.
4. Tìm trong repo: `cho.webm` của bộ t146 (`git ls-files | findstr /i "t146"`), `lam-cho-720.mp4`, `YENLAM_REF_OFFICIAL/image/portrait.webp`, script tách nền đã dùng cho t146 (nếu có thì dùng lại). TUYỆT ĐỐI không dùng bộ `assets/ylk/` (người khác).
5. Ảnh đầu-cuối (làm 1 lần, lưu `lam-clip\khung\`):
   - Kiosk: khung CUỐI của `cho.webm` (giải bằng `-c:v libvpx-vp9`), đặt lên nền xanh lá trơn `#00B140`, PNG 1080×1920 → `khung-kiosk.png`.
   - Điện thoại: khung đầu `lam-cho-720.mp4` → `khung-dt.png` (giữ nền KV).
6. Flow: dự án mới "Lam t147". Chế độ Frames to Video, khung dọc 9:16, Veo 3.1 **Fast**. Ảnh đầu = ảnh cuối = khung ở mục 5, thêm `portrait.webp` làm ảnh tham chiếu nếu Flow cho. Mỗi clip tối đa **2 lượt** sinh; lượt nào đẹp hơn thì lấy. Tải bản gốc mp4 về `lam-clip\goc\<ma>-l<1|2>.mp4`.
7. Đề tiếng Anh = CÂU CHUNG + đề riêng (bảng dưới). Điện thoại: thay "Plain chroma green background" bằng "Same background as start frame", và "full-body-to-knee" bằng "half-body".
8. Hậu kỳ kiosk: cắt còn 5–6 giây, scale 1080×1920, tách nền xanh (script t146, hoặc ffmpeg `chromakey=0x00B140:0.13:0.06,despill=type=green`), ra `t147/<ma>.webm` (VP9, `-pix_fmt yuva420p`, `-auto-alt-ref 0`) + `t147/<ma>.mp4` dự phòng (nền trong suốt thay bằng nền KV hoặc đen). Đặt `t147/` cạnh thư mục chứa `cho.webm`. Điện thoại: `t147/<ma>.mp4` đúng khổ `lam-cho-720.mp4`.
9. Chấm máy BẮT BUỘC mỗi clip: `python viec\lam-clip\cham.py kiosk t147\<ma>.webm <duong\cho.webm> <xong\id>` (điện thoại: `dt ... lam-cho-720.mp4`). Trượt SSIM thì thử: cắt bớt đầu/cuối, hoặc lượt 2. Vẫn trượt thì giữ, ghi lỗi, không sửa ngưỡng.
10. Tự soi (agy) ảnh `<ma>-tam.jpg`: mặt có đổi người không, ngón tay (đếm 3-2-1 đúng 3→2→1), ghim cài áo đỏ, vest xanh, tóc dài, viền xanh lá sót. Ghi 1 dòng mỗi clip.
11. Commit + push nhánh `clip-lam-t147` SAU MỖI CLIP (hết giờ không mất việc). Chép `<ma>-tam.jpg` + `<ma>-cham.json` vào `hang-doi/xong/<id>/` (ảnh ≤ 1 MB).
12. KET-QUA ≤ 2000 ký tự: dòng `KET_LUAN: DAT | MOT_PHAN | HONG | CHUA_DANG_NHAP`, rồi mỗi clip 1 dòng `<ma> | lượt | ssim_dau/ssim_cuoi | tự soi | sha256 webm 12 ký tự`, SHA nhánh, credit đã dùng (đọc trên Flow), `phut_that`, `loi_gap`.

## Câu chung (đặt đầu mọi đề)
Same woman as reference, identical face, long dark wavy hair, royal blue blazer with small red pin, cream top. Vertical 9:16 full-body-to-knee framing identical to start frame. Plain chroma green background, soft studio light. Starts and ends in the exact start-frame pose (hands clasped at waist, looking at camera). 6 seconds, no text, no extra objects. Mouth closed with a gentle smile (no talking).

## Đề riêng
| Mã | Đề riêng |
|---|---|
| m-moi-chup | She smiles, raises right hand palm-up toward the camera in an inviting "let's take a photo" gesture, slight lean forward, returns to pose. |
| m-dem-321 | She holds up right hand and counts down clearly with fingers: three, two, one (correct finger counts, slow), then a small happy nod, returns to pose. |
| m-lai-gan | She tilts head gently, beckons with one hand "come a little closer", warm smile, returns to pose. |
| m-gat-dau | Two slow friendly nods while listening, returns to pose. |
| m-suy-nghi | Finger lightly touches chin, eyes up-left thinking, then smiles, returns to pose. |
| m-bat-ngo | Delighted surprise: eyebrows up, hands come together in a soft clap near chest, big smile, returns to pose. |
| m-chi-qr | Points down-right toward the bottom of the screen with open hand, glances there then back at camera, returns to pose. |
| m-chi-trai | Gestures with open left hand toward screen left as if presenting a card, returns to pose. |
| m-chi-phai | Gestures with open right hand toward screen right as if presenting a card, returns to pose. |
| m-xin-loi | Apologetic soft smile, right hand on chest, small bow of head, returns to pose. |
| m-vay-chao | Waves hello with right hand, friendly, returns to pose. |
| p-vay | Waves hello with right hand, friendly, returns to pose. |
| p-nghe | Listens attentively, slight head tilt, small nod, returns to pose. |
| p-suy-nghi | Finger lightly touches chin, eyes up-left thinking, then smiles, returns to pose. |
| p-vui | Happy delighted smile, small soft clap near chest, returns to pose. |
