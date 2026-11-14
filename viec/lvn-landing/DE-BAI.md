# Đề: landing Listening Vietnam (chạy thử trọn vòng hệ 3 máy, 14/11/2026)

## Mục tiêu
Một trang giới thiệu Listening Vietnam: dịch vụ nghe mạng xã hội tiếng Việt (social listening) cho doanh nghiệp. Người xem: trưởng phòng marketing, thương hiệu, truyền thông. Việc duy nhất họ cần làm: bấm **Nhận báo cáo mẫu** và để lại email.

## Brand (bắt buộc đọc trước khi dựng)
`brand/brand.json`, `brand/LUAT-ONBRAND.md`, logo SVG trong `brand/`. Màu chính Green #00B579, Dark Green #106047, Light Green #74C465, điểm nhấn Lime #D9E74C (nút CTA). Chữ: Nunito Sans (Google Fonts) thay Avenir Next. KHÔNG dùng màu, font, hoạ tiết TUVA. Tên viết đúng: "Listening Vietnam" (không "Listening Việt Nam", không "ListeningVN").

## 5 khối (id bắt buộc, đúng thứ tự)
1. Màn đầu (không đếm vào 5): logo, câu hứa một dòng, nút CTA `data-cta="bao-cao-mau"`.
2. `#van-de`: doanh nghiệp không biết khách nói gì về mình trên mạng.
3. `#cach-lam`: 5 mô-đun Sentinel, Analyzer, Predictor, Narrator, Tracker, mỗi mô-đun 1 câu tiếng Việt.
4. `#bao-cao-mau`: hình minh hoạ báo cáo (vẽ bằng HTML/CSS hoặc SVG, không ảnh nặng) + 3 chỉ số mẫu ghi rõ "số minh hoạ".
5. `#bang-gia`: 3 gói, giá để `[điền sau]`.
6. `#lien-he`: form `#form-lien-he` (email bắt buộc, tên công ty), gửi thì hiện `#cam-on`. Không gửi đi đâu (chưa có máy chủ).

## Ràng buộc
- Một thư mục tĩnh: `index.html` + css/js/ảnh, tổng < 300 KB (không tính `brand/`, `tham-khao/`, `nghiem-thu/`).
- Không thư viện JS ngoài. Font Google được phép.
- Văn thuần Việt, đủ dấu, câu đủ ý, không giọng quảng cáo sáo rỗng, không chêm tiếng Anh trừ tên mô-đun.
- Không bịa khách hàng, không bịa số liệu thật.

## Định nghĩa xong
`nghiem-thu/test_landing.py` đạt hết (KHÔNG được sửa file này hay thư mục `nghiem-thu/`), Lighthouse mobile Performance và Accessibility ≥ 90, ảnh chụp 360 và 1280 trong `bang-chung/`.
