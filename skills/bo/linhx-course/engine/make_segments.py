"""Tách lời giảng trong slides.md (Slidev, notes có [click]) + thư mục frames/ -> segments.json.
Mỗi đoạn lời giảng ứng với đúng một khung ảnh PNG 1920x1080. Dừng với lỗi nếu số đoạn và số khung lệch nhau.
"""
import argparse
import json
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def parse_notes(md: str):
    notes = re.findall(r"<!--(.*?)-->", md, flags=re.S)
    return [n.strip() for n in notes]


def build_segments(slides_md: pathlib.Path, frames_dir: pathlib.Path, out_path: pathlib.Path):
    notes = parse_notes(slides_md.read_text(encoding="utf-8"))
    frames = sorted(frames_dir.glob("*.png"))
    by_slide = {}
    for f in frames:
        parts = f.stem.split("-")
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        s = int(parts[0])
        by_slide.setdefault(s, []).append(f)

    if len(notes) != len(by_slide):
        sys.exit(f"Lệch: {len(notes)} khối notes nhưng {len(by_slide)} slide trong {frames_dir}")

    segs = []
    for n, (s, fs) in zip(notes, sorted(by_slide.items())):
        parts = [p.strip() for p in re.split(r"\[click\]", n)]
        if len(parts) != len(fs):
            sys.exit(f"Slide {s}: {len(parts)} đoạn lời nhưng {len(fs)} khung PNG")
        for c, (p, f) in enumerate(zip(parts, fs)):
            clean_text = re.sub(r"\s+", " ", p).strip()
            segs.append({
                "seg_id": f"{s:03d}-{c+1:02d}",
                "slide": s,
                "click": c,
                "png": f.name,
                "text": clean_text,
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(segs, ensure_ascii=False, indent=1), encoding="utf-8")
    words = sum(len(re.sub(r"<[^>]+>", " ", x["text"]).split()) for x in segs)
    max_words = max((len(re.sub(r"<[^>]+>", " ", x["text"]).split()) for x in segs), default=0)
    print(f"{len(segs)} đoạn, {words} âm tiết (đoạn dài nhất {max_words} âm tiết), ước {words/258:.1f} phút")


def main():
    ap = argparse.ArgumentParser(
        description="Tách lời giảng trong slides.md và ghép với khung hình PNG trong frames/ thành segments.json."
    )
    ap.add_argument("slides_md", help="Đường dẫn tới file slides.md (hoặc thư mục bài học nếu chỉ truyền 1 tham số)")
    ap.add_argument("frames_dir", nargs="?", help="Đường dẫn thư mục frames chứa ảnh PNG")
    ap.add_argument("out", nargs="?", help="Đường dẫn file segments.json đầu ra")
    args = ap.parse_args()

    p = pathlib.Path(args.slides_md)
    if p.is_dir() and not args.frames_dir and not args.out:
        slides_md = p / "slides.md"
        frames_dir = p / "frames"
        out_path = p / "segments.json"
    else:
        if not args.frames_dir or not args.out:
            ap.error("Cần truyền đủ 3 tham số: <slides.md> <frames_dir> <segments.json> hoặc 1 thư mục bài học.")
        slides_md = p
        frames_dir = pathlib.Path(args.frames_dir)
        out_path = pathlib.Path(args.out)

    build_segments(slides_md, frames_dir, out_path)


if __name__ == "__main__":
    main()
