"""Kiểm tra môi trường sản xuất khoá học (ffmpeg, node, vieneu_python, musetalk_python, gpu).
Ghi kết quả vào <course_dir>/doctor.json.
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys

ENGINE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = ENGINE_DIR.parents[3]


def load_cfg(course_dir: pathlib.Path, cfg_override: str | None = None) -> dict:
    for c in [
        pathlib.Path(cfg_override) if cfg_override else None,
        course_dir / "engine.json",
        ENGINE_DIR / "config.example.json",
    ]:
        if c and c.exists():
            return json.loads(c.read_text(encoding="utf-8"))
    return {}


def resolve_bin(val: str) -> str:
    p = pathlib.Path(val)
    if p.is_absolute() and p.exists():
        return str(p)
    rel = (REPO_ROOT / val).resolve()
    if rel.exists():
        return str(rel)
    found = shutil.which(val)
    return found or str(rel)


def run_cmd(cmd: list[str], timeout: int = 20) -> tuple[bool, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        out = (r.stdout or r.stderr or "").strip()
        first_line = out.splitlines()[0].strip() if out else ""
        return (r.returncode == 0, first_line)
    except Exception as e:
        return (False, str(e))


def main():
    ap = argparse.ArgumentParser(
        description="Kiểm tra môi trường (ffmpeg, node, vieneu_python, musetalk_python, gpu) và ghi doctor.json."
    )
    ap.add_argument("course_dir", nargs="?", default="work/course", help="Thư mục khoá học (mặc định: work/course)")
    ap.add_argument("--config", default=None, help="Đường dẫn tới file engine.json")
    args = ap.parse_args()

    course_dir = pathlib.Path(args.course_dir).resolve()
    course_dir.mkdir(parents=True, exist_ok=True)
    cfg = load_cfg(course_dir, args.config)

    ffmpeg_bin = resolve_bin(cfg.get("ffmpeg", "ffmpeg"))
    ff_ok, ff_ver = run_cmd([ffmpeg_bin, "-version"])

    node_bin = resolve_bin(cfg.get("node_exe", "node"))
    node_ok, node_ver = run_cmd([node_bin, "--version"])

    vieneu_py = resolve_bin(cfg.get("vieneu_python", "python"))
    vn_ok, vn_ver = run_cmd([
        vieneu_py, "-I", "-X", "utf8", "-c",
        "import sys, torch, vieneu; print(f'Python {sys.version.split()[0]} | torch {torch.__version__} | cuda={torch.cuda.is_available()}')",
    ], timeout=30)

    musetalk_py = resolve_bin(cfg.get("musetalk_python", "python"))
    mt_ok, mt_ver = run_cmd([
        musetalk_py, "-X", "utf8", "-c",
        "import sys, torch, diffusers; print(f'Python {sys.version.split()[0]} | torch {torch.__version__} | diffusers {diffusers.__version__} | cuda={torch.cuda.is_available()}')",
    ], timeout=45)

    gpu_ok, gpu_info = run_cmd([
        vieneu_py if pathlib.Path(vieneu_py).exists() else sys.executable,
        "-c",
        "import json, torch; "
        "ok = torch.cuda.is_available(); "
        "name = torch.cuda.get_device_name(0) if ok else 'none'; "
        "vram = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2) if ok else 0; "
        "print(json.dumps({'ok': ok, 'name': name, 'vram_gib': vram}))",
    ], timeout=20)
    try:
        gpu_dict = json.loads(gpu_info) if gpu_ok else {"ok": False, "error": gpu_info}
    except Exception:
        gpu_dict = {"ok": False, "raw": gpu_info}

    report = {
        "ffmpeg": {"path": ffmpeg_bin, "version": ff_ver, "ok": ff_ok},
        "node": {"path": node_bin, "version": node_ver, "ok": node_ok},
        "vieneu_python": {"path": vieneu_py, "version": vn_ver, "ok": vn_ok},
        "musetalk_python": {"path": musetalk_py, "version": mt_ver, "ok": mt_ok},
        "gpu": gpu_dict,
    }

    out_file = course_dir / "doctor.json"
    out_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
