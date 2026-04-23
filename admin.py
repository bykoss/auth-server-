"""
admin.py — CLI para gestionar tokens desde tu PC
Uso:
  python admin.py list
  python admin.py create [nombre_usuario]
  python admin.py revoke UNTCH-XXXX-XXXX
  python admin.py restore UNTCH-XXXX-XXXX
  python admin.py info UNTCH-XXXX-XXXX
"""
import sys, json, os, time, random, string, hashlib
from datetime import datetime, timezone

TOKENS_FILE = "tokens_db.json"

def load_db():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE) as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(TOKENS_FILE, "w") as f:
        json.dump(db, f, indent=2)

def fmt(ts):
    if not ts: return "Nunca"
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def hours_active(ss):
    if not ss: return "—"
    d = time.time() - ss
    return f"{int(d//3600)}h {int((d%3600)//60)}m"

def gen_token():
    part = lambda n: ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
    return f"UNTCH-{part(4)}-{part(4)}"

RED   = "\033[91m"
GRN   = "\033[92m"
WHT   = "\033[97m"
GRY   = "\033[90m"
RST   = "\033[0m"
BLD   = "\033[1m"

def cmd_list():
    db = load_db()
    if not db:
        print(f"{RED}No hay tokens.{RST}"); return
    print(f"\n{BLD}{RED}{'TOKEN':<22} {'USUARIO':<18} {'ESTADO':<12} {'ACTIVO':<12} {'ÚLTIMO ACCESO'}{RST}")
    print("─" * 85)
    for tk, e in db.items():
        if e.get("revoked"):   estado = f"{RED}REVOCADO{RST}"
        elif e.get("session_start"): estado = f"{GRN}EN USO{RST}"
        else:                   estado = f"{GRY}SIN USAR{RST}"
        activo = hours_active(e.get("session_start"))
        last   = fmt(e.get("last_seen"))
        user   = e.get("user") or "—"
        print(f"{WHT}{tk:<22}{RST} {GRY}{user:<18}{RST} {estado:<20} {RED}{activo:<12}{RST} {GRY}{last}{RST}")
    print()

def cmd_create(usuario=""):
    db    = load_db()
    token = gen_token()
    db[token] = {
        "user": usuario, "active": True, "created": time.time(),
        "last_seen": None, "session_start": None, "revoked": False
    }
    save_db(db)
    print(f"\n{GRN}Token creado:{RST}")
    print(f"  {BLD}{WHT}{token}{RST}")
    if usuario:
        print(f"  Para: {GRY}{usuario}{RST}")
    print()

def cmd_revoke(token):
    db = load_db()
    token = token.upper()
    if token not in db:
        print(f"{RED}Token no encontrado.{RST}"); return
    db[token]["revoked"] = True
    db[token]["active"]  = False
    save_db(db)
    print(f"{RED}Token revocado: {WHT}{token}{RST}")

def cmd_restore(token):
    db = load_db()
    token = token.upper()
    if token not in db:
        print(f"{RED}Token no encontrado.{RST}"); return
    db[token]["revoked"] = False
    db[token]["active"]  = True
    save_db(db)
    print(f"{GRN}Token restaurado: {WHT}{token}{RST}")

def cmd_info(token):
    db = load_db()
    token = token.upper()
    if token not in db:
        print(f"{RED}Token no encontrado.{RST}"); return
    e = db[token]
    print(f"\n{BLD}{WHT}Token:{RST} {token}")
    print(f"  Usuario:      {e.get('user') or '—'}")
    print(f"  Estado:       {'REVOCADO' if e.get('revoked') else 'ACTIVO'}")
    print(f"  Tiempo activo:{hours_active(e.get('session_start'))}")
    print(f"  Último acceso:{fmt(e.get('last_seen'))}")
    print(f"  Creado:       {fmt(e.get('created'))}")
    print()

def main():
    args = sys.argv[1:]
    if not args:
        print(f"""
{BLD}{RED}BY UNTOUCHABLE — Admin CLI{RST}

  {WHT}python admin.py list{RST}              {GRY}Ver todos los tokens{RST}
  {WHT}python admin.py create [usuario]{RST}  {GRY}Crear nuevo token{RST}
  {WHT}python admin.py revoke TOKEN{RST}      {GRY}Revocar acceso{RST}
  {WHT}python admin.py restore TOKEN{RST}     {GRY}Restaurar acceso{RST}
  {WHT}python admin.py info TOKEN{RST}        {GRY}Ver info de un token{RST}
""")
        return
    cmd = args[0].lower()
    if   cmd == "list":    cmd_list()
    elif cmd == "create":  cmd_create(args[1] if len(args)>1 else "")
    elif cmd == "revoke":  cmd_revoke(args[1] if len(args)>1 else "")
    elif cmd == "restore": cmd_restore(args[1] if len(args)>1 else "")
    elif cmd == "info":    cmd_info(args[1] if len(args)>1 else "")
    else: print(f"{RED}Comando desconocido: {args[0]}{RST}")

if __name__ == "__main__":
    main()
