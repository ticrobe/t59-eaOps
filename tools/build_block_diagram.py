#!/usr/bin/env python3
"""Draw the eaOps block diagram (dist/eaOps.png) from content/ and VERSION.

    python tools/build_block_diagram.py --updated 9/17/2026
    python tools/build_block_diagram.py --out /tmp/preview.png --scale 2

Ops, counts and version are read from the repo. Each Op's emoji is set by its
position in EMOJI below. Needs Pillow plus a colour-emoji font (Apple Color Emoji on macOS, Noto Color
Emoji on Linux). It refuses to overwrite an existing PNG unless --force is given.
"""
import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_html  # noqa: E402  (reuses the YAML loader, VERSION and date helpers)

W, H = 1280, 1120                       # canvas in px at --scale 1
CENTER = (640, 580)
R_CENTER, R_RING, R_OP = 214, 289, 94   # centre circle, ring radius, Op circle
NAVY, RED, GREY, ACCENT = (16, 16, 42), (214, 41, 62), (153, 153, 153), (91, 107, 214)
RING_FILL, RING_HATCH = (238, 240, 251), (211, 215, 247)
CENTER_FILL, CENTER_HATCH = (223, 226, 247), (198, 203, 244)
SS = 3                                  # supersampling, for smooth edges
LABEL_PX, LABEL_MAX_W = 16, 105         # Op label font size and wrap width
PAGE_NAME = "eaOps.html"

# One emoji per Op, by position (Op 1 first, running clockwise from the top).
EMOJI = ["💼", "🤝", "🔬", "⚙️", "🛡️", "💻", "🔄", "🤖", "🔮", "✈️"]
CENTER_EMOJI = "👤"

BOLD = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]
BOLD_ITALIC = ["/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
               "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf", "C:/Windows/Fonts/arialbi.ttf"]
EMOJI_FONTS = ["/System/Library/Fonts/Apple Color Emoji.ttc",
               "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", "C:/Windows/Fonts/seguiemj.ttf"]


def find_font(candidates, what):
    for path in candidates:
        if Path(path).is_file():
            return path
    sys.exit(f"error: no {what} font found (tried: {', '.join(candidates)})")


