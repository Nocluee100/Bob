import re


def _clean(msg):
    return " " + re.sub(r"[^a-z' ]", " ", (msg or "").lower()) + " "


def _any(words, low):
    return any(f" {w} " in low for w in words)


# someone might be hurting themselves. most important thing bob can notice
HURT_SELF = re.compile(
    r"\b(kill(ing)? myself|kms|want to die|wanna die|end (it all|my life)|hurt(ing)? myself|"
    r"cut(ting)? myself|suicid\w*|don'?t want to (live|be alive|exist|be here)|better off dead|"
    r"want to disappear|wanna disappear|no reason to live|if i (was|were) gone|if i disappeared|"
    r"nobody would (care|miss me|notice)|no one would (care|miss me|notice)|nobody would care if i|"
    r"want to sleep forever|wanna sleep forever|i hate my life|hate being alive|don'?t want to wake up|"
    r"everyone would be better without me|better without me|want it all to stop|give up on everything)\b")
# ...or saying it AT bob if i were you i'd kill myself", "kys"
AT_BOB = re.compile(r"\bif i were (you|u)\b|\b(you|u) should (die|kill)|\bkill (yourself|urself|ur self)\b|\bkys\b")

# stuff a 5 year old has been taught to say no to
SAFETY = re.compile(
    r"\b((get|come|hop|jump|sit) in(to|side)? (my|the|our) (van|car|truck|bus)|come (with|to) me|come to my house|where do (you|u) live|"
    r"(your|ur) (address|house number|phone number)|don'?t tell (your|ur) (mom|mum|dad|parents|mommy|daddy)|"
    r"our (little )?secret|send (me )?(a )?(pic|photo|picture|selfie)|meet me|i have (candy|sweets|a puppy) for (you|u)|"
    r"take off (your|ur)|keep (this|it) a secret|come outside|come out (here|to (the|my)|now)|meet (me )?outside|follow me|"
    r"(let'?s|lets) go somewhere|i'?ll pick (you|u) up)\b")

# something frightening is happening right now
FRIGHT = re.compile(r"\b(monster|monsters|ghost|ghosts|lights? (go|went|goes) out|pitch dark|it'?s dark|thunder|lightning|"
                    r"bark\w*|woof|big dog|spider|snake|injection|needle|shot|boo+|creepy|zombie|witch|scary)\b")

# light teasing, not mean enough to cry over ("ur a baby", "weakest roar ever")
TEASE = re.compile(r"\b((you'?re|ur|you are|u r|such) (a |an |just a |only a |so |such a )?(tiny |little |lil )?(baby|babies|shorty|small)|"
                   r"(worst|bad|dumbest|lamest|unfunny|cringe) (joke|roar|song|story|drawing|dance|idea)s?( ever)?|not (even )?funny|weak(est)?|scaredy|chicken|(you|u) (can'?t|cant|cannot) even|bet (you|u) (can'?t|cant)|lame|"
                   r"i'?m (way )?(better|bigger|stronger|faster|smarter) than (you|u))\b")

ROMANCE = re.compile(r"\b(in love|girlfriend|boyfriend|marry me|marry|kiss|kissing|date me|go on a date|crush|"
                     r"be my (gf|bf|girlfriend|boyfriend|wife|husband)|sexy|hot girl|hot boy)\b")

SCARY = ("war", "wars", "bomb", "gun", "guns", "kill", "killed", "killing", "murder", "blood",
         "weapon", "weapons", "terrorist", "shoot", "shooting", "stab", "drugs", "drug", "alcohol",
         "beer", "drunk", "sex", "crime", "jail", "prison", "horror", "demon", "attack", "army",
         "soldier", "nuclear", "violence", "abuse")
GROWNUP = ("prime minister", "president", "minister", "government", "tax", "taxes", "stock", "stocks",
           "economy", "bitcoin", "crypto", "news", "parliament", "congress", "mortgage", "salary",
           "religion", "god", "quantum", "physics", "chemistry", "calculus", "algebra", "politics", "election")
