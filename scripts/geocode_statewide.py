#!/usr/bin/env python3
"""Bulk-geocode Slot Map's statewide Illinois establishments with the U.S. Census geocoder.

The script is deliberately conservative:
- Sends only records that have an official street address and no coordinates.
- Uses the Census batch geocoder in chunks.
- Accepts only Match + Exact results with coordinates inside Illinois' bounding box.
- Keeps all unmatched/ambiguous rows in the enrichment queue.
- Caches raw results so repeated runs do not re-request completed IDs.

No API key is required.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "statewide-master.json"
QUEUE = ROOT / "enrichment-queue.csv"
CACHE = ROOT / "geocoding-cache.json"
RESULTS = ROOT / "geocoding-results.csv"
ESTABLISHMENTS = ROOT / "establishments.js"

CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
BENCHMARK = "Public_AR_Current"

# Broad Illinois bounds, intentionally slightly padded.
IL_BOUNDS = (36.80, 42.55, -91.60, -87.35)  # south, north, west, east


def clean(v):
    return str(v or "").strip()


def in_illinois(lat: float, lon: float) -> bool:
    s, n, w, e = IL_BOUNDS
    return s <= lat <= n and w <= lon <= e


def parse_coord(value: str):
    # Census returns "lon,lat".
    parts = [p.strip() for p in clean(value).split(",")]
    if len(parts) != 2:
        return None
    try:
        lon, lat = map(float, parts)
    except ValueError:
        return None
    if not (math.isfinite(lat) and math.isfinite(lon)):
        return None
    return lat, lon


def parse_zip_from_matched_address(value: str) -> str:
    m = re.search(r"\b(\d{5})(?:-\d{4})?\s*$", clean(value))
    return m.group(1) if m else ""


def multipart_body(csv_bytes: bytes, boundary: str):
    crlf = b"\r\n"
    out = bytearray()
    def add(s: bytes): out.extend(s)
    add(f"--{boundary}".encode()); add(crlf)
    add(b'Content-Disposition: form-data; name="benchmark"'); add(crlf); add(crlf)
    add(BENCHMARK.encode()); add(crlf)
    add(f"--{boundary}".encode()); add(crlf)
    add(b'Content-Disposition: form-data; name="addressFile"; filename="addresses.csv"'); add(crlf)
    add(b"Content-Type: text/csv"); add(crlf); add(crlf)
    add(csv_bytes); add(crlf)
    add(f"--{boundary}--".encode()); add(crlf)
    return bytes(out)


def census_batch(rows, timeout=120, retries=4):
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\n")
    for r in rows:
        w.writerow([r["license"], r["address"], r["city"], "IL", r["zip"]])
    payload = buf.getvalue().encode("utf-8")
    boundary = "----SlotMapCensusBoundary7MA4YWxkTrZu0gW"
    body = multipart_body(payload, boundary)

    last = None
    for attempt in range(retries):
        req = urllib.request.Request(
            CENSUS_URL,
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "SlotMap/12.3"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read().decode("utf-8-sig", errors="replace")
            return list(csv.reader(io.StringIO(data)))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last = exc
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Census batch request failed after {retries} attempts: {last}")


def load_cache():
    if not CACHE.exists():
        return {}
    data = json.loads(CACHE.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def save_cache(cache):
    CACHE.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def result_from_census(row, source):
    # Typical output columns:
    # id, input address, match status, match type, matched address, coordinates, tiger id, side
    padded = list(row) + [""] * max(0, 8 - len(row))
    lic, input_addr, status, match_type, matched_addr, coord = padded[:6]
    parsed = parse_coord(coord)
    out = {
        "license": clean(lic),
        "input_address": clean(input_addr),
        "status": clean(status),
        "match_type": clean(match_type),
        "matched_address": clean(matched_addr),
        "lat": None,
        "lon": None,
        "accepted": False,
        "reason": "",
        "source": source,
    }
    if clean(status).casefold() != "match":
        out["reason"] = "census_no_match"
        return out
    if clean(match_type).casefold() != "exact":
        out["reason"] = "census_non_exact"
        return out
    if not parsed:
        out["reason"] = "missing_coordinates"
        return out
    lat, lon = parsed
    if not in_illinois(lat, lon):
        out["reason"] = "outside_illinois"
        return out
    out.update(lat=lat, lon=lon, accepted=True, reason="exact_illinois_match")
    return out


def write_results(cache):
    fields = ["license", "status", "match_type", "accepted", "reason", "lat", "lon", "matched_address", "input_address", "source"]
    with RESULTS.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for lic in sorted(cache):
            r = cache[lic]
            w.writerow({k: r.get(k, "") for k in fields})


def update_master(master, cache):
    updated = 0
    rejected_zip = 0
    for r in master["establishments"]:
        if r.get("lat") not in (None, "") and r.get("lon") not in (None, ""):
            continue
        c = cache.get(clean(r.get("license")))
        if not c or not c.get("accepted"):
            continue
        # ZIP check is a second guardrail when Census returns one.
        expected_zip = clean(r.get("zip"))[:5]
        matched_zip = parse_zip_from_matched_address(c.get("matched_address", ""))
        if expected_zip and matched_zip and expected_zip != matched_zip:
            c["accepted"] = False
            c["reason"] = "zip_mismatch"
            rejected_zip += 1
            continue
        r["lat"] = round(float(c["lat"]), 7)
        r["lon"] = round(float(c["lon"]), 7)
        r["mapping_status"] = "mapped_census_exact"
        r["coordinate_source"] = "us_census_batch_geocoder"
        updated += 1
    return updated, rejected_zip


def rebuild_queue(master):
    fields = ["license", "name", "municipality", "county", "county_source", "address", "city", "zip", "lat", "lon", "status"]
    rows = []
    for r in master["establishments"]:
        if r.get("record_status") != "current_igb":
            continue
        if r.get("lat") not in (None, "") and r.get("lon") not in (None, ""):
            continue
        has_addr = bool(clean(r.get("address")))
        rows.append({
            "license": clean(r.get("license")), "name": clean(r.get("name")), "municipality": clean(r.get("municipality")),
            "county": clean(r.get("county")), "county_source": clean(r.get("county_source")), "address": clean(r.get("address")),
            "city": clean(r.get("city")), "zip": clean(r.get("zip")), "lat": "", "lon": "",
            "status": "needs_coordinates" if has_addr else "needs_address_and_coordinates",
        })
    with QUEUE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    return len(rows)


def rebuild_live_dataset(master):
    # Keep the exact shape the app already expects, but now include any newly geocoded master records.
    live=[]
    for r in master["establishments"]:
        if r.get("lat") in (None, "") or r.get("lon") in (None, ""):
            continue
        d={k:r.get(k) for k in ("county","id","name","address","city","state","zip","license","type","lat","lon","vgts","played","won","nti","payback")}
        if not d.get("id"):
            d["id"] = f"IL-{clean(r.get('license'))}"
        terms=[d.get(k) for k in ("name","address","city","state","zip","license","county")]
        d["_search"]=" ".join(clean(x).lower() for x in terms if clean(x))
        live.append(d)
    ESTABLISHMENTS.write_text("/* Slot Map establishment data. Generated from statewide-master.json; verified coordinates only. */\nconst R=" + json.dumps(live, separators=(",",":"), ensure_ascii=False) + ";\n", encoding="utf-8")
    return len(live)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=500, help="addresses per Census request")
    ap.add_argument("--limit", type=int, default=0, help="process at most N uncached addresses (0 = all)")
    ap.add_argument("--dry-run", action="store_true", help="prepare/validate only; do not make network requests")
    args=ap.parse_args()

    master=json.loads(MASTER.read_text(encoding="utf-8"))
    cache=load_cache()
    pending=[]
    for r in master["establishments"]:
        if r.get("record_status") != "current_igb": continue
        if r.get("lat") not in (None, "") and r.get("lon") not in (None, ""): continue
        lic=clean(r.get("license"))
        if not lic or lic in cache: continue
        if not clean(r.get("address")) or not clean(r.get("city")) or not clean(r.get("zip")): continue
        pending.append({"license":lic,"address":clean(r.get("address")),"city":clean(r.get("city")),"zip":clean(r.get("zip"))[:5]})
    if args.limit:
        pending=pending[:args.limit]

    print(f"Eligible uncached addresses: {len(pending)}")
    if args.dry_run:
        print("Dry run complete; no network requests made.")
        return

    for start in range(0,len(pending),args.batch_size):
        batch=pending[start:start+args.batch_size]
        rows=census_batch(batch)
        returned=set()
        for row in rows:
            if not row: continue
            res=result_from_census(row,"us_census_batch_geocoder")
            lic=res["license"]
            if not lic: continue
            cache[lic]=res; returned.add(lic)
        for item in batch:
            if item["license"] not in returned:
                cache[item["license"]]={"license":item["license"],"status":"","match_type":"","accepted":False,"reason":"no_row_returned","lat":None,"lon":None,"matched_address":"","input_address":item["address"],"source":"us_census_batch_geocoder"}
        save_cache(cache)
        print(f"Processed {min(start+len(batch),len(pending))}/{len(pending)}")

    updated,rejected_zip=update_master(master,cache)
    master.setdefault("counts",{})["census_geocoded_this_build"]=updated
    master["counts"]["current_with_coordinates"]=sum(1 for r in master["establishments"] if r.get("record_status")=="current_igb" and r.get("lat") not in (None,"") and r.get("lon") not in (None,""))
    MASTER.write_text(json.dumps(master,indent=2,ensure_ascii=False),encoding="utf-8")
    save_cache(cache)
    write_results(cache)
    queue_count=rebuild_queue(master)
    live_count=rebuild_live_dataset(master)
    accepted=sum(1 for v in cache.values() if v.get("accepted"))
    print(f"Accepted exact Illinois matches in cache: {accepted}")
    print(f"Newly applied coordinates: {updated}; ZIP mismatches rejected: {rejected_zip}")
    print(f"Live mapped dataset: {live_count}; remaining enrichment queue: {queue_count}")

if __name__ == "__main__":
    main()
