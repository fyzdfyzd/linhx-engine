may: may-2
phieu: bhc-trien-staging-1
viec: dọn ổ đĩa trên VM ifagent-event (df -h / hiện chỉ còn 4.4G < 5 GB) và tạo /opt/stg-brand/stg-brand.env từ stg-brand.env.example (ADMIN_CODE mới, GEMINI_API_KEY khoá staging)
lenh: gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026 --command="sudo mkdir -p /opt/stg-brand/data && sudo chown -R $(id -u):$(id -g) /opt/stg-brand && df -h /" && gcloud compute scp C:\linhx\ifagent-wt\bhc-staging\infra\staging\stg-brand\compose.yaml C:\linhx\ifagent-wt\bhc-staging\infra\staging\stg-brand\stg-brand.env.example ifagent-event:/opt/stg-brand/ --zone=asia-southeast1-b --project=ifagent-event-2026 && gcloud compute ssh ifagent-event --zone=asia-so...
gio: 2026-11-17T13:15:31+0700
