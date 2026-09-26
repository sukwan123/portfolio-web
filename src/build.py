# -*- coding: utf-8 -*-
"""정적 페이지 생성기.

    python3 src/build.py

src/content.py 의 데이터로 저장소 루트에 HTML 을 쓴다.

  index.html          랜딩 — 프로젝트 6개 카드
  kingsroad.html      대표 프로젝트 허브
  kr-<slug>.html      킹스로드 하위 콘텐츠 10종 + kr-systems.html
  aura.html           AI 목업 파이프라인 (R&D)
  p-<slug>.html       이전 프로젝트 5종
"""
import html
import os
import re
import sys
from datetime import date
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as C  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
FILES = sorted(os.listdir(IMG))

SLOT_LABEL = {"1": "평면도", "2": "목업 전경", "3": "완성 화면"}
SLOT_FILE = {"1": "plan", "2": "mock", "3": "final"}


# ──────────────────────────────────────────────────────── 경력 기간 (실시간)
# 빌드 시점 값을 본문에 적어 두고, 같은 시작일을 data-since 로 넘겨
# 브라우저에서 다시 계산한다. 페이지를 안 고쳐도 달이 바뀌면 숫자가 따라간다.
def months_since(start):
    y, m = (int(x) for x in start.split("-"))
    today = date.today()
    return (today.year - y) * 12 + (today.month - m)


def dur_text(months):
    y, m = divmod(max(months, 0), 12)
    return "%d년 %d개월" % (y, m) if m else "%d년" % y


