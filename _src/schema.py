"""
Two Stooges — interlinked JSON-LD entity graph builder (Universal Prompt v3.1).

One @graph per page. Every node has a stable @id and nodes reference each other by
@id only. Business facts live in one config (BIZ_SCHEMA); services live in SERVICES.
build.py calls `graph_for(key, ...)` for every page and `check_graph()` fails the
build on a dangling @id or a Rule-11 property-placement trap.

Intentionally NOT marked up (see README):
  * Guest reviews/testimonials — displayed on-site but not first-party collected
    ratings; no Review/AggregateRating markup.
  * Past events — visible on /events/ but no longer actionable.
  * paymentAccepted, priceRange, smokingAllowed — not published on the site.
  * sameAs social profiles — none verified yet (add verified URLs to SAME_AS).
"""
import html as _html
import re

SITE = "https://twostooges.com"
BID = SITE + "/#business"
WID = SITE + "/#website"
AREA_ID = SITE + "/#service-area"
PLATFORMS = ["http://schema.org/DesktopWebPlatform", "http://schema.org/MobileWebPlatform"]

# Decoded from plus code 3PXP+85 Fridley → 86Q83PXP+85 (matches the Google Maps embed)
LAT, LNG = 45.098312, -93.264562
SERVICE_RADIUS_MI = 30
SERVICE_RADIUS_M = str(round(SERVICE_RADIUS_MI * 1609.34))
ANCHOR_CITY, STATE = "Fridley", "Minnesota"

# Verified profile URLs (client-supplied 2026-10-17). Never add from memory.
# GBP CID 0x4d32f5c7fba28d0 = 347673670564063440 (matches the ludocid in the client's Google link).
GBP_URL = "https://www.google.com/maps?cid=347673670564063440"
SAME_AS = [
    GBP_URL,
    "https://www.instagram.com/twostoogesbarandgrill/",
    "https://www.yelp.com/biz/two-stooges-sports-bar-and-grill-fridley",
    "https://www.tripadvisor.com/Restaurant_Review-g43087-d5259418-Reviews-Two_Stooges_Sports_Bar_Grill-Fridley_Minnesota.html",
    "https://maps.apple.com/place?place-id=I390CADDFBB3A1DE1",
]
# Wikidata IDs, each confirmed by two independent sources (DBpedia owl:sameAs + Wikidata/OSM/museum-digital).
WIKIDATA = {
    "cue": "https://www.wikidata.org/wiki/Q3341285",     # Cue sports (billiards)
    "darts": "https://www.wikidata.org/wiki/Q131471",    # Darts
    "fridley": "https://www.wikidata.org/wiki/Q985235",  # Fridley, Minnesota
}

WIKI = {
    "pool": ("Pool (cue sports)", "https://en.wikipedia.org/wiki/Pool_(cue_sports)"),
    "cue": ("Billiards", "https://en.wikipedia.org/wiki/Cue_sports"),
    "darts": ("Darts", "https://en.wikipedia.org/wiki/Darts"),
    "straight": ("Straight pool", "https://en.wikipedia.org/wiki/Straight_pool"),
    "eightball": ("Eight-ball", "https://en.wikipedia.org/wiki/Eight-ball"),
    "tenball": ("Ten-ball", "https://en.wikipedia.org/wiki/Ten-ball"),
    "sportsbar": ("Sports bar", "https://en.wikipedia.org/wiki/Sports_bar"),
    "league": ("Sports league", "https://en.wikipedia.org/wiki/Sports_league"),
    "party": ("Party", "https://en.wikipedia.org/wiki/Party"),
}


def thing(k):
    n, u = WIKI[k]
    return {"@type": "Thing", "name": n, "sameAs": [u, WIKIDATA[k]] if k in WIKIDATA else u}


def ep(url):
    """EntryPoint: urlTemplate + actionPlatform and nothing else (Rule 11)."""
    return {"@type": "EntryPoint", "urlTemplate": url, "actionPlatform": PLATFORMS}


