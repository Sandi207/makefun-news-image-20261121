#!/usr/bin/env python3
"""Render a deterministic newspaper front page from the supplied news facts.

All geometry is original and drawn with Pillow at 2048 x 2048. Coordinates
and font sizes below use the final 1024-pixel scale for easier review.
There are no external assets, random values, network requests or clock reads.
"""

import argparse
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE = 1024
SCALE = 2
FONT_DIRECTORY = Path("/usr/share/fonts/truetype/dejavu")
PAPER = "#F6F1E7"
INK = "#202729"
MUTED = "#59635F"
RULE = "#B6B4A8"
RED = "#B13D35"
TEAL = "#345E59"
BLUE = "#315C73"
GOLD = "#C29A52"
PALE_TEAL = "#DCE5DE"
PALE_GOLD = "#EDE2CB"
FOOTER = "#EEE5D6"

MASTHEAD = "THE WORLD TODAY"
DATE = "SATURDAY, 21 NOVEMBER 2026"
LEAD_HEADLINE = "MISSILES FALL ON POLAND"
LEAD_DECK = (
    "Russian missiles and a suspected drone fell during Russia’s massive barrage on Ukraine."
)
LEAD_LINES = (
    "Kh-101 landed about 50 km inside Poland.",
    "Donald Tusk: “deliberate provocation.”",
    "NATO: “grave violation of allied airspace.”",
    "Jets scrambled; Patriot defences activated.",
)
STORIES = (
    {
        "x": 32,
        "width": 466,
        "y": 479,
        "headline_size": 29,
        "headline": ("WALL STREET IN", "CORRECTION"),
        "caption_y": 549,
        "caption": (
            "S&P 500 −3.7% to 6,910; Dow −950 points.",
            "Nasdaq −5.3%; tech lost $4 trillion in a week.",
        ),
    },
    {
        "x": 526,
        "width": 466,
        "y": 479,
        "headline_size": 29,
        "headline": ("TRUMP JOINS EUROPE", "ON UKRAINE"),
        "caption_y": 549,
        "caption": (
            "After meeting Xi Jinping and Vladimir Putin,",
            "Trump joins European allies on Ukraine.",
        ),
    },
    {
        "x": 32,
        "width": 300,
        "y": 713,
        "headline_size": 26,
        "headline": ("DENMARK FOILS", "“RUSSIAN” PLOT"),
        "caption_y": 777,
        "caption": (
            "Two Danes charged in plot",
            "to kill US-Ukrainian rapper.",
        ),
    },
    {
        "x": 356,
        "width": 300,
        "y": 713,
        "headline_size": 26,
        "headline": ("UK & EU SIGN", "NEW DEALS"),
        "caption_y": 777,
        "caption": (
            "Andy Burnham signs deals:",
            "food, carbon, youth mobility.",
        ),
    },
    {
        "x": 680,
        "width": 312,
        "y": 713,
        "headline_size": 26,
        "headline": ("SAUDI INTERCEPTS", "HOUTHI MISSILES"),
        "caption_y": 777,
        "caption": (
            "3 missiles aimed at Riyadh;",
            "Saudi jets strike Hodeidah.",
        ),
    },
)
BRIEFS = (
    (
        "CYCLONE DANA",
        "Clean-up on India’s Odisha coast after landfall; over 300,000 evacuated.",
    ),
    (
        "EU AID",
        "€7.9 billion sent to Ukraine: largest-ever single financial aid payment.",
    ),
    (
        "AI",
        "Trump threatens to ban US firms from building AI data centres overseas.",
    ),
    ("UFOs", "US declassifies more footage filmed in the Middle East."),
    (
        "NEW YORK",
        "Mayor-elect Mamdani plans to close Rikers Island jail by 2032.",
    ),
)


def px(value):
    return round(value * SCALE)


@lru_cache(maxsize=None)
def font(size, weight="regular"):
    filenames = {
        "regular": "DejaVuSans.ttf",
        "bold": "DejaVuSans-Bold.ttf",
        "serif": "DejaVuSerif-Bold.ttf",
    }
    return ImageFont.truetype(str(FONT_DIRECTORY / filenames[weight]), px(size))


