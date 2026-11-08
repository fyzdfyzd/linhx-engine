#!/usr/bin/env python3
"""tai_tao.py: phần máy của skill tai-tao-flow, 0 token, chỉ dùng thư viện chuẩn.

  sach <bai.txt>                bỏ đoạn bị dán lặp, in ra stdout
  cham <flow.json>              in KET-LUAN.md: bảng khả thi, kinh doanh, kết luận
  pack <flow.json> <thu_muc>    sinh khung plugin Claude Code từ mục "pack"
"""
import json
import re
import sys
from pathlib import Path

TIEU_CHI = ["nguoi_tra_tien", "san_sang_tra", "canh_tranh", "loi_the_linh", "bien_loi_nhuan", "kenh"]


def sach(van_ban):
    """Giữ mỗi đoạn một lần, theo thứ tự xuất hiện đầu tiên."""
    da_thay, giu = set(), []
    for doan in re.split(r"\n\s*\n", van_ban.strip()):
        khoa = re.sub(r"\s+", " ", doan).strip().lower()
        if khoa and khoa not in da_thay:
            da_thay.add(khoa)
            giu.append(doan.strip())
    return "\n\n".join(giu) + "\n"


def ket_luan(flow):
    chuc_nang = [c for c in flow["claims"] if c["loai"] == "chuc-nang"]
    kha_thi = sum(c["kha_thi"] for c in chuc_nang) / len(chuc_nang)
    kd = sum(flow["kinh_doanh"][k]["diem"] for k in TIEU_CHI)
    if kha_thi >= 2.2 and kd >= 12:
        kq = "LÀM"
    elif kha_thi >= 1.5 and kd >= 9:
        kq = "THỬ NHỎ"
    else:
        kq = "CHỈ LƯU"
    return round(kha_thi, 2), kd, kq


def cham(flow):
    kha_thi, kd, kq = ket_luan(flow)
    d = [f"# Kết luận: {flow['ten']}", "", f"Nguồn: {flow['nguon']}. Bài thật ra bán: {flow['san_pham_ban_that']}", "",
         f"**{kq}** · khả thi TB {kha_thi}/3 · kinh doanh {kd}/18", "",
         "## Khả thi từng lời hứa", "",
         "| # | Lời hứa | Loại | Khả thi | Thổi phồng | Cách làm (đoán) | Prior art | Mảnh LINHX | Lý do |",
         "|---|---|---|---|---|---|---|---|---|"]
    for c in flow["claims"]:
        d.append(f"| {c['id']} | {c['noi_dung']} | {c['loai']} | {c['kha_thi']} | {c['thoi_phong']} | {c['cach_lam']} | "
                 f"{', '.join(c['prior_art']) or 'cần R&D'} | {', '.join(c['manh_linh']) or '-'} | {c['ly_do']} |")
    d += ["", "## Kinh doanh (phía LINHX)", "", "| Tiêu chí | Điểm | Lý do |", "|---|---|---|"]
    for k in TIEU_CHI:
        d.append(f"| {k} | {flow['kinh_doanh'][k]['diem']} | {flow['kinh_doanh'][k]['ly_do']} |")
    d += ["", "## Điều kiện ẩn người bán tự nhận", ""] + [f"- {x}" for x in flow["dieu_kien_an"]]
    thoi = [c["id"] for c in flow["claims"] if c["thoi_phong"] == 2]
    if thoi:
        d += ["", f"Lời hứa thổi phồng nặng: {', '.join(thoi)}."]
    return "\n".join(d) + "\n"


def pack(flow, dich):
    p = flow["pack"]
    dich = Path(dich)
    (dich / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (dich / ".claude-plugin" / "plugin.json").write_text(json.dumps(
        {"name": p["ten"], "version": "0.0.1", "description": p["mo_ta"], "author": {"name": "LINHX LAB"}},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    viec = []
    for m in p["modules"]:
        f = dich / "skills" / m["ten"] / "SKILL.md"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"---\nname: {m['ten']}\ndescription: {m['mo_ta']}\n---\n\n# {m['ten']} (nháp)\n\n"
                     f"Phục vụ lời hứa: {', '.join(m['tu_claims'])}\n\n## Tái dùng\n\n"
                     + "".join(f"- {x}\n" for x in m["tai_dung"])
                     + "\n## Việc mới phải làm\n\n" + "".join(f"- [ ] {x}\n" for x in m["viec_moi"]), encoding="utf-8")
        viec += [f"- [ ] {m['ten']}: {x}" for x in m["viec_moi"]]
    _, _, kq = ket_luan(flow)
    (dich / "README.md").write_text(f"# {p['ten']}\n\n{p['mo_ta']}\n\nKết luận: {kq}. {p.get('ghi_chu', '')}\n\n"
                                    "## Việc mới\n\n" + "\n".join(viec) + "\n", encoding="utf-8")
    return dich


if __name__ == "__main__":
    lenh = sys.argv[1] if len(sys.argv) > 1 else ""
    if lenh == "sach":
        sys.stdout.write(sach(Path(sys.argv[2]).read_text(encoding="utf-8")))
    elif lenh == "cham":
        sys.stdout.write(cham(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))))
    elif lenh == "pack":
        print(pack(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")), sys.argv[3]))
    else:
        sys.exit(__doc__)
