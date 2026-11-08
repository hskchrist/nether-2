"""Bloques del bioma Mar del Nether (estilo de la foto del usuario): Pasto del Mar del Nether (netherrack con pasto azul
y violeta encima), Hierba del Mar del Nether, Cristal del Mar del Nether (morado, brilla), Carámbano de Hielo (cuelga de
las Hojas de Hielo) y Tronco del Árbol de Hielo (corteza oscura rojiza). Texturas 16x16 pintadas aquí.

También: modelos, estados, nombres, botín, crafteos y etiquetas.
"""
import json
import os
import random

from PIL import Image

from common import ASSETS, DATA, MODID, save_json
import datagen2

R = MODID + ":"
M = "minecraft:"
BLOCK_TEX = os.path.join(ASSETS, "textures", "block")
BM = os.path.join(ASSETS, "models", "block")
IM = os.path.join(ASSETS, "models", "item")
BS = os.path.join(ASSETS, "blockstates")

NAMES = {
    "pasto_mar_nether": ("Pasto del Mar del Nether", "Nether Sea Grass Block"),
    "hierba_mar_nether": ("Hierba del Mar del Nether", "Nether Sea Grass"),
    "cristal_mar_nether": ("Cristal del Mar del Nether", "Nether Sea Crystal"),
    "carambano_hielo": ("Carámbano de Hielo", "Icicle"),
    "tronco_hielo": ("Tronco del Árbol de Hielo", "Frost Log"),
}

# colores sacados de la foto: pasto azul grisáceo con violeta, netherrack rojo oscuro
GRASS = [(86, 92, 138), (104, 108, 160), (70, 74, 120), (122, 116, 184), (92, 84, 150), (60, 62, 104), (136, 140, 196)]
RACK = [(98, 38, 40), (112, 50, 50), (82, 30, 34), (126, 60, 58), (70, 24, 28), (104, 44, 46)]


def px(img, x, y, c):
    img.putpixel((x, y), tuple(int(max(0, min(255, v))) for v in c[:3]) + ((c[3],) if len(c) > 3 else (255,)))


def grass_top():
    r = random.Random(3)
    im = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            c = r.choice(GRASS)
            if r.random() < 0.06:
                c = (150, 90, 200)  # puntitos violeta
            px(im, x, y, c)
    return im


