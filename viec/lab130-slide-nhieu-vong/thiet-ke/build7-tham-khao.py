# Deck CSMO T21 v6 — "hồ sơ kiểm chứng". Toạ độ px trên lưới 1920x1080, cỡ chữ pt.
import sys
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN as A, MSO_ANCHOR as V
from pptx.enum.shapes import MSO_SHAPE as S
from pptx.oxml.ns import qn

PX = 6350
def C(h): return RGBColor.from_string(h)
MUC, NGA, DO, VANG, XAM, XAM2, KEM = C("14130F"), C("F2EDE3"), C("C23B22"), C("B89A5E"), C("8C877D"), C("D9D2C5"), C("E6DFD2")
TD = "Playfair Display"; TH = "Be Vietnam Pro"; THL = "Be Vietnam Pro Light"; THM = "Be Vietnam Pro Medium"; THS = "Be Vietnam Pro SemiBold"
L = 128
prs = Presentation(); prs.slide_width = Emu(1920*PX); prs.slide_height = Emu(1080*PX)
BL = prs.slide_layouts[6]
E = lambda v: Emu(int(v*PX))

def txt(s, x, y, w, h, runs, size, font=TH, color=MUC, align=A.LEFT, anchor=V.TOP, ls=1.1, spc=0, italic=False):
    tb = s.shapes.add_textbox(E(x), E(y), E(w), E(h)); tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    for m in ("margin_left","margin_right","margin_top","margin_bottom"): setattr(tf, m, 0)
    lines = runs if isinstance(runs, list) else [runs]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align; p.line_spacing = ls
        segs = line if isinstance(line, tuple) else (line,)
        for seg in segs:
            t, kw = (seg, {}) if isinstance(seg, str) else seg
            r = p.add_run(); r.text = t; f = r.font
            f.size = Pt(kw.get("size", size)); f.name = kw.get("font", font); f.color.rgb = kw.get("color", color); f.italic = kw.get("italic", italic)
            sp = kw.get("spc", spc)
            if sp: r._r.get_or_add_rPr().set("spc", str(int(sp*100)))
    return tb

def rect(s, x, y, w, h, fill=None, line=None, lw=1.5, shape=S.RECTANGLE):
    r = s.shapes.add_shape(shape, E(x), E(y), E(w), E(h))
    if fill is None: r.fill.background()
    else: r.fill.solid(); r.fill.fore_color.rgb = fill
    if line is None: r.line.fill.background()
    else: r.line.color.rgb = line; r.line.width = E(lw)
    r.shadow.inherit = False
    st = r._element.find(qn("p:style"))
    if st is not None: r._element.remove(st)
    return r

def hline(s, x, y, w, color=VANG, lw=1.5): rect(s, x, y, w, lw, fill=color)

def nen(dark):
    s = prs.slides.add_slide(BL); s.background.fill.solid(); s.background.fill.fore_color.rgb = MUC if dark else NGA
    return s

def dau_trang(s, n, nhan, dark):
    c = XAM
    txt(s, L, 64, 1200, 30, nhan.upper(), 10, font=THM, color=c, spc=2.5)
    txt(s, 1920-L-300, 64, 300, 30, f"{n:02d}", 10, font=THM, color=c, spc=2, align=A.RIGHT)

def nguon(s, t, dark=False, y=1080-96):
    rect(s, L, y+5, 11, 11, fill=DO)
    txt(s, L+24, y, 1500, 30, (("NGUỒN   ", {"font": THS, "spc": 2}), (t, {})), 10, font=TH, color=XAM, spc=0.5)

def note(s, t): s.notes_slide.notes_text_frame.text = t

def luoi_cham(s, x, y, n_to, tong=100, cot=10, d=22, g=14, mau=DO, mau_nen=None, dark=False):
    mau_nen = mau_nen or (C("3A3833") if dark else XAM2)
    for i in range(tong):
        r, c = divmod(i, cot)
        rect(s, x + c*(d+g), y + r*(d+g), d, d, fill=mau if i < n_to else mau_nen, shape=S.OVAL)

N = [0]
def slide(dark, nhan):
    N[0] += 1; s = nen(dark); dau_trang(s, N[0], nhan, dark); return s

import os
from PIL import Image, ImageOps, ImageEnhance, ImageDraw
ANH = os.environ.get("ANH", "anh")
TMP = os.environ.get("TMP_ANH", "anh_xu_ly"); os.makedirs(TMP, exist_ok=True)

