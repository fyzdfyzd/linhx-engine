"""Vẽ hình (exhibit) theo style nhà từ 04-hinh.json, xuất SVG chữ thật.

Dùng: python hinh.py <thu-muc-bao-cao> [--style <style.json>]
Mỗi hình trong 04-hinh.json:
  {"id": "H01", "loai": "thanh-ngang|cot|cot-nhom|duong|bang",
   "tieu_de": "Câu kết luận có dấu chấm.", "doi_tuong": "% người trả lời", "don_vi": "%",
   "nhan": ["A", "B"], "chuoi": [{"ten": "2026", "gia_tri": [1, 2], "bc": "BC03"}],
   "nhan_manh": "A", "nguon": "...", "ghi_chu": "...", "rong": "full|col"}
Luật vẽ (D16): nhãn số trực tiếp, không khung, lưới mảnh, một màu nhấn, chữ trong SVG giữ là chữ.
"""
import json
import sys
from pathlib import Path

import matplotlib
import matplotlib.lines  # noqa: F401
import matplotlib.patches  # noqa: F401
import matplotlib.ticker  # noqa: F401

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

GOC = Path(__file__).resolve().parent.parent


def nap_font():
    for f in (GOC / "fonts").glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))


def so_vn(v, don_vi=""):
    if isinstance(v, float) and not v.is_integer():
        # giữ tới 2 chữ số thập phân có nghĩa (0,79 không thành 0,8; 4,37 không thành 4,4)
        import math
        so_le = max(3, 2 - math.floor(math.log10(abs(v)))) if abs(v) < 1 else (2 if abs(v) < 10 else 1)  # giữ 3 chữ số có nghĩa (0,00146 không thành 0,001)
        s = f"{v:,.{so_le}f}".rstrip("0").rstrip(".")
    else:
        s = f"{int(round(v)):,}"
    s = s.replace(",", "§").replace(".", ",").replace("§", ".")
    return s + ("%" if don_vi == "%" else "")


