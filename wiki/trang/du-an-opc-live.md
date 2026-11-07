---
tieu_de: OPC Live (bảng thợ thời gian thực)
loai: du-an
trang_thai: dang-chay
cap_nhat: 2026-11-08
nguon: [https://claude.ai/artifact/SbxLz9BfZiHmaRF11S8V4h]
---
# OPC Live

**Một câu:** server mỏng trên máy cty cho xem thợ agy và Claude đang làm gì, RAM, log, phòng làm việc ảo; sẽ được Bàn điều hành của engine thay.

## Hiện trạng
- Code `opc-live/` trên main repo chiemtinhso (PR #1, #2 đã merge). Máy cty `D:\LINHX\LINHX-OPC\OPC-LIVE-SRC`, cổng 4900, cloudflared quick tunnel; địa chỉ đổi mỗi lần khởi động, đọc ở `opc-live\var\dia-chi.txt`.
- Tab: Hôm nay, Phòng, Trao đổi, Kiểm thử, Bài học, Việc (Gantt).

## Gộp vào engine
Khi E1, E2, W1 DAT thì Bàn `/#/engine` thay OPC Live. Xem [[hop-nhat]].

## Liên quan
[[hop-nhat]] [[loi-engine]]
