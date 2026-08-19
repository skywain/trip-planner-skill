# art.json — per-trip art direction for the themed renderers (schema v1)

A themed page = **plan** (facts: `plan.geo.json`) + **art** (this file: what the
trip *looks and sounds like* in a given theme) + **renderer** (the theme's craft:
layout, type, colour, motion — knows nothing about any particular trip).

The file sits next to the plan and shares its stem:
`kyoto.geo.json` ↔ `kyoto.art.json`. Renderers pick it up automatically
(`--art <file>` to point elsewhere, `--art none` to render bare).

**Where pictures are looked up** (`theme_common.data_uri`): `--assets DIR` (repeatable,
later wins) → the art file's directory → the plan's directory → the theme library
directory. So a trip keeps its own webp next to its plan and never copies anything
into the library; prefix trip assets with the trip name (`au-…`, `nordic-…`) so a
size variant in the library can never shadow them.

## The one rule for what goes where

**If it names this trip's places, dates, people, jokes, or picture files → art.json.
If it is the theme's own vocabulary (its tape kit, its stamp mechanics, its
doodle sketches, its layout rhythm) → stays in the renderer as a named kit.**
art.json then *picks from the kit and supplies the words*: `{"prop": {"kind":
"vtk", "lines": ["YELLOWSTONE", …]}}` — the vintage-ticket look is the theme's;
the text on it is the trip's.

Every field is optional. **A renderer must produce a usable page from an empty
art file**: no picture instead of a picture, no caption instead of a caption,
never a crash and never a line that belongs to another trip.

## Common block (shared by every theme)

```jsonc
{
  "cover": {
    "zh":  "跨越山海,遇见自由",           // display title, 2-8 chars typical
    "en":  "STARS OVER THE PLAINS",         // English line under it
    "sub": "记录旅途的每一刻心动。",         // one-line subtitle / copy
    "credit": "「星垂平野阔,月涌大江流」—— 杜甫《旅夜书怀》",  // allusion, honest — printed small by all eight themes (zine since 2026-08-16)
    "kick": "美国行",                        // short trip word: <title> prefix + download-filename prefix on a zh page (never the display title)
    "kick_en": "US 2026",                    // CAPS English form: <title> + filename prefix on an en page (lang=en, all eight themes), export frame stamps, tickers
    "postmark_date": "2026-09-25"            // cover postmark; default = first day
  },
  "home": {"city": "北京", "iata": "PEK"},   // where the trip starts/ends
  "end": {                                   // the closing spread
    "date": "2026-10-07",                    // arrival-home date (postmark); missing → no endcap postmark/line
    "mark": "BEIJING",                       // CAPS city on the endcap postmark
    "line": "北京,到家了。",                 // hand-written closing line
    "fine": "10-07 週三 12:00 落地 —— 跨过日界线,日历上的 10-06 在空中消失。",
    "farewell": "SEE YOU, AMERICA"           // 2nd line of the TRIP COMPLETE chop (default HOMEWARD BOUND)
  },
  "days": {
    "2026-09-26": {
      "theme": "曼哈顿日",                   // 4-char editorial day title (was DAY_THEME)
      "en":    "New York, NY",               // English place line
      "mark":  "NEW YORK"                    // short CAPS code (postmarks, stamps, tickers)
    }
  },
  "brief_titles": {"visa": "签证 · EVUS"},   // country-brief section titles: overrides theme_common.BRIEF_TITLES per key — read by EVERY theme
  "themes": { "<theme>": { … } }             // per-theme blocks, below
}
```

**`brief_titles` is shared by all themes.** `plan.brief` keys are English identifiers
(`visa / holidays / weather / money / connectivity / insurance / safety / baggage`); every
renderer labels them from one table, `theme_common.BRIEF_TITLES` (签证 / 节假与人流 / 天气 /
货币与小费 / 通信 / 保险 / 安全 / 行李), overlaid by this block (`"visa": "签证 · EVUS"`);
a key in neither table (a trip's own Chinese heading such as `安全总览`) prints as it is.
The table follows the page language (`theme_common.brief_titles(art)`: `BRIEF_TITLES`
for zh, `BRIEF_TITLES_EN` — Visa & entry / Holidays & crowds / Weather / Money & tipping /
Connectivity / Insurance / Safety / Baggage — for en), so an English trip only lists a
key here when it wants a different heading (`"visa": "Visa & ESTA"`).

## Language (`plan.lang` — the page's UI language)

- **The language is a plan fact, not an art field.** Renderers read `plan["lang"]`
  (fallback `plan["meta"]["lang"]`; `"zh"` default | `"en"`), overridable per run
  with `--lang zh|en` (`theme_common.init_lang(args, plan)` in every `main()`).
- **Shared words** every theme uses live in one table, `theme_common.STRINGS`
  (`T(key)`): tags 钉死/开门冲/可砍/换 → pinned/go first/optional/swap
  (`tag_pretty`), share buttons 保存这一天/保存附录/生成长图 → Save this day/Save
  appendix/Save long image (+ toasts), section names 行前须知/关键取舍/出票前待复核/
  航段/住宿/预算/清单/附录/路线/沿途地图, the day words 天亮/步行/雨备/晚点剪法/逐跳导航,
  weekdays (`weekday(date)`: 週一…/Mon…), `<html lang>` (`html_lang`), theme names in
  `<title>`/export filenames (`theme_name`: 手账版 → Journal …). Add a new shared
  word there, never in a renderer.
- **Theme voice** — each renderer's own words (cover fallback such as 「旅行手账」/
  「拼贴」/「玻璃」, chapter eyebrows, badge/stamp text, quips, footer credit line) sit
  in a local table `L = {"zh": {...}, "en": {...}}` inside that `render_<theme>.py`
  and are picked with `t(k)`; the zh column reproduces today's pages byte for byte.
- **Art copy renders in whatever language it was written**: `cover.zh/en/sub/credit`,
  `days[].theme/en/mark`, `end.line/fine`, `brief_titles`, quips in theme blocks are
  printed as they are — an English trip writes English art (or leaves the field out
  and gets the theme's en fallback), a zh trip writes Chinese. `lang` never
  translates content, it only switches the shell around it.
- **English cover titles**: references/cover-titles.md §Non-Chinese trips (same
  roles, Latin length budgets — the `zh` slot is still the h1 even when Latin).
- `sun` strings written by `route_tools.py sun --write --lang en` say `dawn …`
  instead of `天亮 …`; every renderer's sun parser accepts both.

**`plan.meta.dates` contract (not art, but every cover reads it — `theme_common.short_dates`):**
keep it a bare `YYYY-MM-DD → YYYY-MM-DD` (arrow or dash between). Renderers strip the
years (`09-25 → 10-07`) and swap the arrow for their own dash; `date_span()` takes the two
ISO ends. Prose such as `10.01 抵达 – 10.08 离开(…)` is passed through verbatim minus
years and lands on the cover date line of every theme exactly as written — it folded the
nordic cover.

**`plan.meta.route` is a cover line too** (journal prints it inside the cover envelope,
zine on the cover, clay and splash use it as the fallback for `cover.sub`). Keep it
**≤68 characters** — the journal envelope is the tightest: a 76-character English route
folded to two lines and hit the envelope's bottom edge, 68 sat on one line (Mexico
2026-08-15). CJK routes were not measured — verify with xprobe. If the plan's route must
carry branch prose ("哥伦布(球赛·可切C分支)") for the plain page, give clay/splash their
own short `cover.sub`; journal and zine print `meta.route` as it is.

