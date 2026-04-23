"""
BY UNTOUCHABLE — Auth Server
Railway deployment
"""
import os, json, time, secrets, hashlib
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ─── Archivos de datos ───────────────────────
TOKENS_FILE = "tokens_db.json"

ADMIN_USER = "untouchable"
ADMIN_PASS_HASH = hashlib.sha256("242011".encode()).hexdigest()

# ─── DB helpers ──────────────────────────────
def load_db():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    # Tokens iniciales pre-cargados
    db = {
        "UNTCH-K9X2-M4R7": {"user": "", "active": True,  "created": time.time(), "last_seen": None, "session_start": None, "revoked": False},
        "UNTCH-P3N8-Q6W1": {"user": "", "active": True,  "created": time.time(), "last_seen": None, "session_start": None, "revoked": False},
        "UNTCH-H7T5-B2L9": {"user": "", "active": True,  "created": time.time(), "last_seen": None, "session_start": None, "revoked": False},
        "UNTCH-F1J6-D8V3": {"user": "", "active": True,  "created": time.time(), "last_seen": None, "session_start": None, "revoked": False},
        "UNTCH-C4S0-Y5E2": {"user": "", "active": True,  "created": time.time(), "last_seen": None, "session_start": None, "revoked": False},
    }
    save_db(db)
    return db

def save_db(db):
    with open(TOKENS_FILE, "w") as f:
        json.dump(db, f, indent=2)

