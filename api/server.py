import os
import time
import random
import sqlite3
import logging
import requests

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# =========================================================
# ZOROX AI - CLEAN BACKEND
# WIKRAMASINGHE TECHNOLOGIES
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")
DB_FILE = os.path.join(BASE_DIR, "zorox.db")

load_dotenv(dotenv_path=ENV_FILE)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("zorox")

app = Flask(__name__)
CORS(app)

# =========================================================
# CONFIG
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
JAMENDO_CLIENT_ID = os.getenv("JAMENDO_CLIENT_ID", "").strip()

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"

# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            country TEXT NOT NULL,
            verified INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# GROQ
# =========================================================

def groq_chat(message, history=None):
    if not GROQ_API_KEY:
        return None

    messages = [
        {
            "role": "system",
            "content": (
                "You are ZOROX AI, an AI assistant created by "
                "WIKRAMASINGHE TECHNOLOGIES. "
                "Be helpful, clear and friendly."
            )
        }
    ]

    if history:
        for item in history:
            role = item["role"]

            if role not in ("user", "assistant"):
                continue

            messages.append({
                "role": role,
                "content": item["content"]
            })

    messages.append({
        "role": "user",
        "content": message
    })

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2048
            },
            timeout=60
        )

        if response.status_code != 200:
            logger.error(
                "Groq HTTP %s: %s",
                response.status_code,
                response.text[:500]
            )
            return None

        data = response.json()

        choices = data.get("choices", [])

        if not choices:
            return None

        return (
            choices[0]
            .get("message", {})
            .get("content", "")
            .strip()
        ) or None

    except Exception:
        logger.exception("Groq request failed")
        return None


# =========================================================
# GEMINI
# =========================================================

def gemini_chat(history):
    if not GEMINI_API_KEY:
        return None

    contents = []

    for item in history:
        role = "model" if item["role"] == "assistant" else "user"

        contents.append({
            "role": role,
            "parts": [
                {
                    "text": item["content"]
                }
            ]
        })

    try:
        response = requests.post(
            GEMINI_URL,
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "contents": contents
            },
            timeout=60
        )

        if response.status_code != 200:
            logger.warning(
                "Gemini HTTP %s",
                response.status_code
            )
            return None

        data = response.json()

        candidates = data.get("candidates", [])

        if not candidates:
            return None

        parts = candidates[0].get("content", {}).get("parts", [])

        if not parts:
            return None

        return parts[0].get("text", "").strip() or None

    except Exception:
        logger.exception("Gemini request failed")
        return None


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "name": "ZOROX AI",
        "company": "WIKRAMASINGHE TECHNOLOGIES",
        "version": "2.0"
    })


# =========================================================
# REGISTER
# =========================================================

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

    try:
        existing = conn.execute(
            """
            SELECT id FROM users
            WHERE LOWER(email) = LOWER(?)
               OR LOWER(username) = LOWER(?)
            LIMIT 1
            """,
            (email, username)
        ).fetchone()

        if existing:
            conn.close()

            return jsonify({
                "error": "Email or username already exists"
            }), 409

        password_hash = generate_password_hash(password)

        cursor = conn.execute(
            """
            INSERT INTO users
            (phone, email, username, password_hash, country, verified)
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            (
                phone or None,
                email,
                username,
                password_hash,
                country
            )
        )

        conn.commit()

        user_id = cursor.lastrowid

        conn.close()

        return jsonify({
            "message": "Account created successfully",
            "user": {
                "id": user_id,
                "email": email,
                "username": username,
                "country": country
            }
        }), 201

    except Exception:
        conn.rollback()
        conn.close()

        logger.exception("Registration failed")

        return jsonify({
            "error": "Could not create account"
        }), 500


# =========================================================
# LOGIN
# =========================================================

@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}

    identifier = str(
        data.get("identifier", "")
    ).strip()

    password = str(
        data.get("password", "")
    )

    if not identifier or not password:
        return jsonify({
            "error": "Email/username and password are required"
        }), 400

    conn = get_db()

    user = conn.execute(
        """
        SELECT id, email, username, password_hash, country
        FROM users
        WHERE LOWER(email) = LOWER(?)
           OR LOWER(username) = LOWER(?)
        LIMIT 1
        """,
        (identifier, identifier)
    ).fetchone()

    conn.close()

    if not user:
        return jsonify({
            "error": "Invalid email/username or password"
        }), 401

    try:
        valid = check_password_hash(
            user["password_hash"],
            password
        )
    except Exception:
        valid = False

    if not valid:
        return jsonify({
            "error": "Invalid email/username or password"
        }), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "country": user["country"]
        }
    })


# =========================================================
# MUSIC
# =========================================================

@app.get("/api/music/search")
def music_search():
    query = request.args.get(
        "q",
        ""
    ).strip() or "rock"

    if not JAMENDO_CLIENT_ID:
        return jsonify({
            "error": "JAMENDO_CLIENT_ID is not configured",
            "results": []
        }), 500

    try:
        response = requests.get(
            "https://api.jamendo.com/v3.0/tracks/",
            params={
                "client_id": JAMENDO_CLIENT_ID,
                "format": "json",
                "limit": 20,
                "search": query
            },
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return jsonify({
            "headers": data.get("headers", {}),
            "results": data.get("results", [])
        })

    except Exception as error:
        logger.exception("Music search failed")

        return jsonify({
            "error": str(error),
            "results": []
        }), 500


# =========================================================
# CHAT
# =========================================================

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}

    message = str(
        data.get("message", "")
    ).strip()

    if not message:
        return jsonify({
            "error": "Message is required"
        }), 400

    conn = get_db()

    try:
        conversation = conn.execute(
            """
            SELECT id
            FROM conversations
            ORDER BY updated_at DESC
            LIMIT 1
            """
        ).fetchone()

        if conversation:
            conversation_id = conversation["id"]

        else:
            cursor = conn.execute(
                """
                INSERT INTO conversations (title)
                VALUES (?)
                """,
                (message[:50],)
            )

            conversation_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO messages
            (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (
                conversation_id,
                "user",
                message
            )
        )

        conn.execute(
            """
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (conversation_id,)
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

        # -------------------------
        # Gemini first
        # -------------------------

        reply = gemini_chat(history)

        if reply:
            provider = "gemini"
            fallback = False

        else:
            # -------------------------
            # Groq fallback
            # -------------------------

            reply = groq_chat(
                message,
                history
            )

            if not reply:
                return jsonify({
                    "error": "AI providers temporarily unavailable",
                    "message": "ZOROX AI is temporarily busy. Please try again shortly.",
                    "retryable": True
                }), 503

            provider = "groq"
            fallback = True

        conn.execute(
            """
            INSERT INTO messages
            (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (
                conversation_id,
                "assistant",
                reply
            )
        )

        conn.execute(
            """
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (conversation_id,)
        )

        conn.commit()

        return jsonify({
            "reply": reply,
            "provider": provider,
            "fallback": fallback,
            "conversation_id": conversation_id
        })

    except Exception:
        conn.rollback()

        logger.exception("Chat failed")

        return jsonify({
            "error": "Internal server error",
            "message": "ZOROX AI encountered an internal error."
        }), 500

    finally:
        conn.close()


# =========================================================
# START
# =========================================================

init_db()

if __name__ == "__main__":
    logger.info("Starting ZOROX AI backend")
    logger.info("Database: %s", DB_FILE)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
