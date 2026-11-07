"""Ballena Azul del Océano Púrpura: modelo GeckoLib y textura HD pintada en 3D (mismo método que el delfín).

El modelo mide 8 bloques y el renderizador lo dibuja al doble (16 bloques en el juego), así la textura conserva
5 texeles por unidad: la piel se pinta con moteado en 3 tamaños, pecas, pliegues de la garganta,
cicatrices, diatomeas del vientre, barbas, ojo con párpado y sopladeros.
"""
import math

import numpy as np
from PIL import Image

import delfin
from delfin import paint_box
from models import Geo
from fauna_hd import HDAtlas
from fauna import wave, anim

BACK = np.array([34, 56, 84], float)
SKIN = np.array([74, 104, 138], float)
LIGHT = np.array([112, 140, 170], float)
MOTTLE = np.array([156, 180, 204], float)
FRECKLE = np.array([40, 60, 86], float)
BELLY = np.array([158, 172, 184], float)
SULPHUR = np.array([186, 180, 146], float)
PLEAT = np.array([62, 78, 96], float)
SCAR = np.array([196, 206, 212], float)
EYE = np.array([12, 14, 20], float)


def sstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return a + (b - a) * t


# marcas de rasguños (cicatrices de orca) en los flancos: (z centro, y centro, inclinación, largo, lado)
SCARS = [(-18, 13.0, -0.22, 13, 1), (8, 12.6, -0.18, 11, -1), (20, 11.6, -0.25, 8, 1)]


