may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-quan-tri
nhan: may-2 2026-11-17T11:23:54+0700
moc: c8c7321e1acad043ad7d9376615d045cca173edb

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Server chạy bằng Start-Process, tắt đúng PID.
LUẬT: commit + push ít nhất mỗi 10 phút (WIP cũng được). Commit đầu tiên trong 5 phút.
Quản trị phần B, worktree C:\linhx\ifagent-wt\bhc-quan-tri, nhánh agy/bhc-quan-tri (đỉnh c8c7321, git pull trước).
0. `git merge --no-edit origin/agy/bhc-on-dinh` (cửa chặn AI giả + test:lap + lint cấm delayMs). Push.
1. Menu khi đã đăng nhập: bỏ mục "01 · Đăng nhập", thêm nút "Đăng xuất" (xoá phiên).
2. Màn Chi tiết lượt: sửa bảng sự thật (lưu), "Chấm lại" theo sự thật mới (không hỏi AI lại, điểm đổi theo), "Quét lại" (lượt mới vào hàng đợi), Xuất bản / Ẩn báo cáo (ẩn thì /bao-cao/<mã>/ trả trang "Báo cáo chưa công khai", HTTP 404, noindex).
3. Màn Lead: danh sách, lọc đồng ý có/không, tải CSV, nút "Gửi sang đội event" chỉ ghi trạng thái + thời điểm.
4. Màn Cài đặt: trần lượt/IP, trần lượt/ngày, trần chi phí/ngày, bật/tắt từng làn mô hình, quét nhanh/đầy đủ; lưu data/cai-dat.json, áp dụng ngay.
5. E2E (dùng cửa chặn, không chờ thời gian): sửa sự thật → chấm lại đổi điểm; ẩn → khách thấy chưa công khai; cài trần lượt/ngày = 1 → lượt thứ 2 bị chặn ngay; đăng xuất → API 401. `npm.cmd run test:lap` 5/5 và `npm.cmd run verify` xanh.
6. Ảnh 1280 + 360 cho chi tiết, lead, cài đặt trên app thật vào bang-chung/bhc-quan-tri/, ghep-1280.png đủ 6 màn.
CẤM: deploy, gọi AI thật, in mã quản trị/khoá, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; E2E phần B; test:lap; verify.

nhip: 11:36 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
