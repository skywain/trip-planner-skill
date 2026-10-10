#!/usr/bin/env python3
"""plan_lint.py — the machine gate for plan.geo.json before rendering.

    python3 scripts/plan_lint.py plan.geo.json [--strict] [--asof YYYY-MM-DD] [--art plan.art.json] [--ics gates.ics] [--kml trip.kml]

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
  - no placeholder text anywhere: PLACEHOLDER / TODO / TBD, a bracketed "[to be added |
    filled …]" note, 待补充 / 待填写 standing alone or in brackets; "awaiting" in meta,
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
  - a row's `kind`, when present, is anchor | hop | meal | free
  - timeline rows, only where the keys are present (output-template.md §city-block):
    `sub_stops` a non-empty list of objects, each with a `name` and a `query` or
    `lat`+`lon`; `view` (free text: the picture) a non-empty string; `must` / `tour`
    are true or absent; `must: true` carries a `view` and a `stand`; on a `tour: true`
    row every `must` sub-stop's `confirmed` starts "in writing" or "pending". WARN:
    `pending`, a sub-stop `link` or a row `sub_map` that is not an http(s) URL (run
    `route_tools.py links --write`), `sub_stops` on a row that is not `kind: anchor`
  - a self-drive option (prefs.travel_style self-drive | mixed, prefs.drivers, a
    legs[] row whose type names a rental / self-drive, or a stop with driver: self)
    needs a `brief.driving` card — legality of the licence where the car is driven,
    before rentability
  - every brief card is one string; on a tour row a must-see's `pending` confirmation
    names a checklist row by its item text
  - (2026-10, round 2) more fields, each checked only where present, each defined in
    output-template.md: a row's `hours` is {text, as_of: YYYY-MM-DD, src: http(s)}
    or the literal "unverified" / "open access" (WARN: "unverified" on an anchor);
    a day's `decision_points` (on a day whose date is YYYY-MM-DD) are objects with `t`
    HH:MM and `what` / `check` / `if_no`; `src`, when present, an http(s) URL; `date`,
    when present, the day or the day before; no two on one day share a `what`;
    `brief.driving`
    is read per line carrying "legality:" / "合法性:" — a verdict from the enum right
    after the label (followed by '·' or the end of the line; after a zh label the
    English enum word is accepted too), a desk part after the verdict and an as-of
    stamp on that line, one FAIL each, one for a card with no legality line (WARN: no
    insurance word on the card); a `tour` key on a day object FAILs (it belongs on the
    row); `prefs.languages` set with no tour: true row → WARN; a T-N deadline whose ISO
    date is not departure − N → WARN (FAIL under --strict);
    `meta.review` is {mode, lenses: [{lens, note}], confirmed, refuted} — mode
    reviewers | single pass, three or more distinct lenses of safety | driving | timing
    | rules | hazards each with a note, `driving` whenever a self-drive option exists,
    and every review clause present (meta.self_check, the last decisions[] row)
    agrees with it (WARN: no http(s) source in any note or finding); `stops[].driver`
    ∈ self | hired | taxi | tour (WARN: driver on a stop that is not mode: drive; a
    day mixing driver: self with drive stops that carry none); every `prefs.must_see`
    entry has a `name` and, when present, a non-empty `view`; one with a `view` needs
    a must: true sub-stop carrying a view and a stand, matched by name / query or by
    its row's `what` (the phrases are never compared); `hotels[].options[].checkout` /
    `bag_hold` are non-empty strings (WARN: checkout without HH:MM); `refundable` on a
    checklist or legs row is true or false
--strict adds the 2026-09 contract (new plans; the older examples predate it):
  - brief keys in canonical order and the required cards present (visa · emergency ·
    safety · health · holidays · weather · money · connectivity · insurance)
  - brief.safety opens with the advisory line ("advisory:" / "警示:")
  - checklist carries a visa row, a travel-clinic row, and the T-14 / T-7 / T-3 / T-1
    ladder rows; the last decisions[] row repeats the self-check line
  - prefs.pictures present (native | key | stock)
  - every timeline row carries a `t` (a clock, a range or the departure-day T-formula)
    and a `kind` — a stop list copied into the timeline is not an hour-level plan
  - every day has at least one stop (airports on move days) and a `sun` that is the
    canonical `route_tools.py sun --write` string — a stop-less day is skipped by `sun`
    and a hand-written or "待计算" value is what ends up in the page
  - (2026-10) a trip of seven days or more carries an on-trip re-audit row (D+N in the
    row's item, an ISO date in its deadline)
  - (2026-10, round 2) the hours window: from --asof (default meta.generated; neither
    an ISO date → one FAIL; never the wall clock) through --asof + 14 days, every
    kind: anchor row carries `hours`, and an object's as_of on such a day is no older
    than that day − 14 and no later than the as-of date — the T-3 ladder row and every on-trip re-audit row re-run
    this with --asof <that row's date>
  - a driving card with a jurisdiction (the text before a line's first " · ") whose
    verdict is not legal / unverified while a stop carries driver: self needs a
    decisions[] row naming self-drive / 自驾 (not a negation) that records the
    traveller's choice — else FAIL, naming the jurisdiction
  - the independent review — its trigger set is stated here, once (phase-6-assemble.md
    §Independent review and SKILL.md point here): a self-drive option exists (the four
    conditions above), or any timeline row carries `tour: true`, or any checklist or
    legs row carries `"refundable": false` (the explicit flag; never a keyword match
    on the row's text). When triggered, meta.self_check and the last decisions[] row
    carry the clause ("· independent review: C confirmed, R refuted" or "· independent
    review: single pass"; zh "· 独立复核:确认 C 条,驳回 R 条" / "· 独立复核:单人通读")
    and meta.review exists. A timed check-in with no tour block stays procedure-only.
"""
import argparse
import datetime as _dt
import json
import os
import re
import sys

