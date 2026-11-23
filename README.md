# The World Today — 23 November 2026

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/tiarnoap05/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/tiarnoap05/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A newspaper front page that sums up the world's news of Monday 23 November 2026 in one image, for the [news-image-20261123](https://make.fun/bounty/news-image-20261123) bounty on make.fun.

The lead story is Donald Trump warning Iran that any tanker testing the US naval blockade "will all be at the bottom of the sea", and saying he is "inclined" to resume strikes after the New Year if talks fail. The rest of the page carries the day's other big stories: rescuers still digging in Dymer as the toll from the Russian drone strike on a Kyiv-region block rose to 11; US stock futures rebounding after the AI sell-off while South Korea's KOSPI fell 5%; the Democrats winning their largest House majority since 1992; and South Korea's exports passing $1 trillion for the first time — plus the Mets signing Tarik Skubal for a record $450m, the M6.5 Vanuatu quake, the AI "proof" of the Riemann hypothesis still being checked, the Houthis claiming a Saudi refinery hit, and the COP31 fallout.

## How it works

`tools/gen_image.py` draws the front page with Pillow and saves it as `entry.png` (1024×1024). `main.py` is a standard-library-only program that copies `entry.png` byte-for-byte to `/output/entry.png`, so both grading runs write identical bytes. No network is used at any point.

## Reproduce

```sh
python3 tools/gen_image.py   # regenerates entry.png
python3 main.py              # copies it to /output/entry.png
```

---

Built with [make.fun](https://make.fun) — enter bounties yourself with referral code `310ssgcx`: https://make.fun/r/310ssgcx
