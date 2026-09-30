#!/usr/bin/env python3
"""Refresh src/data/spine.json: the last 12 months of GB grid carbon intensity, daily mean, from NESO.

Source: https://api.carbonintensity.org.uk (National Energy System Operator), licence CC BY 4.0.
The stats endpoint returns up to 30 days per call; we walk back a year in 30-day windows.
Run by .github/workflows/spine.yml daily, or by hand: python3 scripts/refresh_spine.py
"""
import json, sys, time, datetime as dt, urllib.request, pathlib

API = "https://api.carbonintensity.org.uk/intensity/stats/{a}/{b}/24"
OUT = pathlib.Path(__file__).resolve().parents[1] / "src/data/spine.json"

def fetch(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "julian-elliott.github.io spine refresh"}), timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            if i == tries - 1:
                raise
            time.sleep(2 ** i)

def main():
    today = dt.datetime.now(dt.timezone.utc).date()
    end = today  # the stats endpoint returns whole days up to but excluding `end`
    start = end - dt.timedelta(days=365)
    rows = {}
    a = start
    while a < end:
        b = min(a + dt.timedelta(days=30), end)
        data = fetch(API.format(a=f"{a.isoformat()}T00:00Z", b=f"{b.isoformat()}T00:00Z")).get("data", [])
        for p in data:
            d = p["from"][:10]
            v = p.get("intensity", {}).get("average")
            if v is not None:
                rows[d] = int(v)
        a = b
        time.sleep(0.3)
    series = [{"d": d, "v": rows[d]} for d in sorted(rows)]
    if len(series) < 300:
        print(f"only {len(series)} days fetched; keeping the existing file", file=sys.stderr)
        sys.exit(1)
    OUT.write_text(json.dumps(series, separators=(",", ":")))
    print(f"wrote {len(series)} days {series[0]['d']} → {series[-1]['d']} to {OUT}")

if __name__ == "__main__":
    main()
