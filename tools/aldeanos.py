"""Aldeanos del Nether: los aldeanos vanilla toman el tipo "nether" (como cuando cambian de bioma) y se ven con las skins
hechas a partir del Aldeano Necromancer. Cinco profesiones tienen mesa propia del Nether (cartógrafo, flechero,
peletero, pastor y albañil); las otras usan su mesa vanilla (ahumador, barril, soporte para pociones, alto horno,
mesa de herrería y afiladora).

Escribe: las 5 mesas (texturas, modelos, estados, ítems, botín, crafteos, etiquetas), las skins de los aldeanos con sus
ojos que brillan, las texturas de respaldo de tipo/profesión, los nombres y la etiqueta de camas/sitios de trabajo.
"""
import json
import os

import numpy as np
from PIL import Image

from common import ASSETS, DATA, MCDATA, MODID, save_json
import blocks2 as B
import mesas_aldeanos as MA

HERE = os.path.dirname(os.path.abspath(__file__))
SKINS = os.path.join(HERE, "ref", "aldeanos")
M = "minecraft:"
R = MODID + ":"
VTEX = os.path.join(ASSETS, "textures", "entity", "villager")
ZTEX = os.path.join(ASSETS, "textures", "entity", "zombie_villager")

# profesión del mod -> (skin, mesa, nombre es, nombre en)
MOD_PROFESSIONS = {
    "cartografo": ("cartografo", "cartographer_desk", "Cartógrafo del Nether", "Nether Cartographer"),
    "flechero": ("flechero", "fletcher_bench", "Flechero del Nether", "Nether Fletcher"),
    "peletero": ("peletero", "leather_cauldron", "Peletero del Nether", "Nether Leatherworker"),
    "pastor": ("pastor", "shepherd_loom", "Pastor del Nether", "Nether Shepherd"),
    "albanil": ("albanil", "mason_cutter", "Albañil del Nether", "Nether Mason"),
}
BLOCK_NAMES_EN = {"cartographer_desk": "Cartographer Desk", "fletcher_bench": "Fletcher Bench",
                  "leather_cauldron": "Leatherworker Cauldron", "shepherd_loom": "Shepherd Loom", "mason_cutter": "Mason Stonecutter"}
RECIPES = {
    "cartographer_desk": (["PRP", "CCC", "C C"], {"P": M + "paper", "R": R + "ruby", "C": M + "crimson_planks"}),
    "fletcher_bench": (["FRF", "CCC", "CCC"], {"F": M + "flint", "R": R + "ruby", "C": M + "crimson_planks"}),
    "leather_cauldron": (["B B", "BLB", "BRB"], {"B": M + "polished_blackstone", "L": M + "leather", "R": R + "ruby"}),
    "shepherd_loom": (["SRS", "CWC"], {"S": M + "string", "R": R + "ruby", "C": M + "crimson_planks", "W": M + "red_wool"}),
    "mason_cutter": ([" I ", "BRB"], {"I": M + "iron_ingot", "R": R + "ruby", "B": M + "polished_blackstone"}),
}
AXE = ["cartographer_desk", "fletcher_bench", "shepherd_loom"]
PICKAXE = ["leather_cauldron", "mason_cutter"]
ALL_SKINS = ["aldeano_nether", "carnicero", "pescador", "clerigo", "cartografo", "armero", "herrero_herramientas",
             "herrero_armas", "flechero", "peletero", "pastor", "albanil"]
EYES = [(205, 11, 11), (133, 26, 26), (190, 90, 255), (110, 40, 170)]


def glowmask(skin):
    """Sólo los ojos (rojos o morados) de la cara, para que brillen en la oscuridad como el Aldeano Necromancer."""
    a = np.array(skin.convert("RGBA"))
    out = np.zeros_like(a)
    for y in range(8, 18):
        for x in range(8, 16):
            if a[y, x, 3] and tuple(int(v) for v in a[y, x, :3]) in EYES:
                out[y, x] = a[y, x]
    return Image.fromarray(out, "RGBA"), int((out[..., 3] > 0).sum())


