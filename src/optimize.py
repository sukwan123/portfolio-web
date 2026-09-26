# -*- coding: utf-8 -*-
import os, io
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
SRC = r"C:\Users\n-suk\ForClaude\LevelDesign_Portfolio\images"
DST = r"C:\Users\n-suk\ForClaude\_web\img"
os.makedirs(DST, exist_ok=True)

def target(name, w, h):
    # 평면도 = 확대해서 읽어야 하므로 크게 유지
    if "_평면도" in name:      return 2800, 88
    if "인포그래픽" in name:    return 2600, 92
    return 1600, 84            # 목업 · 실작업

tot_in = tot_out = 0
n = 0
for f in sorted(os.listdir(SRC)):
    sp = os.path.join(SRC, f)
    si = os.path.getsize(sp); tot_in += si
    im = Image.open(sp)
    im = im.convert("RGB")
    w, h = im.size
    lim, q = target(f, w, h)
    long_edge = max(w, h)
    if long_edge > lim:
        sc = lim / long_edge
        im = im.resize((round(w*sc), round(h*sc)), Image.LANCZOS)
    base = os.path.splitext(f)[0] + ".jpg"
    op = os.path.join(DST, base)
    im.save(op, "JPEG", quality=q, optimize=True, progressive=True, subsampling=1)
    so = os.path.getsize(op); tot_out += so
    n += 1
    if n % 20 == 0: print("  ...%d장" % n)
print("완료: %d장  %.1fMB -> %.1fMB (%.0f%% 절감)" % (
    n, tot_in/1024/1024, tot_out/1024/1024, 100*(1-tot_out/tot_in)))
