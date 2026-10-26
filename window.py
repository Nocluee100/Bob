import math, queue, random, re, threading
import tkinter as tk
from tkinter import font as tkfont

import brain, commands, config, sprites

BG = "#000000"
INK = "#f4f4f4"
DIM = "#7a7a7a"
BOX = "#141414"

COLS = {"happy": "#ffd84d", "sad": "#6fa8ff", "crying": "#5fe3ff",
        "eating": "#7dff8a", "hungry": "#ff6b6b", "sleeping": "#d68cff"}

TEARS = ["      ' '      ", "      ; ;      ", "      . .      ", "               "]
ZZZ = ["          z    ", "          zZ   ", "          zZz  ", "               "]
BLANK = " " * 15

WIDE = re.compile(r"[^\u0000-￿]")


def first(want, have):
    for f in want:
        if f in have:
            return f
    return want[-1]


class Screen:
    def __init__(self, chat):
        self.chat = chat
        self.q = queue.Queue()
        self.busy = False
        self.left = ""
        self.at = 0
        self.then = None
        self.mood = chat.bob.mood
        self.dots = 0
        self.tick = 0
        self.blink = 0
        self.wink = 30
        self.grr = 0
        self.pop = 0

        root = self.root = tk.Tk()
        root.title("Bob")
        root.configure(bg=BG)
        root.geometry("1000x720")
        root.minsize(620, 480)
        root.protocol("WM_DELETE_WINDOW", self.close)

        have = set(tkfont.families())
        comic = first(["Comic Sans MS", "Comic Neue", "Chalkboard SE", "Chalkboard", "TkDefaultFont"], have)
        mono = first(["Menlo", "Monaco", "DejaVu Sans Mono", "Courier New", "Courier"], have)

        # --- bottom: where you type ---
        bar = tk.Frame(root, bg=BG)
        bar.pack(side="bottom", fill="x", padx=40, pady=(0, 30))
        self.box = tk.Entry(bar, font=(comic, 18), bg=BOX, fg=INK, insertbackground=INK, relief="flat",
                            highlightthickness=1, highlightbackground="#2a2a2a", highlightcolor="#555555")
        self.box.pack(fill="x", ipady=10)
        self.box.bind("<Return>", self.send)
        self.box.focus_set()

        self.note = tk.Label(root, text="(type /help to see what you can do)", font=(comic, 12),
                             bg=BG, fg=DIM, justify="center", height=2)
        self.note.pack(side="bottom", pady=(0, 8))

        # --- middle: bob and what he says ---
        mid = tk.Frame(root, bg=BG)
        mid.pack(expand=True, fill="x")
        self.big = tkfont.Font(family=mono, size=30, weight="bold")
        self.huge = tkfont.Font(family=mono, size=33, weight="bold")
        stage = tk.Frame(mid, bg=BG, height=self.huge.metrics("linespace") * 4 + 24)
        stage.pack(fill="x", pady=(0, 16))
        self.bob = tk.Label(stage, font=self.big, bg=BG, justify="left")
        self.bob.place(relx=0.5, rely=0.5, anchor="center")
        self.said = tk.Text(mid, font=(comic, 22), bg=BG, fg=INK, width=10, height=6, wrap="word",
                            relief="flat", borderwidth=0, highlightthickness=0, cursor="arrow",
                            selectbackground=BG, selectforeground=INK, inactiveselectbackground=BG)
        self.said.tag_configure("mid", justify="center", spacing2=6)
        self.said.tag_configure("hid", foreground=BG)
        self.said.tag_configure("dim", foreground=DIM)
        self.list = tkfont.Font(family=mono, size=12)
        self.said.tag_configure("list", font=self.list, foreground=DIM, justify="left")
        self.said.configure(state="disabled")
        self.said.pack(fill="x", padx=70)
        self.said.bind("<Button-1>", self.skip)
        root.bind("<Escape>", self.skip)

        self.draw()
        self.speak(config.HELLO)
        root.after(120, self.loop)
        threading.Thread(target=self.ping, daemon=True).start()
        root.after(100, self.poll)

    # --- bob ---

    def face(self):
        m, t = self.mood, self.tick
        f = sprites.FACES.get(m, sprites.FACES["happy"])
        if m == "eating" and config.CHEW:
            f = "^o^" if t % 4 < 2 else "^O^"
        if self.blink and m in ("happy", "sad", "hungry"):
            f = "-_-"
        return f

    def draw(self):
        m, t = self.mood, self.tick
        top = low = BLANK
        if m == "sleeping":
            top = ZZZ[t // 5 % len(ZZZ)]
        elif m == "eating" and t % 10 < 6:
            top = "     nom nom   "
        elif m == "hungry" and self.grr:
            top = "    *grumble*  "
        if m == "crying":
            low = TEARS[t // 2 % len(TEARS)]
        s = top + "\n" + sprites.SPRITE.format(face=self.face()) + "\n" + low
        self.bob.configure(text=s, fg=COLS.get(m, INK), font=self.huge if self.pop else self.big)

    def loop(self):
        self.tick += 1
        t, m = self.tick, self.mood
        if self.blink:
            self.blink -= 1
        else:
            self.wink -= 1
            if self.wink <= 0:
                self.blink, self.wink = 2, random.randint(25, 55)
        if self.grr:
            self.grr -= 1
        elif m == "hungry" and random.random() < 0.03:
            self.grr = 8
        self.pop = max(0, self.pop - 1)

        x = y = 0
        if m == "crying":
            x = 3 if t % 2 else -3
        elif m == "hungry":
            x = round(2 * math.sin(t * 0.6))
        elif m == "sad":
            y = round(3 + 3 * math.sin(t * 0.2))
        else:
            y = round(2 * math.sin(t * 0.2))
        if self.at < len(self.left):
            y -= round(7 * abs(math.sin(t * 0.9)))
        self.bob.place_configure(x=x, y=y)
        self.draw()
        self.root.after(120, self.loop)

    def show(self, mood, txt, then=None):
        if mood != self.mood:
            self.pop = 2
        self.mood = mood
        self.draw()
        self.speak(txt, then)

    # --- typing it out ---

    def write(self, txt, tags=("mid",)):
        self.said.configure(state="normal")
        self.said.delete("1.0", "end")
        self.said.insert("1.0", txt, tags)
        self.said.configure(state="disabled")

    def speak(self, txt, then=None):
        self.left = WIDE.sub("", txt).strip()
        self.at = 0
        self.then = then
        self.write(self.left, ("mid", "hid"))
        self.type()

    def type(self):
        if self.at >= len(self.left):
            self.done()
            return
        self.at += 1
        self.said.tag_remove("hid", "1.0", f"1.0+{self.at}c")
        ch = self.left[self.at - 1]
        ms = config.TYPE_MS * random.uniform(0.7, 1.3)
        if ch in ".!?":
            ms += 280
        elif ch in ",;:":
            ms += 120
        self.root.after(int(ms), self.type)

    def skip(self, e=None):
        if self.at < len(self.left):
            self.at = len(self.left) - 1
        return "break"

    def done(self):
        if self.then:
            f, self.then = self.then, None
            f()

    def think(self):
        if not self.busy:
            return
        self.dots = self.dots % 3 + 1
        self.left, self.at = "", 0
        self.write("hmm" + "." * self.dots, ("mid", "dim"))
        self.root.after(400, self.think)

    # --- you ---

    def send(self, e=None):
        line = self.box.get().strip()
        if not line or self.busy:
            return
        self.box.delete(0, "end")
        self.note.configure(text="")
        self.skip()
        cmd, arg = commands.parse(line)
        bob = self.chat.bob

        if cmd in (None, "feed", "sleep") and bob.napped():
            self.note.configure(text="(you were gone a while... Bob fell asleep)")
            self.chat.mem.add("Bob", "Zzz... (fell asleep while you were away)", mood="sleeping")

        if cmd == "quit":
            self.show("sleeping", "Bye bye! I go nap in the computer now.", lambda: self.root.after(1500, self.close))
            self.busy = True
            return
        if cmd == "help":
            self.left, self.at = "", 0
            w = max(self.list.measure(x) for x in commands.HELP.splitlines())
            pad = max(0, (self.said.winfo_width() - w) // 2)
            self.said.tag_configure("list", lmargin1=pad, lmargin2=pad)
            self.write(commands.HELP, ("list",))
            return
        if cmd == "status":
            s = f"Bob is feeling: {bob.mood}     Tummy: {commands.tummy_bar(bob.tummy())}"
            if bob.upset:
                s += "\nBob is still waiting for a sorry..."
            self.note.configure(text=s)
            return
        if cmd == "history":
            self.history()
            return
        if cmd == "clear":
            self.write("")
            return
        if cmd == "unknown":
            self.note.configure(text="Bob doesn't know that one. Type /help")
            return

        self.busy = True
        self.think()
        threading.Thread(target=self.work, args=(cmd, arg), daemon=True).start()

    def work(self, cmd, arg):
        try:
            self.q.put(("ok",) + self.chat.turn(cmd, arg))
        except brain.BrainError as e:
            self.q.put(("err", "sad", str(e)))
        except Exception as e:
            self.q.put(("err", "sad", f"Uh oh, something broke in my computer... ({e})"))

    def ping(self):
        try:
            brain.check()
        except brain.BrainError as e:
            self.q.put(("start", "sad", str(e)))

    def poll(self):
        try:
            while True:
                kind, mood, txt = self.q.get_nowait()
                if kind == "start":
                    self.show(mood, txt)
                    self.note.configure(text="(Bob will keep trying when you talk to him.)")
                    continue
                self.busy = False
                self.show(mood, txt)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def history(self):
        w = tk.Toplevel(self.root, bg=BG)
        w.title("This chat")
        w.geometry("640x520")
        t = tk.Text(w, bg=BG, fg=INK, font=self.note.cget("font"), wrap="word", relief="flat",
                    highlightthickness=0, padx=20, pady=20)
        t.insert("1.0", self.chat.mem.read().rstrip() or "(empty)")
        t.configure(state="disabled")
        t.pack(fill="both", expand=True)

    def close(self):
        self.chat.mem.wipe()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
