#!/usr/bin/env python3
"""
Two Stooges site generator.

Every page shares one header, footer, nav and business-info block defined
here, so hours/phone/nav only ever change in one place.

    python3 _src/build.py          # writes the HTML pages into the repo root

Then commit + push; Cloudflare Pages deploys `main` automatically.
To add an event: add a dict to EVENTS (newest first), drop the flyer in
assets/img/events/, run the build. Past events move to "Recent events"
automatically (at build time and again in the browser via site.js).
"""
import datetime as dt
import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"

# Flip to True on launch day (removes noindex). pages.dev stays noindex via _headers.
LAUNCH = False
SITE = "https://twostooges.com"
ASSET_VER = "20261017"

BIZ = {
    "name": "Two Stooges Sports Bar & Grill",
    "short": "Two Stooges",
    "street": "7178 University Ave NE",
    "city": "Fridley", "region": "MN", "zip": "55432",
    "phone": "(763) 574-1399", "tel": "+17635741399",
    "email": "info@twostooges.com",
    "hours": "Open daily 11 AM – 12 AM",
    "lat": 45.0983387, "lng": -93.2646008,
    "plus_code": "3PXP+85 Fridley, Minnesota",
}
MAP_EMBED = ("https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2816.3812678968425!2d-93.26460080000001"
             "!3d45.09833869999999!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x52b32ff775011167%3A0x4d32f5c7fba28d0"
             "!2sTwo%20Stooges%20Sports%20Bar%20%26%20Grill!5e0!3m2!1sen!2sus!4v1792215491423!5m2!1sen!2sus")
DIRECTIONS = ("https://www.google.com/maps/dir/?api=1&destination=Two+Stooges+Sports+Bar+%26+Grill%2C"
              "+7178+University+Ave+NE%2C+Fridley%2C+MN+55432")
COGNITO_KEY = "e5A6hQ7FG0We3U_f7oZrng"
FORM_LEAGUE = "99"   # existing League Signup form
FORM_EVENT = "96"    # existing Event / private party request form

NAV = [
    ("Eat & Drink", [("Menu", "/menu/", "Wings, burgers, pizza & more"),
                     ("Specials & Happy Hour", "/specials/", "Daily deals, 7 days a week")]),
    ("Play", [("Billiards", "/billiards/", "43 tables · Pro Shop"),
              ("Darts", "/darts/", "Boards & dart leagues"),
              ("Leagues & Tournaments", "/leagues/", "Join a league")]),
    ("Events", [("Upcoming Events", "/events/", "Tournaments & special nights"),
                ("Private Parties", "/private-parties/", "Birthdays, office parties & more")]),
    ("About", "/about/"),
    ("Gallery", "/gallery/"),
    ("Contact", "/contact/"),
]

TODAY = dt.date.today().isoformat()

# ---------------------------------------------------------------------------
# Events (newest first). `end` decides upcoming vs past.
# ---------------------------------------------------------------------------
EVENTS = [
    {
        "id": "bar-box-shootout-2026-11-07",
        "end": "2026-11-07",
        "start_iso": "2026-11-07T11:30:00-06:00",
        "door_iso": "2026-11-07T10:00:00-06:00",
        "dow": "Sat", "date": "Nov 7, 2026", "short_date": "Sat · Nov 7",
        "title": "499 & Under Fargo Rated 8-Ball Bar Box Shootout",
        "flyer": "events/2026-11-07-bar-box-shootout.webp",
        "flyer_alt": "Flyer: Nov 7th 499 and under Fargo rated 8 ball bar box shootout at Two Stooges. First 64 players, 4/3 race, alt break, double elimination, $40 entry fee, money added. Doors 10 AM, check-in closes 11 AM, starts 11:30 AM. Call or text Nick Johnson 612-449-9987.",
        "intro": "An 8-ball bar box shootout for players rated 499 and under on FargoRate. Only the first 64 players who sign up get in, so call or text early to grab your spot.",
        "facts": [("Entry fee", "$40 · money added"), ("Format", "Double elimination"), ("Race", "4/3 · alt break"),
                  ("Field", "First 64 players"), ("Check-in closes", "11:00 AM"), ("Starts", "11:30 AM")],
        "note": "Doors open at 10:00 AM. Players must have 150 robustness in FargoRate, or entry is at the tournament director's discretion.",
        "contact": ("Call or text Nick Johnson", "612-449-9987", "+16124499987"),
        "price": "40",
    },
    {
        "id": "fargo-8-ball-2026-10-10",
        "end": "2026-10-10",
        "start_iso": "2026-10-10T11:30:00-05:00",
        "door_iso": "2026-10-10T10:00:00-05:00",
        "dow": "Sat", "date": "Oct 10, 2026", "short_date": "Sat · Oct 10",
        "title": "499 & Under Fargo Rated 8-Ball Tournament",
        "flyer": "events/2026-10-10-fargo-8-ball.webp",
        "flyer_alt": "Flyer: 499 and under Fargo rated 8-ball tournament, Saturday October 10th 2026, only the first 48 players, $300 added. Doors 10 AM, check-in ends 11 AM, tournament starts 11:30 AM. 4/3 race, alt break. $30 entry fee, $5 green fee included. Call Nick Johnson 612-449-9987.",
        "intro": "8-ball for players rated 499 and under on FargoRate, limited to the first 48 players, with $300 added to the prize fund.",
        "facts": [("Entry fee", "$30 ($5 green fee incl.)"), ("Added", "$300"), ("Race", "4/3 · alt break"),
                  ("Field", "First 48 players"), ("Check-in ends", "11:00 AM"), ("Starts", "11:30 AM")],
        "note": "Doors open at 10:00 AM.",
        "contact": ("Call Nick Johnson", "612-449-9987", "+16124499987"),
        "price": "30",
    },
    {
        "id": "rum-ribs-cigar-night-2026-08-22",
        "end": "2026-08-22",
        "start_iso": "2026-08-22T18:00:00-05:00",
        "door_iso": None,
        "dow": "Sat", "date": "Aug 22, 2026", "short_date": "Sat · Aug 22",
        "title": "Rum, Ribs & Cigar Night",
        "flyer": "events/2026-08-22-rum-ribs-cigar-night.webp",
        "flyer_alt": "Flyer: Rum, Ribs & Cigar Night, Saturday August 22nd at 6 PM. $20 two rum slushies using Zacapa and Bacardi Limón served in a complimentary tiki glass. $45 three course meal: wedge salad; baby back ribs, coleslaw, baked beans, corn bread; key lime pie. $15 premium cigar. Buy all 3 and save $5. Limited seats, first come first served.",
        "intro": "Two rum slushies (Zacapa and Bacardi Limón) in a complimentary tiki glass, a three-course rib dinner and a premium cigar.",
        "facts": [("Rum slushies", "2 for $20"), ("3-course meal", "$45"), ("Premium cigar", "$15"),
                  ("Bundle", "Buy all 3, save $5"), ("Starts", "6:00 PM"), ("Seating", "First come, first served")],
        "note": "Menu: wedge salad · baby back ribs with coleslaw, baked beans & corn bread · key lime pie.",
        "contact": ("Questions? Call Two Stooges", BIZ["phone"], BIZ["tel"]),
        "price": None,
    },
]

LEAGUES = [
    {"day": "Tuesdays", "time": "11 AM", "name": "Straight Pool League",
     "flyer": "events/straight-pool-league.webp",
     "flyer_alt": "Flyer: Straight Pool League, Tuesdays starting Sept 8th, 11 AM start, BCA rules, 3 races to 50 points. Call 763-574-1399 to get signed up.",
     "points": ["11 AM start, every Tuesday", "BCA rules", "3 races to 50 points", "Season started Sept 8"]},
    {"day": "Thursdays", "time": "11 AM", "name": "10-Ball League",
     "flyer": "events/10-ball-league.webp",
     "flyer_alt": "Flyer: 10 Ball League, Thursdays at 11 AM. 3 sets, race to 5. No 10 ball break, spot the 10 ball. 3 foul rule in effect. Played on 9ft Gabriels with new cloth and rails. Starts early September. Call Two Stooges 763-574-1399.",
     "points": ["3 sets, race to 5", "No 10-ball on the break (spot the 10)", "3-foul rule in effect", "Played on 9 ft Gabriel's with new cloth & rails"]},
]

