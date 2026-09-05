---
name: trip-planner
description: >-
  End-to-end international trip planning: turns "I want to go to X for N days" into a
  verified, bookable plan — route skeleton across cities, flight price scans
  (international + domestic legs), train-vs-fly decisions, hour-by-hour daily
  timelines with opening hours, dwell times, holiday collisions and tappable
  turn-by-turn map links (小时级行程+地图导航+离线KML), hotel shortlists by
  neighborhood, budget rollup, and a booking checklist with deep links. Use this
  whenever the user asks to plan a trip, vacation, itinerary or honeymoon, compare
  flight dates/prices, pick between cities or routes, schedule a travel day hour by
  hour, fill a spare block of time ("I'm near X with 2 free hours"), turn a finished
  plan into a designed page (eight themed renders: illustrated / clay / noir / glass /
  journal / zine / splash / portal — 插画/黏土/夜航/玻璃/手账/Zine/闪屏/穿越版), or asks
  旅行规划/行程安排/机票比价/去某国玩N天怎么安排/现在有空档干嘛/把行程做成好看的网页 — even if they only
  mention one piece (just flights, just hotels, or just navigation), the playbook and
  verification rules here still apply.
---

# Trip Planner

Turn a fuzzy trip idea into a plan the user can book link-by-link. The deliverable is
**verified and bookable**, not inspirational: every price and opening time carries a
source + as-of date, or an explicit "verify at link" flag. AI travel tools fail on stale
data, not on prose — fixing exactly that is this skill's job, so verification IS the work.

## Hard rules

1. **Never book, pay, hold, or enter personal data anywhere.** Produce deep links and a
   checklist; the human books. This is what keeps the skill safe to run autonomously.
2. **Prices and hours come from tools, never from memory.** Model memory is fine for
   geography and "what's worth seeing"; anything bookable or closable gets checked.
   A missing price is written "—, check link", never guessed.
3. **Cheap before expensive**: bundled script + keyless APIs first (see
   references/data-sources.md), browser automation second and only for what scripts
   can't get (OTA hotel prices, LCC fares, odd venues). Never curl OTA/airline sites —
   they bot-block instantly; browser pane only. Pace requests like one polite human.
4. **Search budgets are real**: ~25 web searches for your own orchestration work
   (visa, flights, holidays, hotels, assembly) — separate from, not inclusive of, the
   ≤8 written into each parallel city subagent's prompt. Unbounded research agents
   hang and burn money, so the cap goes in the prompt every time. Budget exhausted →
   ship with the least-verified items flagged rather than digging further.
5. Reply in the language the user asked in. Report money in the user's home currency
   (infer from origin), stating the FX rate + date used once. FX source:
   frankfurter.dev first — but it only carries ~30 major currencies, and **closed or
   minor ones (MAD / VND / EGP …) are not "unsupported", they are silently dropped
   from a 200 response** (`symbols=VND,USD` comes back with USD alone). For those use
   `https://open.er-api.com/v6/latest/<BASE>` and **check the returned object has the
   key you asked for**; the plan states which source it used (data-sources.md §FX).
6. Track the phases as todos (whatever task/todo tool the harness has; none → a
   short checklist at the top of your working notes) so a long plan survives
   interruptions and stays visible.

## Interaction contract

Three moments at most, usually two: (0) **one intake message, only if a core fact is
missing and can't be inferred** (Phase 0 — most requests need none); (a) after Phase 2 —
present 2-3 route skeletons, get a pick; (b) final delivery. Everything else runs without
questions. If the user says "一次到位 / don't ask, just plan" or the session is clearly
headless, skip (0) and (a): assume, pick the best skeleton yourself and state every
assumption prominently at the top of the output.

## Quick modes (no full pipeline)

- **Gap filler** — "I'm near X with 2 free hours": offer 2-3 options within a 15-min
  radius, one per energy level (a sight / food / a sit-down), each with walk time, a
  map link, a turn-back deadline, and — the one thing worth a search — confirmation
  that it is open right now. ≤3 searches; answer in minutes, not a report.
