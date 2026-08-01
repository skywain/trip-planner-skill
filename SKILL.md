---
name: travel-planner
description: >-
  End-to-end international trip planning: turns "I want to go to X for N days" into a
  verified, bookable plan — route skeleton across cities, flight price scans
  (international + domestic legs), train-vs-fly decisions, hour-by-hour daily
  timelines with opening hours, dwell times, holiday collisions and tappable
  turn-by-turn map links (小时级行程+地图导航+离线KML), hotel shortlists by
  neighborhood, budget rollup, and a booking checklist with deep links. Use this
  whenever the user asks to plan a trip, vacation, itinerary or honeymoon, compare
  flight dates/prices, pick between cities or routes, schedule a travel day hour by
  hour, fill a spare block of time ("I'm near X with 2 free hours"), or asks
  旅行规划/行程安排/机票比价/去某国玩N天怎么安排/现在有空档干嘛 — even if they only
  mention one piece (just flights, just hotels, or just navigation), the playbook and
  verification rules here still apply.
---

# Travel Planner

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
   (infer from origin), stating the FX rate + date used once (source: frankfurter.dev).
6. Track the phases as todos so a long plan survives interruptions and stays visible.

## Interaction contract

Two checkpoints, no more: (a) after Phase 2 — present 2-3 route skeletons, get a pick;
(b) final delivery. Everything else runs without questions. If the user says "一次到位 /
don't ask, just plan" or the session is clearly headless, skip (a): pick the best
skeleton yourself and state that assumption prominently at the top of the output.

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

## Phase 0 — Intake

Ask once, in one message, only for what's missing; assume and clearly state defaults
for the rest (mid budget, pace 3 anchors/day, ±2 days flexibility, no kids):
origin airport/city · destination country or shortlist · date window + flexibility ·
nights (a range like 10-15 is fine) · party size & mobility · budget style or number ·
interests ranked (food/history/nature/anime/hiking/shopping/photography/nightlife) ·
pace (2/3/4 anchors per day) · passport nationality (visa!) · locked must-sees, if any.

## Phase 1 — Country brief (once per destination, ≤10 lines of output)

- **Visa/entry** for that passport: official government/embassy sources only; put the
  processing lead time on the booking checklist. Rules change — never answer from memory.
- **Holidays colliding with the window**:
  `curl -s "https://date.nager.at/api/v3/PublicHolidays/{year}/{ISO2}"` (keyless ✓).
  A national holiday means closures + crowds + hotel spikes — annotate affected days.
- **What the holiday API can't see** — one budgeted search per city
  (`{city} festival OR events {month} {year}`) plus, where relevant: seasonal
  operating windows for mountain/garden/boat anchors, per-venue annual maintenance
  shutdowns of headliners, and Ramadan dates in Muslim-majority destinations (daytime
  food logistics, shifted hours, packed evenings). A local festival closes streets and
  triples hotel rates while every holiday feed says the day is ordinary.
- **User-named events get verified before anything else is planned.** A match,
  concert or festival in the request is the hardest pin in the whole trip — confirm
  team/venue/city, date, local kickoff time and ticket on-sale status FIRST, because
  the skeleton hangs off it ("Columbus vs Miami" is a home game in Ohio, and a route
  built around the wrong coast is a 13-day bug). US listings put the home side first
  in "A vs B" — but verify, never parse. Kickoff times can move for TV ⚡: re-check
  close to travel.
- **Weather for those dates**: Open-Meteo recipes in data-sources.md (first call can
  take ~10 s). One line: temps, rain odds, daylight.
- **Money & connectivity one-liners**: card vs cash norms, eSIM ballpark, plug type.

## Phase 2 — Route skeleton → checkpoint (a)

1. Longlist cities/areas scored against the user's ranked interests; shortlist by
   geography — order as a line or loop, never a star with backtracking.
2. Nights allocation: ≥2 nights per base (each 1-night stay burns a half day on packing
   and transit); prefer "base + day-trips" over hotel-hopping when the day-trip is
   <90 min each way. 10-15 days ≈ 8-13 usable days ≈ 2-4 bases, and 2-3 beats 4.
3. Day-count honesty: landing before 15:00 = half a sightseeing day, later = zero;
   departure day = zero unless the flight leaves after 18:00.
4. Decide **open-jaw now** (fly into the first base, out of the last) — on multi-city
   routes it usually beats round-trip because it refunds a backtracking day. Check both
   jaw directions in Phase 3; prices are asymmetric.
