"""Texturas procedurales (pixel art) con la paleta de las imágenes de referencia."""
import math
import os
import random
from PIL import Image
from common import *


class Sheet:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((int(x), int(y)), c if len(c) == 4 else (*c, 255))

    def rect(self, x, y, w, h, fn):
        for j in range(int(h)):
            for i in range(int(w)):
                self.px(x + i, y + j, fn(i, j))

    def box(self, u, v, w, h, d, faces):
        w, h, d = int(math.ceil(w)), int(math.ceil(h)), int(math.ceil(d))
        lay = {
            "top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d),
            "right": (u, v + d, d, h), "front": (u + d, v + d, w, h),
            "left": (u + d + w, v + d, d, h), "back": (u + 2 * d + w, v + d, w, h),
        }
        for name, (x, y, fw, fh) in lay.items():
            fn = faces.get(name) or faces.get("all")
            if fn:
                self.rect(x, y, fw, fh, lambda i, j, fn=fn, fw=fw, fh=fh: fn(i, j, fw, fh))


DEF = dict(skin=SKIN, hair=(44, 24, 20), eye=RED_X, tunic=(100, 22, 26), tunic2=(60, 14, 18), trim=GOLD,
           pants=(40, 14, 16), boots=(24, 10, 12), gear="none", plate=None, robe=None, cape=None,
           hood=(52, 12, 14), helm=CHAR, bare=False, quiver=(70, 40, 30))

SPEC = {
    "civil_comun": dict(),
    "aldeano_nether": dict(tunic=(122, 52, 30), tunic2=(80, 32, 22), hair=(30, 20, 18), pants=(56, 26, 22), gear="hood"),
    "guerrero": dict(tunic=(58, 14, 18), plate=CHAR, gear="helm", pants=(30, 12, 14), boots=BLACK, helm=CHAR),
    "arquero": dict(tunic=(70, 16, 18), gear="hood", hood=(52, 12, 14), pants=(34, 12, 14)),
    "mago": dict(tunic=(30, 10, 14), tunic2=(18, 6, 8), trim=RED_L, robe=(24, 8, 10), cape=(34, 10, 14), pants=(20, 8, 10)),
    "summoner": dict(tunic=(22, 8, 12), tunic2=(14, 4, 8), robe=(30, 10, 16), cape=(40, 12, 20), trim=RED_L,
                     eye=(255, 130, 30), pants=(16, 6, 10)),
    "sacerdote": dict(tunic=(120, 20, 26), robe=(100, 16, 22), cape=(60, 10, 14), trim=GOLD, gear="hood", hood=(74, 12, 16)),
    "noble": dict(tunic=(26, 10, 14), robe=(36, 12, 16), cape=(120, 14, 24), trim=GOLD, hair=(20, 10, 10), pants=(20, 8, 10)),
    "guardia_real": dict(tunic=(110, 18, 24), plate=(104, 18, 24), gear="helm", helm=(104, 18, 24), trim=GOLD,
                         pants=(40, 12, 14), boots=BLACK),
    "caballero_rubi": dict(tunic=(60, 12, 16), plate=(66, 12, 18), gear="helm", helm=(66, 12, 18), trim=GOLD,
                           cape=(130, 16, 26), pants=(30, 10, 12), boots=BLACK),
    "arquero_elite": dict(tunic=(36, 10, 14), gear="hood", hood=(28, 8, 12), cape=(60, 12, 18), trim=GOLD,
                          pants=(24, 8, 10), eye=(255, 90, 30)),
    "mago_batalla": dict(tunic=(60, 14, 18), robe=(44, 10, 14), cape=(80, 14, 20), plate=CHAR, trim=GOLD, pants=(30, 10, 12),
                         gear="helm_open", helm=CHAR),
    "berserker": dict(bare=True, hair=(22, 10, 10), pants=(50, 14, 16), plate=(70, 20, 22), trim=GOLD_D, boots=BLACK),
    "sacerdote_supremo": dict(tunic=(40, 10, 14), robe=(52, 10, 16), cape=(140, 16, 28), trim=GOLD,
                              plate=(150, 108, 28), pants=(30, 8, 10), eye=(255, 220, 90)),
    "alma_nether": dict(skin=(150, 215, 235), hair=(80, 160, 200), eye=(230, 255, 255), tunic=(40, 120, 165),
                        tunic2=(24, 80, 120), trim=(210, 245, 255), pants=(24, 70, 110), boots=(16, 50, 90)),
}
CLEAR = (0, 0, 0, 0)


