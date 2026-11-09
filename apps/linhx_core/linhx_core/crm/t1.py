"""Xử lý lưu kết quả đầy đủ T1 Khám đổi lấy email/Zalo, ghi Người + Đồng ý + tầng phễu.

Thuần Python, không phụ thuộc Frappe ở mức module.
Tham khảo luồng CRM và tuân thủ từ:
- nguon/03-opc-os/modules/04_quan_ly_user/module.py
- nguon/03-opc-os/modules/09_tuan_thu/module.py
"""
from __future__ import annotations

from linhx_core.crm import dong_y, gop_trung

NGUON_T1 = "T1"
TANG_PHEU_MOI = "moi"

DO_DAI_TOI_DA_HO_TEN = 120
DO_DAI_TOI_DA_DIEN_THOAI = 20
DO_DAI_TOI_DA_EMAIL = 254
DO_DAI_TOI_DA_ZALO = 64
DO_DAI_TOI_DA_MUC = 120
DIEM_TOI_THIEU = 0
DIEM_TOI_DA = 1000
TRUONG_HONEYPOT = ("website", "hp_url", "trap_field")

CAU_HINH_KHAM_MAC_DINH: dict = {
    "tieu_de": "T1 Khám — Chẩn đoán mức độ sẵn sàng AI & Tự động hoá (LAB113)",
    "cau": [
        {
            "ma": "du_lieu_khach",
            "hoi": "1. Dữ liệu khách hàng tiềm năng (Lead) hiện đang được lưu trữ và quản lý như thế nào?",
            "lua_chon": [
                {"nhan": "Rời rạc trên tin nhắn Zalo, Facebook, sổ tay cá nhân của từng nhân viên", "diem": 1},
                {"nhan": "Gom thủ công vào các file Excel hoặc Google Sheets định kỳ", "diem": 2},
                {"nhan": "Có phần mềm CRM nhưng vẫn phải nhập tay và hay bị trùng lặp hồ sơ", "diem": 3},
                {"nhan": "Tự động gom từ mọi kênh về một hệ thống chung, tự gộp trùng theo SĐT/Email/Zalo", "diem": 4},
            ],
        },
        {
            "ma": "toc_do_phan_hoi",
            "hoi": "2. Khi có khách hàng mới để lại thông tin, mất bao lâu để có người phụ trách tiếp nhận?",
            "lua_chon": [
                {"nhan": "Thường trên 24 giờ hoặc đôi khi bị bỏ sót không ai liên hệ", "diem": 1},
                {"nhan": "Trong ngày làm việc (từ 4 đến 8 giờ sau khi khách điền thông tin)", "diem": 2},
                {"nhan": "Trong vòng 1 đến 4 giờ nhờ quản lý phân công thủ công", "diem": 3},
                {"nhan": "Dưới 1 giờ, hệ thống tự động giao người phụ trách và nhắc việc chờ", "diem": 4},
            ],
        },
        {
            "ma": "hien_dien_ai",
            "hoi": "3. Khi khách hàng hỏi các công cụ AI (ChatGPT, Gemini, Claude) về lĩnh vực của bạn, thương hiệu của bạn xuất hiện ra sao?",
            "lua_chon": [
                {"nhan": "Chưa từng kiểm tra hoặc hoàn toàn không được AI nhắc tới", "diem": 1},
                {"nhan": "Thỉnh thoảng xuất hiện nhưng thông tin sai lệch hoặc thiếu thế mạnh cốt lõi", "diem": 2},
                {"nhan": "Xuất hiện đúng thông tin cơ bản ở một số câu hỏi thương hiệu trực tiếp", "diem": 3},
                {"nhan": "Được AI đề xuất chính xác kèm lý do chọn trong các truy vấn so sánh ngành", "diem": 4},
            ],
        },
        {
            "ma": "tuan_thu_dong_y",
            "hoi": "4. Việc ghi nhận sự đồng ý của khách hàng (liên hệ, tiếp thị, chia sẻ nội bộ) đang được thực hiện thế nào?",
            "lua_chon": [
                {"nhan": "Không có bước xin đồng ý hay lưu nhật ký nào", "diem": 1},
                {"nhan": "Có dòng chữ nhỏ trên form nhưng không lưu trạng thái theo từng khách", "diem": 2},
                {"nhan": "Có lưu trạng thái đồng ý lúc đăng ký nhưng khó tra cứu khi khách yêu cầu rút lại", "diem": 3},
                {"nhan": "Quản lý đồng ý theo từng mục đích, có nhật ký thay đổi và chặn tự động khi rút đồng ý", "diem": 4},
            ],
        },
        {
            "ma": "thanh_toan_ban_giao",
            "hoi": "5. Quy trình từ lúc khách thanh toán gói dịch vụ/báo cáo đến khi nhận kết quả diễn ra như thế nào?",
            "lua_chon": [
                {"nhan": "Khách chụp ảnh màn hình chuyển khoản, kế toán kiểm tra tay rồi mới báo bộ phận chuyên môn", "diem": 1},
                {"nhan": "Có mã QR thanh toán nhưng vẫn phải duyệt tay để kích hoạt đơn hàng", "diem": 2},
                {"nhan": "Tự động xác nhận thanh toán nhưng bước tạo và gửi báo cáo vẫn làm thủ công", "diem": 3},
                {"nhan": "VietQR đối soát tự động theo mã đơn, lập tức khởi chạy tiến trình và giao kết quả", "diem": 4},
            ],
        },
        {
            "ma": "do_luong_pheu",
            "hoi": "6. Ban điều hành theo dõi tỷ lệ chuyển đổi toàn phễu và chi phí vận hành AI/nhân sự bằng cách nào?",
            "lua_chon": [
                {"nhan": "Ước lượng cảm tính, cuối tháng mới tổng hợp số liệu doanh thu", "diem": 1},
                {"nhan": "Nhân viên báo cáo thủ công hàng tuần qua tin nhắn hoặc bảng tính", "diem": 2},
                {"nhan": "Có bảng thống kê từng kênh nhưng chưa nối thông suốt từ Lead tới Đơn đã trả", "diem": 3},
                {"nhan": "Bàn điều hành cập nhật trực tiếp 6 tầng phễu, việc chờ và chi phí từng tác vụ", "diem": 4},
            ],
        },
    ],
    "muc": [
        {
            "tu": 6,
            "den": 11,
            "ten": "Chưa sẵn sàng",
            "tom_tat": "Quy trình tiếp nhận khách hàng và dữ liệu hiện tại còn phân mảnh, phụ thuộc nhiều vào thao tác thủ công. Bạn nên ưu tiên chuẩn hoá nguồn thu thập Lead, thiết lập lưu trữ đồng ý của khách hàng và kiểm tra hiện diện thương hiệu trên AI trước khi mở rộng tự động hoá.",
        },
        {
            "tu": 12,
            "den": 18,
            "ten": "Sẵn sàng một phần",
            "tom_tat": "Doanh nghiệp đã có nền tảng quy trình cơ bản nhưng các khâu giữa tiếp nhận Lead, phân công chăm sóc và đối soát thanh toán chưa nối liền mạch. Đây là thời điểm phù hợp để áp dụng tự động hoá gộp trùng hồ sơ, giao việc có hạn giờ và chẩn đoán sâu thương hiệu trên AI.",
        },
        {
            "tu": 19,
            "den": 24,
            "ten": "Sẵn sàng",
            "tom_tat": "Hệ thống dữ liệu, quy trình phản hồi và đo lường chuyển đổi của bạn đã có cấu trúc vững chắc. Doanh nghiệp hoàn toàn sẵn sàng vận hành khép kín trên nền LINHX ENGINE: từ công cụ phễu tự động, VietQR tự giao báo cáo đến bàn điều hành theo dõi thời gian thực.",
        },
    ],
}


