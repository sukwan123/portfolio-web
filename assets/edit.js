/* 본인 전용 문구 편집 모드
 *
 *  Ctrl+Shift+E → 암호 입력 → 편집 모드. 문단을 눌러 고치고 저장하면
 *  이 브라우저에만 남는다. 서버에는 아무것도 올라가지 않는다(정적 사이트).
 *  고친 내용은 "내보내기" 로 JSON 을 복사해 소스(src/content.py)에 반영한다.
 *
 *  암호는 SHA-256 해시로만 들어 있다. 다만 클라이언트 코드라 완전한 잠금은
 *  아니다 — 남이 풀어도 그 사람 브라우저의 사본만 바뀐다.
 */
(function () {
  'use strict';

  var PASS_HASH = '0f31c318c80aefd477a226467c2c1825d77b146068e2cabf5fd79edde9ebcef5';
  var STORE = 'sw-edits';
  var PAGE = location.pathname.split('/').pop() || 'index.html';

  var SEL = [
    '.hero .lede', '.hero .sub',
    '.phero .note', '.phero .tag',
    '.sec-head h2', '.sec-head .note',
    'main h3', 'main h4',
    'main p.body-p', 'main .bul li', 'main .feat p', 'main .feat h3',
    'main .pbody p', 'main .cbody p', 'main .banner-body p',
    'main .kv-row .v', 'main .job li', 'main .tl p', 'main .card p',
    'main .step p', 'main figcaption', 'main .own-b p',
    'main .stat .l', '.contact p', '.contact h2'
  ].join(',');

  /* ── 저장소 */
  function load() {
    try { return JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (e) { return {}; }
  }
  function save(data) {
    try { localStorage.setItem(STORE, JSON.stringify(data)); return true; } catch (e) { return false; }
  }

  /* ── 요소마다 고정 키 (문서 구조 경로) */
  function keyOf(el) {
    var parts = [];
    for (var n = el; n && n.nodeType === 1 && n !== document.body; n = n.parentElement) {
      var name = n.tagName.toLowerCase();
      if (n.id) { parts.unshift(name + '#' + n.id); break; }
      var i = 1, sib = n;
      while ((sib = sib.previousElementSibling)) if (sib.tagName === n.tagName) i++;
      parts.unshift(name + ':' + i);
    }
    return PAGE + '|' + parts.join('>');
  }

  function targets() {
    return Array.prototype.slice.call(document.querySelectorAll(SEL))
      .filter(function (el) {
        return !el.closest('.lb') && !el.querySelector('iframe,img,video,button');
      });
  }

  /* ── 저장된 수정본 반영 (원문이 그대로일 때만 — 재빌드로 문구가 바뀌면 무시) */
  var data = load();
  function apply() {
    targets().forEach(function (el) {
      var rec = data[keyOf(el)];
      if (rec && rec.orig === el.innerHTML) el.innerHTML = rec.html;
    });
  }
  apply();

  /* ── UI */
  var bar, editing = false;

  function css(el, s) { el.style.cssText = s; }

  function ask(title, cb) {
    var wrap = document.createElement('div');
    wrap.className = 'ed-modal';
    wrap.innerHTML =
      '<div class="ed-box"><p class="ed-t">' + title + '</p>' +
      '<input type="password" id="edPw" autocomplete="off" placeholder="암호">' +
      '<p class="ed-msg" id="edMsg"></p>' +
      '<div class="ed-row"><button type="button" id="edCancel">취소</button>' +
      '<button type="button" id="edOk" class="pri">확인</button></div></div>';
    document.body.appendChild(wrap);
    var input = wrap.querySelector('#edPw');
    input.focus();
    function close() { wrap.remove(); }
    function submit() {
      sha256(input.value).then(function (h) {
        if (h === PASS_HASH) { close(); cb(); }
        else {
          wrap.querySelector('#edMsg').textContent = '암호가 맞지 않습니다.';
          input.select();
        }
      });
    }
    wrap.querySelector('#edOk').addEventListener('click', submit);
    wrap.querySelector('#edCancel').addEventListener('click', close);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') submit();
      if (e.key === 'Escape') close();
    });
    wrap.addEventListener('click', function (e) { if (e.target === wrap) close(); });
  }

  function sha256(txt) {
    if (!window.crypto || !crypto.subtle) return Promise.resolve('');
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode(txt)).then(function (buf) {
      return Array.prototype.map.call(new Uint8Array(buf), function (b) {
        return ('0' + b.toString(16)).slice(-2);
      }).join('');
    });
  }

  function toast(msg) {
    var t = document.createElement('div');
    t.className = 'ed-toast';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 2200);
  }

  function enter() {
    if (editing) return;
    editing = true;
    document.body.classList.add('ed-on');
    targets().forEach(function (el) {
      el.setAttribute('contenteditable', 'true');
      el.classList.add('ed-able');
      if (!el.dataset.edOrig) el.dataset.edOrig = el.innerHTML;
    });
    bar = document.createElement('div');
    bar.className = 'ed-bar';
    bar.innerHTML =
      '<span class="ed-lab">편집 모드</span>' +
      '<button type="button" data-a="save" class="pri">저장</button>' +
      '<button type="button" data-a="export">내보내기</button>' +
      '<button type="button" data-a="reset">이 페이지 되돌리기</button>' +
      '<button type="button" data-a="exit">종료</button>' +
      '<span class="ed-hint">문단을 눌러 고친 뒤 저장하세요. 이 브라우저에만 저장됩니다.</span>';
    document.body.appendChild(bar);
    bar.addEventListener('click', function (e) {
      var a = e.target.getAttribute && e.target.getAttribute('data-a');
      if (a) act(a);
    });
    toast('편집 모드입니다. 문단을 눌러 고치세요.');
  }

  function leave() {
    editing = false;
    document.body.classList.remove('ed-on');
    targets().forEach(function (el) {
      el.removeAttribute('contenteditable');
      el.classList.remove('ed-able');
    });
    if (bar) { bar.remove(); bar = null; }
  }

  function act(a) {
    if (a === 'exit') return leave();
    if (a === 'save') {
      var n = 0;
      targets().forEach(function (el) {
        var k = keyOf(el), orig = el.dataset.edOrig;
        if (el.innerHTML === orig) { if (data[k]) { delete data[k]; n++; } return; }
        data[k] = { orig: orig, html: el.innerHTML, at: new Date().toISOString().slice(0, 10) };
        n++;
      });
      toast(save(data) ? (n ? n + '곳 저장했습니다.' : '바뀐 곳이 없습니다.') : '저장에 실패했습니다.');
      return;
    }
    if (a === 'reset') {
      targets().forEach(function (el) {
        var k = keyOf(el);
        if (data[k]) { el.innerHTML = data[k].orig; delete data[k]; }
        el.dataset.edOrig = el.innerHTML;
      });
      save(data);
      toast('이 페이지를 원래 문구로 되돌렸습니다.');
      return;
    }
    if (a === 'export') {
      var out = JSON.stringify(data, null, 2);
      var ta = document.createElement('textarea');
      ta.className = 'ed-out';
      ta.value = out;
      document.body.appendChild(ta);
      ta.select();
      var done = function (ok) {
        toast(ok ? '클립보드에 복사했습니다. Claude 에게 붙여넣으면 소스에 반영합니다.'
                 : '복사가 막혔습니다. 아래 상자의 내용을 직접 복사하세요.');
        if (ok) setTimeout(function () { ta.remove(); }, 400);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(out).then(function () { done(true); }, function () { done(false); });
      } else { done(false); }
    }
  }

  /* ── 단축키: Ctrl+Shift+E */
  document.addEventListener('keydown', function (e) {
    if (!(e.ctrlKey && e.shiftKey && (e.key === 'E' || e.key === 'e'))) return;
    e.preventDefault();
    if (editing) return leave();
    if (sessionStorage.getItem('sw-edit') === '1') return enter();
    ask('문구 편집 모드', function () {
      try { sessionStorage.setItem('sw-edit', '1'); } catch (err) {}
      enter();
    });
  });
})();
