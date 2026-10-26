HELP = """Things you can type:
  /feed      give Bob a snack (or /feed biryani, /feed white monster...)
  /sleep     tuck Bob into bed
  /poke      poke Bob (he's ticklish)
  /status    see how Bob is doing
  /history   see this session's chat
  /clear     clear the screen
  /help      show this list
  /quit      say bye to Bob"""

SNACK = None
BED = "*tucks Bob into bed*"

CMDS = {
    "/feed": ("feed", SNACK), "/eat": ("feed", SNACK), "/snack": ("feed", SNACK),
    "/sleep": ("sleep", BED), "/bed": ("sleep", BED),
    "/poke": ("poke", None), "/tickle": ("poke", None),
    "/status": ("status", None), "/tummy": ("status", None),
    "/history": ("history", None),
    "/clear": ("clear", None),
    "/help": ("help", None),
    "/quit": ("quit", None), "/q": ("quit", None), "/exit": ("quit", None), "/bye": ("quit", None),
}


def parse(txt):
    parts = txt.strip().split(" ", 1)
    w = parts[0].lower()
    if not w.startswith("/"):
        return None, txt
    cmd, log = CMDS.get(w, ("unknown", None))
    if cmd == "feed" and len(parts) > 1 and parts[1].strip():
        return cmd, parts[1].strip()
    return cmd, None if cmd == "feed" else log


def tummy_bar(full, w=10):
    n = round(full * w)
    return "[" + "#"*n + "."*(w - n) + "]"
