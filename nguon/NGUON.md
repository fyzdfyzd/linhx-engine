# Sổ ghi nguồn gốc (`nguon/`)

Thư mục `nguon/` lưu bản chép tĩnh của các prototype gốc để đối chiếu và chuyển logic sang `apps/linhx_core/`.
**Quy tắc**: Chỉ đọc, không chạy trực tiếp, code trong `apps/` tuyệt đối không `import nguon`.

| Thư mục trong repo | Đường dẫn gốc trên máy công ty | Ngày chép | Ghi chú |
|---|---|---|---|
| `nguon/03-opc-os` | `D:\LINHX\PROTO\03_OPC_OS` | `2026-11-08` | Gồm `README.md`, `core/`, 10 module `modules/01..10/module.py`, `opcs/`, `scripts/`, `A_CODE/`, `B_AGENT/`. Đã bỏ `.env*`, `runtime/`, `sao_luu/`, `vendor/`, `BAO_CAO/`, `reports/`, `.handoff/`, `services/`. |
| `nguon/01-may-noi-dung` | `D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG` | `2026-11-08` | Gồm `README.md`, `dieu_phoi.py` (kèm bản sao `module.py` giữ nguyên nội dung gốc `dieu_phoi.py`), `core_loai_va_gemini.py`, `loai/`, `skills/`, `scripts/`. Đã bỏ `runs/`, `sao_luu/`, `vendor/`, `logs/`, `BAO_CAO/`, `reports/`, `demo/`, `assets_agy/`, `web/`. |
