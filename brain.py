import json
import urllib.error, urllib.request

import config
from sprites import MOODS

SHAPE = {
    "type": "object",
    "properties": {
        "mean": {"type": "boolean"},
        "sorry": {"type": "boolean"},
        "mood": {"type": "string", "enum": list(MOODS)},
        "things": {"type": "string"},
        "twist": {"type": "string"},
        "reply": {"type": "string"},
    },
    "required": ["mean", "sorry", "mood", "things", "twist", "reply"],
}


class BrainError(Exception):
    pass


def req(path, body=None, timeout=10):
    url = config.HOST.rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def check():
    try:
        tags = req("/api/tags")
    except (urllib.error.URLError, OSError):
        raise BrainError("My brain is off! Please start Ollama.")
    names = {m.get("name", "") for m in tags.get("models", [])}
    want = config.MODEL if ":" in config.MODEL else config.MODEL + ":latest"
    if want not in names:
        raise BrainError(f"I need my brain! Type: ollama pull {config.MODEL}")


def body(msgs, temp=None):
    return {
        "model": config.MODEL,
        "messages": msgs,
        "stream": False,
        "think": False,
        "format": SHAPE,
        "keep_alive": "30m",
        "options": {
            "temperature": temp or config.TEMP,
            "top_p": config.TOP_P,
            "top_k": config.TOP_K,
            "min_p": config.MIN_P,
            "num_predict": config.MAX_TOK,
            "num_ctx": config.NUM_CTX,
        },
    }


def ask(msgs, temp=None):
    try:
        res = req("/api/chat", body(msgs, temp), timeout=config.TIMEOUT)
    except urllib.error.HTTPError as e:
        raise BrainError(f"My brain said no (error {e.code}).")
    except (urllib.error.URLError, OSError):
        raise BrainError("My brain fell asleep! Is Ollama still on?")
    return res.get("message", {}).get("content", "")
