# Hour-level scheduling

Read this before assembling any day into a timeline. Hour-level timelines are the
default deliverable; deliver day-level granularity only when the user explicitly wants
a rough cut.

Contents: dwell times · assembly method · day types · traps · verification · format.

## Dwell-time defaults (first visit, tourist median)

| Venue type | Time |
|---|---|
| Flagship museum (Louvre/Vatican/British class) | 3-4 h |
| Standard museum / gallery | 2 h |
| Small museum / single exhibition | 1-1.5 h |
| Temple, shrine, church, mosque (a visit) | 30-45 min — active worship sites: see Traps |
| Headliner temple with an approach street (Kiyomizu, Kinkaku-ji, Todai-ji) | 1-1.5 h incl. the approach |
| Open-air archaeological site (Roman Forum, Pompeii, Ephesus, Acropolis) | 1.5-3 h, +30% if hilly and unshaded |
| Amphitheatre / arena (Colosseum, Arena di Verona) | 1-1.5 h |
| Major complex (Fushimi Inari full hike, Alhambra, Forbidden City) | 2-3 h |
| Castle / palace | 1.5-2.5 h |
| Observation deck / viewpoint | 45-60 min + queue |
| Market / food street | 60-90 min |
| Historic district stroll | 1.5-2 h |
| Garden / park | 45-90 min |
| Aquarium / zoo | 2.5-3 h |
| Theme park | full day |
| Photo-stop landmark | 15-20 min |

These are defaults, not answers: whenever a venue is a headliner for this user,
research its realistic visit time and note the source. Scale by pace: relaxed ×1.3,
packed ×0.8, kids or mobility flags ×1.3.

## Assembly method (per day)

1. **Pin the immovables first**: timed-entry tickets, reserved meals/shows, intercity
   departures, sunrise/sunset shots — these are `[pinned]`, contractually immovable.
   The crowd-window opener from rule 2 is different: it is `[opener]` — movable, but
   moving it costs an hour of queueing. Degradation and live-replan key off this
   distinction, so keep the two tags apart. Everything else schedules around them.
   Early-arrival margin is **tiered**, because a timed ticket buys a place in the
   security line, not entry: 15 min at ordinary venues; **30-45 min wherever there is
   security screening or an ID check** (Vatican, Eiffel, Sagrada Família, Forbidden
   City, teamLab…). And never plan to buy at the door at a flagship — ticket-office
   queues run 30-60+ min against near-zero online. If it can be bought online, even
   same-day, that IS the plan; an unavoidable door purchase gets its own +45 min block
   in the chain so the arithmetic sees it.
2. **Anchor the opener**: put the day's most crowd-sensitive venue at its opening
   time. Top sites are empty in their first hour; the same visit at 11:00 costs
   30-60 min of queueing. Crowd calendar beats the clock, though: put flagships on
   weekdays and save parks/markets/neighborhood walks for the weekend; check each
   headliner for **free-admission days** (commonly the first Sunday; Vatican Museums
   the last Sunday) — the free day is the busiest day of the month, so avoid it or
   treat opening-time arrival as mandatory; and the day after a venue's weekly closure
   day (Tuesday after a Monday closure) carries spillover crowds. When the date is
   fixed and lands on a weekend anyway — a layover, a city break, "we have Sunday
   free" — the rule still has a move: give the flagship the day's **first** entry
   slot, take the top of its arrival-margin tier (45 min), and name the weekend tax in
   the plan instead of pretending it isn't there.
3. **Chain by geography** in the day's cluster order: compute every hop with
   scripts/route_tools.py and verify the load-bearing hops per navigation.md. Each
   block = arrival + dwell + buffer.
4. **Buffers are policy, not padding.** "Hop time" means **door to door**: access
   walk + worst-case headway + in-vehicle + egress walk — and *then* the buffer
   (+10 min per urban hop; +15 min per unfamiliar interchange; +30 min after any
   luggage move). Counting only the ride is how a 25-minute block swallows a
   29-minute journey. The corollary is worth knowing: under roughly 1.2 km in a city,
   walking beats a one-stop metro once the wait is counted — so don't schedule the
   ride. Jet lag is real even when the user says it isn't (see Day types).
