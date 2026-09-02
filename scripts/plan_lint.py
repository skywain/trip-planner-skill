#!/usr/bin/env python3
"""plan_lint.py — the machine gate for plan.geo.json before rendering.

    python3 scripts/plan_lint.py plan.geo.json [--strict] [--art plan.art.json] [--ics gates.ics]

Exit code = number of FAIL lines (0 = clean), like themes/qc.py. WARN lines go to
stderr and never change the exit code.

Why it exists: route_tools `check` proves the geography and themes/qc.py proves the
HTML, but neither looks at what the plan *says* — on a 2026-09 test a plan with no
`brief` at all, "awaiting qc.py" in meta.self_check, "## 总计" in a budget cell and
nine unfilled art placeholders rendered two pages with an empty 行前须知 section while
every exit code stayed green, and the planner reported "nine brief cards complete".
Weak planners trust exit codes; this file makes the required sections part of them.

Default checks (every plan, including the pre-2026-09 examples):
  - JSON parses; `days[]` present, each with a date and a non-empty timeline
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
    when missing (FAIL under --strict — since 2026-09 every plan has ladder gates)
--strict adds the 2026-09 contract (new plans; the older examples predate it):
  - brief keys in canonical order and the required cards present (visa · emergency ·
    safety · health · holidays · weather · money · connectivity · insurance)
  - brief.safety opens with the advisory line ("advisory:" / "警示:")
  - checklist carries a visa row, a travel-clinic row, and the T-14 / T-7 / T-3 / T-1
    ladder rows; the last decisions[] row repeats the self-check line
  - prefs.pictures present (native | key | stock)
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
SELF_CHECK = re.compile(r"(self-checked:\s*\d+|自检[::]?\s*发现并修复\s*\d+)")
ADVISORY = re.compile(r"^\s*(advisory|警示|旅行警示)\s*[::]", re.I)
LADDER = ["T-14", "T-7", "T-3", "T-1"]

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


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--strict", action="store_true",
                    help="also enforce the 2026-09 brief / checklist contract")
    ap.add_argument("--art", default=None, help="art file (default: <plan>.art.json beside it)")
    ap.add_argument("--ics", default=None, help="gates .ics (default: gates.ics / trip.ics beside it)")
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
    days = plan.get("days")
    if not isinstance(days, list) or not days:
        fail("days[] missing or empty")
    else:
        for i, d in enumerate(days, 1):
            if not isinstance(d, dict) or not d.get("date"):
                fail("day {} has no date".format(i))
            elif not d.get("timeline"):
                fail("day {} ({}) has an empty timeline".format(i, d.get("date")))

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
    keys = [norm_key(k) for k in brief]

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
    pictures = (plan.get("prefs") or {}).get("pictures")
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
               "generate it: python3 scripts/route_tools.py ics {} -o gates.ics"
               .format(", ".join(os.path.basename(c) for c in ics_candidates if c), args.plan))
        (fail if args.strict else warn)(msg)

    # ---- strict: the 2026-09 contract ----
    if args.strict:
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
        rows = plan.get("checklist") or []
        text = " \n ".join(json.dumps(r, ensure_ascii=False) for r in rows)
        if not re.search(r"visa|签证|e-?visa|入境", text, re.I):
            fail("checklist has no visa / entry row")
        if not re.search(r"clinic|门诊|疫苗|vaccin", text, re.I):
            fail("checklist has no travel-clinic consult row")
        for t in LADDER:
            if not re.search(re.escape(t) + r"(?!\d)", text):
                fail("checklist has no {} ladder row (output-template.md "
                     "§Pre-departure re-check ladder)".format(t))
        decisions = plan.get("decisions") or []
        if not decisions or not SELF_CHECK.search(str(decisions[-1])):
            fail("last decisions[] row does not repeat the self-check line "
                 "(seven of eight themes render decisions, not meta.self_check)")

    n = len(fails)
    print("{} {} — {} FAIL, {} WARN{}".format(
        "PASS" if n == 0 else "FAIL", args.plan, n, len(warns), " (strict)" if args.strict else ""))
    sys.exit(n)


if __name__ == "__main__":
    main()
