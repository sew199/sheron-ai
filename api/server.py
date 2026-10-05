import os
import time
import random
import sqlite3
import logging
import requests

from flask import Flask, request, jsonify, send_from_directory
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

CINESUBZ_API_URL = os.getenv("CINESUBZ_API_URL", "")
CINESUBZ_SEARCH_API_URL = os.getenv("CINESUBZ_SEARCH_API_URL", "").strip()
CINESUBZ_API_KEY = os.getenv("CINESUBZ_API_KEY", "").strip()
TEST_DOWNLOAD_URL = os.getenv("TEST_DOWNLOAD_URL", "").strip()
MOVIE_PROVIDER_URL = os.getenv("MOVIE_PROVIDER_URL", "").strip()
MOVIE_API_KEY = os.getenv("MOVIE_API_KEY", "").strip()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("zorox")

app = Flask(__name__)
CORS(app)

# =========================================================
# CONFIG
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
SERVER_SECRET = os.getenv("SERVER_SECRET", "").strip()
JAMENDO_CLIENT_ID = os.getenv("JAMENDO_CLIENT_ID", "").strip()
EPIDEMIC_API_KEY = os.getenv("EPIDEMIC_API_KEY", "").strip()

# API HUB
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "").strip()
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY", "").strip()
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY", "").strip()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", "").strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
HF_API_KEY = os.getenv("HF_API_KEY", "").strip()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "").strip()
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "").strip()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()

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
@app.get("/app")
def frontend_home():
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), "web"), "index.html")

@app.get("/app/<path:filename>")
def frontend_files(filename):
    return send_from_directory(os.path.join(os.path.dirname(os.path.dirname(__file__)), "web"), filename)


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

    # Admin monitoring: record last login IP/time without storing plaintext passwords
    conn = get_db()
    conn.execute(
        "UPDATE users SET last_ip = ?, last_seen = CURRENT_TIMESTAMP, last_login = CURRENT_TIMESTAMP, login_count = COALESCE(login_count, 0) + 1 WHERE id = ?",
        (request.headers.get("X-Forwarded-For", request.remote_addr), user["id"])
    )
    conn.commit()
    conn.close()

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
# ADMIN AUTH + MONITORING
# =========================================================

from functools import wraps

ADMIN_TOKENS = set()


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Admin-Token", "")
        if not token or token not in ADMIN_TOKENS:
            return jsonify({"error": "Admin authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapper


@app.post("/api/admin/login")
def admin_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not ADMIN_USERNAME or not ADMIN_PASSWORD or not SERVER_SECRET:
        return jsonify({"error": "Admin security is not configured"}), 503

    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        logger.warning("Failed admin login attempt")
        return jsonify({"error": "Invalid admin credentials"}), 401

    token = __import__("secrets").token_urlsafe(32)
    ADMIN_TOKENS.add(token)

    logger.info("Admin login successful")
    return jsonify({"message": "Admin login successful", "token": token})


@app.get("/api/admin/dashboard")
@admin_required
def admin_dashboard():
    conn = get_db()
    users = conn.execute("SELECT id, phone, email, username, country, verified, created_at, last_ip, last_seen, last_login, login_count FROM users ORDER BY id DESC").fetchall()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_chats = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    online_users = conn.execute("SELECT COUNT(*) FROM users WHERE last_seen IS NOT NULL AND datetime(last_seen) >= datetime('now', '-5 minutes')").fetchone()[0]
    conn.close()

    return jsonify({
        "server": "online",
        "database": "online",
        "ai": "configured" if (GROQ_API_KEY or GEMINI_API_KEY) else "not_configured",
        "movies": "configured" if TMDB_API_KEY else "not_configured",
        "music": "configured" if JAMENDO_CLIENT_ID else "not_configured",
        "stats": {
            "total_users": total_users,
            "online_users": online_users,
            "total_messages": total_chats
        },
        "users": [dict(u) for u in users]
    })

# =========================================================
# MUSIC
# =========================================================

@app.get("/api/music/search")
def music_search():
    query = request.args.get("q", "").strip() or "rock"

    jamendo_results = []
    epidemic_results = []

    # -------------------------
    # JAMENDO
    # -------------------------
    if JAMENDO_CLIENT_ID:
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
            jamendo_results = data.get("results", [])

        except Exception:
            logger.exception("Jamendo music search failed")

    # -------------------------
    # EPIDEMIC SOUND
    # -------------------------
    if EPIDEMIC_API_KEY:
        try:
            response = requests.get(
                "https://partner-content-api.epidemicsound.com/v0/tracks/search",
                headers={
                    "Authorization": f"Bearer {EPIDEMIC_API_KEY}",
                    "Accept": "application/json"
                },
                params={
                    "term": query,
                    "limit": 20
                },
                timeout=20
            )

            response.raise_for_status()
            data = response.json()
            epidemic_results = data.get("tracks", [])

        except Exception:
            logger.exception("Epidemic Sound search failed")

    return jsonify({
        "query": query,
        "sources": {
            "jamendo": len(jamendo_results),
            "epidemic": len(epidemic_results)
        },
        "jamendo": jamendo_results,
        "epidemic": epidemic_results,
        "results": jamendo_results + epidemic_results
    })


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
# ZOROX API HUB - FREE / NO-KEY SERVICES
# =========================================================

@app.get("/api/weather")
def api_weather():
    city = request.args.get("city", "Colombo").strip()

    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10
        ).json()

        results = geo.get("results", [])
        if not results:
            return jsonify({"error": "City not found"}), 404

        place = results[0]

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "timezone": "auto"
            },
            timeout=10
        ).json()

        return jsonify({
            "service": "Open-Meteo",
            "city": place.get("name"),
            "country": place.get("country"),
            "latitude": place.get("latitude"),
            "longitude": place.get("longitude"),
            "current": weather.get("current", {})
        })

    except Exception as e:
        logger.exception("Weather API failed")
        return jsonify({"error": "Weather service unavailable"}), 502


