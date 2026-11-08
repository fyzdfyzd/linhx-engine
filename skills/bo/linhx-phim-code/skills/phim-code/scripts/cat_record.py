#!/usr/bin/env python3
"""Cắt phần hư, làm lại, ậm ờ khỏi file record; ra video sạch + phụ đề theo từng chữ.

Dùng:
  python3 cat_record.py record.mp4 out/            # tự chép lời bằng faster-whisper (cần cài)
  python3 cat_record.py record.mp4 out/ --words words.json   # đã có lời theo từng chữ
  python3 cat_record.py record.mp4 out/ --chi-xem  # chỉ ra cat.json để xem, chưa cắt

words.json: [{"w": "xin", "s": 0.12, "e": 0.40}, ...] (giây).
Ra trong out/: words.json, cat.json (đoạn giữ, đoạn bỏ và lý do), sach.mp4,
phu-de.json (chữ đã dời giờ theo video sạch, cho HyperFrames), phu-de.srt.
"""
import argparse, json, os, re, subprocess, sys

DEM = {"ờ", "ơ", "ừ", "ừm", "ờm", "ơm", "à", "ầm", "hmm", "ừa", "uh", "um", "ah", "eh"}
LAM_LAI = ("làm lại", "quay lại", "nói lại", "cắt đoạn", "cắt cắt", "lại nhé", "sai rồi")
NGAT = 0.6      # im lặng dài hơn thế này thì tách câu
GIU_IM = 0.25   # chừa lại bao nhiêu giây im lặng ở mỗi chỗ cắt
TRUNG = 3       # số chữ đầu trùng thì coi câu trước là bản hỏng


def chuan(w):
    return re.sub(r"[^\wÀ-ỹ]", "", w.lower())


def chep_loi(video):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("Chưa có faster-whisper: pip install faster-whisper (hoặc đưa --words)")
    m = WhisperModel(os.environ.get("WHISPER_MODEL", "large-v3"), compute_type="auto")
    segs, _ = m.transcribe(video, language="vi", word_timestamps=True, vad_filter=True)
    return [{"w": x.word.strip(), "s": round(x.start, 3), "e": round(x.end, 3)}
            for s in segs for x in (s.words or []) if x.word.strip()]


def tach_cau(words):
    cau, cur = [], []
    for w in words:
        if cur and w["s"] - cur[-1]["e"] > NGAT:
            cau.append(cur); cur = []
        cur.append(w)
    if cur:
        cau.append(cur)
    return cau


def danh_dau(cau):
    """Trả về list (câu, lý do bỏ hoặc None)."""
    out = []
    for i, c in enumerate(cau):
        text = " ".join(chuan(w["w"]) for w in c)
        ly_do = None
        if any(k in text for k in LAM_LAI):
            ly_do = "có lời làm lại"
            if out and out[-1][1] is None:
                out[-1] = (out[-1][0], "câu trước lời làm lại")
        elif i + 1 < len(cau):
            a = [chuan(w["w"]) for w in c if chuan(w["w"]) not in DEM][:TRUNG]
            b = [chuan(w["w"]) for w in cau[i + 1] if chuan(w["w"]) not in DEM][:TRUNG]
            if len(a) == TRUNG and a == b:
                ly_do = "nói lại ở câu sau"
        if ly_do is None and all(chuan(w["w"]) in DEM for w in c):
            ly_do = "chỉ ậm ờ"
        out.append((c, ly_do))
    return out


def doan_giu(marked):
    giu = []
    for c, ly_do in marked:
        if ly_do:
            continue
        vua_bo = True
        for w in c:
            if chuan(w["w"]) in DEM:
                vua_bo = True
                if giu:
                    giu[-1][1] = min(giu[-1][1], w["s"])
                continue
            s, e = max(0, w["s"] - GIU_IM / 2), w["e"] + GIU_IM / 2
            if giu and not vua_bo and s - giu[-1][1] <= GIU_IM:
                giu[-1][1] = max(giu[-1][1], e)
            else:
                giu.append([max(s, giu[-1][1]) if giu else s, e])
            vua_bo = False
    return [[round(s, 3), round(e, 3)] for s, e in giu]


def doi_gio(words, giu):
    out, bu = [], 0.0
    for s, e in giu:
        for w in words:
            if w["s"] >= s and w["e"] <= e and chuan(w["w"]) not in DEM:
                out.append({"w": w["w"], "s": round(w["s"] - s + bu, 3), "e": round(w["e"] - s + bu, 3)})
        bu += e - s
    return out


def srt(words, n=7):
    def t(x):
        h, r = divmod(x, 3600); m, s = divmod(r, 60)
        return f"{int(h):02}:{int(m):02}:{int(s):02},{int(round((s % 1) * 1000)):03}"
    lines = []
    for i in range(0, len(words), n):
        g = words[i:i + n]
        lines.append(f"{len(lines) + 1}\n{t(g[0]['s'])} --> {t(g[-1]['e'])}\n{' '.join(w['w'] for w in g)}\n")
    return "\n".join(lines)


def cat_video(video, giu, dst):
    parts = "".join(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS[a{i}];"
                    for i, (s, e) in enumerate(giu))
    parts += "".join(f"[v{i}][a{i}]" for i in range(len(giu))) + f"concat=n={len(giu)}:v=1:a=1[v][a]"
    fs = dst + ".filter.txt"
    open(fs, "w", encoding="utf-8").write(parts)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-filter_complex_script", fs,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", dst], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--words"); ap.add_argument("--chi-xem", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    words = json.load(open(a.words, encoding="utf-8")) if a.words else chep_loi(a.video)
    json.dump(words, open(f"{a.out}/words.json", "w", encoding="utf-8"), ensure_ascii=False)
    marked = danh_dau(tach_cau(words))
    giu = doan_giu(marked)
    bo = [{"tu": c[0]["s"], "den": c[-1]["e"], "ly_do": l, "loi": " ".join(w["w"] for w in c)} for c, l in marked if l]
    goc = words[-1]["e"] if words else 0
    con = sum(e - s for s, e in giu)
    json.dump({"giu": giu, "bo": bo, "goc_giay": goc, "con_giay": round(con, 2)},
              open(f"{a.out}/cat.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Bỏ {len(bo)} câu, giữ {len(giu)} đoạn, {goc:.1f}s → {con:.1f}s. Xem {a.out}/cat.json")
    if a.chi_xem:
        return
    pd = doi_gio(words, giu)
    json.dump(pd, open(f"{a.out}/phu-de.json", "w", encoding="utf-8"), ensure_ascii=False)
    open(f"{a.out}/phu-de.srt", "w", encoding="utf-8").write(srt(pd))
    cat_video(a.video, giu, f"{a.out}/sach.mp4")
    print(f"Xong: {a.out}/sach.mp4, phu-de.json, phu-de.srt")


if __name__ == "__main__":
    main()
