# Design Tokens — Soi thương hiệu trong 10 phút (CSMO Topic 07)

## Hướng thị giác
**Tối giản trắng ngà biên tập (Editorial Ivory Keynote) + 1 màu nhấn đất nung tương phản cao.**
- Bối cảnh sử dụng: khán giả CMO / Brand Director quét mã QR từ màn LED hội trường trên điện thoại cá nhân (ưu tiên khổ dọc `360px`, đọc tốt dưới ánh sáng phòng hội nghị, hoàn thành trong 10 phút).
- Không dùng gradient tím mặc định, không bóng đổ dày, không dùng emoji làm biểu tượng điều hướng.

## Bảng màu (`:root`)
| Token | Giá trị | Vai trò & Tương phản WCAG 2.2 AA |
|---|---|---|
| `--color-bg` | `#FAF8F4` | Nền trang trắng ngà ấm |
| `--color-surface` | `#FFFFFF` | Bề mặt thẻ nội dung chính |
| `--color-surface-muted` | `#F2EFE9` | Nền khối công thức / hộp câu hỏi AI |
| `--color-text` | `#18181B` | Chữ chính mực than (tương phản > 15:1 trên nền) |
| `--color-text-muted` | `#4A4A52` | Chữ phụ, hướng dẫn (tương phản > 7.5:1 trên nền) |
| `--color-border` | `#DDD8CE` | Viền thẻ mảnh |
| `--color-border-strong` | `#B8B0A2` | Viền ô nhập liệu rõ nét (≥ 3:1 cho thành phần UI) |
| `--color-accent` | `#B83A1B` | 1 màu nhấn duy nhất (đỏ gạch ấm; chữ trắng `#FFFFFF` đạt 7.6:1) |
| `--color-accent-hover` | `#962E14` | Trạng thái chạm / rê chuột nút chính |
| `--color-accent-soft` | `#FDF2EE` | Nền nhấn nhẹ cho bước đang chọn / bước đang rơi |
| `--color-ok` / `--color-ok-bg` | `#166534` / `#ECFDF3` | Trạng thái Đạt / Đã lưu |
| `--color-warn` / `--color-warn-bg` | `#92400E` / `#FEF3C7` | Trạng thái Cảnh báo |
| `--color-err` / `--color-err-bg` | `#991B1B` / `#FEF2F2` | Trạng thái Lỗi nhập liệu / Bước rơi nghiêm trọng |

## Thang chữ & Khoảng cách
- Phông chữ: `'Be Vietnam Pro', 'Segoe UI', system-ui, -apple-system, Arial, sans-serif` (`font-display: swap`).
- Cỡ chữ (mọi chữ hiển thị trên `360px` đều `≥ 16px`):
  - `--font-sm`: `16px` (`1rem`) — nhãn phụ, ghi chú, huy hiệu
  - `--font-base`: `16px` (`1rem`) — chữ thân, ô nhập liệu, nút bấm
  - `--font-md`: `18px` (`1.125rem`) — câu hỏi AI, mục quan trọng
  - `--font-lg`: `20px` (`1.25rem`) — tiêu đề thẻ (`h3`)
  - `--font-xl`: `24px` (`1.5rem`) — tiêu đề bước (`h2`)
  - `--font-2xl`: `28px` (`1.75rem`, desktop `36px`) — tiêu đề trang (`h1`) và điểm số (`0–100`)
- Khoảng cách (bội số `4px`): `4px`, `8px`, `12px`, `16px`, `20px`, `24px`, `32px`.
- Vùng chạm tối thiểu: `44px × 44px` (`--touch-min: 44px`, nút chính `48px`).
