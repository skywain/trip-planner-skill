#!/usr/bin/env python3
"""plan_lint.py — the machine gate for plan.geo.json before rendering.

    python3 scripts/plan_lint.py plan.geo.json [--strict] [--art plan.art.json] [--ics gates.ics] [--kml trip.kml]

Exit code = number of FAIL lines (0 = clean), like themes/qc.py, clamped to 255 (an
exit status wraps at 256: 256 FAILs used to exit 0). WARN lines go to stderr and
never change the exit code.

Why it exists: route_tools `check` proves the geography and themes/qc.py proves the
HTML, but neither looks at what the plan *says* — on a 2026-09 test a plan with no
`brief` at all, "awaiting qc.py" in meta.self_check, "## 总计" in a budget cell and
nine unfilled art placeholders rendered two pages with an empty 行前须知 section while
every exit code stayed green, and the planner reported "nine brief cards complete".
Weak planners trust exit codes; this file makes the required sections part of them.

Default checks (every plan, including the pre-2026-09 examples):
  - JSON parses; `days[]` present, each with a date and a non-empty timeline (a list of row objects)
  - `brief` present, a dict, non-empty; every card non-empty
  - no placeholder text anywhere: PLACEHOLDER / TODO / TBD; "awaiting" in meta,
    budget, legs.price, checklist.price, hotels
  - no markdown heading in a table cell (a value starting with "#") in budget /
    checklist / legs / hotels / brief
  - meta.self_check reads "self-checked: N …" (en) or "自检:发现并修复 N 处" (zh);
    meta.budget_total non-empty and not a placeholder
  - art file (--art, or <plan>.art.json beside the plan): `_stock_todo` empty; a
    `_stock` block present ⇔ prefs.pictures == "stock" (when prefs.pictures is set)
  - gates .ics beside the plan (--ics, or gates.ics / trip.ics next to the plan): WARN
    when missing (FAIL under --strict — since 2026-09 every plan has ladder gates);
    WARN when the file is older than the plan
  - checklist, when present, is a list
  - trip.kml beside the plan (--kml, or trip.kml next to the plan): WARN when missing
    (FAIL under --strict — the offline map ships with every plan)
  - timeline rows, only where the keys are present (output-template.md §city-block):
    `sub_stops` a non-empty list of objects, each with a `name` and a `query` or
    `lat`+`lon`; `tier` ∈ eye-level | overlook | from-below; `must` / `tour` are true
    or absent; `must: true` carries a `tier`; on a `tour: true` row every `must`
    sub-stop's `confirmed` starts "in writing" or "pending". WARN: `pending`, a
    sub-stop `link` or a row `sub_map` that is not an http(s) URL (run
    `route_tools.py links --write`), `sub_stops` on a row that is not `kind: anchor`
  - a self-drive option (prefs.travel_style self-drive | mixed, prefs.drivers, or a
    legs[] row whose type names a rental / self-drive) needs a `brief.driving` card —
    legality of the licence where the car is driven, before rentability
  - every brief card is one string; on a tour row a must-see's `pending` confirmation
    names a checklist row by its item text
--strict adds the 2026-09 contract (new plans; the older examples predate it):
  - brief keys in canonical order and the required cards present (visa · emergency ·
    safety · health · holidays · weather · money · connectivity · insurance)
  - brief.safety opens with the advisory line ("advisory:" / "警示:")
  - checklist carries a visa row, a travel-clinic row, and the T-14 / T-7 / T-3 / T-1
    ladder rows; the last decisions[] row repeats the self-check line
  - prefs.pictures present (native | key | stock)
  - every day has at least one stop (airports on move days) and a `sun` that is the
    canonical `route_tools.py sun --write` string — a stop-less day is skipped by `sun`
    and a hand-written or "待计算" value is what ends up in the page
  - (2026-10) a trip of seven days or more carries an on-trip re-audit row (D+N in the
    row's item, an ISO date in its deadline); a plan with a self-drive option records
    the independent review in meta.self_check and in the last decisions[] row
"""
import argparse
import json
import os
import re
import sys

CANON = ["visa", "emergency", "safety", "health", "holidays", "weather", "money",
         "connectivity", "insurance", "baggage"]
