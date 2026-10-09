import random, re

# stuff bob just wonders about
QUESTIONS = [
    "what's the funniest thing that happened to you today",
    "if you could eat only one food forever what would it be",
    "do you think clouds are soft like pillows",
    "what would you do if you were invisible for a whole day",
    "do you have a best friend, what are they like",
    "what's your favorite color and why",
    "if you had a pet dragon what would you name it",
    "do you think fish get thirsty",
    "what's the scariest dream you ever had",
    "what's the best dream you ever had",
    "if you could shrink and come live in the computer with me, what would you do first",
    "what's your favorite cartoon",
    "do you like rainy days or sunny days more",
    "what's the biggest thing you ever saw",
    "can you whistle, i can't, i just go pffff",
    "what do you want to be when you grow up",
    "do you think the moon follows the car on purpose",
    "what's the yuckiest food in the whole world",
    "if your toys came alive at night, which one would be the boss",
    "have you ever seen a rainbow, did you find the end of it",
    "what's your favorite song, can you sing it for me",
    "do you know any jokes",
    "do you know any knock knock jokes",
    "what's the coolest bug you ever saw",
    "if you could talk to animals, which one would you talk to first",
    "do you like birthdays, what was your bestest birthday",
    "what's your favorite game to play outside",
    "what's the loudest sound you ever heard",
    "do you think dinosaurs were nice or grumpy",
    "if you had a robot, what would you make it do",
    "do you have brothers or sisters",
    "what's your favorite thing to do on sunday",
    "have you ever been to the beach, did you make a sandcastle",
    "if you could fly, where would you go first",
    "what's in your pocket right now",
    "what did you eat today",
    "do you like cricket, who's your favorite player",
    "what's your favorite festival, i like diwali because of the sparkly lights",
    "do you like holi, did you get all colorful",
    "what's the best ice cream flavor in the whole universe",
    "can you do a cartwheel",
    "what's the funniest animal",
    "do you think there are monsters under beds, i check under my keyboard sometimes",
    "if you had a magic wand what would you wish for",
    "what makes you laugh the most",
    "what's your favorite shape, mine is the circle because it rolls",
    "do you like drawing, what do you draw",
    "how many teeth do you have, i have pixel teeth",
    "have you ever lost a tooth, did the tooth fairy come",
    "what's the tallest building you ever went in",
    "if you could be any animal what would you be",
    "do you think trees talk to each other at night",
    "what's your favorite word, mine is biryani",
    "do you like puzzles",
    "what's your favorite superhero",
    "if you built a fort, what would be inside it",
    "do you sleep with a teddy or blankie",
    "what do you think stars are made of",
    "have you ever been on an airplane, did you see the clouds from the top",
    "what would you put in a giant sandwich",
    "do you like bubbles, i want to pop a bubble so bad",
    "what's your favorite season",
    "have you ever seen snow",
    "what's the best thing about being a grown up",
    "what's the worst thing about being a grown up, is it taxes, what are taxes",
    "do you think the sun goes to sleep",
    "if you had a treasure chest what would be in it",
    "what's the silliest face you can make",
    "do you like swimming",
    "what color would your house be if you could paint it any color",
    "do you know how to tie your shoes, i don't have shoes",
    "if you had a time machine would you go see dinosaurs or the future",
    "what's your favorite thing about yourself",
    "who is the funniest person you know",
    "what's the best present you ever got",
    "do you like playing hide and seek, i'm really good, i hide in folders",
    "if you were a superhero what would your name be",
    "what's the best smell in the world, i think biryani smell",
    "do you think aliens like biryani",
    "what's a thing you're really really good at",
    "what is your favorite number, mine is a gazillion",
    "do you have a favorite tree",
    "if you could make a new holiday, what would it be called",
    "do you like trains, choo choo",
    "what's the longest word you know",
    "have you ever been to a zoo, which animal was the best",
    "if you could only have one toy forever, which one",
    "what's your favorite thing to build with blocks",
    "do you think the ocean has a bottom",
    "what was the last thing that made you super happy",
    "if you could live in a candy house would you eat the walls",
    "do you have a secret hideout",
    "what's your favorite thing about night time",
    "do you like stories, can you tell me one",
    "should i tell you a story about the computer mouse",
    "do you want to play a guessing game",
    "do you want to play i spy, i spy something... pixely",
    "want to play would you rather",
    "want to make up a song together",
    "want to make up a silly story together, you start",
    "can we play pretend, you be the captain and i'm the pirate",
    "can we count to a hundred together",
    "do you want to hear my bestest joke",
    "do you know what a white monster tastes like, it tastes like ZOOM",
    "do you like pulao, i don't, it's just sad biryani",
    "what do you think lives inside the clouds",
    "if your shoes could talk what would they say",
    "what would happen if it rained ice cream",
    "do you think cats have dreams",
    "what's a sound that makes you happy",
    "if you had a giant balloon, where would you float to",
    "what's your favorite kind of weather to jump in",
    "do you think grown ups ever play with toys secretly",
    "do you like riddles",
    "what was your favorite thing at school today",
    "who is your favorite teacher",
    "do you have homework, i don't have homework, i'm five",
    "what game do you play on the computer, maybe i'm in it",
    "what does your room look like",
    "if you could have any snack right now, what would it be",
    "do you think the wind is a big invisible giant breathing",
    "what's the bravest thing you ever did",
    "do you like the dark, i have a night light, it's the screen",
    "have you ever planted a seed, did it grow",
    "what's your favorite thing to do with your family",
    "what's your favorite movie",
    "if you met a real dinosaur what would you say",
    "if you had a lemonade stand what would you sell instead of lemonade",
    "do you like to dance, i do the wiggle dance",
    "what's the best thing about today",
]

