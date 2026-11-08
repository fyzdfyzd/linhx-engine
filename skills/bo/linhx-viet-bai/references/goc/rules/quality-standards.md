# Quality Standards — Tiêu Chuẩn Bài Viết

## Yêu Cầu Bắt Buộc
- **Số lượng output**: Mỗi đề bài → **3 bài viết** (Variant A, B, C) với góc nhìn khác nhau
- **Độ dài**: Mỗi variant tối thiểu **3500 từ**
- **Điểm Critic**: Mỗi variant tối thiểu **9/10** mới được xuất bản
- **Critic Loop**: Tối đa **3 vòng** lặp cải thiện **per variant**
- **Best Pick**: Sau khi cả 3 variant hoàn thành → so sánh + chọn bản tốt nhất

## Nội Dung Bắt Buộc
1. **Personal Anecdotes** (2-3 đoạn): Câu chuyện cá nhân giả lập — phải tự nhiên, đời thường
2. **Số liệu / Statistics**: Ít nhất 3 con số cụ thể có nguồn
3. **Trích dẫn triết học**: Ít nhất 2 câu trích dẫn từ triết gia hoặc nhà tư tưởng
4. **Nghịch lý trung tâm**: Bài viết phải xoay quanh một paradox rõ ràng

## Rubric Chấm Điểm Critic (10 điểm)
| Tiêu chí | Điểm |
|:---|:---:|
| Độ sắc của "tứ" (insight originality) | /2 |
| Tính văn chương (literary quality) | /2 |
| Chiều sâu triết học (philosophical depth) | /2 |
| Personal Anecdotes thuyết phục | /1 |
| Số liệu + nguồn đáng tin | /1 |
| Cấu trúc & nhịp điệu (rhythm) | /1 |
| Câu kết gây ám ảnh (haunting ending) | /1 |

## Critic Feedback Format
```json
{
  "score": 8,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "specific_fixes": [
    {"paragraph": 3, "issue": "...", "suggestion": "..."}
  ],
  "verdict": "REVISE"  // hoặc "PUBLISH"
}
```
