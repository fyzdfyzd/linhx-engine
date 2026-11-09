---
name: tra-cuu-luat
description: Tra cứu văn bản pháp luật Việt Nam mới nhất về một chủ đề (mặc định luật đất đai, bất động sản) bằng Chrome của Linh, rồi ghi chú tiếng Việt có link nguồn, ngày ban hành, ngày hiệu lực, điểm mới và ý nghĩa với doanh nghiệp. Dùng khi Linh nói "tra luật", "cập nhật luật đất đai", "tìm quy định mới nhất về …", hoặc cần nền pháp lý cho demo, bài giảng (vd Vinhomes).
metadata:
  version: "0.1.0"
---
# Tra cứu luật mới nhất và ghi chú

Mục tiêu: một file ghi chú đọc 30 giây là biết luật nào đang áp dụng, cái gì sắp đổi, và ảnh hưởng gì. Mọi ý đều có link nguồn và ngày.

## Đầu vào
- **Chủ đề**: mặc định "luật đất đai". Có thể là nhà ở, kinh doanh BĐS, thuế, đầu tư…
- **Mốc thời gian**: mặc định "đến hôm nay".
- **Góc nhìn**: ai đọc (vd chủ đầu tư BĐS như Vinhomes, người mua nhà, học viên).
- **Nơi lưu**: thư mục dự án đang làm. Không rõ thì ghi vào `00-INBOX/` và hỏi Linh.

## Bản nền
Nếu chủ đề là đất đai, đọc trước `references/nen-luat-dat-dai-2026-11.md` (bản ghi 03/11/2026). Chỉ tìm cái **mới hơn** bản nền và kiểm các mục "việc cần theo dõi" ở cuối bản đó. Không tra lại từ đầu.

## Các bước
1. **Mở Chrome** (Claude in Chrome). Nạp công cụ một lần: `tabs_context_mcp, navigate, computer, get_page_text, find, javascript_tool, browser_batch, tabs_close_mcp`. Làm trong tab mới của nhóm MCP.
2. **Tìm trên Google**, ba lượt:
   - `<chủ đề> mới nhất <năm>` để lấy bài tổng hợp (LuatVietnam, Thư Viện Pháp Luật).
   - `<chủ đề> sửa đổi Quốc hội kỳ họp` với `&tbs=qdr:m` (trong tháng) để biết dự luật đang bàn.
   - Tên từng nghị quyết, nghị định mới để lấy ngày ban hành và hiệu lực.
   Lấy link kết quả bằng JS: `[...document.querySelectorAll('a h3')].map(h=>h.innerText+' -> '+h.closest('a').href)`.
3. **Đọc bài**. Thứ tự tin cậy: văn bản gốc (congbao.chinhphu.vn, vbpl.vn, chinhphu.vn) > quochoi.vn, cổng bộ ngành > báo lớn (VTV, Vietstock, VnExpress) > LuatVietnam, Thư Viện Pháp Luật > Facebook, YouTube (chỉ để gợi ý, không dẫn nguồn).
4. **Ghi chú** theo khung bên dưới. Tách rõ **đang có hiệu lực** và **dự thảo, chưa thông qua**.
5. **Tự kiểm**: mỗi văn bản có số hiệu, ngày ban hành, ngày hiệu lực, link. Ý nào chỉ thấy ở đoạn trích Google hoặc lấy từ hiểu biết sẵn có thì liệt kê ở mục "Độ tin cậy" cuối file.
6. **Đóng tab** đã mở. Lưu file, gửi Linh, trả lời ngắn: 3 ý chính và những điểm chưa kiểm.
7. Nếu chủ đề là đất đai: chép bản mới đè `references/` của skill này (sửa ở `_system/skills/`, chạy `_system/sync-skills.ps1`), giữ bản cũ trong `references/_archive/`.

## Mẹo trình duyệt (đã gặp)
- **thuvienphapluat.vn** hiện trang Cloudflare "Just a moment". Chờ 4 giây là qua; không bấm captcha. `get_page_text` hay lấy nhầm form đăng ký, nên đọc bằng JS.
- **Kết quả JS bị cắt khoảng 1.000 ký tự.** Lưu chữ vào `window.__t` rồi đọc từng đoạn 1.000 ký tự trong một `browser_batch`:
  ```js
  const h=document.querySelector('h1'); const t=document.body.innerText;
  window.__t=t.slice(Math.max(0,t.indexOf(h?h.innerText.trim():''))); window.__t.slice(0,950)
  ```
  rồi `window.__t.slice(950,1950)`, `slice(1950,2950)`…
- **luatvietnam.vn, vietstock.vn, vtv.vn, quochoi.vn** đọc thẳng được, chờ 2 giây sau khi mở.
- Cuối bài LuatVietnam có "Tin liên quan" dẫn tới bài điểm mới của từng nghị định: lấy link bằng JS lọc `a` theo số hiệu.

## Khung ghi chú
```markdown
---
type: note
status: draft
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
# <Chủ đề>: cập nhật đến DD/MM/YYYY
(Tra ở đâu, ngày nào; câu "ghi chú tham khảo, không phải ý kiến pháp lý")

## 1. Tóm tắt 30 giây        (3–4 gạch đầu dòng)
## 2. Văn bản đang có hiệu lực (bảng: văn bản | ban hành | hiệu lực | ghi chú; luật trước, nghị định sau)
## 3. Điểm mới chính          (đánh số, mỗi điểm nói rõ điều khoản)
## 4. Dự thảo đang bàn        (tiến trình, ngày biểu quyết dự kiến, điểm đề xuất, điểm còn tranh luận)
## 5. Ý nghĩa với <người đọc>
## 6. Việc cần theo dõi tiếp  (có mốc ngày)
## Nguồn                      (tên bài, nơi đăng, ngày, link)
Độ tin cậy: những gì chưa mở văn bản gốc để kiểm.
```

## Luật viết
- Tiếng Việt có dấu, câu ngắn. Ngày dạng `DD/MM/YYYY` trong bài.
- Không bịa số hiệu, ngày. Không chắc thì ghi "chưa kiểm".
- Không dẫn Facebook, YouTube, trang chính trị đối lập làm nguồn.
- Tóm tắt bằng lời mình, không chép nguyên đoạn dài từ bài báo.
