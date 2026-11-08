"""Kiểm pipe.py trên dự án giả theo mẫu deck-slide. Chạy: python -m unittest tests/test_pipe.py"""
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC / "scripts"))
import pipe  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"\0" * 2048
NOI_DUNG = {
    "noi-dung.json": {"id": "s", "kieu": "noi-dung", "tieu_de": "t", "diem": ["a"]},
    "anh-prompt.json": {"prompt": "p", "ref": ["neo.png"]},
    "ra-anh.json": {"ket_luan": "dat"},
    "bo-cuc.json": {"kieu": "noi-dung"},
    "slide.json": {"id": "s", "kieu": "noi-dung", "tieu_de": "t"},
}


def chay(*args):
    out, err = io.StringIO(), io.StringIO()
    ma = 0
    with redirect_stdout(out), redirect_stderr(err):
        try:
            pipe.main([str(a) for a in args])
        except SystemExit as e:
            ma = e.code or 0
    return ma, out.getvalue() + err.getvalue()


class TestPipe(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.d = self.tmp / "deck"
        ma, _ = chay("moi", self.d, "--mau", "deck-slide", "--so", 5)
        self.assertEqual(ma, 0)
        for ten in ("01-de-bai.md", "02-bang-chung.csv", "06-offer.json", "08-the-phong-cach.json", "thuong-hieu.json"):
            (self.d / "chung" / ten).write_text("{}" if ten.endswith(".json") else "x", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def ghi(self, muc, tep, noi_dung=None):
        p = self.d / "muc" / muc / tep
        if tep.endswith(".png"):
            p.write_bytes(PNG)
        else:
            p.write_text(json.dumps(noi_dung or NOI_DUNG[tep]), encoding="utf-8")

    def lam_het(self):
        """Làm mọi ô theo đúng thứ tự `viec` trả về, như Claude sẽ làm."""
        for _ in range(100):
            viec = pipe.danh_sach_viec(pipe.DuAn(self.d))
            if not viec:
                return
            for v in viec:
                self.ghi(v["muc"], Path(v["ghi"]).name)
                ma, out = chay("xong", self.d, "--muc", v["muc"], "--tang", v["tang"])
                self.assertEqual(ma, 0, out)

    def ma_tran(self):
        return pipe.DuAn(self.d).ma_tran()

    def test_bat_dau_chi_tang_dau_san_sang(self):
        mt = self.ma_tran()
        self.assertEqual({mt[m]["noi-dung"] for m in mt}, {"san-sang"})
        self.assertEqual({mt[m]["dung"] for m in mt}, {"cho"})

    def test_lam_het_thi_xong(self):
        self.lam_het()
        mt = self.ma_tran()
        self.assertEqual({s for h in mt.values() for s in h.values()}, {"xong"})

    def test_nhanh_song_song_cung_hien(self):
        self.ghi("slide-01", "noi-dung.json")
        chay("xong", self.d, "--muc", "slide-01", "--tang", "noi-dung")
        tang = {v["tang"] for v in pipe.danh_sach_viec(pipe.DuAn(self.d), muc="slide-01")}
        self.assertEqual(tang, {"anh-prompt", "bo-cuc"})

    def test_linh_sua_slide_4_chi_lam_cu_slide_4(self):
        self.lam_het()
        self.ghi("slide-04", "noi-dung.json", {"id": "s", "kieu": "noi-dung", "tieu_de": "Linh viết lại"})
        self.assertEqual(self.ma_tran()["slide-04"]["noi-dung"], "sua-tay")
        ma, _ = chay("nhan", self.d, "--muc", "slide-04", "--tang", "noi-dung")
        self.assertEqual(ma, 0)
        mt = self.ma_tran()
        cu = sorted((m, t) for m, h in mt.items() for t, s in h.items() if s == "cu")
        self.assertEqual({m for m, _ in cu}, {"slide-04"})
        self.assertEqual(len(cu), 5)  # mọi tầng sau nội dung của slide 4
        viec = pipe.danh_sach_viec(pipe.DuAn(self.d))
        self.assertEqual({(v["muc"], v["tang"]) for v in viec},
                         {("slide-04", "anh-prompt"), ("slide-04", "bo-cuc")})
        self.lam_het()
        mt = self.ma_tran()
        self.assertEqual(mt["slide-04"]["noi-dung"], "xong")
        self.assertTrue(pipe.DuAn(self.d).ban_ghi("slide-04", "noi-dung")["khoa"])

    def test_doi_tep_chung_lam_cu_dung_tang_doc_no(self):
        self.lam_het()
        (self.d / "chung" / "08-the-phong-cach.json").write_text('{"mau": "moi"}', encoding="utf-8")
        mt = self.ma_tran()
        for m in mt:
            self.assertEqual(mt[m]["noi-dung"], "xong")
            self.assertEqual(mt[m]["bo-cuc"], "xong")
            self.assertEqual(mt[m]["anh-prompt"], "cu")
            self.assertEqual(mt[m]["dung"], "cu")

    def test_slide_khong_anh_bo_qua_lan_xuong(self):
        self.ghi("slide-02", "noi-dung.json")
        chay("xong", self.d, "--muc", "slide-02", "--tang", "noi-dung")
        ma, _ = chay("bo-qua", self.d, "--muc", "slide-02", "--tang", "anh-prompt", "--ly-do", "slide chữ")
        self.assertEqual(ma, 0)
        mt = self.ma_tran()["slide-02"]
        self.assertEqual(mt["tao-anh"], "bo-qua")
        self.assertEqual(mt["ra-anh"], "bo-qua")
        self.ghi("slide-02", "bo-cuc.json")
        chay("xong", self.d, "--muc", "slide-02", "--tang", "bo-cuc")
        self.assertEqual(self.ma_tran()["slide-02"]["dung"], "san-sang")

    def test_cong_truot_khong_chot(self):
        self.ghi("slide-01", "noi-dung.json", {"id": "s", "kieu": "noi-dung", "tieu_de": ""})
        ma, out = chay("xong", self.d, "--muc", "slide-01", "--tang", "noi-dung")
        self.assertEqual(ma, 1)
        self.assertIn("tieu_de", out)
        self.assertEqual(self.ma_tran()["slide-01"]["noi-dung"], "san-sang")

    def test_het_tai_nguyen_thu_lai_mot_lan_roi_dung(self):
        for t in ("noi-dung", "anh-prompt"):
            self.ghi("slide-01", f"{t}.json")
            chay("xong", self.d, "--muc", "slide-01", "--tang", t)
        chay("loi", self.d, "--muc", "slide-01", "--tang", "tao-anh", "--ly-do", "hết lượt", "--tai-nguyen")
        self.assertEqual(self.ma_tran()["slide-01"]["tao-anh"], "loi")
        ma, _ = chay("lam-lai", self.d, "--muc", "slide-01", "--tang", "tao-anh")
        self.assertEqual(ma, 0)
        chay("loi", self.d, "--muc", "slide-01", "--tang", "tao-anh", "--ly-do", "hết lượt", "--tai-nguyen")
        self.assertEqual(self.ma_tran()["slide-01"]["tao-anh"], "dung")
        ma, _ = chay("lam-lai", self.d, "--muc", "slide-01", "--tang", "tao-anh")
        self.assertEqual(ma, 2)
        chay("sang-nay", self.d)
        self.assertIn("dừng vì hết tài nguyên", (self.d / "SANG-NAY.md").read_text(encoding="utf-8"))

    def test_o_khoa_cu_chi_viet_de_xuat(self):
        self.lam_het()
        chay("nhan", self.d, "--muc", "slide-03", "--tang", "bo-cuc")
        self.ghi("slide-03", "noi-dung.json", {"id": "s", "kieu": "noi-dung", "tieu_de": "khác"})
        self.assertEqual(self.ma_tran()["slide-03"]["noi-dung"], "sua-tay")
        chay("nhan", self.d, "--muc", "slide-03", "--tang", "noi-dung")
        self.assertEqual(self.ma_tran()["slide-03"]["bo-cuc"], "cu-khoa")
        viec = [v for v in pipe.danh_sach_viec(pipe.DuAn(self.d)) if v["tang"] == "bo-cuc"]
        self.assertTrue(viec[0]["ghi"].endswith("bo-cuc.de-xuat.json"))
        ma, _ = chay("xong", self.d, "--muc", "slide-03", "--tang", "bo-cuc")
        self.assertEqual(ma, 2)

    def test_pipeline_khai_sai_thu_tu(self):
        with self.assertRaises(pipe.LoiPipe):
            pipe.kiem_pipeline({"tang": [{"id": "b", "ra": "b", "can": ["a"]}, {"id": "a", "ra": "a"}]})

    def test_mau_deu_hop_le(self):
        for p in (GOC / "mau").glob("*.json"):
            pipe.kiem_pipeline(json.loads(p.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
