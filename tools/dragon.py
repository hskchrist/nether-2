"""Dragón del Nether (fuego de almas): modelo, textura y animaciones de calidad para GeckoLib.

Partes: cuerpo, pecho, 3 segmentos de cuello, cabeza con mandíbula móvil, dientes, cuernos articulados,
4 patas con codo/rodilla y garras, 5 segmentos de cola con aleta, alas de 3 secciones con membrana
recortada, montura detallada (manta, asiento, pomo, respaldo, cincha, estribos, alforjas, estandarte y bridas)
y armadura de dragón (casco, cuello y peto). Más el huevo (entidad GeckoLib con sus animaciones).
"""
import math
import os
import random
from PIL import Image
from common import ASSETS, save_json, Packer
from models import Geo, anim
from textures import Sheet

rnd = random.Random(7)
PAL = {
    ".": None,
    # escamas
    "S": (52, 30, 34), "s": (30, 16, 20), "l": (76, 42, 46), "h": (98, 54, 58),
    # placas del vientre
    "B": (104, 30, 34), "b": (66, 16, 20), "y": (132, 44, 46),
    # membrana de las alas
    "M": (78, 22, 28), "m": (56, 14, 20), "n": (104, 34, 40), "V": (22, 8, 12), "D": (44, 12, 16),
    # hueso / cuerno
    "I": (96, 62, 64), "i": (66, 40, 44), "j": (36, 20, 24),
    # fuego de almas (brilla)
    "Q": (255, 58, 44), "q": (196, 22, 26), "W": (255, 176, 150),
    # ojo
    "E": (255, 40, 36), "e": (40, 4, 6),
    # boca
    "O": (110, 24, 32), "o": (64, 10, 16), "T": (230, 206, 204),
    # montura
    "L": (98, 56, 32), "k": (70, 38, 22), "K": (42, 22, 12),
    "G": (232, 196, 58), "g": (176, 132, 28), "Y": (255, 238, 130),
    "R": (152, 22, 32), "r": (102, 12, 20), "U": (232, 30, 40), "u": (150, 10, 20),
    # armadura
    "A": (52, 46, 58), "a": (34, 30, 38),
}
GLOW = [PAL["Q"], PAL["q"], PAL["W"], PAL["E"]]


def px(ch, noise=4):
    c = PAL[ch]
    if c is None:
        return (0, 0, 0, 0)
    return tuple(max(0, min(255, v + rnd.randint(-noise, noise))) for v in c) + (255,)


def exact(ch):
    c = PAL[ch]
    return (0, 0, 0, 0) if c is None else c + (255,)


CLEAR = lambda *a: (0, 0, 0, 0)


def fill(ch, alt=None, p=0.2):
    return lambda i, j, fw, fh: px(alt if (alt and rnd.random() < p) else ch)


def rows(*r):
    def f(i, j, fw, fh):
        line = r[min(j, len(r) - 1)]
        return px(line[min(i, len(line) - 1)])
    return f


# ------------------------------------------------------------------ patrones
def _mix(a, b, t):
    return tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))


def scales(i, j, fw, fh, base="S"):
    """Escamas imbricadas con degradado: más claras arriba, sombra abajo, borde de cada escama marcado suave."""
    t = j / max(1, fh - 1)
    top, mid, bot = PAL["l"], PAL[base], PAL["s"]
    c = _mix(top, mid, t * 2) if t < 0.5 else _mix(mid, bot, (t - 0.5) * 2)
    row = j // 2
    k = (i + (row % 2) * 2) % 4
    if j % 2 == 1 and k in (0, 3):
        f = 0.78                                   # sombra bajo la escama
    elif j % 2 == 0 and k in (1, 2):
        f = 1.16                                   # brillo del borde superior
    else:
        f = 1.0
    n = rnd.uniform(0.95, 1.05)
    return tuple(max(0, min(255, int(v * f * n))) for v in c) + (255,)


def scale_face(i, j, fw, fh):
    return scales(i, j, fw, fh)


