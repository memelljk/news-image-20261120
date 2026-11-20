# The Day in Full — 50 verified stories, 3 illustrated heroes, 6 sections, numbers band, sport and late wire: 20 November 2026 in one page

[![Competition](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/memelljk/news-image-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/memelljk/news-image-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

![The Day in Full — front page for 20 November 2026](screenshot.png)

A complete broadsheet front page for **Friday, 20 November 2026**, drawn panel
by panel with PIL — no photos, no templates. An ink-black serif masthead sits
over three large illustrated hero panels (the ICJ genocide ruling drawn as a
courthouse with scales of justice; the Shenzhen three-way summit as three
flags over a skyline; Anthropic's record IPO as a rising NASDAQ chart with a
ringing bell), followed by four colour-coded section grids with pictogram
thumbnails, a scoreboard-style Sport & Play strip, a By the Numbers band of
eight stat tiles, and a black Late Wire ticker band at the foot of the page.

## Story count — 50

The page is rendered from one master list in `dayfront.py`, which prints
`STORY_COUNT=50` from the length of that list:

| Part of the page | Stories |
| --- | --- |
| Hero panels | 3 |
| World | 8 |
| Money & Tech | 7 |
| Science & Planet | 6 |
| Society & Culture | 7 |
| Sport & Play strip | 5 |
| Late Wire | 8 |
| By the Numbers (standalone stat stories) | 6 |
| **Total** | **50** |

The numbers band displays eight tiles: the six counted stat stories plus two
highlights drawn from the hero and World stories ($97.17 Anthropic close and
the 8 killed in Kyiv).

## How to run

```sh
python3 dayfront.py   # writes entry.png (1024×1024, ≤ 1 MiB), prints STORY_COUNT=50
node main.ts          # renders via dayfront.py, validates the PNG, copies it to /output
MAKEFUN_OUTPUT_DIR=out node main.ts   # same, but copies to ./out outside the grader
```

`main.ts` uses only the Node 22 standard library. If python3/Pillow is not
available it falls back to the committed `entry.png`, which is byte-identical
because the renderer is deterministic (fixed data, no clock, no network, no
randomness — two consecutive runs produce the same sha256).

## Fonts

Set in **Noto Serif** (masthead, headlines, numerals) and **Noto Sans**
(kickers, decks, tickers) from the system font collection, with DejaVu Serif /
DejaVu Sans as fallbacks. Every text block is measured with PIL's
`textlength` and shrunk or wrapped to fit its panel — nothing overflows.
