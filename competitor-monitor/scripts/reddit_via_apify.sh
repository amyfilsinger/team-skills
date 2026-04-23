#!/usr/bin/env bash
# Fetch Reddit posts about a competitor via Apify's reddit-scraper-lite actor.
#
# Usage:
#   reddit_via_apify.sh <competitor> [time_range] [max_items]
#
# Args:
#   competitor  — query string, e.g. "ParentSquare"
#   time_range  — Reddit time filter: hour|day|week|month|year|all (default: month)
#   max_items   — max posts to fetch (default: 50)
#
# Token is read from (in order):
#   1. $APIFY_TOKEN env var
#   2. ~/.apify_token (chmod 600)
#
# Output: raw JSON array of posts on stdout. Exits non-zero if auth fails or no results.

set -euo pipefail

COMPETITOR="${1:?competitor name required}"
TIME_RANGE="${2:-month}"
MAX_ITEMS="${3:-50}"

# Resolve token
if [ -z "${APIFY_TOKEN:-}" ]; then
  if [ -r "$HOME/.apify_token" ]; then
    APIFY_TOKEN="$(tr -d '[:space:]' < "$HOME/.apify_token")"
  fi
fi

if [ -z "${APIFY_TOKEN:-}" ]; then
  echo "ERROR: APIFY_TOKEN not set and ~/.apify_token is empty." >&2
  echo "Set one via:  echo 'apify_api_XXXXX' > ~/.apify_token && chmod 600 ~/.apify_token" >&2
  exit 2
fi

# Actor: trudax/reddit-scraper-lite (ID: oAuCIx3ItNrs2okjQ)
ACTOR="trudax~reddit-scraper-lite"

# Build input JSON. searches[] drives Reddit's own search UI; safer than URL-based.
INPUT_JSON=$(python3 -c "
import json, sys
print(json.dumps({
    'searches': [sys.argv[1]],
    'sort': 'new',
    'time': sys.argv[2],
    'maxItems': int(sys.argv[3]),
    'maxPostCount': int(sys.argv[3]),
    'maxComments': 10,
    'skipComments': False,
    'proxy': {'useApifyProxy': True}
}))
" "$COMPETITOR" "$TIME_RANGE" "$MAX_ITEMS")

# Synchronous run — returns dataset items directly. Timeout 300s is typical for lite scraper.
RESPONSE=$(curl -sS \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  --data "$INPUT_JSON" \
  "https://api.apify.com/v2/acts/${ACTOR}/run-sync-get-dataset-items?timeout=300")

# Detect error response (Apify returns an object with 'error' key on failure)
echo "$RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if isinstance(data, dict) and 'error' in data:
    print('APIFY ERROR:', data['error'].get('message', data['error']), file=sys.stderr)
    sys.exit(3)
if not isinstance(data, list) or len(data) == 0:
    print('No results returned.', file=sys.stderr)
    sys.exit(4)
print(json.dumps(data, indent=2))
"
