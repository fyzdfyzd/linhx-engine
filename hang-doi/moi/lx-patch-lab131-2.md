may: may-3
loai: code
tran_phut: 15
theo_doi: D:\linhx\nhat-ky\lab131-patch
phu_thuoc: lx-r6-sua-1; lx-r1-sua-test

Phiếu xuất lại patch để Claude soi, làm y như phiếu lx-patch-lab131 (đọc nó ở hang-doi/xong/), nhưng cho 3 nhánh: (D:\linhx\wt-lx-r6-tha-chuoi-l3, r6) (D:\linhx\wt-lx-r1-phu-thuoc-cho-l4, r1) (D:\linhx\wt-lx-r4-tran-kiem-l4, r4). Xoá thư mục `bao-cao/lab131/<tên>` cũ trước khi chép. Push hang-doi lên trạm, KHÔNG push GitHub.
LUẬT CHỐNG CHUYỂN NỀN: mọi lệnh ghi log ra tệp trong thư mục nhật ký của phiếu, chạy tiền cảnh; công cụ báo đã chuyển nền thì gọi trạng thái liên tục tới khi xong, không kết thúc lượt; test chỉ chạy 1 tệp mỗi lệnh. CẤM chạy `pytest runner` toàn bộ, đụng GitHub, sửa D:\linhx\hang-doi.
KET-QUA: dòng đầu `dat: co|khong`; số patch mỗi nhánh; SHA đã push.
