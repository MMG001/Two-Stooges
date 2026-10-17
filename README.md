# Two Stooges Sports Bar & Grill — website

Static site for Two Stooges, Fridley MN. Hosted on Cloudflare Pages (project `two-stooges`, branch `main`, no build command, output `/`).

## Editing
All pages are generated from **`_src/build.py`**, which holds the shared header, footer, navigation, business info, events, leagues and specials.

```bash
python3 _src/build.py   # rebuilds every page (Pillow optional, adds image sizes)
```

Edit `_src/build.py`, run it, commit, push. Don't hand-edit the generated `*.html`, because the next build overwrites them.

- **Add an event:** add a dict to `EVENTS` and put the flyer in `assets/img/events/`. Past events move to "Recent events" automatically.
- **Styles:** `assets/css/site.css` (colors are tokens at the top).
- **Behavior:** `assets/js/site.js` (mobile menu, dropdowns, open/closed status, today's specials, event auto-archiving, lightbox).
- **Forms:** League sign-up and event requests use the existing Cognito Forms (#99, #96).

## Launch checklist
1. Set `LAUNCH = True` in `_src/build.py` and rebuild (removes `noindex`, opens `robots.txt`).
2. Add `twostooges.com` + `www` under the Pages project → Custom domains.
3. `_redirects` maps the old WordPress URLs to the new pages.
