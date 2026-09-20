#!/usr/bin/env python3
"""Go Fish Costa Rica — static site generator.
Run:  python3 build.py   (from the gofishcr/ folder). Outputs HTML next to this file.
Edit content in data/*.json; edit copy for discover pages below.
"""
import json, os, re, html, datetime
ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
D = lambda n: json.load(open(os.path.join(ROOT, 'data', n)))
FLEET, ADV, DINING, BLOG = D('fleet.json'), D('adventures.json'), D('dining.json'), D('blog.json')
IMG = set(os.listdir(os.path.join(ROOT, 'img')))
MISSING = set()
def img(name):
    if name not in IMG: MISSING.add(name)
    return name
E = html.escape

SITE = 'Go Fish Costa Rica'
EMAIL, PHONE, PHONE_TEL = 'gofishcr@gmail.com', '1-888-434-7491', '+18884347491'
PHONE_CR, PHONE_CR_TEL = '+506 8393 7555', '+50683937555'  # Costa Rica mobile
WHATSAPP = '50683937555'  # same number on WhatsApp; blank hides every WhatsApp button
EMAIL_CC = ''  # optional second inbox copied on every booking request (blank = none)
MAIL_ENDPOINT = 'https://gofish-mail.vercel.app/api/request'  # gofish-mail service (Vercel) that emails the guest + Go Fish; blank = email-app fallback only
SOCIAL = dict(fb='https://www.facebook.com/GoFishCr', ig='https://www.instagram.com/gofishcostarica', yt='https://www.youtube.com/@GoFishCostaRica',
              ta='https://www.tripadvisor.com/Attraction_Review-g309253-d1474067-Reviews-Go_Fish_Costa_Rica-Tamarindo_Province_of_Guanacaste.html')

# ---------------------------------------------------------------- helpers
def boat_len(b): return int(re.match(r"(\d+)", b['name']).group(1))
def adv_from(a):
    """lowest headline price: the rate matrix when there is one, otherwise the copy"""
    if a.get('rates'):
        lo = min(p for v in a['rates']['vehicles'] for p in v['prices'].values())
        return '$%s' % f'{lo:,}'
    txt = ' '.join(a['paras'])
    m = re.search(r'Adults\s*\$(\d[\d,]*)', txt)
    if m: return '$' + m.group(1)
    txt = re.sub(r'(?i)(add|extra person|extra)\s*\$\d[\d,]*', '', txt)
    m = [x for x in re.findall(r'\$(\d[\d,]*)', txt) if int(x.replace(',', '')) >= 40]
    return ('$' + min(m, key=lambda x: int(x.replace(',', '')))) if m else ''
ADV_TAG = {
 'zipline-tour':'10 cables · 3.5 hrs · from Tamarindo or Flamingo','atv-tour':'Private · 2–4 hrs · beaches, mountains, back roads','sunset-catamaran':'Sail, snorkel, paddleboard · open bar · afternoon into sunset',
 'mega-combo-adventure-tour':'Zipline, tubing, horses, hot springs · all day','volcano-hike-mud-baths':'Rincón de la Vieja · hot springs · full day','white-water-rafting':'Class III–V · bilingual guides · full day',
 'waterfall-hike':'La Leona Waterfalls · swim · lunch','birdwatching-tour':'Toucans, hawks, wetlands · all levels','estuary-tour':'Mangroves · crocs, monkeys, birds · 2 hrs','riverboat-pottery-farm':'Palo Verde boat ride · lunch · Guaitil pottery',
 'horseback-riding':'Beach, forest and mountain trails · all levels','monteverde-cloud-forest':'Hanging bridges or zipline · full day','rio-celeste-hike':'Turquoise river · Tenorio Volcano · full day',
 'snorkeling':'Reefs, turtles, tropical fish · guided','surf-lessons':'2 hrs · beginners, families, kids','turtle-tour':'Night nesting tour · seasonal','ultimate-spa-day':'3 treatments · saltwater pool · lunch with wine'}
ADV_SHORT = {'mega-combo-adventure-tour':'Mega Combo Tour','volcano-hike-mud-baths':'Volcano Hike & Mud Baths','rio-celeste-hike':'Rio Celeste Hike','estuary-tour':'Estuary Boat Tour','ultimate-spa-day':'Spa Day','monteverde-cloud-forest':'Monteverde Cloud Forest','riverboat-pottery-farm':'Riverboat & Pottery Farm'}
def adv_short(a): return ADV_SHORT.get(a['slug'], a['name'])

def fleet_js():
    d = {b['slug']: dict(slug=b['slug'], name=b['name'], locations=b['locations'], top=b['top'], top_label=b.get('top_label',''), washroom=b['washroom'], max_pax=b['max_pax'], half=b['half'], three_quarter=b['three_quarter'], full=b['full'], quote=b['quote'], length=boat_len(b), images=b['images'][:1]) for b in FLEET}
    a = {x['slug']: dict(name=adv_short(x), image=x['images'][0], tag=ADV_TAG[x['slug']], from_=adv_from(x)) for x in ADV}
    for v in a.values(): v['from'] = v.pop('from_')
    return '<script>window.FLEET=%s;window.ADV=%s;</script>' % (json.dumps(d), json.dumps(a))


# ---------------------------------------------------------------- booking form fields (Tyler 09-20)
FISH_INSHORE = ['Roosterfish', 'Snapper', 'Jacks', 'African pompano', 'Needlefish']
FISH_OFFSHORE = ['Marlin', 'Sailfish', 'Tuna', 'Mahi mahi', 'Wahoo']
FISH_ANY = ["Whatever's biting"]
FISH_TARGETS = [(f, 'in') for f in FISH_INSHORE] + [(f, 'off') for f in FISH_OFFSHORE] + [(f, 'both') for f in FISH_ANY]
PIN_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>'

def pax_fields(pre, max_pax=None, adults=2):
    cap = max_pax or 20
    a = ''.join(f'<option value="{i}"{" selected" if i == min(adults, cap) else ""}>{i}</option>' for i in range(1, cap + 1))
    k = ''.join(f'<option value="{i}"{" selected" if i == 0 else ""}>{i}</option>' for i in range(0, cap + 1))
    return (f'<div class="fld"><label for="{pre}-adults">Adults</label><select id="{pre}-adults" name="adults">{a}</select></div>'
            f'<div class="fld"><label for="{pre}-kids">Kids</label><select id="{pre}-kids" name="kids">{k}</select></div>')

def style_field(pre):
    rows = []
    for v, t in [('', 'Not sure yet'), ('Inshore', 'Inshore'), ('Offshore', 'Offshore')]:
        on = ' class="on"' if v == '' else ''
        ck = ' checked' if v == '' else ''
        rows.append(f'<label{on}><input type="radio" name="style" value="{v}"{ck}>{t}</label>')
    return (f'<div class="fld"><label for="{pre}-style-g">Inshore or offshore?</label>'
            f'<div class="chip-group" id="{pre}-style-g" data-style>{"".join(rows)}</div>'
            f'<span class="hint">Inshore is roosterfish, snapper and jacks close to the beach. Offshore runs out to the shelf for billfish, tuna and mahi.</span></div>')

def fish_field(pre):
    opts = ''.join(f'<label data-zone="{z}"><input type="checkbox" name="fish" value="{E(f)}">{E(f)}</label>' for f, z in FISH_TARGETS)
    return (f'<div class="fld"><label for="{pre}-fish-g">What do you want to catch?</label>'
            f'<div class="chip-group" id="{pre}-fish-g" data-fish>{opts}</div></div>')

def stay_field(pre):
    return (f'<div class="fld" data-stay><label for="{pre}-stay">Where are you staying?</label>'
            f'<div class="stay-row"><input id="{pre}-stay" name="stay" autocomplete="off" placeholder="Hotel, villa or Airbnb name">'
            f'<button type="button" class="pin-btn" data-pin>{PIN_SVG}Pin it</button></div>'
            f'<span class="hint">Lots of places share a name. Drop a pin so the crew finds you first time.</span>'
            f'<div class="pin-wrap" hidden></div>'
            f'<input type="hidden" name="stay_geo"><input type="hidden" name="stay_map"></div>')


def rates_picker(a):
    """Duration + vehicle chooser for tours that have a rate matrix (ATV)."""
    R = a.get('rates')
    if not R: return '', ''
    durs = ''.join(f'<label{" class=\"on\"" if i == 0 else ""}><input type="radio" name="dur" value="{d["key"]}"{" checked" if i == 0 else ""}>{d["label"]}</label>'
                   for i, d in enumerate(R['durations']))
    vehs = ''.join(f'<option value="{v["key"]}">{E(v["label"])}</option>' for v in R['vehicles'])
    picker = (f'<div class="fld"><label for="ab-dur">{E(R["label"])}</label>'
              f'<div class="chip-group" id="ab-dur" data-dur>{durs}</div></div>'
              f'<div class="fld"><label for="ab-veh">Which machine?</label><select id="ab-veh" name="vehicle">{vehs}</select></div>')
    head = ''.join(f'<th>{E(d["label"])}</th>' for d in R['durations'])
    rows = ''.join('<tr><td>%s <span class="small muted">%s</span></td>%s</tr>' % (
        E(v['label']), E(v['unit']), ''.join(f'<td><b>${v["prices"][d["key"]]:,}</b></td>' for d in R['durations']))
        for v in R['vehicles'])
    table = (f'<h2 style="font-size:26px;margin-top:34px">Rates</h2>'
             f'<table class="rates-t"><tr><th>Machine</th>{head}</tr>{rows}</table>'
             f'<p class="small muted">{E(R["note"])}</p>')
    return picker, table

# ---------------------------------------------------------------- layout
SOCIAL_ICONS = {
  'ig': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.6" y="2.6" width="18.8" height="18.8" rx="5.4" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.4" cy="6.6" r="1.25" fill="currentColor"/></svg>',
  'fb': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9.2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M13.2 18.6v-5.7h1.9l.35-2.3h-2.25V9.15c0-.66.22-1.1 1.16-1.1h1.2V6c-.2-.03-.9-.09-1.7-.09-1.72 0-2.9 1.03-2.9 2.94v1.75H9v2.3h2.05v5.7z" fill="currentColor"/></svg>',
  'yt': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.2" y="5.6" width="19.6" height="12.8" rx="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M10.3 9.5l5.1 2.5-5.1 2.5z" fill="currentColor"/></svg>',
  'ta': '<svg viewBox="0 0 24 24" aria-hidden="true"><ellipse cx="12" cy="12" rx="10.1" ry="6.5" fill="none" stroke="currentColor" stroke-width="1.7"/><circle cx="7.7" cy="12" r="2.85" fill="none" stroke="currentColor" stroke-width="1.7"/><circle cx="16.3" cy="12" r="2.85" fill="none" stroke="currentColor" stroke-width="1.7"/><circle cx="7.7" cy="12" r="1.15" fill="currentColor"/><circle cx="16.3" cy="12" r="1.15" fill="currentColor"/></svg>',
}
SOCIAL_NAMES = {'ig': 'Instagram', 'fb': 'Facebook', 'yt': 'YouTube', 'ta': 'TripAdvisor'}
def social_links(cls):
    return f'<div class="{cls}">' + ''.join(
        f'<a href="{SOCIAL[k]}" target="_blank" rel="noopener" aria-label="{SOCIAL_NAMES[k]}" title="{SOCIAL_NAMES[k]}">{SOCIAL_ICONS[k]}</a>'
        for k in ('ig', 'fb', 'yt', 'ta')) + '</div>'

