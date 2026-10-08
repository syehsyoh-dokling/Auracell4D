"""
AuraCell 4D - GUI launcher + tiny local API (no external dependencies).

    python gui/launch_gui.py            # serves http://127.0.0.1:8765 and opens the browser
    python gui/launch_gui.py --no-open  # just serve

Endpoints used by gui/index.html (Step 4 "Measured results" panel):
    GET  /api/results            -> results/ablation.json (or 404 if evaluate.py has not been run)
    GET  /api/status             -> {"running": bool, "returncode": int|null, "log_tail": [...]}
    POST /api/run?preset=quick   -> runs `python evaluate.py --seqs 01 --detect gt --trackers greedy_nogate ilp_gate`
    POST /api/run?preset=full    -> runs the full ablation (15-30 min)
Everything runs locally; nothing leaves the machine.
"""
import argparse, json, subprocess, sys, threading, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent
GUI = ROOT / "gui"
RESULTS = ROOT / "results"
PRESETS = {
    "quick": ["--seqs", "01", "--detect", "gt", "--trackers", "greedy_nogate", "ilp_gate"],
    "full": [],
}
STATE = {"proc": None, "log": [], "returncode": None, "preset": None}


def _pump(proc):
    for line in proc.stdout:
        STATE["log"].append(line.rstrip())
        if len(STATE["log"]) > 400:
            del STATE["log"][:100]
    proc.wait()
    STATE["returncode"] = proc.returncode


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(GUI), **kw)

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/results":
            full = RESULTS / "ablation.json"
            quick = RESULTS / "quick" / "ablation.json"
            if not full.exists() and not quick.exists():
                return self._json(404, {"error": "no results yet - run evaluate.py (or click Run quick benchmark)"})
            out = {"full": json.loads(full.read_text()) if full.exists() else None,
                   "quick": json.loads(quick.read_text()) if quick.exists() else None}
            return self._json(200, out)
        if u.path == "/api/status":
            running = STATE["proc"] is not None and STATE["proc"].poll() is None
            return self._json(200, {"running": running, "returncode": STATE["returncode"],
                                    "preset": STATE["preset"], "log_tail": STATE["log"][-25:]})
        return super().do_GET()

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/run":
            if STATE["proc"] is not None and STATE["proc"].poll() is None:
                return self._json(409, {"error": "a run is already in progress"})
            preset = parse_qs(u.query).get("preset", ["quick"])[0]
            if preset not in PRESETS:
                return self._json(400, {"error": f"unknown preset {preset}"})
            out_dir = RESULTS if preset == "full" else RESULTS / "quick"  # quick run must not clobber the full ablation
            cmd = [sys.executable, "-u", str(ROOT / "evaluate.py"), "--data", str(ROOT / "data"),
                   "--out", str(out_dir)] + PRESETS[preset]
            STATE.update(log=[f"$ {' '.join(cmd)}"], returncode=None, preset=preset)
            STATE["proc"] = subprocess.Popen(cmd, cwd=str(ROOT), stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
            threading.Thread(target=_pump, args=(STATE["proc"],), daemon=True).start()
            return self._json(202, {"started": True, "preset": preset})
        return self._json(404, {"error": "unknown endpoint"})

    def log_message(self, fmt, *args):  # quieter console
        if "/api/status" not in (args[0] if args else ""):
            super().log_message(fmt, *args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-open", action="store_true")
    a = ap.parse_args()
    url = f"http://127.0.0.1:{a.port}/index.html"
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print("AuraCell 4D GUI  ->", url, "\n(Ctrl+C to stop)")
    if not a.no_open:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
