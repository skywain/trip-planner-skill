#!/usr/bin/env python3
"""Day-route toolbox for the trip-planner skill (stdlib only, Python 3.9+).

Input: a plan JSON — the SAME file render_plan.py consumes, so the map links, the
KML and the written plan can never drift apart:
{
  "trip": "kyoto-oct",
  "tz": "Asia/Tokyo",                      # optional, IANA name; days may override
  "days": [
    {"date": "2026-10-05", "label": "East Kyoto", "tz": "Asia/Tokyo",
     "stops": [
       {"name": "清水寺", "query": "Kiyomizu-dera, Kyoto, Japan"},
       {"name": "Nishiki Market", "lat": 35.005, "lon": 135.764, "mode": "transit"}
     ]}
  ]
}
"query" defaults to "name"; a stop with lat/lon pre-filled skips geocoding; a day
with no stops (a travel day) is fine.

Optional stop "mode" describes the hop INTO that stop and overrides the distance
guess. Values: "walk" | "transit" | "fly" | "drive" | "boat" | "train" | "bus".
Set it whenever the traveller rides a short hop or walks a long one, because it
decides both the walking total and which directions the tappable link opens. Model
a long stroll as a stop at its midpoint, otherwise its kilometres never reach the
walking total. A hop with NO mode is GUESSED from straight-line distance
(<=1.6 km walk, else transit); `check` reports guessed and declared totals apart
and only a hop that is both undeclared AND >12 km counts as SUSPICIOUS (exit 2) —
a declared fly/drive/boat/train/bus hop of any length is a normal itinerary shape,
never a failure.

Timeline hop rows and map links (links --write): hop rows (kind:"hop", map != false)
correspond 1:1, IN ORDER, with the stop-to-stop hops of that day. Two shapes break
that silently and MUST be handled in the plan: the FIRST hop of a day (lodging ->
first stop) and the LAST hop (-> lodging) either carry "map": false, or the lodging
itself is written into stops[0] / stops[-1].
Rail / flight / boat rows — the ONE rule ("map": false depends on the stops list,
not on the vehicle):
  * both ends ARE in that day's stops[] (e.g. stops: [..., 西安北站, 北京西站, ...])
    -> leave the row mappable (NO "map": false). It is one of the day's hops, so it
       keeps the count aligned; `links --write` writes NO link onto it (long leg,
       kept for alignment) and says so.
  * the leg is covered only by legs[] and its stations are NOT in stops[]
    (e.g. stops jump from a Rome museum straight to a Florence piazza)
    -> mark the row "map": false, so it sits outside the stop-to-stop pairing.
  Getting this wrong is silent-ish: N rows vs N+1 hops -> the whole day is parked in
  day["hop_links"] (a WARN tells you), or every later pairing shifts by one.
`links --write` prints the origin -> destination place names next to the row text
it wrote to, refuses a row that names a different stop of the day (weak name check;
the URL is parked in day["hop_links"] instead), and never emits a transit deep link
for a hop >100 km or a declared fly/boat hop (those are covered by legs[]/the
operator's link) — such rows are counted as "long legs kept unlinked (expected)".
The name check (Mexico F2, Turkey F3): only the text around the arrow counts; a
match is case/accent-insensitive and, for Latin words, whole-word ("Mural" does not
hit "Muralismo"); LONGEST FIRST — another stop's name that is a substring of one of
this hop's endpoint names ("格雷梅" inside "格雷梅露天博物馆", "centro" inside
"Hotel · Oaxaca centro") is not a hit, but a longer other-stop name that CONTAINS
the endpoint's name is; a token shared by two differently-named stops of the day
("centro", "Museo") is generic and never a hit on its own. Parking is the designed
fallback and keeps exit 0, but whenever parked > 0 the run ends with a loud stderr
WARN block listing every parked row (day, row number, first 40 chars) — read it.

Map provider (links --provider google|apple|amap, default google):
  google  https://www.google.com/maps/dir/?api=1&origin=..&destination=..&travelmode=..
  apple   https://maps.apple.com/?saddr=lat,lon&daddr=lat,lon&dirflg=w|r|d
  amap    https://uri.amap.com/navigation?from=lon,lat,name&to=lon,lat,name
          &mode=walk|bus|car&src=trip-planner   (keyless; 高德, works in mainland CN)
When the provider is google and a link is actually printed/written whose endpoint
lies in mainland China (coarse polygon, HK/MO/TW excluded), one WARN reminds you
that Google Maps is unreachable behind the GFW and suggests --provider amap or
apple. A Chinese stop by itself (the usual departure airport, its rows map:false)
does not warn (Turkey F8). Whole-day DAY CHAIN links (multi-point) exist for google
and apple only; amap gets per-hop links and no day_map.

Name the file plan.geo.json from the start: geocode then edits it in place and every
later command reads the one file that has everything.

Subcommands:
  geocode plan.geo.json       -> resolves stops in place (+ geocache.json), via
                                 Nominatim/OSM; existing coordinates are PRESERVED
  check   plan.geo.json       -> hop distances (straight-line), walk/transit
                                 estimates marked (est), on-foot vs ridden totals
                                 split into declared / guessed; warns (stderr) when a
                                 day has 0 km on foot but >=2 anchor rows; exits 2
                                 only on an undeclared suspicious hop or a hop with
                                 missing coordinates
  links   plan.geo.json [--write] [--provider google|apple|amap]
                              -> per-hop map links + whole-day chain links;
                                 --write injects them into the plan's hop rows and
                                 ends with a "wrote / parked / suspicious" summary
  kml     plan.geo.json -o trip.kml  -> numbered pins + day route lines
                                        (import into Organic Maps / Google My Maps)
  sun     plan.geo.json [--write] [--tz auto|Area/City] [--only DATE,...] [--lang zh|en]
                              -> per-day civil dawn / sunrise / sunset from
                                 api.sunrise-sunset.org (city-level: the day's first
                                 stop with coordinates; on a MOVING day — travel_day
                                 true, or first and last stop >150 km apart — the LAST
                                 stop with coordinates, because that is where the
                                 evening is spent; day["sun_stop"] = a stop's name or
                                 0-based index in stops[] overrides that pick — e.g.
                                 a "sunrise in Chefchaouen, then fly to Casablanca"
                                 day whose timeline hangs on the FIRST city — the
                                 pick reason then prints "sun_stop=…"; unknown or
                                 coordinate-less -> WARN + old rule), cross-checked
                                 against a local solar model before anything is
                                 written; --write sets day["sun"] to the canonical string
                                 "天亮 HH:MM · ☀ HH:MM / 🌇 HH:MM · TZ · sunrise-sunset.org"
                                 (--lang en, or plan.lang / plan.meta.lang == "en":
                                 "dawn HH:MM · ☀ HH:MM / 🌇 HH:MM · TZ · sunrise-sunset.org")
                                 (renderers take the first HH:MM after 🌇 — keep a
                                 space after every time). Cached in suncache.json next
                                 to the plan, so re-runs on the same day are free.

Time zone for `sun`: day["tz"] > --tz Area/City > plan["tz"] / plan["meta"]["tz"] >
longitude-derived UTC offset (approximate, no DST — printed but NEVER written; pass
--tz or set tz in the plan to write those days).

Sanity checks in `sun` (why they exist: a broken request once returned "equator,
today" with status OK and nearly shipped as Norwegian October data): status must be
OK; the returned local date must equal the requested date; sunrise/sunset must agree
with the local NOAA solar model within 12 min; day length must match within 20 min;
two different days must not come back byte-identical. Any failure -> that day is
reported on stderr and NOT written, and the command exits 3. Every day that ends up
NOT written (no ISO date, no coordinates, approximate tz, request failed, rejected)
gets its own WARN line on stderr and the closing summary lists them by date — do not
count the written days yourself (a day with no stops at all is informational, not
counted). Exit codes of `sun`: 0 = every day handled; 1 = at
least one day NOT written (the others ARE written — re-run `sun --write --only
DATE[,DATE]` for the listed dates; a request/TLS failure just needs the retry, a
missing date / coordinates / approximate tz needs the plan fixed); 3 = a day was
REJECTED by the sanity checks (look before retrying). Non-zero always means "some
day has no sun value from this run" — the file may still have been updated.

Nominatim usage policy is enforced here (User-Agent, 1 req/s, cache) — do not
parallelize around this script and do not strip the throttle. sunrise-sunset.org is
called with the same User-Agent (urllib without one gets 403). geocode also warns
when a hit's display_name does not contain the query's head token (first Latin word
of >=4 letters, or the first 2 CJK characters) — Nominatim happily returns a
guesthouse named after the street, or a bus stop 600 m from the station; that WARN
means "open the coordinates and look before trusting them".

Change log (2026-08-15, after the AU / Nordic test runs):
- links --write: per-link origin -> destination names printed against the row text;
  weak stop-name mismatch check; no transit link >100 km or for fly/boat; summary.
- check: declared vs guessed totals; 0-km-on-foot warning; new long-hop modes do not
  trip exit 2; transit >20 km prints "use the operator timetable" instead of a 4-10x
  overestimated range; (est) markers; warnings on stderr.
- new `sun` subcommand with cache + sanity checks (Nordic F1, AU F7).
Change log (2026-08-15 b, after the China / Italy / Japan runs):
- one consistent rule for "map": false on rail/flight rows (docstring, WARNs, --help
  used to contradict each other — China F2, Italy F2).
- sun: moving days use the last stop; every unwritten day is a WARN + listed (Italy F5,
  China #9).
- links: "long legs kept unlinked (expected)" wording (Japan F11); --provider
  google|apple|amap + mainland-China warning.
Change log (2026-08-15 c, i18n):
- sun: --lang zh|en (default plan.lang > plan.meta.lang > zh) picks the dawn word
  ("天亮" / "dawn"); the renderers accept either spelling. zh output unchanged.
- geocode: head-token WARN on Nominatim hits (Japan F5).
Change log (2026-08-16, after the Mexico / Morocco / Turkey / Vietnam runs):
- links: name check is whole-word + folded for Latin, longest-first / substring-of-
  endpoint rule for CJK, generic shared tokens ignored (Mexico F2, Turkey F3);
  parked > 0 ends with a loud stderr WARN listing the parked rows, exit still 0
  (Morocco F6); the mainland-China WARN fires only for links actually printed /
  written into China, and the China test is a coarse polygon instead of a box that
  swallowed Hanoi (Turkey F8).
- sun: day["sun_stop"] (name or 0-based index) overrides the first/last-stop pick
  (Morocco F5); exit 1 whenever a day was skipped / failed, after writing the good
  days (Vietnam F6); a request failure is a skip (exit 1), not a "rejection" (3).
"""
import argparse
import datetime as _dt
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "trip-planner-skill/1.3 (personal trip planning script)"}
WALK_MIN_PER_KM = 14          # tourist pace incl. lights/photos
MAX_WALK_KM = 1.6             # beyond this, guess transit
DAY_WALK_FLAG_KM = 8.0
SUSPICIOUS_KM = 12.0          # undeclared hop longer than this: same day? same city?
TRANSIT_EST_MAX_KM = 20.0     # beyond this a straight-line minute range is fiction
LINK_MAX_KM = 100.0           # beyond this no Google Maps deep link at all
SUN_MOVE_KM = 150.0           # first->last stop farther than this: the day moved city
LONG_MODES = ("fly", "drive", "boat", "train", "bus")
KNOWN_MODES = ("walk", "transit") + LONG_MODES
PROVIDERS = ("google", "apple", "amap")
# Mainland China outline as a coarse (lat, lon) polygon, minus HK / Macau / Taiwan
# boxes. Coarse on purpose (~10-30 km at the borders): it only decides whether to
# print one WARN. A polygon, not a bounding box, because the box used to swallow
# Hanoi, Ulaanbaatar, Delhi and Chiang Mai (Vietnam run: "20 stops in mainland CN").
_CN_POLY = (
    (39.4, 73.6), (40.4, 75.0), (41.0, 76.9), (42.0, 80.2), (43.1, 80.4),
    (44.6, 80.0), (45.2, 82.4), (46.0, 82.4), (47.3, 82.9), (48.4, 85.6),
    (49.2, 87.4), (48.5, 89.5), (46.9, 90.7), (45.0, 91.0), (44.0, 95.5),
    (42.8, 96.4), (42.6, 100.0), (42.4, 101.8), (41.7, 104.5), (42.4, 107.5),
    (42.5, 109.5), (43.7, 111.9), (44.9, 113.7), (45.4, 115.8), (46.4, 117.4),
    (46.7, 119.9), (47.7, 117.6), (49.9, 116.7), (51.5, 120.0), (53.3, 121.5),
    (53.6, 123.7), (52.7, 126.5), (50.3, 127.6), (49.4, 129.5), (48.4, 135.0),
    (47.7, 134.6), (45.3, 133.5), (44.5, 131.3), (43.4, 131.3), (42.4, 130.7),
    (42.0, 128.4), (41.8, 127.1), (41.2, 126.4), (40.6, 124.9), (40.1, 124.4),
    (38.7, 121.2), (37.4, 122.8), (36.0, 120.6), (34.6, 119.5), (32.2, 121.9),
    (30.5, 122.4), (28.3, 121.9), (26.3, 120.0), (24.6, 118.8), (23.5, 117.5),
    (22.6, 114.9), (21.9, 113.1), (21.4, 111.5), (20.3, 110.5), (19.8, 111.2),
    (18.0, 110.4), (18.1, 108.5), (20.9, 109.4), (21.4, 108.0), (21.55, 107.4),
    (21.95, 106.65), (22.6, 106.7), (22.9, 106.3), (23.0, 105.5), (22.9, 104.5),
    (22.6, 103.9), (22.6, 103.0), (22.4, 102.2), (21.5, 101.75), (21.15, 101.7),
    (21.45, 101.15), (21.7, 100.1), (22.2, 99.4), (23.4, 98.9), (23.95, 97.6),
    (24.3, 97.6), (25.0, 98.2), (26.0, 98.4), (27.7, 98.4), (28.3, 97.5),
    (29.4, 96.1), (28.9, 94.9), (28.3, 93.0), (27.9, 92.0), (28.3, 91.5),
    (28.0, 89.6), (28.1, 88.9), (27.9, 88.1), (27.9, 86.6), (28.2, 85.4),
    (28.7, 84.4), (29.3, 84.0), (30.2, 81.0), (31.2, 79.2), (32.5, 78.5),
    (33.4, 78.9), (34.5, 78.6), (35.5, 78.0), (35.9, 76.6), (37.0, 74.9),
    (38.5, 74.0))
