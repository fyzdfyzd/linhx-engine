"""Tự kiểm: chạy trọn khoi-tao → cau-hoi → (câu trả lời + nhãn giả) → tin-hieu offline → bao-cao. Không gọi mạng."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from abc_cham import parse_json  # noqa: E402
from abc_lib import classify_source, load_json, mentions, negated_only, save_json, wilson  # noqa: E402
from nen.aeoweb import bot_status  # noqa: E402

FAIL: list[str] = []


def check(name, cond):
    print(("  ✓ " if cond else "  ✗ ") + name)
    if not cond:
        FAIL.append(name)


def unit():
    print("Đơn vị")
    check("dò tên có dấu", mentions("Tôi gợi ý **Sữa Mộc Châu** và TH true MILK.", ["Sữa Mộc Châu"]))
    check("dò tên không dấu", mentions("nen chon sua moc chau", ["Sữa Mộc Châu"]))
    check("không khớp nửa từ", not mentions("Vinamilkx là ...", ["Vinamilk"]))
    check("câu phủ định không tính", negated_only("Tôi không tìm thấy thông tin về Mẫu Việt.", ["Mẫu Việt"]))
    lo, hi = wilson(5, 10)
    check("Wilson 5/10 ≈ [24,76]", round(lo * 100) == 24 and round(hi * 100) == 76)
    check("robots chặn GPTBot", not bot_status("User-agent: GPTBot\nDisallow: /", "GPTBot")["allowed"])
    f = {"website": "mauviet.vn", "competitors": [{"name": "Đối thủ", "domain": "doithu.vn"}]}
    check("nguồn của mình", classify_source("https://www.mauviet.vn/a", f) == "cua_minh")
    check("nguồn báo chí", classify_source("https://vnexpress.net/x", f) == "bao_chi")
    check("nguồn đối thủ", classify_source("https://doithu.vn", f) == "doi_thu")
    check("đọc JSON giám khảo có rác quanh", parse_json('ok ```json {"mentioned": true, "claims": [{"label": "xyz"}]} ```')["claims"][0]["label"] == "chua_kiem")


def answer(qid, model, luot, text, src=""):
    return f"ID: {qid}\nPROMPT: q\nMODEL: {model}\nDATE: 2026-10-14\n{'=' * 60}\n\n{text}\n{src}\n"


def e2e():
    print("Trọn luồng (dữ liệu giả)")
    with tempfile.TemporaryDirectory() as t:
        ws = Path(t) / "mau-viet"
        cli = [sys.executable, str(HERE / "brandcheck.py")]
        run = lambda *a: subprocess.run(cli + list(a), capture_output=True, text=True, encoding="utf-8")  # noqa: E731
        r = run("khoi-tao", "-w", str(ws), "--brand", "Mẫu Việt", "--website", "mauviet.vn", "--category", "sữa tươi")
        check("khoi-tao", r.returncode == 0)
        f = load_json(ws / "brand-facts.json")
        f.update({"aliases": ["Mau Viet"], "competitors": [{"name": "Sữa Đối Thủ", "domain": "doithu.vn"}],
                  "positioning": ["sữa sạch từ trang trại", "giá vừa túi tiền"], "channels": []})
        save_json(ws / "brand-facts.json", f)
        r = run("cau-hoi", "-w", str(ws), "--goi", "N")
        check("cau-hoi gói Nhanh 12 câu", r.returncode == 0 and len(load_json(ws / "cau-hoi.json")) == 12)
        qs = {q["id"]: q for q in load_json(ws / "cau-hoi.json")}
        lan = ws / "lan" / "2026-10-14"
        for m in ("gia-a", "gia-b"):
            for luot in (1, 2):
                for qid, q in qs.items():
                    if q["loai"] == "unbranded":
                        txt = "Gợi ý: Mẫu Việt, Sữa Đối Thủ." if (m == "gia-a" or luot == 1) else "Gợi ý: Sữa Đối Thủ."
                        src = "[nguon] vnexpress.net | https://vnexpress.net/sua"
                    else:
                        txt, src = "Mẫu Việt thành lập năm 2015, trụ sở Quận 3.", "[nguon] mauviet.vn | https://mauviet.vn"
                    p = lan / "tra-loi" / m / f"{qid}__l{luot}.md"
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(answer(qid, m, luot, txt, src), encoding="utf-8")
                    j = {"mentioned": "Mẫu Việt" in txt, "brands_named": ["Mẫu Việt", "Sữa Đối Thủ", "Hãng Lạ"],
                         "entity": "khong_ap_dung" if q["loai"] == "unbranded" else "dung",
                         "claims": [] if q["loai"] == "unbranded" else [
                             {"claim": "thành lập 2015", "label": "dung", "fact_id": "founded", "value": "2015" if m == "gia-a" else "2016"},
                             {"claim": "trụ sở Quận 3", "label": "cu", "fact_id": "hq", "value": "Quận 3", "correction": "Quận 1"}],
                         "verdict": "nen_chon" if q["giai_doan"] in ("quyet_dinh", "so_sanh") and q["loai"] != "unbranded" else "khong_ap_dung",
                         "reasons": [], "positioning_hit": ["d1"], "attributes_other": ["đắt"], "sentiment": 1 if "Mẫu Việt" in txt else None,
                         "forbidden": [], "task": None}
                    save_json(lan / "cham" / m / f"{qid}__l{luot}.json", j)
        save_json(ws / "tin-hieu-tay.json", {"B3": {"nguon_doc_lap": ["a", "b", "c"]}, "B4": {"nguoi_dung_ten": [{"ten": "A", "ho_so_url": "x"}]},
                                              "B5": {"diem_review": 4.5, "so_review": 300, "phan_hoi_khieu_nai": True}})
        r = run("tin-hieu", "-w", str(ws), "--lan", "2026-10-14", "--offline")
        check("tin-hieu offline", r.returncode == 0)
        r = run("bao-cao", "-w", str(ws), "--lan", "2026-10-14")
        check("bao-cao chạy", r.returncode == 0)
        if r.returncode:
            print(r.stderr[-1500:])
            return
        d = load_json(lan / "diem.json")
        m = d["chi_so"]
        check("A1 Có mặt = 75% (6/8 câu × lượt có tên)", m["A1"]["score"] == 75)
        check("A1 có khoảng tin cậy", m["A1"]["ci"] is not None)
        check("A1 ổn định 50% (gia-b đổi giữa 2 lượt)", m["A1"]["on_dinh_giua_cac_luot"]["score"] == 50)
        check("A2 thị phần nhắc tên 56% (20 lượt bạn / 36 lượt cả tập)", m["A2"]["score"] == 56)
        check("A2 gợi ý đối thủ chưa khai", "Hãng Lạ" in m["A2"]["doi_thu_chua_khai"])
        check("A4 Độ đúng 50% (1 đúng, 1 cũ)", m["A4"]["score"] == 50 and m["A4"]["nhan"]["cu"] > 0)
        check("A5 nhất quán năm thành lập 50%", m["A5"]["theo_dong"].get("founded") == 50)
        check("A7 khớp định vị 50%", m["A7"]["score"] == 50)
        check("A9 nguồn chính thức được dẫn", m["A9"]["score"] is not None and m["A9"]["co_cau_nguon"].get("cua_minh"))
        check("AVI tính được", isinstance(d["avi"], int))
        check("kế hoạch 4 tuần", len(d["ke_hoach"]) == 4)
        check("HTML có kế hoạch", "Kế hoạch 30 ngày" in (lan / "bao-cao.html").read_text(encoding="utf-8"))
        print(json.dumps({k: v["score"] for k, v in m.items()}, ensure_ascii=False))
        print(f"AVI {d['avi']} · R {d['reputation']} · V {d['verifiable']} · rơi bước {d['roi_o_buoc']}")


def main() -> int:
    unit()
    e2e()
    print("XANH" if not FAIL else f"ĐỎ: {len(FAIL)} lỗi")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
