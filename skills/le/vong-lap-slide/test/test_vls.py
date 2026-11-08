"""Test vls.py trên deck mẫu có lỗi cố ý. Chạy: python test/test_vls.py"""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
VLS = [sys.executable, str(GOC / "scripts" / "vls.py")]
F = "font-family:Arial"
SLIDES = {
    "sach": f'<section style="background:#FAF9F6;color:#1F2933;{F};padding:120px"><h2 style="font-size:56px">Doanh thu quý ba tăng nhờ kênh bán lẻ mới</h2><p style="font-size:32px;margin-top:40px">Kênh bán lẻ đóng góp 40% tăng trưởng</p></section>',
    "tran-the": f'<section style="background:#fff;color:#111;{F};padding:120px"><h2 style="font-size:56px">Thẻ này chứa quá nhiều chữ so với chiều cao</h2><div style="background:#eee;height:120px;width:600px;margin-top:40px;padding:16px"><p style="font-size:32px">Một đoạn rất dài sẽ tràn ra ngoài thẻ có nền xám vì chiều cao thẻ bị cố định quá thấp so với lượng chữ</p></div></section>',
    "chong": f'<section style="background:#fff;color:#111;{F};padding:120px;position:relative"><h2 style="font-size:56px">Hai khối chữ đè lên nhau ở giữa slide này</h2><p style="position:absolute;left:300px;top:400px;font-size:40px">Khối thứ nhất nằm đây</p><p style="position:absolute;left:340px;top:410px;font-size:40px">Khối thứ hai đè lên</p></section>',
    "nho-mo": f'<section style="background:#fff;{F};padding:120px"><h2 style="font-size:56px;color:#111">Chữ nhỏ và chữ nhạt làm người ngồi cuối phòng khó đọc</h2><p style="font-size:16px;color:#111;margin-top:30px">Chú thích chỉ 16px</p><p style="font-size:30px;color:#c8c8c8;margin-top:30px">Chữ xám nhạt trên nền trắng</p></section>',
    "nen-anh": f'<section style="background:linear-gradient(90deg,#ffffff 0%,#ffffff 50%,#101010 50%);{F};padding:120px"><h2 style="font-size:56px;color:#ffffff;width:1600px">Chữ trắng đặt trên nền nửa trắng nửa đen</h2></section>',
    "tieu-de-dai": f'<section style="background:#fff;color:#111;{F};padding:120px"><h2 style="font-size:72px;width:900px">Tiêu đề này dài quá mức cần thiết nên phải xuống tới ba bốn dòng trên slide hẹp</h2></section>',
    "phong-thieu": '<section style="background:#fff;color:#111;font-family:\'Phong Khong Co\';padding:120px"><h2 style="font-size:56px">Phông không nạp được thì đo tràn không tin được</h2></section>',
    "giu-cho": f'<section style="background:#fff;color:#111;{F};padding:120px"><h2 style="font-size:56px">Slide còn chữ giữ chỗ chưa thay nội dung thật</h2><p style="font-size:32px">Lorem ipsum dolor sit amet</p></section>',
    "tran-khung": f'<section style="background:#fff;color:#111;{F};padding:120px;position:relative"><h2 style="font-size:56px">Một dòng chữ chạy ra khỏi mép phải của slide</h2><p style="position:absolute;left:1700px;top:600px;font-size:40px;white-space:nowrap">Chữ này ra ngoài khung</p></section>',
}
KY_VONG = {"sach": set(), "tran-the": {"tran-the"}, "chong": {"chong-lan"}, "nho-mo": {"chu-nho", "tuong-phan"},
           "nen-anh": {"tuong-phan"}, "tieu-de-dai": {"tieu-de-dai"}, "phong-thieu": {"phong"},
           "giu-cho": {"giu-cho"}, "tran-khung": {"tran-khung"}}


def chay(*a, ok=True):
    r = subprocess.run(VLS + list(a), capture_output=True, text=True)
    if ok and r.returncode != 0:
        raise AssertionError(f"{a} lỗi:\n{r.stdout}\n{r.stderr}")
    return r


