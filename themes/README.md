# themes/ — themed renderers for a plan

Eight visual themes that render the same `plan.geo.json` the plain `scripts/render_plan.py`
reads, each into one self-contained HTML (assets inlined as data URIs, opens by
double-click, no network). Manual: `references/themes.md`; art contract: `ART-SCHEMA.md`
here (the only copy).

**One of these pages is the deliverable** — SKILL.md Phase 6 hands the user
`trip-<theme>.html` in the theme chosen at Phase 0 (`prefs.theme`, default
**illustrated**) plus `trip.kml`; a plain text page is never the deliverable. The
`scripts/render_plan.py` page is the printable extra, or the last resort after one honest
fix attempt here. A session with no image generator and no key does not drop to that
plain page either — it renders a theme from the built-in stock kit (below).

## What is here

| file | what |
|---|---|
| `render_theme2.py` 插画 illustrated · `render_clay2.py` 黏土 clay · `render_noir2.py` 夜航 noir · `render_glass2.py` 玻璃 glass · `render_journal.py` 手账 journal · `render_zine.py` zine · `render_splash.py` 闪屏 splash · `render_portal.py` 穿越 portal (video) | the eight renderers, one theme each |
| `render_picker.py` | the style-chooser page (one card per theme) |
| `theme_common.py` | shared helpers: `data_uri`, `load_plan`, `Art`/`load_art`/`add_art_arg`, `export_js` (share buttons), icons, i18n (`STRINGS`/`T`/`init_lang`/`weekday`/`theme_name`) |
| `qc.py` | static QC of a built page — offline contract, no-JS survival, print, focus, link hygiene, inline `url("` |
| `xprobe.sh` · `xt.sh` | headless export probes (with / without picture) |
| `towebp.py` · `cutout.py` · `split_sheet.py` · `gen.py` · `build_manifest.py` · `build_portal_jobs.py` | asset pipeline: png→webp (+ size variants), alpha cut-out, sheet splitting, gpt-image-2 generation, manifest refresh, portal clip job builder |
| `ART-SCHEMA.md` · `lucide-icons.json` | the art.json contract · the icon sprite source |
| `assets/` | the picture library: every embeddable `*.webp`, `caveat-vf.woff2`, `manifest.json` (prompt + cost per generated asset), `IMAGE-LIBRARY.md` (index by subject), `portal/` (the portal footage sidecar dir — empty in the tree, restore command in [`assets/portal/README.md`](assets/portal/README.md)) |

## Three commands

```bash
python3 themes/render_<x>.py plan.geo.json [--art F|none] [--assets DIR ...] [--lang zh|en] -o out.html
python3 themes/qc.py out.html                        # exit 0 = clean; exit code = FAIL count
themes/xprobe.sh out.html module '#d5' out.png       # click the real share button headlessly, look at out.png
```

