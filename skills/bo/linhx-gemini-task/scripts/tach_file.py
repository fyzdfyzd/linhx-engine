"""Tách câu trả lời Argon (một file .md có các khối '### FILE: <đường dẫn>') thành từng file.

Dùng: python tach-file.py <tra-loi.md> <thu-muc-dich>
Nội dung của mỗi file là phần sau tiêu đề tới tiêu đề FILE kế tiếp; nếu nằm trong một khối ``` thì bỏ hàng rào.
"""
import re
import sys
from pathlib import Path

HEAD = re.compile(r"^#{2,4}\s*FILE:\s*(.+?)\s*$", re.M)


def tach(text: str) -> dict[str, str]:
    parts = HEAD.split(text)
    out = {}
    for i in range(1, len(parts) - 1, 2):
        path, body = parts[i].strip().strip("`"), parts[i + 1].strip("\n")
        m = re.match(r"^```[^\n]*\n(.*)\n```\s*$", body.strip(), re.S)
        out[path] = (m.group(1) if m else body.strip()) + "\n"
    return out


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    files = tach(src.read_text(encoding="utf-8"))
    for rel, body in files.items():
        p = (dst / rel).resolve()
        if dst.resolve() not in p.parents:
            print(f"Bỏ qua đường dẫn ra ngoài thư mục: {rel}")
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        print("ghi", p)
    print(f"{len(files)} file")


if __name__ == "__main__":
    main()
