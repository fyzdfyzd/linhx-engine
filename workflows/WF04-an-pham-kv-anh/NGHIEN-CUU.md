# WF04 · Ấn phẩm, KV, ảnh: nghiên cứu nền (9/11)

## Kết luận
1. Skill LINHX (`thiet-ke` nhánh an-pham, `tach-kv`, `kiem-chu-anh`) đã đi xa hơn mọi skill ngoài tôi đọc được: ngoài chỉ có lời khuyên và vỏ gọi API, không có chấm mù, bản vàng, hay kiểm khổ thật.
2. Thiếu lớn nhất của LINHX là **máy đo chạy tự động**: `kiem_thiet_ke.py` chỉ kiểm có đủ tệp, chưa đo gì trên chính ảnh. Đề xuất 6 phép đo rẻ (bên dưới).
3. Chữ tiếng Việt: giữ luật "chữ dựng bằng font thật, không để AI vẽ" (cùng hướng với brand-social-design: "no AI gibberish"). `kiem-chu-anh` nên chạy bằng OCR + so chuỗi thay vì mắt, mắt chỉ soi lại.
4. Tách lớp: `tach-kv` yếu ở chữ đè lên ảnh. Có hai đường nâng cấp mã mở Apache-2.0: LayerD (chạy được CPU) và Qwen-Image-Layered (cần GPU). Chưa chạy thử, cần thử trên KV thật ở vòng 1.
5. Bản vàng: mới tải được 1 mẫu có giấy phép; còn lại là link, cần Linh/Claude máy cty tải thêm (xem Bản vàng).

## Quy trình đề xuất (giữ khung `thiet-ke`, bổ sung)
| Bước | Ai | Thêm so với skill hiện tại |
|---|---|---|
| D1 Brief | Claude | Khai hồ sơ brand trước (màu, font, cấm kỵ, logo file thật hay THAY-SAU). Mượn từ brand-social-design. Một câu "xem xong người ta phải làm gì" (skywork: mục tiêu giao tiếp) |
| D1 Tham chiếu | Claude | ≥8 tham chiếu người làm (đã có) + đặt bản mình cạnh bản vàng cùng khổ |
| D2 Ba hướng | Claude, Linh chọn | Giữ |
| D3 Dựng | agy | Chữ và logo dựng HTML/SVG, chụp Playwright ra PNG đúng px (thay nút html2canvas); ảnh AI chỉ làm nền/thành phần, qua `kiem-chu-anh` |
| D3b Tách lớp | agy | `tach-kv` (hoặc LayerD) + đo sai số ghép lại |
| D4 Chấm | Claude phiên mới, máy đo, Linh | Chạy máy đo 1–6 trước, rồi chấm mù. Luật canvas-design "chỉ tinh chỉnh, không thêm hình" cho vòng sửa cuối |

