"""Đọc hồ sơ và luật dạng md. Phần máy đọc nằm trong khối ```json đầu tiên của mỗi file;
phần chữ còn lại để người và agent đọc."""
import json
import os
import re

FILE = {
    "nhan_vat": "ho-so/nhan-vat.md",
    "hang": "ho-so/hang-rui-ro.md",
    "diem": "ho-so/diem-fan.md",
    "luat_viet": "ho-so/luat-viet.md",
    "nen_tang": "ho-so/nen-tang.md",
    "hanh_vi": "ho-so/hanh-vi.md",
    "phong_cach": "ho-so/phong-cach.md",
}


def doc_json_md(duong_dan):
    with open(duong_dan, encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"```json\s*\n(.*?)\n```", txt, re.S)
    if not m:
        raise ValueError(f"{duong_dan}: thiếu khối ```json")
    return json.loads(m.group(1))


def doc(home, ten):
    return doc_json_md(os.path.join(home, FILE[ten]))


TRUONG_BAT_BUOC = ["ten", "nhan_ai", "cong_khai_nguoi_ao", "tru_cot", "ngan_sach",
                   "muc_tu_chu", "gio_yen_lang", "tu_cam", "nguong_critic", "cau_tu_nhan_ai"]


def kiem_nhan_vat(nv):
    loi = [f"thiếu trường `{k}`" for k in TRUONG_BAT_BUOC if k not in nv]
    if nv.get("cong_khai_nguoi_ao") is not True:
        loi.append("`cong_khai_nguoi_ao` phải là true: người ảo phải công khai là người ảo")
    if not str(nv.get("nhan_ai", "")).strip():
        loi.append("`nhan_ai` rỗng")
    tong = sum(t.get("ty_trong", 0) for t in nv.get("tru_cot", []))
    if nv.get("tru_cot") and abs(tong - 1) > 0.01:
        loi.append(f"tổng tỷ trọng trụ cột là {tong:.2f}, phải bằng 1")
    if nv.get("muc_tu_chu") not in (1, 2, 3):
        loi.append("`muc_tu_chu` phải là 1, 2 hoặc 3")
    return loi