def _kiem_tra_dau_vao(du_lieu: dict) -> tuple[str, str, str, str, str]:
    """Kiểm tra honeypot và giới hạn độ dài các trường đầu vào trước khi chuẩn hoá."""
    for tr_hp in TRUONG_HONEYPOT:
        if str(du_lieu.get(tr_hp) or "").strip():
            raise ValueError("Phát hiện gửi tự động không hợp lệ")

    ho_ten = str(du_lieu.get("ho_ten") or "").strip()
    dien_thoai = str(du_lieu.get("dien_thoai") or "").strip()
    email = str(du_lieu.get("email") or "").strip()
    zalo = str(du_lieu.get("zalo") or "").strip()
    muc = str(du_lieu.get("muc") or "").strip()

    if len(ho_ten) > DO_DAI_TOI_DA_HO_TEN:
        raise ValueError(f"Họ tên vượt quá độ dài tối đa ({DO_DAI_TOI_DA_HO_TEN} ký tự)")
    if len(dien_thoai) > DO_DAI_TOI_DA_DIEN_THOAI:
        raise ValueError(f"Số điện thoại vượt quá độ dài tối đa ({DO_DAI_TOI_DA_DIEN_THOAI} ký tự)")
    if len(email) > DO_DAI_TOI_DA_EMAIL:
        raise ValueError(f"Email vượt quá độ dài tối đa ({DO_DAI_TOI_DA_EMAIL} ký tự)")
    if len(zalo) > DO_DAI_TOI_DA_ZALO:
        raise ValueError(f"Zalo vượt quá độ dài tối đa ({DO_DAI_TOI_DA_ZALO} ký tự)")
    if len(muc) > DO_DAI_TOI_DA_MUC:
        raise ValueError(f"Mức đánh giá T1 vượt quá độ dài tối đa ({DO_DAI_TOI_DA_MUC} ký tự)")

    return ho_ten, dien_thoai, email, zalo, muc


