may: may-2
loai: khac
tran_phut: 40
theo_doi: C:\linhx\wt-ra-qt; C:\linhx\ifagent

KHÔNG chạy lệnh nền (background): mọi lệnh chạy tiền cảnh và chờ xong. Chỉ đọc, không sửa repo ifagent.

Việc: so quy trình hàng đợi máy agy (linhx-engine) với quy trình chất lượng cao của dự án ifagent, tìm chỗ còn thiếu.
1. Repo A: `C:\linhx\wt-ra-qt` (clone nhánh claude/project-thread-jowxv1 của https://github.com/fyzdfyzd/linhx-engine, có rồi thì git pull). Repo B: `C:\linhx\ifagent` (chưa có: `git clone --depth 1 -b claude/project-thread-qdzzr4 https://github.com/fyzdfyzd/ifagent C:\linhx\ifagent`, repo ~3 GB, chờ xong; báo nếu không clone được vì quyền).
2. Đọc ở B: AGENTS.md (nhất là "Quy trình mỗi đề", luật deploy), docs/standards/, docs/huong-dan/, docs/TIEU-CHUAN-PHOTOBOOTH.md, docs/CHECKLIST-SAN-SANG-HOP-YEN-LAM.md, docs/QUY-TRINH-PHOTOBOOTH-FACTORY.md, scripts liên quan cổng/chấm/kiểm.
3. Đọc ở A: skills/le/hang-doi-may/SKILL.md, runner/ (linhx_runner.py, hang_doi_git.py), các skill chất lượng trong skills/ (tìm linhx-chuan, xuong-linhx, agy-tu-chay, vong-lap, thiet-ke nếu có), viec/lvn-landing/ làm ví dụ.
4. Viết `viec/ra-quy-trinh/SO-SANH.md` ở A: bảng 10 khâu (phân tích đề, tiêu chuẩn/ngưỡng điểm, khoá nghiệm thu, chia thợ/điều phối, giám sát thợ, phạm vi diff, E2E + bằng chứng ảnh/video cỡ thật, tự chấm máy, chấm độc lập/ngưỡng, phát hành/rollback, bài học) × cột: ifagent làm thế nào (file:dòng) | hàng đợi có chưa (có/thiếu/một phần, file:dòng) | đề xuất nhỏ nhất. Thêm mục "Cần lấy thêm từ project ifagent-dev" nếu tài liệu nhắc tới thứ không có trong repo (ví dụ NOP/, KE-HOACH-PHAT-HANH, kiem-dot-*.sh).
5. Commit chỉ file đó, `git pull --rebase`, push nhánh. Trả lời ≤1500 ký tự: 5 khâu thiếu quan trọng nhất + danh sách cần lấy thêm + hash.
