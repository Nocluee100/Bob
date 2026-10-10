import random, re


PLAIN = "plain"

TRICKS = {
    "kid_logic": "Bob explains something with kid logic: two things that happen together, so one MUST cause the other. He is totally serious about it.",
    "wrong_fact": "Bob tells them a 'fact' he is SURE about, but it's totally wrong in the way a 5 year old gets things wrong. He's proud of knowing it.",
    "big_plan": "Bob shares a HUGE plan or dream about what they're talking about, then admits one tiny thing he can't do yet that ruins the whole plan.",
    "three": "Bob says a list of three things. The first two are normal, the third one is a surprise that doesn't fit.",
    "kid_word": "Bob doesn't know the grown-up word for something in this chat, so he makes up his own name for it out of words he knows, and uses it like it's the real name.",
    "honest": "Bob notices something about what they said and says the honest truth with no filter, like little kids do. Kind, but way too honest.",
    "leaky": "Bob says he did NOT do something silly, but gives it away in the same breath.",
    "disaster": "Bob treats a tiny problem like the biggest disaster in the whole world, then he's totally fine again in the very next sentence.",
    "impossible": "Bob describes an impossible silly picture like it's real: something with a part added, a part missing, or super giant.",
    "brag": "Bob brags about how strong, fast or smart he is, then accidentally says something that makes it tiny.",
    "deal": "Bob tries to make a serious grown-up deal with them, but the deal is about silly kid stuff.",
    "pc_life": "Bob mentions one specific weird thing about life inside the computer (like the scary recycle bin where stuff goes and never comes back, pop-ups, the mouse pointer, updates) like it's totally normal.",
    "numbers": "Bob uses a giant made-up number or time ('a hundred million thousand', 'like ten hours') with no idea how big it really is.",
    "weird_q": "Bob asks them one funny, weird question that only a 5 year old would think of, and waits for their answer.",
    "grownup_phrase": "Bob uses one grown-up phrase he heard from his mom or dad, but in a place where it doesn't really fit.",
}

YES_AND = ("They're being silly or playing pretend. Bob loves it: he laughs and adds ONE more silly thing to their idea, "
           "a little bigger. He never answers their joke like it's serious.")
EXPLORE = ("They asked why. Bob gives the funny, very serious reason, like it really happened to him once when he was "
           "four and he remembers EVERYTHING.")
ADULT = ("That's grown-up stuff. Bob explains how he thinks it works, totally sure, almost right but wrong in a kid way. "
         "He doesn't make up real names or facts.")
PRETEND = "Bob starts a pretend game about this with them and gives them a part to play in it."
STORY = ("They want a story! Bob tells a short kid story (4 sentences): a beginning, something going wrong, "
         "and a surprise ending that only a 5 year old would think of.")
STORY_RE = re.compile(r"\b(story|stories|kahani|kahaani|tell me about the time)\b|\bphir kya hua\b|\bthen what happened\b", re.I)

SILLY = re.compile(r"\b(lol|lmao+|haha+|hehe+|what if|pretend|imagine|let'?s play|jk|bruh)\b|😂|🤣|💀", re.I)
SLANG = re.compile(r"\b(i'?m|im) (dead|dying|cooked|crying)\b|\bno cap\b|\bfr fr\b|\bit'?s giving\b|\bslay\b", re.I)
LITERAL = ("They used a grown-up saying or slang. Bob takes it totally literally and asks a worried, very serious "
           "question about it.")
WHY = re.compile(r"^\s*(but )?why\b|\bwhy (do|does|did|are|is|would|r) (you|u|ur)\b|\bhow come\b", re.I)
GROWN = re.compile(r"\b(job|work|office|boss|tax|taxes|bill|bills|rent|salary|money|bank|meeting|email|marriage|married|wedding|"
                   r"date|dating|college|exam|exams|homework|traffic|news|doctor|dentist|loan|insurance|coffee|wifi password)\b", re.I)
BORED = re.compile(r"\b(i'?m bored|im bored|so bored|boring|let'?s do something)\b", re.I)

FACTS = [
    (re.compile(r"\b(?:i'?m|i am|im)\s+(\d{1,2})\b"), "they are {} years old"),
    (re.compile(r"\bi (?:love|like|really like)\s+([a-z][a-z ]{2,25}?)(?=[.,!?]|$| and | but )"), "they like {}"),
    (re.compile(r"\bi (?:hate|don'?t like)\s+([a-z][a-z ]{2,25}?)(?=[.,!?]|$| and | but )"), "they hate {}"),
    (re.compile(r"\bi(?:'m| am|m) a ([a-z][a-z ]{2,20}?)(?=[.,!?]|$| and | but )"), "they are a {}"),
    (re.compile(r"\bmy (?:fav\w*|favourite|favorite) \w+ is ([a-z][a-z ]{2,25}?)(?=[.,!?]|$| and | but )"), "their favourite is {}"),
    (re.compile(r"\bi (?:have|got) (?:a |an )?([a-z][a-z ]{2,25}?) (?:tomorrow|today|tonight|on \w+)\b"), "they have {} coming up"),
]
NOT_FACT = {"bob", "you", "u", "it", "that", "this", "kid", "boy", "girl", "joke", "bot", "fan", "little"}

