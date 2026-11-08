"""Tổng hợp giọng giảng viên tiếng Việt từ segments.json -> audio/<seg_id>.wav + timing.json bằng VieNeu-TTS.
Tự động chuyển tiếp sang môi trường ảo VieNeu-TTS trong engine.json nếu gọi từ Python hệ thống.
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import wave

ENGINE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = ENGINE_DIR.parents[3]


def load_engine_cfg(lesson_dir: pathlib.Path, cfg_override: str | None = None) -> dict:
    candidates = []
    if cfg_override:
        candidates.append(pathlib.Path(cfg_override))
    candidates.extend([
        lesson_dir.parent.parent / "engine.json",
        REPO_ROOT / "work" / "course" / "engine.json",
        ENGINE_DIR / "config.example.json",
    ])
    for c in candidates:
        if c.exists():
            return json.loads(c.read_text(encoding="utf-8"))
    return {}


def resolve_path(rel_or_abs: str) -> pathlib.Path:
    p = pathlib.Path(rel_or_abs)
    return p if p.is_absolute() else (REPO_ROOT / p).resolve()


def wav_dur(p: pathlib.Path) -> float:
    with wave.open(str(p), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def load_en_terms(pron_path: pathlib.Path) -> list[str]:
    if not pron_path.exists():
        return []
    txt = pron_path.read_text(encoding="utf-8")
    m = re.search(r"en_terms:\s*\[(.*?)\]", txt, flags=re.S)
    if m:
        raw = [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]
        return sorted(raw, key=len, reverse=True)
    try:
        import yaml
        data = yaml.safe_load(txt) or {}
        terms = data.get("en_terms", [])
        return sorted([str(t).strip() for t in terms if str(t).strip()], key=len, reverse=True)
    except Exception:
        return []


def tag_en(text: str, terms: list[str]) -> str:
    # Nếu đã có thẻ <en> thì gỡ ra rồi bọc lại đồng nhất để tránh lồng thẻ <en><en>...</en></en>
    clean = re.sub(r"</?en>", "", text)
    if not terms:
        return clean
    pat = r"(?<![\w>])(" + "|".join(map(re.escape, terms)) + r")(?![\w<])"
    return re.sub(pat, r"<en>\1</en>", clean)


def main():
    ap = argparse.ArgumentParser(
        description="Sinh audio/<seg_id>.wav và timing.json từ segments.json bằng VieNeu-TTS tự chạy trên máy."
    )
    ap.add_argument("lesson", help="Đường dẫn thư mục bài học (ví dụ: work/course/04-lessons/L01)")
    ap.add_argument("--voice", default=None, help="Tên giọng preset của VieNeu-TTS (mặc định: Hải Đăng)")
    ap.add_argument("--ref-audio", default=None, help="Đường dẫn file .wav mẫu (5-25s) để clone giọng giảng viên")
    ap.add_argument("--ref-text", default=None, help="Đường dẫn file .txt hoặc nội dung văn bản khớp với --ref-audio")
    ap.add_argument("--no-en-tags", action="store_true", help="Không bọc thẻ <en> cho từ tiếng Anh")
    ap.add_argument("--force", action="store_true", help="Sinh lại cả những file wav đã tồn tại")
    ap.add_argument("--config", default=None, help="Đường dẫn tới file engine.json")
    args = ap.parse_args()

    lesson_dir = pathlib.Path(args.lesson).resolve()
    cfg = load_engine_cfg(lesson_dir, args.config)

    if cfg.get("hf_home"):
        os.environ.setdefault("HF_HOME", str(resolve_path(cfg["hf_home"])))

    # Kiểm tra xem Python hiện tại có cài sẵn thư viện vieneu chưa; nếu chưa thì gọi qua vieneu_python
    try:
        from vieneu import Vieneu  # type: ignore
    except ImportError:
        vpy = cfg.get("vieneu_python")
        if not vpy:
            sys.exit("Không tìm thấy module 'vieneu' và không có 'vieneu_python' trong engine.json")
        vpy_path = resolve_path(vpy)
        if not vpy_path.exists():
            sys.exit(f"Không tìm thấy vieneu_python tại: {vpy_path}")
        cmd = [str(vpy_path), "-I", "-X", "utf8", str(pathlib.Path(__file__).resolve())] + sys.argv[1:]
        env = os.environ.copy()
        if cfg.get("hf_home"):
            env["HF_HOME"] = str(resolve_path(cfg["hf_home"]))
        res = subprocess.run(cmd, env=env)
        sys.exit(res.returncode)

    audio_dir = lesson_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    segs = json.loads((lesson_dir / "segments.json").read_text(encoding="utf-8"))
    terms = [] if args.no_en_tags else load_en_terms(lesson_dir / "pronunciation.yaml")

    ref_text_val = None
    if args.ref_audio:
        ref_audio_path = pathlib.Path(args.ref_audio).resolve()
        if args.ref_text:
            rt_path = pathlib.Path(args.ref_text)
            ref_text_val = rt_path.read_text(encoding="utf-8").strip() if rt_path.exists() else args.ref_text.strip()
        elif ref_audio_path.with_suffix(".txt").exists():
            ref_text_val = ref_audio_path.with_suffix(".txt").read_text(encoding="utf-8").strip()
        else:
            ref_text_val = "Xin chào các bạn, hôm nay chúng ta cùng tìm hiểu cách ứng dụng trí tuệ nhân tạo vào công việc hằng ngày."
        # Lưu hồ sơ giọng clone vào <course_dir>/voices/linh/
        course_dir = lesson_dir.parent.parent
        # Giọng mẫu đặt sẵn trong .../voices/<ten>/ thì giữ tên đó, tránh ghi đè hồ sơ của Linh
        voice_name = ref_audio_path.parent.name if ref_audio_path.parent.parent.name == "voices" else "linh"
        voice_dir = course_dir / "voices" / voice_name
        voice_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        if (voice_dir / ref_audio_path.name).resolve() != ref_audio_path:
            shutil.copy2(ref_audio_path, voice_dir / ref_audio_path.name)
        (voice_dir / "ref.txt").write_text(ref_text_val, encoding="utf-8")
        (voice_dir / "profile.json").write_text(
            json.dumps({"ref_audio": ref_audio_path.name, "ref_text": ref_text_val}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        kw = {"ref_audio": str(ref_audio_path), "ref_text": ref_text_val}
    else:
        kw = {"voice": args.voice or "Hải Đăng"}

    tts = None
    t0 = time.time()
    total = 0.0
    timing_items = []
    cursor = 0.0
    gap = 0.3

    missing = [s for s in segs if not (audio_dir / f"{s['seg_id']}.wav").exists() or args.force]
    if missing:
        tts = Vieneu()
        if args.ref_audio and hasattr(tts, "_enroll_reference"):
            # v3 Turbo/Nano: infer() chỉ nhận voice= hoặc ref_audio=; ref_codes/ref_text bị nuốt vào **kwargs
            # và rơi về giọng preset mặc định. Đăng ký giọng mẫu một lần rồi truyền dạng voice dict.
            speaker_emb, ref_codes = tts._enroll_reference(kw["ref_audio"], denoise=True, use_ref_codes=True)
            kw = {"voice": {"speaker_emb": speaker_emb, "codes": ref_codes}}
        elif args.ref_audio:
            ref_codes, resolved_rt = tts._resolve_ref_voice(None, kw["ref_audio"], None, kw["ref_text"])
            kw = {"ref_codes": ref_codes, "ref_text": resolved_rt}
        if hasattr(tts, "infer_batch") and not args.ref_audio:
            # Batch synthesis in groups of 11 segments (batch_size=16 chunks on 8GB VRAM)
            group_sz = 11
            for i in range(0, len(missing), group_sz):
                grp = missing[i : i + group_sz]
                texts = [tag_en(s["text"], terms) for s in grp]
                wavs = tts.infer_batch(texts, batch_size=16, **kw)
                for s, w in zip(grp, wavs):
                    out = audio_dir / f"{s['seg_id']}.wav"
                    tts.save(w, str(out))
                    print(f"[batch] {s['seg_id']} saved ({wav_dur(out):.2f}s)", flush=True)
        else:
            for s in missing:
                out = audio_dir / f"{s['seg_id']}.wav"
                tagged_text = tag_en(s["text"], terms)
                audio = tts.infer(tagged_text, **kw)
                tts.save(audio, str(out))
                print(f"[single] {s['seg_id']} saved ({wav_dur(out):.2f}s)", flush=True)

    for s in segs:
        out = audio_dir / f"{s['seg_id']}.wav"
        d = wav_dur(out)
        total += d
        timing_items.append({
            "seg_id": s["seg_id"],
            "slide": s.get("slide"),
            "click": s.get("click"),
            "start": round(cursor, 3),
            "end": round(cursor + d, 3),
            "duration": round(d, 3),
            "gap_after": gap,
        })
        cursor += d + gap
        print(s["seg_id"], f"{d:.2f}s")

    timing_data = {
        "voice": f"clone:{pathlib.Path(args.ref_audio).name}" if args.ref_audio else kw.get("voice"),
        "gap_sec": gap,
        "audio_total_sec": round(total, 3),
        "video_expected_sec": round(cursor, 3),
        "segments": timing_items,
    }
    (lesson_dir / "timing.json").write_text(json.dumps(timing_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Xong: {total:.1f}s audio ({cursor:.1f}s kèm nghỉ) trong {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
