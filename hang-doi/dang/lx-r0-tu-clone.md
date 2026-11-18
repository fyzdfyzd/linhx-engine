may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-r0-tu-clone; D:\linhx\nhat-ky\lx-r0-tu-clone
nhan: may-3 2026-11-18T13:33:15+0700

Phiếu lx-r0-tu-clone (LAB131). Mục tiêu: runner tự clone trước khi gọi agy, để agy không phải chạy lệnh clone dài (agy hay đẩy clone ra nền rồi ngồi chờ).
LUẬT CHỐNG CHUYỂN NỀN (bắt buộc): mọi lệnh ghi log ra `D:\linhx\nhat-ky\lx-r0-tu-clone\<ten>.log` và chạy tiền cảnh; công cụ báo đã chuyển nền thì gọi trạng thái liên tục tới khi xong, không kết thúc lượt; test chỉ chạy 1 tệp mỗi lệnh. Đầu tiên `New-Item -ItemType Directory -Force D:\linhx\nhat-ky\lx-r0-tu-clone`.
CẤM: sửa runner đang chạy ở D:\linhx\hang-doi, đụng GitHub, deploy, in khoá, chạy `pytest runner` toàn bộ.
1. `git -c sendpack.sideband=false clone -b claude/project-thread-jowxv1 git://192.168.1.136/linhx-engine.git D:\linhx\wt-lx-r0-tu-clone > D:\linhx\nhat-ky\lx-r0-tu-clone\clone.log 2>&1` rồi `git -C D:\linhx\wt-lx-r0-tu-clone checkout -b lx-r0-tu-clone`.
2. VIẾT TEST TRƯỚC `runner/test_tu_clone.py` (repo nguồn giả bằng `git init --bare` trong tmp_path, không mạng), commit riêng, cho thấy ĐỎ: header mới `nguon: <url> <nhanh>` và `nhanh_moi: <ten>`; khi nhận phiếu, runner (trước khi gọi agy) clone `nguon` vào thư mục `theo_doi` đầu tiên nếu chưa có, checkout `-b nhanh_moi`, có trần 5 phút; clone hỏng → KET-QUA `loi` lý do `clone_hong`, không gọi agy; thư mục đã có thì không clone lại; base_sha dùng cho quét bí mật = HEAD sau clone.
3. Vá runner cho test xanh; chạy thêm từng tệp test cũ của hàm đã sửa. Commit "feat(tu-clone): ...".
4. `git -C D:\linhx\wt-lx-r0-tu-clone -c sendpack.sideband=false push origin lx-r0-tu-clone:refs/heads/agy/lx-r0-tu-clone > D:\linhx\nhat-ky\lx-r0-tu-clone\push.log 2>&1`.
KET-QUA: dòng đầu `dat: co|khong`; SHA đỉnh; test đỏ→xanh.

nhip: 13:45 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
