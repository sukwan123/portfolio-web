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

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── 경력 기간을 열어본 시점 기준으로 다시 계산
        (data-since="2014-02", data-kind="dur" | "years") */
  Array.prototype.forEach.call(document.querySelectorAll('.live[data-since]'), function (el) {
    var p = (el.getAttribute('data-since') || '').split('-');
    if (p.length !== 2) return;
    var now = new Date();
    var months = (now.getFullYear() - +p[0]) * 12 + (now.getMonth() + 1 - +p[1]);
    if (months < 0) months = 0;
    var y = Math.floor(months / 12), m = months % 12;
    el.textContent = el.getAttribute('data-kind') === 'years'
      ? String(y)
      : (m ? y + '년 ' + m + '개월' : y + '년');
  });

  /* ── 숫자 롤링 — 화면에 들어올 때 0에서 올라간다 */
  var nums = Array.prototype.slice.call(document.querySelectorAll('.stat .n, .kpi .n'));
  if (nums.length && !reduce) {
    var roll = function (el) {
      var raw = el.innerHTML;
      var head = raw.match(/^\s*([\d,]+)/);
      if (!head) return;                       // "진행 중" 처럼 숫자가 아닌 값은 건너뛴다
      var target = parseInt(head[1].replace(/,/g, ''), 10);
      if (!isFinite(target) || target === 0) return;
      var grouped = head[1].indexOf(',') >= 0;
      var tail = raw.slice(head[0].length);
      var w = el.getBoundingClientRect().width;
      if (w) el.style.minWidth = w + 'px';     // 자릿수가 늘어도 칸이 흔들리지 않게
      var dur = target > 100 ? 1150 : 750;
      var t0 = 0;
      var paint = function (v) {
        el.innerHTML = (grouped ? v.toLocaleString('en-US') : String(v)) + tail;
      };
      paint(0);
      var step = function (ts) {
        if (!t0) t0 = ts;
        var k = Math.min((ts - t0) / dur, 1);
        k = 1 - Math.pow(1 - k, 3);            // ease-out
        paint(Math.round(target * k));
        if (k < 1) requestAnimationFrame(step);
        else { paint(target); el.style.minWidth = ''; }
      };
      requestAnimationFrame(step);
    };
    if ('IntersectionObserver' in window) {
      var nio = new IntersectionObserver(function (es) {
        es.forEach(function (en) {
          if (!en.isIntersecting) return;
          nio.unobserve(en.target);
          roll(en.target);
        });
      }, { threshold: 0.35 });
      nums.forEach(function (el) { nio.observe(el); });
    } else {
      nums.forEach(roll);
    }
  }

  /* ── 스크롤 등장 */
  var rv = Array.prototype.slice.call(document.querySelectorAll('.rv'));
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

/* ── 페이지에서 재생할 수 없는 유튜브 영상 처리
   업로더가 퍼가기를 막았으면(101·150) 빈 상자가 남으므로, 유튜브로 나가는
   썸네일 카드로 바꾼다. 영상이 아예 내려갔으면(100) 항목을 지우고, 그래서
   목록이 다 비면 제목까지 지운다.
   유튜브 API 가 뜨지 않는 환경(차단·오프라인)에서는 아무것도 건드리지 않는다. */
(function () {
  var frames = Array.prototype.slice.call(
    document.querySelectorAll('.vid iframe[src*="enablejsapi=1"]'));
  if (!frames.length) return;

  /* 퍼가기 차단 — 썸네일을 깔고 누르면 유튜브로 나가게 */
  function toLink(fig) {
    var box = fig.querySelector('.vid');
    var lab = fig.querySelector('.vlab');
    if (!box || !lab) return;
    var a = document.createElement('a');
    a.className = 'vout';
    a.href = lab.href;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.innerHTML = '<img src="https://i.ytimg.com/vi/' + fig.dataset.yt +
                  '/hqdefault.jpg" alt="" loading="lazy" onerror="this.remove()">' +
                  '<span class="vout-p" aria-hidden="true"></span>' +
                  '<span class="vout-t">유튜브에서 보기</span>';
    box.innerHTML = '';
    box.appendChild(a);
  }

  /* 영상이 내려감 — 자리를 지우고, 목록이 비면 제목까지 */
  function drop(fig) {
    var grid = fig.parentNode;
    grid.removeChild(fig);
    if (grid.querySelector('.vfig, .lnk')) return;
    var slot = grid.parentNode;
    if (slot.children.length === 2 && slot.children[0].classList.contains('slot-head')) {
      slot.parentNode.removeChild(slot);          // 지역 페이지 — 슬롯 통째로
      return;
    }
    var head = grid.previousElementSibling;       // 프로젝트 페이지 — h3 + 목록
    if (head && head.tagName === 'H3') head.parentNode.removeChild(head);
    grid.parentNode.removeChild(grid);
  }

  window.onYouTubeIframeAPIReady = function () {
    frames.forEach(function (fr) {
      var fig = fr.closest ? fr.closest('.vfig') : null;
      if (!fig || !fig.dataset.yt) return;
      new YT.Player(fr, {
        events: {
          onError: function (ev) {
            if (ev.data === 101 || ev.data === 150) toLink(fig);
            else if (ev.data === 100) drop(fig);
          }
        }
      });
    });
  };

  var s = document.createElement('script');
  s.src = 'https://www.youtube.com/iframe_api';
  document.head.appendChild(s);
})();