def belly(glow=False):
    """Placas del vientre en bandas; con glow=True las juntas brillan con fuego de almas."""
    def f(i, j, fw, fh):
        if j % 3 == 2:
            mid = (fw - 1) / 2
            if glow and abs(i - mid) <= 1.0 and (j // 3) % 2 == 0:
                return exact("Q") if abs(i - mid) < 0.6 else exact("q")
            return px("b", 2)
        if i == 0 or i == fw - 1:
            return px("s", 2)
        return px("y", 3) if j % 3 == 0 else px("B", 3)
    return f


def spine_top(glow=True):
    """Lomo: escamas con una línea central de escamas más grandes y brasas de alma."""
    def f(i, j, fw, fh):
        mid = (fw - 1) / 2
        if abs(i - mid) <= 0.6 + (fw > 6) * 0.5:
            if glow and j % 8 == 1:
                return exact("q")
            return px("s", 3) if j % 2 else px("S", 3)
        return scales(i, j, fw, fh)
    return f


def body_faces(top=None, bottom=None, glow_belly=False):
    return {"all": scale_face, "top": top or spine_top(), "bottom": bottom or belly(glow_belly)}


def horn(i, j, fw, fh):
    t = j / max(1, fh - 1)
    c = _mix(PAL["I"], PAL["j"], t)
    f = 0.85 if (i + j) % 3 == 0 else 1.0
    return tuple(int(v * f) for v in c) + (255,)


def horn_faces(tip_first=False):
    def f(i, j, fw, fh):
        return px("j", 3) if (j + i) % 4 == 0 else px("I" if i % 2 else "i", 3)
    return {"all": f}


def ivory(i, j, fw, fh):
    return px("I", 3) if (i + j) % 3 else px("i", 3)


# ------------------------------------------------------------------ membrana
def membrane(fw, fh, edge="scallop", veins=((0.0, 0.0, 1.0, 1.0),), taper=None, glow=False, torn=False):
    """Membrana del ala. fw = largo (hacia afuera, eje X), fh = ancho (hacia atrás, eje Z).
    veins: segmentos (x0, z0, x1, z1) en coordenadas 0..1 (dedos del ala).
    glow: las venas cerca del brazo brillan con fuego de almas. torn: bordes rasgados de batalla."""
    tr = random.Random(fw * 31 + fh)
    notches = [(tr.random(), 0.04 + tr.random() * 0.07) for _ in range(4)] if torn else []
    holes = [(0.3 + tr.random() * 0.5, 0.35 + tr.random() * 0.4) for _ in range(2)] if torn else []
    grid = [[None] * fw for _ in range(fh)]
    for j in range(fh):
        for i in range(fw):
            x, z = (i + 0.5) / fw, (j + 0.5) / fh
            limit = 1.0
            if edge == "scallop":
                limit = 0.68 + 0.30 * abs(math.cos(math.pi * x * 2.0)) ** 0.6
            if taper == "tip":
                limit = min(limit, 1.0 - x * 0.92)
            for nx, nw in notches:
                if abs(x - nx) < nw:
                    limit -= 0.12 * (1 - abs(x - nx) / nw)
            if z > limit:
                continue
            if any(abs(x - hx) * fw < 1.1 and abs(z - hz) * fh < 0.9 for hx, hz in holes):
                continue
            best = None
            for x0, z0, x1, z1 in veins:
                L = math.hypot(x1 - x0, z1 - z0)
                d = abs((x1 - x0) * (z0 - z) - (x0 - x) * (z1 - z0)) / L
                t = ((x - x0) * (x1 - x0) + (z - z0) * (z1 - z0)) / (L * L)
                if best is None or d < best[0]:
                    best = (d, t)
            d, t = best
            dd = d * min(fw, fh)
            if dd < 0.55:
                c = "q" if (glow and t < 0.22) else "V"
            elif z > limit - 0.07:
                c = "m"
            elif dd < 1.4:
                c = "n"
            else:
                spot = math.sin(x * 7.0 + z * 2.3 + fw) * math.sin(z * 5.5 - x * 2.7 + fh)
                c = "m" if spot > 0.55 else ("M" if tr.random() > 0.06 else "m")
            grid[j][i] = c
    def f(i, j, fw2, fh2):
        ch = grid[j][i]
        if not ch:
            return (0, 0, 0, 0)
        if ch == "q":
            return exact("q")
        c = PAL[ch]
        z = (j + 0.5) / fh
        k = 1.08 - 0.36 * z                       # luz que atraviesa la membrana cerca del brazo
        if ch == "V":
            k = 1.0
        n = tr.uniform(0.96, 1.04)
        return tuple(max(0, min(255, int(v * k * n))) for v in c) + (255,)
    return f


YOUNG = False


def cracked(i, j, fw, fh):
    """Escamas con grietas finas de fuego de almas (como lava azul bajo la piel). Las crías aún no las tienen."""
    if YOUNG or fw < 20:
        return scales(i, j, fw, fh, "l") if (i * 7 + j * 3) % 11 == 0 else scales(i, j, fw, fh)
    seed = (fw * 7 + fh * 13) % 17
    n = 2 if fh >= 12 and fw >= 10 else 1
    for k in range(n):
        y0 = fh * ((0.5) if n == 1 else (0.32 + 0.38 * k))
        yc = y0 + 1.4 * math.sin(i * 0.6 + seed + k * 2.1) + 0.6 * math.sin(i * 1.7 + k)
        if abs(j - yc) < 0.5 and (i + k * 3 + seed) % 7 != 0:
            return exact("Q") if (i + j) % 6 else exact("W")
    return scales(i, j, fw, fh)


def spar_face(i, j, fw, fh):
    return px("j", 3) if i % 4 == 0 else px("i" if (i + j) % 3 else "I", 3)


def bone_plate(i, j, fw, fh):
    if i == 0 or j == 0 or i == fw - 1 or j == fh - 1:
        return px("j", 3)
    return px("I", 4) if (i + 2 * j) % 5 else px("i", 3)


def frill_fan(i, j, fw, fh):
    # abanico con radios óseos que salen desde la esquina delantera inferior
    cx, cy = 0, fh - 1
    ang = math.atan2(cy - j, i - cx + 0.01)
    r = math.hypot(i - cx, cy - j)
    if r > fh - 0.5 - 1.5 * abs(math.sin(ang * 6)):
        return (0, 0, 0, 0)
    if abs(math.sin(ang * 6)) < 0.18:
        return px("I", 3)
    return px("M" if (i + j) % 3 else "m", 3)


def tail_blade_face(i, j, fw, fh):
    cx = (fw - 1) / 2
    half = (fw / 2) * (1 - abs(j - fh * 0.45) / (fh * 0.6))
    if abs(i - cx) > half:
        return (0, 0, 0, 0)
    if abs(i - cx) > half - 1.0:
        return px("I", 3)                       # filo
    if abs(i - cx) < 0.6:
        return exact("q")
    return px("i", 3) if (i + j) % 3 else px("j", 3)


# ------------------------------------------------------------------ modelo
def mirror_origin(o, s):
    return [-(o[0] + s[0]), o[1], o[2]]


def build(young=False):
    global YOUNG
    YOUNG = young
    g = Geo("geometry.nether_dragon", 256, 512)
    pk = Packer([(0, 0, 256, 512)])
    paint = []

    def cube(bone, origin, size, faces, inflate=0.0, rotation=None, pivot=None, uv=None):
        uv = uv or pk.alloc(*[max(1, math.floor(v)) for v in size])
        g.cube(bone, "c", origin, size, uv, inflate, rotation=rotation, pivot=pivot)
        if faces is not None:
            paint.append((uv, size, faces))
        return uv

    def pair(bone_l, bone_r, origin, size, faces, rotation=None, pivot=None):
        """Cubo en el lado izquierdo (+X) y su espejo en el derecho, compartiendo UV."""
        uv = cube(bone_l, origin, size, faces, rotation=rotation, pivot=pivot)
        rot_r = [rotation[0], -rotation[1], -rotation[2]] if rotation else None
        piv_r = [-pivot[0], pivot[1], pivot[2]] if pivot else None
        cube(bone_r, mirror_origin(origin, size), size, None, rotation=rot_r, pivot=piv_r, uv=uv)

    def bone_pair(name, pivot, parent_l, parent_r=None, rotation=None):
        rot_r = [rotation[0], -rotation[1], -rotation[2]] if rotation else None
        g.bone(name + "_l", pivot, parent_l, rotation)
        g.bone(name + "_r", [-pivot[0], pivot[1], pivot[2]], parent_r or parent_l, rot_r)

    def spike(bone, x, y, z, h=3.0, lean=-35, w=1.2, side=0):
        cube(bone, [x - w / 2, y - 0.5, z - w / 2], [w, h, w * 1.6], {"all": horn, "bottom": fill("s")},
             rotation=[lean, 0, side], pivot=[x, y, z])

    def spike_pair(bone, x, y, z, h=3.0, lean=-35, w=1.1, out=28):
        pair(bone, bone, [x - w / 2, y - 0.5, z - w / 2], [w, h, w * 1.5], {"all": horn, "bottom": fill("s")},
             rotation=[lean, 0, -out], pivot=[x, y, z])

    flank = body_faces(glow_belly=False)
    flank["left"] = cracked
    flank["right"] = cracked

    # ---------------- raíz y cuerpo (más ancho y musculoso)
    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 26, 0], "root")
    cube("body", [-8.5, 20, -12], [17, 14.5, 25], flank)
    cube("body", [-8, 19, -21], [16, 14.5, 10], dict(flank, bottom=belly(True)))     # pecho
    cube("body", [-7, 21, 12], [14, 12, 5], body_faces())                             # caderas
    # espinas del lomo en doble fila (las de la montura se ocultan al ponerle silla)
    g.bone("sp_back", [0, 26, 0], "body")
    g.bone("saddle_spikes", [0, 26, 0], "body")
    for k, z in enumerate(range(-19, 15, 4)):
        bone = "saddle_spikes" if -15 <= z <= -1 else "sp_back"
        h = 5.5 if k % 2 == 0 else 4.0
        spike(bone, 0, 34.4, z, h=h, lean=-38, w=1.4)
        if k % 2 == 1:
            spike_pair(bone, 3.2, 34.0, z + 1.5, h=2.6, lean=-40, out=24)
    # placas óseas en hombros y caderas con púas
    g.bone("pl_plates", [0, 26, 0], "body")
    pair("pl_plates", "pl_plates", [7.6, 27.5, -21], [2.2, 6, 9], {"all": bone_plate, "left": bone_plate})
    pair("pl_plates", "pl_plates", [7.4, 26.5, 7], [2.2, 6, 8], {"all": bone_plate})
    spike_pair("pl_plates", 9.2, 32.5, -17, h=3.5, lean=-30, out=40)
    spike_pair("pl_plates", 9.2, 31.5, 10, h=3.0, lean=-30, out=40)

    # ---------------- cuello
    g.bone("neck1", [0, 29, -19], "body", [-40, 0, 0])
    cube("neck1", [-5, 24.5, -29], [10, 9.5, 11], body_faces(glow_belly=True))
    g.bone("sp_neck1", [0, 29, -19], "neck1")
    spike("sp_neck1", 0, 34, -24, 4.4, w=1.3)
    spike_pair("sp_neck1", 3.4, 32.5, -25, 2.4, out=40)
    g.bone("neck2", [0, 29, -28], "neck1", [-16, 0, 0])
    cube("neck2", [-4.5, 25, -37], [9, 8.5, 10], body_faces(glow_belly=True))
    g.bone("sp_neck2", [0, 29, -28], "neck2")
    spike("sp_neck2", 0, 33.4, -32, 4.0, w=1.2)
    spike_pair("sp_neck2", 3.0, 32.2, -33, 2.2, out=40)
    g.bone("neck3", [0, 29, -36], "neck2", [10, 0, 0])
    cube("neck3", [-4, 25.5, -44], [8, 7.5, 9], body_faces(glow_belly=True))
    g.bone("sp_neck3", [0, 29, -36], "neck3")
    spike("sp_neck3", 0, 33, -40, 3.6, w=1.1)

    # ---------------- cabeza: alargada, ceño bajo y una "barba" de púas a lo largo de mandíbula y mejillas
    g.bone("head", [0, 29, -42], "neck3", [44, 0, 0])
    eye_side = lambda front_at_start: (lambda i, j, fw, fh: eye_px(i, j, fw, fh, front_at_start))
    cube("head", [-5.5, 25, -54], [11, 9, 13], {"all": scale_face, "top": spine_top(False), "bottom": belly(),
                                                 "left": eye_side(True), "right": eye_side(False), "front": scale_face})
    cube("head", [-4, 25.4, -65], [8, 6.2, 11], {"all": snout_side, "top": snout_top, "bottom": mouth_roof,
                                                  "front": snout_front})
    cube("head", [-3.4, 26.2, -68.4], [6.8, 5.2, 3.4], {"all": snout_side, "top": snout_top, "bottom": mouth_roof,
                                                        "front": snout_front, "back": CLEAR})           # morro con fosas
    pair("head", "head", [1.2, 30.6, -68.8], [2.0, 1.4, 4], {"all": fill("s", "S", 0.3)})            # bultos de las fosas
    cube("head", [-2.4, 31.6, -64], [4.8, 1.0, 10], {"all": fill("s", "S", 0.4), "top": spine_top(False)})   # cresta nasal
    # ceño: crestas pesadas inclinadas hacia el hocico, tapan la parte alta del ojo
    pair("head", "head", [3.0, 31.4, -56.5], [3.0, 2.8, 10], {"all": fill("s", "S", 0.3), "top": scale_face},
         rotation=[14, -6, 0], pivot=[4.5, 32.8, -47])
    for k in range(3):                                                                               # nudos del ceño
        pair("head", "head", [4.6 - k * 0.2, 33.4 - k * 0.6, -55 + k * 3.2], [1.2, 1.4, 2], {"all": horn},
             rotation=[-30, -10, 0], pivot=[5, 34, -54 + k * 3.2])
    # dientes y colmillos
    for z in (-64.4, -61.8, -59.2, -56.6, -54.0):
        pair("head", "head", [3.1, 24.0, z], [0.8, 1.6, 0.8], {"all": fill("T"), "top": CLEAR})
    pair("head", "head", [2.4, 23.6, -67.4], [0.9, 2.0, 0.9], {"all": fill("T"), "top": CLEAR})          # colmillos
    # cuernos principales: gruesos y barridos hacia atrás
    bone_pair("horn", [3.9, 33.2, -46], "head", rotation=[12, -16, 0])
    pair("horn_l", "horn_r", [2.4, 31.8, -46], [3, 3, 11], {"all": horn})
    bone_pair("horn2", [3.9, 33.2, -35.2], "horn_l", "horn_r", rotation=[10, -8, 0])
    pair("horn2_l", "horn2_r", [2.8, 32.1, -35.2], [2.2, 2.2, 9], {"all": horn})
    bone_pair("horn3", [3.9, 33.2, -26.4], "horn2_l", "horn2_r", rotation=[10, -6, 0])
    pair("horn3_l", "horn3_r", [3.2, 32.5, -26.4], [1.4, 1.4, 6.5], {"all": horn})
    pair("horn3_l", "horn3_r", [3.4, 32.7, -20.2], [1, 1, 3.5], {"all": fill("j", "i", 0.3)})
    # cuernos secundarios bajos, hacia atrás y afuera
    bone_pair("hornb", [5.4, 28.4, -46], "head", rotation=[-4, -34, 0])
    pair("hornb_l", "hornb_r", [4.6, 27.6, -46], [1.8, 1.8, 7.5], {"all": horn})
    pair("hornb_l", "hornb_r", [4.9, 27.9, -38.7], [1.1, 1.1, 3.5], {"all": fill("j", "i", 0.3)})
    # barba de púas: mejillas, contorno de la cabeza y cuello
    g.bone("head_spikes", [0, 29, -42], "head")
    for k, (y, z, ln) in enumerate([(26.0, -58, 2.6), (26.4, -55, 3.2), (26.8, -52, 3.8), (27.4, -49, 4.4),
                                    (28.4, -46, 4.6), (30.0, -45, 4.2), (31.6, -44.6, 3.6)]):
        pair("head_spikes", "head_spikes", [5.0, y - 0.55, z], [1.1, 1.1, ln], {"all": horn},
             rotation=[-12 + k * 6, -38 + k * 3, 0], pivot=[5.5, y, z])
    for k, (y, z) in enumerate([(26.5, -50), (28.0, -48), (29.6, -47.5)]):                           # segunda fila
        pair("head_spikes", "head_spikes", [4.4, y - 0.45, z], [0.9, 0.9, 3.0], {"all": horn},
             rotation=[-20 + k * 10, -58, 0], pivot=[4.8, y, z])
    # gorgueras: abanico de púas detrás de la mandíbula
    bone_pair("frill", [5.6, 26, -47], "head", rotation=[0, -24, 0])
    pair("frill_l", "frill_r", [5.6, 22.0, -47], [0.1, 9, 9], {"all": frill_fan})
    # mandíbula
    g.bone("jaw", [0, 26, -43], "head")
    cube("jaw", [-4, 23, -64], [8, 2.6, 21], {"all": snout_side, "top": jaw_top, "bottom": belly(), "front": fill("s", "S", 0.4)})
    cube("jaw", [-3.2, 23.3, -67.6], [6.4, 2.2, 3.6], {"all": snout_side, "top": jaw_top, "bottom": fill("s", "S", 0.4),
                                                       "front": fill("s", "S", 0.4), "back": CLEAR})
    for z in (-63.2, -60.6, -58.0, -55.4, -52.8):
        pair("jaw", "jaw", [3.0, 25.5, z], [0.8, 1.4, 0.8], {"all": fill("T"), "bottom": CLEAR})
    pair("jaw", "jaw", [2.3, 25.5, -66.4], [0.9, 1.6, 0.9], {"all": fill("T"), "bottom": CLEAR})
    g.bone("jaw_spikes", [0, 26, -43], "jaw")
    for k, z in enumerate((-62, -58.5, -55, -51.5, -48)):                                             # púas de la mandíbula
        pair("jaw_spikes", "jaw_spikes", [3.6, 22.9, z], [1.1, 1.1, 2.6 + k * 0.5], {"all": horn},
             rotation=[-32, -30, 0], pivot=[4.1, 23.4, z])
    for k, z in enumerate((-60, -55, -50)):                                                           # púas bajo el mentón
        cube("jaw_spikes", [-0.55, 21.6, z], [1.1, 2.6, 1.1], {"all": horn}, rotation=[38, 0, 0], pivot=[0, 23, z + 0.5])

    # ---------------- cola (6 tramos, púas laterales y hoja ósea al final)
    tail = [([-5.8, 22.5, 16], [11.6, 10.5, 12]), ([-4.8, 23.5, 27], [9.6, 8.5, 12]), ([-3.8, 24.5, 38], [7.6, 6.5, 12]),
            ([-2.8, 25.5, 49], [5.6, 4.5, 12]), ([-1.9, 26, 60], [3.8, 3.5, 11]), ([-1.3, 26.4, 70], [2.6, 2.6, 8])]
    rots = [[-12, 0, 0], [-6, 0, 0], [4, 0, 0], [7, 0, 0], [6, 0, 0], [4, 0, 0]]
    parent = "body"
    for k, (o, s) in enumerate(tail):
        name = "tail%d" % (k + 1)
        g.bone(name, [0, o[1] + s[1] / 2, o[2]], parent, rots[k])
        cube(name, o, s, flank if k < 2 else body_faces())
        if k < 5:
            sp = "sp_" + name
            g.bone(sp, [0, o[1] + s[1] / 2, o[2]], name)
            spike(sp, 0, o[1] + s[1], o[2] + s[2] / 2, 4.6 - k * 0.7, w=1.3 - k * 0.1)
            if 0 < k < 4:
                spike_pair(sp, o[0] * -1 - 0.3, o[1] + s[1] * 0.55, o[2] + s[2] / 2, 2.8 - k * 0.4, lean=-50, out=70)
        parent = name
    # hoja de la cola: dos filos óseos en forma de hacha doble
    g.bone("tail_blade", [0, 27.7, 74], "tail6")
    cube("tail_blade", [-6, 27.5, 72], [12, 0.4, 9], {"top": tail_blade_face, "bottom": tail_blade_face, "all": fill("i")})
    cube("tail_blade", [-0.8, 27.0, 74], [1.6, 1.6, 9], {"all": horn})
    cube("tail_blade", [-0.5, 28.4, 75], [1, 3.2, 1.4], {"all": horn}, rotation=[-40, 0, 0], pivot=[0, 28.6, 75.5])
    # aleta (crías y jóvenes: se ve en lugar de la hoja)
    g.bone("tail_fin", [0, 27.7, 70], "tail6")
    cube("tail_fin", [-7, 27.6, 71], [14, 0.2, 13], {"top": tail_fin, "bottom": tail_fin, "all": fill("V")})

    # ---------------- patas delanteras (codos con espolón, garras curvas)
    bone_pair("leg_front", [7, 29, -16], "body")
    pair("leg_front_l", "leg_front_r", [5.5, 17, -19.5], [6, 13.5, 7], {"all": cracked, "bottom": fill("s")})
    bone_pair("leg_front2", [8.5, 18, -16], "leg_front_l", "leg_front_r", rotation=[-10, 0, 0])
    pair("leg_front2_l", "leg_front2_r", [6.25, 4.5, -18.25], [4.5, 14, 4.5], {"all": scale_face})
    pair("leg_front2_l", "leg_front2_r", [8.0, 13, -14.6], [1.2, 1.2, 3.6], {"all": horn}, rotation=[-50, 0, 0], pivot=[8.6, 13.6, -14.6])
    bone_pair("foot_front", [8.5, 4.5, -16], "leg_front2_l", "leg_front2_r", rotation=[10, 0, 0])
    pair("foot_front_l", "foot_front_r", [5.75, 0, -21], [5.5, 4, 7.5], {"all": scale_face, "bottom": fill("s")})
    for dx in (0.1, 2.25, 4.4):
        pair("foot_front_l", "foot_front_r", [5.75 + dx, 0.6, -23.8], [1, 1.6, 3], {"all": ivory})
        pair("foot_front_l", "foot_front_r", [5.75 + dx, 0, -25.2], [1, 1, 1.6], {"all": fill("i")})
    pair("foot_front_l", "foot_front_r", [5.0, 0.5, -17.5], [1, 1.2, 2.4], {"all": ivory})

    # ---------------- patas traseras (digitígradas, muslos con grietas de alma)
    bone_pair("leg_back", [7, 28, 7], "body")
    pair("leg_back_l", "leg_back_r", [5, 14.5, 1.5], [7, 14.5, 11], {"all": cracked, "bottom": fill("s")})
    bone_pair("leg_back2", [8.5, 16.5, 10], "leg_back_l", "leg_back_r", rotation=[28, 0, 0])
    pair("leg_back2_l", "leg_back2_r", [6.25, 4, 8], [4.5, 13, 5.5], {"all": scale_face})
    pair("leg_back2_l", "leg_back2_r", [7.9, 15.5, 12.6], [1.2, 1.2, 3.4], {"all": horn}, rotation=[50, 0, 0], pivot=[8.5, 16, 12.6])
    bone_pair("foot_back", [8.5, 4.5, 10.5], "leg_back2_l", "leg_back2_r", rotation=[-28, 0, 0])
    pair("foot_back_l", "foot_back_r", [5.75, 0, 3.5], [5.5, 4.5, 9], {"all": scale_face, "bottom": fill("s")})
    for dx in (0.1, 2.25, 4.4):
        pair("foot_back_l", "foot_back_r", [5.75 + dx, 0.6, 1.0], [1, 1.6, 3], {"all": ivory})
        pair("foot_back_l", "foot_back_r", [5.75 + dx, 0, -0.4], [1, 1, 1.6], {"all": fill("i")})
    pair("foot_back_l", "foot_back_r", [7.6, 0.5, 12.3], [1.2, 1.2, 2.2], {"all": ivory})

    # ---------------- alas largas: 3 secciones, dedos óseos en relieve, garras, membrana moteada y rasgada
    W1, W2, W3 = 24, 30, 28                     # largo de cada sección
    D1, D2, D3 = 30, 34, 30                     # ancho de la membrana
    X2, X3 = 6 + W1, 6 + W1 + W2
    v1 = ((0.0, 0.0, 0.05, 1.0), (1.0, 0.0, 0.75, 1.0))
    v2 = ((0.0, 0.0, 0.35, 1.0), (0.0, 0.0, 0.85, 1.0), (0.0, 0.0, 1.0, 0.55))
    v3 = ((0.0, 0.0, 0.25, 0.75), (0.0, 0.0, 1.0, 0.05))
    m1 = membrane(W1, D1, veins=v1, glow=True)
    m2 = membrane(W2, D2, veins=v2, glow=True, torn=True)
    m3 = membrane(W3, D3, taper="tip", veins=v3, torn=True)

    def spars(bone, x0, z0, W, D, veins, thick=0.8):
        """Dedos óseos en relieve siguiendo las venas de la membrana."""
        for a_, b_, c_, d_ in veins:
            xs, zs = x0 + a_ * W, z0 + b_ * D
            dx, dz = (c_ - a_) * W, (d_ - b_) * D
            L = math.hypot(dx, dz)
            ang = math.degrees(math.atan2(-dz, dx))
            cube(bone, [xs, 32.6, zs - thick / 2], [L, thick, thick], {"all": spar_face},
                 rotation=[0, ang, 0], pivot=[xs, 33.0, zs])
            # garra al final del dedo
            cube(bone, [xs + dx - 0.5, 32.5, zs + dz - 0.5], [1, 1, 1], {"all": fill("i")})

    bone_pair("wing", [6, 33, -12], "body")
    pair("wing_l", "wing_r", [6, 31.4, -13.8], [W1, 3.2, 3.4], {"all": scale_face, "top": spine_top(False)})
    pair("wing_l", "wing_r", [6, 32.9, -12], [W1, 0.1, D1], {"top": m1, "bottom": m1, "all": fill("V")})
    for x in (11, 17, 23):                                                                            # púas del borde
        pair("wing_l", "wing_r", [x - 0.5, 34.2, -13.0], [1, 2.2, 1.4], {"all": horn}, rotation=[-50, 0, 0], pivot=[x, 34.4, -12.4])
    bone_pair("wing2", [X2, 33, -12], "wing_l", "wing_r")
    pair("wing2_l", "wing2_r", [X2, 31.8, -13.3], [W2, 2.4, 2.4], {"all": scale_face})
    pair("wing2_l", "wing2_r", [X2, 32.9, -11.5], [W2, 0.1, D2], {"top": m2, "bottom": m2, "all": fill("V")})
    for x in (X2 + 8, X2 + 18):
        pair("wing2_l", "wing2_r", [x - 0.45, 33.9, -12.8], [0.9, 1.8, 1.2], {"all": horn}, rotation=[-50, 0, 0], pivot=[x, 34.1, -12.3])
    pair("wing2_l", "wing2_r", [X2 - 1.0, 31.8, -17.8], [2, 2, 4.6], {"all": ivory})                 # garra del pulgar
    pair("wing2_l", "wing2_r", [X2 - 0.6, 32.2, -20.2], [1.2, 1.2, 2.4], {"all": fill("i")})
    bone_pair("wing3", [X3, 33, -12], "wing2_l", "wing2_r")
    pair("wing3_l", "wing3_r", [X3, 32.3, -12.7], [W3 - 1, 1.4, 1.4], {"all": scale_face})
    pair("wing3_l", "wing3_r", [X3, 32.9, -11.5], [W3, 0.1, D3], {"top": m3, "bottom": m3, "all": fill("V")})
    pair("wing3_l", "wing3_r", [X3 + W3 - 1.4, 32.1, -13.1], [3, 1.8, 1.8], {"all": ivory})        # garra de la punta
    # dedos óseos (izquierda; el lado derecho se refleja con pair dentro de spars_pair)
    for bone, x0, W, D, vv in (("wing", 6, W1, D1, v1), ("wing2", X2, W2, D2, v2), ("wing3", X3, W3, D3, v3)):
        for a_, b_, c_, d_ in vv:
            xs, zs = x0 + a_ * W, -12 + b_ * D
            dx, dz = (c_ - a_) * W, (d_ - b_) * D
            L = math.hypot(dx, dz)
            ang = math.degrees(math.atan2(-dz, dx))
            pair(bone + "_l", bone + "_r", [xs, 32.55, zs - 0.4], [L, 0.8, 0.8], {"all": spar_face},
                 rotation=[0, ang, 0], pivot=[xs, 32.95, zs])

    # ---------------- montura (visible solo con silla)
    g.bone("saddle", [0, 34, -6], "body")
    cube("saddle", [-8.9, 27, -13], [17.8, 7.7, 14], {"all": blanket_side, "top": blanket_top, "bottom": CLEAR,
                                                      "front": CLEAR, "back": CLEAR})
    cube("saddle", [-5, 34.3, -12], [10, 1.5, 11], {"all": leather, "top": seat_top})
    cube("saddle", [-4, 35.8, -10.5], [8, 1.4, 7], {"all": fill("r", "R", 0.4), "top": cushion})
    cube("saddle", [-1.5, 35.8, -12.6], [3, 3.6, 2.2], {"all": leather, "front": pommel_front})
    cube("saddle", [-1.8, 39.4, -12.9], [3.6, 1, 2.8], {"all": gold})
    cube("saddle", [-4.6, 35.8, -3.6], [9.2, 3.6, 2.2], {"all": leather, "top": gold, "back": cantle_back})
    cube("saddle", [-8.75, 19.4, -5], [17.5, 15.3, 2.2], {"all": strap, "top": CLEAR, "front": CLEAR, "back": CLEAR})
    pair("saddle", "saddle", [8.7, 26.2, -8.6], [0.6, 7.5, 1.2], {"all": fill("K", "k", 0.3)})
    pair("saddle", "saddle", [8.4, 24.6, -9.6], [1.4, 1.6, 3.2], {"all": gold, "top": CLEAR})
    pair("saddle", "saddle", [8.6, 26.5, -1.5], [3, 5.5, 6.5], {"all": saddlebag, "top": fill("k")})
    cube("saddle", [-0.5, 35.8, -1.6], [1, 13, 1], {"all": fill("g", "G", 0.3)})                  # asta del estandarte
    cube("saddle", [-0.75, 48.8, -1.85], [1.5, 1.5, 1.5], {"all": fill("U", "u", 0.3)})
    cube("saddle", [-0.05, 41.5, -0.6], [0.1, 7, 8], {"all": banner})
    # bridas en el hocico (hijas de la cabeza)
    g.bone("bridle", [0, 29, -42], "head")
    cube("bridle", [-3.75, 25.3, -57.5], [7.5, 6.4, 1.3], {"all": fill("K", "k", 0.3), "front": CLEAR, "back": CLEAR})
    pair("bridle", "bridle", [3.7, 26.6, -57.8], [0.6, 1.8, 1.8], {"all": gold})
    pair("bridle", "bridle", [3.6, 27.2, -56.2], [0.4, 0.6, 13.5], {"all": fill("K", "k", 0.3)})

    # ---------------- armadura de dragón (visible solo con armadura)
    g.bone("armor_head", [0, 29, -42], "head")
    cube("armor_head", [-5.4, 33.4, -53.4], [10.8, 1.8, 10], {"all": armor_plate, "top": armor_top})
    cube("armor_head", [-3.9, 31.2, -62.4], [7.8, 1.2, 9.5], {"all": armor_plate, "top": armor_top})
    g.bone("armor_neck1", [0, 29, -19], "neck1")
    cube("armor_neck1", [-4.9, 33.2, -28.6], [9.8, 1.4, 10], {"all": armor_plate, "top": armor_top})
    g.bone("armor_neck2", [0, 29, -28], "neck2")
    cube("armor_neck2", [-4.4, 32.6, -36.6], [8.8, 1.4, 9], {"all": armor_plate, "top": armor_top})
    g.bone("armor_chest", [0, 26, 0], "body")
    cube("armor_chest", [-8.4, 18.4, -21.8], [16.8, 14, 1.6], {"all": armor_plate, "front": armor_breast})
    pair("armor_chest", "armor_chest", [8.1, 22, -20.5], [1.4, 10, 8], {"all": armor_plate, "left": armor_side})

    sheet = Sheet(256, 512)
    for (u, v), size, faces in paint:
        paint_box(sheet, u, v, size, faces)
    return g, sheet.img


