"""python -m unittest discover -s tests (chạy trong thư mục plugin)."""
import os
import sys
import unicodedata
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import viet_chuan as vc  # noqa: E402


class TestVietChuan(unittest.TestCase):
    def test_phone(self):
        self.assertEqual(vc.phone_vn("+84 912 345 678")[0], "0912345678")
        self.assertEqual(vc.phone_vn("01688123456")[0], "0388123456")
        self.assertEqual(vc.phone_vn("01208123456")[0], "0708123456")
        self.assertEqual(vc.phone_vn("912345678")[0], "0912345678")
        self.assertEqual(vc.phone_vn("0912.345.678")[0], "0912345678")
        self.assertEqual(vc.phone_vn("02438123456")[0], "02438123456")
        self.assertTrue(vc.phone_vn("091234")[1])
        self.assertTrue(vc.phone_vn("0912345678 / 0987654321")[1])

    def test_email(self):
        self.assertEqual(vc.email(" An.Nguyen@Example.COM ")[0], "an.nguyen@example.com")
        self.assertTrue(vc.email("abc@")[1])

    def test_date(self):
        self.assertEqual(vc.date_vn("3/1/1990")[0], "1990-01-03")
        self.assertEqual(vc.date_vn("03.01.1990")[0], "1990-01-03")
        self.assertEqual(vc.date_vn("1990-01-03")[0], "1990-01-03")
        self.assertTrue(vc.date_vn("12/25/1990")[1])
        self.assertTrue(vc.date_vn("hôm qua")[1])

    def test_giay_to(self):
        self.assertEqual(vc.cccd("79123456789")[0], "079123456789")
        self.assertEqual(vc.cccd("079123456789.0")[0], "079123456789")
        self.assertIn("CMND", vc.cccd("123456789")[1])
        self.assertEqual(vc.mst("0101234567001")[0], "0101234567-001")

    def test_text(self):
        nfd = unicodedata.normalize("NFD", "Nguyễn")
        self.assertEqual(vc.nfc(nfd)[0], "Nguyễn")
        self.assertEqual(vc.fix_mojibake("Nguyá»…n VÄƒn An")[0], "Nguyễn Văn An")
        self.assertEqual(vc.trim("  Lê   Thu  ")[0], "Lê Thu")
        self.assertEqual(vc.name_vn("NGUYỄN văn AN")[0], "Nguyễn Văn An")
        self.assertIn("không dấu", vc.name_vn("Nguyen Van An")[1])
        self.assertEqual(vc.khoa_ten("Đặng  Thị Hà"), "dang thi ha")
        self.assertTrue(vc.nghi_tcvn3("NguyÔn V¨n An"))
        self.assertFalse(vc.nghi_tcvn3("Nguyễn Văn An"))

    def test_company(self):
        self.assertEqual(vc.company_vn("cty tnhh ABC")[0], "Công ty TNHH ABC")
        self.assertEqual(vc.company_vn("CTCP Sữa Xanh")[0], "Công ty Cổ phần Sữa Xanh")

    @unittest.skipUnless(vc._lay_convert(), "chưa cài underthesea")
    def test_address(self):
        self.assertEqual(vc.address_new("P. Phúc Xá, Q. Ba Đình, TP. Hà Nội")[0], "Phường Hồng Hà, Thành phố Hà Nội")
        self.assertTrue(vc.address_new("phuong phuc xa quan ba dinh ha noi")[1])
        self.assertTrue(vc.dia_chi_cu("Phường Phúc Xá, Quận Ba Đình, Hà Nội"))


if __name__ == "__main__":
    unittest.main()
