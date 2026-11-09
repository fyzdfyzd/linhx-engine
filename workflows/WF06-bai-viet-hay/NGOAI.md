# Người ngoài đã làm: WF06

Bước 0, tìm sơ bộ 9/11 (GitHub, trang skill, blog, mạng). **Cập nhật 9/11 (nghiên cứu nền): đã clone và đọc 10 nguồn ở `D:\LINHX\WF-NC\_refs\WF06\` (chỉ đọc, không chạy code lạ). Tổng hợp ở `NGHIEN-CUU.md`.** Vòng 1 phải đọc code/quy trình ít nhất 3 cái tốt nhất, ghi: lấy gì, bỏ gì, so với skill LINHX đang có.

| Nguồn | Link | Đọc để |
|---|---|---|
| humanizer (aihxp) | https://github.com/aihxp/humanizer | bỏ dấu vết văn AI |
| humanize-writing (jpeggdev) | https://github.com/jpeggdev/humanize-writing | cùng loại |
| Top 5 skill viết theo sao GitHub | https://www.analyticsvidhya.com/blog/2026/08/top-5-claude-writing-skills/ | so với LAB049/LAB080 |
| writing-style (skill-stack) | https://playbooks.com/skills/cdeistopened/skill-stack/writing-style | học giọng tác giả |
| anti-ai-writing | https://skillsmp.com/skills/majiayu000-claude-skill-registry-data-data-anti-ai-writing-skill-md | danh sách mẫu câu AI |

## Còn phải tìm ở vòng 1
- GitHub tìm theo tên skill + 'SKILL.md'; skills.sh, claudemarketplaces, openskillindex.
- Mạng: X, LinkedIn, Reddit, nhóm Facebook VN; tiếng Trung (Zhihu) khi hợp.
- Ghi kết quả đọc vào bảng dưới:

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| blader/humanizer (66.639 sao, MIT, v3.1.0) | `SKILL.md` đủ 26 mẫu, 6 nhóm (dàn dựng, nhịp theo luật, phóng đại, định dạng, dư âm chat, sai người đọc); 4 bước làm | Luật "không thêm fact, tên, số, ngày, trích dẫn nếu không từ nguồn hoặc người dùng"; xếp mẫu mạnh trước, mẫu "yếu khi đứng riêng" phải có mẫu khác đi kèm mới sửa; kiểm lại 5 mẫu hay sót sau khi viết lại | Danh sách từ AI tiếng Anh; luật ngoặc cong; chế độ không có mẫu giọng |
| aihxp/humanizer (MIT, v1.3.1) | `SKILL.md`, `references/tell-patterns.md` (32 mẫu), `do-not-flag.md`, `evals/evals.json` | "Variance over substitution"; đo mật độ trước rồi chọn mức sửa (nhẹ/chuẩn/đủ); mục bắt buộc "Cố ý giữ" và "Kiểm nghĩa", soi cả suy luận mềm (nhân quả, "phần lớn thời gian…"); chế độ thái độ: được thêm thái độ với điều đã có, không thêm sự kiện; lượt 3 tự soát có quyền phủ quyết | Lượt dọn ký tự Unicode ẩn (ít giá trị với bài báo); giới hạn mật độ tính theo mẫu tiếng Anh |
| hardikpandya/stop-slop (18.748 sao, MIT) | `SKILL.md`, `references/structures.md`, `phrases.md` | Thang 5 chiều × 10 (thẳng, nhịp, tin người đọc, thật, đặc), dưới 35/50 thì sửa: dùng làm khung cho giám khảo mù; mẫu "giao hành động người cho vật vô tri" ("dữ liệu cho thấy"); "cắt câu nghe như trích dẫn để đóng khung" | Cấm tuyệt đối gạch dài, mọi trạng từ, mọi câu bị động, mọi danh sách ba: quá gắt, trái giọng Linh (câu dài, dùng "chúng ta") |
| jpeggdev/humanize-writing (79 sao, MIT, v2.0.0) | `SKILL.md` 8 lượt, `references/ai-tells.md` | Luật "chồng mẫu": nhiều tín hiệu yếu trên một cụm tính là một lỗi, không đếm ba lần (áp vào cách đếm M4); bỏ khúc kết "thách thức và triển vọng" | Lượt 8 "thêm hồn": dễ thành bịa chi tiết |
| cdeistopened/skill-stack (29 sao) | `writing-style`, `ghostwriter`, `voice-analyzer` | `voice-analyzer` 5 pha: mẫu → đặc trưng → hồ sơ → skill giọng → kiểm lại với nguồn; mục "những gì tác giả không làm" (LINHX `SO-TAY-GIONG.md` đã có tương tự) | Khung "8 ham muốn", bảng thay từ 1-1 (đổi chữ chỉ dời vết) |
| majiayu000/claude-skill-registry-data | `data/anti-ai-writing`, `data/anti-ai-validator` (tiếng Hàn) | Bằng chứng mỗi ngôn ngữ có mẫu máy riêng (tiếng Hàn ưu tiên "~를 넘어"), nên danh sách tiếng Việt phải học từ dữ liệu Việt, như `tu_may.py` | Danh sách tiếng Anh/Hàn |
| google-deepmind/long-form-factuality (SAFE) | `eval/safe/README.md`, `config.py`, `rate_atomic_fact.py` | Tách bài thành khẳng định nhỏ → viết lại cho tự đứng → lọc liên quan → tra từng cái, nhãn Supported/Not Supported; tối đa 5 bước tra, 3 kết quả mỗi lần. Dùng cho M2, tra trong kho nguồn của bài | Gọi Serper/OpenAI, cần API key; không cài |
| sam-paech/slop-forensics | README, `analysis.py` (LAB080 đã đọc kỹ) | Cách tìm chữ thặng dư theo tỉ lệ tần suất; `tu_may.py` LINHX đã làm theo, so cùng đề | Phần cây phả hệ model |
| errata-ai/write-good, proselint (gói Vale) | cấu trúc tệp luật YAML (Weasel, Passive, Cliches…) | Khuôn một luật = mức + thông báo + mẫu: dùng khi gom luật VA thành `danh-sach-hoc.json` | Không cài Vale; luật tiếng Anh |
| NYT Opinion Guest Essays | trang trợ giúp chính thức | Bản chú nguồn cho từng khẳng định trước khi đăng; nêu vì sao tác giả có quyền nói (khớp chuẩn VA 1.4) | — |
| Wikipedia: Signs of AI writing | phần mở đầu, danh mục | Gốc của blader/jpeggdev; nhóm "dấu hiệu viết bởi người" và "dấu hiệu đã hết tác dụng" | Không dựa vào máy dò AI |
| analyticsvidhya, playbooks.com, skillsmp | chỉ thấy (trang tổng hợp) | Đọc thẳng repo gốc thay cho trang này | — |
| Nội bộ LAB049 (chuẩn VA 29/10, longform v3, `kiem_longform.py`) | đọc đủ, chạy thử trên 8 bài Linh + bản VA | Phải đưa vào `skills/` của repo; là thước chính | — |
