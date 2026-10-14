"""Guerrero Real (espada larga a dos manos) y Ballestero: mismo cuerpo del guerrero del usuario,
skins derivadas con su estética y piezas 3D propias."""
import copy
import math
import os
import random
from PIL import Image
from common import ASSETS, save_json, Packer
from models import Geo, anim
from textures import Sheet
import warrior

TEX_H = 128
rnd = random.Random(21)


def base_skin():
    _, wtex = warrior.load_bbmodel()
    img = Image.new("RGBA", (64, TEX_H), (0, 0, 0, 0))
    img.paste(wtex, (0, 0))
    for y in range(64, 68):
        img.paste(wtex.crop((0, 63, 64, 64)), (0, y))
    return img


def is_gold(c):
    r, g, b, a = c
    return a > 0 and r > 170 and g > 100 and b < 110 and r - b > 90


def is_skin(c):
    r, g, b, a = c
    return a > 0 and r > 150 and 100 < g < 200 and 80 < b < 170 and r - b > 40


def is_red(c):
    r, g, b, a = c
    return a > 0 and r > 150 and g < 90 and b < 90


def lum(c):
    return (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2])


def recolor(img, box, fn):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            c = img.getpixel((x, y))
            if c[3]:
                n = fn(c, x, y)
                if n:
                    img.putpixel((x, y), tuple(int(max(0, min(255, v))) for v in n[:3]) + (c[3],))


def paint(img, x, y, rows, pal):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == " ":
                continue
            c = pal[ch]
            img.putpixel((x + i, y + j), (0, 0, 0, 0) if c is None else tuple(c) + (255,))


# zonas de la skin del guerrero (formato 64x64 con su modelo propio)
HEAD = (0, 0, 32, 16)
HAT = (32, 0, 64, 16)
BODY = (16, 16, 40, 32)
JACKET = (16, 32, 40, 48)
R_ARM = (40, 16, 56, 32)
R_SLEEVE = (40, 32, 56, 48)
L_ARM = (32, 48, 48, 64)
L_SLEEVE = (48, 48, 64, 64)
R_LEG = (0, 16, 16, 32)
R_PANTS = (0, 32, 16, 48)
L_LEG = (16, 48, 32, 64)
L_PANTS = (0, 48, 16, 64)


# ====================================================================== GUERRERO REAL
RP = {
    ".": None,
    "A": (58, 58, 72), "a": (36, 36, 46), "s": (96, 96, 112), "S": (150, 150, 166),     # acero ennegrecido
    "G": (232, 190, 56), "g": (170, 122, 26), "Y": (255, 236, 130),                        # oro
    "R": (226, 26, 36), "r": (130, 10, 18), "E": (255, 70, 60),                            # rubí / ojos
    "C": (150, 20, 30), "c": (100, 12, 20), "k": (60, 8, 12),                               # tela carmesí
    "K": (16, 14, 20),
}


def steel(c, x, y):
    if is_gold(c) or is_red(c) or is_skin(c):
        return None
    l = lum(c)
    return (l * 0.62 + 14, l * 0.62 + 14, l * 0.72 + 22)


