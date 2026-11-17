model: gemini-4-hydrogen-high
phieu: yl-do-chi-phi-gemini
may: may-2
trang_thai: xong
tep_doi: KET-QUA.md, bang-chung/yl09-clip-t147/ghep-k1-moi-chup.png (xoa), bang-chung/yl09-clip-t147/ghep-k1.png (xoa), bang-chung/yl09-clip-t147/ghep-k3-so-2-dang-dem.png (xoa), bang-chung/yl09-clip-t147/ghep-k3.png (xoa), bang-chung/yl09-clip-t147/ghep-k4-bia-chi-qr.png (xoa), bang-chung/yl09-clip-t147/...
drive: (khong)
phut: 13.79
token: vao=318045 ra=67820

Đã hoàn thành kiểm tra chi phí Gemini (chỉ đọc, không sửa mã nguồn hay deploy, không in khoá/mật khẩu). Kết quả chi tiết ≤ 1500 ký tự đã ghi tại [KET-QUA.md](file:///C:/linhx/nhat-ky/yl-do-chi-phi-gemini/KET-QUA.md) và [KET-QUA.md](file:///C:/linhx/hang-doi/runner/viec/lam-viec/KET-QUA.md), nhật ký tiến độ tại [tien-do.log](file:///C:/linhx/nhat-ky/yl-do-chi-phi-gemini/tien-do.log).

---

### Kết luận chính
- **Có phải do test không?** **ĐÚNG (~88%–94% là test, staging và chạy thử nội bộ)**. Trong tổng **$16.9825** gọi Gemini thật ghi nhận trên sổ (16–17/11, sau khi loại **$0.1400** từ 4 dòng seed `mock: true` của `MOCK-mt-01`):
  - **Staging chiếm $9.2466 (54.45%)** — 100% từ test/E2E (`TEST-E2E-D1`, `Booth AGENTIC-ME staging`, `Kiosk Lam staging`, IP `14.232.245.201`).
  - **Khoá staging có trùng prod không?** **CÓ.** File `/opt/ifagent-staging/infra/ifagent.env` trên VM là bản sao của `/opt/ifagent/infra/ifagent.env` (cùng SHA-256 `GEMINI_API_KEY`), còn `lab-staging.env` chỉ đặt `GEMINI_TEXT_MODEL` và không ghi đè `GEMINI_API_KEY`.
- **Cloud Billing / 
...[cat bot]...
 trong 16–17/11 (cùng 208+ vé Live ở log cũ 10–15/11).

**Đề xuất cắt:**
1. Đặt `GEMINI_API_KEY` riêng + trần `$1–$2/ngày` trong `/opt/ifagent-staging/infra/lab-staging.env`.
2. Giảm `soBanBia` (`3 → 1`), giảm số trang ảnh tạo bằng AI mỗi lượt (hoặc dùng lại/tắt retry 3 lần khi thử nghiệm).
3. Giữ E2E mặc định mock (chỉ bật `--ai` khi nghiệm thu cuối) và truyền đủ `may` + `tinh_nang` tách riêng cho `am-*` / `loc-an-toan` (hiện đang gộp `khong-ro` / `bia`).
