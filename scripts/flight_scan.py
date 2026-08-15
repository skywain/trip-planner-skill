#!/usr/bin/env python3
"""Google Flights grid scanner (keyless) — part of the trip-planner skill.

Requires once:  pip3 install --user fast-flights

Examples:
  # round trip, nights ranging 10-15, departure date +/- 2 days
  python3 flight_scan.py --from PVG --to NRT --depart 2026-10-01 --nights 10-15 --flex 2
  # one way (run twice for open-jaw halves)
  python3 flight_scan.py --from KIX --to PVG --depart 2026-10-14 --oneway
  # nonstop only, prices in CNY, 2 adults
  python3 flight_scan.py --from PEK --to SYD --depart 2026-10-01 --nights 7 --nonstop \\
                         --currency CNY --adults 2

What the numbers mean (verified 2026-08-15 by scanning the same date with 1 vs 2
adults: $969 -> $1938):
  * PRICE = TOTAL for all passengers (--adults N), NOT per person. Divide by N.
  * Round trip: the ROUND-TRIP total (outbound + return), shown against the OUTBOUND
    options. Google's first results page lists outbound flights only — the return
    leg is chosen on the next page — so this script never sees return-leg times.
    Need the return leg's timetable? Run the reverse route as --oneway on the return
    date (its prices are one-way fares, not the round-trip split).
  * Currency: --currency XXX (ISO code, e.g. CNY, EUR, JPY) sets Google's `curr=`
    parameter; without it Google picks by the connection's region (USD from a US
    IP). The header line prints which one applied, and each price carries the
    symbol Google returned (e.g. "CN¥6534").
  * Stops: every row shows nonstop / N stop; --nonstop (or --max-stops N) asks
    Google for that filter, so the nonstops are not buried below 80 cheaper
    multi-stop rows (--top 5 sorted by price never reached them before). Without
    the filter, each block also prints the cheapest nonstop it saw.

Prices come from Google's cached results — comparison grade only; the deep link
printed with every block is the source of truth. The script sleeps between fetches
and caps total fetches (--max-fetches, default 12) so it behaves like one polite
human; a wide grid such as "--nights 10-15 --flex 2" is 30 combos, so either raise
the cap (~5-10 s per combo) or accept the centre-out subset it scans by default.

Failures: FETCH FAILED lines name the route and date. AssertionError = Google
answered with a non-200 page (bot wall / consent) and the fallback service could
not render it either; RuntimeError "No flights found" = the page had no result
list (unserved pair, or a date too far out). Both -> use the printed link.
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


def price_symbol(p):
    """The currency prefix Google put on a price string ('CN¥6534' -> 'CN¥')."""
    m = re.match(r"^\s*([^\d\s]+)", p or "")
    return m.group(1) if m else ""


def clock_min(s):
    m = re.search(r"(\d{1,2}):(\d{2})\s*(AM|PM)", s or "")
    if not m:
        return None
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "PM" else 0)
    return h * 60 + int(m.group(2))


MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}


def month_day(s):
    m = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2})", s or "")
    if not m or m.group(1) not in MONTHS:
        return None
    return (MONTHS[m.group(1)], int(m.group(2)))


def hhmm(s):
    m = re.match(r"^(\d{1,2}):(\d{2})$", s)
    if not m:
        raise argparse.ArgumentTypeError("time must be HH:MM (24h), e.g. 08:30")
    v = int(m.group(1)) * 60 + int(m.group(2))
    if not 0 <= v < 1440:
        raise argparse.ArgumentTypeError("time out of range")
    return v


def gflights_link(orig, dest, dep, ret=None, adults=1):
    if ret:
        q = "Flights from {} to {} on {} returning {} for {} adults".format(
            orig, dest, dep, ret, adults)
    else:
        q = "One way flights from {} to {} on {} for {} adults".format(
            orig, dest, dep, adults)
    return "https://www.google.com/travel/flights?q=" + quote(q)


def stops_label(stops):
    if stops == 0:
        return "nonstop"
    if isinstance(stops, int):
        return "{} stop".format(stops)
    return "? stops"


def fetch_grid_cell(legs, trip, pax, max_stops, currency):
    """One Google fetch. Prefers get_flights_from_filter (carries currency and
    max_stops); falls back to get_flights on very old fast-flights builds."""
    try:
        from fast_flights import get_flights_from_filter
        from fast_flights.flights_impl import TFSData
    except ImportError:
        get_flights_from_filter = TFSData = None
    if TFSData is not None:
        try:
            filt = TFSData.from_interface(flight_data=legs, trip=trip,
                                          seat="economy", passengers=pax,
                                          max_stops=max_stops)
        except TypeError:                     # older build: no max_stops kwarg
            if max_stops is not None:
                print("  (this fast-flights build ignores --nonstop/--max-stops)")
            filt = TFSData.from_interface(flight_data=legs, trip=trip,
                                          seat="economy", passengers=pax)
        try:
            return get_flights_from_filter(filt, currency=currency or "",
                                           mode="fallback")
        except TypeError:                     # older build: no currency kwarg
            if currency:
                print("  (this fast-flights build ignores --currency)")
            return get_flights_from_filter(filt, mode="fallback")
    from fast_flights import get_flights
    if currency or max_stops is not None:
        print("  (this fast-flights build ignores --currency/--nonstop)")
    try:
        return get_flights(flight_data=legs, trip=trip, seat="economy",
                           passengers=pax, fetch_mode="fallback")
    except TypeError:
        return get_flights(flight_data=legs, trip=trip, seat="economy",
                           passengers=pax)


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
    ap.add_argument("--adults", type=int, default=1,
                    help="passengers; PRICES ARE THE TOTAL FOR ALL OF THEM")
    ap.add_argument("--top", type=int, default=5,
                    help="show N cheapest options per date combo")
    ap.add_argument("--max-fetches", type=int, default=12)
    ap.add_argument("--nonstop", action="store_true",
                    help="ask Google for nonstop flights only (= --max-stops 0)")
    ap.add_argument("--max-stops", type=int, default=None, metavar="N",
                    help="ask Google for at most N stops")
    ap.add_argument("--currency", default=None, metavar="XXX",
                    help="ISO currency for the prices (CNY, EUR, JPY, AUD ...); "
                         "default: Google's choice for this connection's region")
    # Sorting by price alone surfaces red-eyes and next-day arrivals first — the
    # cheapest rows are often exactly the flights a schedule can't use. These
    # windows make "cheapest USABLE flight" a one-command answer.
    ap.add_argument("--dep-after", type=hhmm, default=None, metavar="HH:MM",
                    help="keep departures at/after this local time (24h)")
    ap.add_argument("--dep-before", type=hhmm, default=None, metavar="HH:MM",
                    help="keep departures at/before this local time")
    ap.add_argument("--arr-before", type=hhmm, default=None, metavar="HH:MM",
                    help="keep SAME-DAY arrivals at/before this local time "
                         "(next-day arrivals are dropped)")
    args = ap.parse_args()

    if not args.oneway and not args.nights:
        ap.error("--nights is required unless --oneway")
    if args.oneway and args.nights:
        ap.error("--oneway and --nights are mutually exclusive")
    max_stops = 0 if args.nonstop else args.max_stops
    if max_stops is not None and max_stops < 0:
        ap.error("--max-stops must be >= 0")
    currency = (args.currency or "").upper() or None
    if currency and not re.fullmatch(r"[A-Z]{3}", currency):
        ap.error("--currency must be a 3-letter ISO code such as CNY")

    try:
        from fast_flights import FlightData, Passengers   # noqa: F401
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

    # Say what the numbers are BEFORE any of them print (Japan F10, AU F13).
    print("PRICES: TOTAL for {} adult(s){} — Google Flights shows all-passenger "
          "totals, not per person; {}; currency: {}. Stops are per row; {}."
          .format(args.adults,
                  " (divide by {} for per person)".format(args.adults)
                  if args.adults > 1 else "",
                  "one-way fare" if args.oneway else
                  "ROUND-TRIP total incl. the return leg, listed against the "
                  "OUTBOUND options (return-leg times are not on Google's first "
                  "page — scan the reverse route --oneway on the return date "
                  "for those)",
                  ("--currency " + currency) if currency else
                  "Google's default for this connection's region (curr= not "
                  "set; the symbol on each price says which)",
                  "nonstop only (--nonstop)" if max_stops == 0 else
                  "<= {} stop(s) (--max-stops)".format(max_stops)
                  if max_stops is not None else
                  "no stop filter (cheapest nonstop also shown per block)"))

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
    seen_symbols = set()
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
        route = "{}->{} {}{}".format(args.orig, args.dest, dep_s,
                                     " / back " + ret_s if ret_s else "")
        if ret_s:
            hdr = "{} -> {} ({} nights)".format(dep_s, ret_s, n)
        else:
            hdr = "{} (one way)".format(dep_s)
        res, err = None, ""
        for attempt in range(2):      # transient Google throttling is common
            try:
                res = fetch_grid_cell(legs, trip, pax, max_stops, currency)
                break
            except Exception as e:
                # AU F13: "FETCH FAILED (AssertionError)" named neither the airports
                # nor the date, so three failing cells were indistinguishable.
                detail = " ".join(str(e).split())[:90]
                err = "{}: {}{}".format(type(e).__name__, route,
                                        " — " + detail if detail else "")
                if attempt == 0:
                    time.sleep(3)
        if res is None:
            hint = ("Google returned a non-200 page (bot wall / consent) and the "
                    "fallback renderer failed too" if err.startswith("AssertionError")
                    else "no result list on the page (unserved pair or date too "
                    "far out)" if err.startswith("RuntimeError") else
                    "network / parser error")
            print("\n== {} ==  FETCH FAILED ({}) — {}; use the link:\n  {}".format(
                hdr, err, hint, link))
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
        for f in flights:
            sym = price_symbol(getattr(f, "price", ""))
            if sym:
                seen_symbols.add(sym)

        if args.dep_after is not None or args.dep_before is not None \
                or args.arr_before is not None:
            def in_window(f):
                dm = clock_min(getattr(f, "departure", ""))
                if args.dep_after is not None and dm is not None \
                        and dm < args.dep_after:
                    return False
                if args.dep_before is not None and dm is not None \
                        and dm > args.dep_before:
                    return False
                if args.arr_before is not None:
                    arr = getattr(f, "arrival", "")
                    md = month_day(arr)
                    if md is not None and md != (d.month, d.day):
                        return False          # next-day arrival
                    am = clock_min(arr)
                    if am is not None and am > args.arr_before:
                        return False
                return True
            kept = [f for f in flights if in_window(f)]
            if len(kept) != len(flights):
                print("  (time window kept {} of {} options)".format(
                    len(kept), len(flights)))
            flights = kept
            if not flights:
                print("  no options inside the time window — widen it or "
                      "check the link below")
        level = getattr(res, "current_price", "?")
        print("\n== {}  [price level: {}] ==".format(hdr, level))
        shown = flights[: args.top]
        def show(f, tag=""):
            print("  {:>12}  {:>8}  {:>8}  {}{}{}".format(
                getattr(f, "price", "?"), getattr(f, "duration", "?"),
                stops_label(getattr(f, "stops", None)), getattr(f, "name", "?"),
                "  [BEST]" if getattr(f, "is_best", False) else "", tag))
            print("      {} -> {}".format(
                getattr(f, "departure", "?"), getattr(f, "arrival", "?")))
        for f in shown:
            show(f)
        if max_stops != 0:
            # Japan F10 / AU F13: nonstops exist but sit below dozens of cheaper
            # connections, so --top never reached them. Surface the cheapest one.
            ns = next((f for f in flights if getattr(f, "stops", None) == 0
                       and price_num(getattr(f, "price", ""))), None)
            if ns is not None and ns not in shown:
                show(ns, "  [cheapest nonstop]")
            elif ns is None and flights:
                print("  (no nonstop in Google's list for this date — try "
                      "--nonstop to be sure, or the link)")
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
        print("Prices are Google-cache comparison grade; TOTAL for {} adult(s), "
              "{}; currency as printed ({}). Book via the links above.".format(
                  args.adults, "one-way" if args.oneway else "round-trip",
                  ", ".join(sorted(seen_symbols)) or
                  ("--currency " + currency if currency else "region default")))


if __name__ == "__main__":
    main()
