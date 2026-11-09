"""Máy đo tự động WF13: kiểm khung.yaml của một bài/lớp corp.

Chạy: python kiem_khoa.py duong/dan/khung.yaml   (cần PyYAML)
Thoát 0 = DAT, 1 = CHUA_DAT. In từng lỗi.

khung.yaml tối thiểu:
muc_tieu: [{id: O1, cau: "Viết ...", danh_gia: [Q1, E1]}]
phan:      # theo thứ tự trong lớp
  - {loai: ket_noi|khai_niem|xu_ly|thuc_hanh|chot, phut: 10, muc_tieu: [O1], nhan: xuong_song|tu_chon}
ban_giang_vien: {theo_phut: true, cau_chot: true, cau_hoi_hay_gap: true, chuyen_y: true, du_phong: true, checklist_d1: true}
"""
import sys

import yaml

TU_MO_HO = ("hiểu", "nắm được", "biết về", "làm quen")
MUC_GV = ("theo_phut", "cau_chot", "cau_hoi_hay_gap", "chuyen_y", "du_phong", "checklist_d1")


def kiem(k):
    loi = []
    mt = {m["id"]: m for m in k.get("muc_tieu", [])}
    phan = k.get("phan", [])
    tong = sum(p.get("phut", 0) for p in phan) or 1
    for m in mt.values():
        c = m.get("cau", "").lower()
        if any(c.startswith(t) or f" {t} " in f" {c} " for t in TU_MO_HO):
            loi.append(f"{m['id']}: động từ mơ hồ ('{m.get('cau')}')")
        if not m.get("danh_gia"):
            loi.append(f"{m['id']}: không có đánh giá")
        if not any(m["id"] in p.get("muc_tieu", []) for p in phan if p.get("loai") == "thuc_hanh"):
            loi.append(f"{m['id']}: không có hoạt động thực hành")
    th = sum(p.get("phut", 0) for p in phan if p.get("loai") == "thuc_hanh")
    if th / tong < 0.40:
        loi.append(f"thực hành {th}/{tong} phút = {th/tong:.0%} < 40%")
    for i, p in enumerate(phan):
        if p.get("loai") == "khai_niem":
            if p.get("phut", 0) > 15:
                loi.append(f"phần {i+1}: khúc giảng {p['phut']} phút > 15")
            sau = phan[i + 1]["loai"] if i + 1 < len(phan) else None
            if sau not in ("xu_ly", "thuc_hanh"):
                loi.append(f"phần {i+1}: khúc giảng không có xử lý theo sau")
        if p.get("nhan") not in ("xuong_song", "tu_chon"):
            loi.append(f"phần {i+1}: thiếu nhãn xuong_song/tu_chon")
    for loai in ("ket_noi", "chot"):
        if not any(p.get("loai") == loai for p in phan):
            loi.append(f"thiếu phần {loai}")
    gv = k.get("ban_giang_vien", {})
    for m in MUC_GV:
        if not gv.get(m):
            loi.append(f"bản giảng viên thiếu mục {m}")
    return loi


if __name__ == "__main__":
    k = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
    loi = kiem(k)
    print("DAT" if not loi else "CHUA_DAT")
    for l in loi:
        print("-", l)
    sys.exit(1 if loi else 0)
