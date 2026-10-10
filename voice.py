import re, zlib, random, difflib

import config

# word -> how bob stretches it
STRETCH = {
    "hello": "hellooooo", "hi": "hiiiii", "hey": "heyyyy", "yes": "yesss", "yeah": "yeahhh",
    "yay": "yaaaaay", "no": "nooooo", "so": "sooooo", "please": "pleeeease",
    "obviously": "obviouslllyyyyyy", "yummy": "yummmmy", "wow": "wooooow", "okay": "okayyyy",
    "really": "reallyyyy", "mine": "miiine", "cool": "coooool", "best": "bestest",
    "love": "loooove", "fun": "fuuun", "big": "biiiig", "hungry": "hunnngry",
    "whoa": "whoaaaa", "awesome": "awesommme", "please?": "pleeeease?", "super": "suuuper",
}

LONG_RE = re.compile(r"([a-zA-Z])\1{2,}")


def stretched(txt):
    return bool(LONG_RE.search(txt))


def unstretch(txt):
    return LONG_RE.sub(r"\1", txt)


def _fix_case(old, new):
    if old.isupper() and len(old) > 1: return new.upper()
    if old[0].isupper(): return new[0].upper() + new[1:]
    return new


def kidify(txt):
    if not txt or stretched(txt):
        return txt
    rng = random.Random(zlib.crc32(txt.encode()))
    if rng.random() > config.STRETCH_CHANCE:
        return txt
    words = list(re.finditer(r"[A-Za-z]+\??", txt))
    hits = [m for m in words if m.group(0).lower() in STRETCH]
    if not hits:
        return txt
    m = rng.choice(hits)
    new = _fix_case(m.group(0), STRETCH[m.group(0).lower()])
    return txt[:m.start()] + new + txt[m.end():]


# little phrases bob falls back on. fine once in a while, annoying every line
TICS = [
    r"\by+a+y+\b|\bya+h+\b", r"\bi lo+ve (you|u)\b", r"\blet'?s play\b", r"\bi lo+ve (your|ur) ideas?\b",
    r"\bdo you want to (play|be|make|build)\b", r"\bcomputer house\b", r"\bpinky promise\b",
    r"\bthe bestest\b", r"\bhappiest\b", r"\bmy tummy\b", r"\bguess what\b", r"\byou know what\b",
    r"\bso+ (fun|cool)\b", r"\bbig hug\b", r"\bbest friend\b", r"\bi'?m (so )?happy\b",
    r"\bfive and a half\b", r"\bthe best\b", r"\bnuh-?uh\b", r"\bfunnest\b", r"\bthe computer\b",
    r"\bhehe+\b", r"\bi'?m so happy\b", r"\bmy friend\b", r"\bso+ fun\b", r"\bgiggl\w*\b",
    r"\bno fair\b", r"\byucky\b", r"\bburps?\b", r"\bboogers?\b", r"\btoots?\b", r"\bbig hug\b", r"\bmoon\b", r"\brobot\b",
]
TIC_RE = [re.compile(t, re.I) for t in TICS]
TIC_RE.append(re.compile(r"\b[Ii] lo+ve [A-Z][a-z]+\b"))   # "I love Kabir!" every line
# "my hamster says 'roar!'" is cute once, then it's a habit
ONCE = re.compile(r"\b\w+ (the \w+ )?says\b", re.I)
SENT = re.compile(r"[^.!?]+[.!?]*")

BIG = ["a gazillion", "a bajillion", "a hundred zillion", "so so many", "a kajillion", "more than all the stars"]


def _plain(s):
    return re.sub(r"[^a-z ]", "", unstretch(s).lower()).strip()


# a sentence he already said word for word (or nearly) gets dropped
def dedupe(txt, recent):
    old = [_plain(p) for r in list(recent)[-config.RECENT_N:] for p in SENT.findall(r)]
    old = [o for o in old if len(o) > 12]
    parts = SENT.findall(txt)
    # asking for a sorry is allowed again and again, that's the point
    keep = [p for p in parts if re.search(r"sor+y", p, re.I) or not any(_plain(p) == o or (len(o) > 25 and difflib.SequenceMatcher(None, _plain(p), o).ratio() > 0.75) for o in old)]
    if keep and len(keep) < len(parts) and len(" ".join(keep).split()) >= 4:
        return _quotes("".join(keep).strip())
    return txt


# don't cut a sentence if what's left leans on it ("...' but I drink it anyway")
def _flows(parts, keep):
    for i, p in enumerate(parts):
        if p in keep and i and parts[i - 1] not in keep:
            t = p.strip()
            if not t or t[0] in "'\"" or t[0].islower() or re.match(r"(but|and|so|because|then)\b", t, re.I):
                return False
    return True


# cutting a sentence can leave half a quote behind
def _quotes(txt):
    out, open_ = [], False
    for k, ch in enumerate(txt):
        if ch == "'" and not (0 < k < len(txt) - 1 and txt[k-1].isalpha() and txt[k+1].isalpha()):
            before = txt[k-1] if k else " "
            if before.isspace() or before in "(\"":
                open_ = True
            elif open_:
                open_ = False
            elif before in ".!?,":
                continue    # closing quote with nothing opened, left over from a cut
        out.append(ch)
    txt = "".join(out)
    if open_:
        txt = re.sub(r"(^|\s)'(?=\w)(?!.*')", r"\1", txt, count=1)
    return txt


