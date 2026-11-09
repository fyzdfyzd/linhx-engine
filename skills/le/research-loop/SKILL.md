---
name: research-loop
description: Chạy vòng lặp nghiên cứu tự động qua đêm (hiểu đề → tài liệu → ý tưởng → thí nghiệm → phân tích) với phép đo khoá, nhật ký TSV và DIGEST buổi sáng. Dùng khi người nói "chạy research loop", "cho agent thử ý tưởng cả đêm", "autoresearch".
metadata:
  version: "0.1.0"
---

# Research loop

Con người đứng **trên** vòng, không đứng **trong** vòng: người viết `program.md` và idea bank buổi tối, agent chạy bước ③④⑤ không hỏi, sáng ra người đọc `DIGEST.md`. Khuôn lấy từ karpathy/autoresearch (phép đo khoá, giữ/bỏ bằng git), AI Scientist v2 (giai đoạn, debug tối đa 3), OpenEvolve (70% khai thác / 30% khám phá), open_deep_research (quay lại đọc tài liệu có trần).

`NK=scripts/nhat_ky.py`, `D=<thư mục chạy>` (mặc định `runs/<ngày>`).

## Thiết lập (cần người, một lần)

1. Chép `templates/program.md` vào gốc dự án, cùng người điền: mục tiêu, **lệnh đo** (in một dòng `metric: <số>`), thấp hay cao là tốt, **file được sửa**, file cấm sửa, ngân sách mỗi lần chạy, trần token cả đêm. Không có lệnh đo cố định thì dừng ở đây và nói với người: vòng lặp chưa chạy được.
2. `python NK init D --thap-tot` (hoặc `--cao-tot`).
3. Nạp idea bank từ literature review của người: mỗi ý một lệnh `python NK y D "mô tả" --nguon "bài báo/người"`.
4. Tạo nhánh git `research/<ngày>`. Thư mục chạy D và `__pycache__` phải nằm trong `.gitignore`; skill và script không được nằm trong repo thí nghiệm (reset sẽ kéo script về bản cũ). Người xác nhận một lần, từ đây không hỏi nữa.

## Vòng lặp (không dừng để hỏi người)

Lặp tới khi hết trần token / thời gian trong `program.md`:

1. `python NK chon D` và làm theo dòng `BUOC:`:
   - `baseline`: chạy nguyên trạng.
   - `khai_thac` / `kham_pha`: sửa **chỉ** các file được phép theo ý đó. Một thay đổi nhỏ, một ý một lần.
   - `quay_lai_doc`: tìm tài liệu tối đa 5 lượt tìm kiếm, nén mỗi nguồn thành 2 dòng vào `D/doc-them.md`, thêm tối đa 3 ý (`--nguon agent:<link>`).
   - `sinh_y`: đọc `nhat-ky.tsv`, viết 3 ý mới khác các ý đã thử (`--nguon agent`).
2. Nếu `git diff --quiet` (code không đổi) thì không chạy, quay lại bước 1. Nếu có đổi: `git commit -am "<ý>: <mô tả>"`, chạy lệnh đo, đẩy log vào file (`> D/run.log 2>&1`), chỉ đọc dòng `metric:`.
3. Không có `metric:` là lỗi: xem `tail -n 30 D/run.log`, sửa tối đa 3 lần; vẫn lỗi thì ghi `crash` và `git reset --hard $(python NK tot D)`.
4. Tốt hơn tốt nhất hiện tại thì `keep` (giữ commit); bằng hoặc kém thì `discard` và `git reset --hard $(python NK tot D)` (commit keep gần nhất; không dùng `HEAD~1`, vì nếu commit bị bỏ qua thì HEAD~1 xoá mất bản tốt nhất). Cùng điểm mà code gọn hơn thì `keep`.
5. `python NK ghi D <Yxxx|BASE> <số|crash> <keep|discard|crash> "mô tả" --commit <hash> --token <ước tính>`.
Không ghi vào nhật ký những commit dọn dẹp (gitignore, đổi tên); chúng làm sai bộ đếm kẹt. Bước 2–5 đã gói sẵn trong `scripts/chay_mot_lan.sh <Yxxx> "mô tả"` (đặt biến NK nếu script không ở ~/.claude/skills).
6. Mỗi 10 thí nghiệm: `python NK tom D > D/DIGEST.md`.

## Luật cứng

- Không sửa lệnh đo, dữ liệu đánh giá, tập giữ riêng. Không cài thư viện mới.
- Không hỏi "có chạy tiếp không". Người có thể đang ngủ.
- Kết quả lệch >30% so với baseline: không ăn mừng, ghi chú "nghi lách phép đo" vào mô tả và chạy lại một lần với seed khác.
- Mọi khẳng định trong DIGEST trỏ về số thứ tự dòng nhật ký hoặc commit.

## Kết thúc

`python NK tom D > D/DIGEST.md`, thêm 3 dòng tự viết: điều học được, ý nên bỏ hẳn, ý nên thử tiếp. Người đọc DIGEST, xem diff của top 3 và mọi dòng "cần người quyết".