def xu_ly_anh(ma, ben="phai"):
    p = os.path.join(ANH, ma + ".jpg")
    if not os.path.exists(p): return None
    im = ImageOps.fit(Image.open(p).convert("RGB"), (1920, 1080), Image.LANCZOS)
    g = ImageOps.grayscale(im); g = ImageEnhance.Contrast(g).enhance(1.15)
    duo = ImageOps.colorize(g, black="#14130F", white="#EADFCB", mid="#7A6A55")
    im = Image.blend(duo, im, 0.35)
    m = Image.new("L", (1920, 1080)); d = ImageDraw.Draw(m)
    for x in range(1920):
        t = x/1919 if ben == "phai" else 1 - x/1919  # ben = phía ảnh hiện rõ
        a = int(235*(1-t)**1.6 + 60)
        d.line([(x, 0), (x, 1080)], fill=min(a, 245))
    dark = Image.new("RGB", (1920, 1080), "#14130F")
    out = Image.composite(dark, im, m)
    q = os.path.join(TMP, ma + ".jpg"); out.save(q, quality=86); return q

def nen_anh(s, ma, ben="phai"):
    q = xu_ly_anh(ma, ben)
    if q:
        pic = s.shapes.add_picture(q, 0, 0, E(1920), E(1080))
        s.shapes._spTree.remove(pic._element); s.shapes._spTree.insert(2, pic._element)
    return q is not None

CHANG = ["Khách", "Agent của khách", "Agent của thương hiệu", "Người của thương hiệu"]
def thanh_chang(s, k, dark=True, y=64):
    # 4 chấm nhỏ ở đầu trang, tô chặng k (0..3) hoặc hop k-k+1
    x0 = 1920 - L - 520
    for i in range(4):
        x = x0 + i*150
        on = i in k
        rect(s, x, y+4, 14, 14, fill=DO if on else (C("4A4740") if dark else XAM2), shape=S.OVAL)
        if i < 3: rect(s, x+20, y+10, 116, 1.5, fill=C("4A4740") if dark else XAM2)
    txt(s, x0-20, y+34, 520+40, 30, " → ".join(CHANG[i] for i in k).upper(), 10, font=THS, color=DO, align=A.RIGHT, spc=1.5)

def chuyen(nhan, ma, k, moc, tieu_de, than, src, nt, ben="phai"):
    N[0] += 1; s = prs.slides.add_slide(BL); s.background.fill.solid(); s.background.fill.fore_color.rgb = MUC
    nen_anh(s, ma, ben)
    txt(s, L, 64, 900, 30, nhan.upper(), 10, font=THM, color=XAM, spc=2.5)
    thanh_chang(s, k)
    txt(s, L, 210, 1000, 40, moc.upper(), 13, font=THS, color=VANG, spc=3)
    txt(s, L, 265, 1000, 380, tieu_de, 40, font=TD, color=NGA, ls=1.12)
    hline(s, L, 660, 120, DO, 3)
    txt(s, L, 695, 900, 260, than, 17, font=THL, color=KEM, ls=1.45)
    nguon(s, src, True); note(s, nt); return s

def xuong_song(nhan, tieu_de, sang, nt, cau_duoi=None, y=560, co=46):
    s = slide(True, nhan)
    txt(s, L, 170, 1664, 160, tieu_de, co, font=TD, color=NGA, ls=1.12)
    xs = [L + 170 + i*((1664-340)/3) for i in range(4)]
    ten = [("Người", "khách hàng"), ("Agent", "của khách"), ("Agent", "của thương hiệu"), ("Người", "đứng sau thương hiệu")]
    dong = ["giao quyền", "hỏi và đối chiếu", "trả lời, cam kết"]
    for i in range(3):
        rect(s, xs[i]+70, y-1, xs[i+1]-xs[i]-140, 2, fill=DO if i in sang else C("4A4740"))
        txt(s, xs[i]+70, y-60, xs[i+1]-xs[i]-140, 40, dong[i], 15, font=THL, color=KEM if i in sang else XAM, align=A.CENTER, italic=True)
    for i, (a, b) in enumerate(ten):
        nguoi = i in (0, 3)
        rect(s, xs[i]-60, y-60, 120, 120, fill=NGA if nguoi else MUC, line=VANG if nguoi else DO, lw=2.5, shape=S.OVAL if nguoi else S.ROUNDED_RECTANGLE)
        txt(s, xs[i]-60, y-60, 120, 120, "◯" if False else ("N" if nguoi else "A"), 34, font=TD, color=MUC if nguoi else DO, align=A.CENTER, anchor=V.MIDDLE)
        txt(s, xs[i]-170, y+85, 340, 50, a, 26, font=TD, color=NGA, align=A.CENTER)
        txt(s, xs[i]-170, y+145, 340, 40, b, 15, font=THL, color=XAM, align=A.CENTER)
    if cau_duoi: txt(s, L, 870, 1664, 80, cau_duoi, 22, font=TD, italic=True, color=VANG)
    note(s, nt); return s
