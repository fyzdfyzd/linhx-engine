#!/usr/bin/env bash
# Dung LINHX ENGINE tren VM Ubuntu da co Docker. Chay: sudo bash len-may.sh http://<IP hoac ten mien>
# Lan dau: tao .env voi mat khau ngau nhien, dung he, tao tho may-cty + cloud-1 + tai khoan Linh.
# Bi mat ghi vao /root/linhx-bi-mat.env (chi root doc), KHONG in ra man hinh.
set -euo pipefail
cd "$(dirname "$0")"
URL="${1:-http://$(curl -s ifconfig.me)}"
if [ ! -f .env ]; then
  ngau() { python3 -c 'import secrets;print(secrets.token_hex(12))'; }
  HOST="${URL#*://}"
  if [[ "$HOST" =~ ^[0-9.]+$ ]]; then ADDR=":80"; else ADDR="$HOST"; fi
  cat > .env <<EOT
SITE=engine.local
SITE_ADDR=$ADDR
PUBLIC_URL=$URL
DB_ROOT_PASSWORD=$(ngau)
ADMIN_PASSWORD=$(ngau)
THO_CLOUD_TOKEN=
AGY_CMD=agy
EOT
  chmod 600 .env
fi
mkdir -p ../trang-bu/out
if [ ! -f ../trang-bu/out/index.html ] && command -v npm >/dev/null 2>&1; then
  (cd ../trang-bu && SITE_JSON="$(cd ../sites/ifagent && pwd)/site.json" NEXT_TELEMETRY_DISABLED=1 npm run build)
fi
docker compose up -d --build
echo "cho Frappe san sang..."
for i in $(seq 1 60); do docker compose exec -T backend curl -sf -H "Host: engine.local" localhost:8000/api/method/ping >/dev/null 2>&1 && break; sleep 5; done
for s in linhx ifagent; do
  for i in $(seq 1 30); do docker compose exec -T backend curl -sf -H "Host: $s" localhost:8000/api/method/ping >/dev/null 2>&1 && break; sleep 2; done
done
BI=/root/linhx-bi-mat.env
if [ ! -f $BI ]; then
  X="docker compose exec -T backend bench --site engine.local execute"
  tk() { $X linhx_worker.setup.tao_tho --kwargs "$1" | grep -o 'LINHX_TOKEN=[^"]*' | head -1 | cut -d= -f2; }
  TK_MAY=$(tk "{'ma':'may-cty','loai':'may','may':'DESKTOP-PVHR2CD','nhan':'repo,trinh-duyet,windows'}")
  TK_CLOUD=$(tk "{'ma':'cloud-1','loai':'cloud','nhan':''}")
  MK_LINH=$(python3 -c 'import secrets;print(secrets.token_hex(8))')
  $X linhx_worker.setup.tao_dieu_hanh --kwargs "{'email':'tuanlinh@urah.vn','mat_khau':'$MK_LINH'}" >/dev/null
  umask 077
  printf "LINHX_URL=%s\nTOKEN_MAY_CTY=%s\nTOKEN_CLOUD_1=%s\nLINH_EMAIL=tuanlinh@urah.vn\nLINH_MAT_KHAU=%s\n" "$URL" "$TK_MAY" "$TK_CLOUD" "$MK_LINH" > $BI
  sed -i "s/^THO_CLOUD_TOKEN=.*/THO_CLOUD_TOKEN=$TK_CLOUD/" .env
fi
DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$DEPLOY_DIR/sao-luu.sh" "$DEPLOY_DIR/khoi-phuc-thu.sh"
sed "s|/home/ADMIN/linhx-engine/deploy|$DEPLOY_DIR|g" "$DEPLOY_DIR/linhx-sao-luu.cron" > /etc/cron.d/linhx-sao-luu
chmod 644 /etc/cron.d/linhx-sao-luu
docker compose --profile tho-cloud up -d --build tho-cloud || echo "tho-cloud chua len (xem README)"
docker compose ps --format "{{.Service}} {{.Status}}"
echo "XONG. Mo $URL . Bi mat o $BI (sudo cat)."
