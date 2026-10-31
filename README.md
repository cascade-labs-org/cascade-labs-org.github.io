# Cascade Labs website

Live at **<https://cascade-labs-org.github.io/>**, published by GitHub Pages from this
repository (`cascade-labs-org/cascade-labs-org.github.io`).

The studio site: a home page, a games list, a page for each game (Tenspire so far), and
the privacy policy and account-deletion pages the app stores require for every game. It is
plain HTML and CSS in `public/` with one small script, no framework and **no build step**.

```
public/                          everything that gets published
  index.html                     home: the fan, our games, how we make games, contact
  games/index.html               every game
  games/tenspire/index.html      Tenspire
  games/tenspire/privacy/        Tenspire's privacy policy          (copied - see below)
  games/tenspire/delete-account/ how to delete a Tenspire account   (copied)
  games/rentfall/                Rentfall's support landing, privacy policy and
                                 account deletion                   (copied)
  tenspire/, rentfall/           short addresses that forward to games/<game>/...
  404.html                       shown for any address that does not exist
  assets/css/site.css            the one stylesheet (colour and type tokens at the top)
  assets/js/site.js              the fan's riffle on hover/tap; the site works without it
  assets/img/                    logos, icons and game art (generated)
brand/                           the logo exactly as supplied
tools/build-assets.py            makes everything generated, from brand/ and the game repos
tools/ribbons.py                 the logo's ribbons traced as vectors
.github/workflows/pages.yml      publishes public/ on every push to main
```

## Preview it

From the `Games` folder, start the **cascade-site** preview (it runs
`python -m http.server 8090 --directory cascade-labs/public`) and open
<http://localhost:8090>. The local server does not show `404.html`; GitHub Pages does.

## Rebuild the generated files

```bash
python -I tools/build-assets.py
```

It reads `brand/`, and the two game repositories in `../games/` (`../games/tenspire` and
`../games/rentfall`), and rewrites:

- the logo and mark with the white background removed, plus a version of the logo for dark
  backgrounds (CASCADE in white),
- the mark redrawn as vector ribbons (`cascade-mark.svg`, `favicon.svg`) and inlined into
  `public/index.html` between the `<!-- fan:start -->` markers, where it fans open,
- favicons and the share images,
- Tenspire's icon and six screenshots as WebP, and Rentfall's icon,
- **each game's privacy and account-deletion pages**, copied from the game's `site/`
  folder. Those are generated in the game's repository from its `docs/PRIVACY-POLICY.md`
  (`npm run site` there) - never edit the copies here.

Commit what it writes and push; the site republishes in a minute or two.

**The games link to these pages**: `SITE_BASE` in each game's `app/src/links.ts` is
`https://cascade-labs-org.github.io/games/<game>`, and the Play listings point at the same
addresses. Moving or renaming them breaks the privacy link in every installed copy.

## Add a game page

Copy `public/games/tenspire/index.html` to `public/games/<game>/`, change the words and
pictures, add the game's art and pages to `build-assets.py`, and link it from
`public/games/index.html` and the home page.

## Before you share it widely

- **Contact address.** Every email link on the site, and the contact on every game's
  privacy and deletion pages, is the placeholder `hello@cascadelabs.example`, which cannot
  receive mail. When the studio has an address: search `public/*.html` and
  `public/games/*/index.html` for `cascadelabs.example`, set `SUPPORT_EMAIL` in each game's
  `app/src/links.ts`, run `npm run site` in each game, then rebuild here.
- **The site's address** is written in full in each page's `<head>` (`canonical`, `og:url`,
  `og:image` - link previews need a full address), in `public/sitemap.xml` and in
  `public/robots.txt`. If the site moves to its own domain, search `public/` for
  `cascade-labs-org.github.io` and change them all, along with `SITE_BASE` in the games.

## Hosting

GitHub Pages, free, from this public repository - **Settings → Pages → Source: GitHub
Actions**. GitHub Pages cannot send custom response headers, so each studio page carries
its Content-Security-Policy in a `<meta>` tag instead.

A domain of your own can be added for free under Settings → Pages → Custom domain; you pay
only the registrar.
