#!/usr/bin/env python3
"""Chuyển một deck của linhx-deck (thư mục có 10-deck.json) sang dự án pipeline theo slide.

    python tu-linhx-deck.py <thư-mục-deck-cũ> <thư-mục-mới> [--anh <thư-mục-ảnh>]

Bước 1-9 của deck cũ chép vào chung/. Mỗi slide thành một mục:
  noi-dung.json  = slide bỏ phần ảnh            (chốt, nguồn = claude)
  anh-prompt.json = ý tưởng ảnh + ref          (chốt; slide không ảnh thì bỏ qua)
  bo-cuc.json    = kiểu slide                   (chốt)
  anh.png        = lấy từ --anh nếu có tệp trùng tên; không có thì để trống cho tầng tạo ảnh
Deck cũ không bị sửa.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PIPE = Path(__file__).resolve().parent / "pipe.py"
CHUNG = ["01-de-bai.md", "02-bang-chung.csv", "06-offer.json", "08-the-phong-cach.json"]


def pipe(*args):
    kq = subprocess.run([sys.executable, str(PIPE), *map(str, args)], capture_output=True, text=True, encoding="utf-8")
    if kq.returncode != 0:
        raise SystemExit(f"pipe.py {' '.join(map(str, args))} lỗi:\n{kq.stdout}{kq.stderr}")
    return kq.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cu"); ap.add_argument("moi"); ap.add_argument("--anh")
    a = ap.parse_args()
    cu, moi = Path(a.cu), Path(a.moi)
    deck = json.loads((cu / "10-deck.json").read_text(encoding="utf-8"))
    ids = [s["id"] for s in deck["slides"]]
    pipe("moi", moi, "--mau", "deck-slide", "--muc", ",".join(ids))

    thieu = []
    for ten in CHUNG:
        if (cu / ten).exists():
            shutil.copy2(cu / ten, moi / "chung" / ten)
        else:
            (moi / "chung" / ten).write_text("{}\n" if ten.endswith(".json") else "(chưa có ở deck cũ)\n", encoding="utf-8")
            thieu.append(ten)
    (moi / "chung" / "thuong-hieu.json").write_text(
        json.dumps({"brand": deck.get("brand", "linhx"), "chan_trang": deck.get("chan_trang", "")}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    for s in deck["slides"]:
        m = moi / "muc" / s["id"]
        noi_dung = {k: v for k, v in s.items() if k != "anh"}
        (m / "noi-dung.json").write_text(json.dumps(noi_dung, ensure_ascii=False, indent=1), encoding="utf-8")
        pipe("xong", moi, "--muc", s["id"], "--tang", "noi-dung", "--nguon", "claude", "--model", "chuyen-tu-linhx-deck")
        anh = s.get("anh")
        if anh:
            (m / "anh-prompt.json").write_text(json.dumps(
                {"prompt": anh.get("y_tuong", ""), "ref": anh.get("ref", ["anh-neo"]), "ti_le": anh.get("ti_le"),
                 "mo_ta": anh.get("mo_ta"), "tep_cu": anh.get("tep")}, ensure_ascii=False, indent=1), encoding="utf-8")
            pipe("xong", moi, "--muc", s["id"], "--tang", "anh-prompt")
            if a.anh and anh.get("tep") and (Path(a.anh) / anh["tep"]).exists():
                shutil.copy2(Path(a.anh) / anh["tep"], m / "anh.png")
                pipe("xong", moi, "--muc", s["id"], "--tang", "tao-anh", "--nguon", "gpt-image")
        else:
            pipe("bo-qua", moi, "--muc", s["id"], "--tang", "anh-prompt", "--ly-do", "slide không có ảnh")
        (m / "bo-cuc.json").write_text(json.dumps({"kieu": s["kieu"]}, ensure_ascii=False, indent=1), encoding="utf-8")
        pipe("xong", moi, "--muc", s["id"], "--tang", "bo-cuc")

    print(f"Đã chuyển {len(ids)} slide sang {moi}.")
    if thieu:
        print("Deck cũ không có các tệp chung sau, đã tạo tệp rỗng:", ", ".join(thieu))
    print(pipe("bang", moi))


if __name__ == "__main__":
    main()
