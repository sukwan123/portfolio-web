/* 손석완 포트폴리오 — 테마 전환 · 이미지 확대 · 등장 모션 */
(function () {
  'use strict';
  var root = document.documentElement;

  /* ── 테마 */
  var btn = document.getElementById('themeBtn');
  if (btn) {
    btn.addEventListener('click', function () {
      var cur = root.getAttribute('data-theme');
      var isDark = cur ? cur === 'dark'
        : window.matchMedia('(prefers-color-scheme: dark)').matches;
      var next = isDark ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('sw-theme', next); } catch (e) {}
    });
  }

  /* ── 라이트박스 */
  var shots = Array.prototype.slice.call(document.querySelectorAll('.shot'));
  var lb = document.getElementById('lb');
  if (lb && shots.length) {
    var lbImg = document.getElementById('lbImg');
    var lbCap = document.getElementById('lbCap');
    var lbIx = document.getElementById('lbIx');
    var cur = -1;

    function show(i) {
      if (i < 0) i = shots.length - 1;
      if (i >= shots.length) i = 0;
      cur = i;
      var el = shots[i];
      var im = el.querySelector('img');
      lbImg.src = el.getAttribute('data-src');
      lbImg.alt = im ? im.alt : '';
      lbCap.textContent = el.getAttribute('data-cap') || '';
      lbIx.textContent = (i + 1) + ' / ' + shots.length;
    }
    function open(i) { show(i); lb.classList.add('on'); document.body.style.overflow = 'hidden'; }
    function close() { lb.classList.remove('on'); document.body.style.overflow = ''; lbImg.src = ''; }

    shots.forEach(function (el, i) { el.addEventListener('click', function () { open(i); }); });
    document.getElementById('lbClose').addEventListener('click', close);
    document.getElementById('lbPrev').addEventListener('click', function (e) { e.stopPropagation(); show(cur - 1); });
    document.getElementById('lbNext').addEventListener('click', function (e) { e.stopPropagation(); show(cur + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb || e.target === lbImg) close(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('on')) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') show(cur - 1);
      else if (e.key === 'ArrowRight') show(cur + 1);
    });
  }

  /* ── 스크롤 등장 */
  var rv = Array.prototype.slice.call(document.querySelectorAll('.rv'));
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!rv.length) return;
  if (reduce || !('IntersectionObserver' in window)) {
    rv.forEach(function (el) { el.classList.add('in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      en.target.classList.add('in');
      io.unobserve(en.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.04 });
  rv.forEach(function (el) { io.observe(el); });
})();
