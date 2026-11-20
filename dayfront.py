#!/usr/bin/env python3
"""dayfront.py — deterministic broadsheet renderer for "The Day in Full".

Renders the 20 November 2026 front page (1024x1024 PNG) from a single
master story list defined below. No clock, no network, no randomness:
two consecutive runs produce byte-identical output.
Prints STORY_COUNT=<n> counted from the master list itself.
"""
from PIL import Image, ImageDraw, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

# ---------------------------------------------------------------- fonts
NOTO = "/usr/share/fonts/truetype/noto"
DEJA = "/usr/share/fonts/truetype/dejavu"


def _pick(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[-1]


SERIF_B = _pick(f"{NOTO}/NotoSerif-Bold.ttf", f"{DEJA}/DejaVuSerif-Bold.ttf")
SERIF = _pick(f"{NOTO}/NotoSerif-Regular.ttf", f"{DEJA}/DejaVuSerif.ttf")
SANS_B = _pick(f"{NOTO}/NotoSans-Bold.ttf", f"{DEJA}/DejaVuSans-Bold.ttf")
SANS = _pick(f"{NOTO}/NotoSans-Regular.ttf", f"{DEJA}/DejaVuSans.ttf")

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
CARD = (255, 253, 246)
INK = (20, 18, 16)
MUTE = (92, 86, 76)
RULE = (60, 55, 48)
C_WORLD = (122, 31, 31)
C_MONEY = (20, 83, 45)
C_SCI = (29, 78, 107)
C_SOC = (91, 58, 142)
C_SPORT = (38, 44, 54)
GOLD = (176, 132, 32)
WIRE_BG = (18, 17, 15)
WIRE_TX = (240, 234, 218)

# ---------------------------------------------------------------- data
# Every figure/date below is taken verbatim from the day's wire copy.
HEROES = [
    {
        "kick": "JUSTICE · THE HAGUE",
        "head": "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
        "deck": "ICJ rules 9\u20136 for The Gambia \u2014 the first genocide finding "
                "against a state by the world court. Rohingya refugees welcome the verdict.",
        "scene": "court",
    },
    {
        "kick": "SHENZHEN SUMMIT",
        "head": "TRUMP, XI AND PUTIN \u2014 ONE TABLE IN SHENZHEN",
        "deck": "First three-way summit agrees a four-point joint peace declaration "
                "as APEC leaders meet alongside.",
        "scene": "flags",
    },
    {
        "kick": "MONEY · NASDAQ",
        "head": "ANTHROPIC'S $81.3B IPO STORMS NASDAQ",
        "deck": "Priced $83, opened $111.50, closed $97.17 (+17%) \u2014 briefly a "
                "$2 trillion company; the largest IPO in history.",
        "scene": "chart",
    },
]

WORLD = [
    ("UKRAINE", "Kyiv bridges hit overnight",
     "Missiles and drones strike three bridges; 8 killed, 28 injured in nine regions.", "bridge"),
    ("NATO", "Poland scrambles defences",
     "Three objects \u2014 two missiles, one drone \u2014 violate Polish airspace.", "jet"),
    ("DIPLOMACY", "Europe ready to talk",
     "Allies in Berlin ready for talks; Trump: \u201cPutin wants to end the war\u201d.", "talk"),
    ("RIYADH", "Houthi missile scars Riyadh",
     "Strike damages the Saudi wealth fund tower, the city's tallest landmark.", "tower"),
    ("BALTIC", "Estonia seals its border",
     "Tallinn closes the Russian border for six months; Moscow cries \u201cIron Curtain\u201d.", "fence"),
    ("GAZA", "Gaza line crossed",
     "Israeli forces cross the Yellow Line in central Gaza as the ceasefire frays.", "line"),
    ("HORN OF AFRICA", "Horn of Africa on edge",
     "Ethiopia and Eritrea mass troops; Somalia orders the UAE envoy out.", "troops"),
    ("SENEGAL", "Senegal boat tragedy",
     "Dozens missing as a boat with about 100 migrants sinks; four bodies found.", "boat"),
]

MONEY = [
    ("WALL STREET", "Fifth straight fall",
     "S&P 500 -2%, Nasdaq -2.2%, Dow -1,101 points as the AI sell-off bites.", "down"),
    ("ASIA", "Nikkei sinks 4.8%",
     "Taiwan index plunges 2,200+ points intraday and breaks below 37,000.", "down"),
    ("IMF", "IMF debt alarm",
     "Global public debt is nearing 100% of world GDP, the IMF warns.", "globe"),
    ("ROME", "Italy fines Meta \u20ac805M",
     "Rome penalises Meta over Android photo access.", "phone"),
    ("SEOUL", "Korea's trillion year",
     "Annual exports pass $1 trillion for the first time in history.", "coin"),
    ("CHIPS", "Chips to China cleared",
     "Washington approves Nvidia and AMD chip sales to Chinese companies.", "chip"),
    ("MUMBAI", "Sensex swims upstream",
     "Sensex +1.21% and Nifty +1.14% \u2014 defying the global rout.", "up"),
]

SCIENCE = [
    ("ODISHA", "Cyclone Akvan makes landfall",
     "300,000 evacuated and 423 rescue teams on the Odisha\u2013Andhra coast.", "cyclone"),
    ("DEEP SPACE", "Voyager's light-day",
     "Voyager 1 is now a full light-day from Earth \u2014 the farthest object ever.", "sat"),
    ("JAXA", "Hayabusa2 limps on",
     "Engine trouble ends Japan's asteroid landing plan for the probe.", "probe"),
    ("FLORIDA", "Florida under water",
     "Catastrophic St. Johns River flooding; Cocoa at record flood stage.", "flood"),
    ("ENERGY", "AI's power bill",
     "IEA: AI data centres could push emissions sharply higher by 2030.", "bolt"),
    ("WILDLIFE", "Rhinos home, giraffes moved",
     "Rescued rhinos and relocated giraffes \u2014 conservation wins in Africa.", "leaf"),
]

SOCIETY = [
    ("ART MARKET", "Van Gogh record",
     "Canvas sells for $190.4M, a record, after a row over its Nazi-era history.", "frame"),
    ("NASHVILLE", "Ella Langley sweeps the CMAs",
     "Entertainer, Female Vocalist, Song and Single of the Year in one night.", "note"),
    ("BASEBALL", "A pardon for Pete Rose",
     "Trump posthumously pardons the baseball legend.", "ball"),
    ("STREETS", "Youth take the streets",
     "Young people in 25+ countries strike over living costs and militarisation.", "crowd"),
    ("CHANNEL", "EU\u2013UK youth bridge",
     "Up to 100,000 a year to live, work and study across the Channel.", "bridge2"),
    ("DHAKA", "Yunus home torched",
     "Fire at the ancestral home of Bangladesh's Muhammad Yunus; arson suspected.", "flame"),
    ("MALAWI", "Malawi's fuel chaos",
     "Fuel crisis halts roads and markets \u2014 \u201ccompletely messed up everything\u201d.", "pump"),
]

SPORT = [
    ("NZ 243/5 vs INDIA", "Wellington Test D1 \u2014 Nicholls 113 not out."),
    ("F1 IN LAS VEGAS", "Prize-money jackpot fight under the lights."),
    ("GTA 6 TOPS $1.80B", "Sales pass The Odyssey's $1.80B global run."),
    ("FAIRFORD TRIAL SET", "Two charged over RAF incursion; trial Nov 2027."),
    ("IRAQ MOVES SOUTH", "Jurf al-Sakhar push vs Kataib Hezbollah smuggling."),
]

WIRE = [
    "US Senate blocks Iran war-powers measure 51\u201348, first vote since the midterms",
    "Trump pushes his Iran decision to the new year: \u201csee what happens\u201d",
    "Senate passes permitting overhaul 62\u201333 to speed energy projects",
    "North Korea expanding uranium enrichment, the IAEA says",
    "Haiti police say 34 gang members killed in a capital raid",
    "Florida carries out a record 20th execution of the year",
    "White House fires its national cyber director amid an outage wave",
    "India\u2013Japan 2+2: Japanese troops to train on Indian ranges from 2027",
]

# By-the-Numbers tiles: the first six are standalone stat stories counted in
# the master list; the last two are highlights drawn from hero/card stories.
NUMBERS_COUNTED = [
    ("$81.3B", "raised in Anthropic's record IPO"),
    ("9\u20136", "ICJ vote on Myanmar genocide"),
    ("300,000", "evacuated ahead of Cyclone Akvan"),
    ("-4.8%", "Nikkei fall on the day"),
    ("$190.4M", "record price for a Van Gogh"),
    ("100,000", "EU\u2013UK youth places a year"),
]
NUMBERS_EXTRA = [
    ("$97.17", "Anthropic close, +17% on debut"),
    ("8", "killed in the Kyiv strikes"),
]
NUMBERS = NUMBERS_COUNTED + NUMBERS_EXTRA

# Master list: the single source the page is rendered from.
STORIES = (
    [("hero", h["head"]) for h in HEROES]
    + [("world", c[1]) for c in WORLD]
    + [("money", c[1]) for c in MONEY]
    + [("science", c[1]) for c in SCIENCE]
    + [("society", c[1]) for c in SOCIETY]
    + [("sport", s[0]) for s in SPORT]
    + [("wire", w) for w in WIRE]
    + [("numbers", n[0]) for n in NUMBERS_COUNTED]
)

# ---------------------------------------------------------------- text utils


def wrap(d, text, font, maxw):
    """Greedy word wrap; returns list of lines each <= maxw (long words split)."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=font) <= maxw:
            cur = trial
            continue
        if cur:
            lines.append(cur)
        while d.textlength(word, font=font) > maxw and len(word) > 1:
            cut = len(word)
            while cut > 1 and d.textlength(word[:cut], font=font) > maxw:
                cut -= 1
            lines.append(word[:cut])
            word = word[cut:]
        cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, text, path, start, minsz, maxw, max_lines, lh_ratio=1.14):
    """Largest font (<= start, >= minsz) whose wrap fits max_lines; returns
    (font, lines, line_height). At min size, overflow lines are ellipsised."""
    size = start
    while size > minsz:
        f = F(path, size)
        ls = wrap(d, text, f, maxw)
        if len(ls) <= max_lines:
            return f, ls, int(size * lh_ratio) + 1
        size -= 1
    f = F(path, minsz)
    ls = wrap(d, text, f, maxw)
    if len(ls) > max_lines:
        ls = ls[:max_lines]
        last = ls[-1]
        while last and d.textlength(last + "\u2026", font=f) > maxw:
            last = last[:-1]
        ls[-1] = last + "\u2026"
    return f, ls, int(minsz * lh_ratio) + 1


def one_line(d, text, path, start, minsz, maxw):
    """Shrink-to-fit single line; ellipsise only as a last resort."""
    size = start
    while size > minsz:
        f = F(path, size)
        if d.textlength(text, font=f) <= maxw:
            return f, text
        size -= 1
    f = F(path, minsz)
    t = text
    while t and d.textlength(t + "\u2026", font=f) > maxw:
        t = t[:-1]
    return f, t + "\u2026"


def draw_lines(d, x, y, lines, font, lh, fill):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


# ---------------------------------------------------------------- scenes


def scene_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 214, 228))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(90, 96, 104))
    cx = x + w // 2
    d.polygon([(cx - 86, y + 30), (cx + 86, y + 30), (cx, y + 8)], fill=(240, 236, 224), outline=INK)
    d.rectangle([x + 28, y + 34, x + w - 28, y + 40], fill=(240, 236, 224), outline=INK)
    for i in range(5):
        px = x + 44 + i * ((w - 88) // 4)
        d.rectangle([px - 6, y + 42, px + 6, y + h - 20], fill=(240, 236, 224), outline=INK)
    # scales of justice
    d.line([cx, y + 46, cx, y + 74], fill=INK, width=3)
    d.line([cx - 26, y + 50, cx + 26, y + 50], fill=INK, width=3)
    for sx in (cx - 26, cx + 26):
        d.line([sx, y + 50, sx - 9, y + 64], fill=INK, width=2)
        d.line([sx, y + 50, sx + 9, y + 64], fill=INK, width=2)
        d.arc([sx - 11, y + 58, sx + 11, y + 74], 0, 180, fill=INK, width=2)
    # gavel
    d.line([x + w - 62, y + h - 30, x + w - 34, y + h - 44], fill=(110, 72, 30), width=5)
    d.rectangle([x + w - 78, y + h - 52, x + w - 58, y + h - 38], fill=(110, 72, 30), outline=INK)


def scene_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 200, 224))
    # skyline
    bx = x + 6
    heights = [34, 52, 26, 62, 40, 56, 30, 46]
    for i, bh in enumerate(heights):
        bw = (w - 12) // len(heights)
        d.rectangle([bx + i * bw, y + h - 14 - bh, bx + (i + 1) * bw - 3, y + h - 14],
                    fill=(70, 84, 102))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(52, 60, 72))
    flags = [(198, 40, 40), (44, 74, 150), (224, 224, 218)]
    for i, col in enumerate(flags):
        px = x + 52 + i * ((w - 104) // 2)
        d.line([px, y + 12, px, y + 66], fill=INK, width=3)
        d.rectangle([px, y + 12, px + 44, y + 34], fill=col, outline=INK)
        if i == 0:
            d.ellipse([px + 6, y + 17, px + 16, y + 27], fill=(250, 210, 60))
        if i == 1:
            for s in range(3):
                d.ellipse([px + 5 + s * 12, y + 16, px + 10 + s * 12, y + 21], fill=(250, 250, 250))
        if i == 2:
            d.rectangle([px, y + 19, px + 44, y + 26], fill=(44, 74, 150))


def scene_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 40, 34))
    for gy in range(1, 4):
        yy = y + gy * (h // 4)
        d.line([x + 8, yy, x + w - 8, yy], fill=(52, 84, 70), width=1)
    pts = [(x + 18, y + h - 22), (x + 70, y + h - 34), (x + 118, y + h - 28),
           (x + 168, y + h - 52), (x + 220, y + h - 46), (x + w - 30, y + 18)]
    d.line(pts, fill=(84, 220, 140), width=4)
    for px, py in pts:
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(250, 210, 60), outline=INK)
    d.polygon([(x + w - 30, y + 8), (x + w - 44, y + 22), (x + w - 16, y + 24)],
              fill=(84, 220, 140))
    # bell
    bx, by = x + 40, y + 12
    d.arc([bx, by, bx + 34, by + 30], 180, 360, fill=(250, 210, 60), width=4)
    d.line([bx, by + 15, bx, by + 28], fill=(250, 210, 60), width=4)
    d.line([bx + 34, by + 15, bx + 34, by + 28], fill=(250, 210, 60), width=4)
    d.line([bx - 3, by + 28, bx + 37, by + 28], fill=(250, 210, 60), width=4)
    # coins
    for i, cx in enumerate((x + w - 92, x + w - 66)):
        cy = y + h - 30 - i * 4
        d.ellipse([cx, cy, cx + 22, cy + 22], fill=(250, 210, 60), outline=INK)
        d.text((cx + 6, cy + 3), "$", font=F(SANS_B, 13), fill=INK)


SCENES = {"court": scene_court, "flags": scene_flags, "chart": scene_chart}

# ---------------------------------------------------------------- icons


def icon(d, kind, x, y, s, col):
    """Tiny deterministic pictogram inside box (x, y, s, s)."""
    cx, cy = x + s // 2, y + s // 2
    if kind == "bridge":
        d.arc([x + 1, y + 4, x + s - 1, y + s + 6], 180, 360, fill=col, width=2)
        d.line([x, y + s - 4, x + s, y + s - 4], fill=col, width=2)
        d.line([x + 4, y + s - 4, x + 4, y + 8], fill=col, width=2)
        d.line([x + s - 4, y + s - 4, x + s - 4, y + 8], fill=col, width=2)
    elif kind == "jet":
        d.polygon([(x + 2, cy), (x + s - 4, y + 3), (x + s - 8, cy), (x + s - 4, y + s - 3)],
                  outline=col, width=2)
        d.line([x + 6, y + s - 5, cx, cy], fill=col, width=2)
    elif kind == "talk":
        d.ellipse([x + 2, y + 3, cx + 2, cy + 3], outline=col, width=2)
        d.ellipse([cx - 2, cy - 1, x + s - 2, y + s - 3], outline=col, width=2)
    elif kind == "tower":
        d.rectangle([cx - 4, y + 2, cx + 4, y + s - 3], outline=col, width=2)
        d.line([cx, y + 2, cx, y - 0], fill=col, width=2)
        d.line([cx - 4, cy, cx + 4, cy], fill=col, width=2)
    elif kind == "fence":
        for i in range(3):
            px = x + 3 + i * (s // 3)
            d.line([px, y + 3, px, y + s - 3], fill=col, width=2)
        d.line([x + 1, y + 7, x + s - 1, y + 7], fill=col, width=2)
        d.line([x + 1, y + s - 7, x + s - 1, y + s - 7], fill=col, width=2)
    elif kind == "line":
        d.line([x + 2, y + s - 3, x + s - 2, y + 3], fill=(200, 160, 20), width=3)
        d.line([x + 2, y + 6, x + 10, y + 6], fill=col, width=2)
    elif kind == "troops":
        d.polygon([(x + 2, y + s - 3), (cx, y + 3), (x + s - 2, y + s - 3)], outline=col, width=2)
        d.ellipse([cx - 3, cy - 2, cx + 3, cy + 4], fill=col)
    elif kind == "boat":
        d.polygon([(x + 3, cy), (x + s - 3, cy), (cx + 3, y + s - 6), (cx - 3, y + s - 6)],
                  outline=col, width=2)
        d.line([cx, cy, cx, y + 3], fill=col, width=2)
        d.arc([x, y + s - 8, cx, y + s + 2], 0, 180, fill=col, width=2)
        d.arc([cx - 2, y + s - 8, x + s, y + s + 2], 0, 180, fill=col, width=2)
    elif kind == "down":
        d.line([x + 2, y + 5, cx, cy + 2, x + s - 6, y + s - 6], fill=col, width=2)
        d.polygon([(x + s - 2, y + s - 10), (x + s - 2, y + s - 2), (x + s - 10, y + s - 2)],
                  fill=col)
    elif kind == "up":
        d.line([x + 2, y + s - 5, cx, cy - 2, x + s - 6, y + 6], fill=col, width=2)
        d.polygon([(x + s - 2, y + 2), (x + s - 2, y + 10), (x + s - 10, y + 2)], fill=col)
    elif kind == "globe":
        d.ellipse([x + 3, y + 3, x + s - 3, y + s - 3], outline=col, width=2)
        d.line([x + 3, cy, x + s - 3, cy], fill=col, width=1)
        d.arc([cx - 4, y + 3, cx + 4, y + s - 3], 0, 360, fill=col, width=1)
    elif kind == "phone":
        d.rectangle([cx - 5, y + 2, cx + 5, y + s - 2], outline=col, width=2)
        d.line([cx - 2, y + s - 6, cx + 2, y + s - 6], fill=col, width=2)
    elif kind == "coin":
        d.ellipse([x + 3, y + 3, x + s - 3, y + s - 3], outline=col, width=2)
        d.text((cx - 4, cy - 7), "$", font=F(SANS_B, 12), fill=col)
    elif kind == "chip":
        d.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], outline=col, width=2)
        for off in (-4, 0, 4):
            d.line([cx + off, cy - 6, cx + off, y + 2], fill=col, width=1)
            d.line([cx + off, cy + 6, cx + off, y + s - 2], fill=col, width=1)
    elif kind == "cyclone":
        for r in (10, 7, 4):
            d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col, width=2)
    elif kind == "sat":
        d.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], outline=col, width=2)
        d.rectangle([x + 1, cy - 3, cx - 6, cy + 3], outline=col, width=1)
        d.rectangle([cx + 6, cy - 3, x + s - 1, cy + 3], outline=col, width=1)
        d.arc([cx - 9, cy + 5, cx + 9, cy + 15], 200, 340, fill=col, width=1)
    elif kind == "probe":
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], outline=col, width=2)
        d.line([cx + 4, cy + 4, x + s - 3, y + s - 3], fill=col, width=2)
        d.line([cx - 4, cy - 4, x + 2, y + 2], fill=col, width=2)
    elif kind == "flood":
        for i, yy in enumerate((cy - 2, cy + 3, cy + 8)):
            d.arc([x + 1 + i * 2, yy - 4, cx + 3 + i * 2, yy + 4], 180, 360, fill=col, width=2)
            d.arc([cx - 1 + i * 2, yy - 4, x + s - 1 + i * 2, yy + 4], 180, 360, fill=col, width=2)
        d.line([cx - 5, y + 3, cx - 5, cy - 3], fill=col, width=2)
        d.polygon([(cx - 5, y + 3), (cx + 4, y + 6), (cx - 5, y + 9)], fill=col)
    elif kind == "bolt":
        d.polygon([(cx + 2, y + 2), (cx - 5, cy + 2), (cx, cy + 2), (cx - 2, y + s - 2),
                   (cx + 5, cy - 2), (cx, cy - 2)], fill=col)
    elif kind == "leaf":
        d.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], outline=col, width=2)
        d.line([x + 5, y + s - 5, x + s - 5, y + 5], fill=col, width=1)
    elif kind == "frame":
        d.rectangle([x + 3, y + 3, x + s - 3, y + s - 3], outline=(150, 110, 30), width=3)
        d.ellipse([cx - 4, cy - 5, cx + 4, cy + 3], fill=(240, 200, 60))
        d.polygon([(x + 5, y + s - 5), (cx, cy + 2), (x + s - 5, y + s - 5)], fill=col)
    elif kind == "note":
        d.ellipse([x + 4, y + s - 8, x + 11, y + s - 3], outline=col, width=2)
        d.line([x + 11, y + s - 6, x + 11, y + 4], fill=col, width=2)
        d.line([x + 11, y + 4, x + s - 4, y + 7], fill=col, width=2)
        d.ellipse([x + s - 11, y + s - 6, x + s - 4, y + s - 1], outline=col, width=2)
    elif kind == "ball":
        d.ellipse([x + 3, y + 3, x + s - 3, y + s - 3], outline=col, width=2)
        d.arc([x + 5, y + 4, x + 12, y + s - 4], 270, 90, fill=(180, 40, 40), width=1)
        d.arc([x + s - 12, y + 4, x + s - 5, y + s - 4], 90, 270, fill=(180, 40, 40), width=1)
    elif kind == "crowd":
        for i, ox in enumerate((4, 11, 18)):
            d.ellipse([x + ox, y + 4 + (i % 2) * 2, x + ox + 6, y + 10 + (i % 2) * 2], fill=col)
            d.arc([x + ox - 1, y + 10, x + ox + 7, y + 20], 180, 360, fill=col, width=2)
    elif kind == "bridge2":
        d.line([x + 1, y + s - 5, x + s - 1, y + s - 5], fill=col, width=2)
        d.arc([x + 2, y + 6, x + s - 2, y + s + 4], 180, 360, fill=col, width=2)
        d.line([cx, y + 7, cx, y + s - 5], fill=col, width=1)
    elif kind == "flame":
        d.polygon([(cx, y + 2), (cx + 6, cy + 3), (cx + 4, y + s - 3), (cx - 4, y + s - 3),
                   (cx - 6, cy + 3)], outline=(200, 90, 20), width=2)
        d.ellipse([cx - 2, cy + 2, cx + 2, y + s - 5], fill=(230, 150, 30))
    elif kind == "pump":
        d.rectangle([cx - 6, y + 3, cx + 3, y + s - 3], outline=col, width=2)
        d.rectangle([cx - 4, y + 6, cx + 1, y + 12], outline=col, width=1)
        d.line([cx + 3, cy, cx + 8, cy + 3], fill=col, width=2)
        d.line([cx + 8, cy + 3, cx + 8, y + s - 5], fill=col, width=2)
    else:
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=col)


# ---------------------------------------------------------------- render
W, H, M = 1024, 1024, 16
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# --- masthead
d.line([M, 12, W - M, 12], fill=INK, width=3)
d.line([M, 17, W - M, 17], fill=INK, width=1)
title = "THE DAY IN FULL"
tf = F(SERIF_B, 46)
tw = d.textlength(title, font=tf)
d.text(((W - tw) / 2, 22), title, font=tf, fill=INK)
sub_l, sub_r = "Vol. I \u00b7 No. 20", "World edition \u00b7 50 stories"
sf = F(SANS, 12)
d.text((M + 2, 76), sub_l, font=sf, fill=MUTE)
rw = d.textlength(sub_r, font=sf)
d.text((W - M - 2 - rw, 76), sub_r, font=sf, fill=MUTE)
dateline = "Friday, 20 November 2026 \u00b7 One page \u00b7 50 stories"
df_ = F(SERIF_B, 14)
dw = d.textlength(dateline, font=df_)
d.text(((W - dw) / 2, 74), dateline, font=df_, fill=INK)
d.line([M, 96, W - M, 96], fill=INK, width=3)
d.line([M, 100, W - M, 100], fill=INK, width=1)

# --- hero row
HY, HH = 108, 210
HW = (W - 2 * M - 20) // 3
for i, hero in enumerate(HEROES):
    x = M + i * (HW + 10)
    d.rectangle([x, HY, x + HW, HY + HH], fill=CARD, outline=RULE, width=1)
    SCENES[hero["scene"]](d, x + 1, HY + 1, HW - 2, 98)
    d.line([x, HY + 100, x + HW, HY + 100], fill=RULE, width=1)
    kf, kt = one_line(d, hero["kick"], SANS_B, 11, 9, HW - 20)
    d.text((x + 10, HY + 106), kt, font=kf, fill=GOLD)
    hf, hl, hlh = fit_lines(d, hero["head"], SERIF_B, 17, 12, HW - 20, 3)
    yy = draw_lines(d, x + 10, HY + 122, hl, hf, hlh, INK)
    dfnt, dl, dlh = fit_lines(d, hero["deck"], SANS, 11, 9, HW - 20, 3)
    draw_lines(d, x + 10, yy + 2, dl, dfnt, dlh, (52, 48, 42))

# --- section columns
SEC_Y = 328
COLW = (W - 2 * M - 10) // 2
ROW_H = 27


def section(x, y, name, color, cards):
    d.rectangle([x, y, x + COLW, y + 22], fill=color)
    d.text((x + 8, y + 4), name, font=F(SANS_B, 13), fill=(250, 247, 238))
    cnt = f"{len(cards)} stories"
    cf = F(SANS, 11)
    cw = d.textlength(cnt, font=cf)
    d.text((x + COLW - 8 - cw, y + 5), cnt, font=cf, fill=(250, 247, 238))
    yy = y + 22
    for j, (kick, head, deck, ic) in enumerate(cards):
        if j % 2 == 0:
            d.rectangle([x, yy, x + COLW, yy + ROW_H], fill=(252, 249, 240))
        d.rectangle([x, yy, x + 3, yy + ROW_H], fill=color)
        icon(d, ic, x + 7, yy + 3, 21, color)
        hf, ht = one_line(d, f"{kick} \u00b7 {head}", SANS_B, 12, 10, COLW - 40)
        d.text((x + 34, yy + 2), ht, font=hf, fill=INK)
        dfnt, dt = one_line(d, deck, SANS, 10, 8, COLW - 40)
        d.text((x + 34, yy + 15), dt, font=dfnt, fill=(66, 61, 53))
        yy += ROW_H
    d.line([x, yy, x + COLW, yy], fill=RULE, width=1)
    return yy


LX, RX = M, M + COLW + 10
end_l = section(LX, SEC_Y, "WORLD", C_WORLD, WORLD)
end_l = section(LX, end_l + 8, "SCIENCE & PLANET", C_SCI, SCIENCE)
end_r = section(RX, SEC_Y, "MONEY & TECH", C_MONEY, MONEY)
end_r = section(RX, end_r + 8, "SOCIETY & CULTURE", C_SOC, SOCIETY)
SEC_END = max(end_l, end_r)

# --- sport strip
SY = SEC_END + 8
SH = 58
d.rectangle([M, SY, W - M, SY + SH], fill=C_SPORT)
d.rectangle([M, SY, M + 86, SY + SH], fill=(24, 28, 36))
for ln, t in enumerate(("SPORT", "& PLAY")):
    f = F(SANS_B, 14)
    tw = d.textlength(t, font=f)
    d.text((M + (86 - tw) / 2, SY + 10 + ln * 18), t, font=f, fill=(250, 210, 60))
CELLW = (W - 2 * M - 86) // 5
for i, (head, deck) in enumerate(SPORT):
    x = M + 86 + i * CELLW
    if i:
        d.line([x, SY + 8, x, SY + SH - 8], fill=(110, 118, 132), width=1)
    hf, hl, hlh = fit_lines(d, head, SANS_B, 12, 9, CELLW - 14, 1)
    yy = draw_lines(d, x + 7, SY + 5, hl, hf, hlh, (250, 247, 238))
    dfnt, dl, dlh = fit_lines(d, deck, SANS, 9, 8, CELLW - 14, 2)
    draw_lines(d, x + 7, yy + 1, dl, dfnt, dlh, (196, 202, 214))

# --- by the numbers band
NY = SY + SH + 8
NH = 62
d.rectangle([M, NY, W - M, NY + NH], fill=(252, 249, 240), outline=RULE, width=1)
d.rectangle([M, NY, M + 86, NY + NH], fill=GOLD)
for ln, t in enumerate(("BY THE", "NUMBERS")):
    f = F(SANS_B, 13)
    tw = d.textlength(t, font=f)
    d.text((M + (86 - tw) / 2, NY + 12 + ln * 17), t, font=f, fill=(24, 20, 10))
TW = (W - 2 * M - 86) // 8
for i, (num, label) in enumerate(NUMBERS):
    x = M + 86 + i * TW
    if i:
        d.line([x, NY + 8, x, NY + NH - 8], fill=(205, 198, 178), width=1)
    nf, nt = one_line(d, num, SERIF_B, 19, 12, TW - 8)
    nw = d.textlength(nt, font=nf)
    d.text((x + (TW - nw) / 2, NY + 6), nt, font=nf, fill=INK)
    lf, ll, llh = fit_lines(d, label, SANS, 9, 7, TW - 10, 2)
    ly = NY + 32
    for ln in ll:
        lw = d.textlength(ln, font=lf)
        d.text((x + (TW - lw) / 2, ly), ln, font=lf, fill=MUTE)
        ly += llh

# --- late wire
WY = NY + NH + 8
WH = H - 14 - WY
d.rectangle([M, WY, W - M, WY + WH], fill=WIRE_BG)
d.text((M + 10, WY + 6), "LATE WIRE", font=F(SANS_B, 14), fill=(250, 210, 60))
wt = "just in \u00b7 8 wires"
wf = F(SANS, 11)
ww = d.textlength(wt, font=wf)
d.text((W - M - 10 - ww, WY + 8), wt, font=wf, fill=(170, 164, 150))
d.line([M + 10, WY + 28, W - M - 10, WY + 28], fill=(90, 85, 74), width=1)
WCOLW = (W - 2 * M - 30) // 2
for i, item in enumerate(WIRE):
    col, row = i % 2, i // 2
    x = M + 10 + col * (WCOLW + 10)
    y = WY + 34 + row * ((WH - 40) // 4)
    d.polygon([(x, y + 2), (x, y + 10), (x + 7, y + 6)], fill=(250, 210, 60))
    fnt, txt = one_line(d, item, SANS, 10, 8, WCOLW - 16)
    d.text((x + 15, y + 1), txt, font=fnt, fill=WIRE_TX)

# --- colophon
col = "Set in Noto Serif & Noto Sans \u00b7 Drawn panel by panel with PIL \u00b7 All figures as reported on the day"
cf = F(SANS, 9)
cw = d.textlength(col, font=cf)
d.text(((W - cw) / 2, H - 12), col, font=cf, fill=MUTE)

img.save(OUT, optimize=True)
print(f"STORY_COUNT={len(STORIES)}")
