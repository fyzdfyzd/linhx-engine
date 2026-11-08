---
name: thoi-quen-ai
description: Kiểm thử một nhận xét về thói quen viết của AI (cụm mở đầu, cấu trúc câu, từ đặc trưng, gạch dài, định dạng...) trên nhiều model với số lượng lớn, ra thống kê. Dùng khi Linh nói "kiểm nhận xét", "AI có hay... không", "model nào hay...", "benchmark thói quen viết".
---

# Kiểm thử thói quen viết của AI

Engine: `scripts/tqa.py` (Python chuẩn, không cần cài gì). Thư viện giả thuyết: `gia-thuyet/thu-vien-en.json`, `gia-thuyet/thu-vien-vi.json`.

## Vòng 5 bước

1. **Nhận xét → giả thuyết.** Viết một mục JSON (xem khuôn dưới). Hỏi lại Linh chỉ khi không rõ so với ai (người hay các model khác). Tìm trong thư viện trước, có rồi thì dùng lại. Ghi giả thuyết vào file TRƯỚC khi nhìn dữ liệu.
2. **Kiểm thước đo.** `tqa.py check --hyp <file> --id <id> --data <jsonl> --n 15` rồi đọc từng chỗ khớp. Sai quá 2/15 thì sửa regex.
3. **Có dữ liệu chưa?** Dùng kho sẵn trước (0 token): `data/` của LAB080, kho slop-forensics. Thiếu model hoặc thiếu ngôn ngữ thì chạy `run`. Cần mốc người thì `import <thư mục bài người> --model human`.
4. **Chạy.** `tqa.py test --data <jsonl...> --hyp <file> --out output/KET-QUA-<ngay>-<ten>.md`.
5. **Báo Linh** 3 dòng: đúng với model nào, ngược với model nào, điều kiện (bộ đề, số bài, lệnh hệ thống). Không kết luận "AI nói chung" khi chỉ so giữa các model; muốn nói "AI hơn người" phải có mốc người cùng đề.

## Khuôn giả thuyết

```json
{"id":"em-dash","claim":"AI dùng gạch dài dày đặc","source":"ai nói, ở đâu",
 "metric":{"kind":"regex","pattern":"—","flags":"i","scope":"text","unit":"per_1k_words"},
 "expect":{"direction":"higher","against":"others","min_ratio":1.5}}
```

- `kind`: `regex` hoặc `stat`.
- `scope` (regex): `text` cả bài · `first_sentence` câu mở bài · `last_sentence` câu kết · `sentence_start` 4 chữ đầu mỗi câu (dùng `^` trong pattern).
- `unit`: `per_1k_words` · `per_sentence` · `presence` (bài có hay không) · `count`.
- `stat`: `sentence_len_mean`, `sentence_len_cv` (thấp = câu đều), `bullet_share`, `heading_count`, `bold_per_1k`, `opener_repeat`, `words`.
- `against`: `others` (so với gộp các model còn lại) · `human` (cần dữ liệu model "human") · `value` kèm `"value": 0.5` (ngưỡng tuyệt đối).
- `direction`: `higher` / `lower`. `min_ratio`: nhận xét kiểu "gấp 3 lần" thì đặt 3.

Kết luận mỗi model: **ĐÚNG** (p Holm < 0,05 và cận dưới CI tỉ lệ ≥ min_ratio) · **ĐÚNG HƯỚNG, CHƯA ĐỦ MẠNH** · **NGƯỢC** (CI nằm hẳn phía bên kia) · **CHƯA RÕ**.

## Chạy model

`tqa.py run --prompts <de.jsonl> --models claude:sonnet,claude:haiku,gemini:gemini-2.5-pro,openrouter:openai/gpt-5,oai:qwen3 --n 1 --out data/<ten>.jsonl`

- `claude:` gọi Claude Code CLI, `gemini:` gọi Gemini CLI, `openrouter:` cần `OPENROUTER_API_KEY` (một khoá cho hàng trăm model, rẻ nhất cho chạy lớn), `oai:` mọi API kiểu OpenAI (`OAI_BASE_URL`, mặc định Ollama máy nhà).
- Lệnh hệ thống mặc định "You are a helpful assistant." để mọi model cùng điều kiện; CLI chạy ở thư mục tạm để không đọc CLAUDE.md của dự án.
- Chạy tiếp được: lượt nào đã có trong file ra thì bỏ qua.
- Chạy lớn (hàng nghìn bài): giao máy Linh hoặc agy chạy `run` với OpenRouter; Claude chỉ chạy `test` trên file kết quả (gần 0 token).

## Tìm thói quen chưa ai nói

`tqa.py explore --data <jsonl> --kind opener_sentence --k 2` liệt kê cụm mở câu (hoặc `opener_text`: mở bài) đặc trưng từng model so với các model khác. Cụm nào đáng ngờ thì viết thành giả thuyết rồi kiểm ở bước 1–4 trên bộ đề KHÁC (tránh tự xác nhận).

## Giới hạn hiện tại

- Regex chỉ bắt mặt chữ; cấu trúc sâu (khuôn từ loại, ẩn dụ xuyên đoạn) cần bước giám khảo LLM, chưa có.
- Tách câu bằng dấu câu, không dùng mô hình ngôn ngữ; tiếng Việt chưa tách từ ghép (đếm âm tiết).
- CI tỉ lệ dùng delta method (bootstrap khi mẫu ≤ 400 bài); chưa tính cụm theo đề.