## Máy đo + ngưỡng (đề xuất; ngưỡng là của tôi đặt, chưa chạy thử, vòng 1 hiệu chỉnh)
| # | Phép đo | Cách chạy | Ngưỡng đạt |
|---|---|---|---|
| 1 | Chữ đúng | OCR (rapidocr, đã dùng trong `tach-kv`) trên vùng chữ, so với bảng chữ đúng; so từng dòng bỏ dấu cách | Chữ dựng bằng font: khớp 100% có dấu. Chữ AI vẽ: không được có (hoặc ghi THAY-SAU) |
| 2 | Tương phản chữ | Lấy màu chữ/nền từ nguồn HTML, tính tỉ lệ WCAG | ≥4,5:1 chữ thường, ≥3:1 chữ ≥ cỡ lớn |
| 3 | Đọc ở khổ xa | Thu còn 8% + mờ Gauss 4 px (đã có trong an-pham.md), OCR tiêu đề chính | Tiêu đề vẫn đọc ra; người chấm mù nói đúng "nhìn gì trước" |
| 4 | Vùng an toàn/tràn | Hộp chữ từ OCR so với lề | Mọi chữ cách mép ≥3% cạnh ngắn (cho pano/poster ≥ 5 mm tại khổ thật); tràn lề in 3 mm |
| 5 | Độ phân giải | Đếm px thật ÷ khổ in | ≥150 dpi ở khổ thật (đã có trong skill) |
| 6 | Tách lớp (nếu có) | Ghép lại các lớp, so ảnh gốc: sai số theo `tach-kv`; nếu dùng LayerD thì RGB L1 và Alpha soft IoU (https://github.com/CyberAgentAILab/LayerD/blob/main/docs/evaluation.md) | Sai số ghép lại trung bình thấp (ngưỡng đặt sau khi thử 3 KV thật) |
| 7 | Chấm mù | 3 người chấm không đọc lý do thợ, 16+5 tiêu chí (đã có) | ≥85 điểm; ≥2/3 đoán "AI làm" thì trượt (đã có) |
| 8 | Luật ảnh Linh | Danh sách 7 luật, soi 100% | Không lỗi nặng (tay, chữ giả, watermark, dấu sao Gemini) |
Phép đo 1 là thay đổi có giá trị nhất: ảnh AI hay sai dấu tiếng Việt, mắt dễ bỏ sót.

## Bản vàng
| Mẫu | Link | Vì sao tốt | Tình trạng |
|---|---|---|---|
| Josef Müller-Brockmann, "der Film" (1960, Kunstgewerbemuseum Zürich) | https://commons.wikimedia.org/wiki/File:Josef_M%C3%BCller-Brockmann_der_Film.jpg | Một chủ thể (chữ), nền tối trống chiếm 2/3, 2 màu phụ, chữ chồng lớp tạo chiều sâu, thông tin phụ nhỏ cùng trục lề trái. Đúng luật ảnh Linh | **Đã lưu** `vang/muller-brockmann-der-film.jpg`. Commons ghi "Public domain" (kiểm lại bản quyền theo luật nước dùng trước khi in lại, tôi không xác minh được) |
| Poster House, bộ sưu tập mở | https://collection-open.posterhouse.org/ | Kho poster có ghi nguồn | [chỉ thấy], chưa chọn mẫu |
| Artvee "viet poster" (tranh cổ động Việt, ghi miền công cộng) | https://artvee.com/dl/viet-poster-1 | Tham chiếu ngữ pháp màu phẳng, chữ to của tranh cổ động Việt | [chỉ thấy] |
| Rice Creative (HCM): ZEROawards UNICEF | https://a-g-i.org/design/unicef-zero-awards-1 | Studio Việt giải quốc tế, mốc cho KV hiện đại có chất Việt | [chỉ thấy], ảnh có bản quyền: chỉ dẫn link, không tải |
Cần thêm 2 mẫu **KV hội thảo công nghệ** và **pano sự kiện** do người làm nghề thật làm; chưa tìm được mẫu có giấy phép. Việc cho Claude máy cty/Linh duyệt: chọn từ Behance/Dribbble (chỉ lưu link + ghi tác giả).

## Sửa vào skill nào, sửa gì
- `thiet-ke/scripts/kiem_thiet_ke.py` (pha d4, nhánh an-pham): thêm phép đo 1–5 trên ảnh thật (hiện chỉ kiểm tệp). Đây là sửa chính.
- `thiet-ke/references/an-pham.md`: thêm mục "Hồ sơ brand khai trước", "cấm thêm hình ở vòng sửa cuối" (canvas-design), cỡ chuẩn social (1080×1080, 1200×630, 1080×1920 theo brand-social-design), thử "tầm tay/2 m" (Better Posters).
- `kiem-chu-anh/SKILL.md`: thêm bước 3b chạy OCR so chuỗi trước khi soi mắt; ghi kết quả JSON.
- `tach-kv/SKILL.md`: mục "đường nâng cấp" ghi rõ LayerD (Apache-2.0, CPU được) là thử đầu tiên, Qwen-Image-Layered nếu có GPU; cần thử trước khi đổi.
- Không sửa: chống mùi AI, 7 luật ảnh, chấm mù, ngân sách chữ: ngoài không có gì tốt hơn.

## Rủi ro
- Ngưỡng ở trên chưa có số thật; phải hiệu chỉnh ở vòng 1 trên đề CSMO.
- OCR tiếng Việt có dấu có thể sai khi chữ cách điệu; dùng cho chữ dựng bằng font, không dùng làm án cho chữ nghệ thuật.
- Chưa đọc được open-design (clone lỗi) và poster-designer (410); chưa có nguồn tiếng Trung/Facebook VN; chưa viết đề Deep Research. Gợi ý DE-1: "quy trình và tiêu chí chấm của studio/agency thiết kế KV sự kiện công nghệ ở Việt Nam và Đông Nam Á", nên chạy nếu vòng 1 cần tiêu chí studio.
- LayerD/Qwen chưa chạy thử; không kết luận chất lượng với chữ tiếng Việt.

## Nguồn
[đọc] https://github.com/anthropics/skills (canvas-design) · https://github.com/omrajguru05/brand-social-design · https://github.com/SkyworkAI/Skywork-Skills (skywork-design/scenarios/poster.md) · https://github.com/CyberAgentAILab/LayerD · https://github.com/QwenLM/Qwen-Image-Layered · https://betterposters.beehiiv.com/p/is-it-big-enough-the-arms-length-10-01-07 · https://dev.to/omrajguru05/i-built-a-claude-skill-to-automate-brand-consistent-social-graphics-html-to-pngthe-backstory-2ld7 · https://commons.wikimedia.org/wiki/File:Josef_M%C3%BCller-Brockmann_der_Film.jpg
[chỉ thấy] https://claudemarketplaces.com/skills/nexu-io/open-design/image-poster · https://openskillindex.com/skills/openclaw-skills-poster-designer · https://www.creativebloq.com/posters/4-rules-visual-hierarchy-poster-design-91516904 · https://collection-open.posterhouse.org/ · https://vietcetera.com/en/rice-creative-meet-the-team-setting-design-standards-in-vietnam · https://artvee.com/dl/viet-poster-1
