phieu: yl-kiem-may2-deploy
may: may-2
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 3.99
token: vao=79730 ra=7592

Kết quả kiểm tra điều kiện deploy staging Yên Lam trên **máy 2**:

1. **`gcloud` & danh sách VM (`ifagent-event-2026`)**: **CÓ**
   - `gcloud --version` (dòng đầu): `Google Cloud SDK 593.0.0` *(lưu ý khi chạy từ runner PowerShell: gọi trực tiếp [gcloud.cmd](file:///C:/Users/Admin/AppData/Local/Google/Cloud%20SDK/google-cloud-sdk/bin/gcloud.cmd) do tiến trình runner chưa nạp lại User `PATH` mới và ExecutionPolicy chặn `gcloud.ps1`)*.
   - `gcloud config get account`: `taidang.urahnetwork@gmail.com`
   - `gcloud compute instances list --project=ifagent-event-2026`:
     - `ifagent-event`: `RUNNING`
     - `linhx-staging`: `RUNNING`

2. **SSH kiểm tra VM `ifagent-event` (`asia-southeast1-b`)**: **CÓ**
   - Đã khởi tạo khoá SSH không passphrase và đọc thông tin thành công:
   - `df -h / | tail -1`: `/dev/root        38G   22G   17G  56% /`
   - `docker ps --format '{{.Names}}'` (10 container): `ifagent-staging-lab`, `ifagent-lab-1`, `ifagent-event-1`, `ifagent-idea-lab-1`, `ifagent-brand-health-1`, `ifagent-concept-note-1`, `luna-unikon-event`, `luna-astro-engine`, `luna-astro-calc`, `ifagent-caddy-1`

3. **File [ifagent.env](file:///C:/linhx/_ENV/ifagent.env)**: **CÓ**
   - Danh sách tên biến (7 biến): `GEMINI_API_KEY`, `GEMINI_KEY_04`, `ADMIN_PASSWORD`, `LOG_RETENTION_DAYS`, `TZ_DISPLAY`, `YL_STG_CHAM_TK`, `YL_STG_CHAM_MK`

4. **Thư mục `C:\linhx\ifagent-nop\`**: **KHÔNG**
   - Chưa tồn tại `C:\linhx\ifagent-nop\` *(hiện tại tại `C:\linhx\` có `ifagent/` và `ifagent-wt/`)*.
