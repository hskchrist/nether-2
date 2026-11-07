"""Silla del Dragón Infernal: un hueso "saddle" (hijo de "body") que se agrega al modelo del usuario sin tocar sus cubos
ni su textura. La silla usa su propia textura (dragon_infernal_saddle.png, del mismo tamaño que la del dragón, con los
píxeles de la silla en una zona que el dragón no usa) y el mod la dibuja encima sólo cuando el dragón está ensillado.

La púa del lomo que queda bajo el asiento pasa a un hueso propio ("spike_saddle", mismo cubo y mismas UV) para
esconderla cuando lleva la silla, como pasa con el Dragón del Nether.
"""
import copy
import json
import os
import random

import numpy as np
from PIL import Image

from common import ASSETS, DATA, MODID, save_json

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref", "infernal")
D = 2              # texeles por unidad del modelo (como el cuerpo del dragón)
TEXW = 512

# paleta: cuero rojo oscuro, manta carmesí con borde de oro, rubí y metal de piedra negra
LEATHER, LEATHER_D, LEATHER_L = (104, 30, 26), (66, 18, 16), (138, 46, 36)
SEAT, SEAT_L = (150, 24, 34), (186, 44, 52)
CLOTH, CLOTH_D = (122, 16, 44), (84, 10, 30)
GOLD, GOLD_D, GOLD_L = (226, 172, 52), (162, 110, 28), (255, 226, 120)
RUBY, RUBY_L, RUBY_D = (214, 28, 44), (255, 120, 130), (120, 8, 20)
IRON, IRON_L, IRON_D = (52, 46, 58), (98, 92, 106), (28, 24, 32)


def cubes():
    """(nombre, origen, tamaño, material). Unidades del modelo; el cuerpo va de x -12..12, y -4..20, z -8..56 y el
    jinete se sienta en z ~ 10 (0,4 bloques detrás del centro)."""
    c = []
    # manta bajo la silla, con faldones a los lados
    c.append(("manta", [-12.6, 19.6, -2], [25.2, 1.0, 22], "cloth"))
    for s in (-1, 1):
        x = -12.6 if s < 0 else 12.0
        c.append(("faldon", [x, 9.0, 0], [0.6, 10.8, 18], "cloth"))
    # asiento, cabezal con cuerno de rubí y respaldo
    c.append(("asiento", [-7, 20.6, 1], [14, 2.0, 16], "seat"))
    c.append(("cabezal", [-5, 22.6, 0], [10, 3.0, 3], "leather"))
    c.append(("cuerno", [-1.5, 25.6, 0.5], [3, 3.0, 2], "gold"))
    c.append(("rubi_cuerno", [-1, 28.6, 1], [2, 1.0, 1], "ruby"))
    c.append(("respaldo", [-6, 22.6, 15], [12, 4.0, 3], "leather"))
    c.append(("rubi_respaldo", [-1.5, 23.6, 14.6], [3, 2.0, 0.4], "ruby"))
    # cincha alrededor del vientre y estribos
    for s in (-1, 1):
        x = -12.9 if s < 0 else 12.6
        c.append(("cincha", [x, -4.6, 7], [0.3, 13.8, 3], "leather"))
        xs = -13.4 if s < 0 else 12.6
        c.append(("correa_estribo", [xs, 0.5, 11.5], [0.8, 19.3, 1.5], "leather"))
        xe = -14.4 if s < 0 else 12.0
        c.append(("estribo", [xe, -2.5, 10.5], [2.4, 3.0, 3.5], "iron"))
    c.append(("cincha_vientre", [-12.9, -4.6, 7], [25.8, 0.6, 3], "leather"))
    return c


FACES = {  # cara -> (ancho, alto) en unidades a partir del tamaño (x, y, z)
    "north": lambda s: (s[0], s[1]), "south": lambda s: (s[0], s[1]),
    "east": lambda s: (s[2], s[1]), "west": lambda s: (s[2], s[1]),
    "up": lambda s: (s[0], s[2]), "down": lambda s: (s[0], s[2]),
}