_NOT_MAINLAND = ((22.15, 22.60, 113.80, 114.45),     # Hong Kong
                 (22.10, 22.22, 113.52, 113.62),     # Macau
                 (21.80, 25.40, 119.30, 122.10))     # Taiwan
DAY_COLORS = ["ff0000ff", "ffff0000", "ff00aa00",
              "ff00aaff", "ffaa00aa", "ff777777"]   # KML aabbggrr
SHAPE = ('Expected: {"days":[{"date":"...","label":"...",'
         '"stops":[{"name":"...","query":"..."}]}]}')


def warn(msg):
    """All warnings go to stderr so stdout stays a clean report."""
    print("WARN: " + msg, file=sys.stderr)


def read_json(path, what="file"):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as ex:
        sys.exit("Cannot read {} ({}): {}".format(path, what, ex))
    except UnicodeDecodeError as ex:
        sys.exit("{} is not UTF-8: {}".format(path, ex))
    try:
        return json.loads(raw)
    except ValueError as ex:
        sys.exit("{} is not valid JSON: {}\n{}".format(path, ex, SHAPE))


def load_plan(path):
    plan = read_json(path, "plan")
    if not isinstance(plan, dict) or not isinstance(plan.get("days"), list):
        sys.exit('{} has no "days" list.\n{}'.format(path, SHAPE))
    problems = []
    for i, day in enumerate(plan["days"], 1):
        if not isinstance(day, dict):
            sys.exit("days[{}] must be an object.\n{}".format(i, SHAPE))
        # Days with no mapped stops are normal (travel day, rest day) — tolerate.
        day.setdefault("stops", [])
        if not isinstance(day["stops"], list):
            sys.exit('days[{}]["stops"] must be a list.\n{}'.format(i, SHAPE))
        where = "day {} ({!r}), stop {}"
        for j, s in enumerate(day["stops"], 1):
            if not isinstance(s, dict):
                problems.append((where.format(i, day.get("label", ""), j),
                                 "must be an object, got {!r}".format(s)))
                continue
            s.setdefault("name", s.get("query") or "stop {}".format(j))
            for k in ("lat", "lon"):
                if s.get(k) is None:
                    continue
                try:
                    s[k] = float(s[k])
                except (TypeError, ValueError):
                    problems.append((
                        where.format(i, day.get("label", ""), j),
                        "{}={!r} is not a number (use decimal degrees, "
                        "e.g. 34.9949)".format(k, s[k])))
            m = s.get("mode")
            if m is not None and m not in KNOWN_MODES:
                warn("{}: unknown mode {!r} — treated as undeclared (known: {})"
                     .format(where.format(i, day.get("label", ""), j), m,
                             "|".join(KNOWN_MODES)))
                s["mode"] = None
    if problems:
        # Report every bad stop at once so the file gets fixed in one pass.
        sys.exit("\n".join("{}: {}".format(w, m) for w, m in problems))
    return plan


