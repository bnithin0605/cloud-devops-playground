from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import sqlite3
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "users.db")
UPLOAD_FOLDER = os.path.join(APP_DIR, "uploads")

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            uploaded_filename TEXT,
            word_count INTEGER
        )
    """)
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, password, firstname, lastname, email, address, uploaded_filename, word_count FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def update_file_info(username, filename, word_count):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET uploaded_filename=?, word_count=? WHERE username=?", (filename, word_count, username))
    conn.commit()
    conn.close()

def count_words(text: str) -> int:
    # simple word count (splits on whitespace)
    return len(text.split())

@app.route("/")
def home():
    return redirect(url_for("register"))

@app.route("/register", methods=["GET", "POST"])
def register():
    init_db()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.")
            return render_template("register.html")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, '', '', '', '')",
                (username, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username already exists. Please pick another.")
            conn.close()
            return render_template("register.html")
        conn.close()

        session["username"] = username
        return redirect(url_for("details"))

    return render_template("register.html")

@app.route("/details", methods=["GET", "POST"])
def details():
    init_db()
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))

    if request.method == "POST":
        firstname = request.form.get("firstname", "").strip()
        lastname = request.form.get("lastname", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()

        if not all([firstname, lastname, email, address]):
            flash("All details are required.")
            return render_template("details.html", username=username)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE users SET firstname=?, lastname=?, email=?, address=? WHERE username=?",
            (firstname, lastname, email, address, username)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("profile", username=username))

    return render_template("details.html", username=username)

@app.route("/profile/<username>", methods=["GET"])
def profile(username):
    init_db()
    user = get_user_by_username(username)
    if not user:
        return "User not found", 404

    data = {
        "username": user[0],
        "firstname": user[2],
        "lastname": user[3],
        "email": user[4],
        "address": user[5],
        "uploaded_filename": user[6],
        "word_count": user[7],
    }
    return render_template("profile.html", user=data)

@app.route("/login", methods=["GET", "POST"])
def login():
    init_db()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = get_user_by_username(username)
        if not user or user[1] != password:
            flash("Invalid username or password.")
            return render_template("login.html")

        session["username"] = username
        return redirect(url_for("profile", username=username))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/upload/<username>", methods=["POST"])
def upload(username):
    init_db()
    # Optional: require logged in user matches target username
    if session.get("username") != username:
        return redirect(url_for("login"))

    if "file" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("profile", username=username))

    f = request.files["file"]
    if f.filename == "":
        flash("No file selected.")
        return redirect(url_for("profile", username=username))

    # enforce Limerick.txt
    if f.filename != "Limerick.txt":
        flash("Please upload the file named exactly: Limerick.txt")
        return redirect(url_for("profile", username=username))

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    save_path = os.path.join(UPLOAD_FOLDER, f.filename)
    f.save(save_path)

    # compute word count
    with open(save_path, "r", encoding="utf-8", errors="ignore") as fp:
        content = fp.read()
    wc = count_words(content)

    update_file_info(username, f.filename, wc)
    flash(f"Uploaded {f.filename}. Word count: {wc}")
    return redirect(url_for("profile", username=username))

@app.route("/download/<username>", methods=["GET"])
def download(username):
    init_db()
    user = get_user_by_username(username)
    if not user or not user[6]:
        return "No uploaded file found for this user.", 404

    filename = user[6]
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# WSGI entry
application = app
