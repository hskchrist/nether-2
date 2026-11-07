"""Delfín del Nether (Océano Púrpura): modelo GeckoLib redondeado y textura HD pintada en 3D.

La textura no se dibuja cara por cara: cada texel sabe en qué punto del cuerpo cae (UV por cara, 4 texeles por unidad),
y el color sale de una función del cuerpo (lomo violeta oscuro, flancos amatista, vientre lavanda, la línea de alma que
brilla, motas, ojos, boca). Así los colores siguen de un cubo al otro sin cortes, aunque el modelo tenga muchas piezas.
"""
import math
import os
import random

import numpy as np
from PIL import Image

from models import Geo
from fauna_hd import HDAtlas, add_cube
from fauna import wave, anim

D = 4                                     # texeles por unidad (HD: 4 veces la densidad normal)

BACK = np.array([46, 20, 92], float)
FLANK = np.array([128, 70, 196], float)
BELLY = np.array([232, 214, 246], float)
SOUL = np.array([96, 238, 255], float)
SOUL2 = np.array([200, 255, 255], float)
EYE = np.array([14, 10, 34], float)
FIN = np.array([60, 26, 118], float)


class Painter:
    def __init__(self, seed=3):
        self.rnd = np.random.RandomState(seed)
        self.noise = self.rnd.rand(64, 64, 64)

    def n3(self, p, s=1.0):
        i = (np.floor(np.array(p) * s).astype(int)) % 64
        return self.noise[i[0], i[1], i[2]]

    def body(self, p, n):
        """p = (x, y, z) en unidades del modelo (cabeza hacia -Z); n = normal de la cara."""
        x, y, z = p
        ax = abs(x)
        yc = 6.0 + 0.04 * (z + 4)                     # línea media del cuerpo
        t = (y - yc) / 3.6                           # -1 vientre .. +1 lomo
        if n[1] > 0.5:
            t = max(t, 0.8)
        if n[1] < -0.5:
            t = min(t, -0.9)
        if t > 0.15:
            c = FLANK + (BACK - FLANK) * min(1, (t - 0.15) / 0.75)
        elif t > -0.35:
            c = FLANK
        else:
            c = FLANK + (BELLY - FLANK) * min(1, (-0.35 - t) / 0.45)
        # cambio de color ondulado entre flanco y vientre (como el delfín real)
        edge = -0.35 + 0.18 * math.sin(z * 0.55)
        if abs(t - edge) < 0.07 and ax > 1.5:
            c = c * 0.8 + BELLY * 0.2
        # línea de alma que brilla a lo largo del costado
        yl = yc + 0.9 + 0.55 * math.sin(z * 0.42 + 0.6)
        if ax > 2.2 and abs(y - yl) < 0.32 and -9 < z < 9:
            c = SOUL2 if abs(y - yl) < 0.14 else SOUL
        # motas de alma en el lomo
        if t > 0.5 and self.n3((x + 9, y, z + 20), 2.0) > 0.965:
            c = SOUL
        # textura fina: piel con un poco de ruido y brillo arriba
        k = (self.n3((x + 9, y + 3, z + 20), 4.0) - 0.5) * 10
        c = c + k + 14 * max(0, t) * (self.n3((x + 3, y, z + 7), 1.0) - 0.4)
        return c

    def head(self, p, n):
        x, y, z = p
        c = self.body(p, n)
        # ojo: un poco detrás de la comisura, a cada lado
        ey, ez = 6.6, -12.4
        r = math.hypot(y - ey, z - ez)
        if abs(x) > 2.0 and r < 0.95:
            c = EYE
            if r < 0.55:
                c = SOUL * 0.8 + EYE * 0.2           # iris de alma
            if math.hypot(y - (ey + 0.3), z - (ez - 0.25)) < 0.22:
                c = np.array([255, 255, 255.0])      # brillo
        elif abs(x) > 2.0 and r < 1.25:
            c = c * 0.7                              # contorno del ojo
        # boca: línea oscura en la parte baja del hocico
        if z < -12 and abs(y - (4.85 + 0.12 * (z + 12))) < 0.18 and abs(x) > 0.6:
            c = np.array([38, 14, 60.0])
        return c

    def fin(self, p, n):
        x, y, z = p
        c = FIN + (self.n3((x + 9, y + 9, z + 20), 3.0) - 0.5) * 12
        return c

    def fin_edge(self, p, n, u, v):
        c = self.fin(p, n)
        if u < 0.06 or u > 0.94 or v < 0.08 or v > 0.92:
            c = c * 0.6 + SOUL * 0.4                 # borde que brilla
        return c