def free_mask():
    """Zonas de la textura del dragón que ninguna cara (con área) usa."""
    g = json.load(open(os.path.join(REF, "dragon_infernal.geo.json")))["minecraft:geometry"][0]
    occ = np.zeros((TEXW, TEXW), bool)
    dims = {"north": (0, 1), "south": (0, 1), "east": (2, 1), "west": (2, 1), "up": (0, 2), "down": (0, 2)}
    for b in g["bones"]:
        for c in b.get("cubes", []):
            for f, d in c["uv"].items():
                a, bb = dims[f]
                if c["size"][a] < 0.1 or c["size"][bb] < 0.1:
                    continue
                u, v = d["uv"]
                du, dv = d["uv_size"]
                x0, x1 = sorted([u, u + du])
                y0, y1 = sorted([v, v + dv])
                occ[int(np.floor(y0)):int(np.ceil(y1)) + 1, int(np.floor(x0)):int(np.ceil(x1)) + 1] = True
    return ~occ


def pack(rects, free):
    """Estantes simples dentro de la zona libre (abajo de la textura: y 400..512)."""
    out = {}
    x, y, row = 0, 402, 0
    for key, (w, h) in sorted(rects.items(), key=lambda kv: -kv[1][1]):
        if x + w > TEXW:
            x, y, row = 0, y + row + 1, 0
        assert y + h <= TEXW, "no cabe la silla en la textura"
        assert free[y:y + h, x:x + w].all(), ("zona ocupada", key, x, y, w, h)
        out[key] = (x, y)
        x += w + 1
        row = max(row, h)
    return out


