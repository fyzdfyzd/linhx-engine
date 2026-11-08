"""M3 loc: bỏ NoAI, tải ảnh TẠM để lọc trùng bằng dHash, ghi hàng chờ phân loại.

  python loc.py            # xử lý bản ghi mới trong nguon/records.jsonl -> nguon/cho-phan-loai.jsonl
  python loc.py --don-tam  # xoá toàn bộ KHO/_tam (chạy sau khi phân loại xong)

dHash 64 bit chỉ cần Pillow (cùng ý với imagededup hashing.py, gọn hơn để khỏi cài torch).
Ảnh trùng (Hamming <= 6) với ảnh đã có: ghi trung_voi = id bài có nhiều tương tác hơn / đăng sớm hơn.
"""
import argparse, json, os, shutil, urllib.request
from pathlib import Path
from PIL import Image

KHO = Path(os.environ.get("KHO_MINH_HOA", r"D:\LINHX\KHO-MINH-HOA"))
REC, HANG, TAM = KHO / "nguon" / "records.jsonl", KHO / "nguon" / "cho-phan-loai.jsonl", KHO / "_tam"
HASHES = KHO / "nguon" / "dhash.json"  # chỉ lưu mã băm, không lưu ảnh
UA = "LINHX-LAB-kho-minh-hoa/0.1 (personal reference)"


def dhash(path, n=8):
    im = Image.open(path).convert("L").resize((n + 1, n), Image.LANCZOS)
    px = list(im.getdata())
    bits = 0
    for r in range(n):
        for c in range(n):
            bits = (bits << 1) | (px[r * (n + 1) + c] > px[r * (n + 1) + c + 1])
    return bits


def doc_jsonl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--don-tam", action="store_true"); a = ap.parse_args()
    if a.don_tam:
        shutil.rmtree(TAM, ignore_errors=True); print("Đã xoá ảnh tạm."); return
    TAM.mkdir(parents=True, exist_ok=True)
    da_xu_ly = {r["id"] for r in doc_jsonl(HANG)}
    hashes = json.loads(HASHES.read_text(encoding="utf-8")) if HASHES.exists() else {}
    moi, n_noai, n_trung, n_loi = [], 0, 0, 0
    for r in doc_jsonl(REC):
        if r["id"] in da_xu_ly:
            continue
        if r.get("co_noai"):
            n_noai += 1; continue
        r["anh_tam"] = ""
        if r.get("anh_tam_url"):
            dst = TAM / (r["id"].replace(":", "_").replace("/", "_")[:80] + ".jpg")
            try:
                req = urllib.request.Request(r["anh_tam_url"], headers={"User-Agent": UA})
                dst.write_bytes(urllib.request.urlopen(req, timeout=30).read())
                h = dhash(dst)
                gan = [k for k, v in hashes.items() if bin(h ^ int(v, 16)).count("1") <= 6]
                if gan:
                    r["trung_voi"] = gan[0]; n_trung += 1
                else:
                    hashes[r["id"]] = f"{h:016x}"
                r["anh_tam"] = str(dst)
            except Exception as e:  # link hết hạn: Claude sẽ mở link_goc trong Chrome
                r["loi_anh"] = str(e)[:120]; n_loi += 1
        r.pop("anh_tam_url", None)
        moi.append(r)
    with HANG.open("a", encoding="utf-8") as f:
        for r in moi:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    HASHES.write_text(json.dumps(hashes), encoding="utf-8")
    print(f"Chờ phân loại: {len(moi)} (trùng {n_trung}, lỗi tải ảnh {n_loi}); bỏ NoAI: {n_noai}. Ảnh tạm ở {TAM}, nhớ chạy --don-tam sau khi phân loại.")


if __name__ == "__main__":
    main()