def fmt_time(ts):
    if not ts: return "Nunca"
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def hours_active(session_start):
    if not session_start: return "—"
    diff = time.time() - session_start
    h = int(diff // 3600)
    m = int((diff % 3600) // 60)
    return f"{h}h {m}m"

# ─── Auth decorator ───────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────
#  API ENDPOINTS (usados por el tool)
# ─────────────────────────────────────────────
@app.route("/api/validate", methods=["POST"])
def validate():
    data  = request.get_json(silent=True) or {}
    token = data.get("token", "").strip().upper()
    user  = data.get("user",  "").strip()
    db    = load_db()
    if token not in db:
        return jsonify({"ok": False, "msg": "Token inválido"}), 401
    entry = db[token]
    if entry.get("revoked"):
        return jsonify({"ok": False, "msg": "Token revocado"}), 403
    if not entry.get("active"):
        return jsonify({"ok": False, "msg": "Token inactivo"}), 403
    # Registrar sesión
    entry["user"]          = user
    entry["last_seen"]     = time.time()
    entry["session_start"] = time.time()
    db[token] = entry
    save_db(db)
    return jsonify({"ok": True, "msg": "Acceso concedido"})

@app.route("/api/heartbeat", methods=["POST"])
def heartbeat():
    data  = request.get_json(silent=True) or {}
    token = data.get("token", "").strip().upper()
    db    = load_db()
    if token not in db or db[token].get("revoked"):
        return jsonify({"ok": False}), 403
    db[token]["last_seen"] = time.time()
    save_db(db)
    return jsonify({"ok": True})

# ─────────────────────────────────────────────
#  PANEL WEB
# ─────────────────────────────────────────────
PANEL_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BY UNTOUCHABLE — Panel</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0a0a0a;color:#fff;font-family:'Courier New',monospace;min-height:100vh}
  .header{background:#111;border-bottom:2px solid #cc0000;padding:18px 32px;display:flex;justify-content:space-between;align-items:center}
  .header h1{color:#cc0000;font-size:1.4em;letter-spacing:3px}
  .header small{color:#666;font-size:.8em}
  .logout{color:#666;text-decoration:none;font-size:.85em;border:1px solid #333;padding:6px 14px;border-radius:4px}
  .logout:hover{border-color:#cc0000;color:#fff}
  .container{max-width:1100px;margin:0 auto;padding:32px 24px}
  .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:32px}
  .stat{background:#111;border:1px solid #222;border-left:3px solid #cc0000;padding:20px;border-radius:6px}
  .stat .num{font-size:2em;color:#cc0000;font-weight:bold}
  .stat .label{color:#666;font-size:.85em;margin-top:4px}
  .section-title{color:#cc0000;font-size:.9em;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;border-bottom:1px solid #222;padding-bottom:8px}
  table{width:100%;border-collapse:collapse;background:#111;border-radius:8px;overflow:hidden}
  th{background:#1a1a1a;color:#cc0000;text-align:left;padding:12px 16px;font-size:.8em;letter-spacing:1px;text-transform:uppercase;border-bottom:1px solid #222}
  td{padding:12px 16px;border-bottom:1px solid #1a1a1a;font-size:.88em;color:#ccc}
  tr:last-child td{border-bottom:none}
  tr:hover td{background:#141414}
  .badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:.75em;font-weight:bold;letter-spacing:1px}
  .badge.active{background:#0d2a0d;color:#4caf50;border:1px solid #1e5c1e}
  .badge.revoked{background:#2a0d0d;color:#cc0000;border:1px solid #5c1e1e}
  .badge.unused{background:#1a1a1a;color:#666;border:1px solid #333}
  .token-val{color:#fff;font-size:.92em;letter-spacing:1px}
  .time-active{color:#cc0000;font-weight:bold}
  .actions{display:flex;gap:8px}
  .btn{padding:5px 14px;border:none;border-radius:4px;cursor:pointer;font-family:'Courier New',monospace;font-size:.8em;font-weight:bold;letter-spacing:1px;transition:.2s}
  .btn-revoke{background:#2a0d0d;color:#cc0000;border:1px solid #5c1e1e}
  .btn-revoke:hover{background:#cc0000;color:#fff}
  .btn-restore{background:#0d2a0d;color:#4caf50;border:1px solid #1e5c1e}
  .btn-restore:hover{background:#4caf50;color:#000}
  .flash{padding:12px 20px;border-radius:6px;margin-bottom:20px;font-size:.9em}
  .flash.ok{background:#0d2a0d;border:1px solid #1e5c1e;color:#4caf50}
  .flash.err{background:#2a0d0d;border:1px solid #5c1e1e;color:#cc0000}
  .create-form{background:#111;border:1px solid #222;border-radius:8px;padding:24px;margin-bottom:32px}
  .create-form input{background:#0a0a0a;border:1px solid #333;color:#fff;padding:10px 14px;border-radius:4px;font-family:'Courier New',monospace;font-size:.9em;width:260px}
  .create-form input:focus{outline:none;border-color:#cc0000}
  .btn-create{background:#cc0000;color:#fff;padding:10px 20px;border:none;border-radius:4px;cursor:pointer;font-family:'Courier New',monospace;font-weight:bold;letter-spacing:1px;margin-left:10px}
  .btn-create:hover{background:#ff0000}
</style>
<script>
  // Auto-refresh cada 30 segundos
  setTimeout(()=>location.reload(), 30000);
</script>
</head>
<body>
<div class="header">
  <div>
    <h1>⚡ BY UNTOUCHABLE</h1>
    <small>Panel de Administración — Tokens</small>
  </div>
  <a href="/logout" class="logout">Cerrar sesión</a>
</div>
<div class="container">

{% if msg %}
<div class="flash {{ 'ok' if msg_type=='ok' else 'err' }}">{{ msg }}</div>
{% endif %}

<div class="stats">
  <div class="stat">
    <div class="num">{{ total }}</div>
    <div class="label">Tokens totales</div>
  </div>
  <div class="stat">
    <div class="num">{{ activos }}</div>
    <div class="label">Activos / en uso</div>
  </div>
  <div class="stat">
    <div class="num">{{ revocados }}</div>
    <div class="label">Revocados</div>
  </div>
</div>

<div class="section-title">Gestión de Tokens</div>
<div class="create-form">
  <form method="POST" action="/panel/create" style="display:flex;align-items:center;gap:0">
    <input type="text" name="custom_token" placeholder="Token personalizado (opcional)" />
    <button type="submit" class="btn-create">+ CREAR TOKEN</button>
  </form>
</div>

<table>
  <thead>
    <tr>
      <th>Token</th>
      <th>Usuario</th>
      <th>Estado</th>
      <th>Tiempo activo</th>
      <th>Último acceso</th>
      <th>Creado</th>
      <th>Acciones</th>
    </tr>
  </thead>
  <tbody>
  {% for token, entry in tokens.items() %}
  <tr>
    <td><span class="token-val">{{ token }}</span></td>
    <td>{{ entry.user or '—' }}</td>
    <td>
      {% if entry.revoked %}
        <span class="badge revoked">REVOCADO</span>
      {% elif entry.session_start %}
        <span class="badge active">EN USO</span>
      {% else %}
        <span class="badge unused">SIN USAR</span>
      {% endif %}
    </td>
    <td><span class="time-active">{{ entry.hours_active }}</span></td>
    <td>{{ entry.last_seen_fmt }}</td>
    <td>{{ entry.created_fmt }}</td>
    <td>
      <div class="actions">
        {% if not entry.revoked %}
        <form method="POST" action="/panel/revoke/{{ token }}">
          <button class="btn btn-revoke">REVOCAR</button>
        </form>
        {% else %}
        <form method="POST" action="/panel/restore/{{ token }}">
          <button class="btn btn-restore">RESTAURAR</button>
        </form>
        {% endif %}
      </div>
    </td>
  </tr>
  {% endfor %}
  </tbody>
</table>

</div>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>BY UNTOUCHABLE — Login</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0a0a0a;color:#fff;font-family:'Courier New',monospace;display:flex;align-items:center;justify-content:center;min-height:100vh}
  .box{background:#111;border:1px solid #222;border-top:3px solid #cc0000;padding:40px 48px;border-radius:8px;width:360px}
  h1{color:#cc0000;font-size:1.3em;letter-spacing:3px;margin-bottom:8px}
  p{color:#666;font-size:.8em;margin-bottom:28px}
  label{color:#888;font-size:.8em;display:block;margin-bottom:6px;letter-spacing:1px}
  input{width:100%;background:#0a0a0a;border:1px solid #333;color:#fff;padding:10px 14px;border-radius:4px;font-family:'Courier New',monospace;font-size:.95em;margin-bottom:18px}
  input:focus{outline:none;border-color:#cc0000}
  button{width:100%;background:#cc0000;color:#fff;border:none;padding:12px;border-radius:4px;cursor:pointer;font-family:'Courier New',monospace;font-weight:bold;letter-spacing:2px;font-size:.95em}
  button:hover{background:#ff0000}
  .err{color:#cc0000;font-size:.85em;margin-bottom:16px;background:#1a0505;padding:10px;border-radius:4px;border:1px solid #5c1e1e}
</style>
</head>
<body>
<div class="box">
  <h1>⚡ UNTOUCHABLE</h1>
  <p>Panel de Administración</p>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <form method="POST">
    <label>USUARIO</label>
    <input type="text" name="user" autocomplete="off" />
    <label>CONTRASEÑA</label>
    <input type="password" name="pass" />
    <button type="submit">ENTRAR</button>
  </form>
</div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("user", "")
        p = request.form.get("pass", "")
        if u == ADMIN_USER and hashlib.sha256(p.encode()).hexdigest() == ADMIN_PASS_HASH:
            session["admin"] = True
            return redirect("/panel")
        return render_template_string(LOGIN_HTML, error="Usuario o contraseña incorrectos")
    return render_template_string(LOGIN_HTML, error=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def index():
    return redirect("/panel")

@app.route("/panel")
@admin_required
def panel():
    db    = load_db()
    total = len(db)
    activos   = sum(1 for e in db.values() if not e.get("revoked") and e.get("session_start"))
    revocados = sum(1 for e in db.values() if e.get("revoked"))
    tokens = {}
    for tk, entry in db.items():
        tokens[tk] = {
            **entry,
            "last_seen_fmt": fmt_time(entry.get("last_seen")),
            "created_fmt":   fmt_time(entry.get("created")),
            "hours_active":  hours_active(entry.get("session_start")),
        }
    return render_template_string(PANEL_HTML, tokens=tokens,
                                   total=total, activos=activos, revocados=revocados,
                                   msg=None, msg_type=None)

@app.route("/panel/revoke/<token>", methods=["POST"])
@admin_required
def revoke(token):
    db = load_db()
    if token in db:
        db[token]["revoked"] = True
        db[token]["active"]  = False
        save_db(db)
    return redirect("/panel")

@app.route("/panel/restore/<token>", methods=["POST"])
@admin_required
def restore(token):
    db = load_db()
    if token in db:
        db[token]["revoked"] = False
        db[token]["active"]  = True
        save_db(db)
    return redirect("/panel")

@app.route("/panel/create", methods=["POST"])
@admin_required
def create_token():
    db = load_db()
    custom = request.form.get("custom_token", "").strip().upper()
    if custom:
        new_token = custom
    else:
        import random, string
        part = lambda n: ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
        new_token = f"UNTCH-{part(4)}-{part(4)}"
    db[new_token] = {
        "user": "", "active": True, "created": time.time(),
        "last_seen": None, "session_start": None, "revoked": False
    }
    save_db(db)
    return redirect("/panel")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