SPECIALS = [  # weekday: 0=Sun … 6=Sat (matches JS getDay)
    (1, "Monday", [("All day", "$2 off any burger", "excludes build-your-own & the Big Stooge"),
                   ("Happy Hour 2–5 PM", "$2 off appetizers", "excludes wings"),
                   ("Happy Hour 2–6 PM", "Drink specials", "domestic bottles & pints $3.50 · rail drinks $4")]),
    (2, "Tuesday", [("All day", "$3 off any entrée", ""),
                    ("Happy Hour 2–5 PM", "$2 off appetizers", "excludes wings"),
                    ("Happy Hour 2–6 PM", "Drink specials", "domestic bottles & pints $3.50 · rail drinks $4")]),
    (3, "Wednesday", [("All day", "$1 wings", "minimum 10"),
                      ("Happy Hour 2–5 PM", "$2 off appetizers", "excludes wings"),
                      ("Happy Hour 2–6 PM", "Drink specials", "domestic bottles & pints $3.50 · rail drinks $4")]),
    (4, "Thursday", [("Happy Hour 2–5 PM", "$2 off appetizers", "excludes wings"),
                     ("Happy Hour 2–6 PM", "Drink specials", "domestic bottles & pints $3.50 · rail drinks $4")]),
    (5, "Friday", [("Happy Hour 11 AM–7 PM", "$2 off appetizers", "excludes wings"),
                   ("Happy Hour 11 AM–7 PM", "Drink specials", "domestic bottles & pints $3.50 · rail drinks $4")]),
    (6, "Saturday", [("11 AM–7 PM", "$2 off sandwiches & wraps", ""),
                     ("11 AM–7 PM", "$3 off large pizza · $2 off small pizza", ""),
                     ("Happy Hour 11 AM–7 PM", "Drink specials", "domestic bottles & pints $3.50 · rail drinks $4")]),
    (0, "Sunday Funday", [("11 AM–7 PM", "$1.50 wings", "minimum 8"),
                          ("11 AM–7 PM", "$3 off large pizza · $2 off small pizza · $2 off any entrée", ""),
                          ("Happy Hour 11 AM–7 PM", "Drink specials + $1 off 22 oz craft beer", "domestic bottles & pints $3.50 · rail drinks $4")]),
]

REVIEWS = [
    ("Food and drinks are amazing. Staff is wonderful. Great environment!", "David"),
    ("We love to go to Two Stooges for a date night! We love to play pool and the food is great too!", "Ashley"),
    ("Great hang out, tucked away in Fridley. Nice staff, good food and drink options. Pool tables are nice. They have multiple dart boards.", "Josh"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
e = lambda s: html.escape(str(s), quote=True)

try:
    from PIL import Image
    def dims(rel):
        with Image.open(IMG / rel) as im:
            return im.size
except ImportError:  # still builds without Pillow, just without width/height
    def dims(rel):
        return (None, None)


def img(rel, alt, sizes="100vw", cls="", eager=False, srcset=True):
    """Responsive <img>. `rel` like 'photos/player-shooting' (no ext) or a full file path."""
    if rel.endswith(".webp") or rel.endswith(".png"):
        w, h = dims(rel)
        src, ss = f"/assets/img/{rel}", ""
    else:
        w, h = dims(rel + ".webp")
        src = f"/assets/img/{rel}.webp"
        ss = ""
        if srcset and (IMG / f"{rel}-sm.webp").exists():
            ss = f' srcset="/assets/img/{rel}-sm.webp 800w, {src} {w}w" sizes="{e(sizes)}"'
    wh = f' width="{w}" height="{h}"' if w else ""
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{src}"{ss}{wh} alt="{e(alt)}"{load}{c}>'


ICONS = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "mail": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "chev": '<polyline points="6 9 12 15 18 9"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "info": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    "award": '<circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>',
    "tv": '<rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="17 2 12 7 7 2"/>',
    "nav": '<polygon points="3 11 22 2 13 21 11 13 3 11"/>',
    "ball": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="11" r="3.5"/>',
    "bag": '<path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>',
    "mug": '<path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/><line x1="6" y1="2" x2="6" y2="4"/><line x1="10" y1="2" x2="10" y2="4"/><line x1="14" y1="2" x2="14" y2="4"/>',
    "fork": '<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>',
    "trophy": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
}


def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


def btn(label, href, style="gold", ic=None, extra=""):
    i = icon(ic) if ic else ""
    return f'<a class="btn btn--{style}" href="{e(href)}"{extra}>{i}{e(label)}</a>'


def rail():
    return '<div class="rail" aria-hidden="true"><div class="rail__diamonds">' + "<span></span>" * 9 + "</div></div>"


def section_head(eyebrow, title, intro="", center=False, h="h2"):
    c = " section-head--center" if center else ""
    p = f"<p>{intro}</p>" if intro else ""
    return f'<div class="section-head{c}"><span class="eyebrow">{eyebrow}</span><{h}>{title}</{h}>{p}</div>'


def cognito(form_id, title):
    return f'''<div class="form-panel">
  <script src="https://www.cognitoforms.com/f/seamless.js" data-key="{COGNITO_KEY}" data-form="{form_id}"></script>
  <noscript><iframe src="https://www.cognitoforms.com/f/{COGNITO_KEY}/{form_id}" title="{e(title)}" style="border:0;width:100%;height:900px"></iframe></noscript>
  <p class="form-panel__fallback">Form not loading? <a href="https://www.cognitoforms.com/f/{COGNITO_KEY}/{form_id}" target="_blank" rel="noopener">Open it in a new tab</a> or call <a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a>.</p>
</div>'''


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
def is_current(path, href):
    return path == href


def header(path):
    items = []
    for item in NAV:
        label, target = item[0], item[1]
        if isinstance(target, list):
            cur = any(is_current(path, h) for _, h, _ in target)
            links = "".join(
                f'<li><a href="{h}"{" aria-current=\"page\"" if is_current(path, h) else ""}>{e(t)}<small>{e(s)}</small></a></li>'
                for t, h, s in target)
            items.append(
                f'<li class="has-sub"><button class="nav__toggle{" is-current" if cur else ""}" type="button" aria-expanded="false">'
                f'{e(label)}{icon("chev", "chev")}</button><ul class="subnav">{links}</ul></li>')
        else:
            ac = ' aria-current="page"' if is_current(path, target) else ""
            items.append(f'<li><a class="nav__link" href="{target}"{ac}>{e(label)}</a></li>')

    mob = []
    flat = []
    for item in NAV:
        label, target = item[0], item[1]
        if isinstance(target, list):
            links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if is_current(path, h) else ""}>{e(t)}</a>' for t, h, _ in target)
            mob.append(f'<div class="mobile-menu__group"><div class="mobile-menu__label">{e(label)}</div>{links}</div>')
        else:
            flat.append(f'<a href="{target}"{" aria-current=\"page\"" if is_current(path, target) else ""}>{e(label)}</a>')
    mob.append(f'<div class="mobile-menu__group"><div class="mobile-menu__label">More</div>{"".join(flat)}</div>')

    return f'''<a class="skip-link" href="#main">Skip to content</a>
<div class="topbar">
  <div class="wrap">
    <div class="topbar__group">
      <span class="topbar__item open-status" data-open-status>{e(BIZ["hours"])}</span>
      <a class="topbar__item" href="{DIRECTIONS}" target="_blank" rel="noopener">{icon("pin")}{e(BIZ["street"])}, {e(BIZ["city"])}, {e(BIZ["region"])}</a>
    </div>
    <div class="topbar__group">
      <a class="topbar__item" href="mailto:{BIZ["email"]}">{icon("mail")}{e(BIZ["email"])}</a>
      <a class="topbar__item" href="tel:{BIZ["tel"]}">{icon("phone")}{e(BIZ["phone"])}</a>
    </div>
  </div>
</div>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/">{img("brand/two-stooges-logo.webp", "Two Stooges Sports Bar & Grill – home", eager=True, srcset=False)}</a>
    <nav class="site-nav" aria-label="Main"><ul class="nav">{"".join(items)}</ul></nav>
    <div class="header-cta">
      <a class="btn btn--outline btn--sm" href="tel:{BIZ["tel"]}">{icon("phone")}Call</a>
      <a class="btn btn--gold btn--sm" href="/private-parties/">Book a Party</a>
    </div>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu"><span class="menu-toggle__bars" aria-hidden="true"></span>Menu</button>
  </div>
  <div id="mobile-menu" class="mobile-menu" hidden>
    <div class="wrap">
      {"".join(mob)}
      <div class="mobile-menu__actions">
        <a class="btn btn--gold" href="tel:{BIZ["tel"]}">{icon("phone")}Call</a>
        <a class="btn btn--outline" href="{DIRECTIONS}" target="_blank" rel="noopener">{icon("nav")}Directions</a>
      </div>
      <p class="mobile-menu__meta">{e(BIZ["hours"])}<br>{e(BIZ["street"])}, {e(BIZ["city"])}, {e(BIZ["region"])} {e(BIZ["zip"])}</p>
    </div>
  </div>
</header>'''


