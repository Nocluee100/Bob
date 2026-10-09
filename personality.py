import json, re

from sprites import MOODS
from system_prompt import SYSTEM_PROMPT, NOTE

def sys_prompt():
    return SYSTEM_PROMPT.format(moods=", ".join(MOODS))


# his old lines, cut short. the little model copies whatever it sees,
# so long lists of shouting in the history turn into more of the same
def short(txt):
    parts = re.findall(r"[^.!?]+[.!?]*", txt or "")
    out = "".join(parts[:3]).strip()
    return out[:200] if out else txt


def build(turns, msg, sit=""):
    msgs = [{"role": "system", "content": sys_prompt()}]
    for who, mood, txt in turns:
        if who == "You":
            msgs.append({"role": "user", "content": txt})
        else:
            msgs.append({"role": "assistant",
                         "content": json.dumps({"mean": False, "sorry": False, "mood": mood or "happy", "reply": short(txt)})})
    if sit:
        msg += "\n" + NOTE.format(situation=sit)
    msgs.append({"role": "user", "content": msg})
    return msgs
