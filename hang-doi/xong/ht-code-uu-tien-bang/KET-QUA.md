model: gemini-pro-orchestrator
phieu: ht-code-uu-tien-bang
may: may-3
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 23.93
token: vao=785121 ra=71577

Đã hoàn tất bổ sung ưu tiên chọn phiếu theo `hang-doi/bang.json` trên nhánh `agy/ht-uu-tien-bang` tại `C:\linhx\wt-ht-uu-tien` (không chạm `hang-doi`, `main` hay nhánh runner đang chạy, không mở PR, không merge).

### Tóm tắt thực hiện
- Trong [linhx_runner.py](file:///C:/linhx/wt-ht-uu-tien/runner/linhx_runner.py#L2179-L2185), hàm `vong` chuyển nguồn `github` sang `hang_doi_git.vong_git`, nơi [hang_doi_git.py](file:///C:/linhx/wt-ht-uu-tien/runner/hang_doi_git.py#L1516-L1546) chọn phiếu tiếp theo trong `hang-doi/moi/` qua `chon_ung_vien`.
- Đã thêm [_doc_bang_uu_tien](file:///C:/linhx/wt-ht-uu-tien/runner/hang_doi_git.py#L1439-L1475), [_ten_phieu_tu_muc](file:///C:/linhx/wt-ht-uu-tien/runner/hang_doi_git.py#L1478-L1493) và [sap_xep_phieu_theo_bang](file:///C:/linhx/wt-ht-uu-tien/runner/hang_doi_git.py#L1496-L1513), gọi trong `chon_ung_vien` tại [hang_doi_git.py](file:///C:/linhx/wt-ht-uu-tien/runner/hang_doi_git.py#L1530-L1534):
  - Đọc `hang-doi/bang.json`; khớp tiền tố `<ma>-` của bảng (ưu tiên khớp mã dài trước, không khớp nhầm tiền tố không có `-`), xếp `uu_tien` tăng dần (`0` trước, `1`, `2`...).
  - Cùng mức ưu tiên giữ nguyên thứ tự cũ (Timsort ổn định); phiếu không thuộc bảng xếp sau cùng; file thiếu/JSON hỏng/không có mục hợp lệ thì giữ nguyên th
...[cat bot]...
_theo_bang` (cùng `_doc_bang_uu_tien`, `_ten_phieu_tu_muc`; gọi trong `chon_ung_vien`), [hang_doi_git.py](file:///C:/linhx/wt-ht-uu-tien/runner/hang_doi_git.py#L13) (`:13`, [`:1439-1513`](file:///C:/linhx/wt-ht-uu-tien/runner/hang_doi_git.py#L1439-L1513), [`:1530-1534`](file:///C:/linhx/wt-ht-uu-tien/runner/hang_doi_git.py#L1530-L1534)) & [test_uu_tien_bang.py](file:///C:/linhx/wt-ht-uu-tien/runner/test_uu_tien_bang.py#L1-L282) (`:1-282`), 144 passed / 3 skipped (`pytest runner`, gồm 6/6 test mới), `2c03204df1e992d0d1fa983a9257ee7031fcc10d`.