def spec_for(tid):
    s = dict(DEF)
    s.update(SPEC[tid])
    return s


def paint_humanoid(tid, cubes, seed):
    s = spec_for(tid)
    rnd = random.Random(seed)
    sh = Sheet(128, 128)
    J = lambda c, a=7: jit(c, rnd, a)
    trim, hair, skin = s["trim"], s["hair"], s["skin"]
    solid = lambda c, a=7: (lambda i, j, w, h: J(c, a))
    clr = lambda *a: CLEAR

    for c in cubes:
        k, (u, v), (w, h, d) = c["kind"], c["uv"], c["size"]
        F = {}
        if k == "head":
            def front(i, j, fw, fh):
                if j < 2 or (i in (0, 7) and j < 5):
                    return J(hair)
                if j == 3 and i in (1, 2, 5, 6):
                    return J(mix(skin, BLACK, 0.55), 3)
                if j == 4 and i in (1, 2, 5, 6):
                    return (*s["eye"], 255)
                if j == 6 and i in (3, 4):
                    return J(mix(skin, BLACK, 0.25), 3)
                return J(skin, 5)
            F = {"top": solid(hair), "bottom": solid(skin, 5), "back": solid(hair), "front": front,
                 "right": lambda i, j, fw, fh: J(hair) if (j < 3 or i >= fw - 3) else J(skin, 5),
                 "left": lambda i, j, fw, fh: J(hair) if (j < 3 or i <= 2) else J(skin, 5)}
        elif k == "hat":
            g = s["gear"]
            if g in ("helm", "helm_open"):
                hc = s["helm"]

                def hfront(i, j, fw, fh, hc=hc, g=g):
                    if j == 0:
                        return J(trim, 4)
                    if i in (0, 7):
                        return J(mix(hc, BLACK, 0.2))
                    if g == "helm_open":
                        return J(hc) if j < 2 else CLEAR
                    if j in (3, 4):
                        return (*s["eye"], 255) if (j == 4 and i in (2, 5)) else (*mix(BLACK, hc, 0.1), 255)
                    if j >= 5:
                        return J(mix(hc, BLACK, 0.15)) if i in (3, 4) or j >= 6 else CLEAR
                    return J(hc)
                F = {"top": solid(trim, 4) if tid in ("guardia_real", "caballero_rubi") else solid(hc),
                     "right": lambda i, j, fw, fh, hc=hc: J(hc), "left": lambda i, j, fw, fh, hc=hc: J(hc),
                     "back": solid(hc), "front": hfront, "bottom": clr}
            elif g == "hood":
                hc = s["hood"]
                F = {"top": solid(hc), "right": solid(hc), "left": solid(hc), "back": solid(hc), "bottom": clr,
                     "front": lambda i, j, fw, fh, hc=hc: J(hc) if (j < 2 or i in (0, 7)) else CLEAR}
        elif k == "body":
            def bfront(i, j, fw, fh):
                if s["bare"]:
                    if j in (9, 10):
                        return J(BLACK, 3)
                    return J(mix(skin, BLACK, 0.2), 5) if (i in (3, 4) and j in (2, 3, 5, 6)) else J(skin, 5)
                if j in (9, 10):
                    return J(trim, 4) if (j == 9 and i in (3, 4)) else J(BLACK, 3)
                if j == 2 and i in (3, 4):
                    return (*RED_X, 255)
                if i in (3, 4):
                    return J(trim, 5)
                return J(s["tunic"] if (i + j) % 5 else s["tunic2"], 6)
            base = skin if s["bare"] else s["tunic"]
            F = {"all": solid(base, 6), "front": bfront}
        elif k == "jacket":
            if s["bare"]:
                F = {"front": lambda i, j, fw, fh: J(s["plate"], 4) if ((i == j or i == 7 - j) and j < 8) else CLEAR,
                     "all": clr}
            elif s["plate"]:
                pc = s["plate"]

                def jfront(i, j, fw, fh, pc=pc):
                    if j < 9 and (j in (0, 8) or i in (0, 7)):
                        return J(trim, 4)
                    if j < 8:
                        return J(mix(pc, WHITE, 0.08) if (i + j) % 2 else pc, 4)
                    return CLEAR
                F = {"front": jfront, "all": lambda i, j, fw, fh, pc=pc: J(pc) if j < 8 else CLEAR,
                     "top": clr, "bottom": clr}
            else:
                F = {"all": clr}
        elif k == "arm":
            def af(i, j, fw, fh):
                if s["bare"]:
                    return J(skin, 5) if j < 9 else J(GOLD_D, 4)
                if j >= 10:
                    return J(skin, 5)
                if j == 9:
                    return J(trim, 4)
                base = s["plate"] or s["robe"] or s["tunic"]
                return J(base, 6)
            F = {"all": af}
        elif k == "sleeve":
            if s["plate"] and not s["bare"]:
                F = {"all": lambda i, j, fw, fh: (J(trim, 4) if j in (0, 6) else J(mix(s["plate"], WHITE, 0.06), 4)) if j < 7 else CLEAR}
            else:
                F = {"all": clr}
        elif k == "leg":
            F = {"all": lambda i, j, fw, fh: J(s["boots"]) if j > 9 else (J(trim, 4) if j == 9 else J(s["pants"], 6))}
        elif k == "pants":
            F = {"all": clr}
        elif k == "crown":
            F = {"all": lambda i, j, fw, fh: J(GOLD_L if (i + j) % 3 == 0 else GOLD, 5)}
        elif k == "gem":
            F = {"all": solid(RED_X, 8)}
        elif k == "hatm":
            F = {"all": solid((24, 8, 12), 5)}
        elif k == "band":
            F = {"all": solid(RED_L, 5)}
        elif k == "horn":
            F = {"all": lambda i, j, fw, fh: J((220, 205, 190) if (i + j) % 3 else (150, 130, 120), 6)}
        elif k == "hood":
            F = {"all": solid(s["hood"], 6)}
        elif k == "cape":
            cc = s["cape"] or s["tunic"]
            F = {"all": lambda i, j, fw, fh, cc=cc: J(trim, 4) if (j >= fh - 2 or i in (0, fw - 1)) else J(cc, 6)}
        elif k == "robe":
            rc = s["robe"] or s["tunic"]
            F = {"all": lambda i, j, fw, fh, rc=rc: J(trim, 4) if (j >= fh - 2 or j == 0) else J(mix(rc, BLACK, 0.2) if i % 3 == 0 else rc, 6)}
        elif k == "quiver":
            F = {"all": solid(s["quiver"], 8)}
        elif k == "arrow":
            F = {"all": solid(WHITE, 8)}
        elif k == "paul":
            pc = s["plate"] or CHAR
            F = {"all": lambda i, j, fw, fh, pc=pc: J(trim, 4) if (i % 3 == 0 or j == 0) else J(pc, 5)}
        if F:
            sh.box(u, v, w, h, d, F)
    return sh.img


