# Agent Logging & Timekeeping — Hệ Thống Ghi Chép

## 1. Agent Work Log (`_agent_log.md`)
Mỗi project folder **BẮT BUỘC** có file `_agent_log.md` ghi lại toàn bộ hoạt động.

### Format
```markdown
# Agent Log — {Project Slug}

## [Timestamp] — {Agent Name} — Bước {N} — Variant {A|B|C|chung}
- **Hành động**: Mô tả ngắn gọn việc đã làm
- **Kết quả**: Tên file output + tóm tắt 1 dòng
- **Ghi chú**: Vấn đề gặp phải (nếu có)
```

> **Bước 1→5**: ghi `Variant: chung` (research dùng chung cho 3 variant)
> **Bước 6→9**: ghi `Variant: A`, `Variant: B`, hoặc `Variant: C`

### Quy tắc
- Ghi log **NGAY KHI BẮT ĐẦU** mỗi bước (ghi timestamp bắt đầu)
- Ghi **NGAY KHI KẾT THÚC** mỗi bước (ghi timestamp kết thúc + kết quả)
- Không bao giờ xóa log cũ — chỉ append

---

## 2. Lessons Learned (`_lessons_learned.md`)
Mỗi agent sau khi hoàn thành bước, phải tự đánh giá và ghi bài học.

### Format
```markdown
# Lessons Learned — {Project Slug}

## {Agent Name} — Bước {N} — {Date}

### Điều làm tốt
- ...

### Điều cần cải thiện
- ...

### Bài học rút ra
- **[INSIGHT]**: Mô tả insight có thể áp dụng cho lần sau
- **[PATTERN]**: Pattern lặp lại cần lưu ý
- **[AVOID]**: Điều cần tránh
```

### Quy tắc
- Ghi **sau mỗi bước** (không đợi hết pipeline mới ghi)
- Critic Agent GHI NHIỀU NHẤT — mỗi loop là 1 entry
- Lessons từ project trước có thể được đọc lại để cải thiện project sau

---

## 3. Timelog (`_timelog.json`)
Thời gian thực thi được tính từ **file modification timestamps (mtime)** của OS — không tự báo cáo.

### Cách hoạt động
- Khi agent lưu file output (ví dụ `01_Seed_Input.json`), OS tự ghi nhận mtime
- Skill `time-tracker` đọc mtime của tất cả file output → tính duration giữa các bước
- **Agent KHÔNG cần tự ghi thời gian** — chỉ cần lưu file đúng thứ tự

### Khi nào generate timelog
- Sau khi pipeline hoàn thành (Bước 9) → chạy skill `time-tracker` để tạo `_timelog.json`
- Khi `/resume-article` → đọc mtime file cuối để biết bước dở dang chạy lúc nào

---

## 4. Tích hợp vào Pipeline
Mỗi skill khi chạy **PHẢI**:
1. Thực thi nhiệm vụ chính → **lưu file output ngay** (OS ghi mtime)
2. Ghi hành động + kết quả vào `_agent_log.md`
3. Tự viết lessons learned vào `_lessons_learned.md`
4. Cập nhật `_status.json`
5. Sau bước cuối cùng (Bước 9) → chạy skill `time-tracker` để generate `_timelog.json`
