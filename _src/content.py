"""Events and tournaments entered through the admin (/admin/, Decap CMS).

Each entry is one JSON file:
    _content/events/<slug>.json        general events (parties, special nights, promotions)
    _content/tournaments/<slug>.json   pool tournaments (one date, or weekly)

build.py calls load() after the image step, so uploaded JPEG/PNG flyers have already been
converted to WebP; load() then points the entry at the .webp (and rewrites the JSON so the
admin shows the same file).
"""
import datetime as dt
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "_content"
IMG = ROOT / "assets" / "img"
TZ = ZoneInfo("America/Chicago")
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "entry"


def prepare_uploads():
    """Run BEFORE images.optimize(): give uploaded flyers safe file names (no spaces/odd characters)."""
    d = IMG / "events"
    renames = {}
    for p in list(d.glob("*")):
        if p.suffix.lower() in (".jpg", ".jpeg", ".png") and not re.fullmatch(r"[a-z0-9-]+", p.stem):
            new = p.with_name(_slug(p.stem) + p.suffix.lower())
            i = 2
            while new.exists():
                new = p.with_name(f"{_slug(p.stem)}-{i}{p.suffix.lower()}")
                i += 1
            p.rename(new)
            renames[p.name] = new.name
    return renames


def _photo(raw, renames):
    """'/assets/img/events/x.jpg' -> 'events/x.webp' (whatever the build produced)."""
    if not raw:
        return None
    name = raw.split("/")[-1]
    name = renames.get(name, name)
    stem = Path(name).stem
    for cand in (stem, _slug(stem)):
        if (IMG / "events" / f"{cand}.webp").exists():
            return f"events/{cand}.webp"
    return None


def _time(t):
    """'18:00' -> '6:00 PM'."""
    if not t:
        return ""
    h, m = map(int, str(t).split(":")[:2])
    return dt.time(h, m).strftime("%-I:%M %p")


def _iso(date, t):
    if not date:
        return None
    d = dt.date.fromisoformat(date)
    if not t:
        return d.isoformat()
    h, m = map(int, str(t).split(":")[:2])
    return dt.datetime(d.year, d.month, d.day, h, m, tzinfo=TZ).isoformat()


def _price(s):
    m = re.search(r"\$?\s*(\d+(?:\.\d{2})?)", s or "")
    return m.group(1) if m else None


def _load(kind, renames):
    out = []
    folder = CONTENT / kind
    for f in sorted(folder.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("published") is False:
            continue
        photo = _photo(d.get("photo"), renames)
        want = f"/assets/img/{photo}" if photo else d.get("photo")
        if photo and d.get("photo") != want:  # keep the admin pointing at the optimized file
            d["photo"] = want
            f.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        weekly = kind == "tournaments" and d.get("repeat") == "weekly"
        date = None if weekly else (str(d.get("date") or "")[:10] or None)
        if not weekly and not date:
            continue
        about = d.get("about") or {}
        body = (about.get("body") or d.get("description") or "").strip()
        ev = {
            "kind": kind, "id": f.stem, "title": d["title"].strip(),
            "desc_title": (about.get("title") or "").strip(),
            "body": body,
            "description": " ".join(x for x in ((about.get("title") or "").strip(), " ".join(body.split())) if x),
            "photo": photo, "photo_alt": (d.get("photo_alt") or "").strip() or f'Flyer: {d["title"].strip()} at Two Stooges',
            "weekly": weekly, "day": d.get("day") if weekly else None,
            "date": date, "start": d.get("start_time") or "", "end_time": d.get("end_time") or "",
            "doors": d.get("doors_time") or "", "signup": d.get("signup_time") or "",
            "facts": [], "note": (d.get("notes") or "").strip(),
            "link": d.get("link") or "", "link_label": d.get("link_label") or "",
            "contact_name": d.get("contact_name") or "", "contact_phone": d.get("contact_phone") or "",
        }
        if kind == "tournaments":
            for label, key in (("Game", "game"), ("Entry fee", "entry_fee"), ("Added money", "added_money"),
                               ("Format", "format"), ("Race", "race"), ("Rating limit", "rating_cap"),
                               ("Field", "player_limit")):
                if d.get(key):
                    ev["facts"].append((label, str(d[key])))
            ev["price"] = _price(d.get("entry_fee"))
        else:
            for row in d.get("details") or []:
                if row.get("label") and row.get("value"):
                    ev["facts"].append((row["label"], row["value"]))
            ev["price"] = _price(d.get("price"))
            if d.get("price"):
                ev["facts"].insert(0, ("Price", d["price"]))
        if ev["doors"]:
            ev["facts"].append(("Doors open", _time(ev["doors"])))
        if ev["signup"]:
            ev["facts"].append(("Sign-up closes", _time(ev["signup"])))
        # display strings
        times = _time(ev["start"])
        if times and ev["end_time"]:
            times += " – " + _time(ev["end_time"])
        if weekly:
            ev["when"] = f"Every {ev['day']}" + (f" · {times}" if times else "")
            ev["sort"] = "0000"
        else:
            d0 = dt.date.fromisoformat(date)
            ev["when"] = d0.strftime("%A, %B %-d, %Y") + (f" · {times}" if times else "")
            ev["short_date"] = d0.strftime("%a · %b %-d")
            ev["date_label"] = d0.strftime("%a · %b %-d, %Y")
            ev["sort"] = date
            ev["start_iso"] = _iso(date, ev["start"])
            ev["end_iso"] = None
            if ev["end_time"]:
                end_day = date
                if ev["start"] and ev["end_time"] < ev["start"]:  # ends after midnight
                    end_day = (d0 + dt.timedelta(days=1)).isoformat()
                ev["end_iso"] = _iso(end_day, ev["end_time"])
            ev["door_iso"] = _iso(date, ev["doors"]) if ev["doors"] else None
        ev["start_label"] = _time(ev["start"])
        out.append(ev)
    return out


def load(renames=None):
    renames = renames or {}
    return {k: _load(k, renames) for k in ("events", "tournaments")}
