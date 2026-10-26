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
import re
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import schema as SG
import images as IMGS

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"

# Flip to True on launch day (removes noindex). pages.dev stays noindex via _headers.
LAUNCH = False
SITE = "https://twostooges.com"
# Cache-busting version, computed from the CSS + JS contents so every change gets a new URL.
import hashlib as _hashlib
from pathlib import Path as _Path
_ROOT = _Path(__file__).resolve().parent.parent
ASSET_VER = _hashlib.sha1(b"".join((_ROOT / f).read_bytes() for f in ("assets/css/site.css", "assets/js/site.js"))).hexdigest()[:10]

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
              ("Leagues & Tournaments", "/leagues/", "Weekly pool & dart leagues"),
              ("League Sign-Up", "/league-signup/", "Join a league online")]),
    ("Events", [("Upcoming Events", "/events/", "Tournaments & special nights"),
                ("Private Parties", "/private-parties/", "Birthdays, office parties & more")]),
    ("About", "/about/"),
    ("Gallery", "/gallery/"),
    ("Contact", [("Contact Us", "/contact/", "Address, hours & message form"),
                 ("FAQ", "/faq/", "Answers to common questions")]),
]

TODAY = dt.date.today().isoformat()
GRAPHS = {}

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


# Day cards: (weekday 0=Sun, day, short, theme, headline price, headline item, note, time, extras, happy hour)
DAY_DEALS = [
    (1, "Monday", "Mon", "Burger Night", "$2 off", "any burger", "Excludes build-your-own & the Big Stooge", "All day",
     [("2–5 PM", "$2 off appetizers (excl. wings)")], "2–6 PM"),
    (2, "Tuesday", "Tue", "Entrée Night", "$3 off", "any entrée", "Pot roast, fish & chips, stir fry & more", "All day",
     [("2–5 PM", "$2 off appetizers (excl. wings)")], "2–6 PM"),
    (3, "Wednesday", "Wed", "Wing Night", "$1", "wings", "Minimum 10 · fresh, never frozen", "All day",
     [("2–5 PM", "$2 off appetizers (excl. wings)")], "2–6 PM"),
    (4, "Thursday", "Thu", "Appetizer Hour", "$2 off", "appetizers", "Excludes wings", "2–5 PM",
     [], "2–6 PM"),
    (5, "Friday", "Fri", "Early Happy Hour", "$2 off", "appetizers", "Excludes wings", "11 AM–7 PM",
     [], "11 AM–7 PM"),
    (6, "Saturday", "Sat", "Pizza & Sandwiches", "$3 off", "large pizza", "$2 off small pizzas too", "11 AM–7 PM",
     [("11 AM–7 PM", "$2 off sandwiches & wraps")], "11 AM–7 PM"),
    (0, "Sunday", "Sun", "Sunday Funday", "$1.50", "wings", "Minimum 8", "11 AM–7 PM",
     [("11 AM–7 PM", "$3 off large · $2 off small pizza"), ("11 AM–7 PM", "$2 off any entrée"), ("Happy hour", "$1 off 22 oz craft beer")], "11 AM–7 PM"),
]
HH_DRINKS = [("$3.50", "Domestic bottles"), ("$3.50", "Domestic pints"), ("$4.25", "Domestic 22 oz"), ("$4", "Rail drinks")]

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

# Google reviews (displayed only, never marked up). First names only, per client.
REVIEWS = [
    ("Will was Amazing! Very welcoming, knowledgeable and accommodating!!! He suggested the nachos! Get the nachos!! Get the stuff separate and make sure it's the chicken and beef combo!!! Sooooo good! Also add lettuce!! The drinks were strong and the pool tables were 6 per person and it's per hour!! Clean place and great service! I'll be back and hungry for more.", "Andrea", 5),
    ("A many-tabled pool hall with a bar, food, darts, and cardboard and e pulltabs. I go mostly to play pull tabs and have had my share of luck with the $1, $2, and $3 boxes. The $5 box is a little too rich for my blood. The charitable gambling benefits the Fridley Lions so even when I lose, it goes to a good cause. The burgers and sandwiches are great and I have to admit that I always finish the hot, crispy, tater tots before I even touch the burger.", "Christopher", 4),
    ("Loved the whole place. We have been looking for a pool hall and this place was perfect. It also has darts and a few arcade games. The drinks are good and strong and its not an arm and a leg for a shot. This place is good for kids, a night out or just brunch. The staff was very nice and helpful. The food was good and the atmosphere would be comfortable for anyone.", "Travel Genius", 4),
    ("Me & my family been going here for years we love the staff, customers, just the environment itself. We like family from other mother's & cultures & how times are now we all need a place to fellowship with peace & love inspite what the world is doing around us..", "Jessica", 5),
]


# ---------------------------------------------------------------------------
# Menu (from twostooges.com/menus, October 2026). Tags: "new", "signature".
# ---------------------------------------------------------------------------
SIDES_NOTE = "Served with fries, tater tots, chips & salsa or chips & queso. Substitute waffle fries +$2, or add a side salad or cup of soup +$3."
BYO = [
    ("Cheese", "$1 each", ["American", "Cheddar", "Pepper Jack", "Mozzarella", "Smokey Gouda", "Swiss"]),
    ("Toppings", "$1 each", ["Onion Straws", "Sautéed Onions", "Raw Onions", "Sautéed Mushrooms", "Jalapeños", "Black Olives",
                             "Green Olives", "Lettuce", "Tomato", "Pickles", "Pico de Gallo"]),
    ("Add-ons", "$2 each", ["Bacon", "Ham", "Fried Egg (cooked to order)*"]),
]
BYO_NOTE = ("<strong>Build it your way:</strong> cheese $1 each (American, cheddar, pepper jack, mozzarella, smoked gouda, Swiss) · "
            "toppings $1 each (onion straws, sautéed or raw onions, sautéed mushrooms, jalapeños, black or green olives, lettuce, tomato, pickles, pico de gallo) · "
            "bacon, ham or fried egg $2 each.")
MENU = [
    {"id": "stoogetizers", "name": "Stoogetizers", "note_top": "Shareable starters for the table, the bar or league night.",
     "advisory": True,
     "items": [
         ("Duck Bacon Wontons", "16", "Served with spicy plum sauce.", []),
         ("Cheese Curds", "12", "Served with marinara.", []),
         ("Chicken Tenders", "13", "Hand-breaded and fried chicken tenders, with french fries and your choice of dipping sauce.", []),
         ("Quesadilla", "15", "Flour tortilla filled with your choice of seasoned chicken, carnitas or beef, mixed cheese and pico de gallo, served with sour cream and salsa.", []),
         ("Nachos", "15", "Corn tortilla chips with your choice of seasoned chicken, carnitas or beef, topped with lettuce, queso, pico de gallo, black olives and jalapeños. Served with salsa and sour cream.", []),
         ("Potato Skins", "10", "Fried skins stuffed with potato, shredded cheese, bacon and green onions.", ["new"]),
         ("Garlic Cheese Bread", "12", "Five pieces of garlic bread topped with mozzarella, served with marinara.", []),
         ("Baskets", "8", "French fries, tater tots, chips and salsa, or chips and queso. Waffle fries $9.", []),
     ],
     "notes": ["Fries and tots come with one dipping sauce. Add cheese &amp; bacon +$3 or Cajun spice +$1."]},
    {"id": "wings", "name": "Wingin' It", "note_top": "Fresh, never frozen.",
     "items": [
         ("8 Bone-In Wings", "15", "Fresh, never frozen. Tossed in your choice of sauce or dry seasoning.", ["signature"]),
         ("9 oz Boneless Wings", "15", "Hand-breaded and tossed in your choice of sauce or dry seasoning.", []),
     ],
     "notes": ["<strong>Sauces:</strong> Honey BBQ · Buffalo · Mango Habanero · Garlic Parmesan · Bourbon · Sweet Thai Chili · Signature Sauce",
               "<strong>Dry seasonings:</strong> Lemon Pepper · Dry Rub · Dill Pickle · Cajun"]},
    {"id": "burgers", "name": "Burgers",
     "note_top": "Fresh, never frozen, handcrafted black Angus patties, cooked to order. " + SIDES_NOTE,
     "feature": ("Ask your server", "About the Burger of the Month"),
     "advisory": True,
     "items": [
         ("Bacon Cheeseburger", "15", "Cheddar cheese and Applewood smoked bacon.", ["raw"]),
         ("Triple B", "16", "Pepper jack, three strips of Applewood smoked bacon and honey BBQ sauce, topped with crispy onion strings.", ["raw"]),
         ("Big Stooge", "19", "Our guest favorite: two black Angus patties with pepper jack, American and cheddar, four strips of bacon, crispy onion strings, A-1, honey BBQ sauce and garlic basil aioli.", ["raw", "signature"]),
         ("Smash Burger", "16", "Two 5 oz patties smashed thin, topped with American cheese, lettuce, tomato and mustard aioli.", ["raw"]),
         ("Bourbon Smokey Burger", "16", "Applewood smoked bacon, honey bourbon BBQ sauce, pickle and smoked gouda.", ["raw"]),
         ("Smash Stuffed Curd Burger", "17", "Two 5 oz patties smashed with Wisconsin cheese curds and pepper jack, with chipotle ranch sauce.", ["raw"]),
         ("Build Your Own Burger", "12", "Start with a black Angus patty and add your favorites from the list below.", ["raw"]),
     ],
     "byo": {"noun": "burger", "photo": ("photos/burger-and-fries", "A Two Stooges double bacon cheeseburger stacked with onion strings, served in a basket with fries and pickles")}, "notes": []},
    {"id": "sandwiches", "name": "Sandwiches & Wraps", "note_top": SIDES_NOTE,
     "advisory": True,
     "items": [
         ("Chicken Tender Melt", "14", "Crispy chicken tenders topped with bacon, melted cheddar and our signature chicken dippin' sauce on sourdough toast.", []),
         ("Buffalo Chicken Wrap", "14", "Crispy chicken, lettuce, tomatoes, celery, shredded cheese, Buffalo sauce and ranch dressing wrapped in a flour tortilla.", []),
         ("Pot Roast French Dip", "15", "Tender pot roast and Swiss on a toasted hoagie, served with au jus. Make it Philly style with peppers and onions +$2.", []),
         ("Grilled Chicken Bacon Ranch", "15", "Grilled chicken, bacon, Swiss cheese and ranch dressing on a bun.", []),
         ("Walleye Sandwich", "19", "Battered walleye with lettuce, American cheese and tartar sauce (or try the spicy tartar) on a toasted hoagie.", ["signature"]),
         ("Dagwood", "17", "Ham, turkey, roast beef, salami, bacon, cheddar and Swiss, topped with lettuce, tomatoes, onions, pickles, Dijon mustard, mayo and oil &amp; vinegar sauce.", []),
         ("Chicken Caesar Wrap", "14", "Grilled chicken, romaine, shredded parmesan and Caesar dressing wrapped in a flour tortilla.", []),
         ("Cuban", "14", "Smoked pork, ham, Swiss cheese, dill pickles and mustard aioli on a grilled and pressed ciabatta bun.", ["new"]),
         ("BBQ Pulled Pork", "14", "Smoked BBQ pulled pork with dill pickles and fried onion straws, served with coleslaw.", ["new"]),
         ("Build Your Own Chicken Sandwich", "12", "Your choice of grilled chicken breast or crispy chicken tenders, built your way with the add-ons below.", []),
     ],
     "byo": {"noun": "sandwich"}, "notes": []},
    {"id": "pizza", "name": "Pizza", "note_top": "Hand-tossed specialty pies or build your own, with gluten-free crust available.",
     "sizes": ("Specialty pizza", [("Small", '9"', "16"), ("Large", '16"', "24"), ("Gluten-free", '10"', "23")]),
     "feature": ("Ask your server", "About today's special"),
     "items": [
         ("Meat Lovers", "16 / 24", "Pepperoni, sausage, ground beef, bacon and salami.", []),
         ("Crowd Pleaser", "16 / 24", "Pepperoni, sausage, green peppers, mushrooms and black olives.", []),
         ("Build Your Own — Small 9\"", "11", "Plus $1.50 per topping.", []),
         ("Build Your Own — Large 16\"", "16", "Plus $2.50 per topping.", []),
         ("Build Your Own — Gluten-Free 10\"", "15", "Plus $1.50 per topping.", []),
     ],
     "toppings": ["Pepperoni", "Sausage", "Bacon", "Ham", "Chicken", "Ground Beef", "Canadian Bacon", "Salami",
                  "Green Peppers", "Red Peppers", "Black Olives", "Green Olives", "Onions", "Red Onions", "Mushrooms",
                  "Jalapeños", "Pineapple", "Tomatoes", "Garlic", "Extra Cheese"],
     "notes": []},
    {"id": "entrees", "name": "Entrées", "note_top": "Add a side salad or a cup of soup to any entrée for $4.",
     "advisory": True,
     "items": [
         ("Chicken Stir Fry", "16", "Grilled chicken, carrots, broccoli, red and green peppers and onion tossed in our signature stir fry sauce, served over jasmine rice.", []),
         ("Mario's Spaghetti", "13", "Mario's signature meat sauce and spaghetti noodles, served with garlic toast.", []),
         ("Meatloaf", "15", "Our own special recipe, served with mashed potatoes, gravy, steamed vegetables and a dinner roll.", []),
         ("Loco Moco", "15", "Burger patty and a fried egg (cooked to order) with mushrooms, red and green onions and gravy, served over jasmine rice.", ["raw", "new"]),
     ],
     "notes": []},
    {"id": "soup-salad", "name": "Soup & Salad", "note_top": "All soups are made from scratch.",
     "advisory": True,
     "items": [
         ("House Salad", "7", "Spring mix, Roma tomatoes, red onion, black olives, shredded cheese and croutons.", []),
         ("Chef Salad", "15", "Heritage blend lettuce, diced ham, diced turkey, hard-boiled egg, diced tomatoes, shredded cheese, black olives and dressing. Served with a slice of garlic bread.", []),
         ("Taco Salad", "14", "Your choice of seasoned chicken, carnitas or beef. Lettuce topped with shredded cheese, black olives, pico de gallo and jalapeños in a crispy tortilla shell, with salsa and sour cream.", []),
         ("Chicken Caesar Salad", "14", "Grilled chicken and romaine topped with croutons, shredded parmesan and Caesar dressing. Served with a slice of garlic bread.", []),
         ("Chili, Creamy Chicken Wild Rice or Soup of the Day", "5 / 7", "Cup $5 · bowl $7. Ask your server for today's selection!", []),
     ],
     "notes": ["<strong>Dressings:</strong> French · Ranch · Blue Cheese · Honey Mustard · 1000 Island · Italian"]},
    {"id": "desserts", "name": "Desserts", "note_top": "Save room for something sweet.",
     "feature": ("Ask your server", "About dessert options"),
     "items": [],
     "notes": []},
]
ADVISORY = ("Consuming raw or undercooked meat, poultry, seafood, shellfish or eggs "
            "may increase your risk of foodborne illness.")


