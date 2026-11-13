#!/usr/bin/env python3
"""
Two Stooges site generator.

Every page shares one header, footer, nav and business-info block defined
here, so hours/phone/nav only ever change in one place.

    python3 _src/build.py          # writes the HTML pages into the repo root

Then commit + push; Cloudflare Pages deploys `main` automatically.
Events and tournaments are entered in the admin (/admin/, Decap CMS) and saved as
JSON in _content/events/ and _content/tournaments/. A GitHub Action rebuilds the site
whenever they change (and once a day, so past dates move to "Recent").
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
import content as CT
import places as PL
import cities as CD

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"

# Flip to True on launch day (removes noindex). pages.dev stays noindex via _headers.
LAUNCH = True
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
              ("Leagues", "/leagues/", "Weekly pool & dart leagues"),
              ("Tournaments", "/tournaments/", "Weekly 8-ball, 9-ball & Fargo events"),
              ("League Sign-Up", "/league-signup/", "Join a league online")]),
    ("Events", [("Upcoming Events", "/events/", "Special nights, parties & promos"),
                ("Private Parties", "/private-parties/", "Birthdays, office parties & more")]),
    ("About", "/about/"),
    ("Gallery", "/gallery/"),
    ("Contact", [("Contact Us", "/contact/", "Address, hours & message form"),
                 ("FAQ", "/faq/", "Answers to common questions")]),
]

TODAY = dt.date.today().isoformat()
GRAPHS = {}

# ---------------------------------------------------------------------------
# Events & tournaments come from _content/ (entered in the admin at /admin/).
# Filled by main() after the image step; see _src/content.py.
# ---------------------------------------------------------------------------
ENTRIES = {"events": [], "tournaments": []}
ENTRY_PAGE = {"events": "/events/", "tournaments": "/tournaments/"}

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
    (2, "Tuesday", "Tue", "Taco Tuesday!", "$8", "2 tacos", "Two tacos for $8", "All day",
     [("2–5 PM", "$2 off appetizers (excl. wings)")], "2–6 PM"),
    (3, "Wednesday", "Wed", "Wing Night", "$1", "wings", "Minimum 10 · fresh, never frozen", "All day",
     [("2–5 PM", "$2 off appetizers (excl. wings)")], "2–6 PM"),
    (4, "Thursday", "Thu", "Appetizer Hour", "$2 off", "appetizers", "Excludes wings", "2–5 PM",
     [], "2–6 PM"),
    (5, "Friday", "Fri", "Appetizer Friday", "$2 off", "appetizers", "Excluding wings", "11 AM–7 PM",
     [], "11 AM–7 PM"),
    (6, "Saturday", "Sat", "Pizza & Sandwiches", "$3 off", "large pizzas", "$2 off small pizzas", "11 AM–7 PM",
     [("11 AM–7 PM", "$2 off sandwiches & wraps")], "11 AM–7 PM"),
    (0, "Sunday", "Sun", "Sunday Funday", "$1.50", "wings", "Minimum 8", "11 AM–7 PM",
     [("11 AM–7 PM", "$3 off large · $2 off small pizza"), ("11 AM–7 PM", "$2 off any entrée"), ("Happy hour", "$1 off 22 oz craft beer")], "11 AM–7 PM"),
]
HH_DRINKS = [("$3.50", "Domestic bottles"), ("$3.50", "Domestic pints"), ("$4.25", "Domestic 22 oz"), ("$4", "Rail drinks")]

SPECIALS = [  # weekday: 0=Sun … 6=Sat (matches JS getDay)
    (1, "Monday", [("All day", "$2 off any burger", "excludes build-your-own & the Big Stooge"),
                   ("Happy Hour 2–5 PM", "$2 off appetizers", "excludes wings"),
                   ("Happy Hour 2–6 PM", "Drink specials", "domestic bottles & pints $3.50 · rail drinks $4")]),
    (2, "Tuesday", [("All day", "Taco Tuesday! 2 tacos for $8", ""),
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
                     ("11 AM–7 PM", "$2 off small pizzas · $3 off large pizzas", ""),
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
     "byo": {"noun": "burger", "photo": ("photos/build-your-own-double-cheeseburger", "A double cheeseburger stacked with lettuce, tomato, red onion and melted cheese on a sesame bun")}, "notes": []},
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
     "byo": {"noun": "sandwich", "base": ("chicken", "Choose your chicken", "", ["Grilled", "Breaded"])}, "notes": []},
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
# Photos shown next to menu items: item name → (image, alt text)
ITEM_PHOTOS = {
    "Nachos": ("photos/food-nachos", "Nachos piled with queso, jalapeños, black olives, lettuce and pico de gallo"),
    "9 oz Boneless Wings": ("photos/food-boneless-wings", "Boneless wings tossed in garlic parmesan sauce with celery sticks"),
    "Big Stooge": ("photos/food-big-stooge-burger", "The Big Stooge: a double burger stacked with bacon, melted cheese and crispy onion strings, with tater tots"),
    "Smash Burger": ("photos/food-smash-burger", "A double smash burger with American cheese, lettuce and tomato, with chips and queso"),
    "Chicken Tender Melt": ("photos/food-chicken-tender-melt", "A chicken tender melt with bacon and cheddar on sourdough toast, with fries"),
}


def item_photo(name):
    if name not in ITEM_PHOTOS:
        return ""
    rel, alt = ITEM_PHOTOS[name]
    return (f'<button class="menu-item__photo" type="button" data-lightbox="/assets/img/{rel}.webp" data-alt="{e(alt)}" '
            f'data-caption="{e(name)}" aria-label="Enlarge photo: {e(name)}">{img(rel, alt, sizes="120px")}</button>')


ADVISORY = ("Consuming raw or undercooked meat, poultry, seafood, shellfish or eggs "
            "may increase your risk of foodborne illness.")


BYO_ICONS = {
    "cheese": '<path d="M3 18 21 8v10H3Z"/><path d="M3 18 13 9.5c2 .3 5.5-1 8-1.5"/><circle cx="15" cy="14.5" r="1.3"/><circle cx="9" cy="15.5" r=".9"/><circle cx="18.5" cy="11.8" r=".8"/>',
    "toppings": '<path d="M4 20c0-9 6.5-16 16-16 0 9.5-7 16-16 16Z"/><path d="M4 20 14 10"/><path d="M9.5 14.5h4.5M12 12V8.5"/>',
    "chicken": '<path d="M15.5 4.5a4.5 4.5 0 0 1 2.6 8.2l-4.3 4.3-3.8-3.8 4.3-4.3A4.5 4.5 0 0 1 15.5 4.5Z"/><path d="m10 13.2-3.3 3.3a2 2 0 1 1-2.2 2.2 2 2 0 1 1 2.2-2.2"/>',
    "bold": '<path d="M12 3c.8 3.6 5 5.4 5 10.5a5 5 0 0 1-10 0c0-2.2 1.2-3.6 2.3-4.5 0 2 1 3.2 2.2 3.4-.4-3.3-.7-6.1.5-9.4Z"/>',
}
BYO_STEPS = [("cheese", "Choose your cheese"), ("toppings", "Add your toppings"), ("bold", "Make it extra bold")]


def byo_card(noun="burger", photo=None, base=None):
    def chip(x):
        if x.endswith("*"):
            return f'<li>{e(x[:-1])}<span class="advisory-mark" aria-hidden="true">*</span></li>'
        return f'<li>{e(x)}</li>'
    steps = "".join(f'''<li class="byo__step">
          <span class="byo__icon"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{BYO_ICONS[key]}</svg></span>
          <div class="byo__step-body"><h4>{e(label)}{f' <span class="byo__price">{e(price)}</span>' if price else ""}</h4>
            <ul class="byo__chips">{"".join(chip(x) for x in items)}</ul></div>
        </li>''' for (key, label), (_, price, items) in ([((base[0], base[1]), (None, base[2], base[3]))] if base else []) + list(zip(BYO_STEPS, BYO)))
    media = (f'<div class="byo__media">{img(photo[0], photo[1], sizes="(max-width:860px) 100vw, 42vw")}</div>' if photo else "")
    return f'''<div class="byo{" byo--photo" if photo else ""}{" byo--4" if base else ""}">
      {media}
      <div class="byo__body">
        <h3 class="byo__title"><span class="byo__title-a">build it</span> <span class="byo__title-b">your way</span></h3>
        <p class="byo__sub">Start with the base, then stack it however you like. Just tell your server when you order. <strong>It's your {e(noun)}.</strong></p>
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
ENTITY_DESC = ("Two Stooges Sports Bar & Grill is a sports bar, billiards hall and darts room at 7178 University Ave NE "
               "in Fridley, Minnesota, in the Twin Cities north metro. Open since 1988, it has 43 pool tables, electronic "
               "dart boards, 34 TV screens and 16 beers on tap.")
AREA_SERVED = ["Fridley", "Columbia Heights", "Spring Lake Park", "New Brighton", "Mounds View", "Coon Rapids", "Blaine", "Minneapolis"]
AWARDS = ["Top Ten Billiard Room in North America", "Best Place to Shoot Pool – City Pages (2017)",
          "Business of the Year", "Billiards Digest “Best of” Architectural Design"]

# key: (path, title ≤60, description 150–160, og source photo, og alt, breadcrumb name)
META = {
    "home": ("/", "Sports Bar, Billiards & Darts - Twin Cities | Two Stooges",
             "Two Stooges is the Twin Cities sports bar for billiards and darts: 43 pool tables, electronic dart boards, 34 screens and 16 taps in Fridley. Plan your visit.",
             "photos/billiard-room-rows", "Rows of pool tables inside Two Stooges Sports Bar in Fridley, MN", None),
    "menu": ("/menu/", "Sports Bar & Grill Menu - Fridley, MN | Two Stooges",
             "The Two Stooges sports bar menu in Fridley: burgers, wings, pizza and Stoogetizers served to your pool table or dart board, with 16 taps. See the full menu.",
             "photos/tenders-and-beer", "Chicken tenders, fries and a cold beer at Two Stooges Sports Bar & Grill", "Menu"),
    "specials": ("/specials/", "Sports Bar Happy Hour & Specials - Fridley | Two Stooges",
                 "Happy hour and daily specials at Two Stooges, the Twin Cities sports bar with billiards and darts: $1 wings Wednesday and $3.50 domestics. See today's deals.",
                 "photos/beers-on-bar", "Ice-cold pints on the bar, happy hour at Two Stooges", "Specials & Happy Hour"),
    "billiards": ("/billiards/", "Billiards & Pool Hall - Twin Cities | Two Stooges",
                  "Shoot pool at Two Stooges, a Twin Cities billiards hall in Fridley with 43 Gabriel's and Diamond tables, daily pool specials, leagues and a Pro Shop. Rack up.",
                  "photos/billiard-room-gabriels-wide", "The 43-table billiard room at Two Stooges Sports Bar in Fridley", "Billiards"),
    "darts": ("/darts/", "Darts & Dart Leagues - Twin Cities | Two Stooges",
              "Throw darts at Two Stooges in Fridley, a Twin Cities sports bar with electronic Bullshooter dart boards, a big screen and dart leagues every day. Sign up today.",
              "photos/dart-room", "Electronic dart boards at Two Stooges Sports Bar in Fridley", "Darts"),
    "leagues": ("/leagues/", "Pool & Dart Leagues - Twin Cities | Two Stooges",
                "Join a pool or dart league at Two Stooges in Fridley, MN: in-house leagues, IBA (M8), APA, UPL and daily dart leagues in the Twin Cities. Sign up online today.",
                "photos/league-night-pool-players", "League night at Two Stooges Sports Bar in Fridley", "Leagues"),
    "signup": ("/league-signup/", "Join a Pool or Dart League - Twin Cities | Two Stooges",
               "Sign up for a pool or dart league at Two Stooges in Fridley, the Twin Cities sports bar for billiards and darts. All skill levels and solo players welcome.",
               "photos/hero-league-signup", "A league player lining up a shot at Two Stooges Sports Bar", "League Sign-Up"),
    "events": ("/events/", "Bar Events & Special Nights - Twin Cities | Two Stooges",
               "Special nights, holiday parties and food and drink events at Two Stooges, the Twin Cities sports bar for billiards and darts in Fridley. See what's next.",
               "photos/billiard-room-hero", "Inside Two Stooges Sports Bar & Grill in Fridley", "Events"),
    "tournaments": ("/tournaments/", "Pool Tournaments - Twin Cities | Two Stooges Sports Bar",
                    "Weekly 8-ball and 9-ball pool tournaments plus FargoRate shootouts at Two Stooges, the Twin Cities billiards hall in Fridley. See dates and sign up today.",
                    "photos/player-shooting", "A tournament player shooting at Two Stooges Sports Bar", "Tournaments"),
    "parties": ("/private-parties/", "Private Party Venue - Twin Cities | Two Stooges Sports Bar",
                "Host a birthday, office party or banquet at Two Stooges, a Twin Cities sports bar in Fridley with custom menus, pool tables and dart boards. Request a date.",
                "photos/hero-private-parties", "Friends playing pool at a party at Two Stooges Sports Bar & Grill in Fridley", "Private Parties"),
    "about": ("/about/", "About Two Stooges: Twin Cities Sports Bar Since 1988",
              "Two Stooges Sports Bar & Grill opened in Fridley in 1988 as University Billiards and grew into a Twin Cities sports bar for billiards and darts. Read our story.",
              "photos/storefront-two-stooges", "The Two Stooges Sports Bar & Grill storefront on University Ave NE, Fridley", "About"),
    "gallery": ("/gallery/", "Photos: Sports Bar, Billiards & Darts | Two Stooges",
                "Photos of Two Stooges, the Twin Cities sports bar in Fridley: the 43-table billiard room, Bullshooter dart boards, center bar and food. Take a look inside.",
                "photos/billiard-room-rows", "Inside the Two Stooges Sports Bar billiard room", "Gallery"),
    "contact": ("/contact/", "Contact & Directions - Fridley, MN | Two Stooges Sports Bar",
                "Contact Two Stooges Sports Bar & Grill, 7178 University Ave NE, Fridley, MN 55432, in the Twin Cities. Call (763) 574-1399. Open daily 11 AM to midnight.",
                "photos/hero-contact-storefront", "Two Stooges Sports Bar & Grill, 7178 University Ave NE, Fridley MN", "Contact"),
    "area": ("/service-area/", "Twin Cities Service Area - Fridley, MN | Two Stooges",
             "Two Stooges Sports Bar in Fridley serves the Twin Cities within about 20 miles. See every community by county, check your city and get directions to the bar.",
             "photos/storefront-two-stooges", "The Two Stooges Sports Bar & Grill storefront on University Ave NE, Fridley", "Service Area"),
    "faq": ("/faq/", "FAQ: Sports Bar, Billiards & Darts | Two Stooges, Fridley",
            "Answers about Two Stooges, the Twin Cities sports bar for billiards and darts in Fridley: hours, pool tables, dart boards, leagues, food and parties. Read more.",
            "photos/billiard-room-gabriels", "The Two Stooges billiard room in Fridley, MN", "FAQ"),
    "eoe": ("/equal-opportunity-employer/", "Equal Opportunity Employer | Two Stooges Sports Bar",
            "Two Stooges Sports Bar & Grill in Fridley, MN is an equal opportunity employer. Read our commitment to fair hiring and a respectful workplace for all employees.",
            "photos/billiard-room-rows", "Two Stooges Sports Bar & Grill", "Equal Opportunity Employer"),
    "privacy": ("/privacy-policy/", "Privacy Policy | Two Stooges Sports Bar",
                "Read the Two Stooges Sports Bar & Grill privacy policy: what information our Fridley, MN website collects through forms and maps, and how we use and protect it.",
                "photos/billiard-room-rows", "Two Stooges Sports Bar & Grill", "Privacy Policy"),
}

PARENT = {}  # page key -> (breadcrumb name, path) of its parent page
CITY_KEY = {n: "city-" + d["slug"] for n, d in CD.CITIES.items()}
COUNTY_KEY = {n: "county-" + d["slug"] for n, d in CD.COUNTIES.items()}
CITY_PATH = {n: f"/service-area/{d['slug']}/" for n, d in CD.CITIES.items()}
COUNTY_PATH = {n: f"/service-area/{d['slug']}/" for n, d in CD.COUNTIES.items()}
_STORE = ("photos/storefront-two-stooges", "The Two Stooges Sports Bar & Grill storefront on University Ave NE, Fridley")
for _n, _d in CD.CITIES.items():
    META[CITY_KEY[_n]] = (CITY_PATH[_n], f"{_n} MN Sports Bar & Pool Hall | Two Stooges", _d["desc"], _STORE[0], _STORE[1], _n)
    PARENT[CITY_KEY[_n]] = ("Service Area", "/service-area/")
for _n, _d in CD.COUNTIES.items():
    META[COUNTY_KEY[_n]] = (COUNTY_PATH[_n], f"{_n} County MN Sports Bar & Pool Hall | Two Stooges", _d["desc"], _STORE[0], _STORE[1], f"{_n} County")
    PARENT[COUNTY_KEY[_n]] = ("Service Area", "/service-area/")

# Related-page cards (descriptive anchors). Silos: Play · Eat & Drink · Plan your visit.
LINK_INFO = {
    "/menu/": ("Two Stooges menu", "Burgers, wings, pizza, Stoogetizers and 16 beers on tap."),
    "/specials/": ("Happy hour & daily specials", "A food or drink deal every day of the week."),
    "/billiards/": ("Billiards in Fridley", "43 tournament tables, pool specials and the Pro Shop."),
    "/darts/": ("Darts at Two Stooges", "Electronic boards and dart leagues every night."),
    "/leagues/": ("Pool & dart leagues", "In-house, IBA (M8), APA, UPL and darts. Sign up online."),
    "/league-signup/": ("League sign-up", "Join a pool or dart league online. Every skill level welcome."),
    "/events/": ("Events & special nights", "Food and drink nights, parties and promotions."),
    "/tournaments/": ("Pool tournaments", "Weekly 8-ball and 9-ball plus FargoRate shootouts."),
    "/private-parties/": ("Private parties", "Birthdays, office parties and banquets with custom menus."),
    "/about/": ("Our story since 1988", "From University Billiards to Two Stooges Sports Bar & Grill."),
    "/gallery/": ("Photo gallery", "Take a look inside the billiard room, dart area and bar."),
    "/faq/": ("Two Stooges FAQ", "Hours, pool tables, leagues, food and parties, answered."),
    "/service-area/": ("Twin Cities service area", "Every community within about 20 miles of Two Stooges, by county."),
    "/contact/": ("Contact & directions", "Address, hours, phone and a map to 7178 University Ave NE."),
}
RELATED = {
    "menu": ["/specials/", "/private-parties/", "/events/"],
    "specials": ["/menu/", "/billiards/", "/events/"],
    "billiards": ["/leagues/", "/tournaments/", "/darts/"],
    "darts": ["/leagues/", "/billiards/", "/private-parties/"],
    "leagues": ["/league-signup/", "/billiards/", "/tournaments/"],
    "signup": ["/leagues/", "/billiards/", "/darts/"],
    "events": ["/private-parties/", "/specials/", "/tournaments/"],
    "tournaments": ["/leagues/", "/billiards/", "/events/"],
    "parties": ["/menu/", "/billiards/", "/darts/"],
    "about": ["/gallery/", "/billiards/", "/contact/"],
    "gallery": ["/about/", "/billiards/", "/darts/"],
    "privacy": ["/contact/", "/about/", "/events/"],
    "eoe": ["/about/", "/contact/", "/faq/"],
    "faq": ["/contact/", "/league-signup/", "/private-parties/"],
    "area": ["/billiards/", "/darts/", "/private-parties/"],
}

FAQ = [
    ("Is Two Stooges in the Twin Cities?",
     'Yes. Two Stooges Sports Bar &amp; Grill is in Fridley, a first-ring suburb in the Minneapolis–Saint Paul (Twin Cities) metro, just north of Minneapolis on University Avenue. It\'s a sports bar with <a href="/billiards/">43 pool tables</a> and <a href="/darts/">electronic dart boards</a> under one roof.',
     "Yes. Two Stooges Sports Bar & Grill is in Fridley, a first-ring suburb in the Minneapolis–Saint Paul (Twin Cities) metro, just north of Minneapolis on University Avenue. It's a sports bar with 43 pool tables and electronic dart boards under one roof."),
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
     'Yes. We run in-house pool leagues as well as IBA (M8), APA and UPL, plus dart leagues every day. <a href="/leagues/">Sign up for a league</a>.',
     "Yes. Two Stooges runs in-house pool leagues as well as IBA (M8), APA and UPL, plus dart leagues every day."),
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
            parts = []
            for suf in ("-sm", "-md"):
                if (IMG / f"{rel}{suf}.webp").exists():
                    vw, _ = dims(f"{rel}{suf}.webp")
                    parts.append(f"/assets/img/{rel}{suf}.webp {vw}w")
            ss = f' srcset="{", ".join(parts + [f"{src} {w}w"])}" sizes="{e(sizes)}"'
    wh = f' width="{w}" height="{h}"' if w else ""
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{src}"{ss}{wh} alt="{e(alt)}"{load}{c}>'


def logo_img(alt, sizes, eager=False):
    """Header/footer logo: 240w copy for 1x/1.75x screens, 400w for 2x+."""
    w, h = dims("brand/two-stooges-logo.webp")
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    return (f'<img src="/assets/img/brand/two-stooges-logo.webp" srcset="/assets/img/brand/two-stooges-logo-240.webp 240w, '
            f'/assets/img/brand/two-stooges-logo.webp {w}w" sizes="{sizes}" width="{w}" height="{h}" alt="{e(alt)}"{load}>')


def flyer_img(rel, alt, sizes):
    """Event flyer with -thumb (240w) and -sm (480w) copies made by images.py."""
    w, h = dims(rel)
    base = rel[:-5]
    parts = [f"/assets/img/{base}{suf}.webp {dims(base + suf + '.webp')[0]}w" for suf in ("-thumb", "-sm") if (IMG / f"{base}{suf}.webp").exists()]
    ss = f' srcset="{", ".join(parts + [f"/assets/img/{rel} {w}w"])}" sizes="{sizes}"' if parts else ""
    return f'<img src="/assets/img/{rel}"{ss} width="{w}" height="{h}" alt="{e(alt)}" loading="lazy" decoding="async">'


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


UPDATED = dt.date.fromisoformat(TODAY).strftime("%B %-d, %Y")

def find_q(question):
    for _, qs in FAQ_GROUPS:
        for q, a in qs:
            if q == question:
                return q, a
    raise KeyError(question)


def page_faq(title, questions, eyebrow="Good to know"):
    """Visible FAQ block built from the same answers as /faq/ (FAQPage schema stays on /faq/ only)."""
    items = "".join(f'<details class="faq"><summary><h3>{e(q)}</h3></summary><p>{a}</p></details>'
                    for q, a in map(find_q, questions))
    return f'''<section class="section section--alt"><div class="wrap" style="max-width:900px">
  {section_head(eyebrow, title, f"More answers in the {L('/faq/', 'full Two Stooges FAQ')}.")}
  <div class="faq-list">{items}</div>
</div></section>'''


def term_table(title, intro, rows, eyebrow="Terms to know"):
    """Keyword and entity table: (term, what it means, at Two Stooges). Cells are trusted HTML."""
    body = "".join(f'<tr><th scope="row">{t}</th><td>{m}</td><td>{w}</td></tr>' for t, m, w in rows)
    return f'''<section class="section"><div class="wrap">
  {section_head(eyebrow, title, intro)}
  <div class="table-scroll"><table class="term-table">
    <thead><tr><th scope="col">Term</th><th scope="col">What it means</th><th scope="col">At Two Stooges</th></tr></thead>
    <tbody>{body}</tbody>
  </table></div>
</div></section>'''


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
    <a class="brand" href="/">{logo_img("Two Stooges Sports Bar & Grill, Fridley MN – home", "(max-width: 900px) 120px, 150px", eager=True)}</a>
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
    return f'''<footer class="site-footer on-dark">
  {rail()}
  <div class="wrap">
    <div class="footer-grid" style="padding-top:3rem">
      <div class="footer-brand">
        {logo_img("Two Stooges Sports Bar & Grill", "190px")}
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
          <li><a href="/leagues/">Leagues</a></li>
          <li><a href="/tournaments/">Tournaments</a></li>
          <li><a href="/league-signup/">League Sign-Up</a></li>
          <li><a href="/events/">Events</a></li>
          <li><a href="/private-parties/">Private Parties</a></li>
          <li><a href="/service-area/">Service Area</a></li>
        </ul>
      </div>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>© <span data-year>2026</span> {e(BIZ["name"])} · Information updated {UPDATED}</span>
    <span><a href="/faq/">FAQ</a> · <a href="/privacy-policy/">Privacy Policy</a> · <a href="/equal-opportunity-employer/">Equal Opportunity Employer</a> · Website by Multimedia Graphics · <a class="footer-admin" href="/admin/" rel="nofollow">Admin</a></span>
  </div>
</footer>
<nav class="action-bar" aria-label="Quick actions">
  <a href="tel:{BIZ["tel"]}">{icon("phone")}Call</a>
  <a href="{DIRECTIONS}" target="_blank" rel="noopener">{icon("nav")}Directions</a>
  <a href="/events/">{icon("calendar")}Events</a>
</nav>
<dialog id="lightbox" class="lightbox" aria-label="Image viewer">
  <button class="lightbox__close" type="button" aria-label="Close image">×</button>
  <button class="lightbox__nav lightbox__nav--prev" type="button" aria-label="Previous photo">‹</button>
  <figure class="lightbox__stage"><img src="data:," alt=""><figcaption><p></p><span class="lightbox__count" aria-live="polite"></span></figcaption></figure>
  <button class="lightbox__nav lightbox__nav--next" type="button" aria-label="Next photo">›</button>
</dialog>'''


AWARDS_VISIBLE = AWARDS
AMENITIES = ["43 pool tables", "6 dart boards", "Pool leagues", "30 HD TVs and 4 monster screens", "NFL Sunday Ticket",
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
        x["keywords"] = "sports bar, billiards, pool tables, darts, dart leagues, pool leagues, Twin Cities, Fridley"
        x["description"] = ENTITY_DESC
    if key in ("home", "menu"):
        x["servesCuisine"] = "American"
    return x


def first_lead(body):
    m = re.search(r'<p class="lead">(.*?)</p>', body, re.S)
    return SG.strip(m.group(1)) if m else ""


BILLIARDS_OFFERS = [{"@type": "Offer", "name": f"Daily pool special – {n}", "price": p, "priceCurrency": "USD",
                     "description": "Table time, 11 AM–5 PM daily, plus tax"} for n, p in (("regular", "12"), ("seniors", "11"))] + [
    {"@type": "Offer", "name": "Lunch special – 1 free hour of pool", "price": "0", "priceCurrency": "USD",
     "description": "1 free hour of pool with lunch purchase, Monday–Friday 11 AM–5 PM"}]


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
        nodes.append(SG.breadcrumb_node(path, crumb, PARENT.get(key)))
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
<link rel="preload" href="/assets/fonts/oswald-latin-var-v5.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/inter-latin-var-v5.woff2" as="font" type="font/woff2" crossorigin>
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


def hero_media(image, alt):
    """Banner image; when a tall <image>-mobile.webp exists, phones get that crop instead."""
    tag = img(image, alt, eager=True)
    mob = f"{image}-mobile.webp"
    if (IMG / mob).exists():
        mw, mh = dims(mob)
        return f'<picture><source media="(max-width: 700px)" srcset="/assets/img/{mob}" width="{mw}" height="{mh}">{tag}</picture>'
    return tag


def page_hero(key, eyebrow, title, lead, image, alt, actions=""):
    crumb = META[key][5]
    par = PARENT.get(key)
    mid = f'<li><a href="{par[1]}">{e(par[0])}</a></li>' if par else ""
    return f'''<section class="page-hero page-hero--{key} on-dark">
  <div class="page-hero__media">{hero_media(image, alt)}</div>
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li>{mid}<li aria-current="page">{e(crumb)}</li></ol></nav>
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
  {section_head("Find us", title, f"We're on University Avenue NE (Highway 47) in Fridley, just north of Minneapolis. {PL.STATEMENT} {L('/service-area/', 'See our service area')}. Walk-ins are always welcome. Planning ahead? {L('/private-parties/', 'Reserve space for a group')}.")}
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
def upcoming(kind):
    """Dated entries still to come (soonest first) and weekly entries (always shown)."""
    dated = sorted((x for x in ENTRIES[kind] if not x["weekly"] and x["date"] >= TODAY), key=lambda x: x["sort"])
    return dated, [x for x in ENTRIES[kind] if x["weekly"]]


def past(kind):
    return sorted((x for x in ENTRIES[kind] if not x["weekly"] and x["date"] < TODAY), key=lambda x: x["sort"], reverse=True)


def flyer_button(ev, sizes, cls="event__flyer"):
    if not ev["photo"]:
        return ""
    big = f"/assets/img/{ev['photo']}"
    return (f'<button class="{cls}" type="button" data-lightbox="{big}" data-alt="{e(ev["photo_alt"])}" '
            f'data-caption="{e(ev["title"])} · {e(ev["when"])}" aria-label="View full flyer: {e(ev["title"])}">'
            f'{flyer_img(ev["photo"], ev["photo_alt"], sizes)}</button>')


def listing(ev):
    """One event/tournament card: H2 title, date & time right under it, short description, then details."""
    facts = "".join(f'<div class="fact"><span class="fact__label">{e(k)}</span><span class="fact__value">{e(v)}</span></div>'
                    for k, v in ev["facts"])
    acts = []
    if ev["contact_phone"]:
        tel = "+1" + re.sub(r"\D", "", ev["contact_phone"])[-10:]
        who = f'Call or text {ev["contact_name"]}' if ev["contact_name"] else "Call or text"
        acts.append(btn(f'{who}: {ev["contact_phone"]}', "tel:" + tel, "gold", "phone"))
    else:
        lead = "Call to sign up: " if ev["kind"] == "tournaments" else "Questions? Call "
        acts.append(btn(lead + BIZ["phone"], "tel:" + BIZ["tel"], "gold", "phone"))
    if ev["link"]:
        lbl = ev["link_label"] or ("Bracket & registration" if ev["kind"] == "tournaments" else "More info")
        acts.append(f'<a class="text-link" href="{e(ev["link"])}" target="_blank" rel="noopener">{e(lbl)}</a>')
    acts.append('<a class="text-link" href="/contact/">Directions to Two Stooges</a>')
    end_attr = "" if ev["weekly"] else f' data-event-end="{ev["date"]}" data-past-card="past-{ev["id"]}"'
    cls = "event event--feature" + ("" if ev["photo"] else " event--nophoto")
    desc = ""
    if ev["desc_title"]:
        desc += f'<h3 class="event__subtitle">{e(ev["desc_title"])}</h3>'
    if ev["body"]:
        paras = [p_ for p_ in re.split(r"\n\s*\n", ev["body"]) if p_.strip()]
        desc += "".join(f'<p class="event__desc">{"<br>".join(e(x.strip()) for x in p_.splitlines() if x.strip())}</p>' for p_ in paras)
    fx = f'<div class="event__facts">{facts}</div>' if facts else ""
    note = f'<p class="event__note">{e(ev["note"])}</p>' if ev["note"] else ""
    out = (f'<article class="{cls}" id="{ev["id"]}"{end_attr}>\n  {flyer_button(ev, "(max-width:820px) min(380px, 100vw), 320px")}\n'
           f'  <div>\n    <h2 class="event__title">{e(ev["title"])}</h2>\n'
           f'    <p class="event__when">{icon("calendar")}<span>{e(ev["when"])}</span></p>\n'
           f'    {desc}\n    {fx}\n    {note}\n    <div class="event__contact">{"".join(acts)}</div>\n  </div>\n</article>')
    if not ev["weekly"]:
        out += f'\n<template id="past-{ev["id"]}">{past_card(ev)}</template>'
    return out


def past_card(ev):
    media = flyer_button(ev, "(max-width:640px) 50vw, 260px", cls="past-card__flyer") or '<div class="past-card__blank" aria-hidden="true"></div>'
    chip = "Past tournament" if ev["kind"] == "tournaments" else "Past event"
    return (f'<article class="past-card">\n  {media}\n  <div><span class="chip">{chip}</span>'
            f'<h3>{e(ev["title"])}</h3><p>{e(ev["date_label"])}</p></div>\n</article>')


def game_thing(ev):
    g = " ".join(v for k, v in ev["facts"] if k == "Game") + " " + ev["title"]
    for key, pat in (("eightball", r"\b8[- ]?ball"), ("nineball", r"\b9[- ]?ball"), ("tenball", r"\b10[- ]?ball")):
        if re.search(pat, g, re.I):
            return SG.thing(key)
    return SG.thing("pool")


def entry_ld(ev):
    page_url = SITE + ENTRY_PAGE[ev["kind"]]
    d = {"@type": "Event", "@id": page_url + "#" + ev["id"], "name": ev["title"],
         "eventStatus": "https://schema.org/EventScheduled",
         "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
         "url": page_url + "#" + ev["id"], "location": {"@id": SG.BID}, "organizer": {"@id": SG.BID}}
    if ev["description"]:
        d["description"] = ev["description"]
    if ev["photo"]:
        d["image"] = [SITE + "/assets/img/" + ev["photo"]]
    if ev["kind"] == "tournaments":
        d["about"] = game_thing(ev)
    if ev["weekly"]:
        sched = {"@type": "Schedule", "byDay": "https://schema.org/" + ev["day"], "repeatFrequency": "P1W",
                 "scheduleTimezone": "America/Chicago"}
        if ev["start"]:
            sched["startTime"] = ev["start"]
        d["eventSchedule"] = sched
        return d
    d["startDate"] = ev["start_iso"]
    if ev.get("end_iso"):
        d["endDate"] = ev["end_iso"]
    if ev.get("door_iso"):
        d["doorTime"] = ev["door_iso"]
    if ev.get("price"):
        d["offers"] = {"@type": "Offer", "price": ev["price"], "priceCurrency": "USD", "url": d["url"],
                       "availability": "https://schema.org/InStock", "validFrom": TODAY}
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
    ups = upcoming("tournaments")[0] + upcoming("events")[0]
    nxt = min(ups, key=lambda x: x["sort"]) if ups else None
    next_card = ""
    if nxt:
        thumb = flyer_img(nxt["photo"], nxt["photo_alt"], "84px") if nxt["photo"] else ""
        meta_line = " · ".join(v for k, v in nxt["facts"][:2])
        more = "Tournament details" if nxt["kind"] == "tournaments" else "Event details"
        next_card = f'''<aside class="next-up" data-next-up="{nxt["date"]}" aria-label="Next event at Two Stooges">
        <div class="next-up__label">{icon("calendar")}Next up · {e(nxt["short_date"])}</div>
        <div class="next-up__body{"" if thumb else " next-up__body--text"}">
          {thumb}
          <div>
            <p class="next-up__title">{e(nxt["title"])}</p>
            <p>{e(nxt["when"].split(" · ", 1)[-1] if nxt["start"] else nxt["when"])}{(" · " + e(meta_line)) if meta_line else ""}</p>
            <a class="text-link" href="{ENTRY_PAGE[nxt["kind"]]}#{nxt["id"]}">{more}</a>
          </div>
        </div>
      </aside>'''

    pillars = [
        ("photos/home-card-billiards-rack", "A racked set of pool balls on blue felt at Two Stooges in Fridley", "43 tables", "Billiards", "/billiards/",
         f"Gabriel's and Diamond tables in 9 ft and 7 ft, {L('/specials/#pool', 'daily pool specials')} and a full Pro Shop.", "Explore the billiard room"),
        ("photos/home-card-darts-bullseye", "A blue-flighted dart in the bullseye of a dartboard, with warm bar lights behind", "Leagues every day", "Darts", "/darts/",
         f"Electronic dart boards, high-tops and {L('/leagues/', 'dart leagues')} for every skill level.", "See the dart area"),
        ("photos/home-card-leagues-billiard-room", "Rows of blue-felt Diamond pool tables with players at the tables in the Two Stooges billiard room", "Weekly play", "Leagues & Tournaments", "/leagues/",
         f"In-house leagues as well as IBA (M8), APA and UPL, plus {L('/tournaments/', 'FargoRate Tournaments')}.", "Join a pool league"),
        ("photos/home-card-private-parties", "A group of friends cheering as one of them lines up a shot at the pool table", "Groups welcome", "Private Parties", "/private-parties/",
         f"Birthdays, office parties and banquets with {L('/menu/', 'custom menus')} and pool tables included.", "Plan a private party"),
    ]
    cards = "".join(f'''<article class="card card--link">
      <div class="card__media">{img(i, a, sizes="(max-width:640px) 100vw, (max-width:1000px) 50vw, 25vw")}</div>
      <div class="card__body"><span class="card__kicker">{k}</span><h3>{t}</h3><p>{d}</p><a class="text-link" href="{h}">{l}</a></div>
    </article>''' for i, a, k, t, h, d, l in pillars)

    spec_html = "".join(deal_card(r) for r in DAY_DEALS if r[0] in (1, 2, 3, 5, 6, 0))

    picks = [("Big Stooge", "19", "Two black Angus patties, three cheeses, four strips of bacon, onion strings, A-1, honey BBQ and garlic basil aioli.", ["raw", "signature"]),
             ("Duck Bacon Wontons", "16", "Crispy wontons with spicy plum sauce.", []),
             ("8 Bone-In Wings", "15", "Fresh, never frozen. Try them in our Signature Sauce.", ["signature"]),
             ("Walleye Sandwich", "19", "Battered walleye, lettuce, American cheese and tartar on a toasted hoagie.", ["signature"])]
    picks_html = "".join(f'''<li class="menu-item"><h3>{e(n)} {tag_chips(t)}</h3><span class="menu-item__price">${p}</span><p>{e(d)}</p></li>''' for n, p, d, t in picks)

    quotes = "".join(f'''<figure class="quote"><div class="quote__stars" role="img" aria-label="{r} out of 5 stars">{"★" * r}{"☆" * (5 - r)}</div><blockquote>{e(q)}</blockquote><figcaption><span class="quote__avatar">{e(n[0])}</span><span>{e(n)}<small>Google review</small></span></figcaption></figure>''' for q, n, r in REVIEWS)
    faqs = "".join(f'<details class="faq"><summary><h3>{e(q)}</h3></summary><p>{a}</p></details>' for q, a, _ in FAQ)

    body = f'''<section class="hero hero--full on-dark">
  <picture class="hero__bg">
    <source media="(max-width: 700px)" srcset="/assets/img/photos/hero-pool-tables-mobile.webp" width="720" height="900">
    <img src="/assets/img/photos/hero-pool-tables-1536.webp" srcset="/assets/img/photos/hero-pool-tables-1280.webp 1280w, /assets/img/photos/hero-pool-tables-1536.webp 1536w" sizes="100vw" width="1536" height="640" alt="The Two Stooges billiard room in Fridley, MN: rows of blue-felt Gabriel's pool tables under wood-trimmed lights, with the bar behind" fetchpriority="high">
  </picture>
  <div class="wrap hero__inner">
    <div class="hero__copy">
      <span class="hero__badge">{icon("pin")}Fridley, MN · Since 1988</span>
      <h1>Two Stooges Sports Bar: <span class="grad-text">billiards &amp; darts</span> in the Twin Cities</h1>
      <p class="lead">The most fun you can have under one roof. Two Stooges Sports Bar &amp; Grill has been the Twin Cities spot for pool and darts since 1988: 43 pool tables, electronic dart boards, 16 ice-cold taps and a full bar &amp; grill in Fridley.</p>
      <div class="btn-row">{btn("Upcoming Events", "/events/", "gold", "calendar")}{btn("See the Menu", "/menu/", "outline")}</div>
      <div class="stat-row">
        <div><span class="stat__num">43</span><span class="stat__label">Pool tables</span></div>
        <div><span class="stat__num">6</span><span class="stat__label">Dart boards</span></div>
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
    <li><a href="/billiards/">{icon("ball")}<span>43 Pool Tables</span></a></li>
    <li><a href="/darts/">{icon("target")}<span>6 Dart Boards</span></a></li>
  </ul>
</div></section>

<section class="section"><div class="wrap">
  {section_head("Pick your game", "Billiards, darts &amp; a sports bar under one roof", f"Two Stooges is the Twin Cities' all-in-one sports bar, restaurant and {L('/billiards/', 'billiard room')}, with {L('/darts/', 'electronic dart boards')} in Fridley. Come for one game and stay for all of them. {L('/gallery/', 'See photos of the room')} or {L('/contact/', 'get directions')}.", center=True)}
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
      {img(*ITEM_PHOTOS["Big Stooge"], sizes="(max-width:860px) 100vw, 50vw")}
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
    return page("home", body, extra_ld=([entry_ld(nxt)] if nxt else []), og_type="business.business")


def p_menu():
    tabs = "".join(f'<button class="menu-tab" type="button" role="tab" id="tab-{s["id"]}" aria-controls="{s["id"]}" aria-selected="{"true" if i == 0 else "false"}"{"" if i == 0 else " tabindex=\"-1\""}>{e(s["name"])}</button>' for i, s in enumerate(MENU))
    panels = []
    for i, s in enumerate(MENU):
        items = "".join(f'''<li class="menu-item{" menu-item--photo" if n in ITEM_PHOTOS else ""}">{item_photo(n)}<h3>{e(n)} {tag_chips(t)}</h3><span class="menu-item__price">${e(p)}</span><p>{d}</p></li>''' for n, p, d, t in s["items"])
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
    body = f'''{page_hero("menu", "Eat &amp; drink", "The Two Stooges Sports Bar <span class='grad-text'>menu</span> in Fridley, MN",
        f"Classic American bar and grill food with our own twist, served in Fridley every day from 11 AM. There are burgers, wings, pizza, sandwiches and entrées, plus 16 beers on tap. Check the {L('/specials/', 'daily specials')} before you order.",
        "photos/tenders-and-beer", "Crispy chicken tenders and fries next to an ice-cold pint of beer on a wood table", btn("Today's Specials", "/specials/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  <div class="menu-tabs" role="tablist" aria-label="Menu categories">{tabs}</div>
  {"".join(panels)}
  <p class="small muted mt-2">{e(MENU_DISCLAIMER)} Planning a group meal? We put together {L("/private-parties/", "custom party menus")}.</p>
</div></section>
<section class="section section--tight food-photos"><div class="wrap">
  {section_head("From the kitchen", "Fresh off the Two Stooges grill", f"A look at what's coming out of the kitchen. Find your favorites on the menu above, and check the {L('/specials/', 'daily specials')} for deals. We'll bring it to you while you shoot {L('/billiards/', 'pool')}, throw {L('/darts/', 'darts')} or play in a {L('/leagues/', 'league')}.")}
  <div class="food-grid food-grid--5">
    {"".join(f'<figure class="gallery__item food-grid__item"><button type="button" data-lightbox="/assets/img/{p_}.webp" data-alt="{e(a_)}" data-caption="" aria-label="Enlarge photo: {e(a_)}">{img(p_, a_, sizes="(max-width:640px) 50vw, 33vw")}</button></figure>' for p_, a_ in [
        *ITEM_PHOTOS.values()])}
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
{cta_band("Feeding a crowd in Fridley?", f"We put together custom menus for birthdays, office parties and banquets. {L('/faq/', 'See party and food FAQs')}.", btn("Plan a Private Party", "/private-parties/", "gold"))}'''
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
    body = f'''{page_hero("specials", "Daily deals", "Two Stooges Sports Bar <span class='grad-text'>specials &amp; happy hour</span> in Fridley, MN",
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
        <p class="deal-card__price">$12 <span>table time</span></p>
        <p class="deal-card__note">Seniors $11 · <strong>11 AM–5 PM</strong></p>
        <ul class="deal-card__extras"><li><span>Mon–Fri 11 AM–5 PM</span>Lunch special: 1 free hour of pool with lunch purchase</li></ul>
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
      <div class="pool-prices">
        <div class="pool-price"><span class="pool-price__lbl">Regular</span><span class="pool-price__num">$12</span></div>
        <div class="pool-price"><span class="pool-price__lbl">Seniors</span><span class="pool-price__num">$11</span></div>
        <div class="pool-price pool-price--hot pool-price--lunch"><span class="pool-price__lbl">Lunch special<small>Mon–Fri 11 AM–5 PM</small></span><span class="pool-price__num">1 free hour<small>of pool with lunch purchase</small></span></div>
        <p class="pool-prices__note">Plus tax · every day 11 AM–5 PM</p>
      </div>
    </div>
  </div>
</section>
{page_faq("Specials questions at Two Stooges in Fridley", ["When is happy hour?", "How many beers are on tap?", "What food does Two Stooges serve?", "What are the hours at Two Stooges?"])}
{cta_band("Celebrating a birthday?", "Bring the crew. We'll set you up with tables, food and drinks for your group.", btn("Book a Party", "/private-parties/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}'''
    return page("specials", body)


def p_billiards():
    gallery = [("photos/billiard-room-trophy-rail", "Players at the Gabriel's tables, seen from the rail under the trophy case and flag"),
               ("photos/billiard-room-gabriels-rows", "Rows of blue-felt Gabriel's tables under wood-trimmed lights"),
               ("photos/billiard-room-diamond-apa", "Diamond tables, including an APA tournament table, with the dart boards behind"),
               ("photos/billiard-room-diamond-lounge", "Diamond tables and high-top seating in the Two Stooges billiard room")]
    g = "".join(f'<figure class="gallery__item"><button type="button" data-lightbox="/assets/img/{p}.webp" data-alt="{e(a)}" data-caption="{e(a)}" aria-label="Enlarge photo: {e(a)}">{img(p, a, sizes="(max-width:640px) 100vw, 33vw")}</button></figure>' for p, a in gallery)
    body = f'''{page_hero("billiards", "43 tables · since 1988", "Billiards at Two Stooges Sports Bar in the <span class='grad-text'>Twin Cities</span>",
        "Two Stooges, in Fridley, has been named a top ten billiard room in North America, and City Pages voted it the best place to shoot pool in the Twin Cities. There are 43 Gabriel's and Diamond tables in 9 ft and 7 ft, with room for league players, casual groups and first-timers around every one.",
        "photos/billiard-room-gabriels-wide", "The Two Stooges billiard room in Fridley: rows of blue-felt Gabriel's pool tables under wood-trimmed lights, with players at the tables", btn("Daily Pool Specials", "#rates", "gold") + btn("Join a Pool League", "/leagues/", "outline"))}
<section class="section"><div class="wrap">
  {section_head("The billiard room", "The Twin Cities' award-winning pool hall", f"Pool has been the heart of Two Stooges since 1988, when it opened as University Billiards. {L('/about/', 'Read the full story')}.")}
  <div class="grid grid--3">
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>43 tournament tables</h3><p>9 ft and 7 ft Gabriel's and Diamond tables on Simonis 860 cloth, with good lighting and comfortable seating at every table.</p></div>
    <div class="tile"><span class="tile__icon">{icon("trophy")}</span><h3>Leagues &amp; tournaments</h3><p>{L("/leagues/", "In-house leagues")} as well as IBA (M8), APA and UPL, plus {L("/tournaments/", "FargoRate Tournaments")}.</p></div>
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
      <ul class="price-list">
        <li><span>Regular</span><span class="price">$12</span></li>
        <li><span>Seniors</span><span class="price">$11</span></li>
      </ul>
      <p class="mt-1"><strong>Lunch Special:</strong> 1 free hour of pool with lunch purchase, Mon–Fri 11 AM–5 PM.</p>
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
    <div class="tile"><h3>Weekly pool leagues</h3><p>Call <a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a> or contact us at <a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a> about our In-House leagues, or visit our partner leagues' websites:</p><ul class="check-list"><li><a href="https://www.ibapool.com/" target="_blank" rel="noopener">IBA (M8)</a></li><li><a href="https://poolplayers.com/" target="_blank" rel="noopener">APA</a></li><li><a href="https://league.ultimatepoolusa.com/ultimatepool/leagues" target="_blank" rel="noopener">UPL</a></li></ul><a class="text-link" href="/leagues/">Pool league details &amp; sign-up</a></div>
    <div class="tile"><h3>Tournaments</h3><p>A variety of tournaments on 7ft and 9ft tables. Spots fill fast, so sign up early.</p><a class="text-link" href="/tournaments/">Upcoming pool tournaments</a></div>
  </div>
</div></section>
<section class="section section--alt" id="pro-shop"><div class="wrap">
  <div class="split split--rev">
    <div class="split__media">{img("photos/pro-shop-counter-cue-wall", "The Two Stooges Pro Shop: glass display cases of cue accessories, a wall of pool cues and cue cases, and the billiard counter, with the pool tables beyond", sizes="(max-width:860px) 100vw, 50vw")}<div class="split__badge">Cues &amp; Stuff<small>Pro Shop · cue repair</small></div></div>
    <div>
      <span class="eyebrow">Pro Shop</span>
      <h2>Two Stooges Pro Shop <span class="grad-text">&amp; cue repair</span></h2>
      <p class="lead">Our Pro Shop carries cues and accessories for pool, and we do cue repair on site.</p>
      <ul class="check-list"><li>Cues &amp; cases</li><li>Chalk, gloves &amp; accessories</li><li>Cue repair</li></ul>
      {btn("Call the Pro Shop", "tel:" + BIZ["tel"], "outline", "phone")}
    </div>
  </div>
</div></section>
<section class="section"><div class="wrap">
  {section_head("The room", "Inside the Two Stooges billiard room", f"More photos in the {L('/gallery/', 'Two Stooges photo gallery')}.")}
  <div class="photo-grid">{g}</div>
</div></section>
{term_table("Pool hall terms at Two Stooges", "The table brands, sizes and league names you'll hear in the billiard room.", [
    ("Gabriel's tables", "Tournament pool tables from the Belgian maker Gabriels.", "9 ft and 7 ft Gabriel's tables in the billiard room."),
    ("Diamond tables", "Pool tables from Diamond Billiard Products, widely used for league and tournament play.", "Diamond tables, including an APA tournament table."),
    ("Simonis 860", "A worsted wool pool cloth made by Iwan Simonis.", "The cloth on our tables."),
    ("9 ft table", "The full-size table used for professional play.", f"Used for our {L('/tournaments/', 'pool tournaments')} along with the 7 ft tables."),
    ("7 ft table (bar box)", "The smaller table size most bar leagues play on.", "Used for bar box shootouts."),
    ("FargoRate", "A rating system that ranks pool players from their game results.", f"Our {L('/tournaments/', 'FargoRate tournaments')} set a rating limit for entry."),
    ("IBA (M8), APA, UPL", "Pool league organizations with handicapped team play.", f"All three run {L('/leagues/', 'pool leagues at Two Stooges')}."),
])}
{page_faq("Billiards questions at Two Stooges in Fridley", ["How many pool tables does Two Stooges have?", "How do I rent a pool table?", "Is there a pro shop?", "Does Two Stooges host pool tournaments?"])}
{cta_band("Host your event on the tables", "Birthdays, draft parties, office parties, celebrations of life and banquets. We'll customize the menu and the room for you.", btn("Plan a Private Party", "/private-parties/", "gold"))}'''
    return page("billiards", body)


def p_darts():
    body = f'''{page_hero("darts", "Darts at Stooges", "Darts at Two Stooges Sports Bar in the <span class='grad-text'>Twin Cities</span>",
        f"Electronic Bullshooter dart boards, high-top tables and a big screen in Fridley, just north of Minneapolis. Bring friends for a casual game or join one of our {L('/leagues/', 'dart leagues')}, which run every day of the week.",
        "photos/dart-bullseye-neon", "A dart hitting the bullseye under colorful bar lights", btn("Join a Dart League", "/league-signup/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  <div class="split">
    <div class="split__media">{img("photos/two-stooges-electronic-dart-boards", "Two Stooges Electronic Dart Boards", sizes="(max-width:860px) 100vw, 50vw")}</div>
    <div>
      <span class="eyebrow">The dart area</span>
      <h2>Electronic dart boards <span class="grad-text">in Fridley</span></h2>
      <p class="lead">Our dart area has a row of electronic boards, high-tops for your crew and a big screen showing the game. It's right next to the {L("/billiards/", "billiard room")}, so your group can switch between pool and darts all night.</p>
      <ul class="check-list"><li>Electronic dart boards</li><li>High-top seating right by the boards</li><li>Food and drinks from the {L("/menu/", "Two Stooges menu")} delivered to your table</li></ul>
    </div>
  </div>
</div></section>
{term_table("Dart terms at Two Stooges", "What to know before your first game on our boards.", [
    ("Electronic dart board", "A board that keeps score automatically as each dart lands.", "6 electronic boards in the dart area."),
    ("Bullshooter", "A line of electronic dart boards made by Arachnid.", "The boards we play on."),
    ("Dart league", "A weekly schedule of matches between teams or players.", f"{L('/leagues/', 'Dart leagues')} run every day of the week."),
    ("Custom league", "A league set up for a particular group.", f"We set up leagues for women, couples and teams. {L('/league-signup/', 'Sign up online')}."),
])}
{page_faq("Darts questions at Two Stooges in Fridley", ["How many dart boards are there?", "Does Two Stooges have pool and dart leagues?", "Do I need a team to join a league?", "What skill level do I need?"])}
{cta_band("Dart night for your group?", f"Birthdays, office outings and team nights. We'll reserve boards and put together food for your group. {L('/gallery/', 'See the dart room in our gallery')}.", btn("Plan a Private Party", "/private-parties/", "gold"))}'''
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
    body = f'''{page_hero("leagues", "Pool &amp; dart leagues", "Pool &amp; dart leagues at <span class='grad-text'>Two Stooges Sports Bar</span> in Fridley, MN",
        f"Leagues at Two Stooges are a great way to meet other pool and dart players in Fridley and across the Twin Cities, and sharpen your skills. There's a league for every skill level on our {L('/billiards/', '43 tables')} and {L('/darts/', 'dart boards')}.",
        "photos/league-night-pool-players", "League night at Two Stooges in Fridley: pool league players in team shirts at rows of blue-felt Diamond tables", btn("Sign Up Online", "/league-signup/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section section--alt"><div class="wrap">
  {section_head("More leagues", "IBA (M8), APA, UPL &amp; dart leagues in the Twin Cities")}
  <div class="grid grid--4">
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>IBA (M8)</h3><p>We host IBA (M8) pool leagues. <a href="https://www.ibapool.com/" target="_blank" rel="noopener">Visit the IBA website</a>.</p></div>
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>APA &amp; UPL</h3><p>We host APA and UPL handicapped pool leagues, open to all skill levels. Visit <a href="https://poolplayers.com/" target="_blank" rel="noopener">APA</a> or <a href="https://league.ultimatepoolusa.com/ultimatepool/leagues" target="_blank" rel="noopener">UPL</a>.</p></div>
    <div class="tile"><span class="tile__icon">{icon("ball")}</span><h3>In-house 8-Ball</h3><p>Our own handicapped 8-ball league, a great first league for newer players.</p></div>
    <div class="tile"><span class="tile__icon">{icon("target")}</span><h3>Dart leagues</h3><p>Leagues every day of the week, plus custom leagues for women, couples and teams. {L("/darts/", "See the dart area")}.</p></div>
  </div>
  <p class="mt-2 muted">Looking for more competition? Check the {L("/tournaments/", "upcoming pool tournaments")}: weekly 8-ball and 9-ball plus FargoRate shootouts.</p>
</div></section>
{term_table("League terms at Two Stooges", "The league names and formats you'll see on the sign-up form.", [
    ("In-house league", "A league run by the venue itself.", "Our own handicapped 8-ball league, a good first league for newer players."),
    ("Handicapped league", "A league that adjusts scoring by skill so newer and experienced players compete on even terms.", "Most of our leagues are handicapped."),
    ("IBA (M8)", "A pool league organization.", 'We host IBA (M8) leagues. <a href="https://www.ibapool.com/" target="_blank" rel="noopener">IBA website</a>.'),
    ("APA", "The American Poolplayers Association, a handicapped pool league.", 'We host APA leagues. <a href="https://poolplayers.com/" target="_blank" rel="noopener">APA website</a>.'),
    ("UPL", "Ultimate Pool's league program.", 'We host UPL leagues. <a href="https://league.ultimatepoolusa.com/ultimatepool/leagues" target="_blank" rel="noopener">UPL website</a>.'),
    ("FargoRate", "A rating system that ranks pool players from their game results.", f"Used to set entry limits for our {L('/tournaments/', 'FargoRate tournaments')}."),
])}
{page_faq("League questions at Two Stooges in Fridley", ["Does Two Stooges have pool and dart leagues?", "Do I need a team to join a league?", "What skill level do I need?", "Does Two Stooges host pool tournaments?"])}
{cta_band("Ready to join a league?", f"Sign up online in a couple of minutes. Solo players are welcome, and we'll help you find a team. Check {L('/specials/', 'league-night drink specials')}, the {L('/menu/', 'bar and grill menu')} and our {L('/faq/', 'league FAQ')}, or {L('/private-parties/', 'book your end-of-season party')}.", btn("League Sign-Up", "/league-signup/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}'''
    return page("leagues", body)


LEAGUE_FAQ = [
    ("Do I need a team to join a league?", "No. Solo players are welcome. Sign up and we'll help place you on a team or league night."),
    ("What skill level do I need?", "Any. Most of our leagues are handicapped, so beginners and experienced players can compete on even terms."),
    ("Which leagues can I join?", "In-house pool leagues as well as IBA (M8), APA and UPL, plus dart leagues every day of the week."),
    ("Can I sign up by phone?", "Yes. Call (763) 574-1399 and a team member will sign you up."),
]


def p_signup():
    benefits = [
        ("users", "Meet your people", "League night is the easiest way to meet other pool and dart players in Fridley and the north metro."),
        ("trophy", "Compete for Prizes & Bragging Rights", "Play for standings and prizes all season, and get ready for our FargoRate tournaments."),
        ("ball", "Every skill level", "Most leagues are handicapped, so newer players and sharks can play together, and every match is competitive."),
        ("target", "Get better every week", "Regular match play against new opponents sharpens your game faster than practice alone."),
        ("calendar", "A standing night out", "Same night, same crew, every week. It's a built-in reason to get out of the house."),
        ("award", "Play on tournament tables", "Pool Leagues are played on 7ft and 9ft tables in a room named a top ten billiard room in North America."),
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
    body = f'''{page_hero("signup", "League sign-up", "Join a league at <span class='grad-text'>Two Stooges Sports Bar</span> in Fridley, MN",
        f"Sign up for a pool or dart league in Fridley. We have handicapped leagues for every skill level on our {L('/billiards/', '43 tables')} and {L('/darts/', 'dart boards')}. Solo players are welcome.",
        "photos/hero-league-signup", "Players racking and waiting their turn at blue-felt Gabriel\'s tables in the Two Stooges billiard room in Fridley", btn("Sign Up Now", "#form", "gold", "trophy") + btn("See All Leagues", "/leagues/", "outline"))}
<section class="section"><div class="wrap">
  {section_head("Why join", "Benefits of joining a Two Stooges league", "More than just a game night. Here's what you get when you join a league in Fridley.", center=True)}
  <div class="grid grid--3">{ben}</div>
</div></section>
<section class="section section--alt" id="form"><div class="wrap">
  <div class="split" style="align-items:start">
    <div>
      <span class="eyebrow">League sign-up form</span>
      <h2>Sign up for a <span class="grad-text">pool or dart league</span></h2>
      <p class="lead">Fill out the form and we'll get you placed on a team or league night. Prefer the phone? Call us and a team member will sign you up.</p>
      <ul class="check-list"><li>Pool or darts</li><li>Solo players welcome. We'll help find you a team.</li><li>Most leagues are handicapped, so every skill level can compete</li></ul>
      {btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone")}
      <div class="faq-list mt-2">{faqs}</div>
    </div>
    {cognito(FORM_LEAGUE, "League sign-up form")}
  </div>
</div></section>'''
    faq_node = {"@type": "FAQPage", "@id": SITE + "/league-signup/#faq", "isPartOf": {"@id": SITE + "/league-signup/#webpage"},
                "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in LEAGUE_FAQ]}
    return page("signup", body, extra_ld=[faq_node], main_entity=SG.SERVICES["leagues"]["@id"])



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


def entries_page(kind, hero, intro_eyebrow, intro_text, empty_text, recent_h2, recent_p, cta):
    dated, weekly = upcoming(kind)
    up = "".join(listing(ev) for ev in dated)
    wk = ""
    if weekly:
        wk = '<p class="eyebrow listing-group">Every week</p>' + "".join(listing(ev) for ev in weekly)
    pasts = past(kind)
    recent = ""
    if pasts:
        recent = f'''<section class="section section--alt" id="recent"><div class="wrap">
  {section_head("Recent", recent_h2, recent_p)}
  <div class="flyer-grid" data-past-grid>{"".join(past_card(ev) for ev in pasts)}</div>
</div></section>'''
    else:
        recent = '<div hidden data-past-grid></div>'
    body = f'''{hero}
<section class="section" id="upcoming"><div class="wrap">
  <div class="section-head"><span class="eyebrow">{intro_eyebrow}</span><p>{intro_text}</p></div>
  <div data-upcoming>{up}</div>
  <div class="empty-note{"" if dated else " is-visible"}" data-empty-note>{empty_text}</div>
  {wk}
</div></section>
{recent}
{cta}'''
    return body, [entry_ld(ev) for ev in dated + weekly]


def p_events():
    hero = page_hero("events", "What's happening", "Events at <span class='grad-text'>Two Stooges Sports Bar</span> in Fridley, MN",
        f"Special nights, parties and promotions at Two Stooges in Fridley, for everyone in the Twin Cities, not just pool players. Click any flyer to see it full size. Looking for pool? See our {L('/tournaments/', 'pool tournaments')}.",
        "photos/billiard-room-hero", "The Two Stooges billiard room",
        btn("Upcoming Events", "#upcoming", "gold") + btn("Pool Tournaments", "/tournaments/", "outline") + btn("Private Parties", "/private-parties/", "outline"))
    body, ld = entries_page("events", hero, "Coming up",
        f"Food and drink nights, holiday parties and specials on the way. Check {L('/specials/', 'daily specials and happy hour')} for deals every day.",
        f"New events are on the way. Call <a href=\"tel:{BIZ['tel']}\">{BIZ['phone']}</a> to find out what's next, or see our {L('/tournaments/', 'upcoming pool tournaments')}.",
        "Recent events at Two Stooges", "Missed one? Here's what we've hosted lately. Most events come back, so watch this page.",
        page_faq("Event questions at Two Stooges in Fridley", ["What are the hours at Two Stooges?", "Is there parking?", "Can I host a private party at Two Stooges?", "How do I book a private party?"]) +
        cta_band("Want to host your own event?", "From birthday bashes to banquets and league parties, we'll help you plan it.",
                 btn("Plan Your Event", "/private-parties/", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone")))
    return page("events", body, extra_ld=ld)


def p_tournaments():
    hero = page_hero("tournaments", "Pool tournaments", "Pool tournaments at <span class='grad-text'>Two Stooges Sports Bar</span> in Fridley, MN",
        f"Weekly 8-ball and 9-ball tournaments plus FargoRate shootouts on our {L('/billiards/', '43 tables')} in Fridley, for players from across the Twin Cities. Click any flyer to see it full size.",
        "photos/player-shooting", "A tournament player shooting at Two Stooges Sports Bar",
        btn("Upcoming Tournaments", "#upcoming", "gold") + btn("Pool Leagues", "/leagues/", "outline") + btn("Events", "/events/", "outline"))
    body, ld = entries_page("tournaments", hero, "Coming up",
        f"Special tournaments first, then our weekly tournaments. Spots are limited, so sign up early. New to FargoRate? Our {L('/leagues/', 'weekly pool leagues')} are a great way to build your rating.",
        f"No special tournaments posted right now. Call <a href=\"tel:{BIZ['tel']}\">{BIZ['phone']}</a> to find out what's coming up next.",
        "Recent pool tournaments", "Missed one? Here are our latest tournaments. Most come back, so watch this page.",
        term_table("Tournament terms at Two Stooges", "How to read a tournament flyer.", [
            ("8-ball, 9-ball, 10-ball", "The three pool games our tournaments are played in.", "Weekly 8-ball on Saturday and 9-ball on Sunday, plus special events."),
            ("Bar box", "A 7 ft pool table.", "Bar box shootouts are played on our 7 ft tables."),
            ("Race", "The number of games a player must win to take the match. A 4/3 race means one player races to 4 and the other to 3.", "Listed on each tournament flyer."),
            ("Alt break", "Players take turns breaking instead of the winner breaking.", "Listed on the flyer when it applies."),
            ("Double elimination", "A format where a player is out after losing two matches.", "Listed on the flyer when it applies."),
            ("FargoRate", "A rating system that ranks pool players from their game results.", "Some tournaments are limited to players at or under a set rating."),
            ("Money added", "Prize money put into the pot on top of the entry fees.", "Shown on the flyer when a tournament has it."),
        ]) + page_faq("Tournament questions at Two Stooges in Fridley", ["Does Two Stooges host pool tournaments?", "How many pool tables does Two Stooges have?", "What skill level do I need?", "Where is Two Stooges Sports Bar located?", "Is there parking?"]) +
        cta_band("Want to run a tournament here?", "Directors and leagues, talk to us about tables, dates and food for your players.",
                 btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "gold", "phone") + btn("League Sign-Up", "/league-signup/", "outline")))
    return page("tournaments", body, extra_ld=ld)


def p_parties():
    occasions = ["Birthdays", "Office parties", "Draft parties", "Holiday parties", "Celebrations of life", "Banquets & league parties", "Business meetings", "Reunions & receptions"]
    occ = "".join(f"<li>{e(o)}</li>" for o in occasions)
    body = f'''{page_hero("parties", "Private parties &amp; events", "Private parties at <span class='grad-text'>Two Stooges Sports Bar</span> in Fridley, MN",
        "Two Stooges is ready for your next birthday, holiday party, office outing or banquet in Fridley, for groups from across the Twin Cities. We'll customize the menu and the space for your group.",
        "photos/hero-private-parties", "Friends laughing around a pool table as one of them lines up a shot during a party at Two Stooges", btn("Request a Date", "#request", "gold") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  <div class="split">
    <div>
      <span class="eyebrow">Perfect for</span>
      <h2>A Fridley party venue for <span class="grad-text">any occasion</span></h2>
      <p class="lead">We have spaces for small and large groups, with {L("/billiards/", "pool tables")}, {L("/darts/", "dart boards")} and big screens included. {L("/gallery/", "See photos of the space")}, read our {L("/faq/", "party FAQ")} or {L("/leagues/", "book a league banquet")}.</p>
      <ul class="check-list check-list--2col">{occ}</ul>
    </div>
    <div class="split__media">
      {img("photos/party-food-spread", "A party spread of cheeseburgers, fries, pizza and salad with cold beers", sizes="(max-width:860px) 100vw, 50vw")}
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
</div></section>
{page_faq("Private party questions at Two Stooges in Fridley", ["Can I host a private party at Two Stooges?", "How do I book a private party?", "Is there parking?", "What food does Two Stooges serve?"])}'''
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
      <p class="lead">What began as a neighborhood {L("/billiards/", "billiard room")} became one of the best-known pool and darts destinations in the Twin Cities and Minnesota, with a full sports bar and {L("/menu/", "kitchen")} to match.</p>
      <ol class="timeline mt-2">{tl_html}</ol>
    </div>
    <div class="split__media split__media--stack">
      {img("photos/billiard-room-diamond-tables", "The Two Stooges billiard room today: rows of blue-felt Diamond pool tables under wood-trimmed lights", sizes="(max-width:860px) 100vw, 50vw")}
      {img("photos/dart-room-big-screen", "The Two Stooges dart room: six lit Bullshooter electronic dart boards under a big projection screen showing the game", sizes="(max-width:860px) 100vw, 50vw")}
    </div>
  </div>
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("Recognition", "Awards &amp; recognition", f"Want to see why? Join a {L('/leagues/', 'pool or dart league')} or enter one of our {L('/tournaments/', 'tournaments')}.", center=True)}
  <div class="grid grid--4">{aw}</div>
</div></section>
<section class="section"><div class="wrap">
  <div class="split split--rev">
    <div class="split__media">{img("photos/sports-bar-center-bar-tables", "The elevated center bar at Two Stooges: cherry wood bar and stools under neon signs and TVs, with high-top tables in front", sizes="(max-width:860px) 100vw, 50vw")}</div>
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
    photos = [("photos/gallery-league-night", "League night in the billiard room, with players at rows of blue-felt Diamond tables"),
              ("photos/gallery-gabriels-racking", "Racking a game on a Gabriel's table while a player waits with his cue"),
              ("photos/gallery-brick-booths", "Brick-walled dining room with red booths, pendant lights and TVs by the windows"),
              ("photos/gallery-diamond-tables-sardo", "Diamond tables with Sardo racks, with the raised bar and high-tops behind"),
              ("photos/gallery-center-bar", "The elevated center bar with neon signs, TVs and a high-top table in front"),
              ("photos/gallery-bar-taps-tvs", "The bar: beer taps, a full back bar and games on the TVs"),
              ("photos/gallery-billiard-room-diamond", "The billiard room: rows of Diamond tables under wood-trimmed lights"),
              ("photos/gallery-storefront", "Outside Two Stooges on University Ave NE in Fridley, with the green awning and window signs"),
              ("photos/gallery-dining-room", "The dining room with wood tables and chairs, looking toward the bar"),
              ("photos/pro-shop-display-case-accessories", "The Pro Shop display case: cue balls, chalk holders, grips and racks on glass shelves"),
              ("photos/pro-shop-billiards-counter", "The Pro Shop counter under the red Billiards neon sign, with the cue wall and glass cases"),
              ("photos/dart-room-bullshooter-boards", "The dart room: six lit Bullshooter boards under the big screen, with high-top tables"),
              ("photos/billiard-room-diamond-apa", "Diamond tables, including an APA tournament table, with the raised bar behind"),
              ("photos/billiard-room-diamond-lounge", "Rows of Diamond tables and high-top seating in the billiard room"),
              ("photos/gallery-claw-machines", "Prize Cube and Toy Chest claw machines by the billiard room"),
              ("photos/gallery-bar-back-bar-tvs", "Behind the bar: the back bar, beer taps and TVs all around"),
              ("photos/billiard-room-trophy-rail", "Players at the Gabriel's tables under the trophy case and American flag"),
              ("photos/food-thin-crust-pizza", "Thin-crust pizza with sausage, mushrooms and red onion"),
              ("photos/food-tater-tots", "A pile of hot, crispy tater tots")]
    g = "".join(f'<figure class="gallery__item"><button type="button" data-lightbox="/assets/img/{p}.webp" data-alt="{e(a)}" data-caption="{e(a)}" aria-label="Enlarge photo: {e(a)}">{img(p, a + " at Two Stooges Sports Bar", sizes="(max-width:640px) 100vw, (max-width:1000px) 50vw, 33vw")}</button><figcaption>{e(a)}</figcaption></figure>' for p, a in photos)
    body = f'''{page_hero("gallery", "Take a look", "Photos of <span class='grad-text'>Two Stooges Sports Bar</span> in Fridley, MN",
        f"Inside the {L('/billiards/', 'billiard room')}, the {L('/darts/', 'dart area')} and the bar in Fridley. Click any photo to see it full size.",
        "photos/pool-hall-interior", "The Two Stooges billiard room")}
<section class="section"><div class="wrap">
  {section_head("Gallery", "Inside the sports bar, billiards hall &amp; dart room", f"Every photo was taken at Two Stooges. Like what you see? {L('/private-parties/', 'Host your next party here')}.")}
  <div class="gallery">{g}</div>
</div></section>
{cta_band("See it in person", "Open every day from 11 AM to midnight at 7178 University Ave NE in Fridley.", btn("Get Directions", DIRECTIONS, "gold", "nav", ' target="_blank" rel="noopener"'))}'''
    return page("gallery", body)


def p_contact():
    body = f'''{page_hero("contact", "Get in touch", "Contact <span class='grad-text'>Two Stooges Sports Bar</span> in Fridley, MN",
        "Questions about leagues, tournaments, parties or the menu? Give us a call or stop in. We're open every day from 11 AM to midnight.",
        "photos/hero-contact-storefront", "The Two Stooges Sports Bar & Grill entrance on University Ave NE in Fridley, with the green awning and window signs", btn("Send a Message", "#form", "gold", "mail") + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone") + btn("Get Directions", DIRECTIONS, "outline", "nav", ' target="_blank" rel="noopener"'))}
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
    <article class="card card--link"><div class="card__body"><span class="tile__icon">{icon("calendar")}</span><h3><a class="stretched" href="/tournaments/">See upcoming tournaments</a></h3><p>See what's coming up and how to get on the bracket.</p></div></article>
  </div>
  <p class="center small muted mt-2">Find Two Stooges on Google Maps: {e(BIZ["plus_code"])}</p>
</div></section>'''
    return page("contact", body, og_type="business.business")


FAQ_GROUPS = [
    ("Visiting Two Stooges", [
        FAQ[1][:2], FAQ[0][:2], FAQ[2][:2],
        ("Is there parking?", 'Yes, there is a parking lot right outside the front doors on University Ave NE. <a href="/contact/">Get directions</a>.'),
        FAQ[6][:2],
    ]),
    ("Pool, darts & the Pro Shop", [
        FAQ[3][:2],
        ("How do I rent a pool table?", 'Stop at the billiard counter and the attendant will set you up with a table and a set of balls. Play as long as you like, then bring the balls back and settle up. <a href="/billiards/#rates">Daily pool specials</a> run 11 AM–5 PM.'),
        ("How many dart boards are there?", 'Two Stooges has 6 electronic dart boards with high-top seating right next to them. <a href="/darts/">See the dart area</a>.'),
        ("Is there a pro shop?", 'Yes. The Pro Shop carries cues, cases, chalk, gloves and accessories, and we do cue repair on site. <a href="/billiards/#pro-shop">Visit the Pro Shop</a>.'),
    ]),
    ("Leagues & tournaments", [
        FAQ[4][:2],
        ("Do I need a team to join a league?", 'No. Solo players are welcome, and we will help place you on a team or league night. <a href="/league-signup/">Sign up for a league</a>.'),
        ("What skill level do I need?", "Any. Most of our leagues are handicapped, so beginners and experienced players can compete on even terms."),
        ("Does Two Stooges host pool tournaments?", 'Yes. We host a weekly 8-ball tournament every Saturday and a 9-ball tournament every Sunday, plus FargoRate 8-ball tournaments and bar box shootouts with money added. <a href="/tournaments/">See upcoming tournaments</a>.'),
    ]),
    ("Food & drink", [
        ("What food does Two Stooges serve?", 'Classic American bar and grill food: Stoogetizers, wings, burgers, sandwiches and wraps, pizza, entrées, soup and salad. <a href="/menu/">See the full menu</a>.'),
        ("When is happy hour?", 'Monday to Thursday 2–6 PM, and Friday to Sunday 11 AM–7 PM, with daily food specials too. <a href="/specials/">See every special</a>.'),
        ("How many beers are on tap?", "Two Stooges pours 16 beers on tap, ice-cold from our iced cobra taps."),
    ]),
    ("Parties & contact", [
        FAQ[5][:2],
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
    body = f'''{page_hero("faq", "Good to know", "Two Stooges Sports Bar in Fridley, MN: <span class='grad-text'>FAQ</span>",
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



# ---------------------------------------------------------------------------
# Service area (venue hub: no city pages, every community listed once as plain text)
# ---------------------------------------------------------------------------
def _miles(lat, lng):
    import math
    k = math.pi / 180
    dx = (lng - SG.LNG) * k * math.cos((lat + SG.LAT) / 2 * k) * 3958.8
    dy = (lat - SG.LAT) * k * 3958.8
    return dx, dy, math.hypot(dx, dy)


def area_places():
    """[(county, [(city, miles, dx, dy)])] sorted nearest first; the build fails if a place is outside the circle."""
    out = []
    for county, rows in PL.COUNTIES.items():
        lst = []
        for name, lat, lng in rows:
            dx, dy, d = _miles(lat, lng)
            assert d <= PL.RADIUS_MI, f"{name} is {d:.1f} mi away, outside the {PL.RADIUS_MI}-mile circle"
            lst.append((name, d, dx, dy))
        out.append((county, sorted(lst, key=lambda r: r[1])))
    return out


def mi_text(d):
    return "under 1 mile" if d < 1 else ("about 1 mile" if round(d) == 1 else f"about {round(d)} miles")


def area_map(places):
    S, C = 12.5, 300  # px per mile, centre
    dots, labels = [], []
    for county, rows in places:
        for name, d, dx, dy in rows:
            x, y = C + dx * S, C - dy * S
            big = name in PL.MAP_LABELS
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4 if big else 2.5}" class="area-map__dot{" area-map__dot--big" if big else ""}"/>')
            if big:
                ox, oy, anchor = PL.MAP_LABELS[name]
                labels.append(f'<text x="{x + ox:.1f}" y="{y + oy:.1f}" text-anchor="{anchor}">{e(name)}</text>')
    r = PL.RADIUS_MI * S
    return f'''<figure class="area-map">
  <svg viewBox="0 0 600 600" role="img" aria-label="Map of the {PL.RADIUS_MI}-mile circle around Two Stooges in Fridley, Minnesota, with the communities inside it marked">
    <rect width="600" height="600" rx="8" class="area-map__bg"/>
    <circle cx="{C}" cy="{C}" r="{r}" class="area-map__ring"/>
    <circle cx="{C}" cy="{C}" r="{r / 2}" class="area-map__ring area-map__ring--half"/>
    <text x="{C}" y="{C + r / 2 + 16}" text-anchor="middle" class="area-map__note">10 miles</text>
    <text x="{C}" y="{C - r + 18}" text-anchor="middle" class="area-map__note">20 miles</text>
    {"".join(dots)}
    <g class="area-map__labels">{"".join(labels)}</g>
    <circle cx="{C}" cy="{C}" r="9" class="area-map__bar"/>
    <text x="{C}" y="{C + 28}" text-anchor="middle" class="area-map__barlabel">Two Stooges</text>
    <text x="572" y="34" text-anchor="middle" class="area-map__note">N ↑</text>
  </svg>
  <figcaption>Gold ring: Two Stooges, Fridley. Outer circle: {PL.RADIUS_MI} miles. North is up; positions are approximate.</figcaption>
</figure>'''


def p_area():
    places = area_places()
    total = sum(len(r) for _, r in places)
    counties = [c for c, _ in places]
    county_text = ", ".join(counties[:-1]) + " and " + counties[-1]
    dist = {name: d for _, rows in places for name, d, _, _ in rows}
    def county_h3(c):
        return f'<a href="{COUNTY_PATH[c]}">{e(c)} County</a>' if c in COUNTY_PATH else f"{e(c)} County"
    city_cards = "".join(f'''<div class="area-county"><h3>{county_h3(c)}</h3>
      <div class="grid grid--4">{"".join(f'''<article class="card card--link" data-place="{e(n)}" data-county="{e(c)}" data-miles="{e(mi_text(d))}" data-href="{CITY_PATH[n]}"><div class="card__body"><span class="card__kicker">{e(mi_text(d))} away</span><h3><a class="stretched" href="{CITY_PATH[n]}">{e(n)}, MN</a></h3></div></article>''' for n, d, _, _ in rows if n in CITY_PATH)}</div></div>'''
                         for c, rows in places if any(n in CITY_PATH for n, *_ in rows))
    groups = "".join(f'''<div class="area-county"><h3>{county_h3(c)}</h3>
      <ul class="area-list">{"".join(f'<li data-place="{e(n)}" data-county="{e(c)}" data-miles="{e(mi_text(d))}">{e(n)} <span>{e(mi_text(d).replace("about ", ""))}</span></li>' for n, d, _, _ in rows if n not in CITY_PATH)}</ul></div>'''
                     for c, rows in places)
    options = "".join(f'<option value="{e(n)}">' for n in sorted(dist))
    quotes = "".join(f'''<figure class="quote"><div class="quote__stars" role="img" aria-label="{r} out of 5 stars">{"★" * r}{"☆" * (5 - r)}</div><blockquote>{e(q)}</blockquote><figcaption><span class="quote__avatar">{e(n[0])}</span><span>{e(n)}<small>Google review</small></span></figcaption></figure>''' for q, n, r in REVIEWS[:3])
    faq = [
        ("How far is Two Stooges from Minneapolis and St. Paul?",
         f"Two Stooges is in Fridley, {mi_text(dist['Minneapolis'])} from the center of Minneapolis and {mi_text(dist['St. Paul'])} from the center of St. Paul, measured in a straight line. We're on University Avenue NE (Highway 47). {L('/contact/', 'Get the address, hours and a map')}."),
        (f"Which counties are within {PL.RADIUS_MI} miles of Two Stooges?",
         f"Communities in {county_text} counties sit within about {PL.RADIUS_MI} miles of the bar. Every one is listed above, grouped by county."),
        ("My city isn't on the list. Can I still come?",
         f"Yes. Everyone is welcome at Two Stooges. The list only shows the communities within about {PL.RADIUS_MI} miles of Fridley."),
        find_q("Is there parking?"),
        ("Do I need a reservation?",
         f"No. Walk-ins are always welcome. For a group, {L('/private-parties/', 'reserve space for a private party')}."),
    ]
    faq_html = "".join(f'<details class="faq"><summary><h3>{e(q)}</h3></summary><p>{a}</p></details>' for q, a in faq)
    body = f'''{page_hero("area", "Service area", "Sports bar, billiards &amp; darts serving the <span class='grad-text'>Twin Cities</span>",
        f"{PL.STATEMENT} That circle takes in {total} communities in {county_text} counties.",
        "photos/storefront-two-stooges", "The Two Stooges Sports Bar & Grill storefront on University Ave NE in Fridley, Minnesota",
        btn("Get Directions", DIRECTIONS, "gold", "nav", ' target="_blank" rel="noopener"') + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  <div class="split">
    <div>
      <span class="eyebrow">The {PL.RADIUS_MI}-mile circle</span>
      <h2>One sports bar for the <span class="grad-text">whole metro</span></h2>
      <p class="lead">Two Stooges has one location, at {e(BIZ["street"])} in Fridley, just north of Minneapolis on Highway 47. Come in from anywhere in the metro for {L("/billiards/", "43 pool tables")}, {L("/darts/", "electronic dart boards")} and a full {L("/menu/", "bar and grill menu")}.</p>
      <ul class="check-list">
        <li>{total} communities in {len(counties)} counties within about {PL.RADIUS_MI} miles</li>
        <li>Open every day, 11 AM to midnight</li>
        <li>Parking lot right outside the front doors</li>
        <li>{L("/leagues/", "Pool and dart leagues")} and {L("/tournaments/", "pool tournaments")} open to players from any city</li>
      </ul>
    </div>
    {area_map(places)}
  </div>
</div></section>
<section class="section section--alt" id="check"><div class="wrap" style="max-width:900px">
  {section_head("Check your city", "Is your city within 20 miles of Two Stooges?", "Type your city to see how far it is from the bar. The city pages and the full list are just below.")}
  <form class="area-check" data-area-check>
    <label for="area-city">Your city</label>
    <div class="area-check__row">
      <input id="area-city" name="city" type="text" list="area-cities" autocomplete="address-level2" placeholder="e.g. Blaine" required>
      <datalist id="area-cities">{options}</datalist>
      <button class="btn btn--gold" type="submit">Check</button>
    </div>
    <p class="area-check__result" role="status" aria-live="polite" data-area-result></p>
  </form>
</div></section>
<section class="section" id="cities"><div class="wrap">
  {section_head("City pages", "Cities closest to Two Stooges", "Each city page has local facts, the distance and directions. Grouped by county.")}
  <div class="area-counties">{city_cards}</div>
</div></section>
<section class="section section--alt" id="communities"><div class="wrap">
  {section_head("We also serve", f"More Twin Cities communities within {PL.RADIUS_MI} miles", "Grouped by county, nearest first.")}
  <div class="area-counties">{groups}</div>
  <p class="small muted mt-2">Distances are straight-line from each city's center to Two Stooges and are approximate. A city that crosses a county line is listed under its main county. Sources: counties from <a href="{PL.SOURCE_COUNTIES}" target="_blank" rel="noopener">Wikipedia's list of cities in Minnesota</a>, city locations from <a href="{PL.SOURCE_COORDS}" target="_blank" rel="noopener">GeoNames</a> (Coon Rapids from its Wikipedia entry).</p>
</div></section>
<section class="section"><div class="wrap">
  {section_head("Guest reviews", "What guests say about Two Stooges in Fridley", "Real reviews from Google, shared with first names only.", center=True)}
  <div class="grid grid--3">{quotes}</div>
  <div class="btn-row mt-2" style="justify-content:center">{btn("Read More Reviews on Google", SG.GBP_URL, "green", None, ' target="_blank" rel="noopener"')}</div>
</div></section>
<section class="section section--alt"><div class="wrap" style="max-width:900px">
  {section_head("Good to know", "Service area questions", f"More answers in the {L('/faq/', 'full Two Stooges FAQ')}.")}
  <div class="faq-list">{faq_html}</div>
</div></section>
{visit_section("Getting to Two Stooges in Fridley, MN")}
{cta_band("Bringing a group from across the metro?", "Birthdays, office parties and league banquets. We'll set up tables, boards and food for your group.", btn("Plan a Private Party", "/private-parties/", "gold") + btn("See Upcoming Events", "/events/", "outline"))}'''
    return page("area", body)


# ---------------------------------------------------------------------------
# City and county pages (closest cities only; each must pass the gate in check_city_pages)
# ---------------------------------------------------------------------------
FACTS_CHECKED_TEXT = dt.date.fromisoformat(CD.FACTS_CHECKED).strftime("%B %-d, %Y")
PLACE_XY = {n: (lat, lng) for rows in PL.COUNTIES.values() for n, lat, lng in rows}


def city_miles(name):
    return _miles(*PLACE_XY[name])[2]


def between(a, b):
    import math
    (la, lo), (lb, lob) = PLACE_XY[a], PLACE_XY[b]
    k = math.pi / 180
    return math.hypot((lob - lo) * k * math.cos((la + lb) / 2 * k), (lb - la) * k) * 3958.8


def nearby_cities(name, n=5):
    """The n nearest cities that have a page (all within about 10 miles), nearest first."""
    return sorted((c for c in CD.CITIES if c != name), key=lambda c: between(name, c))[:n]


def facts_table(rows, src_name, src_url, extra=()):
    """rows: (fact, value) all from one source; extra: (fact, value, source name, url). A source link sits beside every fact."""
    link = lambda n, u: f'<a href="{u}" target="_blank" rel="noopener">{e(n)}</a>'
    body = "".join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td><td>{link(src_name, src_url)}</td></tr>' for k, v in rows)
    body += "".join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td><td>{link(n, u)}</td></tr>' for k, v, n, u in extra)
    return f'''<div class="table-scroll"><table class="term-table">
    <thead><tr><th scope="col">Fact</th><th scope="col">Detail</th><th scope="col">Source</th></tr></thead>
    <tbody>{body}</tbody>
  </table></div>
  <p class="small muted mt-1">Facts were checked against the linked sources on {FACTS_CHECKED_TEXT}.</p>'''


def play_cards():
    cards = [("/billiards/", "Billiards &amp; pool tables", "43 Gabriel's and Diamond tables, daily pool specials and the Pro Shop."),
             ("/darts/", "Electronic darts", "Bullshooter boards, high-tops and a big screen."),
             ("/leagues/", "Pool &amp; dart leagues", "In-house, IBA (M8), APA, UPL and darts. Solo players welcome."),
             ("/tournaments/", "Pool tournaments", "Weekly 8-ball and 9-ball plus FargoRate events."),
             ("/private-parties/", "Private parties", "Birthdays, office parties and banquets with custom menus."),
             ("/menu/", "Bar &amp; grill menu", "Burgers, wings, pizza and 16 beers on tap.")]
    return "".join(f'''<article class="card card--link"><div class="card__body"><h3><a class="stretched" href="{h}">{t}</a></h3><p>{d}</p></div></article>''' for h, t, d in cards)


def city_page(name):
    d = CD.CITIES[name]
    key, miles = CITY_KEY[name], city_miles(name)
    dist = mi_text(miles)
    fmt = lambda t: t.replace("{dist_plain}", dist).replace("{dist}", dist[0].upper() + dist[1:])
    county = d["county"]
    extra = [("Distance to Two Stooges", f"{dist[0].upper() + dist[1:]}, straight line from the city center", *(("Wikipedia: " + name, d["wiki"]) if d.get("coord_src") == "wiki" else ("GeoNames", PL.SOURCE_COORDS)))]
    if d.get("border"):
        extra.insert(0, ("Where it sits", d["border"], "Wikipedia: Fridley", CD.FRIDLEY_SRC))
    near = nearby_cities(name)
    near_links = "".join(f'<li><a href="{CITY_PATH[c]}">{e(c)}, MN</a> <span>{e(mi_text(between(name, c)).replace("about ", ""))} away</span></li>' for c in near)
    origin = "&origin=" + (name + ", MN").replace(",", "%2C").replace(" ", "+")
    faq_html = "".join(f'<details class="faq"><summary><h3>{e(q)}</h3></summary><p>{fmt(a)}</p></details>' for q, a in d["faq"])
    prep = d.get("h1", "near")
    body = f'''{page_hero(key, f"{e(county)} County", f"Sports bar, billiards &amp; darts {prep} <span class='grad-text'>{e(name)}, MN</span>",
        d["lead"], "photos/storefront-two-stooges", "The Two Stooges Sports Bar & Grill storefront on University Ave NE in Fridley, Minnesota",
        btn(f"Directions from {name}", DIRECTIONS + origin, "gold", "nav", ' target="_blank" rel="noopener"') + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  {section_head(f"{e(name)} at a glance", f"{e(name)}, Minnesota: local facts", f'Read more about <a href="{d["wiki"]}" target="_blank" rel="noopener">{e(name)} on Wikipedia</a>.')}
  {facts_table(d["facts"], f"Wikipedia: {name}", d["wiki"], extra)}
</div></section>
<section class="section section--alt"><div class="wrap prose" style="max-width:900px">
  <span class="eyebrow">{e(name)} and Two Stooges</span>
  <h2>{e(d["h2"])}</h2>
  {"".join(f"<p>{fmt(t)}</p>" for t in d["local"])}
</div></section>
<section class="section"><div class="wrap">
  {section_head("What's here", f"Pool, darts and dinner for {e(name)}")}
  <div class="grid grid--3">{play_cards()}</div>
</div></section>
<section class="section section--alt"><div class="wrap" style="max-width:900px">
  {section_head(f"Questions from {e(name)}", f"Two Stooges questions from {e(name)}", f"More answers in the {L('/faq/', 'full Two Stooges FAQ')}.")}
  <div class="faq-list">{faq_html}</div>
</div></section>
<section class="section"><div class="wrap">
  {section_head(f"Near {e(name)}", f"Nearby cities we also serve", f"{e(name)} is in {L(COUNTY_PATH[county], county + ' County')}. See the {L('/service-area/', 'full Two Stooges service area')}.")}
  <ul class="area-list area-list--links">{near_links}</ul>
</div></section>
{cta_band(f"Coming from {e(name)}?", "We're open every day from 11 AM to midnight at 7178 University Ave NE, Fridley. Walk-ins are always welcome.", btn(f"Directions from {name}", DIRECTIONS + origin, "gold", "nav", ' target="_blank" rel="noopener"') + btn("See Upcoming Events", "/events/", "outline"))}'''
    return page(key, body)


def county_page(name):
    d = CD.COUNTIES[name]
    key = COUNTY_KEY[name]
    with_pages = sorted((c for c, cd in CD.CITIES.items() if cd["county"] == name), key=city_miles)
    cards = "".join(f'''<article class="card card--link"><div class="card__body"><span class="card__kicker">{e(mi_text(city_miles(c)))} away</span><h3><a class="stretched" href="{CITY_PATH[c]}">{e(c)}, MN</a></h3></div></article>''' for c in with_pages)
    others = [(n, _miles(lat, lng)[2]) for n, lat, lng in PL.COUNTIES[name] if n not in CD.CITIES]
    other_txt = ", ".join(f"{e(n)} ({round(m)} mi)" for n, m in sorted(others, key=lambda r: r[1]))
    sib = " and ".join(L(COUNTY_PATH[c], c + " County") for c in CD.COUNTIES if c != name)
    faq_html = "".join(f'<details class="faq"><summary><h3>{e(q)}</h3></summary><p>{a}</p></details>' for q, a in d["faq"])
    body = f'''{page_hero(key, "Service area", f"Sports bar, billiards &amp; darts serving <span class='grad-text'>{e(name)} County, MN</span>",
        d["lead"], "photos/storefront-two-stooges", "The Two Stooges Sports Bar & Grill storefront on University Ave NE in Fridley, Minnesota",
        btn("Get Directions", DIRECTIONS, "gold", "nav", ' target="_blank" rel="noopener"') + btn("Call " + BIZ["phone"], "tel:" + BIZ["tel"], "outline", "phone"))}
<section class="section"><div class="wrap">
  {section_head(f"{e(name)} County at a glance", f"{e(name)} County, Minnesota: local facts", f'Read more about <a href="{d["wiki"]}" target="_blank" rel="noopener">{e(name)} County on Wikipedia</a>.')}
  {facts_table(d["facts"], f"Wikipedia: {name} County", d["wiki"])}
</div></section>
<section class="section section--alt"><div class="wrap prose" style="max-width:900px">
  <span class="eyebrow">{e(name)} County and Two Stooges</span>
  <h2>{e(d["h2"])}</h2>
  {"".join(f"<p>{t}</p>" for t in d["local"])}
</div></section>
<section class="section"><div class="wrap">
  {section_head("City pages", f"{e(name)} County cities closest to Two Stooges", "Each page has local facts, the distance and directions.")}
  <div class="grid grid--3">{cards}</div>
  <h3 class="mt-2">Also within {PL.RADIUS_MI} miles in {e(name)} County</h3>
  <p class="muted">{other_txt}. Distances are straight-line and approximate.</p>
  <p class="mt-1">Looking for another county? See {sib}, or the {L("/service-area/", "full Two Stooges service area")}.</p>
</div></section>
<section class="section section--alt"><div class="wrap">
  {section_head("What's here", f"Pool, darts and dinner for {e(name)} County")}
  <div class="grid grid--3">{play_cards()}</div>
</div></section>
<section class="section"><div class="wrap" style="max-width:900px">
  {section_head("Good to know", f"{e(name)} County questions")}
  <div class="faq-list">{faq_html}</div>
</div></section>
{cta_band(f"Coming from {e(name)} County?", "We're open every day from 11 AM to midnight at 7178 University Ave NE, Fridley. Walk-ins are always welcome.", btn("Get Directions", DIRECTIONS, "gold", "nav", ' target="_blank" rel="noopener"') + btn("Plan a Private Party", "/private-parties/", "outline"))}'''
    return page(key, body)


def check_city_pages():
    """Gate (service-area prompt A+): 5+ sourced facts and 300+ words found on no other page, city names masked."""
    names = sorted(list(CD.CITIES) + [c + " County" for c in CD.COUNTIES], key=len, reverse=True)
    mask = re.compile("|".join(re.escape(n) for n in names))

    def sentences(rel):
        h = (ROOT / rel).read_text(encoding="utf-8")
        m = re.search(r"<main.*?</main>", h, re.S).group(0)
        m = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", m, flags=re.S)
        m = re.sub(r"</(p|li|h[1-6]|td|th|summary|div|figcaption)>", ". ", m)
        t = html.unescape(re.sub(r"<[^>]+>", " ", m))
        t = mask.sub("CITY", t)
        return [re.sub(r"\s+", " ", x).strip().lower() for x in re.split(r"(?<=[.?!])\s+", t) if len(x.split()) > 3]

    pages = {rel: sentences(rel) for rel in PAGES if rel.endswith("index.html")}
    errs = []
    for n, dd in list(CD.CITIES.items()) + list(CD.COUNTIES.items()):
        rel = f"service-area/{dd['slug']}/index.html"
        seen = set(s for r, ss in pages.items() if r != rel for s in ss)
        uniq = sum(len(s.split()) for s in set(pages[rel]) if s not in seen)
        need = 300 if n in CD.CITIES else 200
        if uniq < need:
            errs.append(f"{rel}: only {uniq} unique words (need {need})")
        if len(dd["facts"]) < 5:
            errs.append(f"{rel}: fewer than 5 sourced facts")
        print(f"gate {rel}: {uniq} unique words, {len(dd['facts']) + (2 if dd.get('border') else 1 if n in CD.CITIES else 0)} sourced facts")
    if errs:
        raise SystemExit("City page gate failed:\n  " + "\n  ".join(errs))


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


def p_eoe():
    body = f'''{page_hero("eoe", "Careers", "Two Stooges Sports Bar <span class='grad-text'>equal opportunity employer</span>",
        f"{e(BIZ['name'])} is an equal opportunity employer. We hire, train and promote people based on their skills, experience and attitude.",
        "photos/billiard-room-rows", "The Two Stooges billiard room")}
<section class="section"><div class="wrap prose" style="max-width:820px">
  <h2>Our commitment</h2>
  <p>{e(BIZ['name'])} provides equal employment opportunities to all employees and applicants. We do not discriminate on the basis of race, color, religion, creed, sex, sexual orientation, gender identity, national origin, ancestry, age, disability, marital status, familial status, status with regard to public assistance, military or veteran status, genetic information, or any other status protected by federal, Minnesota or local law.</p>
  <h2>Where it applies</h2>
  <p>This applies to every part of employment, including hiring, pay, scheduling, training, promotion, discipline and termination.</p>
  <h2>Accommodations</h2>
  <p>We provide reasonable accommodations for applicants and employees with disabilities, and for religious beliefs and practices, as required by law. To ask for an accommodation, talk to a manager or contact us.</p>
  <h2>Questions</h2>
  <p>Questions about employment at Two Stooges? Call <a href="tel:{BIZ["tel"]}">{BIZ["phone"]}</a>, email <a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a>, or {L("/contact/", "visit our contact page")}.</p>
</div></section>'''
    return page("eoe", body)


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
<link rel="preload" href="/assets/fonts/oswald-latin-var-v5.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/inter-latin-var-v5.woff2" as="font" type="font/woff2" crossorigin>
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
    "events/index.html": p_events, "tournaments/index.html": p_tournaments, "league-signup/index.html": p_signup, "private-parties/index.html": p_parties, "about/index.html": p_about,
    "gallery/index.html": p_gallery, "contact/index.html": p_contact, "privacy-policy/index.html": p_privacy, "equal-opportunity-employer/index.html": p_eoe, "faq/index.html": p_faq, "service-area/index.html": p_area,
    "404.html": p_404,
}
for _n in CD.CITIES:
    PAGES[f"service-area/{CD.CITIES[_n]['slug']}/index.html"] = (lambda n=_n: city_page(n))
for _n in CD.COUNTIES:
    PAGES[f"service-area/{CD.COUNTIES[_n]['slug']}/index.html"] = (lambda n=_n: county_page(n))


_IMG_REF = re.compile(r'/assets/img/([\w./-]+\.(?:webp|png|jpe?g|svg|ico))(?![?\w])')
_IMG_HASH = {}


def bust_images(html_text):
    """Add ?v=<content hash> to every image URL, so a replaced photo is never served from a stale cache."""
    def sub(m):
        rel = m.group(1)
        if rel not in _IMG_HASH:
            f = IMG / rel
            _IMG_HASH[rel] = _hashlib.md5(f.read_bytes()).hexdigest()[:8] if f.exists() else ""
        h = _IMG_HASH[rel]
        return m.group(0) + (f"?v={h}" if h else "")
    return _IMG_REF.sub(sub, html_text)


def main():
    renames = CT.prepare_uploads()  # admin uploads: safe file names before conversion
    IMGS.optimize()  # image rule: every photo web-ready before pages read their sizes
    ENTRIES.update(CT.load(renames))
    print("content: %d events, %d tournaments" % (len(ENTRIES["events"]), len(ENTRIES["tournaments"])))
    for rel, fn in PAGES.items():
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(bust_images(fn()), encoding="utf-8")
        print("wrote", rel)
    # Sitemap: canonical URLs only (matches <link rel=canonical> exactly)
    prio = {"/": "1.0", "/events/": "0.8", "/tournaments/": "0.9", "/billiards/": "0.9", "/specials/": "0.8", "/menu/": "0.8", "/leagues/": "0.8",
            "/darts/": "0.7", "/league-signup/": "0.8", "/private-parties/": "0.8", "/about/": "0.6", "/gallery/": "0.5", "/contact/": "0.7", "/faq/": "0.6", "/service-area/": "0.6", "/privacy-policy/": "0.2", "/equal-opportunity-employer/": "0.2"}
    urls = [m[0] for m in META.values()]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{prio.get(u, '0.5')}</priority></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    robots = ("User-agent: *\nAllow: /\nDisallow: /_src/\nDisallow: /_content/\nDisallow: /admin/\nDisallow: /api/\n\nSitemap: " + SITE + "/sitemap.xml\n") if LAUNCH else "User-agent: *\nDisallow: /\n"
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    print("wrote sitemap.xml, robots.txt (launch=%s)" % LAUNCH)
    check_city_pages()
    bad = IMGS.check()
    if bad:
        raise SystemExit("Image check failed (over budget):\n  " + "\n  ".join(bad))
    print("images: all within budget")


if __name__ == "__main__":
    main()
