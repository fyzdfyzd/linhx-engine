"""Báo cáo ABC: HTML một file + Markdown + kế hoạch 30 ngày. Việc cụ thể lấy từ kết quả, không do AI viết."""

from __future__ import annotations

import html
from collections import Counter

ESC = html.escape
STEP_FIX = {
    1: "Tìm: agent chưa thấy bạn ở trí nhớ mô hình, tìm kiếm web hay dữ liệu sàn.",
    2: "Nhận diện: agent chưa chắc bạn là ai, dễ gán nhầm.",
    3: "Đối chiếu: thông tin về bạn mâu thuẫn giữa các nguồn hoặc giữa các AI.",
    4: "Lọc theo tiêu chí: agent không ghép được bạn với nhu cầu cụ thể của khách.",
    5: "Đề xuất: agent không khuyên bạn, hoặc khuyên vì lý do sai.",
}


def plan(facts: dict, s: dict, signals: dict) -> list[dict]:
    m = s["chi_so"]
    uniq = lambda xs: list(dict.fromkeys(x for x in xs if x))  # noqa: E731
    w1 = uniq(f"{w['mo_hinh']} nói: \"{w['claim']}\" ({w['nhan']})" + (f" → đính chính: {w['dinh_chinh']}" if w['dinh_chinh'] else "") for w in s["noi_sai"])[:8]
    w1 += [f for f in s["co_do"] if "chặn bot" in f or "Nhầm thực thể" in f]
    b1 = (signals.get("B1") or {}).get("checks", {})
    miss = [v["ghi_chu"] for v in b1.values() if v["diem"] == 0]
    w2 = ["Viết bảng sự thật một trang (là ai, làm gì, cho ai, sản phẩm, giá, chính sách, ai đứng sau), mỗi dòng có nguồn và ngày cập nhật; đặt ở một URL cố định."]
    w2 += [f"Website còn thiếu: {x}." for x in miss]
    lech = [k for k, v in (m["A5"].get("theo_dong") or {}).items() if v < 70]
    if lech:
        w2.append("Các AI đang nói khác nhau về: " + ", ".join(lech) + ". Ghi rõ giá trị đúng trên trang chính thức và các kênh.")
    unk = m["A4"].get("nhan", {}).get("chua_kiem", 0)
    if unk:
        w2.append(f"{unk} ý AI nói chưa kiểm được vì bảng sự thật chưa có dòng tương ứng: bổ sung các dòng này.")
    b2 = signals.get("B2_chi_tiet", {})
    w3 = [f"Kênh {r['kenh']} thiếu: {', '.join(r['thieu'])}." for r in b2.get("tu_dong", []) if r["thieu"]]
    w3 += [f"Kiểm tay kênh {r['kenh']} ({r['url']}): máy không đọc được." for r in b2.get("can_kiem_tay", [])]
    w3 = w3 or ["Đồng bộ tên, mô tả, giá, địa chỉ, hotline, người đứng sau trên website, Google Business, fanpage, gian hàng sàn, hồ sơ doanh nghiệp."]
    mix = m["A9"].get("co_cau_nguon", {})
    w4 = []
    if (m["B3"].get("score") or 0) < 60:
        w4.append("Có thêm nguồn độc lập nói về bạn có link (báo chí, hiệp hội, giải thưởng, case khách hàng): mục tiêu ít nhất 11 nguồn khác nhau.")
    if mix.get("doi_thu") or mix.get("bao_chi") or mix.get("review_dien_dan"):
        w4.append(f"Nguồn AI đang dẫn: {', '.join(f'{k} {v}' for k, v in mix.items())}. Ưu tiên có mặt trên đúng những loại nguồn này.")
    if (m["B4"].get("score") or 0) < 60:
        w4.append("Cho một người thật đứng tên các claim quan trọng: trang hồ sơ người sáng lập/chuyên gia, schema Person, liên kết LinkedIn.")
    if m["A7"].get("thieu"):
        w4.append("AI chưa gắn bạn với: " + ", ".join(m["A7"]["thieu"]) + ". Viết bằng chứng cụ thể cho từng thuộc tính.")
    if m["A2"].get("doi_thu_chua_khai"):
        w4.append("AI hay nhắc thêm: " + ", ".join(m["A2"]["doi_thu_chua_khai"][:5]) + ". Thêm vào danh sách đối thủ để theo dõi.")
    w4.append("Quét lại cùng bộ câu hỏi, cùng mô hình, cùng số lượt để so trước sau.")
    return [
        {"tuan": 1, "ten": "Sửa cái sai", "ve": "Verifiable Data", "viec": w1 or ["Lần quét này chưa thấy ý sai, nhầm, bịa hay cũ. Rà lại website và gian hàng."]},
        {"tuan": 2, "ten": "Bảng sự thật máy đọc được", "ve": "Verifiable Data", "viec": w2},
        {"tuan": 3, "ten": "Nhất quán đa kênh", "ve": "Verifiable Data", "viec": w3},
        {"tuan": 4, "ten": "Bên thứ ba, người đứng tên, đo lại", "ve": "Brand Reputation", "viec": w4},
    ]