CANON = ["visa", "emergency", "safety", "health", "holidays", "weather", "money",
         "connectivity", "insurance", "baggage"]
REQUIRED = ["visa", "emergency", "safety", "health", "holidays", "weather", "money",
            "connectivity", "insurance"]
PLACEHOLDER = re.compile(r"\b(PLACEHOLDER|TODO|TBD)\b|\[to be (?:added|filled)[^\]]*\]|^\s*(?:待补充|待填写)\s*$|[\[(（【]\s*(?:待补充|待填写)\s*[\])）】]", re.I)
AWAITING = re.compile(r"\bawaiting\b", re.I)
SELF_CHECK = re.compile(r"(self-checked:\s*\d+|自检[:\uff1a]?\s*发现并修复\s*\d+)")
ADVISORY = re.compile(r"^\s*(advisory|警示|旅行警示)\s*[:\uff1a]", re.I)
LADDER = ["T-14", "T-7", "T-3", "T-1"]
ON_TRIP = re.compile(r"(?<![A-Za-z0-9])D\+\d+")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
PENDING_SEP = re.compile(r"^\s*[·・•\-—–:\uff1a]\s*")
REVIEW = re.compile(r"independent review\s*[:\uff1a]|独立复核\s*[:\uff1a]", re.I)
SUN_OK = re.compile(r"^(?:天亮|dawn) \d{2}:\d{2} · ☀ \d{2}:\d{2} / 🌇 \d{2}:\d{2} · \S+ · sunrise-sunset\.org$")
HOURS_LITERALS = ("unverified", "open access")
KINDS = ("anchor", "hop", "meal", "free")
HOURS_WINDOW_DAYS = 14         # --strict: as-of .. as-of + 14 carry hours; there as_of >= day - 14
HHMM = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d")
CLOCK = re.compile(r"(?<!\d)\d{1,2}:\d{2}(?!\d)")
DRIVERS = ("self", "hired", "taxi", "tour")
LENSES = ("safety", "driving", "timing", "rules", "hazards")
REVIEW_MODES = ("reviewers", "single pass")
REVIEW_COUNTS = re.compile(
    r"independent review\s*[:：]\s*(\d+)\s*confirmed\s*[,，]\s*(\d+)\s*refuted"
    r"|独立复核\s*[:：]\s*确认\s*(\d+)\s*条\s*[,，、]\s*驳回\s*(\d+)\s*条", re.I)
REVIEW_SINGLE = re.compile(r"independent review\s*[:：]\s*single pass"
                           r"|独立复核\s*[:：]\s*单人通读", re.I)
# brief.driving, read per line that carries the legality label (phase-1-brief.md
# §Driving card holds the line form and the enum). Longest verdict first: "not legal"
# before "legal", 不合法 before 合法; an en verdict ends at " ·" or the end of the line,
# so "legal with an IDP" is not one; zh verdicts are matched with whitespace removed and
# end at "·" or the end of the line too, so 合法但需IDP is not one either.
LEGALITY_LABEL = re.compile(r"(?:legality|合法性)\s*[:：]", re.I)
VERDICTS_EN = ("legal with official translation", "legal with IDP", "not legal",
               "unverified", "legal")
VERDICTS_ZH = ("持官方翻译件合法", "持官方翻譯件合法", "持IDP合法", "不合法", "未核实", "未核實",
               "待核实", "待核實", "合法")
VERDICT_EN = re.compile(r"\s*(?:" + "|".join(re.escape(v) for v in VERDICTS_EN)
                        + r")(?=\s*·|\s*$)", re.I)
VERDICT_ZH = re.compile("(?:" + "|".join(VERDICTS_ZH) + r")(?=·|$)", re.I)
DESK = re.compile(r"\b(?:rentals?|rentab\w*|desks?|counters?|hire)\b"
                  r"|租车|租車|柜台|櫃檯|レンタカー", re.I)