ANIMALS = [
    "dog", "cat", "elephant", "tiger", "lion", "giraffe", "monkey", "penguin", "dolphin",
    "shark", "whale", "octopus", "turtle", "frog", "bunny", "panda", "koala", "kangaroo",
    "zebra", "hippo", "crocodile", "snake", "owl", "parrot", "peacock", "eagle", "duck",
    "chicken", "cow", "goat", "sheep", "pig", "horse", "camel", "bear", "polar bear",
    "fox", "wolf", "squirrel", "hamster", "mouse", "butterfly", "ladybug", "bee", "ant",
    "spider", "snail", "jellyfish", "starfish", "seahorse", "crab", "flamingo", "sloth",
    "cheetah", "rhino", "bat", "hedgehog", "raccoon", "otter", "unicorn",
]
ANIMAL_T = [
    "if you had a pet {x}, what would you name it",
    "do you think a {x} could live in a computer like me",
    "can you make the sound a {x} makes, i'll try too",
    "what would a {x} eat for breakfast, i think biryani",
    "would a {x} be a good best friend",
    "do you think a {x} is ticklish",
]

FOODS = [
    "pizza", "ice cream", "chocolate", "mango", "samosa", "jalebi", "noodles", "pancakes",
    "cookies", "cake", "popcorn", "french fries", "watermelon", "dosa", "momos",
    "gulab jamun", "strawberries", "burgers", "cupcakes", "pasta", "sandwiches", "bananas",
    "grapes", "apples", "parathas", "chips", "donuts", "milkshake", "candy", "maggi",
]
FOOD_T = [
    "do you like {x}, is it better than biryani, no way right",
    "what if it rained {x} from the sky",
    "how much {x} can you eat in one go",
    "would you eat {x} for breakfast lunch and dinner",
]

PLACES = [
    "on the moon", "at the beach", "in a jungle", "at the north pole", "in a castle",
    "at the bottom of the ocean", "on a volcano", "in candy land", "in a desert", "in a big city",
    "on a farm", "on a space station", "in a treehouse", "on a pirate ship", "at the zoo at night",
    "on a cloud", "in a toy shop", "in an igloo", "at a waterpark", "on dinosaur island",
    "inside a video game", "on top of a mountain", "in a magic forest", "in a giant library",
    "on mars", "at the circus", "on a train going everywhere", "in a secret cave",
    "in the rainforest", "in a snowy village",
]
PLACE_T = [
    "if we were {x} together, what would we do first",
    "what do you think we would find {x}",
    "would you want to live {x}",
]

POWERS = [
    "fly", "turn invisible", "talk to animals", "breathe underwater", "be super strong",
    "run super fast", "shrink tiny", "grow giant", "teleport", "make it snow",
    "make food appear", "read minds", "stop time", "jump really high", "glow in the dark",
    "turn things into chocolate", "make toys come alive", "walk through walls",
    "control the weather", "never be sleepy", "go inside computers like me", "talk to plants",
    "make bubbles from your hands", "turn into any animal", "speak every language",
]
POWER_T = [
    "if you could {x}, what's the first thing you would do",
    "would you rather {x} or fly, flying is pretty good",
]