def markdown(facts: dict, s: dict, p: list[dict], date: str) -> str:
    m = s["chi_so"]
    L = [f"# Báo cáo ABC: {facts.get('brand')} ({date})", "",
         f"**AVI {s['avi'] if s['avi'] is not None else '?'} / 100, hạng {s['hang']}** · Reputation {s['reputation']} · Verifiable Data {s['verifiable']}", ""]
    thieu = s["thieu_de_tinh"]["R"] + s["thieu_de_tinh"]["V"]
    if thieu:
        L += [f"_Điểm tạm: chưa đo {', '.join(thieu)}, trọng số chia lại cho các chỉ số đã đo._", ""]
    if s["roi_o_buoc"]:
        L += [f"**Đang rơi ở bước {s['roi_o_buoc']}.** {STEP_FIX[s['roi_o_buoc']]}", ""]
    for f in s["co_do"]:
        L.append(f"- ⚠ {f}")
    L += ["", "| # | Chỉ số | Điểm | Khoảng tin cậy | Bằng chứng |", "|---|---|---|---|---|"]
    for k, v in m.items():
        ci = f"{v['ci'][0]}–{v['ci'][1]}" if v.get("ci") else ""
        L.append(f"| {k} | {v['ten']} | {v['score'] if v['score'] is not None else 'chưa đo'} | {ci} | {v.get('bang_chung', '')} |")
    L += ["", "## AI đang nói sai điều gì", ""]
    for w in s["noi_sai"][:20]:
        L.append(f"- [{w['nhan']}] {w['mo_hinh']}: {w['claim']}" + (f" → {w['dinh_chinh']}" if w["dinh_chinh"] else ""))
    L += ["", "## Kế hoạch 30 ngày", ""]
    for t in p:
        L.append(f"### Tuần {t['tuan']}: {t['ten']} ({t['ve']})")
        L += [f"- {x}" for x in t["viec"]] + [""]
    pv = s["pham_vi"]
    L += ["## Phạm vi và giới hạn", "",
          f"Mô hình: {', '.join(pv['mo_hinh'])}; {pv['so_cau_tra_loi']} câu trả lời, tối đa {pv['so_luot_toi_da']} lượt mỗi câu, {pv['da_cham']} đã chấm.",
          "Nhãn do AI giám khảo gán theo bảng sự thật; mọi dòng sai/bịa/nhầm cần người kiểm trước khi dùng công khai. Câu trả lời qua API/CLI có thể khác ứng dụng chat khách dùng."]
    return "\n".join(L) + "\n"


def bar(v):
    if v is None:
        return '<span class="na">chưa đo</span>'
    c = "g" if v >= 65 else "a" if v >= 40 else "r"
    return f'<div class="bar"><i class="{c}" style="width:{v}%"></i></div><b>{v}</b>'


