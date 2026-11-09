# WF12 · Bổ sung vòng 2 (cloud, 9/11/2026)

Bổ sung cho `NGHIEN-CUU.md`, không sửa file đó. Nhìn chung `NGHIEN-CUU.md` đúng; phần dưới chỉ lấp những chỗ còn mỏng. Máy MSI ghi tiếp thì thêm mục mới ở cuối file.

## Kết luận thêm
1. **Đã thử máy đo trên một phim thật** (bài 1 HyperFrames 18,6 giây của LAB042). `kiem_video.py` chạy đúng. `kiem_khung.mjs` báo sai: với trang HyperFrames, nó đếm cả chữ đang ẩn và chữ đang bay vào, nên ra 12 lỗi tràn khung và 5 cảnh báo chữ đè nhau, trong khi phim render không có lỗi nào như vậy. Phải sửa lỗi này trước vòng 1.
2. **Máy đo tự động để lọt một phim kiểu slide.** Phim thử có nền xanh than chuyển màu, chữ nhỏ trôi giữa khung, nhãn ngăn bằng dấu chấm giữa, nhãn ở góc. Mọi thứ này đều nằm trong danh sách CẤM của HyperFrames, nhưng máy chỉ bắt được "đứng hình" và "sai độ dài". Vì vậy cần thêm chấm "độ giống slide" từ bảng cảnh và chấm mù P0/P1/P2.
3. **Phụ đề tiếng Việt đã có chuẩn ngành của Netflix**: 42 ký tự mỗi dòng, tối đa 17 ký tự mỗi giây, mỗi câu hiện từ 5/6 giây đến 7 giây, tối đa hai dòng, dòng trên ngắn hơn dòng dưới. Đây là ngưỡng có nguồn gốc rõ, nên dùng nó cho phụ đề thay cho con số tự đặt. Hiện chưa script nào trong skill kiểm phụ đề theo các ngưỡng này.
4. **Số liệu về "móc 3 giây" có nguồn chính chủ**: TikTok khuyên "Introduce your content proposition in the first 3 seconds" và đặt móc trong 6 giây đầu, nhưng không đưa số đo nào. Nên dùng làm luật, không dùng làm ngưỡng chấm.
5. **Vùng an toàn dọc chưa có số chính chủ.** TikTok chỉ ghi "within the UI safe zone as per ad specifications". Số của Meta mới thấy qua bên thứ ba: trên 14%, dưới 20–35%, hai bên 6%. Con số của HyperFrames (168–1330 px) chặt hơn ở phía dưới. Tạm dùng số HyperFrames rồi kiểm lại trên điện thoại thật.

## Người làm nghề làm thế nào (chỗ còn thiếu)
| Đơn vị | Quy trình | Duyệt | Số có nguồn |
|---|---|---|---|
| Kurzgesagt (studio giải thích, ngang) | nghiên cứu → kịch bản → phác hình ẩn dụ từng cảnh → minh hoạ → lồng giọng → dựng chuyển động → nhạc riêng | chuyên gia kiểm sự thật kịch bản; có bảng nguồn công khai cho mỗi phim; vài ngày cả nhóm ngồi xem lại một lần | "about a dozen drafts" cho kịch bản; "on average 200 panels"; 2–3 người vẽ trong 8–12 tuần, 2–3 người dựng chuyển động trong 8–10 tuần; "at least 1200 hours" mỗi phim (video năm 2020) |
| Netflix (phụ đề, mọi phim giao cho họ) | bản hướng dẫn riêng cho tiếng Việt cộng phần yêu cầu chung | chấm bằng số: ký tự mỗi dòng, ký tự mỗi giây, thời lượng hiện, cách ngắt dòng | xem kết luận 3; bản tiếng Việt sửa lần cuối ngày 19/12/2025 |
| TikTok (quảng cáo hiệu năng) | dọc 9:16, độ phân giải từ 720p, có nhạc, có phụ đề hoặc chữ chồng, có chuyển cảnh và hình dán | thử 3–5 bản sáng tạo cho mỗi nhóm quảng cáo | "5-10 words per second when using text" (số này mâu thuẫn với HyperFrames, xem dưới); trang cập nhật 6/2025 |

