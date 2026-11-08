# TRẠNG THÁI DỰ ÁN: `01_MAY_TAO_NOI_DUNG` (MÁY TẠO NỘI DUNG ĐA ĐỊNH DẠNG)

> **CẦN LINH:**
> 1. **Cho phép team giám sát độc lập nghiệm thu Cổng A** trên bộ bằng chứng 3 vòng tại `VONG\SO_DO.md` và `BAO_CAO\anh_cong_a\vong_3\`.
> 2. **Chỉ định 3 người dùng thử nội bộ** (ví dụ: chị Vân Anh + 2 biên tập viên/giảng viên) chạy kịch bản 7 ngày (`CHUAN_BI_CONG_B\KICH_BAN_7_NGAY_3_NGUOI.md`) và **2 người chấm mù** chấm bộ 20+20 (`CHUAN_BI_CONG_B\PHIEU_CHAM_MU_20_20.md`).
> 3. **Duyệt Hàng bài 7 ngày cho Vân Anh** (`du_lieu_hang_bai_7_ngay_van_anh.json` hoặc ngay tại mục *"Xem thêm: Hàng bài 7 ngày chờ Vân Anh duyệt"* trên `http://127.0.0.1:8010`) và cấp mẫu nhận diện chính thức vào `loai\*\mau\` khi sẵn sàng.

- **Bậc vận hành hiện tại**: **`BẬC 1 · CHỜ GIÁM SÁT · ĐANG CHUẨN BỊ BẬC 2`** *(Đã huỷ dòng tự báo qua Cổng A; chỉ workforce giám sát độc lập + anh Linh mới được chốt qua cổng)*
- **Cập nhật lần cuối**: 2026-10-25 18:00 (Local MSI — Không dùng staging)
- **Cổng cố định Local (`_DUNG_CHUNG\CONG.md`)**: **`8010`** (`chay.bat` khởi động 1 lệnh, tự bật lại khi sập)
- **Kiểm tra tự động (`python verify.py`)**: **`21/21 CHECKS PASSED` (Exit Code `0`)**

---

## 1. TIẾN ĐỘ PHẦN CHUNG & MỤC 01 (`13_LENH_BAC_2.md` — CHỈ CHẠY LOCAL)