def nav(root, light=False):
    dd = ''.join('<li><a href="%sdiscover/%s.html">%s</a></li>' % (root, s, t) for s, t in [('about-us','About Steve & Liisa'),('our-pledge-to-you','Our Pledge'),('crews-equipment','Crews & Equipment'),('fish-seasons','Fish & Seasons'),('guanacaste-fishing','Why Fish Tamarindo'),('weather','Weather'),('contact-us','Contact')])
    return f'''<nav class="top over-photo{' light' if light else ''}"><div class="wrap">
<a class="logo" href="{root}index.html" aria-label="Go Fish Costa Rica home"><img class="lm" src="{root}img/logo.svg" alt="Go Fish Costa Rica"></a>
<ul class="nav-links">
<li><a href="{root}charters/">Fishing Charters</a></li><li><a href="{root}adventures/">Adventures</a></li><li><a href="{root}dining/">Dining</a></li>
<li><a href="{root}discover/">Discover</a><ul class="dd">{dd}<li><a href="{root}blog/">Blog</a></li></ul></li><li><a href="{root}gallery.html">Gallery</a></li></ul>
<a class="nav-trip" href="{root}trip.html" aria-label="My trip"><b>My trip</b><span hidden>0</span></a><a class="nav-cta" href="{root}book.html">Plan my trip</a>
<button class="burger" aria-label="Menu"><span></span><span></span><span></span></button></div></nav>
<div class="drawer"><button class="close" aria-label="Close">&times;</button>
<a href="{root}charters/">Fishing Charters</a><a href="{root}adventures/">Adventures</a><a href="{root}dining/">Dining</a><a href="{root}gallery.html">Gallery</a><a href="{root}blog/">Blog</a><a href="{root}discover/">Discover</a>
<a class="sub" href="{root}discover/about-us.html">About Steve &amp; Liisa</a><a class="sub" href="{root}discover/fish-seasons.html">Fish &amp; Seasons</a><a class="sub" href="{root}discover/crews-equipment.html">Crews &amp; Equipment</a><a class="sub" href="{root}discover/weather.html">Weather</a><a class="sub" href="{root}discover/contact-us.html">Contact</a>
<a class="btn btn-sand" style="margin-top:22px;font-family:Inter;font-size:16px" href="{root}book.html">Plan my trip</a>
<a class="sub drawer-trip" href="{root}trip.html">My trip<span hidden>0</span></a>
{social_links('drawer-social')}</div>'''

def footer(root):
    return f'''<footer><div class="wrap"><div class="cols">
<div><a class="logo" href="{root}index.html"><img src="{root}img/logo.svg" alt="Go Fish Costa Rica"></a>
<p class="brandline">Tamarindo's trusted fishing charter and adventure booking agency since 2010. Steve &amp; Liisa Quinn, Tamarindo &amp; Flamingo.</p>
{social_links('socials')}</div>
<div><h4>Book</h4><ul><li><a href="{root}charters/">Fishing charters</a></li><li><a href="{root}adventures/">Adventures</a></li><li><a href="{root}charters/?base=Tamarindo">Tamarindo boats</a></li><li><a href="{root}charters/?base=Flamingo">Flamingo boats</a></li><li><a href="{root}book.html">Trip planner</a></li></ul></div>
<div><h4>Discover</h4><ul><li><a href="{root}discover/about-us.html">About us</a></li><li><a href="{root}discover/fish-seasons.html">Fish &amp; seasons</a></li><li><a href="{root}discover/crews-equipment.html">Crews &amp; equipment</a></li><li><a href="{root}discover/guanacaste-fishing.html">Why fish Tamarindo</a></li><li><a href="{root}dining/">Where to eat</a></li><li><a href="{root}discover/weather.html">Weather</a></li><li><a href="{root}blog/">Blog</a></li></ul></div>
<div><h4>Contact</h4><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="tel:{PHONE_TEL}">{PHONE} (toll-free)</a></li><li><a href="tel:{PHONE_CR_TEL}">{PHONE_CR}</a> (Costa Rica)</li><li data-wa><a href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" style="width:1em;height:1em;vertical-align:-.12em;margin-right:.45em"><path fill="currentColor" d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2m0 1.67c2.2 0 4.27.86 5.83 2.42a8.2 8.2 0 0 1 2.41 5.82c0 4.54-3.7 8.24-8.25 8.24a8.2 8.2 0 0 1-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.2 8.2 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.26-8.24M8.53 7.33c-.16 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.71 2.74 4.22 3.74 2.08.82 2.5.66 2.96.62.45-.04 1.47-.6 1.68-1.18.2-.58.2-1.07.15-1.18-.07-.1-.23-.16-.48-.28-.25-.13-1.47-.73-1.7-.81-.22-.08-.39-.13-.56.12-.16.25-.63.81-.78.97-.14.17-.29.19-.54.06-.24-.12-1.04-.38-1.98-1.22-.73-.65-1.22-1.46-1.37-1.71-.14-.24-.01-.38.11-.5.11-.12.25-.29.37-.44s.16-.25.24-.42c.08-.17.04-.31-.02-.44-.06-.12-.55-1.34-.76-1.83-.2-.48-.4-.42-.55-.42z"/></svg>Call or text us on WhatsApp</a></li><li>Mon–Sat 8:00am–6:00pm</li><li>Playa Tamarindo &amp; Playa Flamingo<br>Costa Rica 50309</li></ul></div>
</div><div class="bottom"><span>&copy; {datetime.date.today().year} Go Fish Costa Rica. All billfish released. Prices in USD, subject to change.</span><span>Site by <a href="https://coastalcr.com" target="_blank" rel="noopener">Coastal CR</a></span></div></div></footer>'''

def page(root, title, desc, body, light=False, extra_head='', bookbar=''):
    return f'''<!DOCTYPE html>
<html lang="en" data-root="{root}" data-build="{BUILD}" data-email="{EMAIL}" data-cc="{EMAIL_CC}" data-endpoint="{MAIL_ENDPOINT}" data-wa="{WHATSAPP}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(html.unescape(title))}</title>
<meta name="description" content="{E(html.unescape(desc))}">
<link rel="icon" type="image/svg+xml" href="{root}img/logo.svg">
<meta property="og:title" content="{E(html.unescape(title))}"><meta property="og:description" content="{E(html.unescape(desc))}"><meta property="og:image" content="https://gofishcr.com/img/hero-split.jpg"><meta property="og:type" content="website"><meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anybody:wdth,wght@100..150,400..900&family=Hanken+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/style.css?v={BUILD}">{extra_head}
</head>
<body>
{nav(root, light)}
{body}
{footer(root)}{bookbar}
<script src="{root}assets/site.js?v={BUILD}"></script>
</body></html>'''

SITE_URL = 'https://gofishcr.com/'
ORG_LD = json.dumps({
  "@context": "https://schema.org", "@type": "TravelAgency", "@id": SITE_URL + "#org",
  "name": SITE, "url": SITE_URL, "logo": SITE_URL + "img/logo.svg", "image": SITE_URL + "img/hero-split.jpg",
  "description": "Sport fishing charters, private catamarans and adventure tours in Tamarindo and Flamingo, Costa Rica. Booked by Steve & Liisa Quinn since 2010.",
  "email": EMAIL, "telephone": PHONE_TEL, "priceRange": "$700 - $2,100",
  "contactPoint": [{"@type": "ContactPoint", "telephone": PHONE_TEL, "contactType": "reservations", "areaServed": "US", "availableLanguage": ["English", "Spanish"]},
                   {"@type": "ContactPoint", "telephone": PHONE_CR_TEL, "contactType": "customer service", "areaServed": "CR", "availableLanguage": ["English", "Spanish"]}],
  "address": {"@type": "PostalAddress", "addressLocality": "Tamarindo", "addressRegion": "Guanacaste", "postalCode": "50309", "addressCountry": "CR"},
  "areaServed": ["Tamarindo", "Playa Flamingo", "Playa Grande", "Playa Conchal", "Guanacaste"],
  "openingHoursSpecification": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"], "opens": "08:00", "closes": "18:00"},
  "sameAs": list(SOCIAL.values()),
  "aggregateRating": {"@type": "AggregateRating", "ratingValue": "5.0", "reviewCount": "590", "bestRating": "5"},
  "founder": [{"@type": "Person", "name": "Steve Quinn"}, {"@type": "Person", "name": "Liisa Quinn"}],
}, ensure_ascii=False)

def canonical_of(path):
    u = path.replace('index.html', '')
    return SITE_URL + u

