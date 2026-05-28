#!/bin/bash
set -e

echo "[entrypoint] Starting MySQL..."
service mysql start

echo "[entrypoint] Waiting for MySQL to be ready..."
until mysqladmin ping --silent; do sleep 1; done

echo "[entrypoint] Setting up database and user..."
mysql -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME};"
mysql -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';"
mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

echo "[entrypoint] DB setup complete. Starting supervisord..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
