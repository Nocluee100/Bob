import os, re, sys, time
from collections import deque

import brain, checker, cleaner, commands, config, food, personality, senses, sprites, system_prompt, topics, voice
from memory import Memory
from mood import Mood

if sprites.COLOR:
    B, DIM, RST = "\033[1m", "\033[2m", "\033[0m"
else:
    B = DIM = RST = ""


# --- printing ---

def say(mood, txt, animate=False):
    print()
    sprites.show(mood, animate=animate and config.CHEW)
    print(f"{B}Bob:{RST} {txt}\n")

def note(txt):
    print(f"{DIM}{txt}{RST}")

def thinking(on):
    if on: print(f"{DIM}Bob is thinking...{RST}", end="\r", flush=True)
    else: print(" " * 20, end="\r", flush=True)

def cls():
    os.system("cls" if os.name == "nt" else "clear")


SAD_WORDS = re.compile(r"cry|sad|sniff|tear|scared|hurt|sorry|wah+|boo ?hoo|miss|lonely|ouch|no fair|don'?t want|nooo", re.I)


# --- one chat with bob ---

class Chat:
    def __init__(self, clock=time.monotonic):
        self.mem = Memory()
        self.bob = Mood(clock)
        self.recent = deque(maxlen=config.RECENT_N)
        self.used = set()
        self.joke = None     # (joke, step)
        self.ate = None      # (what, turns ago)
        self.pulao = 0       # turns left of "they're pushing pulao on me"
        self.veg = False     # friend said they're vegetarian
        self.food_talk = 99  # turns since the friend last talked about food
        self.name = None
        self.care = 0        # turns left of being extra careful after self-harm talk
        self.liked = deque(["chicken biryani", "white monster"], maxlen=12)
        self.stand = None    # thing they just dissed that bob loves
        self.stuff = []      # their pets and things, so bob doesn't steal them
        self.mem.add("Bob", config.HELLO, mood=self.bob.mood)
        self.recent.append(config.HELLO)

    def reply(self, turns, msg, forced, sit, food_ok=True, upset=False):
        def check(t, recent):
            mine = senses.took(t, self.stuff)
            if mine:
                return f"{mine} belongs to your friend, not to Bob. Say 'your' when you talk about it."
            if self.stand and senses.flip(t, self.stand):
                return f"Bob loves {self.stand}! He doesn't suddenly hate it just because they do."
            return checker.problem(t, recent, msg, food_ok, upset, self.veg)
        temp = None
        picked, txt, flags = None, "", {}
        okish = None   # best reply that only had a small problem
        for n in range(config.RETRIES + 1):
            raw = brain.ask(personality.build(turns, msg, sit), temp)
            picked, txt, flags = cleaner.clean(raw, self.bob.mood)
            issue = check(txt, self.recent)
            if issue is None:
                return picked, txt, flags
            if checker.soft(issue):
                if okish is not None:
                    # second small slip in a row, good enough, don't keep them waiting
                    return picked, txt, flags
                okish = (picked, txt, flags)
            if issue not in sit:
                sit = (sit + " " + issue).strip()
            temp = config.TEMP + config.RETRY_BUMP

        # still bad. try once more with no history to trip over
        raw = brain.ask(personality.build([], msg, sit), config.TEMP)
        picked, txt, flags = cleaner.clean(raw, self.bob.mood)
        issue = check(txt, [])
        if issue is None or checker.soft(issue):
            return picked, txt, flags
        if okish:
            return okish
        return picked, "...", flags

    # what's going on in their message, as notes for the brain
    def notes(self, msg, forced):
        kinds = senses.read(msg)
        if self.bob.upset:
            kinds = [k for k in kinds if k != "tease"]   # already crying, not just teased
        if "hurt_self" in kinds:
            self.care = 6
        elif self.care:
            self.care -= 1
            kinds = kinds + ["care"]
        if senses.veg(msg):
            self.veg = True
        self.name = senses.name(msg) or self.name
        for x in senses.theirs(msg):
            if x not in self.stuff:
                self.stuff = (self.stuff + [x])[-6:]
        out = [senses.notes(kinds)]
        self.stand = senses.against(msg, self.liked)
        if self.stand:
            out.append(senses.against_note(self.stand))
        if self.name:
            out.append(f"(Your friend's name is {self.name}. Other names they mention are pets, family or friends.)")
        if senses.family(msg):
            out.append(senses.FAMILY_NOTE)
        if self.stuff:
            who = self.name or "your friend"
            extra = " When they say 'my' something, it's theirs." if any(not n for _, n in self.stuff) else ""
            out.append("(These are " + who + "'s, not Bob's: " + ", ".join(f"the {k} {n}".strip() for k, n in self.stuff)
                       + "." + extra + ")")
        stuck = [w for w in voice.stuck_on(self.recent, msg) if not self.name or w != self.name.lower()]
        if stuck:
            out.append(f"(Bob keeps talking about {', '.join(stuck[:2])}. This time he doesn't bring it up, he talks about what they said.)")

        if self.joke and len(msg.split()) > 8 and "who" not in msg.lower():
            self.joke = None    # they moved on
        if senses.no_jokes(kinds) or self.care or self.bob.upset:
            self.joke = None
        elif self.joke:
            j, step = self.joke
            t = topics.joke_note(j, step + 1)
            self.joke = (j, step + 1) if t else None
            out.append(t or "")
        else:
            j = topics.joke(msg, self.used)
            if j:
                self.used.add(j)
                self.joke = (j, 0)
                out.append(topics.joke_note(j, 0))

        if not kinds and not self.care and not self.joke and topics.lull(msg) and not forced:
            t = topics.pick(self.used)
            self.used.add(t)
            out.append(f'There is nothing much to talk about, so Bob asks them a fun new question: "{t}?" '
                       "He asks it and lets THEM answer, he doesn't answer it himself.")
        return " ".join(x for x in out if x)

    # knock knock middle lines only work if bob stops right after the word
    def trim_joke(self, txt):
        if not self.joke:
            return txt
        j, step = self.joke
        lines = topics.joke_lines(j)
        if not j.startswith("knock") and step == 0:
            # don't spoil the answer, stop at the question
            i = txt.lower().find(lines[0].lower().rstrip("?"))
            return txt if i < 0 else txt[:i + len(lines[0])].rstrip(" ,.!?") + "?"
        if not j.startswith("knock") or step == len(lines) - 1:
            return txt
        i = txt.lower().find(lines[step].lower())
        if i < 0:
            return txt
        return txt[:i + len(lines[step])].rstrip(" ,.!?") + "!"

    def turn(self, cmd, arg):
        """returns (mood, what bob says)"""
        if cmd is None and topics.bedtime(arg):
            cmd = "sleep"
        self.stand = None
        if self.ate:
            self.ate = (self.ate[0], self.ate[1] + 1) if self.ate[1] < 2 else None
        self.pulao = max(0, self.pulao - 1)
        if cmd == "feed":
            item = arg or food.random_snack()
            if food.kind(item) != "pulao":
                self.ate = (item, 0)
            line = f"*gives Bob {item}*"
            forced, sit = self.bob.feed(item)
        elif cmd == "sleep":
            line = arg if arg and not arg.startswith("*") else "*tucks Bob into bed*"
            forced, sit = self.bob.sleep()
        else:
            line = arg
            # "i have candy for you if you come outside" is not a snack, it's a stranger
            offer = None if "safety" in senses.read(arg) else food.offered(arg)
            if offer:
                forced, sit = self.bob.feed(offer)
                if food.kind(offer) != "pulao":
                    self.ate = (offer, 0)
            else:
                forced, sit = self.bob.chat(arg)
                sit = (sit + " " + self.notes(arg, forced)).strip()
                soon = food.later(arg)
                if soon and "safety" not in senses.read(arg):
                    sit = (sit + f" They are offering to get Bob {soon} soon. He doesn't have it yet and hasn't eaten it. "
                                 + ("He says no thank you, that's pulao!" if food.kind(soon) == "pulao" else "He's excited and waits.")).strip()

        self.food_talk = 0 if food.about_bobs_food(line) or cmd == "feed" else self.food_talk + 1
        food_ok = (cmd == "feed" or forced == "eating" or self.bob.hungry or self.bob.hint
                   or self.food_talk == 0)
        if self.bob.upset and not self.bob.hungry and cmd != "feed":
            food_ok = None   # crying about something mean, food talk would be weird
        fed = cmd == "feed" or forced == "eating"
        if food_ok and not fed:
            extra = system_prompt.FOOD_NOTE
            if self.ate and self.ate[1] > 0:
                extra += f" Bob just had {self.ate[0]} a moment ago, so if they ask about it, he is talking about {self.ate[0]}."
            if food.kind(line) == "pulao":
                self.pulao = 3
            if food.mentions_rice(line) or self.pulao:
                extra += " " + system_prompt.PULAO_NOTE
            if self.veg:
                extra += " " + system_prompt.VEG_NOTE
            sit = (extra + " " + sit).strip()

        turns = self.mem.turns(config.HIST_LEN)
        self.mem.add("You", line)
        upset = self.bob.upset and cmd != "feed"
        picked, txt, flags = self.reply(turns, line, forced, sit, food_ok, upset)
        if picked in ("crying", "sad") and not forced and not SAD_WORDS.search(txt):
            picked = "happy"   # the face has to match the words
        m = self.bob.settle(forced, picked, flags.get("mean"), flags.get("sorry"), line)
        txt = voice.kidify(voice.no_name_start(voice.detic(txt, self.recent), self.recent, self.name))
        txt = self.trim_joke(txt)
        self.mem.add("Bob", txt, mood=m)
        self.recent.append(txt)
        self.liked.extend(x for x in senses.likes(txt) if x not in self.liked)
        return m, txt


