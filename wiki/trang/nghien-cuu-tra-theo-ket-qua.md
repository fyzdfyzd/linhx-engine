---
tieu_de: Thuê agent trả theo kết quả (LAB116)
loai: nghien-cuu
trang_thai: da-luu
cap_nhat: 2026-11-08
nguon: [/mnt/project-files/LAB116-THUE-AGENT-TRA-THEO-KET-QUA/KHAO-SAT.md]
---
# Thuê agent trả theo kết quả (LAB116)

Khảo sát sơ lược 8/11/2026. Bản đủ, nguồn và prototype tính giá: `/mnt/project-files/LAB116-THUE-AGENT-TRA-THEO-KET-QUA/` (KHAO-SAT.md, src/gia_ket_qua.py, test 3/3).

## Điều cần nhớ
- Thế giới: trả theo lượt giải quyết đã thành chuẩn ở chăm sóc khách hàng (Intercom $0,99, Zendesk $1,50–2,00, HubSpot $0,50, giá hãng công bố). Phổ biến nhất 2026 là giá lai: phí nền + theo kết quả.
- Sống được khi: "xong" được máy đếm, hai bên xem chung một sổ, giá khoảng 45% chi phí người làm và chi phí người gấp nhiều lần chi phí máy.
- Rủi ro chính: cãi nhau về định nghĩa "xong", biên mỏng khi giá model đổi, agent hỏng thì mình gánh, doanh thu khó dự báo.
- Việt Nam: chưa thấy ai bán agent theo kết quả công khai (nhận định sơ bộ). Cấm ăn % tiền đòi nợ (Luật Đầu tư 2020).
- Việc hợp nhất ở VN: dọn chứng từ/dữ liệu hộ KD (theo chứng từ), chăm khách Zalo (theo hội thoại xong), báo cáo định kỳ (theo bản giao), nội dung cho agency (theo tài sản được duyệt).

## Đề xuất cho engine (chưa chốt)
- Agent Force [[he-thong-linhx-agent-force]] h08: sau pilot 14 ngày đạt, thêm gói thuê theo việc = sàn + đơn giá × việc xong, có trần tháng. Phục vụ đích ≥50% doanh thu lặp lại.
- Một mảnh nhỏ dùng chung: sổ đếm việc xong (mã, loại, xong/chuyển người, chi phí máy, ai duyệt) khách xem được, đặt cùng báo cáo h22 và CRM h23.
