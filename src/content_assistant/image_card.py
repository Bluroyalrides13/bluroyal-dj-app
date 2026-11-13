"""Branded Instagram graphic (1080x1350, JPEG — what Instagram's API accepts)."""

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from src.content_assistant import config

W, H = 1080, 1350
FONT_DIR = Path(__file__).resolve().parents[2] / "static" / "assistant" / "fonts"


def _font(name: str, size: int, weight: int) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONT_DIR / name), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def _hex(c: str) -> Tuple[int, int, int]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int):
    words, lines, line = text.split(), [], ""
    for w in words:
        test = f"{line} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def _fit(draw, text, fname, weight, max_w, max_h, start, minimum, spacing=1.08):
    size = start
    while size >= minimum:
        font = _font(fname, size, weight)
        lines = _wrap(draw, text, font, max_w)
        h = int(len(lines) * size * spacing)
        if h <= max_h:
            return font, lines, size
        size -= 4
    font = _font(fname, minimum, weight)
    return font, _wrap(draw, text, font, max_w), minimum


def _center(draw, lines, font, size, top, color, spacing=1.08):
    y = top
    for ln in lines:
        w = draw.textlength(ln, font=font)
        draw.text(((W - w) / 2, y), ln, font=font, fill=color)
        y += int(size * spacing)
    return y


def make_card(brand_key: str, headline: str, subline: str, cta: str, dest: Path) -> Path:
    brand = config.BRANDS[brand_key]
    bg, gold, white = (_hex(brand["colors"][k]) for k in ("bg", "accent", "text"))

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    # soft glow + frame
    glow = Image.new("RGB", (W, H), bg)
    gd = ImageDraw.Draw(glow)
    for i, r in enumerate(range(520, 0, -20)):
        mix = min(1.0, i / 26) * 0.10
        col = tuple(int(bg[j] * (1 - mix) + gold[j] * mix) for j in range(3))
        gd.ellipse((W / 2 - r, 470 - r, W / 2 + r, 470 + r), fill=col)
    img = Image.blend(img, glow, 1.0)
    d = ImageDraw.Draw(img)
    d.rectangle((40, 40, W - 40, H - 40), outline=gold, width=3)
    dim = tuple(int(bg[j] * 0.6 + gold[j] * 0.4) for j in range(3))
    d.rectangle((54, 54, W - 54, H - 54), outline=dim, width=1)

    # brand mark
    mark = _font("Montserrat.ttf", 30, 600)
    label = brand["name"].upper()
    spaced = " ".join(label)
    w = d.textlength(spaced, font=mark)
    d.text(((W - w) / 2, 110), spaced, font=mark, fill=gold)
    d.line((W / 2 - 60, 165, W / 2 + 60, 165), fill=gold, width=2)

    # headline
    hfont, hlines, hsize = _fit(d, headline.strip(), "CormorantGaramond.ttf", 700, W - 200, 520, 132, 64)
    sfont, slines, ssize = _fit(d, subline.strip(), "Montserrat.ttf", 400, W - 240, 220, 44, 30, 1.35)
    gap = 70
    block_h = int(len(hlines) * hsize * 1.08) + gap + int(len(slines) * ssize * 1.35)
    area_top, area_bottom = 210, 1060
    top = area_top + max(0, (area_bottom - area_top - block_h) // 2)
    y = _center(d, hlines, hfont, hsize, top, gold)
    _center(d, slines, sfont, ssize, y + gap - int(hsize * 0.08), white, 1.35)

    # CTA pill
    if cta.strip():
        cfont = _font("Montserrat.ttf", 34, 700)
        text = cta.strip().upper()
        tw = d.textlength(text, font=cfont)
        pw, ph = tw + 90, 84
        x0, y0 = (W - pw) / 2, H - 250
        d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=42, fill=gold)
        d.text(((W - tw) / 2, y0 + (ph - 40) / 2), text, font=cfont, fill=bg)

    if brand.get("website"):
        ffont = _font("Montserrat.ttf", 26, 500)
        tw = d.textlength(brand["website"], font=ffont)
        d.text(((W - tw) / 2, H - 120), brand["website"], font=ffont, fill=white)

    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=92, optimize=True)
    return dest
