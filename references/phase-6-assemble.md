# Phase 6 — Assemble, self-check, deliver (the procedure)

Read this at the start of Phase 6, before the final `plan.geo.json` is written.
SKILL.md Phase 6 is the contract — inputs, outputs, and the gates that decide pass/fail;
this file is the whole procedure it points at. Nothing here is optional: the self-check
list runs in full, the acceptance bars are exit codes and eyes, and the exit criteria at
the bottom are ticked before the chat summary goes out.

Inputs: `plan.geo.json` assembled per references/output-template.md, plus Phase 0's
`prefs.theme` / `prefs.pictures` / `plan.lang`. Outputs, three things every time: (1) the
chat summary — route one-liner, total budget, the 3 biggest decisions made for the user,
and in stock mode the picture notice; (2) `trip-<theme>.html`; (3) `trip.kml` — plus the
gates `.ics`, always (the pre-departure ladder rows are date-locked gates).


## Assembly order

Assemble per references/output-template.md: overview → decisions made for the user →
booking checklist → flights/intercity table → day-by-day cards → hotels → budget
rollup → country brief.

## Cover title

**Cover title (bilingual)**: when the deliverable is a rendered page, pick or adapt a
poetic display title from references/cover-titles.md — zh 2-6 characters + an English
line, matched to the trip archetype (road-trip / island / mountain / city / coast).
Never ship a literal placeholder like "X国行"; never use the clichés on that file's
blacklist. Cite the allusion honestly (the source line in the subtitle or a small
credit line).

## Adversarial self-check

**Adversarial self-check** — run this list against the finished plan, fix what it
catches, then record "self-checked: N issues found and fixed" in `meta.self_check`
(the plain page's footer) **and** as the last `decisions[]` row (seven of the eight
themed pages render `decisions`; only journal also prints `meta.self_check`, and
portal renders neither — on portal the chat summary carries it):
- Closure scan: every anchor's closed-days vs its scheduled date (Mondays! holidays
  from Phase 1 — including "closed Tue when Mon is a holiday" rules), **and** the
  classes the holiday feed misses: festivals overlapping the window, seasonal
  operating windows, venue maintenance shutdowns, Ramadan, worship-hour and siesta
  closures (scheduling.md §Traps). Rain alternatives get scanned too — an alternative
  that is closed on the day it backs up is the bug this scan exists to catch.
- Open-jaw direction consistent across flights, hotels, and day order
- Arrival/departure days respect Phase 2 §3; airport buffer = 3 h international + real
  city→airport transfer time
- Every intercity leg: plausible duration; separate-ticket air self-transfer ≥ 4 h;
  rail connections ≥ 30 min — except a **timed meet** (a bus/boat that waits for the
  train, e.g. Füssen train → Neuschwanstein bus, 9 min by design): keep it, name it as
  a meet in the hop note, and give the next timed ticket the slack instead
- Last-entry time vs planned arrival for each anchor
- Timeline checks from scheduling.md §verification: chain arithmetic (block start ≥
  prev end + hop + buffer), day walking totals ≤ 8 km, late hops vs last departures,
  golden-hour blocks vs actual sunset — and every sunrise / sunset / dark-start time
  in the prose was written **after** `sun --write`, matching `days[].sun` (the
  script exited 0; any `sun_stop` override is on the right day); `route_tools check`
  exits 0 (no BROKEN or SUSPICIOUS hops survived into the render)
- Red-eye / timezone day-number arithmetic
- Guided and self-drive days: every `must: true` sub-stop on a `tour: true` row is
  `confirmed` in writing or pending with its checklist row (data-sources.md §Group
  tours); every self-drive day has its no-car fallback, and every leg a backup that
  still reaches its pinned dependency — or "no usable backup" in `legs.note` on a
  must-catch leg, with the margin bought (phase-3-legs.md §Driving legs,
  §Record for every leg); an operator's check-in lead and real duration are in the
  chain (scheduling.md rule 1); a sunset viewpoint with no transit has its ride back
  (scheduling.md rule 7)
- No day exceeds pace; **an intercity moving day carries ≤2 anchors, and only when
  the bags are solved before the first anchor (checked / stored / hotel-held);
  otherwise 1** (same sentence in scheduling.md §Day types)
