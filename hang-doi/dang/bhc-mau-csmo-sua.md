May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 60
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-staging
nhan: may-2 2026-11-19T05:09:23+0700
moc: a54c0312f0288fd8a32e41aba619d56b1acacf83

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT; chạy E2E từng bước (--buoc). Push mỗi bước.
Bối cảnh: báo cáo mẫu CSMO 2026-11-18-csmo-51848e1b (nhánh agy/bhc-staging, bang-chung/bhc-mau-csmo/). Claude chấm: đẹp, nhưng có 3 lỗi phải sửa để thành bản final. KHÔNG gọi AI thật lần nào (dựng lại từ bao-cao-csmo.json + chi-tiet-luot-csmo.json sẵn có).
Nhánh mới agy/bhc-sua-5 từ agy/bhc-sua-4 (7b853da).
1. Ảnh chương landing chụp giữa lúc số đang chạy (06d-landing-chuong-02 hiện 39/37/28, đúng là 86/81/61). Sửa kịch bản chụp: trước mỗi ảnh chờ bộ đếm xong (đợi thuộc tính data-xong hoặc đọc chữ số bằng giá trị cuối, tối đa 5 s) hoặc tắt hiệu ứng khi chụp (prefers-reduced-motion). Thêm test khoá: ảnh/DOM chụp phải có đúng số cuối.
2. Hộp "Điều cần lưu ý nhất": hiện ngoặc lồng ngoặc kiểu AI nói lệch: "…" (Câu lạc bộ … (CSMO Việt Nam), …(VACD)). Sửa mẫu câu: tách thành 2 dòng rõ "AI nói: …" và "Sự thật: …", không lồng ngoặc; tên dài cắt gọn hợp lý. Thêm luật lint/test: chữ hiển thị không được có ngoặc lồng ngoặc.
3. "Ba việc" dùng ngành hàng như danh từ sản phẩm: "danh mục Cộng đồng giám đốc Sales & Marketing", "sản phẩm Cộng đồng giám đốc Sales & Marketing". Sửa mẫu câu: khi ngành hàng không phải hàng hoá (cộng đồng, dịch vụ, tổ chức) thì dùng "lĩnh vực …" / "hoạt động của <tên thương hiệu>", không dùng "danh mục"/"sản phẩm". Test khoá bằng dữ liệu CSMO và Vinamilk (Vinamilk vẫn giữ câu cũ).
4. npm test + node scripts/lint.js trong apps/brand-health phải xanh (≥115 test + test mới). Golden landing VNM/IFA không được đổi; nếu đổi phải nêu lý do trong KET-QUA.
5. Deploy staging stg-brand bản agy/bhc-sua-5 (gộp vào agy/bhc-staging như các lần trước, STG_SHA=<sha mới> docker compose -p stg-brand up -d --force-recreate; healthz đúng SHA). Mã quản trị đọc bằng `sudo cat /opt/stg-brand/ADMIN_CODE.txt` vào biến, không in. Dựng lại báo cáo CSMO cùng mã từ JSON (không quét lại), xuất bản.
6. Chụp lại vào bang-chung/bhc-mau-csmo-final/: 06d chương 01–13 ở 1280 (sáng) và 360 (sáng), landing full 1280/360 sáng+đêm, PDF Full + Light ra PNG 150 dpi. JPG 90 nếu tổng > 40 MB. Push agy/bhc-staging.
CẤM: deploy prod, sửa /opt/ifagent, stg-event, Caddy, rollback-app.sh, in khoá/mã quản trị, gọi AI thật. KET-QUA: dat, SHA, số test, danh sách ảnh, 3 câu trước/sau cho mục 2 và 3.

nhip: 05:42 33p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