FACES = ("north", "south", "east", "west", "up", "down")


def face_points(o, s, face, w, h):
    """Puntos 3D (centro de cada texel) de una cara, en el mismo orden de UV que usa GeckoLib/el visor."""
    x0, y0, z0 = o
    x1, y1, z1 = o[0] + s[0], o[1] + s[1], o[2] + s[2]
    us = (np.arange(w) + 0.5) / w
    vs = (np.arange(h) + 0.5) / h
    U, V = np.meshgrid(us, vs)
    if face == "east":
        P = (np.full_like(U, x0), y1 - V * (y1 - y0), z1 - U * (z1 - z0)); nrm = (-1, 0, 0)
    elif face == "west":
        P = (np.full_like(U, x1), y1 - V * (y1 - y0), z0 + U * (z1 - z0)); nrm = (1, 0, 0)
    elif face == "north":
        P = (x0 + U * (x1 - x0), y1 - V * (y1 - y0), np.full_like(U, z0)); nrm = (0, 0, -1)
    elif face == "south":
        P = (x1 - U * (x1 - x0), y1 - V * (y1 - y0), np.full_like(U, z1)); nrm = (0, 0, 1)
    elif face == "up":
        P = (x0 + U * (x1 - x0), np.full_like(U, y1), z1 - V * (z1 - z0)); nrm = (0, 1, 0)
    else:
        P = (x0 + U * (x1 - x0), np.full_like(U, y0), z0 + V * (z1 - z0)); nrm = (0, -1, 0)
    return P, nrm, U, V


def face_size(s, face):
    w, h, d = s
    if face in ("north", "south"):
        return w, h
    if face in ("east", "west"):
        return d, h
    return w, d


def paint_box(g, at, bone, o, s, fn, painter, rotation=None, pivot=None):
    faces = {}
    for face in FACES:
        fw, fh = face_size(s, face)
        tw, th = max(1, int(round(fw * D))), max(1, int(round(fh * D)))
        (X, Y, Z), nrm, U, V = face_points(o, s, face, tw, th)
        arr = np.zeros((th, tw, 4), np.uint8)
        for j in range(th):
            for i in range(tw):
                p = (X[j, i], Y[j, i], Z[j, i])
                if fn == "fin_edge":
                    c = painter.fin_edge(p, nrm, U[j, i], V[j, i])
                else:
                    c = getattr(painter, fn)(p, nrm)
                arr[j, i, :3] = np.clip(c, 0, 255)
                arr[j, i, 3] = 255
        pos = at.put(arr)
        faces[face] = ([pos[0], pos[1]], [tw, th])
    add_cube(g, bone, o, s, faces, rotation=rotation, pivot=pivot)


