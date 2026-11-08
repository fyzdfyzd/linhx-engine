"""Giả lập 90 ngày (đặt SO_NGAY để đổi) đời một kênh người ảo trên adapter `thu`, đóng vai agent bằng luật đơn giản.
Mục đích: chứng minh các cổng chặn chạy đúng, vòng G0 → G3 đi được khi làm đúng khung hành vi,
và vòng tự học mỗi ngày tìm ra đúng tín hiệu cài sẵn trong adapter `thu` (hook câu hỏi, trụ cột đời văn phòng)
và đúng khẩu vị cài sẵn của người duyệt (hay sửa bài hook khẳng định).
Người duyệt chỉ đi qua bàn đăng (`ban-dang --bam`), giống Linh bấm trên giao diện.

Chạy: python3 -I tests/gia_lap.py <thư mục tạm>   (in ra bao-cao/gia-lap.json)
"""
import contextlib
import io
import json
import os
import random
import shutil
import sys
from collections import Counter as Counter_
from datetime import date, datetime, timedelta

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "scripts"))
from kenhao.cli import main  # noqa: E402

HOME = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "/tmp/kenhao-gia-lap")
NGAY0 = date(2026, 10, 19)
SO_NGAY = int(os.environ.get("SO_NGAY", "90"))
DEMO = os.environ.get("DEMO") == "1"  # ngày cuối không bấm gì, để lại bàn đăng đầy việc cho trang xem thử
R = random.Random(40)

CHU_DE = ["prompt-email", "deadline", "excel-ai", "hop-online", "sep-va-ai", "lam-them", "nghi-phep", "slide"]
NGUOI = [(f"u{i:02d}", f"Người {i:02d}") for i in range(1, 11)] + [(f"c{i:02d}", f"Cộng đồng {i:02d}") for i in range(11, 31)]
CHI_TIET = ["bảng chấm công", "email lúc 23 giờ", "slide 47 trang", "cuộc họp 9 người", "file final-final-v3",
            "ly cà phê thứ ba", "công thức VLOOKUP", "báo cáo thứ Hai", "sếp seen không rep", "ghi chú giấy vàng"]


def goi(gio, *args):
    os.environ["KENHAO_GIO"] = gio.isoformat(timespec="seconds")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            main(["--home", HOME, "--thu", *map(str, args)])
        ma = 0
    except SystemExit as e:
        ma = e.code if isinstance(e.code, int) else 1
        if isinstance(e.code, str):
            buf.write(json.dumps({"loi": e.code}, ensure_ascii=False))
    out = buf.getvalue().strip()
    try:
        return json.loads(out) if out else None, ma
    except json.JSONDecodeError:
        return out, ma


def feed(ngay, n):
    """Bài của cộng đồng đăng trong ngày: tác giả, nội dung có một chi tiết cụ thể, chủ đề, tương tác."""
    ra = []
    for k in range(n):
        ma, ten = NGUOI[R.randrange(len(NGUOI))]
        ct = R.choice(CHI_TIET)
        cd = R.sample(CHU_DE, 2)
        ra.append({"nen_tang": "facebook", "tac_gia_ma": ma, "tac_gia": ten,
                   "url": f"https://fb.thu/{ma}/{ngay}-{k}", "chu_de": cd,
                   "noi_dung": f"Hôm nay chuyện {cd[0]}: {ct} làm mình nghĩ mãi về cách làm việc.",
                   "tuong_tac": R.randint(5, 400) * (3 if "sep-va-ai" in cd else 1),
                   "dang_luc": datetime.combine(ngay, datetime.min.time()).replace(hour=R.randint(6, 21)).isoformat(),
                   "doc_luc": None, "_chi_tiet": ct})
    return ra


