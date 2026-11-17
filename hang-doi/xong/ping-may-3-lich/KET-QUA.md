model: mac-dinh
phieu: ping-may-3-lich
may: may-3
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 0.04
token: vao=0 ra=0

may: DESKTOP-2AUT482
ram_trong_gb: 57.8 / 63.9
o_C: trong 54.7 GB
o_D: trong 305.8 GB
o_G: trong 52.0 GB
agy: 1.5.10
runner_head: 546e9e3 Gộp agy/chan-cho-nen: runner nhận ra agy chờ tác vụ nền, dừng sớm, sửa lượt sau chạy tiền cảnh
tien_trinh_agy: 0
== log: D:\linhx\hang-doi\runner\tho.log
  File "D:\linhx\hang-doi\runner\hang_doi_git.py", line 184, in chay_git
    raise RuntimeError(f"git {' '.join(args)} loi ({p.returncode}): {(p.stderr or p.stdout).strip()}")
RuntimeError: git checkout -B hang-doi refs/remotes/tram/hang-doi loi (128): error: bad signature 0x00000000
fatal: index file corrupt

18:33:15 linhx-runner 0.1.1 tho=may-1 nguon=github nhanh=hang-doi so_phieu=1
18:33:16 loi Traceback (most recent call last):
  File "D:\linhx\hang-doi\runner\hang_doi_git.py", line 2584, in vong_git
    viec = nhan_phieu_git(cfg)
           ^^^^^^^^^^^^^^^^^^^
  File "D:\linhx\hang-doi\runner\hang_doi_git.py", line 1490, in nhan_phieu_git
    wt = dam_bao_worktree(cfg)
         ^^^^^^^^^^^^^^^^^^^^^
  File "D:\linhx\hang-doi\runner\hang_doi_git.py", line 924, in dam_bao_worktree
    chay_git(["checkout", "-B", nhanh, ref_remote], cwd=wt)
  File "D:\linhx\hang-doi\runner\hang_doi_git.py", line 184, in chay_git
    raise RuntimeError(f"git {' '.join(args)} loi ({p.returncode}): {(p.stde
...[cat bot]...
doi so_phieu=1
18:36:14 linhx-runner 0.1.1 tho=may-1 nguon=github nhanh=hang-doi so_phieu=1
18:37:14 linhx-runner 0.1.1 tho=may-1 nguon=github nhanh=hang-doi so_phieu=1
18:37:16 nhan hfcd-kiem-quyen trinh-duyet may-1
{"luc": "2026-11-17T18:38:31+0700", "phieu": "hfcd-kiem-quyen", "so_file": 0, "ngoai_vung": [], "bi_mat": []}
18:38:32 xong hfcd-kiem-quyen xong
18:39:14 linhx-runner 0.1.1 tho=may-1 nguon=github nhanh=hang-doi so_phieu=1
18:40:14 linhx-runner 0.1.1 tho=may-3 nguon=github nhanh=hang-doi so_phieu=1
18:40:18 nhan ping-may-3-lich lenh may-3
