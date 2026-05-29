```python
from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "lostfound_secret_key"

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect("lostfound.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS lost (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        item TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS found (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        item TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("lostfound.db")
        c = conn.cursor()

        c.execute("SELECT password FROM users WHERE username=?", (username,))
        user = c.fetchone()

        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            return redirect(url_for("home"))
        else:
            message = "Invalid username or password"

    return render_template_string("""
    <h2>Login</h2>

    <form method="POST">
        <input name="username" placeholder="Username" required><br><br>
        <input name="password" type="password" placeholder="Password" required><br><br>
        <button>Login</button>
    </form>

    <p style="color:red;">{{message}}</p>

    <a href="/register">Create Account</a>
    """, message=message)

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = sqlite3.connect("lostfound.db")
            c = conn.cursor()

            c.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("login"))

        except:
            message = "Username already exists"

    return render_template_string("""
    <h2>Create Account</h2>

    <form method="POST">
        <input name="username" placeholder="Username" required><br><br>
        <input name="password" type="password" placeholder="Password" required><br><br>
        <button>Create Account</button>
    </form>

    <p style="color:red;">{{message}}</p>

    <a href="/login">Back to Login</a>
    """, message=message)

# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]

    conn = sqlite3.connect("lostfound.db")
    c = conn.cursor()

    c.execute("SELECT * FROM lost")
    lost = c.fetchall()

    c.execute("SELECT * FROM found")
    found = c.fetchall()

    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lost & Found App</title>

<style>
body {
    font-family: Arial;
    text-align:center;
    background:#f4f4f4;
}

h1 {
    background:#4CAF50;
    color:white;
    padding:15px;
}

.card {
    background:white;
    margin:10px;
    padding:15px;
    border-radius:10px;
}

input {
    width:80%;
    padding:10px;
    margin:5px;
}

button {
    width:85%;
    padding:10px;
    background:#4CAF50;
    color:white;
    border:none;
}

a {
    display:block;
    margin:10px;
}
</style>
</head>

<body>

<h1>Lost & Found App</h1>

<p>Welcome, {{username}}</p>

<div class="card">
<h3>Add Lost Item</h3>

<form method="POST" action="/add_lost">
<input name="item" required>
<button>Add</button>
</form>
</div>

<div class="card">
<h3>Add Found Item</h3>

<form method="POST" action="/add_found">
<input name="item" required>
<button>Add</button>
</form>
</div>

<div class="card">
<h3>Lost Items</h3>

{% for i in lost %}
<p><b>{{i[1]}}</b> : {{i[2]}}</p>
{% endfor %}
</div>

<div class="card">
<h3>Found Items</h3>

{% for i in found %}
<p><b>{{i[1]}}</b> : {{i[2]}}</p>
{% endfor %}
</div>

<a href="/logout">Logout</a>

</body>
</html>
""", username=username, lost=lost, found=found)

# ---------------- ADD LOST ----------------
@app.route("/add_lost", methods=["POST"])
def add_lost():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    item = request.form["item"]

    conn = sqlite3.connect("lostfound.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO lost (username, item) VALUES (?, ?)",
        (username, item)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

# ---------------- ADD FOUND ----------------
@app.route("/add_found", methods=["POST"])
def add_found():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    item = request.form["item"]

    conn = sqlite3.connect("lostfound.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO found (username, item) VALUES (?, ?)",
        (username, item)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```