`<x>` ∈ theme2 clay2 noir2 glass2 journal zine splash portal picker. (`render_picker.py plan.geo.json -o picker.html [--products DIR] [--prefix NAME]` links the rendered pages as `{prefix}-{theme}.html` with the English theme key, e.g. `japan-illustrated.html` — pages exported under the old Chinese tag (e.g. `-插画版.html`) still resolve; prefix defaults to `cover.kick_en` with spaces → `-`; products dir defaults to the output dir.) A trip is
rendered into as many themes as you like from the same plan; the theme picks up
`<plan stem>.art.json` beside the plan automatically. UI language (buttons, tags,
section names, weekdays, `<title>` theme name) follows the plan's top-level `"lang"`
(`zh` default | `en`; `--lang` overrides) — shared words in `theme_common.STRINGS`,
each theme's own voice in its renderer's `L` table; plan/art text prints as written
(`references/themes.md` §4a). `<title>` and the download-filename prefix open with
`cover.kick` on a zh page and `cover.kick_en` on an en page (all eight themes,
`theme_common.title_kick`); `cover.credit` (the poem's source) is printed by all
eight, zine included. A plan section of the wrong shape (a dict where `budget` /
`legs` want a list …) renders empty with a stderr `WARN plan.<key>` pointing at
`references/output-template.md` — start from `assets/plan.example.json` and read
stderr. `xprobe.sh … page ''` prints `NO-BTN` on noir/glass (module-only export) but
still leaves the live first screen in `out.png` — that is the cover shot, not a failure
(`references/themes.md` §6).

## art.json in one sentence

Everything that names *this* trip — cover poem title, per-day 4-char titles, captions,
closing line, which picture stems go where — lives in `<plan>.art.json`; the theme's own
kit (tape, stamps, sketches, terrains, moods) stays in the renderer and art only picks
from it. Every field is optional; an empty art file must still render. Schema:
`ART-SCHEMA.md`.

## Where pictures come from

Reuse first: `assets/IMAGE-LIBRARY.md` §Generic pieces (通用件) lists the assets any trip may use
(place-bound ones — landmarks, `noir-*`, `glass-*`, `au-*`, `nordic-*` — do not cross
trips). Missing pieces: **an agent that can generate images natively should just do
that — no key — and then run the same split/cutout/webp steps below** (contract:
ART-SCHEMA.md §Generator choice); `gen.py` is the fallback for environments without native
generation. Full paths — the shell cwd resets between calls:

```bash
python3 themes/gen.py <trip>/jobs.json --outdir <trip> --manifest <trip>/manifest.<trip>.json   # --dry-run first
python3 themes/split_sheet.py <trip>/x-sheet.png --probe                                         # count the cells
python3 themes/split_sheet.py <trip>/x-sheet.png --grid 3x2 name1 … name6 --outdir <trip>        # names in Row 1 → Row 2 order
python3 themes/cutout.py <trip>/x.png --outdir <trip>                                            # cut-out slots → x.cut.webp
python3 themes/towebp.py <trip>/x.png --outdir <trip>                                            # opaque plates/photos → x.webp
python3 themes/towebp.py <trip>/x.cut.png --sizes sm,md,lg --outdir <trip>                       # size variants of a cut-out
```

`--outdir` on `split_sheet.py` / `cutout.py` / `towebp.py` defaults to the input's own
directory. Which slots are cut-outs and which opaque: the "shape" column of the size
table in `ART-SCHEMA.md` (a cut-out slot fed `towebp x.png --sizes md` gets a white
square, silently). Keep a trip's webp beside its plan or pass `--assets DIR`; the lookup
order is `--assets` → art dir → plan dir → `themes/assets/`. **A test trip or a normal
user never writes into `assets/` or `IMAGE-LIBRARY.md`** — `<trip>/manifest.<trip>.json`
is the record; the main agent folds generic pieces back into the library after a batch
(ART-SCHEMA.md §Test-trip asset recycling). Portal needs its clip chain next to the output HTML — it
is the only theme that ships sidecar files. The US reference chain is a release asset, not
in the tree; `assets/portal/` is empty in a fresh clone and
[`assets/portal/README.md`](assets/portal/README.md) has the one-line curl+unzip restore
(the shipped portal case is Morocco, live on the demo site).
`build_portal_jobs.py --spec worlds.json` writes the ComfyUI jobs (`STEPS` = 10 by
default since 2026-08-16).

**Neither native generation nor a key → stock mode** (`prefs.pictures = "stock"`, set by
Phase 0's capability check). `stock_art.py` builds the picture side of the art file from
`assets/stock/` — region cover paintings and landmark / generic-scene cut-outs in the
illustrated style, matched to the plan's country and each day's stops — plus the shared
library's same-country pictures and generic props:

```bash
python3 themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
```

It fills pictures only; the **words** stay yours (cover title, per-day `theme`/`en`/`mark`,
captions, closing line) and shipping its placeholders is a defect. It writes the stock
notice into the page's fine print — keep it, and say the same line once in the chat
summary. Coverage: **illustrated** complete, **clay** works (built-in neutral SVG terrain
kit + generic clay props); the other six themes still need generated pictures
(`references/themes.md` §3b).

In full: `stock_art.py plan.geo.json [--theme illustrated|clay] [--lang zh|en] [--country
ISO2] [--index PATH] [-o OUT] [--force]`. `-o` defaults to `<plan stem>.art.json` beside the
plan — the sidecar every renderer finds by itself — and an existing art file is never
overwritten without `--force`; `--lang` follows `plan.lang` unless you say otherwise. The
day → stem table with the reason for each pick goes to stderr, the output path to stdout, and
the last stderr line is the render command to paste — **including `--assets
themes/assets/stock`, which is not optional**: `data_uri()` searches `themes/assets/` but not
its sub-folders, so a render without it yields a page with no pictures and no errors. The
destination country is read from the plan's own words (trip title, `meta.route`, legs, each
day's city and stop names) against `index.json`'s 225 ISO2 codes; a country named in a single
stop is ignored (the Egyptian Bazaar does not move a trip to Egypt), and when nothing is
recognised the script WARNs, paints a neutral cover and asks for `--country DE`. Illustrated
then gets the cover painting, one cut-out per day (landmarks the trip actually visits first,
then the shared library's same-country stems, then generic scenes; a travel day gets the plane
or the train unless the day is really about a place) and up to three wide `feature` days; clay
gets its terrain `zones` from the country's archetype and one figurine per day.

## Not in the repo

`gen.py` / `genvideo.py` read their credential (`.auth_header`, one line
`Authorization: Bearer <OpenRouter key>`; scratch `.payload.json`) from this directory only; they are gitignored and never copied into a trip folder. PNG
originals, mock/style-research files and trip data (`plan.geo.json`, `plan.art.json`,
rendered pages) also stay out — only the renderers, tools, docs and `assets/` are tracked.

## Video clips (portal theme) — native generation first, else one key (same as images)

An agent with native video generation uses it directly (16:9 h264 mp4, 24 fps, dive 5–6 s /
link 4 s, first/last-frame conditioning for links; no key). Otherwise `genvideo.py` talks to
OpenRouter's video API with the same `.auth_header` as `gen.py`:

```bash
python3 themes/genvideo.py --models                                  # live price / capability table
python3 themes/genvideo.py jobs.json --dry-run                       # nothing sent, nothing charged
python3 themes/genvideo.py jobs.json --outdir trips/x/portal --manifest trips/x/manifest.x.json
```
A job = `{name, prompt, model?, duration, resolution, aspect_ratio, audio, first_frame?, last_frame?, seed?}`;
local frame files become data: URIs, https URLs pass through. Default model `google/veo-3.1-lite`
(720p, no audio ≈ $0.03/s → a ten-world portal chain ≈ $3); `minimax/hailuo-3` is the
quality tier (2K, $0.13/s). Smoke-tested 2026-08-15: 4 s first-frame clip, 65 s wall, $0.12,
1280×720 h264 — the first frame is the still you passed. Our own regression footage is still
rendered on the local 5090 (free); this script is the path anyone with a key can use.