DPAL = {
    "dragon_rubi": dict(base=(150, 14, 24), base2=(184, 28, 38), glow=(255, 70, 80), belly=(222, 110, 84), mem=(112, 10, 20),
                        mem2=(200, 30, 44), spike=(255, 80, 96), eye=(255, 230, 90), horn=(60, 20, 24), gp=0.02),
    "dragon_obsidiana": dict(base=(26, 22, 32), base2=(42, 34, 54), glow=(210, 30, 40), belly=(70, 50, 80), mem=(34, 20, 44),
                             mem2=(120, 30, 60), spike=(90, 40, 130), eye=(240, 80, 255), horn=(18, 14, 22), gp=0.03),
    "dragon_fuego": dict(base=(44, 18, 14), base2=(70, 26, 16), glow=(255, 120, 20), belly=(200, 90, 20), mem=(120, 36, 10),
                         mem2=(255, 150, 30), spike=(255, 190, 40), eye=(255, 255, 120), horn=(36, 14, 10), gp=0.08),
    "dragon_hueso": dict(base=(206, 200, 186), base2=(180, 172, 158), glow=(230, 50, 50), belly=(150, 142, 128), mem=(100, 22, 30),
                         mem2=(210, 200, 186), spike=(236, 230, 216), eye=(255, 70, 50), horn=(236, 230, 216), gp=0.01),
}