REQUIRED = ["visa", "emergency", "safety", "health", "holidays", "weather", "money",
            "connectivity", "insurance"]
PLACEHOLDER = re.compile(r"\b(PLACEHOLDER|TODO|TBD)\b", re.I)
AWAITING = re.compile(r"\bawaiting\b", re.I)
SELF_CHECK = re.compile(r"(self-checked:\s*\d+|自检[:\uff1a]?\s*发现并修复\s*\d+)")
ADVISORY = re.compile(r"^\s*(advisory|警示|旅行警示)\s*[:\uff1a]", re.I)
LADDER = ["T-14", "T-7", "T-3", "T-1"]
ON_TRIP = re.compile(r"(?<![A-Za-z0-9])D\+\d+")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
PENDING_SEP = re.compile(r"^\s*[·・•\-—–:\uff1a]\s*")
REVIEW = re.compile(r"independent review\s*[:\uff1a]|独立复核\s*[:\uff1a]", re.I)
SUN_OK = re.compile(r"^(?:天亮|dawn) \d{2}:\d{2} · ☀ \d{2}:\d{2} / 🌇 \d{2}:\d{2} · \S+ · sunrise-sunset\.org$")
TIERS = ("eye-level", "overlook", "from-below")
# A legs[] row that is a self-driven vehicle. Not stops[].mode "drive" — the examples use
# that for taxis and hired cars with a driver (Mexico, Morocco, Turkey, Vietnam).
_VEH = r"(?:car|van|minivan|suv|camper(?:van)?|motorhome|rv|4x4|4wd|jeep|scooter|moped|motorbike|motorcycle)s?"
VEHICLE_RENTAL = re.compile(
    r"\b" + _VEH + r"\s+(?:hire|rental)\b"
    r"|\b(?:rental|hire|hired|rented)\s+" + _VEH + r"\b"
    r"|\b(?:rent|hire)(?:ing)?\s+(?:an?\s+)?" + _VEH + r"\b"
    r"|rent[-\s]?a[-\s]?car"
    r"|租车|租車|汽车租赁|汽車租賃|租摩托|租机车|租機車|レンタカー", re.I)
BARE_RENTAL = re.compile(r"\brental\b", re.I)
# A bare "rental" whose object is not a motor vehicle is not one …
_NOT = r"(?:e-?bikes?|bikes?|bicycles?|kayaks?|canoes?|boats?|skis?|surfboards?|gear|equipment|apartments?|cottages?|houses?|villas?|cabins?)"
NOT_A_CAR = re.compile(r"\b" + _NOT + r"\s+(?:rental|hire)\b|\b(?:rental|hire)\s+" + _NOT + r"\b", re.I)
# … a car that comes with its driver is not self-drive ("no driver" is not "driver",
# and an "additional driver" is a rental-desk fee, not a chauffeur) …
NO_DRIVER = re.compile(r"不含司机|不带司机|不含司機|不帶司機|无司机|無司機"
                       r"|\b(?:no|without(?:\s+a)?)\s+driver(?:\s+incl\w*)?", re.I)
WITH_DRIVER = re.compile(
    r"(?:\bwith|\bw/|\+|\uff0b|&|\band|\bplus)\s*(?:an?\s+)?"
    r"(?!(?:additional|second|extra|young|named)\b)(?:[\w-]+\s+){0,2}driver\b"
    r"|\bincl(?:\.|uding|udes)?\s+(?:an?\s+)?driver\b|driver\s+incl|\bdriver[-\s]guide"
    r"|\bchauffeur|\bprivate\s+hire\b"
    r"|包车|包車|[+\uff0b带帶配附含]\s*\S{0,3}司[机機]", re.I)
# … and a self-drive word decides only when no rental noun or driver did.
SELF_DRIVE = re.compile(r"self[-\s]?driv|自驾|自駕", re.I)
NOT_SELF_DRIVE = re.compile(r"[非不]\S{0,2}自[驾駕]|\bnot?\s+self[-\s]?driv", re.I)


