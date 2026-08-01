#!/usr/bin/env python3
"""Day-route toolbox for the travel-planner skill (stdlib only, Python 3.9+).

Input: a plan JSON — the SAME file render_plan.py consumes, so the map links, the
KML and the written plan can never drift apart:
{
  "trip": "kyoto-oct",
  "days": [
    {"date": "2026-10-05", "label": "East Kyoto",
     "stops": [
       {"name": "清水寺", "query": "Kiyomizu-dera, Kyoto, Japan"},
       {"name": "Nishiki Market", "lat": 35.005, "lon": 135.764, "mode": "transit"}
     ]}
  ]
}
"query" defaults to "name"; a stop with lat/lon pre-filled skips geocoding; a day
with no stops (a travel day) is fine. Optional "mode": "walk"|"transit" describes the
hop INTO that stop and overrides the distance guess — set it whenever the traveller
rides a short hop or walks a long one, because it decides both the walking total and
which directions the tappable link opens. Model a long stroll as a stop at its
midpoint, otherwise its kilometres never reach the walking total.

Name the file plan.geo.json from the start: geocode then edits it in place and every
later command reads the one file that has everything.

Subcommands:
  geocode plan.geo.json       -> resolves stops in place (+ geocache.json), via
                                 Nominatim/OSM; existing coordinates are PRESERVED
  check   plan.geo.json       -> hop distances, walk/transit estimates, on-foot vs
                                 ridden totals; exits 2 on a suspicious/broken hop
  links   plan.geo.json [--write]
                              -> per-hop Google Maps links + whole-day chain links;
                                 --write injects them into the plan's hop rows
  kml     plan.geo.json -o trip.kml  -> numbered pins + day route lines
                                        (import into Organic Maps / Google My Maps)

Nominatim usage policy is enforced here (User-Agent, 1 req/s, cache) — do not
parallelize around this script and do not strip the throttle.
"""
import argparse
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "travel-planner-skill/1.2 (personal trip planning script)"}
WALK_MIN_PER_KM = 14          # tourist pace incl. lights/photos
MAX_WALK_KM = 1.6             # beyond this, suggest transit
DAY_WALK_FLAG_KM = 8.0
SUSPICIOUS_KM = 12.0
DAY_COLORS = ["ff0000ff", "ffff0000", "ff00aa00",
              "ff00aaff", "ffaa00aa", "ff777777"]   # KML aabbggrr
SHAPE = ('Expected: {"days":[{"date":"...","label":"...",'
         '"stops":[{"name":"...","query":"..."}]}]}')


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
    """(verdict, human duration) for a hop, where `mode` is the stop's optional
    "walk"|"transit" override. Distance alone cannot know whether a traveller rides
    a 1.4 km hop or walks it, and that single fact decides both the walking total and
    which directions the tappable link opens — so when the plan knows, it says so.
    Transit hops get a RANGE: a straight line cannot know the line, the headway, or
    the walk to the platform, and a single number there is false precision the
    planner then schedules against."""
    if mode is None and km > SUSPICIOUS_KM:
        return "SUSPICIOUS (>12 km straight-line — same day? same city?)", None
    walking = mode == "walk" or (mode is None and km <= MAX_WALK_KM)
    if walking:
        verdict = "walk" + ("" if mode is None else " (declared)")
        return verdict, "~{} min".format(max(5, r5(km * WALK_MIN_PER_KM)))
    if km > 40:
        return "TRANSIT (long-distance — use the real timetable)", None
    mins = km * 6 + 8              # ~6 min/km in-vehicle + access/wait allowance
    return "TRANSIT", "~{}-{} min".format(max(15, r5(mins * 0.85)),
                                          r5(mins * 1.25))


