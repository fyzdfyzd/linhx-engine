#!/usr/bin/env python3
"""kiem_van_dich.py - soát "văn dịch" và "văn máy" trong bài tiếng Việt.

Hai tầng:
  1. Danh sách gốc (viết tay, bền): cụm dịch từ tiếng Anh và khuôn cấu trúc của LLM.
  2. Danh sách học (danh-sach-hoc.json, sinh lại bằng lap_danh_sach.py): cụm LLM dùng nhiều hơn văn Linh.

  python kiem_van_dich.py <bai.md> [--hoc danh-sach-hoc.json] [--json]
Điểm = 100 - 6 x (số lỗi gốc trên 1000 chữ) - 2 x (số cụm học bị dùng quá tay trên 1000 chữ), tối thiểu 0.
Không thay người đọc: chỉ bắt dấu vết, không chấm hay dở.
"""
import argparse, json, re, sys
from pathlib import Path

# (mẫu regex, nhóm, gợi ý)
GOC = [
    (r'đóng vai trò (quan trọng|then chốt|chủ chốt)', 'dịch', 'nói thẳng nó làm gì'),
    (r'trong bối cảnh', 'dịch', 'bỏ, hoặc "giữa lúc", "khi"'),
    (r'\bhành trình\b', 'dịch', 'chỉ dùng cho chuyến đi thật'),
    (r'điều đáng chú ý (là|ở đây)', 'dịch', 'bỏ, nói luôn điều đó'),
    (r'không chỉ\b[^.]{0,60}\bmà còn', 'khuôn', 'tách hai câu hoặc chọn một ý'),
    (r'không phải\b[^.]{0,60}\bmà là', 'khuôn', 'chỉ lật khi người đọc thật sự tin vế đầu'),
    (r'\bmột cách (?!nhanh|chậm)\w+', 'dịch', 'bỏ "một cách", dùng thẳng tính từ hoặc từ láy'),
    (r'\b(nói cách khác|tóm lại|nhìn chung|có thể nói)\b', 'máy', 'bỏ'),
    (r'tuy nhiên,? bên cạnh', 'máy', 'bỏ'),
    (r'\b(bức tranh toàn cảnh|khía cạnh|đa chiều|then chốt|cốt lõi)\b', 'máy', 'thay bằng chi tiết cụ thể'),
    (r'(giải pháp|chiến lược) (toàn diện|bền vững|tối ưu)', 'máy', 'nói giải pháp gì'),
    (r'\b(thúc đẩy|tối ưu hoá|tối ưu hóa|nâng tầm|kiến tạo|định hình)\b', 'máy', 'động từ khẩu hiệu, thay bằng việc cụ thể'),
    (r'\b(trao quyền|lan toả|lan tỏa)\b', 'máy', 'từ thời thượng, chỉ dùng khi nhại'),
    (r'\bđược\s+(\w+\s+){0,2}bởi\b', 'dịch', 'bị động kiểu Anh, đổi sang chủ động'),
    (r'\bliệu\b[^.?]*\?', 'máy', 'câu hỏi tu từ "liệu...?" cuối đoạn'),
    (r'\bcuối cùng thì\b', 'dịch', 'bỏ'),
    (r'(là chìa khoá|là chìa khóa|là chìa khoá vàng)', 'máy', 'sáo'),
    (r'\b(tấm huy chương hai mặt|con dao hai lưỡi)\b', 'máy', 'sáo'),
    (r'\bhãy cùng\b', 'máy', 'giọng MC'),
    (r'—', 'máy', 'gạch ngang dài: Linh gần như không dùng'),
]

def cau_chot_doan(doan):
    """Đoạn kết bằng câu ngắn dạng khẩu hiệu đều đặn: đếm để cảnh báo nếu quá dày."""
    cau = [c.strip() for c in re.split(r'(?<=[.!?])\s+', doan) if c.strip()]
    return len(cau) >= 3 and len(cau[-1].split()) <= 9

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bai'); ap.add_argument('--hoc'); ap.add_argument('--json', action='store_true')
    ap.add_argument('--bo-qua', default='', help='cụm thuộc đề tài, cách nhau bằng dấu phẩy, không tính (vd: "một người,công ty")')
    a = ap.parse_args()
    dong = Path(a.bai).read_text(encoding='utf-8').splitlines()
    van = [(i+1, d) for i, d in enumerate(dong) if d.strip() and not d.startswith(('#', '|', '*Nguồn'))]
    so_chu = sum(len(d.split()) for _, d in van) or 1
    loi = []
    for i, d in van:
        thap = d.lower()
        for mau, nhom, goi_y in GOC:
            for m in re.finditer(mau, thap):
                loi.append({'dong': i, 'tang': 'goc', 'nhom': nhom, 'cum': m.group(0), 'goi_y': goi_y})
    if a.hoc and Path(a.hoc).exists():
        bo = [b.strip() for b in a.bo_qua.split(',') if b.strip()]
        hoc = [x for x in json.loads(Path(a.hoc).read_text(encoding='utf-8'))['cum'] if not any(b in x['cum'] or x['cum'] in b for b in bo)]
        toan = ' '.join(re.findall(r"[^\W\d_]+", ' '.join(d for _, d in van).lower()))
        for x in hoc:
            k = len(re.findall(r'\b' + re.escape(x['cum']) + r'\b', toan))
            ky_vong = x['nguoi_moi_1000'] * so_chu / 1000
            # chỉ báo khi bài dùng cụm này nhiều hơn hẳn mức của văn Linh
            if k >= 2 and k > 3 * ky_vong + 1:
                dong_dau = next((i for i, d in van if x['cum'] in ' '.join(re.findall(r"[^\W\d_]+", d.lower()))), 0)
                loi.append({'dong': dong_dau, 'tang': 'hoc', 'nhom': 'tần suất', 'cum': f"{x['cum']} ×{k}", 'goi_y': f"văn Linh kỳ vọng ~{ky_vong:.1f} lần, LLM gấp {x['ti_le']}"})
    chot = sum(cau_chot_doan(d) for _, d in van)
    doan = len(van)
    n_goc = sum(1 for x in loi if x['tang'] == 'goc'); n_hoc = len(loi) - n_goc
    diem = max(0, round(100 - 6 * n_goc * 1000 / so_chu - 2 * n_hoc * 1000 / so_chu))
    kq = {'bai': a.bai, 'so_chu': so_chu, 'diem': diem, 'loi_goc': n_goc, 'loi_hoc': n_hoc,
          'doan_ket_cau_ngan': f'{chot}/{doan}', 'loi': loi}
    if a.json:
        print(json.dumps(kq, ensure_ascii=False, indent=1)); return
    print(f"# Văn dịch: {a.bai} · điểm {diem}/100 · {so_chu} chữ · lỗi gốc {n_goc} · cụm học {n_hoc} · đoạn kết câu ngắn {chot}/{doan}")
    for x in loi:
        print(f"- dòng {x['dong']} [{x['tang']}/{x['nhom']}] «{x['cum']}» → {x['goi_y']}")
    if doan and chot / doan > 0.4:
        print('- Cảnh báo: quá nhiều đoạn kết bằng câu ngắn kiểu châm ngôn; Linh dùng như gia vị.')

if __name__ == '__main__':
    main()
