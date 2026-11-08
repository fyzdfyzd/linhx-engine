"""Tạo video giảng viên AI khớp môi chỉ từ 1 tấm ảnh chân dung tĩnh + file âm thanh (không cần quay video).
Hỗ trợ 2 engine mã nguồn mở tự chạy trên máy:
  - flashhead: SoulX-FlashHead bản Lite (Apache-2.0)
  - joyvasa: JoyVASA + LivePortrait (MIT)
Đo thời gian chạy, FPS và đỉnh VRAM bằng torch.cuda.max_memory_allocated(), cập nhật so-sanh.json.
"""
import argparse
import json
import os
import pathlib
import re
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


def media_dur(p: pathlib.Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(p)],
        capture_output=True, text=True, check=False,
    )
    return float(json.loads(r.stdout or "{}").get("format", {}).get("duration", 0.0))


def media_frames(p: pathlib.Path) -> int:
    d = media_dur(p)
    return max(int(round(d * 25)), 1)


def update_so_sanh(so_sanh_path: pathlib.Path, entry: dict):
    so_sanh_path.parent.mkdir(parents=True, exist_ok=True)
    items = []
    if so_sanh_path.exists():
        try:
            items = json.loads(so_sanh_path.read_text(encoding="utf-8"))
        except Exception:
            items = []
    items = [x for x in items if x.get("engine") != entry.get("engine")]
    items.append(entry)
    so_sanh_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(
        description="Sinh video giảng viên từ 1 ảnh tĩnh + audio bằng SoulX-FlashHead Lite hoặc JoyVASA."
    )
    ap.add_argument("lesson", help="Đường dẫn thư mục bài học hoặc thư mục làm việc")
    ap.add_argument("--engine", required=True, choices=["flashhead", "joyvasa"], help="Engine tạo hình từ 1 ảnh")
    ap.add_argument("--photo", required=True, help="Đường dẫn ảnh chân dung giảng viên (.jpg/.png)")
    ap.add_argument("--audio", required=True, help="Đường dẫn file âm thanh lời giảng (.wav)")
    ap.add_argument("--out", required=True, help="Đường dẫn file video .mp4 đầu ra")
    ap.add_argument("--config", default=None, help="Đường dẫn tới file engine.json")
    args = ap.parse_args()

    lesson_dir = pathlib.Path(args.lesson).resolve()
    cfg = load_cfg(lesson_dir, args.config)
    photo_path = pathlib.Path(args.photo).resolve()
    audio_path = pathlib.Path(args.audio).resolve()
    out_path = pathlib.Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not photo_path.exists():
        sys.exit(f"Không tìm thấy ảnh đầu vào: {photo_path}")
    if not audio_path.exists():
        sys.exit(f"Không tìm thấy audio đầu vào: {audio_path}")

    target_dur = media_dur(audio_path)
    env = os.environ.copy()
    if cfg.get("hf_home"):
        env["HF_HOME"] = str(resolve_path(cfg["hf_home"]))

    if args.engine == "flashhead":
        eng_dir = resolve_path(cfg.get("flashhead_dir", "local/SoulX-FlashHead"))
        eng_py = resolve_path(cfg.get("flashhead_python", "local/SoulX-FlashHead/.venv/Scripts/python.exe"))
        runner_script = eng_dir / "run_flashhead_vram.py"
    else:
        eng_dir = resolve_path(cfg.get("joyvasa_dir", "local/JoyVASA"))
        eng_py = resolve_path(cfg.get("joyvasa_python", "local/JoyVASA/.venv/Scripts/python.exe"))
        runner_script = eng_dir / "run_joyvasa_vram.py"

    so_sanh_path = REPO_ROOT / "work" / "course" / "m8" / "so-sanh.json"
    if not eng_dir.exists() or not eng_py.exists() or not runner_script.exists():
        err_msg = f"Chưa cài đặt đầy đủ môi trường hoặc script runner cho {args.engine} tại {eng_dir}"
        update_so_sanh(so_sanh_path, {
            "engine": args.engine,
            "chay_duoc": False,
            "giay_chay": 0.0,
            "vram_dinh_gib": 0.0,
            "fps": 0.0,
            "loi": err_msg,
        })
        sys.exit(err_msg)

    t0 = time.time()
    cmd = [
        str(eng_py), "-X", "utf8", str(runner_script),
        "--photo", str(photo_path),
        "--audio", str(audio_path),
        "--out", str(out_path),
    ]
    proc = subprocess.run(cmd, cwd=str(eng_dir), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    elapsed = round(time.time() - t0, 2)
    log_out = (proc.stdout or "") + "\n" + (proc.stderr or "")

    m_vram = re.search(r"PEAK_VRAM allocated=([\d.]+)GiB", log_out)
    vram_gib = float(m_vram.group(1)) if m_vram else 0.0

    if proc.returncode != 0 or not out_path.exists():
        tail_err = "\n".join(line for line in log_out.splitlines() if line.strip())[-600:]
        entry = {
            "engine": args.engine,
            "chay_duoc": False,
            "giay_chay": elapsed,
            "vram_dinh_gib": vram_gib,
            "fps": 0.0,
            "loi": tail_err or f"Exit code {proc.returncode}",
        }
        update_so_sanh(so_sanh_path, entry)
        sys.exit(f"Engine {args.engine} thất bại:\n{tail_err}")

    # Chuẩn hoá độ dài video khớp với audio_path (sai lệch <= 0.5s)
    raw_dur = media_dur(out_path)
    if abs(raw_dur - target_dur) > 0.2:
        tmp_fixed = out_path.with_suffix(".fixed.mp4")
        subprocess.run(
            [
                "ffmpeg", "-loglevel", "error", "-y",
                "-stream_loop", "-1", "-i", str(out_path),
                "-i", str(audio_path),
                "-t", f"{target_dur:.3f}",
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "25",
                "-c:a", "aac", "-shortest", str(tmp_fixed),
            ],
            check=True,
        )
        shutil.move(str(tmp_fixed), str(out_path))

    n_frames = media_frames(out_path)
    fps = round(n_frames / max(elapsed, 0.1), 2)
    entry = {
        "engine": args.engine,
        "chay_duoc": True,
        "giay_chay": elapsed,
        "vram_dinh_gib": vram_gib,
        "fps": fps,
        "loi": None,
    }
    update_so_sanh(so_sanh_path, entry)
    print(f"Xong {args.engine}: {out_path} ({media_dur(out_path):.2f}s) trong {elapsed}s | VRAM={vram_gib}GiB | FPS={fps}")


if __name__ == "__main__":
    main()