def gmaps_dir(o, d, mode, waypoints=None):
    p = [("api", "1"),
         ("origin", "{:.6f},{:.6f}".format(*o)),
         ("destination", "{:.6f},{:.6f}".format(*d)),
         ("travelmode", mode)]
    if waypoints:
        p.append(("waypoints",
                  "|".join("{:.6f},{:.6f}".format(*w) for w in waypoints)))
    return "https://www.google.com/maps/dir/?" + urllib.parse.urlencode(p)


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
        walk_km, ride_km, rides = 0.0, 0.0, 0
        worst = "OK"
        for (a, ca), (b, cb) in zip(pts, pts[1:]):
            if not ca or not cb:
                print("  {} -> {}: missing coords — run geocode or fill by hand"
                      .format(a["name"], b["name"]))
                worst = "BROKEN"
                continue
            km = haversine_km(ca, cb)
            verdict, dur = hop_estimate(km, b.get("mode"))
            if verdict.startswith("SUSPICIOUS"):
                worst = "SUSPICIOUS"
            elif verdict.startswith("walk"):
                walk_km += km
            else:
                ride_km += km
                rides += 1
            print("  {:22.22} -> {:22.22} {:5.1f} km  {}{}".format(
                a["name"], b["name"], km, verdict,
                "  " + dur if dur else ""))
        note = []
        if worst != "OK":
            note.append(worst + " HOPS PRESENT")
            bad_days += 1
        if walk_km * 1.3 > DAY_WALK_FLAG_KM:
            note.append("ALREADY OVER {:.0f} km ON FOOT — re-cluster".format(
                DAY_WALK_FLAG_KM))
        print("  on foot: {:.1f} km → ≈{:.1f} km with real streets".format(
            walk_km, walk_km * 1.3))
        if rides:
            print("  ridden:  {:.1f} km over {} hop(s) — not walking".format(
                ride_km, rides))
        print("  + in-venue walking and strolls: add your own; the {:.0f} km cap is "
              "on the SUM — {}".format(DAY_WALK_FLAG_KM,
                                       "; ".join(note) if note else "OK so far"))
    print("\nNote: distances are straight-line; real streets add ~20-30%. Transit "
          "durations are estimates — browser-verify the load-bearing hops.")
    if bad_days:
        sys.exit(2)


def cmd_links(args):
    plan = load_plan(args.plan)
    for i, day in enumerate(plan["days"], 1):
        print("\nDay {} {} — {}".format(i, day.get("date", "?"),
                                        day.get("label", "")))
        mapped = [s for s in day["stops"] if coords(s)]
        pts = [(s["name"], coords(s)) for s in mapped]
        skipped = len(day["stops"]) - len(pts)
        if skipped:
            print("  ({} stop(s) skipped: no coords)".format(skipped))
        hop_urls = []
        for (na, ca), (nb, cb), b in zip(pts, pts[1:], mapped[1:]):
            km = haversine_km(ca, cb)
            verdict, dur = hop_estimate(km, b.get("mode"))
            mode = "walking" if verdict.startswith("walk") else "transit"
            url = gmaps_dir(ca, cb, mode)
            hop_urls.append(url)
            print("  {} -> {}  [{} {:.1f} km {}]\n    {}".format(
                na, nb, mode, km, dur or verdict, url))
        if args.write and hop_urls:
            # Hop rows correspond 1:1, in order, with the stop-to-stop hops — the
            # stops-mirror-the-timeline invariant. Flight/rail rows already covered
            # by the legs table carry "map": false and sit outside that invariant
            # (a day with a flight plus 3 ground hops has 4 hop rows but only 3
            # mapped hops — learned on the first real multi-city trip).
            rows = [it for it in (day.get("timeline") or [])
                    if isinstance(it, dict) and it.get("kind") == "hop"
                    and it.get("map") is not False]
            if len(rows) == len(hop_urls):
                for row, url in zip(rows, hop_urls):
                    row["link"] = url
                print("  ✎ wrote {} link(s) into the timeline's hop rows".format(
                    len(rows)))
            else:
                day["hop_links"] = hop_urls
                print("  ✎ {} mappable hop rows vs {} mapped hops — links parked "
                      "in day['hop_links'] (render_plan shows them as a 逐跳导航 "
                      "row). To place them on rows: give every stop-to-stop "
                      "transition its own hop row and mark flight/rail rows "
                      '"map": false.'.format(len(rows), len(hop_urls)))
        if len(pts) < 2:
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
            url = gmaps_dir(seg[0][1], seg[-1][1], "walking",
                            [c for _, c in seg[1:-1]] or None)
            print("  {} {} -> {} ({} stops):\n    {}".format(
                label, seg[0][0], seg[-1][0], len(seg), url))
            if args.write and s == 0:
                day["day_map"] = url
    if args.write:
        Path(args.plan).write_text(
            json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\nupdated {} in place".format(args.plan))


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


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in [("geocode", cmd_geocode), ("check", cmd_check),
                     ("links", cmd_links), ("kml", cmd_kml)]:
        p = sub.add_parser(name)
        p.add_argument("plan", help="plan JSON path")
        if name == "kml":
            p.add_argument("-o", "--out", default="trip.kml")
        if name == "links":
            p.add_argument("--write", action="store_true",
                           help="inject the URLs into the plan's hop rows and "
                                "day_map, in place, instead of only printing them")
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