def self_drive_leg(t):
    """True when a legs[].type string names a vehicle the traveller drives. Keyword
    heuristics in five ordered tests; prefs.travel_style and prefs.drivers are the
    primary triggers (KNOWN-ISSUES PLN-13)."""
    if WITH_DRIVER.search(NO_DRIVER.sub(" ", t)):
        return False
    if VEHICLE_RENTAL.search(t):
        return True
    if NOT_SELF_DRIVE.search(t):
        return False
    if SELF_DRIVE.search(t):
        return True
    return bool(BARE_RENTAL.search(t)) and not NOT_A_CAR.search(t)


fails, warns = [], []


def fail(msg):
    fails.append(msg)
    print("FAIL " + msg)


def warn(msg):
    warns.append(msg)
    print("WARN " + msg, file=sys.stderr)


def norm_key(k):
    return re.sub(r"[\s_]+", "", str(k)).lower()


def walk_strings(obj, path=""):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, "{}.{}".format(path, k) if path else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, "{}[{}]".format(path, i))


def has_latlon(s):
    """lat and lon both numbers — the test route_tools.sub_point applies."""
    try:
        float(s["lat"]), float(s["lon"])
        return True
    except (KeyError, TypeError, ValueError):
        return False


def is_http(v):
    """The test the renderers apply before they emit an href."""
    return isinstance(v, str) and v.startswith(("https://", "http://"))


