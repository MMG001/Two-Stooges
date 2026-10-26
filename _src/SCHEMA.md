# Structured data (JSON-LD entity graph)

Built by `_src/schema.py` (Universal Prompt v3.1). Every page carries **one** `<script type="application/ld+json">` with a single `@graph`; nodes link by `@id` only.

## Entity graph

| Node | @id | On |
|---|---|---|
| BarOrPub + SportsActivityLocation (one entity) | `/#business` | every page |
| WebSite | `/#website` | every page |
| WebPage / ContactPage / AboutPage / CollectionPage | `<page>#webpage` | every page |
| BreadcrumbList | `<page>#breadcrumb` | every inner page |
| Service ×4 (billiards, darts, leagues, parties) | `/<service>/#service` | every page (three-level rule: full on its own page, card on home, nav elsewhere) |
| GeoCircle service area | `/#service-area` | inside business `areaServed`, referenced by every Service |
| Event (dated tournament) | `/events/#<event-id>` | home (next-up card) + events |
| Event (weekly leagues, `eventSchedule`) | `/events/#straight-pool-league`, `/events/#10-ball-league` | events + leagues |
| Menu → MenuSection → MenuItem | `/menu/#menu` | menu |
| FAQPage | `/#faq` | home (visible FAQ) |

## Business facts