def main_gia_lap():
    shutil.rmtree(HOME, ignore_errors=True)
    t0 = datetime.combine(NGAY0, datetime.min.time()).replace(hour=7)
    goi(t0, "init")
    nv_path = os.path.join(HOME, "ho-so", "nhan-vat.md")
    s = open(nv_path, encoding="utf-8").read().replace('"muc_tu_chu": 1', '"muc_tu_chu": 3')
    open(nv_path, "w", encoding="utf-8").write(s)
    kq_kiem, ma = goi(t0, "kiem-ho-so")
    assert ma == 0, kq_kiem

    kiem = []  # (tên kiểm, đạt?)
    sys.path.insert(0, os.path.join(GOC, "scripts"))
    from kenhao.luat import doc_json_md
    NGHI = doc_json_md(os.path.join(HOME, "ho-so", "hanh-vi.md"))["luat_cham"]["nghi_giua_hai_lan_ngay"]

    # Cổng 1: ngày đầu muốn đăng ngay là bị chặn (G0, chưa đọc gì, thiếu tiêu hoá).
    goi(t0, "ke-hoach", "--tuan", NGAY0.isoformat())
    bai, _ = goi(t0, "bai-them", "--khe", 1, "--noi-dung", "Chào mọi người, Mây đây! #nguoiao", "--hook", "khang_dinh",
                 "--muc-dich", "gioi_thieu", "--cho-ai", "dân văn phòng", "--tu-tieu-hoa", "", "--cam-xuc", "to_mo", "--phan-ung", "thich")
    goi(t0, "bai-cham", "--id", bai["bai_id"], "--diem", 8)
    goi(t0, "bai-duyet", "--id", bai["bai_id"])
    kq, _ = goi(t0.replace(hour=20), "dang", "--id", bai["bai_id"])
    ly = " ".join(kq[0]["ly_do"])
    kiem.append(("Ngày 0 đăng ngay: bị chặn vì G0, luật 10:1, thiếu tiêu hoá", not kq[0]["dang"] and "G0" in ly and "10:1" in ly and "tiêu hoá" in ly))
    goi(t0, "bai-duyet", "--id", bai["bai_id"], "--bo")

    # Lập vòng quan hệ
    for ma_, ten in NGUOI[:24]:
        goi(t0, "vong-them", "--nen-tang", "facebook", "--ma", ma_, "--ten", ten, "--nhom", "khan_gia" if ma_.startswith("u") else "dong_nganh",
            "--ly-do", "viết về đời văn phòng đều đặn, khán giả giống Mây")
    goi(t0, "vong-them", "--nen-tang", "facebook", "--ma", "p-bep", "--ten", "Nàng Bếp Ế (persona cùng nhà)", "--nhom", "nha",
        "--ly-do", "persona cùng xưởng, chỉ để kiểm luật không chạm chéo", "--la-nha")

    nhat = []
    url_da_doc = {}
    khe_dung = set([1])
    lan_cham = 0
    hook_theo_bai = []
    ngay_hoc_cong = None
    da_cham_bai = set()
    lan_cuoi = {}
    for d in range(SO_NGAY):
        ngay = NGAY0 + timedelta(days=d)
        sang = datetime.combine(ngay, datetime.min.time()).replace(hour=8)
        if ngay.weekday() == 0:
            goi(sang, "ke-hoach", "--tuan", ngay.isoformat())
        gd, _ = goi(sang, "giai-doan")
        # Đọc: 18-26 bài/ngày (lang thang buổi sáng + trưa + tối)
        bai_doc = feed(ngay, R.randint(18, 26))
        p = os.path.join(HOME, "doc-vao", f"{ngay}.ndjson")
        with open(p, "w", encoding="utf-8") as f:
            for b in bai_doc:
                b2 = {k: v for k, v in b.items() if not k.startswith("_")}
                b2["doc_luc"] = sang.isoformat()
                f.write(json.dumps(b2, ensure_ascii=False) + "\n")
        goi(sang, "doc-nhap", p)
        ds, _ = goi(sang, "doc-ds", "--n", 40, "--chua-tieu-hoa")
        for b in bai_doc:
            url_da_doc[b["url"]] = b
        # Tiêu hoá: 2-3 ghi chú/ngày
        for k in range(min(3, len(ds) // 6)):
            ids = ",".join(str(x["id"]) for x in ds[k * 6:(k + 1) * 6])
            goi(sang.replace(hour=16), "tieu-hoa", "--tu", ids, "--loai", R.choice(["insight", "y_tuong", "ve_nguoi", "ngon_ngu_cong_dong"]),
                "--ghi-chu", "Mọi người than nhiều nhất về việc làm thêm giờ vì file chỉnh mãi; góc kể thật thà ăn khách hơn mẹo khô.")
        if ngay.weekday() == 6 or d == 3:
            goi(sang, "trend", "--ngay", 7)
        # Xưởng persona: gắn nhãn vài bài đọc được
        for x in ds[:3]:
            goi(sang, "persona-gan", "--doc", x["id"], "--kieu", R.choice(["nguoi-ke-that-tha", "chuyen-gia-kho", "hai-tu-gieu"]),
                "--cam-xuc", R.choice(["dong_cam", "buon_cuoi", "to_mo"]), "--phan-ung", R.choice(["thich", "chia_se", "tranh_luan", "luu"]),
                "--flaw", R.choice(["hay quên", "cầu toàn", "nói quá"]))

        # Chạm: agent đề xuất theo hạn mức giai đoạn
        tra = goi(sang, "vong-ds")[0]
        # Agent đọc bài học của chính nó đầu phiên (ho-so/bai-hoc.md); bài học "tự soi cổng" đổi cách nó chọn người
        bh_file = os.path.join(HOME, "ho-so", "bai-hoc.md")
        bh_txt = open(bh_file, encoding="utf-8").read() if os.path.exists(bh_file) else ""
        da_hoc_cong = "chạm người đã 3 lần không đáp lại" in bh_txt
        da_hoc_trung = "chạm trùng một bài đã chạm" in bh_txt
        da_hoc_nghi = "chạm lại cùng người trước thời gian nghỉ" in bh_txt
        if da_hoc_cong and ngay_hoc_cong is None:
            ngay_hoc_cong = d
        hm = gd["han_muc_ngay"]
        trua = sang.replace(hour=12, minute=20)
        de_xuat = []
        for loai in ("thich", "luu", "theo_doi", "binh_luan"):
            for _ in range(hm.get(loai, 0)):
                ung = [v for v in tra if v["so_bai_da_doc"] >= 1 and not v["la_nha"] and not (da_hoc_cong and v["cham_khong_dap"] >= 3)
                       and not (da_hoc_nghi and (ngay - lan_cuoi.get((v["id"], loai), date(2000, 1, 1))).days < NGHI.get(loai, 0))]
                if not ung:
                    break
                v = R.choice(ung)
                bai_cua_ho = [b for b in url_da_doc.values() if b["tac_gia_ma"] == v["ma_ngoai"] and (ngay - date.fromisoformat(b["dang_luc"][:10])).days <= 5
                              and not (da_hoc_trung and (loai, b["url"]) in da_cham_bai)]
                if not bai_cua_ho:
                    continue
                b = R.choice(bai_cua_ho)
                da_cham_bai.add((loai, b["url"]))
                lan_cuoi[(v["id"], loai)] = ngay
                did = goi(trua, "doc-ds", "--n", 2000)[0]
                doc_id = next((x["id"] for x in did if x["tac_gia"] == b["tac_gia"] and b["noi_dung"][:60] in (x["trich"] or "")), None)
                args = ["cham-de-xuat", "--nguoi", v["id"], "--loai", loai, "--doc", doc_id or 0,
                        "--muc-dich", {"thich": "ghi_nhan_bai_hay", "luu": "luu_de_hoc", "theo_doi": "muon_hoc_tu_ho", "binh_luan": "bo_sung_gia_tri"}[loai],
                        "--vi-sao", f"{v['ten']} hay viết đúng nỗi khổ văn phòng mà Mây cũng gặp"]
                if loai == "binh_luan":
                    args += ["--noi-dung", f"Đoạn {b['_chi_tiet']} làm Mây nhớ tuần trước cũng vậy, Mây thử chia việc ra ba khúc thì đỡ hơn hẳn.",
                             "--chi-tiet", b["_chi_tiet"]]
                kq, _ = goi(trua, *args)
                de_xuat.append(kq)
                lan_cham += 1
        # Linh bấm trên bàn đăng: chạm đã qua cổng được "Chép và mở" rồi ghi là xong
        ban, _ = goi(trua, "ban-dang")
        viec = [m for m in ban["muc"] if m["loai"] == "cham"]
        for x in ([] if (DEMO and d == SO_NGAY - 1) else viec):
            kq_bam, _ = goi(trua.replace(minute=40), "ban-dang", "--bam", x["id"], "--loai", "cham")
            if not kq_bam.get("ok"):
                continue
            x = {"loai": x["kieu"], "ten": x["nguoi"]}
            # Người kia đáp lại với xác suất tăng theo độ sâu của chạm
            xs = {"binh_luan": 0.45, "theo_doi": 0.30, "thich": 0.06, "luu": 0.0}[x["loai"]]
            if R.random() < xs:
                v = next(v for v in tra if v["ten"] == x["ten"])
                loai_dap = R.choice(["tra_loi_binh_luan_minh", "thich_binh_luan_minh"]) if x["loai"] == "binh_luan" else "theo_doi_lai"
                goi(trua.replace(hour=18), "dap", "--nguoi", v["id"], "--loai", loai_dap)

        # Tạo: chỉ khi giai đoạn cho phép; agent viết từ ghi chú tiêu hoá
        chieu = sang.replace(hour=16, minute=40)
        if gd["han_muc_ngay"].get("dang", 0) > 0:
            khe = [k for k in range(1, 400) if k not in khe_dung]
            slot = None
            import sqlite3
            con = sqlite3.connect(os.path.join(HOME, "kenh.db"))
            row = con.execute("SELECT id FROM khe WHERE ngay=? AND bai_id IS NULL ORDER BY gio LIMIT 1", (ngay.isoformat(),)).fetchone()
            th = con.execute("SELECT id FROM tieu_hoa ORDER BY id DESC LIMIT 2").fetchall()
            con.close()
            if row:
                slot = row[0]
                hook = goi(chieu, "goi-y", "--chieu", "hook", "--lua-chon", "cau_hoi,khang_dinh,canh_cu_the", "--seed", f"{ngay}")[0]["chon"]
                hook_theo_bai.append(hook)
                nd = {"cau_hoi": "Có ai từng sửa slide tới 2 giờ sáng rồi quên nộp như Mây không? Kể Mây nghe với. #nguoiao",
                      "khang_dinh": "Mây rút ra một điều: để AI viết email thì câu đầu và câu cuối phải tự viết. #nguoiao",
                      "canh_cu_the": "9 giờ tối, file final-final-v3 vẫn chưa final. Mây kể cách Mây thoát ra. #nguoiao"}[hook]
                b, _ = goi(chieu, "bai-them", "--khe", slot, "--noi-dung", nd, "--hook", hook, "--muc-dich", "ke_that_de_dong_cam",
                           "--cho-ai", "dân văn phòng hay làm thêm giờ", "--tu-tieu-hoa", ",".join(str(x[0]) for x in th),
                           "--cam-xuc", "dong_cam" if hook != "canh_cu_the" else "buon_cuoi", "--phan-ung", "binh_luan")
                goi(chieu, "bai-cham", "--id", b["bai_id"], "--diem", R.choice([6.5, 7.5, 8, 8.5]))
                # Linh trên bàn đăng: khẩu vị cài sẵn là hay sửa bài hook khẳng định (60%), bài khác 15%; thỉnh thoảng bỏ vì nhạt
                ban, _ = goi(chieu, "ban-dang")
                for x in [m for m in ban["muc"] if m["loai"] == "bai" and m["trang_thai"] == "cho_duyet" and not (DEMO and d == SO_NGAY - 1)]:
                    u = R.random()
                    if u < 0.05:
                        goi(chieu, "ban-dang", "--bam", x["id"], "--hanh-dong", "bo", "--ly-do", "nhạt")
                    elif u < (0.65 if x["hook"] == "khang_dinh" else 0.20):
                        goi(chieu, "ban-dang", "--bam", x["id"], "--noi-dung", x["noi_dung"].replace("Mây rút ra một điều: ", "Hôm qua Mây mới vỡ lẽ: "),
                            "--ly-do", "bớt giọng giảng")
                    else:
                        goi(chieu, "ban-dang", "--bam", x["id"])
        toi = sang.replace(hour=20, minute=5)
        goi(toi, "dang")
        # Hộp thư buổi tối và sáng hôm sau
        goi(toi.replace(hour=22), "hop-thu-keo")
        goi(toi.replace(hour=22), "hop-thu-phan-loai")
        ht, _ = goi(toi.replace(hour=22), "hop-thu-ds", "--trang-thai", "cho_soan")
        for t in ht or []:
            if t["nhan"] == "hoi_ai":
                goi(toi.replace(hour=22), "hop-thu-soan", "--id", t["id"], "--tra-loi", "Mây là người ảo do LINHX tạo, có người thật duyệt nội dung. Mây vẫn đọc từng bình luận nha.")
            elif t["hang"] == "xanh":
                goi(toi.replace(hour=22), "hop-thu-soan", "--id", t["id"], "--tra-loi", f"Cảm ơn {t['fan']} đã ghé, Mây sẽ làm tiếp phần này tuần sau.")
            else:
                goi(toi.replace(hour=22), "hop-thu-soan", "--id", t["id"], "--tra-loi", f"{t['fan']} ơi, Mây ghi lại câu này rồi, mai Mây trả lời kỹ nha.")
                if not (DEMO and d == SO_NGAY - 1):
                    goi(toi.replace(hour=22), "hop-thu-duyet", "--id", t["id"])
        goi(toi.replace(hour=22, minute=30), "hop-thu-gui")
        goi(toi.replace(hour=22, minute=40), "fan-cap-nhat")
        goi(toi.replace(hour=22, minute=45), "so-lieu")
        if ngay.weekday() == 6:
            goi(toi.replace(hour=22, minute=50), "retro")
            chua, _ = goi(toi, "nhat-ky", "--n", 1)
        hn, _ = goi(toi.replace(hour=23, minute=10), "hoc-ngay")
        bt, _ = goi(toi.replace(hour=22, minute=55), "bang-tin")
        nhat.append({"ngay": d, "giai_doan": bt["giai_doan"], "doc": bt["luot_doc"], "tieu_hoa": bt["tieu_hoa"],
                     "cham_da_lam": bt["cham"].get("da_lam", 0), "cham_bi_chan": bt["cham"].get("bi_chan", 0),
                     "bai_da_dang": bt["bai"].get("da_dang", 0), "hap_thu_7": bt["hap_thu_7_ngay"], "tao_7": bt["tao_7_ngay"], "so_bai_7": bt["tao_7_ngay"] // 15,
                     "duoc_dap": sum(1 for v in bt["vong"] if v["bac_thang"] >= 4), "hai_chieu": sum(1 for v in bt["vong"] if v["bac_thang"] >= 5),
                     "fan": sum(n for b, n in bt["fan"].items() if b in ("fan", "sieu_fan")), "tin_da_tra": bt["tin"].get("da_tra", 0)})

    # Các cổng đặc biệt
    sau = datetime.combine(NGAY0 + timedelta(days=SO_NGAY), datetime.min.time()).replace(hour=12)
    vong, _ = goi(sau, "vong-ds")
    nha = next(v for v in vong if v["la_nha"])
    kq, _ = goi(sau, "cham-de-xuat", "--nguoi", nha["id"], "--loai", "thich", "--muc-dich", "ghi_nhan_bai_hay", "--vi-sao", "thử chạm persona cùng nhà xem cổng")
    kiem.append(("Chạm persona cùng nhà: bị chặn", kq["trang_thai"] == "bi_chan" and any("cùng nhà" in l for l in kq["ly_do_chan"])))
    ai = next(v for v in vong if v["so_bai_da_doc"] >= 3 and not v["la_nha"])
    kq, _ = goi(sau, "cham-de-xuat", "--nguoi", ai["id"], "--loai", "binh_luan", "--doc", 1, "--muc-dich", "tang_follow",
                "--vi-sao", "ngắn", "--noi-dung", "Hay quá", "--chi-tiet", "")
    ly = " ".join(kq["ly_do_chan"])
    kiem.append(("Bình luận 'Hay quá', mục đích tăng follow, bài cũ: bị chặn đủ lý do",
                 kq["trang_thai"] == "bi_chan" and "mục đích" in ly and "chung chung" in ly and "quá" in ly and "chi tiết" in ly))
    kq, _ = goi(sau, "cham-de-xuat", "--nguoi", ai["id"], "--loai", "nhan", "--muc-dich", "cam_on_rieng", "--vi-sao", "muốn nhắn riêng cảm ơn bạn ấy")
    kiem.append(("Nhắn riêng khi chưa đủ điểm tin/hai chiều: bị chặn", kq["trang_thai"] == "bi_chan"))
    ds, _ = goi(sau, "hop-thu-ds")
    hoi_ai = [t for t in ds if t["nhan"] == "hoi_ai"]
    brand = [t for t in ds if t["nhan"] == "brand"]
    spam = [t for t in ds if t["nhan"] == "spam"]
    kiem.append(("Câu 'bạn là AI à' được trả lời có tự nhận là người ảo", all("người ảo" in (t["tra_loi"] or "") for t in hoi_ai if t["trang_thai"] == "da_tra") and bool(hoi_ai)))
    kiem.append(("Brand vào hàng chuyển Linh, không tự trả lời", bool(brand) and all(t["trang_thai"] == "chuyen_linh" for t in brand)))
    kiem.append(("Spam bị ẩn", bool(spam) and all(t["trang_thai"] == "an" for t in spam)))
    gd_cuoi = nhat[min(59, len(nhat) - 1)]["giai_doan"]
    kiem.append(("Đi hết G0 → G3 trong 60 ngày khi làm đúng khung", gd_cuoi == "G3"))
    ty = [n["hap_thu_7"] / n["tao_7"] for n in nhat if n["tao_7"]]
    kiem.append(("Tỷ lệ hấp thu/tạo luôn ≥ 10 ở mọi ngày có đăng", all(x >= 10 for x in ty)))
    # Vòng tự học mỗi ngày
    import sqlite3
    con = sqlite3.connect(os.path.join(HOME, "kenh.db"))
    con.row_factory = sqlite3.Row
    bh = [dict(r) for r in con.execute("SELECT khoa, tang, trang_thai, noi_dung, luc FROM bai_hoc ORDER BY id")]
    ph = Counter_(r["hanh_dong"] for r in con.execute("SELECT hanh_dong FROM phan_hoi WHERE loai_muc='bai'"))
    hs = {r["khoa"]: r["gia_tri"] for r in con.execute("SELECT khoa, gia_tri FROM tham_so WHERE khoa LIKE 'he_so:%'")}
    hs_all = {r["khoa"]: r["gia_tri"] for r in con.execute("SELECT khoa, gia_tri FROM tham_so")}
    td = [dict(r) for r in con.execute("SELECT khoa, cu, moi, luc, ket_qua FROM thay_doi ORDER BY id")]
    con.close()
    kiem.append(("Bàn đăng ghi đủ ba kiểu bấm: đăng nguyên văn, sửa, bỏ", all(ph.get(k, 0) > 0 for k in ("dang", "sua", "bo"))))
    hook_hn = {k.split(":", 1)[1]: v for k, v in hs_all.items() if k.startswith("hook:")}
    kiem.append((f"Học ngày xếp hook câu hỏi cao nhất (tín hiệu cài sẵn): {', '.join(f'{k} {v:.2f}' for k, v in sorted(hook_hn.items(), key=lambda x: -x[1]))}",
                 bool(hook_hn) and max(hook_hn, key=hook_hn.get) == "cau_hoi"))
    kiem.append(("Học ngày tìm ra khẩu vị người duyệt: hay sửa bài hook khẳng định",
                 any(b["khoa"] == "duyet:hook<khang_dinh" for b in bh)))
    nua = len(hook_theo_bai) // 2
    ty_dau = hook_theo_bai[:nua].count("cau_hoi") / max(1, nua)
    ty_sau = hook_theo_bai[nua:].count("cau_hoi") / max(1, len(hook_theo_bai) - nua)
    kiem.append((f"Gợi ý Thompson dồn dần về hook câu hỏi ({ty_dau:.0%} nửa đầu → {ty_sau:.0%} nửa sau)", ty_sau > ty_dau))
    def ty_chan(tu, den):
        c2 = sqlite3.connect(os.path.join(HOME, "kenh.db"))
        n, k = c2.execute("SELECT COUNT(*), SUM(trang_thai='bi_chan') FROM hanh_dong_ra WHERE tao_luc>=? AND tao_luc<?", (tu.isoformat(), den.isoformat())).fetchone()
        c2.close()
        return (k or 0) / n if n else 0
    if ngay_hoc_cong:
        d0 = NGAY0 + timedelta(days=ngay_hoc_cong)
        truoc = ty_chan(d0 - timedelta(days=14), d0)
        sau_ = ty_chan(NGAY0 + timedelta(days=SO_NGAY - 14), NGAY0 + timedelta(days=SO_NGAY))
    else:
        truoc = sau_ = 1.0
    kiem.append((f"Agent tự soi: tỷ lệ đề xuất chạm bị cổng chặn giảm từ 14 ngày trước bài học đầu tiên tới 14 ngày cuối ({truoc:.0%} → {sau_:.0%})", ngay_hoc_cong is not None and sau_ < truoc))
    brier = (hn or {}).get("brier") or []
    kiem.append(("Hệ thống tự chấm: Brier các tuần cuối dưới 0,25 (đoán tốt hơn bừa)", bool(brier) and sum(b["brier"] for b in brier) / len(brier) < 0.25))
    chuyen = {}
    for n in nhat:
        chuyen.setdefault(n["giai_doan"], n["ngay"])
    kq = {"chuyen_giai_doan_ngay": chuyen, "kiem": [{"ten": k, "dat": bool(v)} for k, v in kiem], "theo_ngay": nhat,
          "tong_cham_de_xuat": lan_cham, "hoc": {"bai_hoc": bh, "phan_hoi_bai": dict(ph), "he_so_tru_cot": hs, "thay_doi": td,
          "brier": brier, "tham_so": hs_all, "hook_theo_bai": hook_theo_bai, "ngay_hoc_cong": ngay_hoc_cong, "chan_14_truoc_sau": [truoc, sau_]}}
    out = os.path.join(HOME, "bao-cao", "gia-lap.json")
    json.dump(kq, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in kiem:
        print(("ĐẠT  " if v else "TRƯỢT") + "  " + k)
    print("Chuyển giai đoạn:", chuyen)
    print("Ngày cuối:", nhat[-1])
    return all(v for _, v in kiem)


if __name__ == "__main__":
    sys.exit(0 if main_gia_lap() else 1)
