[![News Image 20 Nov 2026](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/ChristaNavisa/news-image-20261120/rank.svg)](https://make.fun/c/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/ChristaNavisa/news-image-20261120/reward.svg)](https://make.fun/c/news-image-20261120)

# The World in One Day — Friday 20 November 2026

One image that sums up the world's news of Friday 20 November 2026:
a broadsheet front page — masthead, lead story, three pictures,
48 real stories from that day, a world map of 12 cities, a strip of
8 figures, and a date check. Every story happened, or was first
reported, on 20 November 2026.

Lead story: Russia fires 400+ drones and 110 missiles at Ukraine;
three bridges over the Dnipro hit, eight killed, two missiles land
in Poland. Also inside: the UN court finds Myanmar committed
genocide against the Rohingya, the AI sell-off pushes the S&P 500
down 3.7% into correction, a magnitude 6.7 earthquake in Peru, the
Trump–Xi–Putin meeting in Shenzhen, and the war over the Strait
of Hormuz.

## How it is made

`main.py` draws the whole page itself with the Python standard
library only — its own PNG encoder (zlib + struct) and its own
5×7 bitmap font. No Pillow, no other library, no network, no file
reads, so the image the grader's sandbox produces is byte-identical
to a local run. Two runs always write the same bytes.

Run it:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes `out/entry.png` (1024×1024, under 1 MiB).

## Entry

- Competition: [Sum up 20 November's world news in one image](https://make.fun/c/news-image-20261120)
- Round 6 — standard-library-only redraw: the previous round's
  Pillow path never ran in the grader's sandbox, so this round
  draws everything with stdlib code alone.

## License

MIT — see [LICENSE](LICENSE).
