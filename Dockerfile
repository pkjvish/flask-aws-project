FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV APP_PORT=5000

# Install system dependencies including build tools for mysqlclient
RUN apt-get update && apt-get install -y \
    mysql-server \
    python3 \
    python3-pip \
    supervisor \
    libmysqlclient-dev \
    pkg-config \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Setup application environment tracking dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]