def html_report(facts: dict, s: dict, p: list[dict], date: str) -> str:
    m = s["chi_so"]
    rows = "".join(
        f"<tr><td>{k}</td><td>{ESC(v['ten'])}</td><td class='sc'>{bar(v['score'])}</td>"
        f"<td>{(str(v['ci'][0]) + '–' + str(v['ci'][1])) if v.get('ci') else ''}</td><td>{ESC(str(v.get('bang_chung', '')))}</td></tr>"
        for k, v in m.items())
    steps = "".join(f"<li class='{'weak' if k == s['roi_o_buoc'] else ''}'><b>{k}. {ESC(v['ten'])}</b>{bar(v['score'])}</li>"
                    for k, v in s["buoc_agent"].items())
    wrong = "".join(f"<tr><td>{ESC(w['nhan'])}</td><td>{ESC(w['mo_hinh'])}</td><td>{ESC(w['claim'] or '')}</td><td>{ESC(w['dinh_chinh'] or '')}</td></tr>"
                    for w in s["noi_sai"][:40]) or "<tr><td colspan=4>Chưa thấy ý sai, nhầm, bịa hay cũ.</td></tr>"
    flags = "".join(f"<li>{ESC(f)}</li>" for f in s["co_do"])
    weeks = "".join(f"<section class='wk'><h3>Tuần {t['tuan']} · {ESC(t['ten'])}</h3><small>{t['ve']}</small><ul>"
                    + "".join(f"<li>{ESC(x)}</li>" for x in t["viec"]) + "</ul></section>" for t in p)
    pv = s["pham_vi"]
    thieu = s["thieu_de_tinh"]["R"] + s["thieu_de_tinh"]["V"]
    miss = f"<p><small>Điểm tạm: chưa đo {', '.join(thieu)}, trọng số chia lại cho các chỉ số đã đo.</small></p>" if thieu else ""
    roi = f"<p class='roi'>Đang rơi ở bước {s['roi_o_buoc']}: {ESC(STEP_FIX[s['roi_o_buoc']])}</p>" if s["roi_o_buoc"] else ""
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Báo cáo ABC {ESC(facts.get('brand', ''))}</title><style>
:root{{--bg:#fff;--fg:#1d1d1f;--mu:#6e6e73;--li:#e5e5ea;--g:#2f9e6e;--a:#d99a1e;--r:#d4483b;--ac:#1f4fd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151517;--fg:#f2f2f4;--mu:#a1a1a6;--li:#333338}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,Segoe UI,Roboto,sans-serif}}
main{{max-width:1040px;margin:0 auto;padding:24px 16px}}h1{{margin:0 0 4px}}small,.na{{color:var(--mu)}}
.hero{{display:flex;gap:24px;flex-wrap:wrap;align-items:center;margin:16px 0}}.avi{{font-size:56px;font-weight:700}}
.kv b{{font-size:22px}}table{{width:100%;border-collapse:collapse;margin:8px 0 24px}}td,th{{border-bottom:1px solid var(--li);padding:6px 8px;text-align:left;vertical-align:top}}
.sc{{min-width:150px}}.bar{{display:inline-block;width:100px;height:8px;background:var(--li);border-radius:4px;margin-right:6px}}
.bar i{{display:block;height:100%;border-radius:4px}}.g{{background:var(--g)}}.a{{background:var(--a)}}.r{{background:var(--r)}}
ol.steps{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px}}
ol.steps li{{border:1px solid var(--li);border-radius:8px;padding:8px}}ol.steps li.weak{{border-color:var(--r)}}ol.steps b{{display:block}}
.roi{{font-weight:600;color:var(--r)}}.wk{{border-left:3px solid var(--ac);padding:4px 12px;margin:12px 0}}.wk h3{{margin:0}}
.flags li{{color:var(--r)}}.tbl{{overflow-x:auto}}</style></head><body><main>
<h1>{ESC(facts.get('brand', ''))}: AI và agent đang thấy bạn thế nào</h1><small>Chuẩn ABC v1.0 · {date} · {ESC(', '.join(pv['mo_hinh']))}</small>
<div class="hero"><div><div class="avi">{s['avi'] if s['avi'] is not None else '?'}</div><small>Agentic Visibility Index · hạng {s['hang']}</small></div>
<div class="kv">Reputation <b>{s['reputation']}</b> × Verifiable Data <b>{s['verifiable']}</b></div></div>
{miss}{roi}<ul class="flags">{flags}</ul>
<h2>Năm bước agent đọc thương hiệu</h2><ol class="steps">{steps}</ol>
<h2>16 chỉ số</h2><div class="tbl"><table><tr><th>#</th><th>Chỉ số</th><th>Điểm</th><th>Khoảng tin cậy 95%</th><th>Bằng chứng</th></tr>{rows}</table></div>
<h2>AI đang nói sai điều gì</h2><div class="tbl"><table><tr><th>Nhãn</th><th>Mô hình</th><th>AI nói</th><th>Sự thật</th></tr>{wrong}</table></div>
<h2>Kế hoạch 30 ngày</h2>{weeks}
<h2>Phạm vi và giới hạn</h2><p>{pv['so_cau_tra_loi']} câu trả lời, tối đa {pv['so_luot_toi_da']} lượt mỗi câu, {pv['da_cham']} đã chấm. Không đo thứ hạng. Nhãn do AI giám khảo gán theo bảng sự thật thương hiệu khai; mọi dòng sai/bịa/nhầm cần người kiểm trước khi dùng công khai. Nguyên văn câu trả lời nằm trong thư mục tra-loi/.</p>
</main></body></html>"""