class Page:
    def __init__(self):
        self.image = Image.new("RGB", (px(SIZE), px(SIZE)), PAPER)
        self.draw = ImageDraw.Draw(self.image)

    def rectangle(self, bounds, fill, outline=None, width=1):
        self.draw.rectangle(
            tuple(px(n) for n in bounds), fill=fill, outline=outline, width=px(width)
        )

    def polygon(self, points, fill, outline=None, width=1):
        scaled = [(px(x), px(y)) for x, y in points]
        self.draw.polygon(scaled, fill=fill)
        if outline:
            self.draw.line(scaled + [scaled[0]], fill=outline, width=px(width), joint="curve")

    def line(self, points, fill=INK, width=1):
        self.draw.line(
            [(px(x), px(y)) for x, y in points], fill=fill, width=px(width), joint="curve"
        )

    def ellipse(self, bounds, fill=None, outline=None, width=1):
        self.draw.ellipse(
            tuple(px(n) for n in bounds), fill=fill, outline=outline, width=px(width)
        )

    def arc(self, bounds, start, end, fill=INK, width=1):
        self.draw.arc(
            tuple(px(n) for n in bounds), start, end, fill=fill, width=px(width)
        )

    def text(self, x, y, value, size, weight="regular", fill=INK, max_width=None):
        face = font(size, weight)
        length = face.getlength(value) / SCALE
        if max_width is not None:
            assert length <= max_width, (value, length, max_width)
        bbox = self.draw.textbbox((px(x), px(y)), value, font=face, anchor="lt")
        assert 0 <= bbox[0] and bbox[2] <= px(SIZE), (value, bbox)
        assert 0 <= bbox[1] and bbox[3] <= px(SIZE), (value, bbox)
        self.draw.text((px(x), px(y)), value, font=face, fill=fill, anchor="lt")
        return length

    def centered_text(self, center, y, value, size, weight="regular", fill=INK):
        length = font(size, weight).getlength(value) / SCALE
        return self.text(center - length / 2, y, value, size, weight, fill)

    def tracked_text(self, center, y, value, size, tracking, fill=INK):
        face = font(size, "bold")
        length = sum(face.getlength(c) / SCALE for c in value) + tracking * (len(value) - 1)
        x = center - length / 2
        # All characters share a baseline, including the date's comma.
        baseline = px(y) - face.getbbox("H", anchor="ls")[1]
        for character in value:
            self.draw.text((px(x), baseline), character, font=face, fill=fill, anchor="ls")
            x += face.getlength(character) / SCALE + tracking


def transform(points, cx, cy, angle):
    cosine, sine = math.cos(angle), math.sin(angle)
    return [(cx + x * cosine - y * sine, cy + x * sine + y * cosine) for x, y in points]


def missile(page, cx, cy, length, angle, fill=RED, outline=None):
    points = [
        (0.55, 0), (0.30, -0.11), (-0.33, -0.11), (-0.50, -0.25),
        (-0.48, -0.05), (-0.58, 0), (-0.48, 0.05), (-0.50, 0.25),
        (-0.33, 0.11), (0.30, 0.11),
    ]
    page.polygon(
        transform([(x * length, y * length) for x, y in points], cx, cy, angle),
        fill, outline, 1.2,
    )


def arrowhead(page, tip, direction, length=9, width=4, fill=RED):
    angle = math.atan2(direction[1], direction[0])
    page.polygon(transform([(0, 0), (-length, -width), (-length, width)], *tip, angle), fill)