def coords(stop):
    if stop.get("lat") is not None and stop.get("lon") is not None:
        return stop["lat"], stop["lon"]
    return None


def haversine_km(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def r5(x):
    return int(round(x / 5.0)) * 5


def hop_estimate(km, mode=None):
    """Classify one hop. Returns (cat, declared, verdict, dur):
      cat      'walk' | 'transit' | one of LONG_MODES | 'suspicious'
      declared True when the plan said so, False when guessed from distance
      verdict  human label, always carrying (declared)/(guessed)
      dur      duration string marked (est), or None when we refuse to guess
    Distance alone cannot know whether a traveller rides a 1.4 km hop or walks it,
    and that single fact decides both the walking total and which directions the
    tappable link opens — so when the plan knows, it says so. Transit <=20 km gets a
    RANGE (a straight line cannot know the line, the headway, or the walk to the
    platform); transit >20 km gets NO minutes at all — airport expresses, tunnels
    and dedicated lines were being overestimated 4-10x, which is worse than nothing."""
    declared = mode is not None
    tag = " (declared)" if declared else " (guessed)"
    if mode in LONG_MODES:
        return mode, True, mode.upper() + tag, None
    if not declared and km > SUSPICIOUS_KM:
        return ("suspicious", False,
                "SUSPICIOUS (>{:.0f} km straight-line, no mode — same day? same "
                "city? declare mode fly/drive/boat/train/bus if intended)"
                .format(SUSPICIOUS_KM), None)
    walking = mode == "walk" or (not declared and km <= MAX_WALK_KM)
    if walking:
        return ("walk", declared, "walk" + tag,
                "~{} min (est)".format(max(5, r5(km * WALK_MIN_PER_KM))))
    if km > TRANSIT_EST_MAX_KM:
        return ("transit", declared, "TRANSIT" + tag,
                "{:.0f} km · use the operator timetable".format(km))
    mins = km * 6 + 8              # ~6 min/km in-vehicle + access/wait allowance
    return ("transit", declared, "TRANSIT" + tag,
            "~{}-{} min (est)".format(max(15, r5(mins * 0.85)), r5(mins * 1.25)))


def gmaps_dir(o, d, mode, waypoints=None):
    p = [("api", "1"),
         ("origin", "{:.6f},{:.6f}".format(*o)),
         ("destination", "{:.6f},{:.6f}".format(*d)),
         ("travelmode", mode)]
    if waypoints:
        p.append(("waypoints",
                  "|".join("{:.6f},{:.6f}".format(*w) for w in waypoints)))
    return "https://www.google.com/maps/dir/?" + urllib.parse.urlencode(p)


def _ll(c):
    return "{:.6f},{:.6f}".format(*c)


def dir_url(provider, o, d, mode, waypoints=None, names=None):
    """One directions deep link. mode is the google vocabulary ("walking" |
    "transit" | "driving"); the other providers are mapped from it:
      apple  dirflg w | r | d          (maps.apple.com/?saddr&daddr)
      amap   mode   walk | bus | car   (uri.amap.com/navigation, keyless; from/to
             carry lon,lat,NAME — 高德 puts the name on the pin)
    waypoints (list of (lat, lon)) build a multi-point chain: google via
    &waypoints=, apple via daddr=A+to:B+to:C (iOS 16+ multi-stop; older iOS opens
    only the last leg). amap has no keyless multi-point form -> ValueError, callers
    print per-hop links only."""
    if provider == "google":
        return gmaps_dir(o, d, mode, waypoints)
    if provider == "apple":
        flag = {"walking": "w", "transit": "r", "driving": "d"}[mode]
        daddr = "+to:".join(_ll(c) for c in list(waypoints or []) + [d])
        return ("https://maps.apple.com/?saddr={}&daddr={}&dirflg={}"
                .format(_ll(o), daddr, flag))
    if provider == "amap":
        if waypoints:
            raise ValueError("amap: no keyless multi-point navigation link")
        na, nb = (names or ("起点", "终点"))
        amode = {"walking": "walk", "transit": "bus", "driving": "car"}[mode]
        # 高德 wants lon,lat (the opposite of Google/Apple) and the name in the same
        # comma-separated field, so encode each field by hand.
        return ("https://uri.amap.com/navigation?from={},{}&to={},{}&mode={}"
                "&src=trip-planner".format(
                    "{:.6f},{:.6f}".format(o[1], o[0]),
                    urllib.parse.quote(str(na)[:40], safe=""),
                    "{:.6f},{:.6f}".format(d[1], d[0]),
                    urllib.parse.quote(str(nb)[:40], safe=""), amode))
    raise ValueError("unknown provider {!r}".format(provider))


def in_mainland_china(c):
    """Coarse point-in-polygon (ray casting) against _CN_POLY, then HK/MO/TW cut out."""
    lat, lon = c
    inside = False
    n = len(_CN_POLY)
    for i in range(n):
        y1, x1 = _CN_POLY[i]
        y2, x2 = _CN_POLY[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            if x1 + (lat - y1) * (x2 - x1) / (y2 - y1) > lon:
                inside = not inside
    if not inside:
        return False
    return not any(b[0] <= lat <= b[1] and b[2] <= lon <= b[3] for b in _NOT_MAINLAND)


_LATIN_WORD = re.compile(r"[A-Za-zÀ-ɏ]{4,}")
_CJK_RUN = re.compile(r"[぀-ヿ㐀-鿿]{2,}")


def _fold(s):
    """Casefold + strip diacritics ('Gōra' -> 'gora') so a macron/accent difference
    between the query and Nominatim's display_name is not a false alarm."""
    import unicodedata
    return "".join(ch for ch in unicodedata.normalize("NFKD", str(s))
                   if not unicodedata.combining(ch)).casefold()


def head_token(query):
    """The query's head token: the first CJK run (its first 2 chars) if the query
    starts with CJK, else the first Latin word of >=4 letters. None when neither
    exists (pure digits, 3-letter names) — then no check is possible."""
    q = str(query).strip()
    m_cjk, m_lat = _CJK_RUN.search(q), _LATIN_WORD.search(q)
    if m_cjk and (not m_lat or m_cjk.start() < m_lat.start()):
        return m_cjk.group(0)[:2]
    if m_lat:
        return m_lat.group(0)
    return None


def head_token_missing(query, display_name):
    """True when display_name does not contain the query's head token (Japan F5:
    'Gōra Station' resolved to a point 600 m from the station and nothing said so).
    Only a hint — the address of the right place can legitimately lack the token."""
    tok = head_token(query)
    if not tok or not display_name:
        return False
    return _fold(tok) not in _fold(display_name)


def cmd_geocode(args):
    plan = load_plan(args.plan)
    src = Path(args.plan)
    out = (src if src.stem.lower().endswith(".geo")
           else src.with_name(src.stem + ".geo.json"))

    # Carry over coordinates already present in the output file. The NOT FOUND
    # message tells people to hand-fill lat/lon there; silently clobbering that
    # work on the next run would make the advice a trap.
    kept = 0
    carried = set()
    if out != src and out.exists():
        prev = read_json(out, "previous geocode output")
        known = {}
        for day in (prev.get("days") or []):
            for s in (day.get("stops") or []):
                if isinstance(s, dict) and s.get("lat") is not None:
                    known[s.get("query") or s.get("name")] = (s["lat"], s["lon"])
        for day in plan["days"]:
            for s in day["stops"]:
                key = s.get("query") or s.get("name")
                if coords(s) is None and key in known:
                    s["lat"], s["lon"] = known[key]
                    carried.add(id(s))
                    kept += 1
    if kept:
        print("kept {} hand-entered/previous coordinate(s) from {}".format(
            kept, out.name))

    cache_path = src.parent / "geocache.json"
    cache = read_json(cache_path, "geocache") if cache_path.exists() else {}
    misses = []
    def show(stop, source, detail=""):
        # Every stop prints its provenance, so a wrong-city hit is caught here rather
        # than by the >12 km heuristic in `check` three steps later.
        print("  {:22.22} {:.5f},{:.5f}  [{}] {}".format(
            stop["name"], stop["lat"], stop["lon"], source, detail[:60]))

    for day in plan["days"]:
        for stop in day["stops"]:
            if coords(stop):
                show(stop, "carried" if id(stop) in carried else "preset")
                continue
            q = stop.get("query") or stop["name"]
            hit = cache.get(q)
            from_cache = bool(hit)
            if not hit:
                res = None
                for attempt in range(3):
                    url = ("https://nominatim.openstreetmap.org/search"
                           "?format=jsonv2&limit=1&addressdetails=0&q="
                           + urllib.parse.quote(q))
                    try:
                        with urllib.request.urlopen(
                                urllib.request.Request(url, headers=UA),
                                timeout=20) as r:
                            res = json.loads(r.read().decode("utf-8"))
                        break
                    except Exception as ex:
                        print("  attempt {}/3 failed on {!r}: {}".format(
                            attempt + 1, q, ex))
                        time.sleep(2.0)
                time.sleep(1.1)   # Nominatim policy: max 1 request/second
                if res is None:
                    misses.append(q + "  (network errors — re-run geocode)")
                    continue
                if not isinstance(res, list) or not res:
                    # Negative results are NOT cached: a miss is almost always a bad
                    # query string, and the fix is to re-query — caching null would
                    # make the retry silently impossible.
                    misses.append(q)
                    continue
                try:
                    hit = {"lat": float(res[0]["lat"]), "lon": float(res[0]["lon"]),
                           "display_name": res[0].get("display_name", "")}
                except (KeyError, TypeError, ValueError):
                    misses.append(q + "  (unexpected API response)")
                    continue
                cache[q] = hit
                cache_path.write_text(
                    json.dumps(cache, ensure_ascii=False, indent=1),
                    encoding="utf-8")
            stop["lat"], stop["lon"] = hit["lat"], hit["lon"]
            show(stop, "cache" if from_cache else "api",
                 hit.get("display_name", ""))
            if head_token_missing(q, hit.get("display_name", "")):
                warn("{!r} -> {!r}: the result does not mention {!r} — it may have "
                     "landed on the wrong place (a bus stop / guesthouse nearby). "
                     "Open {:.5f},{:.5f} on a map and check; hand-fill lat/lon if "
                     "off.".format(q, hit.get("display_name", "")[:60], head_token(q),
                                   hit["lat"], hit["lon"]))

    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", out)
    if misses:
        print("NOT FOUND — cheapest fix first: re-query with the local-language name "
              "and drop the neighborhood token (e.g. '八坂神社, 京都市東山区'). Only if "
              "that fails, open the place in Google Maps, copy the place-card "
              "coordinates, and hand-fill lat/lon into {} (re-running geocode keeps "
              "them):".format(out.name))
        for m in misses:
            print("  -", m)


def anchor_rows(day):
    return [it for it in (day.get("timeline") or [])
            if isinstance(it, dict) and it.get("kind") == "anchor"]


def cmd_check(args):
    plan = load_plan(args.plan)
    bad_days = 0
    for i, day in enumerate(plan["days"], 1):
        print("\nDay {} {} — {}".format(i, day.get("date", "?"),
                                        day.get("label", "")))
        pts = [(s, coords(s)) for s in day["stops"]]
        if len(pts) < 2:
            print("  (no hops to check — {} mapped stop(s))".format(len(pts)))
            continue
        walk = {"declared": 0.0, "guessed": 0.0}
        ride = {"declared": 0.0, "guessed": 0.0}
        rides = 0
        long_hops = []
        worst = "OK"
        for (a, ca), (b, cb) in zip(pts, pts[1:]):
            if not ca or not cb:
                print("  {} -> {}: missing coords — run geocode or fill by hand"
                      .format(a["name"], b["name"]))
                worst = "BROKEN"
                continue
            km = haversine_km(ca, cb)
            cat, declared, verdict, dur = hop_estimate(km, b.get("mode"))
            bucket = "declared" if declared else "guessed"
            if cat == "suspicious":
                worst = "SUSPICIOUS"
            elif cat == "walk":
                walk[bucket] += km
            else:
                ride[bucket] += km
                rides += 1
                if cat in LONG_MODES:
                    long_hops.append("{} {:.0f} km".format(cat, km))
            print("  {:22.22} -> {:22.22} {:6.1f} km (straight-line)  {}{}".format(
                a["name"], b["name"], km, verdict,
                "  " + dur if dur else ""))
        note = []
        if worst != "OK":
            note.append(worst + " HOPS PRESENT")
            bad_days += 1
        walk_km = walk["declared"] + walk["guessed"]
        if walk_km * 1.3 > DAY_WALK_FLAG_KM:
            note.append("ALREADY OVER {:.0f} km ON FOOT — re-cluster".format(
                DAY_WALK_FLAG_KM))
        print("  on foot: {:.1f} km (declared {:.1f} · guessed {:.1f}) → ≈{:.1f} km "
              "with real streets (est)".format(walk_km, walk["declared"],
                                               walk["guessed"], walk_km * 1.3))
        if rides:
            print("  ridden:  {:.1f} km over {} hop(s) (declared {:.1f} · guessed "
                  "{:.1f}) — not walking{}".format(
                      ride["declared"] + ride["guessed"], rides, ride["declared"],
                      ride["guessed"],
                      "  [long legs: " + ", ".join(long_hops) + "]"
                      if long_hops else ""))
        n_anchor = len(anchor_rows(day))
        if walk_km == 0 and n_anchor >= 2:
            # AU F2: two 2 km coastal-walk hops were guessed as transit and the day
            # showed 0 km on foot without a word. Anchors imply walking between them.
            warn("Day {} {}: 0 km on foot but {} anchor rows — a walking hop is "
                 "probably guessed as transit; declare \"mode\": \"walk\" on the "
                 "stop it walks INTO (or the day really is all rides — then fine)."
                 .format(i, day.get("date", "?"), n_anchor))
        print("  + in-venue walking and strolls: add your own; the {:.0f} km cap is "
              "on the SUM — {}".format(DAY_WALK_FLAG_KM,
                                       "; ".join(note) if note else "OK so far"))
    print("\nNote: distances are straight-line; real streets add ~20-30%. Every "
          "duration is an estimate (est) — browser-verify the load-bearing hops; "
          "transit >{:.0f} km and fly/drive/boat/train/bus hops get no minutes here, "
          "use the operator timetable / legs[].".format(TRANSIT_EST_MAX_KM))
    if bad_days:
        sys.exit(2)


_SPLIT = re.compile(r"\s*[·/()()\[\]【】,,]\s*|\s+")
# Generic place words in the languages the test runs hit (en/es/it/fr/pt): a token
# from this list can name half the stops of a day ("centro", "mercado", "museo"),
# so it is never evidence that a hop row points at a different stop (Mexico F2).
_STOP_TOKENS = {"the", "and", "beach", "station", "market", "park", "street",
                "hotel", "terminal", "museum", "airport", "wharf", "point", "gorge",
                "river", "lake", "bay", "hall", "tower", "bridge", "square", "road",
                "centro", "centre", "center", "downtown", "plaza", "piazza", "place",
                "mercado", "mercato", "marche", "museo", "musee", "palacio",
                "palazzo", "palace", "catedral", "cathedral", "church", "iglesia",
                "chiesa", "temple", "shrine", "mosque", "castle", "castillo",
                "castello", "garden", "gardens", "jardin", "parque", "parco",
                "port", "puerto", "porto", "harbour", "harbor", "city", "town",
                "north", "south", "east", "west", "island", "gare", "estacion",
                "stazione", "bahnhof", "aeropuerto", "aeroporto", "cafe", "hostel",
                "riad", "medina", "house", "casa", "villa", "monte", "mount"}
_CJK_CHAR = re.compile(r"[぀-ヿ㐀-鿿]")


def name_keys(stop):
    """Weak matching keys for a stop: full name, query, and its meaningful pieces
    (CJK runs of >=2 chars, Latin words of >=4 chars not in a generic stoplist)."""
    full, toks = name_keys2(stop)
    return full | toks


def name_keys2(stop):
    """(full_keys, token_keys): the stop's full name / query, and its pieces
    (CJK runs of >=2 chars, ASCII words of >=4 letters not in _STOP_TOKENS)."""
    full, toks = set(), set()
    for raw in (stop.get("name"), stop.get("query")):
        if not raw:
            continue
        raw = str(raw).strip()
        if len(raw) >= 2:
            full.add(raw)
        for tok in _SPLIT.split(raw):
            tok = tok.strip()
            if not tok:
                continue
            if re.fullmatch(r"[぀-ヿ㐀-鿿]{2,}", tok):
                toks.add(tok)
            elif (len(tok) >= 4 and tok.isascii()
                  and _fold(tok) not in _STOP_TOKENS):
                toks.add(tok)
    return full, toks - full


_KEY_RE = {}


def key_regex(key):
    """Compiled matcher for one key on FOLDED text (see _fold): case-insensitive,
    accent-insensitive, and Latin ends must sit on a word boundary — so the key
    "Mural" no longer hits "Muralismo" (Mexico F2). CJK has no spaces, so an end
    that is a CJK character gets no boundary ("格雷梅" still matches inside a run)."""
    pat = _KEY_RE.get(key)
    if pat is None:
        fk = _fold(key)
        body = re.escape(fk)
        if fk and not _CJK_CHAR.match(fk[0]):
            body = r"(?<!\w)" + body
        if fk and not _CJK_CHAR.match(fk[-1]):
            body = body + r"(?!\w)"
        pat = _KEY_RE[key] = re.compile(body)
    return pat


def foreign_stops(ctx, sa, sb, stops):
    """Names of the OTHER stops of the day that the hop row text `ctx` mentions,
    given the hop's real endpoints sa -> sb. Rules (Mexico F2, Turkey F3):
      1. matching is folded + Latin word-boundary (key_regex);
      2. longest first: a key that is a substring of an endpoint's own name/query is
         NOT a hit — "格雷梅" inside "格雷梅露天博物馆", "centro" inside "Hotel ·
         Oaxaca centro". The other way round (another stop's name CONTAINS the
         endpoint's name and appears in the text) IS a hit;
      3. a token shared by two differently-named stops of the day is generic and
         never counts (only that stop's full name/query can then name it)."""
    fctx = _fold(ctx)
    end_names = {_fold(x) for s in (sa, sb)
                 for x in (s.get("name"), s.get("query")) if x}
    own = {_fold(k) for k in name_keys(sa) | name_keys(sb)}
    tok_owner = {}
    for s in stops:
        for k in name_keys2(s)[1]:
            tok_owner.setdefault(_fold(k), set()).add(_fold(s.get("name")))
    hits = set()
    for s in stops:
        if s is sa or s is sb:
            continue
        full, toks = name_keys2(s)
        for k in full | toks:
            fk = _fold(k)
            if fk in own or any(fk in n for n in end_names):
                continue                                          # rule 2
            if k in toks and len(tok_owner.get(fk, ())) > 1:
                continue                                          # rule 3
            if key_regex(k).search(fctx):
                hits.add(s["name"])
                break
    return sorted(hits)


_ARROW = re.compile(r"\s*(?:→|->|➜|⇒)\s*")
_CTX_CUT = re.compile(r"\s·\s|[((]|\d+(?:\.\d+)?\s*(?:km|分|min)")


def arrow_context(what):
    """The part of a hop row's text that names its endpoints: the segments right
    before and after the arrow ("… · 中央车站→Fish Market 站 · 下车…" -> "中央车站",
    "Fish Market 站"). Rows without an arrow yield the whole text. Restricting the
    mismatch check to this context keeps a street name in a trailing remark
    ("(沿 Esplanade)") from colliding with a stop that happens to carry that word."""
    m = _ARROW.search(what)
    if not m:
        return what
    left = _CTX_CUT.split(what[:m.start()])[-1]
    right = _CTX_CUT.split(what[m.end():])[0]
    return left + " " + right


def cmd_links(args):
    plan = load_plan(args.plan)
    provider = getattr(args, "provider", "google") or "google"
    n_wrote = n_parked = n_susp = n_long = 0
    parked_log = []      # human lines for the closing WARN (Morocco F6)
    cn_links = []        # (day, "A → B") google links whose ends lie in mainland CN
    print("map provider: {}".format(provider))
    for i, day in enumerate(plan["days"], 1):
        print("\nDay {} {} — {}".format(i, day.get("date", "?"),
                                        day.get("label", "")))
        mapped = [s for s in day["stops"] if coords(s)]
        pts = [(s["name"], coords(s)) for s in mapped]
        skipped = len(day["stops"]) - len(pts)
        if skipped:
            print("  ({} stop(s) skipped: no coords)".format(skipped))
        hops = []   # {a, b, url|None, note, km, mode}
        for (na, ca), (nb, cb), sa, sb in zip(pts, pts[1:], mapped, mapped[1:]):
            km = haversine_km(ca, cb)
            cat, declared, verdict, dur = hop_estimate(km, sb.get("mode"))
            url, note = None, None
            if km > LINK_MAX_KM or cat in ("fly", "boat"):
                # AU F1: a 1971 km travelmode=transit deep link was written into a
                # hop row without a word. Long legs live in legs[] / the operator's
                # own link. The row stays in the count (so the day's alignment
                # holds) — it just gets no link. This is the EXPECTED shape for a
                # rail/flight row whose two stations are in stops[]; only a row
                # whose ends are NOT in stops[] takes map:false (see docstring).
                note = ("long leg ({:.0f} km, {}) — no map link written; row kept "
                        "for alignment (expected, NOT an error — do not add "
                        "map:false), book it via legs[]/operator link".format(km, cat))
                n_long += 1
            else:
                mode = ("walking" if cat == "walk" else
                        "driving" if cat == "drive" else "transit")
                url = dir_url(provider, ca, cb, mode, names=(na, nb))
                if provider == "google" and (in_mainland_china(ca)
                                             or in_mainland_china(cb)):
                    cn_links.append((i, "{} → {}".format(na, nb)))
            hops.append({"a": na, "b": nb, "sa": sa, "sb": sb, "url": url,
                         "note": note, "km": km, "verdict": verdict, "dur": dur})
            print("  {} -> {}  [{} {:.1f} km {}]\n    {}".format(
                na, nb, verdict, km, dur or "", url or note))
        if args.write and hops:
            # Hop rows correspond 1:1, in order, with the stop-to-stop hops — the
            # stops-mirror-the-timeline invariant. A flight/rail row whose stations
            # are NOT in stops[] (covered only by legs[]) carries "map": false and
            # sits outside that invariant (a day with such a flight plus 3 ground
            # hops has 4 hop rows but only 3 mapped hops). A rail row whose two
            # stations ARE in stops[] stays mappable: it is hop N of the day, gets
            # no link (long leg) but keeps the count aligned. Position pairing is
            # still weak, so every write is printed with its place names and
            # checked against the other stops' names (AU F1).
            rows = [it for it in (day.get("timeline") or [])
                    if isinstance(it, dict) and it.get("kind") == "hop"
                    and it.get("map") is not False]
            parked = []
            if len(rows) == len(hops):
                for idx, (row, h) in enumerate(zip(rows, hops), 1):
                    what = str(row.get("what", ""))
                    if h["url"] is None:
                        row.pop("link", None)
                        print("  ✎ row {} 「{}」 ← {} → {}: {}".format(
                            idx, what[:48], h["a"], h["b"], h["note"]))
                        continue
                    foreign = foreign_stops(arrow_context(what), h["sa"], h["sb"],
                                            mapped)
                    if foreign:
                        n_susp += 1
                        parked.append(h["url"])
                        parked_log.append("Day {} row {} 「{}」 (names {}; hop is "
                                          "{} → {})".format(
                                              i, idx, what[:40], ", ".join(foreign),
                                              h["a"], h["b"]))
                        row.pop("link", None)
                        warn("Day {} row {} 「{}」 names {} but the hop in this "
                             "position is {} → {} — SUSPICIOUS mismatch, link parked "
                             "in hop_links, not written. Fix: give every stop-to-stop "
                             "transition its own hop row in order; \"map\": false "
                             "only on lodging rows and on rail/flight rows whose "
                             "stations are NOT in stops[] (both ends in stops[] -> "
                             "keep the row mappable)."
                             .format(i, idx, what[:48], ", ".join(foreign),
                                     h["a"], h["b"]))
                        continue
                    row["link"] = h["url"]
                    n_wrote += 1
                    print("  ✎ row {} 「{}」 ← {} → {}".format(
                        idx, what[:48], h["a"], h["b"]))
            else:
                parked.extend(h["url"] for h in hops if h["url"])
                if parked:
                    parked_log.append("Day {}: {} mappable hop row(s) vs {} mapped "
                                      "hop(s) — all {} link(s) of the day parked"
                                      .format(i, len(rows), len(hops), len(parked)))
                for h in hops:
                    if h["url"] is None:
                        print("  ✎ {} → {}: {}".format(h["a"], h["b"], h["note"]))
                warn("Day {}: {} mappable hop rows vs {} mapped hops — links parked "
                     "in day['hop_links'] (render_plan shows them as a 逐跳导航 row). "
                     "To place them on rows: give every stop-to-stop transition its "
                     "own hop row (a rail/flight row whose two stations are in "
                     "stops[] IS one of them — keep it mappable, it just gets no "
                     "link); \"map\": false ONLY on a flight/rail row whose stations "
                     "are not in stops[], and on the lodging->first / last->lodging "
                     "rows (or put the lodging into stops[0]/stops[-1])."
                     .format(i, len(rows), len(hops)))
            n_parked += len(parked)
            # hop_links is script-owned: it holds exactly what this run could not
            # place on a row, so a stale list from an earlier run does not survive.
            if parked:
                day["hop_links"] = parked
            else:
                day.pop("hop_links", None)
        if len(pts) < 2:
            continue
        if provider == "amap":
            # 高德's keyless URI has no multi-point navigation form.
            print("  DAY CHAIN not available for amap — per-hop links only"
                  + (" (day_map removed)" if args.write and day.pop("day_map", None)
                     else ""))
            continue
        # Whole-day overview chains. Google ignores waypoints in transit mode (and
        # caps them at 3 on mobile browsers), so chains are walking-mode overviews
        # only — never navigation. Say so when the day is not actually walkable.
        for s in range(0, len(pts) - 1, 10):
            seg = pts[s:s + 11]
            if len(seg) < 2:
                break
            seg_hops = [haversine_km(a[1], b[1]) for a, b in zip(seg, seg[1:])]
            if max(seg_hops) > SUSPICIOUS_KM:
                print("  DAY CHAIN suppressed: a {:.0f} km hop makes a chained link "
                      "meaningless — use the per-hop links above.".format(
                          max(seg_hops)))
                continue
            label = ("DAY CHAIN" if max(seg_hops) <= MAX_WALK_KM else
                     "DAY CHAIN (overview only — walking mode, NOT a walking route)")
            url = dir_url(provider, seg[0][1], seg[-1][1], "walking",
                          [c for _, c in seg[1:-1]] or None)
            print("  {} {} -> {} ({} stops):\n    {}".format(
                label, seg[0][0], seg[-1][0], len(seg), url))
            if provider == "google" and any(in_mainland_china(c) for _, c in seg):
                cn_links.append((i, "DAY CHAIN {} → {}".format(seg[0][0], seg[-1][0])))
            if args.write and s == 0:
                day["day_map"] = url
    if cn_links:
        # Turkey F8: a Chinese departure airport with map:false rows used to trip
        # this on a plan that wrote zero links into China. Only links that really
        # point into mainland China count (a stop being there is normal).
        warn("{} Google Maps link(s) {} point into mainland China (first: Day {} "
             "{}) — Google Maps is not reachable there; re-run with --provider amap "
             "(高德, keyless) or --provider apple (works in CN with local data)."
             .format(len(cn_links), "written" if args.write else "printed",
                     cn_links[0][0], cn_links[0][1]))
    if args.write:
        Path(args.plan).write_text(
            json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
        # n_long is NOT a failure counter: those rows are rail/flight/boat hops
        # whose ends are in stops[] — kept for alignment, deliberately unlinked.
        print("\nupdated {} in place — wrote {} link(s) onto hop rows / parked {} in "
              "hop_links / suspicious {}; long legs kept unlinked (expected): {}"
              .format(args.plan, n_wrote, n_parked, n_susp, n_long))
        if n_susp or n_parked:
            print("Read the WARN lines on stderr before rendering.")
        if n_parked:
            # Morocco F6: 13 parked links and the command was "green". Exit code
            # stays 0 (parking is the designed fallback), but it must be visible.
            warn("==== links --write: {} link(s) PARKED in day['hop_links'], NOT on "
                 "hop rows — the page degrades to one 逐跳导航 row per such day ===="
                 .format(n_parked))
            for line in parked_log:
                warn("  parked: " + line)


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def cmd_kml(args):
    plan = load_plan(args.plan)
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
             "<name>{}</name>".format(esc(plan.get("trip", "trip")))]
    total, dropped = 0, []
    for i, day in enumerate(plan["days"], 1):
        color = DAY_COLORS[(i - 1) % len(DAY_COLORS)]
        parts.append("<Folder><name>Day {} {} — {}</name>".format(
            i, esc(day.get("date", "")), esc(day.get("label", ""))))
        line, miss = [], []
        for j, s in enumerate(day["stops"], 1):
            c = coords(s)
            if not c:
                miss.append(s["name"])
                continue
            parts.append(
                "<Placemark><name>{}. {}</name>"
                "<Point><coordinates>{:.6f},{:.6f},0</coordinates></Point>"
                "</Placemark>".format(j, esc(s["name"]), c[1], c[0]))
            line.append("{:.6f},{:.6f},0".format(c[1], c[0]))
            total += 1
        if len(line) > 1:
            parts.append(
                "<Placemark><name>Day {} route</name><Style><LineStyle>"
                "<color>{}</color><width>3</width></LineStyle></Style>"
                "<LineString><coordinates>{}</coordinates></LineString>"
                "</Placemark>".format(i, color, " ".join(line)))
        parts.append("</Folder>")
        if miss:
            dropped.append("Day {}: {}".format(i, ", ".join(miss)))
    parts.append("</Document></kml>")
    # Path.open, not write_text(newline=...) — that kwarg is 3.10+.
    with Path(args.out).open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(parts))
    print("wrote {} — {} pin(s) — import into Organic Maps (bookmarks) or "
          "Google My Maps".format(args.out, total))
    for d in dropped:
        print("  omitted (no coords) — {}".format(d))
    if total == 0:
        print("  WARNING: no pins written — run geocode first.")


# ---------------------------------------------------------------- sun -----------

def solar_events_utc(lat, lon, date, zenith=90.833):
    """NOAA-style sunrise/sunset (UTC datetimes) for one date; ~1-2 min accuracy.
    Used ONLY to sanity-check the API answer, never as the published value.
    zenith 90.833 = sunrise/sunset, 96 = civil twilight. Returns (rise, set) or
    (None, None) for polar day/night."""
    n = date.toordinal() - _dt.date(2000, 1, 1).toordinal() + 0.5 - lon / 360.0
    def _pass(rising):
        # Iterate twice: the second pass uses the improved transit time.
        jd = 2451545.0 + n
        for _ in range(2):
            t = (jd - 2451545.0) / 36525.0
            L0 = (280.46646 + t * (36000.76983 + 0.0003032 * t)) % 360
            M = math.radians((357.52911 + t * (35999.05029 - 0.0001537 * t)) % 360)
            C = ((1.914602 - t * (0.004817 + 0.000014 * t)) * math.sin(M)
                 + (0.019993 - 0.000101 * t) * math.sin(2 * M)
                 + 0.000289 * math.sin(3 * M))
            lam = math.radians(L0 + C - 0.00569
                               - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * t)))
            eps = math.radians(23.439291 - 0.0130042 * t
                               + 0.00256 * math.cos(math.radians(125.04 - 1934.136 * t)))
            dec = math.asin(math.sin(eps) * math.sin(lam))
            y = math.tan(eps / 2) ** 2
            e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)
            L0r = math.radians(L0)
            eqt = 4 * math.degrees(
                y * math.sin(2 * L0r) - 2 * e * math.sin(M)
                + 4 * e * y * math.sin(M) * math.cos(2 * L0r)
                - 0.5 * y * y * math.sin(4 * L0r) - 1.25 * e * e * math.sin(2 * M))
            cosH = ((math.cos(math.radians(zenith))
                     - math.sin(math.radians(lat)) * math.sin(dec))
                    / (math.cos(math.radians(lat)) * math.cos(dec)))
            if cosH < -1 or cosH > 1:
                return None
            H = math.degrees(math.acos(cosH))
            minutes = 720 - 4 * (lon + (H if rising else -H)) - eqt   # NOAA sign
            jd = 2451545.0 + n - 0.5 + minutes / 1440.0
        base = _dt.datetime(date.year, date.month, date.day, tzinfo=_dt.timezone.utc)
        return base + _dt.timedelta(minutes=minutes)
    return _pass(True), _pass(False)


