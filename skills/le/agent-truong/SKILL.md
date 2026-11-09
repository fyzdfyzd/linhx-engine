---
name: agent-truong
description: "Agent trưởng điều phối đội subagent nhỏ: chia việc lớn thành đầu việc hẹp, giao cho thợ (tho-tim-nguon, tho-doc-nguon, tho-kiem-chung, tho-viet) chạy song song, kiểm kết quả rồi tổng hợp. Dùng khi Linh nói \"agent trưởng\", \"chia việc cho subagent\", \"giao cho đội làm\", hoặc việc cần đọc nhiều nguồn, nhiều file cùng lúc (vd tra luật đầy đủ, rà nhiều tài liệu)."
metadata:
  version: "0.1.0"
---
# Agent trưởng

Claude ở phiên chính đóng vai **agent trưởng**: lập kế hoạch, giao việc, kiểm, tổng hợp. Thợ chỉ làm một việc hẹp và báo cáo lại. Thợ không gọi được thợ khác; chỉ agent trưởng giao việc.

## Đội thợ (`.claude/agents/`)
| Thợ | Làm | Model |
|---|---|---|
| `tho-tim-nguon` | Tìm link cho một câu hỏi hẹp | haiku |
| `tho-doc-nguon` | Đọc 1–3 link, rút dữ kiện có bằng chứng | sonnet |
| `tho-kiem-chung` | Soi bản nháp, chấm Đạt / Sai / Chưa kiểm được | sonnet |
| `tho-viet` | Viết ghi chú từ dữ kiện đã kiểm | sonnet |

Cần thợ kiểu khác (vd đọc file Excel, rà hợp đồng) thì dùng agent `general-purpose` hoặc `Explore` với đề rõ, hoặc thêm thợ mới vào `_system/agents/`.

## Quy trình
1. **Hiểu việc.** Ghi một câu: Linh cần gì, ai đọc, nộp ở đâu, hạn khi nào. Có skill hợp (vd `tra-cuu-luat`) thì đọc skill đó để lấy khung và bản nền.
2. **Lập kế hoạch.** Ghi `KE-HOACH.md` trong thư mục việc (hoặc in vào chat nếu việc nhỏ):
   ```
   | # | Đầu việc | Thợ | Đầu vào | Đầu ra mong đợi | Phụ thuộc |
   ```
   Luật chia việc:
   - Mỗi đầu việc **một câu hỏi**, làm xong trong vài phút.
   - Đầu việc không phụ thuộc nhau thì chạy **song song** (nhiều lệnh Agent trong một lượt). Tối đa 6 thợ một lượt.
   - Việc chỉ vài lệnh tra là xong thì agent trưởng tự làm, không giao.
3. **Viết đề cho thợ.** Thợ chỉ biết những gì có trong đề. Mỗi đề có:
   - Mục tiêu một câu, mốc thời gian, phạm vi.
   - Đầu vào cụ thể (link, đường dẫn file, danh sách điều cần rút).
   - Điều đã biết, để thợ khỏi làm lại (vd "bản nền ngày 03/11/2026 đã có NQ 254, chỉ tìm cái mới hơn").
   - Khung trả về (theo file của thợ).
4. **Chạy vòng 1: tìm.** Giao song song `tho-tim-nguon`, mỗi thợ một mảng (vd luật và nghị quyết; nghị định, thông tư; dự thảo đang bàn; tin tháng này).
5. **Chạy vòng 2: đọc.** Gộp link, bỏ trùng, chọn nguồn tốt nhất. Chia link cho `tho-doc-nguon`, mỗi thợ 1–3 link.
   - Trang thợ báo "KHÔNG MỞ ĐƯỢC" (Cloudflare, cần đăng nhập): agent trưởng tự mở bằng Chrome của Linh theo mẹo trong `tra-cuu-luat`. Chrome chỉ một mình agent trưởng dùng, không giao thợ, để tránh tranh tab.
6. **Gộp và kiểm.** Agent trưởng gộp dữ kiện, xử lý mâu thuẫn giữa nguồn. Rồi giao `tho-viet` viết nháp, giao `tho-kiem-chung` soi nháp.
7. **Sửa và chốt.** Sửa mọi mục "Sai". Mục "Chưa kiểm được" thì hoặc tự kiểm, hoặc ghi rõ trong phần "Độ tin cậy". Không gửi Linh bản còn lỗi đã biết.
8. **Báo Linh.** Trả lời ngắn: kết quả, link file, những gì chưa chắc. Ghi vào `KE-HOACH.md` mục "Kết quả": thợ nào làm gì, mấy vòng, lỗi đã bắt.

## Luật của agent trưởng
- **Chỉ dùng tài liệu được giao.** Khi Linh đính kèm tài liệu, mọi câu trả lời chỉ lấy từ tài liệu đó. Điều gì tài liệu không có thì ghi đúng `[CHƯA ĐỦ DỮ LIỆU]`, không suy diễn, không bù bằng hiểu biết sẵn có. Khi việc là tra web, "tài liệu" là các nguồn thợ đã đọc. Ghi luật này vào đề của mọi thợ.
- Không tin báo cáo của thợ chỉ vì nó tự tin. Số hiệu, ngày quan trọng phải có nguồn hoặc qua thợ kiểm chứng.
- Không giao giả thuyết của mình cho thợ kiểm chứng (đưa nháp, không đưa kết luận "đã đúng").
- Mọi đầu ra online phải có bản trong thư mục dự án trên `D:\LINHX`.
- Tốn token theo số thợ: chỉ chạy đội khi việc thật sự rộng. Việc nhỏ thì tự làm.

## Ví dụ: "cập nhật luật đất đai đầy đủ"
| # | Đầu việc | Thợ | Phụ thuộc |
|---|---|---|---|
| 1 | Luật, nghị quyết QH mới sau bản nền | tho-tim-nguon | — |
| 2 | Nghị định, thông tư đất đai mới | tho-tim-nguon | — |
| 3 | Tiến trình Luật Đất đai (sửa đổi) tháng này | tho-tim-nguon | — |
| 4 | Bảng giá đất, hệ số 2027 Hà Nội, TP.HCM | tho-tim-nguon | — |
| 5–8 | Đọc link từ 1–4 | tho-doc-nguon ×4 | 1–4 |
| 9 | Viết ghi chú theo khung `tra-cuu-luat` | tho-viet | 5–8 |
| 10 | Soi bản nháp | tho-kiem-chung | 9 |
