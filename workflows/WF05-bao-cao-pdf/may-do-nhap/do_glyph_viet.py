# Đo phủ ký tự tiếng Việt của tệp font (chỉ đọc). Dùng: python -I -X utf8 do_glyph_viet.py <font>...
import sys, unicodedata
import pymupdf

goc = "aăâeêioôơuưyAĂÂEÊIOÔƠUƯY"
dau = ["", "̀", "́", "̉", "̃", "̣"]
viet = {unicodedata.normalize("NFC", c + d) for c in goc for d in dau} | set("đĐ")
viet = sorted(x for x in viet if len(x) == 1)
for p in sys.argv[1:]:
    f = pymupdf.Font(fontfile=p)
    thieu = [c for c in viet if not f.has_glyph(ord(c))]
    print(f"{p.split(chr(92))[-1]}: {len(viet) - len(thieu)}/{len(viet)} ký tự Việt" + (f", thiếu {''.join(thieu[:20])}" if thieu else ""))
