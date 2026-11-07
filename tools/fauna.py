"""Fauna del Océano Púrpura: Pez Brasa, Pez Alma y Anguila de Rubí.

Cada pez: modelo GeckoLib (.geo.json, UV de caja), textura pintada por cara, máscara de brillo,
animaciones (nadar, coletear fuera del agua) y proyecto de Blockbench (.bbmodel) para revisarlo.
La cabeza mira al norte (-Z) y la cola al sur (+Z), como el resto de los mobs del mod.
"""
import json
import math
import os
import random

from PIL import Image

from common import ASSETS, save_json
from models import Geo

HERE = os.path.dirname(os.path.abspath(__file__))


# ====================================================================== utilidades
class Atlas:
    """Reparte las cajas en la textura (UV de caja) y pinta cada cara con una función."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.x = self.y = self.row = 0

    def alloc(self, size):
        w, h, d = [math.floor(v) for v in size]
        rw, rh = 2 * d + 2 * w, d + h
        rw, rh = max(rw, 1), max(rh, 1)
        if self.x + rw > self.w:
            self.x, self.y, self.row = 0, self.y + self.row, 0
        u, v = self.x, self.y
        assert v + rh <= self.h, "textura llena"
        self.x += rw
        self.row = max(self.row, rh)
        return u, v

    def paint(self, uv, size, fn):
        u, v = uv
        w, h, d = [math.floor(s) for s in size]
        faces = {"up": (u + d, v, w, d), "down": (u + d + w, v, w, d), "east": (u, v + d, d, h),
                 "north": (u + d, v + d, w, h), "west": (u + d + w, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h)}
        for face, (x0, y0, fw, fh) in faces.items():
            for j in range(fh):
                for i in range(fw):
                    c = fn(face, i, j, fw, fh)
                    if c is not None:
                        self.img.putpixel((x0 + i, y0 + j), tuple(c) if len(c) == 4 else tuple(c) + (255,))


def box(geo, atlas, bone, origin, size, fn, rotation=None, pivot=None, inflate=0.0):
    uv = atlas.alloc(size)
    atlas.paint(uv, size, fn)
    geo.cube(bone, "box", origin, size, uv, inflate=inflate, rotation=rotation, pivot=pivot)


def mix(a, b, t):
    return tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(len(a)))


def jitter(c, rnd, amt=12):
    return tuple(max(0, min(255, v + rnd.randint(-amt, amt))) for v in c[:3]) + tuple(c[3:])


def anim(bones, length, loop=True):
    return {"animation_length": length, "loop": loop, "bones": bones}


def wave(amp, length, steps=8, phase=0.0, axis=1, extra=None):
    """Fotogramas de una oscilación seno (en grados) sobre un eje."""
    fr = {}
    for k in range(steps + 1):
        t = length * k / steps
        a = amp * math.sin(2 * math.pi * k / steps + phase)
        v = [0.0, 0.0, 0.0]
        v[axis] = round(a, 2)
        if extra:
            v = [v[i] + extra[i] for i in range(3)]
        fr["%.2f" % t] = v
    return fr


def glow_from(img, test):
    g = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for y in range(img.height):
        for x in range(img.width):
            c = img.getpixel((x, y))
            if c[3] and test(c):
                g.putpixel((x, y), c)
    return g


# ====================================================================== Pez Brasa
def pez_brasa():
    """Pez rojo-anaranjado con brasas encendidas en el lomo: brilla un poco bajo el agua morada."""
    rnd = random.Random(11)
    g = Geo("geometry.pez_brasa", 32, 32)
    at = Atlas(32, 32)
    RED, DARK, ORANGE, YEL, BELLY = (214, 46, 22), (122, 20, 12), (255, 128, 30), (255, 214, 90), (255, 176, 78)
    EMBER = [(255, 220, 110), (255, 170, 50), (255, 120, 30)]

    def body(face, i, j, fw, fh):
        if face == "up":
            c = DARK if i in (0, fw - 1) else RED
            if (i + j * 2) % 3 == 0 and 0 < i < fw - 1:
                c = EMBER[(i + j) % 3]
            return jitter(c, rnd, 8)
        if face == "down":
            return jitter(BELLY, rnd, 8)
        t = j / max(1, fh - 1)
        c = mix(RED, ORANGE, max(0, t - 0.25) * 1.4) if t < 0.75 else BELLY
        if face in ("east", "west") and j == 1 and i % 2 == 0:
            c = EMBER[(i // 2) % 3]
        if face in ("east", "west") and j == fh // 2 and (i + 1) % 3 == 0:
            c = YEL
        return jitter(c, rnd, 10)

    def head(face, i, j, fw, fh):
        c = mix(RED, ORANGE, j / max(1, fh - 1))
        if face in ("east", "west"):
            ex = fw - 1 if face == "east" else 0
            if j == 0 and i == ex:
                return (20, 6, 6)
            if j == 0 and abs(i - ex) == 1:
                return YEL
        if face == "north" and j == fh - 1:
            c = DARK
        return jitter(c, rnd, 8)

    def fin(face, i, j, fw, fh):
        edge = (j == 0 or i == 0 or i == fw - 1)
        c = mix(ORANGE, YEL, 0.3) if not edge else (210, 60, 20)
        if (i + j) % 3 == 0:
            c = EMBER[0]
        return c + (235,)

    def tail(face, i, j, fw, fh):
        mid = abs(j - (fh - 1) / 2) < 0.8
        if mid and i < 1:
            return ORANGE
        c = mix((230, 80, 20), YEL, i / max(1, fw - 1))
        if i == fw - 1 or j in (0, fh - 1):
            c = (255, 140, 40)
        return c + (230,)

    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 2, 0], "root")
    box(g, at, "body", [-1.5, 0, -3.5], [3, 4, 7], body)
    box(g, at, "body", [-1, 0.5, -5.5], [2, 3, 2], head)
    box(g, at, "body", [0, 4, -2.5], [0, 2, 5], fin)            # aleta del lomo
    box(g, at, "body", [0, -1, -0.5], [0, 1, 3], fin)           # aleta del vientre
    g.bone("fin_left", [1.5, 1, -1.5], "body")
    box(g, at, "fin_left", [1.5, 1, -1.5], [2, 0, 2], fin)
    g.bone("fin_right", [-1.5, 1, -1.5], "body")
    box(g, at, "fin_right", [-3.5, 1, -1.5], [2, 0, 2], fin)
    g.bone("tail", [0, 2, 3.5], "body")
    box(g, at, "tail", [0, -0.5, 3.5], [0, 5, 4], tail)
    anims = {
        "animation.pez_brasa.swim": anim({
            "body": {"rotation": wave(6, 0.8)},
            "tail": {"rotation": wave(28, 0.8, phase=-1.2)},
            "fin_left": {"rotation": wave(18, 0.8, axis=2)},
            "fin_right": {"rotation": wave(-18, 0.8, axis=2)}}, 0.8),
        "animation.pez_brasa.flop": anim({
            "root": {"rotation": {"0.00": [0, 0, 90], "0.40": [0, 0, 90]},
                     "position": {"0.00": [0, 0, 0], "0.20": [0, 1.5, 0], "0.40": [0, 0, 0]}},
            "tail": {"rotation": wave(35, 0.4, steps=4)}}, 0.4),
    }
    glow = glow_from(at.img, lambda c: c[0] > 245 and c[1] > 160)
    return g, at.img, glow, anims


# ====================================================================== Pez Alma
def pez_alma():
    """Pez celeste translúcido, como los súbditos de almas: ojos huecos y una estela de humo de alma en la cola."""
    rnd = random.Random(7)
    g = Geo("geometry.pez_alma", 32, 32)
    at = Atlas(32, 32)
    CORE, SOUL, DEEP, EYE = (210, 255, 255), (96, 232, 236), (36, 150, 176), (18, 34, 70)

    def body(face, i, j, fw, fh):
        cx, cy = (fw - 1) / 2, (fh - 1) / 2
        r = math.hypot((i - cx) / max(1, cx + 0.5), (j - cy) / max(1, cy + 0.5))
        c = mix(CORE, SOUL, min(1, r * 1.1))
        if j == fh - 1 or (face in ("north", "south") and i in (0, fw - 1)):
            c = DEEP
        if face in ("east", "west") and j == fh // 2 and i % 2 == 1:
            c = CORE
        a = 200 if c != DEEP else 230
        return jitter(c, rnd, 6) + (a,)

    def head(face, i, j, fw, fh):
        c = mix(SOUL, CORE, 0.3)
        if face in ("east", "west"):
            ex = fw - 1 if face == "east" else 0
            if j in (0, 1) and abs(i - ex) <= 0:
                return EYE + (255,)
        if face == "north":
            if j == 1 and i in (0, fw - 1):
                return EYE + (255,)          # la "cara" del alma
            if j == fh - 1 and 0 < i < fw - 1:
                return EYE + (255,)          # boca
        if i in (0, fw - 1) and face in ("up", "down"):
            c = DEEP
        return jitter(c, rnd, 5) + (210,)

    def wisp(face, i, j, fw, fh):
        t = i / max(1, fw - 1)
        mid = abs(j - (fh - 1) / 2) / max(1, (fh - 1) / 2)
        if mid > 1 - t * 0.6 + 0.15:
            return None                      # bordes deshilachados
        c = mix(SOUL, CORE, rnd.random() * 0.5)
        return c + (int(210 - 150 * t),)

    def fin(face, i, j, fw, fh):
        return mix(SOUL, CORE, 0.4) + (150,)

    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 2.5, 0], "root")
    box(g, at, "body", [-1.5, 0, -3], [3, 5, 6], body)
    box(g, at, "body", [-1, 0.5, -5], [2, 4, 2], head)
    box(g, at, "body", [0, 5, -2], [0, 2, 4], fin)
    g.bone("fin_left", [1.5, 1.5, -1], "body")
    box(g, at, "fin_left", [1.5, 1.5, -1], [2, 0, 3], fin)
    g.bone("fin_right", [-1.5, 1.5, -1], "body")
    box(g, at, "fin_right", [-3.5, 1.5, -1], [2, 0, 3], fin)
    g.bone("tail", [0, 2.5, 3], "body")
    box(g, at, "tail", [0, -0.5, 3], [0, 6, 4], wisp)
    g.bone("wisp", [0, 2.5, 7], "tail")
    box(g, at, "wisp", [0, 0, 7], [0, 5, 5], wisp)
    anims = {
        "animation.pez_alma.swim": anim({
            "body": {"rotation": wave(5, 1.2), "position": wave(0.5, 1.2, axis=1, phase=1.5)},
            "tail": {"rotation": wave(22, 1.2, phase=-1.0)},
            "wisp": {"rotation": wave(30, 1.2, phase=-2.2)},
            "fin_left": {"rotation": wave(22, 1.2, axis=2)},
            "fin_right": {"rotation": wave(-22, 1.2, axis=2)}}, 1.2),
        "animation.pez_alma.flop": anim({
            "root": {"rotation": {"0.00": [0, 0, 90], "0.50": [0, 0, 90]},
                     "position": {"0.00": [0, 0, 0], "0.25": [0, 1.2, 0], "0.50": [0, 0, 0]}},
            "tail": {"rotation": wave(30, 0.5, steps=4)}, "wisp": {"rotation": wave(40, 0.5, steps=4, phase=-1)}}, 0.5),
    }
    glow = glow_from(at.img, lambda c: c[2] > 200 and c[1] > 200)
    return g, at.img, glow, anims


# ====================================================================== Anguila de Rubí
def anguila_rubi():
    """Anguila larga con escamas de rubí, vientre dorado y una cresta; 5 segmentos que ondulan al nadar."""
    rnd = random.Random(5)
    g = Geo("geometry.anguila_rubi", 64, 32)
    at = Atlas(64, 32)
    R1, R2, R3, GEM, SPARK, GOLD, DARK = (176, 22, 40), (214, 40, 58), (120, 10, 26), (255, 96, 110), (255, 230, 236), (226, 170, 56), (60, 6, 14)

    def scales(face, i, j, fw, fh):
        if face == "down":
            return jitter(GOLD, rnd, 10)
        if face == "up":
            c = R2 if (i + j) % 2 else R1
            if i == fw // 2 and j % 3 == 1:
                c = GEM
            return jitter(c, rnd, 8)
        # costados y frentes: escamas en diagonal, la fila de abajo dorada
        if j == fh - 1:
            return jitter(GOLD, rnd, 10)
        c = (R1, R2, R3)[(i + j) % 3]
        if (i * 3 + j * 5) % 11 == 0:
            c = GEM
        if (i * 7 + j * 3) % 23 == 0:
            c = SPARK
        return jitter(c, rnd, 6)

    def head(face, i, j, fw, fh):
        c = scales(face, i, j, fw, fh)
        if face in ("east", "west"):
            ex = fw - 2 if face == "east" else 1
            if j == 0 and i == ex:
                return (255, 214, 60)        # ojo amarillo
            if j == fh - 1:
                return DARK                  # línea de la boca
        if face == "north":
            if j == fh - 1:
                return DARK
            if j == 0 and i in (0, fw - 1):
                return (255, 214, 60)
        return c

    def jaw(face, i, j, fw, fh):
        if face == "up" and j == 0 and i % 2 == 0:
            return (250, 245, 235)           # dientes
        return jitter(GOLD if face in ("down", "up") else R3, rnd, 8)

    def crest(face, i, j, fw, fh):
        c = mix(GEM, R1, j / max(1, fh - 1))
        if i % 2 == 0 and j == 0:
            return None
        return c + (240,)

    g.bone("root", [0, 0, 0])
    g.bone("head", [0, 1, -6], "root")
    box(g, at, "head", [-2, -0.25, -10], [4, 3, 4], head)
    box(g, at, "head", [-1.5, -1.25, -9.5], [3, 1, 3], jaw)
    box(g, at, "head", [0, 2.75, -9], [0, 2, 3], crest)
    prev, z = "head", -6
    lengths = [5, 5, 5, 5]
    widths = [3, 3, 2, 2]
    for k, (ln, wd) in enumerate(zip(lengths, widths), 1):
        name = "seg%d" % k
        g.bone(name, [0, 1, z], prev)
        h = wd
        box(g, at, name, [-wd / 2, 1.25 - h / 2, z], [wd, h, ln], scales)
        box(g, at, name, [0, 1.25 + h / 2, z + 0.5], [0, 2 if k < 3 else 1, ln - 1], crest)
        prev, z = name, z + ln
    g.bone("tail", [0, 1, z], prev)
    box(g, at, "tail", [0, -0.75, z], [0, 4, 5], crest)
    swim = {}
    for k, name in enumerate(["head", "seg1", "seg2", "seg3", "seg4", "tail"]):
        swim[name] = {"rotation": wave(9 + k * 3, 1.6, steps=12, phase=-k * 0.9)}
    flop = {"root": {"rotation": {"0.00": [0, 0, 90], "0.60": [0, 0, 90]},
                     "position": {"0.00": [0, 0, 0], "0.30": [0, 1, 0], "0.60": [0, 0, 0]}}}
    for k, name in enumerate(["seg1", "seg2", "seg3", "seg4", "tail"]):
        flop[name] = {"rotation": wave(20, 0.6, steps=6, phase=-k * 1.1)}
    anims = {"animation.anguila_rubi.swim": anim(swim, 1.6), "animation.anguila_rubi.flop": anim(flop, 0.6)}
    glow = glow_from(at.img, lambda c: (c[0] > 250 and c[1] < 120) or c[:3] == SPARK or c[:3] == (255, 214, 60))
    return g, at.img, glow, anims


# ====================================================================== Medusa del Vacío
def medusa_vacio():
    """Medusa morada del vacío: campana translúcida con estrellas negras, núcleo que brilla y 8 tentáculos."""
    rnd = random.Random(21)
    g = Geo("geometry.medusa_vacio", 64, 64)
    at = Atlas(64, 64)
    V1, V2, V3, VOID, CORE, PINK = (120, 50, 190), (160, 80, 230), (70, 24, 120), (18, 8, 30), (236, 170, 255), (255, 120, 230)

    def bell(face, i, j, fw, fh):
        if face == "down":
            r = math.hypot(i - (fw - 1) / 2, j - (fh - 1) / 2) / (fw / 2)
            return mix(V3, VOID, 0.3) + (200,) if r > 0.55 else mix(V2, CORE, 0.3) + (210,)
        c = mix(V2, V1, j / max(1, fh - 1))
        if face == "up":
            c = V2
        if rnd.random() < 0.10:
            c = VOID                       # estrellas del vacío
        elif rnd.random() < 0.06:
            c = PINK
        if face in ("north", "south", "east", "west") and j == fh - 1:
            c = PINK if i % 2 == 0 else V3    # borde ondulado
        return jitter(c, rnd, 6) + (190,)

    def cap(face, i, j, fw, fh):
        c = V2 if face != "up" else mix(V2, CORE, 0.25)
        if rnd.random() < 0.12:
            c = VOID
        return jitter(c, rnd, 6) + (200,)

    def core(face, i, j, fw, fh):
        c = CORE if (i + j) % 3 else PINK
        return c + (255,)

    def tentacle(face, i, j, fw, fh):
        t = j / max(1, fh - 1)
        c = mix(V2, PINK, t) if j % 3 else CORE
        return c + (int(220 - 90 * t),)

    def frill(face, i, j, fw, fh):
        if j == fh - 1 and i % 2:
            return None
        return mix(PINK, V2, j / max(1, fh - 1)) + (170,)

    g.bone("root", [0, 0, 0])
    g.bone("bell", [0, 9, 0], "root")
    box(g, at, "bell", [-4, 9, -4], [8, 5, 8], bell)
    box(g, at, "bell", [-3, 14, -3], [6, 2, 6], cap)
    box(g, at, "bell", [-2, 10, -2], [4, 3, 4], core, inflate=-0.1)
    box(g, at, "bell", [-4, 7, -4], [8, 2, 0], frill)           # faldón de la campana
    box(g, at, "bell", [-4, 7, 4], [8, 2, 0], frill)
    box(g, at, "bell", [-4, 7, -4], [0, 2, 8], frill)
    box(g, at, "bell", [4, 7, -4], [0, 2, 8], frill)
    names = []
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        x, z = round(2.6 * math.cos(a), 1), round(2.6 * math.sin(a), 1)
        n = "tentacle%d" % k
        g.bone(n, [x, 9, z], "bell")
        ln = 8 if k % 2 else 10
        box(g, at, n, [x - 0.5, 9 - ln, z - 0.5], [1, ln, 1], tentacle)
        names.append(n)
    g.bone("arm_a", [0, 9, 0], "bell")                          # brazos orales del centro
    box(g, at, "arm_a", [-1, 1, 0], [2, 8, 0], frill)
    box(g, at, "arm_a", [0, 1, -1], [0, 8, 2], frill)
    swim = {"bell": {"scale": {"0.00": [1, 1, 1], "0.60": [0.86, 1.12, 0.86], "1.20": [1.06, 0.94, 1.06], "2.00": [1, 1, 1]},
                     "position": {"0.00": [0, 0, 0], "0.60": [0, 1.2, 0], "2.00": [0, 0, 0]}},
            "arm_a": {"rotation": wave(6, 2.0, steps=8)}}
    for k, n in enumerate(names):
        a = 2 * math.pi * k / 8
        swim[n] = {"rotation": {"0.00": [0, 0, 0], "0.60": [round(-14 * math.sin(a), 1), 0, round(14 * math.cos(a), 1)],
                                "1.40": [round(8 * math.sin(a), 1), 0, round(-8 * math.cos(a), 1)], "2.00": [0, 0, 0]}}
    anims = {"animation.medusa_vacio.swim": anim(swim, 2.0),
             "animation.medusa_vacio.sting": anim({"bell": {"scale": {"0.00": [1, 1, 1], "0.15": [1.2, 0.85, 1.2], "0.40": [1, 1, 1]}},
                                                   **{n: {"rotation": {"0.00": [0, 0, 0], "0.15": [0, 0, 25 if k % 2 else -25], "0.40": [0, 0, 0]}}
                                                      for k, n in enumerate(names)}}, 0.4, loop=False)}
    glow = glow_from(at.img, lambda c: c[0] > 220 and c[2] > 200)
    return g, at.img, glow, anims


# ====================================================================== Cangrejo de Basalto
def cangrejo_basalto():
    """Cangrejo con caparazón de basalto (columnas grises) y grietas de magma; ojos en antenas y dos tenazas."""
    rnd = random.Random(31)
    g = Geo("geometry.cangrejo_basalto", 64, 32)
    at = Atlas(64, 32)
    B1, B2, B3, DARK, MAG, MAG2, EYE = (92, 90, 98), (120, 118, 126), (64, 62, 70), (34, 32, 38), (255, 120, 30), (255, 190, 70), (255, 220, 90)

    def shell(face, i, j, fw, fh):
        if face == "up":
            c = (B1, B2, B3)[i % 3] if j % 4 else B3       # columnas de basalto
            if (i * 5 + j * 3) % 13 == 0:
                c = MAG
            return jitter(c, rnd, 6)
        if face == "down":
            return jitter(B3, rnd, 5)
        c = B2 if j == 0 else (B1 if i % 2 else B3)
        if j == fh - 1:
            c = DARK
        if (i + j * 2) % 7 == 0 and j > 0:
            c = MAG2
        return jitter(c, rnd, 6)

    def limb(face, i, j, fw, fh):
        c = B1 if (i + j) % 2 else B3
        if face == "down":
            c = B3
        return jitter(c, rnd, 6)

    def claw(face, i, j, fw, fh):
        c = B2 if (i + j) % 2 else B1
        if face == "north" or (face in ("up", "down") and j == 0):
            c = MAG if (i + j) % 2 else DARK            # punta con brasas
        return jitter(c, rnd, 6)

    def eye(face, i, j, fw, fh):
        if face == "up" or j == 0:
            return EYE if face != "south" else DARK
        return DARK

    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 3, 0], "root")
    box(g, at, "body", [-4, 2, -3], [8, 3, 6], shell)
    box(g, at, "body", [-3, 5, -2], [6, 1, 4], shell)
    for side, sx in (("left", 1), ("right", -1)):
        g.bone("eye_" + side, [sx * 1.5, 5, -2.5], "body")
        box(g, at, "eye_" + side, [sx * 1.5 - 0.5, 5, -3], [1, 2, 1], eye)
        g.bone("arm_" + side, [sx * 3, 3, -3], "body", [0, sx * -20, 0])
        box(g, at, "arm_" + side, [sx * 3 - 1, 2.5, -6], [2, 1.5, 3], limb)
        g.bone("claw_" + side, [sx * 3, 3, -6], "arm_" + side)
        box(g, at, "claw_" + side, [sx * 3 - 1.5, 2, -9], [3, 2, 3], claw)
        g.bone("pincer_" + side, [sx * 3, 2, -7], "claw_" + side)
        box(g, at, "pincer_" + side, [sx * 3 - 1, 1, -9], [2, 1, 2], claw)
        for k in range(3):
            n = "leg_%s%d" % (side, k)
            z = -1.5 + k * 1.6
            g.bone(n, [sx * 4, 3, z], "body", [0, 0, sx * 35])
            box(g, at, n, [sx * 4 if sx > 0 else -8, 2.5, z - 0.5], [4, 1, 1], limb)
    walk = {"body": {"position": {"0.00": [0, 0, 0], "0.20": [0, 0.4, 0], "0.40": [0, 0, 0]}},
            "claw_left": {"rotation": wave(6, 0.4, steps=4)}, "claw_right": {"rotation": wave(-6, 0.4, steps=4)}}
    for side, sx in (("left", 1), ("right", -1)):
        for k in range(3):
            ph = (k + (0 if sx > 0 else 1)) % 2
            walk["leg_%s%d" % (side, k)] = {"rotation": wave(18, 0.4, steps=4, phase=math.pi * ph, axis=1,
                                                            extra=[0, 0, 0])}
    pinch = {}
    for side, sx in (("left", 1), ("right", -1)):
        pinch["arm_" + side] = {"rotation": {"0.00": [0, 0, 0], "0.15": [-30, 0, 0], "0.45": [0, 0, 0]}}
        pinch["pincer_" + side] = {"rotation": {"0.00": [0, 0, 0], "0.10": [-35, 0, 0], "0.20": [0, 0, 0], "0.45": [0, 0, 0]}}
    idle = {"eye_left": {"rotation": wave(10, 3.0, steps=6, axis=0)}, "eye_right": {"rotation": wave(10, 3.0, steps=6, axis=0, phase=1.0)},
            "pincer_left": {"rotation": {"0.00": [0, 0, 0], "1.50": [-20, 0, 0], "1.70": [0, 0, 0], "3.00": [0, 0, 0]}},
            "pincer_right": {"rotation": {"0.00": [0, 0, 0], "2.20": [-20, 0, 0], "2.40": [0, 0, 0], "3.00": [0, 0, 0]}}}
    anims = {"animation.cangrejo_basalto.idle": anim(idle, 3.0), "animation.cangrejo_basalto.walk": anim(walk, 0.4),
             "animation.cangrejo_basalto.pinch": anim(pinch, 0.45, loop=False)}
    glow = glow_from(at.img, lambda c: c[0] > 240 and c[1] > 100 and c[2] < 120)
    return g, at.img, glow, anims


# ====================================================================== Caballito de Magma
def caballito_magma():
    """Caballito de mar de bloque de magma: piel negra-roja con grietas encendidas, ojos amarillos y cola enrollada."""
    rnd = random.Random(41)
    g = Geo("geometry.caballito_magma", 32, 32)
    at = Atlas(32, 32)
    D1, D2, R1, ORA, YEL, EYE = (60, 18, 14), (92, 28, 18), (150, 40, 20), (255, 120, 24), (255, 196, 64), (255, 236, 120)

    def skin(face, i, j, fw, fh):
        c = (D1, D2, R1)[(i * 3 + j * 2) % 3]
        if (i * 7 + j * 5) % 9 == 0:
            c = ORA                          # grietas de magma
        elif (i * 7 + j * 5) % 9 == 4:
            c = YEL
        if face == "north":
            c = mix(c, ORA, 0.35)            # pecho más encendido
        return jitter(c, rnd, 8)

    def head(face, i, j, fw, fh):
        c = skin(face, i, j, fw, fh)
        if face in ("east", "west"):
            ex = fw - 1 if face == "east" else 0
            if j == 1 and i == ex:
                return EYE
            if j == 1 and abs(i - ex) == 1:
                return (20, 6, 4)
        return c

    def fin(face, i, j, fw, fh):
        c = mix(ORA, YEL, j / max(1, fh - 1))
        if i % 2 and j == 0:
            return None
        return c + (230,)

    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 5, 0], "root")
    box(g, at, "body", [-1.5, 4, -1.5], [3, 5, 3], skin)          # vientre
    box(g, at, "body", [-1, 9, -1], [2, 2, 2], skin)              # cuello
    box(g, at, "body", [0, 5, 1.5], [0, 5, 2], fin)               # aleta dorsal
    g.bone("head", [0, 11, 0], "body")
    box(g, at, "head", [-1.5, 11, -1.5], [3, 3, 3], head)
    box(g, at, "head", [-0.5, 11.5, -4.5], [1, 1, 3], skin)       # hocico
    box(g, at, "head", [0, 14, -1], [0, 2, 3], fin)               # cresta
    g.bone("tail1", [0, 4, 0], "body")
    box(g, at, "tail1", [-1, 1, -1], [2, 3, 2], skin)
    g.bone("tail2", [0, 1, 0], "tail1", [-30, 0, 0])
    box(g, at, "tail2", [-0.5, -1, -0.5], [1, 2, 1.5], skin)
    g.bone("tail3", [0, -1, 0.5], "tail2", [-60, 0, 0])
    box(g, at, "tail3", [-0.5, -2, 0], [1, 2, 1], skin)
    g.bone("tail4", [0, -2, 0.5], "tail3", [-70, 0, 0])
    box(g, at, "tail4", [-0.5, -3, 0], [1, 1.5, 1], skin)
    g.bone("fin_left", [1.5, 8, 0], "head")
    swim = {"root": {"position": wave(1.0, 2.4, steps=8, axis=1)},
            "body": {"rotation": wave(5, 2.4, steps=8, axis=0, phase=1.0)},
            "head": {"rotation": wave(6, 2.4, steps=8, axis=0, phase=2.0)},
            "tail2": {"rotation": wave(10, 2.4, steps=8, axis=0, extra=[-30, 0, 0])},
            "tail3": {"rotation": wave(14, 2.4, steps=8, axis=0, phase=-0.8, extra=[-60, 0, 0])},
            "tail4": {"rotation": wave(16, 2.4, steps=8, axis=0, phase=-1.6, extra=[-70, 0, 0])}}
    anims = {"animation.caballito_magma.swim": anim(swim, 2.4),
             "animation.caballito_magma.happy": anim({"root": {"rotation": {"0.00": [0, 0, 0], "0.60": [0, 360, 0]},
                                                               "position": {"0.00": [0, 0, 0], "0.30": [0, 2, 0], "0.60": [0, 0, 0]}}}, 0.6, loop=False)}
    glow = glow_from(at.img, lambda c: c[0] > 240 and c[1] > 100)
    return g, at.img, glow, anims


# ====================================================================== Manta Carmesí
def manta_carmesi():
    """Raya gigante (unos 3 bloques de ala a ala) de lomo carmesí con manchas de brillohongo; se puede montar."""
    rnd = random.Random(51)
    g = Geo("geometry.manta_carmesi", 128, 64)
    at = Atlas(128, 64)
    C1, C2, C3, WART, SHROOM, BELLY, BELLY2, EYE = (150, 22, 34), (178, 34, 44), (96, 10, 22), (120, 14, 18), (255, 170, 70), (236, 168, 160), (210, 130, 130), (255, 210, 80)

    def top(face, i, j, fw, fh, edge_side=None):
        if face == "down":
            c = BELLY if (i + j) % 5 else BELLY2
            return jitter(c, rnd, 6)
        if face == "up":
            c = (C1, C2, C1, C3)[(i // 2 + j // 3) % 4]
            if (i * 7 + j * 11) % 29 == 0:
                c = SHROOM                     # manchas que brillan
            elif (i * 3 + j * 5) % 17 == 0:
                c = WART
            return jitter(c, rnd, 7)
        return jitter(C3 if face != "north" else C1, rnd, 6)

    def wing_tip(face, i, j, fw, fh):
        c = top(face, i, j, fw, fh)
        if face == "up" and (i in (0, fw - 1) or j in (0, fh - 1)):
            c = SHROOM if (i + j) % 3 == 0 else C3
        return c

    def head(face, i, j, fw, fh):
        c = top(face, i, j, fw, fh)
        if face in ("east", "west") and j == 0 and i == (fw - 2 if face == "east" else 1):
            return EYE
        if face == "north" and j == fh - 1:
            return (40, 4, 8)                  # boca ancha
        return c

    def tail(face, i, j, fw, fh):
        return jitter(C3 if (i + j) % 3 else SHROOM, rnd, 5)

    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 4, 0], "root")
    box(g, at, "body", [-7, 3, -8], [14, 3, 14], top)
    box(g, at, "body", [-5, 6, -6], [10, 1, 9], top)            # lomo
    box(g, at, "body", [-4, 3.5, -11], [8, 2, 3], head)         # cabeza
    for side, sx in (("left", 1), ("right", -1)):
        g.bone("lobe_" + side, [sx * 3, 4.5, -11], "body")      # aletas cefálicas (los "cuernos")
        box(g, at, "lobe_" + side, [sx * 3 - (0 if sx > 0 else 2), 3.5, -15], [2, 2, 4], top)
        # ala triangular: 4 tramos que se angostan y se van hacia atrás (borde de ataque inclinado)
        x, parent = 7, "body"
        for k, (wd, z0, dp, th) in enumerate([(6, -8, 14, 1.5), (6, -6, 10, 1.5), (5, -4, 7, 1), (4, -2, 4, 1)], 1):
            n = "wing%d_%s" % (k, side)
            g.bone(n, [sx * x, 4.5, -2], parent)
            box(g, at, n, [sx * x if sx > 0 else -(x + wd), 4.75 - th / 2, z0], [wd, th, dp], top if k < 4 else wing_tip)
            x, parent = x + wd, n
    g.bone("tail", [0, 4.5, 6], "body")
    box(g, at, "tail", [-0.5, 4, 6], [1, 1, 16], tail)
    g.bone("saddle_spot", [0, 7, -2], "body")                   # aquí va el jinete
    swim, glide = {}, {}
    for side, sx in (("left", 1), ("right", -1)):
        for k in range(1, 5):
            swim["wing%d_%s" % (k, side)] = {"rotation": wave(sx * (14 + 4 * k), 1.6, steps=8, axis=2, phase=-0.5 * (k - 1))}
            glide["wing%d_%s" % (k, side)] = {"rotation": wave(sx * (3 + 2 * k), 3.0, steps=6, axis=2, phase=-0.4 * (k - 1))}
    swim["tail"] = {"rotation": wave(6, 1.6, steps=8, axis=0, phase=-1.5)}
    swim["body"] = {"position": wave(0.8, 1.6, steps=8, axis=1, phase=1.6)}
    glide["tail"] = {"rotation": wave(4, 3.0, steps=6, axis=1)}
    anims = {"animation.manta_carmesi.swim": anim(swim, 1.6), "animation.manta_carmesi.glide": anim(glide, 3.0)}
    glow = glow_from(at.img, lambda c: c[0] > 240 and c[1] > 140 and c[2] < 120)
    return g, at.img, glow, anims


# ====================================================================== Tortuga Obsidiana
def tortuga_obsidiana():
    """Tortuga enorme con caparazón de obsidiana (vetas moradas de obsidiana llorona) y piel de basalto."""
    rnd = random.Random(61)
    g = Geo("geometry.tortuga_obsidiana", 128, 64)
    at = Atlas(128, 64)
    O1, O2, O3, CRY, CRY2, SK1, SK2, SK3, EYE = (22, 14, 36), (34, 22, 54), (14, 8, 24), (130, 40, 220), (190, 110, 255), (78, 74, 86), (104, 100, 112), (52, 50, 60), (255, 170, 40)

    def shell(face, i, j, fw, fh):
        if face == "down":
            return jitter(SK3 if (i + j) % 2 else SK1, rnd, 5)
        # placas hexagonales: líneas oscuras y vetas de obsidiana llorona
        c = (O1, O2, O1)[(i + j) % 3]
        if face == "up" and (i % 5 == 0 or j % 5 == 0):
            c = O3
        if (i * 7 + j * 13) % 31 == 0:
            c = CRY2
        elif (i * 5 + j * 3) % 19 == 0:
            c = CRY
        return jitter(c, rnd, 5)

    def rim(face, i, j, fw, fh):
        c = O3 if j == fh - 1 else O2
        if (i * 3 + j * 7) % 11 == 0:
            c = CRY
        return jitter(c, rnd, 5)

    def skin(face, i, j, fw, fh):
        c = (SK1, SK2, SK3)[(i * 2 + j) % 3]
        return jitter(c, rnd, 6)

    def head(face, i, j, fw, fh):
        c = skin(face, i, j, fw, fh)
        if face in ("east", "west"):
            ex = fw - 2 if face == "east" else 1
            if j == 1 and i == ex:
                return EYE
            if j == 1 and abs(i - ex) == 1:
                return (20, 10, 4)
        if face == "north":
            if j == fh - 1 or (j == fh - 2 and 0 < i < fw - 1):
                return (230, 190, 120) if j == fh - 2 else (60, 40, 30)   # pico
        return c

    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 5, 0], "root")
    box(g, at, "body", [-8, 3, -9], [16, 2, 18], rim)               # borde del caparazón
    box(g, at, "body", [-7, 5, -8], [14, 4, 16], shell)
    box(g, at, "body", [-5, 9, -6], [10, 2, 12], shell)             # cúpula
    box(g, at, "body", [-6.5, 1.5, -8], [13, 1.5, 16], skin)       # vientre
    g.bone("head", [0, 5, -9], "body")
    box(g, at, "head", [-2, 3.5, -10], [4, 3, 2], skin)             # cuello
    box(g, at, "head", [-2.5, 3, -15], [5, 4, 5], head)
    for side, sx in (("left", 1), ("right", -1)):
        g.bone("front_" + side, [sx * 7, 4, -5], "body")
        box(g, at, "front_" + side, [sx * 7 if sx > 0 else -17, 3.5, -7], [10, 1, 5], skin)
        g.bone("back_" + side, [sx * 6, 4, 7], "body")
        box(g, at, "back_" + side, [sx * 6 if sx > 0 else -12, 3.5, 6], [6, 1, 4], skin)
    g.bone("tail", [0, 4, 9], "body")
    box(g, at, "tail", [-1, 3, 9], [2, 2, 3], skin)
    swim = {"body": {"position": wave(0.6, 2.0, steps=8, axis=1)}, "head": {"rotation": wave(4, 2.0, steps=8, axis=0, phase=1)}}
    walk = {"body": {"rotation": wave(3, 1.2, steps=8, axis=2)}, "head": {"rotation": wave(6, 1.2, steps=8, axis=1)}}
    for side, sx in (("left", 1), ("right", -1)):
        swim["front_" + side] = {"rotation": wave(sx * 30, 2.0, steps=8, axis=2)}
        swim["back_" + side] = {"rotation": wave(sx * 18, 2.0, steps=8, axis=2, phase=-1.0)}
        walk["front_" + side] = {"rotation": wave(28, 1.2, steps=8, axis=1, phase=0 if sx > 0 else math.pi)}
        walk["back_" + side] = {"rotation": wave(22, 1.2, steps=8, axis=1, phase=math.pi if sx > 0 else 0)}
    hide = {"head": {"position": {"0.00": [0, 0, 0], "0.40": [0, -1, 4], "2.00": [0, -1, 4], "2.40": [0, 0, 0]}}}
    anims = {"animation.tortuga_obsidiana.swim": anim(swim, 2.0), "animation.tortuga_obsidiana.walk": anim(walk, 1.2),
             "animation.tortuga_obsidiana.hide": anim(hide, 2.4, loop=False)}
    glow = glow_from(at.img, lambda c: c[2] > 200 and c[0] > 100)
    return g, at.img, glow, anims


FISH = {"pez_brasa": pez_brasa, "pez_alma": pez_alma, "anguila_rubi": anguila_rubi,
        "medusa_vacio": medusa_vacio, "cangrejo_basalto": cangrejo_basalto, "caballito_magma": caballito_magma,
        # la manta y la tortuga usan las texturas del usuario (fauna_hd.py); las versiones de arriba quedan de respaldo
        "manta_carmesi": lambda: _hd("manta"), "tortuga_obsidiana": lambda: _hd("tortuga"),
        # tiburón y serpiente: armados desde las vistas del dibujo del usuario (fauna_hd2.py)
        "tiburon_infernal": lambda: _hd2("tiburon"), "serpiente_marina": lambda: _hd2("serpiente")}


def _hd2(name):
    import fauna_hd2
    return getattr(fauna_hd2, name)(fauna_hd2.native())


def _hd(name):
    import fauna_hd
    return getattr(fauna_hd, name)(fauna_hd.native_sheet())


def write_all(out_dir=None, to_mod=False):
    """Escribe los .bbmodel a out_dir (o tools/ref/fauna); con to_mod=True también los modelos al mod (geo, animaciones, texturas, brillo)."""
    import dragon_v2
    out_dir = out_dir or os.path.join(HERE, "ref", "fauna")
    os.makedirs(out_dir, exist_ok=True)
    result = {}
    for name, fn in FISH.items():
        geo, tex, glow, anims = fn()
        gj = geo.to_json()
        if not to_mod:
            os.makedirs(os.path.join(out_dir, "src"), exist_ok=True)
            save_json(os.path.join(out_dir, "src", name + ".geo.json"), gj)
            save_json(os.path.join(out_dir, "src", name + ".animation.json"), {"format_version": "1.8.0", "animations": anims})
            tex.save(os.path.join(out_dir, "src", name + ".png"))
            glow.save(os.path.join(out_dir, "src", name + "_glowmask.png"))
            bb = dragon_v2.to_bbmodel(gj, tex, anims, name=name)
            bb["model_identifier"] = name
            with open(os.path.join(out_dir, name + ".bbmodel"), "w") as f:
                json.dump(bb, f)
            result[name] = (gj, tex, anims)
            continue
        save_json(os.path.join(ASSETS, "geo", "entity", name + ".geo.json"), gj)
        save_json(os.path.join(ASSETS, "animations", "entity", name + ".animation.json"),
                  {"format_version": "1.8.0", "animations": anims})
        tdir = os.path.join(ASSETS, "textures", "entity", "fauna")
        os.makedirs(tdir, exist_ok=True)
        tex.save(os.path.join(tdir, name + ".png"))
        glow.save(os.path.join(tdir, name + "_glowmask.png"))
        bb = dragon_v2.to_bbmodel(gj, tex, anims, name=name)
        bb["model_identifier"] = name
        with open(os.path.join(out_dir, name + ".bbmodel"), "w") as f:
            json.dump(bb, f)
        result[name] = (gj, tex, anims)
    return result


if __name__ == "__main__":
    write_all()