5. Present 2-3 skeletons (e.g. classic / nature-lean / relaxed): city order, nights per
   base, intercity legs with rough mode + duration, one-line pace verdict. Recommend one.

## Phase 3 — Flights & intercity legs

**International:**
- Run `scripts/flight_scan.py` (Google Flights data, keyless; `--help` for usage) to
  grid-scan the date window and both open-jaw directions. Fails twice → browser on
  Google Flights (URL recipes in data-sources.md). Google unreachable (some CN
  networks) → Trip.com/携程 in the browser.
- Multi-airport cities: compare fare + ground transfer cost + time (HND vs NRT,
  LHR vs LGW/STN…). A ¥400-cheaper fare into a far airport often loses.
- Departing CN: also spot-check one LCC directly in the browser (Spring 春秋, Peach,
  Scoot…) — aggregators miss or misprice some LCC inventory.
- LCC arithmetic: add the checked-bag fee before comparing — a "cheap" fare + ¥280 bag
  usually isn't.

**Intercity within the destination:**
- Mode rule: rail wins under ~5 h station-to-station (city-center to city-center, no
  airport buffers); fly beyond that or across water; overnight options only for
  shoestring budgets.
- Price on the **operator's** site — resellers add fees. Country-quick-notes.md lists
  the operators and their booking-window rules (high-speed fares rise as buckets sell).

**Driving legs (parks and car-first destinations):**
- A national park without a car is a bus-tour compromise — decide that explicitly with
  the user, never by default. A rental is its own leg: pick-up/drop-off at airports,
  one-way drop fees noted, and the airport↔park drive budgeted honestly (Bozeman→Old
  Faithful ≈ 2.5 h, Fresno→Yosemite Valley ≈ 2.5 h — the map's "nearby airport" is
  half a day of driving).
- Record per driving leg: pick-up/drop point + counter hours, car class, price +
  as-of date, insurance note, fuel estimate, park entrance fee (per **vehicle** in the
  US; 3+ parks → the annual pass wins), and the license requirement for the driver's
  passport (see country notes).
- Gateway towns run out of cars and rooms in season — the rental and the first night
  go on the booking checklist, not the "later" pile.

**Record for every leg**: carrier, date, dep/arr local times, price + currency + as-of
date, bag included?, refund/change class, deep link. Output 1 pick + 1 backup per leg.

## Phase 4 — City day-plans

When ≥3 cities and subagents are available, fan out one agent per city; each prompt
must include: the dates, the user's interests + pace, **search budget ≤8**, an
explicit **"do not run geocoding"** line (parallel agents would break Nominatim's
1 req/s policy — the assembler geocodes once, centrally), and the exact return
format from references/output-template.md §city-block — **plan-JSON day objects,
insertable verbatim**, not a summary. Otherwise do the cities sequentially with the
same structure. When the user prefers group tours, the city agent's first job is
finding real in-sale products with departure schedules (data-sources.md §Group
tours) — the tour's schedule then dictates the surrounding legs.

Per city:
1. Anchors per interest-fit, ≤ pace + 1 optional per day. Cluster by geography per day;
   order clusters so the route never criss-crosses town.
2. **Verify every anchor**: open days + hours, last-entry time, price, and sell-out
   pressure (official site beats blogs; treat blog data >12 months old as stale).
   Sells out → booking checklist with lead time (Ghibli, teamLab, Uffizi, Alhambra,
   Sagrada Família… see country-quick-notes.md). For dates more than ~3 months out
   nobody publishes that day's hours yet, so verify the **seasonal pattern + closure
   rule**, stamp it "pattern as of {date}", and put "re-confirm hours 2 weeks before
   travel" on the checklist. Claiming date-specific verification you cannot have is
   worse than admitting the horizon — and prices move on their own schedule
   (admission fees jump at fiscal-year boundaries), so re-check the fee, not just
   the hours.
3. Transit: day-pass vs pay-per-ride arithmetic — sum the day's expected rides and
   recommend the pass only when it actually wins. Note the local IC card / transit app.
4. Each day gets one rain alternative and a food **area** (market/street/neighborhood)
   near the evening cluster — named restaurants only on request; they churn too fast.
5. Timing realism: transit between clusters from Google Maps (browser) or mark the
   estimate unverified; hard stop = last entry, and nothing scheduled after it.