def paint_dragon(did, cubes, seed):
    p = DPAL[did]
    rnd = random.Random(seed)
    sh = Sheet(512, 512)
    J = lambda c, a=6: jit(c, rnd, a)

    def scales(i, j, fw, fh):
        c = p["base2"] if ((i // 3) + (j // 3)) % 2 == 0 else p["base"]
        if rnd.random() < p["gp"]:
            c = p["glow"]
        return J(c)

    for c in cubes:
        k, (u, v), (w, h, d) = c["kind"], c["uv"], c["size"]
        tag = c.get("tag")
        if k == "mem":
            F = {"all": lambda i, j, fw, fh: J(p["mem2"], 5) if (i % 14 == 0 or (i + j) % 19 == 0) else J(p["mem"], 7)}
        elif k == "head":
            def eye_r(i, j, fw, fh, tag=tag):
                return (*p["eye"], 255) if tag == "main" and i in (fw - 5, fw - 4) and j in (2, 3) else scales(i, j, fw, fh)

            def eye_l(i, j, fw, fh, tag=tag):
                return (*p["eye"], 255) if tag == "main" and i in (4, 5) and j in (2, 3) else scales(i, j, fw, fh)
            F = {"all": scales, "right": eye_r, "left": eye_l}
        elif k == "jaw":
            F = {"all": lambda i, j, fw, fh: J(WHITE) if (j < 1 and i % 2 == 0) else J(p["belly"] if (i % 5 == 0) else p["base"])}
        elif k == "belly":
            F = {"all": lambda i, j, fw, fh: J(p["belly"] if (j % 4) else mix(p["belly"], p["base"], 0.5))}
        elif k == "spike":
            F = {"all": lambda i, j, fw, fh: J(p["spike"], 10)}
        elif k == "horn":
            F = {"all": lambda i, j, fw, fh: J(p["horn"], 6)}
        elif k == "claw":
            F = {"all": lambda i, j, fw, fh: J((30, 24, 24) if did != "dragon_hueso" else (236, 230, 216), 6)}
        elif k == "foot":
            F = {"all": lambda i, j, fw, fh: J(p["base2"], 6)}
        elif k == "wing":
            F = {"all": lambda i, j, fw, fh: J(p["base"] if i % 6 else p["base2"], 6)}
        elif k == "saddle":
            F = {"all": lambda i, j, fw, fh: J(GOLD, 4) if (i in (0, fw - 1) or j in (0, fh - 1)) else J((72, 30, 22), 6)}
        elif k == "armor":
            F = {"all": lambda i, j, fw, fh: J(GOLD, 4) if (i % 8 == 0 or j % 8 == 0) else (J(RED, 6) if (i + j) % 5 else CLEAR),
                 "bottom": lambda *a: CLEAR}
        else:
            F = {"all": scales}
        sh.box(u, v, w, h, d, F)
    return sh.img


# ------------------------------------------------------------------ ítems 16x16
def new16():
    return Image.new("RGBA", (16, 16), CLEAR)


def put(im, x, y, c):
    if 0 <= x < 16 and 0 <= y < 16:
        im.putpixel((x, y), (*c[:3], 255))


def outline(im, col=BLACK):
    src = im.copy()
    for y in range(16):
        for x in range(16):
            if src.getpixel((x, y))[3] == 0:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if (dx or dy) and 0 <= nx < 16 and 0 <= ny < 16 and src.getpixel((nx, ny))[3] > 0:
                            im.putpixel((x, y), (*col, 255))
    return im


GEM = [
    "................",
    "................",
    ".....DDDDDD.....",
    "....DRRLLLRD....",
    "...DRRLLWLLRD...",
    "..DRRRLWLLLRRD..",
    "..DRRRRLLLRRRD..",
    "..DDRRRRRRRRDD..",
    "...DDRRRRRRDD...",
    "....DDRRRRDD....",
    ".....DDRRDD.....",
    "......DDDD......",
    ".......DD.......",
    "................",
    "................",
    "................",
]
PAL = {"D": RED_D, "R": RED, "L": RED_L, "W": (255, 190, 180)}


def from_ascii(rows):
    im = new16()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in PAL:
                put(im, x, y, PAL[ch])
    return im


def item_sword():
    im = new16()
    for k in range(3, 13):
        x, y = 1 + k, 14 - k
        put(im, x, y, RED_L if k > 4 else RED)
        put(im, x + 1, y, RED)
        put(im, x, y + 1, RED_D)
    put(im, 13, 2, (255, 190, 180))
    for (x, y) in [(3, 8), (4, 9), (5, 10), (6, 11), (7, 12)]:
        put(im, x, y, GOLD)
    for (x, y) in [(4, 12), (3, 13)]:
        put(im, x, y, GOLD_D)
    put(im, 2, 14, RED_D)
    put(im, 1, 15, GOLD_D)
    return outline(im)


def item_staff():
    im = new16()
    for k in range(10):
        x, y = 2 + k, 14 - k
        put(im, x, y, (70, 40, 34))
        put(im, x + 1, y, (40, 22, 22))
    for dx in range(3):
        for dy in range(3):
            put(im, 11 + dx, 1 + dy, RED_L if (dx + dy) % 2 else RED)
    put(im, 12, 2, (255, 190, 180))
    put(im, 13, 1, GOLD)
    put(im, 11, 4, GOLD)
    put(im, 10, 5, GOLD)
    return outline(im)


def item_bow(pull=0):
    im = new16()
    cx, cy, r = 11, 11, 9
    pts = [(round(cx + r * math.cos(math.radians(a))), round(cy + r * math.sin(math.radians(a)))) for a in range(180, 271, 4)]
    for (x, y) in pts:
        put(im, x, y, RED)
        put(im, x + 1, y, RED_D)
    put(im, *pts[len(pts) // 2], GOLD)
    a, b = pts[0], pts[-1]
    mid = ((a[0] + b[0]) // 2 + pull, (a[1] + b[1]) // 2 + pull)
    for (p0, p1) in [(a, mid), (mid, b)]:
        n = max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]), 1)
        for t in range(n + 1):
            put(im, round(p0[0] + (p1[0] - p0[0]) * t / n), round(p0[1] + (p1[1] - p0[1]) * t / n), (225, 205, 200))
    if pull:
        for t in range(6):
            put(im, mid[0] - t, mid[1] - t, (200, 190, 180))
    return outline(im)


def armor_icon(kind):
    im = new16()

    def rect(x, y, w, h, c=RED):
        for j in range(h):
            for i in range(w):
                put(im, x + i, y + j, c)

    def clear(x, y, w, h):
        for j in range(h):
            for i in range(w):
                im.putpixel((x + i, y + j), CLEAR)
    if kind == "helmet":
        rect(3, 3, 10, 8); clear(5, 8, 6, 3); rect(7, 1, 2, 3, GOLD); rect(3, 3, 10, 1, GOLD)
    elif kind == "chestplate":
        rect(3, 4, 10, 10); rect(1, 3, 4, 5); rect(11, 3, 4, 5); clear(6, 3, 4, 3)
        rect(7, 6, 2, 7, GOLD); rect(3, 11, 10, 1, GOLD)
    elif kind == "leggings":
        rect(3, 2, 10, 5); rect(3, 7, 4, 7); rect(9, 7, 4, 7); rect(3, 2, 10, 1, GOLD)
    elif kind == "boots":
        rect(2, 8, 5, 5); rect(9, 8, 5, 5); rect(2, 8, 5, 1, GOLD); rect(9, 8, 5, 1, GOLD)
    else:  # armadura de dragón
        rect(2, 5, 12, 7); rect(4, 3, 8, 2, GOLD); rect(2, 8, 12, 1, GOLD); rect(1, 10, 2, 3); rect(13, 10, 2, 3)
    for y in range(16):
        for x in range(16):
            r, g, b, a = im.getpixel((x, y))
            if a and (r, g, b) == RED:
                im.putpixel((x, y), (*mix(RED_L, RED_D, (x + y) / 30.0), 255))
    return outline(im)


def block_ruby():
    rnd = random.Random(11)
    im = new16()
    for y in range(16):
        for x in range(16):
            c = RED if ((x // 4) + (y // 4)) % 2 else (190, 30, 40)
            if x % 4 == 0 or y % 4 == 0:
                c = RED_D
            if x % 4 == 1 and y % 4 == 1:
                c = (255, 150, 150)
            im.putpixel((x, y), jit(c, rnd, 5))
    return im


def block_ore():
    rnd = random.Random(12)
    im = new16()
    for y in range(16):
        for x in range(16):
            im.putpixel((x, y), jit((112, 44, 46) if rnd.random() > 0.3 else (92, 34, 38), rnd, 6))
    for (cx, cy) in [(3, 3), (10, 4), (5, 10), (11, 11), (8, 7)]:
        for (dx, dy) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            im.putpixel((cx + dx, cy + dy), (*(RED_L if (dx + dy) % 2 == 0 else RED), 255))
        im.putpixel((cx, cy), (255, 170, 160, 255))
    return im


def block_lamp():
    rnd = random.Random(13)
    im = new16()
    for y in range(16):
        for x in range(16):
            c = mix((255, 70, 60), (255, 200, 110), max(0.0, 1 - math.hypot(x - 7.5, y - 7.5) / 9))
            if x in (0, 15) or y in (0, 15):
                c = GOLD_D
            elif x in (1, 14) or y in (1, 14):
                c = GOLD
            elif x in (7, 8) or y in (7, 8):
                c = mix(c, GOLD, 0.5)
            im.putpixel((x, y), jit(c, rnd, 4))
    return im


def block_bricks():
    rnd = random.Random(14)
    im = new16()
    for y in range(16):
        for x in range(16):
            row = y // 4
            off = 4 if row % 2 else 0
            mortar = (y % 4 == 3) or ((x + off) % 8 == 7)
            c = (30, 14, 18) if mortar else ((70, 16, 22) if ((x + off) // 8 + row) % 2 else (88, 20, 26))
            im.putpixel((x, y), jit(c, rnd, 5))
    for (x, y) in [(3, 1), (11, 5), (6, 9), (13, 13)]:
        im.putpixel((x, y), (*RED_L, 255))
    return im


def armor_layers():
    rnd = random.Random(21)
    outs = []
    for layer in (1, 2):
        sh = Sheet(64, 32)

        def plate(i, j, w, h):
            c = RED if (i + j) % 3 else (190, 30, 40)
            if i in (0, w - 1) or j in (0, h - 1):
                c = GOLD
            return jit(c, rnd, 8)
        if layer == 1:
            sh.box(0, 0, 8, 8, 8, {"all": plate, "bottom": lambda *a: CLEAR})
            sh.box(16, 16, 8, 12, 4, {"all": plate})
            sh.box(40, 16, 4, 12, 4, {"all": lambda i, j, w, h: plate(i, j, w, h) if j < 6 else CLEAR})
            sh.box(0, 16, 4, 12, 4, {"all": lambda i, j, w, h: jit(BLACK, rnd, 3) if j >= 8 else CLEAR})
        else:
            sh.box(16, 16, 8, 12, 4, {"all": lambda i, j, w, h: plate(i, j, w, h) if j >= 8 else CLEAR})
            sh.box(0, 16, 4, 12, 4, {"all": lambda i, j, w, h: plate(i, j, w, h) if j < 9 else CLEAR})
        outs.append(sh.img)
    return outs


def write_all(h_geo, d_geo):
    tex = os.path.join(ASSETS, "textures")
    for sub in ("entity", "item", "block", "models/armor"):
        os.makedirs(os.path.join(tex, sub), exist_ok=True)
    # las clases (guerrero, arquero, rey necromancer y súbdito) las crean warrior.py, archer.py y necro.py
    # el dragón y su huevo los crea dragon_v2.py
    item = os.path.join(tex, "item")
    # rubí detallado 32x32 dibujado aparte (tools/ref/ruby.png)
    Image.open(os.path.join(HERE, "ref", "ruby.png")).save(os.path.join(item, "ruby.png"))
    item_sword().save(os.path.join(item, "ruby_sword.png"))
    import ruby_bow  # arco recurvo 32x32 con estados de tensado
    ruby_bow.write(item)
    # los íconos de la armadura de rubí los crea armor_items.py
    armor_icon("dragon").save(os.path.join(item, "dragon_armor.png"))
    blk = os.path.join(tex, "block")
    block_ruby().save(os.path.join(blk, "ruby_block.png"))
    block_ore().save(os.path.join(blk, "ruby_ore.png"))
    block_lamp().save(os.path.join(blk, "ruby_lamp.png"))
    block_bricks().save(os.path.join(blk, "ruby_bricks.png"))
    l1, l2 = armor_layers()
    l1.save(os.path.join(tex, "models", "armor", "ruby_layer_1.png"))
    l2.save(os.path.join(tex, "models", "armor", "ruby_layer_2.png"))


def glowmasks():
    """Crea <textura>_glowmask.png: solo los píxeles que brillan (ojos, rubíes, escamas incandescentes)."""
    from PIL import Image
    tex = os.path.join(ASSETS, "textures", "entity")
    # clases: ojos rojos y rubíes del guerrero/arquero; almas cian del súbdito
    rules = {"warrior": lambda r, g, b: r > 200 and g < 70 and b < 70,
             "archer": lambda r, g, b: r > 200 and g < 70 and b < 70,
             "soul_minion": lambda r, g, b: r < 150 and g > 200 and b > 200}
    for name, rule in rules.items():
        im = Image.open(os.path.join(tex, name + ".png")).convert("RGBA")
        out = Image.new("RGBA", im.size, CLEAR)
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = im.getpixel((x, y))
                if a and rule(r, g, b):
                    out.putpixel((x, y), (r, g, b, a))
        out.save(os.path.join(tex, name + "_glowmask.png"))

