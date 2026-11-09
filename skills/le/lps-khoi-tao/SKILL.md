---
name: lps-khoi-tao
description: Khởi tạo một dự án webapp/nền tảng mới (hoặc đưa dự án có sẵn) vào chuẩn LINHX Platform Standard (LPS). Dùng khi Linh nói "dự án mới", "khởi tạo theo LPS", "áp chuẩn LPS vào repo này".
metadata:
  version: "0.1.0"
---

# Khởi tạo dự án theo LPS

Nguồn chuẩn: `D:\LINHX\LAB\LAB009-DEV-STANDARD\src\lps\` (gọi tắt là `LPS_HOME`). Đọc `LPS_HOME/STANDARD.md` mục 1–3 trước khi làm.

## Bước
1. **Hỏi đúng 3 điều nếu chưa rõ** (không hỏi thêm): tên dự án; hạng T1/T2/T3 (mặc định T2); dùng stack mặc định hay có lý do đổi (mặc định: dùng).
2. **Chép khung:**
   - `LPS_HOME/AGENTS.md` → gốc repo, điền phần `<...>`; `LPS_HOME/CLAUDE.md` → gốc repo.
   - `LPS_HOME/docs/templates/` → `docs/templates/`; tạo `docs/specs/`, `docs/adr/`, `docs/security/`, `docs/user-tests/`.
   - `PULL_REQUEST_TEMPLATE.md` → `.github/`; `LPS_HOME/ci/quality.yml` và `deploy.yml` → `.github/workflows/`, `dependabot.yml` → `.github/` (T2, T3). Hỏi Linh chọn biến thể hosting trong `deploy.yml` (mặc định T2: Vercel), xoá biến thể kia, ghi ADR.
   - `docs/templates/RUNBOOK.md` → `docs/RUNBOOK.md`; thêm route `GET /api/health` trả phiên bản và trạng thái DB.
   - `LPS_HOME/tool-config/` theo hướng dẫn trong `tool-config/README.md` (hook Claude, gitleaks, dependency-cruiser).
   - Chạy `LPS_HOME/scripts/sync-skills.ps1 -Target <repo>` để chép skill sang `.claude/skills/` và `.agents/skills/`.
3. **Dựng stack mặc định** (STANDARD mục 3): TypeScript strict, pnpm, Vitest, Playwright, ESLint + Prettier, Zod, Drizzle. Gộp `tool-config/package-scripts.json` vào `package.json`; chép `vitest.config.ts`, `playwright.config.ts`, `lefthook.yml`, `.dependency-cruiser.cjs`; chạy `pnpm lefthook install`.
3b. **Nếu sản phẩm gọi LLM:** chép `tool-config/llm/` vào `src/modules/ai/` (theo skill `lps-llm` bước 3), thêm `@anthropic-ai/sdk`, `tsx`, tạo `docs/ai/`.
4. **Viết ADR-0001** "Dùng LPS vX.Y và stack mặc định" (ghi các chỗ lệch nếu có).
5. **Chứng minh khung chạy:** `pnpm verify` xanh với một test mẫu và một e2e mẫu (gắn `@smoke`) mở trang chủ. Nếu T2/T3: commit, tạo repo riêng tư, đẩy lên, mở PR draft, CI xanh.
6. **GitHub:** đưa Linh checklist `docs/templates/GITHUB-SETUP.md` (bảo vệ `main`, Environments, secret). Agent không tự đổi cài đặt bảo vệ nhánh hay secret; chỉ chạy lệnh `gh` cho từng bước khi Linh đồng ý.
7. Báo lại: đường dẫn repo, hạng, lệnh `verify`, những gì còn thiếu.

## Không làm
- Không thêm thư viện ngoài stack mặc định khi chưa có ADR.
- Không tạo bí mật thật; chỉ tạo `.env.example` với giá trị giả.
