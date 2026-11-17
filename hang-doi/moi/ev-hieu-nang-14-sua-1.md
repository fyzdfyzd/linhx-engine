may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: D:\linhx\ifagent-wt\ev-hieu-nang-14

Lượt trước bị dừng vì chạy tác vụ nền rồi chờ. Lượt này mọi lệnh phải chạy tiền cảnh, đợi xong trong cùng lệnh.

Phiếu ev-hieu-nang-14 (song song, máy 3): đo và nâng điểm Lighthouse cho event.ifagent.net bản agy. COMMIT + PUSH SAU MỖI Ý.
0. `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent-wt\ev-hieu-nang-14` (nếu đã có thì fetch), `git checkout -b agy/ev-hieu-nang-14 origin/agy/ev-de-xuat-11`. Trong apps/event: `npm ci`, chạy máy chủ local theo README/package.json của apps/event (tiền cảnh trong cùng lệnh test, không để chạy nền sau khi xong).
1. Chạy Lighthouse (devDependency `lighthouse` + chrome-launcher, headless) chế độ di động và máy bàn cho 18 trang đang có trong test chụp (/, /demo, /giai-phap, 1 trang /giai-phap/<slug>, 1 demo, /blog, 1 bài, /case, /lien-he, /goi, /mau, /thu, /de-xuat, /tao, /tao?agency, 2 trang play, 404). Ghi bảng điểm TRƯỚC vào bang-chung/ev-hieu-nang-14/BANG-DIEM.md (4 cột: hiệu năng, trợ năng, thực hành tốt, SEO).
2. Sửa trong apps/event cho tới khi MỌI trang di động đạt: hiệu năng ≥ 85, trợ năng ≥ 95, thực hành tốt ≥ 95, SEO ≥ 95. Hướng sửa: ảnh đúng cỡ + srcset + loading=lazy ngoài màn đầu, width/height chống nhảy bố cục, preload phông chính, defer script, alt/label/aria, tương phản màu (cả giao diện Đêm và Sáng), meta description/canonical. Không đổi chữ hiển thị, không đổi bố cục thấy được ở 1280 và 360.
3. Thêm test khoá `apps/event/test/e2e/lighthouse-nguong.test.js` (script npm `test:lh`): chạy 18 trang di động, trượt ngưỡng thì báo "Trang <url>: <hạng mục> <điểm> < <ngưỡng> — xem mục <audit id> trong báo cáo". Ghi bảng SAU vào BANG-DIEM.md.
4. Chạy tiền cảnh: test:lh, khong-tran-ngang, giao-dien-sang, de-xuat-slide; npm test sau cùng. Push agy/ev-hieu-nang-14.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-hieu-nang-14/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ, không sinh ảnh AI, không gọi AI thật, không viết chữ mới. Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-de-xuat-11..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA; bảng điểm trước/sau (trung bình + trang thấp nhất); pass/fail.

## Lần trước trượt vì:
model: mac-dinh
phieu: ev-hieu-nang-14
may: may-3
trang_thai: dung
ly_do: cho-tac-vu-nen
tep_doi: (khong)
drive: (khong)
phut: 0.67
token: vao=0 ra=0

dừng agy (cho-tac-vu-nen): waiting up to ... background task
warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the default mode.
root agent idle; waiting up to 40m0s for 1 background task(s)
