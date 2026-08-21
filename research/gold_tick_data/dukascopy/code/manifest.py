"""Turn the hour-level checkpoint into the per-day and per-hour manifests.

checkpoint.jsonl is the resume unit (one line per hour, appended as it lands).
manifest_by_hour.csv is that file as a table; manifest_by_day.csv rolls it up to
the per-date view. Both carry the SHA256 of each raw .bi5 as downloaded, so the
mirror can be re-verified byte-for-byte without re-downloading it.

Status vocabulary, per day:
  ok             every hour of the day answered, at least one carried ticks
  no_data        every hour answered, all of them empty (weekend / holiday)
  partial_error  at least one hour never resolved after all retries
"""
import csv, datetime as dt, json, os
from collections import defaultdict

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS = os.path.join(BASE, "logs")
UTC = dt.timezone.utc


def load():
    recs = {}
    with open(os.path.join(LOGS, "checkpoint.jsonl")) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            prev = recs.get(r["hour_utc"])
            if prev is None or prev["status"] not in ("ok", "empty"):
                recs[r["hour_utc"]] = r
            elif r["status"] in ("ok", "empty"):
                recs[r["hour_utc"]] = r
    return [recs[k] for k in sorted(recs)]


def main():
    recs = load()

    with open(os.path.join(LOGS, "manifest_by_hour.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["hour_utc", "status", "ticks", "bytes", "first_ms_in_hour",
                    "last_ms_in_hour", "retries", "errors", "sha256_raw_bi5", "source_url"])
        for r in recs:
            w.writerow([r["hour_utc"], r["status"], r.get("ticks", 0), r.get("bytes", 0),
                        r.get("first_ms"), r.get("last_ms"), r.get("retries", 0),
                        "; ".join(r.get("errors") or []), r.get("sha256") or "",
                        r.get("url", "")])

    days = defaultdict(list)
    for r in recs:
        days[dt.datetime.fromisoformat(r["hour_utc"]).date().isoformat()].append(r)

    with open(os.path.join(LOGS, "manifest_by_day.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date_utc", "status", "hours_requested", "hours_with_data",
                    "hours_empty", "hours_error", "ticks", "first_timestamp_utc",
                    "last_timestamp_utc", "retries", "errors", "raw_bytes",
                    "sha256_of_day_file_shas"])
        import hashlib
        for d in sorted(days):
            rs = sorted(days[d], key=lambda r: r["hour_utc"])
            n_ok = sum(r["status"] == "ok" for r in rs)
            n_empty = sum(r["status"] == "empty" for r in rs)
            n_err = sum(r["status"] not in ("ok", "empty") for r in rs)
            ticks = sum(r.get("ticks") or 0 for r in rs)
            first = last = ""
            with_data = [r for r in rs if r["status"] == "ok" and (r.get("ticks") or 0) > 0]
            if with_data:
                a, b = with_data[0], with_data[-1]
                ha = dt.datetime.fromisoformat(a["hour_utc"])
                hb = dt.datetime.fromisoformat(b["hour_utc"])
                first = (ha + dt.timedelta(milliseconds=a["first_ms"])).isoformat()
                last = (hb + dt.timedelta(milliseconds=b["last_ms"])).isoformat()
            status = "partial_error" if n_err else ("ok" if n_ok else "no_data")
            errs = "; ".join(f"{r['hour_utc'][11:13]}h:{'|'.join(r.get('errors') or [])}"
                             for r in rs if r["status"] not in ("ok", "empty"))
            roll = hashlib.sha256("".join(r.get("sha256") or "" for r in rs).encode()).hexdigest()
            w.writerow([d, status, len(rs), n_ok, n_empty, n_err, ticks, first, last,
                        sum(r.get("retries", 0) for r in rs), errs,
                        sum(r.get("bytes") or 0 for r in rs), roll])

    n_err = sum(r["status"] not in ("ok", "empty") for r in recs)
    print(f"hours in manifest : {len(recs)}")
    print(f"days in manifest  : {len(days)}")
    print(f"unresolved hours  : {n_err}")
    print(f"total ticks       : {sum(r.get('ticks') or 0 for r in recs):,}")
    print("-> logs/manifest_by_hour.csv, logs/manifest_by_day.csv")


if __name__ == "__main__":
    main()
