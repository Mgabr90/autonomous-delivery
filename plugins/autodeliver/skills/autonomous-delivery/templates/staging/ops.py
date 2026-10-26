"""Staging ops endpoint: an HTTPS front (behind your reverse proxy) for a forced-command SSH gate.

- Every request must carry the header named by OPS_HEADER (default X-Ops-Token). Only SHA-256 hashes of the
  tokens are stored, one per line per client, in TOKEN_FILE. It is re-read on every request, so deleting a line
  revokes that client with no restart.
- Each verb is relayed over SSH to the host, where gate.sh (a forced command) decides what is allowed.
  This container has no Docker socket and no shell access of its own.
- Long verbs run as background jobs; poll GET /_ops/jobs/<id>.
- /_ops/app/api/* is proxied to the staging app on the internal network. That skips any site-wide basic auth,
  but never the app's own login.
"""
import hashlib, hmac, http.client, json, os, re, secrets, subprocess, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

OPS_HEADER = os.environ.get("OPS_HEADER", "X-Ops-Token")
TOKEN_FILE = os.environ.get("TOKEN_FILE", "/run/ops/token_sha256")
SSH_TARGET = os.environ.get("SSH_TARGET", "root@172.17.0.1")  # the Docker host as seen from this container
SSH = ["ssh", "-i", "/run/ops/key", "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
       "-o", "UserKnownHostsFile=/run/ops/known_hosts", "-o", "StrictHostKeyChecking=yes", SSH_TARGET]
APP_HOST = os.environ.get("APP_HOST", "app")
APP_PORT = int(os.environ.get("APP_PORT", "3000"))
TEST_DOMAIN = re.escape(os.environ.get("TEST_ACCOUNT_DOMAIN", "example.com"))

SHA = re.compile(r"^[0-9a-f]{7,40}$")
EMAIL = re.compile(rf"^[A-Za-z0-9._%+-]+@{TEST_DOMAIN}$")
APP_PREFIX = "/_ops/app/"
MAX_APP_BODY = 10_000_000
DROP_REQ = {"host", OPS_HEADER.lower(), "content-length", "connection", "authorization", "proxy-authorization"}
DROP_RES = {"transfer-encoding", "connection", "content-length"}

# verb -> (method, kind, arg). kind: "sync" (run and reply), "job" (background), "stdin" (request body piped to the gate).
# arg: None, ("int", query_key, default, max), ("sha",), ("email",) or a byte limit for "stdin".
VERBS = {
    "status": ("GET", "sync", None),
    "logs": ("GET", "sync", ("int", "n", 200, 500)),
    "logs-since": ("GET", "sync", ("int", "m", 60, 1440)),
    "rehearsal-status": ("GET", "sync", None),
    "upload": ("POST", "stdin", 200_000_000),
    "sql-ro": ("POST", "stdin", 100_000),
    "deploy": ("POST", "job", ("sha",)),
    "verify-test-user": ("POST", "sync", ("email",)),
    "rehearsal-up": ("POST", "job", None),
    "rehearsal-restore": ("POST", "job", None),
    "rehearsal-migrate": ("POST", "job", ("sha",)),
    "rehearsal-check": ("POST", "job", None),
    "rehearsal-down": ("POST", "job", None),
}
JOBS, JOBS_LOCK = {}, threading.Lock()


def token_shas():
    try:
        with open(TOKEN_FILE) as f:
            return {s for s in (line.split("#")[0].strip().lower() for line in f) if len(s) == 64}
    except OSError:
        return set()


