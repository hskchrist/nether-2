"""Dragón de Almas (azul) y Dragón de Obsidiana (morado): las dos especies nuevas con el modelo del Dragón Infernal.

Las skins son las del usuario (tools/ref/infernal/dragon_almas.png y dragon_obsidiana.png, sacadas de sus glTF; no se
toca ni un píxel). Las partes que brillan usan las mismas zonas que el Dragón Infernal. Los huevos y las bolas de fuego
de cada especie son los del Infernal con el color cambiado (azul y morado).

También escribe: nombres, huevos de generación, botín, crafteos de los huevos, apariciones por bioma y los nidos.
Biomas:
  Infernal:  nido en el Bosque Carmesí; también en los Páramos del Nether.
  Almas:     nido en el Valle de Arena de Almas; también en el Bosque Distorsionado.
  Obsidiana: nido en los Deltas de Basalto; también en el Océano Púrpura.
  Páramos del Nether: aparecen las tres especies salvajes, y a veces ya peleando (InfernalDragonEntity.naturalState).
"""
import json
import os
import shutil

import numpy as np
from PIL import Image

from common import ASSETS, DATA, MODID, save_json

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref", "infernal")
M = "minecraft:"
R = MODID + ":"
TEX = os.path.join(ASSETS, "textures")

# especie: (nombre es, nombre en, giro de tono en grados desde el naranjo del Infernal)
SPECIES = {
    "almas": ("Dragón de Almas", "Soul Dragon", 192),
    "obsidiana": ("Dragón de Obsidiana", "Obsidian Dragon", 255),
}
SPAWN_EGG = {
    "dragon_almas": "dragon_almas", "dragon_almas_domesticable": "dragon_almas",
    "dragon_obsidiana": "dragon_obsidiana", "dragon_obsidiana_domesticable": "dragon_obsidiana",
}

S = R + "soul"
LOOT = {
    "almas": [(S, 3, 5, None), (M + "soul_soil", 1, 3, None), (M + "blaze_rod", 0, 2, None)],
    "obsidiana": [(S, 2, 4, None), (M + "crying_obsidian", 1, 3, None), (M + "obsidian", 1, 2, None), (M + "blaze_rod", 0, 2, None)],
}

RECIPES = {
    "almas_dragon_egg": (["SFS", "FEF", "SFS"], {"S": M + "soul_soil", "F": M + "soul_lantern", "E": R + "dragon_egg"}),
    "obsidiana_dragon_egg": (["OCO", "CEC", "OCO"], {"O": M + "obsidian", "C": M + "crying_obsidian", "E": R + "dragon_egg"}),
}

# apariciones naturales (categoría creature): bioma -> [(tipo, peso, mín, máx)]
SPAWNS = {
    "dragones_infernal": (["minecraft:crimson_forest"], [("dragon_infernal", 2, 1, 1), ("dragon_infernal_domesticable", 1, 1, 1)]),
    "dragones_almas": (["minecraft:soul_sand_valley", "minecraft:warped_forest"],
                       [("dragon_almas", 2, 1, 1), ("dragon_almas_domesticable", 1, 1, 1)]),
    "dragones_obsidiana": (["minecraft:basalt_deltas", R + "oceano_purpura"],
                           [("dragon_obsidiana", 2, 1, 1), ("dragon_obsidiana_domesticable", 1, 1, 1)]),
    # campo de batalla: las tres especies salvajes juntas
    "dragones_batalla": (["minecraft:nether_wastes"], [("dragon_infernal", 1, 1, 1), ("dragon_almas", 1, 1, 1),
                                                       ("dragon_obsidiana", 1, 1, 1)]),
}
NESTS = {"almas": ("almas_nest", "minecraft:soul_sand_valley"), "obsidiana": ("obsidiana_nest", "minecraft:basalt_deltas")}