def check_rows(i, d, items=()):
    """The optional row fields (output-template.md §city-block). Every check fires
    only when its key is present, so a plan without them is untouched."""
    rows = d.get("timeline")
    for r, row in enumerate(rows if isinstance(rows, list) else [], 1):
        if not isinstance(row, dict):
            fail("day {} ({}) row {} is not an object, got {}".format(
                i, d.get("date"), r, repr(row)[:40]))
            continue
        where = "day {} ({}) row {} {!r}".format(i, d.get("date"), r,
                                                 str(row.get("what", ""))[:40])
        if "tour" in row and row["tour"] is not True:
            fail("{}: tour is {!r} — true, or leave the key out (absent, never null)"
                 .format(where, row["tour"]))
        if "sub_map" in row and not is_http(row["sub_map"]):
            warn("{}: sub_map is not an http(s) URL — it is script-owned, run "
                 "route_tools.py links --write".format(where))
        if "sub_stops" not in row:
            continue
        subs = row["sub_stops"]
        if not isinstance(subs, list) or not subs or not all(isinstance(s, dict) for s in subs):
            fail("{}: sub_stops must be a non-empty list of objects, got {} — absent, "
                 "never null (output-template.md §city-block)".format(where, repr(subs)[:40]))
            continue
        if row.get("kind") != "anchor":
            warn("{}: sub_stops on a kind:{} row — they belong on the anchor row of the "
                 "sight they sit inside".format(where, row.get("kind")))
        for k, s in enumerate(subs, 1):
            sw = "{} sub-stop {} {!r}".format(where, k, str(s.get("name", ""))[:30])
            if not s.get("name"):
                fail("{}: no name".format(sw))
            q = s.get("query")
            if not (isinstance(q, str) and q.strip()) and not has_latlon(s):
                fail("{}: no query and no lat+lon — its map link is built from one of "
                     "them".format(sw))
            if "tier" in s and s["tier"] not in TIERS:
                fail("{}: tier {!r} is not one of {}".format(sw, s["tier"], " | ".join(TIERS)))
            if "must" in s and s["must"] is not True:
                fail("{}: must is {!r} — true, or leave the key out (absent, never null)"
                     .format(sw, s["must"]))
            if s.get("must") is True and "tier" not in s:
                fail("{}: must:true with no tier — say which level the picture is taken "
                     "from ({})".format(sw, " | ".join(TIERS)))
            conf = s.get("confirmed")
            c = conf.strip().lower() if isinstance(conf, str) else ""
            if row.get("tour") is True and s.get("must") is True \
                    and not (c.startswith("in writing") or c.startswith("pending")):
                fail("{}: a must-see on a tour row needs confirmed = 'in writing · <date> · "
                     "<channel>' or 'pending · <the checklist row that asks it>' (got {!r})"
                     .format(sw, conf))
            if c.startswith("pending") and row.get("tour") is True and s.get("must") is True:
                asked = PENDING_SEP.sub("", c[len("pending"):], count=1).strip()
                if len(asked) < 4 or not any(asked in it or (len(it) >= 8 and it in asked)
                                             for it in items):
                    fail("{}: confirmed is pending but names no checklist row — write 'pending · "
                         "<the item text of the checklist row that asks the operator>' "
                         "(got {!r})".format(sw, conf.strip()[:60]))
                else:
                    warn("{}: confirmation still pending — {}".format(sw, conf.strip()[:60]))
            elif c.startswith("pending"):
                warn("{}: confirmation still pending — {}".format(sw, conf.strip()[:60]))
            if not is_http(s.get("link")):
                warn("{}: no http(s) link — run route_tools.py links --write{}".format(
                    sw, "" if has_latlon(s) else " (an amap pin needs lat/lon: add them, "
                    "or use --provider apple / google)"))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--strict", action="store_true",
                    help="also enforce the 2026-09 brief / checklist contract")
    ap.add_argument("--art", default=None, help="art file (default: <plan>.art.json beside it)")
    ap.add_argument("--ics", default=None, help="gates .ics (default: gates.ics / trip.ics beside it)")
    ap.add_argument("--kml", default=None, help="trip .kml (default: trip.kml beside it)")
    args = ap.parse_args()

    try:
        plan = json.load(open(args.plan, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        fail("plan does not parse: {}".format(e))
        sys.exit(1)
    if not isinstance(plan, dict):
        fail("plan is not a JSON object")
        sys.exit(1)

    # ---- days ----
    checklist = plan.get("checklist")
    if checklist is not None and not isinstance(checklist, list):
        fail("checklist is not a list")
    checklist = checklist if isinstance(checklist, list) else []
    days = plan.get("days")
    if not isinstance(days, list) or not days:
        fail("days[] missing or empty")
    else:
        items = [r["item"].strip().lower() for r in checklist
                 if isinstance(r, dict) and isinstance(r.get("item"), str)
                 and len(r["item"].strip()) >= 4]
        for i, d in enumerate(days, 1):
            if not isinstance(d, dict) or not d.get("date"):
                fail("day {} has no date".format(i))
            elif not isinstance(d.get("timeline"), list) or not d["timeline"]:
                fail("day {} ({}) has an empty or non-list timeline".format(i, d.get("date")))
            if isinstance(d, dict):
                check_rows(i, d, items)

    # ---- brief ----
    brief = plan.get("brief")
    if not isinstance(brief, dict) or not brief:
        fail("brief missing or empty — the 行前须知 section renders blank "
             "(output-template.md §Brief templates)")
        brief = {}
    else:
        for k, v in brief.items():
            if v is None or (isinstance(v, (str, list, dict)) and not v):
                fail("brief.{} is empty".format(k))
            elif not isinstance(v, str):
                fail("brief.{} is {} — a card is one string (lines separated by \\n); the "
                     "page prints anything else raw".format(k, type(v).__name__))
    keys = [norm_key(k) for k in brief]

    # ---- brief.driving: a self-drive option exists (an empty card FAILs above) ----
    prefs = plan.get("prefs") if isinstance(plan.get("prefs"), dict) else {}
    drive = []
    if prefs.get("travel_style") in ("self-drive", "mixed"):
        drive.append("prefs.travel_style = {}".format(prefs["travel_style"]))
    if prefs.get("drivers"):
        drive.append("prefs.drivers")
    legs = plan.get("legs") if isinstance(plan.get("legs"), list) else []
    rental = next((l for l in legs if isinstance(l, dict)
                   and self_drive_leg(str(l.get("type", "")))), None)
    if rental is not None:
        drive.append("legs[] type {!r}".format(str(rental.get("type"))[:30]))
    if drive and "driving" not in keys:
        fail("brief.driving missing but a self-drive option exists ({}) — legality of "
             "each driver's licence where the car is driven comes before rentability "
             "(phase-1-brief.md §Driving card)".format(", ".join(drive)))

    # ---- placeholders and markdown-in-cells ----
    for path, s in walk_strings(plan):
        if PLACEHOLDER.search(s):
            fail("placeholder text at {}: {!r}".format(path, s[:60]))
    for sect in ("meta", "budget", "legs", "checklist", "hotels"):
        for path, s in walk_strings(plan.get(sect), sect):
            if AWAITING.search(s):
                fail("'awaiting' left in {}: {!r}".format(path, s[:60]))
    for sect in ("budget", "checklist", "legs", "hotels", "brief"):
        for path, s in walk_strings(plan.get(sect), sect):
            if s.lstrip().startswith("#"):
                fail("markdown heading inside a cell at {}: {!r} — cells render as "
                     "text, not markdown".format(path, s[:40]))

    # ---- meta ----
    meta = plan.get("meta") or {}
    if not isinstance(meta, dict):
        fail("meta is not an object")
        meta = {}
    sc = str(meta.get("self_check", ""))
    if not SELF_CHECK.search(sc):
        fail("meta.self_check is not the self-check line ({!r}) — expected "
             "'self-checked: N issues found and fixed' / '自检:发现并修复 N 处'".format(sc[:50]))
    bt = str(meta.get("budget_total", "")).strip()
    if not bt:
        fail("meta.budget_total is empty")

    # ---- art file ----
    art_path = args.art or re.sub(r"\.geo\.json$", ".art.json", args.plan)
    if art_path == args.plan:
        art_path = os.path.splitext(args.plan)[0] + ".art.json"
    pictures = prefs.get("pictures")
    if os.path.exists(art_path):
        try:
            art = json.load(open(art_path, encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            fail("art file {} does not parse: {}".format(art_path, e))
            art = {}
        todo = art.get("_stock_todo") if isinstance(art, dict) else None
        if todo:
            fail("art file still has {} unfilled stock placeholder(s) (_stock_todo): {}"
                 .format(len(todo), ", ".join(map(str, list(todo)[:5]))))
        has_stock = isinstance(art, dict) and "_stock" in art
        if pictures is not None:
            if has_stock and pictures != "stock":
                fail("art file was built by stock_art.py but prefs.pictures = {!r} — set it "
                     "to 'stock' (the picture notice keys off it)".format(pictures))
            if pictures == "stock" and not has_stock:
                warn("prefs.pictures = stock but the art file has no _stock block")
        for path, s in walk_strings(art, "art"):
            if PLACEHOLDER.search(s):
                fail("placeholder text in art file at {}: {!r}".format(path, s[:60]))
    elif pictures == "stock":
        warn("prefs.pictures = stock but no art file found at {}".format(art_path))

    # ---- gates .ics ----
    plan_dir = os.path.dirname(os.path.abspath(args.plan))
    ics_candidates = [args.ics] if args.ics else [os.path.join(plan_dir, n) for n in ("gates.ics", "trip.ics")]
    if not any(c and os.path.exists(c) for c in ics_candidates):
        msg = ("no gates .ics beside the plan ({}) — every plan carries the ladder gates; "
               "generate it: python3 scripts/route_tools.py ics {} -o {}"
               .format(", ".join(os.path.basename(c) for c in ics_candidates if c), args.plan,
                       ics_candidates[0]))
        (fail if args.strict else warn)(msg)
    else:
        ics = next(c for c in ics_candidates if c and os.path.exists(c))
        if os.path.getmtime(ics) + 1 < os.path.getmtime(args.plan):
            warn("{} is older than the plan — a checklist row added or re-dated since is not "
                 "in the calendar; re-run: python3 scripts/route_tools.py ics {} -o {}"
                 .format(os.path.basename(ics), args.plan, ics))

    # ---- trip.kml ----
    kml_candidates = [args.kml] if args.kml else [os.path.join(plan_dir, "trip.kml")]
    if not any(c and os.path.exists(c) for c in kml_candidates):
        msg = ("no trip.kml beside the plan ({}) — the offline map ships with every plan; "
               "generate it: python3 scripts/route_tools.py kml {} -o {}"
               .format(os.path.basename(kml_candidates[0]), args.plan, kml_candidates[0]))
        (fail if args.strict else warn)(msg)

    # ---- strict: the 2026-09 contract ----
    if args.strict:
        if isinstance(days, list):
            for i, d in enumerate(days, 1):
                if not isinstance(d, dict):
                    continue
                if not d.get("stops"):
                    fail("day {} ({}) has no stops — every day carries at least one (the airport "
                         "on a move day); `sun --write` skips a stop-less day and the sunrise "
                         "prose has nothing to stand on".format(i, d.get("date")))
                sun = d.get("sun")
                if not isinstance(sun, str) or not SUN_OK.fullmatch(sun):
                    polar = "sun" not in d and any(
                        isinstance(st, dict) and isinstance(st.get("lat"), (int, float))
                        and abs(st["lat"]) >= 60 for st in (d.get("stops") or []))
                    if "sun" in d and sun is None:
                        why = ("sun is null — remove the key instead (absent, never null: renderer copies "
                               "older than 2026-09-05 crash on null; a polar day keeps the key absent)")
                    elif polar:
                        why = ("if `sun --write` REJECTED this day as polar day/night this is the one "
                               "tolerated FAIL (KNOWN-ISSUES PLN-11), otherwise run `sun --write --only {}`; "
                               "sun is never hand-written".format(d.get("date")))
                    else:
                        why = ("run `sun --write --only {}`; a day that crosses the date line or changes "
                               "timezone is rejected until days[].sun_stop names a stop inside the day's tz "
                               "(usually 0); sun is never hand-written".format(d.get("date")))
                    fail("day {} ({}) sun is not the canonical `route_tools.py sun --write` string ({}) — {}"
                         .format(i, d.get("date"), repr(sun)[:30], why))
        for r in REQUIRED:
            if r not in keys:
                fail("brief.{} missing (required, output-template.md §Brief templates)".format(r))
        order = [k for k in keys if k in CANON]
        expect = [k for k in CANON if k in order]
        if order != expect:
            fail("brief keys out of canonical order: {} (expected {})".format(order, expect))
        safety = brief.get("safety") or next((v for k, v in brief.items() if norm_key(k) == "safety"), "")
        stext = safety if isinstance(safety, str) else json.dumps(safety, ensure_ascii=False)
        if stext and not ADVISORY.search(stext.lstrip()):
            fail("brief.safety does not open with the advisory line "
                 "('advisory: level · source · as-of')")
        if pictures not in ("native", "key", "stock"):
            fail("prefs.pictures must be native | key | stock (got {!r})".format(pictures))
        rows = checklist
        text = " \n ".join(json.dumps(r, ensure_ascii=False) for r in rows)
        if not re.search(r"visa|签证|e-?visa|入境", text, re.I):
            fail("checklist has no visa / entry row")
        if not re.search(r"clinic|门诊|疫苗|vaccin", text, re.I):
            fail("checklist has no travel-clinic consult row")
        for t in LADDER:
            if not re.search(re.escape(t) + r"(?!\d)", text):
                fail("checklist has no {} ladder row (output-template.md "
                     "§Pre-departure re-check ladder)".format(t))
        if isinstance(days, list) and len(days) >= 7 and not any(
                isinstance(r, dict) and ON_TRIP.search(str(r.get("item", "")))
                and ISO_DATE.search(str(r.get("deadline", "")))
                for r in rows):
            fail("a trip of seven days or more has no on-trip re-audit row — a checklist row "
                 "whose item carries D+N ('On-trip re-audit · D+3' / '途中复核 · D+3') and whose "
                 "deadline carries the ISO date, one every 3-4 days of travel "
                 "(output-template.md §On-trip re-audit rows)")
        if drive and not REVIEW.search(sc):
            fail("meta.self_check has no independent-review clause although a self-drive "
                 "option exists — '… · independent review: C confirmed, R refuted' / "
                 "'… · 独立复核:确认 C 条,驳回 R 条' (phase-6-assemble.md §Independent review)")
        decisions = plan.get("decisions") or []
        if not decisions or not SELF_CHECK.search(str(decisions[-1])):
            fail("last decisions[] row does not repeat the self-check line "
                 "(seven of eight themes render decisions, not meta.self_check)")
        elif drive and REVIEW.search(sc) and not REVIEW.search(str(decisions[-1])):
            fail("last decisions[] row repeats the self-check count but not its "
                 "independent-review clause — the page prints this row, not meta.self_check")

    n = len(fails)
    print("{} {} — {} FAIL, {} WARN{}".format(
        "PASS" if n == 0 else "FAIL", args.plan, n, len(warns), " (strict)" if args.strict else ""))
    sys.exit(min(n, 255))


if __name__ == "__main__":
    main()
