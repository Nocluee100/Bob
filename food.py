import random, re

# biryani spellings people actually type
BIRYANI = r"b(i|e)r(i|y|iy|ee)?(a|aa)?n(i|y|ee)"

PULAO_RE = re.compile(rf"\b(veg|vegetable|veggie|paneer|aloo|mushroom|soya)\s+{BIRYANI}\b|\bpul(a|l)?(o|v|w)\b|\bpilaf\b", re.I)
BIRYANI_RE = re.compile(rf"\b((chicken|mutton|egg|hyderabadi|lucknowi|kolkata|dum|prawn|fish)\s+)?{BIRYANI}\b", re.I)
# the drink, not the thing under the bed
MONSTER_RE = re.compile(r"\b(white\s+monster|monster\s+(ultra|white|energy|drink|can)s?)\b", re.I)

SNACKS = [
    "chicken biryani", "mutton biryani", "a White Monster", "a cookie", "a mango",
    "a samosa", "a big slice of pizza", "chocolate ice cream", "a banana",
    "some french fries", "a jalebi", "a gulab jamun", "an apple", "a cupcake",
    "some popcorn", "a rasgulla", "a chocolate bar", "egg biryani", "some noodles",
]

FOODS = [
    "biryani", "pulao", "white monster", "pizza", "ice cream", "cookie", "cookies",
    "chocolate", "cake", "cupcake", "mango", "apple", "banana", "samosa", "jalebi",
    "gulab jamun", "rasgulla", "fries", "popcorn", "noodles", "maggi", "candy", "burger",
    "sandwich", "pasta", "dosa", "idli", "paratha", "roti", "dal", "rice", "chips",
    "juice", "milk", "milkshake", "biscuit", "laddoo", "ladoo", "paneer", "momos",
    "grapes", "watermelon", "strawberry", "donut", "pancake", "soup", "khichdi", "chicken",
]

OFFER_RE = re.compile(
    r"\b(here'?s|here is|(?<!i )(?<!we )(?<!they )(?<!you )(?<!u )(?<!do )(?<!to )(?<!he )(?<!she )have (some|a|an|this)|eat (this|some|a|an)|i (got|brought|made|cooked|bought) you|"
    r"take (this|some|a|an)|want (some|a|an)|giving you|for you|here you go|here ya go|try (this|some)|eat up|"
    r"here,? eat|here,? have|here,? take|eat it|have it)\b", re.I)


FOOD_TALK = ("eat", "ate", "eating", "food", "hungry", "drink", "lunch", "dinner", "breakfast", "snack",
             "tummy", "yummy", "cook", "taste")


def talks_food(msg):
    low = (msg or "").lower()
    if BIRYANI_RE.search(low) or PULAO_RE.search(low) or MONSTER_RE.search(low):
        return True
    words = set(re.findall(r"[a-z]+", low))
    return bool(words & set(FOOD_TALK)) or any(re.search(rf"\b{re.escape(f)}(s|es)?\b", low) for f in FOODS)


ASKS_FAV = re.compile(r"\b(fav\w* (food|drink|snack|thing to eat)|what (do|would|will|did) (you|u) (like to |love to |want to |wanna |gonna |want )?(eat|drink|have)|(wanna|want to|want) (eat|drink)|"
                      r"are (you|u) hungry|(you|u) hungry|what('?s| is) for (lunch|dinner|breakfast)|khana khaya|"
                      r"what did (you|u) eat|what('?d| would) (you|u) (like|want) to eat)\b")


# should bob's own food likes come up? only if they ask about his food
def about_bobs_food(msg):
    low = (msg or "").lower()
    return mentions(low) or bool(ASKS_FAV.search(low))


def mentions_rice(txt):
    low = (txt or "").lower()
    return bool(BIRYANI_RE.search(low) or PULAO_RE.search(low))


def mentions(txt):
    low = (txt or "").lower()
    return bool(BIRYANI_RE.search(low) or PULAO_RE.search(low) or MONSTER_RE.search(low))