AS_OF = re.compile(r"(?<![\dA-Za-z])20\d{2}-\d{2}(?:-\d{2})?(?!\d)|20\d{2}\s*年\s*\d{1,2}\s*月")
INSURANCE = re.compile(r"insur|waiver|CDW|LDW|保险|保險", re.I)
_CJK = re.compile(r"[぀-ヿ㐀-鿿]")
# A legs[] row that is a self-driven vehicle. Not stops[].mode "drive" — the examples use
# that for taxis and hired cars with a driver (Mexico, Morocco, Turkey, Vietnam); a stop
# the traveller drives into says so with driver: self, and that is the trigger.
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


def is_text(v):
    """A non-empty string — the shape of a free-text field such as `view` or `stand`."""
    return isinstance(v, str) and bool(v.strip())


def iso_date(v):
    """A YYYY-MM-DD string as a date, else None — the shape of every as-of key."""
    try:
        return (_dt.date.fromisoformat(v)
                if isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v) else None)
    except ValueError:
        return None


def asof_arg(v):
    d = iso_date(v)
    if d is None:
        raise argparse.ArgumentTypeError("not YYYY-MM-DD: {!r}".format(v))
    return d


def check_hours(where, row):
    """A row's `hours` (output-template.md §city-block): {text, as_of, src} read from
    the venue's own page, or the literal "unverified" / "open access"."""
    h = row["hours"]
    if isinstance(h, str):
        if h not in HOURS_LITERALS:
            fail("{}: hours {!r} is a bare string — write {{\"text\", \"as_of\": YYYY-MM-DD, "
                 "\"src\": http(s) URL}} as read from the venue's own page, or the literal "
                 "\"unverified\" / \"open access\" (output-template.md §city-block)"
                 .format(where, h[:40]))
        elif h == "unverified" and row.get("kind") == "anchor":
            warn("{}: hours unverified — read the venue's own page for this date before the "
                 "day (T-3 row / on-trip re-audit)".format(where))
        return
    if not isinstance(h, dict):
        fail("{}: hours is {} — an object {{text, as_of, src}} or \"unverified\" / "
             "\"open access\" (absent, never null)".format(where, repr(h)[:40]))
        return
    if not (isinstance(h.get("text"), str) and h["text"].strip()):
        fail("{}: hours.text is empty — the hours as the venue's page states them "
             "('09:00-17:00 · last entry 16:30')".format(where))
    if iso_date(h.get("as_of")) is None:
        fail("{}: hours.as_of {!r} is not YYYY-MM-DD — the day the page was read"
             .format(where, h.get("as_of")))
    if not is_http(h.get("src")):
        fail("{}: hours.src {!r} is not an http(s) URL — the page the hours were read from"
             .format(where, h.get("src")))


def check_decision_points(i, d):
    """A day's `decision_points` (output-template.md §city-block): the go / no-go
    calls taken on the day or the evening before; `route_tools.py ics` turns each
    into a calendar event at date + t."""
    dps = d["decision_points"]
    where = "day {} ({})".format(i, d.get("date"))
    if not isinstance(dps, list) or not dps or not all(isinstance(x, dict) for x in dps):
        fail("{}: decision_points must be a non-empty list of objects, got {} — absent, "
             "never null (output-template.md §city-block)".format(where, repr(dps)[:40]))
        return
    day = iso_date(d.get("date"))
    if day is None and d.get("date"):          # a missing date is reported once, by main()
        fail("{}: the day's date {!r} is not YYYY-MM-DD — decision points are placed at it "
             "(route_tools.py ics)".format(where, d.get("date")))
    for k, x in enumerate(dps, 1):
        dw = "{} decision point {} {!r}".format(where, k, str(x.get("what", ""))[:40])
        if not (isinstance(x.get("t"), str) and HHMM.fullmatch(x["t"])):
            fail("{}: t {!r} is not HH:MM — ics places the event at the day's date + t"
                 .format(dw, x.get("t")))
        for key, what in (("what", "what is decided"),
                          ("check", "what is read, in words — the feed's URL goes in src"),
                          ("if_no", "the fallback when the answer is no")):
            if not (isinstance(x.get(key), str) and x[key].strip()):
                fail("{}: no {} — {}".format(dw, key, what))
        if "src" in x and not is_http(x["src"]):
            fail("{}: src {!r} is not an http(s) URL".format(dw, x["src"]))
        if "date" in x:
            dd = iso_date(x["date"])
            if dd is None:
                fail("{}: date {!r} is not YYYY-MM-DD — the day itself (the default, leave "
                     "the key out) or the day before".format(dw, x["date"]))
            elif day and not 0 <= (day - dd).days <= 1:
                fail("{}: date {} is neither the day ({}) nor the day before — a gate "
                     "further ahead is a checklist row, not a decision point "
                     "(scheduling.md rule 10)".format(dw, x["date"], day))
    whats = [str(x.get("what", "")).strip() for x in dps]
    dup = sorted({w for w in whats if w and whats.count(w) > 1})
    if dup:
        fail("{}: two decision points share what {!r} — ics derives the UID from the day + "
             "what, so one calendar event would replace the other; word them apart "
             "('decide: …' / 'confirm at breakfast: …')".format(where, dup[0]))