def write(path, content):
    p = os.path.join(ROOT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    if path.endswith('.html') and '</head>' in content:
        c = canonical_of(path)
        content = content.replace('</head>', f'<link rel="canonical" href="{c}"><meta property="og:url" content="{c}">\n<script type="application/ld+json">{ORG_LD}</script>\n</head>', 1)
    open(p, 'w').write(content)

def page_hero(root, title, lead, bg, crumbs=None, pos=None):
    c = ''
    if crumbs: c = '<div class="crumbs">' + ' <span>/</span> '.join('<a href="%s">%s</a>' % (h, t) if h else '<span>%s</span>' % t for t, h in crumbs) + '</div>'
    st = f' style="object-position:{pos}"' if pos else ''
    return f'<header class="page-hero"><img class="bg" src="{root}img/{img(bg)}" alt=""{st}><div class="wrap">{c}<h1>{title}</h1>{"<p>"+lead+"</p>" if lead else ""}</div></header>'

def boat_card(b, root):
    base = ' · '.join(b['locations'])
    rates = f'<div class="rates"><span>½ day<b>{"$%s" % f"{b["half"]:,}" if b["half"] else "Quote"}</b></span><span>¾ day<b>{"$%s" % f"{b["three_quarter"]:,}" if b["three_quarter"] else "Quote"}</b></span><span>Full<b>{"$%s" % f"{b["full"]:,}" if b["full"] else "Quote"}</b></span></div>'
    pax = f'up to {b["max_pax"]} guests' if b['max_pax'] else 'group sails'
    return f'''<a class="card fleet-card" data-boat="{b['slug']}" href="{root}charters/{b['slug']}.html">{f'<span class="tag">{b["top_label"]}</span>' if b['top'] else ''}<span class="tag base">{base}</span>
<div class="ph"><img src="{root}img/{img(b['images'][0])}" alt="{E(b['name'])}" loading="lazy"></div>
<div class="body"><h3>{E(b['name'])}</h3><div class="meta"><span>{pax}</span><span>{'Washroom onboard' if b['washroom'] else 'No washroom'}</span></div>{rates}
<div class="price">{'<b>$%s</b><small> half day · per boat</small>' % f"{b['half']:,}" if b['half'] else '<b>Quote</b><small> private sail</small>'}<span class="go">View boat →</span></div></div></a>'''

def adv_card(b, root, imgonly=False):
    fr = adv_from(b)
    if imgonly:
        return f'''<a class="card img-card" href="{root}adventures/{b['slug']}.html"><div class="ph"><img src="{root}img/{img(b['images'][0])}" alt="{E(adv_short(b))}" loading="lazy"></div>
<div class="body"><h3>{E(adv_short(b))}</h3><div class="meta"><span>{ADV_TAG[b['slug']]}</span></div></div></a>'''
    return f'''<a class="card" href="{root}adventures/{b['slug']}.html"><div class="ph"><img src="{root}img/{img(b['images'][0])}" alt="{E(adv_short(b))}" loading="lazy"></div>
<div class="body"><h3>{E(adv_short(b))}</h3><div class="meta"><span>{ADV_TAG[b['slug']]}</span></div>
<div class="price">{'<b>%s</b><small> per person</small>' % fr if fr else '<b>Ask</b><small> for rates</small>'}<span class="go">Details →</span></div></div></a>'''

REVIEWS = [
 ("I had an amazing experience booking through Go Fish Costa Rica. The team was helpful and communication was clear. The whole process was easy and everything went exactly as planned from start to finish. I highly recommend their excellent service.","Linda Russell","Google review"),
 ("Tyler helped us plan an extraordinary trip to Tamarindo to celebrate our son's college graduation. Every last detail was executed to perfection. We were picked up at the airport, stopped for groceries, and then taken to a beautiful condo. Two days of sailing on a 31 ft flybridge boat with three great captains was the icing on the cake.","Laura Mayer","Google review"),
 ("Just took my family for a SECOND time to Costa Rica for the Go Fish Costa Rica experience. We had such an amazing time! We got to do more stuff this time than the last, including an ATV trip and zip lining. Tyler and Justin made sure we all had a blast.","Tim Primo","Google review")]
def reviews_block(dark=True):
    cards = ''.join(f'<div class="rev rv"><div class="stars">★★★★★</div><p>“{E(t)}”</p><div class="who"><span class="av">{n[0]}</span><span><b>{n}</b><br>{s}</span></div></div>' for t, n, s in REVIEWS)
    return f'<div class="reviews">{cards}</div>'

INCLUDED = ['Fishing gear, bait and tackle','Fruit, soda, juice, water and beer','Light lunch on 3/4 and full day charters','Captain and crew who speak English','Full insurance and Costa Rican permits']
NOT_INCL = ['Fishing licenses','Crew tips (15–20% is customary)']

# ---------------------------------------------------------------- HOME
def home():
    r = ''
    top = sorted([b for b in FLEET if b['top'] and not b['quote']], key=lambda b: -boat_len(b))
    featured = [b for b in top if b['slug'] in ('43-riviera-team-edition','38-riviera','35-cabo','31-chris-craft','28-whitewater-center-console','21-custom-center-console')]
    featured.sort(key=lambda b: -boat_len(b))
    adv_home = [a for a in ADV if a['slug'] in ('sunset-catamaran','atv-tour','zipline-tour','estuary-tour','rio-celeste-hike','surf-lessons','volcano-hike-mud-baths','horseback-riding')]
    gallery = ['45a2ab32-230b-4e6c-9b1c-4e3f0f723691.jpg','img_1784.jpg','c9ff17da-90f2-4181-ac65-593e65008895.jpg','liisa.jpg','img_1769.jpg','a4889ef6-9481-4836-b203-2d3d01ffd918.jpg','15.jpg','img_1762.jpg','img_2016.jpg','04.jpg']
    body = f'''
<header class="hero"><div class="hero-bg">
<video autoplay muted loop playsinline poster="{r}video/hero-poster.jpg"><source src="{r}video/hero.mp4" type="video/mp4"></video>
<div class="tint"></div><div class="vign"></div><div class="grain"></div></div>
<div class="wrap"><div class="eyebrow">Tamarindo &amp; Flamingo · Guanacaste, Costa Rica</div>
<h1>The right boat.<br>The right crew.<br><em>The right day.</em></h1>
<p class="lead">Costa Rica's number one sport fishing operation. Seventeen vetted boats, captains we know by name, and every adventure on the Gold Coast, planned by two people who actually live here.</p>
<div class="hero-actions"><a class="btn btn-sand" href="{r}book.html">Plan my trip</a><a class="btn btn-ghost" href="{r}charters/">See the fleet</a></div>
<div class="hero-stats"><div><b>5★</b><span>TripAdvisor, 2018–2025</span></div><div><b>1,000+</b><span>anglers a year</span></div><div><b>17</b><span>boats, 21' to 65'</span></div><div><b>IGFA</b><span>record waters</span></div></div>
</div><div class="scroll-hint">Scroll</div></header>

<div class="wrap qb"><form id="qb">
<div class="f"><label for="qb-base">Where</label><select id="qb-base" name="base"><option value="">Tamarindo or Flamingo</option><option>Tamarindo</option><option>Flamingo</option></select></div>
<div class="f"><label for="qb-date">When</label><input id="qb-date" type="date" name="date"></div>
<div class="f"><label for="qb-pax">How many</label><select id="qb-pax" name="pax">{''.join(f'<option value="{i}"{" selected" if i==4 else ""}>{i} guest{"s" if i>1 else ""}</option>' for i in range(1,13))}<option value="13">13+ guests</option></select></div>
<div class="go"><button class="btn btn-primary" type="submit">Find my boat</button></div></form></div>

<section class="tight"><div class="wrap"><div class="trust">
<div class="t rv"><i>★</i><div><b>Travelers' Choice</b><span>TripAdvisor Certificate of Excellence, five stars every year since 2018</span></div></div>
<div class="t rv"><i>✓</i><div><b>Every boat vetted</b><span>We personally know each captain, crew and hull we send you out on</span></div></div>
<div class="t rv"><i>◎</i><div><b>Deep water, minutes out</b><span>1,000 ft of water close to shore means more lines in, less running</span></div></div>
<div class="t rv"><i>↺</i><div><b>Billfish released</b><span>Catch and release on all marlin and sailfish, creel limits on table fish</span></div></div>
</div></div></section>

<section><div class="wrap"><div class="sec-head row rv"><div><div class="kicker">The fleet</div><h2>Seventeen boats. <em>One honest recommendation.</em></h2></div><a class="btn btn-ghost" href="{r}charters/">All boats &amp; rates</a></div>
<div class="grid g3">{''.join(boat_card(b, r) for b in featured)}</div></div></section>

<section class="dark"><div class="wrap"><div class="sec-head rv"><div class="kicker">How it works</div><h2>Booking a charter should feel like <em>calling a friend who lives here.</em></h2></div>
<div class="steps">
<div class="s rv"><h3>Tell us your dates and your crew</h3><p>Use the planner or send an email. Where you are staying, how many are fishing, what you want to catch, how hard you want to fish.</p></div>
<div class="s rv"><h3>We match you to the boat</h3><p>Not the most expensive one. The right one for your group, your budget and the season. We confirm availability within hours.</p></div>
<div class="s rv"><h3>Show up at the beach at first light</h3><p>Gear, bait, drinks and lunch are on board. We stay on call the whole trip.</p></div>
</div></div></section>

<section><div class="wrap"><div class="sec-head row rv"><div><div class="kicker">Beyond the boat</div><h2>Adventures for the <em>non-fishing days.</em></h2></div><a class="btn btn-ghost" href="{r}adventures/">All 16 adventures</a></div>
<div class="grid g4">{''.join(adv_card(a, r, True) for a in adv_home)}</div></div></section>

<section class="dark"><div class="wrap split">
<div class="ph rv"><img src="{r}img/{img('steveandliisa.jpg')}" alt="Steve and Liisa Quinn"><div class="cap">Steve &amp; Liisa Quinn · Tamarindo since 2010</div></div>
<div class="rv"><div class="kicker">Who you are dealing with</div><h2>We're Steve and Liisa. <em>We answer the phone.</em></h2>
<p>We came to Costa Rica in 2004, left Canada for good in 2010, ran a restaurant and a B&amp;B, and ended up doing the thing we love most: putting people on fish. We are not a call center. We are two anglers who know every captain in Tamarindo and Flamingo and will tell you straight which boat is worth your money.</p>
<p>Even if you don't book through us, call. We would rather you have a great trip than a bad one with someone else.</p>
<div class="hero-actions"><a class="btn btn-sand" href="{r}discover/about-us.html">Our story</a><a class="btn btn-ghost" href="{r}discover/our-pledge-to-you.html">Our pledge to you</a></div></div>
</div></section>

<section><div class="wrap"><div class="sec-head rv"><div class="kicker">Google reviews</div><h2>Don't just take <em>our word for it.</em></h2></div>{reviews_block()}
<div class="years rv" style="margin-top:34px">{''.join(f'<span style="border-color:var(--line)">{y} ★</span>' for y in range(2018,2026))}</div>
<p class="muted small" style="margin-top:14px">Five stars on TripAdvisor every year since 2018. <a href="{SOCIAL['ta']}" target="_blank" rel="noopener">Read the reviews →</a></p></div></section>

<section class="tight"><div class="wrap"><div class="ig rv"><div><div class="kicker">Follow the action</div><h2 style="font-size:30px">@gofishcostarica</h2></div><a class="btn btn-ghost" href="{SOCIAL['ig']}" target="_blank" rel="noopener">Follow on Instagram</a></div>
<div class="strip" style="margin-top:26px">{''.join(f'<a href="{r}img/{img(g)}" data-lb="home"><img src="{r}img/{img(g)}" alt="" loading="lazy"></a>' for g in gallery)}</div>
<p style="margin-top:16px" class="small"><a href="{r}gallery.html">Full photo gallery →</a></p></div></section>

<section class="cta"><img class="bg" src="{r}img/{img('marlin.jpg')}" alt=""><div class="wrap"><div class="kicker">Ready when you are</div><h2>Let's plan the fishing trip of a lifetime.</h2><p>Tell us your dates and we'll put together a charter built around what you want to catch.</p><div class="row"><a class="btn btn-sand" href="{r}book.html">Start planning</a><a class="btn btn-ghost" href="mailto:{EMAIL}">Email Steve &amp; Liisa</a></div></div></section>
'''
    write('index.html', page(r, 'Go Fish Costa Rica — Fishing Charters & Adventures in Tamarindo & Flamingo', "Costa Rica's #1 sport fishing operation. 17 vetted boats in Tamarindo and Flamingo, plus ATV, zipline, catamaran and volcano adventures. Booked by Steve & Liisa, who live here.", body, extra_head=fleet_js()))

# ---------------------------------------------------------------- CHARTERS
def charters():
    r = '../'
    cards = ''.join(boat_card(b, r) for b in sorted(FLEET, key=lambda b: (b['quote'], b['half'] or 0)))
    body = page_hero(r, 'Fishing charters in Tamarindo &amp; Flamingo', 'From 21-foot center consoles to 43-foot sport fishers and private catamarans. Rates are per boat, all gear and drinks included. Pick a location, tell us your group, and we will tell you which boat is right.', 'offshore-aerial.jpg', [('Home', r+'index.html'), ('Charters', None)]) + f'''
<section style="padding-top:0;position:relative;z-index:2"><div class="wrap">
<form id="fleet-filters" class="filters">
<div class="f"><label>Location</label><select name="base"><option value="">Both</option><option>Tamarindo</option><option>Flamingo</option></select></div>
<div class="f"><label>Guests</label><select name="pax"><option value="">Any</option>{''.join(f'<option value="{i}">{i}</option>' for i in range(1,10))}</select></div>
<div class="f"><label>Budget</label><select name="budget"><option value="">Any</option><option value="800">Under $800</option><option value="1100">Under $1,100</option><option value="1500">Under $1,500</option><option value="2200">Under $2,200</option></select></div>
<div class="f"><label>Washroom</label><select name="wash"><option value="">Either</option><option value="yes">Yes please</option></select></div>
<div class="f"><label>Sort</label><select name="sort"><option value="">Recommended</option><option value="price">Price: low to high</option><option value="price-desc">Price: high to low</option><option value="size">Size: small to big</option><option value="size-desc">Size: big to small</option></select></div>
<button type="button" class="reset">Reset</button></form>
<div class="count"><span id="fleet-count"></span> <span id="fleet-date"></span></div>
<div class="grid g3">{cards}</div>
<div id="fleet-empty" class="empty" style="display:none;margin-top:20px">No single boat fits every filter. Loosen one, or <a href="mailto:{EMAIL}">email us</a>. With ten or more anglers two boats running together is usually the better day.</div>
<div class="incl" style="margin-top:50px"><div><h4>Included on every charter</h4><ul>{''.join(f'<li>{x}</li>' for x in INCLUDED)}</ul></div><div class="no"><h4>Not included</h4><ul>{''.join(f'<li>{x}</li>' for x in NOT_INCL)}</ul><p class="small muted" style="margin-top:12px">Boats stay inshore on half days. To target billfish, book a 3/4 or full day offshore.</p></div></div>
</div></section>'''
    write('charters/index.html', page(r, 'Fishing Charters — Tamarindo & Flamingo | Go Fish Costa Rica', 'Compare 17 fishing boats in Tamarindo and Flamingo with real rates: half, 3/4 and full day. Center consoles, Bertrams, Rivieras, Cabos and private catamarans.', body, extra_head=fleet_js()))
    for b in FLEET: boat_page(b)

def gallery_html(root, images, group, alt):
    imgs = images[:5]
    n = len(imgs); cls = 'one' if n == 1 else 'two' if n == 2 else ''
    out = ''
    for i, im in enumerate(imgs if n <= 3 else imgs[:3]):
        more = f'<span class="more">+{len(images)-3} photos</span>' if (i == 2 and len(images) > 3) else ''
        out += f'<a href="{root}img/{img(im)}" data-lb="{group}"><img src="{root}img/{img(im)}" alt="{E(alt)}"{" loading=lazy" if i else ""}>{more}</a>'
    hidden = ''.join(f'<a href="{root}img/{img(im)}" data-lb="{group}" hidden></a>' for im in images[3:])
    return f'<div class="gal {cls}">{out}</div>{hidden}'

def boat_page(b):
    r = '../'
    base = ' / '.join(b['locations'])
    rates = '' if b['quote'] else f'''<h2 style="font-size:26px;margin-top:34px">Rates for this boat</h2>
<table class="rates-t"><tr><th>Charter</th><th>Hours</th><th>Rate per boat</th></tr>
<tr><td>Half day</td><td>5 hours · inshore</td><td><b>${b['half']:,}</b></td></tr>
<tr><td>3/4 day</td><td>7 hours · inshore or offshore</td><td><b>${b['three_quarter']:,}</b></td></tr>
<tr><td>Full day</td><td>9 hours · inshore or offshore</td><td><b>${b['full']:,}</b></td></tr></table>
<p class="small muted">Rates are per boat, excluding taxes, priced for up to {b['priced_for']} guests, maximum {b['max_pax']} on board. Prices subject to change. To target billfish, book the 7 or 9 hour trip.</p>'''
    seg = '' if b['quote'] else f'''<div class="seg"><label class="on"><input type="radio" name="dur" value="half" checked>5 hrs<small>${b['half']:,}</small></label><label><input type="radio" name="dur" value="tq">7 hrs<small>${b['three_quarter']:,}</small></label><label><input type="radio" name="dur" value="full">9 hrs<small>${b['full']:,}</small></label></div>'''
    pax_opts = ''.join(f'<option value="{i}"{" selected" if i==min(4,b["max_pax"] or 4) else ""}>{i}</option>' for i in range(1, (b['max_pax'] or 20) + 1))
    intro = {
      True: f"Private sailing catamaran out of {base}. Morning or sunset departures, snorkeling and paddleboarding gear, open bar and lunch on the sunset sail. Priced by request depending on group size and season.",
      False: f"{(b['top_label'] + '. ') if b['top'] else ''}Out of {base}, priced for {b['priced_for']} anglers with room for {b['max_pax']}. {'Washroom on board. ' if b['washroom'] else 'No washroom on board, so she is built for a fast inshore run rather than a long day offshore. '}Captain and crew speak English, and every trip runs with catch and release on billfish."
    }[b['quote']]
    body = f'''<header class="page-hero" style="padding-bottom:40px"><img class="bg" src="{r}img/{img(b['images'][0])}" alt=""><div class="wrap"><div class="crumbs"><a href="{r}index.html">Home</a><span>/</span><a href="{r}charters/">Charters</a><span>/</span><span>{E(b['name'])}</span></div>
<div class="chips" style="margin-bottom:16px">{''.join(f'<span class="chip" style="background:rgba(255,255,255,.14);color:#fff">{l}</span>' for l in b['locations'])}{f'<span class="chip" style="background:var(--sand);color:var(--navy)">{b["top_label"]}</span>' if b['top'] else ''}</div>
<h1>{E(b['name'])}</h1><p>{intro}</p></div></header>
<section><div class="wrap detail">
<div class="main">{gallery_html(r, b['images'], 'boat', b['name'])}
<div class="specs"><div><span>Length</span><b>{boat_len(b)} ft</b></div><div><span>Guests</span><b>{('up to %d' % b['max_pax']) if b['max_pax'] else 'Group'}</b></div><div><span>Location</span><b style="font-size:18px">{base}</b></div></div>
<h2 style="font-size:26px">What this boat offers</h2><div class="chips" style="margin:14px 0 8px">{''.join(f'<span class="chip">{E(f)}</span>' for f in b['features'])}<span class="chip">{'Washroom onboard' if b['washroom'] else 'No washroom'}</span></div>
{rates}
<div class="incl"><div><h4>Included</h4><ul>{''.join(f'<li>{x}</li>' for x in INCLUDED)}</ul></div><div class="no"><h4>Not included</h4><ul>{''.join(f'<li>{x}</li>' for x in NOT_INCL)}</ul></div></div>
<div class="prose"><h3>Charter lengths</h3><ul><li><b>Half day</b> · 5 hours. Boats stay inshore: roosterfish, snapper, jacks.</li><li><b>3/4 day</b> · 7 hours. Stay inshore, or run out to the shelf for sailfish, marlin, tuna and mahi.</li><li><b>Full day</b> · 9 hours. The serious billfish day, or a long inshore day if that is your thing.</li></ul>
<p>Tips are not expected but very much appreciated. If the crew works hard for you, 15 to 20% is customary.</p></div>
</div>
<aside><form class="book" id="boat-book">
<div class="from" id="boat-from"><b>{('$%s' % f"{b['half']:,}") if b['half'] else 'Quote'}</b><span>{'5 hours · per boat' if b['half'] else 'private sail'}</span></div>
<div class="sub">Tell us your dates and we will come straight back with availability and a quote.</div>
{seg}
<div class="row3"><div class="fld"><label for="bk-date">Date</label><input id="bk-date" type="date" name="date" required></div>{pax_fields('bk', b['max_pax'])}</div>
{style_field('bk') if not b['quote'] else ''}
{fish_field('bk') if not b['quote'] else ''}
<div class="fld"><label for="bk-name">Full name</label><input id="bk-name" name="name" required autocomplete="name" placeholder="First and last name"></div>
<div class="row2"><div class="fld"><label for="bk-email">Email</label><input id="bk-email" type="email" name="email" required autocomplete="email"></div><div class="fld"><label for="bk-phone">Phone / WhatsApp</label><input id="bk-phone" name="phone" autocomplete="tel"></div></div>
{stay_field('bk')}
<div class="fld"><label for="bk-notes" data-notes-label>Anything else we should know?</label><textarea id="bk-notes" name="notes"></textarea></div>
<div class="fld"><label for="bk-tr">Need transportation?</label><select id="bk-tr" name="transport"><option value="">No, we have it covered</option><option>Yes, hotel to the boat and back</option><option>Yes, airport pickup too</option><option>Not sure yet, tell me the options</option></select></div>
{'<div class="est" id="est"><span><small>Estimated total</small></span><span style="text-align:right"><b></b><small></small></span></div>' if not b['quote'] else ''}
<button class="btn btn-primary btn-block" type="submit">Request this boat</button>
<button class="btn btn-ghost btn-block" type="button" data-add-trip style="margin-top:8px">Add to my trip</button>
<a class="btn btn-ghost btn-block" data-wa href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener" style="margin-top:8px"><svg viewBox="0 0 24 24" aria-hidden="true" style="width:1em;height:1em;vertical-align:-.12em;margin-right:.45em"><path fill="currentColor" d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2m0 1.67c2.2 0 4.27.86 5.83 2.42a8.2 8.2 0 0 1 2.41 5.82c0 4.54-3.7 8.24-8.25 8.24a8.2 8.2 0 0 1-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.2 8.2 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.26-8.24M8.53 7.33c-.16 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.71 2.74 4.22 3.74 2.08.82 2.5.66 2.96.62.45-.04 1.47-.6 1.68-1.18.2-.58.2-1.07.15-1.18-.07-.1-.23-.16-.48-.28-.25-.13-1.47-.73-1.7-.81-.22-.08-.39-.13-.56.12-.16.25-.63.81-.78.97-.14.17-.29.19-.54.06-.24-.12-1.04-.38-1.98-1.22-.73-.65-1.22-1.46-1.37-1.71-.14-.24-.01-.38.11-.5.11-.12.25-.29.37-.44s.16-.25.24-.42c.08-.17.04-.31-.02-.44-.06-.12-.55-1.34-.76-1.83-.2-.48-.4-.42-.55-.42z"/></svg>Text us on WhatsApp</a>
<div class="note">Rates are per boat and exclude taxes. All gear, bait, drinks{' and lunch on longer trips' if not b['quote'] else ''} included. Fishing licence and crew tips extra.</div>
</form></aside>
</div></section>
<section class="tight" style="padding-top:0"><div class="wrap"><div class="sec-head row"><div><div class="kicker">More boats in {base.split(' / ')[0]}</div><h2 style="font-size:30px">Compare with these</h2></div><a class="btn btn-ghost btn-sm" href="{r}charters/">All boats</a></div>
<div class="grid g3">{''.join(boat_card(x, r) for x in sorted([x for x in FLEET if x['slug']!=b['slug'] and set(x['locations'])&set(b['locations']) and x['quote']==b['quote']], key=lambda x: abs((x['half'] or 0)-(b['half'] or 0)))[:3])}</div></div></section>'''
    boatjs = '<script>window.BOAT=%s;</script>' % json.dumps(dict(slug=b['slug'], image=img(b['images'][0]), name=b['name'], locations=b['locations'], half=b['half'], three_quarter=b['three_quarter'], full=b['full'], max_pax=b['max_pax'], quote=b['quote']))
    bar = f'<div class="bookbar"><div><b>{("$%s" % f"{b["half"]:,}") if b["half"] else "Quote"}</b><small>{"half day · per boat" if b["half"] else "private sail"}</small></div><a class="btn btn-primary btn-sm" href="#boat-book">Request this boat</a></div>'
    ld = {"@context": "https://schema.org", "@graph": [
      {"@type": "Product", "name": f"{b['name']} fishing charter", "image": [SITE_URL + 'img/' + i for i in b['images'][:3]],
       "description": re.sub('<[^>]+>', '', intro), "brand": {"@id": SITE_URL + "#org"},
       "offers": [] if b['quote'] else [
         {"@type": "Offer", "name": n, "price": str(pr), "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": SITE_URL + f"charters/{b['slug']}.html", "seller": {"@id": SITE_URL + "#org"}}
         for n, pr in (("Half day", b['half']), ("3/4 day", b['three_quarter']), ("Full day", b['full']))]},
      {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL},
        {"@type": "ListItem", "position": 2, "name": "Charters", "item": SITE_URL + "charters/"},
        {"@type": "ListItem", "position": 3, "name": b['name'], "item": SITE_URL + f"charters/{b['slug']}.html"}]}]}
    boatjs += '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>'
    write(f"charters/{b['slug']}.html", page(r, f"{b['name']} — {base} fishing charter | Go Fish Costa Rica", f"{b['name']} fishing charter in {base}, Guanacaste. {'Half day $%s, 3/4 day $%s, full day $%s per boat.' % (f'{b['half']:,}', f'{b['three_quarter']:,}', f'{b['full']:,}') if not b['quote'] else 'Private catamaran, morning or sunset, quote on request.'} Gear, bait and drinks included.", body, extra_head=boatjs, bookbar=bar))

