# Themed renders — the manual

Read this before rendering any theme, and all of it before touching a renderer.
Written for an AI that meets the theme system for the first time. **A themed page is
the deliverable** — SKILL.md Phase 6: the plan ships as `trip-<theme>.html` in the theme
chosen at Phase 0 (`prefs.theme`, default **illustrated 插画版**) plus `trip.kml`, and a
plain text page is never what the user gets. The plain `scripts/render_plan.py` page is
an **extra** — the printable version on request, or the last resort after one honest fix
attempt at the theme renderer. A session with no image generator and no key does not
fall back to that plain page either: it renders a theme from the built-in stock kit
(§3b).

## 1. The model in one paragraph

A themed page = **plan** (`plan.geo.json`, the facts) + **art** (`plan.art.json`, what
this trip looks and sounds like in a theme: titles, captions, which pictures) +
**renderer** (`themes/render_<x>.py`, the theme's craft — layout, type, colour,
motion; it knows nothing about any particular trip). The one rule for what goes
where: *anything that names this trip's places, dates, people, jokes or picture
files lives in art.json; the theme's own vocabulary (its tape kit, stamp mechanics,
doodle sketches, layout rhythm) stays in the renderer as a named kit that art picks
from and supplies words to.* Every art field is optional and every renderer must
produce a usable page from an empty art file — never a crash, never a line that
belongs to another trip. The full field contract is `themes/ART-SCHEMA.md` (the only
authoritative copy; `references/art-schema.md` just points there).

Commands (all relative to the skill root):

```
python3 themes/render_<x>.py plan.geo.json [--art F|none] [--assets DIR ...] -o out.html
python3 themes/qc.py out.html                       # exit code = number of FAILs
themes/xprobe.sh out.html module '#d5' out.png      # click the real export button, rasterise it
themes/xprobe.sh out.html page   ''    out.png      # whole-page export (ANCHOR=bottom → last 2600px)
themes/xt.sh    out.html module '#d5'               # title-only probe, ~15 s, no picture
python3 themes/render_picker.py plan.geo.json -o picker.html [--products DIR] [--prefix NAME]
    # the style-chooser page; expects the eight pages as {prefix}-{theme}.html
    # with the English theme key (japan-illustrated.html; pages exported under
    # the old Chinese tag — e.g. -插画版.html — still resolve). prefix defaults
    # to cover.kick_en with spaces→"-"
```

Assets are looked up by `theme_common.data_uri(stem, size)` in this order: every
`--assets DIR` (later wins) → the art file's directory → the plan's directory →
`themes/assets/`. So a trip keeps its own webp beside its plan and copies nothing
into the library; prefix trip assets with the trip name (`au-…`, `nordic-…`) so a
library size-variant can never shadow them. Only webp is ever embedded (as data
URIs — pages open by double-click, zero fetches); png originals never enter a page.

## 2. The eight themes

Each theme is a different *species*, not a re-skin. The four axes that keep them
apart (a new theme has to answer all four differently): organising principle ·
interaction · type voice · shape language. Renderer docstrings carry the full ART
contract; this is the field guide.

### illustrated 插画 — `render_theme2.py`
- Paradigm: a **painted book on paper** — one long paper scroll, full-width colour
  bands between chapters, pictures as the page's background rather than framed cards.
- Voice/shape: **zero monospace**, serif with lining numerals; no capsules — 〔square
  bracket〕 annotations, underlined pinned items, footnote `[n]`, printer's rules;
  page-edge bookmark tabs as navigation.
- Art (`themes.illustrated`): `cover.zh/en/credit/sub`, `cover.hero` (full-bleed
  cover painting), `end.hero` (endcap cut-out) + `end.fine`, `days[d].hero` (one
  cut-out stem, inlined as sm/md/lg into menu card / plate sticker / faint backdrop),
  `days[d].feature` (wide menu card). Kit: paper palette, four plate tints cycled by
  day, sticker tilt and backdrop side alternating by day parity.
- Limits: the fine print prints the full date, so `end.fine` is overridden per theme.

### clay 黏土 — `render_clay2.py`
- Paradigm: **one continuous clay landscape** — a road runs the whole page and is
  anchored to the milestone stones; terrain bands (cut-out strips with negative
  margins) and chained gradients make chapters bite into each other.
- Voice/shape: hand-pinched irregular radii (the same curve as the stones); the
  signature only clay can do — a **mini-road navigator** (the world path redrawn into
  300×44, stones are the hit areas).
