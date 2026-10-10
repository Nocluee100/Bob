import json, re

from sprites import MOODS
from system_prompt import SYSTEM_PROMPT, NOTE, REMIND

def sys_prompt():
    return SYSTEM_PROMPT.format(moods=", ".join(MOODS))


# his old lines, cut short. the little model copies whatever it sees,
# so long lists of shouting in the history turn into more of the same
def short(txt):
    parts = re.findall(r"[^.!?]+[.!?]*", txt or "")
    out = "".join(parts[:3]).strip()
    return out[:200] if out else txt


# way back lines just keep their first sentence, so he remembers what happened
# without copying how he said it
def tiny(txt):
    parts = re.findall(r"[^.!?]+[.!?]*", txt or "")
    return (parts[0].strip() if parts else txt)[:80]


def build(turns, msg, sit=""):
    msgs = [{"role": "system", "content": sys_prompt()}]
    mine = [i for i, t in enumerate(turns) if t[0] != "You"]
    recent = set(mine[-2:])
    for i, (who, mood, txt) in enumerate(turns):
        if who == "You":
            msgs.append({"role": "user", "content": txt})
        else:
            msgs.append({"role": "assistant",
                         "content": json.dumps({"mean": False, "sorry": False, "mood": mood or "happy", "reply": short(txt) if i in recent else tiny(txt)})})
    if sit:
        msg += "\n" + NOTE.format(situation=sit)
    msg += "\n" + REMIND
    msgs.append({"role": "user", "content": msg})
    return msgs
