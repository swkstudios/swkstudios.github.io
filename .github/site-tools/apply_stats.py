"""Write values from a stats JSON file into every data-stat element of the site's HTML pages.

One place to update the numbers. Used two ways:
  - in this repo:   python3 -I scripts/apply_stats.py [--check]
  - at Pages build: python3 -I apply_stats.py --stats stats.json --root _site
--check exits 1 if a page does not match the stats file (CI guard); without it, pages are rewritten.
"""
import argparse, json, pathlib, re, sys

here = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--stats", default=str(here / "content/stats.json"))
ap.add_argument("--root", default=str(here / "site"))
ap.add_argument("--check", action="store_true")
args = ap.parse_args()

stats = {k: str(v) for k, v in json.loads(pathlib.Path(args.stats).read_text()).items() if not k.startswith("_")}
pat = re.compile(r'(<(\w+)\b[^>]*\bdata-stat="([a-z_]+)"[^>]*>)([^<]*)(</\2>)')
bad = 0
for page in sorted(pathlib.Path(args.root).glob("*.html")):
    text = page.read_text(encoding="utf-8")
    def sub(m):
        global bad
        key = m.group(3)
        if key not in stats:
            print(f"{page.name}: unknown data-stat {key!r}"); bad += 1; return m.group(0)
        if args.check and m.group(4) != stats[key]:
            print(f"{page.name}: {key} is {m.group(4)!r}, stats file says {stats[key]!r}"); bad += 1
        return m.group(1) + stats[key] + m.group(5)
    new = pat.sub(sub, text)
    if not args.check and new != text:
        page.write_text(new, encoding="utf-8"); print(f"updated {page.name}")
sys.exit(1 if bad else 0)
