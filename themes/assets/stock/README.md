# Stock kit — built-in pictures for agents that cannot generate images

A ready-made illustration set in the **illustrated (插画版) gouache style**, so
the skill can still deliver a themed HTML page when the running agent has no
image generation of its own and no OpenRouter key — the `prefs.pictures: "stock"`
branch of SKILL.md Phase 6. Generated pictures always beat these: they are drawn
for the actual trip. This kit is the honest fallback and says so (*Notice*).

| content | count | files |
|---|---|---|
| region cover paintings (16:9, opaque, full-bleed page cover) | 14 | `stock-cover-<archetype>.webp` |
| generic scene cut-outs (transparent stickers) | 30 | `stock-<scene>.cut.webp` (+ `.sm.webp`, `.md.webp` on 3 stems) |
| world landmark cut-outs (transparent stickers) | 36 | `stock-<landmark>.cut.webp` (+ `.sm.webp`, `.md.webp` on 12 stems) |

Coverage: **illustrated** complete (the default), **clay** works via the built-in
neutral SVG terrain kit; the other six themes need generated pictures
(`docs/KNOWN-ISSUES.md` AST-7/AST-8).

Style: flat hand-drawn gouache, warm muted terracotta / sand beige / dusty teal
/ cream — the `style_anchor` at the top of `themes/assets/manifest.json`; covers
keep the upper two thirds as quiet sky so a large page title fits. Cost
**$0.9284** for 25 gpt-image-2 calls (14 covers + 11 six-cell sheets), prompt
and price per image in `manifest.stock.json`. PNG masters and sheet mothers stay
out of git (`.gitignore: themes/**/*.png`); the 161 webp the renderers inline
(5.2 MB — 14 covers + 66 `.cut` + 66 `.sm` + 15 `.md`) are what ships. `index.json`
is the lookup table: 14 archetypes with keywords, ISO2 → archetype for 225
countries and territories, multilingual country names, a keyword list per cut-out,
the illustrated stems already in `themes/assets/` for JP / TR / US / CN, and the
generic plane / bus / train / balloon.

## How the skill uses it

```bash
python3 themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
python3 themes/render_theme2.py plan.geo.json --art plan.art.json \
        --assets themes/assets/stock -o trip-illustrated.html
```

`stock_art.py` fills the picture side of `art.json` — cover from the destination
country, one hero per day by keyword score; the words (cover title, day themes,
captions) stay the agent's job. **`--assets themes/assets/stock` is required**:
`data_uri()` searches `themes/assets/` and the plan's own directory, not this
sub-folder.

## Notice — keep it visible

The chat reply and the page fine print both carry it, in the page language.
`index.json` holds the canonical wording under `notice`: the page-language string
from `notice` goes into `end.fine`, and `cover.credit` carries a shortened form the
script derives (`stock_art.NOTICE_SHORT` — `credit` is a thin one-line slot in every
theme). If the cover also cites a poem, the citation comes first and the notice
after. Without it a stock page passes itself off as bespoke art, the one thing this
kit must not do.

- en: `Pictures: built-in stock kit — no image generator or key was available;
  provide one and the art is generated for this trip.`
- zh: `图片来自内置素材库(本次未接入生图能力);接入生图模型或 KEY 后可为本次行程定制生成。`

## Extending it

**Maintainer task only** — a trip run never writes into `themes/assets/`; see
`themes/README.md` §Where pictures come from.

Same prompts, same pipeline: copy the skeleton of a `manifest.stock.json` entry
(a cover, or a `stock-sheet-*` six-cell sheet), generate with `themes/gen.py …
--outdir themes/assets/stock --manifest themes/assets/stock/manifest.stock.json`
(`--dry-run` first), then per ART-SCHEMA.md §Image toolchain: `split_sheet.py
<sheet>.png --probe` → the same with the six stems in reading order (add `--grid
3x2` when the probe misses a gutter) → `cutout.py <cell>.png` → `towebp.py
<cell>.cut.png --sizes sm,md,lg`. Covers skip the split: `towebp.py
stock-cover-x.png`, ≲ 130 KB (`--quality 78` if a busy one runs over). Then add
the stem to `index.json` (`covers` or `cutouts`, lower-case multilingual
keywords; a landmark needs its `countries` list or it gets picked for the wrong
trip) and to the count in `IMAGE-LIBRARY.md` §22. Licence: MIT, like the repo.
