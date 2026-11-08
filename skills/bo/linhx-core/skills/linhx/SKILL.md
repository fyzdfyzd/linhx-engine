---
name: linhx
description: Lệnh quản trị plugin linhx-core (xem luật đang bơm, kiểm skill, cài sang Antigravity). Dùng khi Linh gõ /linhx, hỏi "luật LAB đang bơm gì", "cài skill LINHX cho agy", hoặc sau khi sửa skill trong marketplace linhx-lab.
argument-hint: "[context|lint|agy-install|agy-uninstall]"
---

# /linhx

Chạy `node "${CLAUDE_PLUGIN_ROOT}/scripts/linhx.js" <lệnh>` với lệnh Linh gõ, mặc định là `context`.

| Lệnh | Việc |
|---|---|
| `context [thư-mục]` | In đoạn luật mà hook mở phiên sẽ bơm khi đứng ở thư mục đó |
| `lint` | Kiểm mọi SKILL.md trong marketplace: `name` khớp thư mục, description có "Dùng khi" |
| `agy-install` | Chép mọi skill linhx sang `~/.gemini/antigravity/skills/linhx-*`, ghi khối luật vào `~/.gemini/GEMINI.md` (sao lưu file cũ thành `.bak-linhx-core`) |
| `agy-uninstall` | Gỡ những gì `agy-install` đã ghi |

Báo lại cho Linh đúng các dòng script in ra. Antigravity không có hook mở phiên như Claude, nên luật đi qua GEMINI.md và skill tự kích hoạt theo description. Sửa luật ở `rules/LUAT-LINHX.md`, rồi chạy lại `agy-install`.