def resolve_tz(day, plan, cli_tz, lon):
    """(ZoneInfo|fixed tzinfo, label, approx:bool). See docstring for the order."""
    name = day.get("tz")
    if not name and cli_tz and cli_tz != "auto":
        name = cli_tz
    if not name:
        name = plan.get("tz") or (plan.get("meta") or {}).get("tz")
    if name:
        try:
            from zoneinfo import ZoneInfo
            return ZoneInfo(name), name, False
        except Exception as ex:                       # unknown name / no tzdata
            warn("tz {!r} not usable ({}); falling back to a longitude offset"
                 .format(name, ex))
    off = int(round(lon / 15.0))
    return (_dt.timezone(_dt.timedelta(hours=off)),
            "UTC{:+d} (approx from longitude, no DST — pass --tz)".format(off), True)


def fetch_sun(lat, lon, date, tzid, cache, cache_path):
    key = "{:.3f},{:.3f},{},{}".format(lat, lon, date, tzid or "UTC")
    if key in cache:
        return cache[key], True, key
    q = {"lat": "{:.4f}".format(lat), "lng": "{:.4f}".format(lon),
         "date": date, "formatted": "0"}
    if tzid:
        q["tzid"] = tzid
    url = "https://api.sunrise-sunset.org/json?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    time.sleep(1.0)              # be polite; a plan is a handful of requests
    cache[key] = data
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1),
                          encoding="utf-8")
    return data, False, key


