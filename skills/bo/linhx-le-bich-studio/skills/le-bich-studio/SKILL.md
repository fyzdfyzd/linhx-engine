---
name: le-bich-studio
description: Nền tảng tạo nội dung và hoạt hình Lê Bích từ kho PSD/PNG chính chủ (4.000+ mảnh nhân vật, 15+ bộ trang phục thay được, đạo cụ, bóng thoại vẽ tay, hiệu ứng FX). Chạy lệnh CLI `python lebich.py` để tìm kho, dựng truyện 4 khung, sticker động GIF/WebP, hoặc clip dọc MP4 có tiếng Việt & khẩu hình.
---

# Skill: LÊ BÍCH STUDIO (`le-bich-studio`)

## 1. Luật Cứng Bắt Buộc
1. **Nhân vật và đạo cụ đã có trong kho thì tuyệt đối không vẽ lại bằng AI hoặc hình học cơ bản (`rectangle`/`ellipse`)**: Luôn gọi qua bộ dựng `lebich` lấy mảnh PNG thật tách từ PSD gốc (`Le_Bich.psd`, `Zai_a.psd`, `Gai_A.psd`, `Zai_X.psd`, `Gai_X.psd`, `Gau.psd`, `LE BICH OBJECTS.psd`, `LE BICH BUBBLE.psd`, `LE BICH FX.psd`).
2. **Asset mới (`nguon: ai-tao`) phải nằm ở `cho-duyet\`**: Chỉ khi trạng thái là `da-duyet` mới được đưa vào bộ dựng cảnh.
3. **Kho gốc `D:\LINHX\PRJ\LEBICH` chỉ đọc**: Mọi thao tác đọc/xuất file đều thực hiện tại `D:\LINHX\PRJ\LEBICH-STUDIO`.

## 2. Các lệnh CLI chính (`D:\LINHX\PRJ\LEBICH-STUDIO`)
```powershell
$env:PYTHONIOENCODING="utf-8"

# 1. Gõ 1 câu ý tưởng -> Ra trọn bộ Bài đăng (1 Truyện 4 khung PNG + 1 Sticker GIF/WebP + 1 Clip MP4 có tiếng)
python lebich.py tao-bai "Deadline dí sát nút nhưng vẫn bình tĩnh uống trà sữa"

# 2. Chạy từng khối kiến trúc K1..K7
python lebich.py thu          # K1: Kiểm kê kho gốc -> KHO.csv & KHO-TOM-TAT.md
python lebich.py phan-tich    # K2: Tách lớp PSD, cắt 50 ảnh phẳng, cập nhật kho.sqlite & xem-kho.html
python lebich.py chuan        # K3: Chuẩn hoá tỉ lệ, độ dày nét, xuất SVG song song
python lebich.py xuong        # K4: Xuất rig.json, spine.json, dragonbones_ske.json, 24 tư thế & dàn nhân vật
python lebich.py dien         # K5: Xuất 12 động tác chuẩn + GIF thử + khẩu hình tiếng Việt
python lebich.py canh         # K6: Kiểm schema, dựng 3 bài mẫu DE-GEMINI-SPARK + clip thử tủ đồ
python lebich.py tao          # K7: Sổ phong cách, hàng chờ duyệt 17 asset mới, sổ truyện & 5 truyện mới
```

## 3. Danh mục Trang phục thay được (`trang_phuc`)
- `goc` (Bụng phệ quần đùi trắng kinh điển)
- `cong_so`, `hiep_khach`, `do_boi`, `ao_rach`, `tay_to`, `handsome` (từ `01_Le_Bich/Le_Bich.psd`)
- `noel`, `phi_hanh_gia`, `tao_quan`, `bao_cong`, `thien_than`, `ac_quy`, `ao_mua`, `quy_toc` (từ `04.Art_soure/LÊ BÍCH GRAPHIC/0. CHARACTERS/2. MAIN CHARACTERS/Le Bich/`)

## 4. Danh mục 12 Động tác (`dong_tac`) & 6 Biểu cảm (`bieu_cam`)
- **Động tác**: `di_bo`, `chay`, `ngoi`, `vay_tay`, `chi_tay`, `vo_bung`, `giat_minh`, `run_ray`, `om_mat`, `cuoi_lan`, `tho_dai`, `nhay_mung`.
- **Biểu cảm**: `binh_thuong`, `ngac_nhien`, `chan_nan`, `buon_khoc`, `cuoi_hip_mat`, `phan_xet`.
