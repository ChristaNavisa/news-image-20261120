# The World in One Day — Friday 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/ChristaNavisa/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/ChristaNavisa/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

A one-page broadsheet that sums up the world news of **Friday 20 November 2026** — all of the day's news on a single 1024×1024 page.

## What is on the page

- **Masthead** — "THE WORLD IN ONE DAY", dated Friday 20 November 2026.
- **Stat strip** — 8 numbers from the day: 48 stories, 5 regions, 4 hero pictures, 1 world map, 400+ drones at Kyiv, S&P 500 −3.7%, Nvidia −14%, Peru quake 6.7.
- **Four hero pictures, drawn in code** — the Shenzhen summit (Trump, Xi and Putin at one table under three flags), Kyiv under fire at night, the AI stock rout as a plunging chart, and the ICJ verdict in The Hague.
- **World map** — schematic continents with 12 marked cities, from New York to Tokyo, plus a region breakdown and an explicit **DATE CHECK** box.
- **The day in full** — 48 real stories from five regions (Europe 13, Americas 13, Asia 9, Middle East 7, Africa 6), each with a headline and a one-line summary.

## How to run

```sh
python3 main.py
```

The program writes `entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output`). It is fully procedural and deterministic: fixed seeds, no network, no clock, no external files. Running it twice produces a byte-identical PNG.

Pillow is used when installed; if it is missing, a pure standard-library renderer (raw RGB buffer + zlib PNG writer + built-in bitmap font) draws the same broadsheet, so the entry still produces a valid image in a bare sandbox.

## Verification

```sh
mkdir -p /tmp/r5a /tmp/r5b
MAKEFUN_OUTPUT_DIR=/tmp/r5a python3 main.py
MAKEFUN_OUTPUT_DIR=/tmp/r5b python3 main.py
sha256sum /tmp/r5a/entry.png /tmp/r5b/entry.png   # identical
python3 -c "from PIL import Image; im = Image.open('/tmp/r5a/entry.png'); print(im.size, im.format)"
```

Both runs exit 0, produce byte-identical PNGs, and the image is 1024×1024 and under 1 MiB. The masthead carries the date "FRIDAY 20 NOVEMBER 2026", and the story list holds 48 stories.

## Entry

- Competition: [Gambar Berita 20 Nov](https://make.fun/bounty/news-image-20261120)
- Round: 5 — broadsheet, denser than round 3's winning format (48 stories, 4 hero pictures, richer map, more stat numbers).