@app.get("/api/currency")
def api_currency():
    base = request.args.get("base", "USD").upper().strip()
    target = request.args.get("target", "LKR").upper().strip()

    try:
        data = requests.get(
            "https://api.frankfurter.app/latest",
            params={"from": base, "to": target},
            timeout=10
        ).json()

        return jsonify({
            "service": "Frankfurter",
            "base": data.get("base"),
            "date": data.get("date"),
            "rates": data.get("rates", {})
        })

    except Exception:
        logger.exception("Currency API failed")
        return jsonify({"error": "Currency service unavailable"}), 502


@app.get("/api/wiki")
def api_wiki():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        data = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrlimit": 5,
                "prop": "extracts",
                "exintro": 1,
                "explaintext": 1,
                "format": "json"
            },
            headers={"User-Agent": "ZOROX-AI/2.0"},
            timeout=10
        ).json()

        pages = data.get("query", {}).get("pages", {})

        results = []
        for page in pages.values():
            results.append({
                "title": page.get("title"),
                "pageid": page.get("pageid"),
                "extract": page.get("extract", ""),
                "url": "https://en.wikipedia.org/?curid=" + str(page.get("pageid"))
            })

        return jsonify({
            "service": "Wikipedia",
            "results": results
        })

    except Exception:
        logger.exception("Wikipedia API failed")
        return jsonify({"error": "Wikipedia unavailable"}), 502


@app.get("/api/stackexchange")
def api_stackexchange():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        data = requests.get(
            "https://api.stackexchange.com/2.3/search/advanced",
            params={
                "site": "stackoverflow",
                "q": query,
                "pagesize": 5,
                "order": "desc",
                "sort": "relevance"
            },
            timeout=10
        ).json()

        results = []

        for item in data.get("items", []):
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "score": item.get("score"),
                "is_answered": item.get("is_answered"),
                "tags": item.get("tags", [])
            })

        return jsonify({
            "service": "Stack Exchange",
            "results": results
        })

    except Exception:
        logger.exception("Stack Exchange API failed")
        return jsonify({"error": "Stack Exchange unavailable"}), 502


