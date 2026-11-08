"""Vòng học: số trước, giả thuyết sau. CLI chỉ tính số và kiểm cỡ mẫu; agent đọc RETRO rồi
viết giả thuyết, mở thí nghiệm, đề luật viết mới."""
import math
from collections import defaultdict


def can_mau(p, d):
    """Cỡ mẫu mỗi nhánh để thấy chênh lệch tuyệt đối d quanh tỷ lệ nền p (PostHog: N ≈ 16·p(1-p)/d²)."""
    return math.ceil(16 * p * (1 - p) / (d * d))


def ty_le(row):
    tt = row["like_"] + row["comment"] + row["share"] + row["save"]
    return tt / row["view"] if row["view"] else 0.0


def nhom(rows, khoa):
    g = defaultdict(list)
    for r in rows:
        g[khoa(r)].append(r)
    ra = []
    for k, ds in g.items():
        view = sum(r["view"] for r in ds)
        tt = sum(r["like_"] + r["comment"] + r["share"] + r["save"] for r in ds)
        ra.append({"nhom": k, "so_bai": len(ds), "view": view, "ty_le": tt / view if view else 0})
    return sorted(ra, key=lambda x: -x["ty_le"])


def so_sanh(a, b, nen):
    """Trả về (chênh lệch, đủ mẫu?, lý do). Đơn vị thật là bài, nên đòi cả >= 5 bài mỗi nhánh."""
    d = a["ty_le"] - b["ty_le"]
    if abs(d) < 1e-9:
        return d, False, "không chênh"
    n = can_mau(nen, abs(d))
    du_view = min(a["view"], b["view"]) >= n
    du_bai = min(a["so_bai"], b["so_bai"]) >= 5
    if du_view and du_bai:
        return d, True, f"đủ mẫu (cần {n} view/nhánh, có {min(a['view'], b['view'])}; >= 5 bài/nhánh)"
    thieu = []
    if not du_view:
        thieu.append(f"cần {n} view/nhánh, có {min(a['view'], b['view'])}")
    if not du_bai:
        thieu.append(f"cần >= 5 bài/nhánh, có {min(a['so_bai'], b['so_bai'])}")
    return d, False, "tín hiệu yếu: " + "; ".join(thieu)
