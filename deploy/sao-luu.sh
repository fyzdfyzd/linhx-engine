#!/usr/bin/env bash
# Sao lưu DB hằng ngày cho từng site Frappe, giữ tối thiểu 7 bản mỗi site.
set -euo pipefail

GIU_TOI_THIEU="${GIU_TOI_THIEU:-7}"
BENCH_DIR="${BENCH_DIR:-/home/frappe/frappe-bench}"

if [ ! -d "$BENCH_DIR/sites" ] || ! command -v bench >/dev/null 2>&1; then
  DIR="$(cd "$(dirname "$0")" && pwd)"
  exec docker compose -f "$DIR/docker-compose.yml" exec -T backend bash -c "$(cat "$0")" sao-luu.sh "$@"
fi

cd "$BENCH_DIR"
ds_site=()
if [ "$#" -gt 0 ]; then
  ds_site=("$@")
else
  for d in sites/*/; do
    [ -f "${d}site_config.json" ] || continue
    s="$(basename "$d")"
    case "$s" in
      assets|common_site_config.json|tam-khoi-phuc.local|tam-*) continue ;;
    esac
    ds_site+=("$s")
  done
fi

loi=0
for s in "${ds_site[@]}"; do
  if [ ! -f "sites/$s/site_config.json" ]; then
    echo "CANH_BAO: bo qua site $s (khong co site_config.json)" >&2
    loi=1
    continue
  fi
  if ! bench --site "$s" backup </dev/null; then
    echo "LOI: sao luu site $s that bai" >&2
    loi=1
    continue
  fi
  bdir="sites/$s/private/backups"
  if [ -d "$bdir" ]; then
    dem=$(ls -1 "$bdir"/*-database.sql.gz 2>/dev/null | wc -l || true)
    if [ "${dem:-0}" -gt "$GIU_TOI_THIEU" ]; then
      while read -r cu; do
        [ -n "$cu" ] || continue
        find "$bdir" -maxdepth 1 -name "$(basename "${cu%-database.sql.gz}")*" -mtime +7 -delete || true
      done < <(ls -1t "$bdir"/*-database.sql.gz 2>/dev/null | tail -n +"$((GIU_TOI_THIEU + 1))")
    fi
  fi
done

exit "$loi"
