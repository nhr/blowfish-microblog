"""Report CSS classes used in built HTML that no stylesheet defines.

Blowfish's compiled Tailwind CSS only contains the classes Blowfish's own
templates use, so a utility class that looks right can silently do nothing.

Usage: python3 dev/classcheck.py static/css/main.css,static/css/custom.css PUBLIC_DIR
"""
import collections
import glob
import re
import sys

css = "".join(open(f).read() for f in sys.argv[1].split(","))
defined = set()
for m in re.finditer(r'\.((?:\\.|[A-Za-z0-9_-])+)', css):
    defined.add(re.sub(r'\\(.)', r'\1', m.group(1)))

used = collections.defaultdict(set)
for f in glob.glob(sys.argv[2] + "/**/*.html", recursive=True):
    for m in re.finditer(r'class="([^"]*)"', open(f).read()):
        for c in m.group(1).split():
            used[c].add(f)

# Hooks for microformats, JavaScript or category names, not styling.
# fa-* classes sit inside Blowfish's icon SVGs.
# not-prose is Tailwind Typography's opt-out marker, matched by attribute.
hooks = re.compile(
    r'^(h-|p-|u-|dt-|e-|fa-|svg-inline--fa)'
    r'|^(group|peer|nozoom|not-prose|main-menu|logo|article-content'
    r'|article-link--simple|article-link--card|photo-tile|media-play|card-embed'
    r'|search|search-status|search-results|search-scope)$'
)
categories = set()
for f in glob.glob(sys.argv[2] + "/categories/*/", recursive=False):
    categories.add(f.rstrip("/").split("/")[-1])

missing = sorted(c for c in used if c not in defined and not hooks.match(c) and c not in categories)
for c in missing:
    print(f"{c:45s} e.g. {sorted(used[c])[0]}")
print(f"{len(used)} classes used, {len(missing)} missing")
sys.exit(1 if missing else 0)
