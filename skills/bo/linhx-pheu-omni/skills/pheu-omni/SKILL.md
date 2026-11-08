---
name: pheu-omni
description: Lập kế hoạch marketing đa phễu may đo cho một biz bất kỳ (ads, SEO, content hub, personal brand, affiliate, cold reach, offline, search, community, group), giả lập, phản biện và tính 1 đồng marketing thu về bao nhiêu. Dùng khi Linh hoặc owner nói lập phễu, growth plan, ROI marketing, lùa khách.
---

# Phễu omni: từ hồ sơ biz đến "1 đồng vào, bao nhiêu ra"

Đầu ra cuối cùng là 1 file `<biz>-roi.md` + `<biz>-roi.xlsx` cho owner và 1 trang kế hoạch phễu. Không đăng, không gửi, không tiêu tiền thay owner: mọi hành động ra ngoài (đăng bài, nhắn tin, bật quảng cáo) chỉ được soạn sẵn để người bấm.

Thư mục làm việc: `phieu/<ten-biz>/`. Mỗi bước ghi một file, bước sau đọc file bước trước.

## Bước 1. Hồ sơ biz (`01-ho-so.md`), hỏi tối đa 8 câu
Bán gì, cho ai, giá trị đơn (AOV), biên lãi gộp, khách mua lại mấy lần/năm, từ lúc quan tâm đến lúc trả tiền mất bao lâu, mỗi tháng phục vụ tối đa bao nhiêu khách mới (trần năng lực), hiện khách đến từ đâu. Thiếu số thì ghi `[giả định]` và đi tiếp.

## Bước 2. Thấu hiểu khách (`02-khach.md`)
Dùng Jobs-to-be-done: khách "thuê" sản phẩm để làm việc gì, lực đẩy (đau hiện tại), lực kéo (điều mong), lo lắng, thói quen giữ chân (4 lực). Chia 2-4 nhóm theo việc cần làm, không theo tuổi. Nguồn: 5-10 cuộc gọi khách cũ (ưu tiên), bình luận đối thủ, social listening (LAB053), persona ảo LAB048 chỉ để tạo giả thuyết, không thay khách thật. Ghi rõ câu nào từ khách thật, câu nào là đoán.

## Bước 3. Bản đồ điểm chạm (`03-diem-cham.md`)
Bảng: nhóm khách × chặng (Biết → Quan tâm → Cân nhắc → Mua → Dùng → Quay lại → Giới thiệu) × kênh. Mỗi ô: khách hỏi gì lúc đó, ta nói gì, bằng định dạng nào, đo bằng chỉ số nào, và **bước kế tiếp mời khách làm gì** (một CTA duy nhất). Ô nào trống là lỗ rò.

## Bước 4. Chọn phễu (`04-chon-pheu.md`)
Đi qua 10 phễu trong `data/pheu.json`. Bật/tắt từng phễu có lý do một dòng (pháp lý, khớp khách, năng lực owner). Quy tắc: biz mới chỉ bật 3-4 phễu, gồm ít nhất 1 phễu ra tiền nhanh (ads/search/affiliate/group) và 1 phễu tài sản dài hạn (SEO/content hub/community/personal brand).

## Bước 5. Luồng lùa khách (`05-luong.md`)
Vẽ luồng: mọi phễu đều đổ về **một nơi giữ khách** (Zalo OA/danh sách email/cộng đồng) có hồ sơ khách và cột "nguồn". Mỗi luồng ghi: điểm vào → lời mời → nơi giữ → chuỗi nuôi (tin 1, 2, 3) → điểm chốt → sau bán (mua lại, giới thiệu). Liệt kê các đường đi chéo hay gặp (vd thấy ads → xem trang owner → vào group → hỏi bạn → đặt).

## Bước 6. Giả lập số (`bizs/<biz>.json` → `scripts/roi.py`)
Chép một mẫu trong `bizs/`, sửa theo bước 1 và 4, chạy:
```
python -I scripts/roi.py bizs/<biz>.json --ra phieu/<ten-biz>
```
Máy chạy 2000 lần với bộ ba [thấp, hay gặp, cao] mỗi tham số, có hệ số chung của biz (offer dở thì mọi phễu dở), có trần năng lực, có bão hoà ngân sách. Đọc 4 số: doanh thu/1đ, lãi gộp/1đ, xác suất lỗ, tháng hoàn vốn; và ROI biên của phễu trả tiền.

## Bước 7. Phản biện từng luồng (`07-phan-bien.md`)
Với mỗi phễu đã bật, trả lời 6 câu, không được bỏ câu nào:
1. Giả định nào, nếu sai một nửa, làm phễu lỗ? (chạy lại roi.py với số đó)
2. Đơn này có xảy ra kể cả khi không làm phễu không? (tăng thực)
3. Phễu đụng luật nào: Luật Bảo vệ dữ liệu cá nhân (hiệu lực 1/1/2026), NĐ 91/2020 chống tin nhắn/cuộc gọi rác, quy định quảng cáo ngành (mỹ phẩm, y tế, tài chính), thuế hoa hồng affiliate.
4. Nền tảng có thể khoá tài khoản/nhóm không, mất bao lâu dựng lại?
5. Agent làm được phần nào, phần nào bắt buộc người (chạm quan hệ, chốt deal, duyệt nội dung)?
6. Persona phản biện: chạy 6-10 persona LAB048 đóng vai khách đi qua luồng, mỗi persona nói điểm nào nó bỏ đi và vì sao. Ghi lại các điểm bỏ đi lặp từ 3 persona trở lên.
Sửa `bizs/<biz>.json` theo phản biện, chạy lại bước 6, ghi chênh lệch.

## Bước 8. Gói cho owner (`08-ke-hoach.md` + file xlsx)
Một trang: mix phễu, ngân sách tháng, chi phí planning một lần, 1đ vào thu về bao nhiêu (P10 · P50 · P90), tháng hoàn vốn, 3 chỉ số theo dõi tuần, mốc kiểm lại ở tuần 4 và tuần 8. Sheet "May tinh nhanh" để owner thay số đơn thật vào.

## Vòng đo lại (sau khi chạy thật)
Mỗi tuần: đếm đơn theo cột nguồn trong sổ khách + câu hỏi "anh/chị biết đến bên em qua đâu". Tuần 4 và 8: thay bộ ba giả định bằng số thật, chạy lại roi.py, dồn tiền từ phễu có ROI biên thấp sang phễu ROI biên cao. Có ngân sách lớn và trên 1 năm dữ liệu tuần thì mới cân nhắc MMM (Meridian, Robyn); nhỏ hơn thì thử tắt/bật từng phễu theo khu vực hoặc theo tuần.
