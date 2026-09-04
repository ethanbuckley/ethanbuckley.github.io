/* Light and dark mode. Follows the system until the visitor chooses; the choice
   is kept in localStorage and applied before first paint, because this file is
   loaded in <head>. The button is created here so every page gets the same one. */
(function () {
  var KEY = 'theme';
  var root = document.documentElement;
  var dark = window.matchMedia('(prefers-color-scheme: dark)');

  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function effective() {
    var s = stored();
    if (s === 'light' || s === 'dark') return s;
    return dark.matches ? 'dark' : 'light';
  }
  var s0 = stored();
  if (s0 === 'light' || s0 === 'dark') root.setAttribute('data-theme', s0);

  function label(btn) {
    var e = effective();
    btn.textContent = e === 'dark' ? 'Light mode' : 'Dark mode';
    btn.setAttribute('aria-pressed', e === 'dark' ? 'true' : 'false');
    btn.setAttribute('title', e === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }
  function toggle(btn) {
    var next = effective() === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem(KEY, next); } catch (e) {}
    label(btn);
    window.dispatchEvent(new Event('themechange'));
    window.dispatchEvent(new Event('resize'));
  }
  function mount() {
    var btn = document.getElementById('theme-toggle');
    if (!btn) {
      btn = document.createElement('button');
      btn.type = 'button';
      btn.id = 'theme-toggle';
      btn.className = 'theme-toggle';
      var nav = document.querySelector('nav.site-nav');
      var top = document.querySelector('.vg-top .in');
      var back = document.querySelector('a.back');
      if (nav) nav.appendChild(btn);
      else if (top) top.appendChild(btn);
      else if (back && back.parentNode) back.parentNode.insertBefore(btn, back.nextSibling);
      else document.body.insertBefore(btn, document.body.firstChild);
    }
    label(btn);
    btn.addEventListener('click', function () { toggle(btn); });
    if (dark.addEventListener) dark.addEventListener('change', function () { label(btn); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
