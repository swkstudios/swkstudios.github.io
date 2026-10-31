"""Refresh a stats JSON file from the public UniFi Fabric MCP Server project. No credentials needed.

Release values come from the GitHub Releases API. Tool counts come from docs/site-stats.json
inside the LATEST RELEASE TAG, so every number on the page describes the same released version.
If that tag has no stats file yet, nothing except the year changes (the page stays a consistent snapshot).
The copyright year is always set from the current UTC date.

  python3 -I fetch_stats.py --stats content/stats.json
Optional env GITHUB_TOKEN raises the API rate limit (read-only use).
"""
import argparse, datetime, json, os, pathlib, sys, urllib.error, urllib.request

REPO = "swkstudios/unifi-fabric-mcp-server"
ap = argparse.ArgumentParser()
ap.add_argument("--stats", required=True)
args = ap.parse_args()
path = pathlib.Path(args.stats)
cur = json.loads(path.read_text())
new = dict(cur)
new["year"] = str(datetime.datetime.now(datetime.timezone.utc).year)

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "swkstudios-site"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and url.startswith("https://api.github.com/"):
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def warn(msg):
    print(f"::warning::{msg}")

releases = [r for r in get(f"https://api.github.com/repos/{REPO}/releases?per_page=100") if not r["draft"] and not r["prerelease"]]
if not releases:
    sys.exit("no published releases found")
latest = max(releases, key=lambda r: r["published_at"])
tag = latest["tag_name"]
try:
    src = get(f"https://raw.githubusercontent.com/{REPO}/{tag}/docs/site-stats.json")
except urllib.error.HTTPError as e:
    if e.code != 404:
        raise
    src = None
    if tag != cur.get("latest_version"):
        warn(f"{tag} has no docs/site-stats.json; keeping the {cur.get('latest_version')} snapshot")

if src is not None:
    tools, live, unit = (int(src[k]) for k in ("tools", "live_verified", "unit_tested"))
    if src.get("version") != tag:
        sys.exit(f"docs/site-stats.json version {src.get('version')!r} does not match tag {tag!r}")
    if tools <= 0 or live < 0 or unit < 0 or live + unit != tools:
        sys.exit(f"inconsistent counts in {tag}: tools={tools} live={live} unit={unit}")
    published = datetime.datetime.fromisoformat(latest["published_at"].replace("Z", "+00:00"))
    new.update(tools=str(tools), live_verified=str(live), unit_tested=str(unit),
               releases=str(len(releases)), latest_version=tag,
               latest_date=published.strftime("%B %Y"))

changed = {k: (cur.get(k), v) for k, v in new.items() if cur.get(k) != v}
print("changes:", changed or "none")
if changed:
    path.write_text(json.dumps(new, indent=2) + "\n")
