"""Ghép bài giảng: segments.json + frames/ + audio/<seg>.wav [+ avatar.mp4] -> lesson.mp4 + lesson.vtt + narration.wav + timing.json.
Giọng là đồng hồ chủ: mỗi khung hiện đúng bằng thời lượng audio của đoạn đó + khoảng nghỉ.
Chuẩn hoá âm lượng tích hợp về -16 LUFS (nằm trong khoảng -18..-14 LUFS).
"""
import argparse
import json
import pathlib
import subprocess
import sys
import wave

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def dur(p: pathlib.Path) -> float:
    with wave.open(str(p), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def ts(t: float) -> str:
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def main():
    ap = argparse.ArgumentParser(
        description="Ghép khung slide PNG, audio từng đoạn và avatar (tuỳ chọn) thành video bài giảng 1920x1080 kèm phụ đề VTT."
    )
    ap.add_argument("lesson", help="Đường dẫn thư mục bài học (ví dụ: work/course/04-lessons/L01)")
    ap.add_argument("--avatar", default=None, help="Đường dẫn file avatar.mp4 để chèn góc dưới phải")
    ap.add_argument("--gap", type=float, default=0.3, help="Khoảng nghỉ giữa hai đoạn âm thanh (giây, mặc định: 0.3)")
    ap.add_argument("--out", default="build", help="Tên thư mục con chứa kết quả dựng (mặc định: build)")
    ap.add_argument("--out-name", default=None, help="Tên file MP4 đầu ra (mặc định: lesson.mp4, hoặc lesson-avatar.mp4 khi có --avatar)")
    args = ap.parse_args()

    lesson_dir = pathlib.Path(args.lesson).resolve()
    out = lesson_dir / args.out
    out.mkdir(parents=True, exist_ok=True)
    segs = json.loads((lesson_dir / "segments.json").read_text(encoding="utf-8"))

    lst, vtt, t, alist, timing_items = [], ["WEBVTT", ""], 0.0, [], []
    audio_total = 0.0
    for s in segs:
        wav = lesson_dir / "audio" / f"{s['seg_id']}.wav"
        raw_d = dur(wav)
        audio_total += raw_d
        d = raw_d + args.gap
        png_path = (lesson_dir / "frames" / s["png"]).resolve().as_posix()
        lst += [f"file '{png_path}'", f"duration {d:.3f}"]
        alist += [f"file '{wav.resolve().as_posix()}'"]
        clean_sub = s["text"].replace("<en>", "").replace("</en>", "")
        vtt += [f"{ts(t)} --> {ts(t + raw_d)}", clean_sub, ""]
        timing_items.append({
            "seg_id": s["seg_id"],
            "slide": s.get("slide"),
            "click": s.get("click"),
            "start": round(t, 3),
            "end": round(t + raw_d, 3),
            "duration": round(raw_d, 3),
            "gap_after": args.gap,
        })
        t += d

    lst.append(lst[-2])  # concat demuxer cần lặp khung cuối
    (out / "frames.txt").write_text("\n".join(lst), encoding="utf-8")
    (out / "audio.txt").write_text("\n".join(alist), encoding="utf-8")
    (out / "lesson.vtt").write_text("\n".join(vtt), encoding="utf-8")

    timing_path = lesson_dir / "timing.json"
    timing_data = {
        "gap_sec": args.gap,
        "audio_total_sec": round(audio_total, 3),
        "video_expected_sec": round(t, 3),
        "segments": timing_items,
    }
    timing_path.write_text(json.dumps(timing_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Nối từng đoạn kèm khoảng nghỉ, chuẩn hoá loudness -16 LUFS
    pad = f"apad=pad_dur={args.gap}"
    parts = []
    for i, s in enumerate(segs):
        wav = lesson_dir / "audio" / f"{s['seg_id']}.wav"
        p = out / f"a{i:03d}.wav"
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-af", pad, "-ar", "48000", "-ac", "1", str(p)],
            check=True,
        )
        parts.append(f"file '{p.resolve().as_posix()}'")

    (out / "apad.txt").write_text("\n".join(parts), encoding="utf-8")
    narration_wav = out / "narration.wav"
    subprocess.run(
        [
            "ffmpeg", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(out / "apad.txt"),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:linear=false",
            "-ar", "48000", str(narration_wav),
        ],
        check=True,
    )

    out_name = args.out_name or ("lesson-avatar.mp4" if args.avatar else "lesson.mp4")
    target_mp4 = out / out_name

    avatar_input = None
    temp_av_files = []
    if args.avatar:
        av_candidates = []
        for part in str(args.avatar).split(","):
            part_p = pathlib.Path(part.strip()).resolve()
            if part_p.is_dir():
                av_candidates.extend(sorted(part_p.glob("*.mp4")))
            elif part_p.exists():
                av_candidates.append(part_p)
        if not av_candidates:
            sys.exit(f"Không tìm thấy file avatar tại: {args.avatar}")

        if len(av_candidates) == 1:
            avatar_input = av_candidates[0]
        else:
            # Nhóm thời lượng theo từng slide để đổi góc chụp/trang phục giảng viên qua mỗi slide
            slide_durs = []
            for item in timing_items:
                s_idx = item.get("slide") or 1
                seg_total = float(item["duration"]) + float(item["gap_after"])
                if slide_durs and slide_durs[-1][0] == s_idx:
                    slide_durs[-1][1] += seg_total
                else:
                    slide_durs.append([s_idx, seg_total])

            av_concat_lines = []
            for idx, (s_idx, s_dur) in enumerate(slide_durs):
                chosen_av = av_candidates[idx % len(av_candidates)]
                chunk_mp4 = out / f"_av_slide_{idx:03d}.mp4"
                temp_av_files.append(chunk_mp4)
                subprocess.run(
                    [
                        "ffmpeg", "-loglevel", "error", "-y",
                        "-stream_loop", "-1", "-i", str(chosen_av),
                        "-t", f"{s_dur:.3f}",
                        "-vf", "crop='min(iw,ih)':'min(iw,ih)',scale=340:340,fps=25",
                        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                        str(chunk_mp4),
                    ],
                    check=True,
                )
                av_concat_lines.append(f"file '{chunk_mp4.resolve().as_posix()}'")

            av_list_txt = out / "_av_concat.txt"
            temp_av_files.append(av_list_txt)
            av_list_txt.write_text("\n".join(av_concat_lines), encoding="utf-8")
            avatar_track = out / "_avatar_track.mp4"
            temp_av_files.append(avatar_track)
            subprocess.run(
                [
                    "ffmpeg", "-loglevel", "error", "-y",
                    "-f", "concat", "-safe", "0", "-i", str(av_list_txt),
                    "-c", "copy", str(avatar_track),
                ],
                check=True,
            )
            avatar_input = avatar_track

    cmd = [
        "ffmpeg", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", str(out / "frames.txt"),
        "-i", str(narration_wav),
    ]
    if avatar_input:
        cmd += [
            "-stream_loop", "-1", "-i", str(avatar_input.resolve()),
            "-filter_complex",
            "[2:v]crop='min(iw,ih)':'min(iw,ih)',scale=340:340,format=rgba,"
            "geq=r='if(between(hypot(X-170,Y-170),162,168),163,r(X,Y))':"
            "g='if(between(hypot(X-170,Y-170),162,168),211,g(X,Y))':"
            "b='if(between(hypot(X-170,Y-170),162,168),79,b(X,Y))':"
            "a='if(lte(hypot(X-170,Y-170),168),255,0)'[av];"
            "[0:v]scale=1920:1080,fps=25[bg];[bg][av]overlay=W-w-44:H-h-44:shortest=1[v]",
            "-map", "[v]", "-map", "1:a",
        ]
    else:
        cmd += ["-vf", "scale=1920:1080,fps=25", "-map", "0:v", "-map", "1:a"]

    cmd += [
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", "-shortest", str(target_mp4),
    ]
    subprocess.run(cmd, check=True)

    # Dọn các file trung gian a000.wav và _av_slide_*.mp4 để thư mục build gọn gàng
    for i in range(len(segs)):
        p = out / f"a{i:03d}.wav"
        if p.exists():
            p.unlink()
    for p in temp_av_files:
        if p.exists():
            p.unlink()

    print(f"{target_mp4}  {t:.1f}s  {len(segs)} đoạn")


if __name__ == "__main__":
    main()