def footer():
    return f'''<footer class="site-footer">
  {rail()}
  <div class="wrap">
    <div class="footer-grid" style="padding-top:3rem">
      <div class="footer-brand">
        {img("brand/two-stooges-logo.webp", "Two Stooges Sports Bar & Grill", srcset=False)}
        <p>Fridley's home for pool, darts, cold beer and game day since 1988.</p>
      </div>
      <div>
        <h2>Visit</h2>
        <ul>
          <li><a href="{DIRECTIONS}" target="_blank" rel="noopener">{e(BIZ["street"])}<br>{e(BIZ["city"])}, {e(BIZ["region"])} {e(BIZ["zip"])}</a></li>
          <li><a href="tel:{BIZ["tel"]}">{e(BIZ["phone"])}</a></li>
          <li><a href="mailto:{BIZ["email"]}">{e(BIZ["email"])}</a></li>
        </ul>
      </div>
      <div>
        <h2>Hours</h2>
        <div class="footer-hours"><span>Monday – Sunday</span><strong style="color:var(--text)">11 AM – 12 AM</strong><span class="small" style="margin-top:.5rem">Happy hour Mon–Thu 2–6 PM<br>Fri–Sun 11 AM–7 PM</span></div>
      </div>
      <div>
        <h2>Explore</h2>
        <ul>
          <li><a href="/menu/">Menu</a></li>
          <li><a href="/specials/">Specials</a></li>
          <li><a href="/billiards/">Billiards</a></li>
          <li><a href="/darts/">Darts</a></li>
          <li><a href="/leagues/">Leagues</a></li>
          <li><a href="/events/">Events</a></li>
          <li><a href="/private-parties/">Private Parties</a></li>
        </ul>
      </div>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>© <span data-year>2026</span> Two Stooges Sports Bar &amp; Grill. All rights reserved.</span>
    <span><a href="/about/">About</a> · <a href="/gallery/">Gallery</a> · <a href="/contact/">Contact</a> · Website by Multimedia Graphics</span>
  </div>
</footer>
<nav class="action-bar" aria-label="Quick actions">
  <a href="tel:{BIZ["tel"]}">{icon("phone")}Call</a>
  <a href="{DIRECTIONS}" target="_blank" rel="noopener">{icon("nav")}Directions</a>
  <a href="/events/">{icon("calendar")}Events</a>
</nav>
<dialog id="lightbox" class="lightbox" aria-label="Image viewer">
  <button class="lightbox__close" type="button" aria-label="Close image">×</button>
  <img src="data:," alt="">
  <p></p>
</dialog>'''


def local_business_ld():
    return {
        "@context": "https://schema.org",
        "@type": "BarOrPub",
        "@id": SITE + "/#business",
        "name": BIZ["name"],
        "url": SITE + "/",
        "telephone": BIZ["tel"],
        "email": BIZ["email"],
        "image": SITE + "/assets/img/photos/billiard-room-rows.webp",
        "logo": SITE + "/assets/img/brand/two-stooges-logo-1200.png",
        "servesCuisine": "American",
        "priceRange": "$$",
        "foundingDate": "1988",
        "address": {"@type": "PostalAddress", "streetAddress": BIZ["street"], "addressLocality": BIZ["city"],
                    "addressRegion": BIZ["region"], "postalCode": BIZ["zip"], "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": BIZ["lat"], "longitude": BIZ["lng"]},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                       "opens": "11:00", "closes": "23:59"}],
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True}
                           for n in ["43 pool tables", "Dart boards", "30 HD TVs + 4 big screens", "Pro shop", "Private event space"]],
    }


def page(path, title, desc, body, og_image="photos/billiard-room-rows.webp", extra_ld=None):
    full_title = title if "Two Stooges" in title else f"{title} | Two Stooges Sports Bar & Grill, Fridley MN"
    robots = "index, follow, max-image-preview:large" if LAUNCH else "noindex, nofollow"
    lds = [local_business_ld()] + (extra_ld or [])
    ld_html = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    url = SITE + path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#000000">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(BIZ["name"])}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/brand/favicon-48.png">
<link rel="apple-touch-icon" href="/assets/img/brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Oswald:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_VER}">
{ld_html}
</head>
<body>
{header(path)}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/site.js?v={ASSET_VER}" defer></script>
</body>
</html>
'''


def page_hero(crumb, eyebrow, title, lead, image, alt, actions=""):
    return f'''<section class="page-hero">
  <div class="page-hero__media">{img(image, alt, eager=True)}</div>
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / {e(crumb)}</nav>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{title}</h1>
    <p class="lead">{lead}</p>
    {f'<div class="btn-row">{actions}</div>' if actions else ""}
  </div>
</section>
{rail()}'''


def cta_band(title, text, actions):
    return f'''<section class="section section--tight"><div class="wrap"><div class="cta-band">
  <div><h2>{title}</h2><p>{text}</p></div>
  <div class="btn-row">{actions}</div>
</div></div></section>'''


def visit_section(head=True):
    h = section_head("Find us", "Visit Two Stooges", "Right on University Ave NE in Fridley. Plenty of parking, and walk-ins are always welcome.") if head else ""
    return f'''<section class="section section--alt" id="visit"><div class="wrap">
  {h}
  <div class="visit">
    <div class="visit__info">
      <div class="info-row"><span class="tile__icon">{icon("pin")}</span><div><h3>Address</h3><p><a href="{DIRECTIONS}" target="_blank" rel="noopener">{e(BIZ["street"])}<br>{e(BIZ["city"])}, {e(BIZ["region"])} {e(BIZ["zip"])}</a></p></div></div>
      <div class="info-row"><span class="tile__icon">{icon("clock")}</span><div><h3>Hours</h3><p>Open every day, 11 AM – 12 AM</p></div></div>
      <div class="info-row"><span class="tile__icon">{icon("phone")}</span><div><h3>Phone</h3><p><a href="tel:{BIZ["tel"]}">{e(BIZ["phone"])}</a></p></div></div>
      <div class="info-row"><span class="tile__icon">{icon("mail")}</span><div><h3>Email</h3><p><a href="mailto:{BIZ["email"]}">{e(BIZ["email"])}</a></p></div></div>
      <div class="btn-row mt-1">{btn("Get Directions", DIRECTIONS, "gold", "nav", ' target="_blank" rel="noopener"')}{btn("Call Us", "tel:" + BIZ["tel"], "outline", "phone")}</div>
    </div>
    <div class="map"><iframe src="{MAP_EMBED}" title="Map: Two Stooges Sports Bar &amp; Grill, 7178 University Ave NE, Fridley MN" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
  </div>
</div></section>'''


# ---------------------------------------------------------------------------
# Events rendering
# ---------------------------------------------------------------------------
def upcoming_events():
    return [ev for ev in EVENTS if ev["end"] >= TODAY]


def past_events():
    return [ev for ev in EVENTS if ev["end"] < TODAY]


def event_block(ev):
    facts = "".join(f'<div class="fact"><span class="fact__label">{e(k)}</span><span class="fact__value">{e(v)}</span></div>' for k, v in ev["facts"])
    who, num, tel = ev["contact"]
    big = f"/assets/img/{ev['flyer']}"
    return f'''<article class="event" id="{ev["id"]}" data-event-end="{ev["end"]}" data-past-card="past-{ev["id"]}">
  <button class="event__flyer" type="button" data-lightbox="{big}" data-alt="{e(ev["flyer_alt"])}" data-caption="{e(ev["title"])} · {e(ev["date"])}" aria-label="View full flyer: {e(ev["title"])}">
    {img(ev["flyer"], ev["flyer_alt"], srcset=False)}
  </button>
  <div>
    <div class="event__date"><span>{e(ev["dow"])}</span><span>{e(ev["date"])}</span></div>
    <h3>{e(ev["title"])}</h3>
    <p class="muted">{e(ev["intro"])}</p>
    <div class="event__facts">{facts}</div>
    <p class="event__note">{e(ev["note"])}</p>
    <div class="event__contact">
      {btn(f"{who}: {num}", "tel:" + tel, "gold", "phone")}
      <a class="text-link" href="/contact/">Directions &amp; parking</a>
    </div>
  </div>
