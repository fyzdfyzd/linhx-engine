---
type: nghien-cuu
status: xong-nen
created: 2026-11-09
updated: 2026-11-09
---
# WF19 · Nghiên cứu nền: bản tin tuần + freebie qua Zalo

Làm 9/11, 11:20–12:30 giờ VN, máy MSI. Code ngoài chép ở `D:\LINHX\WF-NC\_refs\WF19\` (chỉ đọc, không chạy). Bảng đọc gì, lấy gì: `NGOAI.md`.

## Kết luận 5 dòng
1. Phần bản tin đã có người làm tốt, không nghĩ lại: lấy khung 6 pha của AIGC Weekly (gom → chọn có chấm điểm → soạn → soát PASS/FAIL tối đa 3 vòng → đăng), chạy đều hằng tuần bằng agent.
2. Chống bịa phải là cổng máy, không phải lời dặn: mỗi tin có link nguồn gốc mở được, ngày trong tuần, mỗi con số khớp nguyên văn nguồn. Dùng lại `soat-su-that` của LINHX, thêm điểm "rác" (slopiness) của glebis.
3. Giá trị chính là freebie, không phải tin. Trang h03 đã ghi: học viên "cần mỗi tuần một việc làm thử được ngay cho nghề mình". Ngoài kia chưa thấy ai có cổng thử freebie, LINHX phải tự dựng: trợ giảng thử bằng việc thật, có bấm giờ.
4. Zalo là ràng buộc cứng: theo eSMS (bên thứ ba), người quan tâm chỉ nhận tối đa 4 tin broadcast mỗi tháng từ một OA đã xác thực. Một bản tin mỗi tuần là chạm trần, không còn chỗ cho tin nhắc. Cần kiểm lại ở tài liệu chính thức (đề DR-1).
5. Ngưỡng mở 40% chưa đo được nếu Zalo không có số lượt mở broadcast. Đo bằng lượt mở Mini App và lượt bấm freebie theo mã QR từng lớp. Mốc tham khảo: email trung bình năm 2025 là 43,46% (MailerLite), con số này còn bị Apple làm cao lên.

## Quy trình đề xuất (một tuần)
| Bước | Việc | Ai | Đầu ra (có tệp là xong bước) |
|---|---|---|---|
| 0 | Tham số tuần: mã tuần, từ ngày, đến ngày, số trước | script | `tuan.yaml` |
| 1 | Quét tin trong khung tuần; gom cụm theo `cafebiz-radar` lượt 1 | Máy quét | `items.jsonl`, `clusters.json` |
| 2 | Chọn: chấm 3 trục cho học viên corp (liên quan nghề 40, độ lớn 30, làm thử được 30), lấy ≥70 điểm, tối đa 5 tin; bỏ trùng với các số đã gửi | agy | `chon.yaml` (có điểm từng trục, lý do) |
| 3 | Kiểm nguồn: mở từng link gốc, chép trích nguyên văn cho mỗi con số, ghi điểm rác 0–10 | Claude (subagent mới) | `nguon.yaml` |
| 4 | Soạn tin: mỗi tin 3 tầng theo The Rundown: Chuyện gì · Chi tiết · Vì sao quan trọng với việc của bạn. Bản dài vào Mini App, bản rút ≤2.000 ký tự gửi OA | agy | `ban-tin.md`, `zalo.txt` |
| 5 | Freebie: chọn đề từ câu hỏi học viên (`cau-hoi-thanh-noi-dung`), cắt từ khoá Course OS, có ví dụ đầu vào/đầu ra | agy | `freebie/` |
| 6 | Thử freebie: 2 trợ giảng làm một việc thật, bấm giờ, ghi đạt/không | trợ giảng | `thu-freebie.md` |
| 7 | Soát: máy đo M1–M4 rồi `soat-su-that`; FAIL thì trả agy sửa, tối đa 3 vòng | Claude | `soat.md` (PASS/FAIL) |
| 8 | Duyệt: Linh đọc một trang tóm và bản dựng | Linh ≤30 phút | dấu duyệt |
| 9 | Gửi + đo: link có mã theo lớp; tuần sau đọc số mở Mini App, bấm freebie | agy | `do-tuan.csv` |
| 10 | Sổ đính chính: tin sai thì đính chính ở số sau, ghi lỗi vào `BAI-HOC.md` | Claude | `dinh-chinh.md` |

Bước nào có tệp đầu ra rồi thì bỏ qua khi chạy lại (cách "sản phẩm là trạng thái" của AIGC Weekly).

## Máy đo + ngưỡng
| Mã | Đo gì | Cách đo (máy chạy được) | Ngưỡng qua |
|---|---|---|---|
| M1 | Nguồn sống, đúng tuần | script: mỗi tin có URL, trả HTTP 200, ngày nguồn trong khung `tuan.yaml` | 100% tin |
| M2 | Số khớp nguồn | script: lấy mọi con số trong `ban-tin.md`, tìm trong văn bản nguồn đã tải ở `nguon.yaml` | 0 số lệch |
| M3 | Sự thật từng câu | `soat-su-that` chạy subagent mới | 0 lỗi NG, BI |
| M4 | Khuôn | script: 3–5 tin; `zalo.txt` ≤2.000 ký tự; không nhãn [1] [2], không link giả, không URL trùng số trước (lấy từ checklist techPulse) | đạt hết |
| M5 | Rác nguồn | điểm rác 0–10 theo cờ đỏ/xanh của glebis | không tin nào >6 |
| M6 | Freebie dùng ngay | 2 trợ giảng thử với việc thật của họ | 2/2 đạt, mỗi người ≤15 phút |
| M7 | Chấm mù | 3 persona học viên (ngân hàng, BĐS, văn phòng) so cặp bản tin LINHX với bản vàng đã Việt hoá khuôn, không biết bản nào của ai | ≥2/3 chọn LINHX hoặc hoà |
| M8 | Vận hành | ghi giờ Linh; số mở Mini App / số người nhận; số bấm freebie / số người nhận | Linh ≤30 phút; mở ≥40% sau 4 tuần; bấm freebie ≥30% (ngưỡng h03) |

Ngưỡng M6 15 phút và M7 là đề xuất của Claude, chờ vòng 1 chỉnh.

## Bản vàng
Chi tiết ở `vang/README.md`. Tóm: (1) The Rundown AI số 6/11/2026: khuôn tin 3 tầng. (2) AIGC Weekly Y26W44 (7/11/2026): bản tin tuần do agent làm, 3 mục, link neo trong chữ. (3) TLDR AI: tóm vài câu, người viết. (4) Nhịp AI (Đào Trung Thành), tiếng Việt: mới thấy, chưa đọc số nào. Chưa có bản vàng cho freebie; DR-1 đi tìm.

## Sửa vào skill nào, sửa gì
- `cafebiz-radar` (le/): dùng lượt 1 (gom cụm). Thiếu hồ sơ độc giả "học viên corp cũ" và trục "làm thử được"; hiện góc là tiền, doanh nghiệp cho CafeBiz. Thêm tham số độc giả, không viết skill mới.
- `content-synthesizer`: **không dùng cho bản tin**. Skill bắt "Viết 2-3 Personal Anecdotes" và 3 phương án, hợp bài luận, nguy cơ bịa trong bản tin. Bỏ khỏi mục "Có sẵn" của đề.
- `chuyen-kenh`: `references/kenh.md` chưa có kênh Zalo OA và Mini App. Thêm khuôn: tin follower ≤2.000 ký tự, broadcast tối đa 5 bài, tin đã gửi không thu hồi được.
- `soat-su-that` (linhx-bien-tap): dùng nguyên làm M3.
- `cau-hoi-thanh-noi-dung` (linhx-nuoi-cong-dong): dùng chọn đề freebie từ câu hỏi lặp của học viên.
- **Thiếu**: một skill điều phối `ban-tin-tuan` theo khung bước 0–10 ở trên (học lệnh `/weekly` của AIGC Weekly), và phiếu `thu-freebie` cho trợ giảng. Repo chưa có skill nào cắt freebie từ Course OS.
- LAB075 (Mini App mở khoá QR) không có trên máy này và không có trong `LAB/INDEX.md`; chưa đọc được, vòng 1 phải đọc bản cloud.

## Rủi ro
- Hạn mức và phí tin Zalo do bên thứ ba ghi, số không thống nhất; Zalo đổi luật là vỡ nhịp gửi.
- Không có số lượt mở broadcast thì ngưỡng 40% không kiểm được; phải đo trong Mini App.
- Bản quyền: tóm bằng lời mình, trích nguyên văn ngắn, luôn có link (như luật của `cafebiz-radar`).
- Dữ liệu học viên: chỉ gửi người đã đồng ý (cột `dong_y_lien_he` của nuoi-cong-dong); đối chiếu luật bảo vệ dữ liệu cá nhân hiện hành trước khi mời 30–40 lớp.
- agy hay báo OK sai (sổ nhớ: "agy sai 25% vẫn báo OK"): mọi cổng M1–M5 do script Claude đo lại, không tin báo cáo của agy.
- Tin AI cũ đi trong vài ngày: chốt nội dung trước giờ gửi tối đa 24 giờ.

## Nguồn
- [đọc] AIGC Weekly, code tác nhân: https://github.com/miantiao-me/aigc-weekly (thư mục `agent/.opencode/`). Trích editor.md: "只有**总分 ≥ 70 分**的文章才能入选" (chỉ bài tổng ≥70 điểm mới được chọn). Trích weekly.md: "此过程最多重复 3 次" (soát lặp tối đa 3 lần).
- [đọc] AIGC Weekly số Y26W44: https://aigc-weekly.agi.li/weekly/Y26W44
- [đọc] AIPulse: https://github.com/raghavkv85/AIPulse (lọc LLM, khử trùng Jaccard >0,6, tầng "Why It Matters / What You Can Build").
- [đọc] techPulse: https://github.com/c7ozkan/techPulse (`process/agents/reviewer.py`: checklist link giả, nhãn [1], chữ giữ chỗ).
- [đọc] glebis weekly-digest: https://github.com/glebis/claude-skills/tree/main/weekly-digest. Trích: "No item in top `top_n` has slopiness > 6".
- [đọc] deer-flow newsletter-generation: https://github.com/bytedance/deer-flow/tree/main/skills/public/newsletter-generation. Trích: "Every factual claim has a source link".
- [đọc] fact-check-workflow: https://github.com/jamditis/claude-skills-journalism (journalism-core/skills/fact-check-workflow): thang Verified / False / Unverifiable, mẫu đính chính.
- [đọc] Paxrel trên dev.to: https://dev.to/paxrel/how-to-build-an-automated-ai-newsletter-in-2026-full-pipeline-24ic (chấm 0–30, lấy ≥15; không có bước kiểm sự thật).
- [đọc] The Rundown AI số 6/11/2026: https://www.therundown.ai/articles/big-tech-sues-to-save-the-feed
- [đọc] TLDR AI: https://tldr.tech/ai. [chỉ thấy] lời Dan Ni "Write for somebody that works in the industry." qua kết quả tìm kiếm bài Inc: https://inc-1-smart-business-story.beehiiv.com/p/the-man-silicon-valley-reads-every-morning
- [đọc] eSMS FAQ Zalo OA: https://helpcenter.esms.vn/cau-hoi-thuong-gap/zalo-oa. Trích: "mỗi người quan tâm nhận được tối đa 4 tin/tháng".
- [đọc] Nhanh.vn, các loại tin OA: https://pos.manual.nhanh.vn/pos/cai-dat/gui-zalo-zns/cac-loai-tin-cua-oa. Trích: "Trong vòng 30 ngày, mỗi OA được thiết lập và gửi đi tối đa 40 tin Broadcast."
- [đọc] MailerLite benchmark (12/2024–11/2025): https://www.mailerlite.com/blog/email-marketing-benchmarks. Trích: "The average email open rate in 2025 was 43.46%."
- [chỉ thấy] Nhịp AI: https://blog.uncledao.com · 21st.dev newsletter-digest trong NGOAI.md: link nay là trang thư viện giao diện, không có agent.
- Trong repo: `skills/le/cafebiz-radar`, `skills/bo/linhx-viet-bai/skills/{content-synthesizer,chuyen-kenh}`, `skills/bo/linhx-bien-tap/skills/soat-su-that`, `skills/bo/linhx-nuoi-cong-dong`; wiki `trang/he-thong-linhx-edu.md` (h03, h04, h05) nhánh `claude/project-thread-1xveou`.
- Đề DR: `DR/DE-1.md` (Zalo hạn mức, đo mở, bản vàng freebie, bản tin AI tiếng Việt).