- **Single day** — "we have one day in Rome, what do we do?": run Phase 1's holiday +
  festival check, Phase 4 for that one day, and the Phase 6 self-check. Skip route
  skeletons, flights and hotels entirely; read scheduling.md and navigation.md and
  leave the rest closed. This is the most common request that is not a whole trip.
- **Live replan** — "missed the train / it's pouring": rebuild only the affected day
  from its degradation tags (`[skippable]`/`[swap→…]`/late_cut line) instead of
  re-planning the trip. `[pinned]` blocks hold; `[opener]` may move but costs a queue;
  re-verify only the hops that changed.

## Phase 0 — Intake (one message, or none)

**Read `references/phase-0-intake.md` now, before you decide whether to ask the user
anything** — it is the whole procedure for this phase (what counts as a core fact, how
origin is inferred, the intake message format and its rules, what goes into `prefs`,
the picture-capability check, the style line and the plan language, the exit
criteria). This section is only the contract; do not compose an intake message from
memory of the format.

Inputs: the user's request and anything said earlier. Outputs: the plan's top-level
`prefs` block and `lang`, `prefs.pictures` (native | key | stock), the assumptions block
for checkpoint (a) — and at most one intake message.

Gates — these decide pass/fail and do not move into the reference file:
- **One message, or none.** Ask only when a core fact (origin · destination · when /
  how long · page style) is missing **and** cannot be inferred; ask for everything in
  ONE message in the intake format (core first, optional after, each optional line
  with its default, one "all defaults" line); anything the user already stated is settled and
  never re-asked; never a follow-up "just one more thing".
- **Origin is inferred and stated, not asked** — from the conversation language, the
  locale / timezone or earlier messages, as that city's own international airport — or,
  when only a language / locale is known, that country's largest international gateway
  (phase-0-intake.md lists the common hubs; São Paulo is GRU, not GIG) — unless it is
  genuinely unguessable, which makes it the one core question.
- **The picture-capability check runs silently before styles are mentioned**; never
  ask for a key in chat, never read, print or copy `themes/.auth_header`; with no
  generator the page still ships in a theme on the stock kit (illustrated or clay only;
  the other six need generated pictures — offer illustrated) — a plain text page is
  never the deliverable.
- **`lang` follows the language the user asked in** — it drives the page chrome only
  (`--lang` overrides); every content string in the plan is written in the user's
  language too.

## Phase 1 — Country brief (once per destination)

**Read `references/phase-1-brief.md` now, before any fact about the destination is
written** — it is the whole procedure for this phase (where each fact comes from; the
visa / holiday / event / weather / money / insurance / safety lines; the advisory line,
the emergency card, the health line with the yellow-fever audit, the hazard line; the
exit criteria). This section is only the contract; never answer a Phase 1 fact from
memory of the procedure or of the country. In chat, Phase 1 is ≤ 10 lines — the
`brief` cards themselves follow output-template.md §Brief templates.

Inputs: destination(s), dates, the traveller's passport and origin, the skeleton
candidates. Outputs: the `brief` cards in canonical order, the Phase 1 checklist rows
(visa lead time · travel-clinic consult · yellow-fever vaccine + ICVP · insurance ·
hazard gate · copies + registration), and the facts later phases inherit.

Gates — these decide pass/fail and do not move into the reference file:
- **Every Phase 1 fact is the assembler's alone** — visa / entry, advisory, health,
  hazard, insurance: city agents never decide them, and anything they say is
  overwritten.
- **Official sources only, never memory** — government, embassy and foreign-ministry
  pages, CDC / TravelHealthPro / WHO, the insurer's schedule — each line stamped
  source + as-of; nothing found → "n/a — see advisory", not a guess. The plan never
  doses or prescribes: it writes the travel-clinic consult date and the agenda.
- **The advisory level drives the plan**: a base, leg or day trip in a "do not travel"
  / Level 4 / 暂勿前往 area stops the pipeline and asks the user; Level 3 / "avoid all
  but essential" / 谨慎前往 goes to the user with the line in front of them; regional
  "avoid" areas are checked base by base, leg by leg.