</article>
<template id="past-{ev["id"]}">{past_card(ev)}</template>'''


def past_card(ev):
    big = f"/assets/img/{ev['flyer']}"
    return f'''<article class="past-card">
  <button type="button" data-lightbox="{big}" data-alt="{e(ev["flyer_alt"])}" data-caption="{e(ev["title"])} · {e(ev["date"])}" aria-label="View flyer: {e(ev["title"])}">{img(ev["flyer"], ev["flyer_alt"], srcset=False)}</button>
  <div><h3>{e(ev["title"])}</h3><p>{e(ev["dow"])} · {e(ev["date"])}</p></div>
</article>'''


def event_ld(ev):
    d = {
        "@context": "https://schema.org", "@type": "Event", "name": ev["title"],
        "startDate": ev["start_iso"], "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "description": ev["intro"], "image": [SITE + "/assets/img/" + ev["flyer"]],
        "location": {"@type": "Place", "name": BIZ["name"], "address": {"@type": "PostalAddress",
                     "streetAddress": BIZ["street"], "addressLocality": BIZ["city"], "addressRegion": BIZ["region"],
                     "postalCode": BIZ["zip"], "addressCountry": "US"}},
        "organizer": {"@type": "Organization", "name": BIZ["name"], "url": SITE + "/"},
    }
    if ev.get("door_iso"):
        d["doorTime"] = ev["door_iso"]
    if ev.get("price"):
        d["offers"] = {"@type": "Offer", "price": ev["price"], "priceCurrency": "USD", "url": SITE + "/events/#" + ev["id"],
                       "availability": "https://schema.org/LimitedAvailability"}
    return d


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def p_home():
    ups = upcoming_events()
    nxt = min(ups, key=lambda x: x["end"]) if ups else None  # soonest upcoming
    next_card = ""
    if nxt:
        next_card = f'''<aside class="next-up" data-next-up="{nxt["end"]}" aria-label="Next event">
      <div class="next-up__label">{icon("calendar")}Next up · {e(nxt["short_date"])}</div>
      <div class="next-up__body">
        {img(nxt["flyer"], nxt["flyer_alt"], srcset=False)}
        <div>
          <h3>{e(nxt["title"])}</h3>
          <p>{e(nxt["facts"][0][1])} · {e(nxt["facts"][3][1])} · starts {e(nxt["facts"][5][1])}</p>
          <a class="text-link" href="/events/#{nxt["id"]}">Event details</a>
        </div>
      </div>
    </aside>'''

    pillars = [
        ("photos/player-shooting", "A player lines up a shot on a blue-felt pool table at Two Stooges", "43 Tables", "Billiards",
         "Gabriel's and Diamond tables in 9 ft and 7 ft, daily pool specials and a full Pro Shop.", "/billiards/", "Shoot some pool"),
        ("photos/dart-room", "The Two Stooges dart area with a row of electronic dart boards and high-top tables", "Leagues every day", "Darts",
         "Electronic dart boards, high-tops and leagues for every skill level.", "/darts/", "Throw some darts"),
        ("photos/tournament-table-trophies", "A tournament pool table under the lights with trophies on the shelf above", "Weekly play", "Leagues & Tournaments",
         "Straight pool, 10-ball, APA and UPL leagues, plus FargoRate tournaments.", "/leagues/", "Join a league"),
        ("photos/pool-hall-interior", "The warmly lit Two Stooges billiard room set up for a group", "Up to big groups", "Private Parties",
         "Birthdays, office parties, draft parties and banquets, with food and pool tables included.", "/private-parties/", "Plan your party"),
    ]
    cards = "".join(f'''<article class="card card--link">
      <div class="card__media">{img(i, a, sizes="(max-width:640px) 100vw, (max-width:1000px) 50vw, 25vw")}</div>
      <div class="card__body"><span class="card__kicker">{k}</span><h3><a class="stretched" href="{h}" style="color:inherit;text-decoration:none">{t}</a></h3><p>{d}</p><span class="text-link">{l}</span></div>
    </article>''' for i, a, k, t, d, h, l in pillars)

    sched = [("Tuesday · 11 AM", "Straight Pool League", "BCA rules · 3 races to 50"),
             ("Thursday · 11 AM", "10-Ball League", "3 sets · race to 5"),
             ("Every day", "Dart Leagues", "All skill levels welcome"),
             ("Daily · 11 AM–5 PM", "Pool Specials", "Discounted table time")]
    sched_html = "".join(f'<div class="schedule__item"><div class="schedule__day">{d}</div><h3>{t}</h3><p>{s}</p></div>' for d, t, s in sched)

    deals = [("Monday", "$2 off any burger"), ("Wednesday", "$1 wings"), ("Sunday Funday", "$1.50 wings"), ("Mon–Thu 2–6 PM", "$3.50 domestics · $4 rails")]
    deals_html = "".join(f'<div class="tile" style="background:rgba(0,0,0,.35);border-color:rgba(246,194,26,.25)"><div class="schedule__day">{d}</div><h3 class="mb-0">{t}</h3></div>' for d, t in deals)

    quotes = "".join(f'<figure class="quote"><blockquote>{e(q)}</blockquote><figcaption>— {e(n)}</figcaption></figure>' for q, n in REVIEWS)

    body = f'''<section class="hero">
  <div class="hero__media">{img("photos/billiard-room-rows", "Rows of blue-felt pool tables in the Two Stooges billiard room", eager=True)}</div>
  <div class="wrap hero__inner">
    <div>
      <span class="eyebrow">Fridley, MN · Since 1988</span>
      <h1>The most fun you can have <span class="grad-text">under one roof</span></h1>
      <p class="lead">Classic American sports bar, restaurant and billiard room. 43 pool tables, dart boards, 30 HD TVs plus 4 monster screens, 16 ice-cold taps, and a team that feels like family.</p>
      <div class="btn-row">{btn("Upcoming Events", "/events/", "gold", "calendar")}{btn("Today's Specials", "/specials/", "outline")}</div>
      <div class="stat-row">
        <div><span class="stat__num">43</span><span class="stat__label">Pool tables</span></div>
        <div><span class="stat__num">34</span><span class="stat__label">Screens</span></div>
        <div><span class="stat__num">16</span><span class="stat__label">Taps</span></div>
        <div><span class="stat__num">7</span><span class="stat__label">Days a week</span></div>
      </div>
    </div>
    {next_card}
  </div>
</section>
{rail()}
<section class="section"><div class="wrap">
  {section_head("Pick your game", "Pool, darts &amp; a whole lot more", "Four ways to spend a night at Stooges. Come for one, stay for all of them.", center=True)}
  <div class="grid grid--4">{cards}</div>
</div></section>

<section class="section section--alt section--tight"><div class="wrap">
  <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:end;gap:1rem;margin-bottom:1.5rem">
    <div><span class="eyebrow">Every week</span><h2 class="mb-0">League nights &amp; regular play</h2></div>
    <a class="text-link" href="/leagues/">All leagues &amp; sign-up</a>
  </div>
  <div class="schedule">{sched_html}</div>
</div></section>

