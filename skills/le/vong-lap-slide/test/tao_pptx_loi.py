"""Tạo deck pptx 3 slide có lỗi cố ý để thử nhánh pptx: sạch, tràn hộp + chữ nhỏ, tương phản kém."""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def hop(s, x, y, w, h, chu, co, mau=(17, 17, 17)):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.auto_size = None
    r = tf.paragraphs[0].add_run(); r.text = chu; r.font.size = Pt(co); r.font.name = "Arial"
    r.font.color.rgb = RGBColor(*mau)
    return tb

prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
s = prs.slides.add_slide(prs.slide_layouts[6])
hop(s, 0.8, 0.8, 11, 1.2, "Doanh thu quý ba tăng nhờ kênh bán lẻ mới", 36)
hop(s, 0.8, 2.4, 11, 1, "Kênh bán lẻ đóng góp 40% tăng trưởng", 22)
s = prs.slides.add_slide(prs.slide_layouts[6])
hop(s, 0.8, 0.8, 11, 1.2, "Hộp chữ quá thấp làm chữ tràn xuống dưới", 36)
hop(s, 0.8, 2.4, 4, 0.6, "Một đoạn rất dài sẽ tràn ra ngoài hộp vì hộp bị cố định quá thấp so với lượng chữ cần hiển thị ở đây", 20)
hop(s, 0.8, 6.0, 6, 0.5, "Chú thích nguồn 8pt", 8)
s = prs.slides.add_slide(prs.slide_layouts[6])
hop(s, 0.8, 0.8, 11, 1.2, "Chữ xám nhạt trên nền trắng khó đọc", 36)
hop(s, 0.8, 2.4, 11, 1, "Dòng này màu xám rất nhạt", 24, (205, 205, 205))
prs.save(sys.argv[1])