def da_rut_dong_y(
    so_dong_y: list[dict],
    dinh_danh: str | list[str] | set[str],
    muc_dich: str,
) -> bool:
    """Kiểm tra xem người dùng đã có bản ghi đồng ý cho `muc_dich` nhưng trạng thái hiệu lực
    mới nhất là rút đồng ý (`dong_y=0` / `False`).
    """
    if not so_dong_y:
        return False
    if isinstance(dinh_danh, str):
        tap_ma = {dinh_danh.strip()} if dinh_danh.strip() else set()
    else:
        tap_ma = {str(x).strip() for x in (dinh_danh or []) if str(x or "").strip()}
    if not tap_ma:
        return False

    ma_dai_dien = next(iter(tap_ma))
    so_quy_doi: list[dict] = []
    co_dong = False
    for d in so_dong_y:
        if not isinstance(d, dict):
            continue
        ma_d = dong_y._ma_nguoi(d.get("nguoi"))
        if ma_d in tap_ma:
            if str(d.get("trang_thai") or "").strip() == "cho_xac_minh":
                continue
            if d.get("muc_dich") == muc_dich:
                co_dong = True
            ban_sao = dict(d)
            ban_sao["nguoi"] = ma_dai_dien
            so_quy_doi.append(ban_sao)

    if not co_dong:
        return False
    return not dong_y.hieu_luc(so_quy_doi, ma_dai_dien, muc_dich)


def kiem_diem_theo_bang_muc(
    t1_tong: int,
    t1_muc: str,
    bang_muc: list[dict] | None,
    cau: list[dict] | None = None,
    chon: dict | None = None,
) -> None:
    """Kiểm đối chiếu tổng điểm và tên mức T1 với bảng cấu hình câu hỏi/mức chuẩn."""
    if isinstance(chon, dict) and chon and isinstance(cau, list) and cau:
        tong_tinh = 0
        for c in cau:
            ma = str((c or {}).get("ma") or "")
            ds_lc = (c or {}).get("lua_chon") or []
            if ma not in chon or not isinstance(chon[ma], int) or isinstance(chon[ma], bool):
                raise ValueError("Đáp án câu hỏi T1 không đầy đủ hoặc không hợp lệ")
            idx = chon[ma]
            if idx < 0 or idx >= len(ds_lc):
                raise ValueError("Chỉ số lựa chọn câu hỏi T1 vượt phạm vi")
            tong_tinh += int(ds_lc[idx].get("diem") or 0)
        if tong_tinh != t1_tong:
            raise ValueError("Tổng điểm T1 không khớp với đáp án đã chọn")

    if not bang_muc:
        return

    muc_khop = None
    for m in bang_muc:
        if not isinstance(m, dict):
            continue
        tu = int(m.get("tu", 0))
        den = int(m.get("den", 0))
        if tu <= t1_tong <= den:
            muc_khop = m
            break

    if muc_khop is None:
        raise ValueError("Tổng điểm T1 nằm ngoài phạm vi bảng mức")

    ten_chuan = str(muc_khop.get("ten") or "").strip()
    if ten_chuan and ten_chuan != str(t1_muc or "").strip():
        raise ValueError("Mức đánh giá T1 không khớp với tổng điểm theo bảng mức")


