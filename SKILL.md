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

**Read the request before deciding whether to ask anything.** Most requests already carry
what matters — "帮我安排今年 10.1 到 10.7 的德国之旅" has the destination and the dates,
and gets **zero questions**: infer the rest, list the assumptions in one block at the top
of checkpoint (a), and move. Ask only when a *core* fact is missing **and** cannot be
inferred — and then ask for everything in ONE message in the **intake format** below:
core first, optional after, **only the items the user has not already answered**
(anything stated in the request — destination, dates, party, "自驾", a style name, a
budget — is settled and must not reappear as a question), each optional line with its
default, one "all defaults" escape hatch.

**Core** — must be known or defensibly assumed:
- **Origin** (city/airport). Missing → infer from the conversation language, the user's
  locale/timezone or anything said earlier, pick that country's main international hub and
  state it as an assumption; it costs one line to fix at checkpoint (a) and a whole round
  trip to ask. Genuinely unguessable → it is the one core question.
- **Destination** (country, city or a shortlist). Missing → ask; nothing to plan without it.
- **When / how long** (dates, or a duration + rough month + flexibility). Missing → ask.
- **Page style** — one of the eight themes (Phase 6). Default: **illustrated 插画版**.
  Before you mention styles at all, run the **picture-capability check** below — its
  result decides what you say about pictures.

**Optional** — ask them in the same message only when you are already asking; never
send a message just for these. Unanswered → default, and the assumptions block says so:
- travel style: self-drive · group tour · public transport + walking (default: public
  transport, or self-drive where the destination is car-first — Phase 3 §Driving legs)
- lodging habit: hotel · hostel · B&B / guesthouse · apartment · ryokan/onsen-style
  stays, and the band (default: mid-range hotel, refundable)
- scenery taste: scenery/nature · city · beach · forest · lake · mountain (default: read
  from the destination + interests)
- party size & mobility (default: 2 adults, no kids) · budget style or number (mid) ·
  interests ranked (food/history/nature/anime/hiking/shopping/photography/nightlife) ·
  pace 2/3/4 anchors per day (3) · ±day flexibility (±2) · passport nationality
  (visa! infer from origin, state it) · locked must-sees.

**Intake format** (user's language; markdown; full zh/en samples in
references/output-template.md §Intake message). Keep it to one screen:

```
**先确认几件事 —— 一条消息回我,写序号+答案;没写的按默认**

**必答**
1. 出发城市 —— 我猜是上海(你用中文问的),对吗?
2. 玩多久、大概什么时候 —— 例:10.1–10.7,或「7 天 · 10 月 · 前后可挪 2 天」

**选答(不答走默认)**
3. 页面风格:插画(默认)· 黏土 · 夜航 · 玻璃 · 手账 · Zine · 闪屏 · 穿越 —— 样子见 https://skywain.github.io/trip-planner-skill/
4. 出行方式:公共交通+步行(默认)· 自驾 · 跟团
5. 住宿:中档酒店(默认)· 青旅 · 民宿 · 公寓 · 温泉旅馆
6. 偏好:城市 · 自然风光 · 海滩 · 森林 · 湖泊 · 山 —— 默认按目的地定
7. 人数 / 预算 / 节奏:默认 2 成人 · 中档 · 每天 3 个主要点

ℹ️ 本次会话没有生图能力,页面会用内置插画素材(仍是成品页,只是不如定制图贴合);有 OpenRouter key 的话放进 themes/.auth_header 再告诉我,就能为这趟生成。
💡 回「默认」= 全部按默认,直接开工。
```

Rules for the block: numbering runs continuously over whatever is left; a heading with
nothing under it is dropped; the ℹ️ line appears only in stock mode (Picture-capability
check below), the 💡 line only when at least one optional item is shown; a guessed core
value is asked as a confirmation ("我猜是 X,对吗?"), not as an open question; never
more than one message, never a follow-up "just one more thing". English sample:
output-template.md. The same facts, answered or defaulted, go into `prefs` next.

