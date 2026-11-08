---
name: tao-bai
description: Viết bài cho người ảo từ ghi chú tiêu hoá, theo persona, phong cách chung và luật viết; sinh nhiều ứng viên, tự chấm, đưa vào hàng duyệt. Dùng cho bước tao.
---

# Tạo bài

Gọi CLI là `python "${CLAUDE_PLUGIN_ROOT}/scripts/kenhao.py" --home <kênh>`.

1. Đọc `ho-so/nhan-vat.md`, `ho-so/phong-cach.md`, toàn bộ `ho-so/luat-viet.md`, 5 ghi chú tiêu hoá mới nhất (`doc-ds` + bảng tiêu hoá trong RETRO).
2. Chọn khe trống trong tuần (`ke-hoach` đã tạo khe theo trụ cột và giờ). Viết 3 ứng viên, mỗi cái một `hook` (`cau_hoi`, `khang_dinh`, `canh_cu_the`, …). Mỗi ứng viên nêu rõ: mục đích, cho ai, mọc từ ghi chú tiêu hoá nào, cảm xúc và phản ứng nhắm tới.
3. Chấm từng ứng viên theo rubric 10 điểm: đúng giọng và flaw (3), mọc từ cái đã đọc chứ không chung chung (2), giá trị cho người đọc (2), mở bài bằng cảnh cụ thể (1), không câu like, không bịa số (1), đúng phong cách nhà (1). Giữ ứng viên cao nhất; dưới 7 thì viết lại tối đa 2 lần.
4. `bai-them --khe ID --noi-dung "..." --hook ... --muc-dich ... --cho-ai ... --tu-tieu-hoa 3,4 --cam-xuc ... --phan-ung ...`, rồi `bai-cham --id --diem --ghi-chu`.
5. Ảnh và video: gọi xưởng ảnh (LoRA nhân vật + Qwen-Image-Edit qua ComfyUI) hoặc MoneyPrinterTurbo; ghi đường dẫn vào `--media`.

Nhãn AI (`nhan_ai` trong hồ sơ) phải có trong bài, trừ nền tảng có adapter tự bật nhãn.
