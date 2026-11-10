#!/usr/bin/env bash
# Đồng bộ giao diện BU từ nhánh main của repo lên VM:
# - Kéo origin/main vào kho riêng /var/lib/linhx-giao-dien/repo (chỉ đọc cho www-data)
# - Sinh unit systemd linhx-giao-dien-<bu>.service và khối Caddyfile từ giao_dien.py
# - Chỉ nạp lại systemd / khởi động lại site / reload Caddy khi có thay đổi
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/usr/local/lib/linhx-giao-dien"
REPO_URL="${LINHX_REPO_URL:-https://github.com/fyzdfyzd/linhx-engine.git}"
NHANH="${LINHX_GIAO_DIEN_NHANH:-main}"
STATE_DIR="/var/lib/linhx-giao-dien"
REPO_DIR="${LINHX_GIAO_DIEN_REPO:-$STATE_DIR/repo}"
STATE_SHA_FILE="${LINHX_GIAO_DIEN_SHA_FILE:-$STATE_DIR/da-len.sha}"
VM_IP="${LINHX_VM_IP:-35.198.251.2}"
CONG_DAU="${LINHX_CONG_DAU:-8101}"
CADDY_CONTAINER="${LINHX_CADDY_CONTAINER:-linhx-engine-caddy-1}"
CADDYFILE_MAC_DINH="${LINHX_CADDYFILE:-/home/ADMIN/linhx-engine/deploy/Caddyfile}"
SYSTEMD_DIR="/etc/systemd/system"
LOCK_FILE="/run/lock/linhx-giao-dien.lock"

if [ "${1:-}" = "--cai-dat" ]; then
  install -d -m 0755 -o root -g root "$INSTALL_DIR"
  if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    install -m 0644 -o root -g root "$SCRIPT_DIR/giao_dien.py" "$INSTALL_DIR/giao_dien.py"
    install -m 0755 -o root -g root "$SCRIPT_DIR/len-giao-dien.sh" "$INSTALL_DIR/len-giao-dien.sh"
  fi
  install -m 0644 -o root -g root "$SCRIPT_DIR/linhx-giao-dien.service" "$SYSTEMD_DIR/linhx-giao-dien.service"
  install -m 0644 -o root -g root "$SCRIPT_DIR/linhx-giao-dien.timer" "$SYSTEMD_DIR/linhx-giao-dien.timer"
  systemctl daemon-reload
  systemctl enable --now linhx-giao-dien.timer
  exit 0
fi

