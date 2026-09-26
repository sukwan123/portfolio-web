# -*- coding: utf-8 -*-
"""대외비 자료(평면도 · 목업)를 블러 몽타주로 굽는다.

    python3 src/montage.py

평면도와 목업은 회사 대외비라 배포본에 원본을 두지 않는다. 지역별로 모아
한 장의 몽타주로 합치고, 되돌릴 수 없게 뭉갠 뒤 img/redacted/ 에 저장한다.
CSS 필터로 가리는 방식은 원본 파일이 그대로 내려받아지므로 쓰지 않는다.

뭉개는 방법 (셋을 겹쳐 복원 불가):
  1) 타일마다 22px 폭까지 축소 — 정보 자체를 버린다 (장수와 무관하게 같은 강도)
  2) 다시 확대                — 잃은 정보는 돌아오지 않는다
  3) 가우시안 블러             — 축소 격자와 타일 경계를 지운다

원본은 이 저장소에 없다. 다시 구우려면 원본 저장소(LevelDesign_Portfolio)의
평면도·목업을 img/ 에 되돌려 놓고 실행할 것.
"""
import math
import os

from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
OUT = os.path.join(IMG, "redacted")

WIDTH = 1400          # 몽타주 가로
TILE_PX = 22          # 타일 하나를 이 너비까지 줄였다 되돌린다 (장수와 무관하게 같은 강도)


def tiles_for(n):
    if n <= 2:
        return n
    if n <= 6:
        return 3
    return 5


def redact_tile(im, tw, th):
    """타일 한 장을 복원 불가하게 뭉갠다 — 축소 → 확대 → 블러."""
    small = im.resize((TILE_PX, max(int(TILE_PX * th / tw), 6)), Image.BILINEAR)
    back = small.resize((tw, th), Image.BICUBIC)
    return back.filter(ImageFilter.GaussianBlur(radius=max(tw / 26, 8)))


def montage(files, width=WIDTH):
    cols = tiles_for(len(files))
    rows = math.ceil(len(files) / cols)
    tw = width // cols
    th = int(tw * 9 / 16)
    canvas = Image.new("RGB", (tw * cols, th * rows), (22, 26, 32))
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB")
        want = tw / th                       # 타일 박스에 맞춰 센터 크롭
        w, h = im.size
        if w / h > want:
            nw = int(h * want)
            im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w / want)
            im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        canvas.paste(redact_tile(im, tw, th), ((i % cols) * tw, (i // cols) * th))
    # 타일 경계까지 부드럽게
    return canvas.filter(ImageFilter.GaussianBlur(radius=max(tw / 60, 4)))


def main():
    os.makedirs(OUT, exist_ok=True)
    nums = sorted({f.split("-")[0] for f in os.listdir(IMG)
                   if "-plan" in f or "-mock" in f})
    if not nums:
        print("img/ 에 평면도·목업 원본이 없다. 원본 저장소에서 되돌려 놓고 실행할 것.")
        return
    for num in nums:
        files = sorted(os.path.join(IMG, f) for f in os.listdir(IMG)
                       if f.startswith(num + "-plan") or f.startswith(num + "-mock"))
        out = os.path.join(OUT, "%s.webp" % num)
        montage(files).save(out, "WEBP", quality=70, method=6)
        print("%s  %2d장 → %s  %.0f KB" % (num, len(files), os.path.basename(out),
                                          os.path.getsize(out) / 1024))


if __name__ == "__main__":
    main()
