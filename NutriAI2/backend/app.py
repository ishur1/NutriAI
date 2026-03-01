import sqlite3
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app)
# Temporary in-memory profile storage (resets when server restarts).
PROFILE_STORE = {}
# SQLite file lives next to this backend file.
DB_PATH = Path(__file__).with_name("nutriai.db")


def get_db_connection():
    # Open a new DB connection per request/helper call.
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dict-like objects (row["column_name"]).
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Create users table once if it does not exist yet.
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
        """
            CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            goal TEXT NOT NULL,
            dietary_preference TEXT NOT NULL,
            activity_level TEXT NOT NULL,
            meals_per_day INTEGER NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
        conn.commit()


# Ensure database/table exist on backend startup.
init_db()


@app.get("/api/health")
def health():
    # Lightweight health check endpoint for frontend/testing.
    return jsonify({"ok": True, "message": "NutriAI backend running"})


@app.post("/api/auth/signup")
def signup():
    # Parse JSON body from signup request.
    data = request.get_json(force=True)

    # Validate required fields are present and non-empty.
    required = ["name", "email", "password"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"ok": False, "error": f"Missing fields: {missing}"}), 400

    # Normalize text inputs before saving.
    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    # Minimal password rule for basic account quality.
    if len(password) < 6:
        return jsonify({"ok": False, "error": "Password must be at least 6 characters"}), 400

    # Never store plain-text passwords.
    password_hash = generate_password_hash(password)

    try:
        with get_db_connection() as conn:
            # Insert user record; email is unique.
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        # Raised when email already exists due to UNIQUE constraint.
        return jsonify({"ok": False, "error": "Email already registered"}), 409

    return jsonify({"ok": True, "message": "Account created", "user": {"name": name, "email": email}})


@app.post("/api/auth/login")
def login():
    # Parse JSON body from login request.
    data = request.get_json(force=True)

    # Validate login fields.
    required = ["email", "password"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"ok": False, "error": f"Missing fields: {missing}"}), 400

    # Normalize input so email comparison is consistent.
    email = data["email"].strip().lower()
    password = data["password"]

    with get_db_connection() as conn:
        # Find user by email.
        row = conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    # Reject unknown email or incorrect password.
    if row is None or not check_password_hash(row["password_hash"], password):
        return jsonify({"ok": False, "error": "Invalid email or password"}), 401

    # Return basic user profile data (no password hash).
    return jsonify(
        {
            "ok": True,
            "message": "Login successful",
            "user": {"id": row["id"], "name": row["name"], "email": row["email"]},
        }
    )


@app.post("/api/profile")
def save_profile():
    # Parse JSON payload for personalization settings.
    data = request.get_json(force=True)

    # Ensure required profile fields exist.
    required = ["goal", "dietaryPreference", "activityLevel", "mealsPerDay"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"ok": False, "error": f"Missing fields: {missing}"}), 400

    # Save profile in memory for now (not persisted to DB yet).
    PROFILE_STORE["profile"] = data
    return jsonify({"ok": True, "saved": data})


@app.get("/api/profile")
def get_profile():
    # Return latest saved profile if present.
    profile = PROFILE_STORE.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "No profile saved yet"}), 404
    return jsonify({"ok": True, "profile": profile})


if __name__ == "__main__":
    # Start Flask dev server on port 5000.
    app.run(port=5000, debug=True)
