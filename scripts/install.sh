#!/usr/bin/env bash
set -euo pipefail

echo "JD-Mobile installer (Docker Compose)"
echo

default_dir="/mnt/tank/apps/jd-mobile/config"
read -r -p "Host config directory (persistent) [${default_dir}]: " host_dir
host_dir="${host_dir:-$default_dir}"

read -r -p "Host UI port [8086]: " ui_port
ui_port="${ui_port:-8086}"

if [[ ! -d "$host_dir" ]]; then
  echo "Creating: $host_dir"
  mkdir -p "$host_dir"
fi

cat > .env <<EOF
JD_MOBILE_HOST_CONFIG_DIR=$host_dir
JD_MOBILE_PORT=$ui_port
JD_MOBILE_CONFIG_PATH=/app/config/config.json
EOF

echo
echo "Wrote .env:"
cat .env
echo
echo "Starting container..."
docker compose up -d --build
echo
echo "Open: http://localhost:${ui_port}"
echo "Then complete setup at /setup."