5. **Meals**: lunch 11:30-13:30, dinner 18:00-20:30 (Spain: ~14:00/21:00 — check
   country notes), placed in a food area within 10 min of the adjacent cluster,
   60-90 min per meal.
6. **Energy curve**: at most 2 heavy anchors (>2 h) per day and never back-to-back,
   **and never more than ~3.5 h of continuous on-feet anchor time without a sit-down
   block** — the second test is the one that matters, because shaving two anchors
   from 2 h to 1 h 45 satisfies the first while leaving four unbroken hours on stone.
   One low-effort block (garden, café, shopping street) mid-afternoon — but see the
   siesta trap before putting shopping there; cap time-on-feet at ~8 h (6 h with kids
   or mobility flags).
7. **Golden hour**: run `python3 scripts/route_tools.py sun plan.geo.json --write`
   once the days have a city-level coordinate (any stop's `lat/lon`, or the
   Open-Meteo geocode from Phase 1 dropped into `stops[0]` — a venue 5 km away moves
   sunset by well under a minute) — and run it **before you write a single sunrise /
   golden-hour / dark-start sentence**, not after. The local clock is tzdata's, not
   yours: Morocco leaves UTC+1 for UTC+0 on 2026-09-20, so the "07:15 sunrise" a
   tester wrote from habit was an hour off on all ten days, and nothing downstream
   (`check`, `qc.py`, the renderers) compares prose against `days[].sun`. Order:
   coordinates → `sun --write` → read the values → write the prose.
   It fetches civil dawn / sunrise / sunset per day
   from sunrise-sunset.org (one request per day — keyed on **that day's first stop
   with coordinates** + date + tz, cached next to the plan — **except on a moving
   day, where it takes the day's LAST stop with coordinates**. A day is "moving"
   when it carries `"travel_day": true` **or** its first and last stops with
   coordinates are more than **150 km** apart; the script prints which rule fired
   ("last stop, first->last 1,090 km" / "(travel_day)"). Reason: the evening anchor
   and the sunset that matters are where you sleep, not where you woke up — the
   China test's Xi'an→Beijing day reported Xi'an's 17:41 against a Beijing anchor
   at 16:59 sunset, 42 min wrong on exactly the day that squeezes in an evening
   block. Order the moving day's `stops` in visit order with the arrival city last
   and the rule does the right thing. **When the day's sun-critical anchor is at the
   first stop instead** — a Chefchaouen sunrise before the flight to Casablanca, an
   Erg Chebbi dune sunrise before the drive to Fes — the last-stop default is 25 min
   wrong on exactly the block that cares, so override it: set the day's
   `"sun_stop"` to that stop's `name` (or its 0-based index in `stops`) and `sun`
   keys the day there. The header still prints one 天亮 for the whole day, so on a
   long east–west move say in the day note that the other city's dawn/dusk
   differs),
   **sanity-checks the answer** (rejects `status≠OK`, two cities or two dates
   returning identical times, and a day length that cannot belong to that latitude
   and month — the failure mode that once returned equatorial 12 h 09 m for Norway
   in October with `status: OK`), and writes each day's `sun` string in place.
   **Read the tail of its output**: after the "N request(s), N day(s) written" line
   it prints — and repeats as a `WARN` on stderr — `skipped/failed (N): <date>
   (reason), …` naming **every day it did not write** (no ISO date / no stop with
   coordinates / `tz approximate` — set `days[].tz` or a plan-level `tz`, the
   longitude guess is wrong wherever zones bend / request failed), and one
   `sun REJECTED — …` WARN per day the
   sanity checks refused. A run that says "6 written" on a 7-day plan now names
   the missing date, so you re-run `--only DATE` instead of counting `sun` fields
   by hand (Italy test F5) — and it **exits non-zero (1)** whenever that list is
   non-empty, so a "9/10 written" run cannot pass unnoticed in a pipeline (Vietnam
   test F6: one TLS failure, exit 0, nearly shipped). The written days are kept;
   fix the named ones with `--only` and re-run until it exits 0. Exit **3** = a day
   was REJECTED by the sanity checks (look before retrying). A day with **no stops
   at all** (pure travel/rest day) is informational only — not counted, no exit 1.
   Canonical `sun` format — the renderers parse it, so keep the shape:
   `天亮 HH:MM · ☀ HH:MM / 🌇 HH:MM[ · TZ · sunrise-sunset.org]`
   e.g. `天亮 05:28 · ☀ 05:53 / 🌇 17:38 · JST · sunrise-sunset.org`.
   The dawn word follows the plan language: `sun --write` picks it from `--lang` >
   `plan.lang` > `plan.meta.lang` > zh, so an `en` plan gets
   `dawn HH:MM · ☀ HH:MM / 🌇 HH:MM[ · TZ · sunrise-sunset.org]`
   e.g. `dawn 05:28 · ☀ 05:53 / 🌇 17:38 · JST · sunrise-sunset.org`; the renderers
   accept either spelling (zh output is unchanged).
   **A space always follows a time**; never glue a bracket to it — `🌇 18:00(AEST`
   is what the "golden hour ≈ …" margin line showed when a tester wrote
   `18:00(AEST · …)`. Extra words go after a ` · ` separator. Trips that **cross a
   daylight-saving switch** need a fetch on both sides of the switch (the script
   does this per day; if you hand-fetch, take one date before and one after — the
   Sydney 10-04 jump from 18:00 to 19:00 only shows up that way).
   Manual fallback if the script cannot run:
   `curl -s "https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={YYYY-MM-DD}&formatted=0&tzid={Area/City}"`
   — once per city (plus once per side of any DST switch), not per day; apply the
   same sanity rules by eye (data-sources.md lists them); credit sunrise-sunset.org
   in the footer either way.
   The response carries `civil_twilight_begin/end` — that is 天亮/天黑 as a
   traveller experiences it, ~25-30 min outside sunrise/sunset. Pre-dawn departures
   and sunrise hikes schedule against **civil dawn**, not sunrise: a 06:00 trailhead
   entry for an 06:22 sunrise is a dark-start (headlamp) only if civil dawn is 06:01.
   Any day that starts before civil dawn gets the 天亮 time printed in its header and
   a "prebooked car, no street-hailing in the dark" note.
   Photography interest → schedule one viewpoint or walk at golden hour. Always check
   evening blocks against sunset: an unlit garden at 19:30 in November is a bug; a
   night-view deck is a feature — know which one you scheduled.
