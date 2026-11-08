# Schema một cuộc thi (data/contests.json, data/new-*.json)

```json
{
  "id": "slug-ngan-khong-dau",
  "title": "Tên cuộc thi, có năm",
  "organizer": "Đơn vị tổ chức",
  "category": "van-chuong | bao-chi | truyen-thong-marketing | sang-tao-so-ai | video-anh | giai-thuong-ca-nhan | quoc-te",
  "format": "truyen-ngan | tan-van | tho | bai-bao | tieu-luan | video | anh | podcast | chien-dich | ho-so-de-cu",
  "eligibility": "Ai được nộp, nguyên văn ngắn từ thể lệ (tuổi, quốc tịch, nghề)",
  "language": "vi | en | vi/en",
  "fee": "miễn phí | số tiền",
  "prize": "Giải cao nhất",
  "url": "Trang thể lệ gốc",
  "deadline": "YYYY-MM-DD hoặc null (chỉ khi đọc thấy trong thể lệ năm nay)",
  "expected_deadline": "YYYY-MM theo mùa trước, hoặc null",
  "results_date": "YYYY-MM-DD hoặc null",
  "results_url": "Trang sẽ đăng kết quả (nếu biết)",
  "cycle": "hằng năm | 2 năm | 1 lần",
  "status": "open | upcoming | closed | recurring",
  "verified": true,
  "source": "URL bằng chứng",
  "branding_value": 4,
  "fit_note": "Một câu: vì sao hợp/không hợp với Linh",
  "rules_url": "Link thể lệ/PDF nếu khác url",
  "ai_policy": "cho phép | cấm | không nói",
  "length": "Giới hạn chữ/phút",
  "verified_on": "YYYY-MM-DD ngày đã đọc trang chính thức",
  "gate": "(tuỳ chọn) ghi đè điều kiện: Nộp được | Kiểm điều kiện | Không đủ điều kiện | Qua tổ chức"
}
```

`branding_value` 1–5: 5 = giải quốc gia/quốc tế có báo lớn đưa tin, danh xưng dùng được trong bio; 1 = bình chọn like, đơn vị nhỏ.
