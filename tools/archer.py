"""Arquero del Nether: mismo cuerpo que el guerrero del usuario, skin derivada con su estética,
capucha completa, máscara, chaleco con correa, brazal, carcaj 3D con flechas y arco de rubí."""
import copy
import os
from PIL import Image
from common import ASSETS, save_json
from models import Geo, anim, flip_y
import warrior

TEX_H = 96  # 64 originales + 4 de borde repetido + espacio para piezas 3D (carcaj, flechas, punta de capucha)

C = {
    ".": None,
    "H": (92, 16, 20), "h": (68, 10, 14), "k": (44, 6, 8),
    "g": (200, 146, 32), "G": (244, 204, 74), "R": (222, 26, 32), "r": (140, 10, 16), "W": (240, 238, 232),
    "M": (54, 12, 14), "m": (36, 8, 10),
    "B": (58, 20, 16), "b": (80, 32, 22), "L": (104, 48, 32), "K": (30, 10, 8), "S": (38, 16, 10),
    "T": (176, 150, 118), "t": (130, 104, 76), "F": (230, 230, 226), "f": (200, 30, 36),
}


def paint(img, x, y, rows):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            c = C[ch]
            img.putpixel((x + i, y + j), (0, 0, 0, 0) if c is None else c + (255,))


def is_gold(c):
    r, g, b, a = c
    return a > 0 and r > 170 and g > 100 and b < 110 and r - b > 90


def is_skin(c):
    r, g, b, a = c
    return a > 0 and r > 150 and 100 < g < 200 and 80 < b < 170 and r - b > 40


def build_texture():
    _, wtex = warrior.load_bbmodel()
    img = Image.new("RGBA", (64, TEX_H), (0, 0, 0, 0))
    img.paste(wtex, (0, 0))
    for y in range(64, 68):
        img.paste(wtex.crop((0, 63, 64, 64)), (0, y))

    # --- capucha completa (capa exterior de la cabeza, 32..64 x 0..16)
    side = ["HHHHHHHH", "HhHHHhHH", "HHHHHHHH", "HHhHHHHH", "HHHHHhHH", "hHHHHHHH", "HHHhHHHh", "kkkkkkkk"]
    paint(img, 40, 0, ["HHHHHHHH", "HHHhhHHH", "HHHhhHHH", "HHHhhHHH", "HHHhhHHH", "HHHhhHHH", "HHHhhHHH", "HHHHHHHH"])  # arriba
    paint(img, 48, 0, ["........"] * 8)                                                                                  # abajo
    paint(img, 40, 8, ["hHHHHHHh",
                       "HhHHHHhH",
                       "HkggggkH",
                       "Hk....kH",
                       "H......H",
                       "HMMMMMMH",
                       "HMmMMmMH",
                       "hMMMMMMh"])                                                                                     # frente
    paint(img, 32, 8, side)
    paint(img, 48, 8, side)
    paint(img, 56, 8, ["HHHHHHHH", "HHhHHhHH", "HHHHHHHH", "HhHHHHhH", "HHHgRHHH", "HHHHHHHH", "hHHHHHHh", "kkkkkkkk"])  # espalda

    # --- torso: sin piel al descubierto (bufanda/túnica)
    for x in range(18, 38):
        for y in range(18, 34):
            if is_skin(img.getpixel((x, y))):
                img.putpixel((x, y), C["H"] + (255,) if (x + y) % 3 else C["h"] + (255,))
    # --- chaleco con correa cruzada (frente y espalda de la chaqueta)
    paint(img, 20, 36, ["BbBBBLSS",
                        "BBbBBSSB",
                        "BBBBSSBB",
                        "BbBgGgBb",
                        "BBSgRgBB",
                        "BSSgggBB",
                        "SSBBBBbB",
                        "SBBBBBBB",
                        "BBBbBBBB",
                        "KKKgGKKK",
                        "BBBBbBBB",
                        "BbBBBBBB"])
    paint(img, 28, 36, ["SSBBBBbB",
                        "BSSBBBBB",
                        "BBSSBbBB",
                        "BBBSSBBB",
                        "BbBBSSBB",
                        "BBBBBSSB",
                        "BBbBBBSS",
                        "BBBBBBBS",
                        "BBBBbBBB",
                        "KKKKKKKK",
                        "BBBbBBBB",
                        "BBBBBBbB"])

    # --- mangas: hombreras de oro -> hombreras de cuero con ribete dorado
    for (x0, y0, x1, y1) in [(40, 32, 56, 49), (48, 48, 64, 65)]:
        for x in range(x0, x1):
            for y in range(y0, y1):
                if is_gold(img.getpixel((x, y))):
                    img.putpixel((x, y), (C["b"] if (x + y) % 2 else C["L"]) + (255,))
    for x in range(40, 56):
        img.putpixel((x, 36), C["g"] + (255,))
    for x in range(48, 64):
        img.putpixel((x, 52), C["g"] + (255,))
    # --- brazal de arquero en el antebrazo izquierdo (manga izquierda, filas 8 a 11 de sus 4 caras)
    for face_x in (48, 52, 56, 60):
        paint(img, face_x, 60, ["SgGS", "BLLB", "SgGS", "KKKK"])

    # --- piezas 3D (zona nueva, y >= 68)
    # carcaj 4x12x4 en (0,68): caras de 4x12, tapas de 4x4
    quiver_face = ["gGGg", "BbBB", "BBBB", "bBBb", "BBBB", "BgGB", "BRrB", "BgGB", "BBBb", "bBBB", "BBBB", "gGGg"]
    for fx in (0, 4, 8, 12):
        paint(img, fx, 72, quiver_face)
    paint(img, 4, 68, ["KKKK", "KSSK", "KSSK", "KKKK"])
    paint(img, 8, 68, ["BBBB", "BbBB", "BBbB", "BBBB"])
    # flechas 1x4x1 en (16,68), (20,68), (24,68): punta de plumas arriba, astil abajo
    for ax, tip in ((16, "F"), (20, "f"), (24, "F")):
        for fx in range(4):
            img.putpixel((ax + fx, 68), C["t"] + (255,))
            for yy in (69, 70):
                img.putpixel((ax + fx, yy), C[tip] + (255,))
            for yy in (71, 72):
                img.putpixel((ax + fx, yy), C["t"] + (255,))
    # punta de la capucha 4x4x1 en (28,68)
    paint(img, 28, 68, [".HHHH.....", "HhHHhHHhHH", "HHhHHHHHhH", "hHHHhHhHHH", "HHHHHHHHHH"])
    # variación de tela en la capucha (pliegues)
    import random
    rnd = random.Random(3)
    for x in range(32, 64):
        for y in range(0, 16):
            c = img.getpixel((x, y))
            if c[3] and c[:3] == C["H"] and rnd.random() < 0.22:
                img.putpixel((x, y), ((110, 22, 26) if rnd.random() < 0.5 else C["h"]) + (255,))
    return img


