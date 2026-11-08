---
name: cham-tung-cau
description: Lượt biên tập 4, hai giám khảo tách ngữ cảnh chấm từng câu một nhãn GIỮ, ỔN, SỬA, CẮT có mã lỗi; gộp bằng script và so ngưỡng giao bài. Dùng trong bien-tap-bai hoặc khi cần chấm khắt khe từng câu.
---

# Chấm từng câu (lượt 4)

## Trước khi chấm
- Giám khảo phải qua hiệu chuẩn (`hieu-chuan`) ít nhất một lần cho mỗi mô hình và mỗi hồ sơ biên tập viên. Kết quả hiệu chuẩn mới nhất ghi ở `ho-so-bien-tap/<ten>/HIEU-CHUAN.md`.
- Bài đã qua lượt 0 (máy) và đã sửa hết lỗi chặn ở lượt 1.

## Cách làm
1. Tách câu: `python ${CLAUDE_PLUGIN_ROOT}/scripts/cham_cau.py bai.md --xuat-cau cau.txt` (bỏ bảng, tiêu đề, dòng nguồn; bỏ mã nguồn trong câu).
2. Hai subagent mới, cùng hướng dẫn `references/giam-khao-tung-cau.md`, cùng hai bài mẫu giọng toàn văn (`${CLAUDE_PLUGIN_ROOT}/references/bai-mau/`, chọn hai bài cùng thể loại với bài đang chấm), **đọc bài mẫu theo thứ tự ngược nhau**. Nếu hồ sơ biên tập viên có `LUAT.md`, đưa thêm vào hướng dẫn như "luật của toà soạn".
3. Mỗi giám khảo ghi một bảng vào `bt-4-giam-khao-1.md`, `bt-4-giam-khao-2.md`.
4. Gộp: `python ${CLAUDE_PLUGIN_ROOT}/scripts/tong_hop_cham.py bt-4-giam-khao-1.md bt-4-giam-khao-2.md -o bt-4-tong-hop.md`.

## Ngưỡng giao bài (hiệu chuẩn 19/10/2026)
- GIỮ trung bình ≥ 25% số câu. Bài Linh tự sửa được chấm 26–37% GIỮ; bản máy 2–8%.
- CẮT = 0; SỬA ≤ 10% số câu.
- Mỗi đoạn từ hai câu trở lên có ít nhất một câu GIỮ (đoạn nào cũng phải có một câu chỉ tác giả này viết được).
- Câu lệch từ hai bậc: không tự quyết, đưa tác giả.

## Sửa theo kết quả
- Câu SỬA: dùng câu sửa của giám khảo làm gợi ý, người viết sửa lại bằng giọng mình; không dán nguyên câu giám khảo nếu nó làm câu ngắn lại kiểu máy.
- Đoạn thiếu câu GIỮ: thêm một chi tiết vật chất Việt, một cú lật chữ hoặc một câu tự giễu vào câu sẵn có, không thêm câu mới chỉ để có câu GIỮ.
- Sau mỗi vòng, giám khảo mới (ngữ cảnh mới) chấm lại; tối đa ba vòng.
