"""Build every generated file the site serves.

    python -I tools/build-assets.py

Run from anywhere. It reads the logo sources in brand/ and the store art in the two game
repositories next to this one (../tenfold and ../rentfall), and writes into public/:

- the Cascade Labs logo and mark with the white background taken out (PNG, cropped)
- the mark redrawn as vector ribbons (assets/img/cascade-mark.svg, favicon.svg), and the same
  ribbons inlined into public/index.html between the  <!-- fan:start -->  markers, where the
  page animates them
- favicons, the Apple touch icon and the share image
- Tenspire's icon and screenshots, resized for the web, and Rentfall's icon
- each game's privacy policy and account-deletion pages, copied from the game's generated
  site/ folder (`npm run site` there) into public/games/<game>/, and forwarding pages at the
  short addresses /tenspire/... and /rentfall/...

Generated files are committed, so the site deploys as plain files with no build step.
"""
import html
import math
import os
import re
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ribbons  # noqa: E402

ROOT = os.path.dirname(HERE)
GAMES = os.path.dirname(ROOT)
PUB = os.path.join(ROOT, "public")
IMG = os.path.join(PUB, "assets", "img")
TENSPIRE = os.path.join(GAMES, "tenfold")      # Tenspire's repository keeps its old folder name
RENTFALL = os.path.join(GAMES, "rentfall")

PIVOT_COLOUR = "#3a10e0"