**Latin length ceilings (CJK designs, measured 2026-08-15):** `days[].theme` is sized for
4 CJK glyphs — keep it ≤4 CJK / ≤12 Latin characters everywhere it is used; illustrated
`cover.zh` h1 ≈ 11 Latin characters fills the 500 px line edge-to-edge ("Late Maples");
zine `days[].theme` (the vertical `.vtitle`) ≤ 10 Latin characters — longer titles become
upright letter-stacks that overrun the chapter head. Other themes: see each block's
`reads:` line / builder notes.

`days[date]` may carry any extra shared field a later theme wants; a theme block
overrides per key (`themes.<theme>.days[date]` is merged **over** `days[date]`,
`themes.<theme>.cover` over `cover`, `themes.<theme>.end` over `end`).

**Cover titles are per theme in practice** — every theme has its own poem title
(手账「美国行」/ 夜航「星垂平野」/ 插画「碧海苍梧」…), so `zh/en/sub/credit`
normally live in `themes.<theme>.cover`; the top-level `cover` keeps what is truly
shared: `kick`, `kick_en`, `postmark_date`.

**Same roles in every theme (settled 2026-08-15 after two testers tripped on it):**
`zh` = the big display title (h1) · `sub` = the copy line(s) under it (`\n` breaks) ·
`en` = English line · `credit` = the allusion's source, small (all eight themes print it —
zine since 2026-08-16) · `kick` = the short trip word used ONLY for `<title>` and export
filenames, never as the display title; on an **en page (`lang=en`) every theme takes
`kick_en` instead** for `<title>` and the download prefix (a `kick_en` that already
carries the year is not given a second one), so write it in the CAPS form you want to
see there (`"MOROCCO 2026"`, `"TURKEY 2026"`).
Journal auto-sizes its h1 by character count (2-3 chars full size, 4 slightly smaller,
5-6 smaller, ≥7 shrunk to one line) — a four-character poem title fits; the US page
keeps its owner-approved 大白话「美国行」as `zh` with the poem as `sub`.

**`caption: [a, b]` (journal polaroids, cover photo) is two typographic slots, not two
languages**: `[0]` = the main line (Kaiti), `[1]` = the handwritten aside (Caveat, smaller).
The `[zh, en]` shorthand in the examples is the zh trip's habit; an en trip writes English
in both — "Teotihuacán at dawn" / "Pyramid of the Sun".

## Theme block: `journal` (手账版)

**reads:** common `cover.zh` `cover.sub` `cover.credit` `cover.kick` `cover.postmark_date` ·
`end.date` `end.mark` `end.line` `end.fine` `end.farewell` · `days[d].theme` `days[d].en`
`days[d].mark` · `brief_titles` (not `home`, not `cover.en`; `kick_en` only for the en `<title>`/filename).

```jsonc
"themes": { "journal": {
  "cover": {"zh": "秋水长天",                    // h1 (auto-sized); US page uses「美国行」
            "sub": "十月的峡湾,水和天是同一种颜色。",   // copy under it, \n = line break
            "credit": "「秋水共长天一色」—— 王勃《滕王阁序》",   // optional small source line
            "photo": {"stem": "journal-ph-liberty", "alt": "自由女神",
                      "caption": ["自由女神,老朋友", "Liberty Island"]}},   // cover polaroid; missing → none
  "cover_stamps": [ {"cls": "st-a", "rot": -2}, {"cls": "st-b", "rot": 1.6} ],   // ≤3
  "stamps": {                                  // postage-stamp scans this trip owns
    "st-a":    "journal-stamp-liberty",        // slot → asset stem; st-a / st-b portrait,
    "st-b":    "journal-stamp-goldengate",     // st-wide landscape (84px). Old names
    "st-wide": "journal-stamp-bison"           // st-lib / st-gg / st-bis stay as aliases
  },
  "days": {
    "2026-09-26": {
      "photo":   "journal-ph-nyc",              // the day's polaroid (asset stem)
      "caption": ["布鲁克林桥的黄昏", "New York City"],   // [main, aside] under the polaroid — Kaiti line + Caveat aside, not zh/en slots
      "annot":   "第一站:纽约。大都会的脉动……",             // ✎ margin note under the day head
      "props":   [ {"kind": "stamp", "cls": "st-a", "rot": -3} ],   // rail collage, see kit
      "doodle":  {"sketch": "skyline", "note": "Top of the Rock!\n9/26 ✦", "font": "hand", "rot": -2},
                 // note: English short phrase, or break by hand with \n — ≤2 lines × ≤18 chars,
                 // the box does NOT wrap (a pure-CJK note without \n was a one-glyph column);
                 // rot optional (default seeded). Or a custom line drawing instead of sketch:
                 // "doodle": {"svg": {"viewBox": "0 0 96 62", "d": "M…", "arrow": true}, "note": "…"}
      "photos2": [ {"stem": "journal-ph-slctemple", "en": "Temple & the Wasatch, SLC",
                    "alt": "盐湖城圣殿与瓦萨奇雪山"} ],   // stacked under the polaroid, smaller (254 vs 290px)
      "poster":  {"stem": "journal-poster-yosemite", "alt": "…", "line": "Yosemite — granite & light", "rot": -1.3}
                 // no trip-specific poster scan? drop stem and give it words instead:
                 // "poster": {"title": "BLUE\nMTNS", "line": "three sisters, one valley", "rot": -1.3}
                 //  → the theme's CSS kraft-paper vintage poster frame (tack + tape, big Kaiti title)
    }
  }
}}
```

**Prop kit** (`props[].kind`): `img` (`stem`, `w` in CSS px — 105-220 works, `rot`) ·
`stamp` (`cls`, `rot`) · `vtk` vintage park ticket (`tone` green|brown, `lines`
[name, sub, price, serial], `rot`) · `bagtag` (`lines`, `rot`) · `seal` (`rot`) ·
`flora` (a pressed flower — from the theme's seeded deck, or `stem` + `w`(px, default
90) + `rot` to press one of this trip's own scans) · `postcard` (`stem`, `alt`, `note`,
`rot`, `stamp: {cls, rot}`; replaces the day's prop with a franked postcard; **no
`stem` = the theme's plain linen postcard** carrying just the handwritten `note`,
an address block and the stamp slot — empty dashed frame when no stamp).
Stamp slots `st-a` / `st-b` (portrait) / `st-wide` (landscape) are the kit's;
`stamps` maps a slot to this trip's scan, and a slot with no scan paints nothing
(old names st-lib / st-gg / st-bis are permanent aliases). **Doodle sketches**
(`doodle.sketch`): `skyline` · `bison` · `bridge` · `waves` · `volcano` · `peaks`
(ridge + rock pillars) · `coral` (branch + small fish) · `palm` · `train` (scenic
railway) · `cabin` (timber house) · `ferry` · `aurora` (light band + pines) —
single-line ink drawings the theme owns; `note` is the trip's, `font` hand|cur; or
bring your own path via `doodle.svg`. Days with no doodle get one of the theme's
generic quips — never a place-specific one. `cover.postmark_date` only affects the
cover postmark; day postmarks always use that day's date. Long station names on the
departure chop scale down to fit (Latin and CJK both counted). **en pages**: the
theme's own cover epigraph no longer runs under the postmark and the sticky notes
(`rain_alt` / `late_cut`) keep a margin at the foot (2026-08-16) — English still runs
30–40 % longer than the zh it replaces, so keep note copy short (~≤180 characters) and
`meta.route` ≤68 (the envelope).

## Theme block: `noir` (夜航版)

**reads:** common `cover.zh` `cover.en` `cover.credit` `cover.kick` `cover.kick_en` ·
`days[d].theme` · `brief_titles` (no `home` / `end` / `days[d].en|mark`).

