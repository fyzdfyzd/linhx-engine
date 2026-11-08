"""Một vòng chấm quảng cáo: CSV kết quả -> DE-XUAT.md + actions.json. Không gọi API."""
import argparse, csv, json, os, random

def beta(a, b, rng):
    return rng.betavariate(max(a, 1e-3), max(b, 1e-3))

def cham(rows, muc_tieu="conv", n=4000, seed=7):
    rng = random.Random(seed)
    tong_click = sum(r["clicks"] for r in rows) or 1
    tong_conv = sum(r[muc_tieu] for r in rows)
    tong_imp = sum(r["impressions"] for r in rows) or 1
    tong_spend = sum(r["spend"] for r in rows)
    p0 = (tong_conv + 1) / (tong_imp + 2)          # tỉ lệ conv/hiển thị toàn tài khoản
    cpa_tb = tong_spend / tong_conv if tong_conv else None
    k = 200                                         # độ mạnh tiên nghiệm
    out = []
    for r in rows:
        a, b = r[muc_tieu] + p0 * k, r["impressions"] - r[muc_tieu] + (1 - p0) * k
        hon = sum(beta(a, b, rng) > p0 for _ in range(n)) / n
        cpa = r["spend"] / r[muc_tieu] if r[muc_tieu] else None
        roas = r["revenue"] / r["spend"] if r["spend"] else 0
        if r["impressions"] < 1000:
            loai = "CHƯA ĐỦ"
        elif hon >= 0.9:
            loai = "TĂNG"
        elif hon <= 0.1 and cpa_tb and r["spend"] >= 2 * cpa_tb:
            loai = "TẮT"
        else:
            loai = "GIỮ"
        out.append({**r, "ctr": r["clicks"] / max(r["impressions"], 1), "cpa": cpa,
                    "roas": roas, "p_hon": round(hon, 3), "loai": loai})
    return out, cpa_tb

def doi_ngan_sach(kq, ngan_sach_ngay):
    tat = [r for r in kq if r["loai"] == "TẮT"]
    tang = [r for r in kq if r["loai"] == "TĂNG"]
    con = [r for r in kq if r["loai"] != "TẮT"]
    phan = {r["ad_id"]: ngan_sach_ngay / max(len(kq), 1) for r in kq}  # giả định chia đều hiện tại
    giai_phong = sum(phan[r["ad_id"]] for r in tat)
    actions = [{"lenh": "pause_ad", "ad_id": r["ad_id"], "ly_do": f"P tốt hơn TB = {r['p_hon']}"} for r in tat]
    for r in tang:
        moi = phan[r["ad_id"]] * 1.2               # trần +20%/lần
        actions.append({"lenh": "update_budget", "ad_id": r["ad_id"],
                        "tu": round(phan[r["ad_id"]]), "den": round(moi)})
        giai_phong -= moi - phan[r["ad_id"]]
    if giai_phong > 0:
        actions.append({"lenh": "giu_lai", "so_tien": round(giai_phong),
                        "ghi_chu": "dành cho biến thể mới, tạo ở trạng thái PAUSED"})
    for r in tang:
        actions.append({"lenh": "create_variants", "tu_ad": r["ad_id"], "so": 3,
                        "doi_mot_yeu_to": ["hook", "anh_bia", "cta"], "trang_thai": "PAUSED"})
    return actions

def doc(path, muc_tieu):
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append({"ad_id": r["ad_id"], "ten": r.get("ten", ""),
                         **{c: float(r[c] or 0) for c in ("spend", "impressions", "clicks", muc_tieu, "revenue")}})
    return rows

def ghi(kq, actions, cpa_tb, ra):
    os.makedirs(ra, exist_ok=True)
    d = ["# Đề xuất vòng ads", "", f"CPA trung bình tài khoản: {cpa_tb:,.0f}đ" if cpa_tb else "Chưa có chuyển đổi", "",
         "| Ad | Tên | Tiêu | CTR | CPA | ROAS | P tốt hơn TB | Quyết |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted(kq, key=lambda x: -x["p_hon"]):
        d.append(f"| {r['ad_id']} | {r['ten']} | {r['spend']:,.0f} | {r['ctr']:.2%} | "
                 f"{(f'{r['cpa']:,.0f}' if r['cpa'] else '-')} | {r['roas']:.2f} | {r['p_hon']} | {r['loai']} |")
    d += ["", "## Lệnh chờ duyệt", "", "```json", json.dumps(actions, ensure_ascii=False, indent=1), "```",
          "", "Chưa lệnh nào được gửi. Duyệt xong mới gọi MCP."]
    open(os.path.join(ra, "DE-XUAT.md"), "w", encoding="utf-8").write("\n".join(d))
    json.dump(actions, open(os.path.join(ra, "actions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("csv"); p.add_argument("--muc-tieu", default="conv")
    p.add_argument("--ngan-sach-ngay", type=float, default=1_000_000); p.add_argument("--ra", default="out")
    a = p.parse_args()
    kq, cpa_tb = cham(doc(a.csv, a.muc_tieu), a.muc_tieu)
    ghi(kq, doi_ngan_sach(kq, a.ngan_sach_ngay), cpa_tb, a.ra)
    print("\n".join(f"{r['ad_id']}\t{r['loai']}\t{r['p_hon']}" for r in kq))
