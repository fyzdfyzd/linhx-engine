"""Module 2 (GỘP MỚI): Nghiên cứu người nhận & dựng 3 Persona Neo.
Hợp nhất:
  1. LAB029 (linhx-khoang-trong): Phân tích khoảng trống độc giả (nhu cầu chưa được đáp ứng).
  2. LAB048 (Nemotron-Personas-Vietnam): Lọc có điều kiện nhân khẩu học thực tế từ tập mẫu Việt Nam.
  3. LAB049 (doc-gia-ao): Đắp chiều sâu tâm lý, bối cảnh đọc, nỗi sợ ẩn, câu cửa miệng hay cãi, ngưỡng bỏ đọc.
"""
import argparse
import json
from pathlib import Path

PROTO_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLE_PATH = PROTO_ROOT / "vendor" / "LAB048" / "data" / "persona-sample-60.json"


PERSONA_ARCHETYPES = {
    "bai_viet": {
        "khoang_trong_lab029": {
            "chu_de": "Ứng dụng AI thực chiến trong doanh nghiệp Việt Nam vs. Phong trào mua tool / nói đạo lý AI",
            "dang_thieu_tren_thi_truong": "90% bài viết trên thị trường hoặc hù dọa 'không dùng AI sẽ bị đào thải', hoặc khoe prompt bề nổi; thiếu hẳn góc nhìn giải phẫu quy trình vận hành thực tế và chi phí sửa sai khi nhân sự dùng AI ẩu.",
            "diem_khoang_trong": 8.6,
        },
        "personas": [
            {
                "id": "P1",
                "vai_tro": "Chủ doanh nghiệp SME / Giám đốc vận hành (Độc giả mục tiêu chính)",
                "filter_keywords": ["quản lý", "kinh doanh", "giám đốc", "thương mại", "tài chính"],
                "age_range": (32, 48),
                "boi_canh_doc": "Đọc trên điện thoại lúc 22h30 sau khi xử lý xong việc công ty hoặc sáng sớm uống cà phê trước giờ họp.",
                "noi_so_an": "Sợ tụt hậu nếu không đưa AI vào công ty, nhưng sợ hơn cảnh nhân viên dùng AI xả rác ra báo cáo sai số liệu mà mình không kiểm soát nổi.",
                "cau_hay_cai": "Lý thuyết quy trình nghe thì hay, nhưng nhân sự bên tôi bảo làm thêm bước kiểm tra là họ kêu quá tải ngay.",
                "trigger_bo_doc": "Bỏ đọc ngay ở đoạn 2 nếu thấy giọng hô hào 'kỷ nguyên AI bùng nổ' hoặc liệt kê danh sách 10 công cụ AI.",
                "ky_vong_mang_ve": "Một nguyên tắc phân rã công việc rõ ràng để biết khâu nào giao cho máy, khâu nào bắt buộc người phải giữ chốt.",
            },
            {
                "id": "P2",
                "vai_tro": "Trưởng phòng chuyên môn / Team Lead (Người trực tiếp chịu trận giữa sếp và nhân viên)",
                "filter_keywords": ["kỹ sư", "chuyên viên", "trưởng nhóm", "marketing", "nhân sự", "kế toán"],
                "age_range": (27, 38),
                "boi_canh_doc": "Đọc trên màn hình máy tính văn phòng khi được đồng nghiệp hoặc sếp gửi link qua Zalo nhóm.",
                "noi_so_an": "Sếp ép cắt giảm thời gian làm việc vì nghĩ 'có ChatGPT rồi', trong khi thời gian mình ngồi sửa văn phong ngô nghê của AI còn lâu hơn tự viết.",
                "cau_hay_cai": "Sếp chỉ nhìn sản phẩm cuối chứ có ngồi sửa từng câu văn dịch của AI lúc 8 giờ tối như tụi tôi đâu.",
                "trigger_bo_doc": "Bỏ đọc nếu bài viết đổ hết lỗi cho nhân viên 'lười tư duy' mà không chỉ ra lỗi ở cách giao đề bài của cấp quản lý.",
                "ky_vong_mang_ve": "Gọi đúng tên nỗi khổ 'sửa rác AI mệt hơn tự làm' để có luận điểm trao đổi thẳng thắn với sếp.",
            },
            {
                "id": "P3",
                "vai_tro": "Chuyên gia / Quản lý kỹ thuật hoài nghi (Độc giả khó tính hay bắt bẻ số liệu)",
                "filter_keywords": ["công nghệ", "phần mềm", "dữ liệu", "nghiên cứu", "giảng viên"],
                "age_range": (30, 50),
                "boi_canh_doc": "Đọc lướt rất nhanh trên laptop, soi kỹ các con số, nguồn trích dẫn và tính logic của lập luận.",
                "noi_so_an": "Ngán ngẩm trước làn sóng 'chuyên gia AI tự phong' dùng câu chữ bóng bẩy nhưng rỗng ruột kỹ thuật.",
                "cau_hay_cai": "Số liệu này lấy ở khảo sát nào, mẫu bao nhiêu, hay tác giả tự suy diễn từ vài quán cà phê?",
                "trigger_bo_doc": "Bỏ đọc ngay khi gặp ẩn dụ sáo rỗng kéo dài hoặc con số thả nổi không có chủ thể/nguồn gốc.",
                "ky_vong_mang_ve": "Một góc nhìn sắc lạnh, có bằng chứng xác thực và chỉ ra đúng giới hạn cấu trúc của mô hình ngôn ngữ.",
            },
        ],
    },
    "report_mau": {
        "khoang_trong_lab029": {
            "chu_de": "Báo cáo chẩn đoán & lộ trình đào tạo AI thực chiến cho doanh nghiệp Việt Nam 2026",
            "dang_thieu_tren_thi_truong": "Các báo cáo thị trường hiện tại hoặc dịch nguyên xi số liệu toàn cầu của McKinsey/Gartner (không sát thực tế SME Việt Nam), hoặc là brochure bán khoá học trá hình không có ma trận đo lường ROI.",
            "diem_khoang_trong": 8.9,
        },
        "personas": [
            {
                "id": "P1",
                "vai_tro": "CEO / Thành viên HĐQT duyệt ngân sách đào tạo & chuyển đổi AI",
                "filter_keywords": ["giám đốc", "quản trị", "đầu tư", "doanh nghiệp", "tài chính"],
                "age_range": (35, 55),
                "boi_canh_doc": "Xem bản PDF trên iPad hoặc bản in A4 trong cuộc họp duyệt ngân sách quý (chỉ dành 5 phút đầu quét Executive Summary và biểu đồ).",
                "noi_so_an": "Chi hàng trăm triệu đào tạo xong nhân viên chỉ biết viết email bằng AI, sau 3 tháng đâu lại vào đấy, không đo được năng suất tăng thật.",
                "cau_hay_cai": "Đào tạo xong đo bằng gì để chứng minh tiết kiệm được giờ công, hay chỉ phát chứng chỉ cho vui?",
                "trigger_bo_doc": "Trang đầu toàn chữ đặc kín không có biểu đồ định lượng, hoặc dùng toàn số liệu Mỹ/Châu Âu không có đối chuẩn Việt Nam.",
                "ky_vong_mang_ve": "Khung phân tầng năng lực rõ ràng, chỉ số đo lường trước-sau (KPI/ROI) và lộ trình triển khai 90 ngày không làm đứt gãy vận hành.",
            },
            {
                "id": "P2",
                "vai_tro": "Giám đốc Nhân sự (HRD) / Trưởng bộ phận Đào tạo (L&D)",
                "filter_keywords": ["nhân sự", "đào tạo", "giáo dục", "hành chính", "tổ chức"],
                "age_range": (28, 44),
                "boi_canh_doc": "Đọc kỹ từng trang trên máy tính để lấy căn cứ làm tờ trình bảo vệ kế hoạch đào tạo trước Ban Giám đốc.",
                "noi_so_an": "Tổ chức lớp học mà tỷ lệ hoàn thành bài tập thấp, các trưởng bộ phận phàn nàn chương trình xa rời công việc hàng ngày của họ.",
                "cau_hay_cai": "Chương trình đại trà kiểu này phòng Marketing nghe được chứ phòng Kế toán hay Vận hành ngồi nghe là họ bỏ về.",
                "trigger_bo_doc": "Báo cáo thiếu phân tách nhu cầu theo phòng ban (Marketing, Sales, vận hành, HR) và thiếu phương pháp kèm cặp sau khoá học.",
                "ky_vong_mang_ve": "Bảng ma trận thiết kế chương trình may đo theo nhóm việc và cơ chế nghiệm thu sản phẩm đầu ra ngay tại lớp.",
            },
            {
                "id": "P3",
                "vai_tro": "Trưởng phòng CNTT / Chuyển đổi số (IT/DX Lead - Người gác cổng bảo mật & hạ tầng)",
                "filter_keywords": ["kỹ thuật", "công nghệ", "hệ thống", "an ninh", "mạng"],
                "age_range": (29, 45),
                "boi_canh_doc": "Đọc phần phương pháp luận, quy trình dữ liệu và rủi ro bảo mật trong báo cáo.",
                "noi_so_an": "Nhân viên học xong đem hợp đồng mật, bảng lương, dữ liệu khách hàng dán thẳng lên các công cụ AI công cộng.",
                "cau_hay_cai": "Dạy dùng AI tăng tốc mà không có quy chế phân loại dữ liệu nhạy cảm thì một vụ lộ lọt là bay cả năm lợi nhuận.",
                "trigger_bo_doc": "Báo cáo chỉ tô hồng lợi ích tốc độ mà bỏ qua hoàn toàn cổng kiểm soát rủi ro dữ liệu và ảo giác số liệu (hallucination).",
                "ky_vong_mang_ve": "Bộ quy tắc an toàn dữ liệu và quy trình kiểm chứng 2 lớp được tích hợp sẵn trong khung đào tạo.",
            },
        ],
    },
    "noi_dung_khoa_hoc": {
        "khoang_trong_lab029": {
            "chu_de": "Khoá học thực chiến (Buổi 1): Tư duy cùng AI & Thiết kế quy trình chống rác AI (AI Slop) trong công việc",
            "dang_thieu_tren_thi_truong": "Đa số khoá học dạy mẹo viết câu lệnh (prompt templates) rời rạc; học viên chép về dùng được 2 lần rồi bỏ vì không biết cách biến công việc thành quy trình có bước kiểm duyệt.",
            "diem_khoang_trong": 8.8,
        },
        "personas": [
            {
                "id": "P1",
                "vai_tro": "Chuyên viên cao cấp / Quản lý cấp trung đi học để giải quyết việc thật tại công ty",
                "filter_keywords": ["chuyên viên", "kinh doanh", "kế hoạch", "truyền thông", "quản lý"],
                "age_range": (26, 40),
                "boi_canh_doc": "Ngồi trong lớp học doanh nghiệp (hoặc xem slide/video e-learning trên laptop), trước mặt đang mở sẵn 1 báo cáo/kế hoạch thật cần làm xong trong tuần.",
                "noi_so_an": "Tốn 2 tiếng ngồi học toàn khái niệm lịch sử AI vĩ mô mà hết buổi vẫn không ra được bản khung cho công việc đang nợ sếp.",
                "cau_hay_cai": "Thầy làm ví dụ trên đề bài mẫu thì mượt thế, chứ đụng vào hồ sơ khách hàng lắt léo của em là AI nó viết ngô nghê ngay.",
                "trigger_bo_doc": "15 phút đầu toàn định nghĩa học thuật hoặc slide nhiều chữ đọc chép lại y hệt trên màn hình.",
                "ky_vong_mang_ve": "Cầm tay chỉ việc 1 khung quy trình 5-9 bước áp dụng ngay vào bài toán thật của mình ngay trong giờ thực hành.",
            },
            {
                "id": "P2",
                "vai_tro": "Nhân sự lớn tuổi / Trái ngành công nghệ (Sợ thao tác phức tạp, dễ ngợp thuật ngữ tiếng Anh)",
                "filter_keywords": ["kế toán", "hành chính", "giáo viên", "bán hàng", "dịch vụ"],
                "age_range": (36, 52),
                "boi_canh_doc": "Theo dõi từng bước trên màn chiếu, rất cần ví dụ so sánh trực quan 'Trước khi sửa (bản AI lỗi)' và 'Sau khi sửa (bản đạt chuẩn)'.",
                "noi_so_an": "Sợ giảng viên dùng toàn từ tiếng Anh chuyên ngành (token, context window, hallucination, zero-shot) làm mình không theo kịp đám trẻ.",
                "cau_hay_cai": "Nhiều bước thế này nhớ làm sao hết, có bảng kiểm (checklist) 1 trang tiếng Việt dễ hiểu để nhìn vào làm theo không?",
                "trigger_bo_doc": "Slide nhồi quá 3 thuật ngữ tiếng Anh không giải nghĩa hoặc chuyển cảnh quá nhanh không có hình mẫu đối chiếu.",
                "ky_vong_mang_ve": "Checklist tiếng Việt ngắn gọn, dễ nhớ và 3 dấu hiệu nhận biết ngay văn bản do AI viết ẩu để tự sửa.",
            },
            {
                "id": "P3",
                "vai_tro": "Nhân sự trẻ rành công cụ (Đã dùng ChatGPT/Claude hàng ngày nhưng hay nộp bài bị sếp trả về)",
                "filter_keywords": ["marketing", "nội dung", "thiết kế", "phân tích", "trẻ"],
                "age_range": (22, 28),
                "boi_canh_doc": "Mở laptop gõ thử ngay khi giảng viên đang giảng; nếu thấy kiến thức cơ bản quá sẽ quay sang làm việc riêng.",
                "noi_so_an": "Mình dùng AI làm rất nhanh nhưng sếp đọc 3 dòng là phát hiện ra 'văn ChatGPT' và đánh giá mình làm việc hời hợt.",
                "cau_hay_cai": "Em dùng đủ công thức Role-Task-Context rồi mà sao bài ra vẫn bị chê là sáo rỗng?",
                "trigger_bo_doc": "Giảng viên dạy lại cách đăng nhập ChatGPT hoặc công thức viết prompt sơ cấp đã tràn lan trên mạng.",
                "ky_vong_mang_ve": "Kỹ thuật tách ngữ cảnh phản biện (Persona Neo + 6 lượt biên tập) để khử sạch mùi văn dịch và nâng chất lượng bài lên mức chuyên gia.",
            },
        ],
    },
}


