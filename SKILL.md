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

## Phase 1 — Country brief (once per destination, ≤10 lines of output)

Read the destination's section of references/country-quick-notes.md first. **Destination
not in that file (Mexico, Morocco, Turkey and Vietnam all weren't)** → work through its
"Destination not listed? — the checklist" section instead of improvising: it is the
list of things every new country costs a first planner 6-9 searches to rediscover.

- **Visa/entry** for that passport: official government/embassy sources only; put the
  processing lead time on the booking checklist. Rules change — never answer from memory.
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
  take ~10 s). One line: temps, rain odds, daylight.
- **Money & connectivity one-liners**: card vs cash norms, eSIM ballpark, plug type.
- **Insurance line**: travel-medical insurance with destination-appropriate coverage
  goes on the checklist (US target: ≥$100k medical + medical evacuation — an ER visit
  is four figures before insurance). Tours never substitute for it.
- **Safety paragraph, one per base**: which areas to avoid after dark, and — more
  useful than warnings — design the plan so night movement is door-to-door by car.
  A route that never needs a dark walk beats a list of cautions.

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
  Google Flights (URL recipes in data-sources.md). Google unreachable (some CN
  networks) → Trip.com/携程 in the browser.
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
  US; 3+ parks → the annual pass wins), and the license requirement for the driver's
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
   in this order: **geocode → check → links --write → kml**, so every hop carries a
   distance-sane duration and a tappable map link written into the plan for you.
   Then `sun --write` once the stops carry coordinates: it fills every day's
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
   per-day, so one sweep over `days[].tz` beats fifteen retries. **Non-zero exit = at least one day was skipped or
   rejected**: the written days are fine, re-run `--only DATE` for the ones it
   names before writing prose for them. Mark ridden
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

Assemble per references/output-template.md: overview → decisions made for the user →
booking checklist → flights/intercity table → day-by-day cards → hotels → budget
rollup → country brief.

**Cover title (bilingual)**: when the deliverable is a rendered page, pick or adapt a
poetic display title from references/cover-titles.md — zh 2-6 characters + an English
line, matched to the trip archetype (road-trip / island / mountain / city / coast).
Never ship a literal placeholder like "X国行"; never use the clichés on that file's
blacklist. Cite the allusion honestly (原句 in the subtitle or a small credit line).

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
  script exited 0; any `sun_stop` override is on the right day)
- Red-eye / timezone day-number arithmetic
- No day exceeds pace; **an intercity moving day carries ≤2 anchors, and only when
  the bags are solved before the first anchor (checked / stored / hotel-held);
  otherwise 1** (same sentence in scheduling.md §Day types)
- Every price has source + as-of date; every bookable line has a link
- **Language**: `plan.lang` matches the language the user asked in, and every
  reader-facing string in the plan (day titles, notes, tips, checklist rows,
  decisions, hotel blurbs) is in that language — an English fragment copied verbatim
  from a source into a zh plan gets translated, not shipped. Proper nouns stay in
  their native form with a gloss where useful (浅草寺 Sensō-ji); machine fields are
  exempt (`stops[].query` stays geocoder-friendly, `kind`/`tag`/`verify` keep their
  English enum words)

**Deliver — the deliverable is a themed page, never a plain text one.** Render
`plan.geo.json` through the theme chosen in Phase 0 (`prefs.theme`, default
**illustrated**) — see *Themed renders* below — and hand over: a chat summary (route
one-liner, total budget, the 3 biggest decisions made for the user, and in stock mode
the one-line picture notice) + `trip-<theme>.html`, one self-contained, phone-friendly
file with its own share/export buttons and the appendix (checklist, legs, hotels,
budget, brief). Publish through whatever artifact / file hand-off tool the harness
has (in Claude Code: Artifact, else SendUserFile); otherwise save the file and give
its absolute path. Ship the trip KML (`scripts/route_tools.py kml plan.geo.json -o
trip.kml`) alongside for offline map apps. The plain `scripts/render_plan.py plan.geo.json
-o trip.html` page (printable, checkbox checklist, offline route sketch per day) is an
**extra** — add it when the user asks for a printable/plain version, or as the last
resort if the theme renderer still fails after one honest fix attempt (then say so in
the summary). **`plan.geo.json` is the single editable source** for all of it — every
command above reads that one file — so a later "move day 3 to Nara" is a JSON edit
plus geocode → check → links → kml → render, not a rewrite. The page chrome (section
names, buttons, pills, weekdays) speaks `plan.lang` (set in Phase 0, `zh` default);
`--lang zh|en` on any renderer overrides it, plan content prints as written.

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
     first" applies only to generic props: `themes/assets/IMAGE-LIBRARY.md` §通用件
     lists what any trip may use; generate the rest — **with the agent's own native
     image/video generation if it has one (no key to configure; same specs, same
     prompts-as-style-anchors, same split/cutout/webp/manifest steps — ART-SCHEMA.md
     「生成器选择」), otherwise `gen.py` / `genvideo.py` over OpenRouter** — using the
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
  passes, sell-outs, closure patterns, transit apps per country; destination absent →
  its "Destination not listed? — the checklist" section.
- `references/output-template.md` — read before Phase 4 fan-out (city-block format)
  and Phase 6 (deliverable structure).
- `references/scheduling.md` — read before building any hour-level timeline: dwell
  times, buffers, meals, energy curve, degradation tags, timeline verification.
- `references/navigation.md` — read with it: hop-link recipes, transit-row format,
  exit numbers, verify-vs-estimate policy, offline-maps (KML) workflow.
- `references/cover-titles.md` — bilingual poetic cover-title case library (诗词/散文/
  名著出处 + trip-archetype fit + cliché blacklist); read at Phase 6 when rendering.
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
  (index by subject — check its 通用件 section before generating anything),
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
