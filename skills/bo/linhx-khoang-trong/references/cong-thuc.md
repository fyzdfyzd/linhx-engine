# Công thức và ngưỡng (v0.1, hiệu chỉnh sau 3 lượt chạy thật)

## B2
- **Chỉ số cầu/cung của tag** = trung vị tương tác bài mang tag ÷ trung vị tương tác cả nguồn. Chỉ tính tag có ≥ 30 bài, bỏ tag nội bộ nền tảng (`tag_bo_qua`).
- **Bài vượt** = tương tác bài ÷ max(trung vị bài của chính tác giả, 25% trung vị nguồn) ≥ 3, và bài ≥ trung vị nguồn. Cần tác giả có ≥ 4 bài trong mẫu. (ý từ youtube-niche-finder, social-account-doctor)
- **Nhỏ mà nổ** = tác giả dưới 5.000 follower và bài ở top 10% nguồn. (ý "低粉爆款" của Redfox)
- **Chỉ số cầu/cung của cụm** = trung bình có trọng số (theo số bài) của tỉ lệ trung vị cụm ÷ trung vị nguồn, qua các nguồn.

## B4
`cau_nguon = 0,35 × min(1, log10(tổng người theo + 1) / 7) + 0,35 × min(1, cầu/cung / 3) + 0,15 × min(1, log2(1 + số bài vượt) / 4) + 0,15 × min(1, số tác giả / 50)`

Tăng trưởng 28 ngày = (số bài 28 ngày gần nhất − 28 ngày trước đó) ÷ 28 ngày trước đó.

## B5
- Mức mỗi nền tảng: `covered` khi có kênh ≥ `nguong_kenh_lon` của nền tảng, hoặc ≥ 3 kênh ≥ `nguong_kenh_vua`, hoặc (nền tảng bảng xếp hạng, ngưỡng 0) lọt top 20; `thin` khi có khớp; `open` khi đã quét mà không khớp; `chua_quet`.
- Điểm phủ: open 0,1; thin 0,45; covered 0,9. `phu_vn` = trung bình có trọng số `nen_tang_vn` trên các nền tảng đã quét.
- **Độ phủ dữ liệu** = tổng trọng số nền tảng đã quét ÷ tổng trọng số. Dưới 0,6 thì B6 chỉ ra bản nháp. (luật của youtube-niche-finder)
- Tuỳ chọn `--embed`: `paraphrase-multilingual-MiniLM-L12-v2`, cosine ≥ 0,62 giữa bài Việt và mô tả cụm.

## B6
`điểm = 100 × cau_nguon × chuyen_giao × (1 − phu_vn) × thoi_diem`, với `thoi_diem = 1 + 0,3 × tăng trưởng`, kẹp trong [0,8; 1,3]. Ý gốc: "chênh nhiệt" giữa thị trường (TrendRadar 平台温差) và gap_score đề xuất trong `refs/REPOS-CN.md`.

## Điều chỉnh được trong `cau-hinh.json`
`nen_tang_vn` (trọng số), `nguong_kenh_lon`, `nguong_kenh_vua`, `nguong_phu_du_lieu`, `so_bai_toi_thieu_moi_tag`, `so_bai_toi_thieu_moi_cum`, `follower_nho`, `nguong_tieu_bieu_vuot`, `cua_so_tang_truong_ngay`, `tag_bo_qua`.