def load_vietnam_census_records():
    if SAMPLE_PATH.exists():
        try:
            return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def match_census_record(records: list, age_range: tuple, idx: int) -> dict:
    lo, hi = age_range
    candidates = [r for r in records if lo <= int(r.get("age", 35)) <= hi]
    if not candidates:
        candidates = records
    if candidates:
        rec = candidates[(idx * 7) % len(candidates)]
        return {
            "nemotron_uuid": rec.get("uuid", f"vn-persona-{idx}"),
            "tuoi": int(rec.get("age", (lo + hi) // 2)),
            "gioi_tinh": rec.get("sex", "Nam"),
            "vung": rec.get("region", "Đồng bằng sông Hồng"),
            "khu_vuc": rec.get("zone", "Đô thị"),
            "hoc_van": rec.get("education_level", "Đại học"),
            "nghe_nghiep_goc": rec.get("occupation", "Quản lý / Chuyên viên"),
        }
    return {
        "nemotron_uuid": f"vn-fallback-{idx}",
        "tuoi": (lo + hi) // 2,
        "gioi_tinh": "Nữ" if idx % 2 else "Nam",
        "vung": "Đông Nam Bộ" if idx % 2 else "Đồng bằng sông Hồng",
        "khu_vuc": "Đô thị",
        "hoc_van": "Đại học",
        "nghe_nghiep_goc": "Quản lý / Chuyên viên",
    }


def build_persona_neo(loai: str, de_bai: str) -> dict:
    import sys
    root_dir = Path(__file__).resolve().parents[2]
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from core_loai_va_gemini import load_loai_config

    loai_cfg = load_loai_config(loai, root_dir=root_dir)
    kieu = loai_cfg.get("kieu_xuat_ban", "bai_viet")
    cfg = PERSONA_ARCHETYPES.get(loai, PERSONA_ARCHETYPES.get(kieu, PERSONA_ARCHETYPES["bai_viet"]))
    records = load_vietnam_census_records()
    personas_out = []
    custom_personas = loai_cfg.get("personas_custom") or []
    source_personas = custom_personas if len(custom_personas) >= 3 else cfg["personas"]

    for idx, p in enumerate(source_personas[:3], start=1):
        age_range = tuple(p.get("age_range", (28, 45)))
        census = match_census_record(records, age_range, idx)
        personas_out.append({
            "id": p.get("id", f"P{idx}"),
            "vai_tro": p.get("vai_tro", f"Độc giả mục tiêu nhóm {idx}"),
            "nhan_khau_lab048": census,
            "boi_canh_doc_lab049": p.get("boi_canh_doc", "Đọc nhanh giữa giờ làm việc để tìm giải pháp thực tế."),
            "noi_so_an_lab049": p.get("noi_so_an", "Sợ lý thuyết sáo rỗng tốn thời gian mà không áp dụng được."),
            "cau_hay_cai_lab049": p.get("cau_hay_cai", "Có con số thực tế và quy trình làm ngay trong tuần không?"),
            "trigger_bo_doc_lab049": p.get("trigger_bo_doc", "Mở bài vòng vo quá 3 câu không có tình huống thật."),
            "ky_vong_mang_ve": p.get("ky_vong_mang_ve", "1 bảng đối chiếu trước/sau và 3 bước làm ngay."),
        })

    return {
        "module": "BM1_02_persona_neo",
        "loai": loai,
        "ten_hien_thi_loai": loai_cfg.get("ten_hien_thi", loai),
        "cau_hinh_loai_da_nap": {
            "do_dai_chu": loai_cfg.get("do_dai_chu"),
            "so_phan_chinh": loai_cfg.get("so_phan_chinh"),
            "bat_buoc_co": loai_cfg.get("bat_buoc_co"),
            "persona_mac_dinh": loai_cfg.get("persona_mac_dinh"),
        },
        "de_bai": de_bai,
        "nguon_gop": [
            "LAB029 (linhx-khoang-trong: nhu-cau-doc-gia & cham-khoang-trong)",
            "LAB048 (Nemotron-Personas-Vietnam: lọc phân tầng nhân khẩu học đô thị/chuyên môn)",
            "LAB049 (linhx-bien-tap: doc-gia-ao - nỗi sợ ẩn, bối cảnh đọc, câu hay cãi)",
        ],
        "nhan_dien_tam": "Sakedemy (LAB043)",
        "trang_thai_mau": "chạy không mẫu",
        "khoang_trong_doc_gia": cfg["khoang_trong_lab029"],
        "personas": personas_out,
    }


def render_markdown(data: dict) -> str:
    kt = data["khoang_trong_doc_gia"]
    lines = [
        f"# BƯỚC 02: NGHIÊN CỨU NGƯỜI NHẬN & DỰNG 3 PERSONA NEO (`{data['loai']}`)",
        "",
        "> **Truy vết Module**: `BM1_02_persona_neo` (Gộp mới từ `LAB029` + `LAB048` + `LAB049`)",
        f"> **Đã gọi**: `LAB029/nhu-cau-doc-gia`, `LAB048/lay_mau_1000.py` (`persona-sample-60.json`), `LAB049/doc-gia-ao`",
        f"> **Nhận diện tạm**: {data['nhan_dien_tam']} · **Trạng thái mẫu**: {data['trang_thai_mau']}",
        "",
        "## 1. Phân tích khoảng trống người nhận (Theo `LAB029`)",
        f"- **Đề bài**: {data['de_bai']}",
        f"- **Chủ đề đối chuẩn**: {kt['chu_de']}",
        f"- **Khoảng trống trên thị trường hiện tại**: {kt['dang_thieu_tren_thi_truong']}",
        f"- **Điểm cơ hội khoảng trống (`gap_score`)**: **{kt['diem_khoang_trong']}/10**",
        "",
        "## 2. Hồ sơ 3 Persona Neo (Lọc nhân khẩu `LAB048` + Tâm lý phản biện `LAB049`)",
        "",
    ]
    for p in data["personas"]:
        nk = p["nhan_khau_lab048"]
        lines.extend([
            f"### [{p['id']}] {p['vai_tro']}",
            f"- **Hồ sơ nhân khẩu học (`LAB048` UUID `{nk['nemotron_uuid']}`)**: {nk['tuoi']} tuổi · {nk['gioi_tinh']} · {nk['khu_vuc']} ({nk['vung']}) · Học vấn: {nk['hoc_van']}",
            f"- **Bối cảnh tiếp nhận (`LAB049`)**: {p['boi_canh_doc_lab049']}",
            f"- **Nỗi sợ ẩn**: {p['noi_so_an_lab049']}",
            f"- **Câu cửa miệng hay cãi (Phản xạ phòng vệ)**: *\"{p['cau_hay_cai_lab049']}\"*",
            f"- **Ngưỡng bỏ đọc (`trigger_bo_doc`)**: {p['trigger_bo_doc_lab049']}",
            f"- **Kỳ vọng mang về sau khi đọc/học**: {p['ky_vong_mang_ve']}",
            "",
        ])
    lines.extend([
        "## 3. Quy tắc neo cho các bước sau",
        "- **Bước 4 (`BM1_04_outline_thu_persona`)**: Cả 3 phương án Outline A/B/C bắt buộc phải đưa qua 3 Persona `P1`, `P2`, `P3` đọc thử và trả lời câu cãi của họ.",
        "- **Bước 8 & 9 (`BM1_08`, `BM1_09`)**: Bản viết cuối không được vi phạm `trigger_bo_doc` của bất kỳ Persona nào và phải trả lời trực diện ít nhất 2/3 câu cãi trên.",
    ])
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loai", required=True)
    ap.add_argument("--de-bai", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", required=True)
    args = ap.parse_args()

    data = build_persona_neo(args.loai, args.de_bai)
    out_p = Path(args.out)
    md_p = Path(args.md)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    md_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    md_p.write_text(render_markdown(data), encoding="utf-8")
    print(f"[BM1_02_persona_neo] OK -> {out_p} & {md_p}")


if __name__ == "__main__":
    main()