class WhalePainter(delfin.Painter):
    def smooth(self, p, s=1.0, off=0):
        q = np.array(p, float) * s + off
        i = np.floor(q).astype(int)
        f = q - i
        f = f * f * (3 - 2 * f)
        tot = 0.0
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    w = (f[0] if dx else 1 - f[0]) * (f[1] if dy else 1 - f[1]) * (f[2] if dz else 1 - f[2])
                    tot += w * self.noise[(i[0] + dx) % 64, (i[1] + dy) % 64, (i[2] + dz) % 64]
        return tot

    def fbm(self, p, s, octaves=3, off=0):
        tot, amp, norm = 0.0, 1.0, 0.0
        for o in range(octaves):
            tot += amp * self.smooth(p, s * (2 ** o), off + o * 17)
            norm += amp
            amp *= 0.5
        return tot / norm

    def skin(self, p, n, yc=11.0, half=8.0, belly_ok=True):
        x, y, z = p
        ax = abs(x)
        t = (y - yc) / half
        if n[1] > 0.5:
            t = max(t, 0.9)
        if n[1] < -0.5:
            t = min(t, -1.0)
        # sombreado de contraste: lomo oscuro, flanco azul, panza clara (transiciones suaves)
        c = mix(SKIN, BACK, sstep(0.1, 0.9, t))
        c = mix(c, LIGHT, sstep(-0.1, -0.5, t) * 0.7)
        if belly_ok:
            c = mix(c, BELLY, sstep(-0.45, -0.85, t))
        # moteado en 3 tamaños: manchas grandes claras, manchitas y pecas oscuras
        big = self.fbm((x * 0.8 + 20, y + 20, z * 0.6 + 60), 0.22, 3)
        mid = self.fbm((x + 5, y + 9, z * 0.9 + 30), 0.75, 2, off=5)
        fine = self.smooth((x * 2.0 + 3, y * 2.0 + 7, z * 2.0 + 11), 1.6)
        mott = sstep(0.55, 0.66, big * 0.6 + mid * 0.4)
        if t > -0.6:
            c = mix(c, MOTTLE, mott * 0.42 * (1 - sstep(-0.3, -0.6, t)))
            frk = self.smooth((x * 0.9 + 3, y * 0.9 + 7, z * 0.9 + 11), 1.0)
            if frk > 0.80 and mott < 0.5:
                c = mix(c, FRECKLE, 0.45 * sstep(0.80, 0.86, frk))    # pecas oscuras sobre el azul
            elif fine > 0.78 and mott > 0.5:
                c = mix(c, SKIN, 0.3)                      # puntitos dentro de las manchas claras
        # vientre: manchas amarillentas de diatomeas (el "fondo de azufre")
        if t < -0.4 and belly_ok:
            d = self.fbm((x + 40, y + 40, z * 0.5 + 10), 0.3, 2, off=9)
            c = mix(c, SULPHUR, sstep(0.58, 0.72, d) * 0.3)
        # cicatrices de rasguños en los flancos (3 líneas paralelas)
        if ax > 4:
            for (zc, ys, k, ln, sd) in SCARS:
                if (x > 0) == (sd > 0) and abs(z - zc) < ln / 2:
                    fade = 1 - sstep(ln * 0.3, ln * 0.5, abs(z - zc))
                    for j in range(3):
                        yy = ys + k * (z - zc) + j * 0.5 + 0.15 * math.sin(z * 0.5 + j)
                        dd = abs(y - yy)
                        if dd < 0.13:
                            c = mix(c, SCAR, 0.5 * fade * (1 - dd / 0.13))
        # brillo de piel mojada en la parte alta del flanco
        c = c + 16 * sstep(0.35, 0.6, t) * (1 - sstep(0.6, 0.95, t)) * (0.6 + 0.4 * mid)
        # grano fino de la piel
        c = c + (self.n3((x * 1.7 + 30, y * 1.7 + 30, z * 1.7 + 60), 5.0) - 0.5) * 4
        return c

    def pleats(self, p, n, c, zmax):
        """Pliegues ventrales: surcos largos y paralelos de la barbilla al ombligo."""
        x, y, z = p
        if z > zmax:
            return c
        fade = 1 - sstep(zmax - 6, zmax, z)
        freq = 0.95 * (1 + 0.25 * sstep(-30, -64, z))       # más juntos hacia la barbilla
        u = x * freq + 0.18 * math.sin(z * 0.08)
        fr = u - math.floor(u)
        dist = abs(fr - 0.5)
        if dist < 0.13:
            c = mix(c, PLEAT, 0.65 * fade * (1 - dist / 0.2))
        elif dist < 0.24:
            c = mix(c, c + 18, 0.5 * fade)                   # borde claro del surco
        return c

    def body(self, p, n):
        x, y, z = p
        yc = 11.0 - max(0, z - 10) * 0.08
        half = max(3.0, 8.5 - max(0, z - 10) * 0.12)
        c = self.skin(p, n, yc, half)
        t = (y - yc) / half
        if t < -0.55 or n[1] < -0.5:
            c = self.pleats(p, n, c, -6)
        return c

    def head(self, p, n):
        x, y, z = p
        ax = abs(x)
        c = self.skin(p, n, 10.5, 6.0)
        # cresta central del hocico (más clara) que llega hasta el sopladero
        if n[1] > 0.5 and ax < 0.6 and z < -50:
            c = mix(c, LIGHT, 0.35)
        # boca: sube en curva hacia el ojo; labio claro arriba y barbas oscuras justo debajo
        ym = 8.3 + 0.03 * (z + 64) + 0.9 * sstep(-52, -46.5, z)
        if ax > 5.5 and z < -45.8:
            dy = y - ym
            if abs(dy) < 0.22:
                c = np.array([22, 26, 34.0])
            elif 0.22 <= dy < 0.5:
                c = mix(c, LIGHT, 0.5)                       # labio
            elif -0.75 < dy <= -0.22 and z < -48:
                stripe = (z * 3.0) % 1.0 < 0.5
                c = np.array([58, 58, 62.0]) if stripe else np.array([84, 82, 80.0])   # barbas de ballena
        # ojo con párpado y arrugas alrededor
        r = math.hypot(y - 9.7, (z + 45.6) * 0.9)
        if ax > 6.5:
            if r < 0.42:
                c = EYE
                if math.hypot(y - 9.82, z + 45.75) < 0.11:
                    c = np.array([230, 236, 240.0])          # brillo del ojo
                elif r > 0.3:
                    c = np.array([70, 46, 30.0])             # iris café
            elif r < 0.62:
                c = mix(c, BACK, 0.7)                        # párpado
            elif 0.9 < r < 1.0 or 1.25 < r < 1.33:
                c = mix(c, BACK, 0.35)                       # arrugas
        # sopladeros: dos ranuras con su cresta protectora
        if n[1] > 0.5:
            for sx in (-1, 1):
                dz_, dx_ = z + 49.2, x - sx * 0.9
                if abs(dx_) < 0.32 and abs(dz_) < 1.3:
                    c = np.array([16, 20, 28.0]) if abs(dx_) < 0.18 else mix(c, BACK, 0.6)
            if -51.6 < z < -50.6 and ax < 2.2:
                c = mix(c, LIGHT, 0.3)
        # tubérculos de la barbilla
        for (tx_, tz_) in ((-3.2, -63.0), (3.0, -62.4), (-1.4, -61.6), (1.6, -64.0), (-4.2, -61.0), (4.4, -63.6)):
            if y < 8.2 and math.hypot(x - tx_, z - tz_) < 0.3:
                c = mix(c, BELLY, 0.5)
        return c

    def eye(self, p, n):
        """Ojo de la ballena (pieza propia a cada lado de la cabeza, para que se vea bien)."""
        x, y, z = p
        c = mix(self.skin(p, n, 10.5, 6.0), BACK, 0.35)
        if abs(n[0]) > 0.5 and abs(x) > 10.4:
            r = math.hypot((y - 9.45) * 1.15, z + 46.2) / 1.35
            if r < 0.95:
                c = np.array([40, 52, 66.0])                     # párpado oscuro
            if r < 0.78:
                c = np.array([226, 222, 210.0])                  # blanco del ojo
            if r < 0.62:
                c = np.array([120, 74, 34.0])                    # iris ámbar
                if r > 0.5:
                    c = np.array([76, 44, 20.0])                 # borde del iris
            if r < 0.36:
                c = EYE                                          # pupila
            if math.hypot(y - 9.8, z + 46.55) < 0.18:
                c = np.array([250, 252, 255.0])                  # brillo
            if 0.95 < r < 1.08:
                c = mix(c, BACK, 0.6)                            # arruga del párpado
        return c

    def throat(self, p, n):
        x, y, z = p
        c = self.skin(p, n, 10.5, 6.0)
        if n[1] < -0.5 or y < 5.5:
            c = mix(c, BELLY, 0.75)
            c = self.pleats(p, n, c, 0)
        return self.head_marks(p, n, c)

    def head_marks(self, p, n, c):
        x, y, z = p
        # la línea de la boca continúa por la mandíbula de abajo
        ym = 8.3 + 0.03 * (z + 64) + 0.9 * sstep(-52, -46.5, z)
        if abs(x) > 5.5 and abs(y - ym) < 0.22 and z < -45.8:
            c = np.array([22, 26, 34.0])
        return c

    def flipper(self, p, n):
        x, y, z = p
        ax = abs(x)
        c = self.skin(p, n, 11, 8, belly_ok=False)
        tip = sstep(17, 24, ax)
        if n[1] < -0.5:
            c = mix(c, np.array([206, 214, 220.0]), 0.55 + 0.3 * tip)       # por debajo, blanca
        c = mix(c, np.array([200, 210, 216.0]), tip * 0.55)                  # punta clara
        if z < -35.5:
            c = mix(c, np.array([190, 200, 206.0]), 0.4)                     # borde delantero
        return c

    def fluke(self, p, n):
        x, y, z = p
        if n[1] >= 0:
            c = mix(BACK, SKIN, 0.25)
            m = self.fbm((x + 40, y + 10, z + 10), 0.5, 2)
            c = mix(c, MOTTLE, sstep(0.6, 0.7, m) * 0.35)
        else:
            c = mix(BELLY, BACK, 0.35)
            m = self.fbm((x + 70, y + 10, z + 40), 0.35, 2)
            c = mix(c, np.array([214, 220, 224.0]), sstep(0.5, 0.65, m) * 0.6)   # manchas blancas por debajo
        if self.smooth((x * 3 + 5, y * 3, z * 3 + 5), 1.0) > 0.78:
            c = mix(c, FRECKLE, 0.4)
        return c + (self.n3((x + 9, y, z), 5.0) - 0.5) * 7


