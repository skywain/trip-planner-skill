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
- **Browser**: `https://www.google.com/travel/flights?q=` + URL-encoded natural
  language, e.g. `Flights from PVG to KIX on 2026-10-02 returning from NRT 2026-10-14
  for 2 adults` — the q= parser understands open-jaw phrasing. Currency follows the
  Google region.
- **CN networks / CN carriers**: https://www.trip.com/flights/ (or flights.ctrip.com)
  in the browser pane. Also check one LCC direct (Spring 春秋, Peach, Scoot, AirAsia…).
- **Never** curl airline/OTA sites — instant bot-block, wasted call.

## Hotels
No good keyless API exists — use browser + deep links; recommend neighborhoods and
2-3 properties with a price band, and let the user's click show live prices.
- Google Hotels (browser): https://www.google.com/travel/hotels — search the city, set
  dates, read the price histogram for the band.
- Booking deep link with dates baked in:
  `https://www.booking.com/searchresults.html?ss={CITY}&checkin={YYYY-MM-DD}&checkout={YYYY-MM-DD}&group_adults={N}&order=review_score_and_price`
- Agoda often beats Booking in Asia — search in browser, copy property links.

## Intercity rail / bus / local transit
- Durations & connections (browser, keyless):
  `https://www.google.com/maps/dir/?api=1&origin={A}&destination={B}&travelmode=transit`
- Mode overview A→B: `https://www.rome2rio.com/map/{A}/{B}` (browser).
- SE Asia bookings: `https://12go.asia/en/travel/{a}/{b}`.
- Rail: price on the operator's site (country-quick-notes.md lists them). Resellers
  (Omio/Trainline/Klook) are acceptable when operator sites reject foreign cards —
  note the markup in the plan.
- China domestic: 12306 via browser (or a 12306 MCP if installed).

## Geocoding & day-route sanity — ✓
Venue-level coordinates come from Nominatim/OSM via `scripts/route_tools.py geocode` —
keyless; the script enforces the usage policy (User-Agent + 1 req/s throttle + cache),
so never call Nominatim in parallel or outside the script. Misses: pull coordinates
from the Google Maps place card in the browser and fill them into the plan JSON by
hand. Then `check` (distance/clustering sanity), `links` (per-hop + whole-day Google
Maps deep links), `kml` (offline pins for Organic Maps / My Maps). Details:
references/navigation.md.

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

## Weather — ✓ (archive call can take ~10 s on first hit)
1. Geocode the city: `curl -s "https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"`
2. Same-dates-last-year climate:
   `curl -s "https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={dates-1y}&end_date={dates-1y}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"`
3. Trip starts within 16 days → real forecast instead:
   `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto`
4. Sunrise/sunset for golden-hour scheduling (keyless, any future date; `tzid` on the
   `/json` endpoint verified working 2026-08-01):
   `curl -s "https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={YYYY-MM-DD}&formatted=0&tzid={Area/City}"`
   The service requires **visible attribution** wherever the data is shown — put
   "日出日落数据 / sunrise-sunset.org" in the plan footer — and answers heavy use with
   HTTP 429 + Retry-After, so fetch once per city, not once per day.

## FX — ✓
`curl -s "https://api.frankfurter.dev/v1/latest?base={HOME}&symbols={DEST}"`
(ECB daily fix). Stamp rate + date once in the budget table; don't re-fetch per line.

## Visa / entry
Web search `{nationality} citizens visa {destination}` restricted to official
government/embassy domains — blogs and forums are how people miss rule changes.
Capture: visa type, fee, processing days (→ checklist), passport-validity rule
(the 6-month trap), onward-ticket requirement.

## Optional keyed upgrades (only if the user already has env vars set)
- `AMADEUS_KEY` / `AMADEUS_SECRET` — Amadeus self-service flight/hotel search APIs.
- `SERPAPI_KEY` — Google Flights/Hotels as JSON without a browser.
Never ask the user to sign up for keys mid-plan; the keyless path is the default.
