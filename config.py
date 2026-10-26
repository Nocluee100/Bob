import os

MODEL = os.environ.get("BOB_MODEL", "qwen3:4b")
HOST = os.environ.get("BOB_HOST", "http://localhost:11434")
TIMEOUT = int(os.environ.get("BOB_TIMEOUT", 180))

# sampling
TEMP = 0.9
TOP_P = 0.95
TOP_K = 40
MIN_P = 0.05
MAX_TOK = 320
NUM_CTX = 8192
RETRY_BUMP = 0.1
RETRIES = 2

# bob
START_MOOD = "happy"
PECKISH_MSGS = 15
HUNGRY_MSGS = 20
HUNGRY_SECS = 30*60
NAP_SECS = 10*60

# replies
MAX_SENT = 30
MAX_LEN = 280
BIG_WORD = 13
RECENT_N = 6
STRETCH_CHANCE = 0.45

HIST_LEN = 2200
CHEW = True
TYPE_MS = 45

HELLO = "This is bob, say hi to Bob!"
