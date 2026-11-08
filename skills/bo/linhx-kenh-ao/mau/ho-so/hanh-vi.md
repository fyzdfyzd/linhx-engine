# Khung hành vi

Chỉ số chính: hấp thu/tạo ≥ **10:1 tính bằng phút công** trong 7 ngày (đọc 2, tiêu hoá 10, chạm 2, trả lời 3 phút; mỗi bài tạo 15 phút) · chạm không được đáp tối đa **3** lần liền · G0 → G3 theo ngày tuổi **và** chỉ số quan hệ.

Bốn luật gốc (Linh, 16/10/2026):
1. Đọc, xem, tương tác, tiêu hoá phải gấp ít nhất 10 lần phần tạo.
2. Dựa trên niềm tin và quan hệ: điểm tin chỉ tăng khi người kia đáp lại; chạm một chiều mãi thì dừng.
3. Mọi hành động phải có mục đích nằm trong danh sách dưới, kèm lý do riêng với người đó.
4. Vào cộng đồng như người mới: lang thang đọc, xem trend, kết thân, rồi mới đăng nhiều.

Giai đoạn:
- **G0 Quan sát** (ngày 0-6): chỉ đọc, ghi chú, lập vòng quan hệ. Không chạm, không đăng.
- **G1 Làm quen** (từ ngày 7, khi vòng ≥ 20 người, đã đọc ≥ 100 bài, có ≥ 1 bản đồ trend): thích, lưu, theo dõi chọn lọc, bình luận ít. 1 bài/tuần (bài giới thiệu).
- **G2 Góp chuyện** (từ ngày 21, khi ≥ 8 người đã đáp lại): bình luận đều trên vòng, trả lời người đáp. 3 bài/tuần.
- **G3 Nuôi kênh** (từ ngày 45, khi ≥ 5 quan hệ hai chiều và ≥ 6 bài đã đăng): đăng đều, hộp thư, nuôi fan. Lang thang vẫn là phần lớn thời gian.

Sửa số trong khối json dưới; agent không tự sửa file này, chỉ đề xuất trong RETRO.