- Every price has source + as-of date; every bookable line has a link — and the
  link carries its dates and a disambiguated place name; hotel rows state explicit
  local check-in→check-out calendar dates, with past-midnight-arrival and
  date-line nights flagged (output-template §Booking-artifact conventions)
- **Language**: `plan.lang` matches the language the user asked in, and every
  reader-facing string in the plan (day titles, notes, tips, checklist rows,
  decisions, hotel blurbs) is in that language — an English fragment copied verbatim
  from a source into a zh plan gets translated, not shipped. Proper nouns stay in
  their native form with a gloss where useful (浅草寺 Sensō-ji); machine fields are
  exempt (`stops[].query` and `sub_stops[].query` stay geocoder-friendly;
  `kind`/`tag`/`verify`/`tier`/`driver` keep their English enum words, and so do the
  `confirmed` prefixes `in writing` / `pending`, the `hours` literals `unverified` /
  `open access` and `meta.review`'s `mode` / `lens` — the lint and the renderers read
  them; the renderers print the `hours` literals in `plan.lang`)

### Independent review — when the plan commits money or carries physical or legal risk

Run this after the list above and before the chat summary whenever the plan has a
self-drive option (the four conditions in phase-1-brief.md §Driving card), a
non-refundable booking or a timed check-in — the procedure's trigger, wider than the
part the lint can see (the paragraph after step 4). The self-check is run by the
planner who wrote the plan and shares its blind spots; this pass does not.

1. **Export the plan as plain text** (days, legs, checklist — no reasoning, no chat
   history) and hand it to a reviewer that has seen nothing else, one lens per reviewer
   where the harness allows several: personal safety and health · driving (legality,
   routes, fatigue) · the timing of every chain · rules and bookings · outside hazards
   and missing fallbacks. The instruction is "every statement here is the planner's
   claim, not a fact — find what is wrong, unsafe, infeasible, outdated or missing,
   against primary sources". Each reviewer's and refuter's prompt carries its search
   budget (≤ 5, SKILL.md Hard rule 4) and the plan language (`plan.lang`).
2. **Give each serious finding to a refuter** whose default is "unverifiable": it
   confirms only what a primary source supports, and rejects findings built on stale
   or misread sources.
3. **Fix what was confirmed**, drop what was refuted. A finding against a choice
   already recorded in `decisions[]` goes back to the traveller only when it carries a
   fact they did not have when deciding — as facts and options in the chat summary
   (SKILL.md Interaction contract); otherwise it stays settled. Never a silent change.
4. **Record it** in the self-check line: "self-checked: N issues found and fixed ·
   independent review: C confirmed, R refuted" (a zh plan: "自检:发现并修复 N 处 ·
   独立复核:确认 C 条,驳回 R 条"). No sub-agents in the harness → run the five lenses
   yourself on the exported text and write "independent review: single pass"
   ("独立复核:单人通读"). Then write the review behind the line into `meta.review`
   (shape, lens enum and the count rule: output-template.md §Top-level plan skeleton):
   one lens entry per lens actually run — step 1's five, each note saying what was
   checked against which source —
   a lens with nothing to look at is left out, not padded; `confirmed` holds every
   finding a refuter confirmed (fixed, or under step 3 sent back to the traveller or
   left settled — say which), `refuted` the findings dropped.