# ---------------------------------------------------------------- ADVENTURES
def parse_adv(a):
    """split paragraphs into intro prose + fact pairs (Cost/Duration/Included/What to Bring...)"""
    facts, prose, sections = [], [], []
    for p in a['paras']:
        m = re.match(r'^(Cost|Duration|Included|What to Bring|Age Requirement|Weight Limit|Rates?)\s*(?:\(([^)]*)\))?:\s*(.+)$', p)
        if m:
            facts.append((m.group(1) + (f' ({m.group(2)})' if m.group(2) else ''), m.group(3))); continue
        if p == '---': sections.append(('---', '')); continue
        prose.append(p)
    return prose, facts

def adventures():
    r = '../'
    body = page_hero(r, 'Adventures in Guanacaste', 'Fishing holds a special place in our hearts, but the Gold Coast has more to give. Sixteen tours we have personally done, with guides and operators we trust. Pickup in Tamarindo or Flamingo on most.', 'atv-ridge.jpg', [('Home', r+'index.html'), ('Adventures', None)]) + f'''
<section><div class="wrap"><div class="grid g3">{''.join(adv_card(a, r) for a in ADV)}</div>
<div class="cta" style="margin-top:60px;border-radius:var(--radius);padding:64px 28px"><img class="bg" src="{r}img/{img('sunset-catamarn.jpg')}" alt=""><div class="kicker">Mix and match</div><h2>Fish one day, fly through the canopy the next.</h2><p>Tell us how many days you have and we build the whole week: charters, tours, dinner reservations, the lot.</p><div class="row"><a class="btn btn-sand" href="{r}book.html?type=adventure">Plan my trip</a></div></div></div></section>'''
    write('adventures/index.html', page(r, 'Adventures — Zipline, ATV, Catamaran, Volcano & more | Go Fish Costa Rica', 'Sixteen adventures around Tamarindo and Flamingo: sunset catamaran, ATV, zipline, Rio Celeste, Monteverde, rafting, surf lessons, turtle tours and spa days. Real prices, trusted operators.', body))
    for a in ADV: adv_page(a)