Lấy cho WF12:
- **Kịch bản là nút cổ chai, và là chỗ duy nhất có chuyên gia duyệt** (Kurzgesagt: "Writing is the bottleneck"). Vì vậy D2 của Linh nên đặt ở bước chọn cốt truyện và lời, không đặt ở bước xem hình.
- **Giọng là đồng hồ của hình** (Kurzgesagt: "His voiceover provides the timing for the animation team"). Khớp với `phim-code` bước 4 hiện có. Giữ nguyên.
- **Bảng nguồn cho mỗi phim**: khớp với `NGUON.md` mà `loai-video.md` đã yêu cầu. Nên chuyển yêu cầu này thành điều kiện bắt buộc trước D4.

Mâu thuẫn về tốc độ chữ cần chọn một: TikTok khuyên 5–10 chữ mỗi giây cho chữ chồng (nhưng không có số đo kèm). HyperFrames dùng 0,5 giây cộng 0,3 giây mỗi chữ, tức khoảng 2,7 chữ mỗi giây với câu 8 chữ. Netflix dùng 17 ký tự mỗi giây, tức khoảng 3–4 chữ tiếng Việt mỗi giây. **Đề xuất**: phụ đề theo Netflix, chữ tiêu đề theo HyperFrames, bỏ con số của TikTok.

## Thử máy đo trên mẫu có sẵn
Mẫu: `/mnt/project-files/LAB042-AGENT-DUNG-VIDEO/demo/hyperframes/bai1-hyperframes.mp4` (1920×1080, 18,6 giây, có tiếng). Đồng thời chạy trên 3 bản thử 3–4 giây của LAB059.

| Phép đo | Kết quả | Mắt nhìn có đồng ý? |
|---|---|---|
| `kiem_video.py --kho 16:9 --giay 30-45` | LỖI: dài 18,6 giây; CẢNH BÁO: đứng hình từ 1,0, 9,7 và 14,2 giây; −17,9 LUFS, đỉnh −1,4 dBTP | Đồng ý. Phim đúng là đứng ở mỗi "slide". Theo ngưỡng skill hiện tại (−18…−12) thì độ to **qua**, theo ngưỡng mới đề xuất (−16…−14) thì **trượt**: đổi ngưỡng có tác dụng thật |
| `kiem_khung.mjs --dur 18.6` | 12 LỖI tràn khung, 5 CẢNH BÁO chữ đè, 2 đứng hình, thiếu `v2.wav` | **Không đồng ý**: các lỗi tràn và đè là báo sai. 7 lỗi đo ở giây 0, khi phụ đề và chữ của cảnh 2–3 còn đang ẩn. 5 lỗi đo đúng lúc chữ mới bay vào (`h0` ở 0,5 giây, `h1` ở 7,5 giây…). Cần bỏ qua phần tử có `opacity` 0, `visibility:hidden`, hoặc `.clip` nằm ngoài khoảng `data-start`, và chỉ đo khi chữ đã đứng yên |
| `kiem_khung.mjs` khi thiếu `window.DUR` | dừng lại và báo "không biết độ dài" | Nên đọc `data-duration` của gốc HyperFrames thay vì bắt khai `--dur` |
| `kiem_khung.mjs` khi thiếu `gsap.min.js` | ra 12 lỗi tràn dây chuyền sau lỗi tải | Khi tài nguyên tải hỏng, nên dừng và chỉ báo lỗi tải đó |
| 3 bản thử LAB059 | 0 LỖI; cảnh báo cạnh ngắn dưới 1080 px, không tiếng, khung đầu trơn (2/3 bản) | Đồng ý |
| Mắt, contact sheet 1 khung/giây | nền xanh than chuyển màu, chữ nhỏ giữa khung, nhãn có dấu chấm giữa, nhãn ở góc, phụ đề nhỏ | **Máy không bắt được**: đây chính là "phim slide" mà danh sách CẤM của HyperFrames nhắm tới |

