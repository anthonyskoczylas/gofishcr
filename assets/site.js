/* Go Fish Costa Rica — site behaviour */
(function () {
  'use strict';

  // ---- CONFIG (edit here only) -------------------------------------------
  // WhatsApp: leave empty ('') to hide the WhatsApp buttons. Format: country code + number, digits only.
  var CONFIG = {
    email: 'gofishcr@gmail.com',
    phone: '1-888-434-7491',
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

  // ---- REQUEST HELPERS (static site: email / WhatsApp / phone) ------------
  function buildRequest(lines) {
    var body = lines.filter(Boolean).join('\n');
    return {
      text: body,
      mailto: 'mailto:' + CONFIG.email + '?subject=' + encodeURIComponent(lines[0].replace(/^Request: /, '') + ' — booking request') + '&body=' + encodeURIComponent(body + '\n\nSent from gofishcr.com'),
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
    var durLabel = { half: '1/2 day · 5 hrs · 7am–12pm', tq: '3/4 day · 6+ hrs · 7am–2pm', full: 'Full day · 8+ hrs · 7am–4pm' };
    var price = { half: B.half, tq: B.three_quarter, full: B.full };
    function refresh() {
      $$('.seg label', bp).forEach(function (l) { l.classList.toggle('on', $('input', l).checked); });
      var d = (bp.elements.dur && bp.elements.dur.value) || 'half';
      var est = $('#est'); if (est) { est.querySelector('b').textContent = price[d] ? money(price[d]) : 'Quote'; est.querySelector('small').textContent = price[d] ? 'per boat · ' + durLabel[d] : 'custom quote for private catamarans'; }
      var bb = $('.bookbar b'); if (bb) bb.textContent = price[d] ? money(price[d]) : 'Quote';
    }
    bp.addEventListener('change', refresh); refresh();
    var qs2 = new URLSearchParams(location.search);
    if (qs2.get('date') && bp.elements.date) bp.elements.date.value = qs2.get('date');
    if (qs2.get('pax') && bp.elements.pax) bp.elements.pax.value = Math.min(+qs2.get('pax'), B.max_pax || 20);
    bp.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = bp.elements, d = f.dur ? f.dur.value : 'half';
      var req = buildRequest([
        'Request: ' + B.name + ' (' + B.locations.join(' / ') + ')',
        'Charter length: ' + durLabel[d] + (price[d] ? ' — ' + money(price[d]) + ' per boat' : ' — custom quote'),
        'Date: ' + (fmtDate(f.date.value) || 'flexible'),
        'Guests: ' + f.pax.value,
        'Name: ' + f.name.value,
        'Email: ' + f.email.value,
        f.phone.value ? 'Phone / WhatsApp: ' + f.phone.value : '',
        'Transportation: ' + (f.transport.value || 'not needed'),
        f.notes.value ? 'Notes: ' + f.notes.value : ''
      ]);
      showSent(bp, req, 'Your request for the ' + B.name + ' is ready to send.');
    });
  }

  // ---- ADVENTURE / GENERIC REQUEST PANEL ----------------------------------
  var ap = $('#adv-book');
  if (ap) ap.addEventListener('submit', function (e) {
    e.preventDefault(); var f = ap.elements;
    var req = buildRequest([
      'Request: ' + ap.getAttribute('data-name'),
      'Date: ' + (fmtDate(f.date.value) || 'flexible'),
      'Guests: ' + f.pax.value,
      f.base ? 'Pickup area: ' + f.base.value : '',
      'Name: ' + f.name.value, 'Email: ' + f.email.value,
      f.phone.value ? 'Phone / WhatsApp: ' + f.phone.value : '',
      'Transportation: ' + (f.transport.value || 'not needed'),
      f.notes.value ? 'Notes: ' + f.notes.value : ''
    ]);
    showSent(ap, req, 'Your request is ready to send.');
  });

  // ---- CONTACT FORM --------------------------------------------------------
  var cf = $('#contact-form');
  if (cf) cf.addEventListener('submit', function (e) {
    e.preventDefault(); var f = cf.elements;
    var req = buildRequest(['Request: Message from ' + f.name.value, 'Name: ' + f.name.value, 'Email: ' + f.email.value, f.phone.value ? 'Phone: ' + f.phone.value : '', '', f.message.value]);
    showSent(cf, req, 'Your message is ready to send.');
  });

  function showSent(form, req, title) {
    var wrap = form.parentNode;
    var div = document.createElement('div'); div.className = 'sent';
    div.innerHTML = '<div class="ok">&#10003;</div><h3>' + title + '</h3><p class="muted" style="margin:8px 0 18px">Send it by email and Steve &amp; Liisa reply within hours.</p>'
      + '<a class="btn btn-primary btn-block" href="' + req.mailto + '">Send by email</a>'
      + (req.wa ? '<a class="btn btn-ghost btn-block" style="margin-top:8px" target="_blank" rel="noopener" href="' + req.wa + '">Send on WhatsApp</a>' : '')
      + '<div class="alt"><button type="button" class="btn btn-ghost btn-sm" data-copy>Copy details</button><a class="btn btn-ghost btn-sm" href="tel:' + CONFIG.phone.replace(/[^0-9+]/g, '') + '">Call ' + CONFIG.phone + '</a></div>'
      + '<div class="copybox">' + req.text.replace(/</g, '&lt;') + '</div>';
    form.style.display = 'none'; wrap.appendChild(div);
    $('[data-copy]', div).addEventListener('click', function () { copy(req.text); });
    div.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  // ---- TRIP PLANNER WIZARD -------------------------------------------------
  var wz = $('#wizard');
  if (wz && window.FLEET) {
    var state = { type: '', base: '', date: '', pax: 4, boat: '', dur: 'half', adv: '' };
    try { var saved = JSON.parse(localStorage.getItem('gf_wizard') || 'null'); if (saved) state = Object.assign(state, saved); } catch (e) { }
    var qsw = new URLSearchParams(location.search);
    if (qsw.get('boat')) { state.type = 'fishing'; state.boat = qsw.get('boat'); var bb0 = window.FLEET[state.boat]; if (bb0) state.base = bb0.locations[0]; }
    if (qsw.get('adv')) { state.type = 'adventure'; state.adv = qsw.get('adv'); }
    if (qsw.get('type')) state.type = qsw.get('type');
    var step = 0, panes = $$('.pane', wz), prog = $$('.prog span', wz);
    var durLabel2 = { half: '1/2 day (5 hrs)', tq: '3/4 day (6+ hrs)', full: 'Full day (8+ hrs)' };
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
    var dateI = $('input[name=date]', wz), paxI = $('select[name=pax]', wz);
    if (state.date) dateI.value = state.date; paxI.value = state.pax;
    dateI.addEventListener('change', function () { state.date = dateI.value; });
    paxI.addEventListener('change', function () { state.pax = +paxI.value; });
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
        $('#dur-row').style.display = 'none';
        return;
      }
      var cat = state.type === 'catamaran';
      h.innerHTML = cat ? '<h2>Private catamarans</h2><p class="lead">Morning or sunset sails, priced by request. Pick one and we quote within hours.</p>'
        : '<h2>Boats that fit your group</h2><p class="lead">Showing ' + (state.base || 'Tamarindo &amp; Flamingo') + ' boats that take ' + state.pax + (state.pax > 1 ? ' guests' : ' guest') + '. Every boat is one we know personally.</p>';
      var list = Object.keys(window.FLEET).map(function (k) { return window.FLEET[k]; }).filter(function (b) {
        if (cat !== !!b.quote) return false;
        if (state.base && b.locations.indexOf(state.base) < 0) return false;
        if (!cat && b.max_pax < state.pax) return false;
        return true;
      }).sort(function (a, b) { return (a.half || 0) - (b.half || 0); });
      if (!list.length) { box.innerHTML = '<div class="empty" style="grid-column:1/-1">No single boat takes ' + state.pax + ' guests in ' + state.base + '. Go back and try the other base, or split the group over two boats: email us and we will pair them up.</div>'; }
      list.forEach(function (b) {
        box.insertAdjacentHTML('beforeend', '<label class="pick' + (state.boat === b.slug ? ' on' : '') + '"><input type="radio" name="boat" value="' + b.slug + '">' + (b.top ? '<span class="tb">Top boat</span>' : '') + '<img src="' + ROOT + 'img/' + b.images[0] + '" alt=""><div class="b"><b>' + b.name + '</b><span class="muted small">' + b.locations.join(' · ') + ' · up to ' + (b.max_pax || 'group') + (b.max_pax ? ' guests' : '') + (b.washroom ? ' · washroom' : '') + '</span>' + (b.half ? '<div class="p">' + money(b.half) + ' <small>half day · per boat</small></div>' : '<div class="p">Quote <small>on request</small></div>') + '</div></label>');
      });
      $$('input[name=boat]', box).forEach(function (i) { i.addEventListener('change', function () { state.boat = i.value; state.adv = ''; $$('.pick', box).forEach(function (p) { p.classList.toggle('on', $('input', p).checked); }); }); });
      $('#dur-row').style.display = cat ? 'none' : '';
      $$('input[name=dur]', wz).forEach(function (i) { i.checked = i.value === state.dur; i.addEventListener('change', function () { state.dur = i.value; $$('#dur-row .seg label').forEach(function (l) { l.classList.toggle('on', $('input', l).checked); }); }); });
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
      if (!c) { s.innerHTML = '<div class="empty">Go back and pick a boat or adventure first.</div>'; return; }
      s.innerHTML = '<dl><dt>Trip</dt><dd>' + c.name + '</dd><dt>Base</dt><dd>' + (state.base || 'Either') + '</dd><dt>Date</dt><dd>' + (fmtDate(state.date) || 'Flexible') + '</dd><dt>Guests</dt><dd>' + state.pax + '</dd>' + (state.type !== 'adventure' && !c.boat.quote ? '<dt>Length</dt><dd>' + durLabel2[state.dur] + '</dd>' : '') + '</dl>'
        + '<div class="tot"><span class="muted small">' + (c.est ? 'Estimated total' : '') + '</span><b>' + (c.est || c.price) + '</b></div>'
        + (c.est && c.est !== 'Quote' ? '<div class="muted small" style="margin-top:6px">Per boat, all gear, bait, drinks' + (state.dur !== 'half' ? ' and light lunch' : '') + ' included. Licenses and crew tips not included.</div>' : '');
    }
    $$('[data-next]', wz).forEach(function (b) { b.addEventListener('click', function () {
      if (step === 0 && !state.type) return toast('Pick what kind of day you want');
      if (step === 0 && !state.base && state.type !== 'adventure') return toast('Pick a base: Tamarindo or Flamingo');
      if (step === 2 && !state.boat && !state.adv) return toast('Pick one to continue');
      go(step + 1);
    }); });
    $$('[data-prev]', wz).forEach(function (b) { b.addEventListener('click', function () { go(step - 1); }); });
    $('#wiz-form').addEventListener('submit', function (e) {
      e.preventDefault(); var c = chosen(); if (!c) return go(2);
      var f = e.target.elements;
      var req = buildRequest([
        'Request: ' + c.name + (state.base ? ' (' + state.base + ')' : ''),
        (state.type !== 'adventure' && c.boat && !c.boat.quote) ? 'Charter length: ' + durLabel2[state.dur] : '',
        'Rate: ' + c.price,
        'Date: ' + (fmtDate(state.date) || 'flexible'),
        'Guests: ' + state.pax,
        'Name: ' + f.name.value, 'Email: ' + f.email.value,
        f.phone.value ? 'Phone / WhatsApp: ' + f.phone.value : '',
        'Transportation: ' + (f.transport.value || 'not needed'),
        f.notes.value ? 'Notes: ' + f.notes.value : ''
      ]);
      showSent(e.target, req, 'Your trip request is ready.');
      try { localStorage.removeItem('gf_wizard'); } catch (x) { }
    });
    go(qsw.get('boat') || qsw.get('adv') ? 1 : 0, true);
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