def draw_lead(page):
    page.text(32, 165, "NATO AIRSPACE", 14, "bold", RED)
    page.line([(168, 172), (188, 172)], RULE, 1)
    page.text(201, 165, "RUSSIA’S BARRAGE ON UKRAINE", 14, "bold", MUTED)
    page.text(32, 185, LEAD_HEADLINE, 60, "bold", max_width=960)
    page.text(32, 245, LEAD_DECK, 21, max_width=960)

    # A deliberately schematic, original outline of Poland; no imported map data.
    page.rectangle((32, 279, 452, 452), "#EFEADF")
    ukraine = [
        (247, 305), (278, 312), (304, 305), (326, 317), (362, 306),
        (389, 315), (441, 306), (441, 442), (270, 442), (252, 422), (258, 396),
    ]
    page.polygon(ukraine, PALE_GOLD)
    poland = [
        (59, 311), (80, 301), (111, 289), (132, 288), (140, 294),
        (167, 292), (185, 298), (231, 298), (241, 315), (239, 336),
        (246, 352), (240, 369), (245, 389), (254, 405), (244, 421),
        (250, 434), (232, 438), (217, 430), (202, 434), (190, 429),
        (179, 431), (170, 424), (155, 426), (143, 419), (133, 422),
        (122, 413), (107, 413), (95, 402), (80, 403), (72, 394),
        (61, 392), (63, 376), (55, 366), (59, 351), (53, 337), (61, 326),
    ]
    page.polygon(poland, PALE_TEAL, TEAL, 1.8)
    page.text(95, 320, "POLAND", 22, "bold", TEAL)
    page.text(99, 349, "NATO MEMBER", 12.5, "bold", TEAL)
    page.text(340, 288, "UKRAINE", 16, "bold", MUTED)

    # Curved incoming trajectory, sampled at a fixed number of points.
    start, control, end = (427, 313), (292, 285), (240, 393)
    trajectory = []
    for step in range(49):
        t = step / 48
        trajectory.append((
            (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0] + t ** 2 * end[0],
            (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1] + t ** 2 * end[1],
        ))
    page.line(trajectory, RED, 2.5)
    arrowhead(page, end, (end[0] - control[0], end[1] - control[1]), 10, 4.5)
    missile(page, 348, 315, 39, math.radians(168), PAPER, RED)

    impacts = (
        ((226, 376), ((254, 356), (271, 356)), "Rudnik nad Sanem", 348),
        ((241, 394), ((260, 391), (271, 391)), "Nowy Lipowiec", 383),
        ((237, 414), ((258, 425), (271, 425)), "Molodycz", 417),
    )
    for (x, y), connector, label, text_y in impacts:
        page.line([(x, y), *connector], MUTED, 1)
        page.ellipse((x - 6, y - 6, x + 6, y + 6), PAPER, RED, 2)
        page.ellipse((x - 2, y - 2, x + 2, y + 2), RED)
        page.text(278, text_y, label, 18, max_width=174)
    page.text(44, 438, "SCHEMATIC MAP", 10.5, "bold", MUTED)

    page.line([(468, 283), (468, 451)], RULE, 1)
    for index, value in enumerate(LEAD_LINES):
        page.text(487, 284 + index * 32, value, 22, max_width=505)
    page.rectangle((487, 415, 720, 447), TEAL)
    page.text(500, 423, "No one was hurt.", 20, "bold", PAPER, max_width=207)


def draw_stock_market(page):
    page.text(32, 613, "FRIDAY", 13.5, "bold", RED)
    for y in (638, 652, 673):
        page.line([(34, y), (204, y)], "#D9D6CB", 0.7)
    page.line([(34, 633), (34, 674), (205, 674)], MUTED, 1)
    points = [(37, 636), (63, 641), (87, 638), (120, 657), (148, 651), (193, 672)]
    page.line(points, RED, 4)
    arrowhead(page, points[-1], (45, 21), 11, 5)
    page.text(32, 682, ">10% BELOW PEAKS", 12, "bold", MUTED)
    page.text(230, 617, "Anthropic −9.1% · $88.30", 18, "bold", RED, max_width=268)
    page.text(230, 649, "Nvidia −14%", 22, "bold", RED, max_width=268)


def person(page, cx, cy, radius=5, fill=INK):
    page.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill)
    page.polygon([
        (cx - radius * 1.55, cy + radius * 2.8),
        (cx - radius * 1.1, cy + radius * 1.25),
        (cx + radius * 1.1, cy + radius * 1.25),
        (cx + radius * 1.55, cy + radius * 2.8),
    ], fill)


