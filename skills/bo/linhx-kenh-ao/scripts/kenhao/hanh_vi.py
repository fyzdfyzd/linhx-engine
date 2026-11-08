"""Khung hành vi: người ảo sống như một người mới vào cộng đồng.
Đọc trước, chạm sau, góp chuyện khi đã hiểu người ta, rồi mới đăng nhiều.

Bốn luật gốc (Linh, 16/10/2026):
  - Đọc, xem, tương tác, tiêu hoá phải gấp ít nhất 10 lần phần tạo (cổng `ty_le_hap_thu`).
  - Dựa trên niềm tin và quan hệ: mỗi người trong vòng có điểm tin; chạm mãi không được đáp thì dừng.
  - Mọi hành động phải có mục đích: chọn từ danh sách mục đích cho phép + lý do riêng với người đó.
  - Người ảo vào cộng đồng như người mới: lang thang đọc, xem trend, kết thân, rồi mới đăng.

Ba trục:
  1. Giai đoạn đời tài khoản (G0 quan sát → G1 làm quen → G2 góp chuyện → G3 nuôi kênh).
     Lên giai đoạn cần đủ NGÀY và đủ CHỈ SỐ QUAN HỆ, không chỉ đếm ngày.
  2. Thang quan hệ với từng người trong vòng (giống phễu outbound của sales).
  3. Phiên trong ngày: mỗi phiên là một kịch bản đọc → ghi chú → (chạm) → nghỉ, có hạn mức theo giai đoạn.

Mẫu lấy từ: instagram-ai-agent warmup 14 ngày + budget, xbot máy trạng thái mục tiêu + cooldown,
eliza discovery (ngưỡng điểm like/reply), SalesGPT/Mautic (thang giai đoạn), Xiangyu-CAS (không tự tương tác bài mình).
"""
import random
from datetime import date, datetime, timedelta

from .db import bay_gio

THANG = ["chua_biet", "da_doc", "da_cham", "da_gop_chuyen", "duoc_dap", "hai_chieu", "dong_minh"]


def bac_thang(ten):
    return THANG.index(ten)


def giai_doan_hien_tai(con, nv, hv):
    """Trả về (mã giai đoạn, cấu hình, ngày tuổi, tiêu chí lên giai đoạn kế và đã đạt chưa)."""
    tuoi = (bay_gio().date() - date.fromisoformat(nv["ngay_mo_tai_khoan"])).days
    ds = hv["giai_doan"]
    chi_so = chi_so_quan_he(con)
    hien = ds[0]
    for gd in ds:
        dk = gd.get("vao_khi", {})
        if tuoi >= dk.get("tuoi_ngay", 0) and all(chi_so.get(k, 0) >= v for k, v in dk.items() if k != "tuoi_ngay"):
            hien = gd
        else:
            break
    i = ds.index(hien)
    ke = ds[i + 1] if i + 1 < len(ds) else None
    tieu_chi = []
    if ke:
        for k, v in ke["vao_khi"].items():
            co = tuoi if k == "tuoi_ngay" else chi_so.get(k, 0)
            tieu_chi.append({"chi_so": k, "can": v, "co": co, "dat": co >= v})
    return hien, tuoi, ke, tieu_chi, chi_so


def chi_so_quan_he(con):
    cs = {"so_nguoi_trong_vong": con.execute("SELECT COUNT(*) FROM vong").fetchone()[0],
          "so_bai_da_doc": con.execute("SELECT COUNT(*) FROM luot_doc").fetchone()[0],
          "so_ban_do_trend": con.execute("SELECT COUNT(*) FROM nhat_ky WHERE viec='trend'").fetchone()[0],
          "so_bai_da_dang": con.execute("SELECT COUNT(*) FROM bai WHERE trang_thai='da_dang'").fetchone()[0]}
    for bac in THANG[1:]:
        cs[f"so_nguoi_tu_{bac}"] = con.execute(
            "SELECT COUNT(*) FROM vong WHERE bac_thang>=?", (bac_thang(bac),)).fetchone()[0]
    return cs