BYO_ICONS = {
    "cheese": '<path d="M3 18 21 8v10H3Z"/><path d="M3 18 13 9.5c2 .3 5.5-1 8-1.5"/><circle cx="15" cy="14.5" r="1.3"/><circle cx="9" cy="15.5" r=".9"/><circle cx="18.5" cy="11.8" r=".8"/>',
    "toppings": '<path d="M4 20c0-9 6.5-16 16-16 0 9.5-7 16-16 16Z"/><path d="M4 20 14 10"/><path d="M9.5 14.5h4.5M12 12V8.5"/>',
    "bold": '<path d="M12 3c.8 3.6 5 5.4 5 10.5a5 5 0 0 1-10 0c0-2.2 1.2-3.6 2.3-4.5 0 2 1 3.2 2.2 3.4-.4-3.3-.7-6.1.5-9.4Z"/>',
}
BYO_STEPS = [("cheese", "Choose your cheese"), ("toppings", "Add your toppings"), ("bold", "Make it extra bold")]


def byo_card(noun="burger", photo=None):
    def chip(x):
        if x.endswith("*"):
            return f'<li>{e(x[:-1])}<span class="advisory-mark" aria-hidden="true">*</span></li>'
        return f'<li>{e(x)}</li>'
    steps = "".join(f'''<li class="byo__step">
          <span class="byo__icon"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{BYO_ICONS[key]}</svg></span>
          <div class="byo__step-body"><h4>{e(label)} <span class="byo__price">{e(price)}</span></h4>
            <ul class="byo__chips">{"".join(chip(x) for x in items)}</ul></div>
        </li>''' for (key, label), (_, price, items) in zip(BYO_STEPS, BYO))
    media = (f'<div class="byo__media">{img(photo[0], photo[1], sizes="(max-width:860px) 100vw, 42vw")}</div>' if photo else "")
    return f'''<div class="byo{" byo--photo" if photo else ""}">
      {media}
      <div class="byo__body">
        <h3 class="byo__title"><span class="byo__title-a">build it</span> <span class="byo__title-b">your way</span></h3>
        <p class="byo__sub">Start with the base, then stack it however you like. <strong>It's your {e(noun)}.</strong></p>
        <ol class="byo__steps">{steps}</ol>
      </div>
    </div>'''


ALLERGEN = "Allergen warning: our menu items may contain milk, eggs, peanuts, tree nuts, fish, shellfish, soy and wheat."


def advisory_legend(show_signature=False):
    sig = ('<p class="menu-advisory__key"><span class="chip chip--gold">Signature</span> Signature item</p>' if show_signature else "")
    return (f'<div class="menu-advisory">{sig}'
            f'<p class="menu-advisory__key"><span class="advisory-mark" aria-hidden="true">*</span> {ADVISORY}</p>'
            f'<p class="menu-advisory__key"><span class="menu-advisory__allergen" aria-hidden="true">!</span> <strong>Allergen warning:</strong> {ALLERGEN.split(": ", 1)[1]}</p></div>')


MENU_DISCLAIMER = ("Consuming raw or undercooked meats, poultry, seafood, shellfish or eggs may increase your risk of foodborne illness. "
                   "Prices don't include tax and may change.")


# ---------------------------------------------------------------------------
# SEO: entity facts, page metadata, silos (CheiRank / internal linking)
# ---------------------------------------------------------------------------
KEYWORD = "Two Stooges Sports Bar"
LOCATION = "Fridley, Minnesota"
ENTITY_DESC = ("Two Stooges Sports Bar & Grill is a locally owned sports bar, restaurant and billiard room at "
               "7178 University Ave NE in Fridley, Minnesota. Open since 1988, it has 43 pool tables, dart boards, "
               "34 TV screens and 16 beers on tap.")
AREA_SERVED = ["Fridley", "Columbia Heights", "Spring Lake Park", "New Brighton", "Mounds View", "Coon Rapids", "Blaine", "Minneapolis"]
AWARDS = ["Top Ten Billiard Room in North America", "Best Place to Shoot Pool – City Pages (2017)",
          "Business of the Year", "Billiards Digest “Best of” Architectural Design"]

# key: (path, title ≤60, description 150–160, og source photo, og alt, breadcrumb name)
META = {
    "home": ("/", "Two Stooges Sports Bar - Fridley, MN | Pool, Darts & Grill",
             "Two Stooges Sports Bar & Grill in Fridley, MN: 43 pool tables, darts, 34 screens, 16 taps and daily specials since 1988. See events and plan your visit today.",
             "photos/billiard-room-rows", "Rows of pool tables inside Two Stooges Sports Bar in Fridley, MN", None),
    "menu": ("/menu/", "Bar & Grill Menu in Fridley, MN | Two Stooges Sports Bar",
             "See the Two Stooges Sports Bar menu: burgers, wings, pizza, sandwiches and Stoogetizers in Fridley, MN, with 16 ice-cold taps. Call ahead or stop in today.",
             "photos/tenders-and-beer", "Chicken tenders, fries and a cold beer at Two Stooges Sports Bar & Grill", "Menu"),
    "specials": ("/specials/", "Happy Hour & Daily Specials | Two Stooges Sports Bar",
                 "Two Stooges Sports Bar happy hour and daily specials in Fridley, MN: $1 wings Wednesday, $2 off burgers Monday, $3.50 domestics. See today's deals now.",
                 "photos/beers-on-bar", "Ice-cold pints on the bar, happy hour at Two Stooges", "Specials & Happy Hour"),
    "billiards": ("/billiards/", "Pool Tables & Billiards in Fridley, MN | Two Stooges",
                  "Play pool at Two Stooges Sports Bar in Fridley, MN: 43 Gabriel's and Diamond tables, daily pool specials, leagues, tournaments and a Pro Shop. Rack up today.",
                  "photos/billiard-room-gabriels-wide", "The 43-table billiard room at Two Stooges Sports Bar in Fridley", "Billiards"),
    "darts": ("/darts/", "Darts & Dart Leagues in Fridley, MN | Two Stooges",
              "Throw darts at Two Stooges Sports Bar in Fridley, MN. Electronic dart boards, high-tops, a big screen and dart leagues every day of the week. Sign up today.",
              "photos/dart-room", "Electronic dart boards at Two Stooges Sports Bar in Fridley", "Darts"),
    "leagues": ("/leagues/", "Pool & Dart Leagues in Fridley, MN | Two Stooges",
                "Join a pool or dart league at Two Stooges Sports Bar in Fridley, MN: Straight Pool Tuesdays, 10-Ball Thursdays, APA, UPL and daily darts. Sign up online.",
                "photos/tournament-table-trophies", "League table and trophies at Two Stooges Sports Bar", "Leagues & Tournaments"),
    "signup": ("/league-signup/", "League Sign-Up in Fridley, MN | Two Stooges Sports Bar",
               "Sign up for a pool or dart league at Two Stooges Sports Bar in Fridley, MN. Straight pool, 10-ball, APA, UPL and darts for every skill level. Join today.",
               "photos/player-lining-up-shot", "A league player lining up a shot at Two Stooges Sports Bar", "League Sign-Up"),
    "events": ("/events/", "Pool Tournaments & Events in Fridley | Two Stooges",
               "Upcoming pool tournaments, FargoRate 8-ball shootouts, league nights and special events at Two Stooges Sports Bar in Fridley, MN. See dates and sign up.",
               "photos/player-shooting", "A tournament player shooting at Two Stooges Sports Bar", "Events"),
    "parties": ("/private-parties/", "Private Party Venue in Fridley, MN | Two Stooges",
                "Host a birthday, office party, banquet or draft party at Two Stooges Sports Bar in Fridley, MN, with custom menus, pool tables and darts. Request a date.",
                "photos/pool-hall-interior", "Party space at Two Stooges Sports Bar & Grill in Fridley", "Private Parties"),
    "about": ("/about/", "About Two Stooges Sports Bar | Fridley, MN Since 1988",
              "Two Stooges Sports Bar & Grill opened in Fridley, MN in 1988 as University Billiards. Meet the award-winning billiard room and sports bar. Read our story.",
              "photos/storefront-two-stooges", "The Two Stooges Sports Bar & Grill storefront on University Ave NE, Fridley", "About"),
    "gallery": ("/gallery/", "Photos of Two Stooges Sports Bar | Fridley, MN",
                "Photos of Two Stooges Sports Bar in Fridley, MN: the 43-table billiard room, dart area, sports bar and building on University Ave NE. Take a look inside.",
                "photos/billiard-room-rows", "Inside the Two Stooges Sports Bar billiard room", "Gallery"),
    "contact": ("/contact/", "Contact & Directions | Two Stooges Sports Bar, Fridley",
                "Contact Two Stooges Sports Bar & Grill at 7178 University Ave NE, Fridley, MN 55432. Call (763) 574-1399. Open daily 11 AM to midnight. Get directions.",
                "photos/building-exterior", "Two Stooges Sports Bar & Grill, 7178 University Ave NE, Fridley MN", "Contact"),
    "faq": ("/faq/", "FAQ | Two Stooges Sports Bar & Grill, Fridley MN",
            "Answers about Two Stooges Sports Bar in Fridley, MN: hours, location, pool tables, darts, leagues, tournaments, food, happy hour and private parties. Read more.",
            "photos/billiard-room-gabriels", "The Two Stooges billiard room in Fridley, MN", "FAQ"),
    "privacy": ("/privacy-policy/", "Privacy Policy | Two Stooges Sports Bar",
                "Read the Two Stooges Sports Bar & Grill privacy policy: what information our Fridley, MN website collects through forms and maps, and how we use and protect it.",
                "photos/billiard-room-rows", "Two Stooges Sports Bar & Grill", "Privacy Policy"),
}

# Related-page cards (descriptive anchors). Silos: Play · Eat & Drink · Plan your visit.
LINK_INFO = {
    "/menu/": ("Two Stooges menu", "Burgers, wings, pizza, Stoogetizers and 16 beers on tap."),
    "/specials/": ("Happy hour & daily specials", "A food or drink deal every day of the week."),
    "/billiards/": ("Billiards in Fridley", "43 tournament tables, pool specials and the Pro Shop."),
    "/darts/": ("Darts at Two Stooges", "Electronic boards and dart leagues every night."),
    "/leagues/": ("Pool & dart leagues", "Straight pool, 10-ball, APA, UPL and darts. Sign up online."),
    "/league-signup/": ("League sign-up", "Join a pool or dart league online. Every skill level welcome."),
    "/events/": ("Tournaments & events", "FargoRate shootouts, league nights and special events."),
    "/private-parties/": ("Private parties", "Birthdays, office parties and banquets with custom menus."),
    "/about/": ("Our story since 1988", "From University Billiards to Two Stooges Sports Bar & Grill."),
    "/gallery/": ("Photo gallery", "Take a look inside the billiard room, dart area and bar."),
    "/faq/": ("Two Stooges FAQ", "Hours, pool tables, leagues, food and parties, answered."),
    "/contact/": ("Contact & directions", "Address, hours, phone and a map to 7178 University Ave NE."),
}
RELATED = {
    "menu": ["/specials/", "/private-parties/", "/events/"],
    "specials": ["/menu/", "/billiards/", "/events/"],
    "billiards": ["/leagues/", "/events/", "/darts/"],
    "darts": ["/leagues/", "/billiards/", "/private-parties/"],
    "leagues": ["/league-signup/", "/billiards/", "/events/"],
    "signup": ["/leagues/", "/billiards/", "/darts/"],
    "events": ["/leagues/", "/private-parties/", "/billiards/"],
    "parties": ["/menu/", "/billiards/", "/darts/"],
    "about": ["/gallery/", "/billiards/", "/contact/"],
    "gallery": ["/about/", "/billiards/", "/darts/"],
    "contact": ["/faq/", "/private-parties/", "/leagues/"],
    "privacy": ["/contact/", "/about/", "/events/"],
    "faq": ["/contact/", "/league-signup/", "/private-parties/"],
}

FAQ = [
    ("Where is Two Stooges Sports Bar located?",
     f'Two Stooges Sports Bar &amp; Grill is at 7178 University Ave NE, Fridley, MN 55432, on University Avenue (Highway 47) just north of Minneapolis. <a href="/contact/">Get directions and parking info</a>.',
     "Two Stooges Sports Bar & Grill is at 7178 University Ave NE, Fridley, MN 55432, on University Avenue (Highway 47) just north of Minneapolis."),
    ("What are the hours at Two Stooges?",
     'We\'re open every day from 11 AM to 12 AM (midnight). Happy hour runs Monday to Thursday 2–6 PM and Friday to Sunday 11 AM–7 PM. See <a href="/specials/">today\'s specials</a>.',
     "Two Stooges is open every day from 11 AM to 12 AM. Happy hour runs Monday to Thursday 2–6 PM and Friday to Sunday 11 AM–7 PM."),
    ("How many pool tables does Two Stooges have?",
     'Two Stooges has 43 pool tables, 9 ft and 7 ft Gabriel\'s and Diamond tables on Simonis 860 cloth. <a href="/billiards/">Learn about our billiard room</a>.',
     "Two Stooges has 43 pool tables, 9 ft and 7 ft Gabriel's and Diamond tables on Simonis 860 cloth."),
    ("Does Two Stooges have pool and dart leagues?",
     'Yes. We run a Straight Pool League on Tuesdays at 11 AM, a 10-Ball League on Thursdays at 11 AM, APA, UPL and in-house 8-ball leagues, and dart leagues every day. <a href="/leagues/">Sign up for a league</a>.',
     "Yes. Two Stooges runs a Straight Pool League on Tuesdays at 11 AM, a 10-Ball League on Thursdays at 11 AM, APA, UPL and in-house 8-ball leagues, and dart leagues every day."),
    ("Can I host a private party at Two Stooges?",
     'Yes. Two Stooges hosts birthdays, office parties, draft parties, banquets and celebrations of life, with custom menus, pool tables and darts. <a href="/private-parties/">Request a party date</a>.',
     "Yes. Two Stooges hosts birthdays, office parties, draft parties, banquets and celebrations of life, with custom menus, pool tables and darts."),
    ("Can I watch NFL games at Two Stooges?",
     'Yes. We carry NFL Sunday Ticket and the DirecTV sports channels on 30 HD TVs and 4 monster screens. <a href="/about/">More about the sports bar</a>.',
     "Yes. Two Stooges carries NFL Sunday Ticket and the DirecTV sports channels on 30 HD TVs and 4 monster screens."),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
e = lambda s: html.escape(str(s), quote=True)


def L(href, text):
    """Contextual in-body link with descriptive anchor text (always canonical, trailing slash)."""
    return f'<a href="{href}">{text}</a>'


try:
    from PIL import Image
    def dims(rel):
        with Image.open(IMG / rel) as im:
            return im.size
except ImportError:  # still builds without Pillow, just without width/height
    Image = None
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
            sw, _ = dims(f"{rel}-sm.webp")
            ss = f' srcset="/assets/img/{rel}-sm.webp {sw}w, {src} {w}w" sizes="{e(sizes)}"'
    wh = f' width="{w}" height="{h}"' if w else ""
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{src}"{ss}{wh} alt="{e(alt)}"{load}{c}>'


def make_og(key, src_rel):
    """1200x630 Open Graph image: cover-cropped photo + logo. Written to assets/img/og/<key>.jpg"""
    out = IMG / "og" / f"{key}.jpg"
    if Image is None:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(IMG / f"{src_rel}.webp") as im:
        im = im.convert("RGB")
        W, H = 1200, 630
        s = max(W / im.width, H / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        l, t = (im.width - W) // 2, (im.height - H) // 2
        im = im.crop((l, t, l + W, t + H))
    shade = Image.new("L", (W, H))
    px = shade.load()
    for y in range(H):
        for x in range(0, W, 4):
            a = int(min(235, max(0, 70 + 170 * (y / H) + 60 * (1 - x / W))))
            for k in range(4):
                if x + k < W:
                    px[x + k, y] = a
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, shade)
    with Image.open(IMG / "brand" / "two-stooges-logo-1200.png") as logo:
        logo = logo.convert("RGBA")
        lw = 460
        logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
        im.paste(logo, (56, H - logo.height - 48), logo)
    im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    return out


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
    "fork": '<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>',
    "mug": '<path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/><line x1="6" y1="2" x2="6" y2="4"/><line x1="10" y1="2" x2="10" y2="4"/><line x1="14" y1="2" x2="14" y2="4"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="6.34" y2="6.34"/><line x1="17.66" y1="17.66" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="6.34" y2="17.66"/><line x1="17.66" y1="6.34" x2="19.07" y2="4.93"/>',
    "trophy": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
}