def check_stops(i, d):
    """`stops[].driver` (output-template.md §city-block). Returns where the day's
    first driver: self stop is, or None — that stop makes the plan a self-drive plan."""
    stops = d.get("stops")
    selfdrive, untagged = None, 0
    for j, st in enumerate(stops if isinstance(stops, list) else [], 1):
        if not isinstance(st, dict):
            continue
        sw = "day {} ({}) stop {} {!r}".format(i, d.get("date"), j, str(st.get("name", ""))[:30])
        if "driver" not in st:
            untagged += st.get("mode") == "drive"
            continue
        if st["driver"] not in DRIVERS:
            fail("{}: driver {!r} is not one of {} — self = the traveller drives, hired = a "
                 "car with driver or a pre-booked transfer, taxi = taxi or ride-hail, tour = "
                 "the tour's vehicle".format(sw, st["driver"], " | ".join(DRIVERS)))
            continue
        if st.get("mode") != "drive":
            warn("{}: driver on a mode:{} stop — it says who drives the hop into this stop, "
                 "so it belongs on mode: drive".format(sw, st.get("mode")))
        if st["driver"] == "self" and selfdrive is None:
            selfdrive = sw
    if selfdrive and untagged:
        warn("day {} ({}): driver: self beside {} drive stop(s) with no driver — every drive "
             "stop says who drives it: driver: self on each one the traveller drives, taxi / "
             "hired / tour on one someone else runs (navigation.md §Self-drive days)"
             .format(i, d.get("date"), untagged))
    return selfdrive


LEGAL_OK = ("legal", "legal with idp", "legal with official translation",
            "合法", "持idp合法", "持官方翻译件合法", "持官方翻譯件合法")


def check_driving_card(card):
    """brief.driving, per line that carries the legality label (phase-1-brief.md
    §Driving card is the form's one definition): a verdict right after the label, a
    desk part and an as-of stamp on the line — one FAIL each — and one FAIL for a
    card with no legality line at all. Returns the verdicts read (case-folded)."""
    found = False
    verdicts = []
    for ln in str(card).split("\n"):
        bare = re.sub(r"https?://[!-~]+", "", ln)    # a date inside a URL is not the as-of (a URL ends at the first non-ASCII char)
        m = LEGALITY_LABEL.search(bare)
        if not m:
            continue
        found = True
        lw = "brief.driving line {!r}".format(ln.strip()[:40])
        if m.group(0).startswith("合法性"):
            packed = re.sub(r"\s+", "", bare)
            lm = LEGALITY_LABEL.search(packed)
            verdict = VERDICT_ZH.match(packed, lm.end())
            tail = packed[verdict.end() if verdict else lm.end():]
            if not verdict:                      # the English enum word after a zh label is fine
                verdict = VERDICT_EN.match(bare, m.end())
                if verdict:
                    tail = bare[verdict.end():]
        else:
            verdict = VERDICT_EN.match(bare, m.end())
            tail = bare[verdict.end() if verdict else m.end():]
        if verdict:
            verdicts.append((ln.split("·")[0].strip().casefold(),
                             re.sub(r"\s+", " ", verdict.group(0)).strip().casefold()))
        if not verdict:
            fail("{}: no verdict right after the legality label — one of {} (zh: 合法 · 持 IDP "
                 "合法 · 持官方翻译件合法 · 不合法 · 未核实), followed by ' ·' or the end of the "
                 "line; 'legal with an IDP' is not a verdict (phase-1-brief.md §Driving card)"
                 .format(lw, " | ".join(VERDICTS_EN)))
        if not DESK.search(tail):             # the desk part comes after the verdict
            fail("{}: no desk part — whether a rental desk hands over keys is a separate "
                 "question from legality: '· desks: {{brand policy, …}}' (zh 租车柜台:…) after "
                 "the verdict on that line (phase-1-brief.md §Driving card)".format(lw))
        if not AS_OF.search(bare):
            fail("{}: no as-of stamp — licence rules and desk policies move: end the line "
                 "'· as of YYYY-MM' (zh 截至 YYYY-MM or 截至 YYYY年M月)".format(lw))
    if not found:
        fail("brief.driving has no legality line — one per jurisdiction driven: "
             "'{jurisdiction} · {licence country} licence — legality: {verdict} · desks: … · "
             "{source} · as of YYYY-MM' (zh … 合法性:{结论} …) (phase-1-brief.md §Driving card)")
    if not INSURANCE.search(str(card)):
        warn("brief.driving carries no insurance word (insurance / waiver / CDW / LDW / 保险) "
             "— the insurance consequence is stated once on the card (phase-1-brief.md "
             "§Driving card step 3)")
    return verdicts


