from flask import Flask, request, jsonify, send_from_directory, session, redirect, send_file
from functools import wraps

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "PPTWALLAH@2026#SecureKey"
DATABASE = "ppt_requests.db"



# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            subject TEXT,
            topic TEXT NOT NULL,
            slides INTEGER,
            language TEXT,
            style TEXT,
            graphics TEXT,
            requirements TEXT,
            plan TEXT,
            total_price REAL,
            advance_price REAL,
            remaining_price REAL,
            status TEXT DEFAULT 'New',
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    
    # ---------------- ADMIN LOGIN ----------------

ADMIN_USERNAME = "vineetkandpal7579"
ADMIN_PASSWORD = "vineetkandpal7579"


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/admin-login")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin")

        return "Wrong username or password. <a href='/admin-login'>Try Again</a>"

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PPTWALLAH Admin Login</title>
        <style>
            body {
                margin: 0;
                background: #141a2d;
                color: white;
                font-family: Arial;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .login-box {
                width: 320px;
                padding: 35px;
                background: #1e2640;
                border-radius: 15px;
            }

            h2 {
                text-align: center;
                color: #dc9750;
            }

            input {
                width: 100%;
                box-sizing: border-box;
                padding: 12px;
                margin: 8px 0;
                border: none;
                border-radius: 8px;
            }

            button {
                width: 100%;
                padding: 12px;
                margin-top: 10px;
                background: #dc9750;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
            }
        </style>
    </head>

    <body>

        <div class="login-box">

            <h2>PPTWALLAH</h2>

            <form method="POST">

                <input
                    type="text"
                    name="username"
                    placeholder="Username"
                    required
                >

                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    required
                >

                <button type="submit">
                    Login
                </button>

            </form>

        </div>

    </body>
    </html>
    """


@app.route("/admin-logout")
def admin_logout():
    session.clear()
    return redirect("/admin-login")


# ---------------- MAIN WEBSITE ----------------

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/style.css")
def css():
    return send_from_directory(".", "style.css")


@app.route("/script.js")
def js():
    return send_from_directory(".", "script.js")


# ---------------- SUBMIT REQUEST ----------------

@app.route("/submit-request", methods=["POST"])
def submit_request():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    mobile = data.get("mobile", "").strip()
    topic = data.get("topic", "").strip()

    if not name or not email or not mobile or not topic:
        return jsonify({
            "success": False,
            "message": "Please fill all required fields."
        }), 400

    # Remove ₹ symbol if present
    def clean_price(value):
        try:
            return float(str(value).replace("₹", "").replace(",", "").strip())
        except:
            return 0

    total_price = clean_price(data.get("totalPrice", 0))
    advance_price = clean_price(data.get("advancePrice", 0))
    remaining_price = clean_price(data.get("remainingPrice", 0))

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO requests (
            name,
            email,
            mobile,
            subject,
            topic,
            slides,
            language,
            style,
            graphics,
            requirements,
            plan,
            total_price,
            advance_price,
            remaining_price,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        email,
        mobile,
        data.get("subject", ""),
        topic,
        data.get("slides", 0),
        data.get("language", ""),
        data.get("style", ""),
        data.get("graphics", ""),
        data.get("requirements", ""),
        data.get("plan", ""),
        total_price,
        advance_price,
        remaining_price,
        "New",
        datetime.now().strftime("%d-%m-%Y %I:%M %p")
    ))

    request_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Request submitted successfully!",
        "request_id": request_id
    })
# ---------------- PPT UPLOAD ----------------

@app.route("/upload-ppt/<int:request_id>", methods=["POST"])
@admin_required
def upload_ppt(request_id):

    file = request.files.get("ppt_file")

    if not file or file.filename == "":
        return jsonify({
            "success": False,
            "message": "Please select a PPT file."
        })

    if not file.filename.lower().endswith(".pptx"):
        return jsonify({
            "success": False,
            "message": "Only .pptx files are allowed."
        })

    import os

    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)

    filename = f"request_{request_id}.pptx"
    filepath = os.path.join(upload_folder, filename)

    file.save(filepath)

    return jsonify({
        "success": True,
        "message": "PPT uploaded successfully!"
    })




# ---------------- UPDATE STATUS ----------------

@app.route("/update-status/<int:request_id>", methods=["POST"])
def update_status(request_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No status received"
        }), 400

    status = data.get("status")

    allowed_statuses = [
        "New",
        "Payment Pending",
        "Payment Received",
        "In Progress",
        "Completed"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid status"
        }), 400

    conn = get_db()

    conn.execute("""
        UPDATE requests
        SET status = ?
        WHERE id = ?
    """, (status, request_id))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Status updated"
    })


# ---------------- ADMIN PANEL ----------------

@app.route("/admin")
@admin_required
def admin():

    conn = get_db()

    requests_data = conn.execute("""
        SELECT *
        FROM requests
        ORDER BY id DESC
    """).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM requests"
    ).fetchone()[0]

    new_count = conn.execute(
        "SELECT COUNT(*) FROM requests WHERE status='New'"
    ).fetchone()[0]

    payment_pending = conn.execute(
        "SELECT COUNT(*) FROM requests WHERE status='Payment Pending'"
    ).fetchone()[0]

    payment_received = conn.execute(
        "SELECT COUNT(*) FROM requests WHERE status='Payment Received'"
    ).fetchone()[0]

    in_progress = conn.execute(
        "SELECT COUNT(*) FROM requests WHERE status='In Progress'"
    ).fetchone()[0]

    completed = conn.execute(
        "SELECT COUNT(*) FROM requests WHERE status='Completed'"
    ).fetchone()[0]

    conn.close()

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>PPTWALLAH - Admin Dashboard</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #141a2d;
    color: #f5eadc;
}}

.header {{
    background: #1e2640;
    padding: 22px 35px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}}

.header h1 {{
    margin: 0;
    color: #dc9750;
}}

.header span {{
    color: #aaa;
}}

.container {{
    padding: 30px;
    max-width: 1500px;
    margin: auto;
}}

.stats {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 18px;
    margin-bottom: 30px;
}}

.stat {{
    background: #1e2640;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid rgba(220,151,80,0.2);
}}

.stat h3 {{
    margin: 0 0 10px;
    color: #aaa;
    font-size: 14px;
}}

.stat strong {{
    font-size: 28px;
    color: #dc9750;
}}

.card {{
    background: #1e2640;
    border-radius: 16px;
    padding: 25px;
    overflow-x: auto;
}}

.card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}}

.card-header h2 {{
    margin: 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    min-width: 1200px;
}}

th {{
    text-align: left;
    padding: 14px;
    background: #141a2d;
    color: #dc9750;
    font-size: 13px;
}}

td {{
    padding: 14px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    font-size: 13px;
}}

tr:hover {{
    background: rgba(220,151,80,0.05);
}}

.price {{
    color: #dc9750;
    font-weight: bold;
}}

.status {{
    padding: 7px 10px;
    border-radius: 8px;
    border: none;
    background: #141a2d;
    color: white;
    cursor: pointer;
}}

.whatsapp {{
    display: inline-block;
    padding: 8px 12px;
    background: #25D366;
    color: white;
    text-decoration: none;
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
}}

.view-btn {{
    display: inline-block;
    padding: 8px 12px;
    background: #dc9750;
    color: #141a2d;
    text-decoration: none;
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
    margin-right: 5px;
}}

.empty {{
    text-align: center;
    padding: 50px;
    color: #888;
}}

@media(max-width: 1000px) {{
    .stats {{
        grid-template-columns: repeat(3, 1fr);
    }}
}}

@media(max-width: 600px) {{
    .container {{
        padding: 15px;
    }}

    .stats {{
        grid-template-columns: repeat(2, 1fr);
    }}

    .header {{
        padding: 18px;
    }}
}}

</style>

</head>

<body>

<div class="header">

    <div>
        <h1>🎨 PPTWALLAH</h1>
        <span>Admin Dashboard</span>
    </div>

    <a href="/admin-logout"
       style="
       color:white;
       background:#dc9750;
       padding:10px 18px;
       border-radius:8px;
       text-decoration:none;
       font-weight:bold;">
       Logout
    </a>

</div>

<div class="container">
<input
    type="text"
    id="searchInput"
    placeholder="Search name, mobile, topic..."
    onkeyup="searchRequests()"
    style="
    width:100%;
    padding:12px;
    margin-bottom:15px;
    border-radius:8px;
    border:1px solid #ccc;
    "
>


<!-- STATISTICS -->

<div class="stats">

    <div class="stat">
        <h3>Total Requests</h3>
        <strong>{total}</strong>
    </div>

    <div class="stat">
        <h3>New</h3>
        <strong>{new_count}</strong>
    </div>

    <div class="stat">
        <h3>Payment Pending</h3>
        <strong>{payment_pending}</strong>
    </div>

    <div class="stat">
        <h3>Payment Received</h3>
        <strong>{payment_received}</strong>
    </div>

    <div class="stat">
        <h3>In Progress</h3>
        <strong>{in_progress}</strong>
    </div>

    <div class="stat">
        <h3>Completed</h3>
        <strong>{completed}</strong>
    </div>

</div>


<!-- REQUESTS -->

<div class="card">

<div class="card-header">

    <h2>📋 PPT Requests</h2>

    <span>{total} Requests</span>

</div>


{
    "<table>" if requests_data else """
    <div class="empty">
        <h2>No Requests Yet</h2>
        <p>Customer requests will appear here.</p>
    </div>
    """
}


{
    """
    <table>

    <thead>

    <tr>
        <th>ID</th>
        <th>Customer</th>
        <th>Contact</th>
        <th>Topic</th>
        <th>Slides</th>
        <th>Plan</th>
        <th>Total</th>
        <th>Advance</th>
        <th>Remaining</th>
        <th>Status</th>
        <th>Actions</th>
        <th>Date</th>
    </tr>

    </thead>

    <tbody>

    """ if requests_data else ""
}


{
    "".join([
        f'''
        <tr>

            <td>#{r["id"]}</td>

            <td>
                <strong>{r["name"]}</strong><br>
                <small>{r["email"]}</small>
            </td>

            <td>{r["mobile"]}</td>

            <td>
                <strong>{r["topic"]}</strong><br>
                <small>{r["subject"] or ""}</small>
            </td>

            <td>{r["slides"]}</td>

            <td>{r["plan"]}</td>

            <td class="price">₹{r["total_price"]:.0f}</td>

            <td class="price">₹{r["advance_price"]:.0f}</td>

            <td>₹{r["remaining_price"]:.0f}</td>

            <td>

                <select
                    class="status"
                    onchange="updateStatus({r["id"]}, this.value)"
                >

                    <option {"selected" if r["status"]=="New" else ""}>
                        New
                    </option>

                    <option {"selected" if r["status"]=="Payment Pending" else ""}>
                        Payment Pending
                    </option>

                    <option {"selected" if r["status"]=="Payment Received" else ""}>
                        Payment Received
                    </option>

                    <option {"selected" if r["status"]=="In Progress" else ""}>
                        In Progress
                    </option>

                    <option {"selected" if r["status"]=="Completed" else ""}>
                        Completed
                    </option>

                </select>

            </td>

            <td>

    <a
        class="whatsapp"
        href="https://wa.me/91{''.join(filter(str.isdigit, str(r["mobile"])))}?text=Hello%20{r["name"].replace(" ", "%20")}%2C%20this%20is%20PPTWALLAH%20regarding%20your%20PPT%20request."
        target="_blank"
    >
        WhatsApp
    </a>

    <form
        action="/upload-ppt/{r["id"]}"
        method="POST"
        enctype="multipart/form-data"
        style="margin-top:10px;"
    >
        <input
            type="file"
            name="ppt_file"
            accept=".pptx"
            required
        >

        <button type="submit">
            Upload PPT
        </button>
    </form>

</td>

            <td>{r["created_at"]}</td>

        </tr>
        '''
        for r in requests_data
    ])
    if requests_data else ""
}


{
    "</tbody></table>" if requests_data else ""
}


</div>

</div>


<script>

async function updateStatus(id, status) {{

    try {{

        const response = await fetch(
            "/update-status/" + id,
            {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json"
                }},
                body: JSON.stringify({{
                    status: status
                }})
            }}
        );

        const result = await response.json();

        if (result.success) {{

            alert("Status updated successfully!");

            location.reload();

        }} else {{

            alert(result.message);

        }}

    }} catch(error) {{

        alert("Something went wrong.");

        console.error(error);

    }}

}}

</script>
<script>
function searchRequests() {{
    let input = document.getElementById("searchInput").value.toLowerCase();
    let rows = document.querySelectorAll("tbody tr");

    rows.forEach(row => {{
        row.style.display =
            row.innerText.toLowerCase().includes(input)
            ? ""
            : "none";
    }});
}}
</script>

</body>

</html>
"""


# Initialize database when app starts
init_db()

# ---------------- START SERVER ----------------

if __name__ == "__main__":
    init_db()

    print("PPTWALLAH Server Started")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
    