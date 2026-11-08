# linhx-tu-duy v0.2 (LAB030)

Bộ 52 thẻ mental model bằng tiếng Việt, chia hai nguồn:
- 34 thẻ Naval (A–E, G), rút từ danh mục 252 mục trong `output/DANH-MUC-DAY-DU-NAVAL.md`, câu trích đã đối chiếu navalmanack.com và gắn nhãn `[V]`.
- 16 thẻ Munger/Farnam Street (M1–M16), câu trích gắn nhãn `[R]`, cần đối chiếu lại trước khi trích công khai.

Plugin kèm vòng duy trì sao cho mỗi thẻ gắn với ví dụ thật của Linh.

## Cài
```
/plugin marketplace add D:/LINHX/LAB/LAB030-MENTAL-MODEL/src
/plugin install linhx-tu-duy@linhx-lab-030
```
Lần đầu chạy: `node <plugin>/scripts/tu-duy.js init --linhx`. Lệnh này tạo `D:/LINHX/MENTAL-MODEL` và lưu cấu hình ở `~/.linhx-tu-duy.json`.

Antigravity (agy) không dùng plugin. Gọi thẳng `node .../tu-duy.js <lệnh>` và đọc hướng dẫn trong `skills/*/SKILL.md`.

## Skill
| Gõ | Làm gì |
|---|---|
| `/mm-chon` | Chọn 0–3 thẻ cho tình huống, chạy câu kích hoạt, phản biện, ra thẻ kết quả |
| `/mm-quyet` | Ghi quyết định (chỉ thêm, không sửa) và chấm quyết định cũ |
| `/mm-ngay` | Thẻ của ngày, ghi buổi tối, thêm ví dụ thật |
| `/mm-tuan` | Chấm tuần, độ phủ, thẻ bị quên, hiệu chỉnh; cuối tháng rút heuristic riêng |

## Dữ liệu (thư mục của Linh)
- `su-kien.jsonl`: nguồn gốc, chỉ thêm. Ghi thẻ của ngày, ví dụ, quyết định, lần chấm.
- `nhat-ky-quyet-dinh.md`, `the-hang-ngay.md`: bản đọc được do script ghi thêm.
- `the-rieng/`: thẻ riêng hoặc thẻ sửa lại. Thẻ ở đây có cùng mã thì đè thẻ gốc.
- `ngu-lap-lai.md`: danh sách sai lầm hay lặp (thẻ M8), tối đa 7 dòng.

## Sửa nội dung thẻ
Sửa `LAB030/output/BO-MENTAL-MODEL-*.md`, rồi chạy `python scripts/tach-the.py` để tạo lại `the/`.

## Lịch tự chạy (PA3, chưa bật)
Muốn tự chạy thì dùng Task Scheduler, giống LAB013:
- 7:00 sáng hằng ngày: `ngay`
- 20:00 Chủ nhật: `tuan`
