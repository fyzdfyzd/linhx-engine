#!/usr/bin/env python3
"""Cổng gửi ra (LAB041). Mọi công cụ MCP có vẻ gửi tin/đăng bài ra ngoài thì bắt người bấm duyệt.
Lỗi bất kỳ trong hook → vẫn hỏi duyệt (fail-closed). Không chặn hẳn, chỉ chuyển sang 'ask'."""
import json, re, sys

GUI = re.compile(r"(send|post|publish|forward|reply|comment|message|broadcast|zns|dang_bai|gui_tin)", re.I)
BO_QUA = re.compile(r"^mcp__(hearthbot|claude-code-remote|Claude_Docs)__", re.I)  # chat nội bộ của Claude, không ra ngoài
CHI_DOC = re.compile(r"__(get|list|search|read|fetch|query)_", re.I)


def tra(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "permissionDecision": decision,
                                              "permissionDecisionReason": reason}}, ensure_ascii=False))


try:
    data = json.load(sys.stdin)
    ten = data.get("tool_name", "")
    if BO_QUA.search(ten) or CHI_DOC.search(ten) or not GUI.search(ten):
        sys.exit(0)
    tra("ask", f"Cổng gửi ra LAB041: '{ten}' sẽ gửi/đăng ra ngoài. Linh đọc nội dung rồi tự duyệt. "
               "Không gửi cho người chưa đồng ý liên hệ, không nhắn hàng loạt.")
except SystemExit:
    raise
except Exception as e:  # fail-closed
    tra("ask", f"Cổng gửi ra LAB041 gặp lỗi ({e}); hỏi duyệt cho chắc.")
