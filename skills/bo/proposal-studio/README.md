# proposal-studio

Plugin viết proposal hoạt động/sự kiện từ brief, theo cách làm asset cho Live Character: mọi thứ nằm trong một thư mục, dữ liệu tách khỏi hình, build lại được.

## Đầu vào → đầu ra
Brief → phân tích brief → nghiên cứu công nghệ event thế giới → ý tưởng (có dùng IFAGENT) → chấm điểm → cách hoạt động → tiến trình chơi → từng màn hình (mockup PNG) → minh hoạ kỹ thuật, mặt bằng, thiết bị → vận hành, KPI, tiến độ, ngân sách 3 gói, rủi ro, pháp lý → prompt ảnh ChatGPT Plus / Google Flow → deck PPTX.

## Skills
| Skill | Khi nào |
|---|---|
| proposal-studio | Làm trọn gói proposal từ brief, hoặc build lại |
| proposal-brief | Chỉ phân tích brief, liệt kê điểm thiếu |
| proposal-ideas | Nghiên cứu + đề xuất ý tưởng trước khi làm proposal |
| proposal-images | Viết prompt ảnh, thay ảnh, build lại deck |

## Thay thế nội dung
- Chữ: sửa `proposal.json` → build lại.
- Ảnh: lưu ảnh mới vào `images/` đúng tên (vd. `kv_hero.jpg`) → build lại. Ảnh mới nhất theo tên sẽ được dùng.
- Đổi khách hàng: copy thư mục, đổi `theme`, `meta`, nội dung, ảnh.

## Chạy tay (không cần Claude)
```
pip install python-pptx pillow playwright && playwright install chromium
python skills/proposal-studio/scripts/render_mockups.py <thư_mục_dự_án>
python skills/proposal-studio/scripts/build_deck.py <thư_mục_dự_án>
```
Ví dụ đầy đủ: `skills/proposal-studio/examples/jollibee-2026/`.
