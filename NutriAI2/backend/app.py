import sqlite3
import re
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
CORS(app)

PROFILE_STORE = {}
DB_PATH = Path(__file__).with_name("nutriai.db")
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

MOCK_PRODUCTS = {
    "012345678905": {
        "barcode": "012345678905",
        "name": "Example Granola Bar",
        "nutrition": {
            "calories": 210,
            "protein_g": 6,
            "fiber_g": 4,
            "sugar_g": 14,
            "sodium_mg": 180,
            "sat_fat_g": 2,
        },
    },
    "4902430780015": {
        "barcode": "4902430780015",
        "name": "Plain Greek Yogurt Cup",
        "nutrition": {
            "calories": 120,
            "protein_g": 15,
            "fiber_g": 0,
            "sugar_g": 6,
            "sodium_mg": 55,
            "sat_fat_g": 2,
        },
    },
    "7622210449283": {
        "barcode": "7622210449283",
        "name": "Chocolate Cookie Pack",
        "nutrition": {
            "calories": 260,
            "protein_g": 3,
            "fiber_g": 1,
            "sugar_g": 22,
            "sodium_mg": 240,
            "sat_fat_g": 6,
        },
    },
}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
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
    finally:
        conn.close()


def calculate_score(goal, nutrition):
    score = 70
    reasons = []
    breakdown = {
        "sugarPenalty": 0,
        "fiberBonus": 0,
        "proteinBonus": 0,
        "sodiumPenalty": 0,
        "goalAdjustment": 0,
    }

    sugar = float(nutrition.get("sugar_g", 0))
    fiber = float(nutrition.get("fiber_g", 0))
    protein = float(nutrition.get("protein_g", 0))
    sodium = float(nutrition.get("sodium_mg", 0))
    calories = float(nutrition.get("calories", 0))

    if sugar > 20:
        score -= 20
        breakdown["sugarPenalty"] = -20
        reasons.append("Sugar is high for a single serving.")
    elif sugar > 12:
        score -= 12
        breakdown["sugarPenalty"] = -12
        reasons.append("Sugar is above preferred threshold.")

    if fiber >= 5:
        score += 10
        breakdown["fiberBonus"] = 10
        reasons.append("Fiber is strong and supports satiety.")
    elif fiber >= 3:
        score += 6
        breakdown["fiberBonus"] = 6
        reasons.append("Fiber is moderate and helpful.")

    if protein >= 15:
        score += 12
        breakdown["proteinBonus"] = 12
        reasons.append("Protein content is high.")
    elif protein >= 8:
        score += 6
        breakdown["proteinBonus"] = 6
        reasons.append("Protein content is moderate.")

    if sodium > 300:
        score -= 10
        breakdown["sodiumPenalty"] = -10
        reasons.append("Sodium is high.")
    elif sodium > 200:
        score -= 5
        breakdown["sodiumPenalty"] = -5
        reasons.append("Sodium is moderately high.")

    goal = (goal or "maintain").lower()
    if goal == "lose":
        if calories > 250:
            score -= 10
            breakdown["goalAdjustment"] -= 10
            reasons.append("Calories are high for a fat-loss goal.")
        if sugar > 12:
            score -= 5
            breakdown["goalAdjustment"] -= 5
            reasons.append("Sugar is less ideal for fat-loss.")
    elif goal == "gain":
        if protein >= 12:
            score += 5
            breakdown["goalAdjustment"] += 5
            reasons.append("Protein supports a muscle-gain goal.")
        if calories >= 220:
            score += 3
            breakdown["goalAdjustment"] += 3
            reasons.append("Calories support a gain-focused target.")

    score = max(0, min(100, int(round(score))))
    if score >= 80:
        decision = "good"
    elif score >= 50:
        decision = "moderate"
    else:
        decision = "poor"

    if not reasons:
        reasons.append("This item is nutritionally balanced for a general goal.")

    return {
        "score": score,
        "decision": decision,
        "reasons": reasons,
        "ruleBreakdown": breakdown,
    }


def make_explanation(goal, product_name, score, decision, reasons, nutrition):
    joined_reasons = "; ".join(reasons[:3])
    return (
        f"{product_name} scored {score}/100 and is rated {decision} for your {goal} goal. "
        f"Main factors: {joined_reasons}. "
        f"Nutrition snapshot: {nutrition.get('calories', 0)} kcal, "
        f"{nutrition.get('protein_g', 0)}g protein, {nutrition.get('sugar_g', 0)}g sugar, "
        f"{nutrition.get('fiber_g', 0)}g fiber."
    )


