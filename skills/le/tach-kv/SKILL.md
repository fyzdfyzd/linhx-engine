---
name: tach-kv
description: Phân rã một key visual (KV) phẳng JPG/PNG thành các element độc lập (chữ, logo, ảnh, QR, nền) dạng PNG trong suốt + kv.json vị trí + PSD + SVG, để dùng lại cho ấn phẩm truyền thông. Dùng khi Linh nói tách KV, phân rã KV, bóc layer, lấy logo/chữ từ ảnh.
---

# Tách KV thành element (LAB078)

Cần: `pip install rapidocr_onnxruntime opencv-python-headless pillow psd-tools`. Chạy CPU, khoảng 1 phút cho ảnh 3333 px.

## 4 bước

1. **Đọc**: `python scripts/tach_kv.py doc KV.jpg ra/` → `ra/ocr.json` (hộp chữ) + `ra/ocr-xem.jpg` (đánh số).
2. **Claude soạn bản phân rã** `phan-ra.json` (mẫu: `vi-du-phan-ra.json`). Claude nhìn ảnh + ocr.json rồi ghi từng phần tử:
   - `id` (kebab, tiếng Việt không dấu), `loai`: chu | logo | qr | anh | khoi, `z` (thứ tự chồng lớp).
   - Vùng: `hop` [x0,y0,x1,y1] hoặc `da_giac` [[x,y],...] theo px ảnh gốc. Mẹo lấy toạ độ: kẻ lưới 100 px lên ảnh rồi đọc.
   - `tach`: `mau_don` (chữ/logo một màu, mặc định cho chu/logo), `da_mau` (logo nhiều màu trên nền phẳng), `cat` (ảnh, QR: cắt cứng).
   - `mau` "#ffffff" nếu biết màu chữ (bỏ trống thì tự đoán), `noi_dung` chữ CÓ DẤU (OCR mất dấu, Claude tự sửa).
   - `lan` độ loang quanh nét khi xoá khỏi nền (mặc định 21; chữ to có bóng/glow để 41).
   - Ảnh (`loai: anh`) mặc định KHÔNG xoá khỏi nền, layer ảnh lấy từ nền đã xoá chữ.
3. **Tách**: `python scripts/tach_kv.py tach phan-ra.json ra/` → `layers/NN-id.png`, `nen.png`, `kv.json` (x, y, w, h, z, nội dung, màu), `kv.psd`, `kv.svg`, `xem.html` (bật tắt từng lớp), `ghep-lai.jpg` + sai số ghép lại.
4. **Soát**: xem `nen.png` chỗ từng có chữ. Vết loang thì tăng `lan` hoặc sửa hộp; chữ đè lên ảnh thì nền chỗ đó sẽ mờ (xem Giới hạn).

## Giới hạn và đường nâng cấp
- Nền chỗ chữ đè lên ẢNH chỉ lấp mờ (thuật toán lấp không tự vẽ lại ảnh). Muốn sạch: đưa `nen.png` + mặt nạ cho Gemini (Nano Banana) "xoá vết, vẽ tiếp ảnh" hoặc chạy LaMa trên máy Linh.
- Không vector hoá: logo/chữ là PNG. Cần SVG thật cho logo thì lấy file gốc từ brand guideline (LAB043) hoặc vtracer.
- Toạ độ đa giác ảnh do Claude ước lượng, lệch vài px.
- Hướng tự động hoá hoàn toàn: LayerD (CyberAgent, ICCV 2025, tách lớp thiết kế đồ hoạ) hoặc Qwen-Image-Layered; cần GPU + tải trọng số HuggingFace.
