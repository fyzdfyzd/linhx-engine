"""Ghi bảng radar ra .xlsx có định dạng (cần openpyxl). congdong.py export gọi write_xlsx."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

WIDTH = {"Tên": 28, "Ngành": 22, "Mô tả": 50, "Kênh": 45, "Sự kiện": 40, "Họ nói về gì": 50,
         "Pain point cộng đồng": 55, "Họ đã có gì": 45, "Nguồn": 40, "Cộng đồng (vai trò, năm)": 45,
         "Gợi ý offer/dịch vụ": 45, "Ghi chú CRM": 30, "Ghi chú": 35, "Chủ đề": 45, "Tiêu đề": 70, "URL": 50,
         "Chức danh": 30, "Tổ chức": 25, "LinkedIn": 30, "Facebook": 30, "Website": 28,
         "LINHX chia sẻ / offer": 60, "Dịch vụ agentic có thể bán": 55, "Lời hứa": 45,
         "Chia sẻ miễn phí cho cộng đồng": 50, "Dịch vụ agentic (trả phí)": 50, "Đầu ra": 40,
         "Năng lực đã có (lab)": 35, "Hợp với": 30, "Pain point": 55, "Offer": 30, "Nhà tài trợ, đối tác": 40, "Diễn giả": 40,
         "Người/DN đoạt giải gần đây": 40, "Lý do": 40, "Tổ chức": 25, "Lĩnh vực": 22, "Đối tượng": 22}


def write_xlsx(tables: dict, path: Path, cfg: Path) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "Hướng dẫn"
    guide = [
        ["Radar LINHX: cộng đồng, sự kiện, giải thưởng (LAB035)", ""],
        ["Cập nhật", dt.date.today().isoformat()],
        ["", ""],
        ["Sheet", "Dùng để"],
        ["Cộng đồng", "Hiệp hội, cộng đồng, sự kiện: kênh, họ nói gì, pain point, họ đã có gì"],
        ["Doanh nghiệp", "Nhà tài trợ, đối tác: điểm cơ hội, gợi ý offer, giai đoạn tiếp cận (CRM)"],
        ["KOL", "Diễn giả, cố vấn, sáng lập: chủ đề, kênh, điểm, giai đoạn kết nối"],
        ["Pain → Offer", "Mỗi pain point của cộng đồng → LINHX chia sẻ gì, bán dịch vụ agentic gì"],
        ["Offer & dịch vụ", "Danh mục offer của LINHX (sửa ở config/offers.json)"],
        ["Sự kiện", "Sự kiện business, tech, AI sắp tới: nhãn Đi / Cân nhắc / Xem bản ghi / Bỏ, tài trợ, diễn giả"],
        ["Giải thưởng", "Giải cho DN và cá nhân: nên nộp, ai nộp, hạn, ai vừa thắng"],
        ["Tín hiệu", "Tin, video, thay đổi trang mới nhất từ lượt quét định kỳ"],
        ["", ""],
        ["Cập nhật giai đoạn", "Sửa trực tiếp ở đây sẽ bị ghi đè ở lượt quét sau. Dùng: python congdong.py mark dn \"Tên\" \"đã kết nối\" \"ghi chú\""],
        ["Điểm cơ hội", "Vai trò (tối đa 30) + số cộng đồng (24) + còn hoạt động năm nay (12) + được nhắc 90 ngày (10) + ngành ưu tiên (8) + khớp offer (6) − chưa xác minh (5)"],
    ]
    for r in guide:
        ws.append(r)
    ws["A1"].font = Font(bold=True, size=14)
    for cell in ws[4]:
        cell.font = Font(bold=True)
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 120

    head = PatternFill("solid", fgColor="1F3A5F")
    stages = ["chưa tiếp cận", "đang tìm hiểu", "đã kết nối", "đã chia sẻ", "đã gửi offer",
              "đang trao đổi", "đã chốt", "không hợp"]
    for name, rows in tables.items():
        ws = wb.create_sheet(name[:31])
        for r in rows:
            ws.append([("" if v is None else v) for v in r])
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = head
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        for i, h in enumerate(rows[0], 1):
            col = ws.cell(row=1, column=i).column_letter
            ws.column_dimensions[col].width = WIDTH.get(h, 14)
            if h in ("URL", "Website", "LinkedIn", "Facebook"):
                for row in ws.iter_rows(min_row=2, min_col=i, max_col=i):
                    v = row[0].value
                    if isinstance(v, str) and v.startswith("http"):
                        row[0].hyperlink = v
                        row[0].font = Font(color="1F5FBF", underline="single")
            if h == "Giai đoạn" and ws.max_row > 1:
                dv = DataValidation(type="list", formula1='"' + ",".join(stages) + '"', allow_blank=True)
                ws.add_data_validation(dv)
                dv.add(f"{col}2:{col}{ws.max_row}")
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = ws.dimensions
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path
