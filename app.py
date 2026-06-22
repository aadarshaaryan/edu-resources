from flask import Flask, render_template, request, flash, session, redirect, url_for
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "jgfjiosfjksdfjosd"

DB_NAME = "database.db"

# ------------------ DB Setup ------------------
def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Profiles table linked to users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT,
        class TEXT,
        board TEXT,
        state TEXT,
        gmail TEXT,
        avatar_path TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
""")

    connection.commit()
    connection.close()

init_db()

# ------------------ Home ------------------
@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('index.html')

# ------------------ Show Users ------------------
@app.route("/users")
def show_users():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT id, username FROM users")
    rows = cursor.fetchall()
    connection.close()
    return render_template("users.html", users=rows)

# ------------------ Signup ------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please fill in both fields.")
            return redirect(url_for("signup"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.")
            return redirect(url_for("signup"))

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        try:
            connection = sqlite3.connect(DB_NAME)
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            connection.commit()
            connection.close()
            flash("Signup successful! Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists. Try another.")
            return redirect(url_for("signup"))

    return render_template("signup.html")

# ------------------ Login ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        connection = sqlite3.connect(DB_NAME)
        cursor = connection.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        connection.close()

        if user and bcrypt.checkpw(password.encode("utf-8"), user[2].encode("utf-8")):
            session["user_id"] = user[0]
            session["username"] = user[1]
            flash(f"Login successful! {session['username']}")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))

    return render_template("login.html")

# ------------------ Dashboard ------------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    if request.method == "POST":
        name = request.form.get("name")
        class_val = request.form.get("class")
        board = request.form.get("board")
        state = request.form.get("state")
        gmail = request.form.get("gmail")
        avatar_path = request.form.get("avatar_path")

        cursor.execute("SELECT id FROM profiles WHERE user_id=?", (user_id,))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE profiles
                SET name=?, class=?, board=?, state=?, gmail=?, avatar_path=?
                WHERE user_id=?
            """, (name, class_val, board, state, gmail, avatar_path, user_id))
        else:
            cursor.execute("""
                INSERT INTO profiles (user_id, name, class, board, state, gmail, avatar_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, class_val, board, state, gmail, avatar_path))

        connection.commit()
        flash("Profile updated successfully ✅")

    cursor.execute("SELECT name, class, board, state, gmail, avatar_path FROM profiles WHERE user_id=?", (user_id,))
    profile = cursor.fetchone()
    connection.close()

    return render_template("dashboard.html", username=session['username'], profile=profile)

# ------------------ Logout ------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

@app.route("/tenth")
def tenth():
    return render_template("tenth.html")

@app.route("/ninth")
def ninth():
    return render_template("ninth.html")

@app.route("/twelth")
def twelth():
    return render_template("twelth.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