def han_muc_hom_nay(con, gd, loai):
    hom_nay = bay_gio().date().isoformat()
    da = con.execute("SELECT COUNT(*) FROM hanh_dong_ra WHERE loai=? AND substr(lam_luc,1,10)=? AND trang_thai='da_lam'",
                     (loai, hom_nay)).fetchone()[0]
    cho = con.execute("SELECT COUNT(*) FROM hanh_dong_ra WHERE loai=? AND substr(tao_luc,1,10)=? AND trang_thai IN ('de_xuat','duyet')",
                      (loai, hom_nay)).fetchone()[0]
    return gd["han_muc_ngay"].get(loai, 0), da + cho


def ty_le_hap_thu(con, hv, them_tao=1):
    """Phút công hấp thu trong cửa sổ (đọc + tiêu hoá + chạm đã làm + trả lời đã gửi) so với phút công tạo
    (bài đã đăng trong cửa sổ + bài sắp đăng, mỗi bài `tao_phut_moi_bai`). Tính theo phút chứ không theo
    số lượt, vì đếm lượt thì 10:1 quá dễ đạt. Trả về (hấp thu, tạo, tỷ lệ cần)."""
    cs = hv["ty_le_hap_thu"]
    tu = (bay_gio() - timedelta(days=cs["cua_so_ngay"])).isoformat(timespec="seconds")
    w = cs["trong_so"]
    hap = (w["doc"] * con.execute("SELECT COUNT(*) FROM luot_doc WHERE doc_luc>=?", (tu,)).fetchone()[0]
           + w["tieu_hoa"] * con.execute("SELECT COUNT(*) FROM tieu_hoa WHERE luc>=?", (tu,)).fetchone()[0]
           + w["cham"] * con.execute("SELECT COUNT(*) FROM hanh_dong_ra WHERE trang_thai='da_lam' AND lam_luc>=?", (tu,)).fetchone()[0]
           + w["tra_loi"] * con.execute("SELECT COUNT(*) FROM tin WHERE trang_thai='da_tra' AND tra_luc>=?", (tu,)).fetchone()[0])
    so_bai = con.execute("SELECT COUNT(*) FROM bai WHERE trang_thai='da_dang' AND dang_luc>=?", (tu,)).fetchone()[0] + them_tao
    return hap, so_bai * cs.get("tao_phut_moi_bai", 1), cs["toi_thieu"]


