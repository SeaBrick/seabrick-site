// SeaBrick Society site — small, dependency-free behaviours.
(function () {
  // mobile menu
  var burger = document.querySelector('.burger');
  var menu = document.querySelector('.menu');
  if (burger && menu) {
    burger.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { menu.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); } });
  }

  // technology explorer tabs
  var explorer = document.querySelector('.explorer');
  if (explorer) {
    var tabs = explorer.querySelectorAll('.tabs button');
    var panels = explorer.querySelectorAll('.panel');
    function select(i, focus) {
      tabs.forEach(function (t, k) { t.setAttribute('aria-selected', k === i ? 'true' : 'false'); t.tabIndex = k === i ? 0 : -1; });
      panels.forEach(function (p, k) { p.classList.toggle('active', k === i); });
      if (focus) tabs[i].focus();
      if (history.replaceState) history.replaceState(null, '', '#' + panels[i].id);
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(i, false); });
      t.addEventListener('keydown', function (e) {
        var n = i;
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') n = (i + 1) % tabs.length;
        else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') n = (i - 1 + tabs.length) % tabs.length;
        else if (e.key === 'Home') n = 0; else if (e.key === 'End') n = tabs.length - 1; else return;
        e.preventDefault(); select(n, true);
      });
    });
    var hash = location.hash.replace('#', '');
    var start = 0;
    panels.forEach(function (p, k) { if (p.id === hash) start = k; });
    select(start, false);
  }

  // journal filters
  var filters = document.querySelector('.filters');
  if (filters) {
    var cards = document.querySelectorAll('.posts .post-card');
    filters.querySelectorAll('button').forEach(function (b) {
      b.addEventListener('click', function () {
        filters.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
        b.setAttribute('aria-pressed', 'true');
        var cat = b.dataset.cat;
        cards.forEach(function (c) { c.style.display = (cat === 'all' || c.dataset.cat === cat) ? '' : 'none'; });
      });
    });
  }
})();

// builder frames report their height on phones, so controls run in the page's own scroll
window.addEventListener('message', function (e) {
  if (!e.data || !e.data.seabrickHeight) return;
  document.querySelectorAll('.embed iframe').forEach(function (f) {
    if (f.contentWindow === e.source && window.innerWidth < 820 && e.data.narrow) f.style.height = Math.min(4000, e.data.seabrickHeight) + 'px';
  });
});

// three-state picture on the home page
document.querySelectorAll('.threestate').forEach(function (fig) {
  fig.querySelectorAll('.states button').forEach(function (b) {
    b.addEventListener('click', function () {
      fig.querySelectorAll('img').forEach(function (im) { im.classList.toggle('on', im.dataset.state === b.dataset.state); });
      fig.querySelectorAll('.states button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    });
  });
});

// the connection lab is shown unchanged inside its frame; its own header and footer are hidden so the page has one header
(function () {
  var f = document.getElementById('labframe');
  if (!f) return;
  function tidy() {
    try {
      var d = f.contentDocument; if (!d) return;
      var s = d.createElement('style');
      s.textContent = 'header.site-header,footer,.demo-notice{display:none!important}body{padding-top:0!important}';
      d.head.appendChild(s);
    } catch (e) { /* cross-origin: leave as is */ }
  }
  f.addEventListener('load', tidy); if (f.contentDocument && f.contentDocument.readyState === 'complete') tidy();
})();