```jsonc
"themes": { "noir": {
  "cover": {"zh": "星垂平野", "en": "STARS OVER THE PLAINS", "credit": "「星垂平野阔,月涌大江流」—— 杜甫《旅夜书怀》"},
  "plates": ["noir-hero", "noir-nyc", "noir-stadium", "noir-yellowstone",
             "noir-yosemite", "noir-volcano", "noir-sunrise"],   // reel order; [0] = cover
  "day_plate": {"2026-09-25": 1, "2026-09-26": 1, "2026-09-27": 2, "…": 3}
                // {"<ISO date>" | "<1-based day number>": plate index} — date keys are
                // safer (inserting a day never shifts them); both may be mixed, date wins;
                // a count mismatch or unmatched key prints one stderr warning
}}
```
Missing `plates` → the stage renders with the theme's flat gradient and no
photographs; missing `day_plate` → every day sits on plate 1 (or 0 if only one).


## Theme block: `illustrated` (插画版)

**reads:** common `cover.kick` (`kick_en` on an en page) `cover.zh` `cover.en` `cover.credit` `cover.sub` · `home.city` ·
`end.line` `end.fine` · `days[d].theme` · `brief_titles`. `cover.zh` ≈ 11 Latin chars max.

```jsonc
// ---- ART-SCHEMA.md additions for the illustrated (插画版) block ----
// common fields READ by this renderer (no new common keys; all already in schema):
//   cover.kick (eyebrow prefix + <title> + export filename), home.city (endcap img alt "回到<city>"),
//   end.line, end.fine, days[d].theme.
//   NOTE: this theme's fine print writes the FULL date, so the US page overrides
//   end.fine inside themes.illustrated.end (common end.fine has no year).

"themes": { "illustrated": {
  "cover": {"zh": "碧海苍梧",                       // h1 display title → cover.kick → "旅程"
            "en": "DAWN SEAS · DUSK PEAKS",          // letterspaced English line → omitted
            "credit": "朝碧海而暮苍梧 —— 徐霞客",    // allusion/source, small → omitted
            "sub": "纽约 · 球赛 · 黄石 · 优胜美地 · 火山",   // ornament subtitle (—— … ——) → omitted
            "hero": "cover-hero"},                   // full-bleed cover painting stem → no cover picture
  "end":   {"hero": "tiananmen",                     // endcap cut-out stem (.md) → no picture; alt = "回到"+home.city.
                                                     // This is the COMING-HOME scene — the departure city (Tiananmen for a
                                                     // Beijing trip, the Bund for Shanghai), never a destination sight;
                                                     // cheapest as one extra cell on the illustrated sheet
            "fine": "2026-10-07 週三 12:00 落地 —— …"},   // per-theme override (full date); line comes from common end.line
  "days": {
    "2026-09-27": {"hero": "stadium",                // the day's cut-out stem; kit inlines it as .sm (menu card),
                                                     // .md (plate sticker), .lg (faint tilted backdrop) → all three slots empty
                   "feature": true}                  // wide 170px "feature" menu card → normal card
  }
}}
// Missing everything → paper cover with eyebrow dates only, h1 "旅程", city as day title,
// text-only menu cards, no endcap block. Nothing else in the block is trip-specific.
```

**Kit (theme-owned, not in art)**: Kit kept in render_theme2.py (nothing to choose in art): paper palette tokens + the four plate tints cycled by day number (tint{i%4}); outline ghost numeral; alternating sticker tilt (.polaroid t0/t1) and backdrop side (side-l/side-r) by day parity; data_uri size chain sm/md/lg for the one day stem; KIND_CLASS + inline lucide icon data-URIs for the spine timeline; taped margin note cards (walk/rain/late_cut/note); the 〔…〕bracket export annotations + 〔生成长图〕; appendix ledger/table/brief grid; cover scrims and scroll cue; the "插画版行程" <title> suffix and "旅程" h1 fallback; footer AI-generated credit line.

## Theme block: `clay` (黏土版)

**reads:** common `cover.kick/kick_en/zh/en/credit` (zh → cover sticker alt; en → hand-pinched label; credit → thin line under route), `cover.sub` (route line; falls back to plan meta.route), `end.line` (clay home-plate before the footer), `days[d].theme`, `brief_titles`; theme `cover.title_stem`, `zones[]` (kind ∈ ridge|plain|coast|forest|lake|desert (neutral SVG; **default ridge**) | custom {band,to,decor} (your own band — full recipe below) | city|park|west|isle (US-2026 place-bound cut-out bands — never for another trip)), `days[d].figurine`. Sizes: title_stem/figurine/decor/clouds → md; band → band→cut→md→full. **All clay picture slots are cut-outs** (`.cut.webp` from `cutout.py` / a sheet cell).

```jsonc
// ---- common (used by clay) ----
"cover": {
  "kick": "美国行",              // <title> "{kick} {year} · 黏土版" and export filename prefix (export_prefix) on a zh page
  "kick_en": "US 2026"          // en page: <title> / filename prefix instead of kick
},
"days": { "<date>": { "theme": "跨洋首夜" } },   // art.day_theme(date, city) — copied from theme_common.DAY_THEME

// ---- NEW theme block: `clay` (黏土版) — paste into ART-SCHEMA.md ----
"themes": { "clay": {
  "cover": {"zh": "美国行 捏好了",                       // display title: alt of the sticker image, or the text h1 when no sticker
            "sub": "纽约 → 黄石 → 优胜美地 → 夏威夷 → 北京",  // one-line route under the title. NOT derivable from
                                                        // plan meta.route (that is "北京 → 纽约 → 哥伦布(球赛·可切C分支) → …"),
                                                        // so it lives here; missing → meta.route, else the date span, else no line
            "title_stem": "clay-title"},                // 3D clay title sticker (words baked into the image);
                                                        // missing / file absent → plain embossed text h1 (cover.zh → kick → 黏土世界)
  "zones": [ {"from_day": 1, "kind": "city"},           // where the terrain changes; from_day = 1-based day number OR ISO date;
             {"from_day": 4, "kind": "park"},           // kind ∈ kit terrains (see Kit); first zone always starts on day 1;
             {"from_day": 7, "kind": "west"},           // empty zones dropped; unknown kind → default 'ridge' + one stderr
             {"from_day": 9, "kind": "isle"} ],         // warning; missing → one 'ridge' zone for the whole trip (US-2026 = the
                                                        // four place-bound kinds above; every other trip: neutral kinds or custom).
                                                        // Colour ramp / band / edge furniture per kind are the renderer's.
  "days": {
    "2026-09-26": {"figurine": "clay-liberty"}          // asset stem of the clay figurine beside the day head; missing → none
  }
}}
// Migration table row: | clay 黏土 | ✅ 2026-08-15 | byte-identical rebuild proven; terrain kit (4 kinds) + chained ramp stay in renderer; text-h1 fallback when no title sticker |
```

**Custom terrain — a complete, copy-able zone list** (Turkey test 2026-08-15, three
zones, every seam clean in the export; the China test used the same shape with
`china-strip-xian` / `china-strip-beijing`):

```jsonc
"zones": [
  {"from_day": "2026-10-01", "kind": "custom", "band": "turkey-strip-istanbul",
   "to": "#bfe0e6", "decor": ["clay-signpost", "turkey-clay-tea"]},          // Bosphorus pale teal
  {"from_day": "2026-10-04", "kind": "custom", "band": "turkey-strip-cappadocia",
   "to": "#f0cba4", "decor": ["clay-balloon", "clay-pines"]},                // tuff apricot
  {"from_day": "2026-10-07", "kind": "custom", "band": "turkey-strip-pamukkale",
   "to": "#cfe7ea", "decor": ["clay-pines", "clay-cloud-b"]}                 // travertine blue-white
]
```

