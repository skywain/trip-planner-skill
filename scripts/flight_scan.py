#!/usr/bin/env python3
"""Google Flights grid scanner (keyless) — part of the travel-planner skill.

Requires once:  pip3 install --user fast-flights

Examples:
  # round trip, nights ranging 10-15, departure date +/- 2 days
  python3 flight_scan.py --from PVG --to NRT --depart 2026-10-01 --nights 10-15 --flex 2
  # one way (run twice for open-jaw halves)
  python3 flight_scan.py --from KIX --to PVG --depart 2026-10-14 --oneway

Prices come from Google's cached results — comparison grade only; the deep link
printed with every block is the source of truth. The script sleeps between fetches
and caps total fetches (--max-fetches, default 12) so it behaves like one polite
human; a wide grid such as "--nights 10-15 --flex 2" is 30 combos, so either raise
the cap (~5-10 s per combo) or accept the centre-out subset it scans by default.
"""
import argparse
import re
import sys
import time
from datetime import date, timedelta
from urllib.parse import quote


def parse_nights(s):
    if "-" in s:
        a, b = s.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(s)]


def price_num(p):
    digits = re.sub(r"[^\d]", "", p or "")
    return int(digits) if digits else 0


def gflights_link(orig, dest, dep, ret=None, adults=1):
    if ret:
        q = "Flights from {} to {} on {} returning {} for {} adults".format(
            orig, dest, dep, ret, adults)
    else:
        q = "One way flights from {} to {} on {} for {} adults".format(
            orig, dest, dep, adults)
    return "https://www.google.com/travel/flights?q=" + quote(q)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="orig", required=True,
                    help="IATA airport/city code, e.g. PVG")
    ap.add_argument("--to", dest="dest", required=True)
    ap.add_argument("--depart", required=True, help="YYYY-MM-DD")
    ap.add_argument("--nights", default=None,
                    help='round trip length, e.g. "12" or a range "10-15"')
    ap.add_argument("--oneway", action="store_true")
    ap.add_argument("--flex", type=int, default=0,
                    help="also scan departure +/- N days")
    ap.add_argument("--adults", type=int, default=1)
    ap.add_argument("--top", type=int, default=5,
                    help="show N cheapest options per date combo")
    ap.add_argument("--max-fetches", type=int, default=12)
    args = ap.parse_args()

    if not args.oneway and not args.nights:
        ap.error("--nights is required unless --oneway")
    if args.oneway and args.nights:
        ap.error("--oneway and --nights are mutually exclusive")

    try:
        from fast_flights import FlightData, Passengers, get_flights
    except ImportError:
        print("fast-flights is not installed. Run:\n"
              "  pip3 install --user fast-flights\n"
              "If that fails, skip this script and open the browser instead:\n  "
              + gflights_link(args.orig, args.dest, args.depart,
                              None if args.oneway else args.depart, args.adults))
        sys.exit(2)

    base = date.fromisoformat(args.depart)
    deps = [base + timedelta(days=d) for d in range(-args.flex, args.flex + 1)]
    nights_list = [None] if args.oneway else parse_nights(args.nights)

    combos = [(d, n) for d in deps for n in nights_list]
    if len(combos) > args.max_fetches:
        # Scan the grid centre-out. The requested departure date and the middle of the
        # nights range are what the traveller actually asked about, so truncation has
        # to drop the edges of the grid — never the centre they came in with.
        mid_i = (len(nights_list) - 1) / 2.0
        def rank(c):
            d_off = (c[0] - base).days
            n_off = nights_list.index(c[1]) - mid_i if c[1] is not None else 0
            return (abs(d_off) + abs(n_off), abs(d_off), d_off, n_off)
        combos.sort(key=rank)
        print("NOTE: {} of {} date combos scanned (--max-fetches); kept the ones "
              "nearest {} and the middle of the nights range. Raise --max-fetches "
              "for the full grid, ~5-10 s per combo."
              .format(args.max_fetches, len(combos), args.depart))
        combos = combos[: args.max_fetches]
        combos.sort(key=lambda c: (c[0], c[1] if c[1] is not None else 0))

    pax = Passengers(adults=args.adults, children=0,
                     infants_in_seat=0, infants_on_lap=0)
    best_rows = []
    for i, (d, n) in enumerate(combos):
        dep_s = d.isoformat()
        ret_s = (d + timedelta(days=n)).isoformat() if n else None
        legs = [FlightData(date=dep_s, from_airport=args.orig, to_airport=args.dest)]
        trip = "one-way"
        if ret_s:
            legs.append(FlightData(date=ret_s, from_airport=args.dest,
                                   to_airport=args.orig))
            trip = "round-trip"
        link = gflights_link(args.orig, args.dest, dep_s, ret_s, args.adults)
        if ret_s:
            hdr = "{} -> {} ({} nights)".format(dep_s, ret_s, n)
        else:
            hdr = "{} (one way)".format(dep_s)
        res = None
        for attempt in range(2):      # transient Google throttling is common
            try:
                try:
                    res = get_flights(flight_data=legs, trip=trip, seat="economy",
                                      passengers=pax, fetch_mode="fallback")
                except TypeError:
                    res = get_flights(flight_data=legs, trip=trip, seat="economy",
                                      passengers=pax)
                break
            except Exception as e:
                err = type(e).__name__
                if attempt == 0:
                    time.sleep(3)
        if res is None:
            print("\n== {} ==  FETCH FAILED ({}) — use the link:\n  {}".format(
                hdr, err, link))
            continue

        flights = sorted(list(getattr(res, "flights", [])),
                         key=lambda f: price_num(getattr(f, "price", "")) or 10 ** 9)
        seen = set()
        deduped = []
        for f in flights:
            k = (getattr(f, "name", ""), getattr(f, "departure", ""),
                 getattr(f, "price", ""))
            if k not in seen:
                seen.add(k)
                deduped.append(f)
        flights = deduped
        level = getattr(res, "current_price", "?")
        print("\n== {}  [price level: {}] ==".format(hdr, level))
        for f in flights[: args.top]:
            stops = getattr(f, "stops", None)
            stops_s = "nonstop" if stops == 0 else "{} stop".format(stops)
            print("  {:>12}  {:>8}  {:>8}  {}{}".format(
                getattr(f, "price", "?"), getattr(f, "duration", "?"), stops_s,
                getattr(f, "name", "?"),
                "  [BEST]" if getattr(f, "is_best", False) else ""))
            print("      {} -> {}".format(
                getattr(f, "departure", "?"), getattr(f, "arrival", "?")))
        print("  link: " + link)

        cheapest = next(
            (f for f in flights if price_num(getattr(f, "price", ""))), None)
        if cheapest:
            best_rows.append((price_num(cheapest.price), hdr, cheapest.price,
                              getattr(cheapest, "name", "?")))
        if i < len(combos) - 1:
            time.sleep(1.5)

    if best_rows:
        best_rows.sort()
        print("\n===== CHEAPEST PER DATE COMBO, ACROSS GRID =====")
        for _, hdr, p, name in best_rows[:5]:
            print("  {:>12}  {}  ({})".format(p, hdr, name))
        print("Prices are Google-cache comparison grade; book via the links above.")


if __name__ == "__main__":
    main()
