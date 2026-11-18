may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 15
theo_doi: D:\linhx\wt-lx-r4-tran-kiem-l4; D:\linhx\nhat-ky\lx-r4-tran-kiem-l4
nhan: may-3 2026-11-18T14:37:16+0700
moc: 99cc35716fa08a4ba33fb78de0d9e094cafe1975

Phiếu lx-r4-c-va-2 (LAB131), CHẠY TIẾP lượt c-va bị quá trần 30 phút. Thư mục D:\linhx\wt-lx-r4-tran-kiem-l4 ở nhánh lx-r4-tran-kiem-l4, đã có commit test đỏ (`runner/test_tran_kiem.py`) và có thể có phần vá dở. KHÔNG clone lại, KHÔNG sửa tệp test mới.
LUẬT CHỐNG CHUYỂN NỀN: mọi lệnh ghi log ra `D:\linhx\nhat-ky\lx-r4-tran-kiem-l4\<ten>.log`, chạy tiền cảnh; công cụ báo đã chuyển nền thì gọi trạng thái liên tục, không kết thúc lượt; test chỉ chạy 1 tệp mỗi lệnh. CẤM chạy `pytest runner` toàn bộ, đụng GitHub, sửa D:\linhx\hang-doi.
1. `git -C D:\linhx\wt-lx-r4-tran-kiem-l4 status` và `git -C D:\linhx\wt-lx-r4-tran-kiem-l4 log --oneline -5`, đọc `D:\linhx\nhat-ky\lx-r4-tran-kiem-l4\tien-do.log` để biết đã làm tới đâu. Commit ngay phần vá dở nếu có (commit "wip(r4): ...").
2. Vá runner/linhx_runner.py và/hoặc runner/hang_doi_git.py cho `runner/test_tran_kiem.py` XANH, không đổi hành vi phiếu không có `lenh_kiem`. Commit "fix(r4): ..." sau mỗi ca xanh, đừng dồn tới cuối.
3. Chỉ chạy thêm `runner/test_hang_doi_git.py` làm test cũ.
4. `git -C D:\linhx\wt-lx-r4-tran-kiem-l4 -c sendpack.sideband=false push origin lx-r4-tran-kiem-l4:refs/heads/agy/lx-r4-tran-kiem-l4 > D:\linhx\nhat-ky\lx-r4-tran-kiem-l4\push-c2.log 2>&1`.
KET-QUA: dòng đầu `dat: co|khong`; SHA đỉnh; test_tran_kiem đỏ→xanh (số ca).