def draw_diplomacy(page):
    page.text(526, 613, "SHENZHEN", 15, "bold", MUTED)
    page.rectangle((526, 634, 632, 668), PALE_TEAL, TEAL, 1.5)
    for x in (545, 579, 613):
        person(page, x, 644, 4.4, TEAL)
    page.line([(566, 672), (593, 672)], TEAL, 2)
    page.line([(578, 669), (578, 672)], TEAL, 2)

    page.line([(642, 651), (683, 651)], RED, 1.8)
    arrowhead(page, (683, 651), (1, 0), 7, 3)
    # A small handset makes the remote call explicit.
    page.polygon([
        (650, 632), (653, 628), (658, 632), (657, 636), (664, 642),
        (667, 640), (671, 644), (668, 648), (662, 647), (652, 638),
    ], RED)

    page.ellipse((693, 640, 749, 664), PALE_TEAL, TEAL, 1.5)
    person(page, 721, 627, 4.5, TEAL)
    person(page, 695, 640, 4.5, TEAL)
    person(page, 746, 640, 4.5, TEAL)
    page.line([(707, 663), (703, 672), (739, 672), (735, 663)], TEAL, 1.4)
    page.text(766, 618, "Europe seeks a seat", 17, max_width=226)
    page.text(766, 644, "at the table in talks.", 17, max_width=226)
    page.text(
        526, 679, "France calls for UN Security Council meeting.", 16, max_width=466
    )


def shield(page, cx, top, width, height, fill=TEAL, outline=None):
    points = [
        (cx - width / 2, top), (cx + width / 2, top),
        (cx + width / 2, top + height * 0.48),
        (cx + width * 0.34, top + height * 0.73), (cx, top + height),
        (cx - width * 0.34, top + height * 0.73),
        (cx - width / 2, top + height * 0.48),
    ]
    page.polygon(points, fill, outline, 1.5)


def draw_denmark(page):
    shield(page, 58, 833, 45, 47, TEAL)
    page.line([(47, 854), (55, 862), (70, 845)], PAPER, 3)
    page.text(94, 834, "PET", 20, "bold", TEAL)
    page.text(94, 860, "Plot thwarted", 16, fill=MUTED, max_width=129)
    person(page, 250, 844, 6, INK)
    person(page, 276, 844, 6, INK)
    # A crossed-out microphone represents the thwarted threat to the rapper.
    page.rectangle((307, 838, 316, 853), RED)
    page.ellipse((307, 834, 316, 843), RED)
    page.arc((303, 837, 320, 859), 0, 180, RED, 1.5)
    page.line([(312, 859), (312, 870)], RED, 1.5)
    page.line([(304, 871), (320, 871)], RED, 1.5)
    page.line([(299, 837), (323, 863)], TEAL, 2)


