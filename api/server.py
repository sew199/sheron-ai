import os
import secrets
import resend
import time
import random
import sqlite3
import requests

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DB_PATH = "memory/zorox.db"


def init_users_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            country TEXT NOT NULL,
            verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


GEMINI_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.8-flash:generateContent"
)


def send_otp_email(email, otp):
    params = {
        "from": "ZOROX AI <onboarding@resend.dev>",
        "to": [email],
        "subject": "Your ZOROX AI verification code",
        "html": f"""
        <div style="font-family:Arial;background:#0b0b12;color:white;padding:30px">
            <h2 style="color:#00e5ff">ZOROX AI</h2>
            <p>Your verification code is:</p>
            <h1 style="letter-spacing:8px;color:#7c4dff">{otp}</h1>
            <p>This code expires in 10 minutes.</p>
        </div>
        """
    }
    return resend.Emails.send(params)

@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}

    identifier = str(data.get("identifier", "")).strip()
    password = str(data.get("password", ""))

    if not identifier or not password:
        return jsonify({
            "error": "Email/username and password are required"
        }), 400

    conn = get_db()

    user = conn.execute(
        """
        SELECT id, email, username, password_hash, country, verified
        FROM users
        WHERE email = ? OR username = ?
        LIMIT 1
        """,
        (identifier.lower(), identifier)
    ).fetchone()

    conn.close()

    if not user:
        return jsonify({
            "error": "Invalid email/username or password"
        }), 401

    user_id, email, username, password_hash, country, verified = user

    if not check_password_hash(password_hash, password):
        return jsonify({
            "error": "Invalid email/username or password"
        }), 401

    if not verified:
        return jsonify({
            "error": "Email is not verified"
        }), 403

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user_id,
            "email": email,
            "username": username,
            "country": country
        }
    }), 200

@app.post("/api/send-otp")
def send_otp():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()

    if not email:
        return jsonify({"error": "Email is required"}), 400

    otp = f"{secrets.randbelow(1000000):06d}"
    otp_hash = generate_password_hash(otp)
    expires_at = int(time.time()) + 600

    conn = get_db()
    conn.execute("DELETE FROM email_otps WHERE email = ?", (email,))
    conn.execute("INSERT INTO email_otps (email, otp_hash, expires_at, attempts) VALUES (?, ?, ?, 0)", (email, otp_hash, expires_at))
    conn.commit()
    conn.close()

    try:
        send_otp_email(email, otp)
        return jsonify({"message": "OTP sent successfully"}), 200
    except Exception as error:
        return jsonify({"error": "Could not send OTP", "message": str(error)}), 500

@app.post("/api/verify-otp")
def verify_otp():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    otp = str(data.get("otp", "")).strip()

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    if not otp.isdigit() or len(otp) != 6:
        return jsonify({"error": "OTP must be 6 digits"}), 400

    conn = get_db()
    row = conn.execute(
        "SELECT id, otp_hash, expires_at, attempts FROM email_otps WHERE email = ? ORDER BY id DESC LIMIT 1",
        (email,)
    ).fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "OTP not found or expired"}), 404

    otp_id, otp_hash, expires_at, attempts = row

    if int(time.time()) > expires_at:
        conn.execute("DELETE FROM email_otps WHERE id = ?", (otp_id,))
        conn.commit()
        conn.close()
        return jsonify({"error": "OTP has expired"}), 400

    if attempts >= 5:
        conn.close()
        return jsonify({"error": "Too many attempts. Request a new OTP"}), 429

    if not check_password_hash(otp_hash, otp):
        conn.execute("UPDATE email_otps SET attempts = attempts + 1 WHERE id = ?", (otp_id,))
        conn.commit()
        conn.close()
        return jsonify({"error": "Invalid OTP"}), 400

    conn.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
    conn.execute("DELETE FROM email_otps WHERE id = ?", (otp_id,))
    conn.commit()

    user = conn.execute(
        "SELECT id, username FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    if not user:
        return jsonify({"error": "User account not found"}), 404

    return jsonify({
        "message": "Email verified successfully",
        "user_id": user[0],
        "username": user[1]
    }), 200

@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}

    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    country = str(data.get("country", "")).strip()

    if not email or not username or not password or not country:
        return jsonify({
            "error": "Email, username, password and country are required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    conn = get_db()

    existing = conn.execute(
        "SELECT id FROM users WHERE email = ? OR username = ?",
        (email, username)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({
            "error": "Email or username already exists"
        }), 409

    password_hash = generate_password_hash(password)

    try:
        cursor = conn.execute(
            """
            INSERT INTO users
            (phone, email, username, password_hash, country)
            VALUES (?, ?, ?, ?, ?)
            """,
            (phone or None, email, username, password_hash, country)
        )

        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "message": "Account created successfully",
            "user_id": user_id,
            "username": username
        }), 201

    except Exception as error:
        conn.close()
        return jsonify({
            "error": "Could not create account",
            "message": str(error)
        }), 500


@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "name": "ZOROX AI",
        "company": "WIKRAMASINGHE TECHNOLOGIES"
    })