def paint_box(sheet, u, v, size, faces):
    """GeckoLib redondea hacia abajo el tamaño de cada cubo para el UV. Si algún eje queda en 0 (cubos finos o
    diminutos), las caras leen un solo texel: se pinta toda la zona reservada con el color del cubo."""
    fl = [math.floor(x) for x in size]
    if sum(1 for x in fl if x == 0) >= 2:
        w, h, d = [max(1, x) for x in fl]
        fn = faces.get("all") or next(iter(faces.values()))
        for j in range(h + d):
            for i in range(2 * (w + d)):
                sheet.px(u + i, v + j, fn(min(i, w - 1), min(j, h - 1), w, h))
        return
    sheet.box(u, v, fl[0], fl[1], fl[2], faces)


# ------------------------------------------------------------------ caras especiales
def eye_px(i, j, fw, fh, front_at_start):
    fi = i if front_at_start else fw - 1 - i
    if j == 3 and 1 <= fi <= 4:
        return exact("E") if fi in (2, 3) else exact("q")      # ranura del ojo
    if j in (2, 4) and 0 <= fi <= 5:
        return px("s", 2) if j == 4 else px("V", 2)            # cuenca hundida
    if j == 5 and 1 <= fi <= 3:
        return px("s", 2)
    return scales(i, j, fw, fh)