- Geo: plus code `3PXP+85 Fridley` → `86Q83PXP+85` → **45.098312, -93.264562** (decoded, matches the Google Maps embed).
- `areaServed`: exactly three nodes (v3): GeoCircle **30 mi (`48280` m)** anchored on Fridley (client-confirmed) + State Minnesota + City Fridley (Wikipedia + Wikidata Q985235). **Do not add Twin Cities / Minneapolis / St. Paul or other city nodes**; the radius covers them, and the build fails if `areaServed` is anything other than GeoCircle + State + City. The Twin Cities targeting lives in visible copy (titles, H1/H2s, the Visit section, which states the 30-mile radius and names Minneapolis and St. Paul) and in the business `description`.
- `sameAs` (client-supplied, verified): Google Business Profile `maps?cid=347673670564063440` (CID 0x4d32f5c7fba28d0, matches the client's Google `ludocid`), Instagram, Yelp, Tripadvisor, Apple Maps. Facebook omitted: the supplied link is a search page, not the business page.
- Wikidata IDs, each confirmed by two independent sources (DBpedia owl:sameAs + Wikidata/OSM/museum-digital): Billiards/cue sports **Q3341285**, Darts **Q131471**, Fridley **Q985235**. Used in `knowsAbout`, Service `category` and `areaServed` City.
- Hours: 11:00–23:59 daily ("11 AM – 12 AM" on the old site and in the brief).
- Enrichment used (true + visible): alternateName, slogan (home), foundingDate 1988, publicAccess, hasMenu, tourBookingPage, servesCuisine (home/menu), keywords (home, terms visible in home copy), amenityFeature/award (home/about), knowsAbout (Wikipedia-linked concepts, mirrored onto Services as `category`). Each Service's own page adds `audience` (Audience + audienceType mirroring the page lead; valid on Service, never on the business node).
- **No founder/Person nodes.** The business has new owners (2026-10-25); the previous owners' names were removed from the site and the graph. Add Person nodes only when the client supplies names that are shown on the page.

## Actions (form/conversion wiring)

| Conversion | Action | Target |
|---|---|---|
| Call | CommunicateAction | `tel:+17635741399` |
| Email | CommunicateAction | `mailto:info@twostooges.com` |
| Private party / event request (Cognito form #96) | AskAction | `/private-parties/#request` |
| League sign-up (Cognito form #99) | JoinAction | `/league-signup/#form` |

EntryPoints carry only `urlTemplate` + `actionPlatform`. Form fields are managed in Cognito Forms (key `e5A6hQ7FG0We3U_f7oZrng`) and documented there, not in markup.

## Intentionally NOT marked up

- **Google reviews** (Andrea, Christopher, Travel Genius, Jessica; first names only per client): displayed on the home page with links to Google/Yelp/Tripadvisor, but third-party reviews must NOT be marked up → no Review/AggregateRating. Don't add it.
- **Past events** (Oct 10 tournament, Aug 22 Rum, Ribs & Cigar Night): visible but no longer actionable.
- **paymentAccepted, priceRange, smokingAllowed, isAccessibleForFree**: not published on the site.
- **Facebook**: add the business page URL (not a search URL) to `SAME_AS` in `_src/schema.py` when available.

## Validation

- Build-time (`_src/build.py` fails on error): @id integrity (referenced ⊆ defined), one business node, no Organization in the type array, Rule-11 placement traps (areaServed = GeoCircle + State + City only, no audience/inLanguage on business, no about/inLanguage on Service, EntryPoint keys only urlTemplate/actionPlatform, no `-input` outside SearchAction).
- Property-level lint (`python3 _src/schema_lint.py schemaorg-current-https.jsonld .`) against the official schema.org vocabulary v29.3: **0 errors, 2168 property placements checked** across 14 pages (2026-10-26).
- Still to run after the domain is live: Google Rich Results Test + validator.schema.org on home, /billiards/, /events/, /menu/ (start a fresh crawl, CDN propagation 1–3 min).

## Visible enhancement vs machine-readable only

- Can earn visible SERP features: BreadcrumbList, Event (Nov 7 shootout, weekly leagues), business/local panel facts.
- Machine-readability / AI answers only: Service, FAQPage, Menu, areaServed, knowsAbout, potentialAction.

## Example rendered JSON-LD

Regenerated from the built pages on 2026-10-26.

### Homepage (/)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "https://twostooges.com/#website",
      "url": "https://twostooges.com/",
      "name": "Two Stooges Sports Bar & Grill",
      "publisher": {
        "@id": "https://twostooges.com/#business"
      },
      "inLanguage": "en-US"
    },
    {
      "@type": [
        "BarOrPub",
        "SportsActivityLocation"
      ],
      "@id": "https://twostooges.com/#business",
      "name": "Two Stooges Sports Bar & Grill",
      "alternateName": [
        "Two Stooges",
        "Two Stooges Sports Bar"
      ],
      "url": "https://twostooges.com/",
      "logo": {
        "@type": "ImageObject",
        "url": "https://twostooges.com/assets/img/brand/two-stooges-logo-1200.png?v=1f55c326",
        "width": 1200,
        "height": 543
      },
      "image": "https://twostooges.com/assets/img/og/home.jpg?v=f853b1a1",
      "telephone": "+17635741399",
      "email": "info@twostooges.com",
      "foundingDate": "1988",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "7178 University Ave NE",
        "addressLocality": "Fridley",
        "addressRegion": "MN",
        "postalCode": "55432",
        "addressCountry": "US"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": 45.098312,
        "longitude": -93.264562
      },
      "hasMap": "https://www.google.com/maps?cid=347673670564063440",
      "openingHoursSpecification": [
        {
          "@type": "OpeningHoursSpecification",
          "dayOfWeek": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
          ],
          "opens": "11:00",
          "closes": "23:59"
        }
      ],
      "publicAccess": true,
      "hasMenu": "https://twostooges.com/menu/",
      "tourBookingPage": "https://twostooges.com/private-parties/",
      "areaServed": [
        {
          "@type": "GeoCircle",
          "@id": "https://twostooges.com/#service-area",
          "description": "30-mile service radius anchored on Fridley, Minnesota",
          "geoMidpoint": {
            "@type": "GeoCoordinates",
            "latitude": 45.098312,
            "longitude": -93.264562
          },
          "geoRadius": "48280"
        },
        {
          "@type": "State",
          "name": "Minnesota",
          "sameAs": "https://en.wikipedia.org/wiki/Minnesota"
        },
        {
          "@type": "City",
          "name": "Fridley",
          "sameAs": [
            "https://en.wikipedia.org/wiki/Fridley,_Minnesota",
            "https://www.wikidata.org/wiki/Q985235"
          ]
        }
      ],
      "knowsAbout": [
        {
          "@type": "Thing",
          "name": "Billiards",
          "sameAs": [
            "https://en.wikipedia.org/wiki/Cue_sports",
            "https://www.wikidata.org/wiki/Q3341285"
          ]
        },
        {
          "@type": "Thing",
          "name": "Darts",
          "sameAs": [
            "https://en.wikipedia.org/wiki/Darts",
            "https://www.wikidata.org/wiki/Q131471"
          ]
        },
        {
          "@type": "Thing",
          "name": "Pool (cue sports)",
          "sameAs": "https://en.wikipedia.org/wiki/Pool_(cue_sports)"
        },
        {
          "@type": "Thing",
          "name": "Straight pool",
          "sameAs": "https://en.wikipedia.org/wiki/Straight_pool"
        },
        {
          "@type": "Thing",
          "name": "Eight-ball",
          "sameAs": "https://en.wikipedia.org/wiki/Eight-ball"
        },
        {
          "@type": "Thing",
          "name": "Ten-ball",
          "sameAs": "https://en.wikipedia.org/wiki/Ten-ball"
        },
        {
          "@type": "Thing",
          "name": "Sports bar",
          "sameAs": "https://en.wikipedia.org/wiki/Sports_bar"
        }
      ],
      "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Games, leagues & events at Two Stooges",
        "itemListElement": [
          {
            "@id": "https://twostooges.com/billiards/#service"
          },
          {
            "@id": "https://twostooges.com/darts/#service"
          },
          {
            "@id": "https://twostooges.com/leagues/#service"
          },
          {
            "@id": "https://twostooges.com/private-parties/#service"
          }
        ]
      },
      "potentialAction": [
        {
          "@type": "CommunicateAction",
          "name": "Call Two Stooges",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "tel:+17635741399",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "CommunicateAction",
          "name": "Email Two Stooges",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "mailto:info@twostooges.com",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "AskAction",
          "name": "Request a private party",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "https://twostooges.com/private-parties/#request",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "JoinAction",
          "name": "Sign up for a pool or dart league",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "https://twostooges.com/league-signup/#form",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "AskAction",
          "name": "Send Two Stooges a message",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "https://twostooges.com/contact/#form",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        }
      ],
      "sameAs": [
        "https://www.google.com/maps?cid=347673670564063440",
        "https://www.instagram.com/twostoogesbarandgrill/",
        "https://www.yelp.com/biz/two-stooges-sports-bar-and-grill-fridley",
        "https://www.tripadvisor.com/Restaurant_Review-g43087-d5259418-Reviews-Two_Stooges_Sports_Bar_Grill-Fridley_Minnesota.html",
        "https://maps.apple.com/place?place-id=I390CADDFBB3A1DE1"
      ],
      "award": [
        "Top Ten Billiard Room in North America",
        "Best Place to Shoot Pool – City Pages (2017)",
        "Business of the Year",
        "Billiards Digest “Best of” Architectural Design"
      ],
      "amenityFeature": [
        {
          "@type": "LocationFeatureSpecification",
          "name": "43 pool tables",
          "value": true
        },
        {
          "@type": "LocationFeatureSpecification",
          "name": "6 dart boards",
          "value": true
        },
        {
          "@type": "LocationFeatureSpecification",
          "name": "2 patios",
          "value": true
        },
        {
          "@type": "LocationFeatureSpecification",
          "name": "Pool leagues",
          "value": true
        },
        {
          "@type": "LocationFeatureSpecification",
          "name": "30 HD TVs and 4 monster screens",
          "value": true
        },
        {
          "@type": "LocationFeatureSpecification",
          "name": "NFL Sunday Ticket",
          "value": true
        },
        {
          "@type": "LocationFeatureSpecification",
          "name": "16 beers on tap",
          "value": true
        },
        {
          "@type": "LocationFeatureSpecification",
          "name": "Pro shop and cue repair",
          "value": true
        },
        {
          "@type": "LocationFeatureSpecification",
          "name": "Private event space",
          "value": true
        }
      ],
      "slogan": "The most fun you can have under one roof",
      "keywords": "sports bar, billiards, pool tables, darts, dart leagues, pool leagues, Twin Cities, Fridley",
      "description": "Two Stooges Sports Bar & Grill is a sports bar, billiards hall and darts room at 7178 University Ave NE in Fridley, Minnesota, in the Twin Cities north metro. Open since 1988, it has 43 pool tables, electronic dart boards, 34 TV screens and 16 beers on tap.",
      "servesCuisine": "American"
    },
    {
      "@type": "WebPage",
      "@id": "https://twostooges.com/#webpage",
      "url": "https://twostooges.com/",
      "name": "Sports Bar, Billiards & Darts - Twin Cities | Two Stooges",
      "description": "Two Stooges is the Twin Cities sports bar for billiards and darts: 43 pool tables, electronic dart boards, 34 screens and 16 taps in Fridley. Plan your visit.",
      "isPartOf": {
        "@id": "https://twostooges.com/#website"
      },
      "about": {
        "@id": "https://twostooges.com/#business"
      },
      "inLanguage": "en-US",
      "primaryImageOfPage": {
        "@type": "ImageObject",
        "url": "https://twostooges.com/assets/img/og/home.jpg?v=f853b1a1",
        "width": 1200,
        "height": 630,
        "caption": "Rows of pool tables inside Two Stooges Sports Bar in Fridley, MN"
      },
      "dateModified": "2026-10-26",
      "mainEntity": {
        "@id": "https://twostooges.com/#business"
      }
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/billiards/#service",
      "name": "Billiards & pool table rental",
      "url": "https://twostooges.com/billiards/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      },
      "serviceType": "Pool table rental",
      "areaServed": {
        "@id": "https://twostooges.com/#service-area"
      },
      "category": {
        "@type": "Thing",
        "name": "Billiards",
        "sameAs": [
          "https://en.wikipedia.org/wiki/Cue_sports",
          "https://www.wikidata.org/wiki/Q3341285"
        ]
      },
      "description": "Gabriel's and Diamond tables in 9 ft and 7 ft, daily pool specials and a full Pro Shop."
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/darts/#service",
      "name": "Darts",
      "url": "https://twostooges.com/darts/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      },
      "serviceType": "Electronic dart boards",
      "areaServed": {
        "@id": "https://twostooges.com/#service-area"
      },
      "category": {
        "@type": "Thing",
        "name": "Darts",
        "sameAs": [
          "https://en.wikipedia.org/wiki/Darts",
          "https://www.wikidata.org/wiki/Q131471"
        ]
      },
      "description": "Electronic dart boards, high-tops and dart leagues for every skill level."
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/leagues/#service",
      "name": "Pool & dart leagues",
      "url": "https://twostooges.com/leagues/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      },
      "serviceType": "Pool and dart leagues",
      "areaServed": {
        "@id": "https://twostooges.com/#service-area"
      },
      "category": {
        "@type": "Thing",
        "name": "Sports league",
        "sameAs": "https://en.wikipedia.org/wiki/Sports_league"
      },
      "description": "Straight pool, 10-ball, APA and UPL leagues, plus FargoRate tournaments."
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/private-parties/#service",
      "name": "Private parties & events",
      "url": "https://twostooges.com/private-parties/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      },
      "serviceType": "Private event hosting",
      "areaServed": {
        "@id": "https://twostooges.com/#service-area"
      },
      "category": {
        "@type": "Thing",
        "name": "Party",
        "sameAs": "https://en.wikipedia.org/wiki/Party"
      },
      "description": "Birthdays, office parties and banquets with custom menus and pool tables included."
    },
    {
      "@type": "Event",
      "@id": "https://twostooges.com/events/#bar-box-shootout-2026-11-07",
      "name": "499 & Under Fargo Rated 8-Ball Bar Box Shootout",
      "startDate": "2026-11-07T11:30:00-06:00",
      "eventStatus": "https://schema.org/EventScheduled",
      "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
      "description": "An 8-ball bar box shootout for players rated 499 and under on FargoRate. Only the first 64 players who sign up get in, so call or text early to grab your spot.",
      "image": [
        "https://twostooges.com/assets/img/events/2026-11-07-bar-box-shootout.webp?v=1eb7f9dc"
      ],
      "url": "https://twostooges.com/events/#bar-box-shootout-2026-11-07",
      "location": {
        "@id": "https://twostooges.com/#business"
      },
      "organizer": {
        "@id": "https://twostooges.com/#business"
      },
      "doorTime": "2026-11-07T10:00:00-06:00",
      "offers": {
        "@type": "Offer",
        "price": "40",
        "priceCurrency": "USD",
        "url": "https://twostooges.com/events/#bar-box-shootout-2026-11-07",
        "availability": "https://schema.org/LimitedAvailability",
        "validFrom": "2026-10-26"
      }
    }
  ]
}
```

### Service page (/billiards/)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "https://twostooges.com/#website",
      "url": "https://twostooges.com/",
      "name": "Two Stooges Sports Bar & Grill",
      "publisher": {
        "@id": "https://twostooges.com/#business"
      },
      "inLanguage": "en-US"
    },
    {
      "@type": [
        "BarOrPub",
        "SportsActivityLocation"
      ],
      "@id": "https://twostooges.com/#business",
      "name": "Two Stooges Sports Bar & Grill",
      "alternateName": [
        "Two Stooges",
        "Two Stooges Sports Bar"
      ],
      "url": "https://twostooges.com/",
      "logo": {
        "@type": "ImageObject",
        "url": "https://twostooges.com/assets/img/brand/two-stooges-logo-1200.png?v=1f55c326",
        "width": 1200,
        "height": 543
      },
      "image": "https://twostooges.com/assets/img/og/home.jpg?v=f853b1a1",
      "telephone": "+17635741399",
      "email": "info@twostooges.com",
      "foundingDate": "1988",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "7178 University Ave NE",
        "addressLocality": "Fridley",
        "addressRegion": "MN",
        "postalCode": "55432",
        "addressCountry": "US"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": 45.098312,
        "longitude": -93.264562
      },
      "hasMap": "https://www.google.com/maps?cid=347673670564063440",
      "openingHoursSpecification": [
        {
          "@type": "OpeningHoursSpecification",
          "dayOfWeek": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
          ],
          "opens": "11:00",
          "closes": "23:59"
        }
      ],
      "publicAccess": true,
      "hasMenu": "https://twostooges.com/menu/",
      "tourBookingPage": "https://twostooges.com/private-parties/",
      "areaServed": [
        {
          "@type": "GeoCircle",
          "@id": "https://twostooges.com/#service-area",
          "description": "30-mile service radius anchored on Fridley, Minnesota",
          "geoMidpoint": {
            "@type": "GeoCoordinates",
            "latitude": 45.098312,
            "longitude": -93.264562
          },
          "geoRadius": "48280"
        },
        {
          "@type": "State",
          "name": "Minnesota",
          "sameAs": "https://en.wikipedia.org/wiki/Minnesota"
        },
        {
          "@type": "City",
          "name": "Fridley",
          "sameAs": [
            "https://en.wikipedia.org/wiki/Fridley,_Minnesota",
            "https://www.wikidata.org/wiki/Q985235"
          ]
        }
      ],
      "knowsAbout": [
        {
          "@type": "Thing",
          "name": "Billiards",
          "sameAs": [
            "https://en.wikipedia.org/wiki/Cue_sports",
            "https://www.wikidata.org/wiki/Q3341285"
          ]
        },
        {
          "@type": "Thing",
          "name": "Darts",
          "sameAs": [
            "https://en.wikipedia.org/wiki/Darts",
            "https://www.wikidata.org/wiki/Q131471"
          ]
        },
        {
          "@type": "Thing",
          "name": "Pool (cue sports)",
          "sameAs": "https://en.wikipedia.org/wiki/Pool_(cue_sports)"
        },
        {
          "@type": "Thing",
          "name": "Straight pool",
          "sameAs": "https://en.wikipedia.org/wiki/Straight_pool"
        },
        {
          "@type": "Thing",
          "name": "Eight-ball",
          "sameAs": "https://en.wikipedia.org/wiki/Eight-ball"
        },
        {
          "@type": "Thing",
          "name": "Ten-ball",
          "sameAs": "https://en.wikipedia.org/wiki/Ten-ball"
        },
        {
          "@type": "Thing",
          "name": "Sports bar",
          "sameAs": "https://en.wikipedia.org/wiki/Sports_bar"
        }
      ],
      "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Games, leagues & events at Two Stooges",
        "itemListElement": [
          {
            "@id": "https://twostooges.com/billiards/#service"
          },
          {
            "@id": "https://twostooges.com/darts/#service"
          },
          {
            "@id": "https://twostooges.com/leagues/#service"
          },
          {
            "@id": "https://twostooges.com/private-parties/#service"
          }
        ]
      },
      "potentialAction": [
        {
          "@type": "CommunicateAction",
          "name": "Call Two Stooges",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "tel:+17635741399",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "CommunicateAction",
          "name": "Email Two Stooges",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "mailto:info@twostooges.com",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "AskAction",
          "name": "Request a private party",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "https://twostooges.com/private-parties/#request",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "JoinAction",
          "name": "Sign up for a pool or dart league",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "https://twostooges.com/league-signup/#form",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "AskAction",
          "name": "Send Two Stooges a message",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "https://twostooges.com/contact/#form",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        }
      ],
      "sameAs": [
        "https://www.google.com/maps?cid=347673670564063440",
        "https://www.instagram.com/twostoogesbarandgrill/",
        "https://www.yelp.com/biz/two-stooges-sports-bar-and-grill-fridley",
        "https://www.tripadvisor.com/Restaurant_Review-g43087-d5259418-Reviews-Two_Stooges_Sports_Bar_Grill-Fridley_Minnesota.html",
        "https://maps.apple.com/place?place-id=I390CADDFBB3A1DE1"
      ]
    },
    {
      "@type": "WebPage",
      "@id": "https://twostooges.com/billiards/#webpage",
      "url": "https://twostooges.com/billiards/",
      "name": "Billiards & Pool Hall - Twin Cities | Two Stooges",
      "description": "Shoot pool at Two Stooges, a Twin Cities billiards hall in Fridley with 43 Gabriel's and Diamond tables, daily pool specials, leagues and a Pro Shop. Rack up.",
      "isPartOf": {
        "@id": "https://twostooges.com/#website"
      },
      "about": {
        "@id": "https://twostooges.com/#business"
      },
      "inLanguage": "en-US",
      "primaryImageOfPage": {
        "@type": "ImageObject",
        "url": "https://twostooges.com/assets/img/og/billiards.jpg?v=608e7ad5",
        "width": 1200,
        "height": 630,
        "caption": "The 43-table billiard room at Two Stooges Sports Bar in Fridley"
      },
      "dateModified": "2026-10-26",
      "breadcrumb": {
        "@id": "https://twostooges.com/billiards/#breadcrumb"
      },
      "mainEntity": {
        "@id": "https://twostooges.com/billiards/#service"
      }
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://twostooges.com/billiards/#breadcrumb",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://twostooges.com/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Billiards",
          "item": "https://twostooges.com/billiards/"
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/billiards/#service",
      "name": "Billiards & pool table rental",
      "url": "https://twostooges.com/billiards/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      },
      "serviceType": "Pool table rental",
      "areaServed": {
        "@id": "https://twostooges.com/#service-area"
      },
      "category": {
        "@type": "Thing",
        "name": "Billiards",
        "sameAs": [
          "https://en.wikipedia.org/wiki/Cue_sports",
          "https://www.wikidata.org/wiki/Q3341285"
        ]
      },
      "description": "Two Stooges, in Fridley, has been named a top ten billiard room in North America, and City Pages voted it the best place to shoot pool in the Twin Cities. There are 43 Gabriel's and Diamond tables in 9 ft and 7 ft, with room for league players, casual groups and first-timers around every one.",
      "serviceOutput": {
        "@type": "Thing",
        "name": "Pool table time"
      },
      "audience": {
        "@type": "Audience",
        "audienceType": "League players, casual groups and first-time pool players"
      },
      "isRelatedTo": [
        {
          "@id": "https://twostooges.com/leagues/#service"
        },
        {
          "@id": "https://twostooges.com/darts/#service"
        }
      ],
      "mainEntityOfPage": {
        "@id": "https://twostooges.com/billiards/#webpage"
      },
      "offers": [
        {
          "@type": "Offer",
          "name": "Daily pool special – regular",
          "price": "11",
          "priceCurrency": "USD",
          "description": "Table time, 11 AM–5 PM daily, plus tax"
        },
        {
          "@type": "Offer",
          "name": "Daily pool special – seniors",
          "price": "10",
          "priceCurrency": "USD",
          "description": "Table time, 11 AM–5 PM daily, plus tax"
        },
        {
          "@type": "Offer",
          "name": "Daily pool special – premier table",
          "price": "12",
          "priceCurrency": "USD",
          "description": "Table time, 11 AM–5 PM daily, plus tax"
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/darts/#service",
      "name": "Darts",
      "url": "https://twostooges.com/darts/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      }
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/leagues/#service",
      "name": "Pool & dart leagues",
      "url": "https://twostooges.com/leagues/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      }
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/private-parties/#service",
      "name": "Private parties & events",
      "url": "https://twostooges.com/private-parties/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      }
    }
  ]
}
```