<section class="section section--felt"><div class="wrap">
  <div class="split">
    <div>
      <span class="eyebrow">Specials &amp; happy hour</span>
      <h2>A deal every <span class="grad-text">day of the week</span></h2>
      <p class="lead" style="color:#d5e6db">Happy hour runs Mon–Thu 2–6 PM and all weekend from 11 AM to 7 PM. On top of that there's a food special every day.</p>
      <div class="btn-row mt-2">{btn("See All Specials", "/specials/", "gold")}{btn("View Menu", "/menu/", "outline")}</div>
    </div>
    <div class="grid grid--2">{deals_html}</div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="split">
    <div class="split__media">
      {img("photos/dart-room", "Big-screen TV over the dart area at Two Stooges", sizes="(max-width:860px) 100vw, 50vw")}
      <div class="split__badge">NFL Sunday Ticket<small>+ all the DirecTV sports channels</small></div>
    </div>
    <div>
      <span class="eyebrow">The sports bar</span>
      <h2>Every game, <span class="grad-text">every screen</span></h2>
      <p class="lead">Our elevated bar sits right in the middle of the room, so wherever you sit you're close to the action. It's cherry wood with steel railings, and the tall booths fit your whole crew.</p>
      <ul class="check-list check-list--2col">
        <li>30 HD flat screens</li><li>4 monster screens</li><li>16 taps, poured ice-cold</li><li>Original cocktails</li><li>Scratch-made pub food</li><li>Open 11 AM – midnight</li>
      </ul>
      {btn("About Two Stooges", "/about/", "outline")}
    </div>
  </div>
</div></section>

<section class="section section--alt"><div class="wrap">
  <div class="split split--rev">
    <div class="split__media">
      {img("photos/building-exterior", "The Two Stooges building on University Ave NE in Fridley with its green awnings", sizes="(max-width:860px) 100vw, 50vw")}
      <div class="split__badge">Since 1988<small>Family-run in Fridley</small></div>
    </div>
    <div>
      <span class="eyebrow">Award-winning billiards</span>
      <h2>Named one of the <span class="grad-text">top ten billiard rooms</span> in North America</h2>
      <p class="lead">It started in 1988 as University Billiards. Almost four decades later, Two Stooges is still serving the coldest beer and juiciest burgers around, and City Pages voted us the best place in town to shoot pool.</p>
      <a class="text-link" href="/about/">Our story</a>
    </div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  {section_head("Happy customers", "What people are saying", center=True)}
  <div class="grid grid--3">{quotes}</div>
