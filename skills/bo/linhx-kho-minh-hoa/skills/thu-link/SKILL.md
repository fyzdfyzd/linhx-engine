---
name: thu-link
description: Thu metadata và link (không tải ảnh) từ bộ sưu tập Instagram KHO-Y-TUONG của Linh, Pinterest board, Behance, Bluesky hoặc link Linh dán, ghi vào kho minh hoạ ý tưởng.
---
# Thu link vào kho

Chạy trên máy Linh (container cloud bị chặn các trang này). Trước tiên đọc skill `so-nguon`: chỉ thu nguồn `allowed: true`.

## Instagram (nguồn chính)
1. Linh lướt Instagram như bình thường, thấy hình hay thì bấm Lưu → bộ sưu tập **KHO-Y-TUONG**.
2. Mở bộ sưu tập trên Chrome máy tính, chép URL dạng `https://www.instagram.com/<ten>/saved/kho-y-tuong/<so>/`.
3. Chạy: `python scripts/thu_link.py url "<URL>" --cookies chrome`
   - Dùng cookie Chrome đã đăng nhập, không hỏi mật khẩu. `--sleep 6` mặc định; không chạy quá 1 lần/ngày.
4. Ngay sau đó chạy skill `loc` (link ảnh Instagram hết hạn sau vài giờ đến vài ngày).

## Nguồn khác
- Pinterest: `python scripts/thu_link.py url "https://www.pinterest.com/<ten>/<board>/"`
- Link dán: thêm vào `KHO/nguon/dan-tay.txt` (mỗi dòng một link), chạy `python scripts/thu_link.py dan "%KHO_MINH_HOA%\nguon\dan-tay.txt"`. Với link dán, Claude mở link trong Chrome để lấy tác giả và chú thích khi phân loại.

## Đầu ra
`KHO/nguon/records.jsonl`, mỗi dòng: id, link_goc, tac_gia, nguon, chu_thich_goc, hashtag, tuong_tac, ngay_dang, anh_tam_url (chỉ dùng tạm), co_noai, ngay_quet. Bản ghi trùng id được bỏ qua nên chạy lại an toàn.
