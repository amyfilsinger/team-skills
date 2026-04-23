#!/usr/bin/env python3
"""
Gong fetcher for the schoolwide-call-review skill.

Pulls calls for a team in a date window and writes raw Gong JSON to disk for
downstream filtering and analysis. Uses credentials from ~/.gong/credentials.

Usage:
    python gong_fetch.py \\
        --owner-email dave.herron@classdojo.com \\
        --team direct-reports \\
        --days 14 \\
        --out /tmp/schoolwide-calls

Outputs:
    <out>/users.json         — team member lookup
    <out>/calls.json         — call metadata + topics/trackers
    <out>/transcripts/<id>.json  — one file per transcript

The script separates fetch from analysis so the LLM can work on the saved
files, and so re-runs don't re-hit the API if results already exist.
"""
import argparse, base64, json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

GONG_BASE = "https://api.gong.io"

# Named team shorthands resolved in resolve_team() below.
# "schoolwide-reps" is the default — the reps on David's team who actually run
# schoolwide / district-partnership conversations. Edit this list to add/remove
# reps; SKILL.md points here as the source of truth.
TEAM_SHORTHANDS = {
    "schoolwide-reps": [
        "shanieka.myles@classdojo.com",
        "natasha.fisher@classdojo.com",
        "sarah.zients@classdojo.com",
        "nicole.kindos@classdojo.com",
        "brianna.casas@classdojo.com",
    ],
}


def load_creds(path="~/.gong/credentials"):
    p = Path(os.path.expanduser(path))
    if not p.exists():
        sys.exit(f"ERROR: {p} not found. Create it with GONG_ACCESS_KEY and GONG_ACCESS_KEY_SECRET.")
    creds = {}
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        creds[k.strip()] = v.strip().strip('"').strip("'")
    key = creds.get("GONG_ACCESS_KEY")
    sec = creds.get("GONG_ACCESS_KEY_SECRET")
    if not key or not sec:
        sys.exit(f"ERROR: GONG_ACCESS_KEY or GONG_ACCESS_KEY_SECRET missing in {p}")
    return key, sec


def auth_header(key, sec):
    return "Basic " + base64.b64encode(f"{key}:{sec}".encode()).decode()


def _request(method, path, auth, body=None, retries=3):
    url = GONG_BASE + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": auth}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            msg = e.read().decode(errors="replace")[:500]
            sys.exit(f"ERROR: {method} {path} -> HTTP {e.code}: {msg}")
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            sys.exit(f"ERROR: {method} {path}: {e}")


def list_all_users(auth):
    """Paginate all users. Returns list of user dicts."""
    users = []
    cursor = None
    while True:
        path = "/v2/users?limit=100"
        if cursor:
            path += f"&cursor={cursor}"
        d = _request("GET", path, auth)
        users.extend(d.get("users", []))
        cursor = d.get("records", {}).get("cursor")
        if not cursor:
            break
    return users


def resolve_team(users, owner_email, team_spec):
    """Resolve a team spec against the user list. Returns (owner_user, team_users).

    team_spec can be:
      - a named shorthand in TEAM_SHORTHANDS (default: 'schoolwide-reps')
      - 'direct-reports': everyone whose managerId == owner's id (active only)
      - 'me': just the owner
      - 'email1,email2,...': explicit list of email addresses
    """
    by_email = {(u.get("emailAddress") or "").lower(): u for u in users}
    owner = by_email.get(owner_email.lower())
    if not owner:
        sys.exit(f"ERROR: no Gong user found with email {owner_email}")

    if team_spec == "me":
        return owner, [owner]

    if team_spec == "direct-reports":
        team = [u for u in users if u.get("managerId") == owner.get("id") and u.get("active")]
        return owner, team

    # Named shorthand or comma-separated emails
    if team_spec in TEAM_SHORTHANDS:
        emails = TEAM_SHORTHANDS[team_spec]
    else:
        emails = [e.strip() for e in team_spec.split(",") if e.strip()]

    team, missing = [], []
    for em in [e.lower() for e in emails]:
        u = by_email.get(em)
        if u:
            team.append(u)
        else:
            missing.append(em)
    if missing:
        print(f"WARN: could not resolve emails: {missing}", file=sys.stderr)
    return owner, team