# Services (three-level rule). `home` = exact visible blurb on the home page card.
SERVICES = {
    "billiards": {"@id": SITE + "/billiards/#service", "name": "Billiards & pool table rental", "serviceType": "Pool table rental",
                  "audience": "League players, casual groups and first-time pool players",
                  "url": SITE + "/billiards/", "category": "cue", "output": "Pool table time",
                  "home": "Gabriel's and Diamond tables in 9 ft and 7 ft, daily pool specials and a full Pro Shop."},
    "darts": {"@id": SITE + "/darts/#service", "name": "Darts", "serviceType": "Electronic dart boards",
              "audience": "Casual dart players, groups of friends and dart league teams",
                  "url": SITE + "/darts/", "category": "darts", "output": "Dart board play",
              "home": "Electronic dart boards, high-tops and dart leagues for every skill level."},
    "leagues": {"@id": SITE + "/leagues/#service", "name": "Pool & dart leagues", "serviceType": "Pool and dart leagues",
                "audience": "Pool and dart players of every skill level, including solo players",
                  "url": SITE + "/leagues/", "category": "league", "output": "League membership",
                "home": "In-house leagues as well as IBA (M8), APA and UPL, plus FargoRate Tournaments."},
    "parties": {"@id": SITE + "/private-parties/#service", "name": "Private parties & events", "serviceType": "Private event hosting",
                "audience": "Groups planning birthdays, office parties, banquets and holiday parties",
                  "url": SITE + "/private-parties/", "category": "party", "output": "Private party",
                "home": "Birthdays, office parties and banquets with custom menus and pool tables included."},
}
SERVICE_BY_URL = {v["url"]: k for k, v in SERVICES.items()}


def strip(s):
    return " ".join(_html.unescape(re.sub(r"<[^>]+>", "", s)).split())


def service_node(key, level, page_desc=None, related=(), offers=None, webpage_id=None):
    s = SERVICES[key]
    n = {"@type": "Service", "@id": s["@id"], "name": s["name"], "url": s["url"], "provider": {"@id": BID}}
    if level == "nav":
        return n
    n.update({"serviceType": s["serviceType"], "areaServed": {"@id": AREA_ID}, "category": thing(s["category"])})
    if level == "card":
        n["description"] = s["home"]
        return n
    n["description"] = page_desc
    n["serviceOutput"] = {"@type": "Thing", "name": s["output"]}
    n["audience"] = {"@type": "Audience", "audienceType": s["audience"]}  # audience + intent (visible in page lead)
    rel = [SERVICES[SERVICE_BY_URL[SITE + h]]["@id"] for h in related if SITE + h in SERVICE_BY_URL]
    if rel:
        n["isRelatedTo"] = [{"@id": r} for r in rel]
    if webpage_id:
        n["mainEntityOfPage"] = {"@id": webpage_id}
    if offers:
        n["offers"] = offers
    return n


def business_node(biz, page_key, extras=None):
    n = {
        "@type": ["BarOrPub", "SportsActivityLocation"],
        "@id": BID,
        "name": biz["name"],
        "alternateName": ["Two Stooges", "Two Stooges Sports Bar"],
        "url": SITE + "/",
        "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/brand/two-stooges-logo-1200.png", "width": 1200, "height": 543},
        "image": SITE + "/assets/img/og/home.jpg",
        "telephone": biz["tel"],
        "email": biz["email"],
        "foundingDate": "1988",
        "address": {"@type": "PostalAddress", "streetAddress": biz["street"], "addressLocality": biz["city"],
                    "addressRegion": biz["region"], "postalCode": biz["zip"], "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": LAT, "longitude": LNG},
        "hasMap": GBP_URL,
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                       "opens": "11:00", "closes": "23:59"}],
        "publicAccess": True,
        "hasMenu": SITE + "/menu/",
        "tourBookingPage": SITE + "/private-parties/",
        "areaServed": [
            {"@type": "GeoCircle", "@id": AREA_ID,
             "description": f"{SERVICE_RADIUS_MI}-mile service radius anchored on {ANCHOR_CITY}, {STATE}",
             "geoMidpoint": {"@type": "GeoCoordinates", "latitude": LAT, "longitude": LNG},
             "geoRadius": SERVICE_RADIUS_M},
            {"@type": "State", "name": STATE, "sameAs": "https://en.wikipedia.org/wiki/Minnesota"},
            {"@type": "City", "name": ANCHOR_CITY, "sameAs": ["https://en.wikipedia.org/wiki/Fridley,_Minnesota", WIKIDATA["fridley"]]},
        ],
        "knowsAbout": [thing(k) for k in ("cue", "darts", "pool", "straight", "eightball", "tenball", "sportsbar")],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Games, leagues & events at Two Stooges",
                            "itemListElement": [{"@id": s["@id"]} for s in SERVICES.values()]},
        "potentialAction": [
            {"@type": "CommunicateAction", "name": "Call Two Stooges", "target": ep("tel:" + biz["tel"])},
            {"@type": "CommunicateAction", "name": "Email Two Stooges", "target": ep("mailto:" + biz["email"])},
            {"@type": "AskAction", "name": "Request a private party", "target": ep(SITE + "/private-parties/#request")},
            {"@type": "JoinAction", "name": "Sign up for a pool or dart league", "target": ep(SITE + "/league-signup/#form")},
            {"@type": "AskAction", "name": "Send Two Stooges a message", "target": ep(SITE + "/contact/#form")},
        ],
    }
    if SAME_AS:
        n["sameAs"] = SAME_AS
    n.update(extras or {})
    return n