def royal_texture():
    img = base_skin()
    # armadura de placas de acero ennegrecido en todo el cuerpo (el oro y los rubíes del guerrero se conservan)
    for box in (BODY, JACKET, R_ARM, R_SLEEVE, L_ARM, L_SLEEVE, R_LEG, R_PANTS, L_LEG, L_PANTS):
        recolor(img, box, steel)
    # guanteletes: la piel de los brazos pasa a acero con nudillos de oro
    gaunt = lambda c, x, y: ((RP["G"] if y % 4 == 0 else (RP["s"] if (x + y) % 3 == 0 else RP["A"])) if is_skin(c) else None)
    for box in (R_ARM, L_ARM, R_SLEEVE, L_SLEEVE):
        recolor(img, box, gaunt)
    # yelmo cerrado con visera en T y ojos de rubí (capa exterior de la cabeza)
    side = ["aAAAAAAa", "AsAAAAsA", "AAAAAAAA", "AAsAAAAA", "AAAAAsAA", "AAAAAAAA", "GgGGgGGg", "aaaaaaaa"]
    paint(img, 40, 0, ["AAAAAAAA", "AAAGGAAA", "AAAGGAAA", "AAAGGAAA", "AAAGGAAA", "AAAGGAAA", "AAAGGAAA", "AAAAAAAA"], RP)
    paint(img, 48, 0, ["........"] * 8, RP)
    paint(img, 40, 8, ["aAAGGAAa",
                       "AsAGRAsA",
                       "AKKKKKKA",
                       "AKEKKEKA",
                       "AsAKKAsA",
                       "AAsKKsAA",
                       "GgGKKGgG",
                       "aaaaaaaa"], RP)
    paint(img, 32, 8, side, RP)
    paint(img, 48, 8, side, RP)
    paint(img, 56, 8, ["aAAAAAAa", "AAsAAsAA", "AAAAAAAA", "AsAAAAsA", "AAAGGAAA", "AAAAAAAA", "GgGGgGGg", "aaaaaaaa"], RP)
    # tabardo carmesí con el emblema dorado del reino (frente de la chaqueta)
    paint(img, 20, 36, ["GGGGGGGG",
                        "CcCCCCcC",
                        "CCCYGCCC",
                        "CCGRRGCC",
                        "CCCGGCCC",
                        "CcCCCCcC",
                        "CCCcCCCC",
                        "CCCCCcCC",
                        "GgGGgGGg",
                        "aAGRRGAa",
                        "CCCCCCCC",
                        "CcCCCCcC"], RP)
    paint(img, 28, 36, ["GGGGGGGG", "CCCCcCCC", "CcCCCCCC", "CCCCCcCC", "CCcCCCCC", "CCCCCCcC",
                        "CCCcCCCC", "cCCCCCCC", "GgGGgGGg", "aAAAAAAa", "CCCCCCCC", "CCcCCCCC"], RP)
    # piezas 3D (zona nueva, y >= 68)
    pk = Packer([(0, 68, 64, 128)])
    parts = []

    def part(size, faces):
        uv = pk.alloc(*[max(1, math.floor(v)) for v in size])
        parts.append((uv, size, faces))
        return uv

    F = lambda ch: (lambda i, j, fw, fh: tuple(RP[ch]) + (255,))
    plate = lambda i, j, fw, fh: tuple(RP["G" if j == 0 or j == fh - 1 else ("A" if (i + j) % 3 else "s")]) + (255,)
    gold_band = lambda i, j, fw, fh: tuple(RP["R" if (i == fw // 2 and j == 0) else ("G" if (i + j) % 3 else "g")]) + (255,)
    cape = lambda i, j, fw, fh: tuple(RP["G" if (i in (0, fw - 1) or j == fh - 1) else
                                         ("Y" if (j in (4, 5) and abs(i - fw // 2) <= 1) else
                                          ("R" if (j == 6 and abs(i - fw // 2) <= 0) else ("C" if (i + j) % 4 else "c")))]) + (255,)
    tabard = lambda i, j, fw, fh: tuple(RP["G" if (i in (0, fw - 1) or j == fh - 1) else ("C" if (i + j) % 3 else "c")]) + (255,)
    plume = lambda i, j, fw, fh: tuple(RP["C" if (i + j) % 3 else ("c" if j % 2 else "R")]) + (255,)
    uv = {}
    uv["paul"] = part([5.6, 4, 6.6], {"all": plate, "top": lambda i, j, fw, fh: tuple(RP["G" if (i in (0, fw - 1) or j in (0, fh - 1)) else ("R" if (i == fw // 2 and j == fh // 2) else "A")]) + (255,)})
    uv["paul2"] = part([4.6, 1.4, 5.6], {"all": gold_band})
    uv["circlet"] = part([9.2, 1.4, 9.2], {"all": gold_band, "top": lambda *a: (0, 0, 0, 0), "bottom": lambda *a: (0, 0, 0, 0)})
    uv["crest"] = part([1.2, 1.2, 9.2], {"all": F("G")})
    uv["plume"] = part([1.4, 3, 8], {"all": plume})
    uv["cape"] = part([9, 20, 0.6], {"all": cape})
    uv["tabard"] = part([5, 7, 0.4], {"all": tabard})
    sheet = Sheet(64, TEX_H)
    sheet.img = img
    for (u, v), size, faces in parts:
        fl = [math.floor(x) for x in size]
        sheet.box(u, v, fl[0], fl[1], fl[2], faces)
    return sheet.img, uv


def royal_geo(uv):
    g, _ = warrior.build_geo()
    a = Geo("geometry.nether_royal_warrior", 64, TEX_H)
    a.bones = copy.deepcopy(g.bones)
    a.order = list(g.order)
    a.cubes = list(g.cubes)
    a.bone("right_pauldron", [-6, 24, 0], "right_arm")
    a.cube("right_pauldron", "p", [-9.6, 22.2, -3.3], [5.6, 4, 6.6], uv["paul"])
    a.cube("right_pauldron", "p", [-9.1, 26.0, -2.8], [4.6, 1.4, 5.6], uv["paul2"])
    a.bone("left_pauldron", [6, 24, 0], "left_arm")
    a.cube("left_pauldron", "p", [4.0, 22.2, -3.3], [5.6, 4, 6.6], uv["paul"])
    a.cube("left_pauldron", "p", [4.5, 26.0, -2.8], [4.6, 1.4, 5.6], uv["paul2"])
    a.bone("crest", [0, 34.5, 0], "head")
    a.cube("crest", "c", [-4.6, 33.4, -4.6], [9.2, 1.4, 9.2], uv["circlet"])
    a.cube("crest", "c", [-0.6, 34.4, -4.6], [1.2, 1.2, 9.2], uv["crest"])
    a.bone("plume", [0, 35.2, 2.5], "crest", [-28, 0, 0])
    a.cube("plume", "c", [-0.7, 34.6, 2.0], [1.4, 3, 8], uv["plume"])
    a.bone("cape", [0, 26.2, 2.6], "body", [6, 0, 0])
    a.cube("cape", "c", [-4.5, 6.2, 2.4], [9, 20, 0.6], uv["cape"])
    a.bone("tabard", [0, 13, -2.6], "body")
    a.cube("tabard", "c", [-2.5, 6, -2.9], [5, 7, 0.4], uv["tabard"])
    return a


RA = "animation.nether_royal_warrior."
# Agarre a dos manos: brazos al frente, la mano izquierda junto a la derecha en la empuñadura
GRIP_R = [-48, 22, 0]
GRIP_L = [-54, -30, 0]


def arms_inward(a):
    """Las animaciones se escribieron con el giro Y de los brazos invertido: se corrige aquí
    (Y negativo en el brazo derecho = la mano va hacia el centro del cuerpo)."""
    for an in a.values():
        for b in ("right_arm", "left_arm"):
            rot = an["bones"].get(b, {}).get("rotation")
            if rot:
                for k, v in rot.items():
                    rot[k] = [v[0], -v[1], v[2]]
    return a


def royal_animations():
    a = {}
    a[RA + "idle"] = anim(2.8, True, {
        "body": {"position": {0: [0, 0, 0], 1.4: [0, 0.3, 0], 2.8: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 1.4: [2, 3, 0], 2.8: [0, 0, 0]}},
        "right_arm": {"rotation": {0: GRIP_R, 1.4: [GRIP_R[0] - 3, GRIP_R[1], 0], 2.8: GRIP_R}},
        "left_arm": {"rotation": {0: GRIP_L, 1.4: [GRIP_L[0] - 3, GRIP_L[1], 0], 2.8: GRIP_L}},
        "cape": {"rotation": {0: [6, 0, 0], 1.4: [8, 0, 1], 2.8: [6, 0, 0]}},
    })
    a[RA + "walk"] = anim(1.1, True, {
        "right_leg": {"rotation": {0: [-28, 0, 0], 0.55: [28, 0, 0], 1.1: [-28, 0, 0]}},
        "left_leg": {"rotation": {0: [28, 0, 0], 0.55: [-28, 0, 0], 1.1: [28, 0, 0]}},
        "right_arm": {"rotation": {0: GRIP_R, 0.55: [GRIP_R[0] + 6, GRIP_R[1], 0], 1.1: GRIP_R}},
        "left_arm": {"rotation": {0: GRIP_L, 0.55: [GRIP_L[0] + 6, GRIP_L[1], 0], 1.1: GRIP_L}},
        "body": {"position": {0: [0, 0, 0], 0.275: [0, 0.6, 0], 0.55: [0, 0, 0], 0.825: [0, 0.6, 0], 1.1: [0, 0, 0]},
                 "rotation": {0: [0, 4, 0], 0.55: [0, -4, 0], 1.1: [0, 4, 0]}},
        "cape": {"rotation": {0: [10, 0, 0], 0.275: [16, 0, 2], 0.55: [10, 0, 0], 0.825: [16, 0, -2], 1.1: [10, 0, 0]}},
        "tabard": {"rotation": {0: [-10, 0, 0], 0.55: [10, 0, 0], 1.1: [-10, 0, 0]}},
    })
    # correr: la espada se lleva baja y hacia atrás, a dos manos
    a[RA + "run"] = anim(0.64, True, {
        "right_leg": {"rotation": {0: [-48, 0, 0], 0.32: [44, 0, 0], 0.64: [-48, 0, 0]}},
        "left_leg": {"rotation": {0: [44, 0, 0], 0.32: [-48, 0, 0], 0.64: [44, 0, 0]}},
        "right_arm": {"rotation": {0: [-20, 30, 10], 0.32: [-26, 30, 10], 0.64: [-20, 30, 10]}},
        "left_arm": {"rotation": {0: [-36, -40, 0], 0.32: [-42, -40, 0], 0.64: [-36, -40, 0]}},
        "body": {"rotation": {0: [14, 10, 0], 0.64: [14, 10, 0]},
                 "position": {0: [0, 0, 0], 0.16: [0, 1.2, 0], 0.32: [0, 0, 0], 0.48: [0, 1.2, 0], 0.64: [0, 0, 0]}},
        "head": {"rotation": {0: [-12, -10, 0], 0.64: [-12, -10, 0]}},
        "cape": {"rotation": {0: [36, 0, 0], 0.16: [44, 0, 3], 0.32: [36, 0, 0], 0.48: [44, 0, -3], 0.64: [36, 0, 0]}},
        "tabard": {"rotation": {0: [-24, 0, 0], 0.32: [-14, 0, 0], 0.64: [-24, 0, 0]}},
    })
    # ataque 1: tajo descendente con las dos manos (golpe de ejecución)
    a[RA + "attack_overhead"] = anim(1.1, False, {
        "right_arm": {"rotation": {0: GRIP_R, 0.4: [-172, 14, 0], 0.55: [-172, 14, 0], 0.68: [-36, 18, 0], 0.85: [-30, 18, 0], 1.1: GRIP_R}},
        "left_arm": {"rotation": {0: GRIP_L, 0.4: [-176, -18, 0], 0.55: [-176, -18, 0], 0.68: [-42, -26, 0], 0.85: [-36, -26, 0], 1.1: GRIP_L}},
        "body": {"rotation": {0: [0, 0, 0], 0.4: [-14, 0, 0], 0.55: [-16, 0, 0], 0.68: [22, 0, 0], 0.85: [18, 0, 0], 1.1: [0, 0, 0]},
                 "position": {0: [0, 0, 0], 0.4: [0, 1, 0], 0.68: [0, -1.5, -1], 1.1: [0, 0, 0]}},
        "right_leg": {"rotation": {0: [0, 0, 0], 0.4: [8, 0, 0], 0.68: [-26, 0, 0], 0.85: [-26, 0, 0], 1.1: [0, 0, 0]}},
        "left_leg": {"rotation": {0: [0, 0, 0], 0.68: [22, 0, 0], 0.85: [22, 0, 0], 1.1: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.4: [-10, 0, 0], 0.68: [12, 0, 0], 1.1: [0, 0, 0]}},
        "cape": {"rotation": {0: [6, 0, 0], 0.4: [4, 0, 0], 0.68: [30, 0, 0], 1.1: [6, 0, 0]}},
    })
    # ataque 2: torbellino (giro completo con la hoja extendida, golpea a todos alrededor)
    a[RA + "attack_spin"] = anim(1.2, False, {
        "body": {"rotation": {0: [0, 0, 0], 0.25: [0, 50, 0], 0.5: [0, -60, 0], 0.75: [0, -240, 0], 0.95: [0, -360, 0], 1.2: [0, -360, 0]},
                 "position": {0: [0, 0, 0], 0.25: [0, -1, 0], 0.75: [0, -1.5, 0], 1.2: [0, 0, 0]}},
        "right_arm": {"rotation": {0: GRIP_R, 0.25: [-80, 50, 0], 0.5: [-88, 26, 0], 0.95: [-88, 26, 0], 1.2: GRIP_R}},
        "left_arm": {"rotation": {0: GRIP_L, 0.25: [-70, -10, 0], 0.5: [-84, -36, 0], 0.95: [-84, -36, 0], 1.2: GRIP_L}},
        "right_leg": {"rotation": {0: [0, 0, 0], 0.25: [-20, 0, 0], 0.75: [-20, 0, 0], 1.2: [0, 0, 0]}},
        "left_leg": {"rotation": {0: [0, 0, 0], 0.25: [18, 0, 0], 0.75: [18, 0, 0], 1.2: [0, 0, 0]}},
        "cape": {"rotation": {0: [6, 0, 0], 0.5: [50, 0, 20], 0.95: [50, 0, 20], 1.2: [6, 0, 0]}},
        "tabard": {"rotation": {0: [0, 0, 0], 0.5: [-30, 0, 0], 0.95: [-30, 0, 0], 1.2: [0, 0, 0]}},
    })
    # ataque 3: estocada a fondo
    a[RA + "attack_thrust"] = anim(0.9, False, {
        "right_arm": {"rotation": {0: GRIP_R, 0.3: [-40, 30, 0], 0.45: [-92, 12, 0], 0.65: [-92, 12, 0], 0.9: GRIP_R}},
        "left_arm": {"rotation": {0: GRIP_L, 0.3: [-46, -26, 0], 0.45: [-96, -24, 0], 0.65: [-96, -24, 0], 0.9: GRIP_L}},
        "body": {"rotation": {0: [0, 0, 0], 0.3: [-6, 18, 0], 0.45: [16, -6, 0], 0.65: [16, -6, 0], 0.9: [0, 0, 0]},
                 "position": {0: [0, 0, 0], 0.3: [0, 0, 1.5], 0.45: [0, -1, -3], 0.65: [0, -1, -3], 0.9: [0, 0, 0]}},
        "right_leg": {"rotation": {0: [0, 0, 0], 0.45: [-36, 0, 0], 0.65: [-36, 0, 0], 0.9: [0, 0, 0]}},
        "left_leg": {"rotation": {0: [0, 0, 0], 0.45: [28, 0, 0], 0.65: [28, 0, 0], 0.9: [0, 0, 0]}},
        "cape": {"rotation": {0: [6, 0, 0], 0.45: [28, 0, 0], 0.9: [6, 0, 0]}},
    })
    a[RA + "sit"] = anim(2.0, True, {
        "body": {"position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "right_leg": {"rotation": {0: [-90, 10, 0], 2.0: [-90, 10, 0]}, "position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "left_leg": {"rotation": {0: [-90, -10, 0], 2.0: [-90, -10, 0]}, "position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "right_arm": {"rotation": {0: [-40, 18, 0], 2.0: [-40, 18, 0]}},
        "left_arm": {"rotation": {0: [-46, -26, 0], 2.0: [-46, -26, 0]}},
        "cape": {"rotation": {0: [70, 0, 0], 2.0: [70, 0, 0]}},
        "tabard": {"rotation": {0: [-70, 0, 0], 2.0: [-70, 0, 0]}},
    })
    a[RA + "tamed"] = anim(1.4, False, {
        "right_arm": {"rotation": {0: GRIP_R, 0.35: [-172, 12, 0], 1.0: [-172, 12, 0], 1.4: GRIP_R}},
        "left_arm": {"rotation": {0: GRIP_L, 0.35: [-176, -16, 0], 1.0: [-176, -16, 0], 1.4: GRIP_L}},
        "body": {"position": {0: [0, 0, 0], 0.35: [0, 2, 0], 0.7: [0, 0, 0], 1.4: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.35: [-22, 0, 0], 1.0: [-22, 0, 0], 1.4: [0, 0, 0]}},
    })
    return arms_inward(a)


# ====================================================================== BALLESTERO
CP = {
    ".": None,
    "Q": (118, 24, 30), "q": (84, 14, 20), "w": (150, 40, 44),          # gambesón carmesí acolchado
    "L": (98, 56, 32), "l": (70, 38, 22), "K": (40, 20, 12),             # cuero
    "A": (70, 70, 84), "a": (44, 44, 56), "s": (120, 120, 136),          # acero (capacete)
    "G": (232, 190, 56), "g": (170, 122, 26), "R": (226, 26, 36), "E": (255, 70, 60),
    "M": (40, 12, 14), "m": (28, 8, 10),                                 # bufanda
    "T": (176, 150, 118), "F": (236, 236, 232), "H": (200, 200, 214),
}


def quilt(c, x, y):
    if is_gold(c) or is_red(c) or is_skin(c):
        return None
    l = lum(c)
    k = "q" if (x + y) % 4 == 0 or (x - y) % 4 == 0 else ("w" if l > 70 and (x * 3 + y) % 7 == 0 else "Q")
    return CP[k]


def crossbow_texture():
    img = base_skin()
    for box in (BODY, JACKET, R_SLEEVE, L_SLEEVE):
        recolor(img, box, quilt)
    # capacete de acero (capa exterior de la cabeza) con bufanda que tapa boca y nariz
    side = ["AAAAAAAA", "AsAAsAAA", "GgGGgGGg", "........", "........", "MMMMMMMM", "MmMMmMMM", "MMMMMMMM"]
    paint(img, 40, 0, ["AAAAAAAA", "AsAAAAsA", "AAAAAAAA", "AAAsAAAA", "AAAAAsAA", "AAAAAAAA", "AsAAAAsA", "AAAAAAAA"], CP)
    paint(img, 48, 0, ["........"] * 8, CP)
    paint(img, 40, 8, ["AAAAAAAA",
                       "AsAAAAsA",
                       "GgGRGgGG",
                       "........",
                       "........",
                       "MMMMMMMM",
                       "MmMMMmMM",
                       "MMMmMMMM"], CP)
    paint(img, 32, 8, side, CP)
    paint(img, 48, 8, side, CP)
    paint(img, 56, 8, ["AAAAAAAA", "AAsAAsAA", "GgGGgGGg", "........", "........", "MMMMMMMM", "MMmMMMmM", "MMMMMMMM"], CP)
    # correa cruzada de cuero con hebilla y cinturón con virotes
    for k in range(12):
        x = 20 + (k * 8) // 12
        if 0 <= k < 12:
            img.putpixel((x, 36 + k), CP["L"] + (255,))
            img.putpixel((min(27, x + 1), 36 + k), CP["l"] + (255,))
    for x in range(20, 28):
        img.putpixel((x, 45), CP["K"] + (255,))
    img.putpixel((23, 45), CP["G"] + (255,)); img.putpixel((24, 45), CP["G"] + (255,))
    # brazales de cuero en los antebrazos
    for face_x in (48, 52, 56, 60):
        paint(img, face_x, 58, ["KGGK", "LLlL", "lLLL", "KKKK"], CP)
    for face_x in (40, 44, 48, 52):
        paint(img, face_x, 42, ["KGGK", "LLlL", "lLLL", "KKKK"], CP)
    pk = Packer([(0, 68, 64, 128)])
    parts = []

    def part(size, faces):
        uv = pk.alloc(*[max(1, math.floor(v)) for v in size])
        parts.append((uv, size, faces))
        return uv
    F = lambda ch: (lambda i, j, fw, fh: tuple(CP[ch]) + (255,))
    brim = lambda i, j, fw, fh: tuple(CP["G" if (i in (0, fw - 1) or j in (0, fh - 1)) else ("A" if (i + j) % 4 else "s")]) + (255,)
    dome = lambda i, j, fw, fh: tuple(CP["A" if (i + j) % 5 else "s"]) + (255,)
    case = lambda i, j, fw, fh: tuple(CP["G" if j in (0, fh - 1) else ("L" if (i + j) % 3 else "l")]) + (255,)
    uv = {}
    uv["brim"] = part([12, 0.5, 12], {"all": brim})
    uv["dome"] = part([8, 1.5, 8], {"all": dome})
    uv["case"] = part([2.5, 6, 3.5], {"all": case, "top": F("K")})
    uv["bolt"] = part([0.6, 2.5, 0.6], {"all": F("T")})
    uv["fletch"] = part([0.8, 0.8, 0.8], {"all": F("R")})
    sheet = Sheet(64, TEX_H)
    sheet.img = img
    for (u, v), size, faces in parts:
        fl = [math.floor(x) for x in size]
        if sum(1 for x in fl if x == 0) >= 2:
            w, h, d = [max(1, x) for x in fl]
            for j in range(h + d):
                for i in range(2 * (w + d)):
                    sheet.px(u + i, v + j, faces["all"](i, j, w, h))
        else:
            sheet.box(u, v, fl[0], fl[1], fl[2], faces)
    return sheet.img, uv


def crossbow_geo(uv):
    g, _ = warrior.build_geo()
    a = Geo("geometry.nether_crossbowman", 64, TEX_H)
    a.bones = copy.deepcopy(g.bones)
    a.order = list(g.order)
    a.cubes = list(g.cubes)
    a.bone("hat", [0, 34, 0], "head")
    a.cube("hat", "h", [-6, 31.3, -6], [12, 0.5, 12], uv["brim"])
    a.cube("hat", "h", [-4, 34.4, -4], [8, 1.5, 8], uv["dome"])
    a.bone("bolt_case", [-4.6, 14, 0], "body", [0, 0, -8])
    a.cube("bolt_case", "q", [-7.0, 8.5, -1.7], [2.5, 6, 3.5], uv["case"])
    for k, (dx, dz) in enumerate([(-6.6, -1.2), (-5.7, -0.4), (-6.3, 0.6)]):
        a.cube("bolt_case", "b", [dx, 14.5, dz], [0.6, 2.5, 0.6], uv["bolt"])
        a.cube("bolt_case", "b", [dx - 0.1, 16.8, dz - 0.1], [0.8, 0.8, 0.8], uv["fletch"])
    return a


CA = "animation.nether_crossbowman."
HOLD_R = [-38, 14, 0]
HOLD_L = [-46, -34, 0]
AIM_R = [-90, 12, 0]
AIM_L = [-92, -38, 0]


def crossbow_animations():
    a = {}
    a[CA + "idle"] = anim(2.4, True, {
        "body": {"position": {0: [0, 0, 0], 1.2: [0, 0.3, 0], 2.4: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 1.2: [2, -3, 0], 2.4: [0, 0, 0]}},
        "right_arm": {"rotation": {0: HOLD_R, 1.2: [HOLD_R[0] - 3, HOLD_R[1], 0], 2.4: HOLD_R}},
        "left_arm": {"rotation": {0: HOLD_L, 1.2: [HOLD_L[0] - 3, HOLD_L[1], 0], 2.4: HOLD_L}},
    })
    a[CA + "walk"] = anim(1.0, True, {
        "right_leg": {"rotation": {0: [-30, 0, 0], 0.5: [30, 0, 0], 1.0: [-30, 0, 0]}},
        "left_leg": {"rotation": {0: [30, 0, 0], 0.5: [-30, 0, 0], 1.0: [30, 0, 0]}},
        "right_arm": {"rotation": {0: HOLD_R, 0.5: [HOLD_R[0] + 6, HOLD_R[1], 0], 1.0: HOLD_R}},
        "left_arm": {"rotation": {0: HOLD_L, 0.5: [HOLD_L[0] + 6, HOLD_L[1], 0], 1.0: HOLD_L}},
        "body": {"position": {0: [0, 0, 0], 0.25: [0, 0.6, 0], 0.5: [0, 0, 0], 0.75: [0, 0.6, 0], 1.0: [0, 0, 0]}},
        "bolt_case": {"rotation": {0: [0, 0, -8], 0.25: [4, 0, -12], 0.5: [0, 0, -8], 0.75: [4, 0, -12], 1.0: [0, 0, -8]}},
    })
    a[CA + "run"] = anim(0.6, True, {
        "right_leg": {"rotation": {0: [-48, 0, 0], 0.3: [44, 0, 0], 0.6: [-48, 0, 0]}},
        "left_leg": {"rotation": {0: [44, 0, 0], 0.3: [-48, 0, 0], 0.6: [44, 0, 0]}},
        "right_arm": {"rotation": {0: [-30, 14, 0], 0.3: [-40, 14, 0], 0.6: [-30, 14, 0]}},
        "left_arm": {"rotation": {0: [-40, -34, 0], 0.3: [-50, -34, 0], 0.6: [-40, -34, 0]}},
        "body": {"rotation": {0: [12, 0, 0], 0.6: [12, 0, 0]},
                 "position": {0: [0, 0, 0], 0.15: [0, 1.1, 0], 0.3: [0, 0, 0], 0.45: [0, 1.1, 0], 0.6: [0, 0, 0]}},
        "head": {"rotation": {0: [-10, 0, 0], 0.6: [-10, 0, 0]}},
        "bolt_case": {"rotation": {0: [8, 0, -8], 0.3: [-6, 0, -14], 0.6: [8, 0, -8]}},
    })
    # disparo: apunta, dispara (retroceso) y recarga tensando la cuerda con la mano izquierda
    a[CA + "attack_crossbow"] = anim(2.2, False, {
        "right_arm": {"rotation": {0: HOLD_R, 0.25: AIM_R, 0.45: AIM_R, 0.5: [-104, 12, 0], 0.65: AIM_R,
                                   0.95: [-50, 10, 0], 1.8: [-50, 10, 0], 2.2: HOLD_R}},
        "left_arm": {"rotation": {0: HOLD_L, 0.25: AIM_L, 0.45: AIM_L, 0.5: [-106, -38, 0], 0.65: AIM_L,
                                  0.95: [-60, -20, 0], 1.2: [-30, -10, 0], 1.45: [-62, -22, 0], 1.7: [-28, -10, 0],
                                  1.9: [-46, -30, 0], 2.2: HOLD_L}},
        "body": {"rotation": {0: [0, 0, 0], 0.25: [0, 14, 0], 0.45: [0, 14, 0], 0.5: [-4, 14, 0], 0.65: [0, 14, 0],
                              0.95: [10, 0, 0], 1.8: [10, 0, 0], 2.2: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.25: [0, -14, 0], 0.65: [0, -14, 0], 0.95: [16, 0, 0], 1.8: [16, 0, 0], 2.2: [0, 0, 0]}},
        "right_leg": {"rotation": {0: [0, 0, 0], 0.25: [-10, 0, 0], 0.65: [-10, 0, 0], 2.2: [0, 0, 0]}},
        "left_leg": {"rotation": {0: [0, 0, 0], 0.25: [10, 0, 0], 0.65: [10, 0, 0], 2.2: [0, 0, 0]}},
    })
    a[CA + "sit"] = anim(2.0, True, {
        "body": {"position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "right_leg": {"rotation": {0: [-90, 10, 0], 2.0: [-90, 10, 0]}, "position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "left_leg": {"rotation": {0: [-90, -10, 0], 2.0: [-90, -10, 0]}, "position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "right_arm": {"rotation": {0: [-34, 14, 0], 2.0: [-34, 14, 0]}},
        "left_arm": {"rotation": {0: [-40, -30, 0], 2.0: [-40, -30, 0]}},
    })
    a[CA + "tamed"] = anim(1.2, False, {
        "right_arm": {"rotation": {0: HOLD_R, 0.3: [-170, 10, 0], 0.9: [-170, 10, 0], 1.2: HOLD_R}},
        "body": {"position": {0: [0, 0, 0], 0.3: [0, 2, 0], 0.6: [0, 0, 0], 1.2: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.3: [-20, 0, 0], 0.9: [-20, 0, 0], 1.2: [0, 0, 0]}},
    })
    return arms_inward(a)


def write_all():
    tex, uv = royal_texture()
    g = royal_geo(uv)
    save_json(os.path.join(ASSETS, "geo", "entity", "royal_warrior.geo.json"), g.to_json())
    save_json(os.path.join(ASSETS, "animations", "entity", "royal_warrior.animation.json"),
              {"format_version": "1.8.0", "animations": royal_animations()})
    tex.save(os.path.join(ASSETS, "textures", "entity", "royal_warrior.png"))
    tex2, uv2 = crossbow_texture()
    g2 = crossbow_geo(uv2)
    save_json(os.path.join(ASSETS, "geo", "entity", "crossbowman.geo.json"), g2.to_json())
    save_json(os.path.join(ASSETS, "animations", "entity", "crossbowman.animation.json"),
              {"format_version": "1.8.0", "animations": crossbow_animations()})
    tex2.save(os.path.join(ASSETS, "textures", "entity", "crossbowman.png"))
    return (g, tex), (g2, tex2)
