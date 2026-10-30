# Two Stooges Sports Bar & Grill — website

Static site for Two Stooges, Fridley MN. Hosted on Cloudflare Pages (project `two-stooges`, branch `main`, no build command, output `/`).

## Editing
All pages are generated from **`_src/build.py`**, which holds the shared header, footer, navigation, business info, events, leagues and specials.

```bash
python3 _src/build.py   # rebuilds every page (Pillow optional, adds image sizes)
```

Edit `_src/build.py`, run it, commit, push. The build stops with an error if a title goes over 60 characters or a description falls outside 150–160. Don't hand-edit the generated `*.html`, because the next build overwrites them.

- **Events & tournaments:** entered by the client at **/admin/** (Decap CMS, GitHub login via `functions/api/auth.js` + `callback.js`, secrets `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` in Cloudflare). Entries are JSON in `_content/events/` and `_content/tournaments/`, flyers in `assets/img/events/`. `.github/workflows/build-site.yml` rebuilds and commits the pages after each save (and daily when an event date has passed). Past dates move to "Recent" automatically.
- **Styles:** `assets/css/site.css` (colors are tokens at the top).
- **Behavior:** `assets/js/site.js` (mobile menu, dropdowns, open/closed status, today's specials, event auto-archiving, lightbox).
- **Forms:** League sign-up and event requests use the existing Cognito Forms (#99, #96).

## Launch checklist
1. Set `LAUNCH = True` in `_src/build.py` and rebuild (removes `noindex`, opens `robots.txt`).
2. Add `twostooges.com` + `www` under the Pages project → Custom domains.
3. `_redirects` maps the old WordPress URLs to the new pages.

## Structured data
One interlinked JSON-LD `@graph` per page, built by `_src/schema.py`. See **`_src/SCHEMA.md`** for the entity map, form/action wiring, what is intentionally not marked up (guest reviews, past events), example output, and validation steps. Add verified social/Google profile URLs to `SAME_AS` in `_src/schema.py`. The build fails on a dangling `@id` or a misplaced property.

Cache busting: bump `ASSET_VER` in `_src/build.py`. CSS/JS are served with a 1-day cache (`_headers`) and the version query string.
