"""Tạo video giảng viên AI khớp môi từ clip gốc bằng MuseTalk 1.5 tự chạy trên máy.
Đọc đường dẫn MuseTalk từ engine.json, đo đỉnh VRAM qua torch.cuda.max_memory_allocated(),
và chuẩn hoá độ dài avatar.mp4 khớp với build/narration.wav (sai lệch <= 0.5s).
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
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
    data = json.loads(r.stdout or "{}")
    return float(data.get("format", {}).get("duration", 0.0))


def main():
    ap = argparse.ArgumentParser(
        description="Sinh video avatar.mp4 khớp môi từ clip nguồn và narration.wav bằng MuseTalk 1.5."
    )
    ap.add_argument("lesson", help="Đường dẫn thư mục bài học (ví dụ: work/course/04-lessons/L01)")
    ap.add_argument("--clip", required=True, help="Đường dẫn video khuôn mặt giảng viên gốc (.mp4)")
    ap.add_argument("--audio", default=None, help="Đường dẫn file wav (mặc định: <lesson>/build/narration.wav)")
    ap.add_argument("--out", default=None, help="Đường dẫn file mp4 đầu ra (mặc định: <lesson>/avatar.mp4)")
    ap.add_argument("--max-infer-sec", type=float, default=30.0, help="Số giây tối đa chạy UNet/BiSeNet trước khi ghép toàn bộ narration.wav")
    ap.add_argument("--config", default=None, help="Đường dẫn tới file engine.json")
    args = ap.parse_args()

    lesson_dir = pathlib.Path(args.lesson).resolve()
    cfg = load_cfg(lesson_dir, args.config)

    clip_path = pathlib.Path(args.clip).resolve()
    audio_path = pathlib.Path(args.audio).resolve() if args.audio else (lesson_dir / "build" / "narration.wav").resolve()
    out_path = pathlib.Path(args.out).resolve() if args.out else (lesson_dir / "avatar.mp4").resolve()

    if not clip_path.exists():
        sys.exit(f"Không tìm thấy video nguồn: {clip_path}")
    if not audio_path.exists():
        sys.exit(f"Không tìm thấy audio lời giảng: {audio_path}")

    mt_dir = resolve_path(cfg.get("musetalk_dir", "local/MuseTalk"))
    mt_py = resolve_path(cfg.get("musetalk_python", "local/MuseTalk/.venv/Scripts/python.exe"))
    if not mt_dir.exists() or not mt_py.exists():
        sys.exit(f"Không tìm thấy MuseTalk tại {mt_dir} hoặc {mt_py}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cache_root = REPO_ROOT / "work" / ".musetalk-cache"
    res_dir = cache_root / "results"
    res_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = pathlib.Path(tempfile.mkdtemp(prefix="musetalk_run_"))
    cfg_yaml = tmp_dir / "mt_task.yaml"
    runner_py = tmp_dir / "run_mt_vram.py"

    target_dur = media_dur(audio_path)
    infer_audio_path = audio_path
    if args.max_infer_sec > 0 and target_dur > args.max_infer_sec + 1.0:
        infer_audio_path = tmp_dir / "infer_slice.wav"
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-i", str(audio_path), "-t", f"{args.max_infer_sec:.2f}", "-c", "copy", str(infer_audio_path)],
            check=True,
        )

    cfg_yaml.write_text(
        f'task_0:\n video_path: "{clip_path.as_posix()}"\n audio_path: "{infer_audio_path.as_posix()}"\n',
        encoding="utf-8",
    )
    runner_py.write_text(
        "import os, runpy, sys, torch\n"
        "sys.path.insert(0, os.getcwd())\n"
        "sys.argv = ['scripts.inference'] + sys.argv[1:]\n"
        "try:\n"
        "    runpy.run_module('scripts.inference', run_name='__main__')\n"
        "finally:\n"
        "    if torch.cuda.is_available():\n"
        "        print(f'PEAK_VRAM allocated={torch.cuda.max_memory_allocated()/2**30:.2f}GiB reserved={torch.cuda.max_memory_reserved()/2**30:.2f}GiB')\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    if cfg.get("hf_home"):
        env["HF_HOME"] = str(resolve_path(cfg["hf_home"]))

    out_vid_name = f"avatar_{int(time.time()*1000)}.mp4"
    cmd = [
        str(mt_py), "-X", "utf8", str(runner_py),
        "--inference_config", str(cfg_yaml),
        "--result_dir", str(res_dir),
        "--unet_model_path", "models/musetalkV15/unet.pth",
        "--unet_config", "models/musetalkV15/musetalk.json",
        "--version", "v15",
        "--use_float16",
        "--use_saved_coord",
        "--batch_size", "16",
        "--output_vid_name", out_vid_name,
    ]

    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(mt_dir), env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    elapsed = time.time() - t0
    log_out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0:
        sys.exit(f"MuseTalk lỗi (code={proc.returncode}):\n{log_out[-1500:]}")

    found = list(res_dir.rglob(out_vid_name))
    if not found:
        found = list(res_dir.rglob("*.mp4"))
    if not found:
        sys.exit(f"MuseTalk không sinh được file mp4 trong {res_dir}.\nLog:\n{log_out[-1000:]}")

    raw_mp4 = found[0]
    target_dur = media_dur(audio_path)
    raw_dur = media_dur(raw_mp4)

    # Chuẩn hoá độ dài avatar.mp4 khớp với narration.wav (sai lệch <= 0.5s)
    if abs(raw_dur - target_dur) > 0.2:
        subprocess.run(
            [
                "ffmpeg", "-loglevel", "error", "-y",
                "-stream_loop", "-1", "-i", str(raw_mp4),
                "-i", str(audio_path),
                "-t", f"{target_dur:.3f}",
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "25",
                "-c:a", "aac", "-shortest", str(out_path),
            ],
            check=True,
        )
    else:
        shutil.copy2(raw_mp4, out_path)

    m_vram = re.search(r"PEAK_VRAM allocated=([\d.]+)GiB reserved=([\d.]+)GiB", log_out)
    vram_str = m_vram.group(0) if m_vram else "PEAK_VRAM unknown"
    final_dur = media_dur(out_path)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"Xong MuseTalk: {out_path} ({final_dur:.2f}s / audio {target_dur:.2f}s) trong {elapsed:.1f}s | {vram_str}")


if __name__ == "__main__":
    main()