Ngưỡng cho máy đo WF12, chỗ khác với `NGHIEN-CUU.md`:
- **Phụ đề (mới, chưa có script)**: mỗi câu ≤ 42 ký tự mỗi dòng và ≤ 2 dòng; ≤ 17 ký tự mỗi giây; hiện từ 0,83 đến 7 giây. Đây là phép đo rẻ nhất, chỉ cần đọc file `.srt`. Nên viết thêm `kiem_phu_de.py` hoặc thêm vào `kiem_video.py --srt`.
- **Số trong phụ đề và chữ trên hình**: theo quy ước Netflix tiếng Việt, từ 1 đến 10 viết bằng chữ, thập phân dùng dấu phẩy (2,5), hàng nghìn dùng dấu chấm (1.000), dấu ba chấm là một ký tự (…). Có thể kiểm bằng regex.
- **Sửa `kiem_khung.mjs` trước vòng 1** (3 lỗi ở bảng trên). Nếu không sửa, agy sẽ chạy máy đo, gặp báo sai rồi học cách bỏ qua nó.

## Sửa vào skill (thêm vào danh sách của `NGHIEN-CUU.md`)
7. `scripts/kiem_khung.mjs`: bỏ qua phần tử đang ẩn hoặc `.clip` ngoài khoảng thời gian của nó; đọc `data-duration`; dừng khi tài nguyên tải hỏng.
8. `scripts/kiem_video.py --srt`: thêm kiểm 42 ký tự, 17 ký tự mỗi giây, 0,83–7 giây, 2 dòng (Netflix tiếng Việt).
9. `references/giong-viet.md`: thêm quy ước số, thập phân, dấu ba chấm, dấu ngoặc kép theo Netflix tiếng Việt. Thêm cảnh báo: whisper mặc định `small.en` sẽ **dịch** lời nói sang tiếng Anh, phải truyền `--model small --language vi` (HyperFrames `captions.md`).
10. `references/loai-video.md` mục 1 và 2: bắt buộc có `NGUON.md` trước D4 (theo bảng nguồn công khai của Kurzgesagt).
11. Nguồn chưa có trong `NGOAI.md`: **browser-use/video-use** (MIT, đã đọc `SKILL.md`). Có 12 luật cứng khi cắt cảnh quay: phụ đề áp vào cuối cùng; cắt từng đoạn rồi nối `-c copy`; fade 30 ms ở mỗi mép; không cắt giữa chữ; đệm mép 30–200 ms; tự kiểm ±1,5 giây quanh mỗi điểm cắt; tối đa 3 vòng tự kiểm. Nên đưa vào `record.md` (nhánh B), vì phần này chưa có ở đó.

## Rủi ro thêm
- Ngưỡng 17 ký tự mỗi giây của Netflix là cho phim dài, người xem ngồi đọc. Reel lướt nhanh có thể cần chặt hơn. Chưa có số đo riêng cho reel.
- Máy đo hiện chưa đo được "trông như slide". Nếu chỉ dựa vào máy, phim slide vẫn qua. Phải có bước chấm mù.
- Số giờ làm của Kurzgesagt lấy từ video năm 2020, phụ đề tự sinh nên có lỗi chữ. Chỉ dùng làm mốc độ lớn.

## Nguồn
- [đọc] Netflix, Vietnamese Timed Text Style Guide: https://partnerhelp.netflixstudios.com/hc/en-us/articles/220447048-Vietnamese-Timed-Text-Style-Guide
- [đọc] Netflix, Timed Text Style Guide, General Requirements: https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617
- [đọc] Kurzgesagt, Our video process: https://kurzgesagt.org/youtube/
- [đọc] bản chép lời "How to Make a Kurzgesagt Video in 1200 Hours" (2020): https://rosetta.to/u/kurzgesagt/how-to-make-a-kurzgesagt-video-in-1200-hours
- [đọc] TikTok, Creative best practices for performance ads: https://ads.tiktok.com/help/article/creative-best-practices?lang=en
- [đọc, bên thứ ba] Billo, Meta Ads Safe Zones 2026: https://billo.app/blog/meta-ads-safe-zones (trang chính chủ của Meta chưa đọc: https://www.facebook.com/business/ads-guide/update/video/facebook-facebook-reels)
- [đọc] browser-use/video-use `SKILL.md`: https://github.com/browser-use/video-use
- [đọc] HyperFrames `sound.md`, `captions.md`, `media-use/SKILL.md`, `reverse-any-video/SKILL.md` (commit 7bf6599): https://github.com/heygen-com/hyperframes