- **`to`** = the ground colour the zone ramps down to (`#rrggbb`; bad/missing → `#d8e2d5`
  + one warning). The ramp is chained by the renderer: the sky's foot **`SKY_FOOT
  #dcefe6` → zone1.to → zone2.to → … → appendix `DEEP_TO #5fb2b6`**, each zone starting on
  the previous ground — so pick each `to` as "the colour of *this* landscape's ground"
  and the seams look after themselves (pale sea → warm rock → chalk-white above).
- **`band`** = the terrain strip's stem. Generate a 16:9 white-background strip and run
  `cutout.py` on it — `<stem>.cut.webp` is enough (`band → cut → md → full` chain; a
  hand-cut `.band.webp` is optional). Prompt template: copy the `china-strip-xian` /
  `china-strip-beijing` entries in `themes/assets/manifest.json` (or the Turkey
  `turkey-strip-*` rows in `trips/test-turkey-2026/manifest.turkey.json`): "Wide
  horizontal diorama strip of handmade polymer clay scenery isolated on a solid pure
  white background: … the top half of the image is pure empty white …", `background:
  opaque, aspect_ratio: 16:9, resolution: 2K, quality: medium`, ≈$0.033 each. Missing
  band / absent file → just the ramp, no strip.
- **`decor`** = edge furniture; bare stems take the kit's four edge slots **in order:
  L (upper-left) · R (upper-right) · L-low · R-low** (`CUSTOM_DECOR_POS` in
  `render_clay2.py`); or `{"stem", "pos": "<inline style>"}` to place one yourself. Kit
  props any trip may use: `clay-pines` `clay-signpost` `clay-cloud-a/b/c` `clay-balloon`
  `clay-bus-solo` (IMAGE-LIBRARY §通用件); a trip's own figurine (`turkey-clay-tea`) is fine
  too. Two per zone is the comfortable count.
- The band + figurines + title sticker are all cut-outs (see the size table).

**Kit (theme-owned, not in art)**: TERRAIN kinds (art picks by `kind`): city = strip-mountains band + signpost + pines, ground #cfe8c9 · park = strip-geyser + pines, #e6dcb0 · west = strip-desert + cactus, #f0c9a0 · isle = strip-ocean + palm, #7fc9c6. Ramp chaining: SKY_FOOT #dcefe6 → zone1.to → zone2.to … → appendix DEEP_TO #5fb2b6 (appendix --from = last zone's ground; export-CSS #appendix slice likewise). Sky furniture: clay-cloud-a/b/c, clay-balloon, tour bus clay-bus-solo (kit assets, omitted cleanly if a file is missing via img() helper — never an empty src). PEBBLE palette by day number (i%4), left/right alternation by day parity, winding road + road-nav + scrollspy, mist slabs, export beans, footer 「黏土世界由 AI 生成」 credit, text-h1 fallback CSS (emitted only when there is no title sticker), <title> "{kick} {year} · 黏土版" composition. Class names z-city/z-park/z-west/z-isle/z-deep unchanged.

## Theme block: `glass` (玻璃版)

**reads:** common `cover.kick/kick_en/zh/en/sub/credit` (sub → one glass strip under h1; \n breaks), `days[d].theme`, `brief_titles`; theme `plates[]`, `zones[]`, `day_plate` (date or day-number keys). Sizes: plates → no size arg (md→cut→plain; ship 16:9 `<stem>.webp`). Limits: h1 ≤10 Latin caps / 6 CJK per line (390px: 9/5); en ≤45; sub ≤66 Latin / 32 CJK per line; credit ≤85/39.

```jsonc
// ---- ART-SCHEMA.md additions for theme block `glass` (玻璃版) ----
// Common fields READ by render_glass2: cover.kick (title/<title> + export_prefix), days[date].theme.
// (fragment also carries cover.kick_en / postmark_date and all 11 days[date].theme copied from theme_common.DAY_THEME — values identical to plan-A.art.json.)

"themes": { "glass": {
  "cover": {"zh": "秋水长天", "en": "Where Water Meets Sky",
            "credit": "「秋水共长天一色」—— 王勃《滕王阁序》"},   // zh missing → 玻璃; en/credit missing → line not emitted
  "plates": ["glass-hero", "glass-city", "glass-park", "glass-west", "glass-island", "glass-dawn"],
                // fixed backdrop world in scroll order; [0] = hero/cover backdrop, LAST = appendix backdrop.
                // Missing/empty → no photo layers, flat #eef2f4 + scrim, footer drops the AI-scenery credit;
                // a plate whose file is absent just contributes no layer.
  "zones":  ["hero", "z-city", "z-park", "z-west", "z-isle", "z-dawn"],
                // OPTIONAL, parallel to plates: the data-zone slugs the cross-fade JS keys on (internal, never
                // displayed). Missing/short → "hero", "z1", "z2", … . Only needed to keep existing DOM ids stable.
  "day_plate": {"2026-09-25": 1, "2026-09-26": 1, "2026-09-27": 1, "2026-09-28": 2, "…": 3}
                // {"<ISO date>" | "<1-based day number>": plate index} — same contract as noir.day_plate:
                // date keys safer, mixed OK, date wins; missing key → plate 1 (0 if ≤1 plate); out-of-range
                // index → default; count mismatch / stray keys → one stderr warning each, page still renders.
}}

// Migration-status table row to add:
// | glass 玻璃 | ✅ 2026-08-15 | byte-identical rebuild proven (zero diffs); plates/zones/day_plate; day_plate accepts date keys |
```

**Kit (theme-owned, not in art)**: Stays in render_glass2.py (theme's own, nothing to pick in art): liquid-glass material (.glass blur+saturate, specular rim stack, ::after sheen, .lens SVG feImage displacement filter, Chromium gate); fixed cross-fading backdrop stage (#sky/.bd + IntersectionObserver zone spy, kit default zone ids "hero"/"z<n>" via zone_id()); glass rail → mobile floating dock; hairline time ledger (.tchip / k-anchor / k-meal); pills/pillfold, lazy map embed; export chips (X_ICON, xbtn) + export-only solid-glass extra_css; inlined lucide icons (ic/et); the neutral fallback words 玻璃 (h1) / 玻璃版 (<title>, export tag) and the day-title fallback to plan `city`; js_str() for safe zone-id injection into the script.

## Theme block: `zine` (Zine 版)

**reads:** common `cover.zh` `cover.en` `cover.credit` (since 2026-08-16) `cover.kick`
`cover.kick_en` · `days[d].theme` (≤10 Latin chars — vertical title) · `brief_titles` (no
`home` / `end` / `days[d].en|mark`).

```jsonc
// ---- COMMON (used by zine; values identical to journal/noir fragments) ----
// cover.kick "美国行" · cover.kick_en "US 2026" · days[d].theme (11 entries copied from theme_common.DAY_THEME)
// zine reads no home/end/mark/en.