def check_review(review, clauses, drive):
    """meta.review — the record behind the review clause (phase-6-assemble.md
    §Independent review): its shape, then every clause present must agree with it.
    A missing clause is --strict's business (when the review is triggered)."""
    if not isinstance(review, dict):
        fail("meta.review is {} — an object {{mode, lenses: [{{lens, note}}], confirmed, "
             "refuted}} (phase-6-assemble.md §Independent review)".format(repr(review)[:40]))
        return
    mode = review.get("mode")
    if mode not in REVIEW_MODES:
        fail("meta.review.mode {!r} is not one of {}".format(mode, " | ".join(REVIEW_MODES)))
    lenses = review.get("lenses")
    seen = []
    for k, l in enumerate(lenses if isinstance(lenses, list) else []):
        if not isinstance(l, dict):
            fail("meta.review.lenses[{}] is not an object {{lens, note}}".format(k))
        elif l.get("lens") not in LENSES:
            fail("meta.review.lenses[{}]: lens {!r} is not one of {}"
                 .format(k, l.get("lens"), " | ".join(LENSES)))
        elif not (isinstance(l.get("note"), str) and l["note"].strip()):
            fail("meta.review.lenses[{}] ({}): no note — what was checked and against what; a "
                 "lens with nothing to look at is left out, not padded".format(k, l["lens"]))
        else:
            seen.append(l["lens"])
    if len(set(seen)) < 3:
        fail("meta.review carries {} distinct lens(es) with a note — at least three of {} "
             "(phase-6-assemble.md §Independent review)".format(len(set(seen)), " | ".join(LENSES)))
    if drive and "driving" not in seen:
        fail("meta.review has no driving lens although a self-drive option exists ({}) — add "
             "{{\"lens\": \"driving\", \"note\": …}}".format(", ".join(drive)))
    counts = {}
    bad = False
    for key in ("confirmed", "refuted"):
        v = review.get(key, [])
        if not isinstance(v, list):
            fail("meta.review.{} is {} — a list of findings (absent when empty, never null)"
                 .format(key, repr(v)[:30]))
            v = []
            bad = True
        counts[key] = v
    nc, nr = len(counts["confirmed"]), len(counts["refuted"])
    for where, text in clauses:
        if not REVIEW.search(text):
            continue
        m = REVIEW_COUNTS.search(text)
        c, r = (int(m.group(1) or m.group(3)), int(m.group(2) or m.group(4))) if m else (None, None)
        if mode == "single pass":
            if m:
                fail("{} says {} confirmed, {} refuted but meta.review.mode is single pass — a "
                     "single pass writes 'independent review: single pass' / '独立复核:单人通读'"
                     .format(where, c, r))
            elif not REVIEW_SINGLE.search(text):
                fail("{}: the review clause reads neither 'single pass' nor counts ({!r})"
                     .format(where, text[-60:]))
        elif mode == "reviewers":
            if m and not bad and (c, r) != (nc, nr):
                fail("{} says {} confirmed, {} refuted but meta.review lists {} and {} — the "
                     "clause is the summary of meta.review".format(where, c, r, nc, nr))
            elif not m:
                fail("{}: the review clause carries no counts ({!r}) but meta.review.mode is "
                     "reviewers — 'independent review: C confirmed, R refuted' / "
                     "'独立复核:确认 C 条,驳回 R 条'".format(where, text[-60:]))
    texts = ([l.get("note") for l in lenses if isinstance(l, dict)]
             if isinstance(lenses, list) else []) + counts["confirmed"] + counts["refuted"]
    if not any(isinstance(t, str) and re.search(r"https?://", t) for t in texts):
        warn("meta.review: no lens note or finding carries an http(s) source — a review "
             "against primary sources names one")


def must_see_hit(name, days):
    """True when some must: true sub-stop with a view and a stand is named for the
    must-see: its name or query contains or is contained in the entry's name, or its
    row's `what` does (case-folded; the shorter side ≥ 4 chars, 2 when the name
    carries CJK). The two view phrases are free text and never compared."""
    n = name.casefold().strip()
    need = 2 if _CJK.search(n) else 4

    def near(h):
        h = str(h or "").casefold().strip()
        return min(len(n), len(h)) >= need and (n in h or h in n)
    for d in days:
        rows = d.get("timeline") if isinstance(d, dict) else None
        for row in rows if isinstance(rows, list) else []:
            if not isinstance(row, dict) or not isinstance(row.get("sub_stops"), list):
                continue
            subs = [s for s in row["sub_stops"] if isinstance(s, dict)
                    and s.get("must") is True and is_text(s.get("view"))
                    and is_text(s.get("stand"))]
            if subs and (near(row.get("what"))
                         or any(near(s.get("name")) or near(s.get("query")) for s in subs)):
                return True
    return False


