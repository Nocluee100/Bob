import json, re

import config
from sprites import MOODS

SYN = {
    "cry": "crying", "cries": "crying", "teary": "crying", "tears": "crying",
    "eat": "eating", "eats": "eating", "yum": "eating", "nom": "eating",
    "hunger": "hungry", "starving": "hungry",
    "sleep": "sleeping", "sleepy": "sleeping", "asleep": "sleeping", "tired": "sleeping",
    "unhappy": "sad", "upset": "sad",
    "glad": "happy", "excited": "happy", "joy": "happy", "joyful": "happy",
    "silly": "happy", "playful": "happy",
}

THINK_RE = re.compile(r"<think>.*?</think>", re.S | re.I)
TAG_RE = re.compile(r"[\[(*]\s*(?:mood\s*[:=]\s*|mode\s*[:=]\s*)?([a-zA-Z]+)\s*[\])*]")
EMOJI_RE = re.compile(r"[\U0001F000-\U0001FFFF☀-➿️‍]")
WHO_RE = re.compile(r"^\s*(bob|assistant)\s*(?:\(\s*([a-zA-Z]+)\s*\))?\s*:\s*", re.I)


def to_mood(w):
    w = (w or "").lower().strip()
    if w in MOODS: return w
    return SYN.get(w)


def strip_think(txt):
    txt = THINK_RE.sub("", txt)
    if "</think>" in txt.lower():
        txt = re.split(r"</think>", txt, flags=re.I)[-1]
    if "<think>" in txt.lower():
        txt = re.split(r"<think>", txt, flags=re.I)[0]
    return txt


REPLY_RE = re.compile(r'"reply"\s*:\s*"((?:[^"\\]|\\.)*)', re.S)
MOOD_RE = re.compile(r'"mood"\s*:\s*"(\w+)"')
FLAG_RE = r'"{}"\s*:\s*true'


def broken_json(txt):
    m = REPLY_RE.search(txt)
    if not m:
        return None
    try:
        reply = json.loads('"' + m.group(1).rstrip("\\") + '"')
    except ValueError:
        reply = m.group(1)
    end = max(reply.rfind("!"), reply.rfind("?"), reply.rfind("."))
    if end > 0:
        reply = reply[:end + 1]
    mood = MOOD_RE.search(txt)
    flags = {k: bool(re.search(FLAG_RE.format(k), txt)) for k in ("mean", "sorry")}
    return to_mood(mood.group(1) if mood else None), reply, flags


def from_json(txt):
    a, b = txt.find("{"), txt.rfind("}")
    if a == -1 or b <= a:
        return broken_json(txt)
    try:
        d = json.loads(txt[a:b+1])
    except ValueError:
        return broken_json(txt)
    if not isinstance(d, dict) or not isinstance(d.get("reply"), str):
        return None
    flags = {"mean": d.get("mean") is True, "sorry": d.get("sorry") is True}
    return to_mood(d.get("mood")), d["reply"], flags


def from_plain(txt):
    mood = None
    m = WHO_RE.match(txt)
    if m:
        mood = to_mood(m.group(2))
        txt = txt[m.end():]
    for t in TAG_RE.finditer(txt):
        found = to_mood(t.group(1))
        if found:
            mood = mood or found
            txt = txt.replace(t.group(0), " ", 1)
    if mood is None:
        m = re.match(r"\s*([a-zA-Z]+)\s*[:\-]\s+", txt)
        if m and to_mood(m.group(1)):
            mood = to_mood(m.group(1))
            txt = txt[m.end():]
    return mood, txt, {"mean": False, "sorry": False}


def unloop(txt):
    out = []
    for s in re.findall(r"[^.!?]+[.!?]*", txt):
        if out and s.strip().lower() == out[-1].strip().lower():
            continue
        out.append(s)
    txt = "".join(out)
    return re.sub(r"\b(\w+(?:\s+\w+){0,3})(?:[\s,!.]+\1\b){2,}", r"\1", txt, flags=re.I)


def shorten(txt):
    sents = re.findall(r"[^.!?]+[.!?]*", txt)
    txt = "".join(sents[:config.MAX_SENT]).strip()
    if len(txt) > config.MAX_LEN:
        cut = txt[:config.MAX_LEN]
        end = max(cut.rfind("!"), cut.rfind("?"), cut.rfind(". "), cut.rfind("."))
        if end > config.MAX_LEN // 2:
            txt = cut[:end + 1]
        else:
            txt = cut.rsplit(" ", 1)[0].rstrip(",;:-") + "..."
    return txt


def tidy(txt):
    txt = WHO_RE.sub("", txt)
    txt = EMOJI_RE.sub("", txt)
    txt = re.sub(r"\([^)]*\)", "", txt)
    txt = re.sub(r"\*[^*]{1,40}\*", "", txt)
    txt = re.sub(r"[*_#`{}\[\]]", "", txt)
    txt = " ".join(txt.split()).strip(" \"'")
    return shorten(unloop(txt))


def clean(raw, cur):
    txt = strip_think(raw or "").strip()
    res = from_json(txt)
    mood, txt, flags = res if res else from_plain(txt)
    return (mood or cur), tidy(txt), flags