VEGGIES = re.compile(r"\b(broccoli|spinach|palak|karela|bitter gourd|cabbage|cauliflower|gobi|peas|beans|carrots?|"
                     r"brinjal|baingan|eggplant|lauki|bhindi|okra|salad|lettuce|cucumber|veggies|vegetables?|sprouts|kale|celery|onions?)\b", re.I)


# bob lives in a computer, so these are actually snacks for him
PC_FOOD = re.compile(r"\b(ram|wifi|wi-fi|bytes?|megabytes?|gigabytes?|data|pixels?|usb|batter(y|ies)|electricity|cables?|emojis?|"
                     r"memes?|gifs?|internet|bluetooth|charger|cookies? from (the )?(browser|internet|website))\b", re.I)
# not food at all
THING = re.compile(r"\b(shoes?|socks?|chappals?|slippers?|homework|books?|pencils?|erasers?|crayons?|soap|toothpaste|paper|"
                   r"rocks?|stones?|sand|mud|dirt|bugs?|worms?|spiders?|phones?|remote|keys|coins?|money|tissues?|hair|"
                   r"brother|sister|cat|dog|chair|table|lego|legos|glue|plastic|nothing|air)\b", re.I)


def kind(item):
    s = item or ""
    if PULAO_RE.search(s): return "pulao"
    if BIRYANI_RE.search(s): return "biryani"
    if MONSTER_RE.search(s): return "monster"
    if PC_FOOD.search(s): return "pc"
    if THING.search(s) and not any(re.search(rf"\b{re.escape(f)}", s, re.I) for f in FOODS): return "thing"
    if VEGGIES.search(s): return "veggie"
    return "food"


def random_snack():
    return random.choice(SNACKS)


# "should i make you halwa?", "want some ice cream?" - it's coming, not here yet
LATER_RE = re.compile(r"\b(want|wanna|should i|shall i|should \w+ (make|get|bring|cook|order)|do (you|u) want|would (you|u) like|can i (get|make|bring|order) (you|u)|"
                      r"i'?ll (make|get|bring|order|cook)|i will (make|get|bring|order|cook)|let me (make|get|bring))\b", re.I)


def later(msg):
    low = (msg or "").lower()
    if not LATER_RE.search(low):
        return None
    if PULAO_RE.search(low): return PULAO_RE.search(low).group(0)
    if BIRYANI_RE.search(low): return BIRYANI_RE.search(low).group(0)
    if MONSTER_RE.search(low): return "White Monster"
    for f in FOODS + ["halwa", "kheer", "lollipop", "sweets", "mithai", "laddoos", "fruit"]:
        if re.search(rf"\b{re.escape(f)}(s|es)?\b", low):
            return f
    return None


# "here's some biryani for you!" -> "biryani"
def offered(msg):
    if later(msg):
        return None
    # "a goldfish named biscuit" is a name, not a snack
    msg = re.sub(r"\b(named|called|name is|names?)\s+\w+", " ", msg or "", flags=re.I)
    if not OFFER_RE.search(msg or ""):
        return None
    # "how do u have an apple??" is asking, not giving
    if re.search(r"\b(how|why|where|what|when|who)\b", msg, re.I) and "?" in msg or re.search(r"[\U0001F914\U0001F928]", msg):
        return None
    low = msg.lower()
    if PULAO_RE.search(low): return PULAO_RE.search(low).group(0)
    if BIRYANI_RE.search(low): return BIRYANI_RE.search(low).group(0)
    if MONSTER_RE.search(low): return "White Monster"
    for f in FOODS:
        if re.search(rf"\b{re.escape(f)}(s|es)?\b", low):
            return f
    v = VEGGIES.search(low)
    return v.group(0) if v else None


