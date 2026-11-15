phieu: va-4-cong-phat-hanh
may: may-4
trang_thai: xong
tep_doi: .handoff/BANG.md, .handoff/S-20261115-0925-va4-cong-phat-hanh/BAO-CAO.md, .handoff/VAN-DE.md, .handoff/logs/S-20261115-0925-va4-cong-phat-hanh.md
drive: (khong)
phut: 25.73
token: vao=630937 ra=54471

Đã hoàn thành **Vá 4 — Cổng phát hành** trên `D:\linhx\wt-va4`:

- **Đã làm**:
  1. Thêm [cong_phat_hanh.py](file:///D:/linhx/wt-va4/runner/cong_phat_hanh.py) (`--base`, `--sha`, `--prod`, `--truoc`): chỉ dùng `GET <base>/healthz`, bắt buộc HTTP 200 và khớp `BUILD_SHA`; chặn cứng nếu `--base` hoặc đích redirect trùng tên miền trong `--prod`; chặn nếu giờ VN `> 22h` hoặc `< 7h` (ngoài `07:00–22:00`); không chạy deploy thật.
  2. Thêm khuôn phiếu [deploy-staging.md](file:///D:/linhx/wt-va4/runner/phieu-mau/deploy-staging.md) và cập nhật [SKILL.md](file:///D:/linhx/wt-va4/skills/le/hang-doi-may/SKILL.md) (mục `## Phát hành` và ý ngắn ở `## Bài học` theo luật deploy của `ifagent`): phiếu chỉ đẩy staging, chạy cổng trước/sau, ghi lệnh rollback `:prev`, prod luôn thuộc diện `CAN-LINH` để Linh duyệt và chạy.
  3. Thêm bộ kiểm thử HTTP cục bộ [test_cong_phat_hanh.py](file:///D:/linhx/wt-va4/runner/test_cong_phat_hanh.py) (không `conftest.py`, không mạng ngoài).
- **Số test**: `65 passed` (`python -m pytest runner -q`, gồm 15 test mới + 50 test hiện có).
- **Commit & nhánh**: `f73b083` (`f73b0836fb6ad6af5f1dc0788a9b7113e810b134`), đã `git pull --rebase` và push lên `claude/project-thread-jowxv1`.