`plan_lint.py` sees the machine-readable part of the trigger — the self-drive set,
`"refundable": false` on a legs or checklist row, `tour: true` on a timeline row (the
one list: `plan_lint.py`'s module docstring); a timed check-in without a tour block
stays procedure-only. On that trigger `--strict` fails a plan whose `meta.self_check`
or last `decisions[]` row lacks the clause, or that has no `meta.review`; a
`meta.review` that is present is checked against every clause present, in every mode.
The gate reads a record that is specific and consistent, not proof that the review ran
(KNOWN-ISSUES PLN-13). This review is the pass that catches what the planner itself
just proposed — a self-drive day in a jurisdiction that does not recognise the
traveller's licence is the kind of finding it exists for.

## Deliver

**Deliver — the deliverable is a themed page, never a plain text one.** Render
`plan.geo.json` through the theme chosen in Phase 0 (`prefs.theme`, default
**illustrated**) — see *Themed renders* below — and hand over: a chat summary (route
one-liner, total budget, the 3 biggest decisions made for the user, and in stock mode
the one-line picture notice) + `trip-<theme>.html`, one self-contained, phone-friendly
file with its own share/export buttons and the appendix (checklist, legs, hotels,
budget, brief). Publish through whatever artifact / file hand-off tool the harness
has (in Claude Code: Artifact, else SendUserFile); otherwise save the file and give
its absolute path. Ship the trip KML (`scripts/route_tools.py kml plan.geo.json -o
trip.kml`) alongside for offline map apps, and the gates `.ics` — always, because the
ladder rows are date-locked gates (output-template.md §Pre-departure re-check ladder,
§On-trip re-audit rows for trips of seven days or more, and §Booking-artifact
conventions) — `python3 scripts/route_tools.py ics plan.geo.json -o gates.ics` writes it
from the checklist rows (ISO dates or `T-N` markers in `deadline`) and each day's
`decision_points`; bump `--sequence` on every plan change — a lint fix that adds or
re-dates a checklist row means `ics` runs again; `plan_lint.py` WARNs when the file is
older than the plan. Before any renderer runs, **`python3 scripts/plan_lint.py
plan.geo.json --strict` must exit 0**: it is the machine gate for what the plan says,
and its module docstring is the one list of what it checks. The one FAIL
the gate tolerates: a polar day's `sun` (output-template.md §`sun`; KNOWN-ISSUES
PLN-11) — `sun --write` refuses such a day, so render with exactly those FAIL lines and
no other, name the dates in the chat summary, and never type a `sun` string to turn
them green. `check` proves the geography and `qc.py` the HTML; neither looks at the
words. The plain
`scripts/render_plan.py plan.geo.json
-o trip.html` page (printable, checkbox checklist, offline route sketch per day) is an
**extra** — add it when the user asks for a printable/plain version, or as the last
resort if the theme renderer still fails after one honest fix attempt (then say so in
the summary). **`plan.geo.json` is the single editable source** for all of it — every
command above reads that one file — so a later "move day 3 to Nara" is a JSON edit
plus geocode → check → links → kml → render, not a rewrite. **One hand-off per agreed
version**: while a change is being discussed it moves in `plan.geo.json` only; once the
traveller agrees it, re-stamp `meta.generated`, re-render, re-run `ics` with the next
`--sequence`, and hand the
page, `trip.kml` and the `.ics` over once, with one line restating what changed. The
page chrome (section names, buttons, pills, weekdays) speaks `plan.lang` (set in
Phase 0, `zh` default);
`--lang zh|en` on any renderer overrides it, plan content prints as written.

## Themed renders

