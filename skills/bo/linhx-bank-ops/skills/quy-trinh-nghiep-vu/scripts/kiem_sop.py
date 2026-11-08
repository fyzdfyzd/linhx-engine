"""Tự kiểm một file quy trình nghiệp vụ theo khung 10 mục. 0 token, Python thuần."""
import re, sys

MUC = ["Mục đích", "Phạm vi áp dụng", "Căn cứ", "Định nghĩa", "Vai trò và RACI",
       "Lưu đồ", "Các bước thực hiện", "Rủi ro và kiểm soát", "Biểu mẫu", "Chỉ số đo"]
TU_RUI_RO = ["giải ngân", "chuyển tiền", "phê duyệt", "hạch toán", "dữ liệu khách", "chi tiền"]


def bang(text, tieu_de):
    m = re.search(r"^## \d+\. " + re.escape(tieu_de) + r".*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return []
    dong = [l for l in m.group(1).splitlines() if l.strip().startswith("|")]
    return [[c.strip() for c in l.strip().strip("|").split("|")] for l in dong[2:]]


def kiem(text):
    loi, canh_bao = [], []
    for muc in MUC:
        if not re.search(r"^## \d+\. " + re.escape(muc), text, re.M):
            loi.append(f"Thiếu mục: {muc}")
    if "```mermaid" not in text:
        loi.append("Thiếu lưu đồ mermaid")
    buoc = bang(text, "Các bước thực hiện")
    if not buoc:
        loi.append("Bảng các bước trống")
    for b in buoc:
        if len(b) < 8:
            loi.append(f"Bước {b[0]}: thiếu cột"); continue
        so, ten, nguoi, _, _, _, sla, ks = b[:8]
        if not nguoi: loi.append(f"Bước {so}: thiếu người làm")
        if not re.search(r"\d", sla): loi.append(f"Bước {so}: SLA không có số")
        if any(t in ten.lower() for t in TU_RUI_RO) and not ks:
            loi.append(f"Bước {so} ({ten}): bước rủi ro mà không có kiểm soát")
    for r in bang(text, "Vai trò và RACI"):
        if r and r[0] and [c.upper() for c in r[1:]].count("A") != 1:
            loi.append(f"RACI bước {r[0]}: cần đúng một A")
    canh_bao += [f"Cần xác minh: {l.strip()}" for l in text.splitlines() if "[CẦN XÁC MINH]" in l]
    return loi, canh_bao, len(buoc), sum(1 for b in buoc if len(b) >= 8 and b[7])


if __name__ == "__main__":
    loi, cb, n, nks = kiem(open(sys.argv[1], encoding="utf-8").read())
    for l in loi: print("LỖI  ", l)
    for c in cb: print("XEM  ", c)
    print(f"{'ĐẠT' if not loi else 'CHƯA ĐẠT'}: {n} bước, {nks} điểm kiểm soát, {len(cb)} chỗ cần xác minh")
    sys.exit(1 if loi else 0)
