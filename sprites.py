import os, sys, time

SPRITE = "(     {face}     )\n(>           <)"

FACES = {
    "happy": "^_^",
    "sad": "._.",
    "crying": "T_T",
    "eating": "^o^",
    "hungry": "o_o",
    "sleeping": "-_-",
}
MOODS = tuple(FACES)

CHEW_FRAMES = ("^o^", "^O^", "^o^", "^O^", "^o^")

# colors
COLS = {"happy": "\033[93m", "sad": "\033[94m", "crying": "\033[96m",
        "eating": "\033[92m", "hungry": "\033[91m", "sleeping": "\033[95m"}
RST = "\033[0m"
COLOR = "NO_COLOR" not in os.environ and sys.stdout.isatty()

if os.name == "nt":
    os.system("")


def art(mood, face):
    s = SPRITE.format(face=face)
    if COLOR:
        return COLS.get(mood, "") + s + RST
    return s

def draw(mood):
    return art(mood, FACES.get(mood, FACES["happy"]))


def show(mood, animate=False):
    if animate and mood == "eating" and COLOR:
        for i, f in enumerate(CHEW_FRAMES):
            if i: sys.stdout.write("\033[2A\r")
            sys.stdout.write(art(mood, f) + "\n")
            sys.stdout.flush()
            time.sleep(0.25)
        return
    print(draw(mood))
