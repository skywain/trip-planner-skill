# Data sources & URL recipes

Fallback order everywhere: bundled script / keyless API → browser pane → web search →
deep link marked "verify on click". Statuses marked ✓ were live-tested 2026-08-01.

## Flights
- **scripts/flight_scan.py** (Google Flights via fast-flights, no key). One-time
  dependency: `pip3 install --user fast-flights` — the script says so and prints a
  browser link if the import fails, so a missing dependency never blocks a plan.
  `python3 scripts/flight_scan.py --from PVG --to NRT --depart 2026-10-01 --nights 10-15 --flex 2 --max-fetches 30`
  That grid is 5 dates × 6 trip lengths = 30 combos against a default cap of 12, so
  either pass `--max-fetches` as shown (~5-10 s per combo) or let it scan centre-out
  around your requested date — truncation drops the edges of the grid, never the date
  you actually asked about. One-way (for open-jaw halves): add `--oneway` and drop
  `--nights`. Prices are Google's cache — comparison grade; the deep link printed with
  each row is the source of truth. It sleeps between fetches and retries once on the
  transient throttling Google does to repeat callers.
  **Cheapest-by-price hides usable flights**: the low rows are red-eyes and next-day
  arrivals. For any leg feeding a pinned event or a tour pickup window, scan with
  `--arr-before HH:MM` (and `--dep-after`) — "cheapest USABLE flight" is the number
  the plan needs (live case: CMH→SLC sticker floor $132 was an overnight horror;
  the usable floor was $207).
  **Read the head line of the output first**: it states the **currency** and whether
  each price is **per person or the total** for `--adults N` — it is the **TOTAL for
  all passengers** (`--adults 2` doubles the number; divide by N for per-person) and
  the budget table copies that wording; `--currency XXX` sets the reported currency
  (default follows the Google region). Two testers had to mark their whole budget
  "⚠ pp or total unknown" before this line existed. `--nonstop` keeps only nonstop options — the LHR→HND
  test saw nothing but 30-40 h two-stop rows in the cache until it was asked for
  nonstops; for a long-haul leg run both with and without and quote both floors.
  An **`AssertionError`** means Google returned a non-200 page (bot wall / consent
  page) and the fallback renderer failed too — the error line echoes route + date
  only so you can see which grid cell died; it is **not** a bad airport code
  (CNS→PEK failed on three valid dates this way). Wait and retry, or fall back to
  deep links marked "price unverified". The scan
  returns **outbound legs only** for a return trip: the return leg's departure time
  is not in the output — read it off the deep link when the plan needs a clock.
- **Browser**: `https://www.google.com/travel/flights?q=` + URL-encoded natural
  language, e.g. `Flights from PVG to KIX on 2026-10-02 returning from NRT 2026-10-14
  for 2 adults` — the q= parser understands open-jaw phrasing. Currency follows the
  Google region.
- **CN networks / CN carriers**: https://www.trip.com/flights/ (or flights.ctrip.com)
  in the browser pane. Also check one LCC direct (Spring 春秋, Peach, Scoot, AirAsia…).
- **Never** curl airline/OTA sites — instant bot-block, wasted call.

## Group tours(跟团)— when the traveller prefers not to self-drive
The tour product replaces flights+car+hotel for its days, so research it FIRST — its
schedule dictates the surrounding legs, not the other way around.
- **Where to look**: operator sites first (prices/terms authoritative), then
  aggregators (Viator = often the only statically readable price; GetYourGuide;
  TakeTours), and Chinese-language operators (走四方 usitrip / 途风 Tours4fun / 悦禾
  joytrav) for 中文团 — often cheaper, pages usually JS-only.
- **班期 is life-or-death**: multi-day tours run fixed weekdays, and the product you
  want may simply not exist (learned live: no 2-day Yellowstone tour departs SLC at
  all — shortest is 3-day, and only a "Day 1 = airport-pickup day" 4-day structure
  preserved the onward flight). JS booking calendars cannot be verified statically:
  with the browser pane, verify — page the pricing calendar and read each date cell
  (bookable / sold-out / blank); no browser → ship the calendar link + mark 班期
  unverified, never guess it. **The listing's "Available Days: Mon, Tue…" line is
  marketing, not schedule**: checked live against five product calendars, it
  contradicted every one of them.
- **Fly-in day tours live on a weekday grid with two axes**: the operator's real
  departure days AND the feeder flights' weekday schedule — feasibility is the
  AND of both (learned live: a Sunday Oahu→Big Island day trip was structurally
  dead — no inter-island flight before 8:00 on Sundays AND no package departing
  Sundays; Monday had three pre-7:00 flights, $26 cheaper). When the AND fails,
  don't force it: swap two adjacent flexible days so the fly-in lands on a
  workable weekday — and swap BEFORE anything in the pair is ticketed.
