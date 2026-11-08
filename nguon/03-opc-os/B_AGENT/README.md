# Phương án B · Agent Điều Phối (`03_OPC_OS/B_AGENT/`)

## 1. Nguyên tắc Kiến trúc & Luật An toàn
- **Luật an toàn sắt (`03_OPC_OS.md` & `QUY-CHUAN-OPC.md` 6.2)**:
  - Phần tiền (Module 03 tạo đơn, xác thực webhook, đối soát chống trùng & Module 07 ghi sổ S1a-HKD, báo đỏ 400 triệu) **luôn chạy bằng code cố định 100%**.
  - Agent điều phối **chỉ được đọc sự kiện `don.da_tra`** (sau khi tiền đã được Module 03 xác thực) hoặc sự kiện `khach.hoi`.
  - Agent **tuyệt đối không được** tự chi tiền, đổi giá, tự hoàn tiền, tạo mã giảm giá, đăng nội dung công khai hay xoá dữ liệu.
- **Cách Agent hoạt động**:
  - Khi nhận sự kiện `don.da_tra` hoặc `khach.hoi`, Agent tự lập kế hoạch (`AgentPlanner`), chọn module và tool phù hợp trong `tool_registry` (`inspect_input`, `normalize_edge_birth_time`, `run_domain_compute_and_compose`, `run_anti_slop_gate`, `export_pdf_and_deliver`, `answer_deep_report_question`, `escalate_refund_to_founder`), và ghi toàn bộ nhật ký suy luận vào `agent_trace.jsonl`.

## 2. Cách chạy
```powershell
D:\LINHX\LINHX-OPC\OPC001-CHIEMTINH-VN\src\astro-engine\.venv\Scripts\python.exe B_AGENT/chay_b.py
```