# 01 Bìa
s = slide(True, "VSMCamp & CSMO Summit 2026 · Topic 07 · Trust in the Age of Agents")
txt(s, L, 250, 1664, 360, [("Từ Brand Claim",), (("đến ", {"italic": True, "color": VANG}), ("Verifiable Truth", {}))], 76, font=TD, color=NGA, ls=1.0)
hline(s, L, 630, 120, DO, 3)
txt(s, L, 670, 1200, 120, "Khi khách nhờ AI chọn hộ, thương hiệu được tin bằng gì?", 26, font=THL, color=KEM, ls=1.3)
txt(s, L, 1080-140, 900, 40, (("Đinh Trần Tuấn Linh", {"font": THS, "color": NGA}), ("   ·   19.11.2026   ·   Hồ Tây 2", {})), 13, color=XAM, spc=0.5)
note(s, "Chưa chào. Bước ra, chuyển ngay sang slide 2.")

# 02 60 giây
s = slide(True, "Trước khi bắt đầu")
rect(s, L, 250, 460, 460, line=C("3A3833"), lw=10, shape=S.OVAL)
arc = rect(s, L, 250, 460, 460, line=DO, lw=10, shape=S.ARC)
arc.adjustments[0] = -90; arc.adjustments[1] = 180
txt(s, L, 330, 460, 230, "60", 130, font=TD, color=NGA, align=A.CENTER, anchor=V.MIDDLE)
txt(s, L, 560, 460, 40, "GIÂY", 12, font=THS, color=XAM, align=A.CENTER, spc=4)
rect(s, 720, 270, 1072, 440, fill=C("1F1E1A"), line=C("3A3833"), lw=1.5, shape=S.ROUNDED_RECTANGLE).adjustments[0] = 0.06
txt(s, 776, 310, 900, 30, "HỎI ChatGPT HOẶC GEMINI", 11, font=THS, color=XAM, spc=3)
txt(s, 776, 370, 960, 320, [(("Tôi đang cần ", {}), ("[sản phẩm của bạn]", {"color": DO, "italic": True}), (" ở Việt Nam. Giới thiệu giúp tôi 3 thương hiệu đáng chọn nhất và lý do.", {}))], 28, font=TD, color=NGA, ls=1.3)
txt(s, 720, 750, 1072, 40, "Ai thấy tên thương hiệu mình, giơ tay.", 18, font=THL, color=KEM)
note(s, "Mời anh chị lấy điện thoại ra. Mở ChatGPT hoặc Gemini. Gõ đúng câu trên màn hình, thay chỗ trống bằng ngành của mình. Tôi bấm giờ 60 giây.\nHết giờ: Ai thấy tên thương hiệu mình trong 3 cái tên, giơ tay. Giữ tay. Ai thấy nó nói về mình đúng hoàn toàn? Những người vừa hạ tay: tối qua khách hàng của anh chị cũng hỏi đúng câu đó. Và anh chị không có trong câu trả lời.\nDự phòng nếu ít người làm sau 20 giây: kể chuyện hãng dược Singapore bán kem bôi khớp.")

def chuong(so, ten, phu, nt):
    s = slide(True, f"Phần {so}")
    txt(s, L, 160, 600, 300, f"{so:02d}", 180, font=TD, color=VANG, italic=True, ls=0.9)
    hline(s, L, 480, 1664, C("3A3833"), 1.5)
    txt(s, L, 530, 1500, 260, ten, 54, font=TD, color=NGA, ls=1.1)
    if phu: txt(s, L, 820, 1300, 80, phu, 20, font=THL, color=KEM, ls=1.3)
    note(s, nt)

def so_lon(nhan, con_so, nghia, kem, src, nt, cham=None, dark=False, cham_tong=100, cot=10):
    s = slide(dark, nhan)
    fg = NGA if dark else MUC
    txt(s, L, 200, 1000, 330, con_so, 160, font=TD, color=DO, ls=0.9)
    hline(s, L, 560, 120, VANG, 2)
    txt(s, L, 600, 940, 220, nghia, 26, font=TD, color=fg, ls=1.2)
    if kem: txt(s, L, 830, 940, 80, kem, 17, font=THL, color=XAM, ls=1.35)
    if cham is not None:
        d, g = (30, 18) if cham_tong <= 100 else (22, 14)
        gx = 1920 - L - (cot*(d+g) - g); rows = (cham_tong + cot - 1)//cot
        gy = 540 - (rows*(d+g)-g)//2
        luoi_cham(s, gx, gy, cham, cham_tong, cot, d, g, dark=dark)
    nguon(s, src, dark); note(s, nt); return s

