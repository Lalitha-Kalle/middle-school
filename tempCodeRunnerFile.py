"""
Flask backend for PrepAIR Math Olympiad Studio
Serves questions from olympiad_questions.db
"""

from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
import os
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'prepair-olympiad-secret-key-2024'
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DB_PATH = Path(__file__).parent / "olympiad_questions.db"

# Hardcoded credentials
MASTER_USERNAME = "master_tutor"
MASTER_PASSWORD = "tp@1234"

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def db_exec(query, params=None):
    """Execute query and return results."""
    conn = get_db()
    try:
        cur = conn.execute(query, params or [])
        return cur.fetchall()
    finally:
        conn.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle login."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == MASTER_USERNAME and password == MASTER_PASSWORD:
            user = User(username)
            login_user(user)
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials"), 401

    return render_template("login.html")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    """Handle logout."""
    logout_user()
    return redirect(url_for("login"))

@app.route("/api/exams", methods=["GET"])
@login_required
def get_exams():
    """Return list of unique exams."""
    rows = db_exec("SELECT DISTINCT exam FROM questions WHERE exam IS NOT NULL ORDER BY exam")
    exams = [row[0] for row in rows]
    return jsonify(exams)

@app.route("/api/levels", methods=["GET"])
@login_required
def get_levels():
    """Return difficulty levels for given exam."""
    exam = request.args.get("exam")
    if not exam:
        return jsonify([]), 400

    rows = db_exec(
        "SELECT DISTINCT difficulty FROM questions WHERE exam = ? AND difficulty IS NOT NULL ORDER BY difficulty",
        [exam]
    )
    levels = [row[0] for row in rows]
    return jsonify(levels)

@app.route("/api/chapters", methods=["GET"])
@login_required
def get_chapters():
    """Return chapters for given exam and level."""
    exam = request.args.get("exam")
    difficulty = request.args.get("difficulty")
    if not exam:
        return jsonify([]), 400

    if difficulty:
        rows = db_exec(
            "SELECT chapter FROM questions WHERE exam = ? AND difficulty = ? AND chapter IS NOT NULL GROUP BY chapter ORDER BY MIN(id)",
            [exam, difficulty]
        )
    else:
        rows = db_exec(
            "SELECT chapter FROM questions WHERE exam = ? AND chapter IS NOT NULL GROUP BY chapter ORDER BY MIN(id)",
            [exam]
        )

    chapters = [row[0] for row in rows]
    return jsonify(chapters)

@app.route("/api/topics", methods=["GET"])
@login_required
def get_topics():
    """Return topics for given exam, level, and chapter."""
    exam = request.args.get("exam")
    difficulty = request.args.get("difficulty")
    chapter = request.args.get("chapter")
    if not exam or not chapter:
        return jsonify([]), 400

    if difficulty:
        rows = db_exec(
            "SELECT topic FROM questions WHERE exam = ? AND difficulty = ? AND chapter = ? AND topic IS NOT NULL GROUP BY topic ORDER BY MIN(id)",
            [exam, difficulty, chapter]
        )
    else:
        rows = db_exec(
            "SELECT topic FROM questions WHERE exam = ? AND chapter = ? AND topic IS NOT NULL GROUP BY topic ORDER BY MIN(id)",
            [exam, chapter]
        )

    topics = [row[0] for row in rows]
    return jsonify(topics)

@app.route("/api/questions", methods=["GET"])
@login_required
def get_questions():
    """Return questions matching filters."""
    exam = request.args.get("exam")
    difficulty = request.args.get("difficulty")
    chapter = request.args.get("chapter")
    topic = request.args.get("topic")

    query = "SELECT * FROM questions WHERE 1=1"
    params = []

    if exam:
        query += " AND exam = ?"
        params.append(exam)
    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)
    if chapter:
        query += " AND chapter = ?"
        params.append(chapter)
    if topic:
        query += " AND topic = ?"
        params.append(topic)

    query += " ORDER BY id"

    rows = db_exec(query, params)

    questions = []
    for row in rows:
        # Parse options from columns
        options = []
        for col in ["option_a", "option_b", "option_c", "option_d", "option_e"]:
            val = row[col]
            if val:
                options.append(val)

        # Parse solution steps (split by newlines or semicolons)
        solution_text = row["solution"] or ""
        solution_steps = [s.strip() for s in solution_text.split("\n") if s.strip()]

        # Convert correct_option letter (A-E) to index (0-4)
        correct_index = 0
        correct_option = row["correct_option"]
        if correct_option:
            letter = correct_option.strip().upper()
            if letter in "ABCDE":
                correct_index = ord(letter) - ord('A')

        q = {
            "id": row["id"],
            "exam": row["exam"],
            "lvl": row["difficulty"] or "Level 1",
            "ch": row["chapter"],
            "tp": row["topic"],
            "yr": 2024,  # Default year since not in DB
            "stem": row["question"],
            "opts": options,
            "c": correct_index,
            "sol": solution_steps or ["Work through this problem step by step."],
            "ans": correct_option or "See solution",
        }
        questions.append(q)

    return jsonify(questions)

@app.route("/", methods=["GET"])
def index():
    """Serve the main HTML file or redirect to login."""
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    html_path = Path(__file__).parent / "prepair-olympiad-studio.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # app.run(debug=True, host="127.0.0.1", port=5000)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