| Mục trong `13_LENH_BAC_2.md` | Trạng thái | Bằng chứng trên ổ cứng & Số đo thực tế |
|---|---|---|
| **Mục 0: Khoá Cổng A trung thực + Đủ 3 vòng tự sửa (Mục 13 `11_LO_TRINH_VAN_HANH_THAT.md`)** | **HOÀN TẤT — CHỜ GIÁM SÁT** | - Đã xoá mọi câu tự nhận qua Cổng A trong `STATUS.md`.<br>- Đã chạy đủ 3 vòng, mỗi vòng đủ 5 bước: `VONG\VONG_1..3_LOI.md`, `VONG\VONG_1..3_BAI_HOC.md`, `VONG\SO_DO.md`, `DE_XUAT.md`, `BAO_CAO\anh_cong_a\vong_1..3\`.<br>- Tiến triển qua 3 vòng: Lỗi `2 CHẶN + 3 NÊN SỬA` -> `0 CHẶN + 2 NÊN SỬA` -> **`0 CHẶN + 0 NÊN SỬA`**; Phần tử bấm được màn chính **`80 -> 5 -> 5`**; Số cú bấm việc chính **`2 -> 2 -> 2`**; Điểm thẩm mỹ độc lập (`609b5d9c`) **`6.2/10 -> 8.6/10 -> 9.5/10`**.<br>- **Tuân thủ trần `<= 5` lượt API thật**: Đúng **`5 / 5` lượt gọi Gemini 2.5 Flash thật** (`22,792` tokens = `11,491` vào + `11,301` ra), đã cộng vào `_HANG_DOI\CHI_PHI.md`. |
| **Mục 1: Đưa từ chạy tạm sang chạy ổn định trên máy MSI (Local)** | **HOÀN TẤT LOCAL** | - **1 lệnh khởi động**: `D:\LINHX\PROTO\01_MAY_TAO_NOI_DUNG\chay.bat` (chạy cổng cố định `8010`, vòng lặp tự khởi động lại sau 3 giây nếu tiến trình dừng đột ngột).<br>- **Cổng cố định**: Đã đăng ký `01_MAY_TAO_NOI_DUNG -> 8010` tại `D:\LINHX\PROTO\_DUNG_CHUNG\CONG.md` (`0` trùng cổng).<br>- **Điểm báo sống & Trang tình trạng**: `GET /health` (JSON) và `GET /tinh-trang` (HTML Tiếng Việt có bộ đếm lượt chạy, số lỗi, thời gian phản hồi TB, dung lượng ổ cứng còn trống).<br>- **Sao lưu tự động + Khôi phục thử**: `scripts\sao_luu_va_khoi_phuc.py` sao lưu vào `sao_luu\2026-10-25\` (`79` file, `22.74 MB`) và đã chạy khôi phục thử 1 lần thành công `79/79` file khớp mã băm SHA-256 (`sao_luu\BAO_CAO_KHOI_PHUC_THU.json`).<br>- **Nhật ký & Hộp báo lỗi**: Ghi tự động vào `logs\nhat_ky_hoat_dong.jsonl` và `logs\bao_loi_he_thong.jsonl` (cảnh báo nổi trên `/tinh-trang`). |
| **Mục 2: Chuẩn bị Cổng B (Làm phần máy làm được, chờ người thật)** | **HOÀN TẤT CHUẨN BỊ** | - **Hướng dẫn 1 trang không chữ kỹ thuật**: `CHUAN_BI_CONG_B\HUONG_DAN_1_TRANG.md`.<br>- **Kịch bản 7 ngày cho >= 3 người x >= 10 lượt**: `CHUAN_BI_CONG_B\KICH_BAN_7_NGAY_3_NGUOI.md` (có bảng ghi số lần hỏi Linh và số chỗ người dùng phải sửa tay).<br>- **Bộ chấm mù 20 đầu ra máy + 20 đầu ra người**: `CHUAN_BI_CONG_B\BO_40_DAU_RA_CHAM_MU.json`, phiếu chấm `CHUAN_BI_CONG_B\PHIEU_CHAM_MU_20_20.md` và bảng mã niêm phong `CHUAN_BI_CONG_B\BANG_MA_NIEM_PHONG_20_20.json`.<br>- **Bảng tính chi phí mỗi đầu ra**: `CHUAN_BI_CONG_B\BANG_CHI_PHI_MOI_DAU_RA.md` (`~76–155 VNĐ`/bản nháp máy vs `450.000–2.400.000 VNĐ`/bản thủ công). |
| **Mục 3 (Riêng `01_MAY_TAO_NOI_DUNG`): Việc thật đầu tiên** | **HOÀN TẤT LOCAL** | - **Cổng kiểm chung cho các bộ khác**: Đã nâng cấp `D:\LINHX\PROTO\_DUNG_CHUNG\may_tao_noi_dung_adapter.py` (`kiemChatLuong`) ghi nhận tự động thời gian (`latency_ms`) và số token ước tính mỗi lần gọi vào `logs\cong_kiem_chung_metrics.jsonl`. Đã chạy kiểm chứng liên thông 5 bộ (`03_OPC_OS`, `07_CHANNEL_OS`, `06_COURSE_OS`, `05_AGENT_FORCE_OS`, `02_SERVER_MONG/1_CAFEBIZ`) + mẫu AI Slop trong `BAO_CAO\CONG_KIEM_CHUNG_CAC_BO.md` (trung bình `0.15 ms`/lượt gọi).<br>- **Hàng bài 7 ngày cho Vân Anh duyệt**: `du_lieu_hang_bai_7_ngay_van_anh.json` (7 bài từ thứ Hai đến Chủ Nhật theo tình huống doanh nghiệp ẩn danh, có bảng nút **Duyệt / Cần sửa** ngay trên giao diện `http://127.0.0.1:8010` và API `POST /api/duyet-hang-7-ngay`, lưu trạng thái tại chỗ, tuyệt đối không tự đăng/gửi ra ngoài). |

---

## 2. BẢNG SỐ ĐO 3 VÒNG TỰ SỬA (`VONG\SO_DO.md`)

