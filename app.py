from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "lostfound_secret_key"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("lostfound.db")
c = conn.cursor()

```
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    phone TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS lost (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    phone TEXT,
    item TEXT,
    image TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS found (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    phone TEXT,
    item TEXT,
    image TEXT
)
""")

conn.commit()
conn.close()
```

init_db()

# ---------------- SMART SEARCH ----------------

def smart_match(query, items):
    query = query.lower()
result = []

```
for item in items:
    if query in item[3].lower():
        result.append(item)

return result
```

# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
message = ""

```
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
        message = "Invalid Login"

return render_template_string("""
<style>
body{
    font-family:Arial;
    background:#f4f4f4;
    text-align:center;
    padding-top:50px;
}

.box{
    background:white;
    width:90%;
    max-width:350px;
    margin:auto;
    padding:20px;
    border-radius:15px;
}

input,button{
    width:90%;
    padding:12px;
    margin:8px;
    border-radius:10px;
    border:1px solid #ccc;
}

button{
    background:#4CAF50;
    color:white;
    border:none;
}
</style>

<div class="box">
<h2>Login</h2>

<form method="POST">
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button>Login</button>
</form>

<p style="color:red;">{{message}}</p>

<a href="/register">Create Account</a>
</div>
""", message=message)
```

# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

```
if request.method == "POST":
    username = request.form["username"]
    password = generate_password_hash(request.form["password"])
    phone = request.form["phone"]

    try:
        conn = sqlite3.connect("lostfound.db")
        c = conn.cursor()

        c.execute("""
        INSERT INTO users (username, password, phone)
        VALUES (?, ?, ?)
        """, (username, password, phone))

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    except:
        message = "Username already exists"

return render_template_string("""
<style>
body{
    font-family:Arial;
    background:#f4f4f4;
    text-align:center;
    padding-top:50px;
}

.box{
    background:white;
    width:90%;
    max-width:350px;
    margin:auto;
    padding:20px;
    border-radius:15px;
}

input,button{
    width:90%;
    padding:12px;
    margin:8px;
    border-radius:10px;
    border:1px solid #ccc;
}

button{
    background:#4CAF50;
    color:white;
    border:none;
}
</style>

<div class="box">

<h2>Create Account</h2>

<form method="POST">

<input name="username" placeholder="Username" required>

<input type="password" name="password" placeholder="Password" required>

<input name="phone" placeholder="Phone Number" required>

<button>Create Account</button>

</form>

<p style="color:red;">{{message}}</p>

<a href="/login">Back to Login</a>

</div>
""", message=message)
```

# ---------------- HOME ----------------

@app.route("/")
def home():
    if "user" not in session:
return redirect(url_for("login"))

```
conn = sqlite3.connect("lostfound.db")
c = conn.cursor()

c.execute("SELECT * FROM lost")
lost = c.fetchall()

c.execute("SELECT * FROM found")
found = c.fetchall()

conn.close()

return render_template_string("""
```

<!DOCTYPE html>

<html>

<head>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Lost & Found</title>

<style>

body{
    font-family:Arial;
    background:#f4f4f4;
    margin:0;
}

.header{
    background:#4CAF50;
    color:white;
    padding:15px;
    text-align:center;
}

.card{
    background:white;
    margin:15px;
    padding:15px;
    border-radius:15px;
    box-shadow:0px 2px 5px rgba(0,0,0,0.2);
}

input,button{
    width:95%;
    padding:12px;
    margin:5px;
    border-radius:10px;
    border:1px solid #ccc;
}

button{
    background:#4CAF50;
    color:white;
    border:none;
}

img{
    width:100%;
    border-radius:10px;
    margin-top:10px;
}

.search{
    background:white;
    margin:15px;
    padding:15px;
    border-radius:15px;
}

</style>

</head>

<body>

<div class="header">
<h2>Lost & Found App</h2>
<p>Welcome {{session['user']}}</p>
</div>

<div class="card">

<h3>Add Lost Item</h3>

<form method="POST" action="/add_lost" enctype="multipart/form-data">