def grass_side():
    r = random.Random(5)
    im = Image.new("RGBA", (16, 16))
    drip = [r.randint(2, 5) for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if y < drip[x]:
                c = r.choice(GRASS)
                if y == drip[x] - 1:
                    c = tuple(v * 0.8 for v in c)
            else:
                c = r.choice(RACK)
                if r.random() < 0.12:
                    c = tuple(v * 0.75 for v in c)
            px(im, x, y, c)
    return im


def tall_grass():
    r = random.Random(9)
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for blade in range(9):
        x0 = r.randint(1, 14)
        h = r.randint(6, 14)
        lean = r.choice((-1, 0, 0, 1))
        col = r.choice([(150, 176, 196), (128, 150, 186), (170, 186, 210), (140, 110, 200), (112, 130, 176)])
        for i in range(h):
            y = 15 - i
            x = x0 + (lean * i) // 5
            if 0 <= x < 16:
                k = 0.7 + 0.3 * i / h
                px(im, x, y, tuple(v * k for v in col))
    return im


def crystal():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    shards = [(7, 13, 2), (4, 9, 1), (11, 10, 1), (9, 7, 1), (2, 6, 1), (13, 6, 1)]
    for cx, h, w in shards:
        for i in range(h):
            y = 15 - i
            ww = w if i < h - 2 else 0
            for dx in range(-ww, ww + 1):
                x = cx + dx
                if 0 <= x < 16:
                    t = i / max(1, h)
                    c = (170 + 70 * t, 70 + 110 * t, 230 + 25 * t) if dx <= 0 else (120 + 40 * t, 40 + 50 * t, 180 + 40 * t)
                    px(im, x, y, c)
    return im


def icicle():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    spikes = [(8, 15, 2), (5, 10, 1), (11, 12, 1), (3, 6, 0), (13, 7, 0)]
    for cx, h, w in spikes:
        for i in range(h):
            y = i
            ww = w if i < h * 0.5 else (w - 1 if i < h * 0.8 else 0)
            for dx in range(-max(0, ww), max(0, ww) + 1):
                x = cx + dx
                if 0 <= x < 16:
                    c = (200, 236, 255, 230) if dx < 0 or (dx == 0 and i % 3 == 0) else (140, 196, 240, 215)
                    px(im, x, y, c)
    return im


def log_side():
    r = random.Random(13)
    im = Image.new("RGBA", (16, 16))
    for x in range(16):
        base = r.choice([(52, 16, 22), (66, 22, 28), (44, 12, 18), (78, 28, 32)])
        for y in range(16):
            k = 1.0 + (r.random() - 0.5) * 0.25
            c = tuple(v * k for v in base)
            if r.random() < 0.05:
                c = (120, 170, 220)  # escarcha
            px(im, x, y, c)
    return im


def log_top():
    im = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            d = max(abs(x - 7.5), abs(y - 7.5))
            if d > 6.5:
                c = (52, 16, 22)
            else:
                ring = int(d) % 2
                c = (120, 46, 52) if ring else (98, 36, 42)
            px(im, x, y, c)
    return im


def textures():
    os.makedirs(BLOCK_TEX, exist_ok=True)
    for name, fn in (("pasto_mar_nether_top", grass_top), ("pasto_mar_nether_side", grass_side),
                     ("hierba_mar_nether", tall_grass), ("cristal_mar_nether", crystal), ("carambano_hielo", icicle),
                     ("tronco_hielo", log_side), ("tronco_hielo_top", log_top)):
        fn().save(os.path.join(BLOCK_TEX, name + ".png"))


def T(n):
    return R + "block/" + n


def models():
    save_json(os.path.join(BM, "pasto_mar_nether.json"), {"parent": "minecraft:block/cube_bottom_top", "textures": {
        "top": T("pasto_mar_nether_top"), "side": T("pasto_mar_nether_side"), "bottom": "minecraft:block/netherrack"}})
    save_json(os.path.join(BS, "pasto_mar_nether.json"), {"variants": {"": [
        {"model": R + "block/pasto_mar_nether"}, {"model": R + "block/pasto_mar_nether", "y": 90},
        {"model": R + "block/pasto_mar_nether", "y": 180}, {"model": R + "block/pasto_mar_nether", "y": 270}]}})
    save_json(os.path.join(IM, "pasto_mar_nether.json"), {"parent": R + "block/pasto_mar_nether"})
    for n in ("hierba_mar_nether", "cristal_mar_nether", "carambano_hielo"):
        save_json(os.path.join(BM, n + ".json"), {"parent": "minecraft:block/cross", "render_type": "minecraft:cutout",
                                                  "textures": {"cross": T(n)}})
        save_json(os.path.join(BS, n + ".json"), {"variants": {"": {"model": R + "block/" + n}}})
        save_json(os.path.join(IM, n + ".json"), {"parent": "minecraft:item/generated", "textures": {"layer0": T(n)}})
    save_json(os.path.join(BM, "tronco_hielo.json"), {"parent": "minecraft:block/cube_column", "textures": {
        "end": T("tronco_hielo_top"), "side": T("tronco_hielo")}})
    save_json(os.path.join(BM, "tronco_hielo_horizontal.json"), {"parent": "minecraft:block/cube_column_horizontal",
                                                                  "textures": {"end": T("tronco_hielo_top"), "side": T("tronco_hielo")}})
    save_json(os.path.join(BS, "tronco_hielo.json"), {"variants": {
        "axis=y": {"model": R + "block/tronco_hielo"},
        "axis=z": {"model": R + "block/tronco_hielo_horizontal", "x": 90},
        "axis=x": {"model": R + "block/tronco_hielo_horizontal", "x": 90, "y": 90}}})
    save_json(os.path.join(IM, "tronco_hielo.json"), {"parent": R + "block/tronco_hielo"})


def lang():
    for code in ("es_es", "es_cl", "es_mx", "es_ar", "en_us"):
        p = os.path.join(ASSETS, "lang", code + ".json")
        d = json.load(open(p, encoding="utf-8"))
        for k, (es, en) in NAMES.items():
            d["block.%s.%s" % (MODID, k)] = en if code == "en_us" else es
        save_json(p, d)


def loot():
    lt = os.path.join(DATA, "loot_table", "blocks")
    silk = {"condition": "minecraft:match_tool", "predicate": {"predicates": {"minecraft:enchantments": [
        {"enchantments": "minecraft:silk_touch", "levels": {"min": 1}}]}}}
    shears = {"condition": "minecraft:match_tool", "predicate": {"items": "minecraft:shears"}}
    save_json(os.path.join(lt, "pasto_mar_nether.json"), {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{
        "type": "minecraft:alternatives", "children": [
            {"type": "minecraft:item", "name": R + "pasto_mar_nether", "conditions": [silk]},
            {"type": "minecraft:item", "name": M + "netherrack"}]}]}]})
    save_json(os.path.join(lt, "hierba_mar_nether.json"), {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
        {"type": "minecraft:item", "name": R + "hierba_mar_nether", "conditions": [shears]}]}]})
    for n in ("cristal_mar_nether", "carambano_hielo", "tronco_hielo"):
        save_json(os.path.join(lt, n + ".json"), {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
            {"type": "minecraft:item", "name": R + n}], "conditions": [{"condition": "minecraft:survives_explosion"}]}]})


def recipes():
    datagen2.shapeless("pasto_mar_nether", [M + "netherrack", R + "eternal_frost_leaf"], R + "pasto_mar_nether", 1)
    datagen2.shapeless("hierba_mar_nether", [M + "crimson_roots", R + "frost_leaves"], R + "hierba_mar_nether", 2)
    datagen2.shapeless("cristal_mar_nether", [M + "amethyst_shard", M + "glowstone_dust"], R + "cristal_mar_nether", 2)
    datagen2.shapeless("carambano_hielo", [M + "ice", R + "frost_leaves"], R + "carambano_hielo", 3)
    datagen2.shapeless("tronco_hielo", [M + "crimson_stem", R + "frost_leaves"], R + "tronco_hielo", 1)
    datagen2.shapeless("tablas_de_tronco_hielo", [R + "tronco_hielo"], M + "crimson_planks", 4)


def tags():
    datagen2.add_tag("block/mineable/pickaxe", [R + "pasto_mar_nether"])
    datagen2.add_tag("block/mineable/axe", [R + "tronco_hielo"])
    datagen2.add_tag("block/nylium", [R + "pasto_mar_nether"])  # la hierba y los hongos crecen encima
    datagen2.add_tag("block/logs", [R + "tronco_hielo"])        # las hojas no se caen mientras esté el tronco
    datagen2.add_tag("item/logs", [R + "tronco_hielo"])
    datagen2.add_tag("block/replaceable_by_trees", [R + "hierba_mar_nether"])


def write_all():
    textures()
    models()
    lang()
    loot()
    recipes()
    tags()


if __name__ == "__main__":
    write_all()
