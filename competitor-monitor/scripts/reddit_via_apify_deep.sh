#!/usr/bin/env bash
# Deep Reddit scrape via Apify's trudax/reddit-scraper actor (full version).
#
# Use this when the lite scraper isn't enough — typically when you need:
#   - Comment-text search (not just post search)
#   - Scoped search inside a specific community
#   - Date-range cutoffs beyond Reddit's coarse time filter
#   - Larger volume runs (the full actor has a 3-hour timeout + 2GB memory)
#
# For most battlecard runs, reddit_via_apify.sh (lite) is faster and cheaper.
#
# Usage:
#   reddit_via_apify_deep.sh <competitor> [time_range] [max_items] [community]
#
# Args:
#   competitor  — query string, e.g. "ParentSquare"
#   time_range  — hour|day|week|month|year|all (default: month)
#   max_items   — max total items (posts + optionally comments) (default: 100)
#   community   — optional subreddit name to scope (no "r/" prefix). e.g. "k12sysadmin"
#
# Env:
#   SEARCH_COMMENTS=true  — also search comment bodies (default: false, post-only)
#   SKIP_COMMENT_FETCH=true — skip downloading comment trees for matched posts (faster)
#
# Token is read from (in order):
#   1. $APIFY_TOKEN env var
#   2. ~/.apify_token (chmod 600)
#
# Output: raw JSON array on stdout.

set -euo pipefail

COMPETITOR="${1:?competitor name required}"
TIME_RANGE="${2:-month}"
MAX_ITEMS="${3:-100}"
COMMUNITY="${4:-}"

SEARCH_COMMENTS="${SEARCH_COMMENTS:-false}"
SKIP_COMMENT_FETCH="${SKIP_COMMENT_FETCH:-false}"

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

# Actor: trudax/reddit-scraper (ID: FgJtjDwJCLhRH9saM) — full version
ACTOR="trudax~reddit-scraper"

INPUT_JSON=$(python3 -c "
import json, sys, os
inp = {
    'searches': [sys.argv[1]],
    'searchPosts': True,
    'searchComments': os.environ.get('SEARCH_COMMENTS','false').lower() == 'true',
    'searchCommunities': False,
    'searchUsers': False,
    'sort': 'new',
    'time': sys.argv[2],
    'maxItems': int(sys.argv[3]),
    'maxPostCount': int(sys.argv[3]),
    'maxComments': 25,
    'skipComments': os.environ.get('SKIP_COMMENT_FETCH','false').lower() == 'true',
    'skipUserPosts': True,
    'skipCommunity': True,
    'includeNSFW': False,
    'proxy': {'useApifyProxy': True}
}
if sys.argv[4]:
    inp['searchCommunityName'] = sys.argv[4]
print(json.dumps(inp))
" "$COMPETITOR" "$TIME_RANGE" "$MAX_ITEMS" "$COMMUNITY")

# Synchronous run. The full actor runs longer; allow up to 600s.
RESPONSE=$(curl -sS \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  --data "$INPUT_JSON" \
  "https://api.apify.com/v2/acts/${ACTOR}/run-sync-get-dataset-items?timeout=600")

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
