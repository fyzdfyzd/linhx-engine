import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import giai_ma as g

DUNG = {"id": "a", "nguon": {"ngay": "2026-10", "so_lieu": {"view": 100000, "share": 5000}},
        "gtvh": {"so": ["x", "y"], "so_loai": "sang-hen", "lm": "ha-cap", "ns": "mot-cau",
                 "la": {"thu_phap": "khong"}},
        "vi_sao_hai": {"truong_phai": ["uu-the"]}, "vi_sao_lan": {"khuon_dien": "[X], gét gô"}}


def test_kiem_bat_loi():
    sai = json.loads(json.dumps(DUNG))
    sai["gtvh"]["lm"] = "bua"; sai["nguon"]["ngay"] = None; sai["gtvh"]["so"] = ["x"]
    assert g.loi(DUNG) == []
    assert len(g.loi(sai)) == 3


def test_diem_lan():
    assert g.diem_lan(DUNG) == 5.5          # log10(1e5) + 10*0.05
    assert g.diem_lan({"nguon": {}}) is None


def test_gom_va_xuat():
    d = tempfile.mkdtemp(); m = os.path.join(d, "mau"); os.mkdir(m)
    for i, tp in enumerate(["khong", "noi-lai"]):
        x = json.loads(json.dumps(DUNG)); x["id"] = f"m{i}"
        x["gtvh"]["la"] = {"thu_phap": tp, "goc": "bí mật", "ket_qua": "bật mí"}
        json.dump(x, open(os.path.join(m, f"m{i}.json"), "w"), ensure_ascii=False)
    g.cmd_gom(m); g.cmd_xuat087(m)
    assert "| sang-hen | ha-cap | 2 | 5.50 |" in open(os.path.join(d, "KHUON.md")).read()
    assert list(json.load(open(os.path.join(d, "thu-phap-087.json")))) == ["noi-lai"]


if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f(); print("DAT", k)