<input name="item" placeholder="Lost Item" required>

<input name="phone" placeholder="Phone Number" required>

<input type="file" name="image" required>

<button>Add Lost Item</button>

</form>

</div>

<div class="card">

<h3>Add Found Item</h3>

<form method="POST" action="/add_found" enctype="multipart/form-data">

<input name="item" placeholder="Found Item" required>

<input name="phone" placeholder="Phone Number" required>

<input type="file" name="image" required>

<button>Add Found Item</button>

</form>

</div>

<div class="search">

<h3>Smart Search</h3>

<form method="POST" action="/search">

<input name="query" placeholder="Search item">

<button>Search</button>

</form>

</div>

<div class="card">

<h3>Lost Items</h3>

{% for i in lost %}

<p><b>{{i[1]}}</b></p>

<p>{{i[3]}}</p>

<p>📞 {{i[2]}}</p>

<img src="/static/uploads/{{i[4]}}">

<hr>

{% endfor %}

</div>

<div class="card">

<h3>Found Items</h3>

{% for i in found %}

<p><b>{{i[1]}}</b></p>

<p>{{i[3]}}</p>

<p>📞 {{i[2]}}</p>

<img src="/static/uploads/{{i[4]}}">

<hr>

{% endfor %}

</div>

<div style="text-align:center;">
<a href="/logout">Logout</a>
</div>

</body>
</html>
""", lost=lost, found=found)

# ---------------- ADD LOST ----------------

@app.route("/add_lost", methods=["POST"])
def add_lost():

```
image = request.files["image"]

filename = secure_filename(image.filename)

image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

conn = sqlite3.connect("lostfound.db")
c = conn.cursor()

c.execute("""
INSERT INTO lost (username, phone, item, image)
VALUES (?, ?, ?, ?)
""", (
    session["user"],
    request.form["phone"],
    request.form["item"],
    filename
))

conn.commit()
conn.close()

return redirect(url_for("home"))
```

# ---------------- ADD FOUND ----------------

@app.route("/add_found", methods=["POST"])
def add_found():

```
image = request.files["image"]

filename = secure_filename(image.filename)

image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

conn = sqlite3.connect("lostfound.db")
c = conn.cursor()

c.execute("""
INSERT INTO found (username, phone, item, image)
VALUES (?, ?, ?, ?)
""", (
    session["user"],
    request.form["phone"],
    request.form["item"],
    filename
))

conn.commit()
conn.close()

return redirect(url_for("home"))
```

# ---------------- SEARCH ----------------

@app.route("/search", methods=["POST"])
def search():

```
query = request.form["query"]

conn = sqlite3.connect("lostfound.db")
c = conn.cursor()

c.execute("SELECT * FROM lost")
lost = c.fetchall()

c.execute("SELECT * FROM found")
found = c.fetchall()

conn.close()

result_lost = smart_match(query, lost)
result_found = smart_match(query, found)

return render_template_string("""

<style>
body{
    font-family:Arial;
    background:#f4f4f4;
    padding:20px;
}

.card{
    background:white;
    padding:15px;
    margin:10px;
    border-radius:10px;
}

img{
    width:100%;
    border-radius:10px;
}
</style>

<h2>Search Results</h2>

<div class="card">
<h3>Lost Items</h3>

{% for i in lost %}
<p><b>{{i[1]}}</b></p>
<p>{{i[3]}}</p>
<p>📞 {{i[2]}}</p>
<img src="/static/uploads/{{i[4]}}">
<hr>
{% endfor %}
</div>

<div class="card">
<h3>Found Items</h3>

{% for i in found %}
<p><b>{{i[1]}}</b></p>
<p>{{i[3]}}</p>
<p>📞 {{i[2]}}</p>
<img src="/static/uploads/{{i[4]}}">
<hr>
{% endfor %}
</div>

<a href="/">Back Home</a>

""", lost=result_lost, found=result_found)
```

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
session.clear()
return redirect(url_for("login"))

# ---------------- RUN ----------------

if **name** == "**main**":
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