</div></section>
{visit_section()}'''
    return page("/", "Two Stooges Sports Bar & Grill | Pool, Darts & Sports Bar in Fridley, MN",
                "Fridley's sports bar, restaurant and billiard room since 1988. 43 pool tables, darts, 30 HD TVs plus 4 big screens, 16 taps, daily specials, leagues and tournaments.",
                body)


def p_menu():
    cats = [("Stoogetizers", "Shareable starters for the table"), ("Wings", "Classic bone-in wings with house sauces"),
            ("Burgers", "Including the Big Stooge"), ("Sandwiches & Wraps", "Hot, hearty and handheld"),
            ("Pizza", "Small and large, perfect for league night"), ("Entrées", "Full plates, made to order"),
            ("Soup & Salad", "Lighter options")]
    items = "".join(f'<div class="menu-cat"><span class="menu-cat__num">{i:02d}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></div>' for i, (t, d) in enumerate(cats, 1))
    body = f'''{page_hero("Menu", "Eat &amp; drink", "Pub food <span class='grad-text'>done right</span>",
        "Classic American sports bar food with our own twist, served from 11 AM until close. Burgers, wings, pizza and plenty more, plus 16 beers on tap.",
        "photos/billiard-balls-bokeh", "Colorful pool balls on felt", btn("Today's Specials", "/specials/", "gold") + btn("Call to Order: " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  <!-- TODO(client): send the current food & drink menu with prices to replace the category list below. -->
  <div class="notice mb-0" style="margin-bottom:2rem">{icon("info")}<p><strong>Our full menu is being updated.</strong> Call <a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a> for today's menu, or ask your server.</p></div>
  {section_head("On the menu", "What we're serving", "")}
  <div class="grid grid--2">{items}</div>
</div></section>
<section class="section section--alt"><div class="wrap">
  <div class="split">
    <div>
      <span class="eyebrow">At the bar</span>
      <h2>16 taps, <span class="grad-text">ice-cold</span></h2>
      <p class="lead">Every beer is poured through our iced cobra taps. Pair it with an original cocktail, or catch the happy hour prices on domestics and rails.</p>
      <ul class="price-list">
        <li><span>Domestic bottles &amp; pints <small class="muted">· happy hour</small></span><span class="price">$3.50</span></li>
        <li><span>Domestic 22 oz <small class="muted">· happy hour</small></span><span class="price">$4.25</span></li>
        <li><span>Rail drinks <small class="muted">· happy hour</small></span><span class="price">$4.00</span></li>
      </ul>
      <p class="small muted mt-1">Happy hour: Mon–Thu 2–6 PM · Fri–Sun 11 AM–7 PM.</p>
    </div>
    <div class="split__media">{img("photos/pool-hall-interior", "The Two Stooges room with tables and booths under warm lights", sizes="(max-width:860px) 100vw, 50vw")}</div>
  </div>
</div></section>
{cta_band("Feeding a crowd?", "We put together custom menus for birthdays, office parties, banquets and league banquets.", btn("Plan a Party", "/private-parties/", "gold"))}'''
    return page("/menu/", "Menu", "Burgers, wings, pizza, sandwiches, entrées and Stoogetizers at Two Stooges Sports Bar & Grill in Fridley, MN, plus 16 ice-cold beers on tap.", body)


def p_specials():
    days = []
    for wd, name, deals in SPECIALS:
        d = "".join(f'<div class="deal"><span class="deal__time">{e(t)}</span><span class="deal__what">{e(w)}{f"<br><small>{e(n)}</small>" if n else ""}</span></div>' for t, w, n in deals)
        days.append(f'<article class="day-card" data-weekday="{wd}"><div class="day-card__day"><h3>{e(name)}</h3><span class="today-badge">Today</span></div>{d}</article>')
    body = f'''{page_hero("Specials", "Daily deals", "Specials &amp; <span class='grad-text'>happy hour</span>",
        "There's a deal every day of the week. Today's specials are highlighted below.",
        "photos/billiard-balls-felt", "Pool balls on blue felt", btn("View Menu", "/menu/", "gold") + btn("Pool Specials", "#pool", "outline"))}
<section class="section"><div class="wrap">
  {section_head("This week", "Day-by-day specials", "Food specials, happy hour times and drink prices for each day.")}
  <div class="grid grid--4">{"".join(days)}</div>
  <p class="small muted mt-2">Prices don't include tax. Specials are dine-in only and can't be combined with other offers. Prices and times can change, so ask your server for today's deals.</p>
</div></section>
<section class="section section--alt" id="pool"><div class="wrap">
  <div class="split">
    <div class="split__media">{img("photos/player-lining-up-shot", "A player lining up a shot at Two Stooges", sizes="(max-width:860px) 100vw, 50vw")}</div>
    <div>
      <span class="eyebrow">Daily pool specials</span>
      <h2>Rack 'em up for less, <span class="grad-text">11 AM–5 PM</span></h2>
      <p class="lead">Discounted table time every day from 11 AM to 5 PM.</p>
      <!-- TODO(client): confirm pool special pricing (old site listed $11/$10/$12 on Billiards but $12/$11 on Specials). -->
      <ul class="price-list">
        <li><span>Regular</span><span class="price">$11</span></li>
        <li><span>Seniors</span><span class="price">$10</span></li>
        <li><span>Premier table</span><span class="price">$12</span></li>
      </ul>
      <p class="small muted mt-1">Plus tax. Grab a table and balls at the billiard counter.</p>
      {btn("About Our Tables", "/billiards/", "outline")}
    </div>
  </div>
</div></section>
{cta_band("Celebrating a birthday?", "Bring the crew. We'll set you up with tables, food and drinks for your group.", btn("Book a Party", "/private-parties/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}'''
    return page("/specials/", "Specials & Happy Hour", "Daily food specials and happy hour at Two Stooges in Fridley: $1 wings Wednesday, $2 off burgers Monday, Sunday Funday deals, $3.50 domestics and daily pool specials.", body, og_image="photos/billiard-balls-felt.webp")


def p_billiards():
    gallery = [("photos/billiard-hall-tables", "Rows of tables in the Two Stooges billiard hall"), ("photos/player-racking", "A player racking balls at a Two Stooges table"),
               ("photos/tournament-table-trophies", "Tournament table with trophies above"), ("photos/pool-balls-rack", "A fresh rack of pool balls on blue felt")]
    g = "".join(f'<figure class="gallery__item"><button type="button" data-lightbox="/assets/img/{p}.webp" data-alt="{e(a)}" data-caption="{e(a)}" aria-label="Enlarge: {e(a)}">{img(p, a, sizes="(max-width:640px) 100vw, 33vw")}</button></figure>' for p, a in gallery)
    body = f'''{page_hero("Billiards", "43 tables · since 1988", "Shoot some <span class='grad-text'>pool</span>",
        "Named a top ten billiard room in North America and voted best place to shoot pool by City Pages. 43 Gabriel's and Diamond tables in 9 ft and 7 ft, with room to play around every one.",
        "photos/billiard-hall-tables", "The Two Stooges billiard hall with rows of blue-felt tables", btn("Daily Pool Specials", "#rates", "gold") + btn("Join a League", "/leagues/", "outline"))}
<section class="section"><div class="wrap">
  <div class="grid grid--3">
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>43 tournament tables</h3><p>9 ft and 7 ft Gabriel's and Diamond tables on Simonis 860 cloth, with good lighting and comfortable seating at every table.</p></div>
    <div class="tile"><span class="tile__icon">{icon("trophy")}</span><h3>Leagues &amp; tournaments</h3><p>APA, UPL, in-house 8-ball, straight pool and 10-ball leagues, plus FargoRate tournaments throughout the year.</p></div>
    <div class="tile"><span class="tile__icon">{icon("bag")}</span><h3>Pro Shop</h3><p>Cues, cases, chalk, gloves, darts and accessories, plus cue repair.</p></div>
  </div>
</div></section>
<section class="section section--alt" id="rates"><div class="wrap">
  <div class="split">
    <div>
      <span class="eyebrow">How to rent a table</span>
      <h2>Grab a table, <span class="grad-text">pay when you're done</span></h2>
      <ol class="check-list" style="list-style:none">
        <li>Stop at the billiard counter. The attendant will set you up with a table and a set of balls.</li>
        <li>Play as long as you like. Order food and drinks right at your table.</li>
        <li>Bring the balls back to the counter and settle up.</li>
      </ol>
      <h3 class="mt-2">Daily pool specials · 11 AM–5 PM</h3>
      <!-- TODO(client): confirm pool special pricing. -->
      <ul class="price-list">
        <li><span>Regular</span><span class="price">$11</span></li>
        <li><span>Seniors</span><span class="price">$10</span></li>
        <li><span>Premier table</span><span class="price">$12</span></li>
      </ul>
      <p class="small muted mt-1">Plus tax.</p>
    </div>
    <div class="split__media">{img("photos/player-shooting", "A player shooting on a blue-felt table at Two Stooges", sizes="(max-width:860px) 100vw, 50vw")}<div class="split__badge">Top 10 Billiard Room<small>in North America</small></div></div>
  </div>
</div></section>
<section class="section" id="tournaments"><div class="wrap">
  {section_head("Compete", "Leagues &amp; tournaments", "Handicapped leagues for every skill level, and tournaments that are open to the public. You don't need to be in a league to play.")}
  <div class="grid grid--2">
    <div class="tile"><h3>Weekly leagues</h3><div class="tile__meta"><span class="chip chip--gold">Straight Pool · Tue 11 AM</span><span class="chip chip--gold">10-Ball · Thu 11 AM</span><span class="chip">APA</span><span class="chip">UPL</span><span class="chip">In-house 8-Ball</span></div><p class="mt-1">All leagues are handicapped, so beginners and sharks can play together.</p><a class="text-link" href="/leagues/">League details &amp; sign-up</a></div>
    <div class="tile"><h3>Tournaments</h3><p>FargoRate 8-ball tournaments and bar box shootouts with money added. Spots fill fast, so check the events calendar and sign up early.</p><a class="text-link" href="/events/">Upcoming tournaments</a></div>
  </div>
</div></section>
<section class="section section--alt" id="pro-shop"><div class="wrap">
  <div class="split split--rev">
    <div class="split__media">{img("photos/player-racking", "A player racking a game at Two Stooges", sizes="(max-width:860px) 100vw, 50vw")}</div>
    <div>
      <span class="eyebrow">Pro Shop</span>
      <h2>Gear up <span class="grad-text">in-house</span></h2>
      <p class="lead">Our Pro Shop carries cues and accessories for pool and darts, and we do cue repair on site.</p>
      <ul class="check-list"><li>Cues &amp; cases</li><li>Chalk, gloves &amp; accessories</li><li>Darts &amp; flights</li><li>Cue repair</li></ul>
      {btn("Ask About the Pro Shop", "tel:" + BIZ["tel"], "outline", "phone")}
    </div>
  </div>
</div></section>
<section class="section"><div class="wrap">
  {section_head("The room", "Inside the billiard room")}
  <div class="gallery">{g}</div>
</div></section>
{cta_band("Host your event on the tables", "Birthdays, draft parties, office parties, celebrations of life and banquets. We'll customize the menu and the room for you.", btn("Plan a Party", "/private-parties/", "gold"))}'''
    return page("/billiards/", "Billiards & Pool Tables", "43 Gabriel's and Diamond pool tables in Fridley, MN. Daily pool specials, APA, UPL, straight pool and 10-ball leagues, tournaments and a full Pro Shop with cue repair.", body, og_image="photos/billiard-hall-tables.webp")


def p_darts():
    body = f'''{page_hero("Darts", "Darts at Stooges", "Throw some <span class='grad-text'>darts</span>",
        "Electronic dart boards, high-top tables and a big screen. Bring friends for a casual game or join one of our leagues, which run every day of the week.",
        "photos/dart-bullseye-neon", "A dart hitting the bullseye under colorful bar lights", btn("Join a Dart League", "/leagues/#signup", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  <div class="split">
    <div class="split__media">{img("photos/dart-room", "The Two Stooges dart area with a row of electronic dart boards", sizes="(max-width:860px) 100vw, 50vw")}</div>
    <div>
      <span class="eyebrow">The dart area</span>
      <h2>Step up to <span class="grad-text">the line</span></h2>
      <p class="lead">Our dart area has a row of electronic boards, high-tops for your crew and a big screen showing the game. It's a great way to spend a night out with friends.</p>
      <ul class="check-list"><li>Electronic dart boards</li><li>High-top seating right by the boards</li><li>Food and drinks delivered to your table</li><li>Darts and flights in our Pro Shop</li></ul>
    </div>
  </div>
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("Dart leagues", "Leagues every day of the week", "Meet other players, sharpen your game and win cash. There's a league for every skill level.")}
  <div class="grid grid--3">
    <div class="tile"><span class="tile__icon">{icon("calendar")}</span><h3>Every night</h3><p>Leagues run every day of the week, so pick the night that works for you.</p></div>
    <div class="tile"><span class="tile__icon">{icon("users")}</span><h3>Custom leagues</h3><p>We can set up leagues for women, couples or teams. Just ask.</p></div>
    <div class="tile"><span class="tile__icon">{icon("award")}</span><h3>Win cash</h3><p>Compete for prize money and bragging rights all season long.</p></div>
  </div>
  <div class="btn-row mt-2">{btn("Sign Up for a League", "/leagues/#signup", "gold")}{btn("Ask a Team Member", "tel:" + BIZ["tel"], "outline", "phone")}</div>
</div></section>
{cta_band("Dart night for your group?", "Birthdays, office outings and team nights. We'll reserve boards and put together food for your group.", btn("Plan a Party", "/private-parties/", "gold"))}'''
    return page("/darts/", "Darts & Dart Leagues", "Electronic dart boards and dart leagues every day of the week at Two Stooges Sports Bar & Grill in Fridley, MN. Custom leagues for women, couples and teams.", body, og_image="photos/dart-room.webp")


def p_leagues():
    lg = []
    for L in LEAGUES:
        pts = "".join(f"<li>{e(p)}</li>" for p in L["points"])
        lg.append(f'''<article class="event">
  <button class="event__flyer" type="button" data-lightbox="/assets/img/{L["flyer"]}" data-alt="{e(L["flyer_alt"])}" data-caption="{e(L["name"])}" aria-label="View full flyer: {e(L["name"])}">{img(L["flyer"], L["flyer_alt"], srcset=False)}</button>
  <div>
    <div class="event__date"><span>{e(L["day"])}</span><span>{e(L["time"])}</span></div>
    <h3>{e(L["name"])}</h3>
    <ul class="check-list">{pts}</ul>
    <div class="event__contact">{btn("Call to sign up: " + BIZ["phone"], "tel:" + BIZ["tel"], "gold", "phone")}<a class="text-link" href="#signup">Or sign up online</a></div>
  </div>
</article>''')
    body = f'''{page_hero("Leagues", "Pool &amp; dart leagues", "Join a <span class='grad-text'>league</span>",
        "Stooges leagues are a great way to meet other pool and dart players, sharpen your skills and win cash. There's a league for every skill level.",
        "photos/tournament-table-trophies", "Tournament table with trophies above", btn("Sign Up Online", "#signup", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  {section_head("In-house pool leagues", "Weekday leagues on the 9-footers", "Played on our 9 ft Gabriel's tables. Click a flyer to see it full size.")}
  {"".join(lg)}
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("More leagues", "Something for every player")}
  <div class="grid grid--3">
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>APA &amp; UPL</h3><p>We host APA and UPL handicapped pool leagues, open to all skill levels.</p></div>
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>In-house 8-Ball</h3><p>Our own handicapped 8-ball league, a great first league for newer players.</p></div>
    <div class="tile"><span class="tile__icon">{icon("target")}</span><h3>Dart leagues</h3><p>Leagues every day of the week, plus custom leagues for women, couples and teams.</p></div>
  </div>
</div></section>
<section class="section" id="signup"><div class="wrap">
  <div class="split" style="align-items:start">
    <div>
      <span class="eyebrow">League sign-up</span>
      <h2>Get on <span class="grad-text">the roster</span></h2>
      <p class="lead">Fill out the form and we'll get you placed on a team or league night. Prefer the phone? Call us and a team member will sign you up.</p>
      <ul class="check-list"><li>Pool or darts</li><li>Solo players welcome. We'll help find you a team.</li><li>Handicapped, so every skill level can compete</li></ul>
      {btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone")}
    </div>
    {cognito(FORM_LEAGUE, "League sign-up form")}
  </div>
</div></section>'''
    return page("/leagues/", "Pool & Dart Leagues", "Join a pool or dart league at Two Stooges in Fridley, MN: Straight Pool Tuesdays 11 AM, 10-Ball Thursdays 11 AM, APA, UPL, in-house 8-ball and dart leagues every night.", body, og_image="events/10-ball-league.webp")


def p_events():
    ups = sorted(upcoming_events(), key=lambda x: x["end"])
    up_html = "".join(event_block(ev) for ev in ups)
    past_html = "".join(past_card(ev) for ev in past_events())
    weekly = "".join(f'''<div class="schedule__item"><div class="schedule__day">{e(L["day"])} · {e(L["time"])}</div><h3>{e(L["name"])}</h3><p>{e(L["points"][0])}</p></div>''' for L in LEAGUES)
    weekly += '<div class="schedule__item"><div class="schedule__day">Every day</div><h3>Dart Leagues</h3><p>All skill levels</p></div>'
    weekly += '<div class="schedule__item"><div class="schedule__day">Daily · 11 AM–5 PM</div><h3>Pool Specials</h3><p>Discounted table time</p></div>'
    body = f'''{page_hero("Events", "What's happening", "Upcoming <span class='grad-text'>events</span>",
        "Tournaments, league nights and special events at Two Stooges. Click any flyer to see it full size.",
        "photos/tournament-table-trophies", "Tournament table with trophies on the shelf", btn("Host Your Own Event", "/private-parties/", "gold") + btn("League Nights", "#weekly", "outline"))}
<section class="section"><div class="wrap">
  {section_head("Coming up", "Tournaments &amp; special nights")}
  <div data-upcoming>{up_html}</div>
  <div class="empty-note{"" if ups else " is-visible"}" data-empty-note>New events are on the way. Follow along in the bar or call <a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a> for what's coming up next.</div>
</div></section>
<section class="section section--alt section--tight" id="weekly"><div class="wrap">
  <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:end;gap:1rem;margin-bottom:1.5rem">
    <div><span class="eyebrow">Every week</span><h2 class="mb-0">Weekly league nights</h2></div>
    <a class="text-link" href="/leagues/">League details &amp; sign-up</a>
  </div>
  <div class="schedule">{weekly}</div>
</div></section>
<section class="section"><div class="wrap">
  <details class="past-events">
    <summary>Recent events</summary>
    <div class="past-grid" data-past-grid>{past_html}</div>
  </details>
</div></section>
{cta_band("Want to host a tournament or party?", "From birthday bashes to banquets and league parties, we'll help you plan it.", btn("Plan Your Event", "/private-parties/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}'''
    return page("/events/", "Events & Tournaments", "Upcoming pool tournaments, league nights and special events at Two Stooges Sports Bar & Grill in Fridley, MN.",
                body, og_image=(ups[0]["flyer"] if ups else "photos/tournament-table-trophies.webp"), extra_ld=[event_ld(ev) for ev in ups])


def p_parties():
    occasions = ["Birthdays", "Office parties", "Draft parties", "Holiday parties", "Celebrations of life", "Banquets & league parties", "Business meetings", "Reunions & receptions"]
    occ = "".join(f"<li>{e(o)}</li>" for o in occasions)
    body = f'''{page_hero("Private Parties", "Private parties &amp; events", "Always a reason <span class='grad-text'>to celebrate</span>",
        "Two Stooges is ready for your next birthday, holiday party, office outing or banquet. We'll customize the menu and the space for your group.",
        "photos/pool-hall-interior", "The Two Stooges room set up with tables and booths", btn("Request a Date", "#request", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  <div class="split">
    <div>
      <span class="eyebrow">Perfect for</span>
      <h2>Any occasion, <span class="grad-text">any size crew</span></h2>
      <p class="lead">We have a range of spaces for small and large groups, with pool tables, dart boards and big screens included.</p>
      <ul class="check-list check-list--2col">{occ}</ul>
    </div>
    <div class="split__media">{img("photos/billiard-hall-tables", "Tables ready for a group at Two Stooges", sizes="(max-width:860px) 100vw, 50vw")}</div>
  </div>
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("What's included", "We take care of the details", center=True)}
  <!-- TODO(client): add room names, capacities and package pricing when available. -->
  <div class="grid grid--4">
    <div class="tile"><span class="tile__icon">{icon("users")}</span><h3>Space for your group</h3><p>Different areas for small and large gatherings.</p></div>
    <div class="tile"><span class="tile__icon">{icon("fork")}</span><h3>Custom menus</h3><p>Food packages built for your group and budget.</p></div>
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>Pool &amp; darts</h3><p>Reserve tables and boards so your guests can play.</p></div>
    <div class="tile"><span class="tile__icon">{icon("tv")}</span><h3>Big screens</h3><p>Watch the game, or bring your own slideshow.</p></div>
  </div>
</div></section>
<section class="section" id="request"><div class="wrap">
  <div class="split" style="align-items:start">
    <div>
      <span class="eyebrow">Event request</span>
      <h2>Tell us about <span class="grad-text">your event</span></h2>
      <p class="lead">Send us the date, how many guests and what you're celebrating. We'll get back to you with options and pricing.</p>
      <div class="info-row mt-2"><span class="tile__icon">{icon("phone")}</span><div><h3>Rather talk it through?</h3><p><a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a></p></div></div>
      <div class="info-row mt-1"><span class="tile__icon">{icon("mail")}</span><div><h3>Email</h3><p><a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a></p></div></div>
    </div>
    {cognito(FORM_EVENT, "Private event request form")}
  </div>
</div></section>'''
    return page("/private-parties/", "Private Parties & Event Space", "Host birthdays, office parties, draft parties, banquets and celebrations of life at Two Stooges in Fridley, MN. Custom menus, pool tables, darts and big screens.", body, og_image="photos/pool-hall-interior.webp")


def p_about():
    tl = [("1988", "University Billiards opens", "Owners Ty Wilson and Greg Asproth open the doors in April 1988 with 17 pool tables and a snack bar."),
          ("1990s", "Room to grow", "The room grows to 56 pool tables and a full-service American restaurant."),
          ("1998", "Billiard Street Café", "A new name for a growing destination. You can still spot the sign out front."),
          ("2006", "Two Stooges is born", "A full sports bar joins the billiard room, and the business becomes Two Stooges Sports Bar & Grill."),
          ("Today", "Still racking 'em up", "43 tables, darts, 30 HD TVs plus 4 monster screens, 16 taps, and the same family feel.")]
    tl_html = "".join(f'<li><span class="timeline__year">{y}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for y, t, d in tl)
    awards = [("Top Ten Billiard Room in North America", "Billiards industry recognition"), ("Best Place to Shoot Pool", "City Pages, 2017"),
              ("Business of the Year", "Local business award"), ("Best of: Architectural Design", "Billiards Digest")]
    aw = "".join(f'<div class="tile"><span class="tile__icon">{icon("award")}</span><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in awards)
    body = f'''{page_hero("About", "Our story", "Fridley's game room <span class='grad-text'>since 1988</span>",
        "Two Stooges is a classic American sports bar, restaurant and billiard room. Almost four decades in, we're still serving the coldest beer and juiciest burgers around.",
        "photos/building-exterior", "The Two Stooges building on University Ave NE", btn("Visit Us", "/contact/", "gold"))}
<section class="section"><div class="wrap">
  <div class="split" style="align-items:start">
    <div>
      <span class="eyebrow">How it started</span>
      <h2>From 17 tables to <span class="grad-text">a Fridley institution</span></h2>
      <p class="lead">What began as a neighborhood billiard room became one of the best-known pool and darts destinations in Minnesota, with a full sports bar and kitchen to match.</p>
      <ol class="timeline mt-2">{tl_html}</ol>
    </div>
    <div class="split__media">{img("photos/tournament-table-trophies", "Tournament table with trophies above at Two Stooges", sizes="(max-width:860px) 100vw, 50vw")}</div>
  </div>
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("Recognition", "Award-winning, all-in-one fun", center=True)}
  <div class="grid grid--4">{aw}</div>
</div></section>
<section class="section"><div class="wrap">
  <div class="split split--rev">
    <div class="split__media">{img("photos/dart-room", "Big screen over the dart area", sizes="(max-width:860px) 100vw, 50vw")}</div>
    <div>
      <span class="eyebrow">The sports bar</span>
      <h2>A seat at the <span class="grad-text">center of the fun</span></h2>
      <p class="lead">Our elevated bar sits right in the middle of the room, so wherever you sit you're part of the action. It's cherry wood with steel railings, and the tall booths fit your whole group.</p>
      <ul class="check-list"><li>NFL Sunday Ticket and all the DirecTV sports channels</li><li>30 HD TVs and 4 monster screens</li><li>16 beers on tap</li><li>Original drinks and scratch-made food</li></ul>
    </div>
  </div>
</div></section>
{visit_section()}'''
    return page("/about/", "About Us", "Two Stooges opened in 1988 as University Billiards and grew into an award-winning sports bar, restaurant and billiard room in Fridley, MN.", body, og_image="photos/building-exterior.webp")


def p_gallery():
    photos = [("photos/billiard-room-rows", "Rows of blue-felt tables in the billiard room"), ("photos/player-shooting", "A player taking a shot"),
              ("photos/dart-room", "The dart area with electronic boards and a big screen"), ("photos/pool-hall-interior", "The billiard room under warm lights"),
              ("photos/player-racking", "Racking up a game"), ("photos/building-exterior", "Outside Two Stooges on University Ave NE"),
              ("photos/tournament-table-trophies", "Tournament table and trophies"), ("photos/player-lining-up-shot", "Lining up the shot"),
              ("photos/billiard-hall-tables", "The billiard hall"), ("photos/pool-balls-rack", "A fresh rack on blue felt")]
    g = "".join(f'<figure class="gallery__item"><button type="button" data-lightbox="/assets/img/{p}.webp" data-alt="{e(a)}" data-caption="{e(a)}" aria-label="Enlarge: {e(a)}">{img(p, a, sizes="(max-width:640px) 100vw, (max-width:1000px) 50vw, 33vw")}</button><figcaption>{e(a)}</figcaption></figure>' for p, a in photos)
    body = f'''{page_hero("Gallery", "Take a look", "Inside <span class='grad-text'>Two Stooges</span>",
        "The billiard room, the dart area and the bar. Click any photo to see it full size.",
        "photos/pool-hall-interior", "The Two Stooges billiard room")}
<section class="section"><div class="wrap"><div class="gallery">{g}</div></div></section>
{cta_band("See it in person", "Open every day from 11 AM to midnight at 7178 University Ave NE in Fridley.", btn("Get Directions", DIRECTIONS, "gold", "nav", ' target="_blank" rel="noopener"'))}'''
    return page("/gallery/", "Photo Gallery", "Photos of the billiard room, dart area and sports bar at Two Stooges Sports Bar & Grill in Fridley, MN.", body, og_image="photos/pool-hall-interior.webp")


def p_contact():
    body = f'''{page_hero("Contact", "Get in touch", "Contact &amp; <span class='grad-text'>directions</span>",
        "Questions about leagues, tournaments, parties or the menu? Give us a call or stop in. We're open every day from 11 AM to midnight.",
        "photos/building-exterior", "The Two Stooges building on University Ave NE", btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "gold", "phone") + btn("Get Directions", DIRECTIONS, "outline", "nav", ' target="_blank" rel="noopener"'))}
{visit_section(head=False)}
<section class="section"><div class="wrap">
  {section_head("How can we help?", "Quick links", center=True)}
  <div class="grid grid--3">
    <a class="card card--link" href="/private-parties/#request" style="text-decoration:none;color:inherit"><div class="card__body"><span class="tile__icon">{icon("users")}</span><h3>Plan a party</h3><p>Birthdays, office parties, banquets and more. Send us your event details.</p><span class="text-link">Event request form</span></div></a>
    <a class="card card--link" href="/leagues/#signup" style="text-decoration:none;color:inherit"><div class="card__body"><span class="tile__icon">{icon("trophy")}</span><h3>Join a league</h3><p>Pool or darts, every skill level. Sign up online or by phone.</p><span class="text-link">League sign-up</span></div></a>
    <a class="card card--link" href="/events/" style="text-decoration:none;color:inherit"><div class="card__body"><span class="tile__icon">{icon("calendar")}</span><h3>Tournaments &amp; events</h3><p>See what's coming up and how to get on the bracket.</p><span class="text-link">Upcoming events</span></div></a>
  </div>
  <p class="center small muted mt-2">Find us on Google Maps: {e(BIZ["plus_code"])}</p>
</div></section>'''
    return page("/contact/", "Contact & Directions", "Two Stooges Sports Bar & Grill, 7178 University Ave NE, Fridley, MN 55432. Call (763) 574-1399. Open daily 11 AM – 12 AM.", body, og_image="photos/building-exterior.webp")


def p_404():
    body = f'''<section class="section"><div class="wrap center" style="max-width:720px">
  <span class="eyebrow">Error 404</span>
  <h1>Scratch! <span class="grad-text">Page not found</span></h1>
  <p class="lead" style="margin:0 auto 2rem">That page has moved or doesn't exist. Try one of these instead.</p>
  <div class="btn-row" style="justify-content:center">{btn("Home", "/", "gold")}{btn("Events", "/events/", "outline")}{btn("Specials", "/specials/", "outline")}{btn("Contact", "/contact/", "outline")}</div>
</div></section>'''
    return page("/404.html", "Page Not Found", "The page you were looking for could not be found.", body)


PAGES = {
    "index.html": p_home, "menu/index.html": p_menu, "specials/index.html": p_specials,
    "billiards/index.html": p_billiards, "darts/index.html": p_darts, "leagues/index.html": p_leagues,
    "events/index.html": p_events, "private-parties/index.html": p_parties, "about/index.html": p_about,
    "gallery/index.html": p_gallery, "contact/index.html": p_contact, "404.html": p_404,
}


def main():
    for rel, fn in PAGES.items():
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(fn(), encoding="utf-8")
        print("wrote", rel)
    # sitemap
    urls = [SITE + "/" + (r[:-10] if r.endswith("index.html") else r) for r in PAGES if r != "404.html"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         "".join(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    robots = ("User-agent: *\nAllow: /\n\nSitemap: " + SITE + "/sitemap.xml\n") if LAUNCH else "User-agent: *\nDisallow: /\n"
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    print("wrote sitemap.xml, robots.txt (launch=%s)" % LAUNCH)


if __name__ == "__main__":
    main()