def main():
    tam = Path(tempfile.mkdtemp(prefix="vls-test-"))
    d = tam / "deck"; (d / "slides").mkdir(parents=True)
    (d / "deck.json").write_text(json.dumps({"order": list(SLIDES)}), encoding="utf-8")
    for k, v in SLIDES.items():
        (d / "slides" / f"{k}.html").write_text(v, encoding="utf-8")
    json.dump({"tho": "agy"}, open(d / ".vong-lap-tho.json", "w"))
    tests_0 = [("cổng 0: chưa có mẫu thì từ chối dựng", chay("do", str(d), ok=False).returncode != 0)]
    chay("do", str(d), "--bo-qua-mau")
    tt = json.loads((d / ".vong-lap" / "trang-thai.json").read_text(encoding="utf-8"))
    dat = 0
    for sid, ky in KY_VONG.items():
        ma = {x["ma"] for x in tt["slides"][sid]["vong"][-1]["sai"]}
        thieu, thua = ky - ma, (ma - ky) if not ky else set()
        ok = not thieu and not thua
        dat += ok
        print(("ĐẠT " if ok else "TRƯỢT"), sid, "bắt được", sorted(ma), "" if ok else f"thiếu {sorted(thieu)} thừa {sorted(thua)}")
    # cổng: phiếu chấm
    cfg = json.loads((d / ".vong-lap" / "cau-hinh.json").read_text()); cfg["tho"] = "agy"; cfg["so_nguoi_cham"] = 1
    (d / ".vong-lap" / "cau-hinh.json").write_text(json.dumps(cfg))
    tests = list(tests_0)
    p = tam / "p.json"
    def phieu(**kw):
        base = {"slide": "sach", "nguoi_cham": "claude-sonnet", "ket_luan": "dat",
                "diem": {"y_chinh": 4, "tieu_diem": 4, "doc_duoc": 4, "can_doi": 4, "nhat_quan": 4, "toi_gian": 4, "ngang_mau": 4}, "loi": [], "tom_tat": "ổn"}
        base.update(kw); p.write_text(json.dumps(base, ensure_ascii=False), encoding="utf-8"); return str(p)
    tests.append(("từ chối thợ tự chấm", chay("cham", str(d), "--tep", phieu(nguoi_cham="agy"), ok=False).returncode != 0))
    tests.append(("từ chối 'dat' có lỗi nặng", chay("cham", str(d), "--tep", phieu(loi=[{"muc": "nang", "mo_ta": "x", "sua": "y"}]), ok=False).returncode != 0))
    tests.append(("từ chối 'dat' có tiêu chí 3 điểm", chay("cham", str(d), "--tep", phieu(diem={"y_chinh": 3, "tieu_diem": 4, "doc_duoc": 4, "can_doi": 4, "nhat_quan": 4, "toi_gian": 4, "ngang_mau": 4}), ok=False).returncode != 0))
    tests.append(("nhận phiếu hợp lệ", chay("cham", str(d), "--tep", phieu()).returncode == 0))
    # sửa nguồn sau khi chấm → phiếu hết hạn
    s = d / "slides" / "sach.html"; s.write_text(s.read_text().replace("40%", "45%"))
    r = chay("cham", str(d), "--tep", phieu(), ok=False)
    tests.append(("phiếu hết hạn khi nguồn đổi", r.returncode != 0))
    tests.append(("ket-thuc chặn khi chưa đạt", chay("ket-thuc", str(d), ok=False).returncode == 1))
    # chống sửa quá tay
    tt_ = lambda: json.loads((d / ".vong-lap" / "trang-thai.json").read_text(encoding="utf-8"))
    chay("do", str(d), "--chi", "sach", "--bo-qua-mau")
    loi5 = [{"muc": "nang", "vung": f"vùng {i}", "mo_ta": f"lỗi {i}", "sua": f"sửa {i}"} for i in range(1, 6)]
    chay("cham", str(d), "--tep", phieu(ket_luan="hong", loi=loi5))
    r = chay("trang-thai", str(d))
    tests.append(("lỗi nặng chưa xác minh thì chưa giao sửa", "chờ xác minh" in r.stdout))
    xm = tam / "xm.json"
    xm.write_text(json.dumps({"slide": "sach", "nguoi_xac_minh": "agy", "ket_qua": []}), encoding="utf-8")
    tests.append(("từ chối thợ tự xác minh", chay("xac-minh", str(d), "--tep", str(xm), ok=False).returncode != 0))
    xm.write_text(json.dumps({"slide": "sach", "nguoi_xac_minh": "gemini", "ket_qua": [{"so": 1, "giu": True, "ly_do": "x"}]}), encoding="utf-8")
    tests.append(("từ chối xác minh thiếu lỗi", chay("xac-minh", str(d), "--tep", str(xm), ok=False).returncode != 0))
    xm.write_text(json.dumps({"slide": "sach", "nguoi_xac_minh": "gemini", "ket_qua": [
        {"so": i, "giu": i != 3, "ly_do": "x"} for i in range(1, 6)]}), encoding="utf-8")
    chay("xac-minh", str(d), "--tep", str(xm))
    r = chay("phieu-sua", str(d))
    sach_phan = r.stdout.split("## sach")[1].split("##")[0]
    giao_ = [l for l in sach_phan.splitlines() if l.startswith("- [claude-sonnet")]
    tests.append(("phiếu sửa chỉ 3 lỗi đã xác minh, bỏ lỗi bị bác", len(giao_) == 3 and "lỗi 3" not in sach_phan and "KHÔNG sửa" in sach_phan))
    # bác hết → đạt
    chay("cham", str(d), "--tep", phieu(ket_luan="hong", loi=loi5[:2]))
    xm.write_text(json.dumps({"slide": "sach", "nguoi_xac_minh": "gemini", "ket_qua": [
        {"so": i, "giu": False, "ly_do": "khẩu vị"} for i in (1, 2)]}), encoding="utf-8")
    chay("xac-minh", str(d), "--tep", str(xm))
    tests.append(("bác hết lỗi nặng thì slide đạt", "đạt sau xác minh" in chay("trang-thai", str(d)).stdout))
    # sửa làm tệ hơn → lùi bước → hoàn tác
    s_ = d / "slides" / "sach.html"
    s_.write_text(s_.read_text().replace("font-size:32px", "font-size:14px"))
    chay("do", str(d), "--chi", "sach", "--bo-qua-mau")
    r = chay("trang-thai", str(d))
    tests.append(("phát hiện bản sửa tệ hơn", "lùi bước" in r.stdout))
    chay("hoan-tac", str(d), "--slide", "sach")
    chay("do", str(d), "--chi", "sach", "--bo-qua-mau")
    r = chay("trang-thai", str(d))
    sach_dong = [l for l in r.stdout.splitlines() if " sach " in l][0]
    tests.append(("hoàn tác xong dùng lại phiếu cũ, đạt", "đạt" in sach_dong))
    # viết lại cả slide → cảnh báo sửa quá tay
    chay("phieu-sua", str(d))  # phiếu mới chỉ gồm slide hỏng, không có 'sach'
    s_.write_text('<section style="background:#000;color:#fff;font-family:Arial;padding:100px"><h1 style="font-size:64px">Một slide khác hẳn được viết lại toàn bộ</h1></section>')
    chay("do", str(d), "--chi", "sach", "--bo-qua-mau")
    ly = {x["ma"] for x in tt_()["slides"]["sach"]["vong"][-1]["luu_y"]}
    tests.append(("cảnh báo viết lại và sửa ngoài phạm vi", {"sua-qua-tay", "ngoai-pham-vi"} <= ly))
    # gộp 3 phiếu: trung vị
    cfg["so_nguoi_cham"] = 3; (d / ".vong-lap" / "cau-hinh.json").write_text(json.dumps(cfg))
    chay("do", str(d), "--chi", "sach", "--bo-qua-mau", "--lam-lai")
    hai = {"y_chinh": 5, "tieu_diem": 5, "doc_duoc": 5, "can_doi": 5, "nhat_quan": 5, "toi_gian": 5, "ngang_mau": 5}
    chay("cham", str(d), "--tep", phieu(nguoi_cham="a", diem=hai))
    r1 = chay("trang-thai", str(d)).stdout
    chay("cham", str(d), "--tep", phieu(nguoi_cham="b", ket_luan="hong", diem={**hai, "ngang_mau": 2}, loi=[{"muc": "nang", "mo_ta": "x", "sua": "y"}]))
    chay("cham", str(d), "--tep", phieu(nguoi_cham="c", ket_luan="hong", diem={**hai, "ngang_mau": 3}, loi=[{"muc": "nang", "mo_ta": "z", "sua": "w"}]))
    c = tt_()["slides"]["sach"]["vong"][-1]["cham"]
    tests.append(("3 phiếu: 1 phiếu chưa đủ, đủ 3 thì lấy trung vị và đa số", "1/3 phiếu" in r1 and c["ket_luan"] == "hong" and c["diem"]["ngang_mau"] == 3))
    # nhánh pptx (cần LibreOffice + PyMuPDF)
    if shutil.which("soffice") or shutil.which("libreoffice"):
        px = tam / "loi.pptx"
        subprocess.run([sys.executable, str(GOC / "test" / "tao_pptx_loi.py"), str(px)], check=True)
        chay("do", str(px), "--bo-qua-mau")
        tp = json.loads((tam / "loi.vong-lap" / "trang-thai.json").read_text(encoding="utf-8"))
        for sid, ky in {"s01": set(), "s02": {"chu-nho", "tran-hop"}, "s03": {"tuong-phan"}}.items():
            ma = {x["ma"] for x in tp["slides"][sid]["vong"][-1]["sai"]}
            tests.append((f"pptx {sid} bắt đúng {sorted(ky) or 'không lỗi'} (được {sorted(ma)})", ma == ky))
    for ten, ok in tests:
        print(("ĐẠT " if ok else "TRƯỢT"), ten)
    tong = dat + sum(ok for _, ok in tests); n = len(KY_VONG) + len(tests)
    print(f"\n{tong}/{n} đạt · thư mục thử {tam}")
    sys.exit(0 if tong == n else 1)


if __name__ == "__main__":
    main()
