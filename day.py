# "The Day" — home page for Go Fish Costa Rica. Imported by build.py.
import json

CHAPTERS = [  # (id, clock, sky color for the page background while this chapter is in view, over-photo)
    ('dawn', 'Dawn', '#0d2a3a', True),
    ('sand', 'Boats', '#e8eef2', False),
    ('launch', 'Launch', '#0c1334', True),
    ('shelf', 'Offshore', '#0c1334', True),
    ('bite', 'Hookup', '#edf3f5', False),
    ('lunch', 'Lunch', '#f6f3ea', False),
    ('beach', 'Beach', '#0c1334', True),
    ('sunset', 'Sunset', '#f1e2c6', False),
    ('plan', 'Your day', '#ede0c8', False),
]

def home(ctx):
    E, img, FLEET, ADV, boat_len, SOCIAL, EMAIL, PHONE, PHONE_TEL, REVIEWS, page = (ctx[k] for k in ('E', 'img', 'FLEET', 'ADV', 'boat_len', 'SOCIAL', 'EMAIL', 'PHONE', 'PHONE_TEL', 'REVIEWS', 'page'))
    REVIEWS_ALL = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__), 'data', 'reviews.json')))
    r = ''
    rail_boats = [b for b in FLEET if b['slug'] in ('28-whitewater-center-console', '31-chris-craft', '35-cabo', '35-carolina-classic', '38-riviera', '43-riviera-team-edition')]
    rail_boats.sort(key=lambda b: b['half'])
    def boat(b):
        return f'''<a class="boat" href="{r}charters/{b['slug']}.html"><div class="ph">{f'<span class="tb">{b["top_label"]}</span>' if b['top'] else ''}<span class="base">{' · '.join(b['locations'])}</span><img src="{r}img/{img(b['images'][0])}" alt="{E(b['name'])}" loading="lazy"></div>
<div class="b"><h3>{E(b['name'])}</h3><div class="m">Up to {b['max_pax']} guests · {'washroom on board' if b['washroom'] else 'no washroom'}</div>
<div class="p"><div><b>${b['half']:,}</b><small>half day, per boat</small></div><span>Details</span></div></div></a>'''
    chapters_js = json.dumps([dict(id=i, clock=c, sky=s, photo=p) for i, c, s, p in CHAPTERS])
    rail = ''.join(f'<a href="#{i}" data-ch="{i}">{c}<span></span></a>' for i, c, s, p in CHAPTERS[:-1])

    body = f'''<div class="day" id="day" data-chapters='{chapters_js}'>


<!-- chapter -->
<section class="chapter hero on-photo" id="dawn"><div class="media"><img src="{r}img/hero-split.jpg" alt="Sailfish on a baitball beneath a Go Fish boat off Tamarindo" fetchpriority="high" style="object-position:50% 50%"><div class="scrim hero-scrim-l"></div></div>
<div class="wrap"><div class="ch-copy hero-copy"><div class="t">Go Fish Costa Rica · Tamarindo &amp; Flamingo</div>
<h1>Costa Rica's #1 <em>sportfishing operation.</em></h1>
<p class="lead">Seventeen boats out of Tamarindo and Flamingo, captains we know by name, and fifteen straight years of TripAdvisor Travelers' Choice. Scroll through a day with us, then tell us your dates.</p>
<div class="hero-row"><a class="btn btn-ghost" href="{r}book.html">Plan my day</a><a class="btn btn-ghost" href="#sand">Skip to the boats</a></div>
<div class="hero-foot"><div class="cols"><div><b>5 stars</b>TripAdvisor, every year since 2018</div><div><b>1,000+</b>anglers a year</div><div><b>All billfish released</b>marlin and sailfish, every trip</div></div><div>Tamarindo &amp; Flamingo, Costa Rica</div></div>
</div></div></section>

<!-- chapter -->
<section class="chapter" id="sand"><div class="stamp" aria-hidden="true">Boats</div>
<div class="wrap" style="padding-top:clamp(110px,16vh,180px);padding-bottom:clamp(48px,7vh,80px)"><div class="ch-copy"><div class="t">On the sand</div>
<h2>Pick your boat. We already picked the captain.</h2>
<p>Every hull here is one Steve and Liisa have fished from, and every captain is one they'd put their own family with. Rates are per boat and include gear, bait, drinks and lunch on the longer days. Tell us your group and budget, and we'll tell you which one.</p></div>
<div class="fleet-rail" id="fleet-rail">{''.join(boat(b) for b in rail_boats)}</div>
<div style="display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap"><a class="link" href="{r}charters/">All seventeen boats and rates</a><div class="rail-nav"><button type="button" data-rail="-1" aria-label="Previous boats">&#8249;</button><button type="button" data-rail="1" aria-label="More boats">&#8250;</button></div></div>
</div></section>

<!-- chapter -->
<section class="chapter photo on-photo" id="launch"><div class="stamp" aria-hidden="true">Launch</div>
<div class="media"><video autoplay muted loop playsinline poster="{r}img/launch-poster.jpg" data-src="{r}video/launch.mp4"></video><img class="poster" src="{r}img/launch-poster.jpg" alt=""><div class="scrim"></div></div>
<div class="wrap"><div class="ch-copy" style="max-width:56ch;padding:clamp(140px,22vh,220px) 0 clamp(60px,10vh,100px)"><div class="t">Lines off</div>
<h2>Off the beach, or off the dock.</h2>
<p>In Tamarindo the boats launch straight off the sand, a panga runs you out and you're fishing while the town is still waking up. In Flamingo you step off the dock at the marina. Either way the crew has already loaded ice, bait and the lunch.</p>
<p><a class="link" href="{r}charters/?base=Tamarindo">Tamarindo boats</a> &nbsp;&nbsp; <a class="link" href="{r}charters/?base=Flamingo">Flamingo boats</a></p></div></div></section>

<!-- chapter -->
<section class="chapter photo on-photo" id="shelf"><div class="stamp" aria-hidden="true">Offshore</div>
<div class="media"><video autoplay muted loop playsinline poster="{r}img/offshore-aerial.jpg" data-src="{r}video/offshore.mp4"></video><img class="poster" src="{r}img/offshore-aerial.jpg" alt=""><div class="scrim r"></div></div>
<div class="wrap" style="display:flex;justify-content:flex-end"><div class="ch-copy" style="max-width:52ch;padding:clamp(140px,22vh,220px) 0 clamp(60px,10vh,100px)"><div class="t">The shelf</div>
<h2>Forty minutes out, a thousand feet down.</h2>
<p>About forty minutes at cruise and the bottom falls away to a thousand feet. That edge is where the sailfish, marlin, tuna and mahi live, and it is why this stretch of the North Pacific holds so many IGFA records. Half days stay inshore; 3/4 and full days make the run.</p>
<p><a class="link" href="{r}discover/guanacaste-fishing.html">Why Tamarindo fishes differently</a></p></div></div></section>

<!-- chapter -->
<section class="chapter two flip" id="bite"><div class="stamp" aria-hidden="true">Hookup</div>
<div class="wrap"><div class="trio"><a href="{r}img/{img('sailfish.jpg')}" data-lb="bite"><img src="{r}img/{img('sailfish.jpg')}" alt="Sailfish boatside, about to be released" loading="lazy" style="object-position:70% 50%"></a><a href="{r}img/{img('marlin.jpg')}" data-lb="bite"><img src="{r}img/{img('marlin.jpg')}" alt="Marlin jumping" loading="lazy"></a><a href="{r}img/{img('roosterfish.jpg')}" data-lb="bite"><img src="{r}img/{img('roosterfish.jpg')}" alt="Roosterfish" loading="lazy"></a></div>
<div class="ch-copy"><div class="t">Sailfish up</div>
<h2>Roosters inshore. Sails and marlin off the edge.</h2>
<p>Half days stay along the rocks for roosterfish, snapper and jacks. Go 3/4 or full and you're offshore for sailfish, marlin, tuna and mahi. Sailfish peak May to August, blue marlin November to April, and there is no month here with nothing biting.</p>
<p><a class="link" href="{r}discover/fish-seasons.html">The month by month calendar</a></p></div></div></section>

<!-- chapter -->
<section class="chapter two" id="lunch"><div class="stamp" aria-hidden="true">Lunch</div>
<div class="wrap"><div class="ph rv"><img src="{r}img/{img('lunch-cooler.jpg')}" alt="Cooler open on deck: cold beer, fruit and a sandwich" loading="lazy"><div class="cap">Every charter: fruit, soda, water, beer. Light lunch on 3/4 and full days.</div></div>
<div class="ch-copy"><div class="t">Lunch on the bridge</div>
<h2>Cold beer, a sandwich, and the story you'll tell for years.</h2>
<p>Table fish come home with you; half the restaurants in town will cook your catch that night. Billfish go back in the water, every one. Tips aren't expected, but a crew that worked hard for you will remember 15 to 20 percent.</p>
<p><a class="link" href="{r}dining/">Where we eat in Tamarindo</a></p></div></div></section>

<!-- chapter -->
<section class="chapter photo on-photo" id="beach"><div class="stamp" aria-hidden="true">Beach</div>
<div class="media"><canvas id="scrub" data-frames="{r}video/day/pg_" data-count="120" width="1440" height="810"></canvas><img class="poster" src="{r}video/playa-grande-poster.jpg" alt="Tamarindo bay from the air at golden hour"><div class="scrim b"></div></div>
<div class="wrap" style="display:flex;align-items:flex-end;min-height:100svh;padding-bottom:clamp(48px,8vh,88px)"><div class="ch-copy" style="max-width:54ch"><div class="t">Back on the sand</div>
<h2>Golden hour over Tamarindo bay, and dinner already booked.</h2>
<p>The boat drops you where it picked you up. Shower, sunset, a table Liisa reserved at Pangas or El Chiringuito. Tomorrow could be the zipline, the estuary with the kids, or the boat again.</p></div></div></section>

<!-- chapter -->
<section class="chapter two flip" id="sunset"><div class="stamp" aria-hidden="true">Sunset</div>
<div class="wrap"><div class="ph land rv"><img src="{r}img/{img('42-sunset.jpg')}" alt="Sunset from the 42-foot catamaran off Tamarindo" loading="lazy"><div class="cap">Sunset catamaran: sail, snorkel, paddleboard, open bar. $125 per adult, kids $74.</div></div>
<div class="ch-copy"><div class="t">Sunset sail</div>
<h2>The half of the family that didn't fish gets their day too.</h2>
<p>Sixteen adventures we've done ourselves: the sunset catamaran, ATVs through the back roads, the estuary crocodiles, Rio Celeste, a spa afternoon. Most pick up from your hotel in Tamarindo or Flamingo. We book them all in one email.</p>
<p><a class="link" href="{r}adventures/">All sixteen adventures</a></p></div></div></section>

<!-- your day -->
<section class="chapter" id="plan" style="min-height:auto;padding:clamp(80px,12vh,140px) 0"><div class="wrap plan">
<div class="ch-copy"><div class="t">Your day</div><h2>Tell us your dates. Steve and Liisa answer within hours.</h2>
<p>No payment online and no obligation to ask. You get a straight recommendation, one boat or a whole week, and a price before you commit to anything.</p>
<p class="small muted">Prefer to talk? Toll-free <a href="tel:{PHONE_TEL}">{PHONE}</a>, or <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div>
<form id="qb"><div class="fld"><label for="qb-base">Where are you staying?</label><select id="qb-base" name="base"><option value="">Tamarindo or Flamingo, not sure yet</option><option>Tamarindo</option><option>Flamingo</option></select></div>
<div class="row"><div class="fld"><label for="qb-date">Date</label><input id="qb-date" type="date" name="date"></div><div class="fld"><label for="qb-pax">Guests</label><select id="qb-pax" name="pax">{''.join(f'<option value="{i}"{" selected" if i==4 else ""}>{i}</option>' for i in range(1,13))}<option value="13">13 or more</option></select></div></div>
<button class="btn btn-primary btn-block" type="submit">Show me boats that fit</button>
<a class="link" style="justify-self:center;font-size:14px" href="{r}book.html">Or use the four-step planner</a></form>
</div></section>
</div>

<section class="tight"><div class="wrap split">
<div class="ph wide rv"><img src="{r}img/{img('04.jpg')}" alt="Steve and Liisa Quinn" loading="lazy" style="object-position:50% 30%"><div class="cap">Steve &amp; Liisa Quinn, Go Fish Costa Rica. Tamarindo since 2010.</div></div>
<div class="ch-copy"><div class="t">Who answers the email</div><h2>We're not a call center. We're the two people you'll wave to on the beach.</h2>
<p>We came down from Canada in 2004, stayed for good in 2010, and ended up doing the thing we love most: putting people on fish. Even if you don't book through us, call. We would rather you have a good trip than a bad one with someone else.</p>
<p><a class="link" href="{r}discover/about-us.html">Our story</a> &nbsp;&nbsp; <a class="link" href="{r}discover/our-pledge-to-you.html">Our pledge</a></p></div></div></section>

<section class="awards dark"><div class="wrap">
<div class="aw-head"><img src="{r}img/logo.svg" alt="Go Fish Costa Rica" class="aw-logo"><div><div class="t">Reviews &amp; awards</div><h2>Fifteen years of Travelers' Choice. <em>That is not luck.</em></h2>
<p>TripAdvisor gives its Travelers' Choice award to the top ten percent of attractions in the world, judged on what everyday travelers write afterwards. Go Fish Costa Rica has earned it every year since 2012, 2026 included.</p></div></div>
<div class="aw-grid">
<div class="aw"><b>2012 to 2026</b><span>TripAdvisor Travelers' Choice, fifteen years running</span></div>
<div class="aw"><b>Top 10%</b><span>of attractions worldwide, by traveler reviews</span></div>
<div class="aw"><b>10 years</b><span>Ducks Unlimited Approved Outfitter, partnership award 2025</span></div>
<div class="aw"><b>$1.7M</b><span>raised for conservation through Go Fish trips at DU events</span></div>
<div class="aw"><b>5.0</b><span>on TripAdvisor from 590 reviews, and 5.0 on Google</span></div>
<div class="aw"><b>1,000+</b><span>anglers a year, most of them referred or returning</span></div>
</div>
<div class="aw-row"><div class="aw-photo"><img src="{r}img/{img('steve-liisa-ducks-unlimited.jpg')}" alt="Steve and Liisa Quinn receiving the Ducks Unlimited ten-year Approved Outfitter award" loading="lazy"><div class="cap">Ducks Unlimited Approved Outfitter, ten-year partnership award, 2025</div></div>
<div class="aw-list">
<div class="aw-item"><span class="aw-y">2012 to 2026</span><div><b>TripAdvisor Travelers' Choice</b><span>Fifteen consecutive years. Known as the Certificate of Excellence before 2020. Awarded to the top 10% of attractions worldwide.</span><div class="aw-years">{''.join(f'<i>{y}</i>' for y in range(2012, 2027))}</div></div></div>
<div class="aw-item"><span class="aw-y">2015 to 2025</span><div><b>Ducks Unlimited Approved Outfitter</b><span>Ten-year partnership award. Go Fish trips donated to DU events have raised $1.7 million for wetland conservation.</span></div></div>
<div class="aw-item"><span class="aw-y">2026</span><div><b>5.0 on TripAdvisor, 590 reviews</b><span>581 rated Excellent. Ranked #21 of 255 boat tours and water sports in Tamarindo.</span></div></div>
<div class="aw-item"><span class="aw-y">Google</span><div><b>5.0 rating</b><span>Five stars on every Google review to date.</span></div></div>
<div class="aw-item"><span class="aw-y">Since 2010</span><div><b>1,000+ anglers a year</b><span>Fished out of Tamarindo and Flamingo, most referred by past guests or coming back.</span></div></div>
</div></div>
</div></section>

<section class="tight"><div class="wrap"><div class="ig"><div><div class="t">Follow the action</div><h2 style="font-size:clamp(28px,3vw,40px)">@gofishcostarica</h2></div><a class="btn btn-ghost" href="{SOCIAL['ig']}" target="_blank" rel="noopener">Follow on Instagram</a></div>
<div id="ig-feed" style="margin-top:26px"></div>
<div id="ig-fallback" class="strip" style="margin-top:26px">{''.join(f'<a href="{r}img/{img(g)}" data-lb="ig"><img src="{r}img/{img(g)}" alt="" loading="lazy"></a>' for g in ['9a000add-c9c3-4b54-8f98-1a677dcc7a50.jpg','img_0928.jpg','24fc1498-da0a-47ce-8efb-bf1912a823da.jpg','c3ab02f9-e7ba-41a2-9329-e6dad4d32470.jpg','liisa_crew.jpg'])}</div></div></section>

<section class="reviews-wall"><div class="wrap">
<div class="rw-head"><div><div class="t">What people say</div><h2>590 reviews. <em>581 of them say Excellent.</em></h2></div>
<div class="rw-stats"><div><b>5.0</b><span>TripAdvisor rating</span></div><div><b>#21</b><span>of 255 boat tours in Tamarindo</span></div><div><b>2026</b><span>Travelers' Choice</span></div></div></div>
<div class="rw-grid">{''.join(f'<figure class="rw"><div class="stars">★★★★★</div><blockquote>{E(x["q"])}</blockquote><figcaption><b>{E(x["n"])}</b><span>{E(", ".join(v for v in (x["w"], x["s"] + (" · " + x["d"] if x["d"] else "")) if v))}</span></figcaption></figure>' for x in REVIEWS_ALL)}</div>
<p class="small muted" style="margin-top:28px">Excerpts from public reviews. <a href="{SOCIAL['ta']}" target="_blank" rel="noopener">Read all 590 on TripAdvisor</a> · <a href="{SOCIAL['ig']}" target="_blank" rel="noopener">@gofishcostarica</a></p>
</div></section>'''
    return page(r, 'Go Fish Costa Rica — Fishing Charters & Adventures in Tamarindo & Flamingo', "Tamarindo's number one sport fishing operation. Seventeen vetted boats in Tamarindo and Flamingo, sixteen adventures, booked by Steve and Liisa, who live here. See what a day on the water looks like, hour by hour.", body, extra_head=ctx['fleet_js']())
