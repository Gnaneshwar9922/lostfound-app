from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "lostfound_secret_key"

# ---------------- USERS ----------------
users = {
    "admin": "1234"
}

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect("lostfound.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS lost (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS found (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- AI MATCH FUNCTION ----------------
def smart_match(query, items):
    query = query.lower()
    return [i for i in items if query in i[1].lower()]

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("home"))

    return render_template_string("""
    <h2>Login</h2>
    <form method="POST">
        <input name="username" placeholder="Username">
        <input name="password" type="password" placeholder="Password">
        <button>Login</button>
    </form>
    """)

# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

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
<title>Lost & Found System</title>

<style>
body { font-family: Arial; text-align:center; background:#f4f4f4; }
h1 { background:#4CAF50; color:white; padding:15px; }
input { width:80%; padding:10px; margin:5px; }
button { width:85%; padding:10px; background:#4CAF50; color:white; border:none; }
.card { background:white; margin:10px; padding:10px; border-radius:10px; }
a { display:block; margin:5px; }
</style>
</head>

<body>

<h1>Lost & Found App</h1>

<p>Created by Gnaneshwar Yuvaraj</p>

<div class="card">
<h3>Add Lost Item</h3>
<form method="POST" action="/add_lost">
<input name="item">
<button>Add</button>
</form>
</div>

<div class="card">
<h3>Add Found Item</h3>
<form method="POST" action="/add_found">
<input name="item">
<button>Add</button>
</form>
</div>

<div class="card">
<h3>Lost Items</h3>
{% for i in lost %}
<p>{{i[1]}} <a href="/delete_lost/{{i[0]}}">❌ Delete</a></p>
{% endfor %}
</div>

<div class="card">
<h3>Found Items</h3>
{% for i in found %}
<p>{{i[1]}} <a href="/delete_found/{{i[0]}}">❌ Delete</a></p>
{% endfor %}
</div>

<a href="/search">🔍 Search (AI)</a><br>
<a href="/logout">Logout</a>

</body>
</html>
""", lost=lost, found=found)

# ---------------- ADD LOST ----------------
@app.route("/add_lost", methods=["POST"])
def add_lost():
    item = request.form["item"]
    conn = sqlite3.connect("lostfound.db")
    c = conn.cursor()
    c.execute("INSERT INTO lost (item) VALUES (?)", (item,))
    conn.commit()
    conn.close()
    return home()

# ---------------- ADD FOUND ----------------
@app.route("/add_found", methods=["POST"])
def add_found():
    item = request.form["item"]
    conn = sqlite3.connect("lostfound.db")
    c = conn.cursor()
    c.execute("INSERT INTO found (item) VALUES (?)", (item,))
    conn.commit()
    conn.close()
    return home()

# ---------------- DELETE LOST ----------------
@app.route("/delete_lost/<int:id>")
def delete_lost(id):
    conn = sqlite3.connect("lostfound.db")
    c = conn.cursor()
    c.execute("DELETE FROM lost WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return home()

# ---------------- DELETE FOUND ----------------
@app.route("/delete_found/<int:id>")
def delete_found(id):
    conn = sqlite3.connect("lostfound.db")
    c = conn.cursor()
    c.execute("DELETE FROM found WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return home()

# ---------------- SEARCH (AI SMART) ----------------
@app.route("/search", methods=["GET", "POST"])
def search():
    result_lost = []
    result_found = []

    conn = sqlite3.connect("lostfound.db")
    c = conn.cursor()

    c.execute("SELECT * FROM lost")
    lost = c.fetchall()

    c.execute("SELECT * FROM found")
    found = c.fetchall()

    conn.close()

    if request.method == "POST":
        item = request.form["item"]
        result_lost = smart_match(item, lost)
        result_found = smart_match(item, found)

    return render_template_string("""
<h2>AI Search</h2>

<form method="POST">
<input name="item" placeholder="Search item">
<button>Search</button>
</form>

<h3>Lost Results</h3>
{% for i in lost %}
<p>{{i[1]}}</p>
{% endfor %}

<h3>Found Results</h3>
{% for i in found %}
<p>{{i[1]}}</p>
{% endfor %}

<br>
<a href="/">Back Home</a>
""", lost=result_lost, found=result_found)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- RUN ----------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