def live_span(start, kind="dur", tag="b"):
    n = months_since(start)
    text = str(n // 12) if kind == "years" else dur_text(n)
    return '<%s class="live" data-since="%s" data-kind="%s">%s</%s>' % (tag, start, kind, text, tag)


def tokens(text):
    s = C.SITE
    return (text
            .replace("{{career}}", live_span(s["career_start"]))
            .replace("{{nm_dur}}", live_span(s["netmarble_start"], tag="span"))
            .replace("{{nm_years}}", live_span(s["netmarble_start"], kind="years", tag="span")))


def e(s):
    return html.escape(str(s), quote=True)


def pick(num, slot):
    return [f for f in FILES if f.startswith("%s-%s" % (num, SLOT_FILE[slot]))]


def shots_of(c):
    n = 0
    for slot in ("1", "2", "3"):
        n += len(pick(c["num"], slot))
    return n


# ──────────────────────────────────────────────────────── 영상 임베드
def embed_src(url):
    """유튜브·드라이브 주소를 iframe 에 넣을 주소로 바꾼다.

    watch?v= / youtu.be / ?t=초 형태가 섞여 있어 id 와 시작 지점만 뽑아 쓴다.
    """
    u = urlparse(url)
    if "drive.google.com" in u.netloc:
        m = re.search(r"/file/d/([^/]+)", u.path)
        return "https://drive.google.com/file/d/%s/preview" % m.group(1) if m else None
    vid = None
    if "youtu.be" in u.netloc:
        vid = u.path.strip("/")
    elif "youtube" in u.netloc:
        vid = parse_qs(u.query).get("v", [None])[0]
    if not vid:
        return None
    q = parse_qs(u.query)
    start = (q.get("t") or q.get("start") or [""])[0].rstrip("s")
    src = "https://www.youtube-nocookie.com/embed/%s?rel=0" % vid
    if start.isdigit():
        src += "&start=%s" % start
    return src


def embeds(items):
    """(제목, 주소, 설명) 목록을 16:9 임베드 격자로."""
    out = []
    for label, url, note in items:
        src = embed_src(url)
        if not src:                      # 임베드가 안 되는 주소는 링크로 남긴다
            out.append('<a class="lnk" href="%s" target="_blank" rel="noopener noreferrer">'
                       '<span class="lnk-tag">영상</span><span class="lnk-txt"><b>%s</b></span>'
                       '<span class="lnk-ar">↗</span></a>' % (e(url), e(label)))
            continue
        out.append('<figure class="fig vfig"><div class="vid">'
                   '<iframe src="%s" title="%s" loading="lazy" allowfullscreen '
                   'allow="accelerometer; encrypted-media; picture-in-picture; fullscreen" '
                   'referrerpolicy="strict-origin-when-cross-origin"></iframe></div>'
                   '<figcaption><a class="vlab" href="%s" target="_blank" '
                   'rel="noopener noreferrer">%s <span class="ar">↗</span></a>%s</figcaption></figure>'
                   % (e(src), e(label), e(url), e(label),
                      ("<em>%s</em>" % e(note)) if note else ""))
    return '<div class="vgrid rv">%s</div>\n' % "".join(out)


# ──────────────────────────────────────────────────────── 공통 뼈대
def head(title, desc=""):
    return """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="description" content="%s">
<meta name="color-scheme" content="light dark">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%%3E%%3Crect width='32' height='32' rx='7' fill='%%238A6636'/%%3E%%3Ctext x='16' y='22' font-family='monospace' font-size='15' font-weight='700' fill='%%23fff' text-anchor='middle'%%3ESW%%3C/text%%3E%%3C/svg%%3E">
<script>try{var t=localStorage.getItem('sw-theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}</script>
</head>
<body>
""" % (e(desc), e(title))


def bar(current=None):
    links = "".join(
        '<a href="%s"%s>%s</a>' % (e(href), ' aria-current="page"' if label == current else "", e(label))
        for href, label in C.NAV)
    return """<header class="bar">
  <div class="bar-in">
    <a class="brand" href="index.html">
      <span class="mk">SW</span>
      <b>손석완</b><span>레벨 디자이너</span>
    </a>
    <nav class="bar-nav">%s</nav>
    <button class="theme-btn" id="themeBtn" type="button" aria-label="화면 테마 전환">◐</button>
  </div>
</header>
""" % links


def crumb(trail):
    """trail: [(href|None, label), …] — 마지막 항목은 현재 문서."""
    out = []
    for i, (href, label) in enumerate(trail):
        if i:
            out.append('<i>/</i>')
        if href:
            out.append('<a href="%s">%s</a>' % (e(href), e(label)))
        else:
            out.append('<b>%s</b>' % e(label))
    return '<div class="crumb"><div class="crumb-in">%s</div></div>\n' % "".join(out)


def foot(note="미공개 콘텐츠는 이미지를 싣지 않았습니다"):
    return """<div class="wrap">
  <div class="foot">
    <span>손석완 · 레벨 디자이너 · Updated %s</span>
    <span>%s</span>
  </div>
</div>
""" % (e(C.SITE["updated"]), e(note))


def tail(with_lightbox=True):
    lb = """<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="이미지 확대 보기">
  <button class="lb-close" id="lbClose" type="button" aria-label="닫기">✕</button>
  <button class="lb-btn lb-prev" id="lbPrev" type="button" aria-label="이전 이미지">‹</button>
  <img id="lbImg" src="" alt="">
  <button class="lb-btn lb-next" id="lbNext" type="button" aria-label="다음 이미지">›</button>
  <div class="lb-cap"><span id="lbCap"></span><span class="ix" id="lbIx"></span></div>
</div>
""" if with_lightbox else ""
    return lb + '<script src="assets/app.js"></script>\n</body>\n</html>\n'


def contact_section():
    s = C.SITE
    h = C.HOME
    return """<section class="contact" id="contact">
  <div class="wrap">
    <div class="contact-in rv">
      <div>
        <p class="eyebrow plain">Contact</p>
        <h2 style="margin-top:10px">%s</h2>
        <p>%s</p>
      </div>
      <div class="chips">
        <a class="chip" href="mailto:%s">%s</a>
        <a class="chip" href="tel:%s">%s</a>
      </div>
    </div>
  </div>
</section>
""" % (e(h["contact_h"]), h["contact_p"], e(s["email"]), e(s["email"]), e(s["tel_href"]), e(s["tel"]))


def pager(prev, next_):
    """prev/next: (href, label) 또는 None"""
    def cell(item, kind, lab):
        if not item:
            return '<span class="pg dim %s"><span class="l">%s</span><b>—</b></span>' % (kind, lab)
        return '<a class="pg %s" href="%s"><span class="l">%s</span><b>%s</b></a>' % (
            kind, e(item[0]), lab, e(item[1]))
    return '<div class="wrap" style="padding-bottom:44px"><div class="pager">%s%s</div></div>\n' % (
        cell(prev, "prev", "← 이전"), cell(next_, "next", "다음 →"))


# ──────────────────────────────────────────────────────── 본문 블록
def block(b):
    kind = b[0]
    if kind == "h3":
        return '<h3 class="h3 rv">%s</h3>\n' % b[1]
    if kind == "p":
        return '<p class="body-p rv">%s</p>\n' % b[1]
    if kind == "note":
        return '<p class="undisclosed rv">%s</p>\n' % b[1]
    if kind == "bul":
        return '<ul class="bul rv">%s</ul>\n' % "".join("<li>%s</li>" % x for x in b[1])
    if kind == "kv":
        return '<div class="kv rv">%s</div>\n' % "".join(
            '<div class="kv-row"><div class="k">%s</div><div class="v">%s</div></div>' % (e(k), v)
            for k, v in b[1])
    if kind == "stats":
        return '<div class="stats rv">%s</div>\n' % "".join(
            '<div class="stat"><div class="n">%s</div><div class="l">%s</div></div>' % (n, e(l))
            for n, l in b[1])
    if kind == "launch":
        return '<div class="launch rv">%s</div>\n' % "".join(
            '<div class="launch-row%s"><div class="d">%s</div><div class="t">%s</div></div>' % (
                " hi" if hi else "", e(d), t) for d, t, hi in b[1])
    if kind == "cards":
        out = []
        for h4, m, p, lis in b[1]:
            li = "".join("<li>%s</li>" % x for x in lis)
            out.append('<div class="card"><h4>%s</h4><div class="m">%s</div><p>%s</p>%s</div>' % (
                e(h4), e(m), p, ("<ul>%s</ul>" % li) if li else ""))
        return '<div class="cards rv">%s</div>\n' % "".join(out)
    if kind == "steps":
        out = []
        for cls, k, h4, p in b[1]:
            out.append('<li class="step %s"><div class="k">%s</div><div><h4>%s</h4><p>%s</p></div></li>' % (
                e(cls), e(k), e(h4), p))
        return '<ol class="steps rv">%s</ol>\n' % "".join(out)
    if kind == "figrow":
        out = []
        for src, cap, alt in b[1]:
            out.append('<figure class="fig"><img src="%s" alt="%s" loading="lazy" decoding="async">'
                       '<figcaption>%s</figcaption></figure>' % (e(src), e(alt), e(cap)))
        return '<div class="figrow rv">%s</div>\n' % "".join(out)
    if kind == "vidrow":
        out = []
        for src, cap in b[1]:
            out.append('<figure class="fig"><video src="%s" controls muted loop playsinline '
                       'preload="metadata"></video><figcaption>%s</figcaption></figure>' % (e(src), e(cap)))
        return '<div class="figrow rv">%s</div>\n' % "".join(out)
    if kind == "embeds":
        return embeds(C.VIDEOS[b[1]])
    if kind == "links":
        out = []
        for tag, label, note, url in b[1]:
            out.append('<a class="lnk" href="%s" target="_blank" rel="noopener noreferrer">'
                       '<span class="lnk-tag">%s</span><span class="lnk-txt"><b>%s</b>%s</span>'
                       '<span class="lnk-ar">↗</span></a>' % (
                           e(url), e(tag), e(label), ('<em>%s</em>' % e(note)) if note else ""))
        return '<div class="lnks rv">%s</div>\n' % "".join(out)
    if kind == "shotfig":
        _, src, cap, figcap = b
        return ('<figure class="fig rv"><button class="shot" data-src="%s" data-cap="%s" '
                'aria-label="%s 확대" style="border:0;border-radius:0">'
                '<img src="%s" alt="%s" loading="lazy" decoding="async"></button>'
                '<figcaption>%s</figcaption></figure>\n') % (
            e(src), e(cap), e(figcap), e(src), e(figcap), e(figcap))
    raise ValueError("알 수 없는 블록: %s" % kind)


def blocks(bs):
    return "".join(block(b) for b in bs)


# ──────────────────────────────────────────────────────── 카드
def cover_html(cover, mono, alt, badge=None, extra=""):
    b = ('<span class="badge %s">%s</span>' % (e(badge[0]), e(badge[1]))) if badge else ""
    if cover:
        return ('<div class="pcover"><img src="img/cov/%s.webp" alt="%s" loading="lazy" '
                'decoding="async" width="1000" height="563"><span class="veil"></span>%s%s</div>') % (
            e(cover), e(alt), b, extra)
    return '<div class="pcover blank"><span class="mono">%s</span>%s%s</div>' % (e(mono or "—"), b, extra)


def own_cover(w):
    """개인 작업 커버. 영상이 있으면 유튜브 썸네일을 얹고, 못 불러오면 모노그램이 남는다."""
    base = cover_html(None, w.get("mono"), w["title"])
    if not w.get("videos"):
        return base
    src = embed_src(w["videos"][0][1]) or ""
    vid = src.split("/embed/")[-1].split("?")[0] if "/embed/" in src else ""
    if not vid:
        return base
    # 기본은 숨김 — 썸네일이 실제로 뜬 경우에만 드러낸다 (유튜브가 막힌 환경에서도 모노그램이 남음)
    thumb = ('<img class="ythumb" src="https://i.ytimg.com/vi/%s/hqdefault.jpg" alt="%s" '
             'loading="lazy" decoding="async" onload="this.classList.add(\'on\')" '
             'onerror="this.remove()">' % (e(vid), e(w["title"])))
    return base.replace('</div>', thumb + '<span class="veil"></span></div>')


def project_card(p):
    mini = ""
    if p.get("mini"):
        mini = '<div class="feature-mini">%s</div>' % "".join("<span>%s</span>" % e(x) for x in p["mini"])
    cov = cover_html(p.get("cover"), p.get("mono"), p["title"] + " 대표 이미지", p.get("badge"))
    if p.get("featured"):
        return """<a class="feature rv" href="%s">
  %s
  <div class="feature-body">
    <p class="eyebrow plain">대표 프로젝트</p>
    <h3>%s</h3>
    <div class="m">%s</div>
    <p class="role" style="color:var(--ink);font-weight:500;font-size:14.5px">%s</p>
    <p>%s</p>
    %s
    <div class="more" style="margin-top:14px;font-family:var(--mono);font-size:11.5px;color:var(--accent);letter-spacing:.06em">담당 콘텐츠 10종 보기 <span class="ar">→</span></div>
  </div>
</a>
""" % (e(p["page"]), cov, e(p["title"]), e(p["meta"]), e(p["role"]), p["summary"], mini)
    return """<a class="pcard rv" href="%s">
  %s
  <div class="pbody">
    <h3>%s</h3>
    <div class="m">%s</div>
    <p class="role">%s</p>
    <p>%s</p>
    <div class="more">자세히 보기 <span class="ar">→</span></div>
  </div>
</a>
""" % (e(p["page"]), cov, e(p["title"]), e(p["meta"]), e(p["role"]), p["summary"])


def content_card(c):
    n = shots_of(c)
    extra = '<span class="shotc">이미지 %d장</span>' % n if n else ""
    cov = cover_html(c.get("cover"), c.get("mono"), c["title"] + " 대표 이미지", c.get("badge"), extra)
    return """<a class="ccard rv" href="kr-%s.html">
  %s
  <div class="cbody">
    <div class="m">%s</div>
    <h4>%s</h4>
    <p>%s</p>
    <div class="st">%s</div>
  </div>
</a>
""" % (e(c["slug"]), cov, e(c["meta"]), e(c["title"]), e(c["summary"]), e(c["role"].split(" · ")[0]))


# ──────────────────────────────────────────────────────── 갤러리
def gallery(c):
    out = []
    for slot in ("1", "2", "3"):
        cap = c["caps"].get(slot)
        if not cap:
            continue
        fs = pick(c["num"], slot)
        if not fs:
            continue
        cls = "g1" if len(fs) == 1 else ("g2" if len(fs) <= 4 else "g3")
        cells = []
        for i, f in enumerate(fs):
            alt = "%s %s %d" % (c["title"], SLOT_LABEL[slot], i + 1)
            cells.append('<button class="shot" data-src="img/%s" data-cap="%s" aria-label="%s 확대">'
                         '<img src="img/%s" alt="%s" loading="lazy" decoding="async"></button>'
                         % (e(f), e(cap), e(alt), e(f), e(alt)))
        out.append('<div class="slot rv"><div class="slot-head"><span class="slot-tag">%s</span>'
                   '<p class="slot-cap">%s</p></div><div class="grid %s">%s</div></div>'
                   % (SLOT_LABEL[slot], e(cap), cls, "".join(cells)))
    return "".join(out)


def yt_block(c):
    if not c.get("yt"):
        return ""
    return ('<div class="slot rv"><div class="slot-head"><span class="slot-tag">영상</span>'
            '<p class="slot-cap">실제 플레이 영상입니다. 여기서 바로 재생됩니다.</p></div>'
            '%s</div>') % embeds([(c["ytlab"], "https://youtu.be/" + c["yt"], None)])


# ──────────────────────────────────────────────────────── 페이지 히어로
def phero(eyebrow, title, tag, note, cover=None, num=None, chips=None):
    if cover:
        bg = '<div class="phero-bg" style="background-image:url(img/cov/%s.webp)"></div>' % e(cover)
        cls = ""
    else:                      # 커버 이미지가 없는 문서 — 도면 격자로 대신한다
        bg = '<div class="phero-grid"></div>'
        cls = " blank"
    numel = ('<div class="phero-num">%s</div>' % e(num)) if num else ""
    chipel = ""
    if chips:
        chipel = '<div class="chips">%s</div>' % "".join('<span class="chip">%s</span>' % x for x in chips)
    return """<div class="phero%s">
  %s
  <div class="phero-scrim"></div>
  <div class="phero-in">
    <p class="eyebrow">%s</p>
    <h1>%s</h1>
    <p class="tag">%s</p>
    <p class="note">%s</p>
    %s
  </div>
  %s
</div>
""" % (cls, bg, eyebrow, title, tag, note, chipel, numel)


# ──────────────────────────────────────────────────────── 홈
def build_index():
    h = C.HOME
    kingsroad = [p for p in C.PROJECTS if p.get("featured")][0]
    others = [p for p in C.PROJECTS if not p.get("featured")]

    stats = "".join('<div class="stat"><div class="n">%s</div><div class="l">%s</div></div>' % (n, e(l))
                    for n, l in h["stats"])
    feats = "".join('<div class="feat rv"><div class="k">%s</div><h3>%s</h3><p>%s</p></div>' % (
        e(k), e(t), p) for k, t, p in h["feats"])
    chips = "".join('<span class="chip">%s</span>' % x for x in h["chips"])
    jobs = "".join(
        '<div class="job"><div class="when"><b>%s</b>%s</div><div><h4>%s</h4>'
        '<div class="pos">%s</div><ul>%s</ul></div></div>' % (
            e(when), e(co), e(title), e(pos), "".join("<li>%s</li>" % x for x in lis))
        for when, co, title, pos, lis in h["career"])
    edu = "".join('<div class="kv-row"><div class="k">%s</div><div class="v">%s</div></div>' % (e(k), v)
                  for k, v in h["edu"])
    skills = "".join('<div class="kv-row"><div class="k">%s</div><div class="v">%s</div></div>' % (e(k), v)
                     for k, v in h["skills"])
    off = "".join("<li>%s</li>" % x for x in h["offindustry"])   # 본문 데이터는 서식 태그를 그대로 쓴다

    out = [head("손석완 · 레벨 디자이너 포트폴리오",
                "레벨 디자이너 손석완의 포트폴리오. 왕좌의 게임: 킹스로드 필드·던전 레벨디자인."),
           bar()]

    out.append("""<div class="hero">
  <div class="hero-bg" style="background-image:url(img/cov/hero-home.webp)"></div>
  <div class="hero-scrim"></div>
  <div class="hero-grid"></div>
  <div class="hero-in">
    <div class="hero-col">
      <p class="eyebrow">Level Designer · Portfolio 2026</p>
      <h1>손석완</h1>
      <p class="role">Level Designer / 레벨 디자이너</p>
      <p class="lede">%s</p>
      <p class="sub">%s</p>
      <div class="hero-cta">
        <a class="btn btn-pri" href="kingsroad.html">대표 프로젝트 보기 <span class="ar">→</span></a>
        <a class="btn btn-ghost" href="#projects">프로젝트 6종 <span class="ar">↓</span></a>
      </div>
      <div class="chips">%s<a class="chip" href="mailto:%s">%s</a></div>
    </div>
    <figure class="portrait">
      <img src="img/profile.webp" alt="손석완 프로필 사진" width="660" height="880" fetchpriority="high">
    </figure>
  </div>
</div>
""" % (h["lede"], h["sub"], chips, e(C.SITE["email"]), e(C.SITE["email"])))

    out.append('<main>\n')

    # 요약
    out.append("""<section id="howiwork">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">Summary</p>
      <h2>이렇게 일해왔습니다</h2>
      <p class="note">10년 넘게 6개 프로젝트에서 레벨디자인을 해왔고, 그 사이 시나리오 · 퀘스트 · 시스템 · BM · 운영까지 맡아봤습니다. 하이컨셉 단계부터 글로벌 출시와 라이브 서비스, 그리고 서비스 종료까지 개발 주기 전체를 겪었습니다.</p>
    </div>
    <div class="stats rv">%s</div>
    <div class="feats">%s</div>
  </div>
</section>
""" % (stats, feats))

    # 프로젝트
    out.append("""<section id="projects">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">Projects</p>
      <h2>참여한 6개 프로젝트</h2>
      <p class="note">카드를 누르면 프로젝트별 상세 문서로 들어갑니다. 대표 프로젝트인 <b>왕좌의 게임: 킹스로드</b>는 지역·던전 10종의 작업 과정을 따로 정리해 두었습니다.</p>
    </div>
    %s
    <div class="pgrid">%s</div>
  </div>
</section>
""" % (project_card(kingsroad), "".join(project_card(p) for p in others)))

    # R&D 배너
    out.append("""<section id="rnd">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">R&amp;D</p>
      <h2>목업 제작을 파이프라인으로 만들었습니다</h2>
    </div>
    <a class="banner rv" href="aura.html">
      <div class="banner-body">
        <p class="eyebrow plain">AI Pipeline · 2026</p>
        <h3>평면도 툴 → Aura → UE5 목업</h3>
        <p>평면도를 픽셀 단위로 그려 구조화된 데이터를 뽑는 툴을 직접 만들고, 그 데이터를 언리얼 LLM 플러그인 Aura에 넣어 기획 의도가 반영된 목업을 생성합니다. 팀에도 확산했습니다.</p>
        <div class="kpi">
          <div><span class="n">53%%</span><span class="l">평균 활용률</span></div>
          <div><span class="n">31%%</span><span class="l">평균 시간 절감</span></div>
        </div>
        <div class="more" style="margin-top:12px;font-family:var(--mono);font-size:11.5px;color:var(--accent);letter-spacing:.06em">R&amp;D 리포트 읽기 <span class="ar">→</span></div>
      </div>
      <div class="pcover"><img src="img/cov/aura.webp" alt="Aura로 생성한 목업" loading="lazy" decoding="async" width="1000" height="563"><span class="veil"></span></div>
    </a>
  </div>
</section>
""")

    # 개인 작업
    own_cards = "".join(
        '<a class="pcard rv" href="personal.html#%s">%s<div class="pbody"><h3>%s</h3>'
        '<div class="m">%s</div><p>%s</p>'
        '<div class="more">자세히 보기 <span class="ar">→</span></div></div></a>'
        % (e(w["slug"]), own_cover(w), e(w["title"]), e(w["meta"]), e(w["desc"]))
        for w in C.PERSONAL["own"] if not w.get("draft"))
    out.append("""<section id="personal">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">Personal Works</p>
      <h2>회사 밖에서 만든 것들</h2>
      <p class="note">시킨 사람이 없어도 만듭니다. 개인 제작 프로젝트와 함께, 지난 프로젝트의 기획 문서 %d편과 플레이 영상 %d편을 <a href="personal.html" style="color:var(--accent)">자료실</a>에 모아 뒀습니다.</p>
    </div>
    <div class="pgrid">%s</div>
  </div>
</section>
""" % (len(C.PERSONAL["docs"]), sum(len(v[1]) for v in C.PERSONAL["videos"]), own_cards))

    # 경력
    out.append("""<section id="career">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">Career</p>
      <h2>경력 · 학력</h2>
    </div>
    <div class="career rv">%s</div>
    <div class="kv rv">%s</div>
    <h3 class="h3 rv">업계 외 경력</h3>
    <p class="body-p rv">게임 업계에 오기 전 영화를 전공했고, 시나리오 작가와 영화 스탭으로 일했습니다. 글쓰기는 지금도 이어가고 있어서, 스토리텔링과 연출이 중요한 레벨에서 이 경력이 크게 작용합니다.</p>
    <ul class="bul rv">%s</ul>
    <figure class="fig rv" style="max-width:620px"><img src="img/cov/offindustry.webp" alt="보조작가로 참여한 드라마와 만화" loading="lazy" decoding="async" width="1000" height="563"><figcaption>보조작가로 참여한 어린이 드라마와 만화 · 애니메이션 작업 일부</figcaption></figure>
  </div>
</section>
""" % (jobs, edu, off))

    # 스킬
    out.append("""<section id="skills">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">Skills &amp; Tools</p>
      <h2>다루는 것</h2>
    </div>
    <div class="kv rv">%s</div>
  </div>
</section>
""" % skills)

    out.append(contact_section())
    out.append('</main>\n')
    out.append(foot())
    out.append(tail(with_lightbox=False))
    return "".join(out)


# ──────────────────────────────────────────────────────── 킹스로드 허브
def build_kingsroad():
    k = C.KINGSROAD
    fields = [c for c in C.CONTENTS if c["group"] == "field"]
    dungeons = [c for c in C.CONTENTS if c["group"] == "dungeon"]

    out = [head("왕좌의 게임: 킹스로드 · 손석완 레벨디자인",
                "넷마블네오 왕좌의 게임: 킹스로드에서 담당한 필드 5곳과 던전 5종."),
           bar("킹스로드"),
           crumb([("index.html", "홈"), (None, "왕좌의 게임: 킹스로드")]),
           phero("Current · 넷마블네오", "왕좌의 게임: 킹스로드",
                 "오픈월드 액션 RPG<span class=\"dot\">·</span>PC · 모바일 크로스플레이"
                 "<span class=\"dot\">·</span><b>Unreal Engine 5</b>",
                 k["note"], cover="hero-kingsroad")]

    out.append('<main>\n')
    out.append('<section class="tight"><div class="wrap">')
    out.append(block(("stats", k["stats"])))
    out.append(block(("kv", k["kv"])))
    out.append('<h3 class="h3 rv">출시 마일스톤</h3>')
    out.append(block(("launch", k["launch"])))
    out.append('</div></section>\n')

    out.append("""<section id="work">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">Work · 담당 콘텐츠</p>
      <h2>필드 5곳 · 던전 5종</h2>
      <p class="note">각 문서는 <b>평면도 → 목업 → 완성 화면</b> 순으로 실제 작업 과정을 그대로 실었습니다. 카드를 누르면 지역별 상세 문서로 들어갑니다.</p>
    </div>
    <h3 class="h3 rv">필드 지역</h3>
    <div class="cgrid">%s</div>
    <h3 class="h3 rv" style="margin-top:44px">던전</h3>
    <div class="cgrid">%s</div>
  </div>
</section>
""" % ("".join(content_card(c) for c in fields), "".join(content_card(c) for c in dungeons)))

    # 레벨 기능 · AI 배너
    s = C.SYSTEMS
    out.append("""<section id="more">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">Beyond Terrain</p>
      <h2>지형 밖에서 한 일</h2>
      <p class="note">지형과 동선만이 아니라, 그 위에서 벌어질 일에 필요한 시스템과 작업 방식까지 만들었습니다.</p>
    </div>
    <a class="banner rv" href="%s">
      <div class="banner-body">
        <p class="eyebrow plain">Systems · 2022–2026</p>
        <h3>레벨 기능 · 기믹 기획</h3>
        <p>이동 규칙 · 레벨 기믹 · 가젯 · 전투 연출을 사양 문서로 직접 기획했습니다. 2026년에는 엘리베이터 · 사다리 중간 취소 · 렛지그랩을 상세기획서 개정으로 확정했습니다.</p>
        <div class="kpi">
          <div><span class="n">4</span><span class="l">레벨 시스템 유형</span></div>
          <div><span class="n">12</span><span class="l">상세기획서 개정 (최다)</span></div>
        </div>
        <div class="more" style="margin-top:12px;font-family:var(--mono);font-size:11.5px;color:var(--accent);letter-spacing:.06em">문서 보기 <span class="ar">→</span></div>
      </div>
      <div class="pcover"><img src="img/cov/systems.webp" alt="레벨 기믹 작업 화면" loading="lazy" decoding="async" width="1000" height="563"><span class="veil"></span></div>
    </a>
    <a class="banner rv" href="aura.html" style="margin-top:16px">
      <div class="banner-body">
        <p class="eyebrow plain">R&amp;D · 2026</p>
        <h3>평면도 툴 → Aura → UE5 목업 파이프라인</h3>
        <p>목업 제작 시간을 줄이기 위해 평면도 제작 툴을 직접 만들고, 언리얼 LLM 플러그인 Aura와 연결해 기획 의도가 반영된 목업을 생성하는 파이프라인을 세웠습니다.</p>
        <div class="kpi">
          <div><span class="n">53%%</span><span class="l">평균 활용률</span></div>
          <div><span class="n">31%%</span><span class="l">평균 시간 절감</span></div>
        </div>
        <div class="more" style="margin-top:12px;font-family:var(--mono);font-size:11.5px;color:var(--accent);letter-spacing:.06em">R&amp;D 리포트 읽기 <span class="ar">→</span></div>
      </div>
      <div class="pcover"><img src="img/cov/aura.webp" alt="Aura로 생성한 목업" loading="lazy" decoding="async" width="1000" height="563"><span class="veil"></span></div>
    </a>
  </div>
</section>
""" % e(s["page"]))

    # 타임라인
    tl = "".join('<li><div class="y">%s</div><div><h4>%s</h4><p>%s</p></div></li>' % (e(y), e(t), p)
                 for y, t, p in C.KINGSROAD["timeline"])
    out.append("""<section id="timeline">
  <div class="wrap">
    <div class="sec-head rv">
      <p class="eyebrow">Timeline</p>
      <h2>킹스로드에서의 {{nm_years}}년</h2>
    </div>
    <ul class="tl rv">%s</ul>
  </div>
</section>
""" % tl)

    out.append('</main>\n')
    out.append(pager(("index.html", "홈"), ("kr-%s.html" % C.CONTENTS[0]["slug"], C.CONTENTS[0]["title"])))
    out.append(foot())
    out.append(tail(with_lightbox=False))
    return "".join(out)


# ──────────────────────────────────────────────────────── 콘텐츠 상세
def build_content(c, prev, next_):
    kind = "필드 지역" if c["group"] == "field" else "던전"
    out = [head("%s · 킹스로드 레벨디자인" % c["title"], c["summary"]),
           bar("킹스로드"),
           crumb([("index.html", "홈"), ("kingsroad.html", "왕좌의 게임: 킹스로드"), (None, c["nav"])]),
           phero("%s · %s" % (kind, c["badge"][1]), c["title"],
                 "%s<span class=\"dot\">·</span><b>%s</b>" % (e(c["meta"]), e(c["badge"][1])),
                 c["desc"], cover=c.get("cover"), num=c["num"])]

    out.append('<main>\n<section class="tight"><div class="wrap">')
    out.append(block(("kv", [("담당", c["role"]), ("구분", c["meta"])])))
    if c.get("undisclosed"):
        out.append('<p class="undisclosed rv">%s</p>\n' % e(c["undisclosed"]))
    g = gallery(c)
    if g:
        out.append(g)
    if c.get("partial"):
        out.append('<p class="undisclosed rv">%s</p>\n' % e(c["partial"]))
    out.append(yt_block(c))
    out.append('</div></section>\n</main>\n')
    out.append(pager(prev, next_))
    out.append(foot())
    out.append(tail())
    return "".join(out)


def build_systems(prev, next_):
    s = C.SYSTEMS
    out = [head("레벨 기능 · 기믹 기획 · 킹스로드", s["note"]),
           bar("킹스로드"),
           crumb([("index.html", "홈"), ("kingsroad.html", "왕좌의 게임: 킹스로드"), (None, "레벨 기능 · 기믹")]),
           phero(s["eyebrow"], s["title"], s["tag"], s["note"], cover=s.get("cover"))]
    out.append('<main>\n<section class="tight"><div class="wrap">')
    out.append(blocks(s["blocks"]))
    out.append('</div></section>\n</main>\n')
    out.append(pager(prev, next_))
    out.append(foot())
    out.append(tail())
    return "".join(out)


def build_aura():
    a = C.AURA
    out = [head("AI 목업 파이프라인 · 손석완",
                "평면도 제작 툴과 Aura를 연결한 UE5 목업 파이프라인 — 활용률 53%, 시간 절감 31%."),
           bar("AI 파이프라인"),
           crumb([("index.html", "홈"), ("kingsroad.html", "왕좌의 게임: 킹스로드"), (None, "AI 목업 파이프라인")]),
           phero(a["eyebrow"], a["title"], a["tag"], a["note"], cover=a.get("cover"))]
    out.append('<main>\n<section class="tight"><div class="wrap">')
    out.append(blocks(a["blocks"]))
    out.append('</div></section>\n</main>\n')
    out.append(pager(("kr-systems.html", "레벨 기능 · 기믹 기획"), ("index.html", "홈")))
    out.append(foot())
    out.append(tail())
    return "".join(out)


def build_personal():
    P = C.PERSONAL
    out = [head("개인 작업 · 자료실 · 손석완", P["note"]),
           bar("개인 작업"),
           crumb([("index.html", "홈"), (None, "개인 작업")]),
           phero(P["eyebrow"], P["title"], P["tag"], P["note"])]
    out.append('<main>\n<section class="tight"><div class="wrap">')

    out.append('<h3 class="h3 rv" id="own">직접 만든 것</h3>')
    out.append('<p class="body-p rv">회사 업무가 아니라 개인적으로 파고들어 만든 작업입니다.</p>')
    for w in P["own"]:
        if w.get("draft"):          # 준비 중인 항목은 아직 싣지 않는다
            continue
        extra = block(("links", w["links"])) if w["links"] else ""
        if w.get("videos"):
            extra += embeds(w["videos"])
        out.append('<article class="own rv" id="%s"><div class="own-mk">%s</div>'
                   '<div class="own-b"><h4>%s</h4><div class="m">%s</div><p>%s</p></div></article>\n%s'
                   % (e(w["slug"]), e(w.get("mono", "·")), e(w["title"]), e(w["meta"]),
                      e(w["desc"]), extra))

    out.append('<h3 class="h3 rv" id="docs" style="margin-top:46px">기획 문서</h3>')
    out.append('<p class="body-p rv">지난 프로젝트에서 쓴 기획 문서입니다. 구글 드라이브에서 열립니다.</p>')
    out.append(block(("links", [(tag, label, note, url) for tag, label, note, url in P["docs"]])))

    out.append('<h3 class="h3 rv" id="videos" style="margin-top:46px">플레이 영상</h3>')
    out.append('<p class="body-p rv">직접 만든 콘텐츠가 실제로 돌아가는 화면입니다. 여기서 바로 재생됩니다.</p>')
    for group, key, page in P["videos"]:
        out.append('<p class="grp rv">%s <a href="%s" style="color:var(--accent);'
                   'text-transform:none;letter-spacing:0">프로젝트 문서 →</a></p>' % (e(group), e(page)))
        out.append(embeds(C.VIDEOS[key]))

    out.append('</div></section>\n</main>\n')
    out.append(pager(("index.html", "홈"), ("kingsroad.html", "왕좌의 게임: 킹스로드")))
    out.append(foot())
    out.append(tail(with_lightbox=False))
    return "".join(out)


def build_prev_project(p, page, prev, next_):
    out = [head("%s · 손석완 포트폴리오" % p["title"], page["note"]),
           bar("프로젝트"),
           crumb([("index.html", "홈"), ("index.html#projects", "프로젝트"), (None, p["title"])]),
           phero(page["eyebrow"], page["title"], page["tag"], page["note"],
                 cover=p.get("cover"), num=p.get("mono"))]
    out.append('<main>\n<section class="tight"><div class="wrap">')
    out.append(blocks(page["blocks"]))
    out.append('</div></section>\n</main>\n')
    out.append(pager(prev, next_))
    out.append(foot())
    out.append(tail(with_lightbox=False))
    return "".join(out)


# ──────────────────────────────────────────────────────── 실행
def write(name, text):
    text = tokens(text)
    path = os.path.join(ROOT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return "%-24s %6.1f KB  img %d" % (name, len(text.encode("utf-8")) / 1024, text.count("<img "))


def main():
    made = [write("index.html", build_index()),
            write("kingsroad.html", build_kingsroad())]

    # 킹스로드 하위: 콘텐츠 10종 → 레벨 기능 문서
    seq = [("kr-%s.html" % c["slug"], c["title"]) for c in C.CONTENTS]
    seq.append((C.SYSTEMS["page"], "레벨 기능 · 기믹 기획"))
    for i, c in enumerate(C.CONTENTS):
        prev = seq[i - 1] if i else ("kingsroad.html", "왕좌의 게임: 킹스로드")
        made.append(write(seq[i][0], build_content(c, prev, seq[i + 1])))
    made.append(write(C.SYSTEMS["page"], build_systems(seq[-2], ("aura.html", "AI 목업 파이프라인"))))
    made.append(write("aura.html", build_aura()))
    made.append(write("personal.html", build_personal()))

    prevs = [p for p in C.PROJECTS if not p.get("featured")]
    for i, p in enumerate(prevs):
        before = (prevs[i - 1]["page"], prevs[i - 1]["title"]) if i else ("kingsroad.html", "왕좌의 게임: 킹스로드")
        after = (prevs[i + 1]["page"], prevs[i + 1]["title"]) if i + 1 < len(prevs) else ("index.html", "홈")
        made.append(write(p["page"], build_prev_project(p, C.PREV_PAGES[p["slug"]], before, after)))

    print("\n".join(made))
    print("총 %d 페이지" % len(made))


if __name__ == "__main__":
    main()
