"""Service-area data: every community within about 20 miles of Two Stooges, grouped by county.

Coordinates are city-centre points from GeoNames (https://www.geonames.org/, CC BY 4.0), read 2026-11-12.
Counties are from Wikipedia's "List of cities in Minnesota" (checked 2026-11-12). A city that crosses a
county line is listed once, under its main county. Distances are straight-line and worked out at build time.
"""
RADIUS_MI = 20
STATEMENT = ("Serving the Twin Cities within about 20 miles of Fridley, Minnesota, "
             "from Minneapolis and St. Paul to the north metro.")
SOURCE_COUNTIES = "https://en.wikipedia.org/wiki/List_of_cities_in_Minnesota"
SOURCE_COORDS = "https://www.geonames.org/"

# county -> [(city, latitude, longitude)]
COUNTIES = {
    "Anoka": [
        ("Fridley", 45.08608, -93.26328), ("Spring Lake Park", 45.10774, -93.238), ("Coon Rapids", 45.11997, -93.28773),
        ("Hilltop", 45.0533, -93.24745), ("Columbia Heights", 45.0408, -93.263), ("Blaine", 45.1608, -93.23495),
        ("Lexington", 45.14247, -93.16328), ("Circle Pines", 45.14858, -93.15161), ("Anoka", 45.19774, -93.38718),
        ("Andover", 45.2333, -93.29134), ("Lino Lakes", 45.16024, -93.08883), ("Ham Lake", 45.25024, -93.24995),
        ("Centerville", 45.16302, -93.05578), ("Ramsey", 45.2611, -93.45), ("Columbus", 45.26522, -93.05015),
        ("East Bethel", 45.31941, -93.20245), ("Oak Grove", 45.3408, -93.3269), ("Nowthen", 45.32802, -93.47023),
    ],
    "Hennepin": [
        ("Brooklyn Center", 45.07608, -93.33273), ("Brooklyn Park", 45.09413, -93.35634), ("Robbinsdale", 45.03219, -93.33856),
        ("St. Anthony", 45.02052, -93.218), ("Crystal", 45.03274, -93.36023), ("Osseo", 45.11941, -93.40245),
        ("New Hope", 45.03802, -93.38662), ("Golden Valley", 45.00969, -93.34912), ("Minneapolis", 44.97997, -93.26384),
        ("Champlin", 45.18885, -93.39745), ("Maple Grove", 45.07246, -93.45579), ("Plymouth", 45.01052, -93.45551),
        ("St. Louis Park", 44.9483, -93.34801), ("Corcoran", 45.09524, -93.54746), ("Wayzata", 44.97413, -93.50662),
        ("Richfield", 44.8833, -93.283), ("Edina", 44.88969, -93.34995), ("Hopkins", 44.92496, -93.46273),
        ("Rogers", 45.18885, -93.55301), ("Dayton", 45.24385, -93.51496), ("Medina", 45.03524, -93.58246),
        ("Long Lake", 44.98663, -93.57162), ("Deephaven", 44.92969, -93.52246), ("Minnetonka", 44.9133, -93.50329),
        ("Bloomington", 44.8408, -93.29828), ("Loretto", 45.05469, -93.63552), ("Minnetonka Beach", 44.93969, -93.57662),
        ("Orono", 44.97135, -93.6044), ("Greenwood", 44.91496, -93.55329), ("Eden Prairie", 44.85469, -93.47079),
    ],
    "Ramsey": [
        ("Mounds View", 45.10497, -93.20856), ("New Brighton", 45.06552, -93.20189), ("Shoreview", 45.07913, -93.14717),
        ("Arden Hills", 45.05024, -93.15661), ("Lauderdale", 44.99858, -93.20578), ("Roseville", 45.00608, -93.15661),
        ("Falcon Heights", 44.99163, -93.16633), ("North Oaks", 45.10274, -93.07911), ("Vadnais Heights", 45.05747, -93.07383),
        ("Little Canada", 45.02691, -93.08772), ("White Bear Lake", 45.08469, -93.00994), ("St. Paul", 44.94441, -93.09327),
        ("North St. Paul", 45.01247, -92.99188), ("Maplewood", 44.95302, -92.99522),
    ],
    "Washington": [
        ("Hugo", 45.15997, -92.99327), ("Birchwood Village", 45.06108, -92.97605), ("Dellwood", 45.08997, -92.97244),
        ("Mahtomedi", 45.06969, -92.9516), ("Grant", 45.08441, -92.91049), ("Landfall", 44.9508, -92.9766),
        ("Oakdale", 44.96302, -92.96494), ("Forest Lake", 45.27886, -92.98522), ("Woodbury", 44.92386, -92.95938),
    ],
    "Dakota": [
        ("Lilydale", 44.91608, -93.12605), ("West St. Paul", 44.91608, -93.10161), ("Mendota Heights", 44.88358, -93.13827),
        ("Sunfish Lake", 44.8708, -93.09855), ("South St. Paul", 44.89274, -93.03494),
    ],
}
# Labelled on the map (the rest are unlabelled dots): name -> (dx, dy, text-anchor)
MAP_LABELS = {
    "Minneapolis": (0, 18, "middle"), "St. Paul": (-9, 5, "end"), "Blaine": (8, -6, "start"), "Coon Rapids": (-9, -4, "end"),
    "Anoka": (-8, -6, "end"), "Andover": (0, -10, "middle"), "Maple Grove": (-8, 4, "end"), "Plymouth": (-8, 14, "end"),
    "Eden Prairie": (0, 18, "middle"), "Bloomington": (8, 14, "start"), "Woodbury": (-8, 18, "end"), "White Bear Lake": (0, -10, "middle"),
    "Forest Lake": (-8, 4, "end"), "East Bethel": (8, 4, "start"), "Rogers": (0, 19, "middle"),
}
