# -*- coding: utf-8 -*-
"""카드·히어로용 커버 이미지 생성.

원본(img/*.jpg)에서 16:9 로 센터 크롭해 webp 로 굽는다.
결과는 img/cov/ 에 들어가고, 페이지에서 카드 썸네일·히어로 배경으로 쓴다.

    python3 src/covers.py
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
OUT = os.path.join(IMG, "cov")

# 커버 이름 → (원본 파일, 세로 포커스 0=위 .5=중앙 1=아래)
CARDS = {
    "kingsroad":   ("02-final-10.jpg", 0.45),
    "last-hearth": ("01-final-05.jpg", 0.5),
    "oldtown":     ("02-final-05.jpg", 0.5),
    "highgarden":  ("03-final-04.jpg", 0.5),
    "crows-nest":  ("04-final-05.jpg", 0.5),
    "griffin":     ("05-final-03.jpg", 0.5),
    "kraken":      ("06-final-02.jpg", 0.5),
    "beyond-wall": ("07-final-02.jpg", 0.5),
    "mammoth":     ("redacted/08.webp", 0.5),   # 목업은 대외비 — 블러본 사용
    "harrenhal":   ("redacted/09.webp", 0.5),   # 목업은 대외비 — 블러본 사용
    "systems":     ("04-final-12.jpg", 0.5),
    "aura":        ("aura_08.png", 0.5),
    # 아래 넷은 2022 경력기술서(엑셀)에 들어 있던 공식 이미지, zeta 는 사용자가 준 포스터.
    # 원본은 배포되지 않는 src/media/ 에 둔다.
    "nanolegend":  ("../src/media/nanolegend-store.jpg", 0.5),
    "minimax":     ("../src/media/minimax-promo.jpg", 0.5),
    "kuf2":        ("../src/media/kuf2-art.jpg", 0.42),
    "offindustry": ("../src/media/offindustry.jpg", 0.5),
    "zeta":        ("../src/media/zeta-poster.png", 0.5),
    # 캐시아웃은 직접 만든 게임이라 실제 플레이 화면(그래프)을 잘라 쓴다
    "cashout":     ("../src/media/cashout-chart.png", 0.5),
}

# 히어로 배경 (가로로 더 길게)
HEROES = {
    "home":      ("02-final-10.jpg", 0.45),
    "kingsroad": ("03-final-01.jpg", 0.42),
}

CARD_W, CARD_H = 1000, 563       # 16:9
HERO_W, HERO_H = 2000, 900       # 20:9


def crop(src, w, h, focus):
    im = Image.open(src).convert("RGB")
    sw, sh = im.size
    want = w / h
    have = sw / sh
    if have > want:                       # 원본이 더 넓다 → 좌우 자름
        nw = int(sh * want)
        x = (sw - nw) // 2
        im = im.crop((x, 0, x + nw, sh))
    else:                                 # 원본이 더 높다 → 상하 자름
        nh = int(sw / want)
        y = int((sh - nh) * focus)
        im = im.crop((0, y, sw, y + nh))
    return im.resize((w, h), Image.LANCZOS)


def avatar():
    """상단 바 로고와 파비콘 — 프로필 사진을 얼굴 중심으로 정사각 크롭."""
    src = os.path.join(ROOT, "src", "media", "profile.png")
    if not os.path.exists(src):
        src = os.path.join(IMG, "profile.webp")
    im = Image.open(src).convert("RGB")
    w, h = im.size
    # 원형 마스크를 씌우므로 턱까지 원 안에 들어오도록 넉넉히 잡는다
    side = int(w * 0.88)
    x = (w - side) // 2
    y = int(h * 0.02)
    face = im.crop((x, y, x + side, min(y + side, h)))
    face.resize((96, 96), Image.LANCZOS).save(os.path.join(IMG, "avatar.webp"),
                                              "WEBP", quality=88, method=6)
    face.resize((64, 64), Image.LANCZOS).save(os.path.join(IMG, "favicon.png"),
                                              "PNG", optimize=True)
    print("avatar  img/avatar.webp · img/favicon.png")


def main():
    os.makedirs(OUT, exist_ok=True)
    avatar()
    total = 0
    for name, (src, focus) in sorted(CARDS.items()):
        p = os.path.join(OUT, name + ".webp")
        crop(os.path.join(IMG, src), CARD_W, CARD_H, focus).save(p, "WEBP", quality=72, method=6)
        total += os.path.getsize(p)
        print("card  %-14s %-16s %6.1f KB" % (name, src, os.path.getsize(p) / 1024))
    for name, (src, focus) in sorted(HEROES.items()):
        p = os.path.join(OUT, "hero-" + name + ".webp")
        crop(os.path.join(IMG, src), HERO_W, HERO_H, focus).save(p, "WEBP", quality=64, method=6)
        total += os.path.getsize(p)
        print("hero  %-14s %-16s %6.1f KB" % (name, src, os.path.getsize(p) / 1024))
    print("합계 %.1f KB" % (total / 1024))


if __name__ == "__main__":
    main()