def uk_flag(page, x, y, width, height):
    # Construct the Union Flag entirely from flat, clipped rectangles and lines.
    flag = Image.new("RGB", (px(width), px(height)), BLUE)
    draw = ImageDraw.Draw(flag)
    w, h = flag.size
    draw.line([(0, 0), (w, h)], fill=PAPER, width=px(8))
    draw.line([(0, h), (w, 0)], fill=PAPER, width=px(8))
    draw.line([(0, 0), (w, h)], fill=RED, width=px(2.5))
    draw.line([(0, h), (w, 0)], fill=RED, width=px(2.5))
    draw.rectangle((w // 2 - px(6), 0, w // 2 + px(6), h), fill=PAPER)
    draw.rectangle((0, h // 2 - px(5), w, h // 2 + px(5)), fill=PAPER)
    draw.rectangle((w // 2 - px(3), 0, w // 2 + px(3), h), fill=RED)
    draw.rectangle((0, h // 2 - px(2.5), w, h // 2 + px(2.5)), fill=RED)
    page.image.paste(flag, (px(x), px(y)))


def eu_flag(page, x, y, width, height):
    page.rectangle((x, y, x + width, y + height), BLUE)
    cx, cy = x + width / 2, y + height / 2
    orbit = height * 0.30
    for index in range(12):
        angle = -math.pi / 2 + index * math.pi / 6
        sx, sy = cx + orbit * math.cos(angle), cy + orbit * math.sin(angle)
        star = []
        for vertex in range(10):
            theta = -math.pi / 2 + vertex * math.pi / 5
            radius = 1.6 if vertex % 2 == 0 else 0.7
            star.append((sx + radius * math.cos(theta), sy + radius * math.sin(theta)))
        page.polygon(star, GOLD)


def agreement(page, x, y):
    page.polygon([
        (x, y), (x + 24, y), (x + 32, y + 8),
        (x + 32, y + 44), (x, y + 44),
    ], PAPER, TEAL, 1.3)
    page.polygon([(x + 24, y), (x + 24, y + 8), (x + 32, y + 8)], PALE_TEAL)
    for offset in (15, 21):
        page.line([(x + 6, y + offset), (x + 26, y + offset)], RULE, 1)
    page.line([(x + 10, y + 33), (x + 14, y + 37), (x + 24, y + 28)], TEAL, 2)


def draw_uk_eu(page):
    uk_flag(page, 356, 847, 51, 30)
    eu_flag(page, 415, 847, 51, 30)
    page.text(356, 832, "BRUSSELS", 12.5, "bold", MUTED)
    for x, y in ((492, 834), (533, 838), (574, 834)):
        agreement(page, x, y)
    page.line([(474, 861), (487, 861)], TEAL, 1.5)
    arrowhead(page, (487, 861), (1, 0), 5, 2.5, TEAL)
    page.text(618, 846, "3", 28, "bold", TEAL)


def draw_saudi(page):
    for x, y in ((693, 836), (709, 846), (692, 861)):
        missile(page, x, y, 22, math.radians(18))
    shield(page, 754, 833, 37, 47, PALE_GOLD, TEAL)
    page.line([(744, 851), (752, 860), (765, 844)], TEAL, 2.4)
    # Generic flat city silhouettes; these are symbols, not imported buildings.
    for bounds in (
        (796, 851, 810, 877), (814, 843, 831, 877),
        (837, 836, 852, 877), (858, 855, 872, 877),
    ):
        page.rectangle(bounds, TEAL)
    page.line([(844, 833), (844, 824)], TEAL, 1.5)
    page.text(889, 835, "RIYADH", 17, "bold", TEAL, max_width=103)
    page.text(889, 861, "3 stopped", 17, max_width=103)


def draw_briefs(page):
    page.rectangle((0, 893, SIZE, SIZE), FOOTER)
    page.line([(32, 893), (992, 893)], INK, 1.5)
    page.text(32, 903, "IN BRIEF", 12.5, "bold", RED)
    for index, (label, value) in enumerate(BRIEFS):
        y = 920 + index * 20
        label_width = page.text(32, y, label, 18, "bold")
        bullet_x = 32 + label_width + 10
        page.ellipse((bullet_x, y + 5, bullet_x + 4, y + 9), RED)
        body_x = bullet_x + 14
        page.text(body_x, y, value, 18, max_width=992 - body_x)


def render():
    page = Page()
    page.centered_text(512, 22, MASTHEAD, 83, "serif")
    page.tracked_text(512, 110, DATE, 21, 1.5)
    page.line([(32, 146), (992, 146)], INK, 3)
    draw_lead(page)
    page.line([(32, 460), (992, 460)], INK, 1.5)

    for story in STORIES:
        headline = " ".join(story["headline"])
        assert len(headline.split()) <= 6, headline
        assert len(story["caption"]) == 2
        line_height = 34 if story["y"] == 479 else 31
        for index, value in enumerate(story["headline"]):
            page.text(
                story["x"], story["y"] + index * line_height,
                value, story["headline_size"], "bold", max_width=story["width"],
            )
        for index, value in enumerate(story["caption"]):
            page.text(
                story["x"], story["caption_y"] + index * 26,
                value, 20, max_width=story["width"],
            )

    page.line([(512, 478), (512, 690)], RULE, 1)
    page.line([(32, 701), (992, 701)], RULE, 1)
    page.line([(344, 712), (344, 881)], RULE, 1)
    page.line([(668, 712), (668, 881)], RULE, 1)
    draw_stock_market(page)
    draw_diplomacy(page)
    draw_denmark(page)
    draw_uk_eu(page)
    draw_saudi(page)
    draw_briefs(page)

    # One and only one downsample, after every shape and glyph has been drawn.
    return page.image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output_directory", nargs="?", type=Path,
        default=Path(__file__).resolve().parent,
        help="destination directory (default: directory containing render.py)",
    )
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    destination = args.output_directory / "entry.png"
    image = render()
    assert image.size == (1024, 1024) and image.mode == "RGB"
    image.save(destination, format="PNG", optimize=True, compress_level=9)
    size = destination.stat().st_size
    assert size <= 1024 * 1024, f"PNG exceeds 1 MiB: {size} bytes"
    print(f"Wrote {destination} ({size} bytes; 1024 x 1024 RGB)")


if __name__ == "__main__":
    main()