def write_skins():
    os.makedirs(os.path.join(VTEX, "nether"), exist_ok=True)
    counts = {}
    for name in ALL_SKINS:
        skin = Image.open(os.path.join(SKINS, name + ".png")).convert("RGBA")
        skin.save(os.path.join(VTEX, "nether", name + ".png"))
        g, n = glowmask(skin)
        g.save(os.path.join(VTEX, "nether", name + "_glow.png"))
        counts[name] = n
    # respaldo (por si otro mod dibuja los aldeanos con las capas vanilla)
    base = Image.open(os.path.join(SKINS, "aldeano_nether.png")).convert("RGBA")
    empty = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for folder, img in ((VTEX, base), (ZTEX, empty)):
        os.makedirs(os.path.join(folder, "type"), exist_ok=True)
        img.save(os.path.join(folder, "type", "nether.png"))
    for prof, (skin, *_r) in MOD_PROFESSIONS.items():
        os.makedirs(os.path.join(VTEX, "profession"), exist_ok=True)
        os.makedirs(os.path.join(ZTEX, "profession"), exist_ok=True)
        Image.open(os.path.join(SKINS, skin + ".png")).convert("RGBA").save(os.path.join(VTEX, "profession", prof + ".png"))
        empty.save(os.path.join(ZTEX, "profession", prof + ".png"))
    return counts


def write_stations():
    bm = os.path.join(B.MODELS, "block")
    im = os.path.join(B.MODELS, "item")
    for k, fn in MA.TEX.items():
        B.save_png(B.tex(fn), B.BLOCK_TEX, k)
    models, texsets = MA.models()
    for name, elements in models.items():
        tx = {k: B.T(v) for k, v in texsets[name].items()}
        tx["particle"] = tx[list(tx)[0]]
        save_json(os.path.join(bm, name + ".json"), {"parent": "minecraft:block/block", "render_type": "minecraft:cutout",
                                                     "textures": tx, "elements": elements})
        save_json(os.path.join(ASSETS, "blockstates", name + ".json"), B.facing_blockstate(name))
        save_json(os.path.join(im, name + ".json"), {"parent": "%s:block/%s" % (MODID, name)})
        save_json(os.path.join(DATA, "loot_table", "blocks", name + ".json"), {
            "type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": R + name}],
                                                   "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
        pat, key = RECIPES[name]
        save_json(os.path.join(DATA, "recipe", name + ".json"), {
            "type": "minecraft:crafting_shaped", "category": "misc", "pattern": pat,
            "key": {k: {"item": v} for k, v in key.items()}, "result": {"id": R + name, "count": 1}})


def add_tag(path, values):
    p = os.path.join(MCDATA, "tags", path + ".json")
    d = {"replace": False, "values": []}
    if os.path.exists(p):
        d = json.load(open(p))
    for v in values:
        if v not in d["values"]:
            d["values"].append(v)
    save_json(p, d)


def write_tags():
    add_tag("block/mineable/axe", [R + n for n in AXE])
    add_tag("block/mineable/pickaxe", [R + n for n in PICKAXE])
    # las 5 mesas nuevas son sitios de trabajo que los aldeanos sin oficio pueden tomar
    add_tag("point_of_interest_type/acquirable_job_site", [R + st for (_s, st, _a, _b) in MOD_PROFESSIONS.values()])
    # la cama del Nether cuenta como cama para los aldeanos (para dormir y tener hijos)
    add_tag("block/beds", [R + "nether_bed"])


def write_lang():
    for code in ("es_es", "es_cl", "es_mx", "es_ar", "en_us"):
        p = os.path.join(ASSETS, "lang", code + ".json")
        d = json.load(open(p, encoding="utf-8"))
        en = code == "en_us"
        for prof, (_skin, station, es, eng) in MOD_PROFESSIONS.items():
            d["entity.minecraft.villager.%s.%s" % (MODID, prof)] = eng if en else es
            d["block.%s.%s" % (MODID, station)] = BLOCK_NAMES_EN[station] if en else MA.NAMES[station]
        d["villager_type.%s.nether" % MODID] = "Nether" if en else "del Nether"
        save_json(p, d)


def write_all():
    write_stations()
    counts = write_skins()
    write_tags()
    write_lang()
    return counts


if __name__ == "__main__":
    print(write_all())
