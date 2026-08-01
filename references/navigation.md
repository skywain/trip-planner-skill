# Maps & navigation

Goal: every hop in the plan is tappable — it opens turn-by-turn directions in the
right app — and every day has a chained route link plus an offline fallback. Read this
together with scheduling.md before Phase 4 timeline assembly.

## The workflow

0. **Destination check**: in Korea and mainland China, Google directions are unusable
   (see "Which app where"). Still run `check` and `kml` — distances, clustering and
   offline pins stay valid — but skip the `links` output and substitute Naver / 高德
   search links in the plan, including the day-overview link.
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
   same thing the city-block calls `theme`. Add `"mode": "walk"|"transit"` to a stop
   whenever the hop **into** it is ridden (or walked against the distance guess) —
   1.4 km can be a two-stop metro ride or a pleasant walk, and only the plan knows
   which; the field decides both the walking total and which directions the tappable
   link opens. **`stops` must mirror that day's anchors plus any modelled strolls, in
   visit order** — every map artifact and the walking total are computed from it, so
   a `stops` list that disagrees with the timeline ships a map of a different day.
   Give every stop-to-stop transition its own `kind: hop` row, even a two-minute one
   out the door: N stops ⇒ N-1 hop rows is what lets `links --write` put each URL on
   the right row by itself. Model a long stroll as a stop at its midpoint or its
   kilometres never reach the walking total. (render_plan.py adds more keys to
   the same file — see its docstring.)
2. `python3 scripts/route_tools.py geocode plan.geo.json` — Nominatim/OSM, keyless; the
   script enforces the usage policy (User-Agent, 1 req/s throttle, cache) and prints
   what each stop resolved to, so a wrong-city hit is visible immediately. A miss is
   usually a bad query string: re-query with the local-language name and drop the
   neighborhood token (`八坂神社, 京都市東山区`) before spending a browser trip. Only
   then copy coordinates from the Google Maps place card into `plan.geo.json` — a
   re-run preserves anything already filled in there.
3. `... check plan.geo.json` — distances with walk/transit duration estimates. It
   flags hops >1.6 km (take transit), >12 km (probably a clustering mistake), and
   days over 8 km on foot, and exits non-zero when a day is broken. Catch these
   BEFORE scheduling, not after.
4. `... links plan.geo.json --write` — per-hop Google Maps deep links (mode from each
   stop's `mode`, else guessed from distance) + a whole-day overview link, written
   straight into the timeline's hop rows and `day_map`. Use `--write`: transcribing
   180-character URLs by hand is the most error-prone step in the pipeline, and a
   mis-paste puts the wrong directions on a stop with nothing to catch it.
5. `... kml plan.geo.json -o trip.kml` — numbered pins + a route line per day.
   Deliver the KML next to the HTML plan.
6. Browser-verify the load-bearing hops (rules below), then write the hop rows into
   the timeline.

## Link recipes (what route_tools emits)

- Single hop:
  `https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={lat},{lon}&travelmode=walking|transit|driving`
  Coordinates beat names in these links — names can match the wrong branch/city.
- Whole-day chain: same URL + `&waypoints=p1%7Cp2…` — **max 9 waypoints** (and only
  **3 on mobile browsers**), and Google **ignores waypoints in transit mode**, so
  chains are emitted as walking. That mobile cap is why the chain is presented as the
  day's visual overview only: real navigation on the road uses the per-hop links,
  which have no waypoints. More than ~11 stops → the script splits the chain into
  overlapping segments.

## Hop-row format (canonical — scheduling.md and output-template.md follow this)

`模式 线路名(往…方向) 站数/分钟 票价 · 上车站→下车站 · 出口号`, e.g.
`地铁 乌丸线(往竹田方向) 4站/9分 ¥260 · 四条→京都 · 出口2`
Buses have no exit numbers and the stop count means nothing to a rider, so swap the
last field for the walk off the stop:
`巴士 203(往銀閣寺道) ~25分 ¥230 · 祇園→銀閣寺道 · 下车步行8分`.
Walking hops shorten to `步行 {from}→{to} {km} · {min}分`.

Exit numbers matter: in Tokyo/Seoul/Taipei the wrong exit costs 10 minutes. Capture
the exit when you browser-verify a hop. Every hop carries a verification marker —
`(verified)` or `(est.)` — in its own `verify` field in the city-block YAML
(`verify: verified|est`), never mixed into the `tag` field, which holds only
pinned/opener/skippable/swap→X. Keeping them separate is what lets parallel city
blocks merge without hand-editing.

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
- Mainland China: 高德/百度 only.
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
