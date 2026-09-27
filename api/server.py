import logging
import traceback
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.get("/api/music/search")
def zorox_music_search():
    import os, requests
    q=request.args.get("q","").strip()
    if not q:
        q="rock"
    client_id=os.getenv("JAMENDO_CLIENT_ID")
    if not client_id:
        return jsonify({"error":"JAMENDO_CLIENT_ID is not configured"}),500
    try:
        r=requests.get(
            "https://api.jamendo.com/v3.0/tracks/",
            params={"client_id":client_id,"format":"json","limit":20,"search":q},
            timeout=15
        )
        data=r.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error":str(e)}),500

CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

DB_PATH = "memory/zorox.db"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-120b"


def groq_chat(prompt):
    if not GROQ_API_KEY:
        return None

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None




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


resend.api_key = os.getenv("RESEND_API_KEY")

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
        SELECT id, email, username, password_hash, country
        FROM users
        WHERE LOWER(email) = LOWER(?) OR username = ?
        LIMIT 1
        """,
        (identifier, identifier)
    ).fetchone()

    conn.close()

    if not user:
        return jsonify({
            "error": "Invalid email/username or password"
        }), 401

    user_id, email, username, password_hash, country = user

    try:
        valid_password = check_password_hash(password_hash, password)
    except Exception:
        valid_password = False

    if not valid_password:
        return jsonify({
            "error": "Invalid email/username or password"
        }), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user_id,
            "email": email,
            "username": username,
            "country": country
        }
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

    try:
        existing_email = conn.execute(
            "SELECT id FROM users WHERE LOWER(email) = LOWER(?) LIMIT 1",
            (email,)
        ).fetchone()

        if existing_email:
            conn.close()
            return jsonify({
                "error": "Email already exists. Please use Login or another email."
            }), 409

        existing_username = conn.execute(
            "SELECT id FROM users WHERE LOWER(username) = LOWER(?) LIMIT 1",
            (username,)
        ).fetchone()

        if existing_username:
            conn.close()
            return jsonify({
                "error": "Username already exists. Please choose another username."
            }), 409

        password_hash = generate_password_hash(password)

        cursor = conn.execute(
            """
            INSERT INTO users
            (phone, email, username, password_hash, country, verified)
            VALUES (?, ?, ?, ?, ?, 1)
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
        conn.rollback()
        conn.close()

        return jsonify({
            "error": "Could not create account"
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

    conn = get_db()

    try:
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
            gemini_role = "model" if item["role"] == "assistant" else "user"

            contents.append({
                "role": gemini_role,
                "parts": [
                    {
                        "text": item["content"]
                    }
                ]
            })

        payload = {
            "contents": contents
        }

        # If Gemini key is missing, use Groq directly.
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY is missing; trying Groq fallback")

            groq_reply = groq_chat(message)

            if groq_reply:
                conn.execute(
                    "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                    (conversation_id, "assistant", groq_reply)
                )
                conn.commit()

                return jsonify({
                    "reply": groq_reply,
                    "provider": "groq",
                    "fallback": True,
                    "conversation_id": conversation_id
                }), 200

            return jsonify({
                "error": "No AI provider is configured"
            }), 500

        max_retries = 2

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

                if response.status_code == 429:
                    logger.warning("Gemini rate limited; trying Groq")

                    groq_reply = groq_chat(message)

                    if groq_reply:
                        conn.execute(
                            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                            (conversation_id, "assistant", groq_reply)
                        )
                        conn.commit()

                        return jsonify({
                            "reply": groq_reply,
                            "provider": "groq",
                            "fallback": True,
                            "conversation_id": conversation_id
                        }), 200

                    try:
                        error_data = response.json()
                        error_message = error_data.get(
                            "error", {}
                        ).get("message", response.text)
                    except Exception:
                        error_message = response.text

                    return jsonify({
                        "error": "AI providers temporarily unavailable",
                        "message": "ZOROX AI is temporarily busy. Please try again shortly.",
                        "details": error_message,
                        "status": 503,
                        "retryable": True
                    }), 503

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
                        (conversation_id, "assistant", reply)
                    )

                    conn.execute(
                        "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (conversation_id,)
                    )

                    conn.commit()

                    return jsonify({
                        "reply": reply,
                        "conversation_id": conversation_id,
                        "provider": "gemini"
                    }), 200

                if response.status_code in (408, 500, 502, 503, 504):
                    if attempt < max_retries - 1:
                        delay = (2 ** attempt) + random.uniform(0, 0.5)
                        time.sleep(delay)
                        continue

                logger.error(
                    "Gemini returned HTTP %s: %s",
                    response.status_code,
                    response.text[:500]
                )

                return jsonify(
                    gemini_error(response)
                ), response.status_code

            except requests.Timeout:
                logger.warning("Gemini request timed out")

                if attempt < max_retries - 1:
                    delay = (2 ** attempt) + random.uniform(0, 0.5)
                    time.sleep(delay)
                    continue

                return jsonify({
                    "error": "Gemini request timed out",
                    "message": "Please try again."
                }), 504

            except requests.RequestException as error:
                logger.exception("Gemini request failed")

                return jsonify({
                    "error": "Could not connect to Gemini API",
                    "message": str(error)
                }), 502

        return jsonify({
            "error": "Gemini service is temporarily unavailable",
            "message": "Please try again in a moment."
        }), 503

    except Exception as error:
        logger.exception("Unhandled /api/chat error")

        return jsonify({
            "error": "Internal server error",
            "message": "ZOROX AI encountered an internal error."
        }), 500

    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
