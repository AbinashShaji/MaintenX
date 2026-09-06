from flask import Flask, jsonify, render_template
from config import Config
from database.connection import get_db_connection

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'maintenx-super-secret-key-for-development-only'


# Register Blueprints
from blueprints.auth import auth_bp
from blueprints.user import user_bp
from blueprints.staff import staff_bp
from blueprints.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(admin_bp)

# --- Public Routes ---

@app.route('/')
def home():
    return render_template('public/home.html')

@app.route('/about')
def about():
    return render_template('public/about.html')

@app.route('/services')
def services():
    return render_template('public/services.html')

@app.route('/reviews')
def reviews():
    return render_template('public/reviews.html')

# --- Health Check ---

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health endpoint to verify that the Flask app is running
    and can successfully connect to the SQLite database.
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({
            "status": "error",
            "database": "disconnected"
        }), 503

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        if result and result[0] == 1:
            return jsonify({
                "status": "ok",
                "database": "connected"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "database": "unexpected_result"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "query_failed"
        }), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
