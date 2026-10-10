import time

import config, food, manners
from sprites import MOODS


SAD_WAYS = [
    "he says quietly that the words hurt his feelings and asks for a sorry",
    "he hides under his blanket and talks from under it, all muffled",
    "he hugs his teddy and tells teddy what they said, so they can hear",
    "he goes very quiet and only says a tiny 'sorry?'",
    "he sniffs and asks if they still want to be his friend",
    "he wipes his nose on his sleeve and says he won't stop crying till he hears sorry",
    "he turns around and sits with his back to them, peeking a little",
]


class Mood:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.mood = config.START_MOOD
        self.msgs = 0
        self.fed_at = clock()
        self.seen_at = clock()
        self.upset = False
        self.hint = False 
        self.maybe_mean = 0 
        self.sad_n = 0
        self.game = False

    @property
    def asleep(self):
        return self.mood == "sleeping"

    @property
    def hungry(self):
        return self.msgs >= config.HUNGRY_MSGS or self.clock() - self.fed_at >= config.HUNGRY_SECS

    @property
    def peckish(self):
        return self.msgs >= config.PECKISH_MSGS or self.clock() - self.fed_at >= config.HUNGRY_SECS * 0.75

    def tummy(self):
        a = 1 - self.msgs / config.HUNGRY_MSGS
        b = 1 - (self.clock() - self.fed_at) / config.HUNGRY_SECS
        return max(0.0, min(a, b, 1.0))

    def napped(self):
        away = self.clock() - self.seen_at
        self.seen_at = self.clock()
        if away >= config.NAP_SECS and not self.asleep:
            self.mood = "sleeping"
            return True
        return False

    def chat(self, msg):
        was_asleep = self.asleep
        self.msgs += 1
        notes, forced = [], None
        self.hint = False

        m = manners.judge(msg, self.game)
        if m == "sorry" and self.upset:
            self.upset = False
            forced = "happy"
            notes.append("They just said sorry! Bob stops crying, forgives them right away and is happy again.")
        elif m == "sorry":
            notes.append("They said sorry. Bob says it's okay, he isn't upset.")
        elif m == "mean":
            self.upset = True

        if self.upset:
            forced = "crying"
            notes.append("Someone was mean to Bob. He is crying and hurt. He is NOT mean back. "
                         "Bob did nothing wrong, so he does NOT say sorry himself. "
                         "He keeps crying until they say sorry to him, and asks them to say it. "
                         "Even if they say they were joking, it still hurt, so he is still sad until he hears sorry. "
                         "He talks in real little words, not long sounds. This time he shows it like this: "
                         + SAD_WAYS[self.sad_n % len(SAD_WAYS)] + ".")
            self.sad_n += 1

        if self.hungry:
            forced = "crying"
            notes.append("Bob is SO hungry he is crying for food. He has NOT eaten anything. "
                         "He begs them to type /feed. He really really wants biryani.")
        elif self.peckish and not self.upset:
            forced = forced or "hungry"
            if (self.msgs - config.PECKISH_MSGS) % 3 == 0:
                    notes.append("Bob's tummy is starting to rumble. He has NOT eaten anything, there is no food yet. "
                             "He still answers what they said first (if they asked for a story, he tells it), "
                             "then adds a tiny hint that he is getting hungry.")

        if was_asleep:
            notes.append("Bob was asleep and this message woke him up.")
        return forced, " ".join(notes)

    def feed(self, item):
        was_hungry = self.hungry
        kind, note = food.note(item, was_hungry)
        if kind == "pulao":
            return ("crying" if was_hungry or self.upset else "sad"), note
        if kind == "thing":
            return ("crying" if was_hungry else None), note
        if kind == "veggie":
            return "eating", note    # one brave bite doesn't fill a tummy
        self.msgs = 0
        self.fed_at = self.clock()
        if self.upset:
            note += " But he is still a little sad that someone was mean, he still wants a sorry."
        return "eating", note

    def sleep(self):
        return "sleeping", "Bob is going to sleep now. He says something very sleepy."

    def settle(self, forced, picked, mean=False, sorry=False, msg=None):

        if sorry and msg is not None and not manners.apology(msg.lower()):
            sorry = False
        if mean and msg is not None and (manners.GAME.search(msg.lower()) or self.game) and manners.judge(msg, self.game) != "mean":
            mean = False
        if mean and msg is not None and not manners.at_bob(msg):
            mean = False
            if forced is None and picked == "crying":
                picked = "sad"
        if mean and not self.upset and forced != "eating":

            self.maybe_mean += 1
            if self.maybe_mean >= 2:
                self.upset = True
                forced = "crying"
            elif forced is None and picked in (None, "happy"):
                picked = "sad"
        else:
            if not mean:
                self.maybe_mean = 0
            if sorry and self.upset:
                self.upset = False

        m = forced or picked
        steady = {"happy": "happy", "sad": "sad", "crying": "sad", "eating": "happy"}.get(self.mood, "happy")
        if m not in MOODS:
            m = steady
        if m == "eating" and forced != "eating":
            m = steady
        if m == "hungry" and not self.peckish:
            m = steady
        if m == "sleeping" and forced != "sleeping":
            m = "happy"
        self.mood = m
        return m
