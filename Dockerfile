FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    mysql-server \
    python3 \
    python3-pip \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Setup application environment tracking dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Shell script to dynamically set up MySQL with environment variables at runtime
RUN printf '#!/bin/bash\nset -e\n\
echo "[entrypoint] Starting MySQL..."\n\
service mysql start\n\
echo "[entrypoint] Waiting for MySQL to be ready..."\n\
until mysqladmin ping --silent; do sleep 1; done\n\
echo "[entrypoint] Setting up database and user..."\n\
mysql -e "CREATE DATABASE IF NOT EXISTS \${DB_NAME};"\n\
mysql -e "CREATE USER IF NOT EXISTS \x27\${DB_USER}\x27@\x27localhost\x27 IDENTIFIED BY \x27\${DB_PASSWORD}\x27;"\n\
mysql -e "GRANT ALL PRIVILEGES ON \${DB_NAME}.* TO \x27\${DB_USER}\x27@\x27localhost\x27;"\n\
mysql -e "FLUSH PRIVILEGES;"\n\
echo "[entrypoint] DB setup complete. Starting supervisord..."\n\
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf\n' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
