# IMAGE-LIBRARY — themes/assets/ reusable picture-library index (incl. the eleven test trips' assets (测试行程资产), §13-21 & §23-24)

Actual scan 2026-08-29: **355 stems = 515 webp, 30MB** (**pages use only these**; png
masters stay out of the repo — the pngs kept for re-cutting live in their trips/
directories). Cumulative generation cost **≈$7.33** (manifest sum; portal video billed
separately); look up any item's prompt/params/unit price in `manifest.json` (**201
entries**; sheet-cut sub-pieces are not listed individually — check the parent
`*-sheet-*` entry). **Generic pieces (§12): check this table + manifest first and reuse
what exists; covers / key art / terrain bands = destination scenes and MUST be generated
fresh for the trip at hand (SKILL.md Phase 6); when generating, an agent with native
image generation uses it directly (no KEY), otherwise gen.py/OpenRouter (ART-SCHEMA
"Generator choice (生成器选择)"); any generation that costs money needs the owner's
approval.**
There is also a **stock generic asset pack** (`stock/`, 80 stems / 161 webp / $0.9284,
with its own index and manifest) — the fallback library for **when there is no
image-generation ability**, see §22; it is not a substitute for the "generic pieces":
with generation ability, destination art is still generated fresh per trip.

**How test-trip assets are folded into this library (测试行程资产回收) — decided
2026-08-16; stop writing into themes/ directly the way the pre-§13 sections did**
- Testers / ordinary users **write only their own trip directory**:
  `trips/<trip>/manifest.<trip>.json` is the **authoritative record** for that trip's
  assets (prompt/params/unit price/file sizes all live there); both png and webp stay in
  that directory, and `themes/` is strictly read-only — `themes/*.py`, `ART-SCHEMA.md`,
  and this table must not be touched.
- **The main agent folds a batch in after its test runs finish**: copy the webp (incl.
  `.sm/.md/.lg/.cut/.band/.strip` variants) into `themes/assets/`, hand-merge the trip
  manifest entries into `manifest.json` under this library's schema (add `source_job` /
  `trip` / `note`; `files` lists only the webp actually copied in), append a section to
  this table, and sync that section's generic pieces into §12.
- ⚠️ **Do not run `build_manifest.py` during the fold-in** — it scans `themes/assets` by
  job file and would scramble the trip directory's job↔png relationships; **merge by
  hand**, then verify with `python3 -c`: JSON parses + entry count + `cost_usd` sum.

## Usage notes
- Embedding goes only through `theme_common.data_uri(stem, size=None)`: an explicit size
  fetches `<stem>.<size>.webp` (sm/md/lg/band/strip); with no size it falls back along
  **md.webp → cut.webp → .webp**. Output is a base64 data-URI — the page opens on a
  file:// double-click, zero fetches / external links.
- Variant choice = the smallest tier that covers the displayed size: sm (height ≈128,
  thumbnails/badges) < md (≈300–480, cards/nodes) < lg (≈640) < cut.webp (full-size
  cutout, large subjects) < full-frame .webp (1536×864 backgrounds). Referencing the same
  image in several places doubles the base64 each time (illustrated and glass both got
  burned by this).
- The `cut` family = real alpha cutouts from cutout.py (every cut.webp PIL-verified
  RGBA); their sm/md/lg scales stay transparent; full-frame .webp
  (hero/glass-*/noir-*/zine-* etc.) are opaque RGB.
- The "variants" column below lists **only the embeddable webp tiers** (number = KB);
  each stem's .png / .cut.png masters sit on disk by default and never go into a page.
  Decorative elements (stamps, tape texture, stains, rainbows, grain) are hand-written
  CSS/SVG first — don't pad them out with images.
- The "used by" column = live renderers (theme2 illustrated (插画) / clay2 clay (黏土) /
  noir2 noir (夜航) / glass2 glass (玻璃) / journal (手账) / zine / splash (闪屏));
  `v1` = referenced only by retired renderers, nothing live claims it, reuse freely.
  chart/board/picker use zero images.
- **Cover / key art / title sticker / terrain band / plate / island = destination
  scenes — always generate them for the trip at hand in the theme's style**: prefer the
  destination's own sights (Xi'an city wall / Great Wall) > national landmarks > neutral
  scenes; never leave one empty and never borrow another country's band (owner,
  2026-08-15: a China page opening on a New York-skyline band = a defect); "reuse first"
  applies only to §12's generic props. Terrain-band recipe = the same prompt template as
  the US `strip-*` (see manifest china-strip-xian / -beijing).
