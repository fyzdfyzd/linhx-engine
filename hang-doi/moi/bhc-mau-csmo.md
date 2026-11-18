may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 60
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-staging

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT (lượt quét chạy trên máy chủ, máy chỉ gọi API khởi động rồi kiểm trạng thái bằng lệnh ngắn, mỗi lần kiểm cách nhau ≤ 60 giây bằng một lệnh `Start-Sleep 50; curl ...`). Push mỗi bước.
Linh yêu cầu (04:02 VN 19/11): quét THẬT thương hiệu CSMO trên staging stg-brand thành BÁO CÁO MẪU FINAL, chụp đủ màn hình. Được phép gọi AI thật đúng 1 lượt đầy đủ (6 làn) cho CSMO; tối đa 1 lần chạy lại nếu lỗi mạng. Trần chi tiêu OpenRouter cho phiếu này: 6 USD (kiểm GET https://openrouter.ai/api/v1/key usage trước/sau, chỉ in usage).
0. Staging: gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026; đường hầm 3920. healthz phải là ef3616e. Mã quản trị: `sudo cat /opt/stg-brand/ADMIN_CODE.txt` vào biến, không in.
1. Sự thật gốc CSMO: mở trang chính thức (tìm "CSMO Vietnam Câu lạc bộ Giám đốc Sales & Marketing Việt Nam", trang csmo.vn hoặc trang chính thức tìm được; sự kiện VSMCamp & CSMO Summit, vsmcamp.com). Điền 4–6 dòng sự thật CHỈ từ trang chính thức (tên tổ chức, năm thành lập, hoạt động chính, sự kiện thường niên, trụ sở/website); ghi nguồn URL từng dòng vào bang-chung/bhc-mau-csmo/su-that.md. Dòng nào không chắc thì bỏ. Ngành hàng: "Cộng đồng giám đốc Sales & Marketing". Không tự bịa.
2. Cấu hình tạm: trong /opt/stg-brand/stg-brand.env (root 600) đặt BH_QUICK=0 và trần chi phí ngày đủ cho 1 lượt đầy đủ (BH_TRAN_CHI_PHI_NGAY=300000), recreate chỉ container stg-brand (STG_SHA=ef3616e docker compose -p stg-brand up -d --force-recreate). Ghi lại giá trị cũ để trả về ở bước 6.
3. Quét CSMO qua giao diện thật (trang chủ → bảng sự thật → quét), như khách. Theo dõi đến xong. Sau đó vào quản trị: xuất bản báo cáo công khai. Không sửa điểm bằng tay.
4. Chụp FULL PAGE 1280 và 360 (sáng; thêm đêm cho trang chủ và landing): trang chủ, bảng sự thật, màn đang quét (chụp lúc đang chạy), màn kết quả, landing /bao-cao/<mã>/ (cả trang + từng chương nếu trang quá dài: cắt thành ảnh 1280×2000), ngăn "Xem nguyên văn" mở, form để lại email, quản trị: tổng quan, lượt quét, chi tiết lượt CSMO (chi phí từng làn), lead. Tải PDF Full + Light, xuất từng trang PDF ra PNG (150 dpi). Tất cả vào bang-chung/bhc-mau-csmo/ (anh/, pdf/, man-hinh-1280/, man-hinh-360/) + file JSON báo cáo. Ghi mã báo cáo, thời gian quét, chi phí thật từng làn (đ) và USD trước/sau vào KET-QUA.
5. Push agy/bhc-staging (chỉ bang-chung/bhc-mau-csmo/). Nếu tổng ảnh > 40 MB thì nén PNG 360/1280 sang JPG 90.
6. Trả cấu hình: BH_QUICK và BH_TRAN_CHI_PHI_NGAY về giá trị cũ, recreate stg-brand, healthz ok. Prod demo.ifagent.net/brand-health-check/ và event.ifagent.net phải 200.
CẤM: deploy prod, sửa /opt/ifagent, stg-event, Caddy, rollback-app.sh, in khoá/mã quản trị, quét thương hiệu khác. KET-QUA: dat, mã báo cáo, 3 chỉ số, thời gian, chi phí, danh sách ảnh.
