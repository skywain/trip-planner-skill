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
ISO ends. Prose such as `10.01 抵达 – 10.08 离开(…)` ("arrive 10.01 – depart 10.08")
is passed through verbatim minus
years and lands on the cover date line of every theme exactly as written — it folded the
nordic cover.

**`plan.meta.route` is a cover line too** (journal prints it inside the cover envelope,
zine on the cover, clay and splash use it as the fallback for `cover.sub`). Keep it
**≤68 characters** — the journal envelope is the tightest: a 76-character English route
folded to two lines and hit the envelope's bottom edge, 68 sat on one line (Mexico
2026-08-15). CJK routes were not measured — verify with xprobe. If the plan's route must
carry branch prose ("哥伦布(球赛·可切C分支)" — "Columbus (match · can switch to branch C)")
for the plain page, give clay/splash their
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
(journal「美国行」/ noir「星垂平野」/ illustrated「碧海苍梧」…), so `zh/en/sub/credit`
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
keeps its owner-approved plain-speech「美国行」("US trip") as `zh` with the poem as `sub`.

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
  `clay-bus-solo` (IMAGE-LIBRARY §Generic pieces (通用件)); a trip's own figurine (`turkey-clay-tea`) is fine
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
"cover": {"kick": "美国行"},                    // <title> 「{kick} {year} · 闪屏版行程」 + export filename prefix
"end":   {"line": "北京,到家了。"},             // endcap plate; for fine see the theme block (splash carries the year)
"themes": { "splash": {
  "cover": {"zh": "美国行",                     // title-plate alt; with no title plate it IS the big text title (missing → kick → 「出发!」)
            "sub": "纽约 · 球赛 · 黄石 · 优胜美地 · 火山"},   // route line under the poster (missing → plan meta.route → not written)
  "end":   {"fine": "2026-10-07 週三 12:00 落地 —— 跨过日界线,日历上的 10-06 在空中消失。"},
  "hero": {"palette": "night",                  // chapter-0 (cover) sky: a kit mood name; or "scene": [4 hex] + "wash": [hex…]
           "title": "splash-title",             // hand-drawn title-plate stem (md size, a cut-out: cutout.py → towebp x.cut.png --sizes md); missing → text title (kit CSS injected on demand)
           "art":   "splash-hero",              // poster main-island stem (md size, a cut-out — towebp --sizes md straight on the PNG embeds a white square with zero errors); missing → the whole figure (its fx included) is not drawn
           "sides": ["balloon"]},               // extra floating side-field pieces (kit words, or {"stem","w"} for the trip's own cut-outs)
  "appendix": {"palette": "homebound"},         // final-chapter sky / may also take sides
  "vehicles": {                                 // the trip's own vehicle stickers → generates .veh-<kind>; stems are always cut-outs (.cut.webp)
    "plane":   {"stem": "splash-plane",   "ratio": "428/277", "speedlines": true},   // speedlines = cream contrail; ratio = that .cut.webp's REAL pixel w/h (not the master's / sheet's) — after cutting run `python3 -c 'from PIL import Image;print(Image.open("x.cut.webp").size)'` and copy it in
    "bus":     {"stem": "splash-bus",     "ratio": "399/390"},
    "sequoia": {"stem": "splash-sequoia", "ratio": "395/434"}},
  "mascots": {"hotdog": {"stem": "splash-m-hotdog", "ratio": "330/408"}, "…": {}},   // → .mas-<kind>
  "strips":  {"city": {"stem": "splash-strip-city", "ratio": "1433/314"},            // chapter-foot silhouette strips → .strip-<kind>
              "gg":   {"stem": "splash-strip-goldengate", "ratio": "1431/391"}},
  "days": {
    "2026-09-29": {
      "palette": "rainbow",                     // this chapter's sky mood name (chained: opening colour = previous chapter's closing colour); or explicit "scene"/"wash" hex values
      "island":  "splash-geyser",               // floating-island stem (sm size, a cut-out); missing → no island (with no fx either, a CSS medallion moon/dusk/sunrise is placed by day index)
      "fx":      "rainbow",                     // scene effect behind the island, kit words: halo-cyan|halo-gold|halo-teal|burst|beams-cool|rainbow|"rainbow sm"|sun|moon|dusk|sunrise|"" (none)
      "vehicle": {"kind": "bus", "when": "post",            // kind points into vehicles; when=pre sits behind the island / post in front of it
                  "pos": "left:-14%;bottom:-3%;width:clamp(120px,13vw,150px);--vr:-2deg"},   // inline positioning inside .scene (--vr tilt, --vsx:-1 mirror)
                  // pos safe ranges (.scene is a position:relative centred cell, island width clamp(200px,46vw,330px); .chap overflow:hidden is the backstop):
                  //   left|right: -8% … -18% (negative = poking past the island's outer edge; larger sticks to the chapter edge / gets clipped)
                  //   bottom: -8% … +4% (or top: -12% … +4% to hang on the island's shoulder)
                  //   width: clamp(76–130px, 8–15vw, 100–175px); --vr: -8deg … 8deg
                  // the measured envelope of the 30-odd pos values across the US/China/Vietnam finished pages; out-of-range values render without any error — only an xprobe eyeball catches them
      "mascot":  {"kind": "bison", "pos": "right:-9%;bottom:-2%;width:clamp(88px,9.5vw,120px);--vr:3deg"},   // same pos ranges; mascots usually 8–9.5vw
      "strip":   "city",                        // a name pointing into strips
      "sides":   ["balloon"]                    // extra side-field pieces
    }
  }
}}
```
A vehicles/mascots/strips entry whose asset cannot be found generates no CSS class at
all, and a day referencing it simply skips that piece (the day itself still
renders in full); an unknown palette name falls back to the
day-number rhythm; an unknown side kind is drawn as a spark.

**Kit (theme-owned, not in art)**: what stays in the renderer:
- The MOODS sky-mood table (12 moods: night/neon/lilac/floodlight/dusk/rainbow/alpine/goldfog/canyon/ocean/lava/sunrise/homebound, each with 4 gradient stops + a pastel wash table; stops pre-checked for AA) + the chained-seam mechanism resolve_chain() (chapter i+1's opening colour = chapter i's closing colour) + the HERO_MOOD/APPX_MOOD defaults + DEFAULT_RHYTHM (no art → moods cycle by day number) + contrast_report() to re-check the actual chain at build time.
- The chapter-index convention (0 = hero, 1..N = days, N+1 = appendix) and every seeded RNG (deco washes / light bands / soft-focus / confetti; sides side-field; hill ridges) — seeds are frozen constants, content is rolled by index.
- The side-field pool cloud×2/spark/dot/shard/heart/star + the generic cut-outs splash-cloud-a..d/splash-star/splash-balloon (theme-library embeds) + the newer {"stem","w"} img pieces.
- Head effects head_fx(): halo-cyan/gold/teal, burst, beams-cool, rainbow(sm), sun, plus the three CSS medallions moon/dusk/sunrise (MEDALLIONS — rotated by day index when a day has no island and no fx).
- The **mechanics** of vehicles/mascots/strips: the .veh/.mas/.strip base classes, drift animation, speedlines contrails, the STRIP_A opacity cap, kit_css() generating the .veh-<kind>/.mas-<kind>/.strip-<kind> classes from the registries (mascot selector alignment padding identical to the original hand-written block).
- The ribbon road + the 3.5/96.5 gutter, big numerals, colour bands, export badges, the TITLE_TXT_CSS text-title fallback (injected only when there is no title plate).
- Neutral copy: the <title> suffix 「闪屏版行程」, the h1 fallback 「出发!」, the appendix/endcap graphics.


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
   `IMAGE-LIBRARY.md` §Generic pieces (通用件): a plane, a bus, a cloud, luggage, a wing shot, a
   generic beach. Generate the rest with the sheet recipe; `gen.py --manifest
   <trip>/manifest.<trip>.json` registers it in the trip's own manifest (never
   `themes/assets/manifest.json` — see Test-trip asset recycling (测试行程资产回收)
   below). Title stickers: one
   centred sticker, both lines the same height, no icons/moons inside the letters,
   wide white margin (see china-clay-title2; Turkey tester's tip — simple glyphs, ≤8
   strokes, keep the strokes intact —「九万里风」("ninety-thousand-mile wind") came out
   clean first time).
2b. **No generation capability → stock mode (the built-in asset library), never a fall
   back to a text-only page.** Phase 0's picture-capability check writes its result
   into the plan's `prefs.pictures`: `native` (the agent generates images itself) /
   `key` (`themes/.auth_header` exists — judged with `test -s` only, never read or
   printed) / `stock` (neither). Under `stock`, the built-in asset pack fills in the
   pictures and the page still ships as a themed render:
   ```bash
   python3 <skill>/themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
   # also --theme clay · --lang zh|en · --index PATH (swap in a different stock index)
   ```
   The script picks by trip country + each day's stop keywords, from
   `themes/assets/stock/` (index `stock/index.json`, inventory in `stock/README.md`)
   plus same-country pictures and generic pieces (`IMAGE-LIBRARY.md` §Generic pieces (通用件)) in the
   shared library, and **fills picture slots only**: the cover painting, each day's
   hero / cut-outs, props. **The words are still yours to write** — cover title
   (`references/cover-titles.md`), each day's `theme` (4 chars) / `en` / `mark`,
   captions, annotations, the closing line; shipping with the script's placeholder
   words is a defect, judged exactly like step 3 below. The script writes a
   stock-library notice into `end.fine` — **do not delete it** — and repeat it in the
   chat summary (「图片来自内置素材库(本次未接入生图能力);接入生图模型或 KEY 后可为本次
   行程定制生成。」 — "pictures come from the built-in stock library, no image
   generation was connected this run; hook up an image model or KEY and they can be
   custom-generated for this trip"), and never ask for a KEY in the conversation.
   Coverage: **illustrated** is complete; **clay** is usable (terrain bands fall to the
   built-in neutral SVG kit `ridge|plain|coast|forest|lake|desert` + generic clay
   props); the other six — noir / glass / journal / zine / splash / portal — still
   need their plates, photos, islands and video generated: when the user names one of
   them, explain the situation and steer to illustrated instead — a forced render only
   yields a page of empty picture slots (portal has no stock material at all).
3. Write the words: captions, annotations, doodle notes, the closing line. Voice
   rules live in each theme's renderer docstring.
4. Render, run `qc.py`, eyeball an export.

**Generator choice (生成器选择) — read this first**: if the current AI / agent **has
image (or video) generation of its own** (a built-in image / video tool, native
generation it can call directly), **use that ability first — no KEY needs
configuring**. `gen.py` / `genvideo.py` + OpenRouter are only the spare tyre for
environments with no native generation. Generating natively, the four downstream steps
— sheet-split / cutout / webp / manifest — are **every one still required**, against
the same artefact contract:
- **Specs unchanged**: full-bleed pieces 16:9 (1536×864 or 2K); sheet pieces prompted
  as "N pieces in a C×R grid · pure white background · wide white gutters · no borders,
  no text" (copy the `*-sheet-*` skeleton in the manifest) or `split_sheet.py` will not
  recognise the grid; cut-out pieces = one single subject on a pure-white/solid
  background, or `cutout.py` cannot cut clean; title-sticker rules as in the previous
  section.
- **Prompts copy this library's style anchors**: a same-theme entry's prompt + the
  `style_anchor` at the top of `manifest.json`, so new pieces stay in the same style
  family as the existing assets (clay looks like clay, riso like riso) — no improvised
  style switches.
- **Landing paths and naming unchanged**: `<trip>/<trip>-<name>.png`, then run
  split_sheet / cutout / towebp per steps ①②③④ below.
- **Still record into `<trip>/manifest.<trip>.json`**: `model` = the generator you
  actually used, `cost_usd` = 0 or the real number, `prompt` kept in full — recycling
  into the library and "reuse what already exists" both depend on it.
- **Video (portal)** likewise: artefact contract in the portal block — mp4 h264 16:9
  (1344×768 or 1280×720) 24 fps, dives 5–6 s / links 4 s, links need **first+last-frame
  conditioning**; if native video cannot condition on first/last frames, produce dives
  only, leave links out and note it in art.json — the page falls back to single-slot
  playback.
Only when the current environment has **no** native generation do you take `gen.py` /
`genvideo.py` (needs `themes/.auth_header` — one line, an OpenRouter key) — the
commands below are all this spare-tyre path.

**Image toolchain (图片工具链)** (all of it lives in themes/ — nothing to copy; the key
is read only inside themes/; the shared library is themes/assets/). **Write every
command with full paths** — the agent's shell cwd resets on every call and `cd` does
not persist; below, `<skill>` = the skill root, `<trip>` = the trip directory (e.g.
`trips/kyoto-2027`), and all four steps start from `<skill>`:

```bash
# ① generate (--dry-run first to inspect the payload; PNGs and manifest land in <trip>, themes/assets/manifest.json untouched)
python3 <skill>/themes/gen.py <trip>/jobs.json --outdir <trip> --manifest <trip>/manifest.<trip>.json
# ② split the sheet: --probe first to see how many cells it recognises, then type piece names in the prompt's Row 1 / Row 2 order (reading order)
python3 <skill>/themes/split_sheet.py <trip>/x-sheet.png --probe
python3 <skill>/themes/split_sheet.py <trip>/x-sheet.png --grid 3x2 name1 name2 … name6 --outdir <trip>
# ③ single-piece cutout (the cut-out slots: stickers/islands/figurines/terrain bands/stamps/props)
python3 <skill>/themes/cutout.py <trip>/x.png --outdir <trip>            # → x.cut.png + x.cut.webp
# ④ webp + size variants: feed opaque large pictures the png directly; feed cut-outs the .cut.png (the stem stays x, never becomes x.cut.cut)
python3 <skill>/themes/towebp.py <trip>/x.png --outdir <trip>                       # opaque → x.webp
python3 <skill>/themes/towebp.py <trip>/x.cut.png --sizes sm,md,lg --outdir <trip>  # cut-out → x.sm/md/lg.webp
```
`split_sheet.py` / `cutout.py` / `towebp.py` all default `--outdir` to **the input
file's own directory** (`towebp.py` always did; the other two since 2026-08-16 — they
used to write to cwd), so given `<trip>/x.png` there is no need to write `--outdir` —
it is spelled out above so the landing spot stays visible.

- **Sheet recipe** (one $0.04 sheet cuts into 6–12 pieces, zero rework): copy the
  `journal-sheet-photo-a` prompt skeleton in `manifest.json` — "SIX separate … 3-column
  by 2-row grid on a plain pure white background, WIDE empty white gutters between
  every photo and a wide white margin around the grid, each … a simple borderless
  rectangle, no borders, no text" — then write each cell's content in Row 1/Row 2
  order; parameters `background:opaque, aspect_ratio:3:2, resolution:2K,
  quality:medium`. **Cutting order: `--probe` first to confirm the cell count matches
  the prompt's, then type piece names in Row 1 → Row 2 order** — once names and prompt
  rows misalign, every piece on the sheet is misnamed and downstream raises zero errors
  (Mexico P3). `--probe` finding fewer cells than the prompt has (splash stars drifting
  into a gutter merged two columns into one) → add `--grid 3x2` to hard-cut by
  columns×rows. Products `<name>.png/.cut.png/.cut.webp`. **Sheet-cut pieces usually
  get only the sm + cut variants**: cells run about 300–560 px, `towebp --sizes
  sm,md,lg` skips md/lg (dropped when not smaller than the source, or when the bytes
  actually grow), and illustrated's md/lg slots fall back to `.cut.webp` — normal.
- Which slots are cut-outs and which opaque: the "shape" column of the size table
  above; cut-outs go **first** `cutout.py` **then** `towebp.py x.cut.png` — `towebp
  x.png --sizes md` straight on the PNG yields a white square with zero errors
  (Vietnam F7).
- `gen.py --outdir <trip>` leaves `.png` masters and `.payload.json` drafts in the trip
  directory — they are **not deliverables** (renderers eat only webp). Ship webp only;
  png masters may be deleted, or kept in the trip directory but out of the repo and
  never registered as library assets (one Vietnam run: 62 pngs at 59 MB, real
  deliverables 12 MB).
- Assets can simply live in the trip directory (renderers search the plan's directory →
  `--assets DIR` → themes/assets/); webp names follow the `data_uri` fallback chain —
  never hand-edit the suffixes.

**Test-trip asset recycling (测试行程资产回收)** (settled 2026-08-16):
`<trip>/manifest.<trip>.json` is the **authoritative record** of what the run generated
(prompts, parameters, costs, sheet-cut piece names); written into the trip directory,
registration is complete. **Testers and ordinary users never write `themes/assets/` or
`IMAGE-LIBRARY.md`** — recycling common assets into the shared library and appending
new index chapters is done in one pass by the main agent after a batch of tests
(`build_manifest.py` refreshes the manifest + a hand-written index section).
IMAGE-LIBRARY's 「新测试行程跑完照此追加」 ("append like this after each new test trip")
refers to that main-agent step, not a tester task.

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