def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


def btn(label, href, style="gold", ic=None, extra=""):
    i = icon(ic) if ic else ""
    return f'<a class="btn btn--{style}" href="{e(href)}"{extra}>{i}{e(label)}</a>'


def rail():
    return '<div class="rail" aria-hidden="true"><div class="rail__diamonds">' + "<span></span>" * 9 + "</div></div>"


def section_head(eyebrow, title, intro="", center=False, h="h2"):
    c = " section-head--center" if center else ""
    p = f"<p>{intro}</p>" if intro else ""
    return f'<div class="section-head{c}"><span class="eyebrow">{eyebrow}</span><{h}>{title}</{h}>{p}</div>'


FORM_HEIGHTS = {FORM_LEAGUE: 1200, FORM_EVENT: 592}


def cognito(form_id, title):
    """Cognito Forms iframe embed exactly as supplied by the client (+ title for accessibility)."""
    return f'''<div class="form-panel">
  <iframe src="https://www.cognitoforms.com/f/{COGNITO_KEY}/{form_id}" title="{e(title)}" allow="payment" style="border:0;width:100%;" height="{FORM_HEIGHTS[form_id]}"></iframe>
  <script src="https://www.cognitoforms.com/f/iframe.js"></script>
  <p class="form-panel__fallback">Form not loading? <a href="https://www.cognitoforms.com/f/{COGNITO_KEY}/{form_id}" target="_blank" rel="noopener">Open the {e(title.lower())} in a new tab</a> or call <a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a>. We only use your details to respond to you. See our <a href="/privacy-policy/">privacy policy</a>.</p>
</div>'''


def related(key):
    hrefs = RELATED.get(key)
    if not hrefs:
        return ""
    cards = "".join(f'''<article class="card card--link"><div class="card__body">
      <span class="card__kicker">Keep exploring</span>
      <h3><a class="stretched" href="{h}">{e(LINK_INFO[h][0])}</a></h3>
      <p>{e(LINK_INFO[h][1])}</p>
    </div></article>''' for h in hrefs)
    return f'''<section class="section section--tight related" aria-labelledby="related-h"><div class="wrap">
  <div class="section-head"><span class="eyebrow">More at Two Stooges</span><h2 id="related-h">More to do at Two Stooges in Fridley</h2></div>
  <div class="grid grid--3">{cards}</div>
</div></section>'''


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

    mob, flat = [], []
    for item in NAV:
        label, target = item[0], item[1]
        if isinstance(target, list):
            links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if is_current(path, h) else ""}>{e(t)}</a>' for t, h, _ in target)
            mob.append(f'<div class="mobile-menu__group"><div class="mobile-menu__label">{e(label)}</div>{links}</div>')
        else:
            flat.append(f'<a href="{target}"{" aria-current=\"page\"" if is_current(path, target) else ""}>{e(label)}</a>')
    mob.append(f'<div class="mobile-menu__group"><div class="mobile-menu__label">More</div>{"".join(flat)}</div>')

    return f'''<a class="skip-link" href="#main">Skip to content</a>
<div class="topbar on-dark">
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
<header class="site-header on-dark">
  <div class="wrap header-inner">
    <a class="brand" href="/">{img("brand/two-stooges-logo.webp", "Two Stooges Sports Bar & Grill, Fridley MN – home", eager=True, srcset=False)}</a>
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
    updated = dt.date.fromisoformat(TODAY).strftime("%B %-d, %Y")
    return f'''<footer class="site-footer on-dark">
  {rail()}
  <div class="wrap">
    <div class="footer-grid" style="padding-top:3rem">
      <div class="footer-brand">
        {img("brand/two-stooges-logo.webp", "Two Stooges Sports Bar & Grill", srcset=False)}
        <p>{e(BIZ["name"])} has been Fridley's home for pool, darts, cold beer and game day since 1988.</p>
      </div>
      <div>
        <p class="footer-title">Visit</p>
        <address>
        <ul>
          <li><a href="{DIRECTIONS}" target="_blank" rel="noopener">{e(BIZ["street"])}<br>{e(BIZ["city"])}, {e(BIZ["region"])} {e(BIZ["zip"])}</a></li>
          <li><a href="tel:{BIZ["tel"]}">{e(BIZ["phone"])}</a></li>
          <li><a href="mailto:{BIZ["email"]}">{e(BIZ["email"])}</a></li>
        </ul>
        </address>
        <p class="footer-title" style="margin-top:1.5rem">Find us online</p>
        <ul class="footer-social">
          <li><a href="{SG.SAME_AS[1]}" target="_blank" rel="noopener">Instagram</a></li>
          <li><a href="{SG.GBP_URL}" target="_blank" rel="noopener">Google</a></li>
          <li><a href="{SG.SAME_AS[2]}" target="_blank" rel="noopener">Yelp</a></li>
          <li><a href="{SG.SAME_AS[3]}" target="_blank" rel="noopener">Tripadvisor</a></li>
          <li><a href="{SG.SAME_AS[4]}" target="_blank" rel="noopener">Apple Maps</a></li>
        </ul>
      </div>
      <div>
        <p class="footer-title">Hours</p>
        <div class="footer-hours"><span>Monday – Sunday</span><strong style="color:var(--text)">11 AM – 12 AM</strong><span class="small" style="margin-top:.5rem">Happy hour Mon–Thu 2–6 PM<br>Fri–Sun 11 AM–7 PM</span></div>
      </div>
      <div>
        <p class="footer-title">Explore</p>
        <ul>
          <li><a href="/menu/">Menu</a></li>
          <li><a href="/specials/">Specials &amp; Happy Hour</a></li>
          <li><a href="/billiards/">Billiards</a></li>
          <li><a href="/darts/">Darts</a></li>
          <li><a href="/leagues/">Leagues &amp; Tournaments</a></li>
          <li><a href="/league-signup/">League Sign-Up</a></li>
          <li><a href="/events/">Events</a></li>
          <li><a href="/private-parties/">Private Parties</a></li>
        </ul>
      </div>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>© <span data-year>2026</span> {e(BIZ["name"])}, Fridley, Minnesota. Information updated {updated}.</span>
    <span><a href="/about/">About</a> · <a href="/gallery/">Gallery</a> · <a href="/contact/">Contact</a> · <a href="/faq/">FAQ</a> · <a href="/privacy-policy/">Privacy Policy</a> · Website by Multimedia Graphics</span>
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


AWARDS_VISIBLE = AWARDS
AMENITIES = ["43 pool tables", "6 dart boards", "2 patios", "Pool leagues", "30 HD TVs and 4 monster screens", "NFL Sunday Ticket",
             "16 beers on tap", "Pro shop and cue repair", "Private event space"]
PAGE_TYPES = {"contact": "ContactPage", "about": "AboutPage", "gallery": "CollectionPage"}
SERVICE_PAGES = {"billiards": "billiards", "darts": "darts", "leagues": "leagues", "parties": "parties"}


def biz_extras(key):
    """Enrichment properties only on pages where the fact is visible (Rule 3)."""
    x = {}
    if key in ("home", "about"):
        x["award"] = AWARDS_VISIBLE
        x["amenityFeature"] = [{"@type": "LocationFeatureSpecification", "name": a, "value": True} for a in AMENITIES]
    if key == "home":
        x["slogan"] = "The most fun you can have under one roof"
        x["description"] = ENTITY_DESC
    if key in ("home", "menu"):
        x["servesCuisine"] = "American"
    return x


def first_lead(body):
    m = re.search(r'<p class="lead">(.*?)</p>', body, re.S)
    return SG.strip(m.group(1)) if m else ""


BILLIARDS_OFFERS = [{"@type": "Offer", "name": f"Daily pool special – {n}", "price": p, "priceCurrency": "USD",
                     "description": "Table time, 11 AM–5 PM daily, plus tax"} for n, p in (("regular", "11"), ("seniors", "10"), ("premier table", "12"))]


def build_graph(key, body, title, desc, og_url, og_alt, extra_nodes, main_entity):
    path, crumb = META[key][0], META[key][5]
    svc_key = SERVICE_PAGES.get(key)
    if svc_key and not main_entity:
        main_entity = SG.SERVICES[svc_key]["@id"]
    if key in ("home", "about") and not main_entity:
        main_entity = SG.BID
    biz = dict(BIZ, directions=DIRECTIONS)
    nodes = [SG.website_node(BIZ["name"]),
             SG.business_node(biz, key, biz_extras(key)),
             SG.webpage_node(path, title, desc, og_url, og_alt, PAGE_TYPES.get(key, "WebPage"), crumb, main_entity, TODAY)]
    if crumb:
        nodes.append(SG.breadcrumb_node(path, crumb))
    for k in SG.SERVICES:
        if k == svc_key:
            nodes.append(SG.service_node(k, "full", first_lead(body), RELATED.get(key, []),
                                         BILLIARDS_OFFERS if k == "billiards" else None, SITE + path + "#webpage"))
        elif key == "home":
            nodes.append(SG.service_node(k, "card"))
        else:
            nodes.append(SG.service_node(k, "nav"))
    nodes += [{k: v for k, v in n.items() if k != "@context"} for n in (extra_nodes or [])]
    g = SG.graph(nodes)
    errs = SG.check_graph(g, path)
    if errs:
        raise SystemExit("Schema check failed:\n  " + "\n  ".join(errs))
    return g


def page(key, body, extra_ld=None, og_type="website", main_entity=None):
    path, title, desc, og_src, og_alt, crumb = META[key]
    assert len(title) <= 60, f"title too long ({len(title)}): {title}"
    assert 150 <= len(desc) <= 160, f"description length {len(desc)}: {key}"
    canonical = SITE + path
    og_file = make_og(key, og_src).name
    og_url = f"{SITE}/assets/img/og/{og_file}"
    robots = "index, follow, max-image-preview:large" if LAUNCH else "noindex, nofollow"
    g = build_graph(key, body, title, desc, og_url, og_alt, extra_ld, main_entity)
    GRAPHS[path] = g
    ld_html = f'<script type="application/ld+json">{json.dumps(g, ensure_ascii=False, separators=(",", ":"))}</script>'
    biz_og = ""
    if og_type == "business.business":
        biz_og = f'''
<meta property="business:contact_data:street_address" content="{e(BIZ["street"])}">
<meta property="business:contact_data:locality" content="{e(BIZ["city"])}">
<meta property="business:contact_data:region" content="{e(BIZ["region"])}">
<meta property="business:contact_data:postal_code" content="{e(BIZ["zip"])}">
<meta property="business:contact_data:country_name" content="United States">
<meta property="business:contact_data:phone_number" content="{e(BIZ["phone"])}">
<meta property="business:contact_data:email" content="{e(BIZ["email"])}">
<meta property="place:location:latitude" content="{BIZ["lat"]}">
<meta property="place:location:longitude" content="{BIZ["lng"]}">'''
    return f'''<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta name="geo.region" content="US-MN">
<meta name="geo.placename" content="Fridley">
<meta name="geo.position" content="{BIZ["lat"]};{BIZ["lng"]}">
<meta name="ICBM" content="{BIZ["lat"]}, {BIZ["lng"]}">
<meta name="theme-color" content="#000000">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="{e(BIZ["name"])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_url}">
<meta property="og:image:secure_url" content="{og_url}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(og_alt)}">{biz_og}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og_url}">
<meta name="twitter:image:alt" content="{e(og_alt)}">
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
{related(key)}
</main>
{footer()}
<script src="/assets/js/site.js?v={ASSET_VER}" defer></script>
</body>
</html>
'''


def page_hero(key, eyebrow, title, lead, image, alt, actions=""):
    crumb = META[key][5]
    return f'''<section class="page-hero on-dark">
  <div class="page-hero__media">{img(image, alt, eager=True)}</div>
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">{e(crumb)}</li></ol></nav>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{title}</h1>
    <p class="lead">{lead}</p>
    {f'<div class="btn-row">{actions}</div>' if actions else ""}
  </div>
</section>
{rail()}'''


def cta_band(title, text, actions):
    return f'''<section class="section section--tight"><div class="wrap"><div class="cta-band on-dark">
  <div><h2>{title}</h2><p>{text}</p></div>
  <div class="btn-row">{actions}</div>
</div></div></section>'''


