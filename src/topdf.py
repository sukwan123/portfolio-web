# -*- coding: utf-8 -*-
"""_paper/ 의 html 을 A4 PDF 로 인쇄한다 (src/paper.py 가 이어서 부른다).

크로미움으로 찍으므로 문서 안의 <a> 가 PDF 에서도 눌리는 링크로 남는다.
여백은 html 쪽 @page 가 정하므로 여기서는 0 으로 둔다.
"""
import asyncio
import os

from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_paper")
NAMES = {"resume.html": "손석완_이력서.pdf", "letter.html": "손석완_자기소개서.pdf"}


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page()
        for src, dst in NAMES.items():
            path = os.path.join(OUT, src)
            if not os.path.exists(path):
                continue
            await pg.goto("file://" + path)
            await pg.emulate_media(media="print")
            out = os.path.join(OUT, dst)
            await pg.pdf(path=out, format="A4", print_background=True,
                         margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
            print("%-22s %6.0f KB" % (dst, os.path.getsize(out) / 1024))
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
