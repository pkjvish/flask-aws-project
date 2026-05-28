import os
import logging
from flask import Flask, render_template, jsonify
import mysql.connector

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)

app = Flask(__name__)

def get_db_connection():
    host     = os.environ.get('DB_HOST', '127.0.0.1')
    user     = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    database = os.environ.get('DB_NAME')
    log.debug(f"DB connect → host={host} user={user} db={database}")
    return mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )

# ALB health check endpoint — never touches DB so it always returns 200
@app.route('/health')
def health():
    log.debug("Health check hit")
    return jsonify(status='ok'), 200

@app.route('/')
def index():
    log.info("Index route hit")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        db_version = cursor.fetchone()
        cursor.close()
        conn.close()
        status = f"Successfully authenticated to secure database isolation layout. MySQL Version: {db_version}"
        log.info(f"DB query success: {db_version}")
    except Exception as e:
        log.error(f"DB connection failed: {e}")
        status = f"Database authentication layout failure: {str(e)}"
    return render_template('index.html', status=status)

if __name__ == '__main__':
    port = int(os.environ.get('APP_PORT', 5000))
    log.info(f"Starting Flask on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
