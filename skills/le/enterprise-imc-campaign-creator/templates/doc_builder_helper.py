import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# BTMH Brand Colors
COLOR_PRIMARY_HEX = "721C1B"      # Đỏ Bordeaux Trầm
COLOR_SECONDARY_HEX = "D4AF37"    # Vàng Kim Hoàng Gia
COLOR_DARK_GOLD_HEX = "9E7B15"    # Vàng đậm cho text
COLOR_BG_LIGHT_HEX = "FFFDF9"     # Trắng ngà hoàng triều
COLOR_BG_ALT_HEX = "FDF6ED"       # Nền kem nhạt
COLOR_TEXT_DARK_HEX = "222222"    # Đen than
COLOR_GRAY_LIGHT_HEX = "CCCCCC"

RGB_PRIMARY = RGBColor(0x72, 0x1C, 0x1B)
RGB_SECONDARY = RGBColor(0xD4, 0xAF, 0x37)
RGB_DARK_GOLD = RGBColor(0x9E, 0x7B, 0x15)
RGB_TEXT_DARK = RGBColor(0x22, 0x22, 0x22)
RGB_TEXT_MUTED = RGBColor(0x66, 0x66, 0x66)

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def create_base_document(title, subtitle, category="DEEP RESEARCH CHUYÊN SÂU"):
    doc = docx.Document()
    
    # Page setup A4
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        
        # Header & Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run(f"BẢO TÍN MẠNH HẢI (BTMH) | {category}")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGB_TEXT_MUTED
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Kế hoạch Truyền thông Kim Gia Bảo Gift (2026 - 2027) | Lưu hành Nội bộ")
        frun.font.name = "Arial"
        frun.font.size = Pt(8)
        frun.font.color.rgb = RGB_TEXT_MUTED
        
    # Title Section
    tag_p = doc.add_paragraph()
    tag_p.paragraph_format.space_before = Pt(4)
    tag_p.paragraph_format.space_after = Pt(2)
    tag_run = tag_p.add_run(f"★ BẢO TÍN MẠNH HẢI – {category.upper()} ★")
    tag_run.font.name = "Arial"
    tag_run.font.size = Pt(9.5)
    tag_run.font.bold = True
    tag_run.font.color.rgb = RGB_DARK_GOLD
    
    t_p = doc.add_paragraph()
    t_p.paragraph_format.space_before = Pt(0)
    t_p.paragraph_format.space_after = Pt(4)
    t_run = t_p.add_run(title)
    t_run.font.name = "Arial"
    t_run.font.size = Pt(20)
    t_run.font.bold = True
    t_run.font.color.rgb = RGB_PRIMARY
    
    st_p = doc.add_paragraph()
    st_p.paragraph_format.space_before = Pt(0)
    st_p.paragraph_format.space_after = Pt(14)
    st_run = st_p.add_run(subtitle)
    st_run.font.name = "Arial"
    st_run.font.size = Pt(11)
    st_run.font.italic = True
    st_run.font.color.rgb = RGB_TEXT_MUTED
    
    # Metadata Box
    add_callout(doc, 
        f"Dự án: Chiến dịch Truyền thông Tích hợp (IMC) Kim Gia Bảo Gift 2026-2027\n"
        f"Giai đoạn: Chuẩn bị Quý 4/2026, Đón Tết Bính Ngọ và Ngày Vía Thần Tài 2027\n"
        f"Đơn vị chủ trì: Phòng Truyền thông & Tiếp thị BTMH kết hợp Antigravity Strategic Team\n"
        f"Quy chế: Bảo mật cấp 2 - Lưu hành nội bộ Ban Lãnh đạo & Các phòng ban nghiệp vụ BTMH",
        title="THÔNG TIN HỒ SƠ CHIẾN LƯỢC", border_color="D4AF37", bg_color="FDF6ED"
    )
    
    return doc

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGB_PRIMARY
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGB_DARK_GOLD
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGB_TEXT_DARK
    return p

def add_paragraph(doc, text, bold_prefix=None, space_after=5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        brun = p.add_run(bold_prefix)
        brun.font.name = "Arial"
        brun.font.size = Pt(10)
        brun.font.bold = True
        brun.font.color.rgb = RGB_TEXT_DARK
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10)
    run.font.color.rgb = RGB_TEXT_DARK
    return p

def add_bullet(doc, text, bold_prefix=None, level=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if level > 0:
        p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    if bold_prefix:
        brun = p.add_run(bold_prefix)
        brun.font.name = "Arial"
        brun.font.size = Pt(10)
        brun.font.bold = True
        brun.font.color.rgb = RGB_TEXT_DARK
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10)
    run.font.color.rgb = RGB_TEXT_DARK
    return p

def add_callout(doc, text, title=None, border_color="721C1B", bg_color="FFF9F5"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.47)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
            <w:top w:val="none"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    if title:
        trun = p.add_run(title + "\n")
        trun.font.name = "Arial"
        trun.font.size = Pt(10)
        trun.font.bold = True
        trun.font.color.rgb = RGB_PRIMARY if border_color == "721C1B" else RGB_DARK_GOLD
    
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGB_TEXT_DARK
    
    # spacing after table
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.space_before = Pt(0)
    sp_p.paragraph_format.space_after = Pt(4)

def add_styled_table(doc, headers, data, col_widths=None):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="CCCCCC", sz="4", val="single")
    
    # Header row
    hdr_row = table.rows[0]
    trPr = hdr_row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    
    for i, header_text in enumerate(headers):
        cell = hdr_row.cells[i]
        set_cell_background(cell, COLOR_PRIMARY_HEX)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.1
        run = p.add_run(header_text)
        run.font.name = "Arial"
        run.font.size = Pt(9.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    # Data rows
    for r_idx, row_data in enumerate(data):
        row = table.rows[r_idx + 1]
        bg = COLOR_BG_ALT_HEX if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            cell = row.cells[c_idx]
            if bg != "FFFFFF":
                set_cell_background(cell, bg)
            set_cell_margins(cell, top=90, bottom=90, left=130, right=130)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.1
            run = p.add_run(str(cell_value))
            run.font.name = "Arial"
            run.font.size = Pt(9)
            run.font.color.rgb = RGB_TEXT_DARK
            
    # Set widths if specified
    if col_widths and len(col_widths) == len(headers):
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)
                
    # Spacing after table
    sp_p = doc.add_paragraph()
    sp_p.paragraph_format.space_before = Pt(0)
    sp_p.paragraph_format.space_after = Pt(6)
    return table