8. **Degradation plan**: tag every block that is neither `[pinned]` nor `[opener]`
   as `[skippable]` or `[swap → alternative]`, and give each day one line: "running
   >1 h late → cut X". On-the-ground plans fail; a plan without a failure mode is the
   failure. Swap targets get the same closure check as anchors — a fallback that is
   shut on the day it backs up is worse than none.
9. **Resolution**: quarter-hour granularity ("14:00-15:30") for anything you
   estimated — false precision like "14:07" destroys trust in the honest numbers.
   Verified timetabled departures and arrivals are the exception and keep their
   published minutes ("09:15-11:31"), because that is exactly where the extra digits
   carry real information.

## Day types that need a different structure

- **Arrival day** — landing before 15:00 = half a sightseeing day, later = **zero
  sightseeing days for the count** — but the evening still gets one free, walkable,
  unticketed block near the hotel (same rule in SKILL.md Phase 2 §3). The
  first morning after a long-haul arrival starts no earlier than 10:00. Plan the first
  evening within walking distance of the hotel; nothing ticketed.
- **Moving day (base change)** — luggage-encumbered from checkout (10:00-11:00) to
  next check-in (~15:00), so this is a day-structure problem, not a buffer problem.
  Solve bags before scheduling anything: (a) store at the departing hotel and loop
  back, (b) coin lockers or staffed storage at the rail hub actually used — large
  lockers at major stations sell out by mid-morning, so name a fallback, (c) in Japan,
  takkyubin hotel→hotel forwarding is usually **next-day**: arrange it the evening
  before and keep an overnight kit. Never schedule an anchor with bags in tow — rule 2
  (opener at opening time) is suspended on a checkout day unless bags are already
  stored. **An intercity moving day carries ≤2 anchors, and only when the bags are
  solved before the first anchor (checked / stored / hotel-held); otherwise 1** (same
  sentence in SKILL.md Phase 6 self-check). Two is for the day whose train leaves at
  16:00 and whose bags went into a locker at 09:00 (Göreme open-air museum + Dark
  Church, then Uçhisar, then the night bus); a day that drags a suitcase to the first
  sight is a one-anchor day whatever the timetable says. If the sunrise anchor is at
  the *first* stop, set `sun_stop` (rule 7).
