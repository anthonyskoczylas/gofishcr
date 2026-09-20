/* Go Fish Costa Rica — site behaviour */
(function () {
  'use strict';

  // ---- CONFIG (edit here only) -------------------------------------------
  // WhatsApp: leave empty ('') to hide the WhatsApp buttons. Format: country code + number, digits only.
  var CONFIG = {
    email: document.documentElement.getAttribute('data-email') || 'gofishcr@gmail.com',   // set EMAIL in build.py, not here
    cc: document.documentElement.getAttribute('data-cc') || '',                             // set EMAIL_CC in build.py
    endpoint: document.documentElement.getAttribute('data-endpoint') || '',                 // set MAIL_ENDPOINT in build.py
    phone: '1-888-434-7491',
    phoneCR: '+506 8393 7555',
    whatsapp: '',
    behold: ''   // Behold.so feed ID for @gofishcostarica; leave empty until Steve creates one at behold.so
  };
  window.GF_CONFIG = CONFIG;

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var ROOT = document.documentElement.getAttribute('data-root') || '';
  var money = function (n) { return '$' + Number(n).toLocaleString('en-US'); };

  // ---- NAV -----------------------------------------------------------------
  var nav = $('nav.top');
  var pageHero = document.querySelector('.page-hero');
  function onScroll() { if (!nav) return; nav.classList.toggle('scrolled', window.scrollY > 40); if (pageHero && !document.getElementById('day')) nav.classList.toggle('over-photo', window.scrollY < pageHero.offsetHeight - 72); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  var burger = $('.burger'), drawer = $('.drawer');
  if (burger && drawer) {
    burger.addEventListener('click', function () { drawer.classList.add('open'); document.body.style.overflow = 'hidden'; });
    $('.drawer .close').addEventListener('click', function () { drawer.classList.remove('open'); document.body.style.overflow = ''; });
  }

  // ---- REVEAL --------------------------------------------------------------
  var rv = $$('.rv');
  if ('IntersectionObserver' in window && rv.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    rv.forEach(function (el) { io.observe(el); });
    setTimeout(function () { rv.forEach(function (el) { el.classList.add('in'); }); }, 5000); // failsafe
  } else { rv.forEach(function (el) { el.classList.add('in'); }); }

  // ---- LIGHTBOX ------------------------------------------------------------
  var lbImgs = $$('[data-lb]');
  if (lbImgs.length) {
    var lb = document.createElement('div'); lb.className = 'lb';
    lb.innerHTML = '<button class="x" aria-label="Close">&times;</button><button class="p" aria-label="Previous">&#8249;</button><img alt=""><button class="n" aria-label="Next">&#8250;</button><div class="c"></div>';
    document.body.appendChild(lb);
    var groups = {}, cur = { g: null, i: 0 };
    lbImgs.forEach(function (a) { var g = a.getAttribute('data-lb') || 'x'; (groups[g] = groups[g] || []).push(a.getAttribute('href') || a.getAttribute('data-src')); });
    function show(g, i) {
      var list = groups[g]; cur = { g: g, i: (i + list.length) % list.length };
      $('img', lb).src = list[cur.i]; $('.c', lb).textContent = (cur.i + 1) + ' / ' + list.length;
      lb.classList.add('open'); document.body.style.overflow = 'hidden';
    }
    function hide() { lb.classList.remove('open'); document.body.style.overflow = ''; }
    lbImgs.forEach(function (a) {
      a.addEventListener('click', function (e) { e.preventDefault(); var g = a.getAttribute('data-lb') || 'x'; show(g, groups[g].indexOf(a.getAttribute('href') || a.getAttribute('data-src'))); });
    });
    $('.x', lb).addEventListener('click', hide);
    $('.p', lb).addEventListener('click', function () { show(cur.g, cur.i - 1); });
    $('.n', lb).addEventListener('click', function () { show(cur.g, cur.i + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) hide(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') hide(); if (e.key === 'ArrowLeft') show(cur.g, cur.i - 1); if (e.key === 'ArrowRight') show(cur.g, cur.i + 1);
    });
  }

  // ---- TOAST ---------------------------------------------------------------
  var toastEl;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement('div'); toastEl.className = 'toast'; document.body.appendChild(toastEl); }
    toastEl.textContent = msg; toastEl.classList.add('show'); setTimeout(function () { toastEl.classList.remove('show'); }, 2600);
  }
  function copy(text) {
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(function () { toast('Copied to clipboard'); });
    else toast('Select and copy the text below');
  }

  // ---- CHOICE CHIPS (inshore/offshore, target fish) ------------------------
  function syncChips(group) { $$('label', group).forEach(function (l) { var i = l.querySelector('input'); if (i) l.classList.toggle('on', i.checked); }); }
  $$('.chip-group').forEach(function (g) {
    syncChips(g);
    g.addEventListener('change', function () {
      syncChips(g);
      if (g.hasAttribute('data-style')) { g.setAttribute('data-touched', '1'); filterFish(g.closest('form') || g.parentNode.parentNode || document); }
    });
  });
  function checkedValues(scope, name) {
    return $$('[name="' + name + '"]', scope).filter(function (i) { return i.checked && i.value; }).map(function (i) { return i.value; });
  }
  // Charter length implies where the boat fishes, until the guest says otherwise.
  function autoStyle(scope, dur) {
    var g = $('[data-style]', scope);
    if (g && !g.getAttribute('data-touched')) {
      var want = dur === 'half' ? 'Inshore' : 'Offshore';
      var el = g.querySelector('input[value="' + want + '"]'); if (el) { el.checked = true; syncChips(g); }
    }
    filterFish(scope);
  }
  // Show only the fish you can actually catch where the boat is going.
  function filterFish(scope) {
    var sg = $('[data-style]', scope), fg = $('[data-fish]', scope);
    if (!fg) return;
    var style = sg ? ((sg.querySelector('input:checked') || {}).value || '') : '';
    var want = style === 'Inshore' ? 'in' : style === 'Offshore' ? 'off' : '';
    $$('label', fg).forEach(function (l) {
      var zone = l.getAttribute('data-zone');
      var show = !want || zone === 'both' || zone === want;
      l.hidden = !show;
      if (!show) { var i = l.querySelector('input'); if (i) i.checked = false; }
    });
    syncChips(fg);
  }

  // ---- GUESTS (adults + kids) ----------------------------------------------
  function guests(f) { var a = +((f.adults || {}).value || 0), k = +((f.kids || {}).value || 0); return { adults: a, kids: k, total: a + k }; }
  function guestText(g) {
    var out = g.adults + ' adult' + (g.adults === 1 ? '' : 's');
    if (g.kids) out += ', ' + g.kids + ' kid' + (g.kids === 1 ? '' : 's');
    return out;
  }

  // ---- ACCOMMODATION MAP PICKER (Leaflet + OpenStreetMap, no API key) -------
  var TAMARINDO = [10.2993, -85.8371], leafletP;
  function loadLeaflet() {
    if (leafletP) return leafletP;
    leafletP = new Promise(function (res, rej) {
      var l = document.createElement('link'); l.rel = 'stylesheet';
      l.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css'; document.head.appendChild(l);
      var sc = document.createElement('script'); sc.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js';
      sc.onload = res; sc.onerror = rej; document.head.appendChild(sc);
    });
    return leafletP;
  }
  function osmSearch(q) {
    return fetch('https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=cr&q=' + encodeURIComponent(q))
      .then(function (r) { return r.json(); }).catch(function () { return []; });
  }
  function osmReverse(lat, lng) {
    return fetch('https://nominatim.openstreetmap.org/reverse?format=json&zoom=17&lat=' + lat + '&lon=' + lng)
      .then(function (r) { return r.json(); }).catch(function () { return null; });
  }
  var TICK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
  $$('[data-stay]').forEach(function (box) {
    var btn = $('[data-pin]', box), wrap = $('.pin-wrap', box), input = $('input[name="stay"]', box),
        geo = $('input[name="stay_geo"]', box), link = $('input[name="stay_map"]', box),
        map = null, marker = null, built = false;

    function setPin(lat, lng) {
      geo.value = lat.toFixed(5) + ', ' + lng.toFixed(5);
      link.value = 'https://www.google.com/maps?q=' + lat.toFixed(6) + ',' + lng.toFixed(6);
      var ok = $('.pin-ok', box) || (function () { var d = document.createElement('div'); d.className = 'pin-ok'; box.appendChild(d); return d; })();
      ok.innerHTML = TICK + '<span>Pinned. The crew gets a map link straight to the door.</span>';
      osmReverse(lat, lng).then(function (r) {
        if (r && r.display_name) ok.innerHTML = TICK + '<span>Pinned near <b>' + r.display_name.split(',').slice(0, 3).join(',').replace(/</g, '&lt;') + '</b></span>';
      });
    }
    function place(lat, lng, zoom) {
      if (!marker) { marker = window.L.marker([lat, lng], { draggable: true }).addTo(map); marker.on('dragend', function () { var q = marker.getLatLng(); setPin(q.lat, q.lng); }); }
      else marker.setLatLng([lat, lng]);
      map.setView([lat, lng], zoom || Math.max(map.getZoom(), 16));
      setPin(lat, lng);
    }
    function build() {
      wrap.innerHTML = '<div class="pin-map"></div><div class="pin-bar"><span>Tap the map to drop a pin, then drag it to fine-tune.</span><button type="button" data-clear>Clear</button></div>';
      map = window.L.map($('.pin-map', wrap), { scrollWheelZoom: false }).setView(TAMARINDO, 12);
      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap' }).addTo(map);
      map.on('click', function (e) { place(e.latlng.lat, e.latlng.lng); });
      $('[data-clear]', wrap).addEventListener('click', function () {
        if (marker) { map.removeLayer(marker); marker = null; }
        geo.value = ''; link.value = '';
        var ok = $('.pin-ok', box); if (ok) ok.remove();
      });
      built = true;
      if (input.value.trim()) osmSearch(input.value.trim() + ', Guanacaste, Costa Rica').then(function (hits) { if (hits && hits[0]) place(+hits[0].lat, +hits[0].lon, 16); });
      setTimeout(function () { map.invalidateSize(); }, 60);
    }
    btn.addEventListener('click', function () {
      if (built) { wrap.hidden = !wrap.hidden; if (!wrap.hidden) setTimeout(function () { map.invalidateSize(); }, 60); return; }
      wrap.hidden = false; btn.disabled = true;
      loadLeaflet().then(function () { btn.disabled = false; build(); })
        .catch(function () { btn.disabled = false; wrap.hidden = true; toast('Map could not load. Type the name instead.'); });
    });
  });
  function stayPayload(f) {
    return { stay: (f.stay && f.stay.value) || '', stayGeo: (f.stay_geo && f.stay_geo.value) || '', stayMap: (f.stay_map && f.stay_map.value) || '' };
  }
  function stayLines(f) {
    var out = [];
    if (f.stay && f.stay.value) out.push('Staying at: ' + f.stay.value);
    if (f.stay_map && f.stay_map.value) out.push('Map pin: ' + f.stay_map.value);
    return out;
  }

  // ---- REQUEST HELPERS (static site: email / WhatsApp / phone) ------------
  function buildRequest(lines, data) {
    var body = lines.filter(Boolean).join('\n');
    return {
      text: body,
      data: data || null,
      mailto: 'mailto:' + CONFIG.email + '?' + (CONFIG.cc ? 'cc=' + encodeURIComponent(CONFIG.cc) + '&' : '') + 'subject=' + encodeURIComponent(lines[0].replace(/^Request: /, '') + ' — booking request') + '&body=' + encodeURIComponent(body + '\n\nSent from gofishcr.com'),
      wa: CONFIG.whatsapp ? 'https://wa.me/' + CONFIG.whatsapp + '?text=' + encodeURIComponent(body) : ''
    };
  }
  function todayISO(offsetDays) { var d = new Date(); d.setDate(d.getDate() + (offsetDays || 0)); return d.toISOString().slice(0, 10); }
  function fmtDate(iso) { if (!iso) return ''; var p = iso.split('-'); var d = new Date(p[0], p[1] - 1, p[2]); return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }); }
  $$('input[type=date]').forEach(function (i) { if (!i.min) i.min = todayISO(1); });

  // ---- QUICK BOOK BAR (home) ----------------------------------------------
  var qb = $('#qb');
  if (qb) qb.addEventListener('submit', function (e) {
    e.preventDefault();
    var p = new URLSearchParams();
    ['base', 'date', 'pax'].forEach(function (k) { var v = qb.elements[k] && qb.elements[k].value; if (v) p.set(k, v); });
    window.location.href = ROOT + 'charters/?' + p.toString();
  });

  // ---- FLEET FILTER (charters index) ---------------------------------------
  var fl = $('#fleet-filters');
  if (fl && window.FLEET) {
    var cards = $$('[data-boat]');
    var qs = new URLSearchParams(location.search);
    ['base', 'pax', 'budget', 'wash', 'sort'].forEach(function (k) { if (qs.get(k) && fl.elements[k]) fl.elements[k].value = qs.get(k); });
    if (qs.get('date')) { var d = $('#fleet-date'); if (d) d.textContent = 'Availability for ' + fmtDate(qs.get('date')) + ' is confirmed by email within hours.'; }
    function apply() {
      var base = fl.elements.base.value, pax = +fl.elements.pax.value || 0, budget = +fl.elements.budget.value || 0, wash = fl.elements.wash.value, sort = fl.elements.sort.value;
      var shown = 0, list = [];
      cards.forEach(function (c) {
        var b = window.FLEET[c.getAttribute('data-boat')];
        var ok = true;
        if (base && b.locations.indexOf(base) < 0) ok = false;
        if (pax && b.max_pax && b.max_pax < pax) ok = false;
        if (pax && !b.max_pax && pax > 20) ok = false;
        if (budget && b.half && b.half > budget) ok = false;
        if (wash === 'yes' && !b.washroom) ok = false;
        c.style.display = ok ? '' : 'none'; if (ok) { shown++; list.push(c); }
      });
      var key = { price: function (b) { return b.half || 99999; }, 'price-desc': function (b) { return -(b.half || 99999); }, size: function (b) { return b.length; }, 'size-desc': function (b) { return -b.length; } }[sort];
      if (key) { var grid = cards[0].parentNode; list.sort(function (x, y) { return key(window.FLEET[x.getAttribute('data-boat')]) - key(window.FLEET[y.getAttribute('data-boat')]); }).forEach(function (c) { grid.appendChild(c); }); }
      $('#fleet-count').textContent = shown ? shown + ' boat' + (shown > 1 ? 's' : '') + ' match' : 'No exact match';
      $('#fleet-empty').style.display = shown ? 'none' : '';
      var p = new URLSearchParams(); ['base', 'pax', 'budget', 'wash', 'sort'].forEach(function (k) { if (fl.elements[k].value) p.set(k, fl.elements[k].value); });
      if (qs.get('date')) p.set('date', qs.get('date'));
      history.replaceState(null, '', location.pathname + (p.toString() ? '?' + p : ''));
    }
    fl.addEventListener('change', apply);
    $('.reset', fl).addEventListener('click', function () { ['base', 'pax', 'budget', 'wash', 'sort'].forEach(function (k) { fl.elements[k].value = ''; }); apply(); });
    apply();
  }

  // ---- BOAT BOOKING PANEL --------------------------------------------------
  var bp = $('#boat-book');
  if (bp && window.BOAT) {
    var B = window.BOAT;
    var durLabel = { half: '5 hours · inshore', tq: '7 hours · offshore', full: '9 hours · offshore' };
    var price = { half: B.half, tq: B.three_quarter, full: B.full };
    function refresh() {
      $$('.seg label', bp).forEach(function (l) { l.classList.toggle('on', $('input', l).checked); });
      var d = (bp.elements.dur && bp.elements.dur.value) || 'half';
      var est = $('#est'); if (est) { est.querySelector('b').textContent = price[d] ? money(price[d]) : 'Quote'; est.querySelector('small').textContent = price[d] ? 'per boat, excluding taxes · ' + durLabel[d] : 'custom quote for private catamarans'; }
      var bb = $('.bookbar b'); if (bb) bb.textContent = price[d] ? money(price[d]) : 'Quote';
      var bs = $('.bookbar small'); if (bs) bs.textContent = price[d] ? durLabel[d].split(' \u00b7 ')[0] + ' \u00b7 per boat' : 'private sail';
      // the headline price follows the charter length too
      var from = $('#boat-from');
      if (from) {
        from.querySelector('b').textContent = price[d] ? money(price[d]) : 'Quote';
        from.querySelector('span').textContent = price[d] ? durLabel[d].split(' \u00b7 ')[0] + ' \u00b7 per boat' : 'private sail';
      }
      autoStyle(bp, d);
    }
    bp.addEventListener('change', refresh); refresh();
    var qs2 = new URLSearchParams(location.search);
    if (qs2.get('date') && bp.elements.date) bp.elements.date.value = qs2.get('date');
    if (qs2.get('pax') && bp.elements.adults) bp.elements.adults.value = Math.min(+qs2.get('pax'), B.max_pax || 20);
    bp.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = bp.elements, d = f.dur ? f.dur.value : 'half';
      var g = guests(f);
      if (B.max_pax && g.total > B.max_pax) return toast('This boat takes up to ' + B.max_pax + ' guests. Tell us in the notes and we will pair two boats.');
      if (!g.total) return toast('Add at least one guest');
      var style = (f.style && f.style.value) || '', fish = checkedValues(bp, 'fish');
      var req = buildRequest([
        'Request: ' + B.name + ' (' + B.locations.join(' / ') + ')',
        'Charter length: ' + durLabel[d] + (price[d] ? ' — ' + money(price[d]) + ' per boat' : ' — custom quote'),
        style ? 'Fishing style: ' + style : '',
        fish.length ? 'Target fish: ' + fish.join(', ') : '',
        'Date: ' + (fmtDate(f.date.value) || 'flexible'),
        'Guests: ' + guestText(g),
        'Name: ' + f.name.value,
        'Email: ' + f.email.value,
        f.phone.value ? 'Phone / WhatsApp: ' + f.phone.value : ''
      ].concat(stayLines(f), [
        'Transportation: ' + (f.transport.value || 'not needed'),
        f.notes.value ? 'Notes: ' + f.notes.value : ''
      ]), Object.assign({ kind: 'boat', trip: B.name, base: B.locations.join(' / '), length: durLabel[d], rate: price[d] ? money(price[d]) + ' per boat' : 'custom quote', style: style, fish: fish.join(', '), dateText: fmtDate(f.date.value), pax: g.total, adults: g.adults, kids: g.kids, name: f.name.value, email: f.email.value, phone: f.phone.value, transport: f.transport.value, notes: f.notes.value }, stayPayload(f)));
      showSent(bp, req, 'Your request for the ' + B.name + ' is ready to send.');
    });
  }

  // ---- ADVENTURE / GENERIC REQUEST PANEL ----------------------------------
  var ap = $('#adv-book'), advRate = null;
  // Tours with a rate matrix (ATV): duration + machine drive a live price.
  if (ap && window.ADV_RATES) {
    var R = window.ADV_RATES;
    advRate = function () {
      var dk = (ap.elements.dur && ap.elements.dur.value) || R.durations[0].key;
      var vk = (ap.elements.vehicle && ap.elements.vehicle.value) || R.vehicles[0].key;
      var d = R.durations.filter(function (x) { return x.key === dk; })[0] || R.durations[0];
      var v = R.vehicles.filter(function (x) { return x.key === vk; })[0] || R.vehicles[0];
      return { price: v.prices[dk], duration: d.label, vehicle: v.label, unit: v.unit };
    };
    var refreshRate = function () {
      var r = advRate(), box = $('#adv-from');
      if (box) { box.querySelector('b').textContent = money(r.price); box.querySelector('span').textContent = r.unit + ', excluding taxes'; }
      var bb = $('.bookbar b'); if (bb) bb.textContent = money(r.price);
      var bs = $('.bookbar small'); if (bs) bs.textContent = r.unit;
    };
    ap.addEventListener('change', refreshRate); refreshRate();
  }
  if (ap) ap.addEventListener('submit', function (e) {
    e.preventDefault(); var f = ap.elements;
    var g = guests(f);
    if (!g.total) return toast('Add at least one guest');
    var rate = advRate ? advRate() : null;
    var req = buildRequest([
      'Request: ' + ap.getAttribute('data-name'),
      rate ? 'Option: ' + rate.duration + ' \u00b7 ' + rate.vehicle : '',
      rate ? 'Rate: ' + money(rate.price) + ' ' + rate.unit + ', excluding taxes' : '',
      'Date: ' + (fmtDate(f.date.value) || 'flexible'),
      'Guests: ' + guestText(g),
      f.base ? 'Pickup area: ' + f.base.value : '',
      'Name: ' + f.name.value, 'Email: ' + f.email.value,
      f.phone.value ? 'Phone / WhatsApp: ' + f.phone.value : ''
    ].concat(stayLines(f), [
      'Transportation: ' + (f.transport.value || 'not needed'),
      f.notes.value ? 'Notes: ' + f.notes.value : ''
    ]), Object.assign({ kind: 'tour', trip: ap.getAttribute('data-name'), length: rate ? rate.duration + ' \u00b7 ' + rate.vehicle : '', rate: rate ? money(rate.price) + ' ' + rate.unit + ', excluding taxes' : '', base: f.base ? f.base.value : '', dateText: fmtDate(f.date.value), pax: g.total, adults: g.adults, kids: g.kids, name: f.name.value, email: f.email.value, phone: f.phone.value, transport: f.transport.value, notes: f.notes.value }, stayPayload(f)));
    showSent(ap, req, 'Your request is ready to send.');
  });

  // ---- CONTACT FORM --------------------------------------------------------
  var cf = $('#contact-form');
  if (cf) cf.addEventListener('submit', function (e) {
    e.preventDefault(); var f = cf.elements;
    var req = buildRequest(['Request: Message from ' + f.name.value, 'Name: ' + f.name.value, 'Email: ' + f.email.value, f.phone.value ? 'Phone: ' + f.phone.value : '', '', f.message.value],
      { kind: 'message', name: f.name.value, email: f.email.value, phone: f.phone.value, message: f.message.value });
    showSent(cf, req, 'Your message is ready to send.');
  });

  function showSent(form, req, title) {
    if (!CONFIG.endpoint || !req.data || !window.fetch) return showFallback(form, req, title);
    var btn = form.querySelector('button[type=submit]'), label = btn ? btn.textContent : '';
    if (btn) { btn.disabled = true; btn.textContent = 'Sending\u2026'; }
    var payload = Object.assign({ page: location.href, website: (form.elements.website && form.elements.website.value) || '' }, req.data);
    var ctrl = window.AbortController ? new AbortController() : null, timer = ctrl && setTimeout(function () { ctrl.abort(); }, 12000);
    fetch(CONFIG.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
      .then(function () { showConfirmed(form, req); })
      .catch(function () { showFallback(form, req, title, true); })
      .then(function () { if (timer) clearTimeout(timer); if (btn) { btn.disabled = false; btn.textContent = label; } });
  }
  function showConfirmed(form, req) {
    var wrap = form.parentNode, isMsg = req.data.kind === 'message';
    var div = document.createElement('div'); div.className = 'sent';
    div.innerHTML = '<div class="ok">&#10003;</div><h3>' + (isMsg ? 'Message sent.' : 'Request sent.') + '</h3>'
      + '<p class="muted" style="margin:8px 0 18px">A confirmation is on its way to <b>' + req.data.email.replace(/</g, '&lt;') + '</b>. Steve &amp; Liisa reply within hours' + (isMsg ? '.' : ', then send your payment options.') + '</p>'
      + '<div class="copybox">' + req.text.replace(/</g, '&lt;') + '</div>'
      + '<div class="alt" style="margin-top:14px"><a class="btn btn-ghost btn-sm" href="tel:' + CONFIG.phone.replace(/[^0-9+]/g, '') + '">Call ' + CONFIG.phone + '</a></div>';
    form.style.display = 'none'; wrap.appendChild(div);
    div.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  function showFallback(form, req, title, failed) {
    var wrap = form.parentNode;
    var div = document.createElement('div'); div.className = 'sent';
    div.innerHTML = '<div class="ok">&#10003;</div><h3>' + title + '</h3><p class="muted" style="margin:8px 0 18px">' + (failed ? 'Our sender is busy, so send it from your email app instead. ' : 'Send it by email and ') + 'Steve &amp; Liisa reply within hours.</p>'
      + '<a class="btn btn-primary btn-block" href="' + req.mailto + '">Send by email</a>'
      + (req.wa ? '<a class="btn btn-ghost btn-block" style="margin-top:8px" target="_blank" rel="noopener" href="' + req.wa + '">Send on WhatsApp</a>' : '')
      + '<div class="alt"><button type="button" class="btn btn-ghost btn-sm" data-copy>Copy details</button><a class="btn btn-ghost btn-sm" href="tel:' + CONFIG.phone.replace(/[^0-9+]/g, '') + '">Call ' + CONFIG.phone + '</a><a class="btn btn-ghost btn-sm" href="tel:' + CONFIG.phoneCR.replace(/[^0-9+]/g, '') + '">' + CONFIG.phoneCR + '</a></div>'
      + '<div class="copybox">' + req.text.replace(/</g, '&lt;') + '</div>';
    form.style.display = 'none'; wrap.appendChild(div);
    $('[data-copy]', div).addEventListener('click', function () { copy(req.text); });
    div.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  // ---- TRIP BUILDER (add to my trip + book.html) --------------------------
  var TRIP_KEY = 'gf_trip_v1';
  function tripBlank() {
    return { arrive: '', depart: '', adults: 2, kids: 0, items: [], name: '', email: '', phone: '', stay: '', stay_geo: '', stay_map: '', transport: '', notes: '' };
  }
  function tripLoad() {
    try { var t = JSON.parse(localStorage.getItem(TRIP_KEY) || 'null'); if (t && t.items) return t; } catch (e) { }
    return tripBlank();
  }
  function tripSave(t) { try { localStorage.setItem(TRIP_KEY, JSON.stringify(t)); } catch (e) { } paintTripCount(); }
  // The link is always there so people can find their trip; the badge only shows once something is in it.
  function paintTripCount() {
    var n = tripLoad().items.length;
    $$('.nav-trip, .drawer-trip').forEach(function (a) {
      a.classList.toggle('has-items', !!n);
      var s = a.querySelector('span');
      if (s) { s.hidden = !n; s.textContent = n; }
    });
  }
  function tripAdd(item) {
    var t = tripLoad();
    item.id = 'i' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    t.items.push(item); tripSave(t);
    toast(item.name + ' added to your trip');
  }
  paintTripCount();

  // ---- TRIP PLANNER WIZARD -------------------------------------------------
  var wz = $('#wizard');
  if (wz && window.FLEET) {
    var state = { type: '', base: '', arrive: '', depart: '', when: '', pax: 4, adults: 2, kids: 0, style: '', fish: [], boat: '', dur: 'half', adv: '' };
    function totalPax() { return (+state.adults || 0) + (+state.kids || 0); }
    function wizGuestText() { return guestText({ adults: +state.adults || 0, kids: +state.kids || 0 }); }
    try { var saved = JSON.parse(localStorage.getItem('gf_wizard') || 'null'); if (saved) state = Object.assign(state, saved); } catch (e) { }
    var qsw = new URLSearchParams(location.search);
    if (qsw.get('boat')) { state.type = 'fishing'; state.boat = qsw.get('boat'); var bb0 = window.FLEET[state.boat]; if (bb0) state.base = bb0.locations[0]; }
    if (qsw.get('adv')) { state.type = 'adventure'; state.adv = qsw.get('adv'); }
    if (qsw.get('type')) state.type = qsw.get('type');
    var step = 0, panes = $$('.pane', wz), prog = $$('.prog span', wz);
    var durLabel2 = { half: 'Half day (5 hrs)', tq: '3/4 day (7 hrs)', full: 'Full day (9 hrs)' };
    function save() { try { localStorage.setItem('gf_wizard', JSON.stringify(state)); } catch (e) { } }
    function go(n, noScroll) {
      step = Math.max(0, Math.min(panes.length - 1, n));
      panes.forEach(function (p, i) { p.classList.toggle('on', i === step); });
      prog.forEach(function (p, i) { p.classList.toggle('on', i === step); p.classList.toggle('done', i < step); });
      if (step === 2) renderPicks(); if (step === 3) renderSummary();
      if (!noScroll) wz.scrollIntoView({ behavior: 'smooth', block: 'start' }); save();
    }
    // step 1: type + base
    $$('input[name=type]', wz).forEach(function (i) { i.checked = i.value === state.type; i.addEventListener('change', function () { state.type = i.value; syncOpts(); }); });
    $$('input[name=base]', wz).forEach(function (i) { i.checked = i.value === state.base; i.addEventListener('change', function () { state.base = i.value; syncOpts(); }); });
    function syncOpts() { $$('.opt', wz).forEach(function (o) { o.classList.toggle('on', $('input', o).checked); }); }
    syncOpts();
    // step 2: date + pax
    var arriveI = $('#w-arrive', wz), departI = $('#w-depart', wz), adultsI = $('select[name=adults]', wz), kidsI = $('select[name=kids]', wz);
    var stored = tripLoad();
    if (!state.arrive && stored.arrive) state.arrive = stored.arrive;
    if (!state.depart && stored.depart) state.depart = stored.depart;
    if (state.arrive) arriveI.value = state.arrive;
    if (state.depart) departI.value = state.depart;
    if (adultsI) adultsI.value = state.adults; if (kidsI) kidsI.value = state.kids;
    function syncTripDates() { var t = tripLoad(); t.arrive = state.arrive; t.depart = state.depart; t.adults = state.adults; t.kids = state.kids; tripSave(t); }
    arriveI.addEventListener('change', function () { state.arrive = arriveI.value; departI.min = arriveI.value; if (departI.value && departI.value < arriveI.value) { departI.value = arriveI.value; state.depart = arriveI.value; } syncTripDates(); save(); });
    departI.addEventListener('change', function () { state.depart = departI.value; syncTripDates(); save(); });
    if (state.arrive) departI.min = state.arrive;
    if (adultsI) adultsI.addEventListener('change', function () { state.adults = +adultsI.value; syncTripDates(); save(); });
    if (kidsI) kidsI.addEventListener('change', function () { state.kids = +kidsI.value; syncTripDates(); save(); });
    // fishing style + target fish live in step 3, outside the step-4 form
    var styleG = $('[data-style]', wz), fishG = $('[data-fish]', wz);
    if (styleG) {
      var pre = styleG.querySelector('input[value="' + state.style + '"]'); if (pre) { pre.checked = true; syncChips(styleG); }
      styleG.addEventListener('change', function () { state.style = (styleG.querySelector('input:checked') || {}).value || ''; save(); });
    }
    if (fishG) {
      (state.fish || []).forEach(function (v) { var el = fishG.querySelector('input[value="' + v.replace(/"/g, '') + '"]'); if (el) el.checked = true; });
      syncChips(fishG);
      fishG.addEventListener('change', function () { state.fish = checkedValues(fishG, 'fish'); save(); });
    }
    function setFishRow(show) { var r = $('#fish-row'); if (r) r.style.display = show ? '' : 'none'; }
    // step 3: picks
    function renderPicks() {
      var box = $('#picks'), h = $('#picks-head');
      box.innerHTML = '';
      if (state.type === 'adventure') {
        h.innerHTML = '<h2>Pick an adventure</h2><p class="lead">Every tour includes a guide. Most include pickup in Tamarindo or Flamingo.</p>';
        Object.keys(window.ADV).forEach(function (k) {
          var a = window.ADV[k];
          box.insertAdjacentHTML('beforeend', '<label class="pick' + (state.adv === k ? ' on' : '') + '"><input type="radio" name="adv" value="' + k + '"><img src="' + ROOT + 'img/' + a.image + '" alt=""><div class="b"><b>' + a.name + '</b><span class="muted small">' + a.tag + '</span>' + (a.from ? '<div class="p">' + a.from + ' <small>per person</small></div>' : '<div class="p">Ask <small>for rates</small></div>') + '</div></label>');
        });
        $$('input[name=adv]', box).forEach(function (i) { i.addEventListener('change', function () { state.adv = i.value; state.boat = ''; $$('.pick', box).forEach(function (p) { p.classList.toggle('on', $('input', p).checked); }); }); });
        $('#dur-row').style.display = 'none'; setFishRow(false);
        return;
      }
      var cat = state.type === 'catamaran';
      h.innerHTML = cat ? '<h2>Private catamarans</h2><p class="lead">Morning or sunset sails, priced by request. Pick one and we quote within hours.</p>'
        : '<h2>Boats that fit your group</h2><p class="lead">Showing ' + (state.base || 'Tamarindo &amp; Flamingo') + ' boats that take ' + totalPax() + (totalPax() > 1 ? ' guests' : ' guest') + '. Every boat is one we know personally.</p>';
      var list = Object.keys(window.FLEET).map(function (k) { return window.FLEET[k]; }).filter(function (b) {
        if (cat !== !!b.quote) return false;
        if (state.base && b.locations.indexOf(state.base) < 0) return false;
        if (!cat && b.max_pax < totalPax()) return false;
        return true;
      }).sort(function (a, b) { return (a.half || 0) - (b.half || 0); });
      if (!list.length) { box.innerHTML = '<div class="empty" style="grid-column:1/-1">No single boat takes ' + totalPax() + ' guests in ' + state.base + '. With a group this size two boats is usually the better day anyway: more room to work and more lines in the water. Email us and we will pair the right two.</div>'; }
      list.forEach(function (b) {
        box.insertAdjacentHTML('beforeend', '<label class="pick' + (state.boat === b.slug ? ' on' : '') + '"><input type="radio" name="boat" value="' + b.slug + '">' + (b.top ? '<span class="tb">' + b.top_label + '</span>' : '') + '<img src="' + ROOT + 'img/' + b.images[0] + '" alt=""><div class="b"><b>' + b.name + '</b><span class="muted small">' + b.locations.join(' · ') + ' · up to ' + (b.max_pax || 'group') + (b.max_pax ? ' guests' : '') + (b.washroom ? ' · washroom' : '') + '</span>' + (b.half ? '<div class="p">' + money(b.half) + ' <small>half day · per boat</small></div>' : '<div class="p">Quote <small>on request</small></div>') + '</div></label>');
      });
      $$('input[name=boat]', box).forEach(function (i) { i.addEventListener('change', function () { state.boat = i.value; state.adv = ''; $$('.pick', box).forEach(function (p) { p.classList.toggle('on', $('input', p).checked); }); }); });
      $('#dur-row').style.display = cat ? 'none' : ''; setFishRow(!cat);
      $$('input[name=dur]', wz).forEach(function (i) { i.checked = i.value === state.dur; i.addEventListener('change', function () { state.dur = i.value; $$('#dur-row .seg label').forEach(function (l) { l.classList.toggle('on', $('input', l).checked); }); autoStyle(wz, state.dur); state.style = (($('[data-style] input:checked', wz)) || {}).value || ''; save(); }); });
      $$('#dur-row .seg label').forEach(function (l) { l.classList.toggle('on', $('input', l).checked); });
    }
    function chosen() {
      if (state.type === 'adventure') { var a = window.ADV[state.adv]; return a ? { name: a.name, price: a.from ? a.from + ' per person' : 'rates on request', est: '' } : null; }
      var b = window.FLEET[state.boat]; if (!b) return null;
      var p = { half: b.half, tq: b.three_quarter, full: b.full }[state.dur];
      return { name: b.name, price: p ? money(p) + ' per boat · ' + durLabel2[state.dur] : 'custom quote', est: p ? money(p) : 'Quote', boat: b };
    }
    function renderSummary() {
      var c = chosen(), s = $('#summary');
      if (!c) { s.innerHTML = '<div class="empty">Go back and pick a boat or adventure first.</div>'; paintDayPicker(); paintWizTrip(); return; }
      paintDayPicker(); paintWizTrip();
      s.innerHTML = '<dl><dt>Trip</dt><dd>' + c.name + '</dd><dt>Base</dt><dd>' + (state.base || 'Either') + '</dd><dt>Your dates</dt><dd>' + ((state.arrive && state.depart) ? fmtDate(state.arrive) + ' \u2013 ' + fmtDate(state.depart) : 'Flexible') + '</dd><dt>Guests</dt><dd>' + wizGuestText() + '</dd>' + ((state.type !== 'adventure' && state.style) ? '<dt>Fishing</dt><dd>' + state.style + '</dd>' : '') + ((state.type !== 'adventure' && state.fish && state.fish.length) ? '<dt>Target</dt><dd>' + state.fish.join(', ') + '</dd>' : '') + (state.type !== 'adventure' && !c.boat.quote ? '<dt>Length</dt><dd>' + durLabel2[state.dur] + '</dd>' : '') + '</dl>'
        + '<div class="tot"><span class="muted small">' + (c.est ? (state.type === 'adventure' ? 'Estimated total' : 'Estimated total, excluding taxes') : '') + '</span><b>' + (c.est || c.price) + '</b></div>'
        + (c.est && c.est !== 'Quote' ? '<div class="muted small" style="margin-top:6px">Per boat, all gear, bait, drinks' + (state.dur !== 'half' ? ' and light lunch' : '') + ' included. Taxes, fishing licences and crew tips are not included.</div>' : '');
    }
    // --- multi-activity: day picker, add-another, running list ---------------
    function wizDays() {
      var out = [];
      if (!state.arrive || !state.depart) return out;
      var d = new Date(state.arrive + 'T12:00:00'), end = new Date(state.depart + 'T12:00:00');
      for (var i = 0; i < 40 && d <= end; i++) {
        out.push({ iso: d.toISOString().slice(0, 10), label: d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) });
        d.setDate(d.getDate() + 1);
      }
      return out;
    }
    var daySel = $('#w-when'), dayWrap = $('#wiz-day'), wizTrip = $('#wiz-trip'), addBtn = $('#wiz-add'), sendBtn = $('#wiz-send');
    function paintDayPicker() {
      if (!daySel) return;
      var days = wizDays();
      dayWrap.style.display = days.length ? '' : 'none';
      daySel.innerHTML = '<option value="">Any day that works</option>' + days.map(function (d) {
        return '<option value="' + d.iso + '"' + (state.when === d.iso ? ' selected' : '') + '>' + d.label + '</option>';
      }).join('');
    }
    if (daySel) daySel.addEventListener('change', function () { state.when = daySel.value; save(); });

    function currentItem() {
      var c = chosen(); if (!c) return null;
      var days = {}; wizDays().forEach(function (d) { days[d.iso] = d.label; });
      var isAdv = state.type === 'adventure';
      var src = isAdv ? (window.ADV || {})[state.adv] : (window.FLEET || {})[state.boat];
      var bits = [];
      if (!isAdv && c.boat && !c.boat.quote) bits.push(durLabel2[state.dur]);
      if (!isAdv && state.style) bits.push(state.style);
      if (!isAdv && state.fish && state.fish.length) bits.push(state.fish.join(', '));
      if (isAdv && src && src.tag) bits.push(src.tag);
      return {
        kind: isAdv ? 'tour' : 'boat', slug: isAdv ? state.adv : state.boat, name: c.name,
        image: isAdv ? (src && src.image) : (src && src.images && src.images[0]),
        base: state.base, detail: bits.join(' · '), rate: c.price, price: (c.est && c.est !== 'Quote') ? (({ half: (c.boat || {}).half, tq: (c.boat || {}).three_quarter, full: (c.boat || {}).full })[state.dur] || 0) : 0,
        when: state.when, whenLabel: state.when ? (days[state.when] || state.when) : 'Any day that works'
      };
    }
    function resetPick() {
      state.boat = ''; state.adv = ''; state.when = ''; state.fish = [];
      $$('input[name=boat], input[name=adv]', wz).forEach(function (i) { i.checked = false; });
      var fg = $('[data-fish]', wz); if (fg) { $$('input', fg).forEach(function (i) { i.checked = false; }); syncChips(fg); }
      save();
    }
    function paintWizTrip() {
      if (!wizTrip) return;
      var items = tripLoad().items;
      if (!items.length) { wizTrip.innerHTML = ''; if (sendBtn) sendBtn.textContent = 'Send my request'; return; }
      var total = 0, allPriced = true;
      var rows = items.map(function (it, n) {
        if (it.price) total += it.price; else allPriced = false;
        return '<div class="trip-item" data-id="' + it.id + '">'
          + '<img src="' + ROOT + 'img/' + (it.image || '') + '" alt="">'
          + '<div><h3>' + wesc(it.name) + '</h3><div class="meta">' + wesc([it.detail, it.base].filter(Boolean).join(' · ')) + '</div>'
          + '<div class="meta" style="color:var(--sea);font-weight:600;margin-top:3px">' + wesc(it.whenLabel || 'Any day that works') + '</div>'
          + '<button type="button" class="rm" data-rm>Remove</button></div>'
          + '<div class="price">' + (it.price ? money(it.price) : 'Quote') + '</div></div>';
      }).join('');
      wizTrip.innerHTML = '<div class="sec-head" style="margin:26px 0 12px"><div class="kicker">Already in your trip</div>'
        + '<h2 style="font-size:24px">' + items.length + ' other day' + (items.length > 1 ? 's' : '') + ' planned</h2></div>' + rows
        + '<div class="trip-total"><span class="t">Plus the one above</span><span style="text-align:right"><b>' + (total ? money(total) : 'Quote') + '</b>'
        + '<small class="muted small" style="display:block">' + (allPriced ? 'Added so far, excluding taxes' : 'Added so far, some quoted on request') + '</small></span></div>';
      if (sendBtn) sendBtn.textContent = 'Send my trip';
    }
    function wesc(x) { return String(x == null ? '' : x).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
    if (wizTrip) wizTrip.addEventListener('click', function (e) {
      var rm = e.target.closest('[data-rm]'); if (!rm) return;
      var id = rm.closest('.trip-item').getAttribute('data-id');
      var t = tripLoad(); t.items = t.items.filter(function (i) { return i.id !== id; }); tripSave(t);
      paintWizTrip();
    });
    if (addBtn) addBtn.addEventListener('click', function () {
      var item = currentItem();
      if (!item) return toast('Pick a boat or an adventure first');
      var t = tripLoad();
      item.id = 'i' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5);
      t.items.push(item); t.arrive = state.arrive; t.depart = state.depart; t.adults = state.adults; t.kids = state.kids;
      tripSave(t);
      toast(item.name + ' added. Plan the next one.');
      resetPick(); go(0);
    });

    $$('[data-next]', wz).forEach(function (b) { b.addEventListener('click', function () {
      if (step === 0 && !state.type) return toast('Pick what kind of day you want');
      if (step === 0 && !state.base && state.type !== 'adventure') return toast('Pick a base: Tamarindo or Flamingo');
      if (step === 2 && !state.boat && !state.adv) return toast('Pick one to continue');
      go(step + 1);
    }); });
    $$('[data-prev]', wz).forEach(function (b) { b.addEventListener('click', function () { go(step - 1); }); });
    $('#wiz-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var f = e.target.elements;
      // everything already added, plus whatever is on screen right now
      var stored = tripLoad(), items = (stored.items || []).slice();
      var now = currentItem(); if (now) items.push(now);
      if (!items.length) { toast('Pick a boat or an adventure first'); return go(2); }
      var dates = (state.arrive && state.depart) ? fmtDate(state.arrive) + ' \u2013 ' + fmtDate(state.depart) : '';
      var single = items.length === 1 ? items[0] : null;

      var head = single
        ? ['Request: ' + single.name + (single.base ? ' (' + single.base + ')' : ''),
           single.detail ? 'Details: ' + single.detail : '',
           single.rate ? 'Rate: ' + single.rate : '',
           'Preferred day: ' + (single.whenLabel || 'any day that works')]
        : ['Request: Whole trip, ' + items.length + ' activities'];
      var lines = head.concat([
        dates ? 'Dates: ' + dates : 'Dates: flexible',
        'Guests: ' + wizGuestText(), ''
      ]);
      if (!single) items.forEach(function (i, n) {
        lines.push((n + 1) + '. ' + i.name + ' \u2014 ' + [i.detail, i.base].filter(Boolean).join(' \u00b7 ') + ' \u2014 ' + (i.rate || 'quote') + ' \u2014 ' + (i.whenLabel || 'Any day'));
      });
      lines = lines.concat(['', 'Name: ' + f.name.value, 'Email: ' + f.email.value,
        f.phone.value ? 'Phone / WhatsApp: ' + f.phone.value : ''
      ], stayLines(f), [
        'Transportation: ' + (f.transport.value || 'not needed'),
        f.notes.value ? 'Notes: ' + f.notes.value : ''
      ]);

      var common = { dateText: dates || 'Flexible', arrive: state.arrive, depart: state.depart,
        pax: totalPax(), adults: state.adults, kids: state.kids,
        name: f.name.value, email: f.email.value, phone: f.phone.value,
        transport: f.transport.value, notes: f.notes.value };
      var data = single
        ? Object.assign({ kind: single.kind, trip: single.name, base: single.base, length: single.detail,
            rate: single.rate, style: state.style, fish: (state.fish || []).join(', ') }, common)
        : Object.assign({ kind: 'trip', trip: items.length + ' activities',
            items: items.map(function (i) { return { name: i.name, kind: i.kind, detail: [i.detail, i.base].filter(Boolean).join(' \u00b7 '), rate: i.rate || 'quote on request', when: i.whenLabel || 'Any day' }; }) }, common);

      showSent(e.target, req_or(buildRequest(lines, Object.assign({}, data, stayPayload(f)))), single ? 'Your request is ready.' : 'Your trip is ready to send.');
      try { localStorage.removeItem('gf_wizard'); localStorage.removeItem(TRIP_KEY); } catch (x) { }
      paintTripCount();
    });
    function req_or(x) { return x; }
    go(qsw.get('boat') || qsw.get('adv') ? 1 : 0, true);
  }

  // add-to-trip: boat page
  if (bp && window.BOAT) {
    var addBoat = bp.querySelector('[data-add-trip]');
    if (addBoat) addBoat.addEventListener('click', function () {
      var f = bp.elements, d = f.dur ? f.dur.value : 'half', g = guests(f);
      if (B.max_pax && g.total > B.max_pax) return toast('This boat takes up to ' + B.max_pax + ' guests.');
      var style = (f.style && f.style.value) || '', fish = checkedValues(bp, 'fish');
      var bits = [durLabel[d]]; if (style) bits.push(style); if (fish.length) bits.push(fish.join(', '));
      tripAdd({
        kind: 'boat', slug: B.slug, name: B.name, image: B.image, base: B.locations.join(' / '),
        detail: bits.join(' · '), rate: price[d] ? money(price[d]) + ' per boat, excluding taxes' : 'custom quote',
        price: price[d] || 0, when: ''
      });
    });
  }

  // add-to-trip: adventure page
  if (ap) {
    var addAdv = ap.querySelector('[data-add-trip]');
    if (addAdv) addAdv.addEventListener('click', function () {
      var f = ap.elements, rate = advRate ? advRate() : null;
      tripAdd({
        kind: 'tour', slug: ap.getAttribute('data-slug'), name: ap.getAttribute('data-name'), image: ap.getAttribute('data-image'),
        base: f.base ? f.base.value : '',
        detail: rate ? rate.duration + ' · ' + rate.vehicle : (ap.getAttribute('data-tag') || ''),
        rate: rate ? money(rate.price) + ' ' + rate.unit + ', excluding taxes' : '',
        price: rate ? rate.price : 0, when: ''
      });
    });
  }

  // ---- the trip page itself ------------------------------------------------
  var tripRoot = $('#trip');
  if (tripRoot) {
    var T = tripLoad();
    var arriveI = $('#t-arrive'), departI = $('#t-depart'), tAdults = $('#t-adults'), tKids = $('#t-kids');
    var itemsBox = $('#trip-items'), form = $('#trip-form');

    // deep links: /trip.html?boat=slug or ?adv=slug drop straight into the list
    var q = new URLSearchParams(location.search);
    if (q.get('boat') && window.FLEET && window.FLEET[q.get('boat')]) {
      var b0 = window.FLEET[q.get('boat')];
      if (!T.items.some(function (i) { return i.slug === b0.slug; })) {
        T.items.push({ id: 'i' + Date.now().toString(36), kind: 'boat', slug: b0.slug, name: b0.name, image: b0.images[0],
          base: b0.locations.join(' / '), detail: '5 hours · inshore', rate: b0.half ? money(b0.half) + ' per boat, excluding taxes' : 'custom quote', price: b0.half || 0, when: '' });
      }
    }
    if (q.get('adv') && window.ADV && window.ADV[q.get('adv')]) {
      var a0 = window.ADV[q.get('adv')];
      if (!T.items.some(function (i) { return i.slug === q.get('adv'); })) {
        T.items.push({ id: 'i' + Date.now().toString(36) + 'a', kind: 'tour', slug: q.get('adv'), name: a0.name, image: a0.image,
          base: '', detail: a0.tag || '', rate: a0.from ? a0.from + ' per person' : '', price: 0, when: '' });
      }
    }
    if (q.get('boat') || q.get('adv')) { tripSave(T); history.replaceState(null, '', location.pathname); }

    // restore what they filled in last time
    if (T.arrive) arriveI.value = T.arrive;
    if (T.depart) departI.value = T.depart;
    if (tAdults) tAdults.value = T.adults; if (tKids) tKids.value = T.kids;
    ['name', 'email', 'phone', 'stay', 'transport', 'notes'].forEach(function (k) { if (form.elements[k] && T[k]) form.elements[k].value = T[k]; });
    if (T.stay_geo && form.elements.stay_geo) form.elements.stay_geo.value = T.stay_geo;
    if (T.stay_map && form.elements.stay_map) form.elements.stay_map.value = T.stay_map;

    function stash() {
      T.arrive = arriveI.value; T.depart = departI.value;
      T.adults = +tAdults.value || 0; T.kids = +tKids.value || 0;
      ['name', 'email', 'phone', 'stay', 'stay_geo', 'stay_map', 'transport', 'notes'].forEach(function (k) { if (form.elements[k]) T[k] = form.elements[k].value; });
      tripSave(T);
    }
    tripRoot.addEventListener('change', function () { stash(); if (this._d) return; });
    arriveI.addEventListener('change', function () { if (departI.value && departI.value < arriveI.value) departI.value = arriveI.value; departI.min = arriveI.value; render(); });
    departI.addEventListener('change', render);

    // every date of the stay, so each activity can be pinned to a day
    function stayDays() {
      var out = [];
      if (!T.arrive || !T.depart) return out;
      var d = new Date(T.arrive + 'T12:00:00'), end = new Date(T.depart + 'T12:00:00');
      for (var i = 0; i < 40 && d <= end; i++) {
        out.push({ iso: d.toISOString().slice(0, 10), label: d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) });
        d.setDate(d.getDate() + 1);
      }
      return out;
    }

    function render() {
      T.arrive = arriveI.value; T.depart = departI.value;
      var days = stayDays();
      if (!T.items.length) {
        itemsBox.innerHTML = '<div class="trip-empty"><b>Nothing in your trip yet.</b>Browse the boats and the tours, and hit <em>Add to my trip</em> on anything you like. It all lands here.</div>';
        tripSave(T); return;
      }
      var html = '', total = 0, allPriced = true;
      T.items.forEach(function (it) {
        if (it.price) total += it.price; else allPriced = false;
        var opts = '<option value="">Any day that works</option>' + days.map(function (d) {
          return '<option value="' + d.iso + '"' + (it.when === d.iso ? ' selected' : '') + '>' + d.label + '</option>';
        }).join('');
        html += '<div class="trip-item" data-id="' + it.id + '">'
          + '<img src="' + ROOT + 'img/' + (it.image || '') + '" alt="">'
          + '<div><h3>' + esc(it.name) + '</h3><div class="meta">' + esc([it.detail, it.base].filter(Boolean).join(' · ')) + '</div>'
          + '<div class="when"><label for="w-' + it.id + '">Preferred day</label><select id="w-' + it.id + '" data-when>' + opts + '</select></div>'
          + '<button type="button" class="rm" data-rm>Remove</button></div>'
          + '<div class="price">' + (it.price ? money(it.price) : 'Quote') + '<small>' + esc(it.rate || 'we will quote it') + '</small></div>'
          + '</div>';
      });
      html += '<div class="trip-total"><span class="t">' + T.items.length + ' item' + (T.items.length > 1 ? 's' : '')
        + (days.length ? ' · ' + days.length + ' day' + (days.length > 1 ? 's' : '') + ' here' : '')
        + '</span><span style="text-align:right"><b>' + (total ? money(total) : 'Quote') + '</b>'
        + '<small class="muted small" style="display:block">' + (allPriced ? 'Estimated total, excluding taxes' : 'Estimate so far, some items quoted on request') + '</small></span></div>';
      itemsBox.innerHTML = html;
      if (!days.length) $$('[data-when]', itemsBox).forEach(function (s) { s.disabled = true; s.title = 'Add your dates first'; });
      tripSave(T);
    }
    function esc(x) { return String(x == null ? '' : x).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

    itemsBox.addEventListener('click', function (e) {
      var rm = e.target.closest('[data-rm]'); if (!rm) return;
      var id = rm.closest('.trip-item').getAttribute('data-id');
      T.items = T.items.filter(function (i) { return i.id !== id; });
      render();
    });
    itemsBox.addEventListener('change', function (e) {
      var sel = e.target.closest('[data-when]'); if (!sel) return;
      var id = sel.closest('.trip-item').getAttribute('data-id');
      T.items.forEach(function (i) { if (i.id === id) i.when = sel.value; });
      tripSave(T);
    });

    if (arriveI.value) departI.min = arriveI.value;
    render();

    form.addEventListener('submit', function (e) {
      e.preventDefault(); stash();
      if (!T.items.length) { toast('Add a boat or a tour first'); return window.scrollTo({ top: itemsBox.offsetTop - 120, behavior: 'smooth' }); }
      if (!T.arrive || !T.depart) { toast('Tell us your arrival and departure'); arriveI.focus(); return; }
      var f = form.elements, g = { adults: +tAdults.value || 0, kids: +tKids.value || 0 };
      g.total = g.adults + g.kids;
      if (!g.total) return toast('Add at least one guest');
      var dayLabel = {}; stayDays().forEach(function (d) { dayLabel[d.iso] = d.label; });
      var payloadItems = T.items.map(function (i) {
        return { name: i.name, kind: i.kind, detail: [i.detail, i.base].filter(Boolean).join(' · '), rate: i.rate || 'quote on request', when: i.when ? dayLabel[i.when] || i.when : 'Any day' };
      });
      var dates = fmtDate(T.arrive) + ' – ' + fmtDate(T.depart);
      var lines = ['Request: Whole trip, ' + T.items.length + ' item' + (T.items.length > 1 ? 's' : ''), 'Dates: ' + dates, 'Guests: ' + guestText(g), ''];
      payloadItems.forEach(function (i, n) { lines.push((n + 1) + '. ' + i.name + ' — ' + i.detail + ' — ' + i.rate + ' — ' + i.when); });
      lines.push('', 'Name: ' + f.name.value, 'Email: ' + f.email.value);
      if (f.phone.value) lines.push('Phone / WhatsApp: ' + f.phone.value);
      lines = lines.concat(stayLines(f), ['Transportation: ' + (f.transport.value || 'not needed'), f.notes.value ? 'Notes: ' + f.notes.value : '']);
      var req = buildRequest(lines, Object.assign({
        kind: 'trip', trip: T.items.length + ' item trip', items: payloadItems,
        arrive: T.arrive, depart: T.depart, dateText: dates,
        pax: g.total, adults: g.adults, kids: g.kids,
        name: f.name.value, email: f.email.value, phone: f.phone.value,
        transport: f.transport.value, notes: f.notes.value
      }, stayPayload(f)));
      showSent(form, req, 'Your trip is ready to send.');
      try { localStorage.removeItem(TRIP_KEY); } catch (x) { }
      paintTripCount();
    });
  }

  // ---- MOBILE BOOK BAR -----------------------------------------------------
  var bar = $('.bookbar');
  if (bar) { document.body.classList.add('has-bookbar'); var t = $('#boat-book') || $('#adv-book'); if (t) { var io2 = new IntersectionObserver(function (es) { bar.classList.toggle('show', !es[0].isIntersecting); }); io2.observe(t); } else bar.classList.add('show'); }

  // ---- INSTAGRAM (Behold.so) -----------------------------------------------
  var ig = $('#ig-feed');
  if (ig && CONFIG.behold) {
    var sc = document.createElement('script'); sc.type = 'module'; sc.src = 'https://w.behold.so/widget.js'; document.head.appendChild(sc);
    ig.innerHTML = '<behold-widget feed-id="' + CONFIG.behold + '"></behold-widget>';
    var fb = $('#ig-fallback'); if (fb) fb.style.display = 'none';
  }

  // ---- HIDE WHATSAPP LINKS IF NOT CONFIGURED -------------------------------
  if (!CONFIG.whatsapp) $$('[data-wa]').forEach(function (a) { a.style.display = 'none'; });
  else $$('[data-wa]').forEach(function (a) { a.href = 'https://wa.me/' + CONFIG.whatsapp; });
})();

/* ---- THE DAY (home): sky, clock, rail, scrub, fleet rail ---- */
(function () {
  var day = document.getElementById('day'); if (!day) return;
  var chapters = JSON.parse(day.getAttribute('data-chapters') || '[]');
  var els = chapters.map(function (c) { return document.getElementById(c.id); });
  var nav = document.querySelector('nav.top'), clock = document.querySelector('.nav-clock'), rail = document.querySelector('.rail');
  var railLinks = rail ? Array.prototype.slice.call(rail.querySelectorAll('a')) : [];
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cur = -1;
  function setChapter(i) {
    if (i === cur) return; cur = i; var c = chapters[i];
    document.body.style.setProperty('--sky', c.sky);
    if (nav) nav.classList.toggle('over-photo', !!c.photo);
    if (clock) { clock.textContent = c.clock; clock.classList.toggle('on', i > 0 && c.id !== 'plan'); }
    if (rail) { rail.classList.toggle('on', i > 0 && c.id !== 'plan'); rail.classList.toggle('photo', !!c.photo); railLinks.forEach(function (a) { a.classList.toggle('on', a.getAttribute('data-ch') === c.id); }); }
  }
  function tick() {
    var mid = window.innerHeight * 0.45, best = 0;
    for (var i = 0; i < els.length; i++) { if (!els[i]) continue; var r = els[i].getBoundingClientRect(); if (r.top <= mid) best = i; }
    setChapter(best);
    // photo reveal for split chapters
    document.querySelectorAll('.chapter .ph').forEach(function (p) { var r = p.getBoundingClientRect(); if (r.top < window.innerHeight * 0.9) p.classList.add('in'); });
    scrub();
  }
  // lazy video sources: only load when near
  var vids = Array.prototype.slice.call(document.querySelectorAll('.media video[data-src]'));
  if (!reduce && 'IntersectionObserver' in window) {
    var vio = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { var v = e.target; v.muted = true; if (!v.src) { v.src = v.getAttribute('data-src'); v.load(); } v.play().catch(function () { }); vio.unobserve(v); } }); }, { rootMargin: '60% 0px' });
    vids.forEach(function (v) { vio.observe(v); });
  }
  // scroll scrub: Playa Grande frames drawn to canvas by chapter progress
  var cv = document.getElementById('scrub'), ctx = cv && cv.getContext('2d'), frames = [], loaded = 0, count = cv ? +cv.getAttribute('data-count') : 0, base = cv && cv.getAttribute('data-frames'), lastIdx = -1;
  if (cv && !reduce) {
    var first = new Image(); first.src = base + '001.jpg'; first.onload = function () { frames[0] = first; draw(0); };
    var started = false;
    function preload() { if (started) return; started = true; for (var i = 2; i <= count; i++) (function (i) { var im = new Image(); im.src = base + ('00' + i).slice(-3) + '.jpg'; im.onload = function () { frames[i - 1] = im; loaded++; }; })(i); }
    var pio = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { preload(); pio.disconnect(); } }, { rootMargin: '120% 0px' });
    pio.observe(cv);
    function draw(i) { var im = frames[i]; if (!im) { for (var j = i; j >= 0; j--) if (frames[j]) { im = frames[j]; break; } } if (!im) return; var cw = cv.width, ch = cv.height, s = Math.max(cw / im.width, ch / im.height), w = im.width * s, h = im.height * s; ctx.drawImage(im, (cw - w) / 2, (ch - h) / 2, w, h); }
  } else if (cv) { cv.style.display = 'none'; var po = cv.parentNode.querySelector('img.poster'); if (po) po.style.display = 'block'; }
  function scrub() {
    if (!cv || reduce) return; var sec = cv.closest('.chapter'); var r = sec.getBoundingClientRect(); var span = r.height + window.innerHeight; var p = (window.innerHeight - r.top) / span; p = Math.max(0, Math.min(1, p));
    var idx = Math.round(p * (count - 1)); if (idx !== lastIdx) { lastIdx = idx; draw(idx); }
  }
  // fleet rail arrows
  var fr = document.getElementById('fleet-rail');
  document.querySelectorAll('[data-rail]').forEach(function (b) { b.addEventListener('click', function () { var card = fr.querySelector('.boat'); fr.scrollBy({ left: (card ? card.offsetWidth + 16 : 360) * +b.getAttribute('data-rail'), behavior: 'smooth' }); }); });
  var raf = false;
  window.addEventListener('scroll', function () { if (!raf) { raf = true; requestAnimationFrame(function () { raf = false; tick(); }); } }, { passive: true });
  window.addEventListener('resize', tick); tick();
})();