def tao_ket_qua_day_du(
    t1_tong: int,
    t1_muc: str,
    bang_muc: list[dict] | None = None,
    cau: list[dict] | None = None,
    chon: dict | None = None,
) -> dict:
    """Tạo nội dung báo cáo phân tích đầy đủ phía máy chủ theo điểm vừa gửi."""
    ds_muc = bang_muc if bang_muc else CAU_HINH_KHAM_MAC_DINH["muc"]
    ds_cau = cau if cau else CAU_HINH_KHAM_MAC_DINH["cau"]

    tom_tat = ""
    for m in ds_muc or []:
        if isinstance(m, dict) and int(m.get("tu", 0)) <= t1_tong <= int(m.get("den", 0)):
            tom_tat = str(m.get("tom_tat") or "").strip()
            break

    hang_muc: list[dict] = []
    if isinstance(ds_cau, list) and isinstance(chon, dict):
        for c in ds_cau:
            ma = str((c or {}).get("ma") or "")
            hoi = str((c or {}).get("hoi") or "")
            ds_lc = (c or {}).get("lua_chon") or []
            idx = chon.get(ma)
            if isinstance(idx, int) and not isinstance(idx, bool) and 0 <= idx < len(ds_lc):
                lc = ds_lc[idx] or {}
                diem = int(lc.get("diem") or 0)
                hang_muc.append(
                    {
                        "ma": ma,
                        "hoi": hoi,
                        "nhan": str(lc.get("nhan") or ""),
                        "diem": diem,
                        "khuyen_nghi": (
                            "Ưu tiên chuẩn hoá quy trình và dữ liệu đầu vào trước khi tự động hoá."
                            if diem <= 2
                            else "Đã có nền tảng tốt, có thể triển khai tác tử AI tự động hoá ngay."
                        ),
                    }
                )

    return {
        "tong": t1_tong,
        "muc": t1_muc,
        "tom_tat": tom_tat,
        "lo_trinh_de_xuat": [
            f"Giai đoạn 1: Chuẩn hoá phễu dữ liệu và quy trình ưu tiên cho mức '{t1_muc}' ({t1_tong} điểm).",
            "Giai đoạn 2: Tích hợp CRM tập trung và tự động hoá tiếp nhận/phân bổ cơ hội.",
            "Giai đoạn 3: Đo lường hiệu quả chuyển đổi 6 tầng phễu và tối ưu vận hành.",
        ],
        "hang_muc": hang_muc,
    }


