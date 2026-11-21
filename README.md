[![make.fun bounty](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![make.fun rank](https://make.fun/badge/news-image-20261121/Sandi207/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![make.fun reward](https://make.fun/badge/news-image-20261121/Sandi207/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

# The World Today — Saturday 21 November 2026

A single 1024 × 1024 RGB PNG newspaper front page for the make.fun bounty. Warm paper, dark ink, large headlines and original flat geometric illustrations present only the supplied verified facts. The lead includes a schematic Poland map with the three named debris locations. Five further stories occupy two rows; five one-line briefs complete the page.

The six stories:

- **Missiles fall on Poland.** During Russia’s massive barrage on Ukraine, Russian missiles and a suspected drone came down in NATO-member Poland. A Kh-101 landed about 50 km inside Poland; debris was found near Nowy Lipowiec, Molodycz and Rudnik nad Sanem. Donald Tusk called it a deliberate provocation; NATO called it a grave violation of allied airspace. Polish and NATO jets scrambled, Patriot air defences activated, and no one was hurt.
- **Wall Street in correction.** Friday’s S&P 500 fell 3.7% to 6,910 and the Dow fell 950 points; both were more than 10% below their peaks. The Nasdaq fell 5.3%, in its worst week since March 2020, erasing its 2026 gains. Anthropic fell 9.1% to $88.30, barely above its $83 IPO price a day after its record debut; Nvidia fell 14%. Tech stocks lost $4 trillion in a week.
- **Trump joins Europe on Ukraine.** After the trilateral Shenzhen summit with Xi Jinping and Vladimir Putin, Trump dialled into a meeting of European allies to discuss Ukraine. Europe wants a seat at the table in any talks. France called for a United Nations Security Council meeting over the strikes on Kyiv.
- **Denmark foils a “Russian” murder plot.** Denmark charged two Danes with being recruited by Russia to assassinate a US-Ukrainian rapper. Its PET security service says it thwarted the plot.
- **UK and EU sign new deals.** Andy Burnham signed three agreements with EU leaders in Brussels, covering food trade, carbon markets and youth mobility: the closest UK-EU ties since Brexit.
- **Saudi intercepts Houthi missiles.** The Saudi-led coalition destroyed three Houthi ballistic missiles fired at Riyadh; debris fell on the capital. Saudi jets then struck Hodeidah as the Gulf war widens.

The briefs cover Cyclone Dana clean-up on India’s Odisha coast and more than 300,000 evacuations; the EU’s record €7.9 billion single financial aid payment to Ukraine; Trump’s threat to ban overseas AI data centre construction by US firms; more declassified US UFO footage from the Middle East; and New York mayor-elect Mamdani’s plan to close Rikers Island jail by 2032.

The image is drawn with Pillow and the installed DejaVu fonts, without photographs, downloaded assets, generated bitmap assets, randomness, clock reads or network access. Main captions are 20–22 px at the final scale; footer briefs are 18 px. Everything is drawn at 2048 × 2048 and downsampled once with Lanczos.

Run offline with Node 22 using the plain CommonJS entrypoint (no dependencies):

```sh
node main.ts
```

The default destination is `/output/entry.png`. Override it with `MAKEFUN_OUTPUT_DIR` and verify the copy:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/news-image-20261121-check node main.ts
cmp entry.png /tmp/news-image-20261121-check/entry.png
```

Re-render with Python 3, Pillow and `/usr/share/fonts/truetype/dejavu/`:

```sh
python3 render.py
```

The default output directory is the directory containing `render.py`; an optional positional argument selects another directory. Verify deterministic output and install the verified PNG:

```sh
python3 render.py out1
python3 render.py out2
sha256sum out1/entry.png out2/entry.png
cmp out1/entry.png out2/entry.png
cp out1/entry.png entry.png
python3 -c "from PIL import Image; from pathlib import Path; p = Path('entry.png'); im = Image.open(p); assert im.size == (1024, 1024) and im.mode == 'RGB' and p.stat().st_size <= 1048576; print(im.size, im.mode, p.stat().st_size)"
```

The two render hashes must be identical. The PNG is optimized and at most 1 MiB. Code, image and documentation are available under the MIT license; see [LICENSE](LICENSE).
