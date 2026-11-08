"""Sinh dữ liệu GIẢ LẬP để thử bao_cao.py khi chưa có crawler thật. Không dùng cho báo cáo bán.

Chạy: python tao_mau.py <ra.jsonl> [--den 2026-10-19] [--seed 7]
Ngày 16/10 cố ý có đợt chê pin VF3 để kiểm phát hiện đột biến.
"""
import argparse, json, random
from datetime import date, timedelta

CAU = [
    ("vinfast", "VF3 chạy {km} km mới sạc, tiết kiệm thật, rất hài lòng"),
    ("vinfast", "Xưởng vinfast bảo hành nhanh, nhân viên nhiệt tình"),
    ("vinfast", "VF5 giá {gia} triệu hơi đắt so với trang bị"),
    ("vinfast", "Trạm sạc vinfast lúc nào cũng đông, chờ mãi bực mình"),
    ("vinfast", "Thiết kế VF7 đẹp, nhìn rất ấn tượng"),
    ("honda", "Honda vision bền, đi 5 năm không hỏng gì"),
    ("honda", "Giá sh bây giờ đắt quá, chênh mấy chục triệu"),
    ("honda", "Air blade đời mới chạy êm, ổn"),
    ("yadea", "Yadea rẻ nhưng pin xuống nhanh, thất vọng"),
    ("yadea", "Xe yadea màu đẹp, giá rẻ hợp sinh viên"),
    ("dat bike", "Dat bike chạy mạnh mẽ, sạc nhanh, tuyệt"),
    ("dat bike", "Dat bike bảo hành chậm, chờ linh kiện lâu"),
    ("vinfast", "Tuyển dụng nhân viên kinh doanh vinfast lương cao"),  # phải bị loại trừ
    ("honda", "Chiếc honda này không tệ, đi phố ok"),
]
DOT_BIEN = "VF3 nhà mình bị lỗi pin, sạc không vào, xưởng không giải quyết, quá thất vọng"
NEN_TANG = ["facebook", "facebook", "tiktok", "youtube", "voz", "baochi"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ra"); p.add_argument("--den", default="2026-10-19"); p.add_argument("--seed", type=int, default=7)
    g = p.parse_args()
    r = random.Random(g.seed)
    den = date.fromisoformat(g.den)
    with open(g.ra, "w", encoding="utf-8") as f:
        i = 0
        for lui in range(14):
            d = den - timedelta(days=lui)
            n = r.randint(12, 20) + (40 if d == den - timedelta(days=3) else 0)
            for k in range(n):
                if d == den - timedelta(days=3) and k < 40:
                    text = DOT_BIEN + r.choice(["", "!!", " ai bị giống không", " #vinfast"])
                else:
                    text = r.choice(CAU)[1].format(km=r.randint(150, 220), gia=r.choice([460, 529, 548]))
                i += 1
                f.write(json.dumps({
                    "id": f"gia-{i}", "platform": r.choice(NEN_TANG), "url": f"https://vi-du.invalid/{i}",
                    "author": f"user{r.randint(1, 999)}", "text": text, "published_at": f"{d}T{r.randint(6, 23):02d}:00:00",
                    "metrics": {"like": r.randint(0, 300), "comment": r.randint(0, 60), "share": r.randint(0, 20)},
                }, ensure_ascii=False) + "\n")
    print(f"{i} bản ghi giả lập -> {g.ra}")


if __name__ == "__main__":
    main()
