# -*- coding: utf-8 -*-
"""웹 포트폴리오 전체를 PDF 한 권으로 굽는다 — 파일 첨부만 받는 구직 사이트용.

    python3 src/sitepdf.py [출력 경로]

빌드된 html 을 로컬 서버로 띄워 크로미움으로 한 페이지씩 인쇄하고 하나로 합친다.
화면 모양 그대로(screen 미디어) 찍고, 다음을 손본다.
  - 사이트 안 링크는 실제 배포 주소로 바꾼다 — PDF 에서 눌러도 웹 문서가 열린다.
  - 유튜브 영상과 페이지 안 기획서(iframe)는 PDF 에서 돌지 않으므로 누르면 열리는
    링크 카드로 바꾼다.
  - 숫자 롤링 · 스크롤 등장 효과는 끄고(reduced motion) 처음부터 다 보이게 한다.
  - 문서마다 책갈피를 단다.
"""
import asyncio
import functools
import http.server
import io
import os
import sys
import threading

import pymupdf
from PIL import Image
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as C                                   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get("SITE_URL", "https://portfolio-web-production-8817.up.railway.app").rstrip("/")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "_paper", "손석완_포트폴리오.pdf")
W, H = 1200, 1697                      # A4 비율, 화면 폭 1200px

FIX_CSS = """
.bar{position:static!important}
*{filter:none!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
#themeBtn,.ed-bar,.ed-modal,.ed-toast,.ed-out,.lb{display:none!important}
.rv{opacity:1!important;transform:none!important}
figure,.ccard,.pcard,.card,.kv-row,.stat,.play,.lnk,.shot,.banner,.goal,.tl li,.slot h3{break-inside:avoid}
h2,h3,.h3,.eyebrow{break-after:avoid}
.pdf-link{display:flex;align-items:center;gap:14px;padding:18px 20px;margin-top:22px;
  border:1px solid var(--line);border-radius:var(--r);background:var(--surface);
  text-decoration:none;color:var(--ink);break-inside:avoid}
.pdf-link b{font-size:15px}.pdf-link span{color:var(--ink3);font-size:13px}
.pdf-link i{font-style:normal;margin-left:auto;color:var(--accent-ink);font-weight:700;white-space:nowrap}
"""

FIX_JS = """(site) => {
  document.querySelectorAll('.rv').forEach(e => e.classList.add('in'));
  document.querySelectorAll('img[loading]').forEach(i => i.loading = 'eager');
  // 유튜브 → 링크 카드
  document.querySelectorAll('figure.vfig').forEach(f => {
    const id = f.dataset.yt; if (!id) return;
    const cap = f.querySelector('figcaption');
    const title = cap ? (cap.querySelector('b') || cap).textContent.trim() : '영상';
    const a = document.createElement('a');
    a.className = 'pdf-link'; a.href = 'https://youtu.be/' + id;
    a.innerHTML = '<div><b>▶ ' + title + '</b><br><span>youtu.be/' + id + '</span></div><i>영상 보기 ↗</i>';
    f.replaceWith(a);
  });
  // 페이지 안 기획서 → 링크 카드 (배포 주소로)
  document.querySelectorAll('figure.frame').forEach(f => {
    const fr = f.querySelector('iframe'); const t = f.querySelector('.frame-bar b');
    const a = document.createElement('a');
    a.className = 'pdf-link'; a.href = site + '/' + fr.getAttribute('src');
    a.innerHTML = '<div><b>' + (t ? t.textContent : '문서') + '</b><br><span>인터랙티브 문서라 웹에서 열립니다</span></div><i>웹에서 보기 ↗</i>';
    f.replaceWith(a);
  });
  // 페이지에 직접 넣은 mp4 → 링크 카드 (PDF 에서는 재생되지 않는다)
  document.querySelectorAll('video').forEach(v => {
    const f = v.closest('figure') || v;
    const cap = f.querySelector('figcaption');
    const a = document.createElement('a');
    a.className = 'pdf-link'; a.href = site + '/' + location.pathname.replace(/^\//, '');
    a.innerHTML = '<div><b>▶ ' + (cap ? cap.textContent.trim() : '영상') + '</b><br><span>영상은 웹 페이지에서 재생됩니다</span></div><i>웹에서 보기 ↗</i>';
    f.replaceWith(a);
  });
  // 사이트 안 링크 → 배포 주소
  document.querySelectorAll('a[href]').forEach(a => {
    const h = a.getAttribute('href');
    if (!h || /^(https?:|mailto:|tel:|#|javascript:)/.test(h)) return;
    a.href = site + '/' + h.replace(/^\\.\\//, '');
  });
}"""


