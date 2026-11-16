may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\wt-csmo\deck
phu_thuoc: csmo-mau-slide

Phiếu csmo-deck. Đọc viec/csmo-talk/DE-BAI.md mục "Phiếu csmo-deck", KICH-BAN-v5.md và viec/csmo-talk/mau/ (ảnh mẫu + GHI-CHU.md thẻ phong cách) trên nhánh hang-doi. Nếu chưa có viec/csmo-talk/mau/GHI-CHU.md thì dừng, ghi CHUA_CO_MAU.
0. git clone -b hang-doi https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-csmo\deck. Nhánh agy/csmo-deck.
1. Viết deck/slides.json, script dựng PPTX, dựng CSMO26_T21_v5.pptx. Tối giản: nhiều khoảng trống, 1 ý 1 slide, so từng slide với mẫu, bỏ bớt chi tiết thừa.
2. Render PNG 1920 từng slide + TONG.png. Kiểm dấu tiếng Việt, tràn chữ.
3. Commit pptx, json, script, PNG vào viec/csmo-talk/deck/, push nhánh agy/csmo-deck.
CẤM: sinh ảnh AI, ảnh có chữ do AI vẽ, nêu tên thương hiệu của Linh, sửa ngoài viec/csmo-talk/deck.
KET-QUA.md: dòng đầu dat: co/khong; SHA; số slide; danh sách slide phải bỏ bớt chữ so với kịch bản.
