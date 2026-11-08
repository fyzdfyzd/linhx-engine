---
name: hoc-luat-bien-tap
description: Rút luật biên tập từ bản sửa thật của một biên tập viên (Vân Anh, Linh) - Word track changes hoặc cặp bản trước/sau - thành hồ sơ LUAT.md có bằng chứng, rồi kiểm luật bằng cách để plugin sửa lại chính các bài mẫu. Dùng khi có bài mẫu đã sửa mới trong mau-sua/.
---

# Học từ bản sửa

Đây là phần làm plugin giống một biên tập viên cụ thể chứ không giống "một biên tập viên chung". Cách làm theo ý của CIPHER (Gao et al. 2024): rút luật từ chỗ người thật sửa, mỗi luật phải có bằng chứng, và kiểm luật bằng cách sửa lại bài mẫu khác.

## Đầu vào
`${CLAUDE_PLUGIN_ROOT}/mau-sua/<ten-bien-tap-vien>-<ngay>-<ten-bai>/`, một trong hai dạng:
- `bai.docx` có Track Changes (và comment nếu có);
- `truoc.md` + `sau.md` (hoặc `.docx` không track changes).
Kèm `ghi-chu.md` nếu biên tập viên muốn giải thích (không bắt buộc). Cách gửi xem `mau-sua/HUONG-DAN-VAN-ANH.md`.

## Bước 1. Tách chỗ sửa (máy)
```
python ${CLAUDE_PLUGIN_ROOT}/scripts/doc_ban_sua.py docx mau-sua/<thu-muc>/bai.docx -o mau-sua/<thu-muc>/
python ${CLAUDE_PLUGIN_ROOT}/scripts/doc_ban_sua.py cap mau-sua/<thu-muc>/truoc.md mau-sua/<thu-muc>/sau.md -o mau-sua/<thu-muc>/
```
Ra `cac-cho-sua.md` và `.json`: từng chỗ sửa với câu trước, câu sau, kiểu (cắt, thêm, nối câu, tách câu, thay chữ, viết lại), chữ bỏ và chữ thêm. Chạy thêm `kiem_van.py kiem` trên `truoc.md` và `sau.md` để có số đo trước/sau (câu TB, câu dài, "tôi", gạch ngang, chữ số).

## Bước 2. Gán mã cho từng chỗ sửa (subagent)
Một subagent đọc `cac-cho-sua.md` và `references/ma-loi.md`, với mỗi chỗ sửa ghi: mã lỗi mà chỗ sửa ấy chữa (một hoặc hai mã), và một dòng "biên tập viên làm gì" bằng động từ cụ thể ("nối ba câu cụt thành một câu có 'và'", "bỏ tên nhà nghiên cứu, giữ ý", "thay số liệu bằng chi tiết đời thường"). Chỗ sửa không vào mã nào thì đặt mã tạm `MOI`.

## Bước 3. Rút luật (phiên điều phối)
Gom các dòng "làm gì" giống nhau. Một luật chỉ được ghi khi có **ít nhất hai bằng chứng ở hai chỗ khác nhau** (luật sổ chứng cứ của sổ tay giọng). Mỗi luật có đủ năm cột:

| Mã | Luật (một câu, mệnh lệnh) | Bằng chứng (≥2, trích trước → sau, kèm thư mục mẫu) | Kiểm | Mức |
|---|---|---|---|---|

- **Kiểm**: `máy: <regex hoặc ngưỡng>` nếu kiểm được bằng script, ngược lại `người đọc`.
- **Mức**: chặn / nặng / nhẹ, theo `references/ma-loi.md`.
- Luật trái với luật đã có: giữ cả hai, ghi "mâu thuẫn, hỏi tác giả". Không tự chọn.
- Luật chỉ có một bằng chứng: ghi vào mục "Ứng viên" ở cuối file, chờ mẫu sau.

Ghi vào `${CLAUDE_PLUGIN_ROOT}/ho-so-bien-tap/<ten>/LUAT.md` theo mẫu `ho-so-bien-tap/_mau/LUAT.md`. Cập nhật, không viết đè: luật cũ có thêm bằng chứng thì thêm vào cột bằng chứng.

Thêm số đo trước/sau vào `ho-so-bien-tap/<ten>/SO-DO.md` (mỗi bài mẫu một dòng), để biết biên tập viên này thường kéo câu dài ra hay ngắn lại, cắt bao nhiêu phần trăm chữ.

## Bước 4. Kiểm luật bằng bài chưa thấy
Giữ lại một bài mẫu không dùng ở bước 3. Cho plugin (`bien-tap-bai` với hồ sơ mới) biên tập bản `truoc.md` của bài ấy, rồi so phiếu biên tập với bản `sau.md` thật:
- Tỉ lệ chỗ sửa thật mà plugin bắt được (độ phủ).
- Tỉ lệ chỗ plugin bắt mà biên tập viên không sửa (bắt thừa).
Ghi vào `ho-so-bien-tap/<ten>/HIEU-CHUAN.md`. Độ phủ dưới 40% thì luật còn quá chung; bắt thừa trên 50% thì luật quá rộng.

## Bước 5. Báo
Một bảng ngắn cho người dùng: số bài mẫu, số chỗ sửa, số luật mới, số ứng viên, độ phủ và bắt thừa, và các luật mâu thuẫn cần tác giả quyết.
