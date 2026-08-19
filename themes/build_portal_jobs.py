#!/usr/bin/env python3
"""Build ComfyUI POST bodies (NDJSON, one per line) for portal (穿越版) clips.

The portal page (render_portal.py) plays a chain of N "dive" clips (one per
floating world) joined by N-1 "link" clips whose first/last frames are the
real edge frames of the neighbouring dives, so every seam is a hard cut
between pixel-identical frames. This script only WRITES THE JOBS; the
worlds themselves come from a spec file, one per trip:

  worlds.json = [                                    # reel order, any length ≥ 1
    {"still":    "portal-nyc-w2.png",                # 1344x768 first frame, already in ComfyUI's input\\
     "scene":    "a cute miniature … island at dusk …",   # what the still shows
     "motion":   "the camera dives slowly forward and down …",
     "ambience": "soft evening city traffic, distant horns"},  # audio line; link i borrows world i+1's
    …
  ]
  (The author's US regression spec has 10 worlds; a test trip used 5. Any length works.
   That 19-clip US chain is the style reference / regression fixture and is a release
   asset, NOT in the git tree — restore it into themes/assets/portal/ with the one-line
   curl+unzip in themes/assets/portal/README.md. The shipped portal case is Morocco.)

Usage:
  build_portal_jobs.py --spec worlds.json dives 1,2,3      > dives.ndjson
  build_portal_jobs.py --spec worlds.json dives 1..10      > dives.ndjson   (ranges ok)
  build_portal_jobs.py --spec worlds.json links 1,2        > links.ndjson   (after edge frames exist)
  options: --tpl PATH   ComfyUI API-format workflow JSON to clone (REQUIRED — export your
                        image-to-video workflow from ComfyUI with "Save (API format)"; the
                        author uses a MiniMax-H3 first/last-frame workflow, see WORKFLOW NODES)
           --stem s     file stem → s01-dive-q20 / s01-s02-link-q20 / s01-q20-last.png (default "s")
  Ids are 1-based world numbers: dives 1..N, links 1..N-1 (link i joins world i → i+1).
  Ids outside the spec are an error, not a KeyError.
  Sampler steps: STEPS = 10 (settled by eye: 20/10/8 indistinguishable, 10 ≈ 2:48 per
  5 s clip on an RTX 5090) — the
  "-q20" in the output names is a legacy tag and does not change with STEPS.

Pipeline (each POST body goes to  POST http://<your-comfyui-host>:8188/prompt):
  1. dives   — first_frame = the world's still, no last frame, DIVE_LEN frames.
  2. edge frames — pull each finished dive back and cut its REAL edge frames
     (do not guess with -sseof; frame indices are exact):
       ffmpeg -i s01-dive.mp4 -vf "select='eq(n,123)'" -vframes 1 s01-q20-last.png    # last of DIVE_LEN=124
       ffmpeg -i s02-dive.mp4 -vf "select='eq(n,0)'"   -vframes 1 s02-q20-first.png
     scp both into ComfyUI's input\\ (names must match what `links` writes below).
  3. links   — first_frame = s{i}-q20-last.png, last_frame = s{i+1}-q20-first.png, LINK_LEN frames.

ComfyUI OUTPUT NAMES: `filename_prefix` is a prefix, not the file name — the
saver appends a counter, so  video/s01-dive-q20  lands as
  ComfyUI/output/video/s01-dive-q20_00001_.mp4   (…_00002_ if you re-run it).
Rename while retrieving so art.json can list clean names:
  scp '<gpu-host>:…/ComfyUI/output/video/s01-dive-q20_00001_.mp4' portal/s01-dive.mp4
  scp '<gpu-host>:…/ComfyUI/output/video/s01-s02-link-q20_00001_.mp4' portal/s01-s02-link.mp4

WORKFLOW NODES (what job() patches in the template — edit these ids to match
your own exported workflow if they differ):
  "114" LoadImage  → inputs.image = first frame        "121" LoadImage → inputs.image = last frame
  "104" the MiniMax-H3 conditioning node → inputs.prompt/width/height/length (+ last_frame link)
  "9"   KSampler   → inputs.steps                      "15"  noise seed  → inputs.noise_seed
  "92"  video saver → inputs.filename_prefix
  The template is wrapped as {"prompt": {...nodes...}}; client_id is set by this script.

art.json (themes.portal.clips) then needs, per clip in reel order:
  "file"  the renamed clip under video_dir
  "dur"   ffprobe -v error -show_entries format=duration -of csv=p=0 portal/s01-dive.mp4
          → 5.167 (124f@24fps) / 3.750 (90f); 3 decimals is enough
  "off"   seconds skipped at the HEAD of the clip — 0 unless the first frame is bad;
          the page scrubs t = off + p·(dur − off − 0.03)
  "kind"  "dive" | "link";  "day" (dives only) = 1-based plan day whose overlay shows
"""
import argparse
import copy
import json
import sys

