"""City and county pages under /service-area/ (closest cities only, client decision 2026-11-12).

Every fact below was read from the linked source on FACTS_CHECKED. Nothing here is recalled from memory:
a value the source does not give is left out. Each page must pass the gate in build.py (5+ sourced facts,
300+ words found on no other page with city names masked).
"""
FACTS_CHECKED = "2026-11-12"
W = "https://en.wikipedia.org/wiki/"
FRIDLEY_SRC = W + "Fridley,_Minnesota"

# name -> page data. "border" is the relation to Fridley as stated on Fridley's Wikipedia page.
CITIES = {
    "Fridley": {
        "slug": "fridley-mn", "county": "Anoka", "wiki": FRIDLEY_SRC, "h1": "in",
        "desc": "Two Stooges is Fridley's sports bar and pool hall: 43 pool tables, electronic dart boards and a full grill at 7178 University Ave NE on Highway 47. Stop in.",
        "lead": "Two Stooges Sports Bar &amp; Grill is in Fridley, at 7178 University Ave NE, with 43 pool tables, electronic dart boards and a full bar and grill for Fridley players, teams and groups.",
        "facts": [("County", "Anoka County"), ("Population (2020 census)", "29,590"), ("Incorporated", "Village in 1949, city in 1957"),
                  ("Land area", "10.16 sq mi"), ("ZIP codes", "55421, 55432"),
                  ("Main highways", "Interstate 694, Highway 47, Highway 65"), ("City hall", "Fridley Civic Campus, 7071 University Avenue NE")],
        "h2": "A Fridley pool hall since 1988",
        "local": [
            "Two Stooges is a Fridley business through and through. The bar has been at 7178 University Ave NE since it opened as University Billiards in 1988. University Avenue is Minnesota Highway 47, one of the three main routes through the city along with Highway 65 and Interstate 694, and the Fridley Civic Campus, home to city hall, is on the same avenue at 7071.",
            "Fridley runs along the east bank of the Mississippi River. Rice Creek crosses the middle of the city, and Moore Lake and Locke Lake sit inside its limits. The township was called Manomin, from the Ojibwe word for wild rice, until the legislature renamed it for Abram M. Fridley in 1879. Today the city is home to Medtronic's operational headquarters and to Springbrook Nature Center, a 127-acre preserve on the Coon Rapids border. Whichever end of town you start from, the pool tables are right here in Fridley.",
            "Fridley has a place in frozen pizza history too: Totino's opened a factory in the city in 1970.",
        ],
        "faq": [
            ("Where in Fridley is Two Stooges?", "At 7178 University Ave NE, Fridley, MN 55432, on Highway 47. 55432 is one of Fridley's two ZIP codes; the other is 55421."),
            ("Is Two Stooges in Fridley or in Minneapolis?", "In Fridley, which is its own city in Anoka County. Minneapolis borders Fridley to the southwest."),
            ("How long has Two Stooges been in Fridley?", "Since 1988, when it opened as University Billiards. Fridley itself became a village in 1949 and a city in 1957."),
        ],
    },
    "Spring Lake Park": {
        "slug": "spring-lake-park-mn", "county": "Anoka", "wiki": W + "Spring_Lake_Park,_Minnesota",
        "border": "Northeast of Fridley; Fridley lies on Spring Lake Park's west and south sides",
        "desc": "Spring Lake Park's nearest sports bar and pool hall is Two Stooges in Fridley, on the same University Avenue NE: 43 pool tables, darts and a full grill. Visit.",
        "lead": "Two Stooges is the pool hall and sports bar next door to Spring Lake Park, on University Avenue NE in Fridley, with 43 pool tables, electronic dart boards and a full grill.",
        "facts": [("County", "Mainly Anoka County, with part in Ramsey County"), ("Population (2020 census)", "7,188"), ("Land area", "2.00 sq mi"),
                  ("ZIP code", "55432"), ("Main highways", "Highway 47 (University Avenue NE), Highway 65 (Central Avenue NE), County Highway 10")],
        "h2": "Two Stooges and Spring Lake Park share a road and a ZIP code",
        "local": [
            "Spring Lake Park is Two Stooges' closest neighbor. The city covers just 2 square miles and wraps around Fridley's northeast corner, with Fridley on its west and south sides and Blaine to the north. It even shares the bar's ZIP code, 55432.",
            "Getting here is simple, because University Avenue NE is Highway 47 in Spring Lake Park too: the same road the bar sits on. Central Avenue NE, which is Highway 65, and County Highway 10 are the city's other main routes. Most of Spring Lake Park is in Anoka County, with a small part in Ramsey County. The city nearly doubled in the 1960s, growing from 3,260 residents to 6,417, and Laddie Lake, on the Blaine line, lies partly inside it.",
            "Spring Lake Park High School is the city's high school, and the school district that serves the area keeps its district services and enrollment center in town as well. After a small dip between 2000 and 2010, the population rose 12.1 percent to reach 7,188 by 2020. With Fridley on two sides of the city, Two Stooges is an easy pick for a Spring Lake Park league night.",
        ],
        "faq": [
            ("How far is Two Stooges from Spring Lake Park?", "{dist} from the center of Spring Lake Park in a straight line. Both are on University Avenue NE, which is Highway 47."),
            ("Do Spring Lake Park and Two Stooges share a ZIP code?", "Yes. Spring Lake Park's ZIP code is 55432, and Two Stooges is at 7178 University Ave NE, Fridley, MN 55432."),
            ("Is Spring Lake Park in the same county as Two Stooges?", "Mostly. Spring Lake Park is mainly in Anoka County, with part in Ramsey County. Two Stooges is in Fridley, in Anoka County."),
        ],
    },
    "Coon Rapids": {
        "slug": "coon-rapids-mn", "county": "Anoka", "wiki": W + "Coon_Rapids,_Minnesota", "coord_src": "wiki",
        "border": "North of Fridley; the two cities share a border",
        "desc": "Coon Rapids players come to Two Stooges in Fridley for 43 pool tables, electronic darts, leagues and a full grill, just down Highway 47 from the city. Rack up.",
        "lead": "Two Stooges is the sports bar and pool hall just south of Coon Rapids, on Highway 47 in Fridley, with 43 pool tables, electronic dart boards, leagues and a full grill.",
        "facts": [("County", "Anoka County"), ("Population (2020 census)", "63,599"), ("Incorporated", "Village in 1952, city in 1959"),
                  ("Land area", "22.60 sq mi"), ("ZIP codes", "55433, 55448"), ("Main highways", "U.S. Highway 10, Highway 47, Highway 610")],
        "h2": "From the Coon Rapids Dam to the pool tables",
        "local": [
            "Coon Rapids borders Fridley to the north, and the two cities meet at Springbrook Nature Center, a 127-acre preserve on the city line. Highway 47 is one of the three main highways through Coon Rapids, with U.S. Highway 10 and Highway 610, and it is the road Two Stooges is on in Fridley.",
            "With 63,599 residents at the 2020 census, Coon Rapids is one of the bigger cities in Anoka County. Its name goes back to Coon Creek: when the Coon Rapids Dam was built, the township renamed itself Coon Creek Rapids, later shortened. The dam was finished in 1914 and is now part of a regional park on the Mississippi. Coon Rapids Boulevard follows the Red River Ox Cart Trail, laid out in 1835 between Minneapolis and Anoka. If your day includes Bunker Hills Regional Park or a class at Anoka-Ramsey Community College, pool, darts and dinner are one city south.",
            "Cenaiko Lake and Crooked Lake are shared with Andover, the neighbor to the north; about two-thirds of the pair lies inside Coon Rapids. Mercy, part of the Allina Health system, was the largest employer in the city's 2014 report, and RMS Company, a medical device maker, has its headquarters in town.",
        ],
        "faq": [
            ("How far is Two Stooges from Coon Rapids?", "{dist} from the center of Coon Rapids in a straight line. Coon Rapids covers 22.60 square miles, so the trip is longer from the north end of the city."),
            ("Which highway links Coon Rapids and Two Stooges?", "Highway 47. It is one of the main highways in Coon Rapids, and Two Stooges is on it at 7178 University Ave NE in Fridley."),
            ("Does Coon Rapids border Fridley?", "Yes. Coon Rapids is Fridley's neighbor to the north, and Springbrook Nature Center sits on the border between them."),
        ],
    },
    "Mounds View": {
        "slug": "mounds-view-mn", "county": "Ramsey", "wiki": W + "Mounds_View,_Minnesota",
        "border": "East of Fridley; the two cities share a border",
        "desc": "From Mounds View, Two Stooges is just over the county line in Fridley: a sports bar and pool hall with 43 tables, electronic darts and a full grill. Come play.",
        "lead": "Two Stooges is the sports bar and pool hall next to Mounds View, just across the county line in Fridley, with 43 pool tables, electronic dart boards and a full grill.",
        "facts": [("County", "Ramsey County"), ("Population (2020 census)", "13,249"), ("Incorporated", "Township in 1858, village in 1958"),
                  ("Land area", "4.06 sq mi"), ("ZIP code", "55112"), ("Main highways", "U.S. Highway 10, Interstate 35W, Mounds View Boulevard (County Road 10)")],
        "h2": "One county line between Mounds View and the bar",
        "local": [
            "Mounds View borders Fridley on the east, and the line between them is also the line between Ramsey County and Anoka County: the county boundary forms Mounds View's western and northern edges. A trip to Two Stooges from Mounds View crosses that line, even though the two city centers are only {dist_plain} apart.",
            "U.S. Highway 10, Interstate 35W and Mounds View Boulevard are the city's main roads. The boulevard is County Road 10, renamed inside the city in 2016. Mounds View began as a township in 1858 and became a village exactly a century later. Rice Creek runs through its southeast corner and also through the middle of Fridley, and the two cities share an employer as well: Medtronic opened a campus in Mounds View in 2007 and has its operational headquarters in Fridley.",
            "The Twin Cities Army Ammunition Plant, just across the city's eastern border in Arden Hills, fueled growth here after World War II. Shoreview, Arden Hills, New Brighton, Spring Lake Park and Blaine are the other neighbors, and Edgewood Middle School and Pinewood Elementary belong to Mounds View Public Schools. That Medtronic campus stands in the northeast corner of the city, on what used to be the Bridges of Mounds View golf course, and Sysco is another of the city's notable businesses.",
        ],
        "faq": [
            ("How far is Two Stooges from Mounds View?", "{dist} from the center of Mounds View in a straight line. Mounds View is Fridley's neighbor to the east."),
            ("Is Mounds View in the same county as Two Stooges?", "No. Mounds View is in Ramsey County and Two Stooges is in Fridley, in Anoka County. The county line runs along Mounds View's western edge."),
            ("What ZIP code is Two Stooges in?", "55432. Mounds View uses 55112, so searching by the bar's address works better than searching by ZIP: 7178 University Ave NE, Fridley."),
        ],
    },
    "Brooklyn Center": {
        "slug": "brooklyn-center-mn", "county": "Hennepin", "wiki": W + "Brooklyn_Center,_Minnesota",
        "border": "West of Fridley, across the Mississippi River",
        "desc": "From Brooklyn Center, Two Stooges is across the Mississippi in Fridley: a sports bar and pool hall with 43 tables, electronic darts, leagues and a full grill.",
        "lead": "Two Stooges is the sports bar and pool hall across the river from Brooklyn Center, in Fridley, with 43 pool tables, electronic dart boards, leagues and a full grill.",
        "facts": [("County", "Hennepin County"), ("Population (2020 census)", "33,782"), ("Incorporated", "Village in 1911, charter city in 1966"),
                  ("Land area", "8.00 sq mi"), ("ZIP codes", "55429, 55430"), ("Main highways", "Interstates 94 and 694, Highways 100 and 252")],
        "h2": "Across the Mississippi from Brooklyn Center",
        "local": [
            "Brooklyn Center and Fridley face each other across the Mississippi River. The river is Brooklyn Center's eastern boundary and Fridley's western one, so the bar is on the opposite bank, in Anoka County, while Brooklyn Center is in Hennepin County. Interstate 694 is a main highway in both cities.",
            "Brooklyn Center became a village in 1911, when residents incorporated to keep from being annexed by Minneapolis, and it adopted a city charter in 1966. Interstates 94 and 694 and Highways 100 and 252 all pass through its 8 square miles. Shingle Creek runs through Palmer Lake, a preserve of more than 200 acres, before it reaches the Mississippi, and the Heritage Center, an 1878 country estate, is now a city-owned event center. For a night of pool or darts, cross the river to Fridley.",
            "The village was formed from parts of Brooklyn Township and Crystal Lake Township, and the old road to Osseo is now Brooklyn Boulevard. Upper Twin Lake, in the southwest part of the city, covers 117 acres and connects to a chain of lakes that drains into Shingle Creek. North Mississippi Regional Park lines the river, Brookdale opened in 1960 as the population passed 24,000, and the FBI's Minneapolis field office is located here. Minneapolis lies directly to the south, and Brooklyn Park, the larger city that shares the Brooklyn name, grew out of the same township. PROMEON, a division of Medtronic, is the largest employer listed for the city, another tie to Fridley, where Medtronic has its operational headquarters.",
        ],
        "faq": [
            ("How far is Two Stooges from Brooklyn Center?", "{dist} from the center of Brooklyn Center in a straight line. The Mississippi River is in between, so your route will cross it."),
            ("Which side of the river is Two Stooges on?", "The east side. Two Stooges is in Fridley, on the opposite bank of the Mississippi from Brooklyn Center."),
            ("Is Brooklyn Center in the same county as Two Stooges?", "No. Brooklyn Center is in Hennepin County. Two Stooges is in Fridley, in Anoka County."),
        ],
    },
    "New Brighton": {
        "slug": "new-brighton-mn", "county": "Ramsey", "wiki": W + "New_Brighton,_Minnesota",
        "border": "East of Fridley; the two cities share a border",
        "desc": "New Brighton's neighbor for pool and darts is Two Stooges in Fridley: a sports bar with 43 pool tables, electronic dart boards, leagues and a full grill menu.",
        "lead": "Two Stooges is the sports bar and pool hall next door to New Brighton, in Fridley, with 43 pool tables, electronic dart boards, leagues and a full grill.",
        "facts": [("County", "Ramsey County"), ("Population (2020 census)", "23,454"), ("Incorporated", "1891"),
                  ("Land area", "6.49 sq mi"), ("ZIP code", "55112"), ("Main highways", "Interstate 35W, Interstate 694")],
        "h2": "From the stockyard town to the pool hall next door",
        "local": [
            "New Brighton lies east of Fridley. The two cities share a border, and Interstate 694 is a main highway in both. New Brighton is in Ramsey County and Two Stooges is in Anoka County, so the short trip crosses the county line.",
            "New Brighton was incorporated in 1891, three years after the Minneapolis Stockyards and Packing Company was formed, and it was named after Brighton, Massachusetts. The stockyard years are still celebrated each year at Stockyard Days in Long Lake Regional Park. Interstate 35W is the city's other main highway, and Rice Creek flows through the northern part of New Brighton as well as through central Fridley. When the festival or a day at Long Lake is over, 43 pool tables are waiting one city to the west.",
            "Long before the stockyards, Mdewakanton Dakota people lived near the lakes in the mid-18th century and harvested wild rice. During World War II the Twin Cities Ordnance Plant made .30 and .50 caliber ammunition and employed about 24,000 people at its peak. Glacial terrain is still visible at Long Lake Regional Park, Irondale High School is part of Mounds View Public Schools, and Arden Hills, Shoreview, Roseville and St. Anthony are all close by. The city's ZIP code is 55112, the same one Mounds View uses, while Two Stooges is in Fridley's 55432. Pike Lake gave its name to a former kindergarten center, and APi Group, a company based in the city, joined the Fortune 500 in 2026.",
        ],
        "faq": [
            ("How far is Two Stooges from New Brighton?", "{dist} from the center of New Brighton in a straight line. New Brighton is Fridley's neighbor to the east."),
            ("Which highway do New Brighton and Fridley share?", "Interstate 694. It is a main highway in both cities. Two Stooges itself is on Highway 47, at 7178 University Ave NE in Fridley."),
            ("Is New Brighton in Anoka County?", "No. New Brighton is in Ramsey County. Two Stooges is over the line in Fridley, which is in Anoka County."),
        ],
    },
    "Columbia Heights": {
        "slug": "columbia-heights-mn", "county": "Anoka", "wiki": W + "Columbia_Heights,_Minnesota",
        "border": "South and southeast of Fridley; the two cities share a border",
        "desc": "From Columbia Heights, Two Stooges is straight up University Avenue in Fridley: a sports bar and pool hall with 43 tables, electronic darts and a full grill.",
        "lead": "Two Stooges is the sports bar and pool hall up University Avenue from Columbia Heights, in Fridley, with 43 pool tables, electronic dart boards and a full grill.",
        "facts": [("County", "Anoka County"), ("Population (2020 census)", "21,973"), ("Incorporated", "Village in 1898, city in 1921"),
                  ("Land area", "3.41 sq mi"), ("ZIP code", "55421"), ("Main highways", "Highway 47 (University Avenue), Highway 65 (Central Avenue)")],
        "h2": "Columbia Heights and Fridley: one township, one avenue",
        "local": [
            "Columbia Heights and Fridley started out as one place: Columbia Heights became a village in 1898 by separating from Fridley Township. The two still share a border, with Fridley to the north and west, and they share ZIP code 55421.",
            "University Avenue is Highway 47 in Columbia Heights, and Two Stooges sits on the same avenue farther north, at 7178 University Ave NE. Central Avenue, which is Highway 65, is the other main route. Columbia Heights fits five lakes and ponds, the Heights Theater and Huset Park into 3.41 square miles between Minneapolis and Fridley, and it was named an All-America City in 2016. The small city of Hilltop sits entirely inside it.",
            "One odd piece of local history: Lincoln's funeral car, bought by Thomas Lowry, was stored in the city until a fire destroyed it in 1911. Stinson Boulevard runs along one of the highest points in Hennepin, Ramsey and Anoka counties, Kordiak Park is an Anoka County park within the city limits, and New Brighton and St. Anthony are the neighbors to the east.",
        ],
        "faq": [
            ("How far is Two Stooges from Columbia Heights?", "{dist} from the center of Columbia Heights in a straight line, north along University Avenue."),
            ("Is Two Stooges on the same road as Columbia Heights' University Avenue?", "Yes. University Avenue is Highway 47 in Columbia Heights, and Two Stooges is at 7178 University Ave NE in Fridley, on Highway 47."),
            ("Are Columbia Heights and Fridley in the same county?", "Yes, both are in Anoka County. Columbia Heights was part of Fridley Township until it became a village in 1898."),
        ],
    },
    "Brooklyn Park": {
        "slug": "brooklyn-park-mn", "county": "Hennepin", "wiki": W + "Brooklyn_Park,_Minnesota",
        "border": "West of Fridley, across the Mississippi River",
        "desc": "Brooklyn Park players cross the Mississippi to Two Stooges in Fridley for 43 pool tables, electronic darts, leagues, tournaments and a full grill. Come play.",
        "lead": "Two Stooges is the sports bar and pool hall across the Mississippi from Brooklyn Park, in Fridley, with 43 pool tables, electronic dart boards, leagues and tournaments.",
        "facts": [("County", "Hennepin County"), ("Population (2020 census)", "86,478"), ("Incorporated", "Township in 1858, village in 1954, city in 1969"),
                  ("Land area", "26.08 sq mi"), ("ZIP codes", "55428, 55429, 55443, 55444, 55445"),
                  ("Main highways", "Interstates 94 and 694, U.S. Highway 169, Highways 252 and 610")],
        "h2": "A river away from Brooklyn Park",
        "local": [
            "Brooklyn Park is across the Mississippi from Two Stooges. The river forms the city's eastern boundary, with Fridley and Coon Rapids on the far bank in Anoka County. Brooklyn Park is in Hennepin County and, with 86,478 residents at the 2020 census, has nearly three times Fridley's population.",
            "Settlers from Brooklyn, Michigan, named the township, which became a village in 1954 and a city in 1969. Highways 252 and 610, U.S. Highway 169 and Interstates 94 and 694 are its main routes, and Interstate 694 is a main highway in Fridley too. Local landmarks include the Eidem Homestead, a working farm from the 1900s, Mississippi Gateway Regional Park beside the Coon Rapids Dam, and North Hennepin Community College. Jesse Ventura was mayor here from 1991 to 1995, before he became governor.",
            "Before any of that, the area was settled in 1852 and organized as Brooklyn Township in 1858; the southeast corner split off as Brooklyn Center in 1911. Rasmussen University and a Hennepin Technical College campus are in the city, the Rush Creek Regional Trail is named for a local creek, and manufacturing is the largest source of jobs, ahead of health care. County Road 81 is another of the main routes.",
        ],
        "faq": [
            ("How far is Two Stooges from Brooklyn Park?", "{dist} from the center of Brooklyn Park in a straight line. Brooklyn Park covers 26 square miles, so the distance varies a lot by neighborhood."),
            ("Do I have to cross the Mississippi to get to Two Stooges from Brooklyn Park?", "Yes. The river is Brooklyn Park's eastern boundary, and Two Stooges is in Fridley on the other bank."),
            ("Is Brooklyn Park in the same county as Two Stooges?", "No. Brooklyn Park is in Hennepin County, and Two Stooges is in Fridley, in Anoka County."),
        ],
    },
    "Blaine": {
        "slug": "blaine-mn", "county": "Anoka", "wiki": W + "Blaine,_Minnesota",
        "border": "North of Fridley; the two cities share a border",
        "desc": "Blaine players head down University Avenue to Two Stooges in Fridley: a sports bar and pool hall with 43 tables, electronic darts, leagues and a full grill.",
        "lead": "Two Stooges is the sports bar and pool hall just south of Blaine, down University Avenue in Fridley, with 43 pool tables, electronic dart boards, leagues and a full grill.",
        "facts": [("County", "Mainly Anoka County, with part in Ramsey County"), ("Population (2020 census)", "70,222"), ("Incorporated", "1954 (township organized 1877)"),
                  ("Land area", "32.90 sq mi"), ("ZIP codes", "55014, 55434, 55449"),
                  ("Main highways", "Interstate 35W, U.S. Highway 10, Highways 65 and 610, University Avenue")],
        "h2": "South of Blaine on University Avenue",
        "local": [
            "Blaine is the largest city in Anoka County, and it borders Fridley on the north. University Avenue is one of Blaine's main roads. It continues through Spring Lake Park as Highway 47 to the bar at 7178 University Ave NE.",
            "Blaine was organized as a township in 1877, named for Senator James G. Blaine of Maine, and incorporated in 1954. It now has 70,222 residents across almost 33 square miles, most of it in Anoka County with a part in Ramsey County. The city is known for sports: the National Sports Center, with soccer, golf and an eight-sheet ice arena, and TPC Twin Cities, which hosts the PGA Tour's 3M Open. If you're in town for a tournament at either one, Two Stooges is {dist_plain} south of the city center.",
            "Greenberry Chambers, a formerly enslaved man from Kentucky, became the first permanent resident in 1865. The Blaine Wetland Sanctuary protects 500 acres with a boardwalk and trails, and Laddie Lake, shared with Spring Lake Park, is the city's only natural lake. Aveda and Infinite Campus are the two largest employers listed for the city.",
        ],
        "faq": [
            ("How far is Two Stooges from Blaine?", "{dist} from the center of Blaine in a straight line. Blaine covers almost 33 square miles, so it is farther from the north side of the city."),
            ("Is Two Stooges near the National Sports Center?", "The National Sports Center is in Blaine, and Blaine borders Fridley, where Two Stooges is. Use the directions link on this page for the route from your field or rink."),
            ("Is Blaine in the same county as Two Stooges?", "Yes, for the most part. Blaine is mainly in Anoka County, with part in Ramsey County, and it is the county's largest city. Two Stooges is in Fridley, also in Anoka County."),
        ],
    },
    "Minneapolis": {
        "slug": "minneapolis-mn", "county": "Hennepin", "wiki": W + "Minneapolis",
        "border": "Southwest of Fridley; the two cities share a border",
        "desc": "Just north of Minneapolis, Two Stooges in Fridley is a sports bar and pool hall with 43 tables, electronic darts, leagues, tournaments and a full grill menu.",
        "lead": "Two Stooges is the sports bar and pool hall just north of Minneapolis, in Fridley, with 43 pool tables, electronic dart boards, leagues, tournaments and a full grill.",
        "facts": [("County", "Hennepin County"), ("Population (2020 census)", "429,954"), ("Incorporated", "City in 1867"),
                  ("Land area", "54.00 sq mi"), ("Main highway named", "Interstate 35W")],
        "h2": "Just past the north edge of Minneapolis",
        "local": [
            "Minneapolis sits just southwest of Fridley and directly south of Columbia Heights, so Two Stooges is just past the city's northern edge. From the center of Minneapolis it is {dist_plain} in a straight line.",
            "Highway 47 is University Avenue in Columbia Heights, the city between Minneapolis and Fridley, and Two Stooges is on that avenue at 7178 University Ave NE. Northeast Minneapolis has an arts district with about 400 independent artists and the Art-A-Whirl open studio tour every May. The Mississippi runs through the city past Saint Anthony Falls, the only natural waterfall on the river, and the same river forms Fridley's western border. The name itself joins the Dakota word for water, mni, with the Greek word for city, polis.",
            "The town was authorized in 1856, incorporated as a city in 1867 and merged with St. Anthony in 1872. It holds a 12-mile stretch of the Mississippi and occupies both banks, and its landmarks include the Guthrie Theater, the Walker Art Center, the Mill City Museum and the Basilica of Saint Mary.",
        ],
        "faq": [
            ("How far is Two Stooges from Minneapolis?", "{dist} from the center of Minneapolis in a straight line. It is closer from the north side of the city, which borders Fridley and Columbia Heights."),
            ("Is Two Stooges in Minneapolis?", "No. Two Stooges is in Fridley, a separate city in Anoka County that borders Minneapolis to the northeast. The address is 7178 University Ave NE, Fridley, MN 55432."),
            ("Which county is Two Stooges in?", "Anoka County. Minneapolis is the seat of Hennepin County, so the trip to Two Stooges crosses the county line."),
        ],
    },
}

