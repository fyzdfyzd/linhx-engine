# Nghiên cứu nền WF07 · Content đa kênh

Ngày 9/11/2026, máy Linh. Đọc code thật 6 nguồn (chi tiết ở `NGOAI.md`). Code chép ở `_refs/WF07/`, chỉ đọc, không chạy.

## Kết luận
1. Điểm chung của các nguồn tốt: **tách "nguyên tử" từ bài gốc trước, rồi viết riêng cho từng kênh**. Dán lại hay cắt ngắn bị gọi là "mass-blast".
2. Không nguồn nào có máy chấm thật (claude-repurpose chỉ kiểm file rỗng). LINHX đã có `kiem_van.py` (soat-giong) nên đi trước; thiếu là máy kiểm **chéo kênh** (trùng ý, trùng câu mở, cách ngày, trần bài).
3. LINHX thiếu: bước tách nguyên tử dùng chung, lịch nhiều kênh, khuôn Zalo OA và bản tin trong `chuyen-kenh/references/kenh.md` (hiện có Dân trí, Bloomberg, VnExpress, CafeBiz, Facebook, Substack, LinkedIn).
4. Số liệu Zalo, giờ vàng, tầm với: chưa có nguồn đọc được. Không dùng; đã giao Deep Research (`DR/DE-1.md`).
5. Giữ nguyên thứ đã tốt: soat-giong, giong-linh, tao-bai (rubric 10 điểm), duyet-dang (cổng đăng). Chỉ nối vào.

## Quy trình đề xuất
| Bước | Việc | Ai |
|---|---|---|
| 0 | Chọn ý gốc. Bài lập luận đan chặt, mỗi đoạn phụ thuộc đoạn khác thì để đăng một lần (rampstack: "tightly-integrated argument") | Claude đề xuất, Linh chốt |
| 1 | Tách 5–15 nguyên tử (chuyện, số, luận điểm, câu trích, câu hỏi), mỗi cái ghi chỗ trong bài gốc và điểm 1–5 (theo claude-repurpose) | Claude |
| 2 | Bảng: nguyên tử → 1–2 kênh (Facebook, LinkedIn, Zalo OA, bản tin) + ngày + tên ký | Claude |
| 3 | Viết từng bài theo khuôn kênh (`chuyen-kenh`), 3 ứng viên, chấm theo `tao-bai` | agy |
| 4 | Chạy máy đo (dưới) trên cả chuỗi | Claude |
| 5 | Linh duyệt lịch và bài, đăng qua cổng | Linh |
| 6 | Sau 7 ngày đo tương tác, ghi `BAI-HOC.md` | Claude |

## Máy đo + ngưỡng (đề xuất, ngưỡng cần Linh chốt)
- **Giọng**: `kiem_van.py` mỗi bài ≥ 88 (ngưỡng sẵn có của soat-giong). Mốc đo trên bài dài, cần hiệu chỉnh trên bài Facebook thật của Linh trước khi tin.
- **Chữ máy ≤ 2/1000** (đề thread): chưa có cách đếm; phải định nghĩa (số dấu hiệu AP trên 1000 chữ) rồi mới dùng.
- **Chéo kênh (viết mới, script thường)**: không hai bài trùng câu mở; mỗi bài đứng riêng được, theo ba câu hỏi của rampstack: "Does it stand on its own? Does it use the medium's conventions? Would it earn engagement if it were the only thing the audience saw of this work?" (cả 3 phải có); lịch tối đa 3 bài/ngày, cùng kênh cách ≥ 2 ngày (luật của claude-repurpose, không phải số đo).
- **Sự thật**: mọi số phải có trong nguyên liệu, 0 số bịa là điều kiện dừng. Tham chiếu ngưỡng dừng của rampstack editorial-qa: "If more than 5% of sampled pages fail the manual review, halt new generation".
- **Chấm mù** (đề xuất của mình, chưa có nguồn ngoài): người chấm nhận 8 bài trộn (4 của Linh, 4 của máy) không biết nguồn; đạt khi không đoán đúng hơn ngẫu nhiên.
- **Kết quả thật**: tương tác sau 7 ngày so với trung bình 10 bài trước cùng kênh. Chưa có ngưỡng ngoài đáng tin.

## Bản vàng
Chưa tải được mẫu ngoài đáng tin. Mốc tạm: bài Linh đã in ở trang tác giả Dân trí https://dantri.com.vn/tac-gia/le-bich-3390.htm (đã nằm trong `kenh.md`) cho bài dài. Chuỗi đa kênh tiếng Việt có số đo đã giao `DR/DE-1.md` (câu 4); chọn 3–5 rồi lưu vào `vang/`. [chỉ thấy]

## Sửa vào skill nào
- **Mới: `tach-nguyen-tu`** (hoặc bước đầu trong `chuyen-kenh`): bước 1–2 ở trên, khuôn lấy từ claude-repurpose.
- **`chuyen-kenh/references/kenh.md`**: thêm Zalo OA và bản tin, sau khi có số từ DR.
- **`chuyen-kenh/SKILL.md`**: thêm bước chạy máy chéo kênh và bảng lịch. Bước 3 (Facebook chỉ giữ một tứ một chuyện) giữ.
- **`soat-giong`**: nạp danh sách dấu hiệu AI bài mạng của marketingskills (xem `NGOAI.md`).
- **Chưa kiểm**: `ban-dang`/`duyet-dang` gắn với CLI `kenhao.py` của người ảo; chưa xem có dùng được cho kênh của Linh không.
- Không thấy skill thừa.

## Rủi ro
- Skill Mỹ dịch thẳng sẽ ra giọng máy.
- Brands Vietnam trả 403 cho trình tự động nên số Zalo chưa kiểm.
- Girard, Averi là blog bán dịch vụ: tỉ lệ 12:1 là mục tiêu của họ, không phải chuẩn ngành. Averi ghi hai ngày đăng lệch nhau.

## Nguồn
- [đọc] claude-repurpose: https://github.com/AgriciDaniel/claude-repurpose
- [đọc] marketingskills: https://github.com/coreyhaines31/marketingskills
- [đọc] claude-gtm-plugin: https://github.com/manojbajaj95/claude-gtm-plugin
- [đọc] rampstackco/claude-skills (`content-repurposing`, `editorial-qa`): https://github.com/rampstackco/claude-skills
- [đọc] openclaudia `content-repurposing`: https://github.com/openclaudia/openclaudia-skills
- [đọc] Girard Media: "...targeting a minimum ratio of 12:1 for mature atomization programs." https://girardmedia.com/blog/content-atomization-repurposing-framework
- [đọc] Averi: "...breaking it into smaller pieces only multiplies mediocrity." https://www.averi.ai/how-to/content-repurposing-at-scale-how-to-turn-1-piece-into-20-assets
- [chỉ thấy] ClaudeKit social (docs.claudekit.cc): repo mrgoonie/claudekit-skills không chứa skill social
- [chỉ thấy] Brands Vietnam về Zalo broadcast (403): https://www.brandsvietnam.com/congdong/topic/331972-Gui-tin-nhan-hang-loat-khong-can-tao-nhom-chat-rieng-voi-Zalo-Broadcast
- [DR] chờ `DR/KQ-1.md`
