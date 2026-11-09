# Bài học WF18

Mỗi vòng ghi lỗi gặp và luật rút ra. Luật có ≥ 2 bằng chứng thì sửa vào skill.

## Vòng 1 (9/11, hồ sơ số 0: Linh)
| # | Lỗi quy trình | Chỗ | Luật đề xuất | Bằng chứng |
|---|---|---|---|---|
| L1 | CLI `cau-hoi` không nhận bộ câu riêng; hàm có tham số `bank` nhưng không ai truyền | `skills/bo/linhx-brand-check/scripts/abc_lib.py:115`, `brandcheck.py:158` | Thêm cờ `--bo-cau <file>`; `loai: person` trong facts thì tự dùng `bo-cau-hoi-nguoi.json` | 1 |
| L2 | Bộ câu mặc định chỉ hợp doanh nghiệp (giá, đổi trả, gian hàng) | `data/bo-cau-hoi-abc.json` | Tách bộ câu theo `loai` | 1 |
| L3 | Không khai đối thủ thì `{competitor}` thành "thương hiệu dẫn đầu ngành", câu so sánh người vô nghĩa | `abc_lib.py:119` | Với người: thiếu `competitors` thì bỏ câu `so_sanh` | 1 |
| L4 | Tìm web từ cloud bị chặn LinkedIn, X, Olympia fandom → hồ sơ thiếu đúng những kênh chính chủ nhất | bước 1 | Kênh chặn bot phải đọc bằng Chrome máy công ty; ghi `doc_duoc: false` | 1 |
| L5 | Sai đã biết (Linh bị ghi là CEO IF Agent) chỉ nằm trong bộ nhớ dự án, không trong hồ sơ | `person.json` | Thêm mục `sai_da_biet` và câu gài tương ứng | 1 |
| L6 | `claude-tim/claude-nho` chạy Claude Code (agent), không phải giao diện claude.ai; cần chạy ở thư mục trống để không đọc CLAUDE.md của repo | `abc_hoi.py:55` | Ghi rõ đường lấy; chạy trong thư mục trống | 1 |
| L7 | `collect` chạy tuần tự, 28 câu × 5 lượt × 2 mô hình mất hàng giờ | `abc_hoi.py:collect` | Chạy song song theo câu (đã thử `ThreadPool` 10 luồng) | 1 |
| L8 | **Nhiễm ngữ cảnh chủ tài khoản**: hỏi Claude bằng `claude -p` dưới tài khoản Linh, mô hình thấy email tuanlinh@urah.vn và bộ nhớ dự án, tự nối với "Tuấn Linh" (P07 lượt 1 nhắc LINHX). Tắt bộ nhớ, thay system prompt vẫn còn email. Đã xoá kết quả, không dùng. | `abc_hoi.py:55-58` | Không bao giờ hỏi AI về một người bằng tài khoản của chính người đó. Giao diện: đăng xuất hoặc tài khoản phụ không bộ nhớ; API: khoá riêng. | 1 (nặng, áp ngay) |
| L9 | `--disallowedTools` nhận nhiều giá trị, nuốt câu hỏi đặt sau nó | CLI claude | Đưa câu hỏi qua stdin | 1 |
