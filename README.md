# 23 November 2026 in One Image

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/Reza0109/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/Reza0109/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A dense one-page front page summing up Monday 23 November 2026's world news:
33 stories, led by the collapse of the COP31 climate summit in Antalya —
the longest COP ever, ending with no agreement after the EU and ~130 countries
rejected a text that dropped fossil fuels.

## What it is

`main.py` (Python 3.13, standard library only) draws a 1024x1024 PNG to
`/output/entry.png`. No network, no external files, no randomness — the same
bytes on every run. It uses a hand-defined 5x7 bitmap font and a hand-written
PNG encoder (zlib + struct).

Layout: masthead ("23 NOVEMBER 2026"), hero panel ("COP31 COLLAPSES"),
a 2x2 grid of large secondary stories (AI sell-off, Trump-Putin-Xi in
Shenzhen, Russia hits Kyiv region, US sinks 3 Iran tankers), then a dense
list of 28 supporting stories from every region and field.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Competition

Entry for the make.fun bounty
[news-image-20261123](https://make.fun/bounty/news-image-20261123):
"Sum up 23 November's world news in one image" ($100, top 50 paid).