@app.get("/api/nvd")
def api_nvd():
    keyword = request.args.get("q", "").strip()

    if not keyword:
        return jsonify({"error": "Query is required"}), 400

    try:
        data = requests.get(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            params={
                "keywordSearch": keyword,
                "resultsPerPage": 5
            },
            timeout=15
        ).json()

        results = []

        for item in data.get("vulnerabilities", []):
            cve = item.get("cve", {})
            descriptions = cve.get("descriptions", [])

            results.append({
                "id": cve.get("id"),
                "description": descriptions[0].get("value", "") if descriptions else "",
                "published": cve.get("published"),
                "lastModified": cve.get("lastModified")
            })

        return jsonify({
            "service": "NVD",
            "results": results
        })

    except Exception:
        logger.exception("NVD API failed")
        return jsonify({"error": "NVD unavailable"}), 502


@app.get("/api/dictionary")
def api_dictionary():
    word = request.args.get("word", "").strip()

    if not word:
        return jsonify({"error": "Word is required"}), 400

    try:
        response = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}",
            timeout=10
        )

        if response.status_code != 200:
            return jsonify({"error": "Word not found"}), 404

        return jsonify({
            "service": "Free Dictionary",
            "results": response.json()
        })

    except Exception:
        logger.exception("Dictionary API failed")
        return jsonify({"error": "Dictionary unavailable"}), 502


@app.get("/api/crypto")
def api_crypto():
    coin = request.args.get("coin", "bitcoin").lower().strip()

    try:
        data = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": coin,
                "vs_currencies": "usd,lkr"
            },
            timeout=10
        ).json()

        return jsonify({
            "service": "CoinGecko",
            "coin": coin,
            "data": data
        })

    except Exception:
        logger.exception("CoinGecko API failed")
        return jsonify({"error": "Crypto service unavailable"}), 502


@app.get("/api/ip")
def api_ip():
    ip = request.args.get("ip", "").strip()

    try:
        url = f"https://ipapi.co/{ip}/json/" if ip else "https://ipapi.co/json/"
        data = requests.get(url, timeout=10).json()

        return jsonify({
            "service": "ipapi",
            "data": data
        })

    except Exception:
        logger.exception("IP API failed")
        return jsonify({"error": "IP service unavailable"}), 502

# =========================================================
# START
# =========================================================

init_db()

# =========================================================
# MOVIES (TMDB)
# =========================================================
TMDB_BASE = "https://api.themoviedb.org/3"
MOVIE_CATEGORIES = {
    "trending": "trending/movie/week",
    "popular": "movie/popular",
    "top_rated": "movie/top_rated",
    "now_playing": "movie/now_playing",
    "upcoming": "movie/upcoming",
}


def tmdb_get(path, **params):
    """Call TMDB. Never leaks the API key in error messages."""
    if not TMDB_API_KEY:
        return {"error": "TMDB API key is not configured"}, 500
    params.update({"api_key": TMDB_API_KEY, "language": "en-US"})
    try:
        r = requests.get(f"{TMDB_BASE}/{path}", params=params, timeout=15)
        return r.json(), r.status_code
    except Exception:
        logger.exception("TMDB request failed")
        return {"error": "Movie service unavailable"}, 502


def movie_page_arg():
    try:
        return max(1, min(int(request.args.get("page", 1)), 500))
    except (TypeError, ValueError):
        return 1


@app.get("/api/movies/search")
def movie_search():
    q = str(request.args.get("q", "")).strip()

    if not q:
        return jsonify({"error": "Movie search query is required"}), 400

    if not CINESUBZ_SEARCH_API_URL or not CINESUBZ_API_KEY:
        return jsonify({
            "success": False,
            "message": "CineSubz Search API is not configured."
        }), 503

    try:
        search_url = CINESUBZ_SEARCH_API_URL.replace(
            "[KEYWORDS]",
            requests.utils.quote(q, safe="")
        ).replace(
            "[CINESUBZ_API_KEY]",
            requests.utils.quote(CINESUBZ_API_KEY, safe="")
        )

        response = requests.get(search_url, timeout=30)
        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            return jsonify({
                "success": False,
                "message": "CineSubz search failed"
            }), 502

        results = data.get("results") or []

        return jsonify({
            "success": True,
            "results": [
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "poster": item.get("poster", ""),
                    "description": item.get("description", "")
                }
                for item in results
            ]
        })

    except requests.RequestException:
        logger.exception("CineSubz search request failed")
        return jsonify({
            "success": False,
            "message": "Unable to reach CineSubz Search API"
        }), 502

    except Exception:
        logger.exception("Movie search error")
        return jsonify({
            "success": False,
            "message": "Movie search service error"
        }), 500

