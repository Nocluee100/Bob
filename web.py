import json, os, secrets, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import brain, commands, config, main

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "web", "index.html")
PORT = int(os.environ.get("PORT", 7860))
OLD = 30 * 60
MAX = 300
LONG = 400

chats = {}
keep = threading.Lock()
think = threading.Lock()
waiting = [0]


def tidy():
    while True:
        time.sleep(60)
        now = time.time()
        with keep:
            for k in [k for k, v in chats.items() if now - v[1] > OLD and not v[2]]:
                chats.pop(k)[0].mem.wipe()


def start():
    with keep:
        if len(chats) >= MAX:
            old = min(chats, key=lambda k: chats[k][1])
            chats.pop(old)[0].mem.wipe()
        k = secrets.token_urlsafe(12)
        c = main.Chat()
        chats[k] = [c, time.time(), False]
    return k, {"mood": c.bob.mood, "reply": config.HELLO, "tummy": c.bob.tummy()}


def say(k, line):
    with keep:
        v = chats.get(k)
        if not v:
            return {"gone": True}
        if v[2]:
            return {"note": "Bob is still thinking about the last thing!"}
        v[1] = time.time()
        v[2] = True
    try:
        return answer(v[0], line)
    finally:
        v[2] = False
        v[1] = time.time()


def answer(chat, line):
    bob = chat.bob
    cmd, arg = commands.parse(line)
    out = {}

    if cmd in (None, "feed", "sleep") and bob.napped():
        out["note"] = "(you were gone a while... Bob fell asleep)"
        chat.mem.add("Bob", "Zzz... (fell asleep while you were away)", mood="sleeping")

    if cmd == "quit":
        return {"mood": "sleeping", "reply": "Bye bye! I go nap in the computer now.", "bye": True}
    if cmd == "help":
        return {"help": commands.HELP.replace("  /clear     clear the screen\n", "")}
    if cmd == "status":
        s = f"Bob is feeling: {bob.mood}     Tummy: {commands.tummy_bar(bob.tummy())}"
        return {"note": s + ("\nBob is still waiting for a sorry..." if bob.upset else "")}
    if cmd == "history":
        return {"history": chat.mem.read().rstrip() or "(empty)"}
    if cmd == "clear":
        return {"clear": True}
    if cmd == "unknown":
        return {"note": "Bob doesn't know that one. Type /help"}

    waiting[0] += 1
    try:
        with think:
            m, txt = chat.turn(cmd, arg)
    except brain.BrainError as e:
        m, txt = "sad", str(e)
    finally:
        waiting[0] -= 1
    out.update(mood=m, reply=txt, tummy=bob.tummy())
    return out


class Handler(BaseHTTPRequestHandler):
    def send(self, code, data, kind="application/json"):
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(PAGE, "rb") as f:
                self.send(200, f.read(), "text/html; charset=utf-8")
        elif self.path == "/api/line":
            self.send(200, {"waiting": waiting[0]})
        else:
            self.send(404, {"error": "nope"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 4000:
            return self.send(413, {"error": "too long"})
        try:
            got = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return self.send(400, {"error": "bad json"})
        if self.path == "/api/start":
            k, out = start()
            out["id"] = k
            return self.send(200, out)
        if self.path == "/api/say":
            line = str(got.get("text", "")).strip()[:LONG]
            if not line:
                return self.send(400, {"error": "empty"})
            return self.send(200, say(str(got.get("id", "")), line))
        self.send(404, {"error": "nope"})

    def log_message(self, *a):
        pass


def run():
    threading.Thread(target=tidy, daemon=True).start()
    try:
        brain.check()
    except brain.BrainError as e:
        print("heads up:", e, file=sys.stderr)
    s = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Bob is at http://localhost:{PORT}")
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        pass
    with keep:
        for c, _, _ in chats.values():
            c.mem.wipe()


if __name__ == "__main__":
    run()
