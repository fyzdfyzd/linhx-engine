#!/usr/bin/env python3
"""Giọng Việt cho phim-code: loi.json -> <id>.wav, giong.wav, dur.json, cues.json, phu-de.srt.

loi.json = [{"id": "c01", "text": "chữ hiện phụ đề", "say": "cách đọc (tuỳ chọn)", "nghi": 0.5}]
Dùng edge-tts (cần mạng). --nhap: không gọi mạng, ước thời lượng, tạo tiếng im.
"""
import argparse, asyncio, hashlib, json, os, re, subprocess, sys, wave

GIONG = {"nu": "vi-VN-HoaiMyNeural", "nam": "vi-VN-NamMinhNeural"}
SR = 24000


def ffprobe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(out.stdout.strip())


def silence(path, sec):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"\x00\x00" * int(sec * SR))


def uoc_luong(text):
    am_tiet = len(re.findall(r"\w+", text))
    return max(1.0, am_tiet / 4.2 + 0.3)


async def doc(text, voice, rate, pitch, mp3):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(mp3)


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("loi"); ap.add_argument("out")
    ap.add_argument("--giong", default="nu", help="nu | nam | tên giọng edge-tts")
    ap.add_argument("--toc", default="+0%"); ap.add_argument("--cao", default="+0Hz")
    ap.add_argument("--nghi", type=float, default=0.35, help="giây nghỉ giữa hai câu")
    ap.add_argument("--dau", type=float, default=0.3, help="giây im đầu phim")
    ap.add_argument("--nhap", action="store_true", help="không gọi mạng, ước thời lượng")
    a = ap.parse_args()

    lines = json.load(open(a.loi, encoding="utf-8"))
    voice = GIONG.get(a.giong, a.giong)
    os.makedirs(os.path.join(a.out, ".cache"), exist_ok=True)
    dur, cues, parts, t = {}, [], [], a.dau
    gap0 = os.path.join(a.out, ".cache", "dau.wav"); silence(gap0, a.dau); parts.append(gap0)

    for ln in lines:
        lid, text = ln["id"], ln["text"]; say = ln.get("say", text)
        wav = os.path.join(a.out, f"{lid}.wav")
        if a.nhap:
            d = uoc_luong(say); silence(wav, d)
        else:
            key = hashlib.sha1(f"{say}|{voice}|{a.toc}|{a.cao}".encode()).hexdigest()[:16]
            mp3 = os.path.join(a.out, ".cache", f"{key}.mp3")
            if not os.path.exists(mp3):
                try:
                    asyncio.run(doc(say, voice, a.toc, a.cao, mp3))
                except Exception as e:
                    sys.exit(f"edge-tts lỗi ở câu {lid}: {e}\nKhông có mạng tới Microsoft thì chạy lại với --nhap.")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ac", "1", "-ar", str(SR), wav], check=True)
            d = ffprobe_dur(wav)
        dur[lid] = round(d, 3)
        cues.append({"id": lid, "t0": round(t, 3), "t1": round(t + d, 3), "text": text})
        parts.append(wav)
        nghi = ln.get("nghi", a.nghi)
        g = os.path.join(a.out, ".cache", f"nghi-{lid}.wav"); silence(g, nghi); parts.append(g)
        t += d + nghi

    lst = os.path.join(a.out, ".cache", "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-ac", "1", "-ar", str(SR), os.path.join(a.out, "giong.wav")], check=True)

    json.dump(dur, open(os.path.join(a.out, "dur.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(cues, open(os.path.join(a.out, "cues.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(a.out, "phu-de.srt"), "w", encoding="utf-8") as f:
        for i, c in enumerate(cues, 1):
            f.write(f"{i}\n{srt_time(c['t0'])} --> {srt_time(c['t1'] + 0.4)}\n{c['text']}\n\n")
    print(f"{'NHÁP ' if a.nhap else ''}{len(cues)} câu, tổng {t:.2f} giây, giọng {voice} -> {a.out}")


if __name__ == "__main__":
    main()