def out(*parts):
    p = os.path.join(IMG, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# --- logo: white to transparent ------------------------------------------------------------

def white_to_alpha(im):
    """GIMP's colour-to-alpha against white: the result looks identical on white, and the
    soft edges of the ribbons and letters keep their colour on any other background."""
    im = im.convert("RGB")
    px = im.load()
    w, h = im.size
    res = Image.new("RGBA", (w, h))
    rp = res.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            a = max(255 - r, 255 - g, 255 - b)
            if a < 10:  # paper noise in the source
                rp[x, y] = (0, 0, 0, 0)
                continue
            f = 255.0 / a
            rp[x, y] = (
                max(0, min(255, int(round(255 - (255 - r) * f)))),
                max(0, min(255, int(round(255 - (255 - g) * f)))),
                max(0, min(255, int(round(255 - (255 - b) * f)))),
                a,
            )
    return res.crop(res.getbbox())


def on_dark(im):
    """The logo for a dark background: the black CASCADE turns white; the ribbons and the
    purple LABS keep their colour."""
    im = im.copy()
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and max(r, g, b) - min(r, g, b) < 48 and max(r, g, b) < 140:
                px[x, y] = (255, 255, 255, a)
    return im


def fit_height(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


# --- the mark as vector ribbons ------------------------------------------------------------

def fan_svg(cls="", ids="r", with_xmlns=True, title="Cascade Labs"):
    rs = ribbons.build()
    xs = [x for r in rs for x, _ in r["poly"]]
    ys = [y for r in rs for _, y in r["poly"]]
    pad = 4
    vb = (math.floor(min(xs)) - pad, math.floor(min(ys)) - pad,
          math.ceil(max(xs) - min(xs)) + 2 * pad, math.ceil(max(ys) - min(ys)) + 2 * pad)
    px, py = ribbons.P
    bottom = math.atan2(rs[-1]["tip"][1] - py, rs[-1]["tip"][0] - px)
    grads, paths = [], []
    # Back to front: the top ribbon first, the bottom (darkest, straightest) one last.
    for i, r in enumerate(rs):
        tx, ty = r["tip"]
        light = r["color"].lower() in ("#c99cfb", "#ddbbfd", "#debdfc")
        stops = ('<stop offset="0" stop-color="%s"/><stop offset="%s" stop-color="%s"/>'
                 '<stop offset="1" stop-color="%s"/>' % (r["color"], ".55" if light else ".35",
                                                          r["color"], PIVOT_COLOUR))
        grads.append('<linearGradient id="%s%d" gradientUnits="userSpaceOnUse" x1="%d" y1="%d" '
                     'x2="%d" y2="%d">%s</linearGradient>' % (ids, i, tx, ty, px, py, stops))
        # How far this ribbon turns to lie on the bottom one: the page fans them out from there.
        turn = math.degrees(math.atan2(ty - py, tx - px) - bottom)
        turn = (turn + 540) % 360 - 180
        paths.append('<path class="rb" style="--i:%d;--turn:%.1fdeg" fill="url(#%s%d)" d="%s"/>'
                     % (len(rs) - 1 - i, -turn, ids, i, ribbons.path_d(r["poly"])))
    attrs = ' xmlns="http://www.w3.org/2000/svg"' if with_xmlns else ""
    if cls:
        attrs += ' class="%s"' % cls
    return ('<svg%s viewBox="%d %d %d %d" role="img" aria-label="%s">'
            '<defs>%s</defs><g>%s</g></svg>' % (attrs, *vb, title, "".join(grads), "".join(paths)))


def inject(path, marker, html):
    s = open(path, encoding="utf-8").read()
    pat = re.compile(r"(<!-- %s:start -->).*?(<!-- %s:end -->)" % (marker, marker), re.S)
    if not pat.search(s):
        raise SystemExit("%s has no %s markers" % (path, marker))
    s = pat.sub(lambda m: m.group(1) + html + m.group(2), s)
    open(path, "w", encoding="utf-8", newline="\n").write(s)


# --- share image -----------------------------------------------------------------------------

def share_image(logo, dst):
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), "white")
    lg = fit_height(logo, 250)
    im.paste(lg, ((W - lg.width) // 2, (H - lg.height) // 2 - 10), lg)
    d = ImageDraw.Draw(im)
    d.rectangle((0, H - 14, W, H), fill="#4a16f2")
    im.save(dst, optimize=True)


def webp(src, dst, width=None, height=None, q=82):
    im = Image.open(src)
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
    if width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    elif height:
        im = fit_height(im, height)
    im.save(dst, "WEBP", quality=q, method=6)


# The pages the stores require, from each game's generated site/ folder. Tenspire's own
# page on this site (/games/tenspire/) is the landing its pages link back to, so its
# generated index.html is not copied; Rentfall has no page here yet, so its is.
GAME_PAGES = (
    ("tenspire", TENSPIRE, ("privacy", "delete-account")),
    ("rentfall", RENTFALL, ("index.html", "privacy", "delete-account")),
)

FORWARD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=%(url)s">
<link rel="canonical" href="%(url)s">
</head>
<body>
<p>This page is at <a href="%(url)s">%(url)s</a>.</p>
</body>
</html>
"""


def game_pages():
    for game, repo, items in GAME_PAGES:
        src = os.path.join(repo, "site")
        dst = os.path.join(PUB, "games", game)
        os.makedirs(dst, exist_ok=True)
        for item in items:
            s, d = os.path.join(src, item), os.path.join(dst, item)
            if not os.path.exists(s):
                raise SystemExit("%s is missing - run `npm run site` in %s" % (s, repo))
            if os.path.isdir(s):
                shutil.rmtree(d, ignore_errors=True)
                shutil.copytree(s, d)
            else:
                shutil.copyfile(s, d)
        # Short addresses: /tenspire/privacy/ and friends land on the real pages.
        for page in ("", "privacy/", "delete-account/"):
            url = "/games/%s/%s" % (game, page)
            f = os.path.join(PUB, game, page, "index.html")
            os.makedirs(os.path.dirname(f), exist_ok=True)
            with open(f, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(FORWARD % {"title": html.escape(game.capitalize()), "url": url})


def main():
    mark = white_to_alpha(Image.open(os.path.join(ROOT, "brand", "cascade-mark-source.webp")))
    logo = white_to_alpha(Image.open(os.path.join(ROOT, "brand", "cascade-logo-source.webp")))
    fit_height(logo, 160).save(out("cascade-labs-logo.png"), optimize=True)
    fit_height(on_dark(logo), 160).save(out("cascade-labs-logo-light.png"), optimize=True)
    fit_height(mark, 512).save(out("cascade-labs-mark.png"), optimize=True)

    svg = fan_svg()
    open(out("cascade-mark.svg"), "w", encoding="utf-8").write(svg)
    open(os.path.join(PUB, "favicon.svg"), "w", encoding="utf-8").write(svg)
    inject(os.path.join(PUB, "index.html"), "fan", fan_svg(cls="fan", ids="fan", with_xmlns=False,
                                                        title="The Cascade Labs mark"))

    # Raster icons: the mark centred on white, for places that will not take SVG.
    for size, name in ((32, "favicon-32.png"), (180, "apple-touch-icon.png")):
        sq = Image.new("RGB", (size, size), "white")
        m = fit_height(mark, round(size * 0.84))
        if m.width > size * 0.84:
            m = m.resize((round(size * 0.84), round(m.height * size * 0.84 / m.width)), Image.LANCZOS)
        sq.paste(m, ((size - m.width) // 2, (size - m.height) // 2), m)
        sq.save(os.path.join(PUB, name), optimize=True)
        if size == 180:
            # Browsers ask for /favicon.ico on pages that name no icon (the game pages).
            sq.save(os.path.join(PUB, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

    share_image(logo, out("share-cascade-labs.png"))

    # Tenspire
    ts = os.path.join(TENSPIRE, "store", "screenshots")
    for n in ("2-rules", "3-setup", "4-table", "5-hand", "6-spin", "7-avatars"):
        webp(os.path.join(ts, "android-%s.png" % n), out("tenspire", "%s.webp" % n.split("-", 1)[1]), width=600)
    webp(os.path.join(TENSPIRE, "app", "assets", "store-icon-512-play.png"), out("tenspire", "icon.webp"), width=256)
    Image.open(os.path.join(TENSPIRE, "store", "feature-graphic.png")).convert("RGB").save(
        out("tenspire", "share.png"), optimize=True)

    # Rentfall
    webp(os.path.join(RENTFALL, "app", "assets", "store-icon-512-play.png"), out("rentfall", "icon.webp"), width=256)

    game_pages()

    total = 0
    for dp, _, fs in os.walk(IMG):
        for f in fs:
            total += os.path.getsize(os.path.join(dp, f))
    print("images: %d KB" % (total // 1024))


if __name__ == "__main__":
    main()