- **Transit counts**: the visa audit and the yellow-fever certificate audit both run
  over every transit airport before "no visa needed" is written anywhere — and the
  yellow-fever audit starts from the departure country, not the passport.
- **A hazard-season hit means a gate**: season card, hazard gate on the checklist and
  in the `.ics`, insurance deadline NOW, exposed bookings kept refundable.
- **User-named events are verified before anything else is planned.**

## Phase 2 — Route skeleton → checkpoint (a)

1. Longlist cities/areas scored against the user's ranked interests and
   `prefs.scenery` (nature / city / beach / forest / lake / mountain); shortlist by
   geography — order as a line or loop, never a star with backtracking. `prefs.travel_style`
   shapes the legs: self-drive → a rental leg and park/countryside bases (Phase 3
   §Driving legs); group tour → the tour's own schedule is the spine (Phase 4).
2. Nights allocation: ≥2 nights per base (each 1-night stay burns a half day on packing
   and transit); prefer "base + day-trips" over hotel-hopping when the day-trip is
   <90 min each way. 10-15 days ≈ 8-13 usable days ≈ 2-4 bases, and 2-3 beats 4.
3. Day-count honesty: landing before 15:00 = half a sightseeing day, later = zero
   sightseeing days for the count — the evening still gets one free, walkable,
   unticketed block near the hotel (scheduling.md §Arrival day); departure day = zero
   unless the flight leaves after 18:00.
4. Decide **open-jaw now** (fly into the first base, out of the last) — on multi-city
   routes it usually beats round-trip because it refunds a backtracking day. Check both
   jaw directions in Phase 3; prices are asymmetric.
5. Present 2-3 skeletons (e.g. classic / nature-lean / relaxed): city order, nights per
   base, intercity legs with rough mode + duration, one-line pace verdict. Recommend one.

## Phase 3 — Flights & intercity legs

**Read `references/phase-3-legs.md` now, before the first flight scan** — it is the
whole procedure for this phase (the plan shape, the international price-source ladder,
multi-airport and LCC arithmetic, the separate-tickets audit, intercity rail vs fly,
driving legs, what every leg row records, the exit criteria). This section is only the
contract; do not price a leg from memory of the procedure.

Inputs: the chosen skeleton (Phase 2), `prefs.travel_style`, the Phase 1 visa / entry
facts (transit countries included). Outputs: `legs[]` — one pick + one backup per leg —
the checklist rows for flights, date-locked rail and rentals, their budget rows, and the
baggage walkthrough for multi-leg trips.

Gates — these decide pass/fail and do not move into the reference file:
- **`assets/plan.example.json` is the single source of truth for the plan's shape** —
  open it before writing a field; a wrong shape does not fail loudly — the renderers
  WARN and print an empty section.
