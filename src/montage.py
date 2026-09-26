# -*- coding: utf-8 -*-
"""대외비 자료(평면도 · 목업)를 블러 몽타주로 굽는다.

    python3 src/montage.py

평면도와 목업은 회사 대외비라 배포본에 원본을 두지 않는다. 지역별로 모아
한 장의 몽타주로 합치고, 되돌릴 수 없게 뭉갠 뒤 img/redacted/ 에 저장한다.
CSS 필터로 가리는 방식은 원본 파일이 그대로 내려받아지므로 쓰지 않는다.

가리는 대상은 글씨(지명·수치·주석)다. 동선과 공간 구조는 보여야 작업물 구실을
하므로, 글씨가 읽히지 않는 선까지만 뭉갠다.

  1) 타일 박스 크기로 축소   — 원본 대비 3~4배 축소라 여기서 이미 잔글씨가 사라진다
  2) 절반 크기로 한 번 더    — 남은 큰 글씨까지 버린다. 잃은 정보는 돌아오지 않는다
  3) 약한 가우시안 블러      — 축소 격자를 지운다

원본은 이 저장소에 없다. 다시 구우려면 원본을 아무 데나 풀고 위치를 넘긴다.

    MONTAGE_SRC=/path/to/originals python3 src/montage.py
"""
import math
import os

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
SRC = os.environ.get("MONTAGE_SRC") or IMG      # 원본 위치
OUT = os.path.join(IMG, "redacted")

WIDTH = 1600          # 몽타주 가로 (표시 폭 1000px 의 1.6배)
SCALE = 0.5           # 타일 너비의 이 비율까지 줄였다 되돌린다
BLUR = 3.5            # 가우시안 블러 반경(px) — 축소 격자를 지울 만큼만
BG = (22, 26, 32)     # 빈칸·여백 색


def tiles_for(n):
    if n <= 2:
        return n
    return 3 if n <= 12 else 4


def redact_tile(im, tw, th):
    """타일 한 장에서 글씨를 지운다 — 축소 → 확대 → 약한 블러."""
    small = im.resize((max(int(tw * SCALE), 24), max(int(th * SCALE), 14)), Image.BILINEAR)
    back = small.resize((tw, th), Image.BICUBIC)
    return back.filter(ImageFilter.GaussianBlur(radius=BLUR))


def fit(f, tw, th):
    """타일 박스를 채운다. 목업(가로 스샷)은 센터 크롭, 평면도는 세로라 통째로 넣는다."""
    im = Image.open(f).convert("RGB")
    if "-plan" in os.path.basename(f):
        box = Image.new("RGB", (tw, th), BG)
        im.thumbnail((tw, th), Image.LANCZOS)
        box.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
        return box
    want, (w, h) = tw / th, im.size
    if w / h > want:
        nw = int(h * want)
        return im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    nh = int(w / want)
    return im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


def montage(files, width=WIDTH):
    cols = tiles_for(len(files))
    rows = math.ceil(len(files) / cols)
    tw = width // cols
    th = int(tw * 9 / 16)
    canvas = Image.new("RGB", (width, th * rows), BG)
    for r in range(rows):
        band = files[r * cols:(r + 1) * cols]
        x0 = (width - len(band) * tw) // 2   # 모자라는 마지막 줄은 가운데로
        for i, f in enumerate(band):
            canvas.paste(redact_tile(fit(f, tw, th), tw, th), (x0 + i * tw, r * th))
    return canvas


def main():
    os.makedirs(OUT, exist_ok=True)
    nums = sorted({f.split("-")[0] for f in os.listdir(SRC)
                   if "-plan" in f or "-mock" in f})
    if not nums:
        print("%s 에 평면도·목업 원본이 없다. MONTAGE_SRC 로 원본 위치를 넘길 것." % SRC)
        return
    for num in nums:
        files = [os.path.join(SRC, f) for f in os.listdir(SRC)
                 if f.startswith(num + "-plan") or f.startswith(num + "-mock")]
        # 평면도를 맨 앞에 — 지역을 한눈에 보여주는 자료라 먼저 온다
        files.sort(key=lambda p: ("-plan" not in os.path.basename(p), p))
        out = os.path.join(OUT, "%s.webp" % num)
        montage(files).save(out, "WEBP", quality=70, method=6)
        print("%s  %2d장 → %s  %.0f KB" % (num, len(files), os.path.basename(out),
                                          os.path.getsize(out) / 1024))


if __name__ == "__main__":
    main()