- **Region-bound pieces (Statue of Liberty / Golden Gate / Yellowstone / Yosemite /
  Diamond Head / volcanoes / Salt Lake temple / Tiananmen…) must never be reused across
  trips** — other trips may use only the stems listed in §12 "Generic pieces (通用件)";
  everything else is generated fresh (sheet recipe: ART-SCHEMA.md "Image toolchain
  (图片工具链)").
- **There is exactly one "generic" table: §12.** Any stem whose region column a §13-21 /
  §23-24 per-trip table marks **generic** **must also appear in §12's table** (source
  section noted); marked generic in a section but absent from §12 = a defect, and reusers
  **treat it as unlisted** (i.e. as region-bound — don't use it). Stems marked
  "**depends on the trip**" belong to the "decide per trip" list at the end of §12 and
  are not generic pieces; the "(generic-ish)" markers in §13/§14 are likewise handled as
  "decide per trip", never as generic.
- Variant generation: `towebp.py in.png --sizes sm,md,lg` produces `.webp` / `.cut.webp`
  (depending on alpha) at **longest-edge** tiers sm 128 / md 480 / lg 640; `band`/`strip`
  are hand-made shapes, not size tiers. ⚠️ Library entries from before 2026-08-15 were
  hand-scaled by **height** ≈128/300-320/640 (hence "height ≈128 / ≈300–480" in the
  bullet above); data_uri serves both conventions fine — pick tiers purely by "smallest
  that covers the displayed size".

## 1 Generic illustration set (gouache style) — 13
v1 (build_page/render_theme) also references this set; that does not affect reuse.

| Stem | Variants (KB) | Alpha | Used by | Reuse notes |
|---|---|---|---|---|
| liberty | cut61 md11 sm3 lg22 | ✓ | theme2 | Statue of Liberty — NYC day badge/card |
| golden-gate | cut110 md32 sm10 lg58 | ✓ | theme2,zine | Golden Gate Bridge, San Francisco days |
| diamond-head | cut148 md46 sm11 lg66 | ✓ | theme2,zine | Diamond Head, Honolulu days |
| kilauea | cut144 md19 sm5 lg35 | ✓ | theme2,zine | Kilauea volcano, Big Island days |
| prismatic | cut149 md27 sm7 lg49 | ✓ | theme2,zine | Grand Prismatic Spring, Yellowstone days |
| stadium | cut184 md31 sm7 lg59 | ✓ | theme2 | baseball stadium, used on the soccer-night (绿茵之夜) day |
| teton | cut177 md30 sm7 lg55 | ✓ | theme2 | Grand Teton peaks |
| yosemite | cut183 md27 sm6 lg47 | ✓ | theme2,zine | Yosemite Half Dome |
| tiananmen | cut114 md32 sm8 | ✓ | theme2,zine | Tiananmen — reserved for the return-leg Beijing end cap |
| bus | cut144 md24 sm7 lg43 | ✓ | theme2,zine | retro tour bus, any coach day |
| plane | cut79 md30 sm9 lg35 | ✓ | theme2,zine | airliner side profile, generic for flight days |
| hero | webp248 | ✗ | theme2 fallback + v1 | 16:9 full-frame cover (only when cover-hero is missing) |
| cover-hero | webp101 | ✗ | theme2 | the illustrated theme's current cover art |

## 2 Clay set — 27
| Stem | Variants (KB) | Alpha | Used by | Reuse notes |
|---|---|---|---|---|
| clay-liberty | cut58 md18 sm5 | ✓ | clay,clay2 | clay-landmark 10-piece set: sits beside milestone stones |
| clay-goldengate | cut87 md27 sm8 | ✓ | clay,clay2 | same set as clay-liberty above |
| clay-diamondhead | cut101 md35 sm9 | ✓ | clay,clay2 | same set as clay-liberty above |
| clay-prismatic | cut87 md23 sm6 | ✓ | clay,clay2 | same set as clay-liberty above |
| clay-stadium | cut69 md24 sm7 | ✓ | clay,clay2 | same set as clay-liberty above |
| clay-yosemite | cut87 md19 sm5 | ✓ | clay,clay2 | same set as clay-liberty above |
| clay-teton | cut31 md27 sm7 | ✓ | clay2 | same set as clay-liberty above |
| clay-saltlake | cut22 md17 sm7 | ✓ | clay2 | Salt Lake City Mormon temple |
| clay-volcano | cut29 md20 sm5 | ✓ | clay2 | smoking volcano |
| clay-island | cut37 md34 sm10 | ✓ | clay2 | small Hawaiian island + coconut palms |
| clay-plane | cut19 md16 sm8 | ✓ | clay2 | clay toy plane, flight days |
| clay-bus-solo | cut57 md21 | ✓ | clay2 | clay tour bus (the one glued onto the road) |
| clay-luggage | cut19 md16 sm6 | ✓ | none | suitcase — **unclaimed**, usable as closing/packing-slot decoration |
| clay-balloon | cut14 | ✓ | clay2 | hot-air balloon, sky decoration |
| clay-cactus | cut16 | ✓ | clay2 | cactus (desert leg) |
| clay-palm | cut18 | ✓ | clay2 | palm tree (island leg) |
| clay-pines | cut22 | ✓ | clay2 | pine cluster (mountain leg) |
| clay-signpost | cut15 | ✓ | clay2 | signpost |
| clay-cloud-a/b/c | cut11/6/4 | ✓ | clay2 | three clouds, page-edge sky decoration |
| strip-desert | band77 cut105 | ✓ | clay2 | terrain band: desert (1400×380, negative-margin interlock) |
| strip-geyser | band86 cut123 | ✓ | clay2 | terrain band: geysers |
| strip-mountains | band62 cut90 | ✓ | clay2 | terrain band: snow peaks |
| strip-ocean | band76 cut99 | ✓ | clay2 | terrain band: coastline |
| clay-title | cut132 md83 | ✓ | clay2 | clay 3D title lettering 「美国行」 ("US Trip") |
| clay-hero | webp85 | ✗ | v1 only | v1 full-frame cover, retired; still useful as a style anchor |

## 3 Glass set (16:9 full-frame stills, used as the fixed background layer) — 6
| Stem | Variants (KB) | Alpha | Used by | Reuse notes |
|---|---|---|---|---|
| glass-hero | webp135 strip22 | ✗ | glass2 | cover still; the .strip narrow band (800×300) is v1-only |
| glass-city | webp150 strip23 | ✗ | glass2 | city-leg background (NYC) |
| glass-park | webp152 strip29 | ✗ | glass2 | national-park-leg background |
| glass-island | webp154 strip29 | ✗ | glass2 | island-leg background |
| glass-west | webp131 | ✗ | glass2 | west-leg background |
| glass-dawn | webp33 | ✗ | glass2 | dawn-finale-leg background |

## 4 Noir set (16:9 night paintings, the plate layer) — 7
| Stem | Variants (KB) | Alpha | Used by | Reuse notes |
|---|---|---|---|---|
| noir-hero | webp59 | ✗ | noir2 | prologue plate |
| noir-nyc | webp93 | ✗ | noir2 | New York at night |
| noir-stadium | webp68 | ✗ | noir2 | stadium at night (zine switched to zine-stadium + journal-ph-soccer; the baseball asset is out of the soccer day) |
| noir-yellowstone | webp64 | ✗ | noir2 | Yellowstone springs at night |
| noir-yosemite | webp52 | ✗ | noir2 | Yosemite starry night |
| noir-volcano | webp47 | ✗ | noir2 | volcanic lava at night |
| noir-sunrise | webp50 | ✗ | noir2 | sunrise finale (the warm-toned exit) |

## 5 Zine set (riso poster art) — 4
| Stem | Variants (KB) | Alpha | Used by | Reuse notes |
|---|---|---|---|---|
| zine-nyc | webp324 | ✗ | zine | portrait 1024×1536 chapter-head poster |
| zine-geyser | webp179 | ✗ | zine | chapter-head poster, Yellowstone |
| zine-elcap | webp158 | ✗ | zine | chapter-head poster, Yosemite |
| zine-hawaii | webp301 | ✗ | zine | chapter-head poster, Hawaii |

## 6 Journal set — 25
| Stem | Variants (KB) | Alpha | Used by | Reuse notes |
|---|---|---|---|---|
| journal-ph-* (12 polaroids) | cut:beach58 diamondhead50 geyser40 goldengate28 lava28 liberty38 nyc36 saltlake42 stadium36 (⚠️ baseball, no live user, reuse freely) teton35 wing33 yosemite68 | ✓ | journal,zine | white-frame polaroid photos, pair with CSS tape corner tabs |
| journal-boarding | cut24 | ✓ | journal,zine | boarding-pass prop |
| journal-ticket | cut21 | ✓ | journal,zine | retro admission-ticket stub |
| journal-tag | cut21 | ✓ | journal,zine | luggage tag |
| journal-seal | cut21 | ✓ | journal | wax seal |
| journal-stamp-bison/goldengate/liberty | cut36/33/35 | ✓ | journal | three postage stamps (postmarks are drawn in CSS) |
| journal-tape-a/b/c/d | cut17/16/17/13 | ✓ | journal | four washi-tape strips |
| journal-flower-a/b | cut12/10 | ✓ | journal | two pressed flowers, page-corner decoration |

## 7 Splash set (Brawl Stars thick-paint style) — 10
| Stem | Variants (KB) | Alpha | Used by | Reuse notes |
|---|---|---|---|---|
| splash-title | cut134 md76 | ✓ | splash | thick-paint title art (use md) |
| splash-hero | cut292 md156 | ✓ | splash | key-art character group shot (use md; the cut is heavy, handle with care) |
| splash-geyser | cut130 md108 sm60 | ✓ | splash | geyser hero image |
| splash-volcano | cut101 md83 sm40 | ✓ | splash | volcano hero image |
| splash-{baseball,cliff,ggate,surf,taxi,teton} | cut39–48 sm31–40 | ✓ | splash | six floating-island node pieces (use sm), chapter heads on the ribbon road |

## 8 Portal video plates (i2v seed frames, **never embedded in pages**) — 13
portal-nyc / portal-yellowstone (old 1:1) + portal-{nyc,stadium,saltlake,yellowstone,teton,goldengate,yosemite,waikiki,volcano,diamondhead}-w + portal-nyc-w2 (16:9 wide, 1.5–2.0MB png each).
Consumed only by `build_portal_jobs.py` as video-generation input; pages embed portal's companion mp4 files. The US reference chain (19 clips, ~35MB) is a release asset and is not in the repo tree — `portal/` is empty in a fresh clone; restore commands in [`portal/README.md`](portal/README.md); the portal showcase that ships with the repo is Morocco. Details in the portal-theme memory.

## 9 Wishlist additions (2026-08-13, owner's "全补上" ("add them all"); the used-by column is updated by whoever wires them in)

| Stem | Variants (KB) | Alpha | Used by | Reuse notes |
|---|---|---|---|---|
| zine-goldengate / -teton / -volcano / -stadium | webp142/183/66/195 (1024×1536) | ✗ | zine | 4 zine portrait film shots filling in Golden Gate / Teton / volcano / soccer night, same family as zine-nyc (chapter art for D7/D6/D10/D3) |
| journal-ph-soccer/slctemple/sequoia/tunnelview/canyonfalls/elkarch | cut38-70 | ✓ | journal,zine | 6 Kodak-70s photos: soccer night (replaces baseball) / Salt Lake temple / giant sequoia / Tunnel View / Yellowstone Grand Canyon falls / elk-antler arch (D3/D4/D8/D8/D6/D6) |
| journal-flora-daisy/fern/maple | cut19/36/24 | ✓ | journal | three pressed flowers: daisy / fern / maple leaf; scattered from the same seed pool as flower-a/b |
| journal-washi-floral/ticking/gingham | cut32/30/33 | ✓ | journal | three fabric-texture tapes: floral / ticking stripe / gingham; join tape()'s seven-pattern rotation |
| journal-poster-yosemite | webp298 md77 | ✗ | journal | WPA-style vintage national-park poster (pinned up on D8; the blank band takes a line of Caveat) |
| journal-postcard-hula | webp345 md73 | ✗ | journal | 1950s linen-texture hula postcard (D11 finale, pairs with stamp + postmark) |
| splash-strip-city / splash-strip-goldengate | cut56/63 (1433/1431-wide bands) | ✓ | splash | splash silhouette bands: purple-night city skyline / Golden Gate sunset, ends fade out on their own |
| splash-plane / splash-bus | cut24/33 | ✓ | splash | splash-style plane (d4/d9 flight days) / roof-rack tour bus |
| splash-cloud-a/b/c/d + splash-star | cut14/7/4/2/5 | ✓ | splash | four clouds + a four-point star sparkle in the splash style; already replaced the clay clouds |
| splash-baseball/cliff/ggate/surf/taxi/teton | cut40/48/39/42/41/48 | ✓ | splash | first batch of splash floating-island node cuts (ballpark / cliff / Golden Gate / surf / taxi / Teton), partially superseded by the nodes2 second batch — the baseball piece was retired once the event turned out to be soccer; the rest are still on the page |
| caveat-vf.woff2 | 74KB (woff2, variable weight 400-700) | font | journal | English handwriting face Caveat (OFL open source), embedded base64 via @font-face, heads the --curs stack |

## 10a Draft art mock-* (**style drafts — never embed in pages**) — 19
mock-{bento,bento2,bento3,candy,candy2,cover,day,flow,game2,journal,odyssey,splash,splash2,splash3,splash4,zelda,zine} + clay-mock-{flow,world}.
All png (1.5–3.5MB): layout comps / AI drafts painted for the owner to pick a direction — **not assets**: no variants, no cutouts, and no render_*.py may reference them; skim them as style references before starting a new theme, nothing more.

## 11 Sheet masters and intermediates (**never embed**) — 9
clay-sheet-{deco,props} / journal-sheet-{photo-a,photo-b,props} / splash-sheet-nodes (grid-cut sheet masters — their sub-pieces are already in the tables above) + contact-sheet / contact-sheet2 / world-check (early contact sheets / QA check images). All png, used only when re-cutting (split_sheet.py).

## 10b Splash-only pieces, second batch (2026-08-14, sheet×2 ≈$0.09, style=Brawl Stars splash)
| Stem | Variants (KB) | Alpha | Used by | Reuse notes |
|---|---|---|---|---|
| splash-nightflight | cut29 sm26 | ✓ | splash | night plane resting on a nebula island, D1 chapter head |
| splash-temple | cut31 sm29 | ✓ | splash | Salt Lake temple on a salt-mirror island, D4 chapter head |
| splash-soccer | cut36 sm33 | ✓ | splash | soccer ball + floodlight island, D3 chapter head (replaces baseball) |
| splash-sunrise | cut47 sm44 | ✓ | splash | Diamond Head sunrise island, D11 finale chapter head |
| splash-sequoia | cut48 sm44 | ✓ | splash | sequoia tunnel, D8 companion island (veh-sequoia) |
| splash-balloon | cut31 sm28 | ✓ | splash | striped hot-air balloon + cloud seat, sc-bal (replaces clay-balloon) |
| splash-m-* (6 mascots) | cut26-35 sm26-33 | ✓ | splash | hotdog/whistle/bison/moose/cablecar/ukulele — MASCOT pieces pinned to scene edges |

## 12 Generic pieces (通用件) — reusable by any trip, zero region binding; eyeballed piece by piece 2026-08-15, third batch added 2026-08-16
"Region-bound" = the frame contains a recognizable place (a landmark, a distinctive
landform, a city-specific object). The pieces below contain none — writing them into any
art.json will never "paste someone else's trip onto your page"; every other stem
(especially `*-liberty / -goldengate / -yellowstone / -yosemite / -diamondhead /
-volcano / -kilauea / -prismatic / -teton / -saltlake / -stadium / -tiananmen / zine-* /
noir-* / glass-*` and the eleven test trips' `au-* / nordic-* / japan-* / china-* /
italy-* / mexico-* / morocco-* / turkey-* / vietnam-* / yn-* / peru-*`) is region-bound
by default.
**This table is the sole authority on "generic"**: every stem marked generic in the
§13-21 / §23-24 sections appears here; marked there but missing here = treat as
region-bound (see
the rule at the top).

| Stem | Variants (KB) | Use | Theme |
|---|---|---|---|
| journal-ph-wing | cut33 | wing-through-window polaroid — the `photo`/`photos2` for outbound/return days | journal |
| journal-ph-beach | cut58 | palm-grove beach polaroid (generic tropical beach; skip on Nordic/inland trips) | journal |
| nordic-journal-flora-fern | cut45 | fern pressed flower (props flora stem) | journal |
| nordic-journal-flora-heather | cut37 | heather pressed flower (props flora stem) | journal |
| journal-boarding | cut24 | blank boarding-pass prop (`props kind:img`) | journal |
| journal-ticket | cut21 | ADMIT ONE retro ticket stub | journal |
| journal-tag | cut21 | kraft-paper luggage tag | journal |
| journal-seal | cut21 | compass wax seal (the one the `seal` kit uses) | journal |
| journal-tape-a/b/c/d | cut17/16/17/13 | washi tapes (rotated by the theme's `tape()`; art need not name them) | journal |
| journal-washi-floral/ticking/gingham | cut32/30/33 | fabric-texture tapes (same) | journal |
| journal-flower-a/b · journal-flora-daisy/fern/maple | cut12/10 · 19/36/24 | pressed flowers (`flora` kit pool) | journal |
| plane | cut79 md30 sm9 lg35 | gouache airliner side profile, flight days | illustrated (插画) / zine |
| bus | cut144 md24 sm7 lg43 | gouache retro tour bus, any coach day | illustrated (插画) / zine |
| clay-plane · clay-bus-solo | cut19 md16 sm8 · cut57 md21 | clay toy plane / tour bus | clay |
| clay-luggage | cut19 md16 sm6 | suitcase + camera, closing/packing slot | clay |
| clay-balloon · clay-cloud-a/b/c · clay-signpost | cut14 · 11/6/4 · 15 | sky / page-edge decoration, signpost | clay |
| clay-cactus · clay-palm · clay-pines | cut16/18/22 | terrain vegetation (desert/island/mountain) — pick by the trip's terrain | clay |
| splash-plane · splash-bus · splash-nightflight | cut24/33 · cut29 sm26 | thick-paint plane / tour bus / night plane on a nebula | splash |
| splash-cloud-a/b/c/d · splash-star · splash-balloon | cut14/7/4/2 · 5 · 31 sm28 | clouds, star sparkle, hot-air balloon | splash |
| splash-surf · splash-cliff | cut42 sm40 · cut48 sm44 | surfboard-and-wave island / waterfall-cliff island (no landmark) | splash |
| splash-m-whistle | cut29 sm27 | whistle mascot (referees / match days) | splash |
| caveat-vf.woff2 | 74 | English handwriting font | journal |
| **↓ Added 2026-08-16: marked generic in their sections but missing from this table (rule-conflict fix)** | | | |
| japan-train | cut27 sm4 | white-and-blue Shinkansen nose at three-quarter view, no landmark — any high-speed/intercity rail day | illustrated (插画) / zine (from §15) |
| china-clay-train | cut21 | clay high-speed-rail head car (white body, red stripe) + a short piece of grey track | clay (from §16) |
| china-splash-train | cut42 sm7 | thick-paint high-speed-rail head-car sticker (round headlight eyes), transport slots | splash (from §16) |
| china-splash-veh-train | cut27 | thick-paint high-speed train in motion on a floating island, `vehicle` slot | splash (from §16) |
| **↓ Added 2026-08-16, third test-trip batch (§18-21, each opened and eyeballed)** | | | |
| mexico-journal-ticket-ado | cut35 | long-haul bus ticket stub: bus line drawing + serial 48167, **zero text and zero landmarks in the frame** (the name carries ADO but the image doesn't) — any long-haul/intercity bus day | journal (from §18) |
| morocco-glass-dawn | webp53 | seaside dawn 16:9 plate: calm sea + beach arc + a distant row of low white houses in silhouette, peach-pink sky, no landmark — **§12's first 16:9 photographic plate**; the glass/noir themes can use it for the finale leg directly | glass (from §19) |
| turkey-balloon | cut27 sm8 | four striped hot-air balloons lifting off (gouache), no landmark — sky decoration / balloon days | illustrated (插画) / zine (from §20) |
| vietnam-splash-i-train | cut32 sm7 | green sleeper-carriage floating island + crescent moon, no landmark — night-train-day chapter head | splash (from §21) |
| vietnam-ph-train | webp23 | coastal morning light outside a sleeper-car window (berth + window frame), no landmark; **the coastline reads tropical/subtropical** — skip on inland or Nordic trips | zine / journal (from §21) |
| **↓ Added 2026-08-29, Yunnan/Peru batch (§23-24, each opened and eyeballed)** | | | |
| peru-clay-train | cut26 | blue-and-cream clay tourist-train carriage with big round windows, no landmark and no livery text — any scenic/tourist rail day | clay (from §24) |
| peru-zine-trainwindow | cut62 | b/w view out a moving train window down a rocky river gorge, blurred foliage, no landmark; **the scenery reads steep green mountain gorge** — skip on flat/desert routes | zine / journal (from §24) |

**Decide per trip (regional flavor, but not a landmark)**: `splash-taxi` (yellow cab =
New York), `splash-m-hotdog` (NYC hot-dog cart), `splash-m-cablecar` (San Francisco
cable car), `splash-m-ukulele` (Hawaii), `splash-m-bison/-moose` (North American
animals), `strip-desert` (Southwest desert arches + cacti), `strip-ocean` (volcanic
island), `strip-mountains/-geyser`; **added 2026-08-16**: `china-clay-food` /
`china-splash-m-dumpling` (bamboo steamer + baozi = Chinese cuisine; §16 originally
mislabeled them generic), `au-noir-hero`/`au-noir-dawn` (southern-sky Milky Way / dawn
return flight — Southern-Hemisphere or island trips may borrow), `nordic-noir-aurora`
(aurora — Arctic-Circle trips may borrow); **added 2026-08-29**: `peru-clay-ceviche`
(ceviche plate = Peruvian/coastal Latin cuisine), `peru-noir-hero` (night flight over
dark mountain ridges, no landmark but prompted over the Andes — mountain-country trips
may borrow) — reuse only when the trip actually visits the
matching place / cuisine.

## 13 Australia 2026 test-trip assets (测试行程资产) (2026-08-15, generated by the Opus tester, $0.31; sheet masters au-journal-sheet-photo / -props in manifest) — 19
Region-bound pieces reuse only on Australia trips; `au-noir-hero` (airliner + southern
Milky Way) and `au-noir-dawn` (dawn return flight) lean generic — Southern-Hemisphere /
island trips may borrow them.

| Stem | Variants (KB) | Content | Region | Use |
|---|---|---|---|---|
| au-journal-ph-opera | cut54 | Sydney Opera House + Harbour Bridge at dusk, polaroid | 🇦🇺 Sydney | journal photo |
| au-journal-ph-bondi | cut64 | Bondi Beach polaroid | 🇦🇺 Sydney | journal photo |
| au-journal-ph-bluemtn | cut60 | Blue Mountains Three Sisters polaroid | 🇦🇺 Blue Mountains | journal photo |
| au-journal-ph-reef | cut88 | Great Barrier Reef snorkeling/coral polaroid | 🇦🇺 Cairns | journal photo |
| au-journal-ph-daintree | cut78 | Daintree rainforest boardwalk-to-sea polaroid | 🇦🇺 Cairns | journal photo |
| au-journal-ph-cairns | cut68 | Cairns lagoon/esplanade polaroid | 🇦🇺 Cairns | journal photo |
| au-journal-stamp-opera | cut87 | Opera House stamp (portrait) | 🇦🇺 | journal stamp st-a/st-b |
| au-journal-stamp-kangaroo | cut80 | kangaroo stamp (portrait) | 🇦🇺 | journal stamp st-a/st-b |
| au-journal-stamp-reef | cut71 | Great Barrier Reef stamp (landscape) | 🇦🇺 | journal stamp st-wide |
| au-journal-stamp-cliff | cut81 | sandstone-peak stamp (portrait) | 🇦🇺 Blue Mountains | journal stamp |
| au-journal-card-opal | cut10 | Opal transit card | 🇦🇺 Sydney | journal img prop |
| au-journal-ticket-cable | cut24 | cable-car ticket stub | 🇦🇺 Cairns | journal img prop |
| au-noir-hero | webp110 | airliner under the southern Milky Way (cover plate) | 🇦🇺 (generic-ish) | noir plate 0 |
| au-noir-sydney | webp136 | Sydney Harbour night plate | 🇦🇺 Sydney | noir plate |
| au-noir-coast | webp117 | east-coast clifftop night scene | 🇦🇺 Sydney | noir plate |
| au-noir-bluemtn | webp98 | Blue Mountains at night | 🇦🇺 Blue Mountains | noir plate |
| au-noir-reef | webp85 | night flight over the reef | 🇦🇺 Cairns | noir plate |
| au-noir-rainforest | webp131 | rainforest night | 🇦🇺 Cairns | noir plate |
| au-noir-dawn | webp72 | dawn return flight | 🇦🇺 (generic-ish) | noir plate |

## 14 Nordic/Norway 2026 test-trip assets (测试行程资产) (2026-08-15, generated by the Opus tester, $0.25; sheet masters nordic-journal-sheet-photo / -props in manifest) — 17
The two pressed flowers (fern/heather) carry zero region and are also listed in §12
generic pieces; `nordic-noir-aurora` (aurora) is reusable by any Arctic-Circle trip.

| Stem | Variants (KB) | Content | Region | Use |
|---|---|---|---|---|
| nordic-journal-ph-opera | cut39 | Oslo Opera House white ramp, polaroid | 🇳🇴 Oslo | journal photo |
| nordic-journal-ph-flamtrain | cut57 | Flåm Railway scenic train polaroid | 🇳🇴 Flåm | journal photo |
| nordic-journal-ph-fjordferry | cut40 | Nærøyfjord ferry-bow polaroid | 🇳🇴 fjords | journal photo |
| nordic-journal-ph-stegastein | cut45 | Stegastein viewpoint polaroid | 🇳🇴 fjords | journal photo |
| nordic-journal-ph-bryggen | cut50 | Bergen Bryggen wooden houses polaroid | 🇳🇴 Bergen | journal photo |
| nordic-journal-ph-floyen | cut31 | Bergen from Mount Fløyen, polaroid | 🇳🇴 Bergen | journal photo |
| nordic-journal-stamp-fjord | cut73 | fjord stamp NORGE (portrait) | 🇳🇴 | journal stamp st-a/st-b |
| nordic-journal-stamp-stave | cut68 | stave-church stamp (portrait) | 🇳🇴 | journal stamp st-a/st-b |
| nordic-journal-stamp-aurora | cut67 | aurora stamp (landscape) | 🇳🇴 | journal stamp st-wide |
| nordic-journal-ticket-ferry | cut34 | ferry ticket stub | 🇳🇴 | journal img prop |
| nordic-journal-flora-fern | cut45 | Nordic fern pressed flower | generic (pressed flowers carry no region) | journal flora stem |
| nordic-journal-flora-heather | cut37 | heather pressed flower | generic (pressed flowers carry no region) | journal flora stem |
| nordic-noir-hero | webp36 | fjord night-flight cover plate | 🇳🇴 (generic-ish) | noir plate 0 |
| nordic-noir-oslo | webp101 | Oslo at night | 🇳🇴 Oslo | noir plate |
| nordic-noir-fjord | webp49 | fjord at night | 🇳🇴 fjords | noir plate |
| nordic-noir-bergen | webp167 | Bergen at night | 🇳🇴 Bergen | noir plate |
| nordic-noir-aurora | webp75 | aurora (generic across the Arctic Circle) | 🇳🇴 / Arctic-Circle generic | noir plate |

## 15 Japan 2026 (London departure, English) test-trip assets (测试行程资产) (2026-08-15, illustrated (插画) + zine, $0.41; sheet masters in manifest) — 25
Region-bound pieces reuse only on same-country trips; those marked "generic" may cross
trips. Row content is inferred from stems — open the image for a look before reusing.

| Stem | Variants (KB) | Content (inferred from stem; open before reuse) | Region | Use |
|---|---|---|---|---|
| japan-bamboo | cut56 sm11 | bamboo | 🇯🇵 | illustrated/zine |
| japan-cover-hero | webp112 | cover hero | 🇯🇵 | illustrated |
| japan-gate | cut57 md53 sm7 | gate | 🇯🇵 | illustrated/zine |
| japan-lantern | cut32 sm7 | lantern | 🇯🇵 | illustrated/zine |
| japan-maple | cut68 md73 sm9 | maple | 🇯🇵 | illustrated/zine |
| japan-onsen | cut36 sm7 | onsen | 🇯🇵 | illustrated/zine |
| japan-pagoda | cut34 sm6 | pagoda | 🇯🇵 | illustrated/zine |
| japan-ph-fushimi | cut52 | ph fushimi | 🇯🇵 | illustrated/zine |
| japan-ph-hamarikyu | cut52 | ph hamarikyu | 🇯🇵 | illustrated/zine |
| japan-ph-kiyomizu | cut48 | ph kiyomizu | 🇯🇵 | illustrated/zine |
| japan-ph-meiji | cut54 | ph meiji | 🇯🇵 | illustrated/zine |
| japan-ph-owakudani | cut51 | ph owakudani | 🇯🇵 | illustrated/zine |
| japan-ph-tsukiji | cut47 | ph tsukiji | 🇯🇵 | illustrated/zine |
| japan-ropeway | cut50 sm9 | ropeway | 🇯🇵 | illustrated/zine |
| japan-stage | cut75 md63 sm7 | stage | 🇯🇵 | illustrated/zine |
| japan-stall | cut43 sm7 | stall | 🇯🇵 | illustrated/zine |
| japan-teahouse | cut53 sm8 | teahouse | 🇯🇵 | illustrated/zine |
| japan-torii | cut33 sm7 | torii | 🇯🇵 | illustrated/zine |
| japan-train | cut27 sm4 | white-and-blue Shinkansen nose (three-quarter view) | generic (in §12) | illustrated/zine |
| japan-zine-arashiyama | webp460 | zine arashiyama | 🇯🇵 | zine |
| japan-zine-cover | webp298 | zine cover | 🇯🇵 | zine |
| japan-zine-hakone | webp108 | zine hakone | 🇯🇵 | zine |
| japan-zine-momiji | webp216 | zine momiji | 🇯🇵 | zine |
| japan-zine-toji | webp90 | zine toji | 🇯🇵 | zine |
| japan-zine-tokyo | webp111 | zine tokyo | 🇯🇵 | zine |

## 16 Mainland China 2026 (New York departure, English) test-trip assets (测试行程资产) (2026-08-15, clay (黏土) + splash (闪屏), $0.30; sheet masters in manifest) — 23
Region-bound pieces reuse only on same-country trips; those marked "generic" may cross
trips. Row content is inferred from stems — open the image for a look before reusing.

| Stem | Variants (KB) | Content (inferred from stem; open before reuse) | Region | Use |
|---|---|---|---|---|
| china-clay-food | cut26 | clay bamboo steamer, lid open on four baozi + a wisp of steam | depends on the trip (Chinese cuisine, not a landmark) | clay |
| china-clay-pagoda | cut26 | clay pagoda | 🇨🇳 | clay |
| china-clay-palace | cut36 | clay palace | 🇨🇳 | clay |
| china-clay-title | cut100 md30 | clay title | 🇨🇳 | clay |
| china-clay-train | cut21 | clay high-speed-rail head car (white body, red stripe) + grey track | generic (in §12) | clay |
| china-clay-wall | cut28 | clay wall | 🇨🇳 | clay |
| china-clay-warriors | cut40 | clay warriors | 🇨🇳 | clay |
| china-splash-hero | cut134 md56 | splash hero | 🇨🇳 | splash |
| china-splash-m-dumpling | cut34 | thick-paint bamboo-steamer mascot (with eyes), lid open on baozi | depends on the trip (Chinese cuisine, not a landmark) | splash |
| china-splash-m-lantern | cut30 | splash m lantern | 🇨🇳 | splash |
| china-splash-m-panda | cut34 | splash m panda | 🇨🇳 | splash |
| china-splash-m-tea | cut19 | splash m tea | 🇨🇳 | splash |
| china-splash-m-warrior | cut32 | splash m warrior | 🇨🇳 | splash |
| china-splash-pagoda | cut49 sm8 | splash pagoda | 🇨🇳 | splash |
| china-splash-palace | cut60 sm8 | splash palace | 🇨🇳 | splash |
| china-splash-strip-beijing | cut54 | splash strip beijing | 🇨🇳 | splash |
| china-splash-strip-xian | cut48 | splash strip xian | 🇨🇳 | splash |
| china-splash-tiantan | cut54 sm8 | splash tiantan | 🇨🇳 | splash |
| china-splash-title | cut238 md56 | splash title | 🇨🇳 | splash |
| china-splash-train | cut42 sm7 | thick-paint high-speed-rail head-car sticker (round headlight eyes) | generic (in §12) | splash |
| china-splash-veh-train | cut27 | thick-paint high-speed train in motion, floating island (`vehicle` slot) | generic (in §12) | splash |
| china-splash-wall | cut51 sm8 | splash wall | 🇨🇳 | splash |
| china-splash-warriors | cut51 sm9 | splash warriors | 🇨🇳 | splash |

## 17 Italy 2026 (Singapore departure, Chinese) test-trip assets (测试行程资产) (2026-08-15, glass (玻璃) + portal (穿越), $0.36; sheet masters in manifest) — 6
Region-bound pieces reuse only on same-country trips; those marked "generic" may cross
trips. Row content is inferred from stems — open the image for a look before reusing.

| Stem | Variants (KB) | Content (inferred from stem; open before reuse) | Region | Use |
|---|---|---|---|---|
| italy-glass-arno | webp210 | glass arno | 🇮🇹 | glass |
| italy-glass-dawn | webp32 | glass dawn | 🇮🇹 | glass |
| italy-glass-hero | webp168 | glass hero | 🇮🇹 | glass |
| italy-glass-laguna | webp111 | glass laguna | 🇮🇹 | glass |
| italy-glass-roma | webp238 | glass roma | 🇮🇹 | glass |
| italy-glass-sky | webp31 | glass sky | 🇮🇹 | glass |

## 18 Mexico 2026 (Berlin departure, English) test-trip assets (测试行程资产) (2026-08-15, journal (手账) + noir (夜航), $0.2820; sheet masters mexico-journal-sheet-photo / -props in manifest) — 18
Region-bound pieces reuse only on Mexico trips; `mexico-journal-ticket-ado` shows zero
text and zero landmarks and is also listed in §12 generic pieces. All six noir plates
are real scenes; `mexico-noir-hero` is a wing + a highland sea of lights — generic-ish,
but it still carries Mexico City's landform.

| Stem | Variants (KB) | Content and use | Region | Theme |
|---|---|---|---|---|
| mexico-journal-ph-bellasartes | cut58 | Palacio de Bellas Artes stained-glass dome + orange-tile rooftop view (golden hour) | 🇲🇽 Mexico City | journal photo |
| mexico-journal-ph-teotihuacan | cut50 | stepped pyramid at the end of the Avenue of the Dead | 🇲🇽 Teotihuacán | journal photo |
| mexico-journal-ph-casaazul | cut71 | cobalt-blue courtyard wall + potted green cactus (Casa Azul) | 🇲🇽 Coyoacán | journal photo |
| mexico-journal-ph-marigold | cut87 | flower-market stall with a whole wall of marigolds (journal cover use) | 🇲🇽 | journal photo |
| mexico-journal-ph-panteon | cut64 | Día de Muertos candlelit cemetery | 🇲🇽 Oaxaca | journal photo |
| mexico-journal-ph-montealban | cut78 | leveled hilltop stone plaza overlooking the valley | 🇲🇽 Monte Albán | journal photo |
| mexico-journal-ph-loom | cut65 | treadle loom + half-woven geometric rug + dyed yarn | 🇲🇽 Oaxaca (craft) | journal photo |
| mexico-journal-ph-jalatlaco | cut57 | cobblestone alley + a full painted mural wall | 🇲🇽 Oaxaca | journal photo |
| mexico-journal-stamp-catrina | cut87 | Catrina skull-lady feathered-hat profile stamp (ink purple, portrait) | 🇲🇽 | journal stamp st-a/st-b |
| mexico-journal-stamp-pyramid | cut83 | stepped-pyramid stamp (ochre red, portrait) | 🇲🇽 | journal stamp st-a/st-b |
| mexico-journal-stamp-alebrije | cut83 | painted alebrije wood-carving stamp (teal + orange, landscape) | 🇲🇽 | journal stamp st-wide |
| mexico-journal-ticket-ado | cut35 | long-haul bus ticket stub: bus line drawing + serial number, no text or landmarks in frame | **generic** (see §12) | journal img prop |
| mexico-noir-hero | webp161 | 2 a.m. highland-basin city sea of lights + wing silhouette lower left | 🇲🇽 Mexico City (generic-ish) | noir plate 0 |
| mexico-noir-centro | webp138 | rain-slicked avenue ending at a floodlit white marble theater | 🇲🇽 Mexico City | noir plate |
| mexico-noir-piramides | webp165 | two pyramids flanking the dead-straight Avenue of the Dead under stars | 🇲🇽 Teotihuacán | noir plate |
| mexico-noir-panteon | webp137 | Día de Muertos cemetery: hundreds of candles + marigold arch + brass-band silhouettes | 🇲🇽 Oaxaca | noir plate |
| mexico-noir-oaxaca | webp147 | twin-tower baroque church + papel picado banners + lantern-and-mask procession | 🇲🇽 Oaxaca | noir plate |
| mexico-noir-montealban | webp112 | hilltop stone platforms at night + valley lights + agave in the foreground | 🇲🇽 Monte Albán | noir plate |

## 19 Morocco 2026 (London departure, English) test-trip assets (测试行程资产) (2026-08-15, glass (玻璃) + portal (穿越), $0.3624; the 5 portal seed frames are png-only, see manifest) — 6
The glass / noir / portal themes **structurally have nothing to reuse** (they consume
only 16:9 plates and i2v seed frames, and §12 had not a single 16:9 at the time — the
tester read all of §12 for nothing). This section's `morocco-glass-dawn` has since been
added to §12 as the first generic 16:9 plate.

| Stem | Variants (KB) | Content and use | Region | Theme |
|---|---|---|---|---|
| morocco-glass-hero | webp117 | sea of ochre-rose earthen rooftops + square minaret + distant Atlas snowline (cover) | 🇲🇦 Marrakech | glass background layer |
| morocco-glass-atlas | webp209 | adobe fortress village from above + palm-green band + red-brown ridgelines | 🇲🇦 Aït Benhaddou | glass background layer |
| morocco-glass-fes | webp212 | ultra-dense medina flat roofs + green-tile cone + square minaret | 🇲🇦 Fes | glass background layer |
| morocco-glass-blue | webp275 | a whole town of powder-blue-and-white houses + stair alleys + grey rock peak behind | 🇲🇦 Chefchaouen | glass background layer |
| morocco-glass-dunes | webp43 | dune crestline + three-camel caravan silhouettes | 🇲🇦 Merzouga | glass background layer |
| morocco-glass-dawn | webp53 | seaside dawn: calm sea + beach arc + distant white-house silhouettes, no landmark | **generic** (see §12) | glass finale leg |

**Portal (穿越版) videos stay out of the repo**: the 5 i2v seed frames `morocco-portal-{marrakech,ait,merzouga,fes,chefchaouen}-w` (1536×864 png, **never embedded in pages**; manifest has entries, files stay in trips/) generated **9 mp4s** — 5 dives (`ma01`-`ma05`) + 4 links (`ma01-ma02` … `ma04-ma05`), stored in **`trips/test-morocco-2026/portal/`**; the mp4s total ≈16MB and the whole `portal/` directory (incl. the `chain-frames/` frame-chain QA images) is **23MB** — kept out of `themes/assets/` purely for size. The 5 worlds = Marrakech / Aït Benhaddou / Merzouga dunes / Fes / Chefchaouen (per-world scene/motion/ambience in `trips/test-morocco-2026/portal-worlds.json`).

## 20 Turkey 2026 (Shanghai departure, Chinese) test-trip assets (测试行程资产) (2026-08-15, illustrated (插画) + clay (黏土), $0.2594; sheet masters turkey-sheet-illus / turkey-clay-sheet-figs in manifest) — 19
`turkey-balloon` has no landmark and is in §12; `turkey-shanghai` is the **departure
city** Shanghai (an `end.hero` squeezed into the illustration sheet's 8th cell, zero
cost) — never use it as a Turkey piece; `turkey-clay-title` bakes in the Chinese title
「九万里风」 ("Ninety Thousand Li of Wind") and is **this trip only** — no other trip may
reuse it.

| Stem | Variants (KB) | Content and use | Region | Theme |
|---|---|---|---|---|
| turkey-cover-hero | webp102 | illustrated full-frame cover (top 2/3 left clear for the title) | 🇹🇷 | illustrated (插画) |
| turkey-hagia | cut35 sm9 | grey-pink great dome + four slender minarets | 🇹🇷 Istanbul | illustrated (插画) / zine |
| turkey-bazaar | cut56 sm8 | striped-arch covered bazaar arcade + hanging lamps + stacked rugs | 🇹🇷 Istanbul | illustrated (插画) / zine |
| turkey-chimney | cut38 sm8 | cluster of conical fairy chimneys + small cave windows | 🇹🇷 Cappadocia | illustrated (插画) / zine |
| turkey-balloon | cut27 sm8 | four striped hot-air balloons lifting off, no landmark | **generic** (see §12) | illustrated (插画) / zine |
| turkey-pamukkale | cut31 sm7 | white travertine terraces + pale-teal pool water | 🇹🇷 Pamukkale | illustrated (插画) / zine |
| turkey-ferry | cut32 sm6 | white ferry + domed stone tower (Maiden's Tower) | 🇹🇷 Istanbul | illustrated (插画) / zine |
| turkey-underground | cut45 sm8 | underground stone-city passage + round stone door + lantern | 🇹🇷 Cappadocia | illustrated (插画) / zine |
| turkey-shanghai | cut33 sm8 | Shanghai Bund skyline (spire + bottle-opener tower) | 🇨🇳 Shanghai (**departure city**) | illustrated (插画) `end.hero` |
| turkey-clay-hagia | cut26 | clay grey-pink domed mosque + four minarets | 🇹🇷 Istanbul | clay |
| turkey-clay-bazaar | cut36 | clay bazaar stall: striped awning + rolled rugs + spice cones | 🇹🇷 Istanbul | clay |
| turkey-clay-chimney | cut25 | clay fairy chimneys, three cones + cave windows | 🇹🇷 Cappadocia | clay |
| turkey-clay-pamukkale | cut26 | clay travertine terraces (pale-teal water) | 🇹🇷 Pamukkale | clay |
| turkey-clay-mosque | cut29 | clay Ottoman mosque courtyard + twin-minaret archway | 🇹🇷 | clay |
| turkey-clay-tea | cut36 | clay tulip tea glasses ×2 + copper tray + pink sugar cubes | 🇹🇷 (Turkish tea set) | clay |
| turkey-clay-title | cut91 lg75 md53 sm10 | clay 3D Chinese title 「九万里风」 | **this trip only** (baked-in text) | clay title sticker |
| turkey-strip-istanbul | cut157 | terrain band: Hagia Sophia + Blue Mosque + tower + ferry + cypresses | 🇹🇷 Istanbul | clay band (`to:#bfe0e6`) |
| turkey-strip-cappadocia | cut142 | terrain band: fairy chimneys + cave houses + three balloons | 🇹🇷 Cappadocia | clay band (`to:#f0cba4`) |
| turkey-strip-pamukkale | cut151 | terrain band: travertine terraces + broken columns of the Hierapolis theater | 🇹🇷 Pamukkale | clay band (`to:#cfe7ea`) |

## 21 Vietnam 2026 (Shenzhen departure, Chinese) test-trip assets (测试行程资产) (2026-08-15/16, zine + splash (闪屏), $0.4566; sheet masters vietnam-zine-sheet-photo/-props and vietnam-splash-sheet-islands/-props/-strips in manifest) — 34
The library's largest single-trip section (11 calls cut into 34 stems / 49 webp).
`vietnam-ph-train` and `vietnam-splash-i-train` have no landmark and are also listed
in §12; the rest — conical hats, lanterns, pho bowls, drip-filter coffee, basket
boats — are **Vietnam-specific objects: not landmarks, but still barred from other
trips**.

| Stem | Variants (KB) | Content and use | Region | Theme |
|---|---|---|---|---|
| vietnam-zine-cover | webp230 | karst pillars + wooden junk in morning mist (portrait cover) | 🇻🇳 Ha Long Bay | zine |
| vietnam-zine-hanoi | webp364 | black-and-white: single-track train street in a narrow alley + conical-hat shoulder-pole vendor (portrait) | 🇻🇳 Hanoi | zine chapter head |
| vietnam-zine-hoian | webp206 | riverside old town at night: hundreds of silk lanterns + wet-street reflections (portrait) | 🇻🇳 Hoi An | zine chapter head |
| vietnam-zine-saigon | webp262 | mustard colonial post office + long-exposure scooter streams (portrait) | 🇻🇳 Saigon | zine chapter head |
| vietnam-zine-mekong | webp186 | from inside a sampan: nipa-palm canal archway + conical-hat boatwoman (landscape, closing band) | 🇻🇳 Mekong Delta | zine closer |
| vietnam-ph-pho | webp26 | beef pho on a low plastic stool at a night market | 🇻🇳 | zine photo |
| vietnam-ph-temple | webp55 | red lacquered gate + mossy-tile courtyard + stele-bearing stone turtle | 🇻🇳 Temple of Literature, Hanoi | zine photo |
| vietnam-ph-train | webp23 | coastal dawn light outside a sleeper-car window (no landmark, tropical-leaning coast) | **generic** (see §12) | zine photo |
| vietnam-ph-market | webp50 | covered-market stall: dried spices / chilies / stacked conical hats | 🇻🇳 | zine photo |
| vietnam-ph-cave | webp32 | cave-ceiling skylight falling on a stone Buddha | 🇻🇳 Marble Mountains, Da Nang | zine photo |
| vietnam-ph-motos | webp32 | river of scooters in front of a colonial market at dusk (slow shutter) | 🇻🇳 Saigon | zine photo |
| vietnam-hat | cut31 sm5 | gouache conical hat (with chin strap) | 🇻🇳 | zine prop |
| vietnam-lantern | cut28 sm5 | gouache round silk lantern + tassel | 🇻🇳 Hoi An | zine prop |
| vietnam-pho | cut40 sm7 | gouache pho bowl + chopsticks resting across it | 🇻🇳 | zine prop |
| vietnam-coffee | cut26 sm5 | gouache phin dripper + iced-coffee glass | 🇻🇳 | zine prop |
| vietnam-basketboat | cut43 sm6 | gouache round basket boat + paddle | 🇻🇳 | zine prop |
| vietnam-scooter | cut54 sm7 | gouache side-view scooter + herb basket on the pillion | 🇻🇳 | zine prop |
| vietnam-splash-hero | cut158 md66 | three limestone pillars + junk + two basket boats as a floating island (key visual, **use md**) | 🇻🇳 Ha Long Bay | splash |
| vietnam-splash-i-hoankiem | cut35 sm7 | red arched bridge + three-tier pagoda islet | 🇻🇳 Hoan Kiem Lake, Hanoi | splash day island |
| vietnam-splash-i-karst | cut41 sm6 | limestone pillar + winding lookout-path pavilion + small boat | 🇻🇳 Ha Long Bay | splash day island |
| vietnam-splash-i-train | cut32 sm7 | green sleeper carriage + bright yellow windows + crescent moon, no landmark | **generic** (see §12) | splash day island |
| vietnam-splash-i-bridge | cut36 sm9 | tile-roofed covered bridge hung with round lanterns | 🇻🇳 Japanese Covered Bridge (来远桥), Hoi An | splash day island |
| vietnam-splash-i-basket | cut45 sm10 | basket boat spinning in a nipa-palm pond + conical-hat boatman | 🇻🇳 | splash day island |
| vietnam-splash-i-marble | cut36 sm7 | marble cave arch + hilltop tiered pagoda | 🇻🇳 Marble Mountains, Da Nang | splash day island |
| vietnam-splash-i-postoffice | cut42 sm8 | mustard colonial post office + round clock + two scooters | 🇻🇳 Saigon | splash day island |
| vietnam-splash-i-sampan | cut49 sm10 | narrow wooden sampan in a canal | 🇻🇳 Mekong Delta | splash day island |
| vietnam-splash-moto | cut44 | thick-paint scooter (round headlight eyes) + herb basket | 🇻🇳 | splash vehicle |
| vietnam-splash-junk | cut43 | thick-paint junk with rust-red batwing sails | 🇻🇳 Ha Long Bay | splash vehicle |
| vietnam-splash-hat | cut31 | thick-paint conical hat (little smiley face under the brim) | 🇻🇳 | splash mascot |
| vietnam-splash-pho | cut38 | thick-paint pho bowl + chopsticks + lime | 🇻🇳 | splash mascot |
| vietnam-splash-lantern | cut29 | thick-paint warm-orange silk lantern | 🇻🇳 Hoi An | splash mascot |
| vietnam-splash-coffee | cut31 | thick-paint phin dripper + iced milk coffee | 🇻🇳 | splash mascot |
| vietnam-splash-strip-hanoi | cut70 | indigo old-quarter tube-house skyline silhouette + amber light dots (both ends fade out) | 🇻🇳 Hanoi | splash strip |
| vietnam-splash-strip-saigon | cut93 | deep-teal delta waterfront + palms + clock tower + rows of sampans (magenta afterglow) | 🇻🇳 Saigon | splash strip |

## 22 Stock generic asset pack (`stock/`, 2026-08-17, $0.9284) — 80 stems / 161 webp / 5.2 MB

**This section is only the entry point — the detail lives in `stock/README.md` and
`stock/index.json`; never mix stock pieces into the tables above.**
Purpose: when the agent has **neither native image generation nor a key**
(`prefs.pictures: "stock"`), it still ships illustrated theme pages — this pack is a
pre-generated gouache-style generic picture library. **With generation capability,
don't use it**: covers/key visuals are still generated fresh for the trip (the rule
at the top stands).

| Content | Count | Files | Use |
|---|---|---|---|
| Regional cover paintings (16:9 opaque, top 2/3 left clear for the title) | 14 | `stock-cover-<archetype>.webp` (55–124 KB) | `cover.hero`, picked by country → archetype |
| Generic scene cutouts | 30 | `stock-<scene>.cut.webp` + `.sm` (some `.md`) | day chapter-head `days[date].hero` |
| World-landmark cutouts | 36 | `stock-<landmark>.cut.webp` + `.sm` (some `.md`) | same, preferred when a landmark keyword hits |

- The 14 archetypes: european-old-town / mediterranean-coast / east-asian-temple /
  southeast-asia / tropical-beach / desert-medina / alpine-lake / nordic-fjord /
  modern-skyline / savanna / rainforest / andes-colonial / castle-highlands /
  north-america-roadtrip.
- `stock/index.json` = the lookup table: archetype keywords, **225 ISO2 →
  archetype** mappings, multilingual country names (en/local/Chinese, 702 entries),
  multilingual keywords per cutout, a country index of this library's existing
  illustrated pieces (JP/TR/US/CN), and generic transport pieces
  (plane/bus/japan-train/turkey-balloon).
- Generation is recorded in `stock/manifest.stock.json` (25 calls: 14 covers + 11
  3×2 sheets cut into 66 pieces; prompt skeletons copied from `japan-cover-hero` /
  `japan-sheet-cutouts-a`, `style_anchor` same as this library). PNG masters stay
  out of the repo per `themes/**/*.png`.
- ⚠️ **Rendering needs `--assets themes/assets/stock`**: `data_uri` searches only
  `themes/assets/` and the plan's own directory — it does not recurse into
  subdirectories.
- ⚠️ **The image source must be printed on the page** (`end.fine` + `cover.credit`;
  both language versions are in `index.json.notice`) — omitting it means shipping
  fallback art as if it were custom.

## 23 Yunnan 2026 (Sydney departure, English) test-trip assets (测试行程资产) (2026-08-29, illustrated (插画) + glass (玻璃) + journal (手账) + splash (闪屏), $0.3274; sheet masters yn-illus-sheet / yn-journal-sheet / yn-splash-sheet in manifest) — 32
All 32 stems are region-bound — none enters §12. `yn-i-sydney` is the **departure
city** Sydney (an `end.hero` squeezed into the illustration sheet's 9th cell, zero
cost) — never use it as a Yunnan piece; `yn-splash-title` bakes in the English title
plate "SOUTH OF THE CLOUDS" and is **this trip only**; the generic-looking glass
plates and splash scenery chunks (`yn-glass-hero` lake, `yn-glass-snow` snow ridge,
`yn-si-wetland` reed wetland, `yn-si-dawnpool` pavilion pool) were all prompted as
specific Yunnan scenes and stay Yunnan-bound.

| Stem | Variants (KB) | Content and use | Region | Theme |
|---|---|---|---|---|
| yn-cover-hero | webp102 | illustrated full-frame cover: karst + pagodas-by-the-lake + snow ridge along the lower third, top 2/3 sky left clear for the title | 🇨🇳 Yunnan | illustrated (插画) |
| yn-glass-dawn | webp128 | first light over grey-tiled old-town roofs, mist in the lanes + distant pink snow peak (16:9 plate) | 🇨🇳 Lijiang | glass (玻璃) plate |
| yn-glass-hero | webp150 | aerial: long deep-blue highland lake between snow ridge and village plain (16:9 cover plate) | 🇨🇳 Dali (Erhai) | glass (玻璃) plate 0 |
| yn-glass-karst | webp145 | field of tall grey limestone pinnacles under a high pale sky (16:9 plate) | 🇨🇳 Kunming (Stone Forest) | glass (玻璃) plate |
| yn-glass-snow | webp201 | snow-capped ridge over dark pines + turquoise glacier-melt pool (16:9 plate) | 🇨🇳 Lijiang (Jade Dragon) | glass (玻璃) plate |
| yn-i-gulls | cut31 sm10 | gouache: red-beaked gulls wheeling over a willow-fringed lake pavilion | 🇨🇳 Kunming (Green Lake) | illustrated (插画) |
| yn-i-karst | cut32 sm9 | gouache: karst pinnacle cluster + winding path | 🇨🇳 Kunming (Stone Forest) | illustrated (插画) |
| yn-i-pagodas | cut29 sm8 | gouache: three slender white pagodas + snow ridge behind | 🇨🇳 Dali (Three Pagodas) | illustrated (插画) |
| yn-i-baihouse | cut31 sm8 | gouache: white-walled grey-tiled Bai courtyard house + painted eaves + screen wall | 🇨🇳 Dali (Xizhou) | illustrated (插画) |
| yn-i-snowridge | cut26 sm7 | gouache: snow ridge + one cable-car pylon | 🇨🇳 Lijiang (Jade Dragon) | illustrated (插画) |
| yn-i-pools | cut34 sm9 | gouache: terraced turquoise pools stepping over pale weirs + two pines | 🇨🇳 Lijiang (Baishui / White Water River) | illustrated (插画) |
| yn-i-roofs | cut32 sm8 | gouache: grey-tiled sloping roofs + arched stone bridge over a water channel | 🇨🇳 Lijiang old town | illustrated (插画) |
| yn-i-tiedye | cut30 sm9 | gouache: indigo tie-dyed cloth with white sunburst patterns on a bamboo pole | 🇨🇳 Dali (Bai tie-dye, Zhoucheng) | illustrated (插画) |
| yn-i-sydney | cut36 sm8 | gouache: harbour skyline at dusk — sail-shell opera house + steel arch bridge | 🇦🇺 Sydney (**departure city**) | illustrated (插画) `end.hero` |
| yn-ph-greenlake | cut24 | Kodachrome polaroid: park lake at dawn, gulls over a red lakeside pavilion | 🇨🇳 Kunming (Green Lake) | journal (手账) photo |
| yn-ph-karst | cut28 | polaroid: limestone pinnacle field under a high sky | 🇨🇳 Kunming (Stone Forest) | journal (手账) photo |
| yn-ph-pagodas | cut24 | polaroid: three pagodas mirrored in a still pool + snow ridge | 🇨🇳 Dali (Three Pagodas) | journal (手账) photo |
| yn-ph-erhai | cut26 | polaroid: wide blue mountain lake + weathered jetty + one fishing boat | 🇨🇳 Dali (Erhai) | journal (手账) photo |
| yn-ph-xizhou | cut31 | polaroid: whitewashed courtyard farmhouse at the edge of a stubble field | 🇨🇳 Dali (Xizhou) | journal (手账) photo |
| yn-ph-indigo | cut34 | polaroid: indigo-dyed cloth drying on lines in a village yard | 🇨🇳 Dali (Zhoucheng tie-dye) | journal (手账) photo |
| yn-ph-snowridge | cut24 | polaroid: boardwalk on a bare snow ridge above a sea of cloud | 🇨🇳 Lijiang (Jade Dragon) | journal (手账) photo |
| yn-ph-pools | cut31 | polaroid: terraced turquoise pools below a snow mountain | 🇨🇳 Lijiang (Baishui) | journal (手账) photo |
| yn-ph-nightlane | cut31 | polaroid: night lane of grey-tiled roofs, red lanterns over a stone water channel | 🇨🇳 Lijiang old town | journal (手账) photo |
| yn-splash-title | cut24 | thick-paint game-title plate "SOUTH OF THE CLOUDS" (two lines) | **this trip only** (baked-in text) | splash (闪屏) title |
| yn-splash-hero | cut30 | floating rock chunk + chunky twin-peaked snow mountain + pines (key visual) | 🇨🇳 Lijiang (Jade Dragon) | splash (闪屏) |
| yn-si-greenlake | cut27 sm9 | floating grass chunk: round green lake + red-roofed pavilion + birds | 🇨🇳 Kunming (Green Lake) | splash (闪屏) day island |
| yn-si-karst | cut32 sm10 | floating rock chunk crowded with limestone pinnacles + winding path | 🇨🇳 Kunming (Stone Forest) | splash (闪屏) day island |
| yn-si-pagodas | cut29 sm8 | floating grass chunk: three white pagodas + lake-water front edge | 🇨🇳 Dali (Three Pagodas) | splash (闪屏) day island |
| yn-si-roofs | cut29 sm8 | floating chunk of grey-tiled roofs + arched bridge + waterfall edge | 🇨🇳 Lijiang old town | splash (闪屏) day island |
| yn-si-glacier | cut28 sm9 | floating glacier-ice chunk + slim cable-car pylon + mist | 🇨🇳 Lijiang (Jade Dragon cableway) | splash (闪屏) day island |
| yn-si-wetland | cut30 sm8 | floating wetland chunk: green reeds + wooden rowing boat + two geese | 🇨🇳 Lijiang (Lashihai wetland) | splash (闪屏) day island |
| yn-si-dawnpool | cut31 sm9 | floating chunk: black-tiled pavilion + still pool reflecting a snow peak | 🇨🇳 Lijiang (Black Dragon Pool) | splash (闪屏) day island |

## 24 Peru 2026 (Seoul departure, Chinese) test-trip assets (测试行程资产) (2026-08-29, clay (黏土) + noir (夜航) + zine, $0.4318; sheet masters peru-clay-sheet-figs / peru-zine-sheet in manifest) — 22
`peru-clay-train` and `peru-zine-trainwindow` have no landmark and are also listed in
§12; `peru-clay-ceviche` (Peruvian cuisine) and `peru-noir-hero` (night flight over
dark mountains, prompted over the Andes) sit in §12's **decide-per-trip** list — reuse
only on a matching trip; `peru-clay-title` bakes in the Chinese title 「云上石城」
("Stone City above the Clouds") and is **this trip only**. The rest — llamas, Inca
walls, salt pans, bowler-hat markets — are Peru-bound.

| Stem | Variants (KB) | Content and use | Region | Theme |
|---|---|---|---|---|
| peru-clay-llama | cut23 | clay woolly white llama + red-orange woven blanket | 🇵🇪 (Andes) | clay (黏土) |
| peru-clay-wall | cut27 | clay Inca stone-wall block + trapezoid doorway + tiny terrace | 🇵🇪 Cusco | clay (黏土) |
| peru-clay-cathedral | cut32 | clay pastel cathedral facade, two square bell towers on a plaza base | 🇵🇪 Cusco | clay (黏土) |
| peru-clay-train | cut26 | clay blue-and-cream tourist train carriage, big round windows, no landmark | **generic** (see §12) | clay (黏土) |
| peru-clay-ceviche | cut26 | clay ceviche plate: white fish cubes + red onion curl + corn cob | 🇵🇪 (cuisine — **decide per trip**, see §12) | clay (黏土) |
| peru-clay-salt | cut34 | clay hillside of tiny white salt pans stepping down | 🇵🇪 Maras | clay (黏土) |
| peru-clay-title | cut68 md24 | clay 3D Chinese title 「云上石城」(one line, four characters) | **this trip only** (baked-in text) | clay (黏土) title sticker |
| peru-strip-andes | cut127 | terrain band: green terraces + adobe village + three llamas + Moray circular terraces | 🇵🇪 Sacred Valley | clay (黏土) band |
| peru-strip-lima | cut116 | terrain band: sea cliff + surfers + colonial balcony block + adobe step-pyramid + palms + food cart | 🇵🇪 Lima | clay (黏土) band |
| peru-strip-machu | cut109 | terrain band: yellow tourist train + trapezoid-door ruins + steep pointed peak + cloud puff | 🇵🇪 Machu Picchu | clay (黏土) band |
| peru-noir-hero | webp51 | night flight over dark Andes ridges, amber horizon + airliner silhouette (16:9 plate) | 🇵🇪 (generic-ish — **decide per trip**, see §12) | noir (夜航) plate 0 |
| peru-noir-lima | webp94 | Pacific cliff promenade at blue hour, lamps + towers + sea mist (16:9 plate) | 🇵🇪 Lima (Miraflores) | noir (夜航) plate |
| peru-noir-cusco | webp152 | high Andean colonial town at dusk: terracotta roofs + twin-towered cathedral on a lit square (16:9 plate) | 🇵🇪 Cusco | noir (夜航) plate |
| peru-noir-machu | webp79 | stone citadel at dawn, mist pouring through the valley + pointed peak (16:9 plate) | 🇵🇪 Machu Picchu | noir (夜航) plate |
| peru-zine-cover | webp452 | b/w: stone citadel on a ridge + towering peak + torn cloud (portrait cover) | 🇵🇪 Machu Picchu | zine |
| peru-zine-band | webp227 | b/w: terraced Andean mountainsides falling into a river valley (16:9 band) | 🇵🇪 (Andes) | zine |
| peru-zine-plaza | cut76 | b/w: arcaded colonial square + baroque cathedral, pigeons off wet paving | 🇵🇪 Cusco | zine photo |
| peru-zine-stonewall | cut89 | b/w: massive polygonal Inca wall, one hand for scale | 🇵🇪 Cusco | zine photo |
| peru-zine-market | cut77 | b/w: Andean market alley, stacked blankets + woman in a bowler hat | 🇵🇪 (Andean market) | zine photo |
| peru-zine-trainwindow | cut62 | b/w: view out a moving train window down a river gorge, no landmark | **generic** (see §12) | zine photo |
| peru-zine-salt | cut85 | b/w: hillside of hundreds of salt evaporation pans | 🇵🇪 Maras | zine photo |
| peru-zine-cliff | cut71 | b/w: Pacific sea-cliff promenade + paragliders above the drop | 🇵🇪 Lima (Miraflores) | zine photo |
