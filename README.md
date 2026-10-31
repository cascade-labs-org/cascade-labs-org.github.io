# Cascade Labs game support pages

Served at **<https://cascade-labs-org.github.io/>** by GitHub Pages from this repository.

The pages the app stores need for every Cascade Labs game: a support page, the privacy
policy and how to delete an account, plus a short page listing them all. The studio website
is not here: it lives in
[`cascade-labs-website`](https://github.com/cascade-labs-org/cascade-labs-website).

**The apps and the Play listings link to these addresses, so they must never move.**
`SITE_BASE` in each game's `app/src/links.ts` is
`https://cascade-labs-org.github.io/games/<game>`; the apps open `<SITE_BASE>/privacy`, and
the Play listings name the privacy and account-deletion pages.

```
public/
  index.html                     every game's pages, and the contact address
  games/<game>/                  the game's support page              (copied - see below)
  games/<game>/privacy/          its privacy policy                   (copied)
  games/<game>/delete-account/   how to delete an account             (copied)
  tenspire/, rentfall/           short addresses that forward to games/<game>/... (written
                                 by the copy script)
  404.html                       shown for any address that does not exist
  favicon.ico                    the Cascade Labs mark, from the website's build
tools/copy-game-pages.py         copies the games' pages in and writes the short addresses
.github/workflows/pages.yml      publishes public/ on every push to main
```

Every page here carries its own styles: nothing loads from anywhere else.

## Update a game's pages

Each game generates its pages in its own repository, from its `docs/PRIVACY-POLICY.md`
(`npm run site` there writes its `site/` folder). Never edit the copies here: change the
game, then copy again.

```bash
python -I tools/copy-game-pages.py            # every game
python -I tools/copy-game-pages.py tenspire   # one game
```

It reads `../games/<game>/site/`, so the games must sit next to this repository in
`../games/`. Commit what it writes and push; the pages republish in a minute or two.

## Add a game

Add its folder name to `GAMES` in `tools/copy-game-pages.py`, run it, and add the game to
`public/index.html`.

## Email addresses

`cascadelabs.in@gmail.com` is the contact on every page here. The closed-test note on
`public/index.html` sends sign-ups to `cascadelabs.review@gmail.com`.

The games started with the placeholder `hello@cascadelabs.example`. On 31 October 2026 the
copies here were switched to the real address by hand, before the games themselves were. Each
game still has to set `SUPPORT_EMAIL` in `app/src/links.ts`, fix its
`docs/PRIVACY-POLICY.md` and run `npm run site`. Until it does, the copy script refuses to
copy it, so the live pages cannot go back to the placeholder.

## Preview it

From the folder that holds this repository, run
`python -m http.server 8091 --directory cascade-labs-org.github.io/public` and open
<http://localhost:8091>. The local server does not show `404.html`; GitHub Pages does.

## Hosting

GitHub Pages, free, from this public repository - **Settings → Pages → Source: GitHub
Actions**. It serves the organisation's root address only from the repository named
`cascade-labs-org.github.io`, which is why the games' pages live here.