// ---- NEW theme block: `zine` (拼贴 zine) — paste under "## Theme block" ----
"themes": { "zine": {
  "cover": {"zh": "拾景",                          // h1 (big vertical glyphs, clamp(96px,19vw,196px) each) + "<zh> ZINE" issue name on every page number and in the colophon → kick, then 拼贴.
                                                   // 2 glyphs is the design; 4 is the ceiling (4 CJK ≈ 784px tall on desktop) — trim a 5-char poem title before it gets here
            "en": "GATHERED SCENES",               // eyebrow "<kick> · <en> ZINE · <year>", edge line "<en> · N DAYS · <kick_en>" → "COLLAGE"
            "credit": "「万人如海一身藏」—— 苏轼",  // the allusion's source, small line on the cover (read since 2026-08-16) → omitted
            "photo": {"stem": "zine-nyc", "caption": "MANHATTAN · NEW YORK",
                      "alt": "曼哈顿天际线海报画", "tear_seed": "cover-nyc"}},   // torn cover print; caption = a "PLACE · CITY" letterspaced CAPS side line (not a place for the poem's source — that is cover.credit); alt defaults to caption; tear_seed seeds the torn edge (default "cover-<stem>"; the US page pins the original) → no cover print
  "toc_strip": [ {"stem": "plane", "rot": -3}, {"stem": "prismatic", "rot": 2} ],   // small gouache cut-outs (sm variant) above the contents → none
  "props": {"legs":      {"stem": "journal-boarding", "rot": -3},     // paper prop floated in that colophon section
            "hotels":    {"stem": "journal-tag",      "rot": 4},
            "checklist": {"stem": "journal-ticket",   "rot": -2}},    // missing key → no prop
  "days": {
    "2026-09-27": {
      "poster":  {"stem": "zine-stadium", "caption": "MATCH NIGHT · COLUMBUS"},   // poster-grade torn print, the chapter anchor; optional "alt", optional "side" pl|pr (default: posters alternate pl/pr down the book — kit rhythm)
      "photo":   {"stem": "journal-ph-soccer", "caption": "CREW VS INTER MIAMI",
                  "alt": "球场夜赛看台与绿茵", "treat": "mono", "rot": 2.4},      // one Kodak print on the fibre mat; treat "mono" = B&W + red offset shadow; optional "side" pl|pr (default pr) — IGNORED on a poster day: the print then takes the poster's opposite side, clears it and is emitted after the timeline (kit rule, defect ⑨)
      "pair":    {"prints": [{"stem": "journal-ph-nyc", "alt": "布鲁克林大桥黄昏", "treat": "duo-blue", "rot": -1.0},
                             {"stem": "journal-ph-liberty", "alt": "自由女神像", "rot": 2.3}],
                  "caption": "BRIDGE + LIBERTY · NYC", "rot": -1.2},             // big + small overlapping prints as one figure; treat on a print = img class (duo-blue = blue duotone); wins over photo; either file missing → nothing
      "sticker": {"stem": "prismatic", "size": "md", "side": "sl", "rot": -3.0},   // gouache cut-out near the line drawing; size md|sm (default md), side sl|sr (default sl)
      "band":    {"stem": "zine-hawaii", "caption": "PACIFIC · O'AHU", "tear_seed": "band-hawaii"},   // full-bleed torn band photo closing the chapter (last day of the US book); tear_seed default "band-<stem>"
      "lineart": "stadium"                       // KIT sketch name, or {"svg": "<inner markup>"} (640x190 viewBox, stroked currentColor) → no drawing
    }
  }
}}
// Kit sketches (days[d].lineart): flight (dashed arc + plane) · skyline · stadium · flats (road + sun) · peaks (ridge over a lake) · bridge · ridge (granite ridge) · surf (waves + palm) · volcano · sunrise.
// Print treatments: mono (figure-level, single print) · duo-blue (img-level, pair prints).
// Note on rot values: floats are emitted verbatim (`--rot:-1.0deg`), so write -1.0 not -1 where the original had a float.