def adv_page(a):
    r = '../'
    prose, facts = parse_adv(a)
    # split multi-option pages on '---'
    chunks, cur = [], []
    for p in prose:
        if p == '---': chunks.append(cur); cur = []
        else: cur.append(p)
    chunks.append(cur)
    def render_chunk(ch):
        out = ''
        for p in ch:
            if re.match(r'^[^.:]{4,80}(?: – | - )[^.]{2,60}$', p) and len(p) < 90 and not p.endswith('.'):
                out += f'<h3>{E(p)}</h3>'
            elif re.match(r'^\d+ Hours? – ', p) or re.match(r'^(Private|Semi-Private|Group|Tamarindo|Flamingo|Add \$|Transportation|Pickup|Side-by-Side|ATV Rates)', p):
                out += f'<li>{E(p)}</li>'
            else:
                out += f'<p>{E(p)}</p>'
        out = re.sub(r'(<li>.*?</li>)+', lambda m: '<ul>' + m.group(0) + '</ul>', out, flags=re.S)
        return out
    content = ''.join(render_chunk(c) for c in chunks)
    factbox = f'<div class="facts">{"".join(f"<div><span>{E(k)}</span>{E(v)}</div>" for k, v in facts)}</div>' if facts else ''
    fr = adv_from(a)
    rate_picker, rate_table = rates_picker(a)
    others = [x for x in ADV if x['slug'] != a['slug']][:3]
    body = f'''{page_hero(r, E(a['name']), ADV_TAG[a['slug']], a['images'][0], [('Home', r+'index.html'), ('Adventures', r+'adventures/'), (adv_short(a), None)])}
<section><div class="wrap detail"><div class="main">{gallery_html(r, a['images'], 'adv', a['name'])}
<div class="prose" style="margin-top:28px">{content}</div>{factbox}
<div class="prose">{rate_table}</div>
<div class="prose"><p class="small muted">Pickup from Tamarindo or Flamingo on most tours. Hotels in Pinilla, JW Marriott or Westin may carry a small transport supplement, noted above where it applies.</p></div></div>
<aside><form class="book" id="adv-book" data-name="{E(a['name'])}" data-slug="{a['slug']}" data-image="{img(a['images'][0])}">
<div class="from" id="adv-from"><b>{fr or 'Ask'}</b><span>{('from · per machine' if a.get('rates') else 'per person') if fr else 'for rates'}</span></div>
<div class="sub">Request this tour. We confirm the date, pickup time and final price within hours.</div>
{rate_picker}
<div class="row3"><div class="fld"><label for="ab-date">Date</label><input id="ab-date" type="date" name="date" required></div>{pax_fields('ab')}</div>
<div class="fld"><label for="ab-base">Pickup area</label><select id="ab-base" name="base"><option>Tamarindo</option><option>Flamingo</option><option>Other (tell us below)</option></select></div>
<div class="fld"><label for="ab-name">Full name</label><input id="ab-name" name="name" required autocomplete="name" placeholder="First and last name"></div>
<div class="row2"><div class="fld"><label for="ab-email">Email</label><input id="ab-email" type="email" name="email" required></div><div class="fld"><label for="ab-phone">Phone / WhatsApp</label><input id="ab-phone" name="phone"></div></div>
{stay_field('ab')}
<div class="fld"><label for="ab-notes" data-notes-label>Anything else we should know?</label><textarea id="ab-notes" name="notes"></textarea></div>
<div class="fld"><label for="ab-tr">Need transportation?</label><select id="ab-tr" name="transport"><option value="">No, we have it covered</option><option>Yes, hotel to the boat and back</option><option>Yes, airport pickup too</option><option>Not sure yet, tell me the options</option></select></div>
<button class="btn btn-primary btn-block" type="submit">Request this tour</button>
<button class="btn btn-ghost btn-block" type="button" data-add-trip style="margin-top:8px">Add to my trip</button>
<a class="btn btn-ghost btn-block" data-wa href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener" style="margin-top:8px"><svg viewBox="0 0 24 24" aria-hidden="true" style="width:1em;height:1em;vertical-align:-.12em;margin-right:.45em"><path fill="currentColor" d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2m0 1.67c2.2 0 4.27.86 5.83 2.42a8.2 8.2 0 0 1 2.41 5.82c0 4.54-3.7 8.24-8.25 8.24a8.2 8.2 0 0 1-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.2 8.2 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.26-8.24M8.53 7.33c-.16 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.71 2.74 4.22 3.74 2.08.82 2.5.66 2.96.62.45-.04 1.47-.6 1.68-1.18.2-.58.2-1.07.15-1.18-.07-.1-.23-.16-.48-.28-.25-.13-1.47-.73-1.7-.81-.22-.08-.39-.13-.56.12-.16.25-.63.81-.78.97-.14.17-.29.19-.54.06-.24-.12-1.04-.38-1.98-1.22-.73-.65-1.22-1.46-1.37-1.71-.14-.24-.01-.38.11-.5.11-.12.25-.29.37-.44s.16-.25.24-.42c.08-.17.04-.31-.02-.44-.06-.12-.55-1.34-.76-1.83-.2-.48-.4-.42-.55-.42z"/></svg>Text us on WhatsApp</a>
<div class="note">Steve &amp; Liisa confirm availability within hours and send you the plan for your trip.</div></form></aside></div></section>
<section class="tight" style="padding-top:0"><div class="wrap"><div class="sec-head row"><div><div class="kicker">More adventures</div><h2 style="font-size:30px">You might also like</h2></div><a class="btn btn-ghost btn-sm" href="{r}adventures/">All adventures</a></div><div class="grid g3">{''.join(adv_card(x, r) for x in others)}</div></div></section>'''
    bar = f'<div class="bookbar"><div><b>{fr or "Ask"}</b><small>{"per person" if fr else "for rates"}</small></div><a class="btn btn-primary btn-sm" href="#adv-book">Request this tour</a></div>'
    head = '<script>window.ADV_RATES=%s;</script>' % json.dumps(a.get('rates') or None)
    write(f"adventures/{a['slug']}.html", page(r, f"{a['name']} | Go Fish Costa Rica", (prose[0] if prose else a['name'])[:155], body, extra_head=head, bookbar=bar))

# ---------------------------------------------------------------- DINING
def dining():
    r = '../'
    cards = ''.join(f'''<a class="card" href="{r}dining/{d['slug']}.html"><div class="ph"><img src="{r}img/{img(d['images'][0])}" alt="{E(d['name'])}" loading="lazy"></div><div class="body"><h3>{E(d['name'])}</h3><div class="meta"><span>Tamarindo</span></div><p class="small muted">{E(d['paras'][0][:130])}…</p><div class="price"><span></span><span class="go">Details →</span></div></div></a>''' for d in DINING)
    body = page_hero(r, 'Where we eat in Tamarindo', "Ten spots, all tried firsthand, from sunset ceviche on the sand to Argentinian steak and a food truck park. Steve's happy hour pick is in here too.", 'pangas-06.jpg', [('Home', r+'index.html'), ('Dining', None)]) + f'<section><div class="wrap"><div class="grid g3">{cards}</div></div></section>'
    write('dining/index.html', page(r, 'Where to Eat in Tamarindo — Our Picks | Go Fish Costa Rica', 'Ten Tamarindo restaurants we actually eat at: Pangas Beach Club, El Chiringuito, Patagonia, Green Papaya, Dragonfly, Fish & Cheeses, Ocho, Café Tico, Waffle Monkey and the food truck park.', body))
    for d in DINING:
        others = [x for x in DINING if x['slug'] != d['slug']][:3]
        info = ''
        if d['address']: info += f'<div><h4>Find it</h4><a href="{d["maps"]}" target="_blank" rel="noopener">{E(d["address"])}</a></div>'
        if d['tel']: info += f'<div><h4>Call</h4><a href="tel:{re.sub(r"[^0-9+]","",d["tel"])}">{E(d["tel"])}</a></div>'
        if d['email']: info += f'<div><h4>Email</h4><a href="mailto:{d["email"]}">{E(d["email"])}</a></div>'
        body = page_hero(r, E(d['name']), 'Tamarindo, Guanacaste', d['images'][0], [('Home', r+'index.html'), ('Dining', r+'dining/'), (d['name'], None)]) + f'''
<section><div class="wrap detail"><div class="main">{gallery_html(r, d['images'], 'din', d['name'])}<div class="prose" style="margin-top:28px">{''.join(f'<p>{E(p)}</p>' for p in d['paras'])}</div></div>
<aside><div class="book contact"><div class="info" style="grid-column:1/-1">{info}<div><h4>Reserve</h4><p class="small muted">Book direct with the restaurant. Ask us if you want it folded into your trip plan.</p></div></div></div></aside></div></section>
<section class="tight" style="padding-top:0"><div class="wrap"><div class="sec-head row"><div><div class="kicker">More places</div><h2 style="font-size:30px">Also worth a table</h2></div><a class="btn btn-ghost btn-sm" href="{r}dining/">All restaurants</a></div><div class="grid g3">{''.join(f'<a class="card" href="{r}dining/{x["slug"]}.html"><div class="ph"><img src="{r}img/{img(x["images"][0])}" alt="" loading="lazy"></div><div class="body"><h3>{E(x["name"])}</h3></div></a>' for x in others)}</div></div></section>'''
        write(f"dining/{d['slug']}.html", page(r, f"{d['name']} — Tamarindo | Go Fish Costa Rica", d['paras'][0][:155], body))