- **Departure day** — zero sightseeing unless the flight leaves after 18:00. Work
  backwards from the airport-arrival deadline (3 h international) through the real
  city→airport transfer time, and put the luggage solution in writing again.
  **Return-flight time unknown** (`flight_scan.py` lists outbound legs only, and the
  deep link may not show it statically): pick a plausible departure `T` from the
  carrier's published schedule (or the outbound's mirror), and write the day
  backwards from it as a formula the reader can re-run: **T = takeoff → T−3 h at the
  airport (international; 2 h domestic) → T−4 h 30 leave the hotel** — e.g.
  `T ≈ 12:30 → 09:30 at IST → 08:00 out of the hotel`. The `legs` row carries
  `"dep": "⚠️ ~12:30 — verify"` (not a bare time), the timeline blocks say "T−4h30"
  next to the clock, and `unverified` gets one line: "return flight departure time
  not confirmed — day 10 timeline is built on T ≈ 12:30". A confidently wrong 08:00
  taxi is worse than an honest formula.
- **Tour day (跟团日)** — the pickup is `[pinned]` with a 10-15 min margin, and the
  operator owns the clock: no `late_cut` authority inside the tour, so the day's
  degradation plan covers only what the traveller controls (meals, the evening, the
  next morning's buffer). The evening BEFORE a tour day carries its own pins: buy
  provisions, pack per the tour's luggage rule (2-day tours are often
  overnight-bag-only), sleep early enough for the pickup. A "free activity" block
  inside a tour = the bus waits for latecomers — schedule an alarm, not an itinerary.
- **Dateline day** — a westbound trans-Pacific return to East Asia consumes **two
  calendar days** (depart HNL Oct 5 → land Oct 7); eastbound you land the same day
  you left. Lock the return leg FIRST and allocate the final city's days from it —
  planned the other way round, the dateline silently deletes a day from the last
  stop (learned live: it cost Hawaii its circle-island day).

## Traps that break otherwise-correct timelines

- **Worship-hour closures — everywhere, big cities included.** Mosques close to
  non-worshippers during the five daily prayers (~30-45 min, times shift daily) and
  for most of Friday midday — pull the date's prayer times rather than assuming.
  Churches close to tourists during Mass, Sunday mornings especially, and across Italy
  and Spain they commonly shut 12:00-15:00 — **in central Rome, Milan or Florence the
  shops stay open through the afternoon but the churches still close**, which is the
  half of the story most plans miss. Every worship-site block carries a one-line dress
  code (shoulders and knees covered; headscarf where required) — being turned away at
  the door is a preventable failure.
- **Commercial siesta — Spain nationwide, Italy/Greece outside the big-city centres.**
  Independent shops and family restaurants close roughly 13:30-17:00. The
  mid-afternoon block there must be something that stays open (major museum, garden,
  café terrace, long lunch), with shopping and the paseo moved to 17:30+. Assume
  midday closure for any small venue in these areas unless its hours were verified.