THINGS = [
    "rockets", "trains", "trucks", "fire engines", "helicopters", "submarines", "race cars",
    "tractors", "boats", "hot air balloons", "robots", "dinosaurs", "volcanoes", "rainbows",
    "thunderstorms", "the stars", "planets", "black holes", "comets", "the sun", "magnets",
    "bubbles", "kites", "lego", "puzzles", "crayons", "balloons", "slides", "swings",
    "trampolines", "sandcastles", "snowmen", "fireworks", "magic tricks", "treasure maps",
    "pirates", "knights", "dragons", "fairies", "ghosts", "aliens", "mermaids", "wizards",
    "ninjas", "superheroes", "astronauts", "cowboys", "spies", "detectives", "chefs",
]
THING_T = [
    "do you like {x}, i think {x} are sooo cool",
    "what's the coolest thing about {x}",
    "can you tell me something about {x}, i wanna know",
    "if you had a hundred {x}, what would you do with them",
]

JOBS = [
    "an astronaut", "a doctor", "a firefighter", "a teacher", "a chef", "a pilot",
    "a zookeeper", "a scientist", "a cricketer", "a dancer", "a singer", "a builder",
    "a police officer", "a farmer", "a painter", "a vet", "a train driver", "a youtuber",
    "an ice cream maker", "a biryani maker", "a magician", "a game maker", "a robot maker",
    "a deep sea diver", "a dinosaur digger",
]
JOB_T = [
    "would you want to be {x} when you grow up",
    "what do you think {x} does all day",
]

COLORS = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "black", "white",
          "rainbow", "gold", "silver"]
COLOR_T = [
    "if everything in the world was {x} for a day, what would be the funniest",
    "what's your favorite {x} thing",
]


def _build():
    out = list(QUESTIONS)
    for items, temps in ((ANIMALS, ANIMAL_T), (FOODS, FOOD_T), (PLACES, PLACE_T),
                         (POWERS, POWER_T), (THINGS, THING_T), (JOBS, JOB_T), (COLORS, COLOR_T)):
        for x in items:
            for t in temps:
                out.append(t.format(x=x))
    # would you rather
    a = ANIMALS[::2]
    b = ANIMALS[1::2]
    for x, y in zip(a, b):
        out.append(f"would you rather be a {x} or a {y}")
    for x, y in zip(FOODS[::2], FOODS[1::2]):
        out.append(f"would you rather eat only {x} or only {y} forever")
    seen, res = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            res.append(t)
    return res


ALL = _build()

BED_RE = re.compile(r"\b(time for bed|go to (sleep|bed)|bed ?time(?! stor)|good ?night|nap time|go nap|sleep now|time to sleep)\b", re.I)


def bedtime(msg):
    return bool(BED_RE.search(msg or ""))



