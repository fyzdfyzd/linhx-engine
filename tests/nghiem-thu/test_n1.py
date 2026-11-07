"""N1: repo linhx-engine có code ENGINE 0.1; CI chạy tests/nghiem-thu; không bí mật trong repo."""
import re
import shutil
import subprocess

from _chung import GOC, REPO, BANG_CHUNG, file_bi_mat, quet_bi_mat, doc_json


def test_co_code_engine_0_1():
    for p in ["apps/linhx_worker/pyproject.toml", "apps/linhx_worker/linhx_worker/hooks.py",
              "front/index.html", "runner/linhx_runner.py", "deploy/docker-compose.yml"]:
        assert (GOC / p).exists(), f"thiếu {p}"


def _cac_workflow():
    ung_vien = list((GOC / ".github" / "workflows").glob("*.y*ml"))
    ung_vien += list((REPO / ".github" / "workflows").glob("linhx-engine*.y*ml"))
    return ung_vien


def test_ci_chay_nghiem_thu_tren_nhanh_tu_dong():
    wf = _cac_workflow()
    assert wf, "thiếu workflow CI: .github/workflows/linhx-engine*.yml (gốc repo) hoặc linhx-engine/.github/workflows/*.yml"
    hop = []
    for p in wf:
        chu = p.read_text(encoding="utf-8")
        co_nhanh = re.search(r"tu-dong/\*", chu) is not None
        co_kiem = ("cong_kiem" in chu) or ("tests/nghiem-thu" in chu)
        dung_thu_muc = (p.is_relative_to(GOC)) or ("linhx-engine" in chu)
        if co_nhanh and co_kiem and dung_thu_muc:
            hop.append(p)
    assert hop, "workflow phải chạy trên push nhánh tu-dong/* và chạy cong_kiem hoặc tests/nghiem-thu của linhx-engine"


def test_ci_xanh_co_bang_chung():
    p = BANG_CHUNG / "N1" / "ci.json"
    assert p.exists(), "thiếu bang-chung/N1/ci.json: {url, nhanh, ket_qua} của một lần chạy CI trên nhánh tu-dong/*"
    d = doc_json(p)
    assert re.match(r"^https://github\.com/[^/]+/[^/]+/actions/runs/\d+", d.get("url", "")), "url phải là link lượt chạy GitHub Actions"
    assert str(d.get("nhanh", "")).startswith("tu-dong/"), "lượt CI phải trên nhánh tu-dong/*"
    assert d.get("ket_qua") == "success", "lượt CI chưa xanh"


def test_khong_file_bi_mat():
    loi = file_bi_mat(GOC)
    assert not loi, "có file bí mật trong linhx-engine: " + ", ".join(loi)


def test_khong_chuoi_bi_mat():
    loi = quet_bi_mat(GOC)
    assert not loi, "có chuỗi giống bí mật: " + "; ".join(loi[:10])


def test_gitleaks_neu_co():
    # gitleaks có trên máy/CI thì phải sạch; không có thì bộ quét trên là đủ (không skip)
    exe = shutil.which("gitleaks")
    if not exe:
        return
    r = subprocess.run([exe, "detect", "--no-git", "--source", str(GOC), "--no-banner", "--redact"],
                       capture_output=True, text=True)
    assert r.returncode == 0, "gitleaks thấy bí mật:\n" + (r.stdout + r.stderr)[-1500:]