def list_calls(auth, user_ids, start_dt, end_dt):
    """Paginate through calls/extensive with parties/content/trackers exposed."""
    body = {
        "filter": {
            "fromDateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toDateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "primaryUserIds": user_ids,
        },
        "contentSelector": {
            "exposedFields": {
                "parties": True,
                "content": {"topics": True, "trackers": True, "brief": True, "outline": True, "highlights": True, "callOutcome": True, "keyPoints": True},
                "interaction": {"speakers": True, "questions": True},
            }
        },
    }
    calls = []
    cursor = None
    while True:
        payload = dict(body)
        if cursor:
            payload["cursor"] = cursor
        d = _request("POST", "/v2/calls/extensive", auth, body=payload)
        calls.extend(d.get("calls", []))
        cursor = d.get("records", {}).get("cursor")
        if not cursor:
            break
    return calls


def get_transcripts(auth, call_ids):
    """Fetch transcripts for a set of call IDs. Gong supports batching up to ~100/call."""
    if not call_ids:
        return []
    body = {"filter": {"callIds": list(call_ids)}}
    d = _request("POST", "/v2/calls/transcript", auth, body=body)
    return d.get("callTranscripts", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner-email", required=True)
    ap.add_argument("--team", default="schoolwide-reps",
                    help="Named shorthand (default 'schoolwide-reps'; also 'direct-reports', 'me') "
                         "or a comma-separated email list")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--skip-transcripts", action="store_true",
                    help="Only fetch call metadata; skip transcripts (for triage)")
    ap.add_argument("--transcript-call-ids", default=None,
                    help="Comma-separated call IDs to fetch transcripts for. "
                         "If set, skips listing and only pulls these.")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "transcripts").mkdir(exist_ok=True)

    key, sec = load_creds()
    auth = auth_header(key, sec)

    if args.transcript_call_ids:
        ids = [x.strip() for x in args.transcript_call_ids.split(",") if x.strip()]
        print(f"Fetching {len(ids)} transcript(s) only…", file=sys.stderr)
        transcripts = get_transcripts(auth, ids)
        for t in transcripts:
            cid = t.get("callId")
            (out / "transcripts" / f"{cid}.json").write_text(json.dumps(t, indent=2))
        print(json.dumps({"transcripts_written": len(transcripts)}))
        return

    print("Listing users…", file=sys.stderr)
    users = list_all_users(auth)
    (out / "users.json").write_text(json.dumps(users, indent=2))

    owner, team = resolve_team(users, args.owner_email, args.team)
    user_ids = [u["id"] for u in team]
    print(f"Owner: {owner.get('emailAddress')} ({owner.get('id')})", file=sys.stderr)
    print(f"Team ({args.team}): {len(team)} people", file=sys.stderr)

    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=args.days)
    print(f"Window: {start_dt:%Y-%m-%d} → {end_dt:%Y-%m-%d}", file=sys.stderr)

    print("Listing calls…", file=sys.stderr)
    calls = list_calls(auth, user_ids, start_dt, end_dt)
    summary = {
        "owner": {"id": owner.get("id"), "email": owner.get("emailAddress")},
        "team_spec": args.team,
        "team": [{"id": u.get("id"), "email": u.get("emailAddress"),
                  "name": f"{u.get('firstName','')} {u.get('lastName','')}".strip()} for u in team],
        "window": {"from": start_dt.isoformat(), "to": end_dt.isoformat(), "days": args.days},
        "total_calls": len(calls),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    (out / "calls.json").write_text(json.dumps(calls, indent=2))
    print(f"Wrote {len(calls)} calls to {out}/calls.json", file=sys.stderr)

    if args.skip_transcripts:
        print(json.dumps(summary, indent=2))
        return

    call_ids = [c["metaData"]["id"] for c in calls if c.get("metaData", {}).get("id")]
    # Gong caps transcript batch size; chunk conservatively
    BATCH = 50
    total_written = 0
    for i in range(0, len(call_ids), BATCH):
        batch = call_ids[i:i + BATCH]
        print(f"Transcripts batch {i//BATCH + 1}: {len(batch)} calls", file=sys.stderr)
        transcripts = get_transcripts(auth, batch)
        for t in transcripts:
            cid = t.get("callId")
            (out / "transcripts" / f"{cid}.json").write_text(json.dumps(t, indent=2))
            total_written += 1
    summary["transcripts_written"] = total_written
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
