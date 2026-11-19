may: may-2
phieu: bhc-prod-5a
viec: can Linh nap tien Gemini (prepayment credits tai https://ai.studio/projects) hoac cap GEMINI_API_KEY moi cho prod va staging
lenh: gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026 --command="sudo sed -i 's|^GEMINI_API_KEY=.*|GEMINI_API_KEY=<KHOA_MOI>|' /opt/ifagent/infra/brand-health.env /opt/stg-brand/stg-brand.env && cd /opt/ifagent/infra && sudo docker compose up -d --force-recreate brand-health && cd /opt/stg-brand && sudo STG_SHA=5bbcb0ce docker compose up -d --force-recreate"
gio: 2026-11-19T10:56:31+0700