def paint(img, x, y, w, h, mat, face, rnd):
    px = img.load()
    for j in range(h):
        for i in range(w):
            edge = i == 0 or j == 0 or i == w - 1 or j == h - 1
            n = rnd.randint(-8, 8)
            if mat == "cloth":
                trim = i <= 1 or j <= 1 or i >= w - 2 or j >= h - 2
                if trim and (w > 4 and h > 4):
                    c = GOLD_L if (i + j) % 7 == 0 else (GOLD if not edge else GOLD_D)
                elif (i // 3 + j // 3) % 4 == 0 and (i + j) % 2 == 0:
                    c = CLOTH_D                                     # dibujo de rombos oscuros
                else:
                    c = CLOTH
            elif mat == "seat":
                if edge:
                    c = LEATHER_D
                elif (i == 1 or j == 1 or i == w - 2 or j == h - 2) and (i + j) % 2 == 0:
                    c = GOLD                                        # costura de oro
                else:
                    c = SEAT_L if face == "up" and (j * 3 + i) % 11 == 0 else SEAT
            elif mat == "leather":
                if edge:
                    c = LEATHER_D
                elif (j == 1 or j == h - 2) and i % 2 == 0 and h > 3:
                    c = GOLD_D
                else:
                    c = LEATHER_L if (i * 5 + j * 3) % 13 == 0 else LEATHER
            elif mat == "gold":
                c = GOLD_D if edge else (GOLD_L if (i + j) % 5 == 0 else GOLD)
            elif mat == "ruby":
                c = RUBY_D if edge and w > 2 and h > 2 else (RUBY_L if i + j <= 1 else RUBY)
            else:   # hierro (piedra negra)
                hole = 0 < i < w - 1 and 0 < j < h - 1 and face in ("east", "west") and w > 3 and h > 3
                c = IRON_D if hole else (IRON_L if edge else IRON)
            if mat not in ("gold", "ruby"):
                c = tuple(max(0, min(255, v + n)) for v in c)
            px[x + i, y + j] = c + (255,)


def build():
    geo = json.load(open(os.path.join(REF, "dragon_infernal.geo.json")))
    g = geo["minecraft:geometry"][0]
    free = free_mask()
    cs = cubes()
    rects = {}
    for k, (name, o, s, mat) in enumerate(cs):
        for f, fn in FACES.items():
            w, h = fn(s)
            rects[(k, f)] = (max(1, round(w * D)), max(1, round(h * D)))
    pos = pack(rects, free)
    tex = Image.new("RGBA", (TEXW, TEXW), (0, 0, 0, 0))
    rnd = random.Random(7)
    out_cubes = []
    for k, (name, o, s, mat) in enumerate(cs):
        uv = {}
        for f in FACES:
            x, y = pos[(k, f)]
            w, h = rects[(k, f)]
            paint(tex, x, y, w, h, mat, f, rnd)
            uv[f] = {"uv": [x + 0.0312, y + 0.0312], "uv_size": [w - 0.0624, h - 0.0624]}
        out_cubes.append({"origin": [round(v, 3) for v in o], "size": [round(v, 3) for v in s], "uv": uv})
    body = next(b for b in g["bones"] if b["name"] == "body")
    # la púa delantera del lomo (la que queda bajo el asiento) va a su propio hueso, idéntica
    spike = next(c for c in body["cubes"] if c["origin"] == [-1.0, 20.0, -2.0])
    body["cubes"] = [c for c in body["cubes"] if c is not spike]
    i = g["bones"].index(body)
    g["bones"].insert(i + 1, {"name": "spike_saddle", "parent": "body", "pivot": list(body["pivot"]), "cubes": [spike]})
    g["bones"].insert(i + 2, {"name": "saddle", "parent": "body", "pivot": list(body["pivot"]), "cubes": out_cubes})
    return geo, tex


def icon():
    """Ícono 16x16 de la silla: cuero rojo, manta carmesí con oro, cuerno de rubí y estribo."""
    rows = [
        "................",
        "................",
        "......gr........",
        "......gg........",
        ".....LLLL...LL..",
        "....LSSSSLLLLL..",
        "...LSSSSSSSSL...",
        "..CCCCCCCCCCCC..",
        ".CYYYYYYYYYYYYC.",
        ".CMMCMMCMMCMMMC.",
        ".CMMMMMMMMMMMMC.",
        ".CYYYYYYYYYYYYC.",
        "..CC..L...CCC...",
        "......L.........",
        ".....III........",
        "................",
    ]
    pal = {"L": LEATHER, "S": SEAT, "C": CLOTH_D, "M": CLOTH, "Y": GOLD, "g": GOLD, "r": RUBY, "I": IRON_L}
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                img.putpixel((x, y), pal[ch] + (255,))
    return img


def write_all():
    geo, tex = build()
    gdir = os.path.join(ASSETS, "geo", "entity")
    with open(os.path.join(gdir, "dragon_infernal.geo.json"), "w") as f:
        json.dump(geo, f, indent=1)
    tex.save(os.path.join(ASSETS, "textures", "entity", "dragon_infernal_saddle.png"))
    icon().save(os.path.join(ASSETS, "textures", "item", "infernal_saddle.png"))
    save_json(os.path.join(ASSETS, "models", "item", "infernal_saddle.json"),
              {"parent": "minecraft:item/generated", "textures": {"layer0": MODID + ":item/infernal_saddle"}})
    # crafteo: cuero arriba, rubíes y crema de magma al medio, estribos de hierro abajo
    save_json(os.path.join(DATA, "recipe", "infernal_saddle.json"), {
        "type": "minecraft:crafting_shaped", "category": "equipment", "pattern": ["LLL", "RMR", "I I"],
        "key": {"L": {"item": "minecraft:leather"}, "R": {"item": MODID + ":ruby"}, "M": {"item": "minecraft:magma_cream"},
                "I": {"item": "minecraft:iron_ingot"}},
        "result": {"id": MODID + ":infernal_saddle", "count": 1}})
    for code in ("es_es", "es_cl", "es_mx", "es_ar", "en_us"):
        p = os.path.join(ASSETS, "lang", code + ".json")
        d = json.load(open(p, encoding="utf-8"))
        en = code == "en_us"
        d["item.%s.infernal_saddle" % MODID] = "Infernal Dragon Saddle" if en else "Silla del Dragón Infernal"
        d["tooltip.%s.infernal_saddle" % MODID] = ("Put it on an adult Infernal Dragon to ride it" if en
                                                   else "Pónsela a un Dragón Infernal adulto para montarlo")
        d["msg.%s.need_infernal_saddle" % MODID] = ("The Infernal Dragon needs an Infernal Dragon Saddle to be ridden." if en
                                                    else "El Dragón Infernal necesita una Silla del Dragón Infernal para montarlo.")
        save_json(p, d)
    return geo, tex


if __name__ == "__main__":
    write_all()