def cau(nhan, cau_chinh, phu, nt, dark=True, size=56):
    s = slide(dark, nhan)
    fg = NGA if dark else MUC
    txt(s, L, 120, 70, 120, "“", 120, font=TD, color=DO)
    txt(s, L, 300, 1500, 480, cau_chinh, size, font=TD, color=fg, ls=1.15, anchor=V.MIDDLE)
    if phu: txt(s, L, 840, 1400, 60, phu, 18, font=THL, color=XAM)
    note(s, nt); return s
# Chương 1 + xương sống
chuong(1, "Một lần mua hàng giờ đi qua bốn chặng.", "Hai chặng giữa là máy nói chuyện với máy.", "Chiếc ghế trống: hôm nay phòng này thiếu một vị khách quan trọng nhất. Nó không xem TVC, không theo dõi KOL. Nó đọc, đối chiếu, rồi chọn hộ khách.")
xuong_song("Người → Agent → Agent → Người", "Niềm tin phải đi qua bốn chặng. Gãy một chặng là mất khách.", [0,1,2], "Trước đây: thương hiệu nói, khách nghe. Giờ: khách giao việc cho agent của mình. Agent đó hỏi, đối chiếu với agent và dữ liệu của thương hiệu. Rồi một người thật phía thương hiệu phải đứng ra chịu trách nhiệm cho những gì agent đã nói. Hôm nay tôi kể năm câu chuyện, mỗi câu ở một chặng.", "Thương hiệu không còn nói thẳng với khách. Nó nói qua hai cái máy.")
so_lon("Chặng 1 · Người giao quyền", "87%", "người Việt mua sắm online đã dùng ít nhất một công cụ AI.", "Trung bình mỗi người dùng hai cái.", "Decision Lab, The Connected Consumer Q3/2025", "87% người Việt mua sắm online đã dùng ít nhất một công cụ AI, trung bình mỗi người dùng hai cái.", cham=87)
so_lon("Chặng 1 · Người giao quyền", "57%", "sẵn sàng để AI đổi thương hiệu giúp họ, nếu nó tìm được lựa chọn hời hơn.", "Nhưng chỉ 15% người Mỹ muốn để agent tự bấm mua. Cửa sổ đang mở.", "Checkout.com, Agentic Commerce 2026 · 06/2026; Forbes, J. McKee · 10/2026", "Lòng trung thành, thứ mình mua bằng mười năm quảng cáo, đang được giao cho một cái máy. Tin tốt: người ta chưa tin hẳn. Ai chuẩn bị bây giờ sẽ có mặt khi cửa sổ đóng lại.", cham=57)
chuyen("Câu chuyện 1", "a04", [0,1], "29.09.2025 · Mỹ", "Nút “Mua” xuất hiện ngay trong khung chat.", "Khách mua hàng của người bán trên Etsy mà không cần mở website. OpenAI nói kết quả không có tài trợ, xếp theo mức phù hợp với người hỏi. Nghĩa là chỗ đứng trong câu trả lời không mua được bằng tiền.", "TechCrunch, 29/9/2025 · OpenAI Instant Checkout, Agentic Commerce Protocol cùng Stripe", "Ngày 29/9/2025, OpenAI mở Instant Checkout: người dùng Mỹ bấm Mua ngay trong ChatGPT, hàng của người bán Etsy, hơn một triệu cửa hàng Shopify sắp vào. Câu đáng nhớ: kết quả 'không tài trợ, xếp theo mức phù hợp'. Website của anh chị có thể không bao giờ được mở.")
chuyen("Câu chuyện 2", "a05", [1,2], "01.2026", "Agent của khách nói chuyện thẳng với máy của cửa hàng.", "Google công bố giao thức thương mại cho agent, Walmart nằm trong nhóm đầu tiên. Không còn ai đọc trang sản phẩm đẹp của anh chị. Hai cái máy đọc dữ liệu của nhau.", "Google Developers Blog, CNBC, Axios · 11/01/2026 (Universal Commerce Protocol)", "Tháng 1/2026 Google ra Universal Commerce Protocol, Walmart tham gia cùng Gemini. Agent của khách gọi thẳng vào dữ liệu của cửa hàng. Kiểm lại tên giao thức trước khi nói.")
chuyen("Câu chuyện 3", "a07", [1,2], "15.03.2026 · Trung Quốc", "Chiếc đồng hồ không có thật, được AI giới thiệu sau vài giờ.", "Phóng viên CCTV dựng một mẫu đồng hồ không tồn tại, trả 39,9 tệ cho dịch vụ “tối ưu cho AI”. Vài giờ sau, trợ lý AI đã giới thiệu nó. Agent đọc nhanh hơn người, và bị lừa cũng nhanh hơn.", "CCTV 3.15 (3/2026), qua tổng hợp của Ballerine (11/2026) · cần kiểm bản gốc", "Câu chuyện CCTV 3.15: mẫu đồng hồ Apollo-9 không có thật. Bài học: nếu thương hiệu thật không cấp dữ liệu kiểm chứng được, kẻ làm giả sẽ cấp thay. Kiểm bản gốc trước khi nói.")
# 07 Công thức
s = slide(True, "Công thức")
txt(s, L, 200, 1664, 60, "AGENTIC VISIBILITY  =", 16, font=THS, color=XAM, spc=4)
txt(s, L, 320, 720, 200, "Reputation", 64, font=TD, color=NGA)
txt(s, 860, 250, 200, 260, "×", 170, font=TD, color=DO, align=A.CENTER)
txt(s, 1080, 300, 712, 260, [("Verifiable",), ("Data",)], 64, font=TD, color=NGA, ls=0.95)
hline(s, L, 640, 640, C("3A3833")); hline(s, 1080, 640, 712, C("3A3833"))
txt(s, L, 670, 640, 80, "Con người yêu mến", 22, font=THL, color=KEM)
txt(s, 1080, 670, 712, 80, "Máy xác thực được", 22, font=THL, color=KEM)
txt(s, L, 860, 1500, 60, (("Phép nhân, không phải phép cộng. ", {"color": NGA}), ("Thiếu một bên, kết quả về 0.", {"color": DO})), 24, font=TD, italic=True)
note(s, "Phép nhân, không phải phép cộng. Được yêu mà không kiểm được thì nhân với 0. Dữ liệu đầy đủ mà không ai yêu cũng nhân với 0.")