Write what you learned or assumed into the plan's top-level `prefs` block
(`assets/plan.example.json`: `theme`, `pictures`, `travel_style`, `lodging`, `scenery`,
`pace`, `budget`, and `notes` — the inferred values in one line, e.g. "assumed origin
PVG (zh request, no origin given)"; the assumptions block at checkpoint (a) is written
from it) so Phases 2-6 read one place and a later replan does not re-ask.

**Picture-capability check** — silent, once, before styles come up:
1. You have a **native image-generation tool** → bespoke art for this trip, nothing to
   configure (`prefs.pictures = "native"`).
2. Else `<skill>/themes/.auth_header` exists (`test -s`; never read, print or copy it) →
   `gen.py` over OpenRouter with the user's key (`"key"`).
3. Neither → **the page still ships in a theme** (Phase 6 — a plain text page is never
   the deliverable): the built-in **stock kit** (`themes/assets/stock/`) supplies the
   pictures (`"stock"`). Tell the user once — in the intake message if you are sending
   one, otherwise in the assumptions block at checkpoint (a): *"No image generator is
   available in this session, so the page will use the built-in stock illustrations —
   still a designed page, just less bespoke. If you have an OpenRouter key, put it in
   `themes/.auth_header` (one line: `Authorization: Bearer <key>`) and tell me; then I
   generate the art for this trip."* Never ask for a key in the chat, never handle one.
   Stock mode is complete for **illustrated** (default) and works for **clay** (built-in
   terrain kit); the other six themes need generated pictures — say so if the user asks
   for one, and offer illustrated instead.

Style, when you do ask, is one line: the eight names with the showcase link
(https://skywain.github.io/trip-planner-skill/; offline: render
`themes/render_picker.py`), "skip = illustrated". Set the plan's top-level `"lang"` (`zh` | `en`,
output-template.md §Plan language) from the language the user asked in — the rendered
pages' UI follows it; `--lang` overrides. `lang` covers the page chrome only: **every
content string you write into the plan — day titles, notes, tips, checklist rows,
decisions, hotel blurbs — is in the user's language too.** The research sources are
mostly English and will drag your prose toward English if you let them; a zh user
receiving an English page is a shipped bug, not a style choice (self-check row, Phase 6).

## Phase 1 — Country brief (once per destination; ≤10 lines in chat — the `brief` cards themselves follow output-template.md §Brief templates)

Read the destination's section of references/country-quick-notes.md first. **Destination
not in that file (Mexico, Morocco, Turkey and Vietnam all weren't)** → work through its
"Destination not listed? — the checklist" section instead of improvising: it is the
list of things every new country costs a first planner 6-9 searches to rediscover.

- **Visa/entry** for that passport: official government/embassy sources only; put the
  processing lead time on the booking checklist. Rules change — never answer from memory.
  Transit countries count too: a separate-ticket connection can force ENTERING the hub
  country to re-check bags (Phase 3 §International, the separate-tickets bullet) — run
  that audit here, before writing "no visa needed" anywhere.
  **This judgement is the assembler's alone**: city subagents (Phase 4) do not make
  visa/entry calls, and anything they say about it is overwritten by this line.
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
  take ~10 s). One line: temps, rain odds, daylight — stamped with its mode
  (forecast / 5-yr normals + climate model) and as-of date per data-sources.md
  §Weather; the Phase 6 exit criteria check the stamp.
- **Money & connectivity — fixed lines, not a vibe.** `brief.money` carries the five
  lines of output-template.md §Brief templates (refuse DCC · card FX fee → buffer ·
  ATM rule · cash number · which cards and wallets work) plus the **origin-conditional
  block** when it applies (mainland-China origin: UnionPay vs Visa/MC acceptance,
  Alipay+/WeChat coverage, foreign-cash pre-order); `brief.connectivity` carries the
  eSIM ballpark, plug type and the digital-safety line (home-number SMS 2FA reachable
  abroad, phone-theft plan, cloud + offline copies of passport / visa / policy).
  Recipes and thresholds: data-sources.md §FX → Money safety.
