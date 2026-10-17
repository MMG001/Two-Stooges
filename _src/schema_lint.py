"""Property-level linter against the official schema.org vocabulary (domainIncludes + type hierarchy)."""
import json, re, sys
from pathlib import Path
from collections import defaultdict
voc = json.load(open(sys.argv[1]))
G = voc["@graph"]
def nm(x): return x.split(":")[-1] if isinstance(x, str) else x
parents = defaultdict(set); domains = defaultdict(set); types = set(); props = set()
def ids(v):
    if v is None: return []
    v = v if isinstance(v, list) else [v]
    return [nm(i["@id"]) for i in v if isinstance(i, dict)]
for n in G:
    t = n.get("@type"); t = t if isinstance(t, list) else [t]; i = nm(n["@id"])
    if "rdfs:Class" in t:
        types.add(i); parents[i] |= set(ids(n.get("rdfs:subClassOf")))
    if "rdf:Property" in t:
        props.add(i); domains[i] |= set(ids(n.get("schema:domainIncludes")))
def ancestors(t, seen=None):
    seen = seen or set()
    for p in parents.get(t, ()):
        if p not in seen: seen.add(p); ancestors(p, seen)
    return seen | {t}
ROOT = Path(sys.argv[2]); errs = []; checked = 0; tcount = defaultdict(int)
for f in sorted(ROOT.rglob("index.html")):
    if "_src" in f.parts: continue
    h = f.read_text()
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    where = "/" + str(f.parent.relative_to(ROOT)).replace(".", "") + ("/" if f.parent != ROOT else "")
    if len(blocks) != 1: errs.append(f"{where}: {len(blocks)} JSON-LD blocks (expected 1)")
    g = json.loads(blocks[0])
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', h).group(1)
    wp = [n for n in g["@graph"] if n.get("@id", "").endswith("#webpage")]
    if not wp or wp[0]["url"] != canon: errs.append(f"{where}: WebPage.url != canonical")
    def walk(n, ctx):
        global checked
        if isinstance(n, list):
            for x in n: walk(x, ctx)
            return
        if not isinstance(n, dict): return
        ty = n.get("@type"); tl = ty if isinstance(ty, list) else ([ty] if ty else [])
        for t in tl:
            tcount[t] += 1
            if t not in types: errs.append(f"{where}: unknown type {t}")
        anc = set().union(*[ancestors(t) for t in tl]) if tl else None
        for k, v in n.items():
            if k.startswith("@"): continue
            if k not in props: errs.append(f"{where}: unknown property {k} ({'/'.join(tl)})")
            elif anc is not None:
                checked += 1
                if not (domains[k] & anc): errs.append(f"{where}: '{k}' not defined for {'/'.join(tl)} (domains: {sorted(domains[k])[:6]})")
            walk(v, k)
    walk(g["@graph"], None)
print(f"pages linted, {checked} property placements checked")
print("types used:", dict(sorted(tcount.items())))
print("ERRORS:", len(errs)); [print(" -", e) for e in errs]