6. **Timeline assembly — hour-level is the default deliverable.** Read
   references/scheduling.md (dwell times, tiered ticket margins, buffer policy,
   arrival/moving/departure day structures, worship + siesta + crowd-calendar traps,
   degradation tags) and references/navigation.md (hop links, canonical hop-row
   format, exit numbers, verify-vs-estimate rules), then run scripts/route_tools.py
   in this order: **geocode → check → links --write → kml**, so every hop carries a
   distance-sane duration and a tappable map link written into the plan for you.
   (Sunrise/sunset is a city-level fact — fetch it back in Phase 1 with the holidays
   and FX; it does not need stop coordinates.) Mark ridden hops `"mode": "transit"`
   on the arriving stop, or the walking total and the links will both be wrong.
   Transit durations come back as ranges — keep them ranges unless you
   browser-verified the hop. Deliver day-level granularity only if the user asks for
   a rough cut.

## Phase 5 — Hotels

Per base: pick 1-2 neighborhoods with reasons (near the rail hub actually used, safe
after dark, luggage-friendly). Browser spot-check Google Hotels/Booking with the real
dates for a price band, then list 2-3 concrete properties: name, area, band per night,
deep link with dates baked in (recipes in data-sources.md). Advise: book refundable
now, re-shop 2-3 weeks out.

## Phase 6 — Assemble, self-check, deliver

Assemble per references/output-template.md: overview → decisions made for the user →
booking checklist → flights/intercity table → day-by-day cards → hotels → budget
rollup → country brief.

**Adversarial self-check** — run this list against the finished plan, fix what it
catches, then append "self-checked: N issues found and fixed":
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
  rail connections ≥ 30 min
- Last-entry time vs planned arrival for each anchor
- Timeline checks from scheduling.md §verification: chain arithmetic (block start ≥
  prev end + hop + buffer), day walking totals ≤ 8 km, late hops vs last departures,
  golden-hour blocks vs actual sunset
- Red-eye / timezone day-number arithmetic
- No day exceeds pace; no day mixes an intercity move with >2 anchors
- Every price has source + as-of date; every bookable line has a link

**Deliver**: a chat summary (route one-liner, total budget, the 3 biggest decisions
made for the user) + the full plan rendered by `scripts/render_plan.py plan.geo.json
-o trip.html` — one self-contained, printable, phone-friendly file with a checkbox
booking checklist and an offline route sketch per day. Publish via Artifact when
available, else SendUserFile, else save and give the path. Ship the trip KML
(`scripts/route_tools.py kml plan.geo.json -o trip.kml`) alongside for offline map
apps. **`plan.geo.json` is the single editable source** for all of it — every command
above reads that one file — so a later "move day 3 to Nara" is a JSON edit plus
geocode → check → links → kml → render, not a rewrite.

## When things fail

- flight_scan.py errors twice → browser; browser blocked → deep links marked "price
  unverified", keep moving.
- A venue's hours survive 2 searches unverified → schedule it flagged "confirm on
  arrival"; don't burn more budget.
- Anything still unverified at delivery gets a ⚠️ in the plan — visible honesty beats
  quiet confidence.

## Bundled resources

Paths below are relative to the skill root (the directory holding this SKILL.md) —
resolve it once and call the scripts by absolute path, because a subagent's working
directory is not the skill directory and shell cwd does not persist between calls.

- `references/data-sources.md` — read before Phase 1: every API/URL recipe + fallback
  chain (flights, hotels, rail, venues, weather, FX, holidays, geocoding).
- `references/country-quick-notes.md` — read the destination's section before Phase 2:
  passes, sell-outs, closure patterns, transit apps per country.
- `references/output-template.md` — read before Phase 4 fan-out (city-block format)
  and Phase 6 (deliverable structure).
- `references/scheduling.md` — read before building any hour-level timeline: dwell
  times, buffers, meals, energy curve, degradation tags, timeline verification.
- `references/navigation.md` — read with it: hop-link recipes, transit-row format,
  exit numbers, verify-vs-estimate policy, offline-maps (KML) workflow.
- `scripts/flight_scan.py` — Google Flights grid scanner; run with `--help` first.
- `scripts/route_tools.py` — geocode stops, distance-check clustering, emit per-hop +
  whole-day map links and the trip KML; subcommands geocode / check / links / kml.
- `scripts/render_plan.py` — turn the plan JSON into the final self-contained HTML.
  It reads the same file route_tools does, so write the plan once and render often.
- `assets/plan.example.json` — runnable schema example: copy it, replace the
  placeholders, and both scripts work on it immediately.
