phieu: ra-quy-trinh-chat-luong
may: may-2
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 15.30
token: vao=344307 ra=45450

Đang tiến hành clone repo `linhx-engine` vào `C:\linhx\wt-ra-qt`, chờ lệnh chạy xong trước khi thực hiện bước tiếp theo.
Đã đẩy [SO-SANH.md](file:///C:/linhx/wt-ra-qt/viec/ra-quy-trinh/SO-SANH.md) (`claude/project-thread-jowxv1`, hash `446265484125e867fe61765e9f0d6858e2894b9e`).

**5 khâu thiếu quan trọng nhất:**
1. **Tự chấm máy + khoá `.khoa`:** `agy` thoát 0 là tính `xong`, chưa kiểm `.khoa`/`lenh_kiem:` → nối `canh/cong_kiem.py` vào `hang_doi_git.py`.
2. **Phạm vi diff & bí mật:** Chưa kiểm diff ở `theo_doi:` → nối `canh/rao.py` (`vung:`, log `.jsonl`, quét `.env`/key).
3. **E2E HTTP + ảnh/video thật:** Mới chụp 2 ảnh `file://` → cần HTTP thật, khổ Kiosk/LED/iPhone, `recordVideo`, `dupImg=0`, chép `bang-chung/` lên Drive.
4. **Phát hành & rollback:** Thiếu cổng `stg-*` (`/healthz==BUILD_SHA`, không trùng alias prod), giờ cấm (>22h) và gói rollback `:prev` do Linh mở prod.
5. **Chấm độc lập & ngắt lỗi dây chuyền:** Thiếu phiếu `loai: cham` mắt mới + mốc git hoàn tác, huỷ phiếu con khi `phu_thuoc` lỗi, tạm ngưng máy khi `429`.

**Cần lấy thêm từ `ifagent-dev`:**
- Ngoài git: `NOP/phat-hanh/kiem-dot-{15h,b}.sh`, `NOP/0-TINH-NANG.md`, `NOP/1-LUONG/{DU-LIEU-MAU.json,PROMPT-KIOSK-SACH.md}`, `NOP/2c-*`, `NOP/SP-TO-THAM-DINH-14-11.md`; `KE-HOACH-PHAT-HANH` (§16, §17b, §21.1, §22); `BANG-SU-THAT-CSMO.md`, `CHU-TREN-MAN.md`, `SOAT-{NGUON-LICH,DU-PHONG-LAM,GIAO-DIEN}.md`, `CHUAN-HOA-AUDIT.md`; `XUONG-AI/MAU_*.md`.
- Nhánh rời `ifagent`: `claude/kiem-thu-rc1` (`kiem-thu/`), `claude/project-thread-4abpu3` (`ops/`).