- **Weekend food closures**: city markets are a classic Sunday trap (Rome's Testaccio
  and Campo de' Fiori both shut). If food is a stated interest, verify the market's
  own day-of-week before building a meal around it.
- **Closures the holiday API can't see**: local festivals (streets closed, hotels 3×),
  seasonal operating windows (cable cars, mountain huts, gardens, boats), per-venue
  annual maintenance, and Ramadan in Muslim-majority destinations. SKILL.md Phase 1
  budgets a search for these; the Phase 6 closure scan re-checks them.

## Timeline verification (runs inside the Phase 6 self-check)

- Chain arithmetic: every block starts ≥ previous block end + hop time + buffer
- Anchors: arrival ≥ opening; arrival ≤ last entry; planned exit ≤ closing
- Pinned tickets: arrival margin matches the tier in rule 1 (15 vs 30-45 min)
- No more than ~3.5 h of continuous on-feet anchor time without a sit-down block
- Walking total ≤ 8 km, counted honestly: `check`'s **on-foot** line ×1.3 (its ridden
  line is not walking — mark those hops `"mode": "transit"` so it can tell), **plus**
  in-venue walking and any stroll segments. A stroll is invisible to `check` unless
  you model it as a stop at its midpoint — so model it, and show the arithmetic in
  `walking_km: {total, how}` rather than asserting a bare number.
- Late evenings: last planned hop vs the line's last departure (verify, don't assume).
  If lodging isn't in scope, say "day starts at {first block} / ends at {last block};
  add your hotel hops" and mark this check N/A rather than passed.
- Meal blocks exist and actually sit near the clusters they claim
- Moving days: bags solved in writing, no anchor before storage; ≤2 anchors only if
  the bags are solved before the first one, otherwise ≤1 (§Day types)
- Departure day with an unconfirmed return time: the T-formula is visible in the
  timeline, `legs.dep` carries ⚠️, `unverified` names it (§Day types)
- Worship/siesta/free-day traps checked for every affected block

## Scheduled-day format

Hop rows use the canonical format from navigation.md, and every hop is marked
`(verified)` or `(est.)` so the reader knows which durations were actually checked.
**The arithmetic below is meant to be copied**: every block starts at the previous
block's end plus the hop plus its buffer, and this day passes the whole verification
list above. If you catch yourself writing a 0-minute gap between two places 1 km
apart, that is the bug this example exists to prevent.

```
2026-10-05 (周一) — 京都·东山    天亮 05:28 · ☀ 05:53 / 🌇 17:38 · JST · sunrise-sunset.org
08:00-09:15  清水寺 ¥500 — 06:00 开门,首小时人最少                    [opener]
09:15-09:45  步行 清水坂→三年坂→高台寺 0.7 km ~10分(+街景停留)         (est.)
09:45-10:45  高台寺 ¥600 — 09:00-17:00,最晚入场 17:00
10:45-11:00  步行 高台寺→八坂神社 0.4 km ~5分                          (est.)
11:00-11:30  八坂神社 免费 — 境内 24h                                 [skippable]
11:30-11:45  步行 八坂神社→祇园四条 0.5 km ~8分                        (est.)
11:45-13:00  午餐 · 祇园/花见小路一带                                 [swap → 锦市场]
13:00-13:45  巴士 203(往銀閣寺道) ~25分 ¥230 · 祇園→銀閣寺道 · 下车步行8分  (est.)
13:45-15:15  银阁寺 ¥1,000 — 08:30-17:00(3-11月)
15:15-16:00  哲学之道 散步 ~1.5 km(按站点建模,否则不计入步行总量)      [skippable]
交通算账:巴士 2 段 × ¥230 = ¥460 < 地铁巴士一日券 ¥1,100 → 按次刷卡
步行合计:check 1.6 km(含祇园午餐点)×1.3 + 哲学之道 1.5 + 馆内 ≈ 5.0-5.5 km < 8 km ✓
迟到 >1h → 先砍八坂神社,再砍哲学之道;银阁寺须 15:30 前入场
雨备:三十三间堂(室内长堂,周一开放 — 已核实)。⚠️ 勿用京都国立博物馆:周一闭馆
时刻/票价为 2026-08-01 查得的季节性数据,出行前两周复查
```
