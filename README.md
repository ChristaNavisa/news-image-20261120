# The World in One Day — 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/ChristaNavisa/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/ChristaNavisa/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A front page summing up Friday 20 November 2026 in a single image:
**12 drawn pictures and 36 stories**, built for the
[make.fun bounty](https://make.fun/bounty/news-image-20261120).

## What the picture shows

- **12 illustrated story tiles** — every big story of the day gets its
  own drawing and headline: the Russian missile strike on Kyiv's Dnipro
  bridges (8 dead), Cyclone Akvan's landfall near Gopalpur (300,000
  evacuated), GTA VI's record day one (32.5m copies, $3.79bn), COP31 in
  overtime with "fossil fuels" dropped from the draft, the airspace
  breach into Poland (2 missiles, 1 drone, NATO jets up), the ICJ ruling
  that Myanmar committed genocide against the Rohingya, the US–China–
  Russia joint declaration at Shenzhen, the Houthi strike on Riyadh's
  PIF Tower, markets sliding (Nikkei −5%, S&P down a sixth day),
  Anthropic's shares sliding on day two after its record IPO, Kenya's
  42-day Ebola-free countdown, and an oil tanker burning in Hormuz.
- **24 numbered briefs** below the pictures — the EU–UK summit, the
  100,000-a-year youth mobility scheme, the US Senate's 51–48 Iran
  war-powers vote, the Kerch Bridge reopening, Cyclone Xavier, the
  Saudi interceptions, Iraq, Sri Lanka's rate rise, the cost-of-living
  strikes in 25+ countries, Haiti, the n0n data leak, and more.
- **The date is the masthead**: "FRIDAY 20 NOVEMBER 2026", with every
  story verified as having happened or first been reported that day.

## How it is made

The image is drawn by code from a hand-built list of the day's stories,
researched from 20 November 2026 reporting. The finished image ships as
`entry.png`; `main.py` (Python 3.13, standard library only) copies it to
the output directory, deterministically — two runs write identical bytes,
verified by sha256.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

## License

MIT — see [LICENSE](LICENSE).