WhalePainter.fin = WhalePainter.fluke


def build(dens=5):
    delfin.D = dens
    at = HDAtlas(4096, 4096)
    g = Geo("geometry.ballena_azul", 4096, 4096)
    pt = WhalePainter(seed=11)

    def rounded(bone, cx, cy, cz, w, h, d, fn, cap):
        paint_box(g, at, bone, [cx - w / 2, cy - h / 2, cz - d / 2], [w, h, d], fn, pt)
        paint_box(g, at, bone, [cx - w / 2 + cap, cy + h / 2, cz - d / 2 + cap * 0.5], [w - 2 * cap, cap, d - cap], fn, pt)
        paint_box(g, at, bone, [cx - w / 2 + cap, cy - h / 2 - cap, cz - d / 2 + cap * 0.5], [w - 2 * cap, cap, d - cap], fn, pt)
        paint_box(g, at, bone, [cx + w / 2, cy - h / 2 + cap, cz - d / 2 + cap * 0.5], [cap, h - 2 * cap, d - cap], fn, pt)
        paint_box(g, at, bone, [cx - w / 2 - cap, cy - h / 2 + cap, cz - d / 2 + cap * 0.5], [cap, h - 2 * cap, d - cap], fn, pt)

    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 11, 0], "root")
    rounded("body", 0, 11, -31, 19, 15, 26, "body", 2.5)        # pecho
    rounded("body", 0, 11, -15, 18.5, 14.6, 10, "body", 2.5)
    rounded("body", 0, 11, -2, 17.5, 14, 18, "body", 2.5)       # vientre
    rounded("body", 0, 11.2, 9, 15.5, 12.6, 6, "body", 2.2)
    g.bone("head", [0, 10, -44], "body")
    rounded("head", 0, 12.5, -53, 17, 6, 20, "head", 1.5)       # parte de arriba de la cabeza (ancha y plana)
    rounded("head", 0, 6.5, -52, 18, 7, 22, "throat", 1.5)      # garganta con pliegues
    rounded("head", 0, 9.5, -64.5, 11, 6, 5, "head", 1.2)       # punta del hocico
    paint_box(g, at, "head", [-2.5, 15.5, -51], [5, 1.2, 4], "head", pt)   # cresta del sopladero
    for sx in (1, -1):                                                     # ojos (un poco salidos, como los de verdad)
        paint_box(g, at, "head", [sx * 9.9 - (0 if sx > 0 else 0.7), 7.9, -47.8], [0.7, 3.1, 3.2], "eye", pt)
    g.bone("tail1", [0, 11, 12], "body")
    rounded("tail1", 0, 11.5, 17, 13.5, 11.4, 10, "body", 2)
    rounded("tail1", 0, 11.6, 27, 11.5, 9.6, 10, "body", 1.8)
    g.bone("dorsal", [0, 17, 27], "tail1")
    paint_box(g, at, "dorsal", [-0.6, 17, 25], [1.2, 1.8, 5], "fin", pt)
    paint_box(g, at, "dorsal", [-0.5, 18.4, 27.5], [1.0, 1.4, 3], "fin", pt, rotation=[-30, 0, 0], pivot=[0, 18.4, 27.5])
    g.bone("tail2", [0, 11.5, 32], "tail1")
    rounded("tail2", 0, 12, 36, 9, 7.6, 8, "body", 1.4)
    rounded("tail2", 0, 12, 42.5, 7, 6, 7, "body", 1.2)
    g.bone("tail3", [0, 12, 46], "tail2")
    paint_box(g, at, "tail3", [-2.5, 9.8, 46], [5, 4.6, 9], "body", pt)
    paint_box(g, at, "tail3", [-0.6, 14.4, 46], [1.2, 1.2, 8], "body", pt)          # quilla
    g.bone("flukes", [0, 12, 55], "tail3")
    paint_box(g, at, "flukes", [-3, 11.3, 54], [6, 1.4, 4], "fluke", pt)
    for sx in (1, -1):
        paint_box(g, at, "flukes", [sx * 2.5 - (0 if sx > 0 else 9), 11.4, 54.2], [9, 1.2, 7], "fluke", pt,
                  rotation=[0, sx * -20, 0], pivot=[sx * 2.5, 12, 56])
        paint_box(g, at, "flukes", [sx * 10.5 - (0 if sx > 0 else 8), 11.5, 57.5], [8, 1.0, 4.5], "fluke", pt,
                  rotation=[0, sx * -36, 0], pivot=[sx * 10.5, 12, 59])
    for side, sx in (("left", 1), ("right", -1)):
        g.bone("fin_" + side, [sx * 9, 6.5, -34], "body", [0, 0, sx * 30])
        paint_box(g, at, "fin_" + side, [sx * 9 - (0 if sx > 0 else 16), 6, -36], [16, 1.2, 4.5], "flipper", pt,
                  rotation=[0, sx * -28, 0], pivot=[sx * 9, 6.5, -34])
    # ---------------------------------------------------------------- animaciones (todas lentas: es un animal enorme)
    swim = {"body": {"rotation": wave(1.5, 4.0, steps=8, axis=0, phase=0.6)},
            "head": {"rotation": wave(-1.5, 4.0, steps=8, axis=0, phase=1.0)},
            "tail1": {"rotation": wave(4, 4.0, steps=8, axis=0)},
            "tail2": {"rotation": wave(7, 4.0, steps=8, axis=0, phase=-0.8)},
            "tail3": {"rotation": wave(9, 4.0, steps=8, axis=0, phase=-1.5)},
            "flukes": {"rotation": wave(14, 4.0, steps=8, axis=0, phase=-2.2)},
            "fin_left": {"rotation": wave(5, 4.0, steps=8, axis=2)},
            "fin_right": {"rotation": wave(-5, 4.0, steps=8, axis=2)}}
    # salto (breach): sube casi vertical, sale del agua girando y cae de espaldas
    breach = {"root": {"rotation": {"0.00": [-55, 0, 0], "1.00": [-62, 0, 20], "1.80": [-40, 0, 70], "2.60": [10, 0, 130], "3.40": [30, 0, 160]},
                       "position": {"0.00": [0, -40, 0], "1.00": [0, 40, -10], "1.80": [0, 70, -20], "2.60": [0, 40, -30], "3.40": [0, -20, -36]}},
              "fin_left": {"rotation": {"0.00": [0, 0, 0], "1.20": [0, 0, 45], "2.40": [0, 0, 60], "3.40": [0, 0, 10]}},
              "fin_right": {"rotation": {"0.00": [0, 0, 0], "1.20": [0, 0, -45], "2.40": [0, 0, -60], "3.40": [0, 0, -10]}},
              "flukes": {"rotation": wave(18, 3.4, steps=6, axis=0)}}
    # inmersión: arquea la espalda, baja la cabeza y levanta la cola fuera del agua
    dive = {"root": {"rotation": {"0.00": [0, 0, 0], "1.50": [25, 0, 0], "3.00": [70, 0, 0]},
                     "position": {"0.00": [0, 0, 0], "3.00": [0, -30, -20]}},
            "tail2": {"rotation": {"0.00": [0, 0, 0], "1.50": [-12, 0, 0], "3.00": [-20, 0, 0]}},
            "flukes": {"rotation": {"0.00": [0, 0, 0], "1.50": [-25, 0, 0], "2.40": [-35, 0, 0], "3.00": [-10, 0, 0]}}}
    # resoplido en la superficie (el chorro sale con partículas del juego)
    blow = {"head": {"rotation": {"0.00": [0, 0, 0], "0.60": [-5, 0, 0], "1.60": [0, 0, 0]}},
            "body": {"position": {"0.00": [0, 0, 0], "0.60": [0, 1.5, 0], "1.60": [0, 0, 0]}}}
    anims = {"animation.ballena_azul.swim": anim(swim, 4.0), "animation.ballena_azul.breach": anim(breach, 3.4, loop=False),
             "animation.ballena_azul.dive": anim(dive, 3.0, loop=False), "animation.ballena_azul.blow": anim(blow, 1.6, loop=False)}
    tex = at.image()
    # recortar el atlas a lo usado
    a = np.array(tex)
    rows = np.nonzero(a[..., 3].any(1))[0]
    cols = np.nonzero(a[..., 3].any(0))[0]
    h = int(2 ** math.ceil(math.log2(rows.max() + 1)))
    w = int(2 ** math.ceil(math.log2(cols.max() + 1)))
    g.th, g.tw = h, w
    tex = Image.fromarray(a[:h, :w])
    return g, tex, anims
