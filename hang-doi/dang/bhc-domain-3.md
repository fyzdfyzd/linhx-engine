May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 15
khong_tien_phut: 5
theo_doi: C:\linhx\ifagent-wt\bhc-domain
nhan: may-2 2026-11-19T13:06:53+0700
moc: fb0fd7769937daa4dd4394ecc048f3d44f515142

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Chỉ KIỂM (trừ lệnh caddy reload nêu dưới). Push KET-QUA + ảnh vào bang-chung/bhc-domain-3/ trên nhánh agy/bhc-domain-3.
Linh (13:05 VN 19/11): đã lưu bản ghi A brandcheck → 34.87.102.182 ở GoDaddy. Nếu DNS đã đúng mà Caddy chưa có chứng chỉ sau 3 phút, chạy `sudo docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile --force` (KHÔNG restart container) để Caddy thử lấy chứng chỉ lại.
1. nslookup brandcheck.ifagent.net 8.8.8.8 và 1.1.1.1: phải ra 34.87.102.182.
2. curl -sv https://brandcheck.ifagent.net/ : HTTP, nhà cấp chứng chỉ, ngày hết hạn. Nếu chứng chỉ chưa có: xem log caddy (sudo docker logs --since 30m <container caddy> | grep -i brandcheck | tail -30 qua gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026), ghi lý do; KHÔNG restart caddy.
3. Mở bằng trình duyệt thật 1280 + 360: trang chủ, báo cáo mẫu CSMO https://brandcheck.ifagent.net/bao-cao/2026-11-19-csmo-d88de79d/, /quan-tri/ (chỉ trang đăng nhập). Ghi danh sách yêu cầu lỗi ≥ 400 (phải rỗng). Chụp ảnh.
KET-QUA: dat, IP DNS, HTTP, chứng chỉ, lỗi, ảnh.
