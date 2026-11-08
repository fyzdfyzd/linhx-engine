#!/usr/bin/env python3
"""Hook PreToolUse của linhx-kenh-ao. Lớp chặn thứ hai, sau cổng trong CLI:
1. Không ghi thẳng vào kenh.db (phải qua CLI để cổng và nhật ký chạy).
2. Không gọi thẳng tool đăng/bình luận của MCP (Postiz, xiaohongshu…): phải qua `kenhao.py dang` / `hop-thu-gui`.
3. Agent muốn sửa luật gốc (hanh-vi.md, phong-cach.md, hang-rui-ro.md) thì phải hỏi Linh."""
import json
import re
import sys

d = json.load(sys.stdin)
ten = d.get("tool_name", "")
vao = d.get("tool_input", {}) or {}


def tra(quyet, ly_do):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": quyet, "permissionDecisionReason": ly_do}}, ensure_ascii=False))
    sys.exit(0)


if ten == "Bash":
    lenh = vao.get("command", "")
    if "kenh.db" in lenh and re.search(r"\b(insert|update|delete|drop|alter|replace)\b", lenh, re.I):
        tra("deny", "linhx-kenh-ao: không ghi thẳng vào kenh.db; dùng lệnh kenhao.py để cổng chặn và nhật ký chạy.")
elif ten.startswith("mcp__"):
    if re.search(r"postiz|xiaohongshu|xhs|tiktok|instagram|facebook|threads|douyin", ten, re.I) and \
            re.search(r"post|publish|schedule|comment|reply|like|follow|send|dm|message", ten, re.I) and \
            not re.search(r"list|get|read|search|find", ten.split("__")[-1], re.I):
        tra("deny", "linhx-kenh-ao: đăng, bình luận, nhắn phải đi qua kenhao.py (dang / hop-thu-gui / cham-de-xuat) để qua cổng.")
elif ten in ("Edit", "Write", "MultiEdit"):
    p = vao.get("file_path", "")
    if re.search(r"ho-so[\\/](hanh-vi|phong-cach|hang-rui-ro)\.md$", p):
        tra("ask", "linhx-kenh-ao: đây là luật gốc do Linh đặt. Đề xuất thay đổi trong RETRO; chỉ sửa khi Linh đồng ý.")
sys.exit(0)
