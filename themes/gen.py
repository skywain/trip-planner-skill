#!/usr/bin/env python3
"""OpenRouter gpt-image-2 generator for trip-planner illustration assets.

FALLBACK PATH: an agent that can generate images natively should use that
instead (no key to configure) — same specs and prompts, then the same
split_sheet / cutout / towebp / trip-manifest steps (ART-SCHEMA.md 生成器选择).
This script exists for environments without native generation.

Usage: python3 gen.py <jobs.json> [--outdir DIR] [--manifest PATH] [--dry-run]
Each job: {name, prompt, background, aspect_ratio, resolution, quality}
Saves <name>.png (+ a scratch .payload.json) into --outdir, upserts each
generation into --manifest, prints per-image cost + alpha verification.

  --outdir DIR     where PNGs land (default: themes/assets/, the shared
                   library). A trip keeps its own pictures beside its plan:
                   --outdir trips/kyoto-2027 — data_uri() searches the plan's
                   directory, so nothing has to be copied into themes/assets/.
  --manifest PATH  asset index to upsert into (default: themes/assets/
                   manifest.json). Give a trip its own, e.g.
                   trips/kyoto-2027/manifest.kyoto.json, so it never races
                   the shared index. Created if missing.
  --dry-run        print every payload that WOULD be sent (model, prompt,
                   params) and the exact output paths, then exit. No request,
                   no charge, no files written, manifest untouched.
The credential file (.auth_header — one line "Authorization: Bearer <OpenRouter key>",
passed to curl as a header file) is read ONLY from this script's directory whatever
--outdir says — never copy it into a trip folder. The key is never printed.

A job whose <name>.png already exists in --outdir is skipped (so a re-run
after a partial failure only pays for what is missing).
"""
import argparse
import base64
import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent          # credentials live here, always
ASSETS = HERE / "assets"                      # shared image library + manifest
API = "https://openrouter.ai/api/v1/images"
MODEL = "openai/gpt-image-2"


def payload_for(job):
    return {
        "model": MODEL,
        "prompt": job["prompt"],
        "output_format": "png",
        "background": job.get("background", "auto"),
        "aspect_ratio": job.get("aspect_ratio", "1:1"),
        "resolution": job.get("resolution", "1K"),
        "quality": job.get("quality", "medium"),
    }


def call(job, outdir, attempt=1):
    payload = payload_for(job)
    body_file = outdir / ".payload.json"
    body_file.write_text(json.dumps(payload))
    proc = subprocess.run(
        [
            "curl", "-sS", "--http1.1", "--max-time", "300", "--retry", "0",
            "-H", "Content-Type: application/json",
            "-H", "@" + str(HERE / ".auth_header"),
            "-d", "@" + str(body_file),
            API,
        ],
        capture_output=True, text=True,
    )
    ok = proc.returncode == 0 and proc.stdout.strip()
    if ok:
        try:
            resp = json.loads(proc.stdout)
        except json.JSONDecodeError:
            ok = False
    if not ok or "error" in resp:
        detail = (proc.stdout or proc.stderr)[:400]
        if attempt < 3 and (not ok or resp.get("error", {}).get("code") in (429, 500, 502, 503)):
            time.sleep(10 * attempt)
            return call(job, outdir, attempt + 1)
        raise SystemExit(f"FAIL on {job['name']}: {detail}")
    return resp


def alpha_report(path):
    from PIL import Image

    im = Image.open(path)
    if im.mode != "RGBA":
        return f"mode={im.mode} NO-ALPHA"
    a = im.getchannel("A")
    lo, hi = a.getextrema()
    transparent_px = sum(1 for v in a.getdata() if v < 16)
    pct = 100.0 * transparent_px / (im.width * im.height)
    return f"mode=RGBA alpha_min={lo} alpha_max={hi} transparent={pct:.1f}%"


def register(job, cost, png, mp):
    """Upsert this generation into the manifest at `mp` (asset index)."""
    import datetime
    data = json.loads(mp.read_text()) if mp.exists() else {"assets": []}
    assets = [a for a in data.get("assets", []) if a.get("name") != job["name"]]
    assets.append({
        "name": job["name"],
        "kind": ("mockup" if job["name"].startswith("mock-") else
                 "probe" if job["name"].startswith("probe") else "asset"),
        "prompt": job["prompt"],
        "params": {k: job[k] for k in
                   ("background", "aspect_ratio", "resolution", "quality") if k in job},
        "model": MODEL + " via OpenRouter",
        "cost_usd": cost,
        "generated_at": datetime.date.today().isoformat(),
        "files": {"png": png.stat().st_size},
        "transparent": False,
    })
    data["assets"] = sorted(assets, key=lambda e: (e.get("kind", ""), e["name"]))
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("jobs", help="jobs.json: list of {name, prompt, ...}")
    ap.add_argument("--outdir", type=pathlib.Path, default=ASSETS,
                    help="where <name>.png lands (default: themes/assets/)")
    ap.add_argument("--manifest", type=pathlib.Path, default=ASSETS / "manifest.json",
                    help="asset index to upsert (default: themes/assets/manifest.json)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the payloads and output paths; send nothing")
    args = ap.parse_args()
    outdir = args.outdir
    jobs = json.loads(pathlib.Path(args.jobs).read_text())
    if args.dry_run:
        print(f"DRY RUN — nothing sent. outdir={outdir}  manifest={args.manifest}")
        for job in jobs:
            png = outdir / f"{job['name']}.png"
            state = "exists → would skip" if png.exists() else "would generate"
            print(f"\n[{job['name']}] {state} → {png}")
            print(json.dumps(payload_for(job), ensure_ascii=False, indent=2))
        print(f"\n{len(jobs)} job(s); credentials would be read from {HERE / '.auth_header'}")
        return
    outdir.mkdir(parents=True, exist_ok=True)
    total = 0.0
    for job in jobs:
        png = outdir / f"{job['name']}.png"
        if png.exists():
            print(f"{job['name']}: exists, skipped")
            continue
        t0 = time.time()
        resp = call(job, outdir)
        item = resp["data"][0]
        raw = base64.b64decode(item["b64_json"])
        png.write_bytes(raw)
        cost = resp.get("usage", {}).get("cost")
        total += cost or 0
        register(job, cost, png, args.manifest)
        print(
            f"{job['name']}: {len(raw)//1024}KB in {time.time()-t0:.0f}s "
            f"cost=${cost} media={item.get('media_type')} | {alpha_report(png)}"
        )
    print(f"TOTAL cost=${total:.4f}")


if __name__ == "__main__":
    main()