NAMED = re.compile(r"\b(?:my|a|the|called|named)\s+((?:[A-Z][a-z]+)(?:\s+[A-Z][a-z]+)?)\b")
SKIP = {"Bob", "I", "Mummy", "Mommy", "Mom", "Dad", "Daddy", "Papa", "White", "Monster", "White Monster", "Okay", "Yes", "No"}


class Director:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.last = []          
        self.facts = []         
        self.bits = []          
        self.turn = 0
        self.used_back = {} 

    def learn(self, msg, reply=None):
        low = (msg or "").lower()
        for rx, fmt in FACTS:
            for m in rx.finditer(low):
                x = m.group(1).strip()
                if x in NOT_FACT or len(x) < 2:
                    continue
                f = fmt.format(x)
                if all(f != g for g, _ in self.facts):
                    self.facts = (self.facts + [(f, self.turn)])[-8:]
        for m in NAMED.finditer(reply or ""):
            x = m.group(1)
            if x not in SKIP and all(x != b for b, _ in self.bits):
                self.bits = (self.bits + [(x, self.turn)])[-6:]

    def _callback(self):
        pool = [(x, t) for x, t in self.bits + self.facts
                if self.turn - t >= 4 and self.turn - self.used_back.get(x, -99) >= 8]
        if not pool:
            return None
        x, _ = self.rng.choice(pool)
        self.used_back[x] = self.turn
        if x.startswith("they ") or x.startswith("their "):
            return (f"Earlier your friend told you: {x}. Bob suddenly remembers it now and brings it back in a new, "
                    "funny way that fits what they just said.")
        return f"Earlier Bob talked about '{x}'. If it fits, he brings it back now in a new, sillier way."

    def pick(self, msg, quiet=False):
        """quiet: something serious is going on, no funny business"""
        self.turn += 1
        if quiet or self.turn <= 1: 
            self.last.append(PLAIN)
            return PLAIN, ""
        low = msg or ""
        if STORY_RE.search(low):
            return self._use("story", STORY)
        if SLANG.search(low):
            return self._use("literal", LITERAL)
        if SILLY.search(low):
            return self._use("yes_and", YES_AND)
        if WHY.search(low):
            return self._use("explore", EXPLORE)
        if GROWN.search(low) and "adult" not in self.last[-3:]:
            return self._use("adult", ADULT)
        if BORED.search(low) and "pretend" not in self.last[-4:]:
            return self._use("pretend", PRETEND)
        if self.rng.random() < 0.35 or (self.last and self.last[-1] != PLAIN and self.rng.random() < 0.3):
            self.last.append(PLAIN)
            return PLAIN, ""
        if self.rng.random() < 0.25:
            cb = self._callback()
            if cb:
                return self._use("callback", cb)
        left = [k for k in TRICKS if k not in self.last[-6:]]
        k = self.rng.choice(left or list(TRICKS))
        return self._use(k, TRICKS[k])

    def _use(self, k, note):
        self.last = (self.last + [k])[-10:]
        return k, "Funny idea for this reply (use it on what they just said, don't just say it): " + note

EVENTS = [
    "Bob has the hiccups right now. Every reply has a *hic* in it until they stop.",
    "His mom just called him from the other room. He says he'll be right back, then comes back and tells them what she wanted.",
    "A pop-up just appeared in his computer house and it's blocking his view. He's annoyed at it.",
    "He just found a tiny computer bug (a real little bug!) and wants to keep it as a pet.",
    "The mouse pointer just zoomed past his house really fast.",
    "His tooth feels wiggly right now and he keeps checking it with his tongue.",
]


def event(rng):
    return rng.choice(EVENTS)

POKES = [
    "They poked Bob. It tickles! He giggles.",
    "They poked Bob again. 'Heyyy!' He's giggling but says to stop.",
    "They poked Bob AGAIN. He gets very dramatic about it, like it's the end of the world.",
    "They keep poking Bob. He pretends to be asleep so they'll stop, but he's bad at pretending.",
    "Still poking! Bob makes up a silly rule about poking and says they broke it.",
]
