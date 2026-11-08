"""Tính 16 chỉ số chuẩn ABC từ câu trả lời + nhãn giám khảo + tín hiệu. Thuần tính toán, giải thích được.

Công thức: CHUAN-ABC-v1.md. Thống kê Wilson theo potato; độ ổn định giữa các lượt theo potato score.py;
thị phần nhắc tên theo elmo/HeiGe (brand ÷ (brand + Σ đối thủ)).
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from abc_lib import (brand_names, classify_source, competitor_names, first_pos, fold,  # noqa: E402
                     mentions, negated_only, rate)
from nen.aeolib import extract_citations  # noqa: E402

VERDICT = {"nen_chon": 100, "co_dieu_kien": 60, "khong_nen": 0, "khong_ro": 0}
WRONG = ["sai", "nham", "bia", "cu"]
JUDGED = ["dung", "sai", "nham", "bia", "cu", "khong_biet"]

W_R = {"A1": 20, "A2": 10, "A6": 25, "A8": 10, "B3": 15, "B4": 10, "B5": 10}
W_V = {"A3": 10, "A4": 30, "A5": 15, "A9": 10, "B1": 20, "B2": 15}

STEP = {1: "Tìm", 2: "Nhận diện", 3: "Đối chiếu", 4: "Lọc theo tiêu chí", 5: "Đề xuất và giải thích"}
METRIC_STEPS = {"A1": [1], "A2": [1, 4], "A3": [2], "A4": [2, 3], "A5": [3], "A6": [5], "A7": [4], "A8": [5],
                "A9": [1, 3], "A10": [4, 5], "B1": [1, 2], "B2": [3], "B3": [3, 5], "B4": [2, 5], "B5": [4]}
NAMES = {"A1": "Có mặt", "A2": "Thị phần nhắc tên", "A3": "Nhận diện đúng", "A4": "Độ đúng", "A5": "Độ nhất quán",
         "A6": "Được đề xuất", "A7": "Khớp định vị", "A8": "Cảm nhận", "A9": "Nguồn được dẫn", "A10": "Hoàn thành tác vụ agent",
         "B1": "Sự thật có cấu trúc, máy đọc được", "B2": "Nhất quán đa kênh", "B3": "Bên thứ ba xác nhận",
         "B4": "Người thật đứng tên", "B5": "Hành vi và phản hồi", "B6": "Sẵn sàng giao dịch với agent"}


def _rows(answers, judgements, questions):
    rows = []
    for a in answers:
        j = judgements.get((a["model"], a["qid"], a["luot"]), {})
        q = questions.get(a["qid"], {})
        rows.append({**a, "j": j, "loai": q.get("loai", "branded"), "buoc": q.get("buoc"), "goc": q.get("goc", a["qid"])})
    return rows


def presence(rows, facts):
    names = brand_names(facts)
    un = [r for r in rows if r["loai"] == "unbranded"]
    # Lưới an toàn như bản IF Agent: giám khảo bỏ sót thì dò tên, trừ câu chỉ nói "không tìm thấy X".
    hit = [r for r in un if r["j"].get("mentioned") or (mentions(r["answer"], names) and not negated_only(r["answer"], names))]
    by_model = defaultdict(lambda: [0, 0])
    for r in un:
        by_model[r["model"]][1] += 1
        by_model[r["model"]][0] += r in hit
    # độ ổn định: câu (mô hình × câu) có cùng kết quả có/không ở mọi lượt
    groups = defaultdict(set)
    for r in un:
        groups[(r["model"], r["qid"])].add(r in hit)
    multi = [g for k, g in groups.items() if sum(1 for r in un if (r["model"], r["qid"]) == k) > 1]
    stable = rate(sum(1 for g in multi if len(g) == 1), len(multi))
    return rate(len(hit), len(un)) | {"theo_mo_hinh": {m: rate(k, n) for m, (k, n) in by_model.items()},
                                      "on_dinh_giua_cac_luot": stable,
                                      "bang_chung": f"AI tự nhắc tên trong {len(hit)}/{len(un)} câu trả lời cho câu hỏi chung về ngành."}


def share_of_voice(rows, facts):
    names = brand_names(facts)
    comps = competitor_names(facts)
    un = [r for r in rows if r["loai"] in ("unbranded", "so_sanh")]
    counts = Counter()
    for r in un:
        if mentions(r["answer"], names):
            counts[facts.get("brand")] += 1
        for c in comps:
            if mentions(r["answer"], [c["name"]] + c.get("aliases", [])):
                counts[c["name"]] += 1
    total = sum(counts.values())
    own = counts.get(facts.get("brand"), 0)
    # tên khác AI hay nêu mà chưa khai là đối thủ: gợi ý cho lần sau
    others = Counter(b for r in un for b in r["j"].get("brands_named", []) or []
                     if fold(b) not in {fold(n) for n in names + [c["name"] for c in comps]})
    return {"score": round(100 * own / total) if total else None, "dem": dict(counts.most_common()),
            "doi_thu_chua_khai": [b for b, _ in others.most_common(8)],
            "bang_chung": f"{own}/{total} lượt nhắc tên trong tập thương hiệu đã khai." if total else "Chưa khai đối thủ hoặc không ai được nhắc."}


def entity(rows):
    br = [r for r in rows if r["loai"] != "unbranded" and r["j"].get("entity") in ("dung", "nham", "khong_ro")]
    ok = sum(1 for r in br if r["j"]["entity"] == "dung")
    nham = sum(1 for r in br if r["j"]["entity"] == "nham")
    return rate(ok, len(br)) | {"nham_thuc_the": nham, "bang_chung": f"Nhận đúng thực thể {ok}/{len(br)} lượt; nhầm {nham}."}


def accuracy(rows):
    c = Counter(cl.get("label", "chua_kiem") for r in rows for cl in r["j"].get("claims", []) or [])
    judged = sum(c[k] for k in JUDGED)
    return rate(c["dung"], judged) | {"nhan": {k: c.get(k, 0) for k in JUDGED + ["chua_kiem"]},
                                       "bang_chung": (f"{c['dung']}/{judged} ý đúng; {c['sai']} sai, {c['nham']} nhầm, {c['bia']} bịa, {c['cu']} cũ, {c['khong_biet']} không biết."
                                                      if judged else "Chưa đối chiếu được: cần bảng sự thật.")}


def consistency(rows):
    by_fact = defaultdict(list)
    for r in rows:
        for cl in r["j"].get("claims", []) or []:
            if cl.get("fact_id") and cl.get("value") and cl.get("label") != "khong_biet":
                by_fact[cl["fact_id"]].append(fold(str(cl["value"]))[:40])
    parts = {}
    for fid, vals in by_fact.items():
        if len(vals) < 2:
            continue
        top = Counter(vals).most_common(1)[0][1]
        parts[fid] = round(100 * top / len(vals))
    score = round(sum(parts.values()) / len(parts)) if parts else None
    lech = sorted(parts.items(), key=lambda x: x[1])[:5]
    return {"score": score, "theo_dong": parts,
            "bang_chung": (f"Trung bình {score}% câu trả lời cho cùng giá trị ở {len(parts)} dữ kiện cốt lõi; lệch nhất: "
                           + ", ".join(f"{k} {v}%" for k, v in lech)) if parts else "Chưa đủ câu trả lời nêu cùng dữ kiện để so."}


def recommendation(rows):
    recs = [r for r in rows if r["j"].get("verdict") in VERDICT]
    scores = [VERDICT[r["j"]["verdict"]] * (0.5 if any(x.get("label") == "sai" for x in r["j"].get("reasons", []) or []) else 1) for r in recs]
    yes = sum(1 for r in recs if r["j"]["verdict"] in ("nen_chon", "co_dieu_kien"))
    return {"score": round(sum(scores) / len(scores)) if scores else None, "n": len(recs),
            "bang_chung": f"AI khuyên chọn (kể cả có điều kiện) ở {yes}/{len(recs)} câu trả lời có lời khuyên."}


def positioning(rows, facts):
    pos = facts.get("positioning", [])
    if not pos:
        return {"score": None, "bang_chung": "Chưa khai thuộc tính định vị."}
    hit = {h for r in rows for h in r["j"].get("positioning_hit", []) or []}
    other = Counter(a for r in rows for a in r["j"].get("attributes_other", []) or [])
    ids = [f"d{i + 1}" for i in range(len(pos))]
    return {"score": round(100 * len(hit & set(ids)) / len(ids)),
            "co": [pos[int(i[1:]) - 1] for i in ids if i in hit], "thieu": [pos[int(i[1:]) - 1] for i in ids if i not in hit],
            "ai_gan_them": [a for a, _ in other.most_common(8)],
            "bang_chung": f"AI nhắc {len(hit & set(ids))}/{len(ids)} thuộc tính định vị đã khai."}


def sentiment(rows):
    s = [r["j"]["sentiment"] for r in rows if r["j"].get("sentiment") in (-1, 0, 1)]
    neg = sum(1 for x in s if x == -1)
    return {"score": round(50 * (sum(s) / len(s) + 1)) if s else None, "n": len(s),
            "bang_chung": f"{len(s)} câu trả lời có nhắc; {neg} câu giọng tiêu cực."}


def citations(rows, facts):
    srcs = []
    for r in rows:
        urls = [s.get("url") for s in r["sources"]] + extract_citations(r["answer"])
        titles = [s.get("title") for s in r["sources"] if s.get("title")]
        kinds = {classify_source(u, facts) for u in urls if u and "vertexaisearch" not in u}
        kinds |= {classify_source("https://" + t, facts) for t in titles if "." in t}
        if kinds:
            srcs.append(kinds)
    mix = Counter(k for ks in srcs for k in ks)
    own = sum(1 for ks in srcs if "cua_minh" in ks)
    return rate(own, len(srcs)) | {"co_cau_nguon": dict(mix.most_common()),
                                    "bang_chung": f"Trang chính thức được dẫn ở {own}/{len(srcs)} câu trả lời có nguồn." if srcs else "Không câu trả lời nào có nguồn (chạy mô hình có tra web để đo)."}


def task_success(rows):
    t = [r for r in rows if r["loai"] == "agent_task" and isinstance(r["j"].get("task"), dict) and r["j"]["task"].get("ok") is not None]
    ok = sum(1 for r in t if r["j"]["task"]["ok"] and r["j"]["task"].get("constraints_ok") is not False)
    gay = Counter(r["j"]["task"].get("break_point") for r in t if r["j"]["task"].get("break_point"))
    return rate(ok, len(t)) | {"diem_gay": [b for b, _ in gay.most_common(5)],
                                "bang_chung": f"Agent làm đúng và tôn trọng ràng buộc ở {ok}/{len(t)} tác vụ."}


def wrong_list(rows):
    out = []
    for r in rows:
        for c in r["j"].get("claims", []) or []:
            if c.get("label") in WRONG:
                out.append({"mo_hinh": r["model"], "cau_hoi": r["question"], "claim": c.get("claim"), "nhan": c["label"],
                            "dinh_chinh": c.get("correction", ""), "file": r["file"]})
    return out


def _combine(m, weights):
    have = {k: w for k, w in weights.items() if m.get(k, {}).get("score") is not None}
    tot = sum(have.values())
    return (round(sum(m[k]["score"] * w for k, w in have.items()) / tot) if tot else None), sorted(set(weights) - set(have))


def grade(x):
    if x is None:
        return "?"
    return "A" if x >= 80 else "B" if x >= 65 else "C" if x >= 50 else "D" if x >= 35 else "E"


def score_all(facts, answers, judgements, questions, signals):
    rows = _rows(answers, judgements, questions)
    m = {"A1": presence(rows, facts), "A2": share_of_voice(rows, facts), "A3": entity(rows), "A4": accuracy(rows),
         "A5": consistency(rows), "A6": recommendation(rows), "A7": positioning(rows, facts), "A8": sentiment(rows),
         "A9": citations(rows, facts), "A10": task_success(rows)}
    for k in ("B1", "B2", "B3", "B4", "B5", "B6"):
        m[k] = {"score": (signals.get(k) or {}).get("score"), "bang_chung": (signals.get(k) or {}).get("ghi_chu", "chưa kiểm")}
    for k in m:
        m[k]["ten"] = NAMES[k]
    R, r_miss = _combine(m, W_R)
    V, v_miss = _combine(m, W_V)
    avi = round((R * V) ** 0.5) if R is not None and V is not None else None
    steps = {}
    for s in STEP:
        vals = [m[k]["score"] for k, ss in METRIC_STEPS.items() if s in ss and m[k]["score"] is not None]
        steps[s] = {"ten": STEP[s], "score": round(sum(vals) / len(vals)) if vals else None}
    weakest = min((s for s in steps if steps[s]["score"] is not None), key=lambda s: steps[s]["score"], default=None)
    wrong = wrong_list(rows)
    flags = []
    if m["A3"].get("nham_thuc_the"):
        flags.append("Nhầm thực thể: AI nhận nhầm thương hiệu sang công ty khác.")
    forb = [f for r in rows for f in r["j"].get("forbidden", []) or []]
    if forb:
        flags.append(f"AI lặp claim thương hiệu tự cấm: {', '.join(sorted(set(forb))[:3])}.")
    if (signals.get("B1") or {}).get("bot_bi_chan"):
        flags.append("Website chặn bot AI: " + ", ".join(signals["B1"]["bot_bi_chan"][:6]) + ".")
    if m["A1"]["score"] is not None and m["A1"]["score"] < 34:
        flags.append("Vô hình: AI hiếm khi tự nhắc tới bạn khi khách hỏi chung về ngành.")
    models = sorted({r["model"] for r in rows})
    return {"chi_so": m, "reputation": R, "verifiable": V, "avi": avi, "hang": grade(avi),
            "thieu_de_tinh": {"R": r_miss, "V": v_miss}, "buoc_agent": steps,
            "roi_o_buoc": weakest, "co_do": flags, "noi_sai": wrong,
            "pham_vi": {"mo_hinh": models, "so_cau_tra_loi": len(rows),
                        "so_luot_toi_da": max((r["luot"] for r in rows), default=0),
                        "da_cham": sum(1 for r in rows if r["j"])}}