def snout_side(i, j, fw, fh):
    # línea de la boca larga con dientes a la vista
    if j == fh - 1:
        return px("T", 3) if i % 2 == 0 else px("o", 2)
    if j == fh - 2:
        return px("O", 2) if i % 3 else px("s", 2)
    return scales(i, j, fw, fh)


def snout_top(i, j, fw, fh):
    return scales(i, j, fw, fh) if (i + j) % 5 else px("s", 2)


def snout_front(i, j, fw, fh):
    # fosas nasales grandes
    if j in (0, 1) and i in (0, 1, fw - 2, fw - 1):
        return px("V", 2) if j == 1 else px("s", 2)
    if j == fh - 1:
        return px("T", 3) if i % 2 == 0 else px("o", 2)
    return scales(i, j, fw, fh)


def mouth_roof(i, j, fw, fh):
    return px("O" if (i + j) % 3 else "o", 3)


def jaw_top(i, j, fw, fh):
    if i in (0, fw - 1):
        return px("s", 2)
    return px("O" if j % 3 else "o", 3) if 1 < i < fw - 2 else px("o", 2)


def ear_fin(i, j, fw, fh):
    if j > fh - 1 - i * 0.9:
        return (0, 0, 0, 0)
    return px("m" if (i + j) % 3 else "V", 3)