- **Min-party lines bite solo travellers**: drive-yourself products (UTV, buggy)
  often require "minimum 2 participants" per booking — no pairing with
  strangers; operators usually sell a ride-along/passenger variant that books
  solo, so ask. Operator chatbots hedge ("may not be available…"): the booking
  calendar is the answer, not the bot.
- **Price anatomy** (quote ALL of it, not the sticker): double-occupancy base;
  single supplement ×1.3-1.6 or listed at checkout; mandatory fee package
  ($90-140 门票包 on US park tours); **non-resident surcharges** (US parks:
  +$100/person at 11 flagship parks from 2026 — ask who collects it;
  country-quick-notes.md §USA); driver-guide tips $10-15/person/day (often cash).
- **Structure quirks to check**: which day is a pickup/dropoff day (not a touring
  day); what time it returns on the last day (operators state "book flights after
  X:00" — obey it); overnight-bag-only luggage rules on 2-day tours; whether the
  advertised sight is a stop or a drive-by.
- **Audit the finalists like a hostile lawyer** (1-2 shortlisted products, not the
  longlist): the date-specific fare beats the "From $X" banner (select the date,
  read the fare row — live case: $229 banner, $239 on every bookable date); "park
  entrance fees included for US Residents with acceptable ID" means NOT included
  for your traveller; pickup-point lists often render only inside checkout — walk
  to the checkout page without paying to read them; put the operator phone from
  the product page on the checklist row (the recurring 1★ failure mode is a missed
  pickup with an unreachable driver). If pickup is confirmed "by phone the night
  before" (US operators routinely do this), the plan's connectivity brief must
  require a **local-voice-capable** SIM — data-only eSIMs can't take the call.
- **Reserve-now-pay-later + free cancellation = zero-cost options**: when a
  decision gate (a squad announcement, a companion's dates, an unresolved branch)
  blocks commitment and the departure is capacity-limited ("Likely to sell out"),
  the checklist's TOP row becomes "place the free hold on the branch-compatible
  date now" with the free-cancel deadline as its own row — the user places it
  (SKILL.md Hard rule 1: the agent never books or holds anything). The hold costs nothing,
  survives the gate, and turns "wait and hope" into "decide at leisure". The
  same logic orders ALL bookings: free-cancel holds first, refundables next,
  non-refundables last — every ticketed non-refundable freezes the re-planning
  around it (a pair of "freely swappable" days stops being free the moment the
  flights inside it are ticketed).

## Hotels
No good keyless API exists — use browser + deep links; recommend neighborhoods and
2-3 properties with a price band, and let the user's click show live prices.
- **Compare on the checkout screen's all-in total, never the list price**:
  resort/amenity/urban fees ($30-56/night on resort strips, common in NYC) plus
  ~19% taxes sit between the two — sometimes inside the list price, sometimes
  payable at the property; only the final screen settles which. Calibrate scores
  to the destination's baseline (an ageing resort strip's 8.0 ≈ a mainland
  boutique's 8.5), and when the itinerary has pre-dawn starts, read the RECENT
  low reviews for the three sleep-killers — AC, street/door noise, slow
  elevators — before price breaks the tie. **Cross-validate the score on a second
  platform with a different reviewer base** (Booking ↔ Agoda; Google as
  tie-break): the bases weight cleanliness, noise and breakfast differently, so
  agreement adds confidence and a gap >0.5 is itself a finding — read that
  hotel's low reviews before shortlisting it. The cross-check applies to PRICE
  too: platforms contract different rates for the same room (Agoda often
  undercuts for Asia-market users by tens of dollars a night) — compare
  like-for-like (same room, refundable vs non-refundable) before paying, and
  remember the cancellation terms you get are the booking platform's, not the
  cheapest platform's.
- Google Hotels (browser): https://www.google.com/travel/hotels — search the city,
  **set the dates in the page UI and confirm they display before reading prices**:
  URL date parameters are silently ignored, and the default view shows near-term
  base rates that look plausible (caught live — the first read was 8月 prices
  wearing a 9月 URL).
- Booking deep link with dates baked in:
  `https://www.booking.com/searchresults.html?ss={CITY}&checkin={YYYY-MM-DD}&checkout={YYYY-MM-DD}&group_adults={N}&order=review_score_and_price`
- Agoda often beats Booking in Asia — search in browser, copy property links.

## Intercity rail / bus / local transit
- Durations & connections (browser, keyless):
  `https://www.google.com/maps/dir/?api=1&origin={A}&destination={B}&travelmode=transit`
  (mainland China: this recipe is fine *for you, the planner, on the browser pane*,
  but never ship a Google link to the traveller there — see navigation.md provider
  note).
- Mode overview A→B: `https://www.rome2rio.com/map/{A}/{B}` (browser).
- SE Asia bookings: `https://12go.asia/en/travel/{a}/{b}`.
- Rail: price on the operator's site (country-quick-notes.md lists them). Resellers
  (Omio/Trainline/Klook) are acceptable when operator sites reject foreign cards —
  note the markup in the plan.
- China domestic: 12306 via browser only (12306.cn/en, passport-registered account,
  foreign Visa/Mastercard accepted ⚡; sales open 15 days ahead in station batches);
  Trip.com resells with a fee when the card fails. Real-name rules, the four
  pre-sale clocks and station security are in country-quick-notes.md → China
  (inbound).

## Geocoding & day-route sanity — ✓
Venue-level coordinates come from Nominatim/OSM via `scripts/route_tools.py geocode` —
keyless; the script enforces the usage policy (User-Agent + 1 req/s throttle + cache),
so never call Nominatim in parallel or outside the script. Misses: pull coordinates
from the Google Maps place card in the browser and fill them into the plan JSON by
hand. **Nominatim is weak on non-Latin place names** (Japanese, Chinese, Korean,
Thai…) and fails *quietly* — a station or lane resolves to a similarly named place
a few hundred metres away; the script WARNs when the resolved `display_name` does
not contain the query's head token (first Latin word of ≥4 letters, or the first 2
CJK characters). For those countries pre-filling `est`
coordinates for everything known is the normal path (a trip with 0 Nominatim
requests is fine). Then `check` (distance/clustering sanity), `links` (per-hop +
whole-day deep links — **`--provider google|apple|amap`**, default Google; `amap`
or `apple` for mainland China where Google links are dead, `amap` emits per-hop
links only with no day chain), `kml` (offline pins for Organic Maps / My Maps —
the provider-independent fallback), `sun` (civil dawn / sunrise / sunset per day,
written as `天亮 HH:MM · ☀ HH:MM / 🌇 HH:MM · TZ · sunrise-sunset.org`, or with the
dawn word `dawn …` when the plan is `en` — `--lang zh|en` > `plan.lang` >
`plan.meta.lang` > zh; renderers accept both).
Details: references/navigation.md.
- `check` reads a per-stop `mode` from the vocabulary **`walk | transit | fly |
  drive | boat | train | bus`** (the hop *into* that stop). Anything undeclared is
  guessed from distance, and a guess is silent: a 1.7 km coastal walk becomes
  "transit" and the day's on-foot total reads 0 — declare signature walks. Declared
  fly/drive/boat/train/bus hops are listed as long hops, not `SUSPICIOUS`, so a
  plan with a flight or a reef boat can pass `check` cleanly.
- `check`'s transit durations are a distance formula with no knowledge of tunnels,
  express lines or airport trains: **for any transit hop >20 km it says "use the
  operator timetable" — do that** (Flytoget OSL→Oslo S is 19 min; the formula gave
  195-285). Timetable = operator site (country-quick-notes.md lists them) or the
  Google Maps transit deep link above at the hour the plan uses it.