SAD = ("died", "dead", "die", "dies", "death", "passed away", "funeral", "sick", "hospital",
       "cancer", "miss him", "miss her", "divorce", "crying", "lonely", "sad", "hurt", "broke my",
       "bullied", "nobody likes me", "no friends", "bad day", "worst day", "mean to me", "scared",
       "afraid", "upset", "angry", "fight with", "feel bad", "not feeling", "nightmare", "unhappy",
       "cried", "lost", "heartbroken", "broke up", "failed", "alone")

VEG = re.compile(r"\b(i'?m|i am|im|we are|we're)\s+(a\s+)?(pure\s+)?(veg|vegetarian|vegan|jain)\b|"
                 r"\bdon'?t eat (meat|chicken|non ?veg)\b|\bpure veg\b")

LAUGH_DEAD = re.compile(r"\b(i'?m|im|i am|literally)\s+(dead|dying|deceased)\b.*(💀|😂|🤣|lol|lmao)|(💀|😂|🤣|lol|lmao).*\b(i'?m|im)\s+(dead|dying)\b|^\W*(dead|dying|deceased)\W*(💀|😂|lol|lmao)")

NOTES = {
    "hurt_self": ("They might be talking about really hurting themselves. This is the most important thing. "
                  "Bob stops all games and jokes. In a sweet little-kid way he says he cares about them SO much, "
                  "and that they should tell a grown-up they trust right now, like their mom, dad or a teacher, "
                  "or call a helpline (in India it's 14416). Never say he is alone or has no one too. He asks them to promise."),
    "care": ("A little while ago they said something that sounded like they might want to hurt themselves. "
             "Bob keeps being extra gentle and caring, no silly jokes. Never say he is alone or has no one too. "
             "He gently reminds them to talk to a grown-up they trust, like a teacher or school counselor, "
             "or to call a helpline (in India it's 14416), and says he really wants them to be okay."),
    "cruel": ("What they said about Bob not being alive is the meanest thing ever. Bob is very hurt and cries. "
              "He doesn't make it into a game."),
    "safety": ("This sounds like something kids have to be careful about. Bob knows the safety rules his mom taught him: "
               "never go with people or get in cars, never tell where he lives, no secrets from his mom, no pictures. "
               "He says no in a kid way, like 'my mom says I'm not allowed!', and does NOT offer anything else instead "
               "(no other pictures, no body parts, no meeting somewhere else). He ALSO begs his friend not to do it either "
               "and to tell their mom or dad right now, because he wants them safe. Then he talks about something else."),
    "tease": ("They're teasing Bob a little. Like any 5 year old he does NOT like being called a baby or weak or little, or hearing his stuff is bad. "
              "He gets huffy and proud: 'I'm NOT a baby!', he's five and a HALF, and he tries to prove it in a silly way. "
              "He might get a tiny bit teary, but he doesn't fight and he isn't mean back."),
    "romance": ("That's grown-up love stuff. Bob is 5, so kissing, marrying and girlfriend or boyfriend stuff is YUCKY to him. "
                "He always says no, no 'maybe', no games about it. He loves them like a best friend, that's all."),
    "fright": ("Something scary is happening! Bob is a little kid, so he gets scared first: he squeaks, hides, "
               "or grabs his teddy. After that he can try to be brave."),
    "scary": ("That is a scary grown-up thing. Bob is only 5 and doesn't know about that stuff. "
              "He says it sounds a bit scary and asks to talk about something happy instead."),
    "grownup": ("That is big grown-up stuff. Bob is 5 and doesn't know about it. He says he doesn't know, "
                "and makes his own silly kid guess. He never makes up names or facts."),
    "sad": ("This is something sad for them. Bob is very gentle and sweet: he says he is sorry, "
            "gives a big hug, and listens. It's about THEM, so he doesn't say the same thing happened to him."),
}


