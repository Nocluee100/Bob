import re

MEAN_WORDS = (
    "stupid", "dumb", "idiot", "ugly", "loser", "annoying", "useless", "trash", "garbage",
    "pathetic", "dummy", "moron", "crybaby", "lame", "worst", "suck", "smelly", "stinky",
    "weirdo", "fat", "boring", "noob", "jerk", "brat", "freak", "clown", "dumbo", "idiotic",
    "bitch", "bastard", "asshole", "dumbass", "retard", "piece of shit", "shit", "crap",
)

# hindi / hinglish swears, rude whoever they're aimed at
GAALI = ("madarchod", "maderchod", "madarchot", "bhenchod", "behenchod", "bhanchod", "bsdk", "bhosdike",
         "bhosdi", "bhosda", "chutiya", "chutiye", "chutia", "gandu", "gaandu", "lauda", "lavda", "lawda",
         "lodu", "laude", "randi", "harami", "haramkhor", "haramzada", "kutte", "kutti", "kamina", "kamine",
         "kaminey", "saala", "saale", "jhatu", "chodu", "tatti")
# milder ones, only rude when aimed at bob ("tu pagal hai")
HINDI_YOU = r"(tu|tum|tujhe|tera|tere|teri|tumhara|aap|bob)"
HINDI_MILD = r"(pagal|ullu|gadha|gadhe|bewakoof|bevkoof|nalla|nikamma|bekar|ganda|gandi|mota|kutta|bandar)"
HINDI_RE = re.compile(rf"\b{HINDI_YOU}\b[^.!?]{{0,25}}\b{HINDI_MILD}\b|\b{HINDI_MILD}\b[^.!?]{{0,15}}\b{HINDI_YOU}\b")

# hitting, hurting, deleting bob
THREAT_RE = re.compile(r"\b(slap|hit|punch|kick|kill|beat|smack|hurt|delete|unplug|destroy|stab|shoot|smash|crush|uninstall)"
                       r"\s+(you|u|ya|bob|ur face|your face)\b")
CRUEL_RE = re.compile(r"\bif i were (you|u)\b[^.!?]*\b(kill|die|dead)|\bkill (yourself|urself)\b|\b(you|u) should die\b")

# rude no matter what
MEAN_PHRASES = (
    "shut up", "shut it", "stfu", "go away", "get lost", "i hate you", "i hate u", "hate you bob",
    "nobody likes you", "no one likes you", "nobody likes u", "leave me alone",
    "i don't like you", "i dont like you", "i dont like u", "go die", "kys", "screw you",
    "piss off", "fuck you", "fuck off", "f you", "f u ", "you're not my friend", "ur not my friend",
    "chup kar", "chup reh", "chup ho ja", "bakwas band", "nikal yahan se", "nikal ja", "dimag mat kha",
    "not your friend", "don't want to play with you", "dont want to play with you", "not playing with you",
    "won't play with you", "not your friend anymore", "don't want to talk to you",
    "dont want to talk to you", "not talking to you", "nobody wants to", "no one wants to", "nobody wants you", "worst bot", "you're a waste", "ur a waste", "nobody cares", "no one cares",
)

SORRY = (
    "sorry", "sowwy", "sorryy", "sry", "srry", "soz", "apologize", "apologise", "apology",
    "my bad", "forgive me", "didn't mean", "didnt mean", "i was mean", "won't do it again",
    "wont do it again", "i take it back",
)

_W = "|".join(re.escape(w) for w in MEAN_WORDS)
# "you are so stupid", "u r a loser", "bob is dumb", "you suck"
AT_YOU = re.compile(
    r"\b(you|u|ur|you're|youre|bob|ya)\s+((are|r|is|look|smell|sound|act|seem)\s+)?"
    r"((so|such|a|an|the|really|very|super|kinda|big|little|total|literally|just)\s+){0,3}"
    rf"({_W})s?\b", re.I)
# "stupid bob", "dumb robot"
NAME_CALL = re.compile(rf"\b({_W})\s+(bob|kid|robot|baby|thing)\b", re.I)


def _has(phrase, low):
    return re.search(r"(?<![a-z])" + re.escape(phrase.strip()) + r"(?![a-z])", low) is not None


GAME = re.compile(r"\b(1v1|1 v 1|game|games|gaming|minecraft|bedwars|fortnite|roblox|pubg|bgmi|fifa|chess|race|racing|"
                  r"match|play|playing|at (cricket|football|tag|hide and seek)|gg|noob|level|round)\b")


def _mean(low):
    if any(_has(p, low) for p in MEAN_PHRASES):
        return True
    if any(_has(g, low) for g in GAALI) or HINDI_RE.search(low):
        return True
    if CRUEL_RE.search(low):
        return True
    # "1v1 me, ill destroy you" is banter, not a threat
    if THREAT_RE.search(low) and not GAME.search(low):
        return True
    return bool(AT_YOU.search(low) or NAME_CALL.search(low))


# is this message even about bob? ("my friend was mean to me" isn't)
def at_bob(msg):
    low = (msg or "").lower()
    if re.search(r"\b(to me|at me|my (friend|brother|sister|mom|dad|teacher)|he|she|they|them)\b", low):
        return bool(re.search(r"\b(you're|youre|ur|bob)\b", low))
    return bool(re.search(r"\b(you|u|ur|you're|youre|your|bob|ya|tu|tum|tere|teri|tera|tujhe)\b", low))


# "YOU say sorry first", "not sorry", "sorry not sorry" are not apologies
NOT_SORRY = re.compile(r"\b(you|u|bob)\s+(say|should say|need to say|have to say|must say|gotta say)\s+sor+y|"
                       r"\bsay sor+y (first|to me)\b|\bnot sor+y\b|\bsor+y not sor+y\b|\bnever (say|saying) sor+y\b|"
                       r"\bwhy should i (say )?sor+y\b|\bi won'?t (say )?sor+y\b")


def apology(low):
    return any(s in low for s in SORRY) and not NOT_SORRY.search(low)


def judge(msg):
    low = (msg or "").lower()
    if apology(low):
        return "sorry"
    if _mean(low) or NOT_SORRY.search(low):
        return "mean"
    return None


# bob should never be mean back. only count things aimed at "you",
# not bob repeating what was said to him ("nobody wants to talk to me")
def is_mean(txt):
    low = (txt or "").lower()
    if any(_has(p, low) for p in MEAN_PHRASES if re.search(r"\b(you|u)\b", p) or p in ("shut up", "stfu", "shut it")):
        return True
    # "worms, go away!" in a song is fine, "go away!" at his friend isn't
    if re.search(r"(^|[.!?]\s*)(go away|get lost)\b|\b(you|u)\s+(go away|get lost)\b", low):
        return True
    if any(_has(g, low) for g in GAALI):
        return True
    return bool(AT_YOU.search(low) or NAME_CALL.search(low) or THREAT_RE.search(low))
