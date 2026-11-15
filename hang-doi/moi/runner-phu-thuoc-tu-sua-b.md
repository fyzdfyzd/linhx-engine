may: may-2
loai: code
tran_phut: 40
theo_doi: C:\linhx\wt-phu-thuoc

LƯU Ý: lần trước bị dừng vì agy chạy tác vụ nền rồi ngồi chờ. TUYỆT ĐỐI không chạy lệnh nền (background), mọi lệnh (clone, pytest, git) chạy tiền cảnh và chờ xong. Có thể phần việc đã làm dở trong C:\linhx\wt-phu-thuoc: kiểm `git status` trước, làm tiếp.

Thêm 2 tính năng cho runner (học từ beads và agent-orchestrator).
Repo: `C:\linhx\wt-phu-thuoc` (chưa có: `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-phu-thuoc`; có rồi: `git pull`). KHÔNG sửa C:\linhx\hang-doi. Không đụng runner/bang/ (phiếu khác đang làm).

A. Phụ thuộc: header `phu_thuoc: id1; id2`. Máy chỉ nhận phiếu khi mọi id có `hang-doi/xong/<id>/KET-QUA.md` với `trang_thai: xong`. Nếu một id phụ thuộc kết thúc `loi` hoặc `dung` thì phiếu này bỏ qua (không nhận), KET-QUA không ghi gì. Phiếu không có `phu_thuoc` chạy như cũ.

B. Tự sửa: header `tu_sua: N` (mặc định 0 = tắt, tối đa 3). Khi phiếu kết thúc `loi` hoặc `dung` (không tính lỗi máy: thiếu agy, 429), runner tự tạo `hang-doi/moi/<id>-sua-<k>.md`: giữ nguyên header (giảm `tu_sua` đi 1, cùng `may`, `theo_doi`), thân = đề gốc + mục "Lần trước trượt vì:" chép 1500 ký tự cuối KET-QUA. Hết lượt thì thôi. Push cùng lúc với KET-QUA.

Test mới trong runner/ (không conftest.py, không gọi mạng, chạy tiền cảnh): A nhận đúng/bỏ đúng; B sinh phiếu sửa đúng số lần, không sinh khi lỗi máy. `python -m pytest runner -q` đạt hết (trừ test đường dẫn chỉ Windows nếu có).
Cập nhật mục "Phiếu" trong `skills/le/hang-doi-may/SKILL.md` (thêm 2 dòng header).
`git pull --rebase` rồi push nhánh. Trả lời: số test đạt, hash commit.