chuong(2, "AI đang thấy anh chị thế nào?", "Ba kiểu sai, và cách đo.", "Không đo được thì không quản trị được.")
# 09 8,2%
so_lon("Kiểu sai 1 · Bị nhận nhầm", "8,2%", "câu trả lời AI gán nhãn hiệu của một thương hiệu cho đối thủ.", "Trong khi 1.231 trang của đại lý đều ghi đúng.", "AIMCLEAR · 06/2026 · audit một thương hiệu tiêu dùng trên 5 hệ AI", "Kiểu sai thứ nhất: bị nhận nhầm. Nếu chưa kể ở đầu bài: chuyện công ty Việt phục vụ các ngân hàng lớn bị AI tả thành hãng dược Singapore bán kem bôi khớp.", cham=8)
chuyen("Câu chuyện 4 · Việt Nam", "a11", [1], "2026 · Hà Nội", "Phục vụ các ngân hàng lớn. AI tả họ là hãng dược bán kem bôi khớp.", "Mười năm làm thương hiệu tử tế. Với cái máy, họ là người khác. Khi được hỏi chung về ngành, không AI nào nhắc tên họ.", "Kết quả đo của diễn giả, đã ẩn danh", "Câu chuyện thật, ẩn danh. Nếu đã dùng ở phần mở đầu thì chỉ nhắc lại một câu.")
# 11 19%
so_lon("Kiểu sai 3 · Không kiểm được", "19%", "claim về chứng nhận, giải thưởng được AI xác nhận.", "Thứ mình hay khoe nhất là thứ máy ít tin nhất.", "Empirank AIV-009 · 08/2026 · 26 claim chứng nhận", "Kiểu thứ ba: không kiểm được. Chính thứ mình hay khoe nhất lại là thứ máy ít tin nhất.", cham=19)

