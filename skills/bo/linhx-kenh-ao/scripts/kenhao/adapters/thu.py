"""Adapter `thu`: sân thử không chạm mạng. Đăng thì ghi vào outbox/, bình luận và số liệu
được sinh tất định theo id bài để chạy thử lặp lại được. Số liệu cố ý cài hai tín hiệu
(hook câu hỏi và khung 20:00 tốt hơn, trụ cột đời văn phòng nhỉnh hơn) để vòng học có cái mà tìm."""
import json
import os
import random
from datetime import datetime, timedelta

FAN = [("u01", "Thu Trang"), ("u02", "Minh Khoa"), ("u03", "Hà My"), ("u04", "Tuấn Anh"),
       ("u05", "Bảo Ngọc"), ("u06", "Quang Huy"), ("u07", "Lan Phương"), ("u08", "Đức Long"),
       ("u09", "Khánh Linh"), ("u10", "Hoàng Nam"), ("b01", "Cà phê Gió Sớm (brand)"),
       ("s01", "kiemtien247")]

MAU_BINH_LUAN = [
    ("u", "Hay quá, cảm ơn Mây nha ❤️"),
    ("u", "Lưu lại dùng dần, cảm ơn bạn"),
    ("u", "Cái prompt này dùng được cho Excel không bạn?"),
    ("u", "Mây ơi làm video hướng dẫn chi tiết hơn được không?"),
    ("u", "Bạn là AI thật à hay có người đứng sau vậy?"),
    ("u", "Haha đúng cảnh văn phòng mình luôn 😂"),
    ("u", "Mình thử rồi mà không ra kết quả như bạn, sai ở đâu nhỉ?"),
    ("b", "Chào Mây, bên mình muốn hợp tác booking một video cho chuỗi cà phê, báo giá giúp mình nhé"),
    ("s", "Kiếm 5 triệu/ngày tại nhà, inbox mình link http://bit.ly/xxx"),
    ("u", "Sao dạo này nội dung nhàm thế, thất vọng ghê"),
]


def _rng(*khoa):
    return random.Random("|".join(map(str, khoa)))


def dang(home, bai, cfg):
    os.makedirs(os.path.join(home, "outbox"), exist_ok=True)
    ma = f"thu-{bai['nen_tang']}-{bai['id']}"
    with open(os.path.join(home, "outbox", f"{bai['nen_tang']}.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"ma": ma, "bai_id": bai["id"], "noi_dung": bai["noi_dung"],
                            "media": bai["media"], "nhan_ai_tu_bat": cfg.get("adapter_bat_nhan_ai", False)},
                           ensure_ascii=False) + "\n")
    return ma


def keo_binh_luan(home, bai, cfg):
    r = _rng("bl", bai["id"])
    goc = datetime.fromisoformat(bai["dang_luc"])
    so = r.randint(3, 6)
    ra = []
    chon = r.sample(range(len(MAU_BINH_LUAN)), so)
    for i, k in enumerate(chon):
        kieu, txt = MAU_BINH_LUAN[k]
        if kieu == "b":
            fan = FAN[10]
        elif kieu == "s":
            fan = FAN[11]
        else:
            fan = FAN[r.randint(0, 9)]
        loai = "dm" if kieu == "b" else "binh_luan"
        ra.append({"ma_ngoai": f"{bai['ma_ngoai']}-c{i}", "loai": loai, "fan_ma": fan[0],
                   "fan_ten": fan[1], "noi_dung": txt,
                   "luc": (goc + timedelta(minutes=15 + 20 * i)).isoformat(timespec="seconds")})
    return ra


def gui_tra_loi(home, tin, noi_dung, cfg):
    with open(os.path.join(home, "outbox", "tra-loi.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"tra_loi_cho": tin["ma_ngoai"], "noi_dung": noi_dung}, ensure_ascii=False) + "\n")
    return True


def keo_so_lieu(home, bai, cfg):
    r = _rng("sl", bai["id"])
    view = r.randint(800, 2400)
    he_so = 1.0
    if bai["hook"] == "cau_hoi":
        he_so *= 1.8
    if (bai["dang_luc"] or "")[11:13] == "20":
        he_so *= 1.4
    if bai["tru_cot"] == "doi-van-phong":
        he_so *= 1.3
    ty_le = min(0.25, 0.035 * he_so * r.uniform(0.8, 1.2))
    tuong_tac = int(view * ty_le)
    return {"view": view, "reach": int(view * 0.8), "like_": int(tuong_tac * 0.7),
            "comment": int(tuong_tac * 0.15), "share": int(tuong_tac * 0.07), "save": int(tuong_tac * 0.08)}
