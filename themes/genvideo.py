#!/usr/bin/env python3
"""OpenRouter video generation for the portal theme (and anything else that
wants short clips). Same key as gen.py (themes/.auth_header), same manifest.
FALLBACK PATH: an agent with native video generation should use it directly
(16:9 h264 mp4 24 fps, dive 5-6 s / link 4 s, first/last-frame conditioning
for links; no key) — this script is for environments without one.

  python3 genvideo.py --models                     # live price/capability table
  python3 genvideo.py jobs.json --dry-run          # show what would be sent, no cost
  python3 genvideo.py jobs.json --outdir DIR --manifest PATH [--poll 10]

jobs.json = a list of jobs (or {"jobs": [...]}):
  {"name": "italy-s01-dive",                       # → <outdir>/<name>.mp4
   "prompt": "the camera dives slowly forward …",
   "model": "google/veo-3.1-lite",                 # default; see --models
   "duration": 6,                                  # must be in the model's supported list
   "resolution": "720p", "aspect_ratio": "16:9",
   "audio": false,                                 # generate_audio (costs more when true)
   "first_frame": "italy-rome-w.png",              # local file → data: URI, or an https URL
   "last_frame":  "italy-florence-w.png",          # optional (frame-chained links)
   "seed": 913001}                                 # optional

Flow: POST /api/v1/videos → {id, polling_url} → poll GET until completed →
download unsigned_urls[0] → <name>.mp4; usage.cost goes into the manifest.
Existing <name>.mp4 is skipped (delete to regenerate). Never prints the key.

Cost sense (2026-08-15, per model endpoint): veo-3.1-lite 720p no-audio $0.03/s,
kling-v3.0-std $0.084/s, wan-2.7 $0.10/s, hailuo-3 (2K) $0.13/s. A ten-world
portal chain (10×6s + 9×4s) is ≈$3 on veo-3.1-lite. Our own regression tests
still use the local 5090 (free); this script is the "one key for anyone" path.
"""
import argparse
import base64
import json
import mimetypes
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent
API = "https://openrouter.ai/api/v1/videos"
AUTH = HERE / ".auth_header"
DEFAULT_MODEL = "google/veo-3.1-lite"


def curl_json(url, body=None, out=None, timeout=120):
    cmd = ["curl", "-sS", "--http1.1", "--max-time", str(timeout), "-H", "@" + str(AUTH)]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", "@-"]
    if out:
        cmd += ["-o", str(out)]
    cmd.append(url)
    p = subprocess.run(cmd, input=(json.dumps(body) if body is not None else None),
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"curl failed: {p.stderr.strip()[:300]}")
    if out:
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"non-JSON reply: {p.stdout[:300]}")


def frame_entry(path_or_url, frame_type, base):
    s = str(path_or_url)
    if s.startswith(("http://", "https://", "data:")):
        url = s
    else:
        p = (base / s) if not pathlib.Path(s).is_absolute() else pathlib.Path(s)
        if not p.exists():
            raise FileNotFoundError(f"{frame_type}: {p} not found")
        mime = mimetypes.guess_type(p.name)[0] or "image/png"
        url = f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    return {"type": "image_url", "image_url": {"url": url}, "frame_type": frame_type}


def build_payload(job, base):
    body = {
        "model": job.get("model", DEFAULT_MODEL),
        "prompt": job["prompt"],
        "duration": int(job.get("duration", 6)),
        "resolution": job.get("resolution", "720p"),
        "aspect_ratio": job.get("aspect_ratio", "16:9"),
        "generate_audio": bool(job.get("audio", False)),
    }
    if job.get("seed") is not None:
        body["seed"] = int(job["seed"])
    frames = []
    if job.get("first_frame"):
        frames.append(frame_entry(job["first_frame"], "first_frame", base))
    if job.get("last_frame"):
        frames.append(frame_entry(job["last_frame"], "last_frame", base))
    if frames:
        body["frame_images"] = frames
    return body