if [[ ! "$REPO_URL" =~ ^https://[A-Za-z0-9._/-]+$ ]] || [[ "$REPO_URL" == *".."* ]]; then
  echo "LOI: LINHX_REPO_URL khong hop le: $REPO_URL" >&2
  exit 1
fi
if [[ ! "$NHANH" =~ ^[A-Za-z0-9][A-Za-z0-9._/-]*$ ]] || [[ "$NHANH" == *".."* ]]; then
  echo "LOI: LINHX_GIAO_DIEN_NHANH khong hop le: $NHANH" >&2
  exit 1
fi
if [[ ! "$CONG_DAU" =~ ^[0-9]+$ ]] || [ "$CONG_DAU" -lt 1024 ] || [ "$CONG_DAU" -gt 65000 ]; then
  echo "LOI: LINHX_CONG_DAU khong hop le: $CONG_DAU" >&2
  exit 1
fi

mkdir -p "$(dirname "$LOCK_FILE")"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "linhx-giao-dien: đang có lượt đồng bộ khác chạy, bỏ qua."
  exit 0
fi

TMP_DIR="$(mktemp -d)"
don_tam() {
  rm -rf "$TMP_DIR"
}
trap don_tam EXIT

git_an_toan() {
  GIT_TERMINAL_PROMPT=0 git \
    -c core.hooksPath=/dev/null \
    -c core.fsmonitor=false \
    -c protocol.allow=never \
    -c protocol.https.allow=always \
    "$@"
}

install -d -m 0755 -o root -g root "$(dirname "$REPO_DIR")"
APPLIED_SHA=""
if [ -f "$STATE_SHA_FILE" ] && [ ! -L "$STATE_SHA_FILE" ]; then
  SHA_DOC="$(tr -d '[:space:]' < "$STATE_SHA_FILE" || true)"
  if [[ "$SHA_DOC" =~ ^[0-9a-f]{40}$ ]]; then
    APPLIED_SHA="$SHA_DOC"
  fi
fi

if [ ! -d "$REPO_DIR/.git" ] || [ -L "$REPO_DIR" ]; then
  rm -rf "$REPO_DIR"
  git_an_toan clone --branch "$NHANH" --single-branch -- "$REPO_URL" "$REPO_DIR"
else
  git_an_toan -C "$REPO_DIR" remote set-url origin -- "$REPO_URL"
  git_an_toan -C "$REPO_DIR" fetch --prune origin "+refs/heads/$NHANH:refs/remotes/origin/$NHANH"
  git_an_toan -C "$REPO_DIR" checkout -f -B "$NHANH" "refs/remotes/origin/$NHANH"
  git_an_toan -C "$REPO_DIR" reset --hard "refs/remotes/origin/$NHANH"
  git_an_toan -C "$REPO_DIR" clean -fdx
fi
NEW_SHA="$(git_an_toan -C "$REPO_DIR" rev-parse HEAD)"

chmod 0755 "$REPO_DIR"
if [ -d "$REPO_DIR/giao-dien" ] && [ ! -L "$REPO_DIR/giao-dien" ]; then
  find -P "$REPO_DIR/giao-dien" -not -type l -type d -exec chmod 0755 {} +
  find -P "$REPO_DIR/giao-dien" -not -type l -type f -exec chmod 0644 {} +
fi

GIAO_DIEN_PY="$SCRIPT_DIR/giao_dien.py"
if [ ! -f "$GIAO_DIEN_PY" ] && [ -f "$INSTALL_DIR/giao_dien.py" ]; then
  GIAO_DIEN_PY="$INSTALL_DIR/giao_dien.py"
fi

DICH="127.0.0.1"
CADDYFILE="$CADDYFILE_MAC_DINH"
DUNG_DOCKER_CADDY=0
if command -v docker >/dev/null 2>&1 && docker inspect "$CADDY_CONTAINER" >/dev/null 2>&1; then
  DUNG_DOCKER_CADDY=1
  THONG_TIN_CADDY="$(
    docker inspect "$CADDY_CONTAINER" | python3 -c '
import json, sys
d = json.load(sys.stdin)[0]
net_mode = d.get("HostConfig", {}).get("NetworkMode", "")
gw = "127.0.0.1"
if net_mode != "host":
    for v in (d.get("NetworkSettings", {}).get("Networks") or {}).values():
        if v.get("Gateway"):
            gw = v["Gateway"]
            break
cf = ""
for m in d.get("Mounts") or []:
    if m.get("Destination") == "/etc/caddy/Caddyfile" and m.get("Source"):
        cf = m["Source"]
        break
print(gw + "\t" + cf)
'
  )"
  DICH_TU_DOCKER="${THONG_TIN_CADDY%%$'\t'*}"
  CF_TU_DOCKER="${THONG_TIN_CADDY#*$'\t'}"
  if [ -n "$DICH_TU_DOCKER" ]; then
    DICH="$DICH_TU_DOCKER"
  fi
  if [ -n "$CF_TU_DOCKER" ]; then
    CADDYFILE="$CF_TU_DOCKER"
  fi
elif [ -f "/etc/caddy/Caddyfile" ]; then
  CADDYFILE="/etc/caddy/Caddyfile"
fi

DAEMON_RELOAD=0
declare -A CON_SITE=()
declare -A CAN_KHOI_DONG_LAI=()
declare -A CONG_SITE=()

while IFS=$'\t' read -r ten cong thu_muc; do
  [ -n "$ten" ] || continue
  CON_SITE["$ten"]=1
  CONG_SITE["$ten"]="$cong"
  UNIT_NAME="linhx-giao-dien-${ten}.service"
  UNIT_PATH="$SYSTEMD_DIR/$UNIT_NAME"
  UNIT_TMP="$TMP_DIR/$UNIT_NAME"

  python3 "$GIAO_DIEN_PY" systemd --goc "$REPO_DIR" --ten "$ten" --cong-dau "$CONG_DAU" > "$UNIT_TMP"

  if [ ! -f "$UNIT_PATH" ] || ! cmp -s "$UNIT_TMP" "$UNIT_PATH"; then
    install -m 0644 -o root -g root "$UNIT_TMP" "$UNIT_PATH"
    DAEMON_RELOAD=1
    CAN_KHOI_DONG_LAI["$ten"]=1
  fi

  if [ -z "$APPLIED_SHA" ]; then
    CAN_KHOI_DONG_LAI["$ten"]=1
  elif [ "$APPLIED_SHA" != "$NEW_SHA" ]; then
    if ! git_an_toan -C "$REPO_DIR" cat-file -e "${APPLIED_SHA}^{commit}" 2>/dev/null || \
       ! git_an_toan -C "$REPO_DIR" diff --quiet "$APPLIED_SHA" "$NEW_SHA" -- "giao-dien/$ten" 2>/dev/null; then
      CAN_KHOI_DONG_LAI["$ten"]=1
    fi
  fi
done < <(python3 "$GIAO_DIEN_PY" cac-site --goc "$REPO_DIR" --cong-dau "$CONG_DAU")

for f in "$SYSTEMD_DIR"/linhx-giao-dien-*.service; do
  [ -e "$f" ] || continue
  base="$(basename "$f")"
  [ "$base" != "linhx-giao-dien.service" ] || continue
  ten_cu="${base#linhx-giao-dien-}"
  ten_cu="${ten_cu%.service}"
  if [ -z "${CON_SITE[$ten_cu]:-}" ]; then
    systemctl disable --now "$base" >/dev/null 2>&1 || true
    rm -f "$f"
    DAEMON_RELOAD=1
  fi
done

if [ "$DAEMON_RELOAD" -eq 1 ]; then
  systemctl daemon-reload
fi

for ten in $(printf '%s\n' "${!CON_SITE[@]}" | sort); do
  UNIT_NAME="linhx-giao-dien-${ten}.service"
  cong="${CONG_SITE[$ten]}"
  if ! systemctl is-enabled --quiet "$UNIT_NAME"; then
    systemctl enable "$UNIT_NAME" >/dev/null
  fi
  if [ -n "${CAN_KHOI_DONG_LAI[$ten]:-}" ] || ! systemctl is-active --quiet "$UNIT_NAME"; then
    systemctl restart "$UNIT_NAME"
  fi
  ok_cong=0
  for _ in $(seq 1 30); do
    if curl -fsS --max-time 2 "http://127.0.0.1:${cong}/" >/dev/null 2>&1; then
      ok_cong=1
      break
    fi
    sleep 0.5
  done
  if [ "$ok_cong" -ne 1 ]; then
    echo "LOI: $UNIT_NAME không phản hồi 200 trên cổng $cong" >&2
    exit 1
  fi
done

CADDY_TMP="$TMP_DIR/Caddyfile.moi"
python3 "$GIAO_DIEN_PY" ghep-caddy \
  --caddyfile "$CADDYFILE" \
  --goc "$REPO_DIR" \
  --ip "$VM_IP" \
  --cong-dau "$CONG_DAU" \
  --dich "$DICH" > "$CADDY_TMP"

if [ ! -f "$CADDYFILE" ] || ! cmp -s "$CADDY_TMP" "$CADDYFILE"; then
  if [ "$DUNG_DOCKER_CADDY" -eq 1 ]; then
    docker exec -i "$CADDY_CONTAINER" caddy validate --config - --adapter caddyfile < "$CADDY_TMP" >/dev/null
  elif command -v caddy >/dev/null 2>&1; then
    caddy validate --config "$CADDY_TMP" --adapter caddyfile >/dev/null
  fi

  CADDY_BAK="$TMP_DIR/Caddyfile.bak"
  if [ -f "$CADDYFILE" ]; then
    cp -p "$CADDYFILE" "$CADDY_BAK"
  fi
  # Ghi đè tại chỗ để giữ nguyên inode bind-mount của container Caddy
  cat "$CADDY_TMP" > "$CADDYFILE"

  nap_ok=1
  if [ "$DUNG_DOCKER_CADDY" -eq 1 ]; then
    docker exec "$CADDY_CONTAINER" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile || nap_ok=0
  elif systemctl is-active --quiet caddy; then
    systemctl reload caddy || nap_ok=0
  fi

  if [ "$nap_ok" -ne 1 ]; then
    if [ -f "$CADDY_BAK" ]; then
      cat "$CADDY_BAK" > "$CADDYFILE"
    fi
    echo "LOI: reload Caddy thất bại, đã khôi phục Caddyfile cũ" >&2
    exit 1
  fi
fi

install -d -m 0755 -o root -g root "$(dirname "$STATE_SHA_FILE")"
printf '%s\n' "$NEW_SHA" > "$TMP_DIR/da-len.sha"
install -m 0644 -o root -g root "$TMP_DIR/da-len.sha" "$STATE_SHA_FILE"

echo "linhx-giao-dien: xong commit=$NEW_SHA sites=${#CON_SITE[@]} dich=$DICH"