## Venues, tours, tickets
- Hours/closures: official venue site first; Google Maps place card second (watch for
  "Temporarily closed"); blogs last and only if <12 months old.
- Ticket platforms for comparison + booking links:
  Klook `https://www.klook.com/search/?query={q}` ·
  GetYourGuide `https://www.getyourguide.com/s/?q={q}` · KKday · Viator.
  Platforms sometimes cost MORE than the official site — compare before recommending.

## Public holidays — ✓
`curl -s "https://date.nager.at/api/v3/PublicHolidays/{year}/{ISO2}"` (keyless,
instant). Long weekends near the trip = domestic-tourist crowds even without a direct
collision — check the adjacent weeks too.
**It lists fixed-date secular / statutory holidays only.** In Muslim-majority
countries the lunar-calendar holidays — Eid al-Fitr, Eid al-Adha, Mawlid, Islamic New
Year, and Ramadan itself — are **absent** (2026/MA returned 10 rows, every one a
fixed civic date, zero Eids); Buddhist-calendar holidays in Thailand, Laos, Myanmar,
Sri Lanka (Vesak, Asalha Puja, Khao Phansa…) and the Lunar New Year cluster across
East/Southeast Asia are patchy or missing the same way. Spend one budgeted search on
them: the country's official gazette / government holiday page, or a religious-
holiday calendar page (timeanddate-style) for the year — and put the dates in
`brief.holidays` with that source. Eid dates are moon-dependent and published as
"expected" until ~1 day before: mark them ± 1 day.

## Weather — ✓ (archive call can take ~10 s on first hit)
1. Geocode the city: `curl -s "https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"`
2. Same-dates-last-year climate:
   `curl -s "https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={dates-1y}&end_date={dates-1y}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"`
3. Trip starts within 16 days → real forecast instead:
   `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto`
