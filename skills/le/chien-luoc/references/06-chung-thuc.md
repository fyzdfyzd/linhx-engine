# 06 · Bảng chứng thực số liệu

Rút từ `Chung_Thuc_Du_Lieu_NC7_V4` (Trân Bảo). Mục đích: mọi luận điểm chiến lược truy ngược được về dữ liệu thô nội bộ và được kiểm chéo bằng nguồn công khai. Lãnh đạo khách hỏi "số này ở đâu ra" thì mở bảng này.

## 1. Khuôn

```
# BẢNG CHỨNG THỰC VÀ ĐỐI CHIẾU NGUỒN · <tên báo cáo, phiên bản>

Tài liệu này truy mọi luận điểm trong <báo cáo> về file dữ liệu thô và kiểm chéo bằng nguồn công khai (báo cáo tài chính, website nhãn hàng, báo chí).

## 1. Phần tóm tắt điều hành và xu hướng
| Luận điểm | Nguồn nội bộ (file) | Kiểm chéo bên ngoài (nguồn, link, ngày truy cập) | Kết luận |
|---|---|---|---|
| Khách dịch từ tích trữ sang thời trang và quà | NC9_V2..., NC8_TikTok... | CafeF, Nhịp Cầu Đầu Tư [BC-012] | ĐÃ CHỨNG THỰC |

## 2. Theo từng đối thủ
### 2.1 <Đối thủ A>
| Luận điểm | Nguồn nội bộ | Kiểm chéo | Kết luận |
```

Cột kết luận chỉ có 4 giá trị: **ĐÃ CHỨNG THỰC** · **MỘT PHẦN** (nêu phần nào chưa) · **CHƯA TÌM THẤY** · **SAI, ĐÃ SỬA** (ghi số cũ và số mới).

## 2. Luật

1. Mọi luận điểm có số trong tóm tắt điều hành phải có dòng ở đây.
2. Link phải mở được trên máy có mạng thật lúc lập bảng. Ghi ngày truy cập. (LAB105: agy từng ghi 10/17 link chết mà vẫn báo đạt.)
3. Lời trích phải có nguyên văn trong `bang-chung/`. Máy kiểm bắt câu trích ≥30 ký tự không có nguyên văn.
4. Người chấm **tự mở 5 số ngẫu nhiên** và ghi kết quả vào cuối bảng: `Kiểm ngẫu nhiên 5/5 khớp, người chấm X, ngày Y`. Máy chỉ biết số có xuất hiện trong kho, không biết lấy đúng ô hay không (LAB105 bắt lỗi đọc nhầm cột, sai mẫu số theo cách này).
5. Số nào "SAI, ĐÃ SỬA" thì sửa cả báo cáo gốc và ghi vào STATUS "điểm lại đợt trước".

## 3. bang-chung/INDEX.md

```
| Mã | Nguồn | Loại | Ngày | File nguyên văn | Ghi chú |
| BC-001 | Tổng cục Thống kê, điều tra giữa kỳ 2024 | số liệu chính thức | 06/01/2025 | tcvn-2024.md | trang 12, bảng 3 |
| BC-014 | Bình luận Facebook nhóm "Hội mê vàng" | lời khách | 12/04/2026 | fb-hoi-me-vang.md | đã ẩn tên |
```
Nguyên văn lưu thành file trong `bang-chung/` (kết quả Gemini Deep Research, bài crawler quét, ảnh chụp báo cáo).