COUNTIES = {
    "Anoka": {
        "slug": "anoka-county-mn", "wiki": W + "Anoka_County,_Minnesota",
        "desc": "Two Stooges in Fridley is Anoka County's sports bar and pool hall: 43 pool tables, electronic darts, leagues and a full grill for Blaine, Coon Rapids and more.",
        "lead": "Two Stooges Sports Bar &amp; Grill is in Anoka County, in the city of Fridley, with 43 pool tables, electronic dart boards, leagues and a full grill for players from across the county.",
        "facts": [("County seat", "Anoka"), ("Largest city", "Blaine"), ("Population (2020 census)", "363,887"), ("Organized", "May 23, 1857"),
                  ("Area", "446 sq mi (423 sq mi land)"), ("Neighboring counties", "Isanti, Chisago, Washington, Ramsey, Hennepin, Sherburne")],
        "h2": "Two Stooges' home county",
        "local": [
            "Anoka County is home. Two Stooges is in Fridley, at the county's southern end, where the Mississippi River forms the county's southwest boundary. The county was organized in 1857 from parts of Ramsey and Benton counties and takes its name from the city of Anoka, a Dakota word meaning on both sides, for the city's place on both banks of the Rum River.",
            "The county has 363,887 residents and has become mostly suburban since Interstate 35W was built. Its terrain is low, rolling and wooded, and Rice Creek and Coon Creek both run through it. Blaine is the largest city and Anoka is the county seat.",
        ],
        "faq": [
            ("Is Two Stooges in Anoka County?", "Yes. Two Stooges is at 7178 University Ave NE in Fridley, which is in Anoka County."),
            ("Which Anoka County cities are closest to Two Stooges?", "Fridley, Spring Lake Park, Coon Rapids, Columbia Heights and Blaine. Each has its own page with the distance and local details."),
        ],
    },
    "Hennepin": {
        "slug": "hennepin-county-mn", "wiki": W + "Hennepin_County,_Minnesota",
        "desc": "Hennepin County players cross into Fridley for Two Stooges: a sports bar and pool hall with 43 tables, electronic darts, leagues and a full grill. Come play.",
        "lead": "Two Stooges is the sports bar and pool hall just outside Hennepin County, in Fridley, with 43 pool tables, electronic dart boards, leagues, tournaments and a full grill.",
        "facts": [("County seat", "Minneapolis"), ("Largest city", "Minneapolis"), ("Population (2020 census)", "1,281,565"), ("Founded", "March 6, 1852"),
                  ("Area", "606.75 sq mi (554.02 sq mi land)"), ("Neighboring counties", "Anoka, Ramsey, Dakota, Scott, Carver, Wright, Sherburne")],
        "h2": "Next door to Hennepin County",
        "local": [
            "Hennepin County has 1,281,565 residents, and Anoka County is its neighbor to the northeast. Two Stooges is on the Anoka County side, in Fridley, which borders Minneapolis and sits across the Mississippi River from Brooklyn Center and Brooklyn Park.",
            "The county was founded in 1852 and named for the 17th-century explorer Louis Hennepin, who named Saint Anthony Falls. Waterpower from the falls built Minneapolis into a milling city, and by 1970 more of the county's people lived in the suburbs than in the cities. Interstate 694 is one of the county's interstates and is also a main highway in Fridley.",
        ],
        "faq": [
            ("Is Two Stooges in Hennepin County?", "No. Two Stooges is in Fridley, in Anoka County, which borders Hennepin County to the northeast."),
            ("Which Hennepin County cities are closest to Two Stooges?", "Brooklyn Center, Brooklyn Park and Minneapolis. Brooklyn Center and Brooklyn Park are across the Mississippi River from Fridley, and Minneapolis borders it."),
        ],
    },
    "Ramsey": {
        "slug": "ramsey-county-mn", "wiki": W + "Ramsey_County,_Minnesota",
        "desc": "From Ramsey County, Two Stooges is over the line in Fridley: a sports bar and pool hall with 43 tables, electronic darts, leagues and a full grill. Stop in.",
        "lead": "Two Stooges is the sports bar and pool hall just over the Ramsey County line, in Fridley, with 43 pool tables, electronic dart boards, leagues and a full grill.",
        "facts": [("County seat", "Saint Paul"), ("Largest city", "Saint Paul"), ("Population (2020 census)", "552,352"), ("Founded", "October 27, 1849"),
                  ("Area", "170.01 sq mi (152.26 sq mi land)"), ("Neighboring counties", "Anoka, Washington, Dakota, Hennepin")],
        "h2": "Over the line from Ramsey County",
        "local": [
            "Ramsey County is Minnesota's smallest county by area and its most densely populated, with 552,352 residents in 170 square miles. Anoka County is its neighbor to the north, and that is where Two Stooges is, in Fridley. The county line runs along the west side of Mounds View, and New Brighton borders Fridley as well.",
            "The county dates to 1849 and is named for Alexander Ramsey, the first governor of the Minnesota Territory. Anoka County was later formed partly from Ramsey County land, in 1857. Interstates 35W and 694 are among the county's highways, and Interstate 694 is a main highway in Fridley too.",
        ],
        "faq": [
            ("Is Two Stooges in Ramsey County?", "No. Two Stooges is in Fridley, in Anoka County, which is Ramsey County's neighbor to the north."),
            ("Which Ramsey County cities are closest to Two Stooges?", "Mounds View and New Brighton. Both border Fridley on the east."),
        ],
    },
}