- **Insurance line**: travel-medical insurance with destination-appropriate coverage
  goes on the checklist (US target: ≥$100k medical + medical evacuation — an ER visit
  is four figures before insurance). Tours never substitute for it. When the plan
  carries a monitored hazard gate, the insurance row's deadline is NOW, not "before
  departure" (the user buys — Hard rule 1); the agent's jobs are the read-side ones:
  verify the issued policy rather than the product page, and match the plan's
  activities against the exclusion list by name — data-sources.md §Travel insurance.
- **Emergency & health lines** (`brief.emergency`, `brief.health`): police / ambulance
  numbers, the nearest mission's hotline and the vaccine / vector-borne / water lines
  come only from the traveller's own foreign-ministry advisory page and the insurer's
  assistance line — never from memory; nothing found → "n/a — see advisory" in the
  card, not silence (output-template.md §Brief templates).
- **Safety, written to the `brief.safety` template** (output-template.md §Brief
  templates — six named lines: the destination's named scams · pickpocket hotspots ·
  the taxi rule · the after-dark avoid list per base · what to do when it happens ·
  legal & customs red lines). More useful than warnings: design the plan so night
  movement is door-to-door by car — a route that never needs a dark walk beats a
  list of cautions. Sources: country-quick-notes.md (the destination's section, or
  the "Street safety" line of the not-listed checklist).

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

From here on you are writing `plan.geo.json`. **`assets/plan.example.json` is the single
source of truth for the plan's top-level shape** — `legs`, `checklist`, `budget`,
`hotels`, `brief`, `days[]`… — so open it (or output-template.md §Top-level plan
skeleton, copied from it) before writing a field. `budget` is a list of
`{cat, per_person, total, note}` rows, not `{note, rows}`; `legs` rows use
`from/to/dep/arr`. A wrong shape does not fail loudly: the renderers WARN and print an
empty section (they used to crash — the Vietnam test lost both themed pages to it).

**International:**
- Run `scripts/flight_scan.py` (Google Flights data, keyless; `--help` for usage) to
  grid-scan the date window and both open-jaw directions. Fails twice → browser on
  Google Flights (URL recipes in data-sources.md); that blocked too → the second
  price source (Skyscanner / Kayak; on CN networks Trip.com/携程 is the primary and
  Google the backup); "price unverified" only when every source fails — §When
  things fail. **Every international pick and backup
  is priced in ≥ 2 sources** (Google + Skyscanner / Kayak / Trip.com / the carrier's
  site — data-sources.md §Flights → Second price source); `legs.note` names them
  with the as-of date, a > 10 % disagreement prints as a band. No browser pane →
  Google alone, and `legs.note` says "single source — no browser".
- Multi-airport cities: compare fare + ground transfer cost + time (HND vs NRT,
  LHR vs LGW/STN…). A ¥400-cheaper fare into a far airport often loses.
- Departing CN: also spot-check one LCC directly in the browser (Spring 春秋, Peach,
  Scoot…) — aggregators miss or misprice some LCC inventory.
- **Separate tickets across an international connection are a visa trap, not just
  a baggage nuisance** — audit whenever two PNRs meet at a foreign hub, including
  tickets the user bought before coming to you. Separate-journey policies tag bags
  only to the first ticket's endpoint, and carousels sit landside — so claiming +
  re-checking can REQUIRE entering the transit country. Before writing "no visa
  needed", check: the first carrier's separate-PNR interline stance (assume no
  through-check), the passport's transit-country visa need, and airside overnight
  options if the layover crosses a night. A needed transit visa goes on the
  checklist with its deadline counted back from the departure date.
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
  US; 3+ parks → an annual pass wins — the $80 America the Beautiful is
  residents-only since 2026, non-residents take the $250 pass from the 2nd park,
  country notes §USA), and the license requirement for the driver's
  passport (see country notes).
- Gateway towns run out of cars and rooms in season — the rental and the first night
  go on the booking checklist, not the "later" pile.

