"""V1: cổng kiểm chạy trên VM linhx-engine-1 thay máy cty, mỗi lượt có trần RAM, phân biệt lỗi máy.

Hợp đồng (HOP-DONG.md, Đợt 2c):
- deploy/cong_kiem_vm.py, thuần Python chuẩn (không import frappe), chạy trên VM:
    nhanh_hop_le(ten: str) -> bool
        chỉ nhận "main" hoặc "tu-dong/engine-t<số>"; mọi tên khác (có ; $ ` khoảng trắng .. ) -> False
    lenh_chay(nhanh: str, file_features: str, them: str = "", ram: str = "3G") -> list[str]
        nhánh hoặc file features sai (file phải khớp features-dot[0-9a-z]+.json) -> ValueError;
        trả list đối số (không phải chuỗi shell) bắt đầu bằng "systemd-run", có "--scope" và "-p", "MemoryMax=<ram>",
        và có "canh/cong_kiem.py", "kiem", file_features; them (vd "B4,C2") đưa qua biến môi trường CONG_KIEM_THEM, không nối vào lệnh.
    phan_loai(ma: int, ra: str) -> dict {"ma": int, "loi_may": bool, "ra": str (tối đa 3000 ký tự cuối)}
        loi_may True khi ma 137 hoặc -9, hoặc ra có "Out of memory"/"oom-kill"/"TimeoutExpired"/"No space left"; còn lại False
- CLI trên VM: python3 deploy/cong_kiem_vm.py --nhanh <n> --features <f> [--them ID,ID] [--ram 3G]
    kéo nhánh vào thư mục riêng của nhánh, lấy canh/ từ origin/main, khoá flock (một lượt một lúc), in một dòng JSON phan_loai.
    Không dùng shell=True.
- Bằng chứng chạy thật trên VM: bang-chung/V1/vm.json
    {"luc": str, "may": "linhx-engine-1", "nhanh": str, "features": str, "ma": int, "loi_may": bool,
     "giay": số > 0, "ram": str}
"""
from _chung import GOC, bang_chung_json, nap_module

TEP = GOC / "deploy" / "cong_kiem_vm.py"


def _m():
    assert TEP.exists(), "thiếu deploy/cong_kiem_vm.py"
    return nap_module("cong_kiem_vm", GOC / "deploy")


def test_nhanh_hop_le():
    """Tiêu chí: chỉ nhận nhánh main hoặc tu-dong/engine-tN, chặn tên chèn lệnh"""
    m = _m()
    assert m.nhanh_hop_le("main") and m.nhanh_hop_le("tu-dong/engine-t3")
    for x in ["tu-dong/engine-t1;rm -rf /", "x$(id)", "tu-dong/engine-t1 ", "../main", "tu-dong/engine-tx", "", "feature/a"]:
        assert not m.nhanh_hop_le(x), x


def test_lenh_chay_co_tran_ram():
    """Tiêu chí: lệnh là list đối số qua systemd-run có MemoryMax, không nối chuỗi shell"""
    m = _m()
    l = m.lenh_chay("tu-dong/engine-t2", "features-dot2.json", "B4,C2", "2G")
    assert isinstance(l, list) and l[0] == "systemd-run" and "--scope" in l and "MemoryMax=2G" in l
    assert any("canh/cong_kiem.py" in x for x in l) and "kiem" in l and any(x.endswith("features-dot2.json") for x in l)
    assert not any("B4,C2" in x for x in l)
    for sai in [("x;y", "features-dot2.json"), ("main", "../../etc/passwd"), ("main", "features-dot2.json;id")]:
        try:
            m.lenh_chay(*sai)
        except ValueError:
            continue
        raise AssertionError(f"phải từ chối {sai}")
    chu = TEP.read_text(encoding="utf-8")
    assert "shell=True" not in chu and "import frappe" not in chu and "flock" in chu


def test_phan_loai_loi_may():
    """Tiêu chí: tách lỗi máy (hết RAM, quá giờ, hết đĩa) khỏi lỗi code"""
    m = _m()
    assert m.phan_loai(137, "")["loi_may"] is True
    assert m.phan_loai(1, "kernel: Out of memory: Killed process")["loi_may"] is True
    assert m.phan_loai(1, "subprocess.TimeoutExpired")["loi_may"] is True
    d = m.phan_loai(1, "FAILED tests/nghiem-thu/test_b4.py::test_x\n" + "a" * 5000)
    assert d["loi_may"] is False and d["ma"] == 1 and len(d["ra"]) <= 3000
    assert m.phan_loai(0, "ok")["loi_may"] is False


def test_bang_chung_vm():
    """Tiêu chí: chạy thật một lượt trên VM linhx-engine-1"""
    d = bang_chung_json("V1", "vm.json")
    assert d["may"] == "linhx-engine-1" and isinstance(d["ma"], int) and isinstance(d["loi_may"], bool)
    assert float(d["giay"]) > 0 and str(d["ram"]).endswith("G")
