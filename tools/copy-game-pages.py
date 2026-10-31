"""Copy each game's support pages into public/.

    python -I tools/copy-game-pages.py            every game
    python -I tools/copy-game-pages.py tenspire   one game

Run from anywhere. Each game generates its pages in its own repository, from its
docs/PRIVACY-POLICY.md (`npm run site` there writes its site/ folder). This copies the
game's support page, privacy policy and account-deletion page from ../games/<game>/site/
into public/games/<game>/, and writes forwarding pages at the short addresses /<game>/,
/<game>/privacy/ and /<game>/delete-account/.

It refuses to copy a game whose pages still name the placeholder address the games started
with, so a live privacy or deletion page never goes back to an address nobody reads.
"""
import html
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DIR = os.path.join(os.path.dirname(ROOT), "games")
PUB = os.path.join(ROOT, "public")

# Each game's folder in ../games/, which is also its address here.
GAMES = ("tenspire", "rentfall")
PAGES = ("index.html", "privacy", "delete-account")
PLACEHOLDER = b"hello@cascadelabs.example"

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


def files(path):
    if os.path.isfile(path):
        yield path
    for dp, _, fs in os.walk(path):
        for f in fs:
            yield os.path.join(dp, f)


def check(game):
    repo = os.path.join(GAMES_DIR, game)
    for item in PAGES:
        s = os.path.join(repo, "site", item)
        if not os.path.exists(s):
            raise SystemExit("%s is missing - run `npm run site` in %s" % (s, repo))
        for f in files(s):
            with open(f, "rb") as fh:
                if PLACEHOLDER in fh.read():
                    raise SystemExit("%s still names %s - give %s its real contact address and "
                                     "run `npm run site` there first" % (f, PLACEHOLDER.decode(), game))


def copy(game):
    src = os.path.join(GAMES_DIR, game, "site")
    dst = os.path.join(PUB, "games", game)
    os.makedirs(dst, exist_ok=True)
    for item in PAGES:
        s, d = os.path.join(src, item), os.path.join(dst, item)
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
    games = sys.argv[1:] or GAMES
    for game in games:
        if game not in GAMES:
            raise SystemExit("unknown game %r - add it to GAMES in %s" % (game, __file__))
    # Check every game before copying any, so a refusal leaves public/ as it was.
    for game in games:
        check(game)
    for game in games:
        copy(game)
        print("copied %s" % game)


if __name__ == "__main__":
    main()
