may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: C:\linhx\ifagent-wt\yl-test-a6-c
phu_thuoc: yl-khoa-t1
nhan: may-2 2026-11-15T14:12:42+0700

LƯỢT 3 (hai lượt trước đều bị dừng ở phút 40 vì agy đưa lệnh ra chạy nền rồi ngồi chờ): (1) worktree C:\linhx\ifagent-wt\yl-test-a6-c đã có thì DÙNG LẠI, không tạo lại; đọc git status xem lượt trước làm tới đâu. (2) Mỗi lệnh test bọc trong PowerShell: `$p = Start-Process node -ArgumentList '--test','--test-timeout=120000','<file>' -NoNewWindow -PassThru -Wait` là SAI; hãy gọi thẳng `node --test --test-timeout=120000 <file> 2>&1 | Tee-Object bang-chung\log-<ten>.txt` và đợi lệnh trả về trong CÙNG lượt gọi công cụ. (3) Sau mỗi test viết xong: commit + `git push -u origin agy/yl-test-a6-c` ngay, để lượt sau không mất việc. (4) Lệnh nào quá 5 phút chưa xong thì bỏ, ghi vào KET-QUA, làm phần còn lại.

LUẬT CHẠY (bắt buộc, lượt trước mất 80 phút vì treo chờ tác vụ nền): KHÔNG chạy `npm run dev`, `npm start` hay server lab riêng. Test khoá tự dựng server trong tiến trình (createApp), cứ chạy `node --test --test-timeout=120000 <file>` tiền cảnh. Chụp ảnh/quay video: viết 1 script node tự dựng createApp trong tiến trình, chụp xong tự đóng server và thoát (process.exit), chạy tiền cảnh. Mọi lệnh bọc timeout ≤ 300 s. Nếu buộc phải chạy nền: ghi log vào thư mục theo_doi và tự tắt khi xong.

Phiếu viết lại test đo mức 9 (A6) Yên Lam. CHỈ sửa test, KHÔNG sửa code sản phẩm. Chạy mọi lệnh ở tiền cảnh, KHÔNG dùng background task, mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
1. `git -C C:\linhx\ifagent fetch --all`, `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl-test-a6-c -b agy/yl-test-a6-c origin/agy/yl-test-t1`.
2. Chỉ sửa `apps/lab/test/nghiem-thu-rc6/03-a6-do-muc-9.test.js` và dòng của nó trong KHOA.sha256. KHÔNG đụng 01, 02 (đã khoá; `sha256sum -c` hai dòng đó phải OK).
3. Sửa 2 chỗ sai Claude chỉ ra:
   (a) [A6-07] "lệch bố cục ≤ 2%" KHÔNG phải so màu từng điểm ảnh (ảnh khung là bản vẽ, bản dựng có ảnh Lam/KV thật nên lệch màu luôn cao). Đo theo HỘP: với mỗi màn có khung trong KHUNG/2c-K-AM, lấy toạ độ các khối chính (logo, đầu/khung Lam, tiêu đề, nút chính, ô chat, QR) ghi trong NOP/2c-K-AM/UI-K-AM.md (hoặc đo một lần trên ảnh khung, ghi thành bảng hằng số trong test, kèm nguồn); so với boundingBox thật; lệch = |Δx|+|Δy|+|Δw|+|Δh| chia (2×1080+2×1920), tính %. Mỗi khối ≤ 2%. Xuất bảng khối | khung | thật | lệch%.
   (b) [A6-01] ≤ 12 từ/màn: đếm chữ khách thấy trên màn (bỏ chữ ẩn, aria, chữ trong ảnh). Thêm cột "chữ duyệt CHU-TREN-MAN" cho cùng màn. Nếu chính chữ đã duyệt vượt 12 từ thì ghi CHU_DUYET_VUOT ở bảng (không tính đỏ cho code, Claude báo Linh); nếu chữ thật nhiều hơn chữ duyệt thì đỏ.
   Không đổi ngưỡng nào. Các mục A6-02..06 giữ nguyên.
4. Kiểm hiệu chuẩn: chạy test (b)(a) với chính ảnh khung PNG làm "bản dựng" giả (nạp ảnh khung vào trang trắng có các hộp đúng toạ độ) → phải ra lệch ≈ 0%. Ghi kết quả.
5. Test 03 ghi thêm bảng số ra `bang-chung/<tên nhánh>/do-muc-9.json` dạng [{"ma":"A6-01","ten":"...","nguong":"...","te_nhat":"...","dat":true/false}]. Chạy 03 trên code hiện tại, ghi sha256 mới vào KHOA.sha256, commit, push `agy/yl-test-a6-c`.
CẤM: sửa code sản phẩm, sửa 01/02, sửa TIEU-CHUAN/CHUAN/KHUNG/CHU-TREN-MAN, deploy, in khoá. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co`/`dat: khong`; SHA đỉnh; bảng 7 mục A6 đỏ/xanh; bảng A6-07 theo khối; danh sách màn CHU_DUYET_VUOT; kết quả hiệu chuẩn bước 4.

## Lần trước trượt vì:
model: gemini-4-argon-high
phieu: yl-test-a6-c
may: may-2
trang_thai: dung
tep_doi: KET-QUA.md
drive: (khong)
phut: 40.02
token: vao=0 ra=0

dừng agy: quá trần 40 phút
warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the default mode.
root agent idle; waiting up to 40m0s for 1 background task(s)

nhip: 14:24 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
