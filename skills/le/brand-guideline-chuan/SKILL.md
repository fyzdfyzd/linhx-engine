---
name: "brand-guideline-chuan"
description: "Dựng hoặc làm lại brand guideline công ty theo chuẩn BTMH 2026 (LAB043): khung, bộ dựng, ảnh ChatGPT mockup, phương án chọn. Dùng khi Linh bảo làm/rà soát/chạy lại guideline."
---

# Brand guideline chuẩn BTMH 2026

Gốc dự án: `D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\` (bản sao cloud: `/mnt/project-files/LAB043-DESIGN-ONBRAND/`). Đọc trước:
- `.handoff/` (file bàn giao mới nhất: việc đang dở, trạng thái từng brand)
- `chuan-guideline/KHUNG-GUIDELINE-CHUAN.md` (khung, mục lục, mức chất lượng)
- `chuan-guideline/bo-dung/HUONG-DAN.md` (bộ dựng + ghép mockup)
- Mẫu chuẩn: `chuan-guideline/btmh-2026-trang/tr-NN.jpg` (BTMH Guideline 2026, Linh gọi là "quy chuẩn cao"); mẫu đã đạt: `brands/ifagent/guideline/`, `brands/unikon/guideline/`.

## Chuẩn bắt buộc (Linh chốt 19/10/2026)
- PDF ngang 1920x1080, 30-45 trang, dàn trang như BTMH: đầu trang PHẦN / n.n mục / → tiểu mục, tên brand giữa, số trang; cột trái ô quy tắc đánh số, cột phải hình có nhãn; chân trang tên phần lớn.
- PHẦN 1 Nền tảng, 2 Giọng nói, 3 Nhận diện (logo có số đo x/mm/px, đường chéo/8, lề /20, partnership, nền màu, âm/dương bản, 12-16 lỗi sai; màu có thang 20-180% và tỉ lệ 60/30/10, 50/20/10/10/10 theo dòng sản phẩm; chữ phân cấp; ảnh đặc tả + cần tránh; ứng dụng mockup thật), 4 PHƯƠNG ÁN CHỌN, 5 Pháp lý.
- Mọi chỗ cần quyết: 3-4 phương án KHÁC HẲN NHAU, dựng thành hình thật, ★ khuyến nghị + lý do một dòng, bảng tổng hợp; kèm `brands/<id>/PHUONG-AN-CHON.md` có cột "Chốt".
- Nội dung chỉ lấy từ `nguon-bu/<BRAND>/` (gốc `D:\@WF\DATA\BU\<BRAND>`) và cây brand. Không bịa số liệu, khách hàng, giải thưởng; tên khách hàng chỉ nêu ngành cho tới khi Linh cho phép. Không lorem ipsum, không tên file nội bộ trong trang. Font bản quyền chỉ dùng nội bộ.

## Quy trình một bộ (làm từng bộ, giao từng bộ)
1. Đọc cây `brands/<id>/` (brand.json, DOI-CHIEU.md, 01-logo, 03-chu, 04-hinh-anh) và nguồn doanh nghiệp. Brand chưa có cây: dựng đủ 10 ngăn 00-goc…09-khuon như `brands/ifagent/`.
2. Ảnh: viết `04-hinh-anh/PROMPT-CHATGPT-V2.md` 10 prompt (6 mockup có mặt phẳng hồng phẳng #FF00FF: danh thiếp, bối cảnh chính, trình chiếu, laptop + điện thoại, biển hiệu, quà tặng; 3 ảnh phong cách; 1 ảnh cần tránh). Tạo bằng ChatGPT Plus trên Chrome chính của Linh qua Claude in Chrome (Remote Control ở `D:\LINHX\LAB`), mỗi ảnh một tab/cuộc trò chuyện mới, lưu `gpt2-*.png` + .txt prompt. Ảnh bị từ chối thì bỏ, không lách bộ lọc. Không đăng nhập, không đổi cài đặt.
3. Chép `brands/ifagent/guideline-noi-dung.py` (hoặc bộ gần nhất) sang `brands/<id>/guideline-noi-dung.py`, sửa NOI_DUNG, mockup(), trang(). Không sửa `chuan-guideline/bo-dung/` khi bộ khác đang dựng; hàm thiếu viết trong file nội dung.
4. Ghép mockup: `python chuan-guideline/bo-dung/ghep_mockup.py nen.png tk1.png tk2.png -o ra.jpg --bong 0.6 --phong 1.25`; kiểm góc trước bằng `--chi-do --xem kt.png`. Cảnh có đèn hồng: ngưỡng chặt, chỉ lấy vùng lớn nhất. Ảnh nặng lưu JPEG 85 ở `04-hinh-anh/jpg/`.
5. Dựng (trong `brands/<id>/`): `python ../../chuan-guideline/bo-dung/dung_guideline.py guideline-noi-dung.py --lam-moi-mockup`. Ra `guideline/<id>-brand-guideline-2026.pdf` + .html + trang/ + contact-sheet.png; bản cũ chuyển vào `guideline/v1/`. PDF < 25 MB.
6. Kiểm bằng mắt: xem PNG từng trang, so với BTMH 2026 và IF Agent, sửa ít nhất 2 vòng: không chữ tràn/đè, không trang trống nửa dưới, mockup không viền hồng.
7. Ghi mục "Làm lại <ngày>" đầu `DOI-CHIEU.md`. Giao Linh: PDF, contact sheet, bảng chốt; trả lời ngắn liệt kê các điểm cần chốt với ★.
8. Khi Linh chốt: sửa brand.json, dựng lại, chuyển trang PHẦN 4 đã chốt thành quy tắc ở PHẦN 3.

## Lưu ý máy
- Builder viết cho Chromium Linux; trên Windows trỏ Edge/Chrome (chưa kiểm).
- Sandbox thư mục trên máy không xoá được file: giải nén ra thư mục tạm rồi `cp -r`; file > 25 MB chia phần 8 MB khi chép.
- Rác tạm: `D:\LINHX\LAB\_tam-lab043-nap\` (Linh tự xoá).