// Migration table row: | zine 拼贴 | ✅ 2026-08-15 | byte-identical rebuild; posters/prints/pairs/stickers/band/lineart/toc strip/colophon props all from art; poster side alternation + poster-day print placement are kit rules |
```

**Kit (theme-owned, not in art)**: Stays in render_zine.py (theme-owned, art only picks): (1) colour-band cycle BAND=[ink,blue,yellow,red,blue,ink,red,yellow,blue,ink,red] via band_for(i) — wraps for >11 days without adjacent repeats; (2) poster side rhythm — k-th rendered poster alternates pl/pr (art may override with poster.side); (3) poster-day print rule — print/pair takes the poster's OPPOSITE side + clr and is emitted after the timeline (defect ⑨), otherwise its own side/pr before the timeline; (4) print treatments: mono (figure class + red offset shadow), duo-blue (img class); (5) LA line-art sketches keyed by name: flight, skyline, stadium, flats, peaks, bridge, ridge, surf, volcano, sunrise, plus {"svg": ...} passthrough; (6) torn-edge generators (_tear_polys / torn_photo_polys / torn_band_polys / chip_poly), noise + ring textures, halftone .ht, crop marks, barcode issue strip (digits from plan dates), rubber stamp frame (text "READ BEFORE DEPARTURE · <kick_en> ·"), riso export plates, rail chips, tocstrip/prop/sticker frames (sm/md variants); (7) neutral fallbacks: h1 "拼贴", en "COLLAGE", <title> "<kick> <year> · Zine 拼贴版", export theme "Zine版".

## Theme block: `splash` (闪屏版)

**reads:** common `cover.kick/kick_en/zh/sub/en/credit` (kick_en → en `<title>`/filename; en → small-caps line under the title plate; credit → cream mono badge under the route), `end.line/fine`, `days[d].theme`, `brief_titles`; theme `hero`, `appendix`, `vehicles/mascots/strips` registries, `days[d].{island,palette,fx,sides,strip,vehicle,mascot}`. Sizes: hero.title/hero.art → md; days[d].island → sm; vehicles/mascots/strips/kit and sides {stem,w} → cut/sm; `ratio` = cut-out w/h. Limits: text title without a plate ~14 Latin caps / 8 CJK (1200px), ~8/5 (390px); route/sub 27 Latin / 18 CJK per line at 390px.


```jsonc
"cover": {"kick": "美国行"},                    // <title> 「{kick} {year} · 闪屏版行程」+ 导出文件名前缀
"end":   {"line": "北京,到家了。"},             // 尾牌;fine 见主题块(闪屏版带年份)
"themes": { "splash": {
  "cover": {"zh": "美国行",                     // 标题牌 alt;没有标题牌时就是文字大标题(缺→kick→「出发!」)
            "sub": "纽约 · 球赛 · 黄石 · 优胜美地 · 火山"},   // 海报下的路线行(缺→plan meta.route→不写)
  "end":   {"fine": "2026-10-07 週三 12:00 落地 —— 跨过日界线,日历上的 10-06 在空中消失。"},
  "hero": {"palette": "night",                  // 第 0 章(封面)天色:kit 情绪名;或 "scene":[4 hex] + "wash":[hex…]
           "title": "splash-title",             // 手绘标题牌 stem(md 档,抠图件:cutout.py → towebp x.cut.png --sizes md);缺→文字标题(kit CSS 按需注入)
           "art":   "splash-hero",              // 海报主岛 stem(md 档,抠图件——直接 towebp --sizes md 会嵌进一张白底方块且零报错);缺→整个 figure(含其 fx)不画
           "sides": ["balloon"]},               // 侧场额外漂浮件(kit 词或 {"stem","w"} 行程自有抠图)
  "appendix": {"palette": "homebound"},         // 末章天色 / 可加 sides
  "vehicles": {                                 // 行程自己的交通工具贴纸 → 生成 .veh-<kind>;stem 一律是抠图件(.cut.webp)
    "plane":   {"stem": "splash-plane",   "ratio": "428/277", "speedlines": true},   // speedlines = 奶油尾迹;ratio = 该 .cut.webp 的真实像素 w/h(不是母图/sheet 的)—— 抠完 `python3 -c 'from PIL import Image;print(Image.open("x.cut.webp").size)'` 抄进来
    "bus":     {"stem": "splash-bus",     "ratio": "399/390"},
    "sequoia": {"stem": "splash-sequoia", "ratio": "395/434"}},
  "mascots": {"hotdog": {"stem": "splash-m-hotdog", "ratio": "330/408"}, "…": {}},   // → .mas-<kind>
  "strips":  {"city": {"stem": "splash-strip-city", "ratio": "1433/314"},            // 章脚剪影条 → .strip-<kind>
              "gg":   {"stem": "splash-strip-goldengate", "ratio": "1431/391"}},
  "days": {
    "2026-09-29": {
      "palette": "rainbow",                     // 本章天色情绪名(链式:起色=上一章末色);或 "scene"/"wash" 显式色值
      "island":  "splash-geyser",               // 漂浮岛 stem(sm 档,抠图件);缺→无岛(无 fx 时按序号放 CSS 勋章 moon/dusk/sunrise)
      "fx":      "rainbow",                     // 岛后场景特效,kit 词:halo-cyan|halo-gold|halo-teal|burst|beams-cool|rainbow|"rainbow sm"|sun|moon|dusk|sunrise|""(不要)
      "vehicle": {"kind": "bus", "when": "post",            // kind 指向 vehicles;when=pre 在岛后 / post 在岛前
                  "pos": "left:-14%;bottom:-3%;width:clamp(120px,13vw,150px);--vr:-2deg"},   // .scene 内的内联定位(--vr 倾斜,--vsx:-1 镜像)
                  // pos 安全范围(.scene 是 position:relative 的居中格,岛宽 clamp(200px,46vw,330px);.chap overflow:hidden 兜底):
                  //   left|right: -8% … -18%(负值 = 探到岛外侧;再大就贴到章节边缘/被裁)
                  //   bottom: -8% … +4%(或 top: -12% … +4% 挂在岛肩上)
                  //   width: clamp(76–130px, 8–15vw, 100–175px);--vr: -8deg … 8deg
                  // 以上是 US/China/Vietnam 三份成品页 30 余条 pos 的实测区间;出圈的值渲染不会报错,只能靠 xprobe 目检
      "mascot":  {"kind": "bison", "pos": "right:-9%;bottom:-2%;width:clamp(88px,9.5vw,120px);--vr:3deg"},   // 同一套 pos 范围;吉祥物一般 8–9.5vw
      "strip":   "city",                        // 指向 strips 的名字
      "sides":   ["balloon"]                    // 侧场额外件
    }
  }
}}
```
资源找不到的 vehicles/mascots/strips 条目整个不生成 CSS 类,引用它的日子也不画;未知 palette 名回落到序号节奏;未知 side kind 画成 spark。

**Kit (theme-owned, not in art)**: 留在渲染器的 kit:
- MOODS 天色情绪表(12 种:night/neon/lilac/floodlight/dusk/rainbow/alpine/goldfog/canyon/ocean/lava/sunrise/homebound,每种 4 个渐变停点 + 洗色 pastel 表;停点已按 AA 预校)+ 链式接缝机制 resolve_chain()(第 i+1 章起色 = 第 i 章末色)+ HERO_MOOD/APPX_MOOD 默认 + DEFAULT_RHYTHM(无 art 时按天序号循环情绪)+ contrast_report() 建期复核实际链。
- 章节索引约定(0=hero,1..N=天,N+1=附录)及所有 seeded RNG(deco 洗/光带/柔焦/纸屑;sides 侧场;hill 山脊)——种子是冻结常量,内容按索引掷。
- 侧场池 cloud×2/spark/dot/shard/heart/star + 通用抠图 splash-cloud-a..d/splash-star/splash-balloon(主题库 embeds)+ 新增 {"stem","w"} img 件。
- 头部特效 head_fx():halo-cyan/gold/teal、burst、beams-cool、rainbow(sm)、sun,以及三枚 CSS 勋章 moon/dusk/sunrise(MEDALLIONS,无岛无 fx 时按序号轮放)。
- 交通工具/吉祥物/剪影条的**机制**:.veh/.mas/.strip 基类、drift 动画、speedlines 尾迹、STRIP_A 透明度封顶、kit_css() 按注册表生成 .veh-<kind>/.mas-<kind>/.strip-<kind> 类(吉祥物选择器对齐补空与原手写块一致)。
- 丝带路 + 3.5/96.5 gutter、大数字、色带、导出徽章、TITLE_TXT_CSS 文字标题回退(仅无标题牌时注入)。
- 文案中性词:<title> 后缀「闪屏版行程」、h1 回退「出发!」、附录/尾牌图形。


## Theme block: `portal` (穿越版 — scroll-scrubbed video)

**reads:** common `cover.kick/kick_en/zh/en` (kick_en → en `<title>`/filename; en → en-page h1 first), `days[d].theme`; theme `tag` (intro eyebrow; default "PORTAL · <N> WORLDS · ONE TAKE", N = dives), `intro`, `outro{tag,zh,text}`, `video_dir` (relative to THIS art file; page links clips relative to the OUTPUT html), `clips[]{file,dur,off,kind,day}` (dur = ffprobe seconds; off = seconds skipped at the head; 0 clips → intro/outro only, 1 → single-slot playback, ≥2 → frame-chained seams). Footage: `genvideo.py` (OpenRouter) or `build_portal_jobs.py --spec worlds.json` (local ComfyUI).

```jsonc
"themes": { "portal": {
  "cover": {"zh": "穿越美国行"},               // intro h1 → "穿越{kick}" → "穿越"; en page reads cover.en first, then zh
  "intro": "滚动就是飞行:纽约黄昏 → … 十个小世界一镜到底 …",   // intro paragraph → generic sentence
  "outro": {"tag": "DIAMOND HEAD · SUNRISE", "zh": "落在日出里", "text": "…"},   // → TOUCHDOWN / 落地 / generic; en page: outro.en before outro.zh
  "video_dir": "../../themes/assets/portal",  // relative to THIS art file (or absolute); the page links
                                              // clips relative to the OUTPUT html so file:// still works.
                                              // NB: that dir is EMPTY in a fresh clone — the US reference
                                              // chain is a release asset, restored with one curl+unzip
                                              // (themes/assets/portal/README.md). A real trip points
                                              // video_dir at its OWN chain beside the plan.
  "clips": [                                   // reel order; kind dive|link; day = 1-based plan day whose
    {"file": "s01-dive.mp4", "dur": 5.167, "off": 0, "kind": "dive", "day": 2},   //   overlay fades in
    {"file": "s01-s02-link.mp4", "dur": 3.75, "off": 0, "kind": "link"}
  ]
}}
```
No `clips` → the page renders intro/outro only (no footage). Footage: either
`themes/genvideo.py` (OpenRouter video API — same key as images; `first_frame` = the world's
still, links use `first_frame` + `last_frame`; ≈$3 per ten-world chain on veo-3.1-lite) or
`build_portal_jobs.py` on a local MiniMax-H3 ComfyUI box (free, our regression path;
`STEPS` defaults to 10 since 2026-08-16 — 20 looked the same to the owner and took twice
the wall clock: 5 dives + 4 links ≈ 21 min at 10 vs ≈ 39 min at 20). A
missing clip file prints a WARN and the page simply has a black gap there.

## Sizes each field resolves (`data_uri(stem, size)`)

`data_uri` chain: an explicit size tries `<stem>.<size>.webp` first, then falls through
`<stem>.md.webp` → `<stem>.cut.webp` → `<stem>.webp`; **no size given = the md-first
chain**. So a field listed as `md` (or "—") is happy with only a `.cut.webp` / `.webp` on
disk; a field listed as `sm` wants a `.sm.webp` or it inlines the whole cut file into a
thumbnail slot (the base64 doubling IMAGE-LIBRARY warns about). Column "wants" = the
variant to ship; "falls to" = what it inlines when that file is missing.

**Column "shape" — cut-out or opaque — decides which tool makes the file, and the wrong
tool fails silently.** A *cut-out* slot (sticker, island, figurine, band, stamp, prop) is
`cutout.py x.png` → `x.cut.webp` (a sheet cell already is one), then, if the slot wants
sizes, `towebp.py x.cut.png --sizes sm,md,lg` (the `.cut` stem is kept: `x.sm.webp` …).
Running `towebp.py x.png --sizes md` straight on the generated PNG makes `x.md.webp` from
the white-background original — a white square, zero errors, and `data_uri` embeds it
(Vietnam splash `hero.art`, 2026-08-15). An *opaque* slot (photo, plate, poster, cover
painting) is `towebp.py x.png` → `x.webp` — never `cutout.py` (it would eat the sky).

| theme | field | shape | wants | falls to |
|---|---|---|---|---|
| journal | `days[d].props[kind=img \| flora].stem`, `stamps.*`, kit scans (tapes / washi / flora / seal / tag) | cut-out | — (md-first) | md → cut → full |
| journal | `cover.photo.stem`, `days[d].photo`, `days[d].photos2[].stem` | rectangle inside a polaroid frame — a sheet cell (`.cut.webp`) or an opaque `.webp` both work | — (md-first) | md → cut → full |
| journal | `days[d].props[kind=postcard].stem`, `days[d].poster.stem` | opaque scan | md | cut → full |
| noir | `plates[]` | opaque 16:9 | — (md-first; ship the opaque `<stem>.webp` — no md exists for 16:9 plates) | md → cut → full |
| illustrated | `days[d].hero` | **cut-out** | **sm** (menu card) + **md** (plate sticker) + **lg** (backdrop) — three inlines of one stem. (A sheet cell yields only sm + cut — cells are 300–560 px, `towebp` skips md/lg that would not shrink; the md/lg slots then fall to `.cut.webp`, which is normal and looks right.) | each → md → cut → full |
| illustrated | `cover.hero` | opaque full-bleed painting | — (md-first; ship the full `<stem>.webp`) | md → cut → full |
| illustrated | `end.hero` | **cut-out** (the coming-home scene) | md | cut → full |
| zine | `cover.photo.stem`, `days[d].poster.stem`, `days[d].photo.stem`, `days[d].pair.prints[].stem`, `days[d].band.stem` | opaque print | — (md-first) | md → cut → full |
| zine | `props.{legs,hotels,checklist}.stem` (paper props: boarding pass / tag / ticket) | cut-out | — (md-first) | md → cut → full |
| zine | `days[d].sticker.stem` | **cut-out** (gouache) | `sticker.size` (md \| sm, default md) | md → cut → full |
| zine | `toc_strip[].stem` | **cut-out** | **sm** | md → cut → full |
| clay | `cover.title_stem`, `days[d].figurine`, `zones[].decor[]`, kit clouds | **cut-out** (all of clay) | md | cut → full |
| clay | `zones[].band` | **cut-out** strip (16:9 generated, `cutout.py` is enough) | band | cut → md → full |
| glass | `plates[]` | opaque 16:9 `<stem>.webp` | no size arg (md → cut → plain) | |
| splash | `hero.title`, `hero.art` | **cut-out** | md | cut → full |
| splash | `days[d].island` | **cut-out** | **sm** | md → cut → full |
| splash | `vehicles/mascots/strips` registry stems, kit cut-outs | **cut-out** (`ratio` = that `.cut.webp`'s w/h) | cut | md → full |
| splash | `sides[] {stem,w}` | **cut-out** | sm | md → cut → full |
| portal | no images — `clips[].file` mp4 sidecars | | | |

## Authoring a new trip's art (what the skill does at Phase 6)

1. Pick the theme(s). Fill the **common** block first: cover title from
   `references/cover-titles.md`, `home`, `end`, and for every day `theme` (4 chars),
   `en`, `mark`.
2. Per theme, pick pictures. **Destination scenery is generated for THIS trip, in
   the theme's style, every time**: the cover painting / hero plate / title sticker /
   clay terrain bands / noir plates / splash islands. Priority: the trip's own sights
   (Xi'an wall + bell tower + warriors + pagoda; Great Wall over ridges + Forbidden
   City — see `china-strip-xian` / `china-strip-beijing`, made from the same prompt
   template as the US `strip-*` bands) > a national landmark > a neutral scene. A
   page that opens on another country's skyline is a defect, not a saving; a page
   with no scenery at all is a missed shot. "Reuse first" applies to generic props only —
   `IMAGE-LIBRARY.md` §通用件: a plane, a bus, a cloud, luggage, a wing shot, a
   generic beach. Generate the rest with the sheet recipe; `gen.py --manifest
   <trip>/manifest.<trip>.json` registers it in the trip's own manifest (never
   `themes/assets/manifest.json` — see 测试行程资产回收 below). Title stickers: one
   centred sticker, both lines the same height, no icons/moons inside the letters,
   wide white margin (see china-clay-title2; Turkey tester's tip — simple glyphs, ≤8
   strokes, keep the strokes intact:「九万里风」came out clean first time).
2b. **没有生成能力就走素材库(stock 模式),不是退回纯文本页。** Phase 0 的图片能力检查把结果
   写进 plan 的 `prefs.pictures`:`native`(agent 自带生图)/ `key`(存在
   `themes/.auth_header`,只 `test -s` 判断,永不读取打印)/ `stock`(两者都没有)。`stock` 下
   用内置素材包把图片补齐,页面照样交付主题版:
   ```bash
   python3 <skill>/themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
   # 还有 --theme clay · --lang zh|en · --index PATH(换一份 stock 索引)
   ```
   脚本按行程国家 + 每天停靠点的关键词,从 `themes/assets/stock/`(索引 `stock/index.json`,
   清单见 `stock/README.md`)加共享图库里同国图片与通用件(`IMAGE-LIBRARY.md` §通用件)挑图,
   **只填图片槽位**:封面画、每天的 hero / 抠图件、道具。**文字照旧由你写**——封面标题
   (`references/cover-titles.md`)、每天 `theme`(4 字)/ `en` / `mark`、图注、批注、结尾句;
   带着脚本占位词交付算缺陷,判据和下面第 3 步一样。脚本会把素材库说明写进 `end.fine`,**别删**,
   聊天摘要里再说一遍(「图片来自内置素材库(本次未接入生图能力);接入生图模型或 KEY 后可为本次
   行程定制生成。」),也永远不要在对话里索要 KEY。覆盖度:**插画版**完整;**黏土版**可用(地形带
   走内置中性 SVG 套件 `ridge|plain|coast|forest|lake|desert` + 通用黏土道具);夜航 / 玻璃 /
   手账 / Zine / 闪屏 / 穿越这六个主题的图版、照片、岛屿、视频仍然必须生成——用户点名要它们时,
   说明情况并改推插画版,硬渲染只会得到一页空图槽(穿越版更是连素材都没有)。
3. Write the words: captions, annotations, doodle notes, the closing line. Voice
   rules live in each theme's renderer docstring.
4. Render, run `qc.py`, eyeball an export.

**生成器选择(先看这一条)**:如果当前 AI / agent **自身就有图片(或视频)生成能力**(内置的
image / video 生成工具、可直接调用的原生生图),**优先直接用自己的能力生成,不需要配置任何 KEY**——
`gen.py` / `genvideo.py` + OpenRouter 只是给「运行环境没有原生生成能力」准备的备胎。用自身能力时,
下游的切图 / 抠图 / webp / manifest 四步**一步不少**,而且要满足同一套产物契约:
- **规格照旧**:全幅件 16:9(1536×864 或 2K);sheet 件按「N 件 C×R 网格 · 纯白背景 · 宽白沟槽 ·
  无边框无文字」写提示词(照抄 manifest 里 `*-sheet-*` 的骨架)才能被 `split_sheet.py` 认格;
  抠图件=单一主体 + 纯白/纯色背景,`cutout.py` 才抠得净;标题贴纸规则同上一节。
- **提示词照抄本库的风格锚**:同主题条目的 prompt + `manifest.json` 顶部 `style_anchor`,保证和
  已有资产同一风格族(黏土像黏土、riso 像 riso),不要即兴换风格。
- **落盘位置与命名不变**:`<trip>/<trip>-<name>.png`,然后照下面 ①②③④ 跑 split_sheet / cutout / towebp。
- **仍要记进 `<trip>/manifest.<trip>.json`**:`model` 写你实际用的生成器名,`cost_usd` 写 0 或实际,
  `prompt` 全文保留——回收入库和「已有就复用」都靠它。
- **视频(portal)**同理:产物契约见 portal 块——mp4 h264 16:9(1344×768 或 1280×720)24 fps,
  dive 5–6 s / link 4 s,link 需要**首尾帧条件**;原生视频能力若不支持首尾帧,只出 dive、link 留空并在
  art.json 里注明,页面会走单段兜底。
只有当前环境**没有**原生生成能力时,才走 `gen.py` / `genvideo.py`(需要 `themes/.auth_header` 一行
OpenRouter key)——下面的命令都是这条备胎路径。

**图片工具链**(全部在 themes/,不必复制;密钥只在 themes/ 读;共享图库在 themes/assets/)。
**每条命令都写全路径**——agent 的 shell cwd 每次调用都会重置,`cd` 不保留;下面
`<skill>` = skill 根目录,`<trip>` = 行程目录(如 `trips/kyoto-2027`),四步都从 `<skill>` 起跑:

```bash
# ① 生成(先 --dry-run 看 payload;PNG 与 manifest 落到 <trip>,themes/assets/manifest.json 不动)
python3 <skill>/themes/gen.py <trip>/jobs.json --outdir <trip> --manifest <trip>/manifest.<trip>.json
# ② 切 sheet:先 --probe 看它认出几格,再按 prompt 的 Row 1 / Row 2 顺序敲件名(reading order)
python3 <skill>/themes/split_sheet.py <trip>/x-sheet.png --probe
python3 <skill>/themes/split_sheet.py <trip>/x-sheet.png --grid 3x2 name1 name2 … name6 --outdir <trip>
# ③ 单件抠图(抠图槽位:贴纸/岛/小人/地形带/邮票/道具)
python3 <skill>/themes/cutout.py <trip>/x.png --outdir <trip>            # → x.cut.png + x.cut.webp
# ④ webp 与尺寸档:不透明大图直接喂 png;抠图件喂 .cut.png(stem 保持 x,不会变成 x.cut.cut)
python3 <skill>/themes/towebp.py <trip>/x.png --outdir <trip>                       # 不透明 → x.webp
python3 <skill>/themes/towebp.py <trip>/x.cut.png --sizes sm,md,lg --outdir <trip>  # 抠图 → x.sm/md/lg.webp
```
`split_sheet.py` / `cutout.py` / `towebp.py` 的 `--outdir` 默认都是**输入文件所在目录**
(`towebp.py` 一直如此;前两者 2026-08-16 起——之前写 cwd),所以给了 `<trip>/x.png` 就不必再写
`--outdir`——上面写出来是为了看得见落点。

- **sheet 配方**(一张 $0.04 切 6–12 件,零返工):照抄 `manifest.json` 里
  `journal-sheet-photo-a` 的 prompt 骨架——「SIX separate … 3-column by 2-row grid on a plain
  pure white background, WIDE empty white gutters between every photo and a wide white
  margin around the grid, each … a simple borderless rectangle, no borders, no text」,
  再逐格写 Row 1/Row 2 的内容;参数 `background:opaque, aspect_ratio:3:2, resolution:2K,
  quality:medium`。**切格顺序:先 `--probe` 确认格数与 prompt 的格数一致,再按 Row 1 → Row 2
  的顺序敲件名**——件名和 prompt 行序一旦错位,整张 sheet 的件全部错名而下游零报错(墨西哥 P3)。
  `--probe` 认出的格数少于 prompt(闪屏星星落进沟槽把两列并成一列)→ 加 `--grid 3x2` 按列×行硬切。
  产物 `<name>.png/.cut.png/.cut.webp`。**sheet 切出的件通常只有 sm + cut 两档**:格子约 300–560 px,
  `towebp --sizes sm,md,lg` 会跳过 md/lg(不比源小或字节反而更大就丢),插画 md/lg 槽位回落到
  `.cut.webp`,正常。
- 哪些槽位是抠图件、哪些是不透明件,看上面尺寸表的「shape」列;抠图件**先** `cutout.py` **再**
  `towebp.py x.cut.png`,直接 `towebp x.png --sizes md` 会得到一张白底方块且零报错(越南 F7)。
- `gen.py --outdir <trip>` 会在行程目录留下 `.png` 母图与 `.payload.json` 草稿——它们
  **不是交付物**(渲染器只吃 webp)。交付时只留 webp;png 母图可以删,或留在行程目录但不进 repo、
  不当资产入库(越南一趟 62 个 png 占 59 MB,真交付物 12 MB)。
- 资产放在行程目录即可(渲染器搜 plan 所在目录 → `--assets DIR` → themes/assets/);
  webp 命名与 `data_uri` 回退链一致,不要手改后缀。

**测试行程资产回收**(2026-08-16 定):`<trip>/manifest.<trip>.json` 是这趟生成物的**权威记录**
(prompt、参数、花费、切件名),写在行程目录就算登记完成。**测试员与普通用户不写 `themes/assets/`
和 `IMAGE-LIBRARY.md`**——通用件回收进共享图库、索引追加新章,由主 agent 在一批测试跑完后
统一做(`build_manifest.py` 刷 manifest + 手写索引段)。IMAGE-LIBRARY 里「新测试行程跑完照此追加」
说的是主 agent 的那一步,不是测试员的任务。

## Migration status

| theme | reads art.json | notes |
|---|---|---|
| journal 手账 | ✅ 2026-08-15 | byte-identical rebuild proven; same day: neutral stamp slots, 12 sketches + custom svg, CSS poster/postcard blanks, flora stem, CJK-safe note, auto-sized h1 |
| noir 夜航 | ✅ 2026-08-15 | one CSS comment generalised (only diff); day_plate accepts date keys |
| illustrated / clay / glass / zine / splash | ✅ 2026-08-15 | all five byte-identical rebuilds proven, kyoto bare renders verified; one merged `plan-A.art.json` drives all seven |
| portal 穿越版 | ✅ 2026-08-15 | `themes.portal` = clips / video_dir / intro / outro / cover.zh; clips linked relative to the output HTML; `theme_common.DAY_THEME` deleted the same day |

## Versioning

`"schema": 1` at the top level. Additive changes only; a renderer ignores keys it
does not know.