# 12 Bốn chỉ số 2x2
s = slide(False, "Đo")
txt(s, L, 170, 1664, 120, (("Đừng đo thứ hạng. ", {}), ("Đo bốn điều.", {"color": DO, "italic": True})), 52, font=TD)
o = [("Có mặt", "Hỏi chung về ngành, AI có tự nhắc tới mình không?"), ("Đúng", "Hỏi thẳng về mình, đúng bao nhiêu ý?"), ("Được đề xuất", "AI có khuyên chọn mình, vì lý do đúng không?"), ("Nhất quán", "Các AI có nói giống nhau về mình không?")]
for i, (a, b) in enumerate(o):
    x = L + (i % 2)*852; y = 360 + (i//2)*270
    hline(s, x, y, 780, MUC, 1.5)
    txt(s, x, y+28, 90, 60, f"0{i+1}", 14, font=THS, color=DO, spc=2)
    txt(s, x+110, y+18, 670, 70, a, 34, font=TD)
    txt(s, x+110, y+90, 640, 100, b, 18, font=THL, color=C("3A3833"), ls=1.35)
nguon(s, "Hỏi 2 lần, AI cho cùng danh sách dưới 1/100 lần · SparkToro × Gumshoe · 01/2026")
note(s, "Hỏi hai lần, AI ra hai danh sách khác nhau. Đo thứ hạng trên AI giống đo chiều cao của sóng. Hỏi nhiều AI, nhiều lần, đo bốn điều này.")

# 13 Chương 3
chuong(3, "Agent không cảm thương hiệu. Nó đọc và đối chiếu.", "Năm bước, mỗi bước là một chỗ có thể rơi.", "Có 5 bước, mỗi bước là một chỗ anh chị có thể rơi.")

# 14 Sơ đồ 5 bước
s = slide(False, "Agent đọc thương hiệu qua 5 bước")
txt(s, L, 170, 1664, 100, "Năm bước, năm chỗ rơi.", 52, font=TD)
bs = [("Tìm", "Không có ở nguồn nó đọc thì vô hình.", "Có mặt"), ("Nhận diện", "Tên ngắn, trùng tên thì bị gán nhầm.", "Đúng"), ("Đối chiếu", "Web, sàn, báo nói khác nhau thì bớt tin.", "Đúng · Nhất quán"), ("Lọc theo khách", "Không nói rõ dành cho ai thì không được ghép.", "Được đề xuất"), ("Đề xuất", "Lý do có nguồn thì khách tin.", "Được đề xuất")]
cx0, step, cy = L + 170, (1664-340)/4, 440
hline(s, cx0, cy, 1664-340, MUC, 2)
for i, (a, b, c) in enumerate(bs):
    cx = cx0 + i*step
    rect(s, cx-22, cy-22, 44, 44, fill=NGA, line=MUC, lw=2, shape=S.OVAL)
    txt(s, cx-22, cy-22, 44, 44, str(i+1), 14, font=THS, align=A.CENTER, anchor=V.MIDDLE)
    w = 320; x = cx - w/2
    al = A.CENTER
    txt(s, x, cy+60, w, 60, a, 22, font=TD, align=al)
    txt(s, x, cy+120, w, 120, b, 16, font=THL, color=C("3A3833"), align=al, ls=1.35)
    rect(s, cx-1, cy+300, 2, 60, fill=DO)
    txt(s, x, cy+380, w, 40, c.upper(), 10, font=THS, color=DO, align=al, spc=2)
txt(s, L, 940, 1664, 40, "Chỉ số yếu cho biết anh chị đang rơi ở bước nào.", 16, font=THL, color=XAM)
note(s, "Bốn chỉ số vừa rồi cho anh chị biết mình rơi ở bước nào. Không có mặt: bước 1. Sai, nhầm: bước 2 và 3. Không được đề xuất: bước 4 và 5.")

chuyen("Câu chuyện 5", "a03", [2,3], "2022 → 02.2024 · Canada", "Chatbot hứa hoàn tiền vé tang. Hãng nói chatbot tự chịu. Toà nói không.", "Một hành khách mất bà, hỏi chatbot của Air Canada và được bảo có thể xin giá vé tang sau khi bay. Chính sách thật không cho phép. Toà buộc hãng bồi thường. Agent nói thay anh chị, anh chị chịu thay agent.", "Global News, 15/2/2024 · Civil Resolution Tribunal, British Columbia", "Jake Moffatt, 2022, hỏi chatbot Air Canada về giá vé tang. Chatbot nói có thể xin hoàn sau. Air Canada lập luận không chịu trách nhiệm về thông tin của chatbot. Toà ở British Columbia bác, buộc bồi thường hơn 650 đô la Canada. Số tiền nhỏ, bài học lớn: chặng Agent → Người, thương hiệu chịu trách nhiệm.")
# 15 Chương 4
chuong(4, "Claim là điều mình tự nói. Bằng chứng là điều máy kiểm được.", None, "Mỗi claim cần một bằng chứng.")

# 16 Claim -> bằng chứng
s = slide(False, "Viết lại claim · ví dụ minh hoạ")
txt(s, L, 170, 1664, 100, "Mỗi claim một bằng chứng.", 52, font=TD)
txt(s, L, 330, 600, 30, "CLAIM", 11, font=THS, color=XAM, spc=3)
txt(s, 820, 330, 900, 30, "BẰNG CHỨNG MÁY ĐỌC ĐƯỢC", 11, font=THS, color=DO, spc=3)
rows = [("Thương hiệu số 1 Việt Nam", "Phục vụ 1.240 doanh nghiệp tính đến 11/2026. Danh sách công khai tại [link]."), ("Chất lượng hàng đầu", "Đạt ISO 22000, số chứng nhận …, tra tại trang tổ chức cấp."), ("Được khách hàng tin yêu", "4,7/5 trên 3.100 đánh giá. 96% khiếu nại xử lý trong 48 giờ.")]
for j, (a, b) in enumerate(rows):
    y = 380 + j*175; hline(s, L, y, 1664, MUC if j == 0 else XAM2, 1.5)
    t = txt(s, L, y+36, 600, 100, a, 26, font=TD, color=XAM)
    for r in t.text_frame.paragraphs[0].runs: r._r.get_or_add_rPr().set("strike", "sngStrike")
    rect(s, 820, y+44, 22, 22, fill=DO)
    txt(s, 820, y+44, 22, 22, "✓", 11, font=THS, color=NGA, align=A.CENTER, anchor=V.MIDDLE)
    txt(s, 870, y+34, 920, 120, b, 22, font=TH, ls=1.35)
nguon(s, "Ví dụ minh hoạ, số liệu giả định")
note(s, "Slide này để anh chị chụp lại. Dừng 5 giây.")

# 17 Năm lớp
s = slide(False, "Năm lớp bằng chứng")
txt(s, L, 170, 1664, 100, "Năm lớp bằng chứng máy đọc được.", 52, font=TD)
lop = [("Sự thật có cấu trúc", "Một trang: là ai, làm gì, cho ai, giá, chính sách, ngày cập nhật. Viết bằng chữ."), ("Nhất quán mọi kênh", "Cùng tên, giá, địa chỉ trên web, Google, fanpage, sàn."), ("Bên thứ ba xác nhận", "Giải thưởng có link, chứng nhận có số hiệu, case có tên."), ("Người thật đứng tên", "Nhà sáng lập, chuyên gia ký dưới claim quan trọng."), ("Phản hồi đã xử lý", "Review, khiếu nại, đổi trả. Bán đúng người.")]
for i, (a, b) in enumerate(lop):
    y = 320 + i*120; fill = MUC if i < 2 else KEM
    rect(s, L, y, 1340, 104, fill=fill)
    fg = NGA if i < 2 else MUC
    txt(s, L+32, y+26, 80, 50, f"0{i+1}", 12, font=THS, color=DO if i >= 2 else VANG, spc=2)
    txt(s, L+110, y+22, 480, 60, a, 24, font=TD, color=fg, anchor=V.MIDDLE)
    txt(s, L+580, y+12, 740, 80, b, 14, font=THL, color=fg if i < 2 else C("3A3833"), anchor=V.MIDDLE, ls=1.3)
rect(s, 1500, 320, 3, 224, fill=VANG); rect(s, 1500, 560, 3, 344, fill=DO)
txt(s, 1530, 390, 270, 80, [("Verifiable",), ("Data",)], 24, font=TD, italic=True, ls=1.0)
txt(s, 1530, 690, 270, 80, [("Reputation",), ("máy đọc được",)], 24, font=TD, italic=True, ls=1.0)
note(s, "Hai lớp đầu là Verifiable Data. Ba lớp sau là Reputation mà máy đọc được. Thiếu bên nào, phép nhân về 0.")

chuyen("Câu chuyện 6", "a06", [3], "2026 · American Express", "Hãng thẻ cam kết bồi hoàn khi agent đã đăng ký mua nhầm.", "Agent được cấp danh tính, chủ thẻ được xác thực trước khi agent được mua. Niềm tin giữa hai cái máy cuối cùng vẫn cần một người đứng tên chịu trách nhiệm.", "The Financial Brand, 1/5/2026 (bình luận của Riskified)", "Đầu 2026 Amex ra bộ công cụ cho thương mại agent, cam kết xử lý các giao dịch nhầm của agent đã đăng ký. Đó là chặng cuối: một người, một tổ chức đứng tên.")
# 18 Bán sai người
cau("Bán đúng người", "Mỗi đơn bán sai người để lại một bằng chứng xấu mà agent đọc được.", "Agent đọc review, khiếu nại, đổi trả.", "Phục vụ đúng người là một truth signal.")

# 19 QR
s = slide(True, "Phần 05 · Làm ngay")
txt(s, L, 220, 960, 300, [("Soi thương hiệu",), (("trong 10 phút.", {"italic": True, "color": VANG}),)], 58, font=TD, color=NGA, ls=1.05)
hline(s, L, 500, 120, DO, 3)
for k, t in enumerate(["Tự đo 4 chỉ số.", "Biết mình rơi ở bước nào.", "Nhận kế hoạch 30 ngày."]):
    txt(s, L, 545 + k*60, 800, 50, (("0%d   " % (k+1), {"font": THS, "color": DO, "size": 13}), (t, {})), 22, font=THL, color=KEM)
txt(s, L, 1080-150, 800, 40, "Miễn phí. Không cần đăng nhập. Không bán gì trên sân khấu.", 14, font=THL, color=XAM)
rect(s, 1160, 210, 632, 632, fill=NGA)
txt(s, 1160, 210, 632, 632, "QR", 40, font=TD, color=XAM, align=A.CENTER, anchor=V.MIDDLE)
txt(s, 1160, 870, 632, 40, "[đường dẫn]", 14, font=THM, color=XAM, align=A.CENTER, spc=1)
note(s, "Để slide 45 giây. Tôi không bán gì trên sân khấu. Quét mã này, 10 phút tối nay anh chị tự đo thương hiệu mình theo 4 chỉ số, biết mình rơi ở bước nào, và nhận kế hoạch 30 ngày.")

# 20 Ba việc
s = slide(False, "Trước thứ Hai")
txt(s, L, 170, 1664, 100, (("Ba việc ", {}), ("trước thứ Hai.", {"italic": True, "color": DO})), 52, font=TD)
vi = [("Hỏi", "2 AI, mỗi AI 3 lần, 3 câu trong phiếu. Chụp lại câu trả lời."), ("Viết", "Bảng sự thật một trang. Đặt lên web bằng chữ."), ("Sửa", "Chỗ lệch giữa web và Google Business Profile.")]
for i, (a, b) in enumerate(vi):
    y = 360 + i*180; hline(s, L, y, 1664, XAM2 if i else MUC, 1.5)
    rect(s, L, y+44, 40, 40, line=MUC, lw=2)
    txt(s, L+80, y+30, 300, 70, a, 40, font=TD)
    txt(s, 560, y+44, 1100, 90, b, 22, font=THL, color=C("3A3833"), ls=1.35)
note(s, "Ba việc này làm trong một buổi chiều.")

# 21 30 ngày
s = slide(False, "30 ngày")
txt(s, L, 170, 1664, 100, "Ba mươi ngày.", 52, font=TD)
tu = [("Tuần 1", "Sửa chỗ AI đang nói sai."), ("Tuần 2", "Viết Bảng sự thật."), ("Tuần 3", "Đồng bộ thông tin mọi kênh."), ("Tuần 4", "Thêm bằng chứng bên thứ ba. Đo lại.")]
w4 = (1664 - 3*24)/4
for i, (a, b) in enumerate(tu):
    x = L + i*(w4+24)
    rect(s, x, 440, w4, 10, fill=DO if i == 3 else MUC)
    txt(s, x, 480, w4, 60, a.upper(), 12, font=THS, color=DO if i == 3 else XAM, spc=3)
    txt(s, x, 530, w4-30, 200, b, 28, font=TD, ls=1.2)
txt(s, L, 860, 1664, 60, (("Ngày 30: ", {"font": THS, "color": DO}), ("hỏi lại AI đúng câu lúc nãy.", {})), 20, font=THL)
note(s, "Ba mươi ngày nữa, hỏi lại AI đúng câu lúc nãy.")

xuong_song("Kết", "Mười năm tới, thương hiệu thắng là thương hiệu đi qua cả bốn chặng mà không bị bóp méo.", [0,1,2], "Ba mươi ngày nữa, anh chị hỏi lại AI đúng câu lúc nãy. Tôi mong lần đó anh chị là người giơ tay. Cảm ơn.", "Dễ kiểm chứng nhất, không phải kể hay nhất.", y=600, co=40)
s = prs.slides[-1]; txt(s, L, 1080-140, 1300, 40, (("Đinh Trần Tuấn Linh", {"font": THS, "color": NGA}), ("   ·   Mời ở lại panel 16:15, Hồ Tây 2", {})), 13, color=XAM, spc=0.5)
prs.save(sys.argv[1]); print(N[0])
