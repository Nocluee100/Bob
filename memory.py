import atexit, os, re, tempfile

LINE_RE = re.compile(r"^(You|Bob)(?: \((\w+)\))?: (.*)$")


class Memory:
    def __init__(self):
        fd, self.path = tempfile.mkstemp(prefix="bob_session_", suffix=".txt")
        os.close(fd)
        atexit.register(self.wipe)

    def add(self, who, txt, mood=None):
        tag = f"{who} ({mood})" if mood else who
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"{tag}: {txt}\n")

    def read(self, n=None):
        try:
            with open(self.path, encoding="utf-8") as f:
                txt = f.read()
        except OSError:
            return ""
        if n and len(txt) > n:
            keep, size = [], 0
            for ln in reversed(txt.splitlines(keepends=True)):
                if keep and size + len(ln) > n:
                    break
                keep.append(ln)
                size += len(ln)
            txt = "".join(reversed(keep))
        return txt

    def turns(self, n=None):
        out = []
        for ln in self.read(n).splitlines():
            m = LINE_RE.match(ln)
            if m: out.append((m[1], m[2], m[3]))
        return out

    def wipe(self):
        try: os.remove(self.path)
        except OSError: pass