def build():
    at = HDAtlas(512, 512)
    g = Geo("geometry.delfin_nether", 512, 512)
    pt = Painter()
    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 6, 0], "root")
    # cuerpo redondeado: núcleo + "tapas" un poco más chicas arriba, abajo y a los lados
    def rounded(bone, cx, cy, cz, w, h, d, fn="body", cap=1.0):
        paint_box(g, at, bone, [cx - w / 2, cy - h / 2, cz - d / 2], [w, h, d], fn, pt)
        paint_box(g, at, bone, [cx - w / 2 + cap, cy + h / 2, cz - d / 2 + cap], [w - 2 * cap, cap, d - 2 * cap], fn, pt)
        paint_box(g, at, bone, [cx - w / 2 + cap, cy - h / 2 - cap, cz - d / 2 + cap], [w - 2 * cap, cap, d - 2 * cap], fn, pt)
        paint_box(g, at, bone, [cx + w / 2, cy - h / 2 + cap, cz - d / 2 + cap], [cap, h - 2 * cap, d - 2 * cap], fn, pt)
        paint_box(g, at, bone, [cx - w / 2 - cap, cy - h / 2 + cap, cz - d / 2 + cap], [cap, h - 2 * cap, d - 2 * cap], fn, pt)
    rounded("body", 0, 6, 0, 7, 6, 12)                          # tronco
    rounded("body", 0, 6.2, -7.5, 6, 5.4, 3)                     # pecho
    g.bone("head", [0, 6, -9], "body")
    rounded("head", 0, 6.4, -11.5, 5.2, 4.8, 4, fn="head")       # melón (la frente redonda)
    paint_box(g, at, "head", [-1.5, 4.4, -16.5], [3, 2.0, 3.0], "head", pt)       # hocico
    paint_box(g, at, "head", [-1.1, 4.5, -17.4], [2.2, 1.6, 1.0], "head", pt)     # punta del hocico
    g.bone("tail1", [0, 6, 6], "body")
    rounded("tail1", 0, 6.2, 8.5, 5, 4.4, 5, cap=0.8)
    g.bone("tail2", [0, 6.3, 11], "tail1")
    rounded("tail2", 0, 6.4, 13, 3.4, 3.0, 4, cap=0.6)
    g.bone("flukes", [0, 6.4, 15], "tail2")
    paint_box(g, at, "flukes", [-1.5, 5.9, 14.8], [3, 1.0, 2.0], "body", pt)
    # aleta caudal en media luna: tramo interior ancho y punta más fina, inclinadas hacia atrás
    for sx in (1, -1):
        paint_box(g, at, "flukes", [sx * 1.2 - (0 if sx > 0 else 3.8), 6.0, 15.4], [3.8, 0.8, 2.6], "fin_edge", pt,
                  rotation=[0, sx * -24, 0], pivot=[sx * 1.2, 6.4, 15.6])
        paint_box(g, at, "flukes", [sx * 4.2 - (0 if sx > 0 else 2.6), 6.1, 17.2], [2.6, 0.6, 1.6], "fin_edge", pt,
                  rotation=[0, sx * -40, 0], pivot=[sx * 4.2, 6.4, 17.6])
    g.bone("dorsal", [0, 9, 0], "body")
    paint_box(g, at, "dorsal", [-0.5, 9.8, -1.5], [1, 1.8, 4.5], "fin", pt)
    paint_box(g, at, "dorsal", [-0.45, 11.4, 0.0], [0.9, 1.6, 3.0], "fin_edge", pt, rotation=[-28, 0, 0], pivot=[0, 11.4, 0.2])
    paint_box(g, at, "dorsal", [-0.4, 12.8, 1.4], [0.8, 1.0, 1.8], "fin_edge", pt, rotation=[-40, 0, 0], pivot=[0, 12.8, 1.6])
    for side, sx in (("left", 1), ("right", -1)):
        g.bone("fin_" + side, [sx * 3.4, 4.2, -5], "body", [0, 0, sx * 35])
        paint_box(g, at, "fin_" + side, [sx * 3.4 - (0 if sx > 0 else 3.6), 3.8, -6], [3.6, 0.8, 2.6], "fin_edge", pt,
                  rotation=[0, sx * -25, 0], pivot=[sx * 3.4, 4.2, -5])
    swim = {"body": {"rotation": wave(3, 1.0, steps=8, axis=0, phase=0.8)},
            "head": {"rotation": wave(-3, 1.0, steps=8, axis=0, phase=1.2)},
            "tail1": {"rotation": wave(10, 1.0, steps=8, axis=0)},
            "tail2": {"rotation": wave(14, 1.0, steps=8, axis=0, phase=-0.9)},
            "flukes": {"rotation": wave(20, 1.0, steps=8, axis=0, phase=-1.8)},
            "fin_left": {"rotation": wave(8, 1.0, steps=8, axis=2)},
            "fin_right": {"rotation": wave(-8, 1.0, steps=8, axis=2)}}
    jump = {"root": {"rotation": {"0.00": [-35, 0, 0], "0.60": [0, 0, 0], "1.20": [40, 0, 0]},
                     "position": {"0.00": [0, 0, 0], "0.60": [0, 18, 0], "1.20": [0, 0, 0]}},
            "flukes": {"rotation": wave(25, 1.2, steps=6, axis=0)}}
    ram = {"body": {"position": {"0.00": [0, 0, 0], "0.18": [0, 0, 4], "0.30": [0, 0, -6], "0.55": [0, 0, 0]}},
           "head": {"rotation": {"0.00": [0, 0, 0], "0.25": [10, 0, 0], "0.35": [-12, 0, 0], "0.55": [0, 0, 0]}},
           "tail2": {"rotation": {"0.00": [0, 0, 0], "0.20": [-30, 0, 0], "0.40": [25, 0, 0], "0.55": [0, 0, 0]}}}
    anims = {"animation.delfin_nether.swim": anim(swim, 1.0), "animation.delfin_nether.jump": anim(jump, 1.2, loop=False),
             "animation.delfin_nether.ram": anim(ram, 0.55, loop=False)}
    tex = at.image()
    a = np.array(tex)
    glow = np.zeros_like(a)
    sel = (a[..., 3] > 0) & (a[..., 2].astype(int) > 230) & (a[..., 1].astype(int) > 200) & (a[..., 0].astype(int) < 215)
    glow[sel] = a[sel]
    return g, tex, Image.fromarray(glow, "RGBA"), anims