def visit_section(title="Visit Two Stooges Sports Bar in Fridley, MN"):
    return f'''<section class="section section--alt" id="visit"><div class="wrap">
  {section_head("Find us", title, f"We're on University Avenue NE (Highway 47) in Fridley, just north of Minneapolis, serving guests within about 30 miles, from Columbia Heights and Spring Lake Park to New Brighton, Coon Rapids, Blaine and the rest of the north metro. Walk-ins are always welcome. Planning ahead? {L('/private-parties/', 'Reserve space for a group')}.")}
  <div class="visit">
    <div class="visit__info">
      <div class="info-row"><span class="tile__icon">{icon("pin")}</span><div><h3>Address</h3><p><a href="{DIRECTIONS}" target="_blank" rel="noopener">{e(BIZ["street"])}<br>{e(BIZ["city"])}, {e(BIZ["region"])} {e(BIZ["zip"])}</a></p></div></div>
      <div class="info-row"><span class="tile__icon">{icon("clock")}</span><div><h3>Hours</h3><p>Open every day, 11 AM – 12 AM</p></div></div>
      <div class="info-row"><span class="tile__icon">{icon("phone")}</span><div><h3>Phone</h3><p><a href="tel:{BIZ["tel"]}">{e(BIZ["phone"])}</a></p></div></div>
      <div class="info-row"><span class="tile__icon">{icon("mail")}</span><div><h3>Email</h3><p><a href="mailto:{BIZ["email"]}">{e(BIZ["email"])}</a></p></div></div>
      <div class="btn-row mt-1">{btn("Get Directions", DIRECTIONS, "gold", "nav", ' target="_blank" rel="noopener"')}{btn("Call Two Stooges", "tel:" + BIZ["tel"], "outline", "phone")}</div>
    </div>
    <div class="map"><iframe src="{MAP_EMBED}" title="Map to Two Stooges Sports Bar &amp; Grill, 7178 University Ave NE, Fridley MN" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
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
    return f'''<article class="event event--feature" id="{ev["id"]}" data-event-end="{ev["end"]}" data-past-card="past-{ev["id"]}">
  <button class="event__flyer" type="button" data-lightbox="{big}" data-alt="{e(ev["flyer_alt"])}" data-caption="{e(ev["title"])} · {e(ev["date"])}" aria-label="View full flyer: {e(ev["title"])}">
    {img(ev["flyer"], ev["flyer_alt"], srcset=False)}
  </button>
  <div>
    <div class="event__date"><span>{e(ev["dow"])}</span><span>{e(ev["date"])}</span></div>
    <h3>{e(ev["title"])}</h3>
    <p class="muted">{e(ev["intro"])} New to FargoRate? Our {L("/leagues/", "weekly pool leagues")} are a great way to build your rating.</p>
    <div class="event__facts">{facts}</div>
    <p class="event__note">{e(ev["note"])}</p>
    <div class="event__contact">
      {btn(f"{who}: {num}", "tel:" + tel, "gold", "phone")}
      <a class="text-link" href="/contact/">Directions to Two Stooges</a>
    </div>
  </div>
</article>
<template id="past-{ev["id"]}">{past_card(ev)}</template>'''


def past_card(ev):
    big = f"/assets/img/{ev['flyer']}"
    return f'''<article class="past-card">
  <button type="button" data-lightbox="{big}" data-alt="{e(ev["flyer_alt"])}" data-caption="{e(ev["title"])} · {e(ev["date"])}" aria-label="View flyer: {e(ev["title"])}">{img(ev["flyer"], ev["flyer_alt"], srcset=False)}</button>
  <div><span class="chip">Past event</span><h3>{e(ev["title"])}</h3><p>{e(ev["dow"])} · {e(ev["date"])}</p></div>
</article>'''


def event_ld(ev):
    d = {
        "@type": "Event", "@id": SITE + "/events/#" + ev["id"], "name": ev["title"],
        "startDate": ev["start_iso"], "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "description": ev["intro"], "image": [SITE + "/assets/img/" + ev["flyer"]],
        "url": SITE + "/events/#" + ev["id"],
        "location": {"@id": SG.BID}, "organizer": {"@id": SG.BID},
    }
    if ev.get("door_iso"):
        d["doorTime"] = ev["door_iso"]
    if ev.get("price"):
        d["offers"] = {"@type": "Offer", "price": ev["price"], "priceCurrency": "USD", "url": SITE + "/events/#" + ev["id"],
                       "availability": "https://schema.org/LimitedAvailability", "validFrom": TODAY}
    return d


LEAGUE_SCHEDULE = {
    "Straight Pool League": {"slug": "straight-pool-league", "day": "Tuesday", "start": "2026-09-08", "concept": "straight",
                             "desc": "Weekly straight pool league on Tuesdays at 11 AM. BCA rules, 3 races to 50 points."},
    "10-Ball League": {"slug": "10-ball-league", "day": "Thursday", "start": None, "concept": "tenball",
                       "desc": "Weekly 10-ball league on Thursdays at 11 AM. 3 sets, race to 5, no 10-ball on the break, 3-foul rule, on 9 ft Gabriel's tables."},
}


def league_event_nodes():
    out = []
    for L_ in LEAGUES:
        m = LEAGUE_SCHEDULE[L_["name"]]
        sched = {"@type": "Schedule", "byDay": "https://schema.org/" + m["day"], "startTime": "11:00",
                 "repeatFrequency": "P1W", "scheduleTimezone": "America/Chicago"}
        n = {"@type": "Event", "@id": SITE + "/events/#" + m["slug"], "name": f'{L_["name"]} at Two Stooges',
             "description": m["desc"], "image": [SITE + "/assets/img/" + L_["flyer"]], "url": SITE + "/events/#weekly",
             "eventSchedule": sched, "eventStatus": "https://schema.org/EventScheduled",
             "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
             "location": {"@id": SG.BID}, "organizer": {"@id": SG.BID}, "about": SG.thing(m["concept"])}
        if m["start"]:
            sched["startDate"] = m["start"]
            n["startDate"] = m["start"] + "T11:00:00-05:00"
        out.append(n)
    return out


def faq_ld():
    return {"@type": "FAQPage", "@id": SITE + "/#faq", "isPartOf": {"@id": SITE + "/#webpage"}, "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain}} for q, _, plain in FAQ]}


def tag_chips(tags):
    m = {"new": '<span class="chip chip--orange">New</span>', "signature": '<span class="chip chip--gold">Signature</span>',
         "raw": '<span class="advisory-mark" aria-hidden="true">*</span><span class="visually-hidden">(cooked to order, see consumer advisory)</span>'}
    return "".join(m[t] for t in tags)


def menu_ld():
    def price(p):
        return p.split(" / ")[0]
    return {"@type": "Menu", "@id": SITE + "/menu/#menu", "name": "Two Stooges Sports Bar & Grill Menu",
            "url": SITE + "/menu/", "inLanguage": "en-US", "mainEntityOfPage": {"@id": SITE + "/menu/#webpage"},
            "hasMenuSection": [{"@type": "MenuSection", "name": sec["name"], "url": SITE + "/menu/#" + sec["id"],
                                "hasMenuItem": [{"@type": "MenuItem", "name": n, "description": html.unescape(d),
                                                 "offers": {"@type": "Offer", "price": price(p), "priceCurrency": "USD"}}
                                                for n, p, d, _ in sec["items"]]} for sec in MENU if sec["items"]]}


def p_home():
    ups = upcoming_events()
    nxt = min(ups, key=lambda x: x["end"]) if ups else None
    next_card = ""
    if nxt:
        next_card = f'''<aside class="next-up" data-next-up="{nxt["end"]}" aria-label="Next event at Two Stooges">
        <div class="next-up__label">{icon("calendar")}Next up · {e(nxt["short_date"])}</div>
        <div class="next-up__body">
          {img(nxt["flyer"], nxt["flyer_alt"], srcset=False)}
          <div>
            <p class="next-up__title">{e(nxt["title"])}</p>
            <p>{e(nxt["facts"][0][1])} · {e(nxt["facts"][3][1])} · starts {e(nxt["facts"][5][1])}</p>
            <a class="text-link" href="/events/#{nxt["id"]}">Tournament details</a>
          </div>
        </div>
      </aside>'''

    pillars = [
        ("photos/home-card-billiards-rack", "A racked set of pool balls on blue felt at Two Stooges in Fridley", "43 tables", "Billiards", "/billiards/",
         f"Gabriel's and Diamond tables in 9 ft and 7 ft, {L('/specials/#pool', 'daily pool specials')} and a full Pro Shop.", "Explore the billiard room"),
        ("photos/home-card-darts-bullseye", "A blue-flighted dart in the bullseye of a dartboard, with warm bar lights behind", "Leagues every day", "Darts", "/darts/",
         f"Electronic dart boards, high-tops and {L('/leagues/', 'dart leagues')} for every skill level.", "See the dart area"),
        ("photos/home-card-leagues-cues", "Two polished pool cues resting beside a rack of billiard balls", "Weekly play", "Leagues & Tournaments", "/leagues/",
         f"Straight pool, 10-ball, APA and UPL leagues, plus {L('/events/', 'FargoRate tournaments')}.", "Join a pool league"),
        ("photos/home-card-private-parties", "A group of friends cheering as one of them lines up a shot at the pool table", "Groups welcome", "Private Parties", "/private-parties/",
         f"Birthdays, office parties and banquets with {L('/menu/', 'custom menus')} and pool tables included.", "Plan a private party"),
    ]
    cards = "".join(f'''<article class="card card--link">
      <div class="card__media">{img(i, a, sizes="(max-width:640px) 100vw, (max-width:1000px) 50vw, 25vw")}</div>
      <div class="card__body"><span class="card__kicker">{k}</span><h3>{t}</h3><p>{d}</p><a class="text-link" href="{h}">{l}</a></div>
    </article>''' for i, a, k, t, h, d, l in pillars)

    spec_html = "".join(deal_card(r) for r in DAY_DEALS if r[0] in (1, 2, 3, 0))

    picks = [("Big Stooge", "19", "Two black Angus patties, three cheeses, four strips of bacon, onion strings, A-1, honey BBQ and garlic basil aioli.", ["raw", "signature"]),
             ("Duck Bacon Wontons", "16", "Crispy wontons with spicy plum sauce.", []),
             ("8 Bone-In Wings", "15", "Fresh, never frozen. Try them in our Signature Sauce.", ["signature"]),
             ("Walleye Sandwich", "19", "Battered walleye, lettuce, American cheese and tartar on a toasted hoagie.", ["signature"])]
    picks_html = "".join(f'''<li class="menu-item"><h3>{e(n)} {tag_chips(t)}</h3><span class="menu-item__price">${p}</span><p>{e(d)}</p></li>''' for n, p, d, t in picks)

    quotes = "".join(f'''<figure class="quote"><div class="quote__stars" role="img" aria-label="{r} out of 5 stars">{"★" * r}{"☆" * (5 - r)}</div><blockquote>{e(q)}</blockquote><figcaption><span class="quote__avatar">{e(n[0])}</span><span>{e(n)}<small>Google review</small></span></figcaption></figure>''' for q, n, r in REVIEWS)
    faqs = "".join(f'<details class="faq"><summary><h3>{e(q)}</h3></summary><p>{a}</p></details>' for q, a, _ in FAQ)

    body = f'''<section class="hero hero--full on-dark">
  <picture class="hero__bg">
    <source media="(max-width: 700px)" srcset="/assets/img/photos/hero-pool-tables-mobile.webp" width="800" height="1000">
    <img src="/assets/img/photos/hero-pool-tables-1536.webp" srcset="/assets/img/photos/hero-pool-tables-1280.webp 1280w, /assets/img/photos/hero-pool-tables-1536.webp 1536w" sizes="100vw" width="1536" height="640" alt="The Two Stooges billiard room in Fridley, MN: rows of blue-felt Gabriel's pool tables under wood-trimmed lights, with the bar behind" fetchpriority="high">
  </picture>
  <div class="wrap hero__inner">
    <div class="hero__copy">
      <span class="hero__badge">{icon("pin")}Fridley, MN · Since 1988</span>
      <h1>Two Stooges Sports Bar &amp; Grill in <span class="grad-text">Fridley, MN</span></h1>
      <p class="lead">The most fun you can have under one roof: 43 pool tables, dart boards, 34 TV screens, 16 ice-cold taps and a full bar &amp; grill.</p>
      <div class="btn-row">{btn("Upcoming Events", "/events/", "gold", "calendar")}{btn("See the Menu", "/menu/", "outline")}</div>
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
<section class="badge-strip" aria-label="Two Stooges highlights"><div class="wrap">
  <ul class="badges">
    <li><a href="/leagues/">{icon("trophy")}<span>Pool Leagues</span></a></li>
    <li><span class="badge-static">{icon("sun")}<span>2 Patios</span></span></li>
    <li><a href="/billiards/">{icon("ball")}<span>43 Pool Tables</span></a></li>
    <li><a href="/darts/">{icon("target")}<span>6 Dart Boards</span></a></li>
  </ul>
</div></section>

<section class="section"><div class="wrap">
  {section_head("Pick your game", "Pool, darts &amp; more at Two Stooges", f"Two Stooges is Fridley's all-in-one sports bar, restaurant and {L('/billiards/', 'billiard room')}. Come for one game and stay for all of them.", center=True)}
  <div class="grid grid--4">{cards}</div>
</div></section>

<section class="section section--photo section--specials on-dark">
  <div class="section__bg">{img("photos/friends-at-the-bar", "Friends sharing beers at the bar", sizes="100vw")}</div>
  <div class="wrap">
  <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:end;gap:1rem;margin-bottom:2rem">
    <div class="section-head" style="margin:0"><span class="eyebrow">Nightly traditions</span><h2 class="mb-0">Daily specials at Two Stooges</h2></div>
    <p class="muted" style="max-width:420px;margin:0">Happy hour runs Mon–Thu 2–6 PM and Fri–Sun 11 AM–7 PM, and there's a food deal almost every day. {L("/specials/", "See every special")}.</p>
  </div>
  <div class="deal-grid on-light">{spec_html}</div>
</div></section>

<section class="section"><div class="wrap">
  <div class="split">
    <div class="split__media">
      {img("photos/burger-and-fries", "A Two Stooges double bacon cheeseburger stacked with onion strings, served in a basket with seasoned fries and pickles", sizes="(max-width:860px) 100vw, 50vw")}
      <div class="split__badge">Bar &amp; grill<small>Open daily 11 AM – midnight</small></div>
    </div>
    <div>
      <span class="eyebrow">From the kitchen</span>
      <h2>Burgers, wings &amp; <span class="grad-text">bar favorites</span></h2>
      <p class="lead">Classic American bar food with our own twist, plus 16 beers poured ice-cold from our iced cobra taps.</p>
      <ul class="menu-items" style="grid-template-columns:1fr;list-style:none;padding:0;margin:0 0 1.5rem">{picks_html}</ul>
      <p class="small muted" style="margin:-.75rem 0 1.5rem"><span class="advisory-mark" aria-hidden="true">*</span> Cooked to order. {ADVISORY}</p>
      <div class="btn-row">{btn("View the Full Menu", "/menu/", "green")}{btn("Today's Specials", "/specials/", "outline")}</div>
    </div>
  </div>
