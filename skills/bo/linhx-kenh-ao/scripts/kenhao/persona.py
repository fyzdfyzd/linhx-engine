"""Xưởng persona: tự học kiểu nhân vật nào làm người ta thích, chia sẻ, tranh luận.

Vòng: đọc bài người khác → agent gắn nhãn (kiểu nhân vật, cảm xúc, phản ứng chính, khuyết điểm, giọng)
→ CLI xếp hạng kiểu theo tương tác thật → agent phát triển 2-3 persona ứng viên (mỗi persona bắt buộc
có character flaw và theo phong cách chung) → thử trên kênh → retro theo persona và cảm xúc → chọn.

Ranh giới: "tranh luận" là quan điểm có lập luận trong vùng cho phép, không phải câu giận dữ (rage bait),
không thông tin sai, không chủ đề cấm. Khuyết điểm là nét người (vụng, cả thèm chóng chán, cứng đầu...),
không phải hành vi gây hại."""
import json
import os
from collections import Counter, defaultdict

TRUONG_PERSONA = ["ma", "mot_cau", "flaw", "cam_xuc_muc_tieu", "phan_ung_muc_tieu", "lap_truong", "giong", "phong_cach"]


def xep_hang(con, toi_thieu=2):
    nhom = defaultdict(list)
    for r in con.execute("""SELECT q.*, d.tuong_tac FROM quan_sat_persona q JOIN luot_doc d ON d.id=q.luot_doc_id"""):
        nhom[r["kieu"]].append(r)
    tong_tb = None
    ra = []
    for kieu, ds in nhom.items():
        tt = [r["tuong_tac"] or 0 for r in ds]
        cx = Counter(c for r in ds for c in json.loads(r["cam_xuc"] or "[]"))
        pu = Counter(r["phan_ung"] for r in ds)
        fl = Counter((r["flaw"] or "").strip() for r in ds if (r["flaw"] or "").strip())
        ra.append({"kieu": kieu, "so_bai": len(ds), "tb_tuong_tac": round(sum(tt) / len(tt)),
                   "cam_xuc": dict(cx.most_common(3)), "phan_ung": dict(pu.most_common()),
                   "flaw_hay_gap": [f for f, _ in fl.most_common(3)],
                   "tin_hieu": "đủ" if len(ds) >= toi_thieu * 2 else "yếu"})
    return sorted(ra, key=lambda x: (x["so_bai"] < toi_thieu * 2, -x["tb_tuong_tac"]))


def kiem_persona(p, phong_cach, hv):
    loi = [f"thiếu `{k}`" for k in TRUONG_PERSONA if not p.get(k)]
    for f in p.get("flaw", []):
        for k in ("khuyet_diem", "bieu_hien", "khong_bao_gio"):
            if not f.get(k):
                loi.append(f"flaw `{f.get('khuyet_diem', '?')}` thiếu `{k}`")
    if p.get("phong_cach") and p["phong_cach"] != phong_cach.get("ma"):
        loi.append(f"persona dùng phong cách `{p['phong_cach']}`, kênh thống nhất `{phong_cach.get('ma')}`")
    cam = [c.lower() for c in hv["tranh_luan"]["chu_de_cam"]]
    for lt in p.get("lap_truong", []):
        if any(c in lt.get("chu_de", "").lower() for c in cam):
            loi.append(f"lập trường `{lt.get('chu_de')}` thuộc chủ đề cấm tranh luận")
        if not lt.get("vi_sao"):
            loi.append(f"lập trường `{lt.get('chu_de')}` thiếu `vi_sao` (lập luận)")
    sai_cx = [c for c in p.get("cam_xuc_muc_tieu", []) if c not in hv["cam_xuc"]]
    if sai_cx:
        loi.append(f"cảm xúc không có trong danh sách: {', '.join(sai_cx)}")
    return loi