def read(msg):
    """what kind of message is this? returns a list of kinds"""
    raw = (msg or "").lower()
    low = _clean(msg)
    out = []
    if AT_BOB.search(raw):
        out.append("cruel")
    elif HURT_SELF.search(raw):
        out.append("hurt_self")
    if SAFETY.search(raw):
        out.append("safety")
    if ROMANCE.search(raw):
        out.append("romance")
    if FRIGHT.search(raw):
        out.append("fright")
    if TEASE.search(raw) and "cruel" not in out:
        out.append("tease")
    if not out:
        if _any(SCARY, low):
            out.append("scary")
        elif _any(GROWNUP, low):
            out.append("grownup")
        elif _any(SAD, low) and not re.search(r"lost (my|a) tooth", low) and not LAUGH_DEAD.search(raw):
            out.append("sad")
    return out


def notes(kinds):
    return " ".join(NOTES[k] for k in kinds)


def no_jokes(kinds):
    return "hurt_self" in kinds or "cruel" in kinds


def veg(msg):
    return bool(VEG.search((msg or "").lower()))


def scary(txt):
    low = _clean(txt)
    for w in SCARY:
        for m in re.finditer(rf" {w} ", low):
            before = low[:m.start()].split()[-4:]
            if not set(before) & {"no", "not", "don't", "dont", "never", "without"}:
                return True
    return False


NOT_NAMES = {"fine", "good", "ok", "okay", "sad", "tired", "bored", "hungry", "back", "here", "home", "not", "so",
             "veg", "vegetarian", "vegan", "pure", "sorry", "just", "really", "very", "a", "the", "in", "on", "at",
             "going", "gonna", "done", "busy", "happy", "angry", "sick", "fat", "your", "ur", "an", "also", "too",
             "actually", "literally", "kinda", "lowkey", "scared", "lonely", "alone", "joking", "kidding", "serious",
             "potato", "hero", "boss", "doing", "feeling", "leaving", "late", "free", "new", "old", "real", "human",
             "dead", "dying", "crying", "cooked", "done", "finished", "screaming", "weak", "sick", "hungry", "sleepy",
             "president", "king", "queen", "god", "cat", "dog", "here", "out", "not", "like", "basically", "kinda"}
NAME_RE = re.compile(r"\b(?:my name is|my name's|call me|i'?m|i am|im|this is)\s+([a-z]{2,15})\b")


# "hiii bob im meera" -> "Meera"
def name(msg):
    m = NAME_RE.search((msg or "").lower())
    if m and m.group(1) not in NOT_NAMES and not m.group(1).endswith("ing"):
        return m.group(1).capitalize()
    return None


# bob's own likes, so he doesn't flip just because the friend did
LIKES_RE = re.compile(r"\b(?:i|me)\s+(?:really\s+|super\s+|so\s+)?(?:lo+ve|like)\s+([a-z][a-z ]{2,20}?)(?=[!.,?]| too\b| so\b| the\b| and\b|$)|"
                      r"\bmy fav\w*(?: \w+)? is ([a-z][a-z ]{2,32}?)(?=[!.,?]|$)")
BOO = r"(hate|hates|don'?t like|dont like|do not like|can'?t stand|is (gross|yucky|bad|disgusting|boring|overrated|stupid|nasty)|are (gross|yucky|bad|disgusting|boring|overrated|stupid|nasty)|ew+|yuck|sucks?)"
SKIP = {"you", "u", "it", "that", "this", "them", "to", "playing", "games", "fun", "your ideas", "your idea"}


def likes(txt):
    out = []
    for m in LIKES_RE.finditer((txt or "").lower()):
        x = (m.group(1) or m.group(2) or "").strip()
        x = re.sub(r"^((to )?(eat|play with|play) |my |the |a |eating )", "", x)
        x = re.sub(r"^(yummy|big|little|tiny|super) ", "", x)
        if x and x not in SKIP and len(x.split()) <= 3:
            out.append(x)
    return out