</div></section>

<section class="section section--photo section--leagues on-dark">
  <div class="section__bg">{img("photos/pool-rack-blue-felt", "A full rack of pool balls on blue felt with a player lining up the break at Two Stooges", sizes="100vw")}</div>
  <div class="wrap">
  <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:end;gap:1rem;margin-bottom:2rem">
    <div><span class="eyebrow">Every week</span><h2 class="mb-0">Pool &amp; dart league nights in Fridley</h2></div>
    <a class="text-link" href="/leagues/">League details &amp; sign-up</a>
  </div>
  <div class="grid grid--4">
    <div class="deal-tile deal-tile--hot"><div class="schedule__day">Tuesday · 11 AM</div><h3>Straight Pool League</h3></div>
    <div class="deal-tile"><div class="schedule__day">Thursday · 11 AM</div><h3>10-Ball League</h3></div>
    <div class="deal-tile"><div class="schedule__day">Every day</div><h3>Dart Leagues</h3></div>
    <div class="deal-tile"><div class="schedule__day">Daily · 11 AM–5 PM</div><h3>Pool Specials</h3></div>
  </div>
  <div class="league-cta">
    <p><strong>Want in?</strong> Leagues are handicapped, so every skill level can compete. Solo players welcome.</p>
    <div class="btn-row">{btn("Sign Up for a League", "/league-signup/", "gold", "trophy")}{btn("See All Leagues", "/leagues/", "outline")}</div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="split split--rev">
    <div class="split__media">
      {img("photos/billiard-room-diamond-tables", "The wide-open Two Stooges billiard room in Fridley: rows of blue-felt Diamond pool tables under wood-trimmed lights, with players at the tables", sizes="(max-width:860px) 100vw, 50vw")}
      <div class="split__badge">Since 1988<small>Locally owned in Fridley</small></div>
    </div>
    <div>
      <span class="eyebrow">Award-winning billiards</span>
      <h2>A top ten billiard room in <span class="grad-text">North America</span></h2>
      <p class="lead">University Billiards opened in 1988 with 17 tables. Today Two Stooges has 43 tables, a full sports bar with NFL Sunday Ticket on 34 screens, and City Pages named it the best place to shoot pool in 2017.</p>
      <ul class="check-list check-list--2col"><li>NFL Sunday Ticket</li><li>30 HD TVs + 4 big screens</li><li>Elevated center bar</li><li>Pro Shop &amp; cue repair</li></ul>
      <a class="text-link" href="/about/">Read the Two Stooges story</a>
    </div>
  </div>
</div></section>

<section class="section section--alt"><div class="wrap">
  {section_head("Guest reviews", "What guests say about Two Stooges", "Real reviews from Google, shared with first names only.", center=True)}
  <div class="grid grid--2">{quotes}</div>
  <div class="btn-row mt-2" style="justify-content:center">{btn("Read More Reviews on Google", SG.GBP_URL, "green", None, ' target="_blank" rel="noopener"')}{btn("Yelp", SG.SAME_AS[2], "outline", None, ' target="_blank" rel="noopener"')}{btn("Tripadvisor", SG.SAME_AS[3], "outline", None, ' target="_blank" rel="noopener"')}</div>
</div></section>