# jokes a 5 year old would know (bob tells them his own way)
JOKES = [
    "knock knock / who's there / banana / banana who / knock knock / who's there / orange / orange who / orange you glad I didn't say banana",
    "knock knock / who's there / boo / boo who / don't cry, it's just a joke",
    "knock knock / who's there / cow says / cow says who / no silly, cow says moo",
    "knock knock / who's there / lettuce / lettuce who / lettuce in, it's cold out here",
    "knock knock / who's there / interrupting cow / interrupting c- / MOOO",
    "knock knock / who's there / olive / olive who / olive you",
    "knock knock / who's there / tank / tank who / you're welcome",
    "knock knock / who's there / ice cream / ice cream who / ice cream every time I see a ghost",
    "knock knock / who's there / atch / atch who / bless you",
    "knock knock / who's there / owls say / owls say who / yes they do",
    "knock knock / who's there / honeybee / honeybee who / honeybee a dear and get me some biryani",
    "knock knock / who's there / dishes / dishes who / dishes Bob, open up",
    "why did the cookie go to the doctor? because it felt crummy",
    "what do you call a sleeping dinosaur? a dino-snore",
    "why did the banana go to the doctor? because it wasn't peeling well",
    "what do you call a fish with no eyes? a fsh",
    "why can't a bicycle stand up by itself? because it's two tired",
    "what did one wall say to the other wall? I'll meet you at the corner",
    "why did the teddy bear say no to dessert? because she was stuffed",
    "what do you call a bear with no teeth? a gummy bear",
    "why do cows wear bells? because their horns don't work",
    "what's orange and sounds like a parrot? a carrot",
    "what do you call a dog magician? a labracadabrador",
    "why did the computer go to the doctor? it had a virus",
    "why was the computer cold? it left its windows open",
    "what do elves learn at school? the elf-abet",
    "why did the golfer wear two pants? in case he got a hole in one",
    "what do you call a pig that does karate? a pork chop",
    "how do you make a tissue dance? put a little boogie in it",
    "what has ears but cannot hear? a cornfield",
    "why did the egg hide? it was a little chicken",
    "what do you call a cow with no legs? ground beef",
    "why don't eggs tell jokes? they'd crack each other up",
    "what do you call a train carrying bubblegum? a chew chew train",
    "what kind of tree fits in your hand? a palm tree",
    "why are ghosts bad at lying? you can see right through them",
    "what do you call a snowman in summer? a puddle",
    "what animal needs to wear a wig? a bald eagle",
    "where do cows go on a date? to the moo-vies",
    "what do you call a duck that gets all A's? a wise quacker",
    "why did the kid bring a ladder to school? to go to high school",
    "what's a cat's favorite color? purr-ple",
    "how does the moon cut his hair? eclipse it",
    "why did the tomato blush? it saw the salad dressing",
    "what do you call a dinosaur with a big vocabulary? a thesaurus",
    "what did the zero say to the eight? nice belt",
    "why do bees have sticky hair? they use honeycombs",
    "what do you call a sleeping bull? a bulldozer",
    "what falls but never gets hurt? the rain",
    "what's brown and sticky? a stick",
]

JOKE_RE = re.compile(r"\b(joke|jokes|funny one|make me laugh|riddle)\b", re.I)


# "it was a joke", "jk" is not asking for one
NOT_ASK = re.compile(r"\b(was|just|only) (a |kidding|joking)|\b(it'?s|its|it was) (a |just a )?joke\b|\bjk\b", re.I)


# they have to actually ask ("worst joke ever" isn't asking)
ASK = re.compile(r"\b(tell|another|more|know (a|any)|got (a|any)|say|give|hear|share|make me laugh|funny one|riddle|joke\?|jokes\?|joke pls|joke please)\b", re.I)


def joke(msg, used=()):
    if not JOKE_RE.search(msg or "") or NOT_ASK.search(msg or "") or not ASK.search(msg or ""):
        return None
    knock = "knock" in (msg or "").lower()
    left = [j for j in JOKES if j not in used and (j.startswith("knock") or not knock)] or JOKES
    return random.choice(left)


# the lines bob says, one per turn
def joke_lines(j):
    if j.startswith("knock knock"):
        parts = [p.strip() for p in j.split("/")]
        return parts[0::2]
    q, a = j.split("?", 1)
    return [q.strip() + "?", a.strip()]


def joke_note(j, step):
    lines = joke_lines(j)
    if step >= len(lines):
        return None
    line = lines[step]
    if step == 0 and j.startswith("knock"):
        return f'Bob is telling a knock-knock joke. Right now he only says: "{line}!" and waits for them to say who\'s there.'
    if step == 0:
        return f'Bob is telling a joke. Right now he only asks: "{line}" and lets them guess. He does NOT say the answer yet.'
    if step == len(lines) - 1:
        return f'This is the funny end of the joke. He says: "{line}!" and then laughs and giggles a lot.'
    return f'Bob is in the middle of his knock-knock joke. He says just "{line.capitalize()}!" and nothing else, then waits for them to ask who.'


BORED = ("idk", "i dont know", "i don't know", "dunno", "nothing", "bored", "boring",
         "whatever", "u pick", "you pick", "you choose", "u choose", "anything",
         "what should we talk", "what do you want to talk", "talk about something",
         "say something", "hmm", "meh", "nm", "not much", "nothing much", "k", "ok", "okay")


def lull(msg):
    low = (msg or "").lower().strip(" .!?")
    if not low:
        return True
    if len(low.split()) > 5:
        return False
    if any(low == b or low.startswith(b + " ") for b in BORED):
        return True
    return any(b in low for b in BORED[:16])


def pick(used=()):
    left = [t for t in ALL if t not in used] or ALL
    return random.choice(left)