def register(manifest_path, job, body, cost, out_file, job_id):
    mp = pathlib.Path(manifest_path)
    m = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {"assets": []}
    assets = m["assets"] if isinstance(m, dict) else m
    entry = {
        "name": job["name"], "kind": "video", "prompt": job["prompt"],
        "params": {k: body[k] for k in ("model", "duration", "resolution",
                                        "aspect_ratio", "generate_audio") if k in body},
        "frames": {k: str(job[k]) for k in ("first_frame", "last_frame") if job.get(k)},
        "model": body["model"] + " via OpenRouter /videos",
        "cost_usd": cost, "generated_at": time.strftime("%Y-%m-%d"),
        "job_id": job_id,
        "files": {"mp4": out_file.stat().st_size if out_file.exists() else None},
    }
    assets[:] = [a for a in assets if a.get("name") != job["name"]] + [entry]
    assets.sort(key=lambda a: a.get("name", ""))
    mp.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def list_models():
    d = curl_json(API + "/models")
    rows = d.get("data", d)
    print(f"{'model':32} {'frames':22} {'durations':22} {'res':18} {'audio':6} pricing")
    for m in rows:
        sk = m.get("pricing_skus") or {}
        price = ", ".join(f"{k}={v}" for k, v in list(sk.items())[:3])
        print(f"{m['id']:32} {','.join(m.get('supported_frame_images') or []):22} "
              f"{str(m.get('supported_durations'))[:22]:22} "
              f"{','.join(m.get('supported_resolutions') or []):18} "
              f"{str(m.get('generate_audio')):6} {price}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs", nargs="?")
    ap.add_argument("--outdir", default=None, help="where the mp4s go (default: jobs file dir)")
    ap.add_argument("--manifest", default=None, help="manifest to upsert (default: <outdir>/manifest.json)")
    ap.add_argument("--poll", type=float, default=10, help="seconds between status polls")
    ap.add_argument("--max-wait", type=float, default=900, help="give up after N seconds per job")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--models", action="store_true", help="list video models with prices and exit")
    a = ap.parse_args()
    if a.models:
        list_models(); return
    if not a.jobs:
        ap.error("jobs.json required (or --models)")
    if not AUTH.exists() and not a.dry_run:
        sys.exit(f"missing {AUTH} (Authorization header file) — see themes/README.md")
    jobs_path = pathlib.Path(a.jobs)
    spec = json.loads(jobs_path.read_text(encoding="utf-8"))
    jobs = spec["jobs"] if isinstance(spec, dict) else spec
    outdir = pathlib.Path(a.outdir) if a.outdir else jobs_path.parent
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = pathlib.Path(a.manifest) if a.manifest else outdir / "manifest.json"
    total = 0.0
    for job in jobs:
        out = outdir / f"{job['name']}.mp4"
        if out.exists():
            print(f"[{job['name']}] exists → skip ({out})"); continue
        body = build_payload(job, jobs_path.parent)
        shown = dict(body)
        if "frame_images" in shown:
            shown["frame_images"] = [{**f, "image_url": {"url": f["image_url"]["url"][:40] + "…"}}
                                     for f in body["frame_images"]]
        if a.dry_run:
            print(f"[{job['name']}] would POST {API} → {out}\n  {json.dumps(shown, ensure_ascii=False)}")
            continue
        t0 = time.time()
        r = curl_json(API, body)
        jid, purl = r.get("id"), r.get("polling_url")
        if not jid:
            print(f"[{job['name']}] submit failed: {json.dumps(r)[:400]}"); continue
        print(f"[{job['name']}] submitted id={jid} status={r.get('status')}")
        status, res = r.get("status"), r
        while status not in ("completed", "failed") and time.time() - t0 < a.max_wait:
            time.sleep(a.poll)
            res = curl_json(purl or f"{API}/{jid}")
            status = res.get("status")
            print(f"  … {status} ({time.time() - t0:.0f}s)")
        if status != "completed":
            print(f"[{job['name']}] {status}: {json.dumps(res)[:400]}"); continue
        urls = res.get("unsigned_urls") or []
        if not urls:
            print(f"[{job['name']}] completed but no unsigned_urls: {json.dumps(res)[:400]}"); continue
        curl_json(urls[0], out=out, timeout=600)
        cost = (res.get("usage") or {}).get("cost")
        total += cost or 0
        register(manifest, job, body, cost, out, jid)
        print(f"[{job['name']}] ✓ {out.name} {out.stat().st_size // 1024}KB  cost=${cost}  {time.time() - t0:.0f}s")
    if not a.dry_run:
        print(f"done — total cost ${total:.3f}; manifest {manifest}")


if __name__ == "__main__":
    main()
