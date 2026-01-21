from flask import Flask, request, jsonify
import sqlite3
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()
RUN_KEY = os.getenv("RUN_KEY")
URL_END = os.getenv("URL_END", "!tsem.com")  # default if not in .env

DB_FILE = "auth.db"
app = Flask(__name__)
CORS(app)

# ----------------- DATABASE ----------------- #
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        key TEXT NOT NULL
    )
    """)
    # Mail table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        recipient TEXT NOT NULL,
        subject TEXT,
        body TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- DATABASE HELPERS ---------------- #
def query_db(query, args=(), fetchone=False):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchone() if fetchone else cursor.fetchall()
    conn.commit()
    conn.close()
    return result

def require_run_key(func):
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-API-KEY")
        if key != RUN_KEY:
            return jsonify({"error": "Invalid API key"}), 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def require_user(func):
    """Check user using email + key (key is now password)"""
    def wrapper(*args, **kwargs):
        email = request.headers.get("X-USER-EMAIL")
        key = request.headers.get("X-USER-KEY")  # this will now be password
        if not email or not key:
            return jsonify({"error": "Missing user credentials"}), 403
        # Check user exists and password matches
        user = query_db("SELECT * FROM users WHERE email=? AND password=?", [email, key], fetchone=True)
        if not user:
            return jsonify({"error": "Invalid user credentials"}), 403
        return func(email, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ---------------- USER ROUTES ---------------- #
@app.route("/register", methods=["POST"])
@require_run_key
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if not username.endswith(URL_END):
        email = f"{username}{URL_END}"
    else:
        email = username
    # Now store password as key too
    try:
        query_db("INSERT INTO users (email, password, key) VALUES (?, ?, ?)", [email, password, password])
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 400
    return jsonify({"email": email, "key": password})

@app.route("/users", methods=["GET"])
@require_run_key
def list_users():
    users = query_db("SELECT email, key FROM users")
    return jsonify([{"email": u[0], "key": u[1]} for u in users])

# ---------------- EMAIL ROUTES ---------------- #
@app.route("/send_email", methods=["POST"])
@require_user
def send_email(user_email):
    data = request.json
    recipient = data.get("recipient")
    subject = data.get("subject", "")
    body = data.get("body", "")
    if not recipient or not body:
        return jsonify({"error": "Recipient and body required"}), 400
    # Check recipient exists
    if not query_db("SELECT * FROM users WHERE email=?", [recipient], fetchone=True):
        return jsonify({"error": "Recipient does not exist"}), 400
    query_db("INSERT INTO mail (sender, recipient, subject, body) VALUES (?, ?, ?, ?)", 
             [user_email, recipient, subject, body])
    return jsonify({"status": "Email sent", "to": recipient})

@app.route("/inbox", methods=["GET"])
@require_user
def inbox(user_email):
    mails = query_db("SELECT id, sender, subject, body, timestamp FROM mail WHERE recipient=? ORDER BY timestamp DESC", 
                     [user_email])
    emails = []
    for m in mails:
        emails.append({
            "id": m[0],
            "from": m[1],
            "subject": m[2],
            "body": m[3],
            "timestamp": m[4]
        })
    return jsonify(emails)

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