def tail_fin(i, j, fw, fh):
    # abanico en punta de flecha con radios oscuros y borde festoneado
    cx = (fw - 1) / 2
    half = (fw / 2) * (1 - abs(j - fh * 0.40) / (fh * 0.62))
    if j > fh * 0.4:
        half -= 0.9 * abs(math.sin((i - cx) * 1.1))
    if abs(i - cx) > half:
        return (0, 0, 0, 0)
    ang = math.atan2(j, (i - cx) + 0.01)
    if abs(i - cx) < 0.6 or abs(math.sin(ang * 4)) < 0.16:
        return px("V", 2)
    z = j / max(1, fh - 1)
    c = _mix(PAL["n"], PAL["m"], z)
    return c + (255,)


def leather(i, j, fw, fh):
    if j == 0 or j == fh - 1:
        return px("K", 2)
    return px("L", 4) if (i * 3 + j) % 5 else px("k", 3)


def gold(i, j, fw, fh):
    return px("Y" if (i + j) % 4 == 0 else ("G" if (i + j) % 3 else "g"), 3)


def seat_top(i, j, fw, fh):
    if i == 0 or i == fw - 1 or j == 0 or j == fh - 1:
        return px("G", 3) if (i + j) % 2 else px("g", 2)
    return leather(i, j, fw, fh)


def cushion(i, j, fw, fh):
    if (i + j) % 3 == 0:
        return px("r", 3)
    if i % 3 == 1 and j % 3 == 1:
        return px("G", 2)                       # botones dorados del capitoné
    return px("R", 3)


def pommel_front(i, j, fw, fh):
    if j == 1 and i == fw // 2:
        return exact("U")
    return leather(i, j, fw, fh)


def cantle_back(i, j, fw, fh):
    mid = fw // 2
    if j in (1, 2) and abs(i - mid) <= 1:
        return px("G", 2) if abs(i - mid) == 1 else exact("U")
    return leather(i, j, fw, fh)


def blanket_top(i, j, fw, fh):
    if i <= 1 or i >= fw - 2:
        return px("G", 3) if (j % 2) else px("g", 3)
    return px("R", 3) if (i + j) % 5 else px("r", 3)


def blanket_side(i, j, fw, fh):
    # manta roja con borde dorado y flecos, emblema del reino (rombo de rubí)
    if j == fh - 1:
        return px("G", 3) if i % 2 else (0, 0, 0, 0)
    if j == fh - 2:
        return px("g", 3)
    cx, cy = fw // 2, fh // 2 - 1
    d = abs(i - cx) + abs(j - cy)
    if fw > 8 and d <= 2:
        return exact("U") if d <= 1 else px("G", 2)
    return px("R", 3) if (i + j) % 6 else px("r", 3)


def strap(i, j, fw, fh):
    if j % 5 == 0 and i in (0, fw - 1):
        return px("G", 2)
    return px("K", 3) if (i + j) % 3 else px("k", 3)


def saddlebag(i, j, fw, fh):
    if j == 1:
        return px("k", 2)
    if j == 2 and i == fw // 2:
        return px("G", 2)
    return leather(i, j, fw, fh)


def banner(i, j, fw, fh):
    if j >= fh - 1 and i % 2:
        return (0, 0, 0, 0)
    cx, cy = fw / 2 - 0.5, fh / 2 - 0.5
    d = abs(i - cx) + abs(j - cy)
    if d <= 1.2:
        return exact("U")
    if d <= 2.2:
        return px("G", 2)
    if i == 0 or j == 0:
        return px("G", 2)
    return px("R", 3) if (i + j) % 4 else px("r", 3)


def armor_plate(i, j, fw, fh):
    if j == 0 or j == fh - 1 or i == 0 or i == fw - 1:
        return px("G", 3)
    return px("A", 3) if (i + j) % 4 else px("a", 3)


def armor_top(i, j, fw, fh):
    if i == 0 or i == fw - 1 or j == 0 or j == fh - 1:
        return px("G", 3) if (i + j) % 2 else px("g", 3)
    if i == fw // 2:
        return px("Y", 3) if j % 2 else px("G", 3)
    if j == fh // 2 and abs(i - fw // 2) == 2:
        return exact("U")
    return px("A", 3) if (i + j) % 3 else px("a", 3)


def armor_breast(i, j, fw, fh):
    cx, cy = fw // 2, fh // 2
    d = abs(i - cx) + abs(j - cy)
    if d <= 1:
        return exact("U")
    if d <= 3:
        return px("G", 2)
    return armor_top(i, j, fw, fh)


def armor_side(i, j, fw, fh):
    if j % 3 == 0:
        return px("G", 3)
    return px("A", 3)


# ================================================================== ANIMACIONES
A = "animation.nether_dragon."

FOLD = ([-42, -58, -76], [0, 6, 176], [0, -8, 178])
FOLD_L = {"wing_l": FOLD[0], "wing2_l": FOLD[1], "wing3_l": FOLD[2]}
FOLD_R = {"wing_r": [FOLD[0][0], -FOLD[0][1], -FOLD[0][2]], "wing2_r": [FOLD[1][0], -FOLD[1][1], -FOLD[1][2]],
          "wing3_r": [FOLD[2][0], -FOLD[2][1], -FOLD[2][2]]}


def folded(extra=None, t=(0,)):
    """Alas plegadas a lo largo del cuerpo."""
    out = {}
    for d in (FOLD_L, FOLD_R):
        for b, r in d.items():
            out[b] = {"rotation": {k: r for k in t}}
    if extra:
        for b, ch in extra.items():
            out.setdefault(b, {}).update(ch)
    return out


def wing_cycle(t_vals, down_l, up_l):
    """Keyframes de aleteo para ambas alas: down/up son (wing, wing2, wing3) en el lado izquierdo."""
    res = {}
    for side, sign in (("l", 1), ("r", -1)):
        for idx, bname in enumerate(("wing", "wing2", "wing3")):
            frames = {}
            for t, pose in t_vals:
                r = (down_l if pose == "d" else up_l if pose == "u" else pose)[idx]
                frames[t] = [r[0], r[1] * sign, r[2] * sign]
            res["%s_%s" % (bname, side)] = {"rotation": frames}
    return res


def merge(*ds):
    out = {}
    for d in ds:
        for b, ch in d.items():
            out.setdefault(b, {}).update(ch)
    return out