def detic(txt, recent):
    txt = dedupe(txt, recent)
    last = list(recent)[-3:]
    tired = [t for t in TIC_RE if t.search(txt) and sum(bool(t.search(r)) for r in last) >= 2]
    if ONCE.search(txt) and any(ONCE.search(r) for r in last):
        tired.append(ONCE)
    if tired:
        parts = SENT.findall(txt)
        keep = [p for p in parts if re.search(r"sor+y", p, re.I) or not any(t.search(p) for t in tired)]
        if keep and len(" ".join(keep).split()) >= 6 and _flows(parts, keep):
            txt = _quotes("".join(keep).strip())
    # "a million" every other line gets boring
    if "a million" in txt.lower() and any("million" in r.lower() for r in last[-2:]):
        rng = random.Random(zlib.crc32(txt.encode()))
        txt = re.sub(r"\ba million\b", lambda m: rng.choice(BIG), txt, count=1, flags=re.I)
    return _quotes(txt)


COMMON = set("""about after again always because before being could doesn't don't every going gonna great happy
having little maybe never other really should something their there these thing things think those today tomorrow
wanna where which while would yours friend friends people super funny bigger biggest please thank thanks inside
crying sorry hungry tummy kabir want like have love that this with what your just yeah okay make good
know they them then said says when very much more some here come does cool also will been were from into over
only even ever back time real wanna play nooo yesss heyy hiii feel help need look lots best same tell told
hehe haha yummy yucky didn't can't isn't it's i'm you're that's what's let's""".split())


# a word that keeps popping up in his last few lines ("blueberry" x4)
def stuck_on(recent, said=""):
    seen = {}
    for r in list(recent)[-4:]:
        for w in sorted(set(re.findall(r"[a-z]{4,}", unstretch(r).lower()))):
            w = w[:-3] + "y" if w.endswith("ies") else w[:-1] if w.endswith("s") and not w.endswith("ss") else w
            seen[w] = seen.get(w, 0) + 1
    said = (said or "").lower()
    return sorted(w for w, n in seen.items() if n >= 3 and w not in COMMON and w[:-1] not in said)


# "Kabir! ..." at the start of every single line
def no_name_start(txt, recent, name):
    if not name:
        return txt
    pat = re.compile(rf"^\W*{re.escape(name)}\s*(!+|\.\.+|,)\s*", re.I)
    if pat.search(txt) and sum(bool(pat.search(r)) for r in list(recent)[-3:]) >= 2:
        rest = pat.sub("", txt, count=1)
        if len(rest.split()) >= 3:
            return rest[0].upper() + rest[1:]
    return txt


STOP = set("""i a an the to and is it my you your me so of in on that this it's i'm was be are with for what do
but at we he she they not can just like have has oh ooh wow yes no""".split())


# two-word bits that keep coming back ("snack monster", "my tummy")
def overused(recent):
    seen = {}
    for r in list(recent)[-5:]:
        w = re.findall(r"[a-z']+", unstretch(r).lower())
        for g in sorted(set(zip(w, w[1:]))):
            if not set(g) <= STOP:
                seen[g] = seen.get(g, 0) + 1
    return [" ".join(g) for g, n in sorted(seen.items()) if n >= 3]


# "...and guess what?" with nothing after it
def no_hanging(txt):
    out = re.sub(r"\s*(and\s+)?(guess what|you know what)\W*$", "", txt, flags=re.I).strip()
    return out if len(out.split()) >= 3 else txt


# "hellooo beta!" - he's the kid, grown-ups call HIM beta
def no_beta(txt):
    txt = re.sub(r"\b((?:hi+|hel+o+|hey+|bye+|ok(?:ay)?)\W*?)[ ,]+beta\b", r"\1", txt, flags=re.I)
    return re.sub(r",\s*beta(?=\s*[!?.])", "", txt, flags=re.I)


# they: "i ate a whole cloud"  bob: "I ate a whole cloud too!"
def mirrors(txt, msg):
    m = re.search(r"\bi(?:'m| am|m)?\s+(?:a |now )?(ate|am|turned into|drank|have|got|became|built|made|did|found|saw|grow|grew|lost|broke|fell|won|went|wrote|work|worked|used to)\s+(?:a |an |the )?(\w+(?: \w+)?)", (msg or "").lower())
    if not m:
        return False
    verb, thing = m.group(1), m.group(2)
    low = (txt or "").lower()
    v = verb if verb not in ("built", "made") else "built|made"
    return bool(re.search(rf"\bi(?:'m| am)?\s+(?:{v}|a|an)\s+(?:a |an |the |it |one )?(?:\w+ )?{re.escape(thing.split()[0])}", low)) and \
        "you" not in low.split(thing.split()[0])[0][-30:]