# ---------------------------------------------------------------- DISCOVER
def discover():
    r = '../'
    items = [('about-us','About Steve & Liisa','Two Canadians who left in 2010 and never went back.','steveandliisa.jpg'),('our-pledge-to-you','Our pledge to you','Objective, personal, and on call from first email to last cast.','sloth.jpg'),('crews-equipment','Crews & equipment','What every boat we send you on has to have.','fb_img_1555113966938.jpg'),('fish-seasons','Fish & seasons','What bites when on the Gold Coast, month by month.','roosterfish.jpg'),('guanacaste-fishing','Guanacaste fishing','IGFA record waters and why the North Pacific is different.','guanacaste-papagayo-gulf.jpg'),('weather','Weather','Live forecast for Tamarindo and Flamingo.','tamarindo-beach.jpg'),('contact-us','Contact us','Hours, locations and the fastest way to reach us.','costaricajaco.jpg')]
    cards = ''.join(f'<a class="card" href="{r}discover/{s}.html"><div class="ph"><img src="{r}img/{img(im)}" alt="" loading="lazy"></div><div class="body"><h3>{t}</h3><p class="small muted">{d}</p></div></a>' for s, t, d, im in items)
    body = page_hero(r, 'Discover Go Fish', 'The people, the pledge, the fish and the water. Everything you would want to know before you book with the only trusted fishing charter and adventure agency on the Guanacaste coast.', 'guanacaste-papagayo-gulf.jpg', [('Home', r+'index.html'), ('Discover', None)]) + f'<section><div class="wrap"><div class="grid g3">{cards}</div></div></section>'
    write('discover/index.html', page(r, 'Discover Go Fish Costa Rica', 'About Steve & Liisa Quinn, our pledge, crews and equipment standards, fish seasons, Guanacaste fishing guide, weather and contact.', body))

    def simple(slug, title, lead, bg, content, extra='', pos=None):
        body = page_hero(r, title, lead, bg, [('Home', r+'index.html'), ('Discover', r+'discover/'), (title, None)], pos=pos) + f'<section><div class="wrap-n prose">{content}</div>{extra}</section>'
        write(f'discover/{slug}.html', page(r, f'{re.sub("<[^>]+>","",title)} | Go Fish Costa Rica', re.sub('<[^>]+>','',lead)[:155], body))

    simple('about-us', 'About Steve &amp; Liisa', 'Your travel gurus in Tamarindo since 2010.', 'steveandliisa.jpg', f'''
<img src="{r}img/{img('steve-liisa-ducks-unlimited.jpg')}" alt="Steve and Liisa Quinn with their Ducks Unlimited ten-year partnership award">
<p class="lede">Our journey started in 2004. After countless trips down, we made the audacious decision in 2010 to say goodbye to our Canadian life and dive headfirst into Costa Rica.</p>
<p>Over the years we have dabbled in a few ventures: a vibrant restaurant (not exactly smooth sailing) and one of Costa Rica's premier bed and breakfasts. Then we found our true calling, running one of the most sought-after sport fishing charter services in the region. We are anglers first. That is why we do this.</p>
<h2>One call, whole trip</h2>
<p>We are your one-stop shop for adventure and relaxation on the Gold Coast. We handle the boats, the tours, dinner reservations, car rental recommendations and the little things that make a week here effortless. Prefer to soak it in from your villa? Want a town tour? Want to know which beach the locals surf? Ask.</p>
<p>Every client we have served has become a friend, and we intend to keep it that way. Whether you are after adrenaline or a hammock, our job is to make sure your trip is nothing short of extraordinary.</p>
<h2>Community</h2>
<p>Ten years as a Ducks Unlimited partner and counting. We live here, our kids grew up here, and we put money and time back into the town that made this possible.</p>
<p><a class="btn btn-primary" href="{r}book.html">Plan a trip with us</a></p>''', pos='50% 18%')

    simple('our-pledge-to-you', 'Our pledge to you', 'To elevate your angling experience, by any means necessary.', 'sloth.jpg', f'''
<p class="lede">We pledge to not just meet but exceed your expectations. As anglers ourselves, we know what matters: top-notch service, a safe boat, a crew that knows the water, and gear that matches what you came to catch.</p>
<p>Our pride comes from the reviews and the repeat clients we have earned over the years. Your trip to Costa Rica is not just about fishing. It is an adventure, and we are honored to be part of it. We are your go-to for any question about fishing here or the country itself.</p>
<h2>Costa Rica: a true angler's paradise</h2>
<p>For over three decades this country has captivated anglers from around the globe. Two international airports, accommodation at every level, world-class dining and a national culture that prioritizes tourism and conservation.</p>
<p>Catch-and-release rules on billfish, limits on long-line fishing and protected marine parks have made Costa Rica the top sport fishing destination in the world. Paradise is not a dream here. It is a Tuesday.</p>
<h2>Why we remain the best</h2>
<ul><li><b>We are objective.</b> Not all boats and crews are created equal. We find the right fit for your group, not the biggest commission.</li>
<li><b>We know every captain personally.</b> We will not compromise our reputation for profit or ego.</li>
<li><b>We take your trust seriously.</b> From the first call to the final cast, you get an unmatched level of service.</li>
<li><b>We do this at scale.</b> Year after year we serve more than 1,000 anglers in Tamarindo and the North Pacific.</li></ul>''')

    simple('crews-equipment', 'Crews &amp; equipment', 'Fish the finest fleet in Costa Rica.', 'fb_img_1555113966938.jpg', f'''
<p class="lede">Would you perform surgery on yourself? Probably not. So why gamble on which boat and crew to trust with your family, your friends and your week off?</p>
<p>We have seen plenty of flashy websites for boats we would not trust to float, let alone take offshore. After years running the premier fishing outfit in Tamarindo we know every hull, captain and mate we send you out with, and we vouch for each one.</p>
<h2>Every boat and crew we represent has</h2>
<ul><li>A boat fully equipped for the trip you booked</li><li>A captain and crew fluent in English</li><li>Years of experience on these specific waters</li><li>Comprehensive insurance for your peace of mind</li><li>Premium tackle, rods and reels on board</li><li>Complimentary drinks and snacks, plus a light lunch on 3/4 and full days</li><li>Full compliance with Costa Rican regulations</li><li>Catch and release on all billfish</li><li>Responsible creel limits on table fish</li><li>Flexibility for different group sizes and special requests</li></ul>
<h2>Knowledge is power</h2>
<p>Attempting to navigate this alone will not save you time or money. Before you book anywhere, reach out. Even if you decide not to book through Go Fish, we want your Costa Rican fishing trip to be a good one.</p>
<p>Call us seven days a week at <a href="tel:{PHONE_TEL}">{PHONE}</a>. In Costa Rica, call or text <a href="tel:{PHONE_CR_TEL}">{PHONE_CR}</a> — it is on WhatsApp, so a message reaches us wherever we are. Or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<p><a class="btn btn-primary" href="{r}charters/">See the fleet</a></p>''')

    # fish & seasons — calendar. 0 = possible, 1 = good, 2 = peak
    cal = [('Sailfish','sailfish.jpg','Peak May – August',[1,1,1,1,2,2,2,2,1,1,1,1],"Not as big as a marlin, but every bit as spectacular: aerial leaps and lightning runs. Sailfish are here year-round thanks to the live bait in these waters, with the best numbers from May to August. A 3/4 or full day gets you offshore to them."),
           ('Blue, black &amp; striped marlin','marlin.jpg','Peak November – April',[2,2,2,2,1,1,1,1,1,1,2,2],"Blue marlin dominate the dry season. Black marlin, which can push 1,500 pounds, headline the tournaments out of Flamingo Marina. Full day charters only, and every one is released."),
           ('Yellowfin tuna','yellow-fin-tuna.jpg','Peak June – October',[0,0,0,1,1,2,2,2,2,2,1,0],"Yellowfin, skipjack and bigeye from 30 pounds to 300-plus. Yellowfin is the best-eating tuna there is: the crew will fillet it, and half the restaurants in town will cook your catch."),
           ('Mahi mahi (dorado)','mahi-mahi.jpg','Best with the rains, Nov – Jan',[2,1,0,0,1,1,1,1,1,2,2,2],"Bright, acrobatic and delicious. Dorado stack up around floating debris when the green-season rivers push out to sea, and stay strong into the early dry season."),
           ('Roosterfish','roosterfish.jpg','Year-round inshore',[1,1,1,1,2,2,2,2,2,2,1,1],"The signature inshore fish of Guanacaste, that comb of a dorsal fin cutting the surface behind a live bait. Roosters are caught along the rocks and beaches all year, and even a half day can put you on one."),
           ('Wahoo','wahoo.jpg','Year-round, best on the rocks',[1,1,1,1,1,1,1,1,1,1,1,1],"Streamlined and fast, often 5 to 6 feet, with fish to 8 feet on record. The rocky coastline around Las Catalinas is the classic wahoo ground."),
           ('Snapper','snapper.jpg','Year-round inshore',[1,1,1,1,1,1,1,1,1,1,1,1],"Red snapper (pargo rojo) and the big cubera, the Pacific dog snapper, which runs 50 to 80 pounds and more. Half-day territory, and the best thing on the grill that night.")]
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    rows = ''.join(f'<tr><td>{n}</td>{"".join(f"<td><i class=\"{ {0:'',1:'g',2:'p'}[v] }\"></i></td>" for v in v12)}</tr>' for n, im, w, v12, t in cal)
    fishcards = ''.join(f'<div class="f rv"><img src="{r}img/{img(im)}" alt=""><div><h3>{n}</h3><div class="when">{w}</div><p>{t}</p></div></div>' for n, im, w, v12, t in cal)
    body = page_hero(r, 'Fish &amp; seasons', 'There is no bad month on the Gold Coast, only different fish. Here is what bites when.', 'sailfish.jpg', [('Home', r+'index.html'), ('Discover', r+'discover/'), ('Fish & seasons', None)]) + f'''
<section><div class="wrap"><div class="sec-head"><div class="kicker">Season calendar</div><h2>What's biting, <em>month by month</em></h2><p>A guide, not a promise. Fish move with water temperature and bait. Ask us about the week you are coming and we will tell you what the boats have been seeing.</p></div>
<div class="season"><table><tr><th>Species</th>{''.join(f'<th>{m}</th>' for m in months)}</tr>{rows}</table></div>
<div class="legend"><span><i></i>Possible</span><span><i class="g"></i>Good</span><span><i class="p"></i>Peak</span></div>
<div class="fish" style="margin-top:50px">{fishcards}</div>
<div class="prose" style="margin-top:40px;max-width:70ch"><p>Boats stay inshore on half-day charters, which is roosterfish, snapper and jack water. To target sailfish, marlin, tuna and mahi you need a 3/4 or full day to get offshore where the continental shelf drops away. <a href="{r}charters/">Compare the boats</a> or <a href="{r}book.html">start a trip plan</a>.</p></div></div></section>'''
    write('discover/fish-seasons.html', page(r, 'Fish & Seasons — Costa Rica Fishing Calendar | Go Fish Costa Rica', 'Month-by-month fishing calendar for Tamarindo and Flamingo: sailfish, marlin, yellowfin tuna, mahi mahi, roosterfish, wahoo and snapper.', body))

    simple('guanacaste-fishing', 'Guanacaste fishing', 'IGFA world-record waters, minutes from the beach.', 'black-marlin-1715038309.jpg', f'''
<p class="lede">For generations the North Pacific coast of Costa Rica has stood as an icon among the world's premier fishing destinations, with a history peppered with International Game Fish Association world records.</p>
<p>What sets this region apart is not just the track record. It is the calm Pacific water and the underwater terrain: tranquil bays, rugged cliffs and reef, a migratory pathway and a home for marlin, sailfish, tuna and the rest of the list.</p>
<h2>Big game, close to shore</h2>
<p>In big game fishing, proximity is everything. Every minute spent running to the grounds is a minute without lines in. Along this coast the bays and beaches drop to over 1,000 feet of water moments from shore, because the continental shelf runs parallel to the coastline. More fishing, less commuting.</p>
<img src="{r}img/{img('tamarindo-beach.jpg')}" alt="Tamarindo beach from the air">
<h2>Tamarindo</h2>
<p>The vibrant hub of the Gold Coast, revered by travel authorities and anglers alike. A deep bench of charter boats launching off the beach, and every kind of accommodation from luxury hotels to family lodges, restaurants, surf and nightlife when the lines are in.</p>
<img src="{r}img/{img('flamingo-beach.jpg')}" alt="Flamingo beach">
<h2>Flamingo</h2>
<p>Just north of Tamarindo, Flamingo's marina put Costa Rica on the international sport fishing map, and the rebuilt marina has made it a serious hub again. Close to the Catalina Islands, rich water, big-boat territory, with resorts and quiet beaches on the shore side.</p>
<img src="{r}img/{img('guanacaste-papagayo-gulf.jpg')}" alt="Papagayo Gulf">
<h2>Carrillo and the south</h2>
<p>Heading south you reach Carrillo, a small bay near the tip of the peninsula that comes alive for a few months each year. There are permanent operations there, but talk to us first so you land on the right one.</p>
<p>Online photos can be deceiving and there is no guarantee of accuracy. Call us toll-free at <a href="tel:{PHONE_TEL}">{PHONE}</a> and let us pair you with the right crew.</p>''')

    body = page_hero(r, 'Weather', 'Live forecast for Tamarindo and Flamingo. Dry season runs December to April; green season May to November brings afternoon showers, calmer mornings and the tuna.', 'tamarindo-beach.jpg', [('Home', r+'index.html'), ('Discover', r+'discover/'), ('Weather', None)]) + f'''
<section><div class="wrap"><div class="sec-head"><div class="kicker">Tamarindo · Flamingo</div><h2>Wind, swell and rain, <em>right now</em></h2></div>
<div class="iframe-wrap"><iframe title="Tamarindo weather" src="https://embed.windy.com/embed2.html?lat=10.30&lon=-85.84&detailLat=10.30&detailLon=-85.84&width=650&height=450&zoom=9&level=surface&overlay=wind&product=ecmwf&menu=&message=true&marker=true&calendar=now&pressure=&type=map&location=coordinates&detail=true&metricWind=kt&metricTemp=%C2%B0C&radarRange=-1" loading="lazy"></iframe></div>
<div class="prose" style="margin-top:36px;max-width:70ch"><h3>What the seasons mean on the water</h3><p><b>December to April</b> is dry season: sunny, windy afternoons from the Papagayo winds, glassy mornings. Marlin peak. <b>May to November</b> is green season: lush, afternoon rain, calmer seas and the best sailfish, tuna and dorado fishing of the year. September and October are the quietest months in town, so you get the water and the crews largely to yourself.</p><p>Charters run rain or shine. Captains call it off only for genuine safety conditions, and then we rebook or refund.</p></div></div></section>'''
    write('discover/weather.html', page(r, 'Weather in Tamarindo & Flamingo | Go Fish Costa Rica', 'Live wind, swell and rain forecast for Tamarindo and Flamingo, plus what dry season and green season mean for fishing.', body))

    body = page_hero(r, 'Contact us', 'We would love to hear from you. Steve &amp; Liisa Quinn.', 'costaricajaco.jpg', [('Home', r+'index.html'), ('Discover', r+'discover/'), ('Contact', None)]) + f'''
<section><div class="wrap contact"><div class="info">
<div><h4>Email</h4><a href="mailto:{EMAIL}">{EMAIL}</a></div>
<div><h4>Toll-free</h4><a href="tel:{PHONE_TEL}">{PHONE}</a><p class="small muted">Seven days a week for fishing questions.</p></div>
<div><h4>In Costa Rica</h4><a href="tel:{PHONE_CR_TEL}">{PHONE_CR}</a><p class="small muted">Call or text this number once you are here. It is on WhatsApp too.</p></div><div data-wa><h4>WhatsApp</h4><a href="https://wa.me/{WHATSAPP}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" style="width:1em;height:1em;vertical-align:-.12em;margin-right:.45em"><path fill="currentColor" d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2m0 1.67c2.2 0 4.27.86 5.83 2.42a8.2 8.2 0 0 1 2.41 5.82c0 4.54-3.7 8.24-8.25 8.24a8.2 8.2 0 0 1-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.2 8.2 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.26-8.24M8.53 7.33c-.16 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.71 2.74 4.22 3.74 2.08.82 2.5.66 2.96.62.45-.04 1.47-.6 1.68-1.18.2-.58.2-1.07.15-1.18-.07-.1-.23-.16-.48-.28-.25-.13-1.47-.73-1.7-.81-.22-.08-.39-.13-.56.12-.16.25-.63.81-.78.97-.14.17-.29.19-.54.06-.24-.12-1.04-.38-1.98-1.22-.73-.65-1.22-1.46-1.37-1.71-.14-.24-.01-.38.11-.5.11-.12.25-.29.37-.44s.16-.25.24-.42c.08-.17.04-.31-.02-.44-.06-.12-.55-1.34-.76-1.83-.2-.48-.4-.42-.55-.42z"/></svg>{PHONE_CR}</a><p class="small muted">Text us on the same number. Usually the fastest way to reach us.</p></div>
<div><h4>Office hours</h4>Monday to Saturday, 8:00am to 6:00pm<br>Sunday closed</div>
<div><h4>Playa Tamarindo</h4>Tamarindo Beach, Guanacaste, Costa Rica 50309</div>
<div><h4>Playa Flamingo</h4>Flamingo Beach, Guanacaste, Costa Rica</div>
<div><h4>Follow</h4><a href="{SOCIAL['ig']}" target="_blank" rel="noopener">Instagram</a> · <a href="{SOCIAL['fb']}" target="_blank" rel="noopener">Facebook</a> · <a href="{SOCIAL['yt']}" target="_blank" rel="noopener">YouTube</a> · <a href="{SOCIAL['ta']}" target="_blank" rel="noopener">TripAdvisor</a></div>
</div>
<div><form class="form-card" id="contact-form"><h3 style="margin-bottom:18px">Send a message</h3>
<div class="fld"><label for="c-name">Your name</label><input id="c-name" name="name" required></div>
<div class="row2"><div class="fld"><label for="c-email">Email</label><input id="c-email" type="email" name="email" required></div><div class="fld"><label for="c-phone">Phone</label><input id="c-phone" name="phone"></div></div>
<div class="fld"><label for="c-msg">Message</label><textarea id="c-msg" name="message" required style="min-height:140px"></textarea></div>
<button class="btn btn-primary btn-block" type="submit">Send message</button>
<p class="small muted" style="margin-top:10px">Booking a boat? The <a href="{r}book.html">trip planner</a> is faster.</p></form></div></div></section>'''
    write('discover/contact-us.html', page(r, 'Contact Go Fish Costa Rica', f'Email {EMAIL}, call toll-free {PHONE}, or call and text {PHONE_CR} in Costa Rica — also on WhatsApp. Offices at Playa Tamarindo and Playa Flamingo, Guanacaste.', body))

