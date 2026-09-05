# Known issues

Everything below is a defect or a hard limit that is **live in the current tree** —
each entry was re-checked against the code or the doc it points at before being
listed here. Nothing is aspirational: if a limit is deliberate, the entry says so and
still lists it, because it will bite whoever hits it first.

`Status` is `open` (no fix scheduled), `planned` (on the [Roadmap](#roadmap)), or
`resolved` (kept for the record — the entry says what fixed it).
Source pointers are `file → function / section`.

| ID | Area | One line | Status |
|---|---|---|---|
| [EXP-1](#exp-1) | Export engine | Whole-page export pads blank paper onto the tail | planned |
| [EXP-2](#exp-2) | Export engine | Splash whole-page export starts at DAY 01, not the cover | open |
| [EXP-3](#exp-3) | Journal theme | Cover quote collides with the postmark on `zh` pages | planned |
| [EXP-4](#exp-4) | Renderers | Chinese text left in CSS/JS comments of `en` pages | open |
| [EXP-5](#exp-5) | Picker | `zh` picker copy carries US-trip-specific history | planned |
| [EXP-6](#exp-6) | Portal theme | No portrait/mobile video chain — landscape only | planned |
| [EXP-7](#exp-7) | Probes | macOS headless Chrome will not go below ~500 px wide | open |
| [EXP-8](#exp-8) | Probes | Chrome 151 headless never exits; scripts self-kill | open |
| [EXP-9](#exp-9) | Export engine | Zine/splash whole-page export dropped its tail (foreignObject lays out taller than the live page) | resolved |
| [PLN-1](#pln-1) | route_tools | `sun` falls back to a longitude offset with no DST | open |
| [PLN-2](#pln-2) | route_tools | Mainland-China polygon is coarse at the borders | open |
| [PLN-3](#pln-3) | route_tools | `sun_stop` is new and only exercised synthetically | open |
| [PLN-4](#pln-4) | flight_scan | Outbound legs only; return times are back-computed | open |
| [PLN-5](#pln-5) | Hotels | No keyless hotel API — bands and deep links only | open |
| [PLN-6](#pln-6) | Geocoding | Nominatim: 1 req/s, quiet misses on non-Latin names | open |
| [PLN-7](#pln-7) | FX | frankfurter covers ~30 currencies; fallback is external | open |
| [PLN-8](#pln-8) | Holidays | nager.at has no religious / lunar holidays | open |
| [PLN-9](#pln-9) | Geocoding | A mis-geocoded stop inside 60 km is not detected; `check` only catches the long ones | open |
| [PLN-10](#pln-10) | Gates | The exit-code gates are advisory: renderers run with `plan_lint --strict` and `check` red | open |
| [PLN-11](#pln-11) | Lint | `plan_lint --strict` is blind to language and source stamps (the KML and empty-stop / `sun` checks landed 2026-09-05) | partly resolved |
| [PLN-12](#pln-12) | Text | Cover-title fallback (mode wording, the `fast-flights` install line and origin → hub landed 2026-09-05) | partly resolved |
| [AST-1](#ast-1) | Asset pipeline | `towebp.py` silently makes a white square from an un-cut PNG | open |
| [AST-2](#ast-2) | Asset library | Test-asset reclaim is a manual merge | open |
| [AST-3](#ast-3) | Generation | Without native generation in the agent, image/video generation needs an OpenRouter key | open |
| [AST-4](#ast-4) | Portal footage | Cloud video path smoke-tested on one 4 s clip | open |
| [AST-5](#ast-5) | Zine theme | `cover.zh` is a hard 2–4 glyph column | open |
| [AST-6](#ast-6) | Renderers | Wrong plan section type warns instead of failing | open |
| [AST-7](#ast-7) | Stock mode | Stock kit covers illustrated fully and clay partially; six themes still need generated pictures | open |
| [AST-8](#ast-8) | Stock mode | The stock kit is drawn in the illustrated style only — per-style stock packs are future work | open |
| [AST-9](#ast-9) | Stock mode | A stock render without `--assets themes/assets/stock` silently drops the stock pictures | open |
| [SCO-1](#sco-1) | Scope | Personal-use posture — not licensable as a service | planned |
| [SCO-2](#sco-2) | Scope | Not real-time: no delay tracking, no rebooking | open |
| [SCO-3](#sco-3) | Scope | Beyond ~3 months only the seasonal pattern is knowable | open |
| [SCO-4](#sco-4) | Project | Name settled 2026-08-16: `trip-planner-skill` (descriptive on purpose — trip = one specific journey, the unit this skill plans; same-named repos exist, ours competes on substance) | resolved |

---

## Export engine and renderers

### EXP-1
**Whole-page export sizes the canvas from the live `scrollHeight`, so the long image
ends in blank paper.**

- **Symptom** — 「生成长图」 / *Save long image* on Clay, Journal, Zine and Splash
  produces a PNG whose content stops well before the bottom edge; the remainder is
  flat page background. Roughly 900 px on a laptop viewport, up to ~2600 px in a
  tall probe window.
- **Cause** — the canvas is measured from the live element. That number counts every
  in-flow `.no-export` node (share-button rows, closed `<details>` hop links) that
  the capture clone then strips, and it ignores height pins applied via `extra_css`.
- **Impact** — cosmetic but obvious on the exact artifact meant for sharing. No data
  is lost; nothing is cropped.
- **Workaround** — crop the tail by hand, or probe with
  `ANCHOR=bottom ./themes/xprobe.sh page.html page '' tail.png` to see how much to
  cut. Illustrated already opts into the fix (`export_js(measure_clone=True)`), so
  its long image is correct.
- **Why it is not on by default** — `measure_clone=True` was tried as the global
  default on 2026-08-16 and Splash then exported **400 px shorter than its content**
  (出票前待复核 + the end card cropped): the off-screen clone does not lay out like
  the in-document page for every theme. Enabling it per theme requires probing both
  the top of the export and `ANCHOR=bottom`.
- **Source** — `themes/theme_common.py` → `export_js()` docstring, `measure_clone`
  parameter; `themes/render_theme2.py` module docstring (2026-08-16 note);
  call sites `render_clay2.py:1286`, `render_journal.py:1659`, `render_zine.py:1490`,
  `render_splash.py:1645`.
- **Status** — planned

### EXP-2
**The Splash whole-page export deliberately starts at DAY 01 — the cover is not in
it.**

- **Symptom** — `xprobe.sh page.html page '' cover.png` on the Splash theme returns
  a picture whose first screen is DAY 01. The painted hero poster is missing.
- **Cause** — by design. Inside a `foreignObject`, `vh`/`svh` resolve against the
  **whole capture box**, so a `100svh` hero would balloon to the full page height and
  push everything else off the canvas. `extra_css` zeroes it.
- **Impact** — anyone eyeballing the cover from the export will conclude the cover is
  broken. It is not.
- **Workaround** — shoot the live page instead:
  `./themes/xprobe.sh page.html live '' cover.png` (any MODE other than
  `page`/`module` finds no button, prints `NO-BTN`, and still writes a plain
  screenshot of the live page's first 2600 px).
- **Source** — `themes/render_splash.py` module docstring (PNG export paragraph);
  `themes/xprobe.sh` header; `references/themes.md` §6 "Cover check".
- **Status** — open (deliberate trade-off; documented rather than fixed)

### EXP-3
**The Journal cover carries a theme-owned English quote that overlaps the postmark
ring on `zh` pages.**

- **Symptom** — on the cover, the three-line quote
  `the world is a book, and those / who do not travel / read only one page.`
  runs under the postmark ring on wide viewports (the first line reaches x≈1036, the
  ring starts at x=1000).
- **Cause** — the fix exists but is scoped to non-`zh` builds. `CSS_EN` adds
  `@media (min-width:761px) { .cov-side { padding-top:80px } }`; the `zh` stylesheet
  is deliberately frozen byte-for-byte against the US baselines, so it never got the
  same padding. The quote itself is a hard-coded English literal in the markup, which
  means every language — `zh` and the US trip included — renders it.
- **Impact** — cosmetic on the first screen of the `zh` Journal page. Phones stack
  the cover and never collide.
- **Workaround** — none in-product. Editing `.cov-side` for `zh` breaks the
  byte-identical regression gate (`references/themes.md` §4a "zh bytes never move"),
  so the fix has to be made and the US baselines rebuilt on purpose in one change.
- **Source** — `themes/render_journal.py` → cover markup (`.cov-side` / `.covq`,
  ~line 1518), `CSS` (`.covq`, ~line 1939), `CSS_EN` (end of file, ~line 2483).
- **Status** — planned

### EXP-4
**Chinese text survives in CSS/JS comments of English pages.**

- **Symptom** — a bare `grep -o '[一-龥]\{2,\}'` on a rendered `en` page returns 1–4
  hits per theme (Journal 纽约/第一站/秋水长天, Noir 路线地图/插画版, the export
  engine's 渲染引擎不支持 from `theme_common`).
- **Impact** — **none for readers** — every hit is inside a `<style>`/`<script>`
  comment and is never painted. The cost is a permanently noisy i18n leak check.
- **Workaround** — do not use the bare grep. `references/themes.md` §4a ships a
  comment-stripping Python one-liner that prints `no CJK outside comments` on a clean
  page; a hit **from that script** on an `en` page whose plan and art carry no
  Chinese is a real leak.
- **Source** — `references/themes.md` §4a, "The CJK-leak grep, comment-free"
  (verified 2026-08-16 on the Mexico Journal/Noir and Morocco Glass/Portal `en`
  pages).
- **Status** — open

### EXP-5
**The `zh` style-picker page hard-codes US-project history into every trip.**

- **Symptom** — the footnote under the cards on any `zh` picker page reads
  「已放弃:时刻表版(2026-08-08…)、航图版(2026-08-15,视觉不过关)」 — the
  abandonment log of two retired editions of *this project*, printed on a stranger's
  Japan or Morocco chooser.
- **Cause** — the string lives in `L["zh"]["retired"]`. The `en` column already
  neutralises it (`"retired": ""` — the footnote is dropped entirely on `en` pages).
- **Impact** — a leak of internal development history into a user-facing page. No
  functional effect.
- **Workaround** — render the picker with `--lang en`, or delete the `retired` value
  before rendering.
- **Source** — `themes/render_picker.py` → `L["zh"]["retired"]` (~line 65); the
  module docstring already notes "in en … the retired-editions footnote (US history)
  is dropped".
- **Status** — planned

### EXP-6
**Portal has no portrait video chain — the footage is landscape only.**

- **Symptom** — on a phone held upright, the scroll-scrubbed flight plays a 16:9
  landscape frame letterboxed into a tall viewport.
- **Cause** — the whole pipeline is landscape end to end: the US reference chain is
  1344×768 @ 24 fps, and `genvideo.py` defaults to `"resolution": "720p",
  "aspect_ratio": "16:9"`. There is no 9:16 job spec, no portrait seed frames, and no
  portrait branch in the renderer.
- **Impact** — Portal is the weakest of the eight themes on mobile, which is where
  most trip pages are actually read.
- **Workaround** — none. Ship a different theme for a mobile-first audience; Portal
  is already flagged as "the only-when-footage-exists theme".
- **Source** — `themes/render_portal.py` module docstring (FOOTAGE block);
  `themes/genvideo.py` job schema defaults (~line 14, ~line 82);
  `references/themes.md` §2 "portal 穿越".
- **Status** — planned

### EXP-7
**macOS headless Chrome refuses to shrink `innerWidth` below ≈500 px, so the 390 px
acceptance check cannot be done by resizing the window.**

- **Symptom** — `--window-size=390,844` renders a **500 px-wide** layout and
  screenshots its left 390 px. The result looks exactly like a horizontal-overflow
  bug that is not there.
- **Impact** — every narrow-viewport regression read off a naive probe is suspect in
  both directions: false overflow reports, and real 390 px overflow that the probe
  cannot reach.
- **Workaround** — measure inside the page instead of narrowing the window: wrap the
  page in a 390 px container/iframe, or compare
  `document.documentElement.scrollWidth` against `innerWidth` from an injected
  script.
- **Source** — `themes/xprobe.sh` header, "Viewport floor".
- **Status** — open

### EXP-8
**Chrome 151 headless hangs at exit on this machine.**

- **Symptom** — the render work completes, output is written, and the process never
  quits (0 % CPU, forever).
- **Workaround** — already implemented: `xprobe.sh` and `xt.sh` launch each Chrome in
  the background with its own throwaway `--user-data-dir`, poll for the output file,
  then kill **only** that Chrome by matching its unique profile path. A
  `Killed: 9` job line from an older copy of either script is that self-kill, not a
  failure; the title/PNG line is the result.
- **Impact** — never wait on headless Chrome in the foreground, and never run the two
  probes concurrently — each is a full browser and this machine has 8 GB.
- **Source** — `themes/xprobe.sh` / `themes/xt.sh` headers;
  `references/themes.md` §6.
- **Status** — open (environment defect, worked around)

---

### EXP-9
**Zine/splash whole-page export dropped its tail (decisions / colophon / end card).**

- **Symptom** — whole-page long images of prose-heavy pages ended one screen early
  with no error: the China splash page (2026-08-16 first sighting, 1367 × 23412)
  and the Peru zine / Vietnam splash pages (2026-09-01) all lost their closing
  blocks, with the cut landing mid-element.
- **Root cause** — not the area budget, as first suspected: the SVG image used for
  capture lays the same markup out ~5–7% **taller** than the live page (font
  fallback / line wrapping inside an SVG image; CJK prose sections worst, up to
  +40%), and a `foreignObject` clips silently at the `<svg>` height attribute,
  which was sized from the live page's `scrollHeight`. `measure_clone` cannot help:
  it measures HTML layout, and the growth only exists inside the SVG. The clip
  evaded every bottom-anchored probe because a clipped export still ends in
  plausible-looking prose.
- **Fix (2026-09-02)** — the engine rasterises once with 35% headroom, finds the
  lowest inked row on a 64px-wide thumbnail, and sizes the real canvas from that:
  ink at or past the measured height grows the canvas (+140px of paper), ink clear
  of it takes the pre-fix code path (verified: clay/illustrated whole pages and a
  noir day module byte-identical old-engine-vs-new in same-day runs — cross-day
  comparisons jitter from rasterisation nondeterminism alone; zine and splash
  tails complete). Pages rendered before the fix carry the old engine — re-render
  to pick it up.
- **Status** — resolved (`themes/theme_common.py` `export_js`)

---

## Planning scripts and data sources

### PLN-1
**`route_tools.py sun` falls back to a longitude-derived UTC offset when no time zone
is declared — approximate, and with no DST.**

- **Symptom** — output carries `UTC±N (approx from longitude, no DST — pass --tz)`
  and the day is **skipped by `--write`**, with a WARN and a non-zero exit.
- **Impact** — deliberate fail-safe, not silent corruption: an approximate zone is
  printed but never written into the plan. The risk is transcribing the printed time
  by hand and shipping an hour-wrong sunrise across a DST boundary (Morocco returns
  to UTC+0 on 2026-09-20 — a hand-written set of times was an hour off for all ten
  days of a test trip).
- **Workaround** — set `day["tz"]` / `plan["tz"]` to an IANA name, or pass
  `--tz Area/City`. Resolution order: `day["tz"]` > `--tz` > `plan["tz"]` /
  `plan["meta"]["tz"]` > longitude.
- **Source** — `scripts/route_tools.py` → `resolve_tz()` (~line 1003) and the module
  docstring, "Time zone for `sun`"; `references/data-sources.md` §Weather item 4.
- **Status** — open

### PLN-2
**The mainland-China test polygon is coarse; points within ~10–30 km of a land border
can be classified wrongly.**

- **Symptom** — a stop just inside or just outside the border may or may not trigger
  the "Google Maps links are dead in mainland China" warning.
- **Impact** — bounded by design: `in_mainland_china()` gates exactly **one WARN
  line** and nothing else. It is a polygon rather than a bounding box precisely
  because the box used to swallow Hanoi, Ulaanbaatar, Delhi and Chiang Mai (one
  Vietnam run reported "20 stops in mainland CN").
- **Workaround** — for a trip that hugs a Chinese land border, choose the provider
  explicitly: `--provider amap` (or `apple`) rather than relying on the warning.
- **Source** — `scripts/route_tools.py` → `_CN_POLY` (~line 193, "Coarse on purpose
  (~10-30 km at the borders)") and `in_mainland_china()` (~line 385).
- **Status** — open

### PLN-3
**`days[].sun_stop` is a recent addition, exercised only on a synthetic regression
case.**

- **Symptom** — none observed. The field overrides which stop anchors the day's
  sunrise/sunset lookup (default: first stop, or the **last** stop on a moving day).
- **Impact** — the override path — name match, case/width-folded name match, 0-based
  index, and the three WARN fallbacks (unknown name, no coordinates, bool) — has been
  driven by the Morocco F5 test case (a Chefchaouen sunrise before the flight to
  Casablanca) and not by a real booked trip.
- **Workaround** — read the `sun` output: the picked stop is echoed as
  `sun_stop=…` with `(would have been the …)` when it changed the answer. If it
  WARNs, the old rule silently applied and the times belong to a different city.
- **Source** — `scripts/route_tools.py` → `sun` command, `sun_stop` block
  (~lines 1098–1131); `references/scheduling.md` rule 7;
  `references/output-template.md` `days[].sun_stop`.
- **Status** — open

### PLN-4
**`flight_scan.py` scans outbound legs only; return-flight times are a formula, not
data.**

- **Symptom** — round-trip rows show the **round-trip total price against the
  outbound option**. No return-leg times ever appear.
- **Cause** — Google Flights' first results page lists outbound flights only; the
  return leg is chosen on the next page, which the scanner never fetches.
- **Impact** — the departure day of a plan cannot be scheduled from scanned data.
- **Workaround** — two paths, both documented: run the reverse route as `--oneway` on
  the return date (its prices are one-way fares, **not** the round-trip split), or
  write the departure day backwards from a plausible `T` as a re-runnable formula —
  `T = takeoff → T−3 h at the airport (international; 2 h domestic) → T−4 h 30 leave
  the hotel`.
- **Source** — `scripts/flight_scan.py` module docstring, "Round trip" bullet;
  `references/scheduling.md` §Departure day.
- **Status** — open

### PLN-5
**No keyless hotel API exists, so hotels are neighbourhood bands plus deep links.**

- **Symptom** — the plan recommends areas and emits dated Booking / Google Hotels
  deep links instead of quoting a nightly price.
- **Impact** — the budget line for lodging is a band, not a quote; the traveller has
  to click to get a number.
- **Workaround** — none, and this is preferred over a price the tool cannot verify.
  `AMADEUS_KEY` / `SERPAPI_KEY` are recognised if the user already has them, but the
  skill never asks for a signup mid-plan.
- **Source** — `references/data-sources.md` §Hotels; `README.md` (source table note).
- **Status** — open

### PLN-6
**Nominatim is rate-limited to 1 req/s and fails quietly on non-Latin place names.**

- **Symptom** — a station or lane resolves to a similarly named place a few hundred
  metres away, with no error. Weakest on Japanese, Chinese, Korean and Thai.
- **Impact** — a silently wrong coordinate poisons the hop distances, the walking
  total, the map deep links and the KML.
- **Mitigations in place** — `route_tools.py geocode` enforces the usage policy
  (User-Agent, 1 req/s throttle, cache) and WARNs when the resolved `display_name`
  does not contain the query's head token. Never call Nominatim in parallel or
  outside the script.
- **Workaround** — for well-known venues in those countries, pre-fill `est`
  coordinates by hand from the Google Maps place card. **A trip with zero Nominatim
  requests is a normal, healthy outcome**, not a shortcut.
- **Source** — `references/data-sources.md` §"Geocoding & day-route sanity".
- **Status** — open

### PLN-7
**frankfurter.dev covers ~30 currencies and fails open; the fallback is a second
external service.**

- **Symptom** — an unsupported symbol does **not** error. The call returns HTTP 200
  and the `rates` object simply lacks the key (`symbols=VND,USD` → `{"USD": …}`
  alone).
- **Impact** — a script reading `rates[DEST]` blindly picks the wrong currency
  (Vietnam) or ships no rate at all (Morocco). Missing: MAD, VND, EGP, TND, DZD, KHR,
  LAK, LKR, NPR, UZS and more.
- **Workaround** — the mandated sequence is in `SKILL.md` and the data-source doc:
  assert the destination key is present → on miss fall back to
  `https://open.er-api.com/v6/latest/{HOME}` (~160 currencies, daily) → check the key
  there too → record which source was used in `meta.fx`.
- **Residual risk** — the fallback is a second unaffiliated free service with no SLA;
  if both are down there is no FX line.
- **Source** — `references/data-sources.md` §FX.
- **Status** — open

### PLN-8
**date.nager.at lists fixed-date secular holidays only — religious and lunar
holidays are absent.**

- **Symptom** — `2026/MA` returns 10 rows, every one a fixed civic date, **zero
  Eids**. The same gap hits Buddhist-calendar holidays (Vesak, Asalha Puja, Khao
  Phansa) in Thailand, Laos, Myanmar and Sri Lanka, and the Lunar New Year cluster
  across East and Southeast Asia.
- **Impact** — the single largest closure/crowd event of a trip can be invisible to
  the holiday check.
- **Workaround** — spend one budgeted search on the country's official gazette or a
  religious-holiday calendar for that year, and put the dates in `brief.holidays`
  with the source. Eid dates are moon-dependent and published as "expected" until
  ~1 day before — mark them ± 1 day.
- **Source** — `references/data-sources.md` §"Public holidays".
- **Status** — open

---

## Assets and generation

### AST-1
**`towebp.py` turns an un-cut PNG into a white square, with no error.**

- **Symptom** — a cut-out slot (sticker, island, figurine, terrain band, stamp, prop,
  title plate) fed `towebp.py x.png --sizes md` gets an opaque `<stem>.md.webp` that
  renders as a white rectangle on the page. Exit code 0, no warning.
- **Cause** — the tool branches on alpha: RGB input → `<stem>.webp` (opaque), RGBA
  input → `<stem>.cut.webp`. A PNG that was never cut out has no alpha, so the opaque
  branch is correct behaviour for the tool and wrong for the slot.
- **Impact** — first hit on the Vietnam splash `hero.art` (F7). Only visible by
  looking at the rendered page.
- **Workaround** — run `cutout.py x.png` **first**, then `towebp.py x.cut.png
  --sizes …`. Which slots are cut-outs and which are opaque is the **"shape" column**
  of the size table in `ART-SCHEMA.md`; an opaque slot (photo, plate, poster, cover
  painting) must **not** go through `cutout.py` — it would eat the sky.
- **Source** — `themes/ART-SCHEMA.md` §Image toolchain (图片工具链) (~lines 632–682, 601) and the
  per-theme size table; `themes/towebp.py` docstring (Naming block);
  `themes/README.md` (asset pipeline paragraph).
- **Status** — open

### AST-2
**Folding a test trip's assets back into the shared library is a manual merge —
`build_manifest.py` must not be used for it.**

- **Symptom** — running `build_manifest.py` during a reclaim scrambles the job↔PNG
  relationships, because it scans job files against `themes/assets/` while the trip's
  jobs and PNGs still live in `trips/<trip>/`.
- **Impact** — a corrupted `manifest.json` is the authoritative cost/prompt record
  for 181 entries and ≈$6.57 of generation; it is not cheaply reconstructible.
- **Workaround** — the documented reclaim: copy the webp variants
  (`.sm/.md/.lg/.cut/.band/.strip`) into `themes/assets/`, merge the trip manifest
  entries into `manifest.json` **by hand** in the library's schema (adding
  `source_job` / `trip` / `note`; `files` records only the webp actually copied),
  append a section to `IMAGE-LIBRARY.md`, sync its generic pieces into §12, then
  validate with a `python3 -c` check of JSON validity, entry count and the `cost_usd`
  sum. `build_manifest.py` remains fine for its own job: refreshing the index in
  place after generation inside `themes/assets/`.
- **Note** — testers and ordinary users never write into `themes/assets/` or
  `IMAGE-LIBRARY.md` at all; `trips/<trip>/manifest.<trip>.json` is their record.
- **Source** — `themes/assets/IMAGE-LIBRARY.md` header, "How test-trip assets are folded into this library"
  (2026-08-16), bullets 2–3; `themes/build_manifest.py` docstring;
  `themes/README.md`.
- **Status** — open

### AST-3
**Generating new images or video requires an OpenRouter key — unless the agent can generate natively.** (Since 2026-08-16 the docs say: an agent with its own image/video generation uses it directly, no key; `gen.py` / `genvideo.py` are the fallback for environments without one — ART-SCHEMA.md §Generator choice.)

- **Symptom** — without `themes/.auth_header` (one line `Authorization: Bearer <OpenRouter
  key>`, passed to curl as a header file), `gen.py` and `genvideo.py` cannot run.
- **Impact** — a trip whose destination scenery is not already in the library cannot
  get its cover, hero, title sticker, terrain band, noir plate or splash island —
  and those slots are explicitly **never** reused across trips (a China page opening
  with a New York skyline band was logged as a defect).
- **Workaround** — **stock mode** (2026-08-17): `themes/stock_art.py` fills the picture
  slots from the built-in stock kit (`themes/assets/stock/`) plus the shared library's
  same-country pictures and generic props, so a keyless session still delivers a themed
  page instead of a plain one — with the one-line notice that the pictures are stock. Its
  coverage is uneven (AST-7) and its style is illustrated-only (AST-8). Needs no key, no
  Pillow and no network. Or supply a key. Credentials are read from `themes/` only, are
  gitignored, are never copied into a trip folder and are never printed. Generation costs
  money and needs the owner's approval.
- **Fixed in part, 2026-08-17** — the *deliverable* consequence is closed. Before this
  date, no native generator + no key meant the user got the plain `render_plan.py` text
  page; SKILL.md Phase 0 now runs a picture-capability check (`prefs.pictures` =
  `native|key|stock`) and Phase 6 states that a plain text page is never the deliverable.
  What stays open is the line above it: *generating* new pictures still needs either a
  native generator or a key.
- **Source** — `themes/gen.py` docstring (credentials paragraph);
  `themes/README.md` §"Not in the repo"; `README.md` §Requirements;
  `SKILL.md` Phase 0 (picture-capability check) + Phase 6; `references/themes.md` §3b.
- **Status** — open (narrowed 2026-08-17)

### AST-4
**The cloud path for Portal footage has been smoke-tested on a single 4-second clip;
the full chain is built on the author's local GPU.**

- **Symptom** — none at runtime. `genvideo.py`'s only live verification is one
  first-frame clip on 2026-08-15: 4 s, 65 s wall clock, $0.12, 1280×720 h264.
- **Impact** — the "one key for anyone" path is unproven at chain scale (10 dives +
  9 frame-chained links, ≈$3 on `google/veo-3.1-lite`). Frame-chaining, seam
  continuity and per-model duration constraints across a whole reel are untested
  through this route. Reproducing the shipped quality currently means running
  ComfyUI/MiniMax-H3 on a local 5090 via `build_portal_jobs.py` — a high bar for an
  outside contributor.
- **Workaround** — `--dry-run` first (nothing sent, nothing charged), then generate
  one dive and inspect it before committing to a chain. Existing `<name>.mp4` files
  are skipped, so a chain can be built incrementally.
- **Source** — `themes/README.md` §"Video clips (portal theme)";
  `themes/genvideo.py` docstring; `references/themes.md` §2 "portal 穿越".
- **Status** — open

### AST-5
**Zine's `cover.zh` is a vertical column with a hard 2–4 glyph ceiling.**

- **Symptom** — a fifth CJK glyph, or a Latin word longer than four letters, clips
  off the bottom of the page.
- **Cause** — `.cv h1 { writing-mode:vertical-rl; font-size:clamp(96px,19vw,196px) }`
  with **no** character-count tier (unlike Journal's four auto-sizing tiers). Four CJK
  glyphs are already ~784 px tall on desktop.
- **Impact** — silent overflow: the page renders, the title is cut.
- **Workaround** — pick a 2–4 glyph cover word (人海 / KOYO are the right size); a
  longer allusion goes in `cover.credit`, which every theme prints small. The same
  value is reused as the `<zh> ZINE` issue name, so keep it short for that too.
- **Source** — `references/cover-titles.md` §"Latin character budgets per theme"
  (zine bullet); `themes/render_zine.py` ART CONTRACT (`cover.zh`) and `.cv h1` CSS
  (~line 910).
- **Status** — open

### AST-6
**A top-level plan section of the wrong type warns instead of failing, and the cells
render blank.**

- **Symptom** — the page builds, exit code 0, and a whole section (legs, hotels,
  budget, checklist…) comes out empty. On stderr:
  `WARN plan.<key>: expected list of objects, got dict — …` or
  `WARN plan.<key>: no row carries any of the expected keys (…) — every cell will
  render blank`.
- **Cause** — deliberate. `norm_plan()` type-normalises every section in place and
  substitutes a usable fallback (a dict is salvaged from its first list-of-objects
  value, a stray string becomes a one-item list, anything else becomes empty; non-
  object rows are dropped) so a malformed plan never produces a traceback mid-render.
- **Impact** — the failure is loud on stderr and invisible in the artifact. In a
  pipeline that swallows stderr, a blank hotels table looks like an authoring
  omission.
- **Workaround** — **read stderr on every render.** `assets/plan.example.json` is the
  runnable source of truth for the shape; `references/output-template.md` documents
  every key. A plan that already has the right shapes passes through untouched with
  no WARN and byte-identical output.
- **Source** — `themes/theme_common.py` → `PLAN_SHAPE` / `norm_plan()`
  (~lines 286–360); `assets/plan.example.json`; `references/output-template.md`.
- **Status** — open

### AST-7
**Stock mode covers illustrated completely and clay partially; the other six themes
still need generated pictures.**

- **Symptom** — `prefs.pictures = "stock"` (no native generator, no key) with a theme
  other than illustrated or clay: `stock_art.py` has nothing to put in that theme's own
  picture slots, so noir/glass plates, journal photos and stamps, zine prints, splash
  islands come out empty, and portal has no footage at all. The page renders — every
  renderer must survive an empty art file — it just loses the images that carry it.
- **Cause** — the kit is a **finite** set of region cover paintings and landmark /
  generic-scene cut-outs. Illustrated's slots (cover painting, per-day cut-out hero,
  feature card) map onto exactly that; clay works because its terrain bands come from the
  built-in neutral SVG kit (`ridge|plain|coast|forest|lake|desert`) rather than from
  pictures, with generic clay props on top. The remaining six are built around
  photographic plates or per-theme illustrated objects that no generic library can stand
  in for — and their scenery slots are the ones explicitly never reused across trips
  (AST-3).
- **Impact** — a user in a keyless session who names one of those six gets a visibly
  thinner page than the showcase, for a reason that is not their fault.
- **Workaround** — in stock mode, offer **illustrated** (the default) or clay, and say
  plainly that the other six need an image generator or a key. Do not render one of the
  six "anyway" without telling the user what they will get.
- **Source** — `SKILL.md` Phase 0 (picture-capability check, last bullet) + Phase 6
  (stock branch); `references/themes.md` §3b (Coverage today); `themes/ART-SCHEMA.md`
  §"Authoring a new trip's art" step 2b; `themes/stock_art.py` (`--theme` accepts
  illustrated and clay).
- **Status** — open

### AST-8
**The stock kit is drawn in one style — illustrated. There are no per-style stock
packs.**

- **Symptom** — nothing at runtime; it is why AST-7 exists. Every picture in
  `themes/assets/stock/` is painted in the illustrated theme's visual language, so it can
  only ever stand in for slots that suit that language.
- **Cause** — deliberate scope for the first version (2026-08-17): one style, complete,
  for the default theme, rather than eight styles half-done. Each additional pack is a
  separate generation batch with its own style anchor (a riso pack for zine, a night
  photographic pack for noir, a clay-prop pack, …), and each costs money and review time.
- **Impact** — the ceiling on stock mode is a design decision, not a bug, but it means
  "themed page without a generator" effectively means "illustrated page" today.
- **Workaround** — none needed for illustrated. For another style, supply a native
  generator or a key and generate for the trip, which is better art in any case.
- **Future work** — a per-style stock pack, one style at a time, each following the same
  contract as the illustrated kit (`stock/index.json` entries + `stock/README.md` row +
  the same webp/cut-out shapes the theme's size table asks for, `themes/ART-SCHEMA.md`).
  Not on the [Roadmap](#roadmap) yet — no fix scheduled.
- **Source** — `themes/assets/stock/README.md`; `references/themes.md` §3b;
  `SKILL.md` §Bundled resources (`themes/assets/` and `themes/stock_art.py` entries).
- **Status** — open

### AST-9
**A stock-mode render that forgets `--assets themes/assets/stock` drops the stock
pictures without any error.**

- **Symptom** — the render exits 0, `qc.py` returns `PASS`, and the page simply has
  fewer pictures: the summary line's `assets=N` is lower, with no WARN naming a
  missing file. Measured on the Japan example (2026-08-17): without the flag
  `no.html: 1014KB, days=8, assets=17`; with it
  `yes.html: 1422KB, days=8, assets=26`. Every stem `stock_art.py` resolved out of
  `themes/assets/stock/` is silently blank; only the stems that happen to live in
  `themes/assets/` itself survive, which is why a trip to a country the shared
  library already covers looks almost right and a trip to one it does not looks
  gutted.
- **Cause** — `theme_common.data_uri()` searches the `--assets` dirs, the art file's
  directory, the plan's directory and `themes/assets/`, and it does **not** recurse
  into sub-folders of any of them. `themes/assets/stock/` is a sub-folder, so it is
  never reached unless it is passed explicitly. A stem that resolves nowhere returns
  `""` rather than raising — the same fail-soft rule that lets an empty art file
  render.
- **Impact** — the failure is invisible to both gates a user would think to run
  (exit code, `qc.py`), so a keyless session can ship a visibly thin page believing
  stock mode did not work at all.
- **Workaround** — paste the render command `stock_art.py` prints on its last stderr
  lines, which already carries the flag and the reason; or simply always pass
  `--assets themes/assets/stock` on a stock render. To check after the fact, compare
  `assets=N` against a run with the flag.
- **Source** — `themes/theme_common.py` → `data_uri()` (~line 210) and
  `add_asset_dir`; `themes/stock_art.py` → the `next:` block at the end of the stderr
  summary (~line 780); `themes/README.md` §Where pictures come from;
  `themes/assets/stock/README.md` §"How the skill uses it"; `SKILL.md` Phase 6
  (stock branch).
- **Status** — open

---

### PLN-9
**A stop geocoded to the wrong place is only caught when it lands far away.**

- **Symptom** — on the 2026-09 São Paulo → Kenya test, "Nairobi city center hotels"
  resolved to Kisumu (257 km away); the planner wrote `"mode": "transit"` on the hop
  and `check` exited 0, so the KML, the day-1 sunrise point and the walking total were
  all wrong with every light green.
- **Mitigations in place** — `route_tools.py check` now flags a DECLARED transit /
  walk hop longer than 60 km as SUSPICIOUS (exit 2) — a city ride does not cross 60 km,
  so the stop is mis-geocoded or the ride is a train / bus / boat / drive / fly that must
  say so; `geocode` already WARNs when the hit's `display_name` lacks the query's head
  token. A wrong hit *inside* 60 km (the next suburb, a same-name street) still passes.
- **Workaround** — read `geocache.json`'s `display_name` for every stop of a day
  before `sun --write`, and hand-fill coordinates from the Google Maps place card for
  anything that names another town; never keep a `mode` that only exists to silence
  the flag (SKILL.md Phase 4 gate; phase-4-days.md step 6).
- **Source** — `scripts/route_tools.py → hop_estimate` (DECLARED_CITY_MAX_KM),
  `cmd_geocode` (head-token WARN). **Status:** open — the fix is comparing the hit's
  city / county token with the day's `city` and exiting non-zero on a mismatch.

### PLN-10
**The exit-code gates are advisory — a renderer runs whether or not they passed.**

- **Symptom** — on the 2026-09-05 São Paulo → Kenya re-run (PR head, clean worktree,
  Haiku) the tester ran `plan_lint --strict` (exit 6: two `TBD` placeholders,
  `meta.self_check` still "pending", no T-1 row, no self-check `decisions[]` row) and
  `route_tools check` (exit 2: a real Wilson → Seronera flight with no `mode: fly`),
  fixed the two items a single command could fix (`gates.ics`, the art file), and
  rendered both themes with the other four FAILs in place; `qc.py` exited 0 on both
  pages and the summary said "all phases complete".
- **Mitigations in place** — the text says "exit 0 before rendering" in four places
  (SKILL.md Phase 4 and Phase 6 gates, phase-6-assemble.md Deliver and exit criteria);
  a weak model reads it as advice.
- **Workaround** — run the three gates yourself before opening a page from a plan you
  did not write: `route_tools check`, `plan_lint --strict`, `qc.py` after.
- **Source** — `themes/render_theme2.py`, `scripts/render_plan.py`, `themes/theme_common.py`.
  **Status:** open — the fix is for the renderers to call `plan_lint --strict` and
  `route_tools check` themselves and refuse on a non-zero exit, with an
  `--allow-failing-gates` escape hatch that watermarks the cover and the fine print
  ("content gates: N FAIL"), writes `_gates_failed` into the art file, and makes
  `qc.py` non-zero on a watermarked page. Note the conflict to resolve first: the seven
  `examples/` predate the 2026-09 brief contract and fail `--strict` by design, so the
  enforced level for them is the default checks, or their briefs are re-authored.

### PLN-11
**`plan_lint --strict` does not look at the four defects that were heaviest on the re-run.**

- **Symptom** — same run: `lang: zh` with 43 of 43 timeline rows, all nine brief
  cards, legs, hotels and budget categories in English (0 FAIL); brief lines with no
  source, a `visa` as-of dated in the future (2026-11-01 on a plan generated
  2026-09-05) and `money` sourced to "local knowledge" (0 FAIL); four days with
  `stops: []` and therefore no `sun` (the non-zero `sun --write` exit was ignored; 0
  FAIL); no `trip.kml` beside the plan (0 FAIL, while the `.ics` is checked).
- **Mitigations in place** — the existence / order / placeholder / self-check /
  ladder checks; `sun --write` exits non-zero on skipped days.
- **Workaround** — read the page in the user's language for thirty seconds; grep the
  plan for `"sun"` per day and for a `Source` / `as-of` on every brief line.
- **Source** — `scripts/plan_lint.py`. **Status:** partly resolved (2026-09-05) — the
  `trip.kml` check (WARN by default, FAIL under `--strict`, the `.ics` rule) and the
  per-day checks (at least one stop; `sun` is the canonical `sun --write` string)
  landed. Still open under `--strict`: a CJK ratio over reader-facing fields when
  `lang` is zh (FAIL under 80 %), and a source + as-of on every brief line with as-of
  ≤ the generation date and no "memory" / "local knowledge" source. Also open: polar
  day / night — `sun --write` refuses such a day (exit 3) and writes nothing, so the
  per-day `sun` check has no passing shape for Tromsø in December; the fix is for
  `cmd_sun` to write a canonical polar string and for the lint to accept it (and to
  raise the polar test above the time-parsing block — today an API reply with
  unparseable times on a polar day is rejected as "unparseable times" without the
  "polar day/night" words the docs key on). Until then: remove that day's `sun` key
  (absent — not `null`, not `""`), note it, render with exactly those FAIL lines and
  name the dates in the chat summary (phase-6-assemble.md Deliver / exit criteria).

### PLN-12
**Four small text and tool items from the 2026-09-05 pair of end-to-end runs.**

- **Mode wording** — SKILL.md's Phase 4 gate says a SUSPICIOUS hop is "never …
  silenced with a mode" while `check`'s own hint says "declare mode fly/drive/… if
  intended"; one tester silenced a mis-geocoded hotel with `mode: transit`, the next
  left a real flight undeclared and shipped exit 2. The sentence should separate the
  two cases: a vehicle really runs the hop → declare its mode on the arriving stop and
  have a `legs[]` row for it; nothing runs it (a 250 km hop inside one city is a
  geocoding error) → fix the stop, never the mode.
- **`fast-flights` under PEP 668** — `pip3 install --user fast-flights`
  (data-sources.md §Flights, the `flight_scan.py` import-failure hint) is refused by
  Homebrew / Debian Python ("externally-managed-environment"); the line needs the
  `--break-system-packages`, `venv` or `pipx` variant, or a weak model declares the
  scanner uninstallable and prices every leg from one web search.
- **Origin → hub** — both trees put "São Paulo" at GIG (Rio's Galeão); the Phase 0
  rule "pick that country's main international hub" wants a short city → hub table
  for the departure cities that recur (GRU · GIG · EZE · MEX · PVG · PEK/PKX · CAN ·
  SZX · HKG · TPE · SIN · …).
- **Cover-title fallback** — with the art placeholders unfilled both pages titled
  themselves "旅程" although `plan.trip` carried a real title; the fallback chain
  should be `art.cover.zh` → `plan.trip` → "旅程" (and the `<title>` likewise),
  without changing lint's FAIL on the unfilled placeholders.
- **Status:** the first three resolved 2026-09-05 (the Phase 4 gate, phase-4-days.md and
  `check`'s own hint now separate the two cases; the install line carries the PEP 668
  variants; phase-0-intake.md lists the common hubs); the cover-title fallback stays open.

## Method and scope

### SCO-1
**Personal-use posture — the data path is not licensable as a hosted service.**

The browser and scraping steps are exactly what one traveller would do by hand, at
one traveller's pace (`flight_scan.py` sleeps between fetches and caps total fetches;
Nominatim is throttled to 1 req/s). None of the free sources here are licensed for
redistribution. Turning this into a product for other people needs affiliate rails —
Travelpayouts, an Amadeus production key, Viator/GetYourGuide APIs — not more
scraping. **Source:** `README.md` §"Limitations and non-goals". **Status:** planned

### SCO-2
**Not real-time.** It plans; it does not track delays, gate changes or cancellations,
and it never rebooks. Every price and hour carries an as-of date for that reason, and
the skill never books, pays, holds, or enters personal data anywhere — it emits deep
links and a deadline-sorted checklist. **Source:** `README.md` §"Limitations and
non-goals", rule 1; `SKILL.md` rule 1. **Status:** open

### SCO-3
**Beyond ~3 months out, nobody publishes that day's opening hours.** The plan
verifies the **seasonal pattern plus the closure rule** (weekly closing day, seasonal
schedule change, known annual shutdown), stamps "as of {date}", and puts a re-confirm
task on the checklist instead of claiming a certainty it cannot have. Treat any
exact-to-the-minute hour for a far-future date as a modelling error.
**Source:** `README.md` rule 5; `SKILL.md` Phase 4 (~line 208);
`assets/plan.example.json` (the second checklist row is exactly this task).
**Status:** open

### SCO-4
**Name settled (2026-08-16): `trip-planner-skill`.** A descriptive name was chosen
over a coined brand on purpose ("trip" = one specific journey, which is the unit this
skill plans; "travel" is the domain word and stays in the description/topics): the repo
is `skywain/trip-planner-skill`, the skill directory / slash command is `trip-planner`,
and the SKILL.md `name:` is `trip-planner`. Known cost: a handful of other GitHub repos
carry the same name (all ≤2★, single-day commits) — discoverability therefore leans on the repo
description, topics (`claude-skill`, `claude-code-skill`, `agent-skills`, `travel`,
`travel-planner`, `trip-planner`, `itinerary`, `itinerary-planner`, `travel-itinerary`,
`flight-search`, `kml`) and the README's first screen, all of which carry the
trip / travel / itinerary keywords in both languages.
**Source:** `README.md` line 3; `SKILL.md` front matter. **Status:** resolved

---

## Roadmap

Short list, roughly in the order the work makes sense:

1. **Whole-page export sizing, per theme** — probe `measure_clone=True` on Clay,
   Journal, Zine and Splash individually, at both `ANCHOR=bottom` and the top of the
   export, and opt each one in only when both ends are clean (EXP-1).
2. **Journal cover quote fix** — move the `.cov-side` padding out of `CSS_EN` into
   the shared stylesheet and rebuild the US `zh` baselines in the same change
   (EXP-3).
3. **Picker copy neutralisation** — drop the US retired-editions footnote from the
   `zh` column (EXP-5).
4. **Portal portrait chain** — 9:16 seed frames, a portrait job spec in
   `genvideo.py` / `build_portal_jobs.py`, and a renderer branch that picks the chain
   by viewport (EXP-6).
5. **Photo album (post-trip) MVP** — the return trip of the same data: the plan
   becomes the spine a traveller hangs their own photos on.
6. **Affiliate rails for a hosted version** — the only route from personal-use
   posture to something usable by other people (SCO-1).
7. **Publishing** — name is settled (SCO-4); on the first push set the repo description and the topic list from SCO-4, then submit the awesome-list entries.