@app.get("/api/movies/discover")
def movie_discover():
    category = request.args.get("category", "trending").strip().lower()
    path = MOVIE_CATEGORIES.get(category)
    if not path:
        return jsonify({"error": "Invalid category"}), 400
    data, status = tmdb_get(path, page=movie_page_arg())
    return jsonify(data), status


@app.get("/api/movies/<int:movie_id>")
def movie_details(movie_id):
    data, status = tmdb_get(f"movie/{movie_id}", append_to_response="videos,credits")
    if status != 200:
        return jsonify(data), status

    videos = (data.get("videos") or {}).get("results", [])
    yt = [v for v in videos if v.get("site") == "YouTube" and v.get("type") == "Trailer"]
    trailer = next((v for v in yt if v.get("official")), None) or (yt[0] if yt else None)
    cast = (data.get("credits") or {}).get("cast", [])[:8]

    return jsonify({
        "id": data.get("id"),
        "title": data.get("title"),
        "tagline": data.get("tagline"),
        "overview": data.get("overview"),
        "runtime": data.get("runtime"),
        "release_date": data.get("release_date"),
        "vote_average": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "genres": [g.get("name") for g in data.get("genres", [])],
        "poster_path": data.get("poster_path"),
        "backdrop_path": data.get("backdrop_path"),
        "trailer_key": trailer.get("key") if trailer else None,
        "cast": [{"name": c.get("name"), "character": c.get("character")} for c in cast],
    })


@app.get("/api/admin/logs")
@admin_required
def admin_logs():
    from pathlib import Path

    log_file = Path(BASE_DIR) / "zorox-server.log"

    if not log_file.exists():
        return jsonify({"logs": [], "message": "Log file not found"})

    try:
        lines = log_file.read_text(errors="replace").splitlines()
        return jsonify({
            "logs": lines[-200:]
        })
    except Exception as e:
        logger.exception("Failed to read admin logs")
        return jsonify({"error": "Unable to read logs"}), 500

@app.get("/api/movies/download")
def movie_download():
    movie_url = request.args.get("url", "").strip()
    quality = request.args.get("quality", "").strip().lower()

    if not movie_url:
        return jsonify({"message": "Movie URL is required"}), 400

    if not movie_url.startswith(("http://", "https://")):
        return jsonify({"message": "Invalid movie URL"}), 400

    if quality not in {"480p", "720p", "1080p"}:
        return jsonify({"message": "Invalid quality"}), 400

    if not CINESUBZ_API_URL or not CINESUBZ_API_KEY:
        return jsonify({
            "status": "not_configured",
            "message": "CineSubz API is not configured."
        }), 503

    try:
        base_url = CINESUBZ_API_URL.split("?", 1)[0]

        provider_url = (
            base_url
            + "?url="
            + requests.utils.quote(movie_url, safe="")
            + "&api_key="
            + requests.utils.quote(CINESUBZ_API_KEY, safe="")
        )

        print(
            "CineSubz provider:",
            base_url + "?url=[HIDDEN]&api_key=[HIDDEN]"
        )

        response = requests.get(provider_url, timeout=30)
        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            return jsonify({
                "status": "provider_error",
                "message": "Movie provider failed"
            }), 502

        result = data.get("result") or {}
        download_links = result.get("download_links") or []

        selected = None

        for item in download_links:
            label = str(item.get("label", "")).lower()
            link = item.get("link", "")

            if quality in label and link:
                selected = item
                break

        if not selected:
            return jsonify({
                "status": "not_available",
                "message": f"{quality} download is not available",
                "available": [
                    item.get("label", "")
                    for item in download_links
                    if item.get("link")
                ]
            }), 404

        return jsonify({
            "status": "ready",
            "success": True,
            "title": result.get("title", ""),
            "quality": quality,
            "label": selected.get("label", ""),
            "url": __import__("html").unescape(
                selected.get("link", "")
            )
        })

    except requests.RequestException as e:
        logger.exception("CineSubz provider request failed")
        return jsonify({
            "status": "provider_error",
            "message": "Unable to reach movie provider"
        }), 502

    except Exception as e:
        logger.exception("Movie download error")
        return jsonify({
            "status": "error",
            "message": "Movie download service error"
        }), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False
    )
