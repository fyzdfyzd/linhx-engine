# Trích xuất để lượng hoá (ẩn dụ, số liệu, chuyện, chủ thể)

Bạn là người trích dữ liệu, không chấm hay dở. Đọc bài, đánh số đoạn văn xuôi từ 1 (bỏ tít, sapo in nghiêng, dòng tác giả, bảng, dòng nguồn, hộp "Bài này nói gì"). Trả về **một khối JSON duy nhất** theo khuôn dưới. Mọi trường `trich` phải chép **nguyên văn** từ bài (để máy dò lại), ngắn nhất đủ nhận ra, tối đa 15 chữ.

```json
{
  "so_doan": 0,
  "an_du": [
    {"trich": "…", "hinh": "tên hình ảnh, 1-3 chữ, vd: tab trình duyệt", "doan": [3, 6, 9]}
  ],
  "so_lieu": [
    {"trich": "…", "doan": 4, "loai": "số|tên nghiên cứu/tổ chức|trích lời", "y_no_do": "câu luận điểm nó đỡ, chép nguyên văn; null nếu không có câu nào dựa vào nó", "nhac_lai_o_doan": []}
  ],
  "chuyen": [
    {"doan": [1, 2], "nhan_vat": "…",
     "neo": {"ten_rieng": 0, "noi_chon": 0, "moc_thoi_gian": 0, "loi_thoai_nguyen_van": 0, "chi_tiet_giac_quan": 0, "con_so_doi_thuong": 0},
     "cau_tom_tat": 0, "so_cau": 0}
  ],
  "chu_the": [
    {"trich": "…", "doan": 5, "chu_the": "…", "co_ten": true}
  ],
  "phai_nho": [
    {"doan": 7, "can_nho_tu_doan": 3, "cai_gi": "…"}
  ],
  "thuat_ngu": [
    {"tu": "…", "doan_dau": 2, "giai_nghia_o_lan_dau": false}
  ]
}
```

Định nghĩa:
- **an_du**: hình ảnh không nói theo nghĩa đen (so sánh, ẩn dụ, nhân hoá) mà tác giả dựng lên. Cùng một hình ảnh dùng lại ở đoạn khác thì gộp vào một mục, liệt kê mọi đoạn có nó. Thành ngữ, tục ngữ quen thuộc không tính.
- **so_lieu**: mỗi con số, tên nghiên cứu, tổ chức, báo cáo, hoặc lời trích của người ngoài đưa vào làm bằng chứng. `y_no_do` là câu trong bài dùng nó để nói một điều; nếu số chỉ đứng đó, không câu nào dựa vào, ghi null. `nhac_lai_o_doan`: các đoạn sau nhắc lại đúng số hoặc nguồn ấy.
- **chuyen**: một chuyện kể về người cụ thể (kể cả tác giả). Đếm số lần mỗi loại neo xuất hiện trong chuyện. `cau_tom_tat`: câu kể lại bằng khái quát, không có cảnh (vd "anh mệt lắm", "cậu kể đủ thứ"). `so_cau`: số câu của chuyện.
- **chu_the**: mỗi câu khẳng định một sự việc hay quan điểm mà gán cho một chủ thể bên ngoài tác giả (chính phủ, chuyên gia, nghiên cứu, người ta, giới…). `co_ten` true khi đọc xong biết chính xác là ai (tên người, tên cơ quan, tên nghiên cứu).

- **phai_nho**: đọc như một người ngoài ngành đọc báo. Với mỗi đoạn, người ấy phải nhớ điều gì từ một đoạn trước (không liền kề) mới hiểu được đoạn này: một hình ảnh, một tên gọi tác giả tự đặt, một con số, một nhân vật được gọi tắt. Mỗi điều phải nhớ một mục.
- **thuat_ngu**: từ viết tắt, từ chuyên ngành, từ tiếng Anh mà người đọc báo phổ thông có thể không biết. `giai_nghia_o_lan_dau` true nếu ngay lần đầu có giải thích.

Không thêm lời bình. Không bỏ sót: thà liệt kê thừa một mục còn hơn thiếu.
