may: may-3
loai: code
tran_phut: 15
theo_doi: D:\linhx\nhat-ky\lab131-patch
nhan: may-3 2026-11-18T14:37:15+0700

Phiếu xuất patch 4 nhánh LAB131 vào nhánh hang-doi để Claude soi diff. Không sửa code.
LUẬT CHỐNG CHUYỂN NỀN: mọi lệnh ghi log ra `D:\linhx\nhat-ky\lab131-patch\<ten>.log`, chạy tiền cảnh; công cụ báo đã chuyển nền thì gọi trạng thái liên tục tới khi xong, không kết thúc lượt. KHÔNG push lên GitHub (lượt trước push GitHub bị treo).
1. `New-Item -ItemType Directory -Force D:\linhx\nhat-ky\lab131-patch`.
2. Với mỗi cặp (thư mục, tên): (D:\linhx\wt-lx-r5-bi-mat-goc-l3, r5) (D:\linhx\wt-lx-r6-tha-chuoi-l3, r6) (D:\linhx\wt-lx-r1-phu-thuoc-cho-l4, r1) (D:\linhx\wt-lx-r0-tu-clone, r0): `git -C <thư mục> format-patch origin/claude/project-thread-jowxv1..HEAD -o D:\linhx\nhat-ky\lab131-patch\patch\<tên> > D:\linhx\nhat-ky\lab131-patch\fp-<tên>.log 2>&1`.
3. `git -c sendpack.sideband=false clone --depth 5 -b hang-doi git://192.168.1.136/linhx-engine.git D:\linhx\wt-lab131-patch > D:\linhx\nhat-ky\lab131-patch\clone.log 2>&1` (có rồi thì xoá trước).
4. Chép `D:\linhx\nhat-ky\lab131-patch\patch\*` vào `D:\linhx\wt-lab131-patch\bao-cao\lab131\`, `git add bao-cao/lab131`, commit "LAB131: patch r0 r1 r5 r6 de soi".
5. Push: `git -C D:\linhx\wt-lab131-patch -c sendpack.sideband=false push origin HEAD:hang-doi > D:\linhx\nhat-ky\lab131-patch\push.log 2>&1`; bị từ chối thì `git pull --rebase origin hang-doi` rồi push lại, tối đa 3 lần.
KET-QUA: dòng đầu `dat: co|khong`; số tệp patch mỗi nhánh; SHA commit đã push.
