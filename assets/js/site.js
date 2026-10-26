/* Two Stooges — site behaviour (no dependencies) */
(function () {
  'use strict';
  var TZ = 'America/Chicago';

  /* Current date/time in Fridley, regardless of the visitor's timezone */
  function nowCentral() {
    var parts = new Intl.DateTimeFormat('en-US', {
      timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', hour12: false, weekday: 'short'
    }).formatToParts(new Date());
    var o = {};
    parts.forEach(function (p) { o[p.type] = p.value; });
    return {
      ymd: o.year + '-' + o.month + '-' + o.day,
      hour: parseInt(o.hour, 10) % 24,
      weekday: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(o.weekday)
    };
  }
  var now = nowCentral();

  /* ---------- Mobile menu ---------- */
  var toggle = document.querySelector('.menu-toggle');
  var panel = document.getElementById('mobile-menu');
  if (toggle && panel) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      panel.hidden = open;
      document.documentElement.style.overflow = open ? '' : 'hidden';
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { toggle.click(); toggle.focus(); }
    });
    window.matchMedia('(min-width: 1081px)').addEventListener('change', function (mq) {
      if (mq.matches && toggle.getAttribute('aria-expanded') === 'true') toggle.click();
    });
  }

  /* ---------- Desktop dropdowns (click + keyboard; hover handled in CSS) ---------- */
  var subs = Array.prototype.slice.call(document.querySelectorAll('.has-sub'));
  function closeAll(except) {
    subs.forEach(function (li) {
      if (li !== except) { li.classList.remove('is-open'); li.querySelector('.nav__toggle').setAttribute('aria-expanded', 'false'); }
    });
  }
  subs.forEach(function (li) {
    var btn = li.querySelector('.nav__toggle');
    btn.addEventListener('click', function () {
      var open = li.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', String(open));
      closeAll(li);
    });
    li.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeAll(); btn.focus(); } });
    li.addEventListener('focusout', function (e) { if (!li.contains(e.relatedTarget)) { li.classList.remove('is-open'); btn.setAttribute('aria-expanded', 'false'); } });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.has-sub')) closeAll(); });

  /* ---------- Open / closed status (open daily 11 AM – 12 AM) ---------- */
  document.querySelectorAll('[data-open-status]').forEach(function (el) {
    var open = now.hour >= 11; // 11:00–23:59
    el.setAttribute('data-state', open ? 'open' : 'closed');
    el.textContent = open ? 'Open now · until midnight' : 'Closed · opens 11 AM';
  });

  /* ---------- Highlight today's specials ---------- */
  document.querySelectorAll('[data-weekday]').forEach(function (card) {
    if (parseInt(card.getAttribute('data-weekday'), 10) === now.weekday) card.classList.add('is-today');
  });

  /* ---------- Events: move past events out of "Upcoming" automatically ---------- */
  var upcoming = document.querySelector('[data-upcoming]');
  var pastGrid = document.querySelector('[data-past-grid]');
  document.querySelectorAll('[data-event-end]').forEach(function (ev) {
    if (ev.getAttribute('data-event-end') < now.ymd) {
      if (pastGrid && ev.hasAttribute('data-past-card')) {
        var tpl = document.getElementById(ev.getAttribute('data-past-card'));
        if (tpl) pastGrid.prepend(tpl.content.cloneNode(true));
      }
      ev.remove();
    }
  });
  if (upcoming && !upcoming.querySelector('[data-event-end]')) {
    var empty = document.querySelector('[data-empty-note]');
    if (empty) empty.classList.add('is-visible');
  }
  /* Home "next up" card: hide when that event has passed */
  document.querySelectorAll('[data-next-up]').forEach(function (card) {
    if (card.getAttribute('data-next-up') < now.ymd) card.remove();
  });

  /* ---------- Lightbox for flyers + gallery (X, arrows, keys, swipe) ---------- */
  var dlg = document.getElementById('lightbox');
  if (dlg && typeof dlg.showModal === 'function') {
    var img = dlg.querySelector('img');
    var cap = dlg.querySelector('p');
    var count = dlg.querySelector('.lightbox__count');
    var prev = dlg.querySelector('.lightbox__nav--prev');
    var next = dlg.querySelector('.lightbox__nav--next');
    var group = [], idx = 0;
    var show = function (i) {
      idx = (i + group.length) % group.length;
      var t = group[idx];
      img.src = t.getAttribute('data-lightbox');
      img.alt = t.getAttribute('data-alt') || '';
      cap.textContent = t.getAttribute('data-caption') || '';
      var many = group.length > 1;
      prev.hidden = next.hidden = !many;
      count.textContent = many ? (idx + 1) + ' / ' + group.length : '';
      if (many) { var pre = new Image(); pre.src = group[(idx + 1) % group.length].getAttribute('data-lightbox'); }
    };
    document.addEventListener('click', function (e) {
      var trigger = e.target.closest('[data-lightbox]');
      if (!trigger || dlg.contains(trigger)) return;
      e.preventDefault();
      var box = trigger.closest('.gallery, .photo-grid, .mosaic, .food-grid, section') || document.body;
      group = Array.prototype.slice.call(box.querySelectorAll('[data-lightbox]'));
      show(group.indexOf(trigger));
      dlg.showModal();
    });
    prev.addEventListener('click', function () { show(idx - 1); });
    next.addEventListener('click', function () { show(idx + 1); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    dlg.querySelector('.lightbox__close').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('keydown', function (e) {
      if (group.length < 2) return;
      if (e.key === 'ArrowLeft') { e.preventDefault(); show(idx - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); show(idx + 1); }
    });
    var x0 = null;
    dlg.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    dlg.addEventListener('touchend', function (e) {
      if (x0 === null || group.length < 2) return;
      var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) show(idx + (dx < 0 ? 1 : -1));
    });
    dlg.addEventListener('close', function () { img.src = 'data:,'; });
  }

  /* ---------- Menu tabs (all panels show without JS) ---------- */
  var tablist = document.querySelector('.menu-tabs');
  if (tablist) {
    var tabs = Array.prototype.slice.call(tablist.querySelectorAll('[role="tab"]'));
    var select = function (tab, focus, keepHash) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
      });
      if (focus) tab.focus();
      if (!keepHash && history.replaceState) history.replaceState(null, '', '#' + tab.getAttribute('aria-controls'));
    };
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t); });
      t.addEventListener('keydown', function (e) {
        var k = e.key, n = null;
        if (k === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
        if (k === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (k === 'Home') n = tabs[0];
        if (k === 'End') n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
    var fromHash = tabs.filter(function (t) { return '#' + t.getAttribute('aria-controls') === location.hash; })[0];
    select(fromHash || tabs[0], false, true);
    if (fromHash) tablist.scrollIntoView();
  }

  /* ---------- Footer year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = now.ymd.slice(0, 4); });
})();
