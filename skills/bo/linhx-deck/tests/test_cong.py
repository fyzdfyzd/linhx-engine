"""Kiểm chính các cổng của deck.py bằng lỗi cài sẵn. Chạy: python tests/test_cong.py"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
S = [sys.executable, str(GOC / "scripts" / "deck.py")]
MAU_DECK = GOC / "tests" / "mau-deck"


NEO_TAM = Path(tempfile.mkdtemp()) / "neo"  # thư viện neo riêng cho test, không đụng du-lieu/neo thật


def chay(*a):
    import os
    r = subprocess.run(S + list(a), capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "LINHX_DECK_NEO": str(NEO_TAM)})
    return r.returncode, r.stdout + r.stderr


def deck_tam():
    d = Path(tempfile.mkdtemp()) / "deck"
    shutil.copytree(MAU_DECK, d)
    return d


def sua_deck(d, f):
    p = d / "10-deck.json"
    dk = json.loads(p.read_text(encoding="utf-8"))
    f(dk)
    p.write_text(json.dumps(dk, ensure_ascii=False), encoding="utf-8")


def test_deck_mau_dat():
    d = deck_tam()
    rc, out = chay("kiem-deck", str(d))
    assert rc == 0, out


def test_so_khong_nguon():
    d = deck_tam()
    def f(dk):
        dk["slides"][3]["dai"] = "Khách mất 37% thời gian cho báo cáo."
        dk["slides"][3].pop("bang_chung", None)
    sua_deck(d, f)
    rc, out = chay("kiem-deck", str(d))
    assert rc == 1 and "không có bang_chung" in out, out


def test_tieu_de_khong_ket_luan():
    d = deck_tam()
    sua_deck(d, lambda dk: dk["slides"][3].update(tieu_de="Bối cảnh thị trường"))
    rc, out = chay("kiem-deck", str(d))
    assert rc == 1 and "phải là một câu kết luận" in out, out


def test_tu_cam_theo_brand():
    d = deck_tam()
    sua_deck(d, lambda dk: dk.update(brand="chiemtinh"))
    rc, out = chay("kiem-deck", str(d))
    assert rc == 1 and "cụm cấm 'giải hạn'" in out, out


def test_tran_chu_va_so_the():
    d = deck_tam()
    sua_deck(d, lambda dk: dk["slides"][3]["muc"].extend([{"tieu_de": "x", "noi_dung": "y"}] * 2))
    rc, out = chay("kiem-deck", str(d))
    assert rc == 1 and "tối đa 4" in out, out


def test_offer_khong_co_nang_luc():
    d = deck_tam()
    (d / "04-pain-gain.json").write_text(json.dumps({"pains": [
        {"id": "P1", "mo_ta": "a", "diem": 9, "bang_chung": ["BC01"]},
        {"id": "P2", "mo_ta": "b", "diem": 5, "bang_chung": [], "nhan": "gia-thuyet"},
        {"id": "P3", "mo_ta": "c", "diem": 4, "bang_chung": [], "nhan": "gia-thuyet"}],
        "gains": [{"id": "G1", "mo_ta": "d", "diem": 7, "bang_chung": [], "nhan": "gia-thuyet"},
                  {"id": "G2", "mo_ta": "e", "diem": 6, "bang_chung": [], "nhan": "gia-thuyet"}]}), encoding="utf-8")
    of = {"khoang_trong": [], "offers": [
        {"id": "O1", "ten": "Agent", "giai_pain": ["P1"], "nang_luc": ["NL-04"], "nhan": "chinh"},
        {"id": "O2", "ten": "Phụ", "giai_pain": ["P2"], "nang_luc": ["NL-01"], "nhan": "chinh"},
        {"id": "O3", "ten": "Lạ", "giai_pain": ["P1"], "nang_luc": ["NL-99"], "nhan": "chinh"}]}
    (d / "06-offer.json").write_text(json.dumps(of, ensure_ascii=False), encoding="utf-8")
    rc, out = chay("doi-chieu", str(d))
    assert rc == 1, out
    assert "O1: năng lực chính (NL-04) chưa 'da-chung-minh'" in out, out
    assert "O2: không giải pain nào có điểm ≥ 7" in out, out
    assert "NL-99" in out, out


def test_ra_anh_khong_tu_cho_qua():
    d = deck_tam()
    sua_deck(d, lambda dk: dk["slides"][0].update(anh={"tep": "bia.png", "y_tuong": "x", "ti_le": "16:9"}))
    (d / "12-ra-anh.json").write_text(json.dumps({"anh": [{"tep": "bia.png", "kiem": {h: True for h in
        ["H1", "H2", "H3", "H4", "H5", "H6", "H7"]} | {"H8": False}, "loi": [], "ket_luan": "dat"}]}), encoding="utf-8")
    rc, out = chay("cong", str(d), "12")
    assert rc == 1 and "không được tự cho qua" in out, out


def test_xuat_claude_slides():
    d = deck_tam()
    rc, out = chay("xuat", str(d))
    assert rc == 0, out
    dk = json.loads((d / "13-claude-deck/project/deck.json").read_text(encoding="utf-8"))
    assert dk["v"] == 4 and len(dk["order"]) == len(list((d / "13-claude-deck/project/slides").glob("*.html")))
    for f in (d / "13-claude-deck/project/slides").glob("*.html"):
        t = f.read_text(encoding="utf-8")
        assert t.count("<section") == 1 and "<style" not in t and "class=" not in t and "margin" not in t, f


def png(p, w=1536, h=864, mau=0):
    import struct, zlib
    def khoi(k, d):
        return struct.pack(">I", len(d)) + k + d + struct.pack(">I", zlib.crc32(k + d) & 0xffffffff)
    du_lieu = zlib.compress((b"\x00" + bytes([mau, 80, 120]) * w) * h)
    Path(p).write_bytes(b"\x89PNG\r\n\x1a\n" + khoi(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                        + khoi(b"IDAT", du_lieu) + khoi(b"IEND", b""))


def test_vong_anh_chrome_co_ref_va_sua():
    d = deck_tam()
    tai = d.parent / "Downloads"; tai.mkdir()
    sua_deck(d, lambda dk: dk["slides"][0].update(anh={"tep": "bia.png", "y_tuong": "x", "ti_le": "16:9"}))
    (d / "08-moodboard").mkdir(); png(d / "08-moodboard/mb-01.png", 600, 400)
    rc, out = chay("goi-anh", str(d)); assert rc == 0, out
    rc, out = chay("cong", str(d), "11"); assert rc == 0, out
    png(tai / "ChatGPT Image 1.png")
    rc, out = chay("nhan-anh", str(d), "--tu", str(tai), "--vao", "anh", "--ten", "anh-neo.png")
    assert rc != 0 and "phải có ảnh tham chiếu" in out, out
    rc, out = chay("nhan-anh", str(d), "--tu", str(tai), "--vao", "anh", "--ten", "anh-neo.png", "--ref", "08-moodboard/mb-01.png")
    assert rc == 0, out
    png(tai / "ChatGPT Image 2.png")
    rc, out = chay("nhan-anh", str(d), "--tu", str(tai), "--vao", "anh", "--ten", "bia.png", "--ref", "08-moodboard/mb-01.png")
    assert rc != 0 and "ảnh neo" in out, out
    rc, out = chay("nhan-anh", str(d), "--tu", str(tai), "--vao", "anh", "--ten", "bia.png",
                   "--ref", "11-goi-anh/anh/anh-neo.png,08-moodboard/mb-01.png")
    assert rc == 0, out
    rc, out = chay("ra-anh", str(d)); assert rc == 0, out
    p = d / "12-ra-anh.json"; ra = json.loads(p.read_text(encoding="utf-8"))
    for x in ra["anh"]:
        x["kiem"].update({h: True for h in ["H1", "H2", "H3", "H4", "H7"]}); x["kiem"]["H8"] = False
        x["loi"] = [{"muc": "H8", "muc_do": "nang", "mo_ta": "warped glass cards", "sua": "straighten the glass cards"}]
        x["ket_luan"] = "sua"
    p.write_text(json.dumps(ra, ensure_ascii=False), encoding="utf-8")
    rc, out = chay("sua-anh", str(d)); assert rc == 0 and "straighten the glass cards" in out and "vòng 2" in out, out
    png(tai / "ChatGPT Image 3.png", mau=200)
    rc, out = chay("nhan-anh", str(d), "--tu", str(tai), "--vao", "anh", "--ten", "bia.png",
                   "--ref", "11-goi-anh/anh/anh-neo.png"); assert rc == 0 and "bản 2" in out, out
    assert (d / "11-goi-anh/anh/cu/bia-v1.png").exists()
    rc, out = chay("ra-anh", str(d)); assert "chấm lại" in out, out
    x = json.loads(p.read_text(encoding="utf-8"))["anh"][0]
    assert x["kiem"]["H1"] is None and x["ket_luan"] is None and len(x["lich_su"]) == 1, x
    x_all = json.loads(p.read_text(encoding="utf-8"))
    for x in x_all["anh"]:
        x["kiem"] = {h: True for h in x["kiem"]}; x["loi"] = []; x["ket_luan"] = "dat"
    p.write_text(json.dumps(x_all, ensure_ascii=False), encoding="utf-8")
    rc, out = chay("cong", str(d), "12"); assert rc == 0, out


def test_logo_ta_va_logo_khach():
    d = deck_tam()
    sua_deck(d, lambda dk: dk.update(khach="Ngân hàng A"))
    rc, out = chay("kiem-deck", str(d), "--ban-cuoi")
    assert rc == 1 and "thiếu logo_ta" in out and "thiếu logo_khach" in out, out
    png(d.parent / "ta.png", 300, 100); png(d.parent / "kh.png", 300, 100, mau=200)
    rc, out = chay("logo", str(d), "--ta", str(d.parent / "ta.png"), "--khach", str(d.parent / "kh.png"))
    assert rc == 0 and (d / "logo/ta-ta.png").exists() and (d / "logo/khach-kh.png").exists(), out
    rc, out = chay("kiem-deck", str(d), "--ban-cuoi")
    assert "logo" not in out, out
    (d / "13-claude-deck").mkdir(exist_ok=True)
    (d / "13-claude-deck/anh-map.json").write_text(json.dumps({"logo/ta-ta.png": "/_blob/aa", "logo/khach-kh.png": "/_blob/bb"}))
    rc, out = chay("xuat", str(d), "--anh-map", str(d / "13-claude-deck/anh-map.json")); assert rc == 0, out
    bia = next((d / "13-claude-deck/project/slides").glob(json.loads((d / "10-deck.json").read_text(encoding="utf-8"))["slides"][0]["id"] + ".html")).read_text(encoding="utf-8")
    assert "/_blob/aa" in bia and "/_blob/bb" in bia, bia
    rc, out = chay("cong", str(d), "13")
    assert rc == 1 and "chưa chụp kiểm slide" in out, out


def test_neo_brand_dung_chung():
    a = deck_tam()
    (a / "11-goi-anh/anh").mkdir(parents=True); png(a / "11-goi-anh/anh/anh-neo.png")
    (a / "08-moodboard").mkdir(); png(a / "08-moodboard/mb-01.png", 600, 400)
    brand = json.loads((a / "10-deck.json").read_text(encoding="utf-8")).get("brand", "linhx")
    (a / "08-the-phong-cach.json").write_text(json.dumps({"brand": brand, "huong": [{"id": "H1", "anh": ["08-moodboard/mb-01.png"]}],
        "huong_chon": "H1", "nguon_anh": [{"tep": "08-moodboard/mb-01.png", "nguon": "x"}]}), encoding="utf-8")
    rc, out = chay("neo", str(a), "--luu"); assert rc == 0 and (NEO_TAM / brand / "anh-neo.png").exists(), out
    rc, out = chay("neo", str(a), "--luu"); assert rc != 0 and "--ghi-de" in out, out
    b = deck_tam()
    sua_deck(b, lambda dk: dk["slides"][0].update(anh={"tep": "bia.png", "y_tuong": "x", "ti_le": "2:3"}))
    rc, out = chay("goi-anh", str(b)); assert rc != 0 and "neo <dir> --lay" in out, out
    rc, out = chay("neo", str(b), "--lay"); assert rc == 0, out
    assert (b / "11-goi-anh/anh/anh-neo.png").read_bytes() == (a / "11-goi-anh/anh/anh-neo.png").read_bytes()
    nk = json.loads((b / "11-goi-anh/nhat-ky.json").read_text(encoding="utf-8"))
    assert nk["anh"][0]["nguon"].startswith("neo-brand") and nk["anh"][0]["ref"], nk
    rc, out = chay("goi-anh", str(b)); assert rc == 0, out


def test_xem_bat_tran_chu():
    try:
        import playwright  # noqa: F401
    except ImportError:
        print("  (bỏ qua: không có Playwright)")
        return
    d = deck_tam()
    rc, out = chay("xuat", str(d)); assert rc == 0, out
    rc, out = chay("xem", str(d))
    assert (d / "13-claude-deck/xem/bao-cao.json").exists(), out
    sua_deck(d, lambda dk: dk["slides"][3].update(diem_chinh="X" * 160))
    chay("xuat", str(d))
    rc, out = chay("xem", str(d))
    assert rc == 1 and ("chữ tràn hộp" in out or "lấn lề" in out or "tràn khung" in out), out


def test_duyet_tu_dong_can_hoi_du_10_phut():
    d = deck_tam()
    chay("ghost", str(d))
    rc, out = chay("cong", str(d), "10")
    assert rc == 1 and "chưa được duyệt" in out, out  # bước 1, 6, 7 chưa duyệt thì bước 10 không đạt
    for b in ("1", "6", "7"):
        chay("duyet", str(d), b, "--bo-qua", "deck mẫu của test")
    rc, out = chay("cong", str(d), "10")
    assert rc == 3 and "CHỜ DUYỆT" in out, out
    rc, out = chay("duyet", str(d), "10", "--nguoi", "tu-dong-10-phut")
    assert rc != 0 and "deck.py hoi" in out, out
    rc, out = chay("hoi", str(d), "10", "--cau", "Duyệt ghost deck? Khuyến nghị: duyệt"); assert rc == 0, out
    rc, out = chay("duyet", str(d), "10", "--nguoi", "tu-dong-10-phut")
    assert rc != 0 and "phút" in out, out
    p = d / "trang-thai.json"; tt = json.loads(p.read_text(encoding="utf-8"))
    tt["hoi"]["10"]["luc"] = "2020-01-01T00:00:00+00:00"; p.write_text(json.dumps(tt), encoding="utf-8")
    sua_deck(d, lambda dk: dk["slides"][3].update(dai="Câu mới sau khi hỏi."))
    rc, out = chay("duyet", str(d), "10", "--nguoi", "tu-dong-10-phut")
    assert rc != 0 and "đã đổi sau khi hỏi" in out, out
    chay("hoi", str(d), "10", "--cau", "Bản mới")
    p = d / "trang-thai.json"; tt = json.loads(p.read_text(encoding="utf-8"))
    tt["hoi"]["10"]["luc"] = "2020-01-01T00:00:00+00:00"; p.write_text(json.dumps(tt), encoding="utf-8")
    rc, out = chay("duyet", str(d), "10", "--nguoi", "tu-dong-10-phut"); assert rc == 0, out
    rc, out = chay("cong", str(d), "10"); assert rc == 0, out


def test_duyet_tu_choi_khi_noi_dung_truot():
    d = deck_tam()
    sua_deck(d, lambda dk: dk["slides"][3].update(tieu_de="Bối cảnh thị trường"))
    rc, out = chay("duyet", str(d), "10", "--nguoi", "Linh")
    assert rc != 0 and "còn lỗi nội dung" in out, out


def test_ngay_thang_khong_phai_so_lieu():
    d = deck_tam()
    def f(dk):
        dk["slides"][3]["dai"] = "Hai bên chốt phạm vi trước ngày 31/12/2026, rà lại vào Q1."
        dk["slides"][3].pop("bang_chung", None)
    sua_deck(d, f)
    rc, out = chay("kiem-deck", str(d))
    assert "không có bang_chung" not in out, out


def test_o_anh_phai_tieng_anh_va_du_truong():
    d = deck_tam()
    sua_deck(d, lambda dk: dk["slides"][0].update(anh={"tep": "bia.png", "y_tuong": "Một cây cầu kính phát sáng giữa đêm", "ti_le": "9:7"}))
    rc, out = chay("kiem-deck", str(d))
    assert rc == 1 and "tiếng Anh" in out and "ti_le '9:7'" in out and "thiếu 'mo_ta'" in out, out


def test_ngay_va_tien_khong_bat_nham():
    d = deck_tam()
    def f(dk):
        dk["slides"][3]["dai"] = "Chốt trước ngày 23/10, thị trường 76,1 triệu người dùng, vàng 24K."
        dk["slides"][3]["bang_chung"] = ["BC01"]
    sua_deck(d, f)
    (d / "01-de-bai.md").write_text("- Giá/khung giá được phép nói: không nêu giá\n", encoding="utf-8")
    rc, out = chay("kiem-deck", str(d))
    assert "con số tiền" not in out and "'/10'" not in out, out
    sua_deck(d, lambda dk: dk["slides"][3].update(dai="Chi phí gói 120 triệu đồng."))
    rc, out = chay("kiem-deck", str(d))
    assert rc == 1 and "con số tiền" in out, out


def test_tieu_diem_va_hinh_thuc():
    d = deck_tam()
    def f(dk):
        dk["slides"][3].pop("diem_chinh", None); dk["slides"][3].pop("nhan_manh", None)
        dk["slides"][4]["hinh_thuc"] = "bieu-do"
    sua_deck(d, f)
    rc, out = chay("kiem-deck", str(d))
    assert rc == 1 and "thiếu diem_chinh" in out and "khối ngang nhau" in out and "không khớp kiểu" in out, out


def test_bieu_do_can_nguon_va_diem_nhan():
    d = deck_tam()
    sua_deck(d, lambda dk: dk["slides"].insert(5, {"id": "bd", "kieu": "bieu-do", "tieu_de": "Doanh thu quý tăng gấp đôi nhờ kênh mới mở trong năm",
        "diem_chinh": "Kênh mới chiếm phần lớn tăng trưởng", "hinh_thuc": "bieu-do", "ghi_chu": "x " * 50,
        "bieu_do": {"loai": "cot", "nhan": ["Q1", "Q2", "Q3"], "chuoi": [{"ten": "DT", "gia_tri": [10, 14, 22]}]}}))
    rc, out = chay("kiem-deck", str(d))
    assert rc == 1 and "diem_nhan" in out and "bang_chung" in out, out


def test_hanh_trinh_chu_y():
    d = deck_tam()
    p = d / "10-hanh-trinh.json"; ht = json.loads(p.read_text(encoding="utf-8"))
    for r in ht["slides"]:
        r["tai"] = 4; r["moc"] = "khong"
    p.write_text(json.dumps(ht, ensure_ascii=False), encoding="utf-8")
    rc, out = chay("hanh-trinh", str(d))
    assert rc == 1 and "câu móc" in out and "quá 2 slide nặng" in out and "đặt lại chú ý" in out, out


def test_bo_cuc_moi_kieu_phai_co():
    d = deck_tam()
    p = d / "08-the-phong-cach.json"; t = json.loads(p.read_text(encoding="utf-8"))
    t["bo_cuc_slide"].pop("so-lon"); t["bo_cuc_slide"]["bang"] = "khong-co"
    p.write_text(json.dumps(t, ensure_ascii=False), encoding="utf-8")
    chay("ghost", str(d))
    rc, out = chay("cong", str(d), "10")
    assert "chưa chọn bố cục: ['so-lon']" in out and "bang→khong-co" in out, out
    rc, out = chay("bo-cuc", "chon", str(d))
    assert "so-lon → so-lon-hero" in out, out


def test_bieu_do_va_anh_nen_ve_duoc():
    try:
        import playwright  # noqa: F401
    except ImportError:
        return
    d = deck_tam()
    sua_deck(d, lambda dk: dk["slides"].insert(5, {"id": "bd", "kieu": "bieu-do", "tieu_de": "Doanh thu quý tăng gấp đôi nhờ kênh mới mở trong năm",
        "diem_chinh": "Kênh mới chiếm phần lớn tăng trưởng", "hinh_thuc": "bieu-do", "bang_chung": ["BC01"], "nguon": "x",
        "bieu_do": {"loai": "cot", "nhan": ["Q1", "Q2", "Q3"], "chuoi": [{"ten": "DT", "gia_tri": [10, 14, 22]}], "diem_nhan": 2}}))
    rc, out = chay("xuat", str(d)); assert rc == 0, out
    html_ = (d / "13-claude-deck/project/slides/bd.html").read_text(encoding="utf-8")
    assert 'data-hero="1"' in html_ and "22" in html_, html_
    rc, out = chay("xem", str(d))
    assert "bd: không có tiêu điểm" not in out, out


def test_gia_xet_tung_truong_va_linh_can_chot():
    d = deck_tam()
    def f(dk):
        dk["slides"][3]["diem_chinh"] = "Sản phẩm đủ vững để đầu tư tiếp"
        dk["slides"][3]["dai"] = "Doanh thu 73,30 tỷ trong hai tháng [CẦN LINH: số chốt]"
        dk["slides"][3]["bang_chung"] = ["BC01"]
    sua_deck(d, f)
    (d / "01-de-bai.md").write_text("- Giá/khung giá được phép nói: không nêu giá\n", encoding="utf-8")
    rc, out = chay("kiem-deck", str(d))
    assert "con số tiền" not in out, out
    rc, out = chay("trang-thai", str(d))
    assert "Linh cần chốt" in out and "CẦN LINH: số chốt" in out, out


if __name__ == "__main__":
    loi = 0
    for ten, f in list(globals().items()):
        if ten.startswith("test_"):
            try:
                f()
                print(f"✓ {ten}")
            except AssertionError as e:
                loi += 1
                print(f"✗ {ten}\n{str(e)[:800]}")
    sys.exit(1 if loi else 0)