- Art (`themes.clay`): `cover.zh/sub`, `cover.title_stem` (3-D clay title sticker;
  absent → embossed text h1), `zones` (`from_day` = day number or ISO date, `kind` ∈
  the neutral SVG kit ridge|plain|coast|forest|lake|desert, or `custom` with your own
  `{band, to, decor}` — the copy-able three-zone recipe is in ART-SCHEMA's clay block;
  city|park|west|isle are the US-2026 bands), `days[d].figurine`. Every clay picture
  slot is a cut-out.
- Limits: `zones` is where the terrain changes; an unknown kind falls back to ridge
  with one stderr warning.

### noir 夜航 — `render_noir2.py`
- Paradigm: **one unbroken tracking shot** — a single sticky 100svh night negative;
  days scroll over it, the plate cross-dissolves only inside the hop interstitial
  between two days; a travelling amber glow tracks trip progress; titles are burned
  into the negative (`mix-blend-mode:overlay`) and glide aside as body text arrives.
- Voice/shape: **monospace as body**, serif only for the giant title (the inverse of
  illustrated); no boxes — hairlines and letterspaced labels; bottom numbered rail.
- Art (`themes.noir`): `cover.zh/en/credit`, `plates` (stems in reel order, `[0]` =
  cover), `day_plate` (`{"<ISO date>"|"<day no>": plate index}`; date keys survive
  inserting a day). No plates → flat gradient, no photos, no AI credit line.
- Limits: **module-only export** (day / appendix blocks; a sticky stage cannot be
  flattened into a whole-page image).

### glass 玻璃 — `render_glass2.py`
- Paradigm: **Liquid Glass** — frosted glass panes floating over a fixed world of
  photographs that cross-fade by zone (IntersectionObserver zone spy).
- Voice/shape: capsules (it is an app), the focus ring is itself a pane of glass;
  glass rail → floating dock on mobile. Recipe: low blur (8–10px) high saturate,
  directional inset specular stack, `feImage` displacement lens (Chromium only,
  gated), one glass never on top of another.
- Art (`themes.glass`): `cover.zh/en/credit`, `plates` (`[0]` hero, last = appendix
  backdrop), optional `zones` (slugs, internal), `day_plate` as in noir.
- Limits: **module-only export**; `backdrop-filter` does not survive `foreignObject`,
  exports use a solid semi-opaque stand-in (clean but not glassy — accepted).

### journal 手账 — `render_journal.py`
- Paradigm: **a vintage travel journal lying open on a dark desk** — the book is an
  object (page-edge shadow stairs, curled corner, foxing), one continuous sheet of
  aged paper, a fountain-pen route down the spine, brass push-pins as navigation.
- Voice/shape: Kaiti handwriting for titles/annotations, typewriter for clock digits,
  Caveat (embedded OFL webfont) for English asides; torn edges, washi tape, ticket
  stubs, postage stamps, postmarks, wax seal; blocks rotate ≤1°.
- Art (`themes.journal`): `cover.zh` (auto-sized h1: 2–3 chars full size, ≥7 shrunk
  to one line) / `sub` / `credit` / `photo`, `cover_stamps` (≤3), `stamps` (slot →
  scan: `st-a`/`st-b` portrait, `st-wide` landscape), per day `photo`, `caption
  [main, aside]` (two type slots — Kaiti line + Caveat aside — not two languages),
  `annot`, `props` (kit: img · stamp · vtk vintage ticket · bagtag · seal
  · flora · postcard), `doodle` (`sketch` from 12 kit drawings or your own `svg`, +
  `note` ≤2 lines × ≤18 chars, break by hand with `\n` — the box does not wrap),
  `photos2`, `poster` (stem, or `title` for the CSS kraft poster).
- Limits: a pure-CJK doodle note without `\n` was once a one-glyph column; large
  reveal animations were removed for performance — do not add them back.

### zine — `render_zine.py`
- Paradigm: **paper-poster zones** — real photographs as anchors, colour blocks as
  structure; the cover alone is a solid flood, inner pages return to cream paper
  with a torn colour band per chapter head; giant vertical riso two-colour glyphs.
- Voice/shape: structured sans + DIN print numerals; torn edges and flat blocks —
  anti-card, anti-radius; left-edge torn ticket index 01–NN.
