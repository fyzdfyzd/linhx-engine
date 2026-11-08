#!/usr/bin/env python3
"""Mô hình chi phí Persona OS. Mọi con số giả định nằm trong GIA_DINH để Linh sửa và chạy lại.
Giá model Claude lấy từ bảng giá Anthropic (bản lưu 06/10/2026). Giá GPU thuê, VPS, lương, tỷ giá là
GIẢ ĐỊNH chưa kiểm, ghi rõ trong báo cáo.

Chạy: python tools/chi_phi.py [--json]"""
import json
import sys

GIA = {  # USD / 1 triệu token: vào, ra, đọc cache
    "haiku": (0.10, 0.50, 0.01),   # cache Haiku: giả định 10% giá vào
    "sonnet": (2.00, 10.00, 0.20),
    "opus": (4.00, 20.00, 0.20),
}

GIA_DINH = {
    "ty_gia": 26300,                 # VND/USD, giả định
    "he_so_thinking": 2.0,           # token ra thực tế = ra nhìn thấy × hệ số (suy nghĩ thích ứng)
    "so_ngach": 10,
    "bai_pool_ngach_ngay": 400,      # bài cộng đồng mỗi ngách được lọc nhanh mỗi ngày (dùng chung các persona cùng ngách)
    "bible_token": 6000,             # hồ sơ persona + phong cách + luật viết (được cache)
    "doc_sau_persona_ngay": 40,      # bài mỗi persona đọc kỹ qua lăng kính riêng
    "tieu_hoa_ngay": 4,
    "cham_ngay": 15,                 # đề xuất chạm (bình luận, theo dõi, thích có lý do)
    "tin_den_ngay": 40, "tin_soan_ngay": 20,
    "bai_ngay": 1.0,                 # G3 trung bình; G1-G2 thấp hơn
    "ung_vien_moi_bai": 3,
    "anh_moi_bai": 3,                # gồm cả ảnh sinh lại
    "video_tuan": 3, "clip_moi_video": 4,
    "giay_moi_anh_4060": 90,         # giả định Qwen-Image offload trên RTX 4060 8 GB
    "phut_moi_clip_4060": 6,         # giả định Wan2.1 1.3B 5 giây
    "gpu_thue_usd_gio": 0.45,        # giả định 4090 thuê theo giờ
    "toc_do_4090_so_voi_4060": 3.0,
    "vps_usd_thang": 40,             # Postiz + CSDL + crawler, giả định
    "sim_tai_khoan_vnd_thang": 60000,  # mỗi persona 1 số điện thoại xác minh, giả định
    "luong_van_hanh_vnd_thang": 14000000,  # 1 người vận hành toàn thời gian, giả định
    "phut_duyet_persona_ngay": {"A": 12, "B": 6, "C": 6},  # thời gian người duyệt mỗi persona mỗi ngày
    "lora_usd_moi_persona": 6,       # train LoRA một lần trên GPU thuê (khoảng 10-15 giờ 4090), giả định, chia 12 tháng
    "thue_bao_usd_thang": 200,       # gói thuê bao Claude cao nhất cho PA-A, giả định; chỉ hợp thử nghiệm
}


def usd(model, vao, ra, cache=0):
    g = GIA[model]
    return (vao * g[0] + ra * g[1] + cache * g[2]) / 1e6


def token_persona_ngay(gd):
    """Chi phí LLM một persona một ngày theo từng việc (USD), API."""
    b = gd["bible_token"]
    t = gd["he_so_thinking"]
    viec = {}
    viec["doc_sau + tieu_hoa (Sonnet, batch 50%)"] = 0.5 * usd(
        "sonnet", gd["doc_sau_persona_ngay"] * 1200, (gd["tieu_hoa_ngay"] * 400 + gd["doc_sau_persona_ngay"] * 60) * t, cache=b * gd["tieu_hoa_ngay"])
    viec["cham: chọn người + soạn bình luận (Sonnet)"] = usd(
        "sonnet", gd["cham_ngay"] * 1800, gd["cham_ngay"] * 150 * t, cache=b * gd["cham_ngay"])
    viec["hop_thu: phân loại (Haiku) + trả lời (Sonnet)"] = usd(
        "haiku", gd["tin_den_ngay"] * 800, gd["tin_den_ngay"] * 30) + usd(
        "sonnet", gd["tin_soan_ngay"] * 1200, gd["tin_soan_ngay"] * 100 * t, cache=b * gd["tin_soan_ngay"])
    viec["tao: viết ứng viên (Opus) + critic (Sonnet)"] = gd["bai_ngay"] * (
        usd("opus", 9000, gd["ung_vien_moi_bai"] * 450 * t, cache=b) + usd("sonnet", 4000, 500 * t, cache=b))
    viec["hoc: retro tuần (Opus), chia 7"] = usd("opus", 60000, 6000 * t) / 7
    viec["persona: gắn nhãn kiểu nhân vật (Haiku)"] = usd("haiku", 20 * 1500, 20 * 80)
    return viec


