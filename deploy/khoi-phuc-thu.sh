#!/usr/bin/env bash
# Sao lưu linhx + ifagent, khôi phục thử vào site tạm tam-khoi-phuc.local và curl ping.
# Cách chạy: sudo bash deploy/khoi-phuc-thu.sh [duong-dan-file-json]
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_FILE="${1:-}"

bash "$DIR/sao-luu.sh" linhx ifagent >&2

if [ ! -f "$DIR/.env" ]; then
  echo "LOI: thieu file $DIR/.env" >&2
  exit 1
fi

DB_ROOT_PASSWORD="$(grep '^DB_ROOT_PASSWORD=' "$DIR/.env" | head -1 | cut -d= -f2-)"
ADMIN_PASSWORD="$(grep '^ADMIN_PASSWORD=' "$DIR/.env" | head -1 | cut -d= -f2-)"

JSON_KQ="$(docker compose -f "$DIR/docker-compose.yml" exec -T \
  -e DB_ROOT_PASSWORD="$DB_ROOT_PASSWORD" \
  -e ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  backend bash -s <<'EOF'
set -euo pipefail
cd /home/frappe/frappe-bench

SITE_TAM="tam-khoi-phuc.local"
FILE_LINHX="$(ls -1t sites/linhx/private/backups/*-database.sql.gz | head -1)"
FILE_IFAGENT="$(ls -1t sites/ifagent/private/backups/*-database.sql.gz | head -1)"

if [ -d "sites/$SITE_TAM" ]; then
  bench drop-site "$SITE_TAM" --root-password "$DB_ROOT_PASSWORD" --force --no-backup >/dev/null 2>&1 || rm -rf "sites/$SITE_TAM"
fi

bench new-site "$SITE_TAM" \
  --mariadb-root-password "$DB_ROOT_PASSWORD" \
  --admin-password "$ADMIN_PASSWORD" \
  --no-mariadb-socket >/dev/null 2>&1

bench --site "$SITE_TAM" restore "$FILE_LINHX" \
  --mariadb-root-password "$DB_ROOT_PASSWORD" \
  --admin-password "$ADMIN_PASSWORD" >/dev/null 2>&1

PING_CODE="$(curl -s -o /dev/null -w "%{http_code}" -H "Host: $SITE_TAM" http://localhost:8000/api/method/ping)"

./env/bin/python - "$SITE_TAM" "$FILE_LINHX" "$FILE_IFAGENT" "$PING_CODE" <<'PY'
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys

site_tam, file_linhx, file_ifagent, ping_code = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
tz_vn = dt.timezone(dt.timedelta(hours=7))


def thong_tin_backup(ten_site: str, duong_dan: str) -> dict:
    p = pathlib.Path(duong_dan)
    m = re.search(r"(\d{8})_(\d{6})-", p.name)
    if m:
        t = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").replace(tzinfo=tz_vn)
    else:
        t = dt.datetime.fromtimestamp(p.stat().st_mtime, tz=tz_vn)
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    return {
        "ten": ten_site,
        "file": duong_dan,
        "luc": t.isoformat(timespec="seconds"),
        "kich_thuoc_bytes": p.stat().st_size,
        "sha256": h,
    }


kq = {
    "luc_kiem": dt.datetime.now(tz=tz_vn).isoformat(timespec="seconds"),
    "may": "linhx-engine-1",
    "script": "deploy/khoi-phuc-thu.sh",
    "sites": [
        thong_tin_backup("linhx", file_linhx),
        thong_tin_backup("ifagent", file_ifagent),
    ],
    "khoi_phuc_thu": {
        "site_tam": site_tam,
        "tu_file": file_linhx,
        "ping": ping_code,
    },
}
print(json.dumps(kq, ensure_ascii=False, indent=2))
PY

bench drop-site "$SITE_TAM" --root-password "$DB_ROOT_PASSWORD" --force --no-backup >/dev/null 2>&1 || rm -rf "sites/$SITE_TAM"
EOF
)"

if [ -n "$OUT_FILE" ]; then
  mkdir -p "$(dirname "$OUT_FILE")"
  printf "%s\n" "$JSON_KQ" > "$OUT_FILE"
fi
printf "%s\n" "$JSON_KQ"