**Record for every leg**: carrier, date, dep/arr local times, price + currency + as-of
date, **checked-bag fee** (US domestic: $35-45 per bag per one-way on every major
since Southwest ended free bags in 2025 — 4 legs is a real budget line; UA Basic
Economy is personal-item-only on domestic and short-haul Latin America routes,
while long-haul international Basic Economy does include the carry-on ⚡),
refund/change class, deep link. Multi-leg trips get a
**baggage walkthrough**: where the big bag physically is on every tour/venue day
(day tours = bag stays at hotel; stadiums ban bags; 2-day tours are often
overnight-bag-only). Output 1 pick + 1 backup per leg.

## Phase 4 — City day-plans

When ≥3 cities and subagents are available, fan out one agent per city; each prompt
must include: the dates, the user's interests + pace, **search budget ≤8**, an
explicit **"do not run geocoding"** line (parallel agents would break Nominatim's
1 req/s policy — the assembler geocodes once, centrally), **the plan language**
(`plan.lang`, with one line telling the agent every reader-facing string in its
returned block — `label`, `what`, `note`, `why`, hotel blurbs, checklist rows,
`unverified[]` — is written in that language; its sources will mostly be
English, and English notes pasted verbatim are how a zh plan goes half-English.
Machine fields keep the schema's form regardless: `stops[].query` stays
geocoder-friendly romanized/destination-local, and `kind`/`tag`/`verify` keep
the English enum words the renderers switch on),
and the exact return
format from references/output-template.md §city-block — **plan-JSON day objects,
insertable verbatim**, not a summary. Hard rule for the prompt: **city agents do not
make visa/entry judgements** — no visa rows in their `checklist_items`, no "you need
a visa" in notes. Visa/entry facts are the assembler's Phase 1 job and override
anything a city block says (Turkey test: both city agents put an outdated "visa
required" as checklist item #1; entry had been visa-free since 2026-01-02).
Otherwise do the cities sequentially with the
same structure. When the user prefers group tours, the city agent's first job is
finding real in-sale products with departure schedules (data-sources.md §Group
tours) — the tour's schedule then dictates the surrounding legs, and a fly-in day
tour must clear BOTH weekday grids (operator departure days AND feeder-flight
schedules — same section) before its day is fixed in the skeleton.

Per city:
1. Anchors per interest-fit, ≤ pace + 1 optional per day. Cluster by geography per day;
   order clusters so the route never criss-crosses town.
2. **Verify every anchor**: open days + hours, last-entry time, price, and sell-out
   pressure (official site beats blogs; treat blog data >12 months old as stale).
   Sells out → booking checklist with lead time (Ghibli, teamLab, Uffizi, Alhambra,
   Sagrada Família… see country-quick-notes.md). For dates more than ~3 months out
   nobody publishes that day's hours yet, so verify the **seasonal pattern + closure
   rule**, stamp it "pattern as of {date}", and let the **T-14 row of the pre-departure
   re-check ladder** (output-template.md §Pre-departure re-check ladder) carry the
   re-confirmation. Claiming date-specific verification you cannot have is
   worse than admitting the horizon — and prices move on their own schedule
   (admission fees jump at fiscal-year boundaries), so re-check the fee, not just
   the hours. National parks and other big nature anchors: also read the park's
   official Alerts/Current Conditions page — storm, fire and eruption closures
   outlast news cycles, and a partially-open park may hold 2-3 hours of content
   where the brochure promises a day (resize the day; design it droppable while
   the region is in disaster recovery). When the draw is a natural phenomenon
   (lava fountains, aurora), plan the day to work WITHOUT it: base rate ≈ event
   duration ÷ recurrence interval, the official forecast horizon (days, not
   weeks) sets a decision gate on the checklist — keep every related booking
   cancellable until that gate, and pay no premium for a lottery ticket.
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
   in this order: **geocode → per-day tz sweep → sun --write → links --write →
   check → kml**, so every hop carries a distance-sane duration and a tappable map
   link written into the plan for you. **`check` must exit 0 before rendering** —
   a BROKEN hop is a stop with no lat/lon (geocode it, or hand-fill: navigation.md
   §2), a SUSPICIOUS hop is an undeclared hop over 12 km (the day is mis-clustered,
   or the ride needs its `mode`); fix the plan, never explain the flag away — not in
   prose, and not with a `mode` slapped on to silence it (a tester shipped exit-2
   output rationalised as "expected for a multi-city trip" — every flagged hop was
   a real defect).
   `sun --write` runs once the stops carry coordinates: it fills every day's
   `sun` (civil dawn · sunrise / sunset) in one canonical string and refuses data
   that fails a solar sanity check — never hand-copy sunrise numbers, and **run it
   before writing any sunrise / golden-hour / dark-start prose**: tz changes live in
   tzdata, not in your head (Morocco moves to UTC+0 on 2026-09-20 — the tester's
   hand-written times were an hour off on all ten days, and neither `check` nor
   `qc.py` compares prose against `sun`). A moving day defaults to the last stop;
   when the day's sunrise anchor is at the *first* stop, set the day's `sun_stop`
   (scheduling.md rule 7). **A plan that crosses timezones stamps every day's `tz`
   (IANA name) before `sun --write`** — sun refuses any day whose zone it would
   have to guess from longitude (the guess puts Hawaii at UTC-11), and it refuses
   per-day, so one sweep over `days[].tz` beats fifteen retries.
   **`sun`: non-zero exit = at least one day was skipped or rejected** — the written
   days are fine, re-run `--only DATE` for the ones it names before writing prose
   for them. Mark ridden
   hops with a `mode` on the arriving stop (`transit`/`train`/`bus`/`drive`/`boat`/
   `fly`; long signature walks `walk`), or the walking total and the links will
   both be wrong — `check` says (guessed) next to anything you left it to infer.
   Transit durations come back as ranges — keep them ranges unless you
   browser-verified the hop. Deliver day-level granularity only if the user asks for
   a rough cut. Each finished day also gets its `ribbon` one-liner (Stop1 →walk 12′→
   Stop2 →metro 9′→ …, output-template.md §5) — no script writes it; seven blank
   ribbons is the usual way to find out you forgot.

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
- **Acceptance bars are exit codes and eyes, not prose**: `route_tools check` exits 0
  before rendering, `themes/qc.py` exits 0 after, and the export-probe PNG or the page
  in a browser was actually looked at — none available → say so in the summary.
- **`plan.geo.json` stays the single editable source**: a later "move day 3 to Nara"
  is a JSON edit plus geocode → check → links → kml → render, never a rewrite.
- **Cover title** comes from references/cover-titles.md — never a literal placeholder,
  never a blacklisted cliché.

## When things fail

- flight_scan.py errors twice → browser Google Flights; that blocked too → the second
  price source (Skyscanner / Kayak, data-sources.md §Flights → Second price source);
  only when every source fails do deep links go out marked "price unverified", keep
  moving.
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
- `references/phase-6-assemble.md` — read at the start of Phase 6, before the final
  plan is written: assembly order, cover title, the full adversarial self-check list,
  delivery (themed page + KML + gates .ics), the themed-render flow incl. stock mode,
  the qc / export-probe acceptance bars, and the exit criteria. SKILL.md Phase 6 is
  only the contract; this file is the procedure.
- `scripts/flight_scan.py` — Google Flights grid scanner; run with `--help` first.
- `scripts/route_tools.py` — geocode stops, distance-check clustering, emit per-hop +
  whole-day map links and the trip KML; subcommands geocode / check / links / kml /
  sun (civil dawn + sunrise/sunset per day from sunrise-sunset.org, sanity-checked,
  written into `days[].sun` in the canonical format; point = first stop, last stop
  on a moving day, or the day's `sun_stop` when set; non-zero exit = a day was
  skipped/rejected).
- `scripts/render_plan.py` — turn the plan JSON into the final self-contained HTML.
  It reads the same file route_tools does, so write the plan once and render often.
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