def chi_phi(so_persona, pa):
    gd = GIA_DINH
    tg = gd["ty_gia"]
    ngach = min(gd["so_ngach"], max(1, so_persona // 5))
    pool = ngach * usd("haiku", gd["bai_pool_ngach_ngay"] * 700, gd["bai_pool_ngach_ngay"] * 60)
    viec = token_persona_ngay(gd)
    llm_persona = sum(viec.values())
    # GPU
    anh_ngay = so_persona * gd["bai_ngay"] * gd["anh_moi_bai"]
    clip_ngay = so_persona * gd["video_tuan"] * gd["clip_moi_video"] / 7
    gio_4060 = anh_ngay * gd["giay_moi_anh_4060"] / 3600 + clip_ngay * gd["phut_moi_clip_4060"] / 60
    if pa == "A":
        gio_thue = max(0, gio_4060 - 20)  # máy nhà chạy tối đa ~20 giờ/ngày
    elif pa == "B":
        gio_thue = max(0, gio_4060 - 10) / gd["toc_do_4090_so_voi_4060"]  # 4060 chạy đêm, phần dư đẩy lên GPU thuê
    else:
        gio_thue = gio_4060 / gd["toc_do_4090_so_voi_4060"]
    gpu_thang = gio_thue * 30 * gd["gpu_thue_usd_gio"]
    if pa == "C":
        gpu_thang = max(gpu_thang, 24 * 30 * gd["gpu_thue_usd_gio"])  # thuê trọn 1 máy 4090 + talking head/live
    gio_duyet = so_persona * gd["phut_duyet_persona_ngay"][pa] / 60
    nguoi = gio_duyet / 7  # số người toàn thời gian (7 giờ duyệt/ngày)
    if pa == "C":
        nguoi += 1.5  # sản xuất video/live + bán brand
    # PA-A dùng thuê bao thay API: ước số gói cần (giả định 1 gói gánh ~8 persona ở nhịp này)
    if pa == "A":
        llm_thang = max(1, -(-so_persona // 8)) * gd["thue_bao_usd_thang"]
    else:
        llm_thang = (llm_persona * so_persona + pool) * 30
    kq = {
        "so_persona": so_persona, "pa": pa,
        "llm_usd_thang": round(llm_thang, 1),
        "gpu_usd_thang": round(gpu_thang, 1),
        "vps_usd_thang": gd["vps_usd_thang"] * (1 if so_persona <= 50 else 2),
        "lora_usd_thang": round(so_persona * gd["lora_usd_moi_persona"] / 12, 1),
        "sim_vnd_thang": so_persona * gd["sim_tai_khoan_vnd_thang"],
        "nguoi_toan_thoi_gian": round(nguoi, 2),
        "nguoi_vnd_thang": round(nguoi * gd["luong_van_hanh_vnd_thang"]),
        "gio_gpu_4060_ngay": round(gio_4060, 1), "gio_thue_ngay": round(gio_thue, 1),
        "llm_persona_ngay_usd": round(llm_persona, 3), "pool_ngay_usd": round(pool, 3),
    }
    usd_tong = kq["llm_usd_thang"] + kq["gpu_usd_thang"] + kq["vps_usd_thang"] + kq["lora_usd_thang"]
    kq["tong_vnd_thang"] = round(usd_tong * tg + kq["sim_vnd_thang"] + kq["nguoi_vnd_thang"])
    kq["moi_persona_vnd_thang"] = round(kq["tong_vnd_thang"] / so_persona)
    kq["khong_tinh_nguoi_vnd_thang"] = round(usd_tong * tg + kq["sim_vnd_thang"])
    return kq, viec


def main():
    ra = {"gia_dinh": GIA_DINH, "gia_model": GIA, "kich_ban": []}
    _, viec = chi_phi(1, "B")
    ra["llm_mot_persona_ngay"] = {k: round(v, 4) for k, v in viec.items()}
    for pa in ("A", "B", "C"):
        for n in (10, 50, 100):
            ra["kich_ban"].append(chi_phi(n, pa)[0])
    if "--json" in sys.argv:
        print(json.dumps(ra, ensure_ascii=False, indent=1))
        return
    print("LLM một persona một ngày (USD, API):")
    for k, v in ra["llm_mot_persona_ngay"].items():
        print(f"  {k}: {v:.4f}")
    print(f"  tổng: {sum(viec.values()):.3f}")
    print("\nPA | persona | LLM $/th | GPU $/th | người | tổng triệu VND/th | mỗi persona nghìn VND/th | không tính người")
    for k in ra["kich_ban"]:
        print(f"{k['pa']} | {k['so_persona']} | {k['llm_usd_thang']} | {k['gpu_usd_thang']} | {k['nguoi_toan_thoi_gian']} | "
              f"{k['tong_vnd_thang'] / 1e6:.1f} | {k['moi_persona_vnd_thang'] / 1e3:.0f} | {k['khong_tinh_nguoi_vnd_thang'] / 1e6:.1f}")


if __name__ == "__main__":
    main()