def pages():
    """책 순서 — 홈 · 킹스로드와 하위 문서 · 다른 프로젝트 · 개인 작품."""
    out = [("index.html", "홈")]
    for p in C.PROJECTS:
        out.append((p["page"], p["title"]))
        if p["slug"] == "kingsroad":
            out += [("kr-%s.html" % c["slug"], "  " + c["title"]) for c in C.CONTENTS]
            out.append((C.SYSTEMS["page"], "  " + C.SYSTEMS["title"]))
    out.append(("personal.html", "개인 작품"))
    out += [(w["page"], "  " + w["title"]) for w in C.PERSONAL["own"] if not w.get("draft")]
    seen, res = set(), []
    for f, t in out:
        if f not in seen and os.path.exists(os.path.join(ROOT, f)):
            seen.add(f); res.append((f, t))
    return res


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    h.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


async def main():
    srv = serve()
    base = "http://127.0.0.1:%d" % srv.server_address[1]
    tmp = os.path.join(os.path.dirname(OUT), "_sitepdf")
    os.makedirs(tmp, exist_ok=True)
    parts = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        ctx = await b.new_context(viewport={"width": W, "height": 1000}, reduced_motion="reduce")
        async def route(r):
            url = r.request.url
            if not url.startswith(base):                     # 바깥 요청(유튜브 등)은 막는다
                return await r.abort()
            path = os.path.join(ROOT, url[len(base) + 1:].split("?")[0])
            if path.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) and os.path.exists(path):
                # PDF 가 무거워지지 않게, 브라우저에 넘기기 전에 줄여서 JPEG 로
                im = Image.open(path)
                if im.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", im.size, (12, 15, 20) if "cov" in path else (255, 255, 255))
                    im = im.convert("RGBA"); bg.paste(im, mask=im.split()[-1]); im = bg
                im = im.convert("RGB"); im.thumbnail((1200, 1200))
                buf = io.BytesIO(); im.save(buf, "JPEG", quality=68, optimize=True)
                return await r.fulfill(body=buf.getvalue(), content_type="image/jpeg")
            await r.continue_()
        await ctx.route("**/*", route)
        pg = await ctx.new_page()
        for i, (f, title) in enumerate(pages()):
            await pg.goto("%s/%s" % (base, f), wait_until="networkidle")
            await pg.add_style_tag(content=FIX_CSS)
            await pg.evaluate(FIX_JS, SITE)
            await pg.evaluate("Promise.all([...document.images].map(i => i.complete ? 0 : "
                              "new Promise(r => { i.onload = i.onerror = r; })))")
            await pg.emulate_media(media="screen")
            path = os.path.join(tmp, "%02d.pdf" % i)
            await pg.pdf(path=path, width="%dpx" % W, height="%dpx" % H, print_background=True,
                         margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
            parts.append((path, title))
            print("%-24s %s" % (f, title.strip()))
        await b.close()
    srv.shutdown()

    book, toc = pymupdf.open(), []
    for path, title in parts:
        d = pymupdf.open(path)
        toc.append([2 if title.startswith("  ") else 1, title.strip(), book.page_count + 1])
        book.insert_pdf(d)
    book.set_toc(toc)
    book.set_metadata({"title": "손석완 레벨 디자이너 포트폴리오", "author": C.SITE["name"]})
    # rewrite_images 는 배경 그림(패턴)을 깨뜨리므로 쓰지 않는다 — 크기는 위에서 줄였다
    book.save(OUT, garbage=4, deflate=True, use_objstms=1)
    print("\n%s  %d쪽  %.1f MB" % (OUT, book.page_count, os.path.getsize(OUT) / 1e6))


if __name__ == "__main__":
    asyncio.run(main())
