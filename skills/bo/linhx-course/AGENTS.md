# linhx-course — quy tắc chung
- Trạng thái nằm trên đĩa: `course/course.json` + các file của từng bước. Bước sau chỉ chạy khi file đầu ra của bước trước tồn tại.
- Agent chỉ viết file text (YAML/MD/JSON). Render, TTS, lip-sync, ghép video do script trong `engine/` làm, không gọi LLM.
- Giọng là đồng hồ chủ: khoá lời giảng → TTS → đo thời lượng → mới ghép hình.
- Hỏi người dùng trước mọi bước tốn GPU hoặc tiền. Chạy 1 bài pilot trước cả khoá.
- Tiếng Việt: font có dấu (Be Vietnam Pro), thuật ngữ tiếng Anh liệt kê trong `pronunciation.yaml`.
