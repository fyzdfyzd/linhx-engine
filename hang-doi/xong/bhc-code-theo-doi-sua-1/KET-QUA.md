model: gemini-4-argon-high
phieu: bhc-code-theo-doi-sua-1
may: may-2
trang_thai: xong
tep_doi: KET-QUA.md, bang-chung/bhc-theo-doi/quan-tri-1280.png, bang-chung/bhc-theo-doi/quan-tri-360.png, bang-chung/bhc-theo-doi/so-sanh-1280.png, bang-chung/bhc-theo-doi/so-sanh-360.png, theo_doi/00-fetch.log, theo_doi/00-npm-ci.log, theo_doi/test-lap.log, theo_doi/verify.log, xong/ev-anh-ly-12f/ly-ngan...
drive: G:\My Drive\LINHX-VIEC\bhc-code-theo-doi-sua-1\xong\ev-anh-ly-12f\ly-ngang.jpg
phut: 16.24
token: vao=192484 ra=36134

Đang chạy `npm.cmd run verify` và chờ kết quả hoàn tất.
Đang chạy `npm.cmd run test:lap` (5 vòng E2E liên tiếp) và chờ kết quả hoàn tất.
Đã hoàn thành sửa lỗi trang so sánh 2 kỳ trên nhánh `agy/bhc-theo-doi` (`19457bc22584a5476454d06242d54b4292bd5c8a`):

1. **Sửa thuật toán so sánh** trong [so-sanh.js](file:///C:/linhx/ifagent-wt/bhc-theo-doi/apps/brand-health/server/lib/so-sanh.js#L82-L195):
   - Chuẩn hoá `tomTatTrangThaiCau()` để chữ ký `sig`, `trangThai`, `soLuot` và `score` bám sát trạng thái nhận định (`topVerdict`) và số lượt hiển thị (`nenChon/tong` hoặc `nhac/tong`).
   - Làn không đổi trạng thái lẫn số lượt (`stNay.sig === stTruoc.sig || stNay.moTa === stTruoc.moTa || (stNay.trangThai === stTruoc.trangThai && stNay.soLuot === stTruoc.soLuot)`) bị bỏ qua hoàn toàn: không hiện trong phần 03, không cộng vào `"Đổi ý N câu"` ở phần 02.
   - Câu chỉ có các làn không đổi (`!troLyDoi.length`, như câu `D1`) bị bỏ khỏi danh sách `cauDoiY` và không cộng vào tổng số câu đổi ý trong câu nhận định tổng hợp (`ta
...[cat bot]...
file`, `104 tests (100 pass, 0 fail, 4 skip)`.
   - `npm.cmd run test:lap`: `5/5 lần xanh (11 ca mỗi lần, 0 chập chờn)`.
   - Ảnh chụp mới: [so-sanh-1280.png](file:///C:/linhx/ifagent-wt/bhc-theo-doi/bang-chung/bhc-theo-doi/so-sanh-1280.png), [so-sanh-360.png](file:///C:/linhx/ifagent-wt/bhc-theo-doi/bang-chung/bhc-theo-doi/so-sanh-360.png).
   - Báo cáo kết quả: [KET-QUA.md](file:///C:/linhx/hang-doi/runner/viec/lam-viec/KET-QUA.md).
