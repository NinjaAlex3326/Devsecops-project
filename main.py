import hmac, ipaddress, json, os, re, shutil, subprocess, threading
from pathlib import Path
import markdown
from flask import Flask, Response, abort, jsonify, render_template, request

BASE = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DATA_DIR", BASE / "data"))
DEPLOYS, DB, LOCK = DATA / "deployments", DATA / "deployments.json", threading.Lock()
REGIONS = {"aws": "eu-central-1", "azure": "westeurope", "oci": "eu-frankfurt-1"}
NAME_RE = re.compile(r"^[a-z][a-z0-9-]{2,30}$")
# Comenzi presetate: sigure si usor de extins. Comenzi libere doar cu ALLOW_CUSTOM_SSH=1
PRESETS = {"uptime": "uptime", "disk": "df -h", "memory": "free -m", "docker": "docker ps",
           "updates": "apt list --upgradable 2>/dev/null | head -20",
           "errors": "journalctl -p err -n 30 --no-pager"}
app = Flask(__name__)


def load():
    return json.loads(DB.read_text()) if DB.exists() else {}


def update(name, **kw):
    with LOCK:
        d = load(); d.setdefault(name, {}).update(kw)
        DATA.mkdir(parents=True, exist_ok=True); DB.write_text(json.dumps(d, indent=2))


@app.before_request
def auth():
    pw = os.environ.get("ADMIN_PASSWORD")
    if not pw:
        abort(503, "Seteaza ADMIN_PASSWORD in .env")
    a = request.authorization
    if not (a and hmac.compare_digest((a.password or "").encode(), pw.encode())):
        return Response("Autentificare necesara", 401, {"WWW-Authenticate": 'Basic realm="Deployer"'})


@app.after_request
def headers(r):
    r.headers.update({"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
                      "Referrer-Policy": "no-referrer",
                      "Content-Security-Policy": "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"})
    return r


def run_tf(name, action):
    wd = DEPLOYS / name
    try:
        with open(wd / "deploy.log", "a") as f:
            for cmd in (["init", "-input=false"], [action, "-auto-approve", "-input=false"]):
                if subprocess.run(["terraform", f"-chdir={wd}", *cmd], stdout=f,
                                  stderr=subprocess.STDOUT, timeout=1800).returncode:
                    raise RuntimeError(cmd[0])
        if action == "apply":
            ip = subprocess.run(["terraform", f"-chdir={wd}", "output", "-raw", "public_ip"],
                                capture_output=True, text=True).stdout.strip()
            update(name, status="running", ip=ip)
        else:
            update(name, status="destroyed", ip="")
    except Exception as e:
        update(name, status=f"failed: {e} (vezi log)")


def valid_ip(v):
    try:
        return str(ipaddress.ip_address(v))
    except ValueError:
        return None


@app.get("/")
def index():
    return render_template("dashboard.html", providers=list(REGIONS), pages=sorted(p.stem for p in (BASE / "docs").glob("*.md")))


@app.get("/api/vms")
def vms():
    return jsonify(load())


@app.post("/api/deploy")
def deploy():
    j = request.get_json() or {}
    name, prov, my_ip = j.get("name", ""), j.get("provider", ""), valid_ip(j.get("my_ip", ""))
    if prov not in REGIONS or not NAME_RE.match(name) or not my_ip:
        return jsonify(error="Nume, provider sau IP invalid"), 400
    if load().get(name, {}).get("status", "destroyed") != "destroyed":
        return jsonify(error="Exista deja"), 409
    wd = DEPLOYS / name
    shutil.rmtree(wd, ignore_errors=True)
    shutil.copytree(BASE / "terraform" / prov, wd)  # state separat per deployment
    key = Path(os.environ["SSH_PUBLIC_KEY_PATH"]).read_text().strip()
    (wd / "terraform.tfvars.json").write_text(json.dumps(
        {"name": name, "region": REGIONS[prov], "my_ip": my_ip, "public_key": key}))
    update(name, provider=prov, status="deploying", ip="", user="ubuntu")
    threading.Thread(target=run_tf, args=(name, "apply"), daemon=True).start()
    return jsonify(ok=True), 202


@app.post("/api/destroy")
def destroy():
    name = (request.get_json() or {}).get("name", "")
    rec = load().get(name)
    if not rec or rec["provider"] == "external":
        return jsonify(error="Nu exista / extern"), 404
    update(name, status="destroying")
    threading.Thread(target=run_tf, args=(name, "destroy"), daemon=True).start()
    return jsonify(ok=True), 202


@app.post("/api/vms")  # inregistreaza VM existent (ex. al unui client)
def add_vm():
    j = request.get_json() or {}
    name, ip, user = j.get("name", ""), valid_ip(j.get("ip", "")), j.get("user", "ubuntu")
    if not NAME_RE.match(name) or not ip or not re.match(r"^[a-z_][a-z0-9_-]{0,31}$", user):
        return jsonify(error="Date invalide"), 400
    update(name, provider="external", status="running", ip=ip, user=user)
    return jsonify(ok=True)


@app.post("/api/ssh")
def ssh():
    j = request.get_json() or {}
    rec = load().get(j.get("name", ""))
    cmd = PRESETS.get(j.get("preset")) or (j.get("command") if os.environ.get("ALLOW_CUSTOM_SSH") == "1" else None)
    if not rec or not rec.get("ip") or not cmd:
        return jsonify(error="VM sau comanda invalida"), 400
    r = subprocess.run(["ssh", "-i", os.environ["SSH_KEY_PATH"], "-o", "StrictHostKeyChecking=accept-new",
                        "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", f"{rec['user']}@{rec['ip']}", cmd],
                       capture_output=True, text=True, timeout=60)
    return jsonify(output=(r.stdout + r.stderr)[-5000:], code=r.returncode)


@app.get("/api/log/<name>")
def log(name):
    f = DEPLOYS / name / "deploy.log"
    if not NAME_RE.match(name) or not f.exists():
        return jsonify(output="(fara log)")
    return jsonify(output=f.read_text()[-6000:])


@app.get("/docs/<page>")
def docs(page):
    f = BASE / "docs" / f"{page}.md"
    if not re.match(r"^[\w-]+$", page) or not f.exists():
        abort(404)
    html = markdown.markdown(f.read_text(), extensions=["fenced_code", "tables"])
    return render_template("docs.html", html=html, pages=sorted(p.stem for p in (BASE / "docs").glob("*.md")))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