- Art (`themes.zine`): `cover.zh` (vertical glyphs — 2 by design, 4 the ceiling) /
  `en` / `credit` (printed on the cover since 2026-08-16) / `photo` (torn cover print,
  `tear_seed`; its `caption` is a "PLACE · CITY" caps side line, not the poem's source),
  `toc_strip`, `props` (colophon paper props by section), per day `poster`,
  `photo` (`treat: mono`), `pair` (two overlapping prints), `sticker`, `band`
  (full-bleed closing photo), `lineart` (kit sketch name or `{svg}`).
- Limits: kit rule — on a poster day the print takes the poster's opposite side and
  is emitted **after** the timeline (defect ⑨ below); write floats as `-1.0`, they
  are emitted verbatim.

### splash 闪屏 — `render_splash.py`
- Paradigm: **a game splash screen stretched into a scroll** — 13 chapters of
  180° gradients chained end-to-start into a day/night narrative, floating islands
  per day, seeded particles, side floaters at two depths, ribbon road per chapter.
- Voice/shape: thick-painted title plate + round 900 weight, brush-feel big
  numerals; bold silhouettes and bevelled solid badges, zero white rounded cards.
- Art (`themes.splash`): `cover.zh/sub`, `hero.palette` (kit mood name) / `title` /
  `art` / `sides`, `appendix.palette`, `vehicles` / `mascots` / `strips`
  registries (`stem` + `ratio`), per day `palette`, `island`, `fx` (kit words),
  `vehicle` / `mascot` (`kind` + inline `pos` — safe ranges and the `ratio` = real
  `.cut.webp` w/h rule are in ART-SCHEMA's splash block), `strip`, `sides`.
- Limits: unknown palette → index rhythm; a registry entry whose file is missing
  emits no CSS class and its days draw nothing; contrast report prints at build.

### portal 穿越 — `render_portal.py`

Footage can come from the agent's **own native video generation** if it has one (no key; 16:9 h264 mp4 24 fps, dive 5–6 s / link 4 s, first/last-frame conditioning for links — ART-SCHEMA.md 「生成器选择」), from `themes/genvideo.py` (OpenRouter video API, same key as `gen.py`; first/last-frame conditioning; ≈$3 per ten-world chain on `google/veo-3.1-lite`, `minimax/hailuo-3` for quality), or from the local ComfyUI/MiniMax-H3 pipeline (`build_portal_jobs.py`, free).
- Paradigm: **scroll = flight** — scroll position scrubs a chain of mp4 clips
  (dive into a world, frame-chained link to the next, dive again); day overlays
  fade in while the camera is inside that day's world. Two `<video>` slots, hard
  cuts at seams (never crossfade — it overlays a frozen future frame), blob preload
  over HTTP, direct `src` fallback on `file://` so double-click always works.
- Art (`themes.portal`, contract in the renderer docstring): `intro`, `outro`,
  `video_dir` (relative to the art file), `clips` (`file/dur/off/kind/day`).
- Limits: **the "only when footage exists" theme** — the US reference chain (19 clips,
  ~35 MB) is a release asset, **not in the tree**: `themes/assets/portal/` is empty in a
  fresh clone and [its README](../themes/assets/portal/README.md) has the one-line
  curl+unzip restore. The shipped portal case is Morocco (live on the demo site); the US
  chain is the style reference / pipeline fixture only, so another trip needs its own
  clips (build recipe: `build_portal_jobs.py --spec worlds.json` + a ComfyUI i2v
  box; sampler `STEPS` defaults to **10** since 2026-08-16 — same look as 20 to the
  owner's eye, half the wall clock, ≈21 min for 5 dives + 4 links). Videos stay
  sidecar files next to the HTML. Share buttons are exempt (video state) — so no
  `xprobe.sh` on portal; eyeball it in a browser.

`render_picker.py` renders the style chooser (one card per live theme + a table);
add every new theme to its `THEMES` list or the chooser silently falls behind.

## 3. Rendering a trip (Phase 6 checklist)

**Destination scenery is never reused.** Cover / hero / title sticker / clay terrain band / noir plate / splash island are generated for the trip; only generic props (IMAGE-LIBRARY §12) are shared. Clay's default terrain is the neutral `ridge`; `city|park|west|isle` are US-2026 bands.

0. **Start the plan from `assets/plan.example.json`** — it is the only complete
   example of the plan skeleton the renderers read (`budget` = a list of `{cat,
   per_person, total, note}` rows, `legs` = a list of objects, `checklist`, …;
   `references/output-template.md` describes the sections in prose). A section of
   the wrong shape no longer crashes a renderer — `theme_common.norm_plan` prints
   `WARN plan.<key>: expected …` on stderr pointing at output-template.md and renders
   that block empty — so **read stderr after every render**: an empty budget/legs
   grid with a green qc is a plan-shape bug, not a theme bug.
1. Pick the theme(s). Write the **common** art block: cover poem title from
   `references/cover-titles.md` (roles: `zh` = display h1 · `sub` = copy · `en` =
   English line · `credit` = source, printed by all eight themes · `kick` = short trip
   word used ONLY for `<title>` and export filenames on a zh page; `kick_en` takes
   that job on an en page), `home`, `end`, and for every day `theme` (4
   chars) / `en` / `mark`. Titles are per theme in practice — put `zh/en/sub/credit`
   under `themes.<theme>.cover`.
2. Per theme, pick pictures — **reuse first**: `themes/assets/IMAGE-LIBRARY.md`
   §通用件 lists what any trip may use (a plane, a bus, a beach, tape, flora…).
   Place-bound assets (Liberty, Golden Gate, Yosemite, `noir-*`, `glass-*`,
   `zine-*`, `au-*`, `nordic-*`…) never cross trips. Note the index's merged rows
   (`name-a/b/c`, `name-*(N)`) — expand before deciding something is missing.
3. Generate only what is missing — with the agent's **own native image generation if
   it has one (no key; same specs/prompts, then the same split/cutout/webp/manifest
   steps — ART-SCHEMA.md 「生成器选择」)**, otherwise `python3 themes/gen.py <trip>/jobs.json --outdir
   <trip> --manifest <trip>/manifest.<trip>.json` (`--dry-run` first; small parts go
   on a **sheet** — one image cut into 6–12 pieces by `split_sheet.py`, ~$0.005 each;
   `--probe` first, then names in the prompt's Row 1 → Row 2 order; recipe and the
   full command forms in ART-SCHEMA.md 图片工具链), then `cutout.py` for every
   **cut-out** slot (stickers, islands, figurines, bands, stamps, props — the "shape"
   column of ART-SCHEMA's size table) or `towebp.py` for opaque plates/photos, and
   `towebp.py x.cut.png --sizes sm,md,lg` for size variants of a cut-out (running
   `towebp --sizes` on the white-background PNG gives a white square, silently).
   `split_sheet.py` / `cutout.py` / `towebp.py` all take `--outdir` and default to
   the input's directory — write full paths, the shell cwd does not persist between
   calls. Pick the smallest variant that fits the display size — the same image
   referenced twice doubles its base64. The trip's `manifest.<trip>.json` is the
   record of what was generated; **do not write into `themes/assets/` or
   `IMAGE-LIBRARY.md`** — folding a test trip's generic pieces back into the
   library is the main agent's job after the batch (ART-SCHEMA 测试行程资产回收).
4. Write the words: captions, annotations, doodle notes, the closing line. Voice
   rules live in each renderer's docstring.
5. Render → `qc.py` exit 0 → `xprobe.sh` one module and, for whole-page themes, one
   page export → **look at both PNGs** (§6). Deliver the HTML (and for portal, the
   video directory beside it).

Steps 2-3 above assume the session **can** make pictures. Whether it can is decided
once, at Phase 0, and recorded in `prefs.pictures` — §3b is the branch for when it
cannot.

### 3b. Stock mode — no generator, no key, still a themed page

Phase 0's **picture-capability check** writes one of three values into the plan's
`prefs.pictures`, and Phase 6 reads it instead of guessing:

1. **`native`** — the agent has its own image-generation tool → generate this trip's art
   with it; nothing to configure, no key. Same specs, same prompts-as-style-anchors, same
   four downstream steps (ART-SCHEMA.md 「生成器选择」). §3 steps 2-3 as written.
2. **`key`** — `themes/.auth_header` exists (checked with `test -s`; never read, print or
   copy it) → `gen.py` / `genvideo.py` over OpenRouter with the user's key. §3 steps 2-3.
3. **`stock`** — neither. **This is not a reason to ship the plain page.** The built-in
   stock kit supplies the pictures and the page still renders in a theme:

```
python3 themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
    # also: --theme clay · --lang zh|en · --index PATH (a different stock index)
```

- **What the script fills**: the picture side of the art file — cover painting, per-day
  heroes/cut-outs and props — matched to the plan's country and each day's stops from
  `themes/assets/stock/` (`stock/index.json`, catalogue in `stock/README.md`) plus the
  shared library's same-country pictures and generic props (`IMAGE-LIBRARY.md` §通用件).
- **What it does not fill — you write the words**: the cover title from
  `references/cover-titles.md`, each day's `theme` (4 chars) / `en` / `mark`, captions,
  annotations and the closing line. A page shipped with the script's placeholders in it
  is a defect, exactly as in §3 step 4.
- **Keep the notice.** The script writes the stock notice into the page's fine print
  (`end.fine`); leave it there, and repeat it once in the chat summary — *"pictures come
  from the built-in stock kit because no image generator or key was available; provide
  one and the art gets generated for this trip."* Never ask the user for a key in chat
  and never handle one.
- **Coverage today**: **illustrated** (the default) is complete; **clay** works — its
  terrain bands come from the built-in neutral SVG kit (`ridge|plain|coast|forest|lake|
  desert`) plus generic clay props. The other six themes (noir, glass, journal, zine,
  splash, portal) need generated pictures for their plates / photos / islands / footage —
  if the user asks for one of them in stock mode, say so and offer illustrated instead;
  rendering them anyway gives a page with empty picture slots, and portal has no footage
  at all. Stock packs for the remaining styles are future work
  ([`docs/KNOWN-ISSUES.md`](../docs/KNOWN-ISSUES.md) AST-8).
- Everything else is unchanged: render, `qc.py` exit 0, probe and **look** at the PNG
  (§6). A stock page is a real themed page and gets the same verification.

## 4. Adding a theme

1. **Answer the four questions first**, or do not start: ① organising principle
   (paper / terrain / negative / imagery / …) ② interaction (vertical scroll,
   horizontal paging, spatial selection…) ③ type voice (which face does which job)
   ④ shape language (what buttons and markers look like). Swapping backgrounds and
   illustrations = a re-skin; an audit will call it the same species. Check the
   result against §2's axes; the strongest differentiation is a move only this
   theme can make (clay's mini-road, noir's hop-band dissolve).
2. Owner's bar for every theme: modules blend into one another (no "box next to
   box"), the main picture is the page's background rather than a framed painting,
   and the theme carries pictures — pure-text designs are retired.
3. Start from the shortest live renderer; `from theme_common import …` gives you
   `esc/et/ic/sprite`, `data_uri`, `day_embed_url`, `dist_km`, `load_plan`,
   `short_dates`, `Art/load_art/add_art_arg`, `export_prefix`, `export_js`, and the
   i18n set `init_lang/lang/T/tag_pretty/weekday/theme_name/brief_titles` (§4a). Share
   only what does not hurt identity: **layout, type, colour, motion and interaction
   widgets stay in the renderer** — that is exactly the part that must differ.
4. Contract to honour: `add_art_arg(ap)` + `load_art(plan, args.art, args.assets)`;
   read the common block via `Art` (theme block merges over common per key); every
   field optional with the neutral fallbacks documented in your docstring; a
   `--art none` render of `examples/kyoto-sample.plan.geo.json` must work with no
   trace of any other trip (`grep` the renderer for place names: zero hits).
5. Share buttons: wire `theme_common.export_js(theme, page_bg, extra_css,
   page_root)`. Buttons are `class="xbtn no-export"` with `data-x-for="#dN"
   data-x-label="DAY0N"` (module) or `data-x-page` (whole page); build-time
   `html.replace("EXPORT_JS_PLACEHOLDER", export_js(...))`. `.no-export` content is
   excluded. `extra_css` is make-or-break: anything revealed by scroll (`.reveal`,
   rAF opacity) must be forced visible with `!important` under the `.__xbody`
   prefix, or the export is blank. Sticky/fixed-stage themes pass `page_root=""`
   (module-only). Labels are fixed: 保存这一天 / 保存附录 / 生成长图 (never 导出/下载/
   存储) — always via `T("btn.save_day")` etc. so the en page says Save this day /
   Save appendix / Save long image (§4a); the button must speak the theme's own shape
   language.
6. **Continuous-world recipe** (any "one landscape" theme): per-chapter gradient
   whose start colour = previous chapter's end (never a page-wide percentage
   gradient — content height changes and the stops drift); terrain strips = cut-out
   webp with negative margins + `first-of-type` padding to protect the next line;
   any decoration line that spans the page is drawn **per chapter** (a single global
   SVG is covered by chapter backgrounds; layer order background < line < content);
   each layer's SVG holds only the path segments inside its own window (a 12k-px
   path in every layer blows the GPU texture limit — blank tiles), and no CSS
   `filter:blur()` on long paths (fake it with 2–3 wide low-alpha strokes).
7. Acceptance: `qc.py` exit 0 · **byte-identical rebuild** (render twice to two
   files and `cmp` — all randomness must be seeded; a diff means `Math.random` or a
   timestamp leaked in) · 390px cold load with per-element `right > innerWidth`
   check · re-derive the signature mechanic with your own arithmetic in the browser
   (§6) · module + page export probed and eyeballed · added to `render_picker.py`.

### 4a. i18n — how the pages speak two languages, and how to add a third

- **Source of truth**: `plan["lang"]` (fallback `plan["meta"]["lang"]`; `zh` default,
  `en`), overridden per run by `--lang` (added by `add_art_arg`). Every renderer's
  `main()` calls `init_lang(args, plan)` right after `load_plan`; nothing else in the
  file decides the language.
- **Three tables, one per kind of word** (`themes/theme_common.py` §i18n):
  1. `STRINGS[lang]` — words every theme shares, read with `T(key)`: `tag.*`
     (`tag_pretty(tag)`, incl. `swap→X`), `btn.save_day|save_appendix|save_page`,
     `toast.*` (baked into `export_js` at build time), `label.page|day|appendix`,
     `sec.*` (brief/decisions/unverified/legs/hotels/budget/checklist/appendix/route/
     map), `sun.dawn`/`walk`/`rain_alt`/`late_cut`/`hop.map`/`verify.est`/
     `price.check`/`link`, `week` (`weekday(date)`), `html_lang` (`<html lang>`).
  2. `THEME_NAMES[lang]` — `theme_name(key)` for `<title>` and export filenames
     (手账版 → Journal …); `BRIEF_TITLES` / `BRIEF_TITLES_EN` behind `brief_titles(art)`.
  3. Each renderer's local `L = {"zh": {...}, "en": {...}}` + `t(k)` — the theme's own
     voice only (cover fallback word, chapter eyebrows, stamp/badge text, quips,
     credit line). Generic words never go here; if two themes need the same word it
     is a `STRINGS` key.
  Content is never translated: plan text, art copy and `sun` are printed as written
  (`sun` parsers accept 天亮 and dawn — `route_tools.py sun --write --lang en`).
- **Adding a language `xx`**: add `STRINGS["xx"]` (every key of `zh`, including
  `week` and `html_lang`), `THEME_NAMES["xx"]`, a `BRIEF_TITLES_XX` and its branch in
  `brief_titles()`, `SUN_DAWN["xx"]` in `route_tools.py`, then an `"xx"` column in each
  renderer's `L` (`t()` falls back to zh for a missing key, so ship complete columns);
  `--lang` picks up the new choice from `STRINGS` automatically. Then render an `xx`
  plan through every theme + `render_picker.py`, `qc.py` exit 0, and grep the output
  for CJK — any Chinese that is not plan/art content is a leaked shell string.
- **The CJK-leak grep, comment-free**: a bare `grep -o '[一-龥]\{2,\}'` hits CSS/JS
  *comments* on every en page (journal 纽约/第一站/秋水长天, noir 路线地图/插画版, and the
  export engine's `渲染引擎不支持` from theme_common — all comments, all invisible), so
  strip comments first, then look:

  ```bash
  python3 - out.html <<'EOF'
  import re, sys
  s = open(sys.argv[1], encoding="utf-8").read()
  def strip(m):                       # comments inside <script>/<style> only
      body = re.sub(r"/\*[\s\S]*?\*/", "", m.group(0))
      return re.sub(r"(?m)^[ \t]*//.*$", "", body)      # line-start // (URLs keep theirs)
  s = re.sub(r"<(script|style)\b[^>]*>[\s\S]*?</\1>", strip, s)
  s = re.sub(r"<!--[\s\S]*?-->", "", s)
  hits = sorted(set(re.findall(r"[一-鿿]{2,}", s)))
  print(*hits, sep="\n") if hits else print("no CJK outside comments")
  EOF
  ```
  Verified 2026-08-16 on the Mexico journal/noir and Morocco glass/portal en pages: the
  bare grep hits 1–4 comment strings each, this prints `no CJK outside comments`. **The
  known residue lives only in comments**; a hit from this script on an en page whose
  plan/art carry no Chinese is a real leak.
- **Regression gate — zh bytes never move**: `zh` is the historical shell, and the
  US baselines (`trips/us-2026/US-2026-<theme>版.html`) are the oracle. After any i18n
  edit, render `trips/us-2026/plan-A.geo.json` with each renderer (no `--lang`, and
  again with `--lang zh`) and `cmp` against the baseline: byte-identical or the change
  is wrong (a shifted RNG call, a re-ordered replace, a stray space). Never edit a zh
  value in `STRINGS`/`L` without rebuilding the baselines on purpose.

## 5. Recurring-defect checklist (run every item on every new theme)

Two audit rounds produced 76 findings; every class below recurred in ≥2 themes.

1. **Contrast** — decorative colours are fine, text gets its own `-ink` ramp; compute
   the worst case over the whole background gradient with the relative-luminance
   formula, do not eyeball (illustrated once had 16/16 tokens failing AA).
2. **The signature mechanic itself is broken** — the most expensive class; §6.
3. **`.reveal{opacity:0}` without JS** — scope as `.js .reveal{}`, add the `js`
   class as the IIFE's first statement, wrap decoration JS in try/catch.
4. **Print strips backgrounds** — filled chips go white-on-white; dark themes leak
   their tokens into `@media print` — reset the whole token set there and use
   `print-color-adjust:exact` on the few colours that matter.
5. **No `:focus-visible` rule** (four themes missed it).
6. **Icon links without an accessible name / <44px hit area; `target=_blank`
   without `rel=noopener`.**
7. **Compositor killers** — world-length paths in every SVG layer; `filter:blur()`
   on long paths; `overflow:clip` + `border-radius` around a 12k-px element.
   Symptom: scroll areas screenshot as flat colour, real devices stall.
8. **Quote nesting in inline `url("data:…")`** — the style attribute truncates and
   every decoration silently dies (25 stamps once rendered as `url("")` while QC
   passed). Emit `url(<fully-escaped uri>)` unquoted; qc.py check 7 fails on
   `url("` inside a style attribute. Same family: a bare `<` in CSS tears the
   export `<foreignObject>` XML — the engine now escapes `&`/`<`; whenever HTML/CSS
   is spliced into another syntax (XML, attribute, URL), escape at the boundary.
9. **Grid/flex row between two floats collapses to a one-glyph column** — on a
   poster day float the print/sticker after the timeline so the flow ever sees one
   float at a time. Only a headless-Chrome screenshot catches this.
9½. **`file://` synchronous-init ordering** — declarations reached by init must sit
   before the loader block; over HTTP the async fetch hides the bug, on `file://`
   the sync path throws on every scroll (portal once lost every overlay). Accept
   under both modes.
10. **Sprite `<use>` across documents** — the export clone is a separate SVG
   document, so `<use href="#i-…">` dangles and icons/particles export blank while
   the probe title stays green. The engine copies referenced `<symbol>`s
   (`spriteFor()`), but audit every `#id` reference (use, `url(#grad)`, filter,
   clip-path, mask) on any clone/serialise path; and when another theme has fixed
   the same class, promote the fix to the engine or this list.

Runtime half (browser only): 390px cold-load per-element overflow (`docOv=0` is
not proof — `overflow-x:clip` hides content silently); grid children holding long
text need `minmax(0,1fr)` + `min-width:0` + `overflow-wrap:anywhere`; data-URI
images never `loading=lazy`; itinerary grids never `grid-auto-flow:dense`.

## 6. Verification discipline

- **"Works on paper ≠ works in CSS."** Noir's burned-in title was dead for days: a
  `z-index` on the content layer created a stacking context that isolated the blend
  group — the fix is lowering the plate, not raising the content. Clay's road once
  missed the stones it claimed to thread by 137px (anchored to viewport ratios) —
  anchor to `getBoundingClientRect()` centres, and re-run on `ResizeObserver` plus
  a capture-phase `toggle` listener (`<details>` toggles do not bubble).
- **Scan the whole interval, not the endpoints.** A dissolve checked only at chapter
  and hop centres passed while mid-chapter was a 50/50 double exposure; sample
  10%–90% in nine steps per chapter and require every one to pass.
- **Read authoritative fields, never sniff prose** — transport mode comes from
  `legs`, not hop text (a precedence slip once made 8/11 days "fly").
- **Export probes**: `xprobe.sh` reports `OK <w>x<h> blob=<bytes> errs=<n>` and
  writes the export as PNG. Green is necessary, not sufficient — **open the image**:
  icons and particles present? no stray colour band at the top? last decoration
  at the bottom intact? `ANCHOR=bottom … page ''` shows the tail. Both `xprobe.sh`
  and `xt.sh` start Chrome in the background with a throwaway `--user-data-dir`,
  poll for output, then kill that Chrome by profile — do not wait on it in the
  foreground (Chrome 151 headless never exits on this machine) and do not run
  headless Chrome unless the task calls for it (memory). A `Killed: 9` job line
  from an older copy of either script is that self-kill, not a failure (the
  current scripts swallow it); the title/png line is the result.
- **Cover check — which themes have a whole-page button, and what `page ''` gives you.**
  Whole-page (`data-x-page`) buttons exist in illustrated, clay, journal, zine and
  splash. **noir and glass are module-only** (sticky/fixed stage, `page_root=""`), and
  portal has no share buttons at all. On those, `xprobe.sh out.html page '' cover.png`
  prints `NO-BTN` — **not a failure**: pass 2 still screenshots the live page at
  1200×2600, so `cover.png` is the first 2600 px of the real page, i.e. exactly the
  cover shot you wanted to eyeball. **splash** is the opposite trap: its whole-page
  export deliberately zeroes the hero's 100svh (`extra_css`, see the renderer
  docstring), so the export's first screen is DAY 01 and the cover is not in it —
  shoot the live page instead. Same for any theme whose cover you want at true
  viewport geometry. Live-page shot, the way xprobe.sh does it (background Chrome,
  throwaway profile, poll, kill by profile — never wait on Chrome in the foreground):

  ```bash
  CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  mkdir -p "${TMPDIR:-/tmp}/xprobe" qa; UDD=$(mktemp -d "${TMPDIR:-/tmp}/xprobe/udd.XXXXXX"); OUT=$PWD/qa/splash-live-cover.png
  { "$CH" --headless=new --disable-gpu --no-first-run --user-data-dir="$UDD" --hide-scrollbars \
      --window-size=1200,2600 --virtual-time-budget=45000 --screenshot="$OUT" "file://$PWD/out.html" 2>/dev/null & } 2>/dev/null
  last=-1; for i in $(seq 1 120); do [ -s "$OUT" ] && { sz=$(stat -f%z "$OUT"); [ "$sz" = "$last" ] && break; last=$sz; }; sleep 1; done
  { pkill -9 -f -- "--user-data-dir=$UDD"; wait; } 2>/dev/null; rm -rf "$UDD"
  ```
  (For a `.reveal` theme inject `.reveal{opacity:1!important}` into a copy first —
  IntersectionObserver never fires headless.) `ANCHOR=bottom xprobe.sh … page ''`
  shows the export's last 2600 px — the tail check; on a module-only theme it is the
  same live first screen, so check the tail there with a module probe on the last
  block (noir `module '.appx'`, glass `module '#checklist'` / `'#brief'` — the
  selectors are the page's own `data-x-for` values).
- **Headless viewport floor**: macOS headless Chrome will not shrink `innerWidth`
  below ≈500 no matter what `--window-size` says — `--window-size=390,844`
  lays the page out at 500 px and screenshots its left 390 px, which looks exactly
  like an overflow bug. Run the 390 px cold-load check by injecting the
  measurement into the page (a 390 px-wide iframe/container, or per-element
  `right > innerWidth` printed into the title) rather than by narrowing the window.
- **English trips**: the CJK-sized slots have Latin ceilings — `days[].theme`
  ≤12 Latin chars (zine's vertical title ≤10), illustrated `cover.zh` ≈11 — see
  ART-SCHEMA.md "Latin length ceilings"; longer titles overrun rather than wrap.
  On an en page `<title>` and the download prefix come from `cover.kick_en`
  (`theme_common.title_kick`, all eight themes), so write it as you want it read
  (`"MEXICO 2026"`). English copy runs 30–40 % longer than the Chinese it replaces:
  containers sized for CJK — journal sticky notes (`rain_alt` / `late_cut`), the
  cover envelope (`meta.route` ≤68 chars), noir/glass credit lines — need a look
  in the export, not just a green probe. Journal now leaves room at the foot of
  its en notes and keeps its cover epigraph off the postmark (2026-08-16), but keep
  note copy short (~≤180 chars) rather than relying on it.
- **Screenshot traps**: measure and shoot at the same viewport (svh/sticky shift
  layout); in headless, IntersectionObserver never fires — inject
  `.reveal{opacity:1!important}` before shooting `.reveal` themes; a hidden in-app
  browser pane freezes rAF/video and reports 0×0 geometry — check `innerWidth>0`
  first, prefer geometry assertions (rect intersection, `isPointInStroke`) over
  pixels; only a real wheel scroll moves the screenshot engine, JS `scrollTo` does
  not; bust caches with `?v=n` after a rebuild.
- **Export engine defaults**: day blocks PNG 2×; blocks over ~1.2e7 px and whole
  pages JPEG 0.92; height cap 30000, page area budget 3.2e7 px, one half-size
  retry; viewport units are frozen to px before capture (skipping `url(...)`).

## 7. Recipes worth reusing

- **Google Maps embed, keyless**: `https://maps.google.com/maps?saddr=<start>&daddr=<2nd>+to:<3rd>…+to:<end>&dirflg=r&output=embed` — `daddr` starts the chain and the last stop closes it; take the longest run of hops each ≤150 km (skip flights); inject the iframe `src` only when its `<details>` opens (`theme_common.day_embed_url`).
- **Smooth-scroll fallback**: the in-app browser ignores `scroll-behavior` and
  `scrollTo({behavior:'smooth'})` — try smooth, hard-jump after 350 ms if nothing moved.
