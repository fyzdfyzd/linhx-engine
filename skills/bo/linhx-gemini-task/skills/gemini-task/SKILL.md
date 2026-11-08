---
name: gemini-task
description: Giao việc cho Gemini Task (Gemini Ultra, chế độ Nhiệm vụ, model Argon) thay vì tự làm bằng token Claude. Dùng mỗi khi việc là nghiên cứu web diện rộng, gom dữ liệu nhiều nguồn, dựng kho CSV/SQLite, chạy dài nhiều giờ, dựng PDF/ảnh/GIF/MP4/PPTX hàng loạt, hoặc khi Linh nói "giao Gemini", "thả đề Gemini", "dùng Argon", "Gemini Task".
---

# Giao việc cho Gemini Task

Linh có gói **Gemini Ultra** trả phí cố định trên tài khoản **Art Urah** (`gemini.google.com/u/1`). Chỉ tài khoản này có chế độ **Nhiệm vụ** và model **Argon**; tài khoản mặc định tuanlinh@chiemtinh.vn thì không. Mỗi nhiệm vụ không tốn token Claude, chỉ trừ hạn mức của gói. Ngày 17/10/2026, 8 nhiệm vụ chạy song song không gặp giới hạn hay CAPTCHA. Vì vậy **mặc định là giao Gemini mọi việc giao được**; Claude giữ phần cần phán đoán.

## Chia việc
| Giao Gemini | Claude giữ |
|---|---|
| Quét web nhiều nguồn, lập danh mục, đọc sitemap | Quyết định làm gì, viết đề |
| Dựng kho CSV/SQLite có nguồn, tóm ý hàng trăm trang | Chấm kết quả, gộp vào kho chung |
| Việc dài nhiều giờ, lặp đệ quy tới bão hoà | Việc cần file, tài khoản, phần mềm trên máy Linh |
| Dựng PDF, ảnh, GIF, MP4, PPTX hàng loạt bằng code | Việc cần sửa repo, mở PR |
| Prototype nhỏ chạy bằng Python/Node có sẵn | Chạy test thật, kiểm URL mẫu, đọc dòng ngẫu nhiên |

Việc lớn thì **tách thành nhiều nhiệm vụ song song** (theo lăng kính, theo ngách, theo nguồn), mỗi nhiệm vụ một mã riêng.

Không giao: dữ liệu cá nhân của khách, mật khẩu, tài liệu mật, việc cần đăng nhập trang khác hay vượt paywall.

## Vòng 6 bước
Script: `python "${CLAUDE_PLUGIN_ROOT}/scripts/gt.py" <lệnh>`. Trên máy Linh, thư mục nhiệm vụ là `<thư mục LAB>/argon/<MÃ>/`; sổ chung ở `D:/LINHX/LAB/GEMINI-TASK/so-nhiem-vu.jsonl`.

1. **Viết đề.** `gt.py moi <thư mục LAB> <MÃ> --loai quet|dai|media|code --muc-tieu "..."` tạo `DE.txt` từ khuôn (`templates/khuon-de.txt`), `yeu-cau.json`, `CHAY.md`. Điền đủ 7 phần của khuôn: vai và mục tiêu, luật, cấu trúc thư mục cố định, các pha có đích đếm được kèm checkpoint zip, tự kiểm, nối lượt, đầu ra cuối. Sửa `yeu-cau.json` cho khớp tên file, cột, số dòng tối thiểu mà đề đòi. Đề mẫu tốt: `references/de-mau.md`.
2. **Gửi.** Theo skill `gemini-gui`. Đề ngắn thì Claude gửi. Đề "chạy tự do cả đêm" có thể bị bộ lọc quyền trên máy chặn; khi đó đưa Linh file và đường dẫn để Linh dán (khoảng 1 phút). Ghi `gt.py gui <thư mục> --link <URL>`.
3. **Chờ.** Không canh, không poll. Argon tự lập kế hoạch và chạy; Linh nhắn khi xong, hoặc hẹn giờ quay lại kiểm.
4. **Lấy về và chấm.** Theo skill `gemini-lay-cham`.
5. **Gộp.** Đưa dữ liệu đạt chuẩn vào kho của lab, ghi điểm Argon vào `CHAM.md`, `gt.py trang-thai <thư mục> da-cham`.
6. **Đề tiếp.** Nếu có `TIEP-THEO.md` thì viết lượt sau từ đó, đính kèm zip lượt trước.

## Luật viết đề (rút từ lỗi thật 17/10)
- Luôn chèn khối "Thực tế máy" (`templates/may-argon.txt`), hoặc gọi Skill `@linhx-nhiem-vu` nếu đã cài trong Gemini (xem skill `gemini-skill`). Bash trong máy Argon không ra mạng, không cài được thư viện, không có pytest.
- Đòi câu trọn vẹn; cấm cắt theo số chữ. Lượt đầu 296/413 đoạn bị cắt cứng ở 76 chữ.
- Đòi mọi số trong tổng kết do script đếm. Lượt đầu hứa 35 trang, thực tế 3–8.
- Đòi ghi kết quả ra file và zip. Kết quả chỉ nằm trong canvas thì không lấy được.
- Đòi URL gốc trong CSV, không dán URL trong bảng markdown vì Gemini bọc thành `google.com/search?q=`.
- Định nghĩa rõ từng khái niệm đếm (ví dụ "sản phẩm đang bán" khác "trang tài liệu").
- Viết đề bằng tiếng Việt, đủ ý, không cần ngắn: Argon đọc hết.

## Báo Linh
Một câu cho mỗi nhiệm vụ: đã gửi hay chưa, link, việc Linh cần làm (thường là không gì). Khi chấm xong: điểm, cái dùng được, cái phải chạy lại.