def status(bob):
    note(f"Bob is feeling: {bob.mood}")
    note(f"Tummy:          {commands.tummy_bar(bob.tummy())}")
    if bob.upset:
        note("Bob is still waiting for a sorry...")


# --- main loop ---

def main():
    chat = Chat()
    bob = chat.bob

    say(bob.mood, config.HELLO)
    note("(type /help to see what you can do)")

    try:
        brain.check()
    except brain.BrainError as e:
        say("sad", str(e))
        note("(Bob will keep trying when you talk to him.)")

    while True:
        try:
            line = input(f"{B}You:{RST} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            line = "/quit"
        if not line:
            continue

        cmd, arg = commands.parse(line)

        if cmd in (None, "feed", "sleep") and bob.napped():
            note("(you were gone a while... Bob fell asleep)")
            sprites.show("sleeping")
            chat.mem.add("Bob", "Zzz... (fell asleep while you were away)", mood="sleeping")

        if cmd == "quit":
            say("sleeping", "Bye bye! I go nap in the computer now.")
            break
        elif cmd == "help":
            note(commands.HELP); continue
        elif cmd == "status":
            status(bob); continue
        elif cmd == "history":
            note("--- this session ---")
            print(chat.mem.read().rstrip() or "(empty)")
            note("--------------------")
            continue
        elif cmd == "clear":
            cls()
            sprites.show(bob.mood)
            continue
        elif cmd == "unknown":
            note("Bob doesn't know that one. Type /help"); continue

        thinking(True)
        try:
            m, txt = chat.turn(cmd, arg)
        except brain.BrainError as e:
            thinking(False)
            say("sad", str(e))
            continue
        except KeyboardInterrupt:
            thinking(False)
            note("(okay, Bob stopped thinking)")
            continue
        thinking(False)
        say(m, txt, animate=True)

    chat.mem.wipe()


if __name__ == "__main__":
    sys.exit(main())
