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
RUN echo '#!/bin/bash\n\
service mysql start\n\
mysql -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME};"\n\
mysql -e "CREATE USER IF NOT EXISTS '"'"'${DB_USER}'"'"'@'"'"'localhost'"'"' IDENTIFIED BY '"'"'${DB_PASSWORD}'"'"';"\n\
mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '"'"'${DB_USER}'"'"'@'"'"'localhost'"'"';"\n\
mysql -e "FLUSH PRIVILEGES;"\n\
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