# ---------------------------------------------------------------- GALLERY
def gallery():
    r = ''
    ims = D('gallery.json')
    tiles = ''.join(f'<a href="{r}img/{g}" data-lb="g"><img src="{r}img/{g}" alt="" loading="lazy"></a>' for g in ims)
    body = page_hero(r, 'Photo gallery', 'Fishing adventures and memorable moments from unforgettable trips. Tag us @gofishcostarica and we will add yours.', 'img_0928.jpg', [('Home', r+'index.html'), ('Gallery', None)]) + f'<section><div class="wrap"><div class="masonry">{tiles}</div></div></section>'
    write('gallery.html', page(r, 'Photo Gallery | Go Fish Costa Rica', 'Marlin, sailfish, roosterfish, tuna and the crews and families who caught them. Photos from Go Fish Costa Rica charters in Tamarindo and Flamingo.', body))
    return len(ims)

# ---------------------------------------------------------------- BLOG
def blog():
    r = '../'
    def card(p):
        return f'<a class="card post-card" href="{r}blog/{p["slug"]}.html"><div class="ph"><img src="{r}img/{img(p["image"])}" alt="" loading="lazy"></div><div class="body"><span class="date">{p["date"]}</span><h3>{E(p["title"])}</h3><p class="small muted">{E((p["desc"] or (p["paras"][0] if p["paras"] else ""))[:140])}…</p></div></a>'
    per = 12; pages = [BLOG[i:i+per] for i in range(0, len(BLOG), per)]
    for n, chunk in enumerate(pages):
        pager = '<div class="pager">' + ''.join(f'<a class="{"on" if i==n else ""}" href="{r}blog/{"index" if i==0 else "page-%d" % (i+1)}.html">{i+1}</a>' for i in range(len(pages))) + '</div>' if len(pages) > 1 else ''
        body = page_hero(r, 'The Go Fish blog', 'Fishing reports, seasons, festivals, where to eat and what we have been up to since 2017.', 'two-marlin.jpg', [('Home', r+'index.html'), ('Blog', None)]) + f'<section><div class="wrap"><div class="grid g3">{"".join(card(p) for p in chunk)}</div>{pager}</div></section>'
        write(f'blog/{"index" if n==0 else "page-%d" % (n+1)}.html', page(r, f'Blog{"" if n==0 else " — page %d" % (n+1)} | Go Fish Costa Rica', 'Fishing tips, seasonal reports, Tamarindo and Flamingo news from Go Fish Costa Rica.', body))
    for i, p in enumerate(BLOG):
        content = ''
        for q in p['paras']:
            if len(q) < 90 and not q.endswith('.') and not q.endswith('!') and not q.endswith('?') and not q.endswith(':') and len(q.split()) <= 12 and not re.match(r'^\d', q): content += f'<h3>{E(q)}</h3>'
            else: content += f'<p>{E(q)}</p>'
        nxt = BLOG[i+1] if i+1 < len(BLOG) else BLOG[0]
        body = f'''<header class="page-hero"><img class="bg" src="{r}img/{img(p['image'])}" alt=""><div class="wrap"><div class="crumbs"><a href="{r}index.html">Home</a><span>/</span><a href="{r}blog/">Blog</a></div><div class="kicker" style="color:var(--sand)">{p['date']}</div><h1 style="font-size:clamp(32px,4.6vw,56px);max-width:22ch">{E(p['title'])}</h1></div></header>
<section><div class="wrap-n prose">{content}
<hr style="border:0;border-top:1px solid var(--line);margin:40px 0">
<p class="small muted">Next up: <a href="{r}blog/{nxt['slug']}.html">{E(nxt['title'])}</a> · <a href="{r}blog/">All posts</a></p></div></section>
<section class="cta"><img class="bg" src="{r}img/{img('marlin.jpg')}" alt=""><div class="wrap"><h2>Ready to fish Guanacaste?</h2><p>Seventeen boats, two locations, one honest recommendation.</p><div class="row"><a class="btn btn-sand" href="{r}book.html">Plan my trip</a><a class="btn btn-ghost" href="{r}charters/">See the fleet</a></div></div></section>'''
        write(f"blog/{p['slug']}.html", page(r, f"{p['title']} | Go Fish Costa Rica", (p['desc'] or (p['paras'][0] if p['paras'] else p['title']))[:155], body))

