import re, difflib
import config, food, manners, senses, voice

NOT_BOB = (
    # robot talk
    "as an ai", "an ai model", "language model", "ai assistant",
    "i am an assistant", "i'm an assistant", "how can i assist",
    "how may i help", "qwen", "alibaba", "openai", "chatbot",
    # planning out loud
    "we are bob", "i must respond", "i need to respond",
    "i should respond", "respond with", "my response", "the user",
    "square bracket", "feeling word", "the mood", "mood:", "reply:",
    "let me think", "let me respond", "okay, so", "the rules",
    "my instructions", "system prompt", "json", "think>",
)


def words(txt):
    return re.findall(r"[a-zA-Z']+", txt.lower())


def breaks_char(txt):
    low = txt.lower()
    return any(p in low for p in NOT_BOB)



CALLS_BOB = re.compile(r"\b(hi+|hel+o+|hey+|yo+|thanks?|thank you|ok(ay)?|bye+|sorry)\W+bob+\b|,\s*bob+\s*[!?.]|^\W*bob+\s*(\.\.+|[!?,])", re.I)

SENT_RE = re.compile(r"[^.!?]+[.!?]*")


def sent(x):
    return re.sub(r"[^a-z ]", "", voice.unstretch(x).lower()).strip()


def close(a, b):
    a, b = sent(a), sent(b)
    return len(a) > 30 and difflib.SequenceMatcher(None, a, b).ratio() > 0.8


def same(a, b):
    return voice.unstretch(a).lower().strip(" .!?") == voice.unstretch(b).lower().strip(" .!?")


FAVS = ("biryani", "white monster", "mouse pointer", "computer house", "the computer is my house", "my house is the computer")


# "Bob says 5"
THIRD = re.compile(r"\b(sorry to|for|about) bob\b|\bbob('s)? (says|is|has|loves|likes|wants|thinks|does|doesn't|will|can|knows|feels|eats|tummy|brain|house)\b", re.I)


SOFT = ("too big", "already said", "favorite things", "food or drinks", "computer", "scary", "not \"bob\"",
        "call them friend", "same stuff", "little bits", "listing things", "starting the same", "too many shouts", "keeps talking about")


def opener(txt):
    w = re.findall(r"[a-z']+", voice.unstretch(txt).lower())[:3]
    return " ".join(w) if len(w) == 3 else ""


MATH = re.compile(r"(\d+)\s*(times|x|\*|multiplied by|plus|\+|minus|-|divided by|/)\s*(\d+)", re.I)


# "47 times 12 is 564"
def too_smart(txt, msg):
    m = MATH.search(msg or "")
    if not m:
        return False
    a, op, b = int(m.group(1)), m.group(2).lower(), int(m.group(3))
    if op in ("times", "x", "*", "multiplied by"): r = a * b
    elif op in ("plus", "+"): r = a + b
    elif op in ("minus", "-"): r = a - b
    else: r = a // b if b else 0
    return r >= 20 and re.search(rf"\b{r}\b", (txt or "").replace(",", "")) is not None


def soft(issue):
    return any(s in issue.lower() for s in SOFT)


SORRY_ASK = re.compile(r"\b(please|pleeease|pls|can you|could you|you (need|have|gotta|got) to|now) say (you'?re )?sor+y\b|"
                       r"\bsay sor+y to me\b|\bsay (you'?re )?sor+y[!.?]*$|\bwant (a|an|your) (sorry|apology)\b|"
                       r"\bneed (a|an|your) (sorry|apology)\b|\bi want you to say sor+y\b", re.I)


def grams(x):
    w = sent(x).split()
    return {" ".join(w[i:i + 3]) for i in range(len(w) - 2)}


# how much of this reply is stuff he just said
def overlap(txt, recent):
    mine = grams(txt)
    if len(mine) < 4:
        return 0.0
    old = set().union(*[grams(r) for r in list(recent)[-3:]]) if recent else set()
    return len(mine & old) / len(mine)