DEFAULT_TPL = None   # no bundled workflow: pass --tpl (see the docstring)

STEPS = 10      # sampler steps; 10 is the settled default (20/10/8
                # indistinguishable by eye, 10 ≈ 2:48 per 5 s clip). The "q20" in
                # the file names is a historical tag, not the step count.
W, H = 1344, 768
DIVE_LEN, LINK_LEN = 124, 90


def parse_ids(text):
    """'1,2,5' | '1..10' | '1-10' | mixes thereof → sorted unique ints."""
    ids = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        for sep in ("..", "-"):
            if sep in part:
                a, b = part.split(sep, 1)
                ids.update(range(int(a), int(b) + 1))
                break
        else:
            ids.add(int(part))
    return sorted(ids)


def job(tpl, prompt, first, last, length, seed, prefix):
    j = copy.deepcopy(tpl)
    p = j["prompt"]
    p["114"]["inputs"]["image"] = first
    if last is None:
        del p["121"]
        del p["104"]["inputs"]["last_frame"]
    else:
        p["121"]["inputs"]["image"] = last
    p["104"]["inputs"].update(prompt=prompt, width=W, height=H, length=length)
    p["9"]["inputs"]["steps"] = STEPS
    p["15"]["inputs"]["noise_seed"] = seed
    p["92"]["inputs"]["filename_prefix"] = prefix
    j["client_id"] = "mac-claude-q20"
    return json.dumps(j)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("kind", choices=("dives", "links"))
    ap.add_argument("ids", help="1-based world ids: '1,2,3' or '1..10'")
    ap.add_argument("--spec", required=True,
                    help="worlds.json — list of {still, scene, motion, ambience} in reel order")
    ap.add_argument("--tpl", default=DEFAULT_TPL,
                    help="ComfyUI API-format workflow JSON to clone (required)")
    ap.add_argument("--stem", default="s", help="file stem: s → s01-dive-q20 (default s)")
    args = ap.parse_args()

    worlds = json.load(open(args.spec))
    if not isinstance(worlds, list) or not worlds:
        sys.exit(f"{args.spec}: expected a non-empty JSON list of worlds")
    for k, w in enumerate(worlds, 1):
        missing = [f for f in ("still", "scene", "motion", "ambience") if not w.get(f)]
        if missing:
            sys.exit(f"{args.spec}: world {k} missing {missing}")
    n = len(worlds)
    if not args.tpl:
        sys.exit("--tpl PATH is required: export your ComfyUI image-to-video workflow with "
                 "\"Save (API format)\" and pass it here (see the docstring, WORKFLOW NODES).")
    tpl = json.load(open(args.tpl))
    st = args.stem
    ids = parse_ids(args.ids)
    hi = n if args.kind == "dives" else n - 1
    bad = [i for i in ids if not 1 <= i <= hi]
    if bad:
        sys.exit(f"{args.kind}: ids {bad} out of range 1..{hi} "
                 f"(spec has {n} world(s) → {n} dives, {n - 1} links)")

    for i in ids:
        if args.kind == "dives":
            w = worlds[i - 1]
            prompt = (f"The shot begins exactly on this image: {w['scene']}. "
                      f"{w['motion']}, gentle parallax, smooth continuous motion, no cuts."
                      f"\nAudio: {w['ambience']}")
            print(job(tpl, prompt, w["still"], None, DIVE_LEN, 913000 + i,
                      f"video/{st}{i:02d}-dive-q20"))
        else:
            # link i joins world i -> world i+1 (first frame = dive i real last
            # frame, last frame = dive i+1 real first frame); ambience of the
            # world we are arriving at
            amb = worlds[i]["ambience"]
            prompt = ("A seamless flying transition between two miniature floating "
                      "worlds. The shot begins exactly on image 1 and ends exactly "
                      "on image 2. The camera pulls up and away from the first "
                      "scene, rushes through soft glowing clouds, and glides down "
                      "toward the next floating island as it emerges from the sky. "
                      "Smooth continuous motion, no cuts."
                      f"\nAudio: a soft wind whoosh, muffled cloud rush, then {amb} fading in.")
            print(job(tpl, prompt, f"{st}{i:02d}-q20-last.png", f"{st}{i + 1:02d}-q20-first.png",
                      LINK_LEN, 924000 + i, f"video/{st}{i:02d}-{st}{i + 1:02d}-link-q20"))


if __name__ == "__main__":
    main()