def ghi_ket_qua(du_lieu: dict, ds_nguoi: list, so_dong_y: list, luc: str) -> dict:
    """Ghi nhận kết quả T1 Khám đổi lấy email/Zalo, gộp trùng Người và ghi sổ Đồng ý một bước.

    Tham số:
        du_lieu: {"email" | "zalo", "ho_ten"?, "tong": int, "muc": str,
                  "dong_y_lien_he": True, "dong_y_marketing"?: bool}
        ds_nguoi: danh sách hồ sơ Người hiện có
        so_dong_y: danh sách dòng đồng ý hiện có
        luc: thời điểm ghi nhận ("YYYY-MM-DD HH:MM:SS")

    Trả về:
        {"ds_nguoi": list, "nguoi": dict, "so_dong_y": list}
    """
    if not isinstance(du_lieu, dict):
        raise ValueError("Dữ liệu kết quả T1 không hợp lệ")

    if du_lieu.get("dong_y_lien_he") is not True:
        raise ValueError("Phải đồng ý liên hệ để nhận kết quả T1 đầy đủ")

    ho_ten, dien_thoai, email_raw, zalo_raw, t1_muc = _kiem_tra_dau_vao(du_lieu)
    email_chuan = gop_trung.chuan_hoa_email(email_raw)
    zalo_chuan = gop_trung.chuan_hoa_zalo(zalo_raw)
    if not email_chuan and not zalo_chuan:
        raise ValueError("Phải cung cấp ít nhất email hoặc Zalo")

    tong_raw = du_lieu.get("tong")
    if tong_raw is None or isinstance(tong_raw, bool):
        raise ValueError("Thiếu tổng điểm T1")
    try:
        t1_tong = int(tong_raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("Tổng điểm T1 không hợp lệ") from exc
    if t1_tong < DIEM_TOI_THIEU or t1_tong > DIEM_TOI_DA:
        raise ValueError("Tổng điểm T1 nằm ngoài phạm vi cho phép")

    if not t1_muc:
        raise ValueError("Thiếu mức đánh giá T1")

    if du_lieu.get("bang_muc"):
        kiem_diem_theo_bang_muc(
            t1_tong,
            t1_muc,
            du_lieu.get("bang_muc"),
            du_lieu.get("cau"),
            du_lieu.get("chon"),
        )

    luc_str = str(luc or "").strip() or dong_y.bay_gio()

    ban_lien_he: dict = {}
    if ho_ten:
        ban_lien_he["ho_ten"] = ho_ten
    if dien_thoai:
        ban_lien_he["dien_thoai"] = dien_thoai
    if email_raw:
        ban_lien_he["email"] = email_raw
    if zalo_raw:
        ban_lien_he["zalo"] = zalo_raw

    khoa_moi = gop_trung.khoa_gop(ban_lien_he)
    nguoi_cu_khop = None
    for cu in ds_nguoi or []:
        if isinstance(cu, dict) and (gop_trung.khoa_gop(cu) & khoa_moi):
            nguoi_cu_khop = cu
            break

    da_co_nguoi = nguoi_cu_khop is not None
    if not da_co_nguoi:
        ban_moi = dict(ban_lien_he)
        ban_moi["nguon"] = NGUON_T1
        ban_moi["tang_pheu"] = TANG_PHEU_MOI
        ban_moi["t1_tong"] = t1_tong
        ban_moi["t1_muc"] = t1_muc
        ds_moi = gop_trung.gop(ds_nguoi, ban_moi)
        nguoi_ket_qua = ds_moi[-1]
    else:
        # Người đã có: không ghi đè dữ liệu cũ (ho_ten, email, zalo, dien_thoai, nguon, tang_pheu, điểm cũ)
        # bằng dữ liệu form; chỉ điền t1_tong/t1_muc khi hồ sơ cũ chưa có điểm T1.
        ds_moi = [dict(x) if isinstance(x, dict) else x for x in (ds_nguoi or [])]
        nguoi_ket_qua = None
        for item in ds_moi:
            if isinstance(item, dict) and (gop_trung.khoa_gop(item) & khoa_moi):
                if gop_trung._la_trong(item.get("nguon")):
                    item["nguon"] = NGUON_T1
                if gop_trung._la_trong(item.get("tang_pheu")):
                    item["tang_pheu"] = TANG_PHEU_MOI
                cu_da_co_diem = (
                    item.get("t1_tong") not in (None, "", 0)
                    or bool(str(item.get("t1_muc") or "").strip())
                )
                if not cu_da_co_diem:
                    item["t1_tong"] = t1_tong
                    item["t1_muc"] = t1_muc
                else:
                    lich_su = list(item.get("lich_su_t1") or [])
                    muc_ls: dict = {"luc": luc_str, "t1_tong": t1_tong, "t1_muc": t1_muc}
                    lich_su.append(muc_ls)
                    item["lich_su_t1"] = lich_su
                nguoi_ket_qua = item
                break
        if nguoi_ket_qua is None:
            nguoi_ket_qua = ds_moi[-1]

    ma_nguoi = str(
        nguoi_ket_qua.get("name")
        or email_chuan
        or zalo_chuan
        or nguoi_ket_qua.get("email")
        or nguoi_ket_qua.get("zalo")
    ).strip()

    cac_dinh_danh = {
        x
        for x in (
            ma_nguoi,
            str(nguoi_ket_qua.get("name") or "").strip(),
            str(nguoi_ket_qua.get("email") or "").strip(),
            str(nguoi_ket_qua.get("zalo") or "").strip(),
            email_chuan,
            email_raw,
            zalo_chuan,
            zalo_raw,
        )
        if x
    }

    so_moi = [dict(d) if isinstance(d, dict) else d for d in (so_dong_y or [])]
    if not (da_co_nguoi and da_rut_dong_y(so_moi, cac_dinh_danh, "lien_he")):
        so_moi = dong_y.ghi(so_moi, ma_nguoi, "lien_he", True, luc_str, NGUON_T1)

    if du_lieu.get("dong_y_marketing") is True:
        if not (da_co_nguoi and da_rut_dong_y(so_moi, cac_dinh_danh, "marketing")):
            so_moi = dong_y.ghi(
                so_moi,
                ma_nguoi,
                "marketing",
                True,
                luc_str,
                NGUON_T1,
                trang_thai="cho_xac_minh",
            )

    return {
        "ds_nguoi": ds_moi,
        "nguoi": dict(nguoi_ket_qua),
        "so_dong_y": so_moi,
    }
