"""Kết xuất slides.md của một bài học thành các khung ảnh PNG 1920x1080 theo từng click bằng Slidev
(sử dụng Node 22.12 portable và Playwright Chromium khai báo trong engine.json),
sau đó gọi make_segments.py để tạo segments.json.
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

ENGINE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = ENGINE_DIR.parents[3]


def load_cfg(lesson_dir: pathlib.Path, cfg_override: str | None = None) -> dict:
    for c in [
        pathlib.Path(cfg_override) if cfg_override else None,
        lesson_dir.parent.parent / "engine.json",
        REPO_ROOT / "work" / "course" / "engine.json",
        ENGINE_DIR / "config.example.json",
    ]:
        if c and c.exists():
            return json.loads(c.read_text(encoding="utf-8"))
    return {}


def resolve_path(val: str) -> pathlib.Path:
    p = pathlib.Path(val)
    return p if p.is_absolute() else (REPO_ROOT / p).resolve()


def main():
    ap = argparse.ArgumentParser(
        description="Render slides.md thành ảnh PNG 1920x1080 theo từng click bằng Slidev và tạo segments.json."
    )
    ap.add_argument("lesson", help="Đường dẫn thư mục bài học (ví dụ: work/course/04-lessons/L01)")
    ap.add_argument("--config", default=None, help="Đường dẫn tới file engine.json")
    args = ap.parse_args()

    lesson_dir = pathlib.Path(args.lesson).resolve()
    slides_md = lesson_dir / "slides.md"
    style_css = lesson_dir / "style.css"
    frames_dir = lesson_dir / "frames"

    if not slides_md.exists():
        sys.exit(f"Không tìm thấy {slides_md}")

    cfg = load_cfg(lesson_dir, args.config)
    node_dir = resolve_path(cfg.get("node_dir", "local/.node/node-v22.12.0-win-x64"))
    pw_browsers = resolve_path(cfg.get("playwright_browsers", "local/.pw-browsers"))
    npm_cache = resolve_path(cfg.get("npm_cache", "local/.npm-cache"))
    slidev_workdir = resolve_path(cfg.get("slidev_workdir", "local/pilot/L01"))

    env = os.environ.copy()
    env["PATH"] = f"{node_dir};{env.get('PATH', '')}"
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(pw_browsers)
    env["npm_config_cache"] = str(npm_cache)

    # Để không phải cài lại node_modules cho từng bài học, chép tạm slides.md + style.css vào slidev_workdir để export
    work_slides = slidev_workdir / "_render_slides.md"
    work_style = slidev_workdir / "style.css"
    work_frames = slidev_workdir / "_render_frames"

    if work_frames.exists():
        shutil.rmtree(work_frames)
    shutil.copy2(slides_md, work_slides)
    if style_css.exists():
        shutil.copy2(style_css, work_style)
    lesson_public = lesson_dir / "public"
    work_public = slidev_workdir / "public"
    if lesson_public.exists():
        work_public.mkdir(parents=True, exist_ok=True)
        for item in lesson_public.iterdir():
            if item.is_file():
                shutil.copy2(item, work_public / item.name)

    npx_cmd = str(node_dir / "npx.cmd")
    t0 = time.time()
    cmd = [
        npx_cmd, "slidev", "export", "_render_slides.md",
        "--format", "png", "--with-clicks", "--scale", "1",
        "--output", "_render_frames",
    ]
    proc = subprocess.run(cmd, cwd=str(slidev_workdir), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        sys.exit(f"Slidev export lỗi:\n{(proc.stdout or '')[-1000:]}\n{(proc.stderr or '')[-1000:]}")

    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)
    for png in sorted(work_frames.glob("*.png")):
        shutil.copy2(png, frames_dir / png.name)

    work_slides.unlink(missing_ok=True)
    shutil.rmtree(work_frames, ignore_errors=True)

    print(f"Đã xuất {len(list(frames_dir.glob('*.png')))} khung PNG trong {time.time() - t0:.1f}s")
    subprocess.run(
        [sys.executable, "-X", "utf8", str(ENGINE_DIR / "make_segments.py"), str(slides_md), str(frames_dir), str(lesson_dir / "segments.json")],
        check=True,
    )


if __name__ == "__main__":
    main()