def animations():
    a = {}
    # ---------------- en tierra
    a[A + "idle"] = anim(4.0, True, folded({
        "body": {"position": {0: [0, 0, 0], 2.0: [0, 0.4, 0], 4.0: [0, 0, 0]}},
        "neck1": {"rotation": {0: [0, 0, 0], 2.0: [-3, 4, 0], 4.0: [0, 0, 0]}},
        "neck2": {"rotation": {0: [0, 0, 0], 2.0: [-2, 3, 0], 4.0: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 1.0: [4, -6, 0], 2.0: [0, -10, 0], 3.0: [-3, 2, 0], 4.0: [0, 0, 0]}},
        "jaw": {"rotation": {0: [0, 0, 0], 3.0: [0, 0, 0], 3.3: [8, 0, 0], 3.6: [0, 0, 0]}},
        "tail1": {"rotation": {0: [0, 6, 0], 2.0: [0, -6, 0], 4.0: [0, 6, 0]}},
        "tail2": {"rotation": {0: [0, 8, 0], 2.0: [0, -8, 0], 4.0: [0, 8, 0]}},
        "tail3": {"rotation": {0: [0, 10, 0], 2.0: [0, -10, 0], 4.0: [0, 10, 0]}},
        "tail4": {"rotation": {0: [0, 12, 0], 2.0: [0, -12, 0], 4.0: [0, 12, 0]}},
        "tail5": {"rotation": {0: [0, 14, 0], 2.0: [0, -14, 0], 4.0: [0, 14, 0]}},
    }, t=(0, 4.0)))
    gait = lambda L, amp: {
        "leg_front_l": {"rotation": {0: [-amp, 0, 0], L / 2: [amp, 0, 0], L: [-amp, 0, 0]}},
        "leg_front_r": {"rotation": {0: [amp, 0, 0], L / 2: [-amp, 0, 0], L: [amp, 0, 0]}},
        "leg_back_l": {"rotation": {0: [amp, 0, 0], L / 2: [-amp, 0, 0], L: [amp, 0, 0]}},
        "leg_back_r": {"rotation": {0: [-amp, 0, 0], L / 2: [amp, 0, 0], L: [-amp, 0, 0]}},
        "leg_front2_l": {"rotation": {0: [0, 0, 0], L / 4: [-20, 0, 0], L / 2: [0, 0, 0], L: [0, 0, 0]}},
        "leg_front2_r": {"rotation": {0: [0, 0, 0], L / 2: [0, 0, 0], 3 * L / 4: [-20, 0, 0], L: [0, 0, 0]}},
        "leg_back2_l": {"rotation": {0: [0, 0, 0], L / 2: [0, 0, 0], 3 * L / 4: [18, 0, 0], L: [0, 0, 0]}},
        "leg_back2_r": {"rotation": {0: [0, 0, 0], L / 4: [18, 0, 0], L / 2: [0, 0, 0], L: [0, 0, 0]}},
        "body": {"position": {0: [0, 0, 0], L / 4: [0, 0.8, 0], L / 2: [0, 0, 0], 3 * L / 4: [0, 0.8, 0], L: [0, 0, 0]},
                 "rotation": {0: [0, 2, 1], L / 2: [0, -2, -1], L: [0, 2, 1]}},
        "neck1": {"rotation": {0: [2, 0, 0], L / 4: [-2, 0, 0], L / 2: [2, 0, 0], 3 * L / 4: [-2, 0, 0], L: [2, 0, 0]}},
        "head": {"rotation": {0: [-2, 0, 0], L / 4: [2, 0, 0], L / 2: [-2, 0, 0], 3 * L / 4: [2, 0, 0], L: [-2, 0, 0]}},
        "tail1": {"rotation": {0: [0, 8, 0], L / 2: [0, -8, 0], L: [0, 8, 0]}},
        "tail2": {"rotation": {0: [0, 6, 0], L / 2: [0, -6, 0], L: [0, 6, 0]}},
        "tail3": {"rotation": {0: [0, 4, 0], L / 2: [0, -10, 0], L: [0, 4, 0]}},
        "tail4": {"rotation": {0: [0, 0, 0], L / 2: [0, -12, 0], L: [0, 0, 0]}},
        "tail5": {"rotation": {0: [0, -4, 0], L / 2: [0, -14, 0], L: [0, -4, 0]}},
    }
    a[A + "walk"] = anim(1.6, True, folded(gait(1.6, 22), t=(0, 1.6)))
    run = gait(0.8, 34)
    run["body"]["rotation"] = {0: [4, 0, 0], 0.2: [-3, 0, 0], 0.4: [4, 0, 0], 0.6: [-3, 0, 0], 0.8: [4, 0, 0]}
    run["body"]["position"] = {0: [0, 0, 0], 0.2: [0, 1.6, 0], 0.4: [0, 0, 0], 0.6: [0, 1.6, 0], 0.8: [0, 0, 0]}
    run["neck1"] = {"rotation": {0: [14, 0, 0], 0.4: [10, 0, 0], 0.8: [14, 0, 0]}}
    run_wings = folded(t=(0, 0.8))
    for b in ("wing_l", "wing_r"):
        r = run_wings[b]["rotation"][0]
        run_wings[b]["rotation"] = {0: r, 0.4: [r[0] - 6, r[1] * 0.9, r[2] * 2.5], 0.8: r}
    a[A + "run"] = anim(0.8, True, merge(run_wings, run))
    # descansando: se echa, enrosca la cola y apoya la cabeza en el suelo
    rest = {
        "body": {"position": {0: [0, -14.5, 0], 3.0: [0, -14.0, 0], 6.0: [0, -14.5, 0]}},
        "leg_front_l": {"rotation": {0: [-80, 0, 0], 6.0: [-80, 0, 0]}},
        "leg_front_r": {"rotation": {0: [-80, 0, 0], 6.0: [-80, 0, 0]}},
        "leg_front2_l": {"rotation": {0: [70, 0, 0], 6.0: [70, 0, 0]}},
        "leg_front2_r": {"rotation": {0: [70, 0, 0], 6.0: [70, 0, 0]}},
        "foot_front_l": {"rotation": {0: [10, 0, 0], 6.0: [10, 0, 0]}},
        "foot_front_r": {"rotation": {0: [10, 0, 0], 6.0: [10, 0, 0]}},
        "leg_back_l": {"rotation": {0: [-70, 0, 0], 6.0: [-70, 0, 0]}},
        "leg_back_r": {"rotation": {0: [-70, 0, 0], 6.0: [-70, 0, 0]}},
        "leg_back2_l": {"rotation": {0: [-18, 0, 0], 6.0: [-18, 0, 0]}},
        "leg_back2_r": {"rotation": {0: [-18, 0, 0], 6.0: [-18, 0, 0]}},
        "foot_back_l": {"rotation": {0: [88, 0, 0], 6.0: [88, 0, 0]}},
        "foot_back_r": {"rotation": {0: [88, 0, 0], 6.0: [88, 0, 0]}},
        "neck1": {"rotation": {0: [26, -24, 0], 6.0: [26, -24, 0]}},
        "neck2": {"rotation": {0: [14, -22, 0], 6.0: [14, -22, 0]}},
        "neck3": {"rotation": {0: [8, -18, 0], 6.0: [8, -18, 0]}},
        "head": {"rotation": {0: [4, -10, 6], 3.0: [6, -10, 6], 6.0: [4, -10, 6]}},
        "tail1": {"rotation": {0: [10, -22, 0], 6.0: [10, -22, 0]}},
        "tail2": {"rotation": {0: [0, -28, 0], 6.0: [0, -28, 0]}},
        "tail3": {"rotation": {0: [-4, -30, 0], 6.0: [-4, -30, 0]}},
        "tail4": {"rotation": {0: [-6, -30, 0], 3.0: [-6, -34, 0], 6.0: [-6, -30, 0]}},
        "tail5": {"rotation": {0: [-6, -28, 0], 3.0: [-6, -36, 0], 6.0: [-6, -28, 0]}},
    }
    a[A + "rest"] = anim(6.0, True, folded(rest, t=(0, 6.0)))
    # sentado (orden de quedarse quieto): patas traseras dobladas, pecho erguido
    sit = {
        "body": {"rotation": {0: [-18, 0, 0], 3.0: [-18, 0, 0]}, "position": {0: [0, -6, 2], 3.0: [0, -6, 2]}},
        "leg_back_l": {"rotation": {0: [-48, 0, 0], 3.0: [-48, 0, 0]}},
        "leg_back_r": {"rotation": {0: [-48, 0, 0], 3.0: [-48, 0, 0]}},
        "leg_back2_l": {"rotation": {0: [-30, 0, 0], 3.0: [-30, 0, 0]}},
        "leg_back2_r": {"rotation": {0: [-30, 0, 0], 3.0: [-30, 0, 0]}},
        "foot_back_l": {"rotation": {0: [96, 0, 0], 3.0: [96, 0, 0]}},
        "foot_back_r": {"rotation": {0: [96, 0, 0], 3.0: [96, 0, 0]}},
        "leg_front_l": {"rotation": {0: [18, 0, 0], 3.0: [18, 0, 0]}},
        "leg_front_r": {"rotation": {0: [18, 0, 0], 3.0: [18, 0, 0]}},
        "neck1": {"rotation": {0: [8, 0, 0], 1.5: [6, 4, 0], 3.0: [8, 0, 0]}},
        "head": {"rotation": {0: [10, 0, 0], 1.5: [8, -6, 0], 3.0: [10, 0, 0]}},
        "tail1": {"rotation": {0: [18, 0, 0], 3.0: [18, 0, 0]}},
        "tail2": {"rotation": {0: [8, 10, 0], 3.0: [8, 10, 0]}},
        "tail3": {"rotation": {0: [0, 16, 0], 1.5: [0, 20, 0], 3.0: [0, 16, 0]}},
        "tail4": {"rotation": {0: [0, 18, 0], 1.5: [0, 24, 0], 3.0: [0, 18, 0]}},
    }
    a[A + "sit"] = anim(3.0, True, folded(sit, t=(0, 3.0)))

    # ---------------- en el aire
    DOWN = ([0, 0, 40], [0, 0, -16], [0, 0, -14])    # ala abajo (Z positivo baja el ala izquierda)
    UP = ([0, 0, -44], [0, 0, 22], [0, 0, 18])       # ala arriba
    MID = ([0, 0, -4], [0, 0, 4], [0, 0, 2])
    fly_body = {
        "body": {"position": {0: [0, 1.5, 0], 0.3: [0, -1.5, 0], 0.6: [0, 0, 0], 0.9: [0, 1.5, 0], 1.2: [0, 1.5, 0]},
                 "rotation": {0: [0, 0, 0], 1.2: [0, 0, 0]}},
        "neck1": {"rotation": {0: [20, 0, 0], 0.6: [22, 0, 0], 1.2: [20, 0, 0]}},
        "neck2": {"rotation": {0: [10, 0, 0], 0.6: [12, 0, 0], 1.2: [10, 0, 0]}},
        "neck3": {"rotation": {0: [4, 0, 0], 1.2: [4, 0, 0]}},
        "head": {"rotation": {0: [-26, 0, 0], 0.6: [-28, 0, 0], 1.2: [-26, 0, 0]}},
        "tail1": {"rotation": {0: [14, 0, 0], 0.6: [10, 0, 0], 1.2: [14, 0, 0]}},
        "tail2": {"rotation": {0: [6, 3, 0], 0.6: [2, -3, 0], 1.2: [6, 3, 0]}},
        "tail3": {"rotation": {0: [-4, 5, 0], 0.6: [-6, -5, 0], 1.2: [-4, 5, 0]}},
        "tail4": {"rotation": {0: [-7, 7, 0], 0.6: [-9, -7, 0], 1.2: [-7, 7, 0]}},
        "tail5": {"rotation": {0: [-6, 8, 0], 0.6: [-8, -8, 0], 1.2: [-6, 8, 0]}},
        "leg_front_l": {"rotation": {0: [42, 0, 0], 1.2: [42, 0, 0]}},
        "leg_front_r": {"rotation": {0: [42, 0, 0], 1.2: [42, 0, 0]}},
        "leg_front2_l": {"rotation": {0: [40, 0, 0], 1.2: [40, 0, 0]}},
        "leg_front2_r": {"rotation": {0: [40, 0, 0], 1.2: [40, 0, 0]}},
        "leg_back_l": {"rotation": {0: [60, 0, 0], 1.2: [60, 0, 0]}},
        "leg_back_r": {"rotation": {0: [60, 0, 0], 1.2: [60, 0, 0]}},
        "leg_back2_l": {"rotation": {0: [10, 0, 0], 1.2: [10, 0, 0]}},
        "leg_back2_r": {"rotation": {0: [10, 0, 0], 1.2: [10, 0, 0]}},
        "foot_back_l": {"rotation": {0: [40, 0, 0], 1.2: [40, 0, 0]}},
        "foot_back_r": {"rotation": {0: [40, 0, 0], 1.2: [40, 0, 0]}},
        "foot_front_l": {"rotation": {0: [30, 0, 0], 1.2: [30, 0, 0]}},
        "foot_front_r": {"rotation": {0: [30, 0, 0], 1.2: [30, 0, 0]}},
    }
    fly_wings = wing_cycle([(0, "u"), (0.3, MID), (0.55, "d"), (0.9, MID), (1.2, "u")], DOWN, UP)
    a[A + "fly"] = anim(1.2, True, merge(fly_body, fly_wings))
    # planeo: alas extendidas, leve balanceo
    glide_wings = wing_cycle([(0, ([0, 0, -6], [0, 0, 2], [0, 0, 4])), (1.5, ([0, 0, -10], [0, 0, 4], [0, 0, 7])),
                              (3.0, ([0, 0, -6], [0, 0, 2], [0, 0, 4]))], DOWN, UP)
    glide_body = dict(fly_body)
    glide_body["body"] = {"rotation": {0: [0, 0, -4], 1.5: [0, 0, 4], 3.0: [0, 0, -4]},
                          "position": {0: [0, 0, 0], 1.5: [0, -1, 0], 3.0: [0, 0, 0]}}
    glide_body = {k: ({"rotation": {0: list(v["rotation"].values())[0], 3.0: list(v["rotation"].values())[0]}}
                      if k != "body" else v) for k, v in glide_body.items()}
    a[A + "glide"] = anim(3.0, True, merge(glide_body, glide_wings))
    # suspendido en el aire (cuando escupe fuego en vuelo o despega): cuerpo erguido, aleteo rápido
    hover_body = {
        "body": {"rotation": {0: [-30, 0, 0], 0.8: [-30, 0, 0]},
                 "position": {0: [0, 1, 0], 0.2: [0, -1, 0], 0.4: [0, 1, 0], 0.6: [0, -1, 0], 0.8: [0, 1, 0]}},
        "neck1": {"rotation": {0: [24, 0, 0], 0.8: [24, 0, 0]}},
        "neck2": {"rotation": {0: [10, 0, 0], 0.8: [10, 0, 0]}},
        "head": {"rotation": {0: [-6, 0, 0], 0.8: [-6, 0, 0]}},
        "leg_front_l": {"rotation": {0: [20, 0, -8], 0.4: [28, 0, -8], 0.8: [20, 0, -8]}},
        "leg_front_r": {"rotation": {0: [20, 0, 8], 0.4: [28, 0, 8], 0.8: [20, 0, 8]}},
        "leg_front2_l": {"rotation": {0: [-50, 0, 0], 0.8: [-50, 0, 0]}},
        "leg_front2_r": {"rotation": {0: [-50, 0, 0], 0.8: [-50, 0, 0]}},
        "leg_back_l": {"rotation": {0: [30, 0, 0], 0.4: [24, 0, 0], 0.8: [30, 0, 0]}},
        "leg_back_r": {"rotation": {0: [30, 0, 0], 0.4: [24, 0, 0], 0.8: [30, 0, 0]}},
        "tail1": {"rotation": {0: [30, 0, 0], 0.8: [30, 0, 0]}},
        "tail2": {"rotation": {0: [10, 6, 0], 0.4: [10, -6, 0], 0.8: [10, 6, 0]}},
        "tail3": {"rotation": {0: [0, 8, 0], 0.4: [0, -8, 0], 0.8: [0, 8, 0]}},
        "tail4": {"rotation": {0: [-6, 10, 0], 0.4: [-6, -10, 0], 0.8: [-6, 10, 0]}},
    }
    hover_wings = wing_cycle([(0, ([24, 0, -40], [0, 0, 20], [0, 0, 16])), (0.4, ([-24, 0, 34], [0, 0, -16], [0, 0, -12])),
                              (0.8, ([24, 0, -40], [0, 0, 20], [0, 0, 16]))], DOWN, UP)
    a[A + "hover"] = anim(0.8, True, merge(hover_body, hover_wings))
    # despegue: se agacha y salta con un gran aletazo
    a[A + "takeoff"] = anim(1.0, False, merge({
        "body": {"position": {0: [0, 0, 0], 0.25: [0, -5, 0], 0.5: [0, 6, 0], 1.0: [0, 2, 0]},
                 "rotation": {0: [0, 0, 0], 0.25: [8, 0, 0], 0.5: [-24, 0, 0], 1.0: [-6, 0, 0]}},
        "leg_back_l": {"rotation": {0: [0, 0, 0], 0.25: [-30, 0, 0], 0.5: [50, 0, 0], 1.0: [55, 0, 0]}},
        "leg_back_r": {"rotation": {0: [0, 0, 0], 0.25: [-30, 0, 0], 0.5: [50, 0, 0], 1.0: [55, 0, 0]}},
        "leg_front_l": {"rotation": {0: [0, 0, 0], 0.25: [20, 0, 0], 0.5: [-30, 0, 0], 1.0: [45, 0, 0]}},
        "leg_front_r": {"rotation": {0: [0, 0, 0], 0.25: [20, 0, 0], 0.5: [-30, 0, 0], 1.0: [45, 0, 0]}},
        "neck1": {"rotation": {0: [0, 0, 0], 0.25: [12, 0, 0], 0.5: [-6, 0, 0], 1.0: [18, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.5: [-10, 0, 0], 1.0: [-24, 0, 0]}},
    }, wing_cycle([(0, FOLD), (0.25, ([0, 0, -50], [0, 0, 30], [0, 0, 20])),
                   (0.55, ([0, 0, 40], [0, 0, -20], [0, 0, -14])), (1.0, ([0, 0, -30], [0, 0, 14], [0, 0, 10]))], DOWN, UP)))

    # ---------------- acciones (se mezclan encima del movimiento)
    a[A + "breath"] = anim(1.6, False, {
        "neck1": {"rotation": {0: [0, 0, 0], 0.25: [-14, 0, 0], 0.45: [16, 0, 0], 1.3: [16, 0, 0], 1.6: [0, 0, 0]}},
        "neck2": {"rotation": {0: [0, 0, 0], 0.25: [-8, 0, 0], 0.45: [8, 0, 0], 1.3: [8, 0, 0], 1.6: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.25: [-12, 0, 0], 0.45: [-8, 0, 0], 0.9: [-10, 3, 0], 1.3: [-8, -3, 0], 1.6: [0, 0, 0]}},
        "jaw": {"rotation": {0: [0, 0, 0], 0.25: [10, 0, 0], 0.45: [38, 0, 0], 1.3: [38, 0, 0], 1.6: [0, 0, 0]}},
    })
    a[A + "bite"] = anim(0.6, False, {
        "neck1": {"rotation": {0: [0, 0, 0], 0.15: [-10, 0, 0], 0.3: [22, 0, 0], 0.6: [0, 0, 0]}},
        "neck2": {"rotation": {0: [0, 0, 0], 0.3: [10, 0, 0], 0.6: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.15: [-14, 0, 0], 0.3: [6, 0, 0], 0.6: [0, 0, 0]}},
        "jaw": {"rotation": {0: [0, 0, 0], 0.15: [36, 0, 0], 0.3: [0, 0, 0], 0.6: [0, 0, 0]}},
    })
    a[A + "roar"] = anim(2.0, False, merge({
        "neck1": {"rotation": {0: [0, 0, 0], 0.4: [-24, 0, 0], 1.5: [-24, 0, 0], 2.0: [0, 0, 0]}},
        "neck2": {"rotation": {0: [0, 0, 0], 0.4: [-12, 0, 0], 1.5: [-12, 0, 0], 2.0: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.4: [-20, 0, 0], 0.8: [-24, 6, 0], 1.2: [-24, -6, 0], 1.5: [-20, 0, 0], 2.0: [0, 0, 0]}},
        "jaw": {"rotation": {0: [0, 0, 0], 0.4: [40, 0, 0], 1.5: [40, 0, 0], 2.0: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.4: [-10, 0, 0], 1.5: [-10, 0, 0], 2.0: [0, 0, 0]}},
    }, wing_cycle([(0, FOLD), (0.5, ([-10, 24, -30], [0, -10, 10], [0, 0, 10])),
                   (1.5, ([-10, 24, -34], [0, -10, 12], [0, 0, 12])), (2.0, FOLD)], DOWN, UP)))
    return a


# ================================================================== HUEVO
EGG_PAL = {"S": (48, 28, 32), "s": (28, 14, 18), "l": (74, 40, 44), "Q": (255, 58, 44), "q": (196, 22, 26), "W": (255, 176, 150)}


def build_egg():
    g = Geo("geometry.nether_dragon_egg", 64, 64)
    pk = Packer([(0, 0, 64, 64)])
    paint = []
    rings = [([-3, 0, -3], [6, 1, 6]), ([-4, 1, -4], [8, 3, 8]), ([-4.5, 4, -4.5], [9, 4, 9]), ([-4, 8, -4], [8, 3, 8]),
             ([-3, 11, -3], [6, 2, 6]), ([-2, 13, -2], [4, 1, 4])]
    g.bone("egg", [0, 0, 0])
    g.bone("shell", [0, 0, 0], "egg")
    for k, (o, s) in enumerate(rings):
        uv = pk.alloc(*[math.ceil(v) for v in s])
        g.cube("shell", "c", o, s, uv)
        paint.append((uv, s, k))
    sheet = Sheet(64, 64)
    er = random.Random(11)

    def egg_face(level, face):
        # grietas de alma: solo en el frente y en un costado, en zigzag hacia arriba
        crack_col = {"front": 3, "left": 4, "back": -99, "right": -99}.get(face, -99)

        def f(i, j, fw, fh):
            y = level + j
            cc = crack_col + ((y // 2) % 2) - (1 if y > 8 else 0)
            if face in ("front", "left") and 2 <= y <= 12 and i == cc:
                return (EGG_PAL["Q"] if y % 3 else EGG_PAL["W"]) + (255,)
            if face == "front" and y in (6, 7) and i == cc + 1:
                return EGG_PAL["q"] + (255,)
            # escamas de obsidiana
            row = y // 2
            k = (i + (row % 2) * 2) % 4
            if y % 2 == 1 and k in (0, 3):
                c = EGG_PAL["s"]
            elif y % 2 == 0 and k in (1, 2):
                c = EGG_PAL["l"]
            else:
                c = EGG_PAL["S"]
            return tuple(max(0, min(255, v + er.randint(-3, 3))) for v in c) + (255,)
        return f
    for (u, v), s, k in paint:
        lv = int(rings[k][0][1])
        sheet.box(u, v, s[0], s[1], s[2], {"front": egg_face(lv, "front"), "left": egg_face(lv, "left"),
                                           "right": egg_face(lv, "right"), "back": egg_face(lv, "back"),
                                           "top": egg_face(lv + s[1], "top"), "bottom": egg_face(lv, "bottom")})
    return g, sheet.img


def egg_animations():
    E = "animation.nether_dragon_egg."
    return {
        E + "idle": anim(3.0, True, {"shell": {"scale": {0: [1, 1, 1], 1.5: [1.02, 1.03, 1.02], 3.0: [1, 1, 1]}}}),
        E + "wobble": anim(1.2, True, {"egg": {"rotation": {0: [0, 0, 0], 0.15: [0, 0, 10], 0.3: [0, 0, -9], 0.45: [0, 0, 6],
                                                               0.6: [0, 0, -3], 0.75: [0, 0, 0], 1.2: [0, 0, 0]}}}),
        E + "hatch": anim(1.0, False, {"egg": {"rotation": {0: [0, 0, 0], 0.1: [8, 0, 10], 0.2: [-8, 0, -10], 0.3: [6, 0, 8],
                                                              0.4: [0, 0, 0], 1.0: [0, 0, 0]},
                                                 "scale": {0: [1, 1, 1], 0.4: [1.1, 0.9, 1.1], 0.6: [1.15, 1.2, 1.15], 1.0: [0.2, 0.2, 0.2]}}}),
    }


def egg_icon():
    """Ícono 16x16 del huevo."""
    rows_ = ["......ssss......", ".....sSlSSs.....", "....sSSSSlSs....", "....SlSSSSSS....", "...sSSSlSQSSs...",
             "...SSSSSQSlSS...", "..sSlSSSWSSSSs..", "..SSSSSQSSSlSS..", "..SSlSSQSSSSSS..", "..sSSSSSQSlSSs..",
             "..SSSlSSWSSSSS..", "...SSSSQSSSlS...", "...sSlSSQSSSs...", "....sSSSSSSs....", ".....ssSSss.....", "................"]
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, r in enumerate(rows_):
        for x, ch in enumerate(r):
            if ch in EGG_PAL:
                im.putpixel((x, y), EGG_PAL[ch] + (255,))
    return im


# ================================================================== brillo
def is_glow_pixel(c):
    r, g_, b, a = c
    if a == 0:
        return False
    return any(abs(r - q[0]) + abs(g_ - q[1]) + abs(b - q[2]) <= 10 for q in GLOW)


def glowmask(img):
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for y in range(img.height):
        for x in range(img.width):
            c = img.getpixel((x, y))
            if is_glow_pixel(c):
                out.putpixel((x, y), c)
    return out


def write_all():
    g, tex = build()
    save_json(os.path.join(ASSETS, "geo", "entity", "nether_dragon.geo.json"), g.to_json())
    save_json(os.path.join(ASSETS, "animations", "entity", "nether_dragon.animation.json"),
              {"format_version": "1.8.0", "animations": animations()})
    tex.save(os.path.join(ASSETS, "textures", "entity", "nether_dragon.png"))
    glowmask(tex).save(os.path.join(ASSETS, "textures", "entity", "nether_dragon_glowmask.png"))
    eg, etex = build_egg()
    save_json(os.path.join(ASSETS, "geo", "entity", "nether_dragon_egg.geo.json"), eg.to_json())
    save_json(os.path.join(ASSETS, "animations", "entity", "nether_dragon_egg.animation.json"),
              {"format_version": "1.8.0", "animations": egg_animations()})
    etex.save(os.path.join(ASSETS, "textures", "entity", "nether_dragon_egg.png"))
    glowmask(etex).save(os.path.join(ASSETS, "textures", "entity", "nether_dragon_egg_glowmask.png"))
    egg_icon().save(os.path.join(ASSETS, "textures", "item", "nether_dragon_egg.png"))
    return g, tex


# ================================================================== FASES DE CRECIMIENTO
SPIKES = ["sp_back", "sp_neck1", "sp_neck2", "sp_neck3", "sp_tail1", "sp_tail2", "sp_tail3", "sp_tail4", "sp_tail5"]
EXTRAS = ["horn2_l", "horn2_r", "horn3_l", "horn3_r", "hornb_l", "hornb_r", "head_spikes", "jaw_spikes",
          "frill_l", "frill_r", "pl_plates", "tail_blade", "saddle_spikes"] + SPIKES
# Cada fase: crecimiento mínimo (0..1), escala del cuerpo y de cada parte, y qué piezas aparecen.
# Las crías tienen cabeza grande, cuello/cola/patas cortos y alitas; la textura joven no tiene grietas.
def _st(name, grow, scale, head, wings, horns, spikes, tail, neck, legs, visible, young):
    return dict(name=name, grow=grow, scale=scale, head=head, wings=wings, horns=horns, spikes=spikes,
                tail=tail, neck=neck, legs=legs, visible=visible, young=young)


STAGES = [
    _st("Recién nacido", 0.00, 0.22, 1.65, 0.42, 0.40, 0.0, 0.55, 0.70, 0.72, [], True),
    _st("Cría", 0.15, 0.36, 1.42, 0.62, 0.70, 0.55, 0.70, 0.80, 0.80, ["horn2_l", "horn2_r"] + SPIKES, True),
    _st("Joven", 0.40, 0.55, 1.20, 0.82, 0.90, 0.80, 0.85, 0.90, 0.90,
        ["horn2_l", "horn2_r", "horn3_l", "horn3_r", "hornb_l", "hornb_r", "head_spikes", "saddle_spikes"] + SPIKES, False),
    _st("Subadulto", 0.70, 0.80, 1.07, 0.94, 1.0, 1.0, 0.95, 1.0, 0.97, [b for b in EXTRAS if b != "tail_blade"], False),
    _st("Adulto", 1.00, 1.00, 1.00, 1.00, 1.0, 1.0, 1.0, 1.0, 1.0, list(EXTRAS), False),
]
LEG_BONES = ["leg_front_l", "leg_front_r", "leg_back_l", "leg_back_r"]


def stage_for(growth):
    st = STAGES[0]
    for s in STAGES:
        if growth >= s["grow"]:
            st = s
    return st


def stage_pose(st, pose=None):
    """Pose + partes ocultas para mostrar una fase (lo mismo que hará el renderizador del juego)."""
    p = {k: {c: list(v2) for c, v2 in v.items()} for k, v in (pose or {}).items()}
    sets = [("head", st["head"]), ("wing_l", st["wings"]), ("wing_r", st["wings"]), ("horn_l", st["horns"]),
            ("horn_r", st["horns"]), ("tail1", st["tail"]), ("neck1", st["neck"])] + [(b, st["legs"]) for b in LEG_BONES]
    for b, v in sets:
        p.setdefault(b, {})["scale"] = [v, v, v]
    for b in SPIKES:
        sp = st["spikes"] or 1
        p.setdefault(b, {})["scale"] = [sp, sp, sp]
    drop = 28.5 * (1 - st["legs"])
    body = p.setdefault("body", {})
    pos = body.get("position", [0, 0, 0])
    body["position"] = [pos[0], pos[1] - drop, pos[2]]
    hidden = [b for b in EXTRAS if b not in st["visible"]]
    if "tail_blade" not in hidden:
        hidden.append("tail_blade")              # este diseño usa la aleta en abanico en todas las fases
    return p, hidden, st["scale"]