def cong_ra(con, nv, hv, hd):
    """Cổng cho một hành động ra ngoài (thích, lưu, theo dõi, bình luận, nhắn) lên tài khoản người khác."""
    loi = []
    md_cho_phep = hv["muc_dich"].get(hd["loai"], [])
    if not hd.get("muc_dich"):
        loi.append(f"thiếu `--muc-dich`; với `{hd['loai']}` được chọn: {', '.join(md_cho_phep)}")
    elif hd["muc_dich"] not in md_cho_phep:
        loi.append(f"mục đích `{hd['muc_dich']}` không có trong danh sách cho `{hd['loai']}`: {', '.join(md_cho_phep)}")
    if len((hd.get("vi_sao") or "").strip()) < hv["luat_cham"]["vi_sao_toi_thieu_ky_tu"]:
        loi.append("thiếu `--vi-sao` cụ thể với người này (vì sao chạm họ lúc này)")
    gd, tuoi, *_ = giai_doan_hien_tai(con, nv, hv)
    luat = hv["luat_cham"]
    tran, da = han_muc_hom_nay(con, gd, hd["loai"])
    if tran == 0:
        loi.append(f"giai đoạn {gd['ma']} ({gd['ten']}) chưa cho phép `{hd['loai']}`")
    elif da >= tran:
        loi.append(f"hết hạn mức `{hd['loai']}` hôm nay ở {gd['ma']} ({da}/{tran})")
    nguoi = con.execute("SELECT * FROM vong WHERE id=?", (hd["vong_id"],)).fetchone() if hd["vong_id"] else None
    if nguoi is None:
        loi.append("người này chưa có trong vòng quan hệ: thêm bằng `vong them` và đọc họ trước")
        return loi
    tran_khong_dap = hv["luat_cham"]["dung_khi_cham_khong_dap"]
    if nguoi["cham_khong_dap"] >= tran_khong_dap and hd["loai"] != "thich":
        loi.append(f"đã chạm {nguoi['ten']} {nguoi['cham_khong_dap']} lần liền không được đáp: dừng, chờ họ đáp trước")
    can_tin = hv["luat_cham"]["diem_tin_toi_thieu"].get(hd["loai"])
    if can_tin is not None and nguoi["diem_tin"] < can_tin:
        loi.append(f"điểm tin với {nguoi['ten']} là {nguoi['diem_tin']}, cần {can_tin} trước khi `{hd['loai']}`")
    if nguoi["la_nha"] and not hv["luat_cham"].get("cho_cham_nguoi_nha_cong_khai"):
        loi.append(f"{nguoi['ten']} là persona cùng nhà (Persona OS): không tương tác chéo để tránh hành vi phối hợp thiếu minh bạch")
    if nguoi["la_minh"]:
        loi.append("không tự tương tác với tài khoản của chính mình")
    can_doc = luat["doc_toi_thieu_truoc"].get(hd["loai"], 0)
    if nguoi["so_bai_da_doc"] < can_doc:
        loi.append(f"mới đọc {nguoi['so_bai_da_doc']} bài của {nguoi['ten']}, cần đọc {can_doc} bài trước khi `{hd['loai']}`")
    can_bac = luat["bac_toi_thieu_truoc"].get(hd["loai"])
    if can_bac and nguoi["bac_thang"] < bac_thang(can_bac):
        loi.append(f"quan hệ với {nguoi['ten']} mới ở `{THANG[nguoi['bac_thang']]}`, cần `{can_bac}` trước khi `{hd['loai']}`")
    cd = luat["nghi_giua_hai_lan_ngay"].get(hd["loai"])
    if cd:
        # Không tính chính đề xuất đang được duyệt (`_bo_qua_id`), nếu không nó tự chặn chính nó
        gan = con.execute("SELECT MAX(COALESCE(lam_luc, tao_luc)) FROM hanh_dong_ra WHERE vong_id=? AND loai=? AND trang_thai IN ('de_xuat','duyet','da_lam') AND id<>?",
                          (nguoi["id"], hd["loai"], hd.get("_bo_qua_id") or -1)).fetchone()[0]
        if gan and bay_gio() - datetime.fromisoformat(gan) < timedelta(days=cd):
            loi.append(f"đã `{hd['loai']}` {nguoi['ten']} lúc {gan[:16]}, phải nghỉ {cd} ngày")
    if hd.get("luot_doc_id"):
        trung = con.execute("SELECT COUNT(*) FROM hanh_dong_ra WHERE luot_doc_id=? AND loai=? AND trang_thai IN ('de_xuat','duyet','da_lam') AND id<>?",
                            (hd["luot_doc_id"], hd["loai"], hd.get("_bo_qua_id") or -1)).fetchone()[0]
        if trung:
            loi.append(f"đã có `{hd['loai']}` cho đúng bài này rồi: không chạm trùng một bài")
        doc = con.execute("SELECT * FROM luot_doc WHERE id=?", (hd["luot_doc_id"],)).fetchone()
        if doc and doc["dang_luc"]:
            tuoi_bai = (bay_gio() - datetime.fromisoformat(doc["dang_luc"])).days
            if tuoi_bai > luat["bai_cu_toi_da_ngay"]:
                loi.append(f"bài đã {tuoi_bai} ngày, quá {luat['bai_cu_toi_da_ngay']} ngày: đừng đào bài cũ")
    elif hd["loai"] in ("binh_luan", "thich", "luu"):
        loi.append("phải gắn với một bài đã đọc (`--doc ID`)")
    if hd["loai"] in ("binh_luan", "nhan"):
        nd = (hd["noi_dung"] or "").strip()
        thap = nd.lower()
        if len(nd) < luat["binh_luan_toi_thieu_ky_tu"]:
            loi.append(f"bình luận quá ngắn ({len(nd)} ký tự): phải nói được điều cụ thể")
        chung = [m for m in luat["cum_chung_chung"] if thap.strip(" .!❤️") == m or thap.startswith(m + " ") and len(nd) < 40]
        if chung:
            loi.append("bình luận chung chung kiểu bot: " + ", ".join(chung))
        ct = (hd.get("chi_tiet") or "").strip().lower()
        if not ct:
            loi.append("thiếu `--chi-tiet`: chi tiết cụ thể của bài gốc mà bình luận nhắc tới")
        elif ct not in thap:
            loi.append("bình luận không nhắc tới chi tiết đã khai: phải phản hồi đúng bài, không dán câu mẫu")
        if hd.get("luot_doc_id") and ct:
            doc = con.execute("SELECT noi_dung FROM luot_doc WHERE id=?", (hd["luot_doc_id"],)).fetchone()
            if doc and ct not in (doc["noi_dung"] or "").lower():
                loi.append("chi tiết khai không có trong bài gốc đã đọc")
        if gd["ma"] in luat["cam_tu_quang_cao_o"]:
            qc = [m for m in luat["dau_hieu_tu_quang_cao"] if m in thap]
            if qc:
                loi.append(f"đang ở {gd['ma']}: không tự quảng bá trong bình luận ({', '.join(qc)})")
        cam = [w for w in nv["tu_cam"] if w.lower() in thap]
        if cam:
            loi.append(f"có từ cấm: {', '.join(cam)}")
    if hd["loai"] == "nhan" and nguoi["bac_thang"] < bac_thang("hai_chieu"):
        loi.append("chỉ nhắn riêng khi quan hệ đã hai chiều")
    return loi