def gate(args, stdin=None, timeout=120):
    p = subprocess.run(SSH + [" ".join(args)], input=stdin, capture_output=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def run_job(job_id, args):
    try:
        code, out = gate(args, timeout=3600)
    except subprocess.TimeoutExpired:
        code, out = 124, b"timed out after 3600s"
    with JOBS_LOCK:
        JOBS[job_id].update(state="done", exit=code, output=out.decode("utf-8", "replace")[-20000:], ended=time.time())


class H(BaseHTTPRequestHandler):
    server_version = "staging-ops"

    def log_message(self, fmt, *a):  # never log headers: they carry the token
        print(f"{self.address_string()} {self.command} {urlparse(self.path).path} {a[1] if len(a) > 1 else ''}", flush=True)

    def send(self, code, body, ctype="text/plain; charset=utf-8", extra=None):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def authed(self):
        tok = self.headers.get(OPS_HEADER, "")
        digest = hashlib.sha256(tok.encode()).hexdigest()
        ok = bool(tok) and any([hmac.compare_digest(digest, s) for s in token_shas()])
        if not ok:
            self.send(401, "unauthorized\n")
        return ok

    def body(self, limit):
        n = int(self.headers.get("Content-Length") or 0)
        if n > limit:
            self.send(413, "too large\n")
            return None
        return self.rfile.read(n)

    def start_job(self, args):
        job_id = secrets.token_hex(8)
        with JOBS_LOCK:
            for old in [k for k, j in JOBS.items() if j.get("ended", time.time()) < time.time() - 86400]:
                del JOBS[old]
            JOBS[job_id] = {"id": job_id, "args": args, "state": "running", "started": time.time()}
        threading.Thread(target=run_job, args=(job_id, args), daemon=True).start()
        self.send(202, json.dumps({"job": job_id, "poll": f"/_ops/jobs/{job_id}"}) + "\n", "application/json")

    def proxy_app(self):
        rest = self.path[len(APP_PREFIX):]
        if not rest.startswith("api/") or ".." in rest:
            return self.send(404, "only /_ops/app/api/* is proxied\n")
        data = self.body(MAX_APP_BODY) if self.command in ("POST", "PUT", "PATCH", "DELETE") else b""
        if data is None:
            return
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in DROP_REQ and not k.lower().startswith("x-forwarded")}
        conn = http.client.HTTPConnection(APP_HOST, APP_PORT, timeout=120)
        try:
            conn.request(self.command, "/" + rest, body=data or None, headers=headers)
            res = conn.getresponse()
            payload = res.read()
        except OSError as e:
            return self.send(502, f"app unreachable: {e}\n")
        finally:
            conn.close()
        self.send_response(res.status)
        for k, v in res.getheaders():
            if k.lower() not in DROP_RES:
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def dispatch(self):
        if not self.authed():
            return
        if self.path.startswith(APP_PREFIX):
            return self.proxy_app()
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        m = re.fullmatch(r"/_ops/jobs/([0-9a-f]{16})", u.path)
        if m and self.command == "GET":
            with JOBS_LOCK:
                job = JOBS.get(m.group(1))
            return self.send(200, json.dumps(job) + "\n", "application/json") if job else self.send(404, "no such job\n")
        verb = u.path.removeprefix("/_ops/")
        spec = VERBS.get(verb)
        if not spec or spec[0] != self.command:
            listing = " | ".join(f"{m} {v}" for v, (m, _, _) in VERBS.items())
            return self.send(404, f"verbs: {listing} | GET jobs/<id> | ANY app/api/*\n")
        _, kind, arg = spec
        args = [verb]
        if isinstance(arg, tuple) and arg[0] == "int":
            _, key, default, cap = arg
            raw = q.get(key, str(default))
            args.append(str(min(int(raw), cap)) if raw.isdigit() else str(default))
        elif isinstance(arg, tuple) and arg[0] == "sha":
            if not SHA.match(q.get("sha", "")):
                return self.send(400, "sha=<7-40 hex> required\n")
            args.append(q["sha"])
        elif isinstance(arg, tuple) and arg[0] == "email":
            if not EMAIL.match(q.get("email", "")):
                return self.send(400, "email=<test account> required\n")
            args.append(q["email"])
        if kind == "stdin":
            data = self.body(arg)
            if data is None:
                return
            code, out = gate(args, stdin=data, timeout=600)
            return self.send(200 if code == 0 else 502, out, extra={"X-Exit-Code": str(code)})
        if kind == "job":
            return self.start_job(args)
        code, out = gate(args)
        self.send(200 if code == 0 else 502, out, extra={"X-Exit-Code": str(code)})

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = dispatch


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), H).serve_forever()