def gemini_error(response):
    try:
        result = response.json()
    except ValueError:
        result = {}

    error = result.get("error", {})

    return {
        "error": "Gemini API error",
        "status": response.status_code,
        "message": error.get("message", "Unknown Gemini API error"),
        "type": error.get("status", "UNKNOWN")
    }


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({
            "error": "Message is required"
        }), 400

    if not GEMINI_API_KEY:
        return jsonify({
            "error": "Gemini API key is not configured"
        }), 500

    conn = get_db()

    conversation = conn.execute(
        "SELECT id FROM conversations ORDER BY updated_at DESC LIMIT 1"
    ).fetchone()

    if conversation:
        conversation_id = conversation["id"]
    else:
        cursor = conn.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (message[:50],)
        )
        conversation_id = cursor.lastrowid

    conn.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, "user", message)
    )
    conn.commit()

    history = conn.execute(
        """
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
        LIMIT 20
        """,
        (conversation_id,)
    ).fetchall()

    contents = []

    for item in history:
        contents.append({
            "role": item["role"],
            "parts": [
                {
                    "text": item["content"]
                }
            ]
        })

    payload = {
        "contents": contents
    }

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = requests.post(
                GEMINI_URL,
                headers={
                    "x-goog-api-key": GEMINI_API_KEY,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()

                candidates = result.get("candidates", [])

                if not candidates:
                    return jsonify({
                        "error": "Gemini returned no candidates",
                        "details": result
                    }), 502

                content = candidates[0].get("content", {})
                parts = content.get("parts", [])

                if not parts:
                    return jsonify({
                        "error": "Gemini returned no response text",
                        "details": result
                    }), 502

                reply = parts[0].get("text", "").strip()

                if not reply:
                    return jsonify({
                        "error": "Gemini returned an empty response"
                    }), 502

                conn.execute(
                    "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                    (conversation_id, "model", reply)
                )

                conn.execute(
                    "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (conversation_id,)
                )

                conn.commit()
                conn.close()

                return jsonify({
                    "reply": reply,
                    "conversation_id": conversation_id
                })

            # Retry only temporary errors
            if response.status_code in (408, 429, 500, 502, 503, 504):
                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(0, 0.5)
                    time.sleep(delay)
                    continue

            return jsonify(gemini_error(response)), response.status_code

        except requests.Timeout:
            if attempt < max_retries - 1:
                delay = (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(delay)
                continue

            return jsonify({
                "error": "Gemini request timed out",
                "message": "Please try again."
            }), 504

        except requests.RequestException as error:
            return jsonify({
                "error": "Could not connect to Gemini API",
                "message": str(error)
            }), 502

    return jsonify({
        "error": "Gemini service is temporarily unavailable",
        "message": "Please try again in a moment."
    }), 503


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