SUN_DAWN = {"zh": "天亮", "en": "dawn"}   # the renderers accept both spellings


def plan_lang(plan, arg=None):
    """--lang > plan.lang > plan.meta.lang > zh (same order as the theme renderers)."""
    for cand in (arg, plan.get("lang"), (plan.get("meta") or {}).get("lang")):
        if cand in SUN_DAWN:
            return cand
    return "zh"


def cmd_sun(args):
    plan = load_plan(args.plan)
    dawn_word = SUN_DAWN[plan_lang(plan, getattr(args, "lang", None))]
    src = Path(args.plan)
    cache_path = src.parent / "suncache.json"
    cache = read_json(cache_path, "suncache") if cache_path.exists() else {}
    only = set(x.strip() for x in (args.only or "").split(",") if x.strip())
    seen = {}            # raw (sunrise, sunset) -> "Day i date" for the identical check
    failures, written, requests = [], 0, 0   # failures = sanity-check rejections
    skipped = []         # (date, why) — every day this run did NOT write (Italy F5)
    def skip(day_date, head, why):
        skipped.append((day_date or "?", why))
        warn("{}: skipped — {}".format(head, why))
    for i, day in enumerate(plan["days"], 1):
        date = day.get("date")
        head = "Day {} {} — {}".format(i, date or "?", day.get("label", ""))
        if only and date not in only:
            continue
        if not date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(date)):
            print("{}\n  skipped: no ISO date".format(head))
            skip(date, head, "no ISO date")
            continue
        with_c = [s for s in day["stops"] if coords(s)]
        if not day["stops"]:
            # A day with NO stops at all (pure travel/rest day, e.g. the kyoto
            # sample's day 2) has nothing to compute from — informational, not
            # counted as "not written" (no exit 1 for it).
            print("{}\n  no stops (travel/rest day) — nothing to compute, not "
                  "counted; add one city-level stop if you want a sun line".format(head))
            continue
        if not with_c:
            print("{}\n  skipped: no stop with lat/lon (travel/rest day) — set one "
                  "city-level stop or leave sun as is".format(head))
            skip(date, head, "no stop with lat/lon — set one city-level stop")
            continue
        # A moving day (travel_day, or the day's first and last stop are more than
        # SUN_MOVE_KM apart) spends its evening at the LAST stop, so the sunset that
        # matters is there (China #9: Xi'an's 17:41 was written for a day that ended
        # in Beijing at 16:59). Ordinary days keep the first stop (city-level).
        span_km = haversine_km(coords(with_c[0]), coords(with_c[-1]))
        moving = bool(day.get("travel_day")) or span_km > SUN_MOVE_KM
        pick = with_c[-1] if moving else with_c[0]
        pick_why = ("last stop — moving day{}".format(
            ", first->last {:.0f} km".format(span_km) if span_km > SUN_MOVE_KM
            else " (travel_day)") if moving else "first stop")
        # Morocco F5: D9 "sunrise in Chefchaouen, then fly to Casablanca" is a moving
        # day whose whole timeline hangs on the FIRST city's sunrise. day["sun_stop"]
        # (a stop's name, or its 0-based index in stops[]) overrides the automatic
        # pick; missing / unknown / no coordinates -> WARN and the old rule applies.
        chosen = day.get("sun_stop")
        if chosen is not None:
            override = None
            if isinstance(chosen, bool):
                pass
            elif isinstance(chosen, int):
                if 0 <= chosen < len(day["stops"]):
                    override = day["stops"][chosen]
            else:
                want = str(chosen).strip()
                for s in day["stops"]:
                    if str(s.get("name", "")).strip() == want:
                        override = s
                        break
                else:
                    for s in day["stops"]:
                        if _fold(s.get("name", "")).strip() == _fold(want):
                            override = s
                            break
            if override is None:
                warn("{}: sun_stop={!r} matches no stop of the day (use a stop's "
                     "exact name or its 0-based index) — falling back to the {}"
                     .format(head, chosen, pick_why))
            elif not coords(override):
                warn("{}: sun_stop={!r} -> {!r} has no lat/lon — falling back to "
                     "the {}".format(head, chosen, override.get("name"), pick_why))
            else:
                pick = override
                pick_why = "sun_stop={!r}{}".format(
                    chosen, " (would have been the {})".format(pick_why)
                    if override is not (with_c[-1] if moving else with_c[0]) else "")
        lat, lon = coords(pick)
        tz, tzlabel, approx = resolve_tz(day, plan, args.tz, lon)
        tzid = None if approx else tzlabel
        try:
            data, cached, ckey = fetch_sun(lat, lon, date, tzid, cache, cache_path)
        except Exception as ex:
            print("{}\n  FAILED: {}".format(head, ex))
            skip(date, head, "request failed ({}) — re-run, it retries "
                 "uncached days".format(ex))
            continue
        requests += 0 if cached else 1
        res = data.get("results") if isinstance(data, dict) else None
        status = (data or {}).get("status")
        problems = []
        if status != "OK" or not isinstance(res, dict):
            problems.append("status {!r}".format(status))
        try:
            rise = _dt.datetime.fromisoformat(res["sunrise"]).astimezone(tz)
            sset = _dt.datetime.fromisoformat(res["sunset"]).astimezone(tz)
            dawn = _dt.datetime.fromisoformat(res["civil_twilight_begin"]).astimezone(tz)
        except Exception as ex:
            problems.append("unparseable times ({})".format(ex))
            rise = sset = dawn = None
        d = _dt.date.fromisoformat(date)
        if rise is not None:
            # 1. the API answered for the day we asked (the "today" bug)
            for what, t in (("sunrise", rise), ("sunset", sset)):
                if t.date() != d:
                    problems.append("{} dated {} but asked {}".format(
                        what, t.date(), d))
            # 2. and for the place we asked (the "equator" bug): local solar model
            m_rise, m_set = solar_events_utc(lat, lon, d)
            if m_rise is None:
                problems.append("polar day/night at {:.2f}N — model has no "
                                "sunrise; check by hand".format(lat))
            else:
                for what, t, m in (("sunrise", rise, m_rise), ("sunset", sset, m_set)):
                    diff = abs((t - m).total_seconds()) / 60.0
                    if diff > 12:
                        # allow the ±1 day date shift of the UTC fallback
                        diff = min(diff, abs(diff - 1440), abs(diff - 2880))
                    if diff > 12:
                        problems.append("{} {} vs local solar model {} — {:.0f} min "
                                        "apart (wrong place/date?)".format(
                                            what, t.strftime("%H:%M"),
                                            m.astimezone(tz).strftime("%H:%M"), diff))
                api_len = (sset - rise).total_seconds() / 60.0
                mod_len = (m_set - m_rise).total_seconds() / 60.0
                if abs(api_len - mod_len) > 20:
                    problems.append("day length {:.0f} min vs model {:.0f} min at "
                                    "{:.1f}° lat".format(api_len, mod_len, lat))
            # 3. two different days never come back byte-identical
            sig = (res.get("sunrise"), res.get("sunset"))
            if sig in seen:
                problems.append("identical to {} — API ignored the date/coords"
                                .format(seen[sig]))
            seen.setdefault(sig, head)
            api_tz = data.get("tzid") or res.get("tzid")   # top-level in the API
            if tzid and api_tz and api_tz != tzid:
                problems.append("API tzid {!r} != requested {!r}".format(
                    api_tz, tzid))
        print(head)
        print("  city point: {} ({:.4f},{:.4f}; {}) · tz {} · {}".format(
            pick["name"], lat, lon, pick_why, tzlabel, "cache" if cached else "api"))
        if problems:
            failures.append("{}: {}".format(head, "; ".join(problems)))
            print("  REJECTED: " + "; ".join(problems))
            skip(date, head, "rejected by sanity checks (see below)")
            # Evict so the next run re-asks the API instead of re-failing on cache.
            if cache.pop(ckey, None) is not None:
                cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
            continue
        abbr = rise.tzname() or tzlabel
        value = "{} {} · ☀ {} / 🌇 {} · {} · sunrise-sunset.org".format(
            dawn_word, dawn.strftime("%H:%M"), rise.strftime("%H:%M"), sset.strftime("%H:%M"),
            abbr if not approx else tzlabel)
        print("  sun: {}".format(value))
        if day.get("sun") and day["sun"] != value:
            print("  (was: {})".format(day["sun"]))
        if args.write:
            if approx:
                skip(date, head, "tz approximate — NOT written; pass --tz Area/City "
                     "or set day.tz / plan.tz")
                continue
            day["sun"] = value
            written += 1
    if args.write and written:
        src.write_text(json.dumps(plan, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    if args.write:
        print("\n{} API request(s), {} day(s) written{}".format(
            requests, written,
            " to " + str(src) if written else " — file untouched"))
    else:
        print("\n{} API request(s), printed only (add --write to update the plan)"
              .format(requests))
    if skipped:
        # Named, not counted: "6 written" out of 7 is only visible if you count.
        line = "skipped/failed ({}): {}".format(
            len(skipped), ", ".join("{} ({})".format(d, w.split(" — ")[0])
                                     for d, w in skipped))
        print(line)
        warn("sun " + line)
    if failures:
        for f in failures:
            warn("sun REJECTED — " + f)
        warn("{} day(s) rejected by sanity checks — nothing about them was written."
             .format(len(failures)))
        sys.exit(3)
    if skipped:
        # Vietnam F6: one TLS failure out of ten used to end with exit 0 and a
        # summary line nobody reads. Non-zero = at least one day has no sun value
        # from this run; the successful days ARE written above. Re-run with
        # --only DATE[,DATE] for the listed dates (a request failure retries;
        # no-date / no-coordinates / approximate-tz days need the plan fixed).
        warn("sun: {} day(s) NOT written — exit 1; fix/re-run with --only {}".format(
            len(skipped), ",".join(d for d, _ in skipped)))
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in [("geocode", cmd_geocode), ("check", cmd_check),
                     ("links", cmd_links), ("kml", cmd_kml), ("sun", cmd_sun)]:
        p = sub.add_parser(name, description={
            "check": "Straight-line hop distances, (est) durations, on-foot vs "
                     "ridden totals split declared/guessed. Exit 2 only for an "
                     "undeclared >12 km hop or missing coordinates; declared "
                     "fly/drive/boat/train/bus hops are fine.",
            "geocode": "Resolve stops via Nominatim in place (+ geocache.json); "
                       "preset/hand-filled coordinates are kept. WARNs when a hit's "
                       "display_name lacks the query's head token (possible wrong "
                       "place — look at it).",
            "links": "Per-hop map links (google | apple | amap). --write prints "
                     "origin -> destination names per row, refuses mismatched rows "
                     "and >100 km / fly / boat links, and summarises wrote / parked / "
                     "suspicious + 'long legs kept unlinked (expected)'. The row "
                     "name check is whole-word (Latin) / longest-first (CJK: another "
                     "stop's name that is a substring of this hop's endpoint is not "
                     "a mismatch); a token shared by two stops of the day is ignored. "
                     "parked > 0 -> exit still 0, but a loud stderr WARN lists every "
                     "parked row (day, row, text) — read it. Rail/flight row rule: "
                     "both stations in stops[] -> keep the row mappable (no link, "
                     "count aligned); stations NOT in stops[] (legs[] only) "
                     "-> \"map\": false. Mainland-China WARN only when a Google link "
                     "actually points there.",
            "sun": "Civil dawn / sunrise / sunset per day from sunrise-sunset.org "
                   "with local sanity checks; writes day['sun'] only with --write. "
                   "Point: the day's first stop, or the LAST stop on a moving day "
                   "(travel_day, or first->last >150 km); day['sun_stop'] (a stop's "
                   "name or 0-based index in stops[]) overrides that pick and is "
                   "echoed as 'sun_stop=…' (unknown -> WARN + old rule). Every "
                   "unwritten day is a WARN and listed at the end. Exit 0 = all "
                   "days handled; 1 = some day NOT written (others are; re-run "
                   "--write --only DATE,... for the listed dates); 3 = a day was "
                   "REJECTED by the sanity checks.",
        }.get(name), formatter_class=argparse.RawDescriptionHelpFormatter)
        p.add_argument("plan", help="plan JSON path")
        if name == "kml":
            p.add_argument("-o", "--out", default="trip.kml")
        if name == "links":
            p.add_argument("--write", action="store_true",
                           help="inject the URLs into the plan's hop rows and "
                                "day_map, in place, instead of only printing them; "
                                "prints each link's origin -> destination against "
                                "the row text and a wrote/parked/suspicious summary")
            p.add_argument("--provider", choices=PROVIDERS, default="google",
                           help="deep-link provider: google (default; DAY CHAIN "
                                "multi-point links), apple (maps.apple.com, "
                                "dirflg w|r|d, chain via +to:), amap (uri.amap.com "
                                "keyless, per-hop only, for mainland China — a WARN "
                                "suggests it when a google link actually points "
                                "into mainland CN)")
        if name == "sun":
            p.add_argument("--write", action="store_true",
                           help="write day['sun'] in place (default: print only); "
                                "exit 1 if any day was skipped/failed (the good "
                                "days are still written — re-run with --only for "
                                "the dates listed), 3 on a sanity-check rejection")
            p.add_argument("--tz", default="auto",
                           help="IANA zone (Area/City) for all days lacking day.tz; "
                                "'auto' = day.tz > plan.tz > longitude offset "
                                "(approx, never written)")
            p.add_argument("--only", default="",
                           help="comma-separated ISO dates to (re)fetch, e.g. "
                                "2026-10-01,2026-10-04")
            p.add_argument("--lang", default=None, choices=sorted(SUN_DAWN),
                           help="language of the written string's dawn word "
                                "(zh '天亮' / en 'dawn'); default: plan.lang > "
                                "plan.meta.lang > zh")
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