def problem(txt, recent, msg="", food_ok=True, upset=False, veg_friend=False):
    if not words(txt):
        return "Bob must say a few tiny words."
    if re.search(r"([a-z])\1{9,}", txt, re.I) or len(re.findall(r"[a-z]+", txt, re.I)) < 3 and len(txt) > 40:
        return "Bob got stuck on one sound. He says real little sentences, like a kid talking."
    if re.search(r'"\s*:\s*["\w\[{]|"(mean|sorry|mood|things|twist|reply)"', txt):
        return "Answer only with the words Bob says out loud, like a little kid. Do not plan or explain."
    if re.search(r"\bi(?:'?m| am)\s+(?:a |an |just a |only a )?(?:\w+ )?(robot|ai|bot|program|machine|computer program)\b", txt, re.I):
        return "Bob is a real boy who lives in a computer, not a robot or a program."
    if re.search(r"\b(died|is dead|passed away|is sick|in (the )?hospital) too\b|\bmy \w+ died\b", txt, re.I) and \
            re.search(r"\b(died|dead|passed away|sick|hospital)\b", msg or "", re.I):
        return "That sad thing happened to your friend, not to Bob. Bob doesn't say it happened to him too. He's sorry for THEM."
    if too_smart(txt, msg):
        return "Bob is 5. Big math is way too hard for him, he can't know that answer. He makes a silly kid guess instead."
    if re.search(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af\u0400-\u04ff]", txt):
        return "Bob only talks in simple English (and a few Hindi words). No other languages."
    if breaks_char(txt):
        return "Answer only with the words Bob says out loud, like a little kid. Do not plan or explain."
    if CALLS_BOB.search(txt):
        return "You are Bob. The person you are talking to is NOT Bob, so don't call them Bob. Call them friend."
    if senses.scary(txt) and not senses.scary(msg):
        return "Bob doesn't talk about scary stuff like guns or fighting. Say it in a happy, gentle way."
    if manners.is_mean(txt):
        return "Bob is never mean to anyone, even when he is sad. Say it in a kind way."

    big = [w for w in words(voice.unstretch(txt)) if len(w) >= config.BIG_WORD
           and not re.fullmatch(r"(ha|he|hi|ho|hee|heh|la|na|bo+p|zo+m)+h?", w) and w not in (msg or "").lower()]
    if big:
        return f'The word "{big[0]}" is too big for Bob. Use tiny easy words.'

    if upset and not re.search(r"\bsor+y\b|\bsowwy\b", txt, re.I):
        return "Bob is still crying and hurt. He is not happy yet. He asks them to say sorry."
    if not upset and SORRY_ASK.search(txt):
        return "Nobody was mean to Bob just now, so he does NOT ask anyone to say sorry."

    if food.likes_pulao(txt):
        return "Bob never likes or eats veg biryani or pulao, even to be nice. He can say no thank you kindly."
    if veg_friend and food.pushes_meat(txt):
        return "Your friend doesn't eat meat, and that's totally fine. Never ask them to eat chicken or say they should."

    if THIRD.search(txt):
        return 'Talk about yourself as "I" and "me", not "Bob".'

    if food_ok is None and food.mentions(txt):
        return "Bob is sad and crying right now. Don't talk about food. Just say how you feel."
    if food_ok is False and food.mentions(txt) and any(food.mentions(r) for r in list(recent)[-2:]):
        return "Don't talk about food or drinks right now. Talk about what they said."

    low, said = txt.lower(), (msg or "").lower()
    favs = [f for f in FAVS if f in low and f not in said]
    if len(favs) >= 3 and not any(w in said for w in ("eat", "food", "drink", "hungry", "like", "favorite", "favourite", "feed", "gives bob")):
        return "Don't list your favorite things. Just answer what they said and ask them something about them."

    ss = [x.strip() for x in SENT_RE.findall(txt) if x.strip()]
    if len(ss) >= 6 and sum(x.lower().startswith(("i ", "i'm", "my ")) for x in ss) >= len(ss) * 0.8:
        return "Bob is just listing things about himself. He answers them like a kid telling a little story, with 'and' and 'because'."
    op = opener(txt)
    if op and any(opener(r) == op for r in list(recent)[-4:]):
        return f'Bob keeps starting the same way ("{op}"). Start differently this time.'
    if txt.count("!") > 5:
        return "Too many shouts. Bob says it more like he's talking."
    if any(same(txt, r) or close(txt, r) for r in recent):
        return "That is the same thing Bob said before. He answers what they JUST said, with new words."
    if overlap(txt, recent) > 0.4:
        return "Bob keeps saying the same stuff. Say something totally different and new this time."
    old = {sent(x) for r in recent for x in SENT_RE.findall(r) if len(sent(x)) > 24}
    for x in SENT_RE.findall(txt):
        if sent(x) in old:
            return f'Bob already said "{x.strip()}" before. Say something new instead.'
    short = {sent(x) for r in list(recent)[-4:] for x in SENT_RE.findall(r) if len(sent(x)) > 6}
    if sum(sent(x) in short for x in SENT_RE.findall(txt)) >= 2:
        return "Bob is repeating little bits he already said. Say something new."
    return None