def lap_phien(con, nv, hv, ngay):
    """Kịch bản phiên trong ngày theo giai đoạn. Giờ có lệch ngẫu nhiên (tất định theo ngày) để không đều như máy."""
    gd, *_ = giai_doan_hien_tai(con, nv, hv)
    r = random.Random(f"phien|{ngay}")
    phien = []
    for p in hv["phien_mau"][: gd["so_phien_ngay"]]:
        gio, phut = map(int, p["gio"].split(":"))
        lech = r.randint(-p.get("lech_phut", 0), p.get("lech_phut", 0))
        t = datetime(ngay.year, ngay.month, ngay.day, gio, phut) + timedelta(minutes=lech)
        buoc = [b for b in p["buoc"] if b["loai"] in gd["viec_duoc_lam"]]
        phien.append({"luc": t.strftime("%H:%M"), "ten": p["ten"], "phut": p["phut"], "buoc": buoc})
    return gd, phien


def cap_nhat_tin(con, hv, vong_id):
    """Điểm tin = tổng sự kiện hai chiều có giảm dần; chạm một chiều không cộng điểm."""
    giam = hv["diem_tin"]["giam_moi_tuan"]
    t = bay_gio()
    tong = 0.0
    for sk in con.execute("SELECT diem, luc FROM su_kien_vong WHERE vong_id=?", (vong_id,)):
        tuan = (t - datetime.fromisoformat(sk["luc"])).days / 7
        tong += sk["diem"] * (giam ** max(0, tuan))
    con.execute("UPDATE vong SET diem_tin=? WHERE id=?", (round(tong, 2), vong_id))
    return round(tong, 2)


def len_thang(con, vong_id, bac_moi):
    hien = con.execute("SELECT bac_thang FROM vong WHERE id=?", (vong_id,)).fetchone()[0]
    if bac_thang(bac_moi) > hien:
        con.execute("UPDATE vong SET bac_thang=? WHERE id=?", (bac_thang(bac_moi), vong_id))
        return True
    return False
