# State Preservation — Bảo Toàn Trạng Thái

## Nguyên Tắc Core
- **Write-as-you-go**: Lưu file vật lý **ngay sau khi hoàn thành** mỗi bước
- **Read-before-act**: Luôn **đọc `_status.json`** trước khi bắt đầu bất kỳ bước nào
- **No overwrite**: KHÔNG ghi đè file bước trước — dữ liệu là immutable sau khi hoàn thành

## Quy Trình Cập Nhật _status.json
Sau mỗi bước hoàn thành:
1. Thêm step number vào `steps_completed`
2. Tăng `current_step` lên bước tiếp theo
3. Cập nhật `last_updated`
4. Cập nhật `variants.X.status` nếu đang chạy variant (Bước 6+)

## 3-Variant Awareness
- Bước 1→5: files nằm ở **project root** → trạng thái chung
- Bước 6→9: files nằm trong **Variant_X/** → trạng thái per variant
- `_status.json` theo dõi trạng thái từng variant:
  ```json
  "variants": {
    "A": { "status": "completed", "critic_score": 9 },
    "B": { "status": "in_progress", "critic_score": null },
    "C": { "status": "pending", "critic_score": null }
  }
  ```
- `current_step = 10` (done) **CHỈ KHI** cả 3 variant + `_best_pick.md` hoàn thành

## Resume Logic
Khi mở lại project (conversation mới hoặc resume):
1. Đọc `_status.json` → xác định `current_step` + trạng thái variants
2. Verify file của bước trước tồn tại và hợp lệ
3. Nếu có `--variant X` → resume chỉ variant đó
4. Nếu không → resume variant đầu tiên chưa xong

## Backup
- Trước khi Critic Loop sửa draft: copy draft hiện tại vào folder Loop tương ứng
- KHÔNG bao giờ xóa draft cũ