**Themed renders** — the same `plan.geo.json` through one of the eight themes in
`themes/`. Themes: **illustrated 插画** (a painted book on paper — the default) ·
**clay 黏土** (one continuous clay landscape with a road) · **noir 夜航** (a single
night-negative tracking shot) · **glass 玻璃** (liquid-glass panes over crossfading
photos) · **journal 手账** (a vintage travel journal: tape, stamps, polaroids) ·
**zine** (torn riso-poster collage) · **splash 闪屏** (game-splash floating islands,
chained sky gradients) · **portal 穿越** (scroll-scrubbed video fly-through — needs
footage, see below). `render_picker.py` renders a one-page style chooser of all of
them. Flow:
1. Write `<plan>.art.json` next to the plan (contract: `themes/ART-SCHEMA.md`) — the
   **common** block first (cover poem title from references/cover-titles.md, `kick`,
   `home`, `end`, and per day `theme` 4 chars / `en` / `mark`), then one block per
   theme you render. Pictures, by `prefs.pictures` (Phase 0):
   - **native / key — generate for this trip.** The cover / hero / title sticker /
     terrain bands are destination scenery and are ALWAYS generated for this trip, in
     the theme's own style — priority: the trip's actual sights (Xi'an city wall, the
     Great Wall) > a national landmark > a neutral scene, but never blank and never
     another trip's band (a China page once opened on the New York skyline because a
     default band was reused). The same ladder applies to `end.hero` / the tail cover,
     with one twist: that picture is the **return to the departure city** (home skyline
     at landing, not another destination view) — generated for this trip too. "Reuse
     first" applies only to generic props: `themes/assets/IMAGE-LIBRARY.md` §Generic pieces (通用件)
     lists what any trip may use; generate the rest — **with the agent's own native
     image/video generation if it has one (no key to configure; same specs, same
     prompts-as-style-anchors, same split/cutout/webp/manifest steps — ART-SCHEMA.md
     §Generator choice), otherwise `gen.py` / `genvideo.py` over OpenRouter** — using the
     sheet recipe in ART-SCHEMA.md (title stickers: one centred sticker, symmetric
     lines, no icons inside the letters), then `towebp.py`, and keep the webp beside
     the plan (or pass `--assets DIR`).
   - **stock — no generator, no key: use the stock kit, still a themed page.**
     Two commands, both from the skill root (absolute paths when your cwd is the
     trip folder):
     ```
     python3 <skill>/themes/stock_art.py plan.geo.json --theme illustrated -o plan.art.json
         # also --theme clay · --lang zh|en · --country ISO2 (when the plan's own words
         # do not name the destination) · --index PATH · --force (overwrite)
     python3 <skill>/themes/render_theme2.py plan.geo.json --art plan.art.json \
         --assets <skill>/themes/assets/stock -o trip-illustrated.html
         # --assets is REQUIRED in stock mode: data_uri() does not look inside
         # themes/assets/stock on its own — without it the page renders, qc passes,
         # and the stock pictures are silently missing. The script prints this exact
         # render line on its last stderr line; paste it.
     ```
     `stock_art.py` builds the picture side of the art file from `themes/assets/stock/`
     (region cover paintings, landmark and generic-scene cut-outs, matched to the
     plan's country and each day's stops; `themes/assets/stock/README.md`) plus the
     shared library's same-country pictures and generic props. It leaves the **words**
     to you — fill `cover` title (references/cover-titles.md), each day's `theme` /
     `en` / `mark`, captions and the closing line before rendering; a page shipped
     with the script's placeholders is a defect. The script writes the stock notice
     into `end.fine` (full) and `cover.credit` (short form; if the cover also cites a
     poem, keep the citation first and the notice after it — the fine print carries
     the full text anyway); keep both, and repeat the notice in the chat summary —
     `prefs.pictures` is set to `stock` the moment `stock_art.py` runs, whatever Phase 0
     found — the summary's notice keys off it;
     the exact strings are `notice.en` / `notice.zh` in `themes/assets/stock/index.json`
     (en: "Pictures: built-in stock kit — no image generator or key was available;
     provide one and the art is generated for this trip.").
2. `python3 themes/render_<theme>.py plan.geo.json -o trip-<theme>.html`
   (`--art F|none`, `--assets DIR`, `--lang zh|en`); a missing art file must still
   render. Renderer files: illustrated = `render_theme2.py`, clay = `render_clay2.py`,
   noir = `render_noir2.py`, glass = `render_glass2.py`; journal / zine / splash /
   portal use their own name (`render_journal.py` …). All eight themes and the picker render in **en** as well as zh: the UI
   shell (buttons, tags, section names, weekdays, cover fallbacks) follows
   `plan.lang` / `--lang`, art copy renders in whatever language it was written
   (ART-SCHEMA.md §language; English cover titles: references/cover-titles.md).
3. `python3 themes/qc.py trip-<theme>.html` must exit 0, then
   `themes/xprobe.sh trip-<theme>.html module '#d5' out.png` and **look at the PNG**
   — a green probe title is not proof; blank icons and cropped tails only show visually.
   No headless Chrome in this environment → open the HTML in whatever browser tool
   you have (a browser pane may refuse `file://` — serve the folder with
   `python3 -m http.server` and open `http://localhost:8000/trip-<theme>.html`) and
   look at the cover and one day; if you have none, say so in the summary.
Each of the seven still themes carries its own share buttons (保存这一天 / 保存附录 /
生成长图 — Save this day / Save appendix / Save long image in en), offline, no
dependencies; noir and glass export day modules only, portal (video) has none —
screenshot it. Portal is the "only when footage exists" theme: it needs **its own**
footage chain beside the HTML; the US 19-clip chain is the style reference and pipeline
example, not a substitute (another trip's scenery on a cover is a logged defect). That
chain is a release asset, **not in the tree** — `themes/assets/portal/` is empty in a
fresh clone and its README.md has the one-line curl+unzip restore; the shipped portal
case is Morocco (live on the demo site). Details, per-theme limits and the new-theme
manual: references/themes.md.

## After the trip

Read this when the traveller is home and asks about a refund, a receipt, a complaint or
a review; nothing here runs before delivery, and the exit criteria below do not cover it.
Each item below is a draft: the traveller submits the claim, the receipt request and the
complaint themselves (SKILL.md Hard rule 1 — a claim form carries personal data).
- **A refund claim starts from the leg row**: quote its refund/change class and
  checked-bag fee (phase-3-legs.md §Record for every leg) verbatim before raising it —
  no refund exists for a bag a basic fare never included.
- **A flown trip drops out of the carrier's "my trips"**: the 13-digit e-ticket number
  (phase-3-legs.md §Record for every leg) finds the receipt; an OTA order number does not.
- **Reviews and complaints go inside the operator's window**, through the operator's
  own form first.
- **The other post-trip output** is the photo album — on the roadmap
  (docs/KNOWN-ISSUES.md §Roadmap), not built yet.


## Exit criteria — tick every line before the chat summary goes out

- [ ] `python3 scripts/plan_lint.py plan.geo.json --strict` exited 0 before rendering
      (brief present and in order, no placeholders, self-check line, art filled, `.ics`
      and `trip.kml` beside the plan, a stop and a `sun --write` string on every day) —
      or exited with only the polar-day `sun` FAILs (PLN-11), named in the chat summary.
- [ ] Adversarial self-check ran in full; "self-checked: N issues found and fixed" is in
      `meta.self_check` **and** the last `decisions[]` row (portal: in the chat summary).
- [ ] A plan with a self-drive option, a non-refundable booking or a timed check-in went
      through §Independent review, the same line (in `meta.self_check` and the last
      `decisions[]` row) says "independent review: C confirmed, R refuted" (or "single
      pass"), and `meta.review` records the lenses and findings behind it.
- [ ] `route_tools.py links --write` was re-run after the last `sub_stops` edit —
      `plan_lint` prints no "no link" WARN.
- [ ] `route_tools check` exited 0 before rendering; every sunrise / sunset / dark-start
      time in the prose was written after `sun --write` and matches `days[].sun`.
- [ ] `plan.lang` matches the user's language; no untranslated source fragments.
- [ ] Every price carries source + as-of date; every bookable line has a link that carries
      its dates and a disambiguated place; hotel rows state check-in→check-out dates.
- [ ] `trip-<theme>.html` rendered through the Phase 0 theme; `themes/qc.py` exited 0;
      the export probe PNG or the page in a browser was looked at (none available → the
      summary says so).
- [ ] Cover title from references/cover-titles.md — never a placeholder, never a
      blacklisted cliché; the allusion is credited.
- [ ] Stock mode: the picture notice is in `end.fine`, `cover.credit` and the chat
      summary, and every script placeholder was replaced with real words.
- [ ] `brief` keys in the canonical order with the required cards present
      (output-template.md §Brief templates), every card titled in `BRIEF_TITLES`;
      `brief.weather` and every weather line carry the mode (forecast / normals /
      climate model) + as-of.
- [ ] Phase 1 still holds at delivery: `brief.safety` line 0 carries level · source ·
      date and no base sits in an avoid area; the yellow-fever audit covered transit;
      the hazard gate exists when the window hits a season; the travel-clinic row
      exists when the health page recommends anything (phase-1-brief.md exit criteria).
- [ ] The pre-departure re-check ladder (T-14 / T-7 / T-3 / T-1) closes the
      pre-departure part of the checklist and shipped as the gates `.ics`.
- [ ] A trip of seven days or more carries the on-trip re-audit rows (`D+N · <date>`,
      one every 3-4 days of travel, each note naming what it covers —
      output-template.md §On-trip re-audit rows).
- [ ] `trip.kml` shipped (the gates `.ics` is covered by the ladder line above — every
      plan has gates now).
- [ ] The chat summary carries the route one-liner, total budget and the 3 biggest
      decisions made for the user.