# ---------------------------------------------------------------- TRIP PLANNER
def planner():
    r = ''
    body = f'''<header class="page-hero" style="padding-bottom:120px"><img class="bg" src="{r}img/{img('offshore-aerial.jpg')}" alt="Sport fishing boat trolling offshore from Tamarindo"><div class="wrap"><div class="crumbs"><a href="{r}index.html">Home</a><span>/</span><span>Trip planner</span></div><h1>Plan your trip in <em style="color:var(--foam)">four steps</em></h1><p>Tell us what kind of day you want and we match you to a boat or a tour that fits. No obligation to ask. Steve &amp; Liisa confirm availability within hours and send you the plan for your trip.</p></div></header>
<section style="margin-top:-100px;padding-top:0;position:relative;z-index:2"><div class="wrap"><div class="wiz" id="wizard">
<div class="prog"><span class="on">1 · Trip</span><span>2 · When</span><span>3 · Pick</span><span>4 · Send</span></div>
<div class="pane on"><h2>What kind of day are you after?</h2><p class="lead">Pick one. You can add more days once we are talking.</p>
<div class="opts">
<label class="opt"><input type="radio" name="type" value="fishing"><span class="ic">◐</span><b>Fishing charter</b><small>Half, 3/4 or full day on one of 14 sport fishing boats. Inshore roosters to offshore marlin.</small></label>
<label class="opt"><input type="radio" name="type" value="catamaran"><span class="ic">◭</span><b>Private catamaran</b><small>Your own 40', 42' or 65' cat for a morning or sunset sail. Snorkel gear, bar, lunch.</small></label>
<label class="opt"><input type="radio" name="type" value="adventure"><span class="ic">▲</span><b>Adventures</b><small>ATV, zipline, volcano, Rio Celeste, estuary, surf lesson, spa and more.</small></label></div>
<h2 style="font-size:24px;margin-top:30px">Which location is closer to you?</h2><p class="lead">Boats launch from the beach at both. Tours pick up from either.</p>
<div class="opts" style="grid-template-columns:1fr 1fr 1fr">
<label class="opt"><input type="radio" name="base" value="Tamarindo"><b>Tamarindo</b><small>Also Langosta, Pinilla, JW Marriott, Avellanas.</small></label>
<label class="opt"><input type="radio" name="base" value="Flamingo"><b>Flamingo</b><small>Also Potrero, Conchal, Brasilito, Westin, Las Catalinas.</small></label>
<label class="opt"><input type="radio" name="base" value=""><b>Not sure yet</b><small>Show me both. I will decide with you.</small></label></div>
<div class="nav-row"><span></span><button type="button" class="btn btn-primary" data-next>Next: dates &amp; group</button></div></div>

<div class="pane"><h2>When are you here, and how many?</h2><p class="lead">Give us your arrival and departure. You can pin each activity to a day later, or leave that to us.</p>
<div class="row3" style="max-width:620px"><div class="fld"><label for="w-arrive">Arrival</label><input id="w-arrive" type="date" name="arrive"></div><div class="fld"><label for="w-depart">Departure</label><input id="w-depart" type="date" name="depart"></div></div>
<div class="row3" style="max-width:620px;margin-top:12px">{pax_fields('w')}</div>
<p class="small muted">Charter rates are per boat, not per person. Fishing with ten or more? Two boats is usually the better call: more room to work, more lines in the water and more chances at a fish. Tell us the group and we will pair the right two.</p>
<div class="nav-row"><button type="button" class="btn btn-ghost" data-prev>Back</button><button type="button" class="btn btn-primary" data-next>Next: pick your boat</button></div></div>

<div class="pane"><div id="picks-head"></div>
<div id="dur-row" style="max-width:420px;margin-bottom:22px"><label class="small muted" style="display:block;margin-bottom:6px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;font-size:11.5px">Charter length</label><div class="seg"><label class="on"><input type="radio" name="dur" value="half" checked>Half day<small>inshore · 5 hrs</small></label><label><input type="radio" name="dur" value="tq">3/4 day<small>inshore/offshore · 7 hrs</small></label><label><input type="radio" name="dur" value="full">Full day<small>inshore/offshore · 9 hrs</small></label></div></div>
<div id="fish-row" style="max-width:560px;margin-bottom:24px">{style_field('w')}{fish_field('w')}</div>
<div class="picks" id="picks"></div>
<div class="nav-row"><button type="button" class="btn btn-ghost" data-prev>Back</button><button type="button" class="btn btn-primary" data-next>Next: your details</button></div></div>

<div class="pane"><h2>Almost there.</h2><p class="lead">Check the summary, add your details, and send. We confirm availability within hours.</p>
<div class="summary" id="summary"></div>
<div class="fld" id="wiz-day" style="max-width:340px;margin:20px 0 4px"><label for="w-when">Which day would you like this?</label><select id="w-when" name="when"></select></div>
<div class="row" style="gap:10px;margin:18px 0 8px"><button type="button" class="btn btn-ghost" id="wiz-add">Add this and plan another day</button></div>
<div id="wiz-trip"></div>
<form id="wiz-form"><div class="fld"><label for="w-name">Full name</label><input id="w-name" name="name" required autocomplete="name" placeholder="First and last name"></div>
<div class="row2"><div class="fld"><label for="w-email">Email</label><input id="w-email" type="email" name="email" required autocomplete="email"></div><div class="fld"><label for="w-phone">Phone / WhatsApp</label><input id="w-phone" name="phone" autocomplete="tel"></div></div>
{stay_field('w')}
<div class="fld"><label for="w-notes" data-notes-label>Anything else we should know?</label><textarea id="w-notes" name="notes"></textarea></div>
<div class="fld"><label for="w-tr">Need transportation?</label><select id="w-tr" name="transport"><option value="">No, we have it covered</option><option>Yes, hotel to the boat and back</option><option>Yes, airport pickup too</option><option>Not sure yet, tell me the options</option></select></div>
<div class="nav-row"><button type="button" class="btn btn-ghost" data-prev>Back</button><button class="btn btn-primary" type="submit" id="wiz-send">Send my request</button></div></form></div>
</div>
<p class="small muted" style="text-align:center;margin-top:24px">Prefer to talk? Call toll-free <a href="tel:{PHONE_TEL}">{PHONE}</a> or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div></section>'''
    write('book.html', page(r, 'Plan Your Trip | Go Fish Costa Rica', 'Four-step trip planner: pick fishing charter, private catamaran or adventure, choose your location and dates, see the boats that fit your group, send a request.', body, extra_head=fleet_js()))

def trip_page():
    """trip.html — the running list. The planner still books one thing; this stacks a whole week."""
    r = ''
    body = f"""<header class="page-hero" style="padding-bottom:110px"><img class="bg" src="{r}img/{img('offshore-aerial.jpg')}" alt="Sport fishing boat trolling offshore from Tamarindo"><div class="wrap"><div class="crumbs"><a href="{r}index.html">Home</a><span>/</span><span>My trip</span></div>
<h1>Your <em style="color:var(--foam)">whole trip</em>, in one request.</h1>
<p>Everything you added lives here. Tell us when you land and when you leave, pin a day to anything you feel strongly about, and send it as one request. Steve &amp; Liisa come back within hours with availability and one price for the lot.</p></div></header>

<section><div class="wrap-n" id="trip">

<div class="trip-block">
  <div class="sec-head"><div class="kicker">Step one</div><h2 style="font-size:30px">When are you here?</h2></div>
  <div class="row3" style="max-width:620px">
    <div class="fld"><label for="t-arrive">Arrival</label><input id="t-arrive" type="date" name="arrive" required></div>
    <div class="fld"><label for="t-depart">Departure</label><input id="t-depart" type="date" name="depart" required></div>
  </div>
  <div class="row3" style="max-width:620px;margin-top:12px">{pax_fields('t')}</div>
  <p class="small muted" style="margin-top:10px">Dates can be approximate. Once we have them we can tell you what is biting and what is already booked.</p>
</div>

<div class="trip-block">
  <div class="sec-head row"><div><div class="kicker">Step two</div><h2 style="font-size:30px">Your trip</h2></div>
  <div class="row" style="gap:8px"><a class="btn btn-ghost btn-sm" href="{r}charters/">Add a boat</a><a class="btn btn-ghost btn-sm" href="{r}adventures/">Add a tour</a></div></div>
  <div id="trip-items"></div>
</div>

<div class="trip-block">
  <div class="sec-head"><div class="kicker">Step three</div><h2 style="font-size:30px">Where do we send the plan?</h2></div>
  <form id="trip-form" class="form-card" style="max-width:720px">
    <div class="fld"><label for="t-name">Full name</label><input id="t-name" name="name" required autocomplete="name" placeholder="First and last name"></div>
    <div class="row2"><div class="fld"><label for="t-email">Email</label><input id="t-email" type="email" name="email" required autocomplete="email"></div><div class="fld"><label for="t-phone">Phone / WhatsApp</label><input id="t-phone" name="phone" autocomplete="tel"></div></div>
    {stay_field('t')}
    <div class="fld"><label for="t-tr">Need transportation?</label><select id="t-tr" name="transport"><option value="">No, we have it covered</option><option>Yes, hotel to the boat and back</option><option>Yes, airport pickup too</option><option>Not sure yet, tell me the options</option></select></div>
    <div class="fld"><label for="t-notes" data-notes-label>Anything else we should know?</label><textarea id="t-notes" name="notes" placeholder="What you want to catch, anything you are celebrating."></textarea></div>
    <button class="btn btn-primary btn-block" type="submit">Send my trip</button>
    <div class="note">Steve &amp; Liisa confirm availability within hours and send you the plan for your whole trip.</div>
  </form>
</div>

</div></section>
<p class="small muted" style="text-align:center;margin:0 0 60px">Booking just one day? The <a href="{r}book.html">trip planner</a> walks you through it. Or call toll-free <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>"""
    write('trip.html', page(r, 'My Trip | Go Fish Costa Rica', 'Your running list of Go Fish charters and adventures. Add your dates and send the whole trip as one request.', body, extra_head=fleet_js()))

# ---------------------------------------------------------------- 404 + sitemap
def extras():
    r = ''
    body = f'<header class="page-hero" style="min-height:70vh;display:flex;align-items:center"><img class="bg" src="{r}img/{img("sloth.jpg")}" alt=""><div class="wrap"><div class="kicker" style="color:var(--sand)">404</div><h1>That one got away.</h1><p>The page you are after has moved or never existed. The fish are still here though.</p><div class="hero-actions"><a class="btn btn-sand" href="{r}index.html">Back to the beach</a><a class="btn btn-ghost" href="{r}charters/">See the fleet</a></div></div></header>'
    write('404.html', page(r, 'Page not found | Go Fish Costa Rica', 'Page not found.', body))
    urls = ['', 'charters/', 'adventures/', 'dining/', 'discover/', 'gallery.html', 'blog/', 'book.html', 'trip.html'] + [f'charters/{b["slug"]}.html' for b in FLEET] + [f'adventures/{a["slug"]}.html' for a in ADV] + [f'dining/{d["slug"]}.html' for d in DINING] + [f'discover/{s}.html' for s in ['about-us','our-pledge-to-you','crews-equipment','fish-seasons','guanacaste-fishing','weather','contact-us']] + [f'blog/{p["slug"]}.html' for p in BLOG]
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(f'<url><loc>https://gofishcr.com/{u}</loc></url>' for u in urls) + '\n</urlset>\n')
    write('robots.txt', 'User-agent: *\nAllow: /\nSitemap: https://gofishcr.com/sitemap.xml\n')
    write('version.json', json.dumps({'build': BUILD}) + '\n')
    # Old-site addresses that have no matching page in the new build -> instant redirect
    for src, dst in [('reservation.html', 'book.html'), ('discover/blog.html', 'blog/'), ('locations/tamarindo.html', 'discover/guanacaste-fishing.html'),
                     ('locations/flamingo.html', 'discover/guanacaste-fishing.html'), ('locations/index.html', 'discover/guanacaste-fishing.html'), ('sitemap.html', 'index.html')]:
        write(src, f'<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=/{dst}"><link rel="canonical" href="https://gofishcr.com/{dst}"><title>Redirecting</title></head><body><a href="/{dst}">Continue</a></body></html>')

if __name__ == '__main__':
    import day
    write('index.html', day.home(dict(E=E, img=img, FLEET=FLEET, ADV=ADV, boat_len=boat_len, SOCIAL=SOCIAL, EMAIL=EMAIL, PHONE=PHONE, PHONE_TEL=PHONE_TEL, PHONE_CR=PHONE_CR, PHONE_CR_TEL=PHONE_CR_TEL, REVIEWS=REVIEWS, page=page, fleet_js=fleet_js))); charters(); adventures(); dining(); discover(); n = gallery(); blog(); planner(); trip_page(); extras()
    pages = sum(len([f for f in fs if f.endswith('.html')]) for _, _, fs in os.walk(ROOT) if '/dl' not in _)
    print('built', pages, 'pages ·', n, 'gallery photos')
    if MISSING: print('MISSING IMAGES:', sorted(MISSING))