- **Every international pick and backup is priced in ≥ 2 sources** (flight_scan /
  Google + Skyscanner / Kayak / Trip.com / the carrier's site); `legs.note` names them
  with the as-of date; a > 10 % disagreement prints as a band; no browser pane → Google
  alone and the note says so. "Price unverified" only when every source fails.
- **Separate tickets across a foreign hub are a visa trap**: the audit runs before "no
  visa needed" is written anywhere — including tickets the user already holds.
- **Rail wins under ~5 h station-to-station; price on the operator's site.** A park
  without a car is decided with the user, never by default.
- **Every leg row carries price + currency + as-of, the checked-bag fee, the refund /
  change class and a deep link**; one pick + one backup per leg.

## Phase 4 — City day-plans

**Read `references/phase-4-days.md` now, before any city is planned or any city agent
is launched** — it is the whole procedure for this phase (the city-agent contract, the
six per-city steps, the route_tools order, the `sun` / `check` rules, and the exit
criteria). This section is only the contract; do not plan a city from memory of the
procedure, and build every city-agent prompt from that file's §City-agent contract
(paste its lines, or pass the file's absolute path — the agent never sees SKILL.md).

Inputs: the chosen skeleton (Phase 2), the legs table (Phase 3), the Phase 1 brief
facts and `prefs`. Outputs: per city, plan-JSON day objects insertable verbatim into
`days[]` (output-template.md §city-block) — `stops`, hour-level `timeline`,
`hop_links`, `sun`, `rain_alt`, `ribbon` — plus the city's `checklist_items`.

Gates — these decide pass/fail and do not move into the reference file:
- **City agents never make visa / entry / health / advisory / hazard / insurance
  calls.** Those
  facts are the assembler's Phase 1 job and override anything a city block says; a
  city agent's prompt carries **search budget ≤ 8**, an explicit **"do not run
  geocoding"** line, the plan language, the §city-block return format, and the
  visa / entry hard rule as its last line.
- **Hour-level timelines are the default deliverable**; day-level only when the user
  asks for a rough cut.
- **`route_tools.py check` exits 0 before rendering** — a BROKEN or SUSPICIOUS hop is
  fixed in the plan, never explained away in prose. A SUSPICIOUS hop has exactly two
  fixes: a vehicle really runs it (fly / drive / boat / train / bus) → declare that
  `mode` on the arriving stop and give it its `legs[]` row (add the row if the leg has
  none); nothing runs it (a 250 km hop inside one city is a mis-geocoded stop) → fix
  the stop, never the `mode`.
- **`sun --write` runs before any sunrise / golden-hour / dark-start prose**, after
  the stops carry coordinates; a plan that crosses timezones stamps every day's `tz`
  first.
- Every day has its rain alternative, its food area and its `ribbon`; anchors are
  chosen per interest-fit, ≤ pace + 1 optional per day.

## Phase 5 — Hotels

Per base: pick 1-2 neighborhoods with reasons (near the rail hub actually used, safe
after dark, luggage-friendly), in the lodging type and band from `prefs.lodging`
(default mid-range hotel; a ryokan/onsen or B&B habit changes which properties you list). Browser spot-check Google Hotels/Booking with the real
dates for a price band, then list 2-3 concrete properties: name, area, band per night,
deep link with dates baked in (recipes in data-sources.md). Advise: book refundable
now, re-shop 2-3 weeks out.

## Phase 6 — Assemble, self-check, deliver

**Read `references/phase-6-assemble.md` now, before the final `plan.geo.json` is
written** — it is the whole procedure for this phase (assembly order, cover title, the
adversarial self-check list, delivery, the themed-render flow incl. stock mode, and the
exit criteria). This section is only the contract; do not assemble or render from memory
of the procedure.

Inputs: `plan.geo.json` assembled per references/output-template.md — the single
editable source — plus Phase 0's `prefs.theme` / `prefs.pictures` / `plan.lang`.
Outputs — three things every time, handed over through the harness's artifact / file
tool: (1) the **chat summary** — route one-liner, total budget, the 3 biggest decisions
made for the user, and in stock mode the picture notice; (2) `trip-<theme>.html`;
(3) `trip.kml` — plus the gates `.ics`, always: the pre-departure ladder rows are
date-locked gates (output-template.md §Pre-departure re-check ladder).

Gates — these decide pass/fail and do not move into the reference file:
- **The deliverable is a themed page, never a plain text one.** The plain
  `render_plan.py` page is an extra: on request for a printable version, or as the last
  resort after one honest fix attempt of the theme renderer — and then the summary says so.
- **The adversarial self-check runs in full before delivery**, fixes what it catches,
  and is recorded as "self-checked: N issues found and fixed" in `meta.self_check` and
  the last `decisions[]` row. The list lives in the reference file; a skipped item is
  a defect, not a shortcut.
- **Acceptance bars are exit codes and eyes, not prose**: `route_tools check` and
  `scripts/plan_lint.py --strict` exit 0 before rendering (the only tolerated FAIL: a
  polar day's `sun`, PLN-11), `themes/qc.py` exits 0 after, and the export-probe PNG
  or the page in a browser was actually looked at — none available → say so in the
  summary.
- **`plan.geo.json` stays the single editable source**: a later "move day 3 to Nara"
  is a JSON edit plus geocode → check → links → kml → render, never a rewrite.
- **Cover title** comes from references/cover-titles.md — never a literal placeholder,
  never a blacklisted cliché.

## When things fail

- flight_scan.py errors twice (or cannot be installed — data-sources.md §Flights has
  the PEP 668 variants) → browser Google Flights; that blocked too → the second price
  source (Skyscanner / Kayak, data-sources.md §Flights → Second price source); only
  when every source fails do deep links go out marked "price unverified", keep moving.
  A harness with no browser pane is the one case a single source is acceptable — then
  `legs.note` says "single source — no browser"; a web search is never the rung after
  a failed scan while a browser exists.
- A venue's hours survive 2 searches unverified → schedule it flagged "confirm on
  arrival"; don't burn more budget.
- Anything still unverified at delivery gets a ⚠️ in the plan — visible honesty beats
  quiet confidence.

## Bundled resources

Paths below are relative to the skill root (the directory holding this SKILL.md) —
resolve it once and call the scripts by absolute path, because a subagent's working
directory is not the skill directory and shell cwd does not persist between calls.

- `references/data-sources.md` — read before Phase 1: every API/URL recipe + fallback
  chain (flights, hotels, rail, venues, weather, FX, holidays, geocoding) — **plus
  the booking-judgment rules that decide plans**: §Group tours (weekday grids,
  min-party, calendar-vs-marketing, zero-cost holds and booking order) and §Hotels
  (checkout all-in pricing). Not just a curl cookbook.
- `references/country-quick-notes.md` — read the destination's section before Phase 2:
  passes, sell-outs, closure patterns, transit apps per country; destination absent →
  its "Destination not listed? — the checklist" section.
- `references/output-template.md` — read before Phase 4 fan-out (city-block format)
  and Phase 6 (deliverable structure).
- `references/scheduling.md` — read before building any hour-level timeline: dwell
  times, buffers, meals, energy curve, degradation tags, timeline verification.
- `references/navigation.md` — read with it: hop-link recipes, transit-row format,
  exit numbers, verify-vs-estimate policy, offline-maps (KML) workflow.
- `references/cover-titles.md` — bilingual poetic cover-title case library (poetry /
  prose / classic-literature sources + trip-archetype fit + cliché blacklist); read
  at Phase 6 when rendering.
- `references/phase-0-intake.md` — read at the start of Phase 0, before deciding whether
  to ask anything: core vs optional facts and their defaults, origin inference, the
  intake message format and rules (zh sample inline, en in output-template.md), the
  `prefs` block, the picture-capability check (native | key | stock), the style line and
  plan language, and the exit criteria. SKILL.md Phase 0 is only the contract; this
  file is the procedure.
- `references/phase-1-brief.md` — read at the start of Phase 1, before any destination
  fact is written: where each fact comes from, the visa / holiday / event / weather /
  money / insurance / safety lines, the advisory line (level → plan behaviour), the
  emergency card, the health line with the yellow-fever audit, the hazard line (season
  card + hazard gate), and the exit criteria. SKILL.md Phase 1 is only the contract;
  this file is the procedure.
- `references/phase-3-legs.md` — read at the start of Phase 3, before the first flight
  scan: the plan shape and its two traps, the international price-source ladder and the
  ≥ 2-sources rule, multi-airport and LCC arithmetic, the separate-tickets visa audit,
  intercity rail vs fly, driving legs, the fields every leg row records, the baggage
  walkthrough, and the exit criteria. SKILL.md Phase 3 is only the contract; this file
  is the procedure.
- `references/phase-4-days.md` — read at the start of Phase 4, before any city is
  planned: the city-agent contract (what every fan-out prompt must carry), the six
  per-city steps, the route_tools order (geocode → tz → sun → links → check → kml),
  the `sun` / `check` acceptance rules, and the exit criteria. SKILL.md Phase 4 is
  only the contract; this file is the procedure.
- `references/phase-6-assemble.md` — read at the start of Phase 6, before the final
  plan is written: assembly order, cover title, the full adversarial self-check list,
  delivery (themed page + KML + gates .ics), the themed-render flow incl. stock mode,
  the qc / export-probe acceptance bars, and the exit criteria. SKILL.md Phase 6 is
  only the contract; this file is the procedure.
- `scripts/flight_scan.py` — Google Flights grid scanner; run with `--help` first.
- `scripts/route_tools.py` — geocode stops, distance-check clustering, emit per-hop +
  whole-day map links and the trip KML; subcommands geocode / check / links / kml /
  ics (the gates `.ics` from the checklist's dated rows — `-o gates.ics`, bump
  `--sequence` on every plan change) /
  sun (civil dawn + sunrise/sunset per day from sunrise-sunset.org, sanity-checked,
  written into `days[].sun` in the canonical format; point = first stop, last stop
  on a moving day, or the day's `sun_stop` when set; non-zero exit = a day was
  skipped/rejected).
- `scripts/render_plan.py` — turn the plan JSON into the final self-contained HTML.
  It reads the same file route_tools does, so write the plan once and render often.
- `scripts/plan_lint.py` — the plan's **content** gate, run with `--strict` before any
  renderer (exit = FAIL count, like qc.py): brief present, non-empty and in canonical
  order; no placeholder / "awaiting" text; no markdown headings in cells; the
  self-check line in `meta.self_check`; art placeholders filled and `prefs.pictures`
  matching how the art was made; the gates `.ics` and `trip.kml` beside the plan;
  under `--strict` every day has at least one stop and a `sun` written by `sun --write`.
  `check` proves the geography and `qc.py` the HTML — this proves the words.
- `assets/plan.example.json` — runnable schema example **and the single source of
  truth for the plan's top-level keys** (`prefs`/`budget`/`legs`/`checklist`/`hotels`/
  `brief`/`days[]`… shapes; output-template.md §Top-level plan skeleton mirrors it):
  copy it, replace the placeholders, and both scripts work on it immediately.
- `references/themes.md` — the themed-render manual: what each of the eight themes
  is, its art fields and known limits, how to add a theme, the recurring-defect
  checklist and the verification discipline. Read before rendering any theme.
- `themes/` — the themed renderers (`render_journal.py`, `render_noir2.py`,
  `render_theme2.py` = illustrated, `render_clay2.py`, `render_glass2.py`,
  `render_zine.py`, `render_splash.py`, `render_portal.py`, `render_picker.py`)
  plus `theme_common.py`, `qc.py` (static QC, exit code = FAIL count),
  `xprobe.sh` / `xt.sh` (headless export probes), `towebp.py` / `gen.py` /
  `split_sheet.py` / `cutout.py` (asset pipeline), `ART-SCHEMA.md` (the one
  authoritative art.json contract) and `themes/README.md`.
- `themes/assets/` — the shared picture library: all embeddable webp, the Caveat
  webfont, `manifest.json` (prompt/cost per generated asset), `IMAGE-LIBRARY.md`
  (index by subject — check its Generic pieces section before generating anything),
  `portal/` (the portal theme's footage sidecar dir — empty in the tree; the US
  reference chain is a release asset, see `portal/README.md`) and `stock/` — the **stock kit**
  (region cover paintings + landmark / generic-scene cut-outs in the illustrated
  style, `stock/index.json` + `stock/README.md`) that `themes/stock_art.py` uses to
  build an art file when the session has no image generator and no key.
- `themes/stock_art.py` — `plan.geo.json --theme illustrated|clay [--lang zh|en]
  [--country ISO2] [--index PATH] [--force] -o plan.art.json`: fills the picture slots
  from the stock kit + shared library (country match, day keyword match, generic
  props); you write the words; render with `--assets themes/assets/stock`. Stock mode
  only (Phase 0).
