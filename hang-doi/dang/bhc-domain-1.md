May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-domain
nhan: may-2 2026-11-19T11:45:22+0700

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Push KET-QUA vào bang-chung/bhc-domain-1/ trên nhánh agy/bhc-domain-1 sau mỗi bước. KHÔNG in khoá/mã.
LINH YÊU CẦU (11:42 VN 19/11, nguyên văn "https://brandcheck.ifagent.net/ golive domain này cho tôi đi"): đưa Brand Health Check production lên tên miền riêng brandcheck.ifagent.net, phục vụ ở GỐC "/". Giữ nguyên đường cũ demo.ifagent.net/brand-health-check/ (QR bài nói đang trỏ vào đó).
DNS: Linh tự thêm bản ghi A brandcheck → 34.87.102.182 ở GoDaddy (có thể chưa có khi phiếu chạy; Caddy sẽ tự lấy chứng chỉ khi DNS có).
1. gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026. Sao lưu /opt/ifagent/infra/Caddyfile thành Caddyfile.bak-19-11 (cùng quyền). Ghi HTTP trước của demo.ifagent.net/, demo.ifagent.net/brand-health-check/, event.ifagent.net/, bd.ifagent.net/, lab.ifagent.net/.
2. Thêm khối mới NGAY SAU khối demo.ifagent.net, không sửa khối khác:
brandcheck.ifagent.net {
	import common
	reverse_proxy brand-health:3020
}
3. Kiểm cú pháp TRƯỚC khi nạp: `sudo docker compose exec -T caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile` (đọc compose.yaml để biết tên service caddy và đường dẫn Caddyfile trong container). Lỗi thì khôi phục .bak, DỪNG. Đạt thì `sudo docker compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile` (KHÔNG restart container caddy).
4. Kiểm sau: 5 địa chỉ ở bước 1 giữ đúng HTTP cũ. Nếu DNS brandcheck đã có (nslookup brandcheck.ifagent.net 8.8.8.8 ra 34.87.102.182): https://brandcheck.ifagent.net/ 200, chứng chỉ hợp lệ, mở bằng trình duyệt thật 1280 và 360: đủ CSS/logo, 0 yêu cầu 404, link báo cáo mẫu Vinamilk/IF Agent mở được, trang /quan-tri/ mở được. Chụp vào bang-chung/bhc-domain-1/. Nếu DNS chưa có: ghi "chờ DNS", vẫn đạt nếu reload thành công và 5 địa chỉ cũ nguyên.
5. Nếu app có biến BH_URL_GOC (đường dẫn gốc dùng cho link chia sẻ, mail, PDF): đặt BH_URL_GOC=https://brandcheck.ifagent.net trong /opt/ifagent/infra/brand-health.env (sao lưu trước), recreate CHỈ brand-health, healthz 200.
6. Cập nhật infra/Caddyfile trong repo ifagent giống bước 2, commit vào nhánh agy/bhc-domain-1.
Hỏng bất kỳ: khôi phục Caddyfile.bak-19-11 + reload, kiểm 5 địa chỉ cũ 200, ghi rõ.
CẤM: restart caddy/event/các service khác, sửa khối khác trong Caddyfile, sửa DNS, in khoá. KET-QUA: dat, đã đổi gì, HTTP trước/sau, trạng thái DNS + chứng chỉ, ảnh.

nhip: 11:48 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