class Painter:
    def __init__(self, scale):
        self.k = scale * SS
        self.canvas = Image.new("RGBA", (W * self.k, H * self.k), (255, 255, 255, 255))
        self.draw = ImageDraw.Draw(self.canvas)
        self.fonts = {}
        self.emoji_path = find_font(EMOJI_FONTS, "colour emoji")

    def font(self, style, px):
        key = (style, px)
        if key not in self.fonts:
            path = find_font(BOLD_ITALIC if style == "bi" else BOLD, "bold" + (" italic" if style == "bi" else ""))
            self.fonts[key] = ImageFont.truetype(path, round(px * self.k))
        return self.fonts[key]

    def _box(self, cx, cy, r):
        return round((cx - r) * self.k), round((cy - r) * self.k), round(2 * r * self.k)

    def fill_circle(self, cx, cy, r, fill, hatch):
        """Opaque flat circle with a 45-degree hatch. The hatch is aligned to the page,
        so overlapping circles show one seamless pattern."""
        ox, oy, d = self._box(cx, cy, r)
        period = round(14 * self.k)
        mask = Image.new("L", (d, d), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, d - 1, d - 1), fill=255)
        strokes = Image.new("L", (d, d), 0)
        stroke = ImageDraw.Draw(strokes)
        for x in range(-((ox - oy) % period) - period * (d // period + 1), d, period):
            stroke.line((x, 0, x + d, d), fill=255, width=round(1.5 * self.k))
        tile = Image.new("RGBA", (d, d), fill + (255,))
        tile.paste(hatch + (255,), mask=strokes)
        self.canvas.paste(tile, (ox, oy), mask)

    def outline(self, cx, cy, r):
        ox, oy, d = self._box(cx, cy, r)
        self.draw.ellipse((ox, oy, ox + d, oy + d), outline=ACCENT + (255,), width=round(2 * self.k))

    def text(self, xy, s, style, px, fill, anchor="mm"):
        self.draw.text((xy[0] * self.k, xy[1] * self.k), s, font=self.font(style, px), fill=fill, anchor=anchor)

    def runs(self, x, y, parts, style, px, align="l"):
        """Draw (text, colour) runs on one line; align 'r' right-aligns to x."""
        f = self.font(style, px)
        total = sum(f.getlength(s) for s, _ in parts) / self.k
        cursor = x - total if align == "r" else x
        for s, colour in parts:
            self.draw.text((cursor * self.k, y * self.k), s, font=f, fill=colour, anchor="lm")
            cursor += f.getlength(s) / self.k

    def emoji(self, char, cx, cy, size):
        native = None
        for n in (160, 109, 128):               # bitmap emoji fonts only load at fixed sizes
            try:
                font, native = ImageFont.truetype(self.emoji_path, n), n
                break
            except OSError:
                continue
        if native is None:
            sys.exit(f"error: cannot load {self.emoji_path}")
        tile = Image.new("RGBA", (native * 2, native * 2), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((native // 2, native // 2), char, font=font, embedded_color=True)
        tile = tile.crop(tile.getbbox())
        f = size * self.k / max(tile.size)
        tile = tile.resize((round(tile.width * f), round(tile.height * f)), Image.LANCZOS)
        self.canvas.alpha_composite(tile, (round(cx * self.k - tile.width / 2), round(cy * self.k - tile.height / 2)))

    def wrap(self, label, max_px):
        f, lines = self.font("bi", LABEL_PX), []
        for word in label.split():
            if lines and f.getlength(lines[-1] + " " + word) / self.k <= max_px:
                lines[-1] += " " + word
            else:
                lines.append(word)
        return lines

    def vertical(self, cx, cy, parts, px):
        f = self.font("bi", px)
        w = round(sum(f.getlength(s) for s, _ in parts)) + 4
        strip = Image.new("RGBA", (w, round(px * self.k * 1.6)), (0, 0, 0, 0))
        sd, cursor = ImageDraw.Draw(strip), 0
        for s, colour in parts:
            sd.text((cursor, strip.height / 2), s, font=f, fill=colour, anchor="lm")
            cursor += f.getlength(s)
        strip = strip.rotate(90, expand=True)
        self.canvas.alpha_composite(strip, (round(cx * self.k - strip.width / 2), round(cy * self.k - strip.height / 2)))

    def result(self, scale):
        return self.canvas.convert("RGB").resize((W * scale, H * scale), Image.LANCZOS)


def build_diagram(ops, version, updated, author, scale):
    p = Painter(scale)
    n = len(ops)
    if n > len(EMOJI):
        sys.exit(f"error: {n} Ops but only {len(EMOJI)} emoji defined in EMOJI")
    counts = (n, sum(len(o["functions"]) for o in ops),
              sum(len(f["parameters"]) for o in ops for f in o["functions"]))

    # Op circles run clockwise from the top. Fills first, then every outline (so
    # overlapping outlines all show), then the centre circle on top of them.
    spots = []
    for i in range(n):
        angle = 2 * math.pi * i / n - math.pi / 2
        spots.append((CENTER[0] + R_RING * math.cos(angle), CENTER[1] + R_RING * math.sin(angle)))
    for cx, cy in spots:
        p.fill_circle(cx, cy, R_OP, RING_FILL, RING_HATCH)
    for cx, cy in spots:
        p.outline(cx, cy, R_OP)
    p.fill_circle(*CENTER, R_CENTER, CENTER_FILL, CENTER_HATCH)
    p.outline(*CENTER, R_CENTER)

    for i, ((cx, cy), op) in enumerate(zip(spots, ops)):
        lines = p.wrap(op["title"], LABEL_MAX_W)
        top = cy - (38 + 20 * len(lines)) / 2       # emoji + gap + label lines, centred on the circle
        p.emoji(EMOJI[i], cx, top + 16, 32)
        for j, line in enumerate(lines):
            p.text((cx, top + 44 + 20 * j), line, "bi", LABEL_PX, NAVY)
    p.emoji(CENTER_EMOJI, CENTER[0], CENTER[1] - 40, 64)
    p.text((CENTER[0], CENTER[1] + 27), "Enterprise", "bi", 32, RED)
    p.text((CENTER[0], CENTER[1] + 62), "Architect", "bi", 32, RED)

    # Header, counts, side caption and footer.
    p.text((30, 60), "eaOps", "b", 34, NAVY, anchor="ls")
    p.text((143, 58), version, "b", 13, GREY, anchor="ls")
    p.text((30, 77), "Multi-Cloud|AI-native Enterprise", "b", 14, NAVY, anchor="lm")
    p.text((30, 96), "Architecture Operations (eaOps).", "b", 14, NAVY, anchor="lm")
    for j, (num, word) in enumerate(zip(counts, ("ops.", "functions.", "parameters."))):
        p.runs(1250, 40 + 25 * j, [(str(num), RED), (" " + word, NAVY)], "b", 15.5, align="r")
    p.vertical(171, 560, [("top ", NAVY), (str(n), RED), (" must-have Ops of an ", NAVY),
                          ("Enterprise Architect", RED)], 22)
    p.text((30, 1064), author, "b", 13.9, RED, anchor="lm")
    p.text((30, 1082), f"Last Updated: {updated}", "b", 13.9, RED, anchor="lm")
    p.text((1250, 1066), "For more details...read on...", "b", 13.9, NAVY, anchor="rm")
    p.text((1250, 1082), PAGE_NAME, "b", 13.9, RED, anchor="rm")
    return p.result(scale)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--updated", default=build_html.today(), help="'Last Updated' date, e.g. 9/17/2026 (default: today)")
    parser.add_argument("--author", default="Suresh Banda")
    parser.add_argument("--out", type=Path, default=build_html.ROOT / "dist" / "eaOps.png", help="output PNG file (default: dist/eaOps.png)")
    parser.add_argument("--scale", type=int, default=1, help="output size multiplier, e.g. 2 for a sharper image")
    parser.add_argument("--force", action="store_true", help="overwrite the output if it already exists")
    args = parser.parse_args()

    if args.out.exists() and not args.force:
        raise build_html.ContentError(f"{args.out} already exists. Pass --force to overwrite it.")
    ops = build_html.load_ops(build_html.ROOT / "content")
    image = build_diagram(ops, build_html.read_version(), args.updated, args.author, args.scale)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.out, optimize=True)
    print(f"Wrote {args.out} ({image.width}x{image.height})")


if __name__ == "__main__":
    try:
        main()
    except build_html.ContentError as err:
        sys.exit(f"error: {err}")
