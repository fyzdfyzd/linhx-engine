#!/usr/bin/env bash
# Sao lưu DB hằng ngày cho từng site Frappe, giữ tối thiểu 7 bản mỗi site.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
GIU_TOI_THIEU="${GIU_TOI_THIEU:-7}"

sao_luu_trong_bench() {
  local bench_dir="${1:-/home/frappe/frappe-bench}"
  cd "$bench_dir"
  local ds_site=()
  if [ "$#" -gt 1 ]; then
    shift
    ds_site=("$@")
  else
    for d in sites/*/; do
      [ -f "${d}site_config.json" ] || continue
      local s
      s="$(basename "$d")"
      case "$s" in
        assets|common_site_config.json|tam*|*restore*|*test*) continue ;;
      esac
      ds_site+=("$s")
    done
  fi

  for s in "${ds_site[@]}"; do
    [ -f "sites/$s/site_config.json" ] || continue
    bench --site "$s" backup </dev/null
    local bdir="sites/$s/private/backups"
    if [ -d "$bdir" ]; then
      local dem
      dem=$(ls -1 "$bdir"/*-database.sql.gz 2>/dev/null | wc -l || true)
      if [ "${dem:-0}" -gt "$GIU_TOI_THIEU" ]; then
        ls -1t "$bdir"/*-database.sql.gz 2>/dev/null | tail -n +"$((GIU_TOI_THIEU + 1))" | while read -r cu; do
          [ -n "$cu" ] || continue
          find "$bdir" -maxdepth 1 -name "$(basename "${cu%-database.sql.gz}")*" -mtime +7 -delete || true
        done
      fi
    fi
  done
}

if [ -d "/home/frappe/frappe-bench/sites" ] && command -v bench >/dev/null 2>&1; then
  sao_luu_trong_bench "/home/frappe/frappe-bench" "$@"
else
  docker compose -f "$DIR/docker-compose.yml" exec -T backend bash -s -- "$@" <<'EOF'
set -euo pipefail
GIU_TOI_THIEU="${GIU_TOI_THIEU:-7}"
cd /home/frappe/frappe-bench
if [ "$#" -gt 0 ]; then
  ds_site=("$@")
else
  ds_site=()
  for d in sites/*/; do
    [ -f "${d}site_config.json" ] || continue
    s="$(basename "$d")"
    case "$s" in
      assets|tam*|*restore*|*test*) continue ;;
    esac
    ds_site+=("$s")
  done
fi
for s in "${ds_site[@]}"; do
  [ -f "sites/$s/site_config.json" ] || continue
  bench --site "$s" backup </dev/null
  bdir="sites/$s/private/backups"
  if [ -d "$bdir" ]; then
    dem=$(ls -1 "$bdir"/*-database.sql.gz 2>/dev/null | wc -l || true)
    if [ "${dem:-0}" -gt "$GIU_TOI_THIEU" ]; then
      ls -1t "$bdir"/*-database.sql.gz 2>/dev/null | tail -n +"$((GIU_TOI_THIEU + 1))" | while read -r cu; do
        [ -n "$cu" ] || continue
        find "$bdir" -maxdepth 1 -name "$(basename "${cu%-database.sql.gz}")*" -mtime +7 -delete || true
      done
    fi
  fi
done
EOF
fi