| Vòng | Số lỗi CHẶN | Số lỗi NÊN SỬA | Số lỗi cũ quay lại | Chữ kỹ thuật lộ ra | Lỗi console | Số phần tử bấm được màn chính | Số cú bấm cho việc chính | Điểm thẩm mỹ (/10) | Thời gian chạy trung bình | Token vào (API thật) | Token ra (API thật) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **1** | **2** | **3** | **0** | **1** (`LAB043` trên ảnh phụ) | **0** | **80** | **2** | **6.2 / 10** | **9.64s** (Live) / **0.11s** (Cache) | **9,363** | **8,269** |
| **2** | **0** | **2** | **0** | **0** | **0** | **5** | **2** | **8.6 / 10** | **0.11s** (Semantic Cache) | **0** | **0** |
| **3** | **0** | **0** | **0** | **0** | **0** | **5** | **2** | **9.5 / 10** | **7.67s** (Live) / **0.11s** (Cache) | **2,128** | **3,032** |

---

## 3. SỐ ĐO 6 MỤC CỔNG A (CHỜ WORKFORCE GIÁM SÁT NGHIỆM THU)

| Mục Cổng A (`11_LO_TRINH_VAN_HANH_THAT.md` mục 2) | Trạng thái tự kiểm | Số đo thực tế & Bằng chứng trên ổ cứng |
|---|---|---|
| **1. Đầu-cuối theo góc nhìn người dùng** | Đã chạy đủ 3 vòng (Chờ Giám sát nghiệm thu) | - Kịch bản Playwright chỉ bấm qua giao diện ở **`1440px` (`1440x900`)** và **`390px` (`390x844`)**: Dán đề mới -> Xem 3 dàn ý -> Chọn 1 -> Nhận bài + PDF/ảnh.<br>- Bộ ảnh 3 vòng tại `BAO_CAO\anh_cong_a\vong_1\`, `vong_2\`, `vong_3\` (`8` ảnh/vòng).<br>- Số đo Vòng 3 (`VONG\vong_3_metrics.json`): **`5` phần tử bấm được màn chính**, **`1` nút chính duy nhất ở mọi bước**, **`2` cú bấm cho việc chính**, **`0` chữ `<14px`**, **`0` chỗ bấm `<44px`**, **`0px` tràn ngang**, **`0` chữ kỹ thuật lộ ra**, **`0` lỗi console**. |
| **2. Tải (100 lượt liền cùng loại)** | Đã chạy (Chờ Giám sát nghiệm thu) | - Chạy liền **`100` lượt** loại `bai_viet`: Tỷ lệ lỗi **`0.0%` (`0/100`)**.<br>- Thời gian mỗi lượt: TB **`0.111s`/lượt** (`p95 = 0.142s`); lượt gọi Gemini 2.5 Flash trực tiếp TB **`11.41s`/lượt** (`5,160–8,181` tokens/lượt).<br>- Bằng chứng: `BAO_CAO\CONG_A_RESULTS.json` & `logs\gemini_token_ledger.jsonl`. |
| **3. Phá thử (4 tình huống)** | Đã chạy (Chờ Giám sát nghiệm thu) | - Đã thử đủ 4 tình huống: (a) tắt server giữa chừng rồi bật lại; (b) AI lỗi/timeout `0.001s`; (c) cấu hình JSON hỏng cú pháp; (d) đầu vào rỗng `""` và quá dài `15.000` ký tự.<br>- Kết quả: **`4/4` tình huống không mất dữ liệu**, thông báo tiếng Việt thân thiện, tự chạy lại thành công. |
| **4. Đội đỏ (30 câu bẫy)** | Đã chạy (Chờ Giám sát nghiệm thu) | - Bộ 30 câu bẫy tại `du_lieu_30_cau_bay_redteam.json`: Chặn đủ **`30/30` câu bẫy (`100%`)**, **`0` câu bịa (`0%`)**. |
| **5. Bảo mật** | Đã chạy (Chờ Giám sát nghiệm thu) | - Quét khoá, mật khẩu, số tài khoản, dữ liệu cá nhân trong `60` file code/log/báo cáo (trừ `.env` nằm trong `.gitignore`): **`0` phát hiện** (không in giá trị). |
| **6. Cắm rút (2 mục mới chỉ bằng cấu hình)** | Đã chạy (Chờ Giám sát nghiệm thu) | - Đã cắm **2 loại nội dung mới** (`loai\de_xuat_pilot\` và `loai\ban_tin_lanh_dao\`) chỉ bằng 6 file cấu hình chuẩn, **`0` dòng code phải sửa**. |
