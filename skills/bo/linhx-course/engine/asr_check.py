"""Kiểm lời tự động bằng mô hình ASR mã nguồn mở chạy trên máy (faster-whisper hoặc transformers Whisper).
Nhận dạng từng file audio/<seg_id>.wav, ghi 04-lessons/<L>/asr.json với văn bản thô từ model,
và tính sai số ký tự (CER) để phát hiện các đoạn đọc sai (CER > 0.30).
"""
import argparse
import json
import os
import pathlib
import re
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


def cer(a: str, b: str) -> float:
    a_clean = re.sub(r"\W", "", a.lower())
    b_clean = re.sub(r"\W", "", b.lower())
    prev = list(range(len(b_clean) + 1))
    for i, x in enumerate(a_clean, 1):
        cur = [i]
        for j, y in enumerate(b_clean, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1] / max(len(a_clean), 1)


def main():
    ap = argparse.ArgumentParser(
        description="Nhận dạng giọng nói từng đoạn audio/<seg_id>.wav bằng Whisper, ghi asr.json và tính CER."
    )
    ap.add_argument("lesson", help="Đường dẫn thư mục bài học (ví dụ: work/course/04-lessons/L01)")
    ap.add_argument("--model", default="small", help="Tên model faster-whisper hoặc HF Whisper (mặc định: small)")
    ap.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"], help="Thiết bị chạy ASR")
    ap.add_argument("--config", default=None, help="Đường dẫn tới file engine.json")
    args = ap.parse_args()

    lesson_dir = pathlib.Path(args.lesson).resolve()
    cfg = load_cfg(lesson_dir, args.config)

    if cfg.get("hf_home"):
        os.environ.setdefault("HF_HOME", str(resolve_path(cfg["hf_home"])))

    # Kiểm tra môi trường có faster_whisper hoặc torch+transformers chưa; nếu chưa thì chuyển sang vieneu_python
    has_asr = False
    try:
        import faster_whisper  # noqa: F401
        has_asr = True
    except ImportError:
        try:
            import torch  # noqa: F401
            import transformers  # noqa: F401
            has_asr = True
        except ImportError:
            has_asr = False

    if not has_asr:
        vpy = cfg.get("vieneu_python")
        if vpy:
            vpy_path = resolve_path(vpy)
            if vpy_path.exists() and pathlib.Path(sys.executable).resolve() != vpy_path.resolve():
                env = os.environ.copy()
                if cfg.get("hf_home"):
                    env["HF_HOME"] = str(resolve_path(cfg["hf_home"]))
                cmd = [str(vpy_path), "-I", "-X", "utf8", str(pathlib.Path(__file__).resolve())] + sys.argv[1:]
                res = subprocess.run(cmd, env=env)
                sys.exit(res.returncode)
        sys.exit("Thiếu thư viện ASR (faster-whisper hoặc transformers+torch).")

    segs = json.loads((lesson_dir / "segments.json").read_text(encoding="utf-8"))
    audio_dir = lesson_dir / "audio"

    t0 = time.time()
    results = []
    model_label = args.model

    try:
        from faster_whisper import WhisperModel  # type: ignore
        import librosa
        import numpy as np
        import soundfile as sf
        import torch
        dev = ("cuda" if torch.cuda.is_available() else "cpu") if args.device == "auto" else args.device
        ctype = "float16" if dev == "cuda" else "int8"
        cache_root = str(resolve_path(cfg.get("hf_home", "local/.hf")))
        wmodel = WhisperModel(args.model, device=dev, compute_type=ctype, download_root=cache_root)
        model_label = f"faster-whisper-{args.model} ({dev}/{ctype})"
        for s in segs:
            wav = audio_dir / f"{s['seg_id']}.wav"
            speech, sr = sf.read(str(wav), dtype="float32")
            if speech.ndim > 1:
                speech = speech.mean(axis=1)
            if sr != 16000:
                speech = librosa.resample(speech, orig_sr=sr, target_sr=16000).astype(np.float32)
            segments_gen, _ = wmodel.transcribe(speech, language="vi", beam_size=5, vad_filter=False)
            hyp_text = " ".join(seg.text.strip() for seg in segments_gen).strip()
            results.append({"seg_id": s["seg_id"], "hyp": hyp_text})
    except ImportError:
        import torch
        import soundfile as sf
        import librosa
        from transformers import pipeline
        dev = (0 if torch.cuda.is_available() else -1) if args.device == "auto" else (0 if args.device == "cuda" else -1)
        hf_model = args.model if "/" in args.model else f"openai/whisper-{args.model}"
        dtype = torch.float16 if dev == 0 else torch.float32
        asr_pipe = pipeline(
            "automatic-speech-recognition",
            model=hf_model,
            device=dev,
            torch_dtype=dtype,
        )
        model_label = f"{hf_model} ({'cuda' if dev == 0 else 'cpu'})"
        for s in segs:
            wav = audio_dir / f"{s['seg_id']}.wav"
            speech, sr = sf.read(str(wav))
            if speech.ndim > 1:
                speech = speech.mean(axis=1)
            if sr != 16000:
                speech = librosa.resample(speech, orig_sr=sr, target_sr=16000)
            out = asr_pipe(
                {"raw": speech, "sampling_rate": 16000},
                generate_kwargs={"language": "vi", "task": "transcribe"},
            )
            hyp_text = out["text"].strip()
            results.append({"seg_id": s["seg_id"], "hyp": hyp_text})

    out_json = {"model": model_label, "segments": results}
    (lesson_dir / "asr.json").write_text(json.dumps(out_json, ensure_ascii=False, indent=2), encoding="utf-8")

    # Tính và in CER để kiểm tra
    ref_map = {s["seg_id"]: re.sub(r"<[^>]+>", "", s["text"]) for s in segs}
    cer_list = []
    high_cer = []
    for item in results:
        sid = item["seg_id"]
        c = cer(ref_map[sid], item["hyp"])
        cer_list.append(c)
        if c > 0.30:
            high_cer.append((sid, c, ref_map[sid], item["hyp"]))

    avg_cer = sum(cer_list) / max(len(cer_list), 1)
    print(f"Xong ASR ({model_label}) trong {time.time() - t0:.1f}s | CER trung bình: {avg_cer:.3f} ({len(results)} đoạn)")
    if high_cer:
        print(f"CẢNH BÁO: Có {len(high_cer)} đoạn CER > 0.30:")
        for sid, c, r_txt, h_txt in high_cer:
            print(f"  - {sid} (CER={c:.2f}):\n      REF: {r_txt}\n      HYP: {h_txt}")


if __name__ == "__main__":
    main()