def ve(h, th, ra):
    mau = th["mau"]
    pal = mau["bieu_do"]
    font = th["font"]["phu"]
    plt.rcParams.update({
        "font.family": font, "font.size": 8.5, "svg.fonttype": "none",
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.edgecolor": mau["ke"], "axes.labelcolor": mau["chu"],
        "xtick.color": mau["chu_phu"], "ytick.color": mau["chu"],
        "axes.grid": False, "grid.color": mau["ke"], "grid.linewidth": 0.4,
    })
    loai = h["loai"]
    nhan = h.get("nhan", [])
    chuoi = h.get("chuoi", [])
    dv = h.get("don_vi", "")
    rong = 6.9 if h.get("rong", "full") == "full" else 3.3
    cao = h.get("cao") or (0.32 * len(nhan) + 0.5 if loai == "thanh-ngang" else 2.7)
    fig, ax = plt.subplots(figsize=(rong, cao))
    nm = h.get("nhan_manh")
    if loai == "thanh-ngang":
        gt = chuoi[0]["gia_tri"]
        thu_tu = sorted(range(len(nhan)), key=lambda i: gt[i])
        yy = range(len(thu_tu))
        nen = pal[3] if nm else pal[0]  # có hạng mục nhấn thì các thanh khác lùi về sắc nhạt
        mau_cot = [mau["nhan"] if nhan[i] == nm else nen for i in thu_tu]
        ax.barh(list(yy), [gt[i] for i in thu_tu], height=0.6, color=mau_cot)
        if len(chuoi) > 1:
            g2 = chuoi[1]["gia_tri"]
            ax.scatter([g2[i] for i in thu_tu], list(yy), marker="|", s=140, color=pal[-1], linewidths=2, zorder=3,
                       label=chuoi[1]["ten"])
        import textwrap
        rong_nhan = 60 if h.get("rong", "full") == "full" else 20  # hình hẹp: xuống dòng nhãn dài để trục không bị ép
        ax.set_yticks(list(yy), [textwrap.fill(nhan[i], rong_nhan) for i in thu_tu])
        ax.tick_params(axis="y", length=0)
        ax.set_xticks([])
        ax.spines["bottom"].set_visible(False)
        mx = max(max(c["gia_tri"]) for c in chuoi)
        for k, i in enumerate(thu_tu):
            m = max(c["gia_tri"][i] for c in chuoi)
            ax.text(m + mx * 0.015, k, so_vn(gt[i], dv), va="center", fontsize=8, fontweight="bold", color=mau["chu"])
        ax.set_xlim(0, mx * (1.22 if h.get("rong", "full") == "full" else 1.5))  # 1,12 cắt nhãn dài như "0,00431" (vòng thử 9/11)  # hình hẹp cần chỗ cho nhãn số
        if len(chuoi) > 1:
            ax.legend(frameon=False, fontsize=7.5, loc="lower right",
                      handles=[matplotlib.patches.Patch(color=pal[0], label=chuoi[0]["ten"]),
                               matplotlib.lines.Line2D([], [], marker="|", ls="", color=pal[-1], mew=2, ms=9,
                                                       label=chuoi[1]["ten"])])
    elif loai in ("cot", "cot-nhom"):
        n = len(chuoi)
        w = (0.75 if len(nhan) > 4 else 0.52) / n  # ít hạng mục thì cột thanh mảnh hơn
        mx = max(max(c["gia_tri"]) for c in chuoi)
        for j, c in enumerate(chuoi):
            xs = [i + (j - (n - 1) / 2) * w for i in range(len(nhan))]
            col = [mau["nhan"] if (n == 1 and nhan[i] == nm) else (pal[3] if (n == 1 and nm) else pal[j % len(pal)])
                   for i in range(len(nhan))]
            ax.bar(xs, c["gia_tri"], width=w * 0.92, color=col, label=c["ten"])
            for x, v in zip(xs, c["gia_tri"]):
                ax.text(x, v + mx * 0.02, so_vn(v, dv), ha="center", fontsize=7.5, fontweight="bold", color=mau["chu"])
        ax.set_xticks(range(len(nhan)), nhan)
        ax.tick_params(axis="x", length=0)
        ax.set_yticks([])
        ax.set_ylim(0, mx * 1.15)
        if n > 1:
            ax.legend(frameon=False, fontsize=7.5, ncol=n, loc="upper left", bbox_to_anchor=(0, 1.1))
    elif loai == "duong":
        for j, c in enumerate(chuoi):
            col = mau["nhan"] if c["ten"] == nm else pal[j % len(pal)]
            ax.plot(range(len(nhan)), c["gia_tri"], color=col, lw=2 if c["ten"] == nm else 1.4)
            ax.text(len(nhan) - 1 + 0.08, c["gia_tri"][-1], f'{c["ten"]} {so_vn(c["gia_tri"][-1], dv)}',
                    va="center", fontsize=7.5, color=col, fontweight="bold")
        ax.set_xticks(range(len(nhan)), nhan)
        ax.grid(axis="y")
        ax.tick_params(length=0)
        ax.set_xlim(-0.2, len(nhan) - 1 + 0.9)
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: so_vn(v, dv)))
    else:
        raise SystemExit(f"loại hình chưa hỗ trợ: {loai}")
    fig.tight_layout(pad=0.3)
    fig.savefig(ra)
    plt.close(fig)


def main():
    d = Path(sys.argv[1])
    style = None
    if "--style" in sys.argv:
        style = Path(sys.argv[sys.argv.index("--style") + 1])
    else:
        tt = json.loads((d / "trang-thai.json").read_text(encoding="utf-8"))
        style = Path(tt["style"])
    th = json.loads(style.read_text(encoding="utf-8"))
    nap_font()
    spec = json.loads((d / "04-hinh.json").read_text(encoding="utf-8"))
    out = d / "04-hinh"
    out.mkdir(exist_ok=True)
    for h in spec["hinh"]:
        if h["loai"] == "bang":
            continue
        ve(h, th, out / f'{h["id"]}.svg')
        print("đã vẽ", h["id"])


if __name__ == "__main__":
    main()