def note(item, was_hungry):
    k = kind(item)
    if k == "pulao":
        n = (f"They tried to give Bob {item}. That is NOT biryani, that is just pulao! "
             "Bob does not eat pulao. He pushes it away and asks for real chicken biryani.")
        if was_hungry:
            n += " He is still super hungry, so he is still crying for real food."
        return k, n
    if k == "biryani":
        n = f"They gave Bob {item}! Biryani is his most favorite food in the whole world. He is soooo happy."
    elif k == "veggie":
        n = (f"They gave Bob {item}. Vegetables are YUCKY to Bob, like most kids. He makes a big yucky face, "
             "maybe takes one teeny tiny brave bite, and is very proud of himself.")
    elif k == "pc":
        n = (f"They gave Bob {item}. He lives in a computer, so that's real computer food for him! He tells them exactly "
             "what it tastes like, in a silly, very specific way.")
    elif k == "thing":
        n = (f"They tried to feed Bob {item}. That is NOT food! Bob reacts like a real kid: shocked, grossed out or giggly. "
             "He does not eat it, and he's still waiting for real food.")
        if was_hungry:
            n += " He is still super hungry, so he's crying for real food."
        return k, n
    elif k == "monster":
        n = "They gave Bob a White Monster! His favorite drink ever! He is super duper happy and full of zoom."
    else:
        n = f"They gave Bob {item}. He eats it all up and is happy."
    if was_hungry:
        n += " He was crying for food before, so now he stops crying, feels all better and says thank you."
    return k, n


NO = r"(don'?t|do not|not|never|no|hate|yuck|yucky|eww)"
LIKES_PULAO = re.compile(
    rf"\b(i\s*('?m|am)?\s*(love|like|want|eat|ate|eating|will eat|'ll eat|enjoy)|let'?s (eat|have))\b[^.!?]{{0,25}}\b(veg\w*|paneer)\s+{BIRYANI}|"
    rf"\b(i\s*('?m|am)?\s*(love|like|want|eat|ate|eating|will eat|'ll eat|enjoy)|let'?s (eat|have))\b[^.!?]{{0,25}}\bpul(a|l)?(o|v|w)\b|"
    rf"\b((veg\w*|paneer)\s+{BIRYANI}|pul(a|l)?(o|v|w))\b[^.!?]{{0,20}}\b(is|was|tastes)\s+(the best|so good|yummy|yum|delicious|tasty|good|great|amazing)", re.I)


# "veg biryani is the best!" from bob = no
def likes_pulao(txt):
    for s in re.findall(r"[^.!?]+[.!?]*", txt or ""):
        if LIKES_PULAO.search(s) and not re.search(rf"\b{NO}\b", s, re.I):
            return True
    return False


PUSH_RE = re.compile(r"\b(you (should|have to|need to|must|gotta) (eat|try)|(?<!n't )(?<!not )(?<!never )(?<!dont )eat (chicken|meat|mutton)|"
                     r"(chicken|mutton|meat|non ?veg)[^.!?]{0,20}(with me|together|for you|you'?ll love)|try (some )?(chicken|meat|mutton)|(give|share|offer|bring) (you|u) (my |some |a )?(chicken|mutton|meat))", re.I)


def pushes_meat(txt):
    return bool(PUSH_RE.search(txt or ""))


# "my chicken biryani is yucky" - never
FAV_BAD = re.compile(rf"(?<!veg )(?<!paneer )(?<!vegetable )\b({BIRYANI}|white monster)\b[^.!?]{{0,15}}[.!?]?\s*(it\s+)?(is|are|was|'s|tastes?)\s+(so\s+|really\s+)?(yucky|gross|bad|disgusting|icky|eww)", re.I)


def dislikes_fav(txt):
    return bool(FAV_BAD.search(txt or ""))


ATE = re.compile(r"\bi (just |already )?(ate|had|drank|eated|gobbled)\b|\bi'?ve (just )?(eaten|had)\b", re.I)


# "i ate biryani for lunch!" when nobody fed him
def claims_ate(txt):
    for s in re.findall(r"[^.!?]+", txt or ""):
        if ATE.search(s) and (mentions(s) or any(re.search(rf"\b{re.escape(f)}", s, re.I) for f in FOODS + ["snack", "food", "lunch", "dinner", "breakfast"])):
            return True
    return False
