---
name: nghien-cuu-thi-truong
description: Viết báo cáo nghiên cứu thị trường truy được nguồn, ước tính quy mô TAM/SAM/SOM theo kịch bản, phân tích đối thủ, dự báo có độ nhạy. Dùng khi Linh hỏi quy mô thị trường, khả thi sản phẩm (PIVS, LINHX B2C), đối thủ, hoặc cần số liệu thị trường cho đề xuất hay hồ sơ.
---

# Nghiên cứu thị trường (bản LINHX)

Mượn từ skill `market-research-reports` của K-Dense Scientific Agent Skills (MIT, xem `goc/LICENSE-KDENSE.md`). Quy trình đầy đủ bằng tiếng Anh nằm ở `goc/SKILL-GOC.md`; tài liệu chi tiết ở `goc/references/`, mẫu ở `goc/assets/`. Script trong `goc/scripts/` chỉ dùng Python chuẩn, chạy offline và không ghi đè file có sẵn.

## Khác bản gốc

- Viết bằng tiếng Việt. Tiền tệ mặc định là **VND** (ghi rõ năm gốc, giá danh nghĩa hay thực); quy đổi USD chỉ khi so quốc tế, kèm tỷ giá và ngày.
- Nguồn Việt Nam ưu tiên: Tổng cục Thống kê (GSO), các Bộ (Bộ Công Thương, Bộ TT&TT), Ngân hàng Nhà nước, báo cáo ngành của hiệp hội, báo cáo công khai của doanh nghiệp niêm yết. Báo cáo của hãng nghiên cứu trả phí chỉ được dẫn đúng phần đã công bố công khai. Không bịa con số.
- Đầu ra mặc định là Markdown đặt trong folder lab hoặc dự án, không dùng LaTeX.

## Quy trình

1. **Hợp đồng nghiên cứu:** ghi rõ câu hỏi quyết định, ranh giới thị trường, địa lý, kỳ, đơn vị và mẫu số. Nếu thiếu thông tin, hỏi Linh một lần rồi chọn mặc định hợp lý.
2. **Dựng khung** bằng manifest mẫu (sửa từ `goc/assets/report_manifest_template.json`):
   `python "<skill>/goc/scripts/generate_report_scaffold.py" manifest.json <thư-mục-mới>`
3. **Sổ nguồn và sổ khẳng định:** mỗi con số đều có `source_id`. Kiểm bằng:
   - `python ".../validate_evidence_ledger.py" sources/source_ledger.csv`
   - `python ".../audit_claim_citations.py" data/claims_ledger.csv sources/source_ledger.csv`
4. **Quy mô theo kịch bản:** làm cả top-down và bottom-up, với vùng phủ không trùng nhau, rồi đối chiếu:
   `python ".../calculate_market_sizing.py" analysis/market_sizing.json`
5. **Dự báo có độ nhạy:** `python ".../forecast_sensitivity.py" analysis/forecast_sensitivity.json`
6. **Đối thủ:** dùng ma trận tính năng (`goc/assets/competitor_feature_matrix_template.csv`), kiểm bằng `validate_competitor_matrix.py`. Thông tin không rõ thì ghi `unknown`, không đoán.
7. **Cổng phát hành:** đi hết checklist "Release gate" trong `goc/SKILL-GOC.md`, sau đó chạy skill `xac-minh-truoc-khi-bao-xong` của linhx-core.

`<skill>` là thư mục chứa file này. Trong Claude Code, đường dẫn đó là `${CLAUDE_PLUGIN_ROOT}/skills/nghien-cuu-thi-truong`.

## Luật

- TAM/SAM/SOM và dự báo luôn là **kịch bản có điều kiện**, không phải một con số chắc chắn.
- Script hợp lệ chỉ chứng minh cấu trúc dữ liệu đúng. Nó không chứng minh nguồn ủng hộ khẳng định; điều đó vẫn phải đọc nguồn.
- Không mạo danh hãng tư vấn, không đưa lời khuyên đầu tư.