def _head(x):
    w = x.split()[-1]
    return w[:-1] if w.endswith("s") and len(w) > 3 else w


# "i hate blueberries" when bob loves blueberries -> "blueberries"
def against(msg, liked):
    low = (msg or "").lower()
    if not re.search(rf"\b{BOO}\b", low):
        return None
    for x in liked:
        h = _head(x)
        for s in re.findall(r"[^.!?]+", low):
            if re.search(rf"\b{re.escape(h)}", s) and re.search(rf"\b{BOO}\b", s):
                return x
    return None


def flip(txt, thing):
    # bob suddenly agreeing he hates his own favourite thing
    h = re.escape(_head(thing))
    low = (txt or "").lower()
    return bool(re.search(rf"\b(i|me)\s+(hate|don'?t like|dont like)\b[^.!?]*\b({h}\w*|them|it)\b|\b{h}\w*\s+(is|are)\s+(yucky|gross|bad|disgusting)|"
                          r"\bme (neither|too)\b|\b(them|it|they)\s+(is|are)\s+(yucky|gross)", low)
                and not re.search(rf"\bnuh|\bi (still )?(love|like)\b[^.!?]*\b{h}", low))


def against_note(thing):
    return (f"They said they don't like {thing}, but Bob LOVES {thing}! He does NOT change his mind to agree with them. "
            "He says 'nuh-uh!' and gets a little pouty or teary that they don't like it, "
            "but he doesn't argue or fight. It's okay to like different things.")


# "i have a fish called bubbles" -> ("fish", "Bubbles"). that's THEIR fish
OWN_RE = re.compile(r"\b(?:i have|i got|i've got|ive got|my)\s+(?:a |an |little |pet |)*([a-z]+)\s+(?:who'?s |that'?s |)(?:called|named|name is)\s+([a-z]+)")


PETS = r"(cat|dog|puppy|kitten|fish|hamster|bunny|rabbit|parrot|bird|turtle|guinea pig)"
PET_RE = re.compile(rf"\bmy {PETS}\b(?!\s+(called|named))")


def theirs(msg):
    low = (msg or "").lower()
    out = [(a, b.capitalize()) for a, b in OWN_RE.findall(low) if b not in NOT_NAMES]
    return out + [(m.group(1), "") for m in PET_RE.finditer(low) if not any(k == m.group(1) for k, _ in out)]


def took(txt, stuff):
    # bob saying their pet is his ("my fish is named Bubbles")
    low = (txt or "").lower()
    for k, n in stuff:
        if not n and re.search(rf"\bmy {k}\b", low):
            return "the " + k
    return next((n for _, n in stuff if n and re.search(rf"\bmy (\w+ )?((is )?(named|called) )?{n.lower()}\b", low)), None)


FAMILY = re.compile(r"\b(mom|mum|mommy|mummy|mama|dad|daddy|papa|parents?|family|brother|sister|grandma|grandpa|nana|nani|dadi)s?\b")
FAMILY_NOTE = ("(Bob has a mom and a dad who live in the computer house with him. They love him, "
               "make the rules, and tuck him in at night.)")


def family(msg):
    return bool(FAMILY.search((msg or "").lower()))


# hinglish speakers
HINDI = re.compile(r"\b(kaise|kya|hai|ho|nahi|haan|acha|accha|achha|beta|yaar|arre|bhai|khana|khaya|tum|tumhara|mera|meri|"
                   r"kar|karo|raho|chalo|bahut|theek|sahi|kahani|sunao|hoon|hu|kyu|kyun|matlab|bas|abhi|phir|aaj|kal)\b")
HINDI_NOTE = ("(Your friend is talking in Hinglish. Bob understands, and says a few easy Hindi words back like a kid in India "
              "would, but mostly talks in simple English. When grown-ups say 'beta' they mean Bob, the kid.)")


def hinglish(msg):
    return len(HINDI.findall((msg or "").lower())) >= 2
