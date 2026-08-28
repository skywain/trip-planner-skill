#!/usr/bin/env python3
"""Build/refresh manifest.json — the asset index for every generated image.

Scans all job JSON files (batch*.json, cover.json, mockups.json …) for
prompts/params, matches them to files on disk, records derived variants
(cut/md/sm/lg/webp) with sizes. Existing manifest entries win on fields
the scan can't know (cost, generated_at). Run after any manual cleanup;
gen.py also upserts entries automatically on each successful generation.

Usage: python3 build_manifest.py [--assets DIR] [--jobs DIR ...]
  --assets DIR  image library + manifest.json (default: themes/assets/)
  --jobs DIR    extra directory to scan for job JSON files (repeatable; the
                assets dir itself is always scanned). Entries whose job file
                is gone but whose images remain are kept from the old manifest.
"""
import argparse
import json
import pathlib

HERE = pathlib.Path(__file__).parent
ASSETS = HERE / "assets"          # overridden by --assets in main()
MANIFEST = ASSETS / "manifest.json"

KNOWN_COSTS = {  # from generation logs (usage.cost, USD)
    "liberty": 0.053, "golden-gate": 0.053, "prismatic": 0.053,
    "diamond-head": 0.053, "hero": 0.033, "cover-hero": 0.033,
    "mock-cover": 0.033, "mock-day": 0.033, "mock-flow": 0.033,
}


def variants(name):
    out = {}
    for suffix in ("png", "cut.png", "cut.webp", "webp", "md.webp", "sm.webp", "lg.webp"):
        p = ASSETS / f"{name}.{suffix}"
        if p.exists():
            out[suffix] = p.stat().st_size
    return out


def main():
    global ASSETS, MANIFEST
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--assets", type=pathlib.Path, default=ASSETS,
                    help="image library + manifest.json (default: themes/assets/)")
    ap.add_argument("--jobs", type=pathlib.Path, action="append", default=[],
                    metavar="DIR", help="extra dir of job JSON files (repeatable)")
    args = ap.parse_args()
    ASSETS = args.assets
    MANIFEST = ASSETS / "manifest.json"
    old = {}
    if MANIFEST.exists():
        old = {e["name"]: e for e in json.loads(MANIFEST.read_text()).get("assets", [])}

    job_files = []
    for d in [ASSETS] + list(args.jobs):
        job_files += sorted(pathlib.Path(d).glob("*.json"))
    entries = {}
    for jf in job_files:
        if jf.name in ("manifest.json", ".payload.json", "geocache.json"):
            continue
        try:
            jobs = json.loads(jf.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(jobs, list):
            continue
        for job in jobs:
            if not isinstance(job, dict) or "name" not in job or "prompt" not in job:
                continue
            name = job["name"]
            v = variants(name)
            if not v:
                # not in the assets dir (PNG-only originals live outside the
                # repo): keep the previous entry verbatim if there was one
                if name in old:
                    entries[name] = old[name]
                continue
            prev = old.get(name, {})
            entries[name] = {
                "name": name,
                "kind": ("mockup" if name.startswith("mock-") else
                         "probe" if name.startswith("probe") else "asset"),
                "prompt": job["prompt"],
                "params": {k: job[k] for k in
                           ("background", "aspect_ratio", "resolution", "quality")
                           if k in job},
                "model": prev.get("model", "openai/gpt-image-2 via OpenRouter"),
                "cost_usd": prev.get("cost_usd", KNOWN_COSTS.get(name)),
                "generated_at": prev.get("generated_at", "2026-08-05/06"),
                "source_job": prev.get("source_job", jf.name),
                "files": v,
                "transparent": "cut.webp" in v,
            }

    # keep entries whose job file vanished (job JSONs are not shipped);
    # refresh their variant sizes when the files are here, else keep verbatim
    for name, e in old.items():
        if name not in entries:
            if variants(name):
                e["files"] = variants(name)
            entries[name] = e

    data = {
        # must stay byte-identical to the hand-merged _readme in manifest.json —
        # this write overwrites it, so any drift here silently rewrites the manifest
        "_readme": ("Generated-image index — check here before generating a new image "
                    "and reuse what already exists. gen.py registers every successful "
                    "generation automatically; run build_manifest.py to refresh after "
                    "manual cleanup. transparent=true means a .cut.webp real-alpha "
                    "cutout exists. Test-trip assets (测试行程资产) are hand-merged in "
                    "by the main agent from trips/test-*/manifest.<trip>.json (without "
                    "running build_manifest.py — it would scramble the job↔png "
                    "relationships in the trip directories); those entries' files.png "
                    "refers to the png master under trips/, which stays out of the repo."),
        "style_anchor": ("Flat hand-drawn travel illustration, gouache paint texture "
                         "with soft grain, warm muted palette of terracotta, sand beige, "
                         "dusty teal and cream, clean rounded shapes, minimal cozy "
                         "storybook style — 贴纸类加: thick organic silhouette, no text, "
                         "no border, single isolated subject centered on a solid pure "
                         "white background, no shadow"),
        "assets": sorted(entries.values(), key=lambda e: (e["kind"], e["name"])),
    }
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    kinds = {}
    for e in entries.values():
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    print(f"manifest.json: {len(entries)} entries {kinds}")


if __name__ == "__main__":
    main()
