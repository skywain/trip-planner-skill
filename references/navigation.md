# Maps & navigation

Goal: every hop in the plan is tappable — it opens turn-by-turn directions in the
right app — and every day has a chained route link plus an offline fallback. Read this
together with scheduling.md before Phase 4 timeline assembly.

## The workflow

0. **Destination check**: in Korea and mainland China, Google directions are unusable
   (see "Which app where" and "Google Maps is unavailable in some destinations").
   Still run `check` and `kml` — distances, clustering and offline pins stay valid.
   Mainland China: run `links --provider amap` (or `apple`) instead of the default
   Google links. Korea: skip the `links` output and substitute Naver search links in
   the plan, including the day-overview link.
1. Write the plan JSON — **name it `plan.geo.json` from the start**, because geocode
   edits a file with that stem in place and every later command then reads the one
   file that has everything. It feeds the maps, the KML and the final HTML, which is
   what keeps them from drifting apart:
   ```json
   {"trip": "kyoto-oct",
    "days": [{"date": "2026-10-05", "label": "East Kyoto",
              "stops": [{"name": "清水寺", "query": "Kiyomizu-dera, Kyoto, Japan"},
                        {"name": "锦市场", "lat": 35.005, "lon": 135.764}]}]}
   ```
   `query` defaults to `name`; pre-filled `lat`/`lon` skip geocoding; `label` is the
   day's theme line, same field name everywhere. Add `"mode"` to a stop whenever the
   hop **into** it is ridden (or walked against the distance guess) — vocabulary
   `walk | transit | fly | drive | boat | train | bus` — because 1.4 km can be a
   two-stop metro ride or a pleasant walk, and only the plan knows which; the field
   decides the walking total, which directions the tappable link opens, and whether
   a 45 km boat or a 1,900 km flight is a declared long hop or a clustering mistake.
   **A signature walk longer than 1.6 km must carry `mode: walk`** or `check` counts
   it as ridden and the day's on-foot total silently reads 0 (the Bondi→Coogee case). **`stops` must mirror that day's anchors plus any modelled strolls, in
   visit order** — every map artifact and the walking total are computed from it, so
   a `stops` list that disagrees with the timeline ships a map of a different day.
   Give every stop-to-stop transition its own `kind: hop` row, even a two-minute one
   out the door: N stops ⇒ N-1 hop rows is what lets `links --write` put each URL on
   the right row by itself. Model a long stroll as a stop at its midpoint or its
   kilometres never reach the walking total. (render_plan.py adds more keys to
   the same file — see its docstring.)

   **Two ways that count goes wrong on ordinary days** (both found by testers on
   their first unfamiliar trip; both let `links --write` line up by accident and
   put the wrong directions on a row):
   - **The day's first hop (lodging → first stop) and last hop (→ lodging).** They
     are real hop rows in the timeline but the lodging is not a stop, so the row
     count is off by one or two. Either mark those rows `"map": false`, or —
     recommended — put the lodging into `stops[0]` / `stops[-1]` (a name plus
     `lat`/`lon` is enough). Writing it in fixes the count *and* gives the day chain
     its true start and end.
   - **A displacement written as an anchor.** A fjord cruise, a scenic railway, a
     ferry crossing, a coach transfer inside a tour: the ride is the day's main
     sight, so it lands in the timeline as `kind: anchor` — and then it is not a hop
     row, while its two ends are two stops. Keep the anchor row (that is what the
     traveller reads) but **add a `kind: hop` row for the displacement itself**,
     e.g. `游船 Flåm→Gudvangen 2 h`, and put `"mode": "boat"` (or `train`/`bus`/
     `drive`/`fly`) on the arriving stop so `check` stops guessing. Leave the row
     mappable (no `map:false`) when both ends are in `stops` — that is what pairs it
     with the geometry hop between them. Same rule for a coach that moves you
     between cities mid-day.
   - **Intercity rail / flight rows — the `map:false` truth** (two testers were
     misled by an older sentence that said "legs rows take `map:false`"; the rule is
     about the *stops*, not the row): if **both stations/airports are in that day's
     `stops`** (Xi'an North → Beijing West, both written as stops), the hop **exists
     in the geometry chain**, so the row **stays mappable** — it gets no link (long
     leg, see below) but it holds its place and the count stays aligned. Only a row
     whose ends are **not** in `stops` — the leg is described by `legs[]` alone and
     the timeline hop row is just a reminder — takes `"map": false`, so it drops out
     of the count. Getting this backwards on a day with a rail leg parks every link
     of that day (`N rows vs N+1 hops`).
   - **A day that returns the way it came** (one road in and out, up the valley and
     back): only the outbound chain rows stay mappable; every retraced return row
     takes `"map": false` — its geometry already exists in the forward direction,
     so a mappable return row would demand a hop the day's chain does not have.
   **Three more shapes that go quietly wrong** (all three on one Morocco day — 13
   links parked on the first `--write`, then every later pairing off by one; the
   command itself was green):
   - **One row covering two hops.** `机场 → 卡萨中转站 → 马拉喀什` written as one
     line while `stops` has all three places ⇒ 3 stops, 1 row. Correct: two hop rows
     (`机场→卡萨中转站`, `卡萨中转站→马拉喀什`), or drop the middle place from
     `stops` if nothing happens there.
   - **Out-and-back with no return row.** Walk up to the Spanish Mosque viewpoint and
     back down: the return is not a new stop, so it feels like no hop — but if the
     viewpoint is in `stops` and the next stop is back in the medina, the walk down
     *is* the hop into that stop and needs its own `步行 西班牙清真寺→…` row.
     (Alternative: keep the viewpoint out of `stops` and mark the whole excursion a
     `kind: anchor` block; then no rows either way.)
   - **The 100 m hop that doesn't feel like one.** Blue Gate → Bou Inania is two
     stops in `stops`, so it is one hop and needs a row even if it is a two-minute
     stroll (`步行 蓝门→布伊纳尼亚 0.1 km · 2分`). Any consecutive pair in `stops`
     with no row between them shifts every pairing after it.
   Rule of thumb: walk the timeline top to bottom, and for every consecutive pair in
   `stops` there must be exactly one hop row between them, and that row's `what`
   should carry both stop names (`A→B`) — `links --write` prints the pairing it
   made so you can see it, and parks a row whose text names a *different* stop of
   the day. Declared `fly`/`boat` rows and legs over 100 km stay in the
   count and simply get no link (a declared `train`/`bus` under 100 km still gets a transit link) (the script says so per row) — do **not** answer
   that note by adding `map:false`, or every pairing after it shifts.
2. `python3 scripts/route_tools.py geocode plan.geo.json` — Nominatim/OSM, keyless; the
   script enforces the usage policy (User-Agent, 1 req/s throttle, cache) and prints
   what each stop resolved to, so a wrong-city hit is visible immediately, and
   **WARNs when the resolved `display_name` does not contain the query's head
   token** — the first Latin word of ≥4 letters, or the first 2 CJK characters
   (`Gōra Station` → a hit whose name starts elsewhere ≈ 600 m off;
   `Sannenzaka` → a guesthouse named after the street) — a WARN there means "hand
   check", not "fine". A miss is usually a bad query string: re-query with the
   local-language name and drop the neighborhood token (`八坂神社, 京都市東山区`)
   before spending a browser trip. Only then copy coordinates from the Google Maps
   place card into `plan.geo.json` — a re-run preserves anything already filled in
   there. **Hand-filling `lat/lon` for anything famous, marked `est`, is the
   normal path, not a workaround** — Nominatim is weak on non-Latin names (Japanese,
   Chinese, Korean, Thai…) and the Italy and China tests ran with 0 Nominatim
   requests, every stop pre-filled ±100 m; `geocode` then runs as a no-op.
3. `... check plan.geo.json` — distances with walk/transit duration estimates. It
   flags hops >1.6 km (take transit), >12 km with no declared mode (probably a
   clustering mistake), and days over 8 km on foot, and exits non-zero when a day
   is broken — **exit 0 is the acceptance bar before rendering** (SKILL.md Phase 4),
   the same way `links` accepts only `parked 0 / suspicious 0`. Declared `fly/drive/boat/train/bus` hops are reported as such, not as
   suspicious. Its transit estimate is a distance formula: for any transit hop
   **>20 km** it prints "use the operator timetable" instead of a number — obey it
   (a 19-min airport express was estimated at 195-285 min). Catch these BEFORE
   scheduling, not after.
4. `... links plan.geo.json --write [--provider google|apple|amap]` — per-hop deep
   links (mode from each stop's `mode`, else guessed from distance) + a whole-day
   overview link, written straight into the timeline's hop rows and `day_map`.
   Default provider is Google; for mainland China pass `--provider amap` (or
   `apple`) — see "Google Maps is unavailable in some destinations". Use `--write`: transcribing
   180-character URLs by hand is the most error-prone step in the pipeline, and a
   mis-paste puts the wrong directions on a stop with nothing to catch it.
   **Read its output, don't just look for "wrote"** — the first unfamiliar-trip
   tests each shipped a day where the row count matched by coincidence and a
   `Central→Fish Market` row got the airport link. Since then `--write`:
   - prints, for every hop row it is about to fill, `row "<what>"  ←  <origin name>
     → <destination name>` — scan that column: the two names on the right must be
     the two names in the row text on the left;
   - **refuses to write a row whose text names another stop of the day** (the words
     around the arrow mention a stop that is not this hop's origin/destination —
     the classic one-off shift) — that URL is **parked** in `day["hop_links"]`
     (rendered as a hop-by-hop maps row) instead of being written to the wrong
     line, and the row is named so you can fix it (add the missing stop, mark the
     lodging/legs row `map:false`, or correct the names) and re-run. A row that
     names *neither* endpoint is still written — that is why the printed pairing
     must be read;
   - writes **no link at all for legs over 100 km or declared `fly`/`boat`** (a
     `travelmode=transit` link across 1,971 km is never right): the row is kept in
     the count for alignment and gets a per-row note; nothing is parked;
   - ends the run with `wrote N / parked M / suspicious K; long legs kept unlinked
     (expected): L`. Anything other than `parked 0 / suspicious 0` is a to-do, not
     a warning to scroll past; `L` is **not** a failure counter — it is the number
     of rail/boat/flight rows that correctly got no link (a tester read the older
     `(long legs without link: 1)` as a fourth kind of error; it never was).
     **`parked > 0` still exits 0** — the plan is renderable, the links just moved
     to the hop-by-hop maps row — but stderr carries a loud `WARN` block naming
     each parked row; go back and read it before rendering. `check` will not catch
     this later, and the page degrades silently from tappable rows to a bare
     per-hop list.
   - How the name check matches (so you can predict a park instead of discovering
     it): stop names of the day are tried **longest first**; Latin names match on
     **word boundaries** (`Mural` no longer fires inside `Muralismo`; `centro`
     inside `Centro Cultural` still does — it is a whole word); a CJK stop name that
     is a **substring of this hop's own endpoint name does not count as "another
     stop"** (`格雷梅` inside `格雷梅露天博物馆→乌奇希萨尔` is fine now). What still
     parks a row: an *unrelated* stop of the day named in the arrow context. So keep
     street names, hotel names and asides out of the arrow context — after ` · ` or
     in parentheses — and prefer distinct names for the day's stops: **stop names on
     one day should not be prefixes/substrings of each other** (Chinese place names
     love shared prefixes — 格雷梅 / 格雷梅露天博物馆 / 格雷梅长途车站; write
     格雷梅镇中心, or add the venue word). Generic tokens (`centro`, `hotel`, `museo`,
     `market`) as a whole stop name are the Latin version of the same trap.
   - `--provider google` prints the mainland-China WARN ("re-run with --provider
     amap/apple") **only when it actually writes a Google link whose endpoint lies in
     mainland China** — a Shanghai departure airport on a day whose hop rows are all
     `map:false` no longer triggers it (a Chinese origin is normal on an outbound
     trip). If you do see it, some written link *is* dead on the ground: fix it.
   After it runs, spot-check by opening two links per day on the browser pane — a
   deep link is the one artifact the reader taps blind on the street.
5. `... kml plan.geo.json -o trip.kml` — numbered pins + a route line per day.
   Deliver the KML next to the HTML plan.
6. Browser-verify the load-bearing hops (rules below), then write the hop rows into
   the timeline.

## Link recipes (what route_tools emits with the default `--provider google`)

- Single hop:
  `https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={lat},{lon}&travelmode=walking|transit|driving`
  Coordinates beat names in these links — names can match the wrong branch/city.
- Whole-day chain: same URL + `&waypoints=p1%7Cp2…` — **max 9 waypoints** (and only
  **3 on mobile browsers**), and Google **ignores waypoints in transit mode**, so
  chains are emitted as walking. That mobile cap is why the chain is presented as the
  day's visual overview only: real navigation on the road uses the per-hop links,
  which have no waypoints. More than ~11 stops → the script splits the chain into
  overlapping segments.

## Google Maps is unavailable in some destinations

Every link above is a Google Maps URL by default, and **in mainland China (and any
other walled destination) a Google Maps link is dead on the ground** — the NYC→China
test shipped 30 of them before anyone noticed. `route_tools.py links` therefore takes
`--provider google|apple|amap` (default `google`):

- `--provider google` — the default recipe below; opens the native app on iOS and
  Android. When it actually **writes a Google link with an endpoint in mainland
  China** (bounding box; HK/MO/TW excluded) it prints one **WARN** — "… Google Maps
  is not reachable there; re-run with --provider amap (高德, keyless) or --provider
  apple" — and still writes, so a plan built by habit is caught before it ships.
  A mainland stop that gets no link (`map:false` rows, a fly leg out of PVG) does
  not trigger it. The run also prints `map provider: <name>` first, so the choice
  is on record.
- `--provider amap` — 高德 per-hop links
  (`https://uri.amap.com/navigation?from=lon,lat,name&to=lon,lat,name&mode=walk|bus|car`,
  keyless). **Per-hop links only: no DAY CHAIN / `day_map` is emitted** (高德's
  keyless URI has no multi-point form; the script prints "DAY CHAIN not available
  for amap — per-hop links only" and, with `--write`, removes a stale `day_map`) —
  the day-overview slot stays empty and the plan says so; navigation on the ground
  is per hop anyway. Spot-check two links per day in the browser pane as usual: OSM
  coordinates are WGS-84 and Chinese map apps draw on the GCJ-02 datum, so a pin
  can sit a few hundred metres off — acceptable for "open directions to X", and the
  reason the KML pins are labelled `est` there.
- `--provider apple` — Apple Maps links
  (`https://maps.apple.com/?saddr=lat,lon&daddr=lat,lon&dirflg=w|r|d`); works
  inside China (Apple Maps runs on local data there) and elsewhere, keeps the DAY
  CHAIN, opens the Apple Maps app on iOS. Use it for an iPhone traveller; Android
  users get `amap`.

Whatever the provider, **the trip KML in Organic Maps is the hard fallback** — it
needs no network and no provider — and in China the connectivity note belongs in the
plan too: a **roaming eSIM from home tunnels out** (Google works), a local SIM or the
hotel Wi-Fi does not (country-quick-notes.md, China inbound). Korea is different in
kind: Google directions are legally crippled but Google *search* works, and there is
no Naver provider — hand-write Naver search links per "Which app where".

## Hop-row format (canonical — scheduling.md and output-template.md follow this)

`模式 线路名(往…方向) 站数/分钟 票价 · 上车站→下车站 · 出口号` — in the plan's
language: mode, line (toward …), stops/minutes, fare · boarding→alighting stop ·
exit number. zh e.g. `地铁 乌丸线(往竹田方向) 4站/9分 ¥260 · 四条→京都 · 出口2`
Buses have no exit numbers and the stop count means nothing to a rider, so swap the
last field for the walk off the stop:
bus, line (toward …), ~minutes, fare · boarding→alighting stop · walk-off time;
zh e.g. `巴士 203(往銀閣寺道) ~25分 ¥230 · 祇園→銀閣寺道 · 下车步行8分`.
Walking hops shorten to walk, from→to, km · minutes — zh e.g.
`步行 清水寺→八坂神社 1.2 km · 15分`.

Exit numbers matter: in Tokyo/Seoul/Taipei the wrong exit costs 10 minutes. Capture
the exit when you browser-verify a hop. Every hop carries a verification marker —
`(verified)` or `(est.)` — in its own `verify` field in the day object
(`"verify": "verified"|"est"`), never mixed into the `tag` field, which holds only
pinned/opener/skippable/swap→X; a flight/rail hop row carries `"map": false` **only
when its two ends are not in that day's `stops`** (see the `map:false` truth in
step 1) — with both stations in `stops` the row stays mappable and simply gets no
link. Keeping these separate is what lets parallel city blocks merge without
hand-editing.

## Verify vs estimate

Browser-verify in Google Maps **at the hour the plan uses it** (frequency and routing
change by time of day):
- airport ↔ hotel, both ends of the trip
- any hop feeding a timed-entry ticket or an intercity departure
- late-evening hops — also capture the **last departure time** and write it in the plan
Everything else: route_tools estimate + `(est.)` marker. Don't burn browser time
verifying a 600 m walk. Browser map lookups do **not** count against the web-search
budget — they are not searches. If the browser is unavailable entirely, every hop
ships as a **range** with `(est.)` and lands in the ⚠️ unverified list; never convert
an estimate into a single confident number just because it looks tidier.

## Which app where

- Japan: Google Maps is reliable (Yahoo!乗換案内 for platform-level detail at complex
  stations).
- Korea: Google directions are crippled by law — plan with Naver Map / Kakao Map and
  put Naver search links (`https://map.naver.com/p/search/{query}` — the `/p/` path is
  current; pre-2023 `/v5/` links are legacy) in the plan instead of Google dir links.
- Mainland China: 高德/百度 only (Apple Maps also works, on Amap data) — Google is
  blocked, so build links with `links --provider amap` (Android) or `apple`
  (iPhone); see "Google Maps is unavailable in some destinations".
- Big Western cities: Google fine; Citymapper is often better for transit nuance.
- Default link recipe stays Google because the link opens the native app on both iOS
  and Android.

## Offline fallback

- **Organic Maps** (free, OSM): imports the trip KML — numbered pins + day lines work
  fully offline. Recommend it in every plan footer with a one-line import hint
  (download country map → bookmarks → import KML).
- Google Maps offline areas: download per city; note transit routing does not work
  offline, walking does.

## Geocoding discipline

Nominatim is a shared free service. The script already does this correctly — proper
User-Agent, ≤1 request/second, on-disk cache next to the plan (`geocache.json`) — so
never call Nominatim in parallel and never strip the throttle. Resolved stops are
cached, so re-running is nearly free; misses are deliberately **not** cached, because
a miss is almost always a fixable query string and caching it would make the retry
impossible.

Expect **national-park POIs to miss** (Old Faithful, Artist Point, Tunnel View…):
OSM names them inconsistently. For world-famous landmarks, hand-filling coordinates
from general knowledge is acceptable — the schematic map and KML need ±100 m, not
survey grade — mark the day's map `est` and only chase exact coordinates when a hop
calculation actually depends on them. City venues stay on the re-query-then-browser
path.

Expect **non-Latin place names to resolve badly rather than not at all** (Japanese,
Chinese, Korean, Thai…): a famous name may hard-fail (loud, fine), but a station or
a lane can land on the nearest thing with a similar name — 600 m off, silently.
`geocode` prints a **WARN when the resolved `display_name` does not contain the
query's head token** (first Latin word of ≥4 letters, or the first 2 CJK
characters); treat it as "open the coordinates and look", and for those countries prefer
pre-filled `est` coordinates plus a local-language re-query (`強羅駅` rather than
`Gora Station`) over trusting the first hit. Zero Nominatim requests on a trip is a
legitimate outcome, not a skipped step.