def website_node(name):
    return {"@type": "WebSite", "@id": WID, "url": SITE + "/", "name": name, "publisher": {"@id": BID}, "inLanguage": "en-US"}


def webpage_node(path, title, desc, og_url, og_alt, page_type="WebPage", crumb=None, main_entity=None, date=None):
    n = {"@type": page_type, "@id": SITE + path + "#webpage", "url": SITE + path, "name": title, "description": desc,
         "isPartOf": {"@id": WID}, "about": {"@id": BID}, "inLanguage": "en-US",
         "primaryImageOfPage": {"@type": "ImageObject", "url": og_url, "width": 1200, "height": 630, "caption": og_alt}}
    if date:
        n["dateModified"] = date
    if crumb:
        n["breadcrumb"] = {"@id": SITE + path + "#breadcrumb"}
    if main_entity:
        n["mainEntity"] = {"@id": main_entity}
    return n


def breadcrumb_node(path, name):
    return {"@type": "BreadcrumbList", "@id": SITE + path + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": SITE + path}]}


def graph(nodes):
    return {"@context": "https://schema.org", "@graph": nodes}


# ---------------------------------------------------------------------------
# Build-time checks (Deliverables 5 + 6)
# ---------------------------------------------------------------------------
KNOWN_TYPES = {"BarOrPub", "SportsActivityLocation", "WebSite", "WebPage", "ContactPage", "AboutPage", "CollectionPage",
               "BreadcrumbList", "ListItem", "Service", "Thing", "OfferCatalog", "Offer", "EntryPoint", "CommunicateAction",
               "AskAction", "JoinAction", "GeoCircle", "GeoCoordinates", "State", "City", "PostalAddress", "ImageObject",
               "OpeningHoursSpecification", "LocationFeatureSpecification", "Person", "FAQPage", "Question", "Answer",
               "Event", "Schedule", "Audience", "Menu", "MenuSection", "MenuItem"}
ENTRYPOINT_KEYS = {"@type", "urlTemplate", "actionPlatform"}


def _walk(x, fn, parent_type=None):
    if isinstance(x, dict):
        fn(x)
        t = x.get("@type")
        for k, v in x.items():
            _walk(v, fn, t)
    elif isinstance(x, list):
        for v in x:
            _walk(v, fn, parent_type)


def check_graph(g, where):
    errs, defined, refs = [], set(), set()

    def visit(n):
        t = n.get("@type")
        types = t if isinstance(t, list) else ([t] if t else [])
        if "@id" in n:
            (refs if set(n) == {"@id"} else defined).add(n["@id"])
        for ty in types:
            if ty not in KNOWN_TYPES:
                errs.append(f"{where}: unknown/unvetted @type {ty}")
        if n.get("@id") == BID:
            for bad in ("audience", "inLanguage"):
                if bad in n:
                    errs.append(f"{where}: '{bad}' on business node")
            if "Organization" in types:
                errs.append(f"{where}: Organization smuggled into business @type")
            area = n.get("areaServed", [])
            if set(n) != {"@id"} and [x.get("@type") for x in area] != ["GeoCircle", "State", "City"]:
                errs.append(f"{where}: areaServed must be exactly GeoCircle + State + anchor City (v3), got {[x.get('@type') for x in area]}")
        if "Service" in types:
            for bad in ("about", "inLanguage"):
                if bad in n:
                    errs.append(f"{where}: '{bad}' on Service {n.get('@id')}")
        if "EntryPoint" in types and set(n) - ENTRYPOINT_KEYS:
            errs.append(f"{where}: extra keys on EntryPoint {sorted(set(n) - ENTRYPOINT_KEYS)}")
        for k in n:
            if k.endswith("-input") and k != "query-input":
                errs.append(f"{where}: '{k}' annotation outside SearchAction")

    _walk(g["@graph"], visit)
    for r in sorted(refs - defined):
        errs.append(f"{where}: dangling @id {r}")
    biz = [n for n in g["@graph"] if n.get("@id") == BID]
    if len(biz) != 1:
        errs.append(f"{where}: expected exactly one business node, found {len(biz)}")
    return errs
