---
name: research-write
description: Viết bài báo từ kết quả research-loop theo thứ tự chứng cứ trước, lời sau - chuẩn bị đầu vào, cổng người duyệt, viết, phản biện độc lập. Dùng khi người nói "viết bài từ kết quả", "viết manuscript", "chuẩn bị bản thảo Q1".
metadata:
  version: "0.1.0"
---

# Research write (bước 6, sau research-loop)

Khuôn từ quy trình 8 subagent + điều phối (bài chia sẻ 4/11), rút còn 5 vai vì 3 việc đã làm bằng code. `KB=scripts/kiem_bai.py`, `D=<thư mục bài>`.

## A. Chuẩn bị (agent làm, chưa viết chữ nào của bài)
1. **Tài liệu** → `D/evidence.tsv` cột `khoa doi pmid nguon cau_ho_tro`. Mỗi dòng có DOI/PMID và câu gốc trích nguyên văn. Lấy từ idea bank + `doc-them.md` của research-loop rồi tìm thêm (PubMed cho y sinh, OpenAlex/arXiv cho ML). Thêm cột `khoang_trong` cho research gap.
2. **Phương pháp** → `D/lech-ke-hoach.md`: đối chiếu `program.md` (kế hoạch) với `git log` + `nhat-ky.tsv` (thực tế). Liệt kê mọi lệch: đổi lệnh đo, sửa file ngoài phạm vi, thiếu seed.
3. **Kết quả** → `D/ket-qua.md`: bảng số duy nhất của bài, chép từ `nhat-ky.tsv`/output, **kể cả số phái sinh** (% chênh, CI). Không số nào được sinh ở bước sau.

## B. Cổng người (dừng, bắt buộc)
Người đọc 3 file trên, sửa, ghi `DUYET <ngày>` vào đầu `ket-qua.md`. Chưa có dòng này thì không sang C.

## C. Viết (một agent, hai lượt)
1. Mở bài, Phương pháp, Kết quả: chỉ dùng 3 file đã duyệt. Mọi câu nhắc y văn có `[@khoa]`.
2. Bàn luận (lượt riêng, đầu tư nhất): mỗi phát hiện chính → giống/khác y văn nào → giải thích → hạn chế. Gắn nhãn `[DU_LIEU]` cho điều dữ liệu đỡ, `[GIA_THUYET]` cho điều chưa kiểm.

## D. Phản biện độc lập (không thấy suy nghĩ của người viết, chỉ thấy bản thảo + 3 file đã duyệt)
1. **Máy đo trước, 0 token** (chặn cứng):
   - `python KB so D/ban-thao.md D/ket-qua.md` : số lạ = bịa hoặc phái sinh chưa vào bảng.
   - `python KB trich D/ban-thao.md D/evidence.tsv --mang` : trích bịa, thiếu mã, DOI/PMID không tồn tại. Chạy máy có mạng (cloud chặn Crossref/PubMed).
2. **Đọc trích dẫn** (LLM): với mỗi `[@khoa]`, câu trong bài có đúng ý `cau_ho_tro` không.
3. **Thống kê** (nên dùng model khác, ví dụ Gemini): effect size, CI, p, multi-seed; câu nào kết luận vượt thiết kế.
4. **Biên tập**: mạch lập luận, author guidelines, checklist báo cáo (STROBE/CONSORT/PRISMA cho y sinh; checklist tái lập NeurIPS cho ML).

## E. Điều phối tổng hợp → `D/CAN-TAC-GIA-QUYET.md`
Gộp phiếu, ghi chỗ các vai mâu thuẫn, ≤10 việc tác giả phải quyết, mỗi việc trỏ dòng. Sửa theo phiếu, chạy lại D1, tối đa 3 vòng.

## Luật cứng
- Không viết trước rồi tìm nguồn hợp lý hoá.
- Người phản biện không đọc lời giải thích của người viết.
- Máy đo D1 trượt thì không đưa bài cho người đọc.