### Primary conversion page (/private-parties/)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "https://twostooges.com/#website",
      "url": "https://twostooges.com/",
      "name": "Two Stooges Sports Bar & Grill",
      "publisher": {
        "@id": "https://twostooges.com/#business"
      },
      "inLanguage": "en-US"
    },
    {
      "@type": [
        "BarOrPub",
        "SportsActivityLocation"
      ],
      "@id": "https://twostooges.com/#business",
      "name": "Two Stooges Sports Bar & Grill",
      "alternateName": [
        "Two Stooges",
        "Two Stooges Sports Bar"
      ],
      "url": "https://twostooges.com/",
      "logo": {
        "@type": "ImageObject",
        "url": "https://twostooges.com/assets/img/brand/two-stooges-logo-1200.png?v=1f55c326",
        "width": 1200,
        "height": 543
      },
      "image": "https://twostooges.com/assets/img/og/home.jpg?v=f853b1a1",
      "telephone": "+17635741399",
      "email": "info@twostooges.com",
      "foundingDate": "1988",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "7178 University Ave NE",
        "addressLocality": "Fridley",
        "addressRegion": "MN",
        "postalCode": "55432",
        "addressCountry": "US"
      },
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": 45.098312,
        "longitude": -93.264562
      },
      "hasMap": "https://www.google.com/maps?cid=347673670564063440",
      "openingHoursSpecification": [
        {
          "@type": "OpeningHoursSpecification",
          "dayOfWeek": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
          ],
          "opens": "11:00",
          "closes": "23:59"
        }
      ],
      "publicAccess": true,
      "hasMenu": "https://twostooges.com/menu/",
      "tourBookingPage": "https://twostooges.com/private-parties/",
      "areaServed": [
        {
          "@type": "GeoCircle",
          "@id": "https://twostooges.com/#service-area",
          "description": "30-mile service radius anchored on Fridley, Minnesota",
          "geoMidpoint": {
            "@type": "GeoCoordinates",
            "latitude": 45.098312,
            "longitude": -93.264562
          },
          "geoRadius": "48280"
        },
        {
          "@type": "State",
          "name": "Minnesota",
          "sameAs": "https://en.wikipedia.org/wiki/Minnesota"
        },
        {
          "@type": "City",
          "name": "Fridley",
          "sameAs": [
            "https://en.wikipedia.org/wiki/Fridley,_Minnesota",
            "https://www.wikidata.org/wiki/Q985235"
          ]
        }
      ],
      "knowsAbout": [
        {
          "@type": "Thing",
          "name": "Billiards",
          "sameAs": [
            "https://en.wikipedia.org/wiki/Cue_sports",
            "https://www.wikidata.org/wiki/Q3341285"
          ]
        },
        {
          "@type": "Thing",
          "name": "Darts",
          "sameAs": [
            "https://en.wikipedia.org/wiki/Darts",
            "https://www.wikidata.org/wiki/Q131471"
          ]
        },
        {
          "@type": "Thing",
          "name": "Pool (cue sports)",
          "sameAs": "https://en.wikipedia.org/wiki/Pool_(cue_sports)"
        },
        {
          "@type": "Thing",
          "name": "Straight pool",
          "sameAs": "https://en.wikipedia.org/wiki/Straight_pool"
        },
        {
          "@type": "Thing",
          "name": "Eight-ball",
          "sameAs": "https://en.wikipedia.org/wiki/Eight-ball"
        },
        {
          "@type": "Thing",
          "name": "Ten-ball",
          "sameAs": "https://en.wikipedia.org/wiki/Ten-ball"
        },
        {
          "@type": "Thing",
          "name": "Sports bar",
          "sameAs": "https://en.wikipedia.org/wiki/Sports_bar"
        }
      ],
      "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Games, leagues & events at Two Stooges",
        "itemListElement": [
          {
            "@id": "https://twostooges.com/billiards/#service"
          },
          {
            "@id": "https://twostooges.com/darts/#service"
          },
          {
            "@id": "https://twostooges.com/leagues/#service"
          },
          {
            "@id": "https://twostooges.com/private-parties/#service"
          }
        ]
      },
      "potentialAction": [
        {
          "@type": "CommunicateAction",
          "name": "Call Two Stooges",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "tel:+17635741399",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "CommunicateAction",
          "name": "Email Two Stooges",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "mailto:info@twostooges.com",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "AskAction",
          "name": "Request a private party",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "https://twostooges.com/private-parties/#request",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "JoinAction",
          "name": "Sign up for a pool or dart league",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "https://twostooges.com/league-signup/#form",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        },
        {
          "@type": "AskAction",
          "name": "Send Two Stooges a message",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "https://twostooges.com/contact/#form",
            "actionPlatform": [
              "http://schema.org/DesktopWebPlatform",
              "http://schema.org/MobileWebPlatform"
            ]
          }
        }
      ],
      "sameAs": [
        "https://www.google.com/maps?cid=347673670564063440",
        "https://www.instagram.com/twostoogesbarandgrill/",
        "https://www.yelp.com/biz/two-stooges-sports-bar-and-grill-fridley",
        "https://www.tripadvisor.com/Restaurant_Review-g43087-d5259418-Reviews-Two_Stooges_Sports_Bar_Grill-Fridley_Minnesota.html",
        "https://maps.apple.com/place?place-id=I390CADDFBB3A1DE1"
      ]
    },
    {
      "@type": "WebPage",
      "@id": "https://twostooges.com/private-parties/#webpage",
      "url": "https://twostooges.com/private-parties/",
      "name": "Private Party Venue - Twin Cities | Two Stooges Sports Bar",
      "description": "Host a birthday, office party or banquet at Two Stooges, a Twin Cities sports bar in Fridley with custom menus, pool tables and dart boards. Request a date.",
      "isPartOf": {
        "@id": "https://twostooges.com/#website"
      },
      "about": {
        "@id": "https://twostooges.com/#business"
      },
      "inLanguage": "en-US",
      "primaryImageOfPage": {
        "@type": "ImageObject",
        "url": "https://twostooges.com/assets/img/og/parties.jpg?v=027fbd99",
        "width": 1200,
        "height": 630,
        "caption": "Friends playing pool at a party at Two Stooges Sports Bar & Grill in Fridley"
      },
      "dateModified": "2026-10-26",
      "breadcrumb": {
        "@id": "https://twostooges.com/private-parties/#breadcrumb"
      },
      "mainEntity": {
        "@id": "https://twostooges.com/private-parties/#service"
      }
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://twostooges.com/private-parties/#breadcrumb",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://twostooges.com/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Private Parties",
          "item": "https://twostooges.com/private-parties/"
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/billiards/#service",
      "name": "Billiards & pool table rental",
      "url": "https://twostooges.com/billiards/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      }
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/darts/#service",
      "name": "Darts",
      "url": "https://twostooges.com/darts/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      }
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/leagues/#service",
      "name": "Pool & dart leagues",
      "url": "https://twostooges.com/leagues/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      }
    },
    {
      "@type": "Service",
      "@id": "https://twostooges.com/private-parties/#service",
      "name": "Private parties & events",
      "url": "https://twostooges.com/private-parties/",
      "provider": {
        "@id": "https://twostooges.com/#business"
      },
      "serviceType": "Private event hosting",
      "areaServed": {
        "@id": "https://twostooges.com/#service-area"
      },
      "category": {
        "@type": "Thing",
        "name": "Party",
        "sameAs": "https://en.wikipedia.org/wiki/Party"
      },
      "description": "Two Stooges is ready for your next birthday, holiday party, office outing or banquet in Fridley, for groups from across the Twin Cities. We'll customize the menu and the space for your group.",
      "serviceOutput": {
        "@type": "Thing",
        "name": "Private party"
      },
      "audience": {
        "@type": "Audience",
        "audienceType": "Groups planning birthdays, office parties, banquets and holiday parties"
      },
      "isRelatedTo": [
        {
          "@id": "https://twostooges.com/billiards/#service"
        },
        {
          "@id": "https://twostooges.com/darts/#service"
        }
      ],
      "mainEntityOfPage": {
        "@id": "https://twostooges.com/private-parties/#webpage"
      }
    }
  ]
}
```
