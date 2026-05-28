import os
from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    # Safely fetches configurations strictly from the system environment rules
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', '127.0.0.1'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        db_version = cursor.fetchone()
        cursor.close()
        conn.close()
        status = f"Successfully authenticated to secure database isolation layout. MySQL Version: {db_version}"
    except Exception as e:
        status = f"Database authentication layout failure: {str(e)}"
    
    return render_template('index.html', status=status)

if __name__ == '__main__':
    port = int(os.environ.get('APP_PORT', 5000))
    app.run(host='0.0.0.0', port=port)
