#!/usr/bin/env bash
# Dựng Frappe bench v15 trong WSL Ubuntu trên máy cty cho thợ cài thật (N3, A1, B1...). Chạy lại được nhiều lần.
# Gọi (từ Windows): wsl -d Ubuntu -u root -- bash /mnt/d/LINHX/LINHX-ENGINE/canh/dung-bench.sh
# Kết quả: user "frappe", bench ở /home/frappe/frappe-bench, site "test" (Administrator mật khẩu admin, chỉ dùng cục bộ),
#          user thường kiem@test.local (mật khẩu kiem-thuong-123) để kiểm "ẩn khỏi API" qua HTTP.
# Distro "Ubuntu" trên máy cty là 26.04 (python3 hệ thống 3.14, apt không có 3.12): Python 3.12 lấy qua uv (bench init --python), Node 18 qua nodesource.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
echo "== $(date -Is) bắt đầu dựng bench"
apt-get update -q
apt-get install -yq git curl ca-certificates build-essential pkg-config python3-dev python3-venv python3-pip pipx \
  mariadb-server mariadb-client libmariadb-dev redis-server xvfb libfontconfig1 cron sudo rsync
if ! command -v node >/dev/null || [ "$(node -v | cut -c2-3)" != "18" ]; then
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
  apt-get install -yq nodejs
fi
npm i -g yarn >/dev/null 2>&1 || true

# MariaDB utf8mb4, root dùng mật khẩu cục bộ (chỉ trong WSL)
cat >/etc/mysql/mariadb.conf.d/99-frappe.cnf <<'EOF'
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
[mysql]
default-character-set = utf8mb4
EOF
service mariadb restart || service mysql restart
mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('root-wsl-cuc-bo'); FLUSH PRIVILEGES;" 2>/dev/null \
  || mysql -uroot -proot-wsl-cuc-bo -e "SELECT 1" >/dev/null
service redis-server start || true

id frappe >/dev/null 2>&1 || useradd -m -s /bin/bash frappe
echo "frappe ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/frappe

sudo -iu frappe bash <<'EOF'
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12
PY312="$(uv python find 3.12)"
"$PY312" --version
command -v bench >/dev/null || pipx install --python "$PY312" frappe-bench
grep -q '.local/bin' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
if [ ! -d ~/frappe-bench/apps/frappe ]; then
  bench init --frappe-branch version-15 --python "$PY312" --skip-redis-config-generation ~/frappe-bench
fi
cd ~/frappe-bench
bench set-config -g redis_cache redis://127.0.0.1:6379 && bench set-config -g redis_queue redis://127.0.0.1:6379 && bench set-config -g redis_socketio redis://127.0.0.1:6379
if [ ! -d sites/test ]; then
  bench new-site test --admin-password admin --mariadb-root-password root-wsl-cuc-bo --mariadb-user-host-login-scope='%'
fi
bench --site test set-config allow_tests true
bench use test
bench --site test execute frappe.client.insert --kwargs '{"doc": {"doctype": "User", "email": "kiem@test.local", "first_name": "Kiem", "new_password": "kiem-thuong-123", "send_welcome_email": 0, "user_type": "System User"}}' >/dev/null 2>&1 || true
echo "frappe $(bench version 2>/dev/null | grep -i frappe)"
EOF
echo "== $(date -Is) xong: bench /home/frappe/frappe-bench, site test"
