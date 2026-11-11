# LOG: LABNNN

<!-- Mỗi mục: thời gian, đã thử gì, kết quả, lỗi và cách sửa. Mới nhất ở dưới. -->

## YYYY-MM-DD HH:MM
- Thử:
- Kết quả:
- Ghi chú:

## 2026-11-11 06:55 (MSI)
- Thử: lấy bộ chuẩn từ repo linhx-engine nhánh claude/project-thread-2m7vtb (viec/brand-id-4bu) vào `chuan/`. BRAND\ trên MSI thiếu, không ghi vào đó.
- Kết quả: G0 Unikon `UNIKON/00-goc/CORE-VALUE.md` nguyên văn từ GE PROPOSAL 2021 slide 11 và Credentials 2025 slide 6, 10–11. Giá trị cốt lõi: chưa có trong tài liệu.
- Ghi chú: cungai ĐÃ có logo gốc `nguon-logo-linh-19-10/cung ai/aida_cungai_logo.ai` + bản có pattern, trái với đề "chưa có logo". Hỏi Linh.

## 2026-11-11 07:40 (MSI)
- Thử: giao agy G1 (đề `.handoff/tasks/T-G1-UNIKON.md`, `T-G1-SAKEDEMY.md`). `--dangerously-skip-permissions` bị bộ lọc của Claude chặn; chạy không cờ thì agy tự từ chối lệnh "command" ở chế độ headless → 0 kết quả.
- Kết quả: dựng `src/unikon_g45.py` (Playwright + Edge, font Montserrat gốc), ra 4 PNG: Về thương hiệu, Tinh thần (Unique × Mass scale, chữ nguồn tầm nhìn 2021), 3 pattern (A Vành khuyết ★, B Tia sừng, C Dải phổ) trên 3 nền, CHO-CHOT.png. Soát mắt: sửa trang Tinh thần trống nửa dưới.
- Ghi chú: màu đo từ stop-color logo gốc, không có đỏ #BC002D. Chờ Linh chốt 1–4 và cách chạy G1.

## 2026-11-11 08:10 (MSI)
- Thử: G0 Sakédemy từ PDF "Sakedemy_đào tạo doanh nghiệp.pdf" (tr.3–4) + OVERVIEW hồ sơ; dựng `src/sakedemy_g45.py` (màu file gốc #1CA571 #23B7AC #66BC66 #A3D34F, rêu #02403B; script tự chặn màu hồng/đỏ).
- Kết quả: 4 PNG Sakédemy (Về thương hiệu, Tinh thần Sáng tạo × Công nghệ, 3 pattern lá A Gân lá ★ / B Lá vuông / C Lá rơi, CHO-CHOT). Soát mắt: dời nội dung trang 1 xuống cho khỏi trống đáy.
- Ghi chú: Unikon đã báo thread lúc ~07:45, chưa có trả lời của Linh.

## 2026-11-11 08:35 (MSI)
- Linh chốt Unikon (qua coordinator): 1B định vị Sub-Agency; tagline "Agentic content at mass scale"; 2A 3A 4A đi theo ★ chưa duyệt; G1 Linh tự chạy agy; logo cungai coi như đã chốt.
- Kết quả: sửa `src/unikon_g45.py` (trang Về thương hiệu, Tinh thần Agentic × Mass scale, chờ chốt), dựng `src/unikon_g5v2.py` → `UNIKON/05-pattern/G5-pattern-vong2.png` (A1 Lưới vành ★, A2 Vành xoay, A3 Vành lớn; 3 nền + bài 1:1 + bìa 16:9, logo ở vùng trống).
- Sakédemy: G0 + G4 + G5 vòng 1 + CHO-CHOT xong (xem mục 08:10).

## 2026-11-11 09:05 (MSI)
- Linh nhắn lại "1B Agentic content at mass scale" (đã áp từ trước). Unikon 2A 3A 4A + vòng 2 A1, Sakédemy 1A 2A 3B 4A: đi theo ★, chưa duyệt.
- TUVA: G0 từ TUVA_Credentials.pdf (2022, tr.5–8) + DATA/01_COMPANY_PROFILE.md; dựng `src/tuva_g45.py` (nâu #2A1F1B, cam #FAA71B, mọi hoạ tiết xoắn logarit); 4 PNG + CHO-CHOT.md. Tự soát: C Xoắn lớn dễ trông như vòng đồng tâm, đã ghi chú.

## 2026-11-11 09:50 (MSI)
- Áp chốt Linh 06:59 (Unikon vòng 2 A1 duyệt; Sakédemy 1A hai nhóm, 2A, định vị AI là nhánh phụ, Gân lá signature) và 07:01 (TUVA 1A, hỏi vế decent AI, REACHING OUT thêm nghĩa công nghệ, Sóng xoắn duyệt).
- Kết quả: sửa trang G4 Sakédemy và TUVA; dựng `src/sakedemy_g5v2.py`, `src/tuva_g5v2.py` (3 option × 3 nền + bài 1:1 + bìa 16:9); trang gộp `output/CHO-CHOT-GOP.png` (`src/cho_chot_gop.py`): S3 S5 T2 T3 T5.
- Ghi chú: T2, T3 là đề xuất mới, ghi rõ không phải lời nguồn.

## 2026-11-11 10:20 (MSI)
- Linh: "5 tôi đang làm rồi" (đang chạy agy G1 Unikon, tracklog .handoff/logs/T-G1-UNIKON-20261111-0658.md); "6 a" (logo cungai coi như đã chốt).
- Viết đề `.handoff/tasks/T-G1-TUVA.md`, `T-G1-CUNGAI.md`; thêm dòng CẤM sửa CHO-CHOT/CORE-VALUE/tệp ngoài 01-tham-chieu vào cả 4 đề. Kiểm: agy chưa sửa UNIKON/CHO-CHOT.md.
- G0 cungai: `CUNGAI/00-goc/CORE-VALUE.md` từ Claude Doc "cungai.vn · Plan 5 năm" (mục 0, 1) + OVERVIEW Cùng AI của Sakédemy. 3 câu hỏi: cách viết tên, câu định vị, giá trị cốt lõi.

## 2026-11-11 (MSI, sau khi lên lại)
- Linh chốt cungai 07:36: C1A "cungai" chữ thường; C2B định vị "Sống cùng AI"; C3 Claude tự viết giá trị (3 bộ, ★A) → CORE-VALUE.md mục 5–6.
- G4 + G5 vòng 1 cungai xong (`src/cungai_g45.py`), CHO-CHOT C3 C4.

## 2026-11-11 10:40 (MSI)
- Linh 10:35: "ghi vào kho brand ssi unikon vành lớn / tuva chỉ để 1 bên sóng / còn đâu ok rồi triển khai đi" → Unikon A3; TUVA B2 sóng một bên; S3A S5A2 T2C T3A T5B2 C3A C4A duyệt. Ghi vào CORE-VALUE 4 BU.
- `src/chot_pattern.py` → `<BU>/05-pattern/PATTERN-CHOT.png` (3 nền + bài 1:1 + bìa 16:9). `tuva_g5v2.py` B2: 4 hàng sóng ở nửa dưới.
