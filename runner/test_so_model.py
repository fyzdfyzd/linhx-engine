from pathlib import Path

from runner import so_model


def _ghi(goc: Path, ma: str, nd: str) -> None:
    (goc / ma).mkdir(parents=True)
    (goc / ma / "KET-QUA.md").write_text(nd, encoding="utf-8")


def test_tong_hop_theo_model(tmp_path):
    _ghi(tmp_path, "a-code-1", "model: m1\ntrang_thai: xong\nphut: 4.0\ntoken: vao=100 ra=10\n")
    _ghi(tmp_path, "a-code-2", "model: m1\ntrang_thai: loi\nphut: 6.0\ntoken: vao=300 ra=30\n")
    _ghi(tmp_path, "b-kiem-1", "model: m2\ntrang_thai: xong\nphut: 1.0\ntoken: vao=0 ra=0\n")
    _ghi(tmp_path, "c-hong", "khong co model\n")
    kq = so_model.tong_hop(tmp_path)
    assert kq["m1"] == {"phieu": 2, "xong": 1, "phut_tv": 5.0, "vao_tv": 200, "ra_tv": 20}
    assert kq["m2"]["xong"] == 1 and kq["m2"]["vao_tv"] == 0
    assert set(so_model.tong_hop(tmp_path, "a-")) == {"m1"}
