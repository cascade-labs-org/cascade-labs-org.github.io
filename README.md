# cascade-labs-org.github.io

Public pages for Cascade Labs' games, served at <https://cascade-labs-org.github.io/>.
The game repositories are private, and a private repository cannot serve GitHub Pages on a
free plan, so the pages the stores require live here.

| Path | What it is |
|---|---|
| `tenspire/privacy/` | Tenspire privacy policy |
| `tenspire/delete-account/` | How to delete a Tenspire account and what happens to its data |
| `rentfall/privacy/` | Rentfall privacy policy |
| `rentfall/delete-account/` | How to delete a Rentfall account |

**Do not edit the game folders by hand.** They are generated in each game's repository
(`npm run site`, from its `docs/PRIVACY-POLICY.md`) so the published policy cannot drift
from the reviewed one: copy the game's `site/` folder here, without its README, and push.

The same pages used to live at `akashkalala.github.io/tenfold/...`, `/rentfall/...` and
`/freehold/...`; those addresses now forward here, so links in apps already installed
keep working.