init_db()


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "message": "NutriAI backend running"})


@app.post("/api/auth/signup")
def signup():
    data = request.get_json(force=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return jsonify({"ok": False, "error": "Missing fields: ['name', 'email', 'password']"}), 400

    if not EMAIL_REGEX.fullmatch(email):
        return jsonify({"ok": False, "error": "Invalid email format"}), 400

    if len(password) < 6:
        return jsonify({"ok": False, "error": "Password must be at least 6 characters"}), 400

    password_hash = generate_password_hash(password)

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"ok": False, "error": "Email already registered"}), 409
    finally:
        conn.close()

    return jsonify({"ok": True, "message": "Account created", "user": {"name": name, "email": email}})


@app.post("/api/auth/login")
def login():
    data = request.get_json(force=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return jsonify({"ok": False, "error": "Missing fields: ['email', 'password']"}), 400

    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    finally:
        conn.close()

    if row is None or not check_password_hash(row[3], password):
        return jsonify({"ok": False, "error": "Invalid email or password"}), 401

    return jsonify(
        {
            "ok": True,
            "message": "Login successful",
            "user": {"id": row[0], "name": row[1], "email": row[2]},
        }
    )


@app.post("/api/product/lookup")
def lookup_product():
    data = request.get_json(force=True) or {}
    barcode = str(data.get("barcode", "")).strip()

    if not barcode:
        return jsonify({"ok": False, "error": "Missing required field: barcode"}), 400

    product = MOCK_PRODUCTS.get(barcode)
    if not product:
        return jsonify({"ok": False, "error": "Unknown barcode"}), 404

    return jsonify({"ok": True, "product": product})


@app.post("/api/score")
def score_route():
    data = request.get_json(force=True) or {}
    goal = data.get("goal", "maintain")
    product = data.get("product")

    if not isinstance(product, dict):
        return jsonify({"ok": False, "error": "Missing required field: product"}), 400

    nutrition = product.get("nutrition")
    if not isinstance(nutrition, dict):
        return jsonify({"ok": False, "error": "Missing required field: product.nutrition"}), 400

    result = calculate_score(goal, nutrition)
    return jsonify({"ok": True, **result})


@app.post("/api/explain")
def explain_route():
    data = request.get_json(force=True) or {}
    goal = data.get("goal", "maintain")
    product_name = data.get("productName", "this item")
    score = data.get("score")
    decision = data.get("decision")
    reasons = data.get("reasons")
    nutrition = data.get("nutrition")

    if score is None or not decision or not isinstance(reasons, list) or not isinstance(nutrition, dict):
        return jsonify({"ok": False, "error": "Missing required explanation fields"}), 400

    explanation = make_explanation(goal, product_name, score, decision, reasons, nutrition)
    return jsonify({"ok": True, "explanation": explanation})


@app.post("/api/scan/evaluate")
def scan_evaluate():
    data = request.get_json(force=True) or {}
    barcode = str(data.get("barcode", "")).strip()
    goal = str(data.get("goal", "maintain")).strip() or "maintain"

    if not barcode:
        return jsonify({"ok": False, "error": "Missing required field: barcode"}), 400

    product = MOCK_PRODUCTS.get(barcode)
    if not product:
        return jsonify({"ok": False, "error": "Unknown barcode"}), 404

    scoring = calculate_score(goal, product["nutrition"])
    explanation = make_explanation(
        goal,
        product["name"],
        scoring["score"],
        scoring["decision"],
        scoring["reasons"],
        product["nutrition"],
    )

    return jsonify(
        {
            "ok": True,
            "product": product,
            "score": scoring["score"],
            "decision": scoring["decision"],
            "reasons": scoring["reasons"],
            "ruleBreakdown": scoring["ruleBreakdown"],
            "explanation": explanation,
        }
    )


@app.post("/api/profile")
def save_profile():
    data = request.get_json(force=True) or {}

    required = ["goal", "dietaryPreference", "activityLevel", "mealsPerDay"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"ok": False, "error": f"Missing fields: {missing}"}), 400

    PROFILE_STORE["profile"] = data
    return jsonify({"ok": True, "saved": data})


@app.get("/api/profile")
def get_profile():
    profile = PROFILE_STORE.get("profile")
    if not profile:
        return jsonify({"ok": False, "error": "No profile saved yet"}), 404
    return jsonify({"ok": True, "profile": profile})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
