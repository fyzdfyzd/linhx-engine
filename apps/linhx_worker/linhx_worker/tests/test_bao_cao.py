import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bao_cao  # noqa: E402

MAU = {"ai": [
    {"ten": "ChatGPT", "cau": [
        {"ma": "Q1", "nhac_brand": True}, {"ma": "Q2", "nhac_brand": False}, {"ma": "Q3", "nhac_brand": True, "de_xuat": "khuyen"},
        {"ma": "Q4", "nhan": "dung", "du_kien": {"nam": "thành lập 2015", "website": "https://www.abc.vn/"}},
        {"ma": "Q5", "nhan": "bia"}, {"ma": "Q7", "de_xuat": "co_dieu_kien", "ly_do_sai": True}]},
    {"ten": "Gemini", "cau": [
        {"ma": "Q1", "nhac_brand": False}, {"ma": "Q4", "nhan": "cu", "du_kien": {"nam": "2015", "website": "abc.vn"}},
        {"ma": "Q3", "loi": "captcha"}]},
    {"ten": "Claude", "loi": "đòi đăng nhập", "cau": []},
]}


class TestBaoCao(unittest.TestCase):
    def test_chi_so(self):
        c = bao_cao.tinh(MAU)
        g, ge, cl = c["hang"]
        self.assertEqual(g["co_mat"], 67)
        self.assertEqual(g["dung"], 50)
        self.assertEqual(g["de_xuat"], 65)  # (100 + 60*0.5)/2
        self.assertEqual(ge["co_mat"], 0)   # Q3 loi bi bo
        self.assertEqual(ge["dung"], 0)
        self.assertIsNone(ge["de_xuat"])
        self.assertIsNone(cl["co_mat"])
        self.assertEqual(c["nhat_quan"], 100)  # nam + website khop giua 2 AI

    def test_tach_json_trong_chu(self):
        s = "Đây là kết quả:\n```json\n" + json.dumps(MAU) + "\n```\nxong"
        self.assertTrue(bao_cao.dung(s)["ok"])

    def test_khong_phai_json(self):
        r = bao_cao.dung("agy trả chữ thường")
        self.assertFalse(r["ok"])
        self.assertEqual(r["tho"], "agy trả chữ thường")


if __name__ == "__main__":
    unittest.main()
