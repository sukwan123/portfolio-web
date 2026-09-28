# -*- coding: utf-8 -*-
"""_paper/ 의 html 을 A4 PDF 로 인쇄한다 (src/paper.py 가 이어서 부른다).

크로미움으로 찍으므로 문서 안의 <a> 가 PDF 에서도 눌리는 링크로 남는다.
여백은 html 쪽 @page 가 정하므로 여기서는 0 으로 둔다.

파일 이름에 버전과 날짜를 붙인다 — 손석완_자기소개서_v3_260928.pdf
받는 쪽에서 같은 이름으로 덮어쓰지 않게 하려는 것이다. 내용(html)이 지난
버전과 같으면 새 버전을 만들지 않는다. 기록은 _paper/versions.json 에 있다.
"""
import asyncio
import datetime
import hashlib
import json
import os

from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_paper")
LOG = os.path.join(OUT, "versions.json")
DOCS = {"resume.html": "이력서", "letter.html": "자기소개서"}


def load():
    try:
        with open(LOG, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


async def main():
    log = load()
    today = datetime.date.today().strftime("%y%m%d")
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page()
        for src, name in DOCS.items():
            path = os.path.join(OUT, src)
            if not os.path.exists(path):
                continue
            with open(path, "rb") as f:
                digest = hashlib.sha1(f.read()).hexdigest()
            hist = log.setdefault(name, [])
            if hist and hist[-1]["hash"] == digest and os.path.exists(
                    os.path.join(OUT, hist[-1]["file"])):
                print("%-30s 변경 없음" % hist[-1]["file"])
                continue
            v = hist[-1]["v"] + 1 if hist else 1
            dst = "손석완_%s_v%d_%s.pdf" % (name, v, today)
            await pg.goto("file://" + path)
            await pg.emulate_media(media="print")
            await pg.pdf(path=os.path.join(OUT, dst), format="A4", print_background=True,
                         margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
            hist.append({"v": v, "date": today, "hash": digest, "file": dst})
            print("%-30s %6.0f KB  (새 버전)" % (dst, os.path.getsize(os.path.join(OUT, dst)) / 1024))
        await b.close()
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    asyncio.run(main())