<section class="section section--tight"><div class="wrap">
  <div class="cta-band on-dark">
    <div><span class="eyebrow">Private parties</span><h2>Celebrate at Two Stooges</h2><p>Birthdays, office parties, draft parties and banquets, with custom menus, pool tables and darts for your group. Questions first? Check the {L("/faq/", "Two Stooges FAQ")}.</p></div>
    <div class="btn-row">{btn("Plan a Party", "/private-parties/", "gold")}{btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone")}</div>
  </div>
</div></section>
'''
    return page("home", body, extra_ld=([event_ld(nxt)] if nxt else []), og_type="business.business")


def p_menu():
    tabs = "".join(f'<button class="menu-tab" type="button" role="tab" id="tab-{s["id"]}" aria-controls="{s["id"]}" aria-selected="{"true" if i == 0 else "false"}"{"" if i == 0 else " tabindex=\"-1\""}>{e(s["name"])}</button>' for i, s in enumerate(MENU))
    panels = []
    for i, s in enumerate(MENU):
        items = "".join(f'''<li class="menu-item"><h3>{e(n)} {tag_chips(t)}</h3><span class="menu-item__price">${e(p)}</span><p>{d}</p></li>''' for n, p, d, t in s["items"])
        notes = "".join(f'<p class="menu-note">{n}</p>' for n in s["notes"])
        feature = ""
        if s.get("feature"):
            k, t = s["feature"]
            feature = f'<aside class="menu-feature" aria-label="{e(t)}"><span class="menu-feature__icon" aria-hidden="true">{icon("fork")}</span><p><span class="menu-feature__kicker">{e(k)}</span><strong>{e(t)}</strong></p></aside>'
        legend = (advisory_legend(any("signature" in it[3] for it in s["items"])) if s.get("advisory") else "")
        byo = byo_card(**s["byo"]) if s.get("byo") else ""
        toppings = ""
        if s.get("toppings"):
            toppings = ('<div class="menu-toppings"><h3>Toppings</h3><ul>'
                        + "".join(f"<li>{e(t)}</li>" for t in s["toppings"]) + "</ul></div>")
        sizes = ""
        if s.get("sizes"):
            label, tiles = s["sizes"]
            sizes = (f'<div class="menu-sizes"><h3 class="menu-sizes__label">{e(label)}</h3><ul class="menu-sizes__list">'
                     + "".join(f'<li class="menu-size"><span class="menu-size__name">{e(n)}</span><span class="menu-size__inch">{e(inch)}</span>'
                               f'<span class="menu-size__price"><sup>$</sup>{e(pr)}</span></li>' for n, inch, pr in tiles)
                     + "</ul></div>")
        panels.append(f'''<section class="menu-panel" id="{s["id"]}" role="tabpanel" aria-labelledby="tab-{s["id"]}" data-menu-panel>
    <div class="menu-panel__head"><h2>{e(s["name"])}</h2><p>{e(s["note_top"])}</p></div>
    {sizes}
    {toppings}
    {feature}
    {f'<ul class="menu-items" style="list-style:none;padding:0;margin:0">{items}</ul>' if items else ""}
    {byo}
    {notes}
    {legend}
  </section>''')
    body = f'''{page_hero("menu", "Eat &amp; drink", "The Two Stooges Sports Bar <span class='grad-text'>menu</span>",
        f"Classic American bar and grill food with our own twist, served in Fridley every day from 11 AM. There are burgers, wings, pizza, sandwiches and entrées, plus 16 beers on tap. Check the {L('/specials/', 'daily specials')} before you order.",
        "photos/tenders-and-beer", "Crispy chicken tenders and fries next to an ice-cold pint of beer on a wood table", btn("Today's Specials", "/specials/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  <div class="menu-tabs" role="tablist" aria-label="Menu categories">{tabs}</div>
  {"".join(panels)}
  <p class="small muted mt-2">{e(MENU_DISCLAIMER)} Planning a group meal? We put together {L("/private-parties/", "custom party menus")}.</p>
</div></section>
<section class="section section--tight food-photos"><div class="wrap">
  {section_head("From the kitchen", "Fresh off the Two Stooges grill", f"A look at what's coming out of the kitchen. Find your favorites on the menu above, and check the {L('/specials/', 'daily specials')} for deals.")}
  <div class="food-grid">
    {"".join(f'<figure class="gallery__item food-grid__item"><button type="button" data-lightbox="/assets/img/{p_}.webp" data-alt="{e(a_)}" data-caption="" aria-label="Enlarge photo: {e(a_)}">{img(p_, a_, sizes="(max-width:640px) 50vw, 33vw")}</button></figure>' for p_, a_ in [
        ("photos/food-bacon-burger-onion-straws", "A bacon burger with onion straws and greens on a toasted bun, with fries and a pickle"),
        ("photos/food-wings-two-sauces", "Bone-in wings in two sauces with celery"),
        ("photos/food-club-sandwich", "A stacked club sandwich with kettle chips"),
        ("photos/food-tater-tots-window", "A pile of crispy tater tots"),
        ("photos/food-onion-rings", "Golden battered onion rings"),
        ("photos/food-thin-crust-pizza", "Thin-crust pizza with sausage, mushrooms and red onion"),
        ("photos/food-steak-bites-onion-rings", "Seared steak bites topped with onion rings")])}
  </div>
</div></section>
<section class="section section--alt"><div class="wrap">
  <div class="split">
    <div>
      <span class="eyebrow">At the bar</span>
      <h2>16 beers on tap, <span class="grad-text">ice-cold</span></h2>
      <p class="lead">Every beer is poured through our iced cobra taps. Pair it with an original cocktail, or catch {L("/specials/", "happy hour prices")} on domestics and rails.</p>
      <h3>Happy hour drink prices</h3>
      <ul class="price-list">
        <li><span>Domestic bottles &amp; pints</span><span class="price">$3.50</span></li>
        <li><span>Domestic 22 oz</span><span class="price">$4.25</span></li>
        <li><span>Rail drinks</span><span class="price">$4.00</span></li>
      </ul>
      <p class="small muted mt-1">Happy hour: Mon–Thu 2–6 PM · Fri–Sun 11 AM–7 PM.</p>
    </div>
    <div class="split__media">{img("photos/beer-taps", "A row of draft beer tap handles at the Two Stooges bar, including Grain Belt, Coors Light, Blue Moon, Samuel Adams, Budweiser and Michelob Golden Light", sizes="(max-width:860px) 100vw, 50vw")}</div>
  </div>
</div></section>
{cta_band("Feeding a crowd in Fridley?", "We put together custom menus for birthdays, office parties and banquets.", btn("Plan a Private Party", "/private-parties/", "gold"))}'''
    return page("menu", body, extra_ld=[menu_ld()], main_entity=SITE + "/menu/#menu")


def deal_card(row):
    wd, day, short, theme, price, item, note, when, extras, hh = row
    ex = "".join(f'<li><span>{e(t)}</span>{e(w)}</li>' for t, w in extras)
    return f'''<article class="deal-card{" deal-card--sun" if wd == 0 else ""}" data-weekday="{wd}">
      <header class="deal-card__head"><span class="deal-card__day">{e(day)}</span><span class="today-badge">Today</span></header>
      <div class="deal-card__body">
        <p class="deal-card__theme">{e(theme)}</p>
        <p class="deal-card__price">{e(price)} <span>{e(item)}</span></p>
        <p class="deal-card__note">{e(note)} · <strong>{e(when)}</strong></p>
        {f'<ul class="deal-card__extras">{ex}</ul>' if ex else ""}
      </div>
      <footer class="deal-card__hh">{icon("mug")}Happy hour drinks {e(hh)}</footer>
    </article>'''


def p_specials():
    days = [deal_card(row) for row in DAY_DEALS]
    drinks = "".join(f'<div class="hh-price"><span class="hh-price__num">{e(p_)}</span><span class="hh-price__lbl">{e(l_)}</span></div>' for p_, l_ in HH_DRINKS)
    body = f'''{page_hero("specials", "Daily deals", "Two Stooges Sports Bar <span class='grad-text'>specials &amp; happy hour</span>",
        f"There's a deal every day at Two Stooges in Fridley, and today's specials are highlighted below. Browse the {L('/menu/', 'full bar and grill menu')} or grab a table with our {L('#pool', 'daily pool specials')}.",
        "photos/beers-on-bar", "Three ice-cold pints of beer lined up on the bar", btn("Today's Deal", "#week", "gold") + btn("Pool Specials", "#pool", "outline"))}
<section class="section section--felt on-dark hh-band"><div class="wrap">
  <div class="hh">
    <div class="hh__intro">
      <span class="eyebrow">Happy hour</span>
      <h2>Happy hour at <span class="grad-text">Two Stooges</span></h2>
      <div class="hh__times">
        <div><span class="hh__days">Mon–Thu</span><span class="hh__hours">2–6 PM</span></div>
        <div><span class="hh__days">Fri–Sun</span><span class="hh__hours">11 AM–7 PM</span></div>
      </div>
      <p class="muted">Plus $2 off appetizers (excluding wings) Mon–Thu 2–5 PM and Friday 11 AM–7 PM.</p>
    </div>
    <div class="hh__prices">{drinks}</div>
  </div>
</div></section>
<section class="section" id="week"><div class="wrap">
  {section_head("This week", "Daily food &amp; drink specials in Fridley", "A different deal every day. Today's card is highlighted.")}
  <div class="deal-grid">{"".join(days)}
    <a class="deal-card deal-card--pool" href="#pool">
      <header class="deal-card__head"><span class="deal-card__day">Every day</span></header>
      <div class="deal-card__body">
        <p class="deal-card__theme">Pool specials</p>
        <p class="deal-card__price">$11 <span>table time</span></p>
        <p class="deal-card__note">Seniors $10 · Premier $12 · <strong>11 AM–5 PM</strong></p>
      </div>
      <footer class="deal-card__hh">{icon("ball")}See pool specials →</footer>
    </a>
  </div>
  <p class="small muted mt-2">Prices don't include tax. Specials are dine-in only and can't be combined with other offers. Prices and times can change, so ask your server for today's deals.</p>
</div></section>
<section class="section section--photo on-dark pool-band" id="pool">
  <div class="section__bg">{img("photos/friends-pool-beers", "Friends with beers laughing around a pool table as one lines up a shot", sizes="100vw")}</div>
  <div class="wrap">
    <div class="pool-band__inner">
      <div class="pool-band__copy">
        <span class="eyebrow">Daily pool specials</span>
        <h2>Pool specials, <span class="grad-text">11 AM–5 PM daily</span></h2>
        <p class="lead">Discounted table time every day from 11 AM to 5 PM on our {L("/billiards/", "43 Gabriel's and Diamond tables")}. Grab a table and balls at the billiard counter and pay when you're done.</p>
        <div class="btn-row">{btn("About Our Tables", "/billiards/", "gold", "ball")}{btn("Join a Pool League", "/league-signup/", "outline")}</div>
      </div>
      <!-- TODO(client): confirm pool special pricing (old site listed $11/$10/$12 on Billiards but $12/$11 on Specials). -->
      <div class="pool-prices">
        <div class="pool-price"><span class="pool-price__lbl">Regular</span><span class="pool-price__num">$11</span></div>
        <div class="pool-price"><span class="pool-price__lbl">Seniors</span><span class="pool-price__num">$10</span></div>
        <div class="pool-price pool-price--hot"><span class="pool-price__lbl">Premier table</span><span class="pool-price__num">$12</span></div>
        <p class="pool-prices__note">Plus tax · every day 11 AM–5 PM</p>
      </div>
    </div>
  </div>
</section>
{cta_band("Celebrating a birthday?", "Bring the crew. We'll set you up with tables, food and drinks for your group.", btn("Book a Party", "/private-parties/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}'''
    return page("specials", body)


def p_billiards():
    gallery = [("photos/billiard-hall-tables", "Rows of tables in the Two Stooges billiard hall"), ("photos/player-racking", "A player racking balls at a Two Stooges pool table"),
               ("photos/tournament-table-trophies", "Tournament table with trophies above"), ("photos/pool-balls-rack", "A fresh rack of pool balls on blue felt")]
    g = "".join(f'<figure class="gallery__item"><button type="button" data-lightbox="/assets/img/{p}.webp" data-alt="{e(a)}" data-caption="{e(a)}" aria-label="Enlarge photo: {e(a)}">{img(p, a, sizes="(max-width:640px) 100vw, 33vw")}</button></figure>' for p, a in gallery)
    body = f'''{page_hero("billiards", "43 tables · since 1988", "Billiards at Two Stooges Sports Bar in <span class='grad-text'>Fridley</span>",
        "Two Stooges has been named a top ten billiard room in North America, and City Pages voted it the best place to shoot pool. There are 43 Gabriel's and Diamond tables in 9 ft and 7 ft, with room to play around every one.",
        "photos/billiard-room-gabriels-wide", "The Two Stooges billiard room in Fridley: rows of blue-felt Gabriel's pool tables under wood-trimmed lights, with players at the tables", btn("Daily Pool Specials", "#rates", "gold") + btn("Join a Pool League", "/leagues/", "outline"))}
<section class="section"><div class="wrap">
  {section_head("The billiard room", "Fridley's award-winning pool hall", f"Pool has been the heart of Two Stooges since 1988, when it opened as University Billiards. {L('/about/', 'Read the full story')}.")}
  <div class="grid grid--3">
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>43 tournament tables</h3><p>9 ft and 7 ft Gabriel's and Diamond tables on Simonis 860 cloth, with good lighting and comfortable seating at every table.</p></div>
    <div class="tile"><span class="tile__icon">{icon("trophy")}</span><h3>Leagues &amp; tournaments</h3><p>APA, UPL, in-house 8-ball, straight pool and 10-ball {L("/leagues/", "pool leagues")}, plus {L("/events/", "FargoRate tournaments")} throughout the year.</p></div>
    <div class="tile"><span class="tile__icon">{icon("bag")}</span><h3>Pro Shop</h3><p>Cues, cases, chalk, gloves, {L("/darts/", "darts")} and accessories, plus {L("#pro-shop", "cue repair")}.</p></div>
  </div>
</div></section>
<section class="section section--alt" id="rates"><div class="wrap">
  <div class="split">
    <div>
      <span class="eyebrow">How to rent a table</span>
      <h2>Renting a pool table <span class="grad-text">at Two Stooges</span></h2>
      <ol class="check-list" style="list-style:none">
        <li>Stop at the billiard counter. The attendant will set you up with a table and a set of balls.</li>
        <li>Play as long as you like and order from the {L("/menu/", "bar and grill menu")} right at your table.</li>
        <li>Bring the balls back to the counter and settle up.</li>
      </ol>
      <h3 class="mt-2">Daily pool specials · 11 AM–5 PM</h3>
      <!-- TODO(client): confirm pool special pricing. -->
      <ul class="price-list">
        <li><span>Regular</span><span class="price">$11</span></li>
        <li><span>Seniors</span><span class="price">$10</span></li>
        <li><span>Premier table</span><span class="price">$12</span></li>
      </ul>
      <p class="small muted mt-1">Plus tax. See every {L("/specials/", "food and drink special")} too.</p>
    </div>
    <div class="split__media">{img("photos/friends-playing-pool", "Friends laughing around a pool table as one lines up a shot", sizes="(max-width:860px) 100vw, 50vw")}<div class="split__badge">Top 10 Billiard Room<small>in North America</small></div></div>
  </div>
</div></section>
<section class="section section--photo section--photo-strong on-dark" id="tournaments">
  <div class="section__bg">{img("photos/pool-rack-break", "A racked set of pool balls on blue felt with a player lining up the break", sizes="100vw")}</div>
  <div class="wrap">
  {section_head("Compete", "Pool leagues &amp; tournaments in Fridley", "Handicapped leagues for every skill level, and tournaments that are open to the public. You don't need to be in a league to play.")}
  <div class="grid grid--2 on-light">
    <div class="tile"><h3>Weekly pool leagues</h3><div class="tile__meta"><span class="chip chip--gold">Straight Pool · Tue 11 AM</span><span class="chip chip--gold">10-Ball · Thu 11 AM</span><span class="chip">APA</span><span class="chip">UPL</span><span class="chip">In-house 8-Ball</span></div><p class="mt-1">All leagues are handicapped, so beginners and sharks can play together.</p><a class="text-link" href="/leagues/">Pool league details &amp; sign-up</a></div>
    <div class="tile"><h3>FargoRate tournaments</h3><p>FargoRate 8-ball tournaments and bar box shootouts with money added. Spots fill fast, so sign up early.</p><a class="text-link" href="/events/">Upcoming pool tournaments</a></div>
  </div>
</div></section>
<section class="section section--alt" id="pro-shop"><div class="wrap">
  <div class="split split--rev">
    <div class="split__media">{img("photos/pro-shop-counter-cue-wall", "The Two Stooges Pro Shop: glass display cases of cue accessories, a wall of pool cues and cue cases, and the billiard counter, with the pool tables beyond", sizes="(max-width:860px) 100vw, 50vw")}<div class="split__badge">Cues &amp; Stuff<small>Pro Shop · cue repair</small></div></div>
    <div>
      <span class="eyebrow">Pro Shop</span>
      <h2>Two Stooges Pro Shop <span class="grad-text">&amp; cue repair</span></h2>
      <p class="lead">Our Pro Shop carries cues and accessories for pool and {L("/darts/", "darts")}, and we do cue repair on site.</p>
      <ul class="check-list"><li>Cues &amp; cases</li><li>Chalk, gloves &amp; accessories</li><li>Darts &amp; flights</li><li>Cue repair</li></ul>
      {btn("Call the Pro Shop", "tel:" + BIZ["tel"], "outline", "phone")}
    </div>
  </div>
</div></section>
<section class="section"><div class="wrap">
  {section_head("The room", "Inside the Two Stooges billiard room", f"More photos in the {L('/gallery/', 'Two Stooges photo gallery')}.")}
  <div class="photo-grid">{g}</div>
</div></section>
{cta_band("Host your event on the tables", "Birthdays, draft parties, office parties, celebrations of life and banquets. We'll customize the menu and the room for you.", btn("Plan a Private Party", "/private-parties/", "gold"))}'''
    return page("billiards", body)


def p_darts():
    body = f'''{page_hero("darts", "Darts at Stooges", "Darts at Two Stooges Sports Bar in <span class='grad-text'>Fridley</span>",
        f"Electronic dart boards, high-top tables and a big screen. Bring friends for a casual game or join one of our {L('/leagues/', 'dart leagues')}, which run every day of the week.",
        "photos/dart-bullseye-neon", "A dart hitting the bullseye under colorful bar lights", btn("Join a Dart League", "/league-signup/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  <div class="split">
    <div class="split__media">{img("photos/dart-room", "The Two Stooges dart area with a row of electronic dart boards", sizes="(max-width:860px) 100vw, 50vw")}</div>
    <div>
      <span class="eyebrow">The dart area</span>
      <h2>Electronic dart boards <span class="grad-text">in Fridley</span></h2>
      <p class="lead">Our dart area has a row of electronic boards, high-tops for your crew and a big screen showing the game. It's right next to the {L("/billiards/", "billiard room")}, so your group can switch between pool and darts all night.</p>
      <ul class="check-list"><li>Electronic dart boards</li><li>High-top seating right by the boards</li><li>Food and drinks from the {L("/menu/", "Two Stooges menu")} delivered to your table</li><li>Darts and flights in our {L("/billiards/#pro-shop", "Pro Shop")}</li></ul>
    </div>
  </div>
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("Dart leagues", "Dart leagues every day of the week", "Meet other players, sharpen your game and win cash. There's a league for every skill level.")}
  <div class="grid grid--3">
    <div class="tile"><span class="tile__icon">{icon("calendar")}</span><h3>Every night</h3><p>Leagues run every day of the week, so pick the night that works for you.</p></div>
    <div class="tile"><span class="tile__icon">{icon("users")}</span><h3>Custom leagues</h3><p>We can set up leagues for women, couples or teams. Just ask.</p></div>
    <div class="tile"><span class="tile__icon">{icon("award")}</span><h3>Win cash</h3><p>Compete for prize money and bragging rights all season long.</p></div>
  </div>
  <div class="btn-row mt-2">{btn("Sign Up for a Dart League", "/league-signup/", "gold")}{btn("Ask a Team Member", "tel:" + BIZ["tel"], "outline", "phone")}</div>
</div></section>
<section class="section section--alt"><div class="wrap">
  <div class="split split--rev">
    <div class="split__media">{img("photos/dart-red-black", "A red dart in the bullseye of a dartboard", sizes="(max-width:860px) 100vw, 50vw")}</div>
    <div>
      <span class="eyebrow">New to darts?</span>
      <h2>Easy to start, <span class="grad-text">hard to put down</span></h2>
      <p class="lead">Never thrown before? Ask a team member and we'll get you set up on a board. The electronic boards keep score for you, so you can focus on the fun.</p>
      <ul class="check-list"><li>Electronic boards keep score automatically</li><li>Bring your own darts or pick up a set in the {L("/billiards/#pro-shop", "Pro Shop")}</li><li>Ready to compete? {L("/league-signup/", "Join a dart league")}</li></ul>
    </div>
  </div>
</div></section>
<section class="section" id="pro-shop"><div class="wrap">
  {section_head("Pro Shop", "Darts, cues &amp; gear at the Two Stooges Pro Shop", f"Pick up darts, flights, cues, cases, chalk, gloves and accessories right on site, and bring your cue in for repair. More on the {L('/billiards/#pro-shop', 'Pro Shop & cue repair')}.")}
  <div class="mosaic">
    {"".join(f'<figure class="gallery__item mosaic__item"><button type="button" data-lightbox="/assets/img/{p_}.webp" data-alt="{e(a_)}" data-caption="{e(a_)}" aria-label="Enlarge photo: {e(a_)}">{img(p_, a_, sizes=sz)}</button></figure>' for p_, a_, sz in [
        ("photos/pro-shop-counter-wide", "The Two Stooges Pro Shop: a wood-and-glass counter of accessories in front of lit racks of pool cues and a wall of cue cases", "(max-width:860px) 100vw, 60vw"),
        ("photos/pro-shop-cue-wall", "A lit wall of pool cues above a row of cue cases in the Pro Shop", "(max-width:860px) 50vw, 30vw"),
        ("photos/pro-shop-display-case", "Glass display cases with colorful cue holders, gloves, chalk holders and cue cases", "(max-width:860px) 50vw, 30vw")])}
  </div>
  <div class="btn-row mt-2">{btn("Visit the Pro Shop", "/billiards/#pro-shop", "green", "bag")}{btn("Call the Pro Shop", "tel:" + BIZ["tel"], "outline", "phone")}</div>
</div></section>
{cta_band("Dart night for your group?", f"Birthdays, office outings and team nights. We'll reserve boards and put together food for your group.", btn("Plan a Private Party", "/private-parties/", "gold"))}'''
    return page("darts", body)


def p_leagues():
    lg = []
    for L_ in LEAGUES:
        pts = "".join(f"<li>{e(p)}</li>" for p in L_["points"])
        lg.append(f'''<article class="event">
  <button class="event__flyer" type="button" data-lightbox="/assets/img/{L_["flyer"]}" data-alt="{e(L_["flyer_alt"])}" data-caption="{e(L_["name"])}" aria-label="View full flyer: {e(L_["name"])}">{img(L_["flyer"], L_["flyer_alt"], srcset=False)}</button>
  <div>
    <div class="event__date"><span>{e(L_["day"])}</span><span>{e(L_["time"])}</span></div>
    <h3>{e(L_["name"])} at Two Stooges</h3>
    <ul class="check-list">{pts}</ul>
    <div class="event__contact">{btn("Call to sign up: " + BIZ["phone"], "tel:" + BIZ["tel"], "gold", "phone")}<a class="text-link" href="/league-signup/">Sign up for a league online</a></div>
  </div>
</article>''')
    body = f'''{page_hero("leagues", "Pool &amp; dart leagues", "Pool &amp; dart leagues at <span class='grad-text'>Two Stooges Sports Bar</span>",
        f"Leagues at Two Stooges are a great way to meet other pool and dart players in Fridley, sharpen your skills and win cash. There's a league for every skill level on our {L('/billiards/', '43 tables')} and {L('/darts/', 'dart boards')}.",
        "photos/tournament-table-trophies", "Tournament table with trophies above", btn("Sign Up Online", "/league-signup/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  {section_head("In-house pool leagues", "Weekday pool leagues in Fridley", "Played on our 9 ft Gabriel's tables. Click a flyer to see it full size.")}
  {"".join(lg)}
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("More leagues", "APA, UPL &amp; dart leagues")}
  <div class="grid grid--3">
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>APA &amp; UPL</h3><p>We host APA and UPL handicapped pool leagues, open to all skill levels.</p></div>
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>In-house 8-Ball</h3><p>Our own handicapped 8-ball league, a great first league for newer players.</p></div>
    <div class="tile"><span class="tile__icon">{icon("target")}</span><h3>Dart leagues</h3><p>Leagues every day of the week, plus custom leagues for women, couples and teams. {L("/darts/", "See the dart area")}.</p></div>
  </div>
  <p class="mt-2 muted">Ready to compete for money? Check the {L("/events/", "upcoming pool tournaments")} for FargoRate 8-ball shootouts.</p>
</div></section>
{cta_band("Ready to join a league?", "Sign up online in a couple of minutes. Solo players are welcome, and we'll help you find a team.", btn("League Sign-Up", "/league-signup/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}'''
    return page("leagues", body, extra_ld=league_event_nodes())


LEAGUE_FAQ = [
    ("Do I need a team to join a league?", "No. Solo players are welcome. Sign up and we'll help place you on a team or league night."),
    ("What skill level do I need?", "Any. Our leagues are handicapped, so beginners and experienced players can compete on even terms."),
    ("Which leagues can I join?", "Straight Pool on Tuesdays at 11 AM, 10-Ball on Thursdays at 11 AM, APA, UPL and in-house 8-ball pool leagues, plus dart leagues every day of the week."),
    ("Can I sign up by phone?", "Yes. Call (763) 574-1399 and a team member will sign you up."),
]


def p_signup():
    benefits = [
        ("users", "Meet your people", "League night is the easiest way to meet other pool and dart players in Fridley and the north metro."),
        ("trophy", "Compete for cash & bragging rights", "Play for standings, prizes and cash, and get ready for our FargoRate tournaments with money added."),
        ("ball", "Every skill level", "Leagues are handicapped, so newer players and sharks can play together, and every match is competitive."),
        ("target", "Get better every week", "Regular match play against new opponents sharpens your game faster than practice alone, and it builds your FargoRate."),
        ("calendar", "A standing night out", "Same night, same crew, every week. It's a built-in reason to get out of the house."),
        ("award", "Play on tournament tables", "Pool leagues are played on our 9 ft Gabriel's tables with new cloth and rails, in a room named a top ten billiard room in North America."),
    ]
    ben = "".join(f'<div class="tile"><span class="tile__icon">{icon(i)}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, t, d in benefits)
    leagues = [("Tuesdays · 11 AM", "Straight Pool League", "BCA rules · 3 races to 50 points"),
               ("Thursdays · 11 AM", "10-Ball League", "3 sets, race to 5 · 9 ft Gabriel's"),
               ("Your league night", "APA & UPL", "Handicapped pool leagues for all levels"),
               ("Your league night", "In-house 8-Ball", "A great first league for newer players"),
               ("Every day", "Dart Leagues", "Plus custom leagues for women, couples & teams")]
    lg = "".join(f'<div class="schedule__item"><div class="schedule__day">{e(d)}</div><h3>{e(n)}</h3><p>{e(x)}</p></div>' for d, n, x in leagues)
    steps = [("1", "Fill out the form", "Tell us whether you want pool or darts, which night works, and whether you have a team."),
             ("2", "We'll place you", "A team member will contact you to confirm your league, team and start date."),
             ("3", "Show up and play", "Grab a table, meet your team and rack 'em up.")]
    st = "".join(f'<div class="step"><span class="step__num">{n}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></div>' for n, t, d in steps)
    faqs = "".join(f'<details class="faq"><summary><h3>{e(q)}</h3></summary><p>{e(a)}</p></details>' for q, a in LEAGUE_FAQ)
    body = f'''{page_hero("signup", "League sign-up", "Join a league at <span class='grad-text'>Two Stooges Sports Bar</span>",
        f"Sign up for a pool or dart league in Fridley. We have handicapped leagues for every skill level on our {L('/billiards/', '43 tables')} and {L('/darts/', 'dart boards')}. Solo players are welcome.",
        "photos/player-lining-up-shot", "A league player lining up a shot at Two Stooges", btn("Sign Up Now", "#form", "gold", "trophy") + btn("See All Leagues", "/leagues/", "outline"))}
<section class="section"><div class="wrap">
  {section_head("Why join", "Benefits of joining a Two Stooges league", "More than just a game night. Here's what you get when you join a league in Fridley.", center=True)}
  <div class="grid grid--3">{ben}</div>
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("Pick your league", "Pool &amp; dart leagues you can join", f"See full rules and flyers on the {L('/leagues/', 'leagues page')}, or check {L('/events/', 'upcoming tournaments')}.")}
  <div class="schedule schedule--5">{lg}</div>
</div></section>
<section class="section"><div class="wrap">
  {section_head("How it works", "Signing up takes about two minutes", center=True)}
  <div class="steps">{st}</div>
</div></section>
<section class="section section--alt" id="form"><div class="wrap">
  <div class="split" style="align-items:start">
    <div>
      <span class="eyebrow">League sign-up form</span>
      <h2>Sign up for a <span class="grad-text">pool or dart league</span></h2>
      <p class="lead">Fill out the form and we'll get you placed on a team or league night. Prefer the phone? Call us and a team member will sign you up.</p>
      <ul class="check-list"><li>Pool or darts</li><li>Solo players welcome. We'll help find you a team.</li><li>Handicapped, so every skill level can compete</li></ul>
      {btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone")}
      <div class="faq-list mt-2">{faqs}</div>
    </div>
    {cognito(FORM_LEAGUE, "League sign-up form")}
  </div>
</div></section>'''
    faq_node = {"@type": "FAQPage", "@id": SITE + "/league-signup/#faq", "isPartOf": {"@id": SITE + "/league-signup/#webpage"},
                "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in LEAGUE_FAQ]}
    return page("signup", body, extra_ld=league_event_nodes() + [faq_node], main_entity=SG.SERVICES["leagues"]["@id"])



def league_block(L_):
    pts = "".join(f"<li>{e(p)}</li>" for p in L_["points"])
    return f'''<article class="event">
  <button class="event__flyer" type="button" data-lightbox="/assets/img/{L_["flyer"]}" data-alt="{e(L_["flyer_alt"])}" data-caption="{e(L_["name"])}" aria-label="View full flyer: {e(L_["name"])}">{img(L_["flyer"], L_["flyer_alt"], srcset=False)}</button>
  <div>
    <div class="event__date"><span>{e(L_["day"])}</span><span>{e(L_["time"])}</span></div>
    <h3>{e(L_["name"])} at Two Stooges</h3>
    <ul class="check-list">{pts}</ul>
    <div class="event__contact">{btn("Call to sign up: " + BIZ["phone"], "tel:" + BIZ["tel"], "gold", "phone")}<a class="text-link" href="/league-signup/">Sign up for a league online</a></div>
  </div>
</article>'''


def p_events():
    ups = sorted(upcoming_events(), key=lambda x: x["end"])
    up_html = "".join(event_block(ev) for ev in ups)
    past_html = "".join(past_card(ev) for ev in past_events())
    body = f'''{page_hero("events", "What's happening", "Events &amp; tournaments at <span class='grad-text'>Two Stooges Sports Bar</span>",
        f"Pool tournaments, weekly league nights and special events at Two Stooges in Fridley. Click any flyer to see it full size. Want your own event? {L('/private-parties/', 'Book a private party')}.",
        "photos/billiard-room-hero", "The Two Stooges billiard room", btn("Upcoming Tournament", "#upcoming", "gold") + btn("Weekly Leagues", "#weekly", "outline") + btn("Recent Events", "#recent", "outline"))}
<section class="section" id="upcoming"><div class="wrap">
  {section_head("Coming up", "Upcoming pool tournaments in Fridley", f"FargoRate events on our {L('/billiards/', 'tournament tables')}. Spots are limited, so call to sign up.")}
  <div data-upcoming>{up_html}</div>
  <div class="empty-note{"" if ups else " is-visible"}" data-empty-note>New events are on the way. Call <a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a> to find out what's coming up next, or {L("/leagues/", "join a weekly league")}.</div>
</div></section>
<section class="section section--alt" id="weekly"><div class="wrap">
  {section_head("Every week", "Weekly league nights at Two Stooges", f"Our in-house pool leagues on the 9 ft Gabriel's tables. Dart leagues run every day, too. See {L('/leagues/', 'all pool and dart leagues')}.")}
  {"".join(league_block(L_) for L_ in LEAGUES)}
</div></section>
<section class="section" id="recent"><div class="wrap">
  {section_head("Recent events", "Recent events at Two Stooges", "Missed one? Here's what we've hosted lately. Most events come back, so watch this page.")}
  <div class="flyer-grid" data-past-grid>{past_html}</div>
</div></section>
{cta_band("Want to host a tournament or party?", "From birthday bashes to banquets and league parties, we'll help you plan it.", btn("Plan Your Event", "/private-parties/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}'''
    return page("events", body, extra_ld=[event_ld(ev) for ev in ups] + league_event_nodes())


def p_parties():
    occasions = ["Birthdays", "Office parties", "Draft parties", "Holiday parties", "Celebrations of life", "Banquets & league parties", "Business meetings", "Reunions & receptions"]
    occ = "".join(f"<li>{e(o)}</li>" for o in occasions)
    body = f'''{page_hero("parties", "Private parties &amp; events", "Private parties at <span class='grad-text'>Two Stooges Sports Bar</span>",
        "Two Stooges is ready for your next birthday, holiday party, office outing or banquet in Fridley. We'll customize the menu and the space for your group.",
        "photos/private-party-banquet-wide", "Two Stooges set up for a private party: round tables with white and black linens, roses and place settings, with the bar and dart boards behind", btn("Request a Date", "#request", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  <div class="split">
    <div>
      <span class="eyebrow">Perfect for</span>
      <h2>A Fridley party venue for <span class="grad-text">any occasion</span></h2>
      <p class="lead">We have spaces for small and large groups, with {L("/billiards/", "pool tables")}, {L("/darts/", "dart boards")} and big screens included.</p>
      <ul class="check-list check-list--2col">{occ}</ul>
    </div>
    <div class="split__media collage">
      {img("photos/private-party-string-lights", "A Two Stooges banquet setup with string lights and draped fabric overhead, linen-covered round tables and roses", sizes="(max-width:860px) 100vw, 50vw")}
      {img("photos/private-party-buffet", "A buffet line of chafing dishes with roasted potatoes, vegetables and entrées for a catered event", sizes="(max-width:860px) 60vw, 25vw", cls="collage__inset")}
      <div class="split__badge">Custom menus<small>Buffets &amp; party packages</small></div>
    </div>
  </div>
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("What's included", "Party packages at Two Stooges", center=True)}
  <!-- TODO(client): add room names, capacities and package pricing when available. -->
  <div class="grid grid--4">
    <div class="tile"><span class="tile__icon">{icon("users")}</span><h3>Space for your group</h3><p>Different areas for small and large gatherings.</p></div>
    <div class="tile"><span class="tile__icon">{icon("fork")}</span><h3>Custom menus</h3><p>Food packages built from the {L("/menu/", "Two Stooges menu")} for your group and budget.</p></div>
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>Pool &amp; darts</h3><p>Reserve tables and boards so your guests can play.</p></div>
    <div class="tile"><span class="tile__icon">{icon("tv")}</span><h3>Big screens</h3><p>Watch the game on our 34 screens, or bring your own slideshow.</p></div>
  </div>
</div></section>
<section class="section" id="request"><div class="wrap">
  <div class="split" style="align-items:start">
    <div>
      <span class="eyebrow">Event request</span>
      <h2>Request a <span class="grad-text">party date</span></h2>
      <p class="lead">Send us the date, how many guests and what you're celebrating. We'll get back to you with options and pricing. Planning a tournament? See our {L("/events/", "past and upcoming events")} for ideas.</p>
      <div class="info-row mt-2"><span class="tile__icon">{icon("phone")}</span><div><h3>Rather talk it through?</h3><p><a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a></p></div></div>
      <div class="info-row mt-1"><span class="tile__icon">{icon("mail")}</span><div><h3>Email</h3><p><a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a></p></div></div>
    </div>
    {cognito(FORM_EVENT, "Private event request form")}
  </div>
</div></section>'''
    return page("parties", body)


def p_about():
    tl = [("1988", "University Billiards opens", "University Billiards opens its doors in April 1988 with 17 pool tables and a snack bar."),
          ("1990s", "Room to grow", "The room grows to 56 pool tables and a full-service American restaurant."),
          ("1998", "Billiard Street Café", "A new name for a growing destination. You can still spot the sign out front."),
          ("2006", "Two Stooges is born", "A full sports bar joins the billiard room, and the business becomes Two Stooges Sports Bar & Grill."),
          ("Today", "Still racking 'em up", "43 tables, darts, 30 HD TVs plus 4 monster screens, 16 taps, and the same family feel.")]
    tl_html = "".join(f'<li><span class="timeline__year">{y}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for y, t, d in tl)
    awards = [("Top Ten Billiard Room in North America", "Billiards industry recognition"), ("Best Place to Shoot Pool", "City Pages, 2017"),
              ("Business of the Year", "Local business award"), ("Best of: Architectural Design", "Billiards Digest")]
    aw = "".join(f'<div class="tile"><span class="tile__icon">{icon("award")}</span><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in awards)
    body = f'''{page_hero("about", "Our story", "About Two Stooges Sports Bar: <span class='grad-text'>Fridley since 1988</span>",
        f"{e(ENTITY_DESC)} Almost four decades in, we're still serving the coldest beer and juiciest burgers around.",
        "photos/storefront-two-stooges", "The Two Stooges Sports Bar & Grill storefront in Fridley: red and yellow signs over green awnings marked Darts, Cafe, Pro Shop and Billiards", btn("Visit Us", "/contact/", "gold"))}
<section class="section"><div class="wrap">
  <div class="split" style="align-items:start">
    <div>
      <span class="eyebrow">How it started</span>
      <h2>The history of <span class="grad-text">Two Stooges</span></h2>
      <p class="lead">What began as a neighborhood {L("/billiards/", "billiard room")} became one of the best-known pool and darts destinations in Minnesota, with a full sports bar and {L("/menu/", "kitchen")} to match.</p>
      <ol class="timeline mt-2">{tl_html}</ol>
    </div>
    <div class="split__media">{img("photos/billiard-room-trophies", "Gabriel's tournament tables in the Two Stooges billiard room, with league trophies displayed above the table lights", sizes="(max-width:860px) 100vw, 50vw")}</div>
  </div>
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("Recognition", "Awards &amp; recognition", f"Want to see why? Join a {L('/leagues/', 'pool or dart league')} or enter one of our {L('/events/', 'tournaments')}.", center=True)}
  <div class="grid grid--4">{aw}</div>
</div></section>
<section class="section"><div class="wrap">
  <div class="split split--rev">
    <div class="split__media">{img("photos/sports-bar-center-bar", "The Two Stooges center bar: wood bar top and stools, TVs showing games overhead and a full back bar", sizes="(max-width:860px) 100vw, 50vw")}</div>
    <div>
      <span class="eyebrow">The sports bar</span>
      <h2>A Fridley sports bar with <span class="grad-text">a seat at the center</span></h2>
      <p class="lead">Our elevated bar sits right in the middle of the room, so wherever you sit you're part of the action. It's cherry wood with steel railings, and the tall booths fit your whole group. Take a look in the {L("/gallery/", "photo gallery")}.</p>
      <ul class="check-list"><li>NFL Sunday Ticket and the DirecTV sports channels</li><li>30 HD TVs and 4 monster screens</li><li>16 beers on tap</li><li>Original drinks and {L("/specials/", "daily specials")}</li></ul>
    </div>
  </div>
</div></section>
{visit_section()}'''
    return page("about", body)


def p_gallery():
    photos = [("photos/sports-bar-game-day", "The sports bar on game day: a long high-top table in front of the center bar, with games on the TVs and Packers on the big screen"),
              ("photos/sports-bar-center-bar", "The center bar with wood bar top, stools, TVs and a full back bar"),
              ("photos/pro-shop-counter-wide", "The Pro Shop counter in front of lit racks of pool cues and cue cases"),
              ("photos/sports-bar-booths", "Booths and high-tops along the bar, overlooking the billiard room"),
              ("photos/dart-boards-bullshooter", "The row of six electronic Bullshooter dart boards"),
              ("photos/event-pool-tournament-crowd", "A crowd watching a shot during a group event on a Gabriel's table"),
              ("photos/food-steak-bites-onion-rings", "Steak bites topped with onion rings"),
              ("photos/food-thin-crust-pizza", "Thin-crust pizza with sausage, mushrooms and red onion"),
              ("photos/food-tater-tots", "A pile of hot, crispy tater tots"),
              ("photos/billiard-room-rows", "Rows of blue-felt pool tables in the billiard room"), ("photos/player-shooting", "A player taking a shot"),
              ("photos/dart-room", "The dart area with electronic boards and a big screen"), ("photos/pool-hall-interior", "The billiard room under warm lights"),
              ("photos/player-racking", "Racking up a game"), ("photos/building-exterior", "Outside Two Stooges on University Ave NE, Fridley"),
              ("photos/tournament-table-trophies", "Tournament table and trophies"), ("photos/player-lining-up-shot", "Lining up the shot"),
              ("photos/billiard-hall-tables", "The billiard hall"), ("photos/pro-shop-cues-and-stuff", "The Pro Shop: cues, cases and accessories"), ("photos/pool-balls-rack", "A fresh rack on blue felt")]
    g = "".join(f'<figure class="gallery__item"><button type="button" data-lightbox="/assets/img/{p}.webp" data-alt="{e(a)}" data-caption="{e(a)}" aria-label="Enlarge photo: {e(a)}">{img(p, a + " at Two Stooges Sports Bar", sizes="(max-width:640px) 100vw, (max-width:1000px) 50vw, 33vw")}</button><figcaption>{e(a)}</figcaption></figure>' for p, a in photos)
    body = f'''{page_hero("gallery", "Take a look", "Photos of <span class='grad-text'>Two Stooges Sports Bar</span>",
        f"Inside the {L('/billiards/', 'billiard room')}, the {L('/darts/', 'dart area')} and the bar in Fridley. Click any photo to see it full size.",
        "photos/pool-hall-interior", "The Two Stooges billiard room")}
<section class="section"><div class="wrap">
  {section_head("Gallery", "Inside the Fridley pool hall &amp; sports bar", f"Every photo was taken at Two Stooges. Like what you see? {L('/private-parties/', 'Host your next party here')}.")}
  <div class="gallery">{g}</div>
</div></section>
{cta_band("See it in person", "Open every day from 11 AM to midnight at 7178 University Ave NE in Fridley.", btn("Get Directions", DIRECTIONS, "gold", "nav", ' target="_blank" rel="noopener"'))}'''
    return page("gallery", body)


def p_contact():
    body = f'''{page_hero("contact", "Get in touch", "Contact <span class='grad-text'>Two Stooges Sports Bar</span> in Fridley, MN",
        "Questions about leagues, tournaments, parties or the menu? Give us a call or stop in. We're open every day from 11 AM to midnight.",
        "photos/building-exterior", "The Two Stooges building on University Ave NE", btn("Send a Message", "#form", "gold", "mail") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone") + btn("Get Directions", DIRECTIONS, "outline", "nav", ' target="_blank" rel="noopener"'))}
<section class="section" id="form"><div class="wrap">
  <div class="split" style="align-items:start">
    <div>
      <span class="eyebrow">Send a message</span>
      <h2>Contact <span class="grad-text">Two Stooges</span></h2>
      <p class="lead">Questions about leagues, tournaments, parties or the menu? Send us a note and a team member will get back to you. For anything urgent, call {BIZ["phone"]}.</p>
      <div class="info-row mt-2"><span class="tile__icon">{icon("phone")}</span><div><h3>Phone</h3><p><a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a></p></div></div>
      <div class="info-row mt-1"><span class="tile__icon">{icon("mail")}</span><div><h3>Email</h3><p><a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a></p></div></div>
      <div class="info-row mt-1"><span class="tile__icon">{icon("clock")}</span><div><h3>Hours</h3><p>Open every day, 11 AM – 12 AM</p></div></div>
    </div>
    {cognito(FORM_EVENT, "Contact form")}
  </div>
</div></section>
{visit_section("Two Stooges address, hours &amp; phone")}
<section class="section"><div class="wrap">
  {section_head("How can we help?", "Plan your visit to Two Stooges", f"Quick answer? Try the {L('/faq/', 'Two Stooges FAQ')}.", center=True)}
  <div class="grid grid--3">
    <article class="card card--link"><div class="card__body"><span class="tile__icon">{icon("users")}</span><h3><a class="stretched" href="/private-parties/#request">Plan a private party</a></h3><p>Birthdays, office parties, banquets and more. Send us your event details.</p></div></article>
    <article class="card card--link"><div class="card__body"><span class="tile__icon">{icon("trophy")}</span><h3><a class="stretched" href="/league-signup/">Join a pool or dart league</a></h3><p>Every skill level is welcome. Sign up online or by phone.</p></div></article>
    <article class="card card--link"><div class="card__body"><span class="tile__icon">{icon("calendar")}</span><h3><a class="stretched" href="/events/">See upcoming tournaments</a></h3><p>See what's coming up and how to get on the bracket.</p></div></article>
  </div>
  <p class="center small muted mt-2">Find Two Stooges on Google Maps: {e(BIZ["plus_code"])}</p>
</div></section>'''
    return page("contact", body, og_type="business.business")


FAQ_GROUPS = [
    ("Visiting Two Stooges", [
        FAQ[0][:2], FAQ[1][:2],
        ("Does Two Stooges have outdoor seating?", "Yes. Two Stooges has two patios."),
        ("Is there parking?", 'Yes, there is a parking lot right outside the front doors on University Ave NE. <a href="/contact/">Get directions</a>.'),
        FAQ[5][:2],
    ]),
    ("Pool, darts & the Pro Shop", [
        FAQ[2][:2],
        ("How do I rent a pool table?", 'Stop at the billiard counter and the attendant will set you up with a table and a set of balls. Play as long as you like, then bring the balls back and settle up. <a href="/billiards/#rates">Daily pool specials</a> run 11 AM–5 PM.'),
        ("How many dart boards are there?", 'Two Stooges has 6 electronic dart boards with high-top seating right next to them. <a href="/darts/">See the dart area</a>.'),
        ("Is there a pro shop?", 'Yes. The Pro Shop carries cues, cases, chalk, gloves, darts and accessories, and we do cue repair on site. <a href="/billiards/#pro-shop">Visit the Pro Shop</a>.'),
    ]),
    ("Leagues & tournaments", [
        FAQ[3][:2],
        ("Do I need a team to join a league?", 'No. Solo players are welcome, and we will help place you on a team or league night. <a href="/league-signup/">Sign up for a league</a>.'),
        ("What skill level do I need?", "Any. Our leagues are handicapped, so beginners and experienced players can compete on even terms."),
        ("Does Two Stooges host pool tournaments?", 'Yes. We host FargoRate 8-ball tournaments and bar box shootouts with money added. <a href="/events/">See upcoming tournaments</a>.'),
    ]),
    ("Food & drink", [
        ("What food does Two Stooges serve?", 'Classic American bar and grill food: Stoogetizers, wings, burgers, sandwiches and wraps, pizza, entrées, soup and salad. <a href="/menu/">See the full menu</a>.'),
        ("When is happy hour?", 'Monday to Thursday 2–6 PM, and Friday to Sunday 11 AM–7 PM, with daily food specials too. <a href="/specials/">See every special</a>.'),
        ("How many beers are on tap?", "Two Stooges pours 16 beers on tap, ice-cold from our iced cobra taps."),
    ]),
    ("Parties & contact", [
        FAQ[4][:2],
        ("How do I book a private party?", 'Send your date, guest count and occasion with the <a href="/private-parties/#request">event request form</a>, or call (763) 574-1399.'),
        ("How do I contact Two Stooges?", 'Call (763) 574-1399, email info@twostooges.com, or use the <a href="/contact/#form">contact form</a>.'),
    ]),
]


def p_faq():
    groups = []
    for title, qs in FAQ_GROUPS:
        items = "".join(f'<details class="faq"><summary><h3>{e(q)}</h3></summary><p>{a}</p></details>' for q, a in qs)
        groups.append(f'<section class="faq-group"><h2>{e(title)}</h2><div class="faq-list">{items}</div></section>')
    jump = "".join(f'<a class="chip chip--green" href="#faq-{i}">{e(t)}</a>' for i, (t, _) in enumerate(FAQ_GROUPS))
    groups_html = "".join(g.replace('<section class="faq-group">', f'<section class="faq-group" id="faq-{i}">', 1) for i, g in enumerate(groups))
    body = f'''{page_hero("faq", "Good to know", "Two Stooges Sports Bar <span class='grad-text'>FAQ</span>",
        f"Quick answers about visiting Two Stooges in Fridley: hours, pool tables, darts, leagues, food and private parties. Can't find what you need? {L('/contact/#form', 'Send us a message')}.",
        "photos/billiard-room-gabriels", "The Two Stooges billiard room", btn("Contact Us", "/contact/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap" style="max-width:900px">
  <nav class="faq-jump" aria-label="FAQ topics">{jump}</nav>
  {groups_html}
</div></section>
{visit_section()}'''
    node = {"@type": "FAQPage", "@id": SITE + "/faq/#faq", "isPartOf": {"@id": SITE + "/faq/#webpage"},
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": SG.strip(a)}}
                           for _, qs in FAQ_GROUPS for q, a in qs]}
    return page("faq", body, extra_ld=[node], main_entity=SITE + "/faq/#faq")



def p_privacy():
    upd = dt.date.fromisoformat(TODAY).strftime("%B %-d, %Y")
    # TODO(client): have the owners review this policy.
    body = f'''{page_hero("privacy", "Legal", "Two Stooges Sports Bar <span class='grad-text'>privacy policy</span>",
        f"How {e(BIZ['name'])} handles information collected through this website. Last updated {upd}.",
        "photos/billiard-room-rows", "The Two Stooges billiard room")}
<section class="section"><div class="wrap prose" style="max-width:820px">
  <h2>Information we collect</h2>
  <p>We only collect the information you choose to send us, such as your name, phone number, email address and event or league details when you fill out our {L("/private-parties/#request", "event request form")} or {L("/league-signup/", "league sign-up form")}. These forms are provided by Cognito Forms, which processes the information on our behalf.</p>
  <h2>How we use it</h2>
  <p>We use your information to respond to your request, schedule your event or league, and contact you about it. We don't sell or rent your personal information.</p>
  <h2>Third-party services</h2>
  <p>This site uses Google Maps (to show our location), Google Fonts (for text styling) and Cloudflare (to host and protect the site). These services may receive technical information such as your IP address and browser type when the page loads, under their own privacy policies.</p>
  <h2>Cookies</h2>
  <p>We don't use advertising cookies. Embedded services like Google Maps may set their own cookies.</p>
  <h2>Contact us</h2>
  <p>Questions about this policy? Email <a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a>, call <a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a>, or {L("/contact/", "visit our contact page")}.</p>
</div></section>'''
    return page("privacy", body)


def p_404():
    body = f'''<section class="section"><div class="wrap center" style="max-width:720px">
  <span class="eyebrow">Error 404</span>
  <h1>Scratch! <span class="grad-text">Page not found</span></h1>
  <p class="lead" style="margin:0 auto 2rem">That page has moved or doesn't exist. Try one of these Two Stooges pages instead.</p>
  <div class="btn-row" style="justify-content:center">{btn("Home", "/", "gold")}{btn("Events", "/events/", "outline")}{btn("Specials", "/specials/", "outline")}{btn("Contact", "/contact/", "outline")}</div>
</div></section>'''
    # 404 is never indexed and carries no canonical (a canonical on an error page is invalid).
    html_ = f'''<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page Not Found | Two Stooges Sports Bar</title>
<meta name="robots" content="noindex, follow">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/brand/favicon-48.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Oswald:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_VER}">
</head>
<body>
{header("/404.html")}
<main id="main">{body}</main>
{footer()}
<script src="/assets/js/site.js?v={ASSET_VER}" defer></script>
</body>
</html>
'''
    return html_


PAGES = {
    "index.html": p_home, "menu/index.html": p_menu, "specials/index.html": p_specials,
    "billiards/index.html": p_billiards, "darts/index.html": p_darts, "leagues/index.html": p_leagues,
    "events/index.html": p_events, "league-signup/index.html": p_signup, "private-parties/index.html": p_parties, "about/index.html": p_about,
    "gallery/index.html": p_gallery, "contact/index.html": p_contact, "privacy-policy/index.html": p_privacy, "faq/index.html": p_faq,
    "404.html": p_404,
}


def main():
    IMGS.optimize()  # image rule: every photo web-ready before pages read their sizes
    for rel, fn in PAGES.items():
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(fn(), encoding="utf-8")
        print("wrote", rel)
    # Sitemap: canonical URLs only (matches <link rel=canonical> exactly)
    prio = {"/": "1.0", "/events/": "0.9", "/billiards/": "0.9", "/specials/": "0.8", "/menu/": "0.8", "/leagues/": "0.8",
            "/darts/": "0.7", "/league-signup/": "0.8", "/private-parties/": "0.8", "/about/": "0.6", "/gallery/": "0.5", "/contact/": "0.7", "/faq/": "0.6", "/privacy-policy/": "0.2"}
    urls = [m[0] for m in META.values()]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{prio.get(u, '0.5')}</priority></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    robots = ("User-agent: *\nAllow: /\nDisallow: /_src/\n\nSitemap: " + SITE + "/sitemap.xml\n") if LAUNCH else "User-agent: *\nDisallow: /\n"
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    print("wrote sitemap.xml, robots.txt (launch=%s)" % LAUNCH)
    bad = IMGS.check()
    if bad:
        raise SystemExit("Image check failed (over budget):\n  " + "\n  ".join(bad))
    print("images: all within budget")


if __name__ == "__main__":
    main()