def build_geo():
    g, _ = warrior.build_geo()
    a = Geo("geometry.nether_archer", 64, TEX_H)
    a.bones = copy.deepcopy(g.bones)
    a.order = list(g.order)
    a.cubes = list(g.cubes)
    a.bone("quiver", [0, 20, 4.2], "body", [0, 0, 22])
    a.cube("quiver", "quiver", [-2, 13.5, 2.5], [4, 12, 4], [0, 68])
    a.cube("quiver", "arrow", [-1.6, 25, 3.0], [1, 4, 1], [16, 68])
    a.cube("quiver", "arrow", [0.4, 25.6, 3.8], [1, 4, 1], [20, 68])
    a.cube("quiver", "arrow", [-0.6, 24.8, 5.0], [1, 4, 1], [24, 68])
    a.bone("hood_tip", [0, 30, 4.6], "head", [12, 0, 0])
    a.cube("hood_tip", "hood", [-2, 26.5, 4.4], [4, 4, 1], [28, 68])
    return a


P = "animation.nether_archer."


def animations():
    a = {}
    a[P + "idle"] = anim(2.4, True, {
        "body": {"position": {0: [0, 0, 0], 1.2: [0, 0.3, 0], 2.4: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 1.2: [2, 3, 0], 2.4: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [-12, 0, -5], 1.2: [-15, 0, -6], 2.4: [-12, 0, -5]}},
        "right_arm": {"rotation": {0: [0, 0, 5], 1.2: [-2, 0, 7], 2.4: [0, 0, 5]}},
        "quiver": {"rotation": {0: [0, 0, 22], 1.2: [2, 0, 22], 2.4: [0, 0, 22]}},
    })
    a[P + "walk"] = anim(1.0, True, {
        "right_leg": {"rotation": {0: [-30, 0, 0], 0.5: [30, 0, 0], 1.0: [-30, 0, 0]}},
        "left_leg": {"rotation": {0: [30, 0, 0], 0.5: [-30, 0, 0], 1.0: [30, 0, 0]}},
        "right_arm": {"rotation": {0: [28, 0, 5], 0.5: [-28, 0, 5], 1.0: [28, 0, 5]}},
        "left_arm": {"rotation": {0: [-18, 0, -5], 0.5: [-6, 0, -5], 1.0: [-18, 0, -5]}},
        "body": {"position": {0: [0, 0, 0], 0.25: [0, 0.6, 0], 0.5: [0, 0, 0], 0.75: [0, 0.6, 0], 1.0: [0, 0, 0]}},
        "quiver": {"rotation": {0: [0, 0, 20], 0.25: [4, 0, 24], 0.5: [0, 0, 20], 0.75: [4, 0, 24], 1.0: [0, 0, 20]}},
        "hood_tip": {"rotation": {0: [12, 0, 0], 0.25: [20, 0, 0], 0.5: [12, 0, 0], 0.75: [20, 0, 0], 1.0: [12, 0, 0]}},
    })
    a[P + "run"] = anim(0.6, True, {
        "right_leg": {"rotation": {0: [-50, 0, 0], 0.3: [45, 0, 0], 0.6: [-50, 0, 0]}},
        "left_leg": {"rotation": {0: [45, 0, 0], 0.3: [-50, 0, 0], 0.6: [45, 0, 0]}},
        "right_arm": {"rotation": {0: [50, 0, 6], 0.3: [-50, 0, 6], 0.6: [50, 0, 6]}},
        "left_arm": {"rotation": {0: [-40, 0, -6], 0.3: [-20, 0, -6], 0.6: [-40, 0, -6]}},
        "body": {"rotation": {0: [12, 0, 0], 0.6: [12, 0, 0]},
                 "position": {0: [0, 0, 0], 0.15: [0, 1.1, 0], 0.3: [0, 0, 0], 0.45: [0, 1.1, 0], 0.6: [0, 0, 0]}},
        "head": {"rotation": {0: [-10, 0, 0], 0.6: [-10, 0, 0]}},
        "hood_tip": {"rotation": {0: [35, 0, 0], 0.3: [45, 0, 0], 0.6: [35, 0, 0]}},
        "quiver": {"rotation": {0: [6, 0, 18], 0.3: [10, 0, 26], 0.6: [6, 0, 18]}},
    })
    # Disparo: alza el arco, tensa la cuerda hasta la cara, apunta y suelta
    a[P + "attack_bow"] = anim(1.2, False, {
        "left_arm": {"rotation": {0: [-12, 0, -5], 0.2: [-90, 12, 0], 0.85: [-90, 12, 0], 1.0: [-80, 8, 0], 1.2: [-12, 0, -5]}},
        "right_arm": {"rotation": {0: [0, 0, 5], 0.2: [-88, -10, 0], 0.3: [-92, -10, 0], 0.75: [-92, -50, 0],
                                   0.85: [-92, -50, 0], 0.9: [-70, -80, 0], 1.2: [0, 0, 5]},
                      "position": {0: [0, 0, 0], 0.3: [0, 0, 0], 0.75: [0, 0, 1.5], 0.85: [0, 0, 1.5], 1.0: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.2: [0, -18, 0], 0.85: [0, -18, 0], 0.95: [-4, -14, 0], 1.2: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.2: [0, 18, 0], 0.85: [0, 18, 0], 1.2: [0, 0, 0]}},
        "right_leg": {"rotation": {0: [0, 0, 0], 0.2: [-8, 0, 0], 0.85: [-8, 0, 0], 1.2: [0, 0, 0]}},
        "left_leg": {"rotation": {0: [0, 0, 0], 0.2: [8, 0, 0], 0.85: [8, 0, 0], 1.2: [0, 0, 0]}},
    })
    a[P + "sit"] = anim(2.0, True, {
        "body": {"position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "right_leg": {"rotation": {0: [-90, 10, 0], 2.0: [-90, 10, 0]}, "position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "left_leg": {"rotation": {0: [-90, -10, 0], 2.0: [-90, -10, 0]}, "position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "right_arm": {"rotation": {0: [-30, 0, 6], 2.0: [-30, 0, 6]}},
        "left_arm": {"rotation": {0: [-35, 0, -6], 2.0: [-35, 0, -6]}},
    })
    a[P + "tamed"] = anim(1.2, False, {
        "left_arm": {"rotation": {0: [-12, 0, -5], 0.3: [-175, 0, -10], 0.9: [-175, 0, -10], 1.2: [-12, 0, -5]}},
        "body": {"position": {0: [0, 0, 0], 0.3: [0, 2, 0], 0.6: [0, 0, 0], 1.2: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.3: [-20, 0, 0], 0.9: [-20, 0, 0], 1.2: [0, 0, 0]}},
    })
    return a


def write_all():
    g = build_geo()
    tex = build_texture()
    save_json(os.path.join(ASSETS, "geo", "entity", "archer.geo.json"), g.to_json())
    save_json(os.path.join(ASSETS, "animations", "entity", "archer.animation.json"),
              {"format_version": "1.8.0", "animations": flip_y(animations())})
    tex.save(os.path.join(ASSETS, "textures", "entity", "archer.png"))
    return g, tex
