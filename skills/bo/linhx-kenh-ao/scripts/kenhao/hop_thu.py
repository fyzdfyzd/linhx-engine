"""Hộp thư: phân loại theo luật trước (rẻ, giải thích được), agent sửa nhãn sau khi cần.
Mẫu lấy từ SalesGPT (phân loại giai đoạn trước, viết sau) và Chatwoot (chuyển người có lý do)."""


def phan_loai(luat_hang, noi_dung):
    thap = noi_dung.lower()
    for l in luat_hang["nhan"]:
        trung = [m for m in l["mau"] if m.lower() in thap]
        if trung:
            return l["hang"], l["nhan"], f"khớp mẫu: {', '.join(trung[:3])}", l.get("hanh_dong")
    md = luat_hang["mac_dinh"]
    return md["hang"], md["nhan"], "không khớp mẫu nào", None