def hue_shift(src, dst, degrees):
    """Copia src cambiando el tono (mantiene brillo, saturación y transparencia)."""
    im = Image.open(src).convert("RGBA")
    a = np.array(im)
    alpha = a[..., 3].copy()
    hsv = np.array(Image.fromarray(a[..., :3], "RGB").convert("HSV")).astype(np.int32)
    hsv[..., 0] = (hsv[..., 0] + int(round(degrees / 360.0 * 256))) % 256
    rgb = np.array(Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB"))
    out = np.dstack([rgb, alpha])
    Image.fromarray(out.astype(np.uint8), "RGBA").save(dst)


def textures():
    ent = os.path.join(TEX, "entity")
    item = os.path.join(TEX, "item")
    for sp in SPECIES:
        for suf in ("", "_glowmask"):
            src = os.path.join(REF, "dragon_%s%s.png" % (sp, suf))
            if os.path.exists(src):
                shutil.copy(src, os.path.join(ent, "dragon_%s%s.png" % (sp, suf)))
        deg = SPECIES[sp][2]
        hue_shift(os.path.join(ent, "infernal_dragon_egg.png"), os.path.join(ent, "%s_dragon_egg.png" % sp), deg)
        g = os.path.join(ent, "infernal_dragon_egg_glowmask.png")
        if os.path.exists(g):
            hue_shift(g, os.path.join(ent, "%s_dragon_egg_glowmask.png" % sp), deg)
        hue_shift(os.path.join(ent, "infernal_fireball.png"), os.path.join(ent, "%s_fireball.png" % sp), deg)
        hue_shift(os.path.join(item, "infernal_dragon_egg.png"), os.path.join(item, "%s_dragon_egg.png" % sp), deg)


def lang():
    for code in ("es_es", "es_cl", "es_mx", "es_ar", "en_us"):
        p = os.path.join(ASSETS, "lang", code + ".json")
        d = json.load(open(p, encoding="utf-8"))
        en = code == "en_us"
        for sp, (es, eng, _) in SPECIES.items():
            n = eng if en else es
            tn = ("Tameable " + eng) if en else (es + " Domesticable")
            d["entity.%s.dragon_%s" % (MODID, sp)] = n
            d["entity.%s.dragon_%s_domesticable" % (MODID, sp)] = tn
            d["item.%s.dragon_%s_spawn_egg" % (MODID, sp)] = ("%s Spawn Egg" % n) if en else ("Huevo de generación de %s" % n)
            d["item.%s.dragon_%s_domesticable_spawn_egg" % (MODID, sp)] = ("%s Spawn Egg" % tn) if en else ("Huevo de generación de %s" % tn)
            egg = ("%s Egg" % eng) if en else ("Huevo de " + es)
            d["item.%s.%s_dragon_egg" % (MODID, sp)] = egg
            d["tooltip.%s.%s_dragon_egg" % (MODID, sp)] = (
                "The hatchling will be your %s" % tn) if en else ("La cría será un %s y será tuya" % tn)
        d["msg.%s.nest_robbed" % MODID] = "The dragon saw you steal its egg!" if en else "¡El dragón te vio robar su huevo!"
        save_json(p, d)


def models():
    im = os.path.join(ASSETS, "models", "item")
    for sp in SPECIES:
        save_json(os.path.join(im, "%s_dragon_egg.json" % sp), {"parent": "minecraft:item/generated",
                                                               "textures": {"layer0": R + "item/%s_dragon_egg" % sp}})
    for k in SPAWN_EGG:
        save_json(os.path.join(im, k + "_spawn_egg.json"), {"parent": "minecraft:item/template_spawn_egg"})


def recipes():
    import datagen2
    for name, (pat, key) in RECIPES.items():
        datagen2.shaped(name, pat, key, R + name, 1, "misc")


def loot():
    for sp, pools in LOOT.items():
        out = []
        for itm, lo, hi, chance in pools:
            p = {"rolls": 1, "entries": [{"type": "minecraft:item", "name": itm, "functions": [
                {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]}]}
            if chance:
                p["conditions"] = [{"condition": "minecraft:random_chance", "chance": chance}]
            out.append(p)
        for name in ("dragon_" + sp, "dragon_%s_domesticable" % sp):
            save_json(os.path.join(DATA, "loot_table", "entities", name + ".json"), {"type": "minecraft:entity", "pools": out})


def worldgen():
    bm = os.path.join(DATA, "neoforge", "biome_modifier")
    for name, (biomes, spawners) in SPAWNS.items():
        save_json(os.path.join(bm, name + ".json"), {
            "type": "neoforge:add_spawns", "biomes": biomes if len(biomes) > 1 else biomes[0],
            "spawners": [{"type": R + t, "weight": w, "minCount": lo, "maxCount": hi} for t, w, lo, hi in spawners]})
    wg = os.path.join(DATA, "worldgen")
    for sp, (feature, biome) in NESTS.items():
        nid = "nido_" + sp
        save_json(os.path.join(wg, "configured_feature", nid + ".json"), {"type": R + feature, "config": {}})
        save_json(os.path.join(wg, "placed_feature", nid + ".json"), {
            "feature": R + nid, "placement": [
                {"type": "minecraft:rarity_filter", "chance": 36}, {"type": "minecraft:in_square"},
                {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform", "min_inclusive": {"absolute": 32},
                                                               "max_inclusive": {"absolute": 100}}},
                {"type": "minecraft:biome"}]})
        save_json(os.path.join(bm, nid + ".json"), {
            "type": "neoforge:add_features", "biomes": biome, "features": R + nid, "step": "surface_structures"})


def write_all():
    textures()
    lang()
    models()
    recipes()
    loot()
    worldgen()


if __name__ == "__main__":
    write_all()