def check_rows(i, d, items=()):
    """The optional row fields (output-template.md §city-block). Every check fires
    only when its key is present, so a plan without them is untouched."""
    if "tour" in d:
        fail("day {} ({}) carries tour at day level — tour: true belongs on the timeline row "
             "the guided block owns, where the lint reads it (output-template.md §city-block)"
             .format(i, d.get("date")))
    rows = d.get("timeline")
    for r, row in enumerate(rows if isinstance(rows, list) else [], 1):
        if not isinstance(row, dict):
            fail("day {} ({}) row {} is not an object, got {}".format(
                i, d.get("date"), r, repr(row)[:40]))
            continue
        where = "day {} ({}) row {} {!r}".format(i, d.get("date"), r,
                                                 str(row.get("what", ""))[:40])
        if "kind" in row and row["kind"] not in KINDS:
            fail("{}: kind {!r} is not one of {} (output-template.md §city-block)"
                 .format(where, row["kind"], " | ".join(KINDS)))
        if "tour" in row and row["tour"] is not True:
            fail("{}: tour is {!r} — true, or leave the key out (absent, never null)"
                 .format(where, row["tour"]))
        if "sub_map" in row and not is_http(row["sub_map"]):
            warn("{}: sub_map is not an http(s) URL — it is script-owned, run "
                 "route_tools.py links --write".format(where))
        if "hours" in row:
            check_hours(where, row)
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
            missing = [k for k in ("view", "stand") if not is_text(s.get(k))]
            if "view" in s and not is_text(s["view"]) and s.get("must") is not True:
                fail("{}: view is {!r} — a short phrase naming the picture, or leave the key "
                     "out (absent, never null)".format(sw, s["view"]))
            if "must" in s and s["must"] is not True:
                fail("{}: must is {!r} — true, or leave the key out (absent, never null)"
                     .format(sw, s["must"]))
            if s.get("must") is True and missing:
                said = [("no " + k) if k not in s else "{} {!r}".format(k, s[k]) for k in missing]
                fail("{}: must:true with {} — name the picture the traveller came for "
                     "(view) and where to stand for it (stand), both non-empty text"
                     .format(sw, " and ".join(said)))
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
    ap.add_argument("--asof", type=asof_arg, default=None, metavar="YYYY-MM-DD",
                    help="--strict: the date the hours window starts from (default "
                         "meta.generated, never today; the T-3 row and every on-trip "
                         "re-audit row pass their own date)")
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
    self_stops, tour_rows = [], []      # the review's triggers that live on days (below)
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
                if "decision_points" in d:
                    check_decision_points(i, d)
                self_stop = check_stops(i, d)
                if self_stop and not self_stops:
                    self_stops.append(self_stop + " driver = self")
                tour_rows.extend("day {} ({}) row {!r} carries tour: true".format(
                    i, d.get("date"), str(row.get("what", ""))[:40])
                    for row in (d.get("timeline") if isinstance(d.get("timeline"), list) else [])
                    if isinstance(row, dict) and row.get("tour") is True)

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
    drive.extend(self_stops)
    if drive and "driving" not in keys:
        fail("brief.driving missing but a self-drive option exists ({}) — legality of "
             "each driver's licence where the car is driven comes before rentability "
             "(phase-1-brief.md §Driving card)".format(", ".join(drive)))
    card = next((v for k, v in brief.items() if norm_key(k) == "driving"), None)
    verdicts = check_driving_card(card) if isinstance(card, str) and card.strip() else []

    # ---- prefs.languages (a guided option may have been priced) but no row is a tour row ----
    has_tour_row = any(isinstance(r, dict) and r.get("tour") is True
                       for d in (days if isinstance(days, list) else []) if isinstance(d, dict)
                       for r in (d.get("timeline") if isinstance(d.get("timeline"), list) else []))
    if prefs.get("languages") and not has_tour_row:
        warn("prefs.languages is set (a guided option may have been priced) and no timeline row "
             "carries tour: true — if the traveller chose the guided block, mark that row tour: "
             "true; only there are its must-sees' confirmations checked (output-template.md "
             "§city-block)")

    # ---- prefs.must_see: every entry with a view has its must sub-stop ----
    if "must_see" in prefs:
        ms = prefs["must_see"]
        if not isinstance(ms, list) or not ms or not all(
                isinstance(e, dict) and isinstance(e.get("name"), str) and e["name"].strip()
                for e in ms):
            fail("prefs.must_see must be a non-empty list of {{\"name\", \"view\"?}} objects, got "
                 "{} — absent, never null (output-template.md §Intake prefs)".format(repr(ms)[:40]))
        else:
            for e in ms:
                if "view" not in e:
                    continue
                if not is_text(e["view"]):
                    fail("prefs.must_see {!r}: view is {!r} — the picture the traveller described "
                         "(or the one assumed, said so in prefs.notes), or leave the key out "
                         "(absent, never null)".format(e["name"], e["view"]))
                elif not must_see_hit(e["name"], days if isinstance(days, list) else []):
                    fail("prefs.must_see {!r} ({!r}): no must: true sub-stop with a view and a stand "
                         "is named for it — write or complete the must sub-stop (name, query, view, stand) on the "
                         "anchor row whose `what` carries the must-see's name (phase-4-days.md §Per "
                         "city step 2); a must-see the traveller dropped, or a picture the operator "
                         "refused in writing: edit or remove this entry's view and write the "
                         "decisions[] row (phase-0-intake.md §prefs)".format(e["name"], e["view"][:40]))

    # ---- hotels: check-out and bag hold sit on the booked option ----
    hotels = plan.get("hotels") if isinstance(plan.get("hotels"), list) else []
    for hi, h in enumerate(hotels):
        if not isinstance(h, dict):
            continue
        for key in ("checkout", "bag_hold"):
            if key in h:
                warn("hotels[{}].{} sits on the base row — it belongs on the booked property, "
                     "hotels[].options[] (the page prints it under the option)".format(hi, key))
        opts = h.get("options") if isinstance(h.get("options"), list) else []
        for oi, o in enumerate(opts):
            if not isinstance(o, dict):
                continue
            ow = "hotels[{}].options[{}] {!r}".format(hi, oi, str(o.get("name", ""))[:30])
            for key, what in (("checkout", "the check-out time as the property's own policies "
                                           "page states it ('11:00 · property FAQ · as of YYYY-MM')"),
                              ("bag_hold", "where bags wait and until when, from the same page")):
                if key not in o:
                    continue
                v = o[key]
                if not (isinstance(v, str) and v.strip()):
                    fail("{}: {} is {} — one string, {} (absent, never null)"
                         .format(ow, key, repr(v)[:30], what))
                elif key == "checkout" and not CLOCK.search(v):
                    warn("{}: checkout carries no HH:MM ({!r}) — read the time off the property's "
                         "own page, never the 12:00 in your head".format(ow, v[:40]))

    # ---- the independent review's trigger set (docstring): self-drive · tour · refundable ----
    nonref = []
    for sect in ("checklist", "legs"):
        rows = plan.get(sect) if isinstance(plan.get(sect), list) else []
        for ri, r in enumerate(rows):
            if not isinstance(r, dict) or "refundable" not in r:
                continue
            if not isinstance(r["refundable"], bool):
                fail("{}[{}].refundable is {!r} — true or false, or leave the key out (absent, "
                     "never null); false is the flag the independent review keys on"
                     .format(sect, ri, r["refundable"]))
            elif r["refundable"] is False:
                nonref.append("{}[{}] {!r} carries refundable: false".format(
                    sect, ri, str(r.get("item") or r.get("type") or "")[:30]))
    review_why = (["a self-drive option exists ({})".format(", ".join(drive))] if drive else []) \
        + tour_rows[:1] + nonref[:1]

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

    # ---- meta.review: the record behind the review clause (when present) ----
    decisions = plan.get("decisions") if isinstance(plan.get("decisions"), list) else []
    clauses = [("meta.self_check", sc)] + (
        [("last decisions[] row", str(decisions[-1]))] if decisions else [])
    if "review" in meta:
        check_review(meta["review"], clauses, drive)

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

    # ---- T-N deadlines: the ISO date must be departure − N (route_tools ics trusts the date) ----
    dep0 = None
    try:
        dep0 = _dt.date.fromisoformat(str(days[0].get("date", ""))[:10])
    except (ValueError, IndexError, KeyError, AttributeError, TypeError):
        pass
    for r in (checklist if isinstance(checklist, list) else []):
        if not isinstance(r, dict):
            continue
        dl = str(r.get("deadline", ""))
        tm, im = re.search(r"\bT-(\d+)\b", dl), ISO_DATE.search(dl)
        if dep0 and tm and im:
            try:
                got = _dt.date.fromisoformat(im.group(0))
            except ValueError:
                continue
            want = dep0 - _dt.timedelta(days=int(tm.group(1)))
            if got != want:
                (fail if args.strict else warn)(
                    "checklist row {!r}: deadline {!r} — T-{} from departure {} is {}, not {}; "
                    "ics trusts the date (output-template.md §Pre-departure re-check ladder)"
                    .format(str(r.get("item", ""))[:40], dl[:40], tm.group(1), dep0, want, got))

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
        # every timeline row is an hour-level row: a clock and a kind (a stop list copied
        # into timeline[] passed every other gate in a 2026-10 Gemini end-to-end run)
        for i, d in enumerate(days if isinstance(days, list) else [], 1):
            rows = d.get("timeline") if isinstance(d, dict) and isinstance(d.get("timeline"), list) else []
            thin = [r for r, row in enumerate(rows, 1) if isinstance(row, dict)
                    and not (isinstance(row.get("t"), str) and row["t"].strip() and row.get("kind") in KINDS)]
            if thin:
                fail("day {} ({}): {} of {} timeline row(s) lack a t (a clock, a range or a T-formula) or a kind "
                     "({}) — a timeline is hour-level, not a stop list (scheduling.md §Scheduled-day "
                     "format; output-template.md §city-block)"
                     .format(i, d.get("date"), len(thin), len(rows), " | ".join(KINDS)))
        # the hours window, measured from --asof (default meta.generated) — never today
        asof = args.asof or iso_date(meta.get("generated"))
        if asof is None:
            fail("meta.generated {!r} missing or not YYYY-MM-DD — the hours window is measured "
                 "from it; pass --asof YYYY-MM-DD".format(meta.get("generated")))
        for i, d in enumerate(days if isinstance(days, list) and asof else [], 1):
            day = iso_date(d.get("date")) if isinstance(d, dict) else None
            if day is None or not 0 <= (day - asof).days <= HOURS_WINDOW_DAYS:
                continue
            rows = d.get("timeline") if isinstance(d.get("timeline"), list) else []
            for r, row in enumerate(rows, 1):
                if not isinstance(row, dict) or row.get("kind") != "anchor":
                    continue
                where = "day {} ({}) row {} {!r}".format(i, d.get("date"), r,
                                                         str(row.get("what", ""))[:40])
                if "hours" not in row:
                    fail("{}: an anchor inside the hours window ({} → +{} days) carries no hours "
                         "— read them from the venue's own page for this date ({{text, as_of, "
                         "src}}), or write \"unverified\" / \"open access\" (phase-4-days.md "
                         "§Per city step 2)".format(where, asof, HOURS_WINDOW_DAYS))
                elif isinstance(row["hours"], dict):
                    read = iso_date(row["hours"].get("as_of"))
                    if read is not None and read > asof:
                        fail("{}: hours read on {} — after the as-of date {}: when they were re-read "
                             "since, re-stamp meta.generated (output-template.md §Top-level plan "
                             "skeleton) or pass --asof <the re-read's date>; never move as_of back"
                             .format(where, read, asof))
                    elif read is not None and (day - read).days > HOURS_WINDOW_DAYS:
                        fail("{}: hours read on {} — re-read them inside the window (as_of ≥ {})"
                             .format(where, read, day - _dt.timedelta(days=HOURS_WINDOW_DAYS)))
        # the independent review: trigger set in the docstring, clause in both places + meta.review
        if review_why and not REVIEW.search(sc):
            fail("meta.self_check has no independent-review clause although {} — '… · "
                 "independent review: C confirmed, R refuted' / '… · 独立复核:确认 C 条,驳回 R 条' "
                 "(phase-6-assemble.md §Independent review)".format(review_why[0]))
        if not decisions or not SELF_CHECK.search(str(decisions[-1])):
            fail("last decisions[] row does not repeat the self-check line "
                 "(seven of eight themes render decisions, not meta.self_check)")
        elif review_why and REVIEW.search(sc) and not REVIEW.search(str(decisions[-1])):
            fail("last decisions[] row repeats the self-check count but not its "
                 "independent-review clause — the page prints this row, not meta.self_check")
        bad_j = sorted({j for j, v in verdicts
                        if not any(v2 in LEGAL_OK for j2, v2 in verdicts if j2 == j)})
        if bad_j and self_stops \
                and not any(SELF_DRIVE.search(str(x)) and not NOT_SELF_DRIVE.search(str(x))
                            for x in (decisions if isinstance(decisions, list) else [])):
            fail("brief.driving reads {} for {!r} but the plan is self-drive ({}) and no decisions[] "
                 "row records the traveller's choice — build the days on the legal option, or "
                 "record the choice as a decisions[] row naming self-drive / 自驾 with its source "
                 "(phase-1-brief.md §Driving card step 4)"
                 .format(" / ".join(v for j, v in verdicts if j == bad_j[0]), bad_j[0][:40],
                         ", ".join(self_stops)))
        if review_why and "review" not in meta:
            fail("meta.review missing although {} — the clause is the summary, meta.review is "
                 "the review behind it: {{mode, lenses: [{{lens, note}}], confirmed, refuted}} "
                 "(phase-6-assemble.md §Independent review)".format(review_why[0]))

    n = len(fails)
    print("{} {} — {} FAIL, {} WARN{}".format(
        "PASS" if n == 0 else "FAIL", args.plan, n, len(warns), " (strict)" if args.strict else ""))
    sys.exit(min(n, 255))


if __name__ == "__main__":
    main()
