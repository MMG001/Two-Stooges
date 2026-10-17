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

  /* ---------- Lightbox for flyers + gallery ---------- */
  var dlg = document.getElementById('lightbox');
  if (dlg && typeof dlg.showModal === 'function') {
    var img = dlg.querySelector('img');
    var cap = dlg.querySelector('p');
    document.addEventListener('click', function (e) {
      var trigger = e.target.closest('[data-lightbox]');
      if (!trigger) return;
      e.preventDefault();
      img.src = trigger.getAttribute('data-lightbox');
      img.alt = trigger.getAttribute('data-alt') || '';
      cap.textContent = trigger.getAttribute('data-caption') || '';
      dlg.showModal();
    });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    dlg.querySelector('.lightbox__close').addEventListener('click', function () { dlg.close(); });
  }

  /* ---------- Footer year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = now.ymd.slice(0, 4); });
})();