4. Sunrise/sunset for golden-hour scheduling — preferred path is
   `python3 scripts/route_tools.py sun plan.geo.json --write` (per-day fetch keyed on
   the day's first stop — the **last** stop on a moving day, or the day's `sun_stop`
   when set —, cache, the sanity rules below applied for you, canonical `sun`
   string written into the plan, a WARN per skipped/rejected day with its date and a
   **non-zero exit** when there is any; see scheduling.md rule 7). **Run it before
   writing any sunrise/golden-hour prose**: the local clock comes from tzdata, which
   knows about time-zone changes you don't (Morocco returns to UTC+0 on 2026-09-20 —
   the tester's hand-written times were an hour off for all ten days); `sun`'s
   output is the truth, prose follows it.
   Manual fallback (keyless, any future date; `tzid`
   on the `/json` endpoint verified working 2026-08-01):
   `curl -s "https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={YYYY-MM-DD}&formatted=0&tzid={Area/City}"`
   The service requires **visible attribution** wherever the data is shown — put
   "日出日落数据 / sunrise-sunset.org" in the plan footer — and answers heavy use with
   HTTP 429 + Retry-After, so fetch once per city (plus one fetch on each side of a
   daylight-saving switch), not once per day.
   **Sanity rules — the API fails open.** A malformed or missing `lat`/`lng`/`date`
   (a shell variable that didn't split, a stray quote) does **not** error: it
   returns today's times for 0°,0° with `"status":"OK"` — 07:59/20:09, day length
   12 h 09 m — which looks perfectly plausible for a plan and nearly went onto eight
   Norwegian day cards. Don't trust a response unless: `status` is `OK`; two
   different cities or two different dates give **different** times; and the day
   length is possible for that latitude and month (60°N in early October ≈ 11 h and
   shortening by ~5 min a day; a flat 12 h that doesn't move from one date to the
   next is the equator, not your destination). Anything else → fix the request and
   re-fetch, or ship the day without `sun` rather than with a wrong one.
   From Python, `urllib` direct hits get **HTTP 403 without a User-Agent** — set one
   (`{"User-Agent": "trip-planner-skill/1.x (personal trip planning)"}`, which the
   script already does); curl works because it sends its own.

## FX — ✓
`curl -s "https://api.frankfurter.dev/v1/latest?base={HOME}&symbols={DEST}"`
(ECB daily fix). Stamp rate + date once in the budget table; don't re-fetch per line.
**Coverage is ~30 major currencies only** (`/v1/currencies` lists them: EUR USD GBP
JPY CNY KRW THB AUD CAD MXN TRY … — no MAD, VND, EGP, TND, DZD, KHR, LAK, LKR, NPR,
UZS…). An unsupported symbol does **not** error: the call returns HTTP 200 and the
`rates` object simply lacks that key (`symbols=VND,USD` → `{"USD": …}` alone), so a
script that reads `rates[DEST]` blindly takes the wrong currency (Vietnam) or ships
no rate at all (Morocco). Therefore:
1. after any frankfurter call, **assert the destination key is present** in `rates`;
2. missing → fall back to `curl -s "https://open.er-api.com/v6/latest/{HOME}"`
   (keyless, ~160 currencies, daily; read `rates.{DEST}` and `time_last_update_utc`)
   — check the key there too;
3. write which source you used into `meta.fx`, e.g.
   `1 CAD = 6.70 MAD (open.er-api.com, 2026-08-15 — MAD not on frankfurter)`.

A third failure mode: frankfurter can answer a `?base=…&symbols=…` call with an
**empty body** — 0 bytes, HTTP 200, no error text — so the JSON parse fails on
nothing rather than on a missing key. Retry the same date with another base
(`base=EUR`) and cross-multiply to the pair you need
(`HOME→DEST = (EUR→DEST) / (EUR→HOME)`); if that is what produced the number, say so
in `meta.fx`, e.g. `1 CAD = 108.4 JPY (frankfurter.dev via EUR cross, 2026-08-15 —
direct CAD call returned an empty body)`. An empty body twice → go to step 2's
fallback.
Closed currencies (MAD, TND, DZD, …) also get one line in the money brief: not
buyable before departure, not exportable — exchange on arrival / ATM.

## Visa / entry
Web search `{nationality} citizens visa {destination}` restricted to official
government/embassy domains — blogs and forums are how people miss rule changes.
Capture: visa type, fee, processing days (→ checklist), passport-validity rule
(the 6-month trap), onward-ticket requirement.

## Optional keyed upgrades (only if the user already has env vars set)
- `AMADEUS_KEY` / `AMADEUS_SECRET` — Amadeus self-service flight/hotel search APIs.
- `SERPAPI_KEY` — Google Flights/Hotels as JSON without a browser.
Never ask the user to sign up for keys mid-plan; the keyless path is the default.