```json
{
 "ty_le_hap_thu": {"toi_thieu": 10, "cua_so_ngay": 7, "don_vi": "phút công",
   "trong_so": {"doc": 2, "tieu_hoa": 10, "cham": 2, "tra_loi": 3}, "tao_phut_moi_bai": 15},
 "giai_doan": [
  {"ma": "G0", "ten": "Quan sát", "y_nghia": "đọc để hiểu cộng đồng, chưa ai biết mình",
   "vao_khi": {"tuoi_ngay": 0}, "so_phien_ngay": 2,
   "viec_duoc_lam": ["doc", "tieu_hoa", "trend", "vong"],
   "han_muc_ngay": {"thich": 0, "luu": 0, "theo_doi": 0, "binh_luan": 0, "nhan": 0, "dang": 0}},
  {"ma": "G1", "ten": "Làm quen", "y_nghia": "chạm nhẹ, cho người ta thấy mình đọc kỹ",
   "vao_khi": {"tuoi_ngay": 7, "so_nguoi_trong_vong": 20, "so_bai_da_doc": 100, "so_ban_do_trend": 1},
   "so_phien_ngay": 3, "dang_toi_da_tuan": 1,
   "viec_duoc_lam": ["doc", "tieu_hoa", "trend", "vong", "cham"],
   "tu_lam_khong_duyet": ["thich", "luu"],
   "han_muc_ngay": {"thich": 15, "luu": 10, "theo_doi": 3, "binh_luan": 3, "nhan": 0, "dang": 1}},
  {"ma": "G2", "ten": "Góp chuyện", "y_nghia": "góp ý có giá trị, bắt đầu được đáp lại",
   "vao_khi": {"tuoi_ngay": 21, "so_nguoi_tu_duoc_dap": 8},
   "so_phien_ngay": 3, "dang_toi_da_tuan": 3,
   "viec_duoc_lam": ["doc", "tieu_hoa", "trend", "vong", "cham", "tao", "hop_thu"],
   "tu_lam_khong_duyet": ["thich", "luu"],
   "han_muc_ngay": {"thich": 25, "luu": 15, "theo_doi": 5, "binh_luan": 8, "nhan": 0, "dang": 1}},
  {"ma": "G3", "ten": "Nuôi kênh", "y_nghia": "có quan hệ thật, đăng đều và chăm người theo",
   "vao_khi": {"tuoi_ngay": 45, "so_nguoi_tu_hai_chieu": 5, "so_bai_da_dang": 6},
   "so_phien_ngay": 4, "dang_toi_da_tuan": 7,
   "viec_duoc_lam": ["doc", "tieu_hoa", "trend", "vong", "cham", "tao", "hop_thu", "hoc"],
   "tu_lam_khong_duyet": ["thich", "luu"],
   "han_muc_ngay": {"thich": 30, "luu": 20, "theo_doi": 5, "binh_luan": 12, "nhan": 3, "dang": 2}}
 ],
 "muc_dich": {
  "thich": ["ghi_nhan_bai_hay", "ung_ho_nguoi_moi"],
  "luu": ["luu_de_hoc", "luu_lam_tu_lieu"],
  "theo_doi": ["muon_hoc_tu_ho", "cung_cong_dong", "dap_le_nguoi_da_theo"],
  "binh_luan": ["bo_sung_gia_tri", "hoi_de_hieu", "chia_se_trai_nghiem", "tra_loi_cau_hoi_cua_ho", "phan_bien_co_ly"],
  "nhan": ["cam_on_rieng", "tra_loi_ho", "de_nghi_hop_tac_cong_khai"]
 },
 "luat_cham": {
  "vi_sao_toi_thieu_ky_tu": 15,
  "doc_de_len_da_doc": 3,
  "doc_toi_thieu_truoc": {"thich": 1, "luu": 1, "theo_doi": 3, "binh_luan": 3, "nhan": 5},
  "bac_toi_thieu_truoc": {"binh_luan": "da_cham", "nhan": "hai_chieu"},
  "diem_tin_toi_thieu": {"nhan": 8},
  "nghi_giua_hai_lan_ngay": {"binh_luan": 3, "theo_doi": 9999, "nhan": 7},
  "dung_khi_cham_khong_dap": 3,
  "bai_cu_toi_da_ngay": 7,
  "binh_luan_toi_thieu_ky_tu": 40,
  "cum_chung_chung": ["hay quá", "tuyệt vời", "cảm ơn bạn", "quá đỉnh", "chuẩn", "hay", "nice", "great post"],
  "cam_tu_quang_cao_o": ["G0", "G1", "G2"],
  "dau_hieu_tu_quang_cao": ["kênh mình", "follow mình", "ghé trang", "inbox mình", "link bio", "http"],
  "cho_cham_nguoi_nha_cong_khai": false
 },
 "diem_tin": {
  "giam_moi_tuan": 0.9, "dong_minh_tu": 25,
  "su_kien": {"tra_loi_binh_luan_minh": 3, "thich_binh_luan_minh": 1, "theo_doi_lai": 3,
              "binh_luan_bai_minh": 4, "chia_se_bai_minh": 5, "nhan_rieng_cho_minh": 5, "nhac_ten_minh": 4, "cung_lam_gi_do": 8},
  "len_thang": {"tra_loi_binh_luan_minh": "duoc_dap", "thich_binh_luan_minh": "duoc_dap", "theo_doi_lai": "duoc_dap",
                "binh_luan_bai_minh": "hai_chieu", "chia_se_bai_minh": "hai_chieu", "nhan_rieng_cho_minh": "hai_chieu",
                "nhac_ten_minh": "hai_chieu"}
 },
 "tieu_hoa_loai": ["insight", "y_tuong", "ve_nguoi", "trend", "ngon_ngu_cong_dong", "dieu_khong_lam"],
 "cam_xuc": ["buon_cuoi", "dong_cam", "to_mo", "ngac_nhien", "tu_hao", "hoai_niem", "bat_binh_chinh_dang", "nhe_nhom", "khao_khat", "xau_ho_de_thuong"],
 "phan_ung": ["thich", "chia_se", "tranh_luan", "luu", "binh_luan", "gan_ten_ban"],
 "tranh_luan": {"chu_de_cam": ["chính trị", "tôn giáo", "vùng miền", "giới tính", "sắc tộc", "y tế", "đầu tư tài chính", "chủ quyền"],
                "cho_phep_mau": ["cách làm việc", "công cụ", "thói quen", "lựa chọn nghề", "quan điểm sống thường ngày"]},
 "phien_mau": [
  {"ten": "Cà phê sáng: lướt và đọc", "gio": "07:40", "lech_phut": 25, "phut": 25,
   "buoc": [{"loai": "doc", "viec": "đọc 15-25 bài mới trong vòng và hashtag trụ cột"},
            {"loai": "trend", "viec": "đánh dấu 3 chủ đề đang lên"},
            {"loai": "cham", "viec": "thích/lưu bài thật sự đọc xong"}]},
  {"ten": "Nghỉ trưa: góp chuyện", "gio": "12:15", "lech_phut": 20, "phut": 20,
   "buoc": [{"loai": "doc", "viec": "đọc kỹ 5 bài của người trong vòng"},
            {"loai": "cham", "viec": "1-3 bình luận có chi tiết cụ thể"},
            {"loai": "hop_thu", "viec": "trả lời bình luận buổi sáng"}]},
  {"ten": "Chiều: tiêu hoá và tạo", "gio": "16:30", "lech_phut": 30, "phut": 30,
   "buoc": [{"loai": "tieu_hoa", "viec": "rút 2-4 ghi chú từ những gì đã đọc"},
            {"loai": "tao", "viec": "viết bài từ ghi chú tiêu hoá, chấm, đưa vào hàng duyệt"},
            {"loai": "vong", "viec": "thêm/bớt người trong vòng"}]},
  {"ten": "Tối: đăng và ở lại trò chuyện", "gio": "20:00", "lech_phut": 15, "phut": 40,
   "buoc": [{"loai": "tao", "viec": "đăng bài đã duyệt"},
            {"loai": "hop_thu", "viec": "ở lại 30 phút trả lời bình luận đầu"},
            {"loai": "doc", "viec": "đọc bài tối của vòng"},
            {"loai": "hoc", "viec": "ghi một dòng nhật ký nhân vật"}]}
 ]
}
```
