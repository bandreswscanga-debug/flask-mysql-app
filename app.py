import os
import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "servidor-bd-ejemplo")
DB_USER = os.environ.get("DB_USER", "usuario_ejemplo")
DB_PASS = os.environ.get("DB_PASS", "contraseña_ejemplo")
DB_NAME = os.environ.get("DB_NAME", "base_ejemplo")


def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.route("/")
def index():
    return jsonify({"status": "API funcionando correctamente"}), 200


@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@app.route("/api/data")
def get_data():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS resultado")
            result = cursor.fetchone()
        conn.close()
        return jsonify({"data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # nosec B104 - needed for container/bridge networking
    app.run(host="0.0.0.0", port=5000, debug=False)
