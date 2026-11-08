"""Cổng chặn. Mỗi hàm trả về danh sách lý do chặn; rỗng nghĩa là được đi.
Cổng là code, không phải prompt: agent không thể nói khéo để vượt qua."""
from datetime import datetime, timedelta

from .db import bay_gio, dem_hanh_dong
from . import hanh_vi


def _trong_gio_yen_lang(nv, t):
    bat_dau, ket_thuc = nv["gio_yen_lang"]  # ví dụ [23, 7]
    h = t.hour
    return h >= bat_dau or h < ket_thuc if bat_dau > ket_thuc else bat_dau <= h < ket_thuc


def _tu_cam(nv, noi_dung):
    thap = noi_dung.lower()
    return [w for w in nv["tu_cam"] if w.lower() in thap]


def cong_dang(con, nv, nen_tang_cfg, bai, hv):
    loi = []
    t = bay_gio()
    gd, tuoi, *_ = hanh_vi.giai_doan_hien_tai(con, nv, hv)
    tran = gd["han_muc_ngay"].get("dang", 0)
    if tran == 0:
        loi.append(f"giai đoạn {gd['ma']} ({gd['ten']}, ngày tuổi {tuoi}) chưa cho đăng bài")
    tran_tuan = gd.get("dang_toi_da_tuan")
    if tran_tuan is not None:
        tu = (t - timedelta(days=7)).isoformat(timespec="seconds")
        da_tuan = con.execute("SELECT COUNT(*) FROM bai WHERE trang_thai='da_dang' AND dang_luc>=?", (tu,)).fetchone()[0]
        if da_tuan >= tran_tuan:
            loi.append(f"{gd['ma']} chỉ cho {tran_tuan} bài/7 ngày, đã đăng {da_tuan}")
    hap, tao, can = hanh_vi.ty_le_hap_thu(con, hv)
    if hap < can * tao:
        loi.append(f"luật 10:1: hấp thu {hap} phút / tạo {tao} phút trong {hv['ty_le_hap_thu']['cua_so_ngay']} ngày, cần {can * tao} phút hấp thu")
    if not (bai["muc_dich"] or "").strip() or not (bai["cho_ai"] or "").strip():
        loi.append("bài thiếu mục đích (`--muc-dich`) hoặc thiếu người được phục vụ (`--cho-ai`)")
    if not (bai["tieu_hoa_ids"] or "").strip():
        loi.append("bài không dẫn từ ghi chú tiêu hoá nào (`--tu-tieu-hoa`): tạo phải mọc từ cái đã đọc")
    if bai["trang_thai"] != "duyet":
        loi.append(f"bài đang ở trạng thái `{bai['trang_thai']}`, chưa được duyệt")
    if bai["diem_critic"] is None or bai["diem_critic"] < nv["nguong_critic"]:
        loi.append(f"điểm critic {bai['diem_critic']} dưới ngưỡng {nv['nguong_critic']}")
    cfg = nen_tang_cfg.get(bai["nen_tang"], {})
    if not cfg:
        loi.append(f"nền tảng `{bai['nen_tang']}` chưa khai trong nen-tang.md")
    co_nhan = nv["nhan_ai"].lower() in (bai["noi_dung"] or "").lower()
    if not co_nhan and not cfg.get("adapter_bat_nhan_ai"):
        loi.append(f"thiếu nhãn AI `{nv['nhan_ai']}` trong bài và adapter không tự bật nhãn")
    cam = _tu_cam(nv, bai["noi_dung"] or "")
    if cam:
        loi.append(f"có từ cấm: {', '.join(cam)}")
    gioi_han = cfg.get("do_dai_toi_da")
    if gioi_han and len(bai["noi_dung"] or "") > gioi_han:
        loi.append(f"dài {len(bai['noi_dung'])} ký tự, quá {gioi_han} của {bai['nen_tang']}")
    if _trong_gio_yen_lang(nv, t):
        loi.append(f"đang trong giờ yên lặng {nv['gio_yen_lang']}")
    da_dang = dem_hanh_dong(con, "dang", t.date().isoformat())
    if da_dang >= nv["ngan_sach"]["dang_bai_ngay"]:
        loi.append(f"hết ngân sách đăng hôm nay ({da_dang}/{nv['ngan_sach']['dang_bai_ngay']})")
    return loi


def cong_tra_loi(con, nv, tin, fan, linh_duyet):
    """Hạng xanh: tự gửi khi mức tự chủ 3. Vàng: cần duyệt. Đỏ: chỉ Linh duyệt."""
    loi = []
    t = bay_gio()
    if tin["trang_thai"] not in ("da_soan", "duyet"):
        loi.append(f"tin ở trạng thái `{tin['trang_thai']}`, chưa có câu trả lời soạn sẵn")
    hang = tin["hang"]
    muc = nv["muc_tu_chu"]
    if muc == 1:
        loi.append("mức tự chủ 1: hộp thư chỉ soạn, không gửi")
    elif hang == "do" and not linh_duyet:
        loi.append("hạng đỏ: chỉ gửi khi Linh duyệt (`--linh`)")
    elif hang == "vang" and tin["trang_thai"] != "duyet" and not linh_duyet:
        loi.append("hạng vàng: cần duyệt trước (`hop-thu duyet`)")
    elif hang == "xanh" and muc < 3 and tin["trang_thai"] != "duyet" and not linh_duyet:
        loi.append("hạng xanh nhưng mức tự chủ < 3: cần duyệt")
    if tin["nhan"] == "hoi_ai" and nv["cau_tu_nhan_ai"].lower() not in (tin["tra_loi"] or "").lower():
        loi.append(f"người hỏi có phải AI không: câu trả lời phải chứa `{nv['cau_tu_nhan_ai']}`")
    cam = _tu_cam(nv, tin["tra_loi"] or "")
    if cam:
        loi.append(f"câu trả lời có từ cấm: {', '.join(cam)}")
    if tin["loai"] == "dm":
        luc_tin = datetime.fromisoformat(tin["luc"])
        if t - luc_tin > timedelta(hours=24):
            loi.append("DM quá cửa sổ 24 giờ kể từ tin của fan")
    if fan and fan["khong_nhan"] and tin["loai"] == "dm":
        loi.append("fan đã yêu cầu không nhắn")
    da = dem_hanh_dong(con, "tra_loi", t.date().isoformat())
    if da >= nv["ngan_sach"]["tra_loi_ngay"]:
        loi.append(f"hết ngân sách trả lời hôm nay ({da})")
    return loi
