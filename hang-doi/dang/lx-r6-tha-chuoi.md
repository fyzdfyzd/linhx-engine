may: bat-ky
loai: code
tran_phut: 40
tu_sua: 0
theo_doi: D:\linhx\wt-lx-r6-tha-chuoi
phu_thuoc: lx-thu-5p
nhan: may-3 2026-11-18T07:12:07+0700

Phiếu lx-r6-tha-chuoi (sửa runner, LAB131). Chạy mọi lệnh ở TIỀN CẢNH, không background task, không tự chạy `pytest runner` toàn bộ (chỉ chạy test của phiếu và tệp test đụng tới). Mỗi 5 phút có tệp mới hoặc commit.
1. `git -c sendpack.sideband=false clone -b claude/project-thread-jowxv1 git://192.168.1.136/linhx-engine.git D:\linhx\wt-lx-r6-tha-chuoi` rồi `git -C D:\linhx\wt-lx-r6-tha-chuoi checkout -b lx-r6-tha-chuoi`.
2. Việc: luật "chạy phiếu thử trước mỗi chuỗi" hiện chỉ là lời dặn, Claude đã bỏ qua đêm 17/11. Viết `runner/tha_chuoi.py <thu-muc-phieu> --may <may>`: đọc mọi .md trong thư mục, tự sinh 1 phiếu ping (dùng `tao_phieu_ping`, tran_phut 5) làm gốc, chèn `phu_thuoc: <id ping>` vào mọi phiếu không có phu_thuoc, kiểm không có vòng phụ thuộc và mọi id phu_thuoc tồn tại, rồi mới ghi vào `hang-doi/moi/` + commit + push (pull --rebase tối đa 3 lần).
3. VIẾT TEST TRƯỚC (repo giả tmp_path, không mạng), commit riêng, cho thấy ĐỎ: chuỗi 3 phiếu → 4 tệp trong moi/, ping là gốc; vòng phụ thuộc hoặc id lạ → thoát mã 2, không ghi gì.
4. Viết cho test xanh, commit "feat(tha-chuoi): ...".
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá. Không đổi hành vi ngoài phạm vi phiếu.
Cuối: `git -C D:\linhx\wt-lx-r6-tha-chuoi -c sendpack.sideband=false push origin lx-r6-tha-chuoi`.
KET-QUA (ngắn): dòng đầu `dat: co|khong`; SHA đỉnh lx-r6-tha-chuoi; test mới đỏ→xanh; số test chạy.
