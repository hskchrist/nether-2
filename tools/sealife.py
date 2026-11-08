"""Fauna del Mar del Nether (12 criaturas) y Dragón Infernal: modelos, texturas, animaciones, nombres, ítems,
crafteos, botín, etiquetas, apariciones y el nido del Dragón Infernal en el Bosque Carmesí.

Los modelos y texturas de las criaturas están en tools/ref/sea (los que vio y aprobó el usuario);
tools/fauna.py, fauna_hd.py, fauna_hd2.py, fauna_hd3.py (peces, anguila, medusa, cangrejo y caballito HD), delfin.py y ballena.py son los scripts con que se hicieron.
"""
import json
import os
import shutil

from common import ASSETS, DATA, MCDATA, MODID, save_json
import infernal
import sea_icons

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref", "sea")
M = "minecraft:"
R = MODID + ":"

# id: (nombre es, nombre en, color del huevo de fondo, color de las pintas)
CREATURES = {
    "pez_brasa": ("Pez Brasa", "Ember Fish", 0x3A0A06, 0xFF8A1A),
    "pez_alma": ("Pez Alma", "Soul Fish", 0x10263A, 0x7AE6FF),
    "anguila_rubi": ("Anguila de Rubí", "Ruby Eel", 0x2A0610, 0xE0283C),
    "medusa_vacio": ("Medusa del Vacío", "Void Jellyfish", 0x1C0838, 0xB070FF),
    "cangrejo_basalto": ("Cangrejo de Basalto", "Basalt Crab", 0x2B2B31, 0xFF7A1A),
    "caballito_magma": ("Caballito de Magma", "Magma Seahorse", 0x5A1408, 0xFFB347),
    "manta_carmesi": ("Manta Carmesí", "Crimson Manta", 0x5A0A1E, 0xFF4A6A),
    "tortuga_obsidiana": ("Tortuga Obsidiana", "Obsidian Turtle", 0x0C0614, 0x8A5CD0),
    "tiburon_infernal": ("Tiburón Infernal", "Infernal Shark", 0x1A1418, 0xFF3A1A),
    "serpiente_marina": ("Serpiente Marina del Nether", "Nether Sea Serpent", 0x2A0620, 0xFF6AB4),
    "delfin_nether": ("Delfín del Nether", "Nether Dolphin", 0x3B1F5C, 0xE8C8FF),
    "ballena_azul": ("Ballena Azul del Nether", "Nether Blue Whale", 0x1E2E5A, 0x9AB8FF),
}
INFERNAL = ("Dragón Infernal", "Infernal Dragon", 0x2A0A04, 0xFF7A1A)

ITEMS = {
    "pez_brasa": ("Pez Brasa", "Ember Fish"),
    "cooked_pez_brasa": ("Pez Brasa asado", "Cooked Ember Fish"),
    "dientes_tiburon": ("Dientes de Tiburón", "Shark Teeth"),
    "escama_serpiente": ("Escama de Serpiente", "Serpent Scale"),
    "void_gel": ("Gel del Vacío", "Void Gel"),
    "basalt_shell": ("Caparazón de Basalto", "Basalt Shell"),
    "obsidian_scale": ("Escama Obsidiana", "Obsidian Scale"),
    "obsidian_turtle_helmet": ("Casco de Tortuga Obsidiana", "Obsidian Turtle Helmet"),
    "serpent_helmet": ("Casco de la Serpiente", "Serpent Helmet"),
    "ruby_trident": ("Tridente de Rubí", "Ruby Trident"),
    "infernal_dragon_egg": ("Huevo de Dragón Infernal", "Infernal Dragon Egg"),
}
MESSAGES = {
    "entity.civilizacion_nether.dragon_infernal": INFERNAL[:2],
    "item.civilizacion_nether.dragon_infernal_spawn_egg": ("Huevo de generación de Dragón Infernal", "Infernal Dragon Spawn Egg"),
    "entity.civilizacion_nether.dragon_infernal_domesticable": ("Dragón Infernal Domesticable", "Tameable Infernal Dragon"),
    "item.civilizacion_nether.dragon_infernal_domesticable_spawn_egg": ("Huevo de generación de Dragón Infernal Domesticable",
                                                                         "Tameable Infernal Dragon Spawn Egg"),
    "msg.civilizacion_nether.grab_cooldown": ("Tu dragón todavía no puede volver a agarrar", "Your dragon can't grab again yet"),
    "key.civilizacion_nether.dragon_grab": ("Dragón: agarrar / lanzar", "Dragon: grab / throw"),
    "tooltip.civilizacion_nether.cooked_pez_brasa": ("Da resistencia al fuego por 30 segundos", "Grants fire resistance for 30 seconds"),
    "tooltip.civilizacion_nether.obsidian_turtle_helmet": ("Puedes respirar bajo el agua", "Lets you breathe underwater"),
    "tooltip.civilizacion_nether.serpent_helmet": ("Respiras y ves bajo el agua, y nadas más rápido",
                                                   "Breathe and see underwater, and swim faster"),
    "tooltip.civilizacion_nether.ruby_trident": ("Como el tridente normal; lanzado va en llamas y quema", "Like a trident; flies on fire and burns what it hits"),
    "tooltip.civilizacion_nether.infernal_dragon_egg": ("La cría será un Dragón Infernal Domesticable y será tuya", "The hatchling will be your Tameable Infernal Dragon"),
    "msg.civilizacion_nether.seahorse_tamed": ("¡El Caballito de Magma ahora te sigue!", "The Magma Seahorse follows you now!"),
    "msg.civilizacion_nether.manta_saddle": ("Ponle una silla para montarla", "Put a saddle on it to ride it"),
    "msg.civilizacion_nether.nest_robbed": ("¡El Dragón Infernal te vio robar su huevo!", "The Infernal Dragon saw you steal its egg!"),
    "msg.civilizacion_nether.grab_hint": ("G (o R en el Infernal): lanzar lo que llevas agarrado", "G (or R on the Infernal): throw what you carry"),
    "msg.civilizacion_nether.nothing_to_grab": ("No hay nada que agarrar adelante", "Nothing to grab in front of you"),
}

# loot: id -> lista de pools (ítem, mín, máx, probabilidad)
S = R + "soul"
LOOT = {
    "pez_brasa": [(R + "pez_brasa", 1, 1, None), (M + "bone_meal", 1, 1, 0.05), (S, 1, 1, 0.1)],
    "pez_alma": [(S, 1, 1, 0.4), (M + "bone_meal", 1, 1, 0.1)],
    "anguila_rubi": [(R + "ruby", 1, 1, 0.3), (S, 1, 1, 0.15)],
    "medusa_vacio": [(R + "void_gel", 1, 2, None), (S, 1, 1, 0.2)],
    "cangrejo_basalto": [(R + "basalt_shell", 1, 1, None), (M + "basalt", 0, 1, None), (S, 1, 1, 0.2)],
    "caballito_magma": [(M + "magma_cream", 0, 1, None), (S, 1, 1, 0.2)],
    "manta_carmesi": [(M + "leather", 0, 2, None), (S, 1, 1, None)],
    "tortuga_obsidiana": [(R + "obsidian_scale", 1, 2, None), (S, 1, 1, None)],
    "tiburon_infernal": [(R + "dientes_tiburon", 1, 3, None), (R + "pez_brasa", 0, 2, None), (S, 1, 1, None)],
    "serpiente_marina": [(R + "escama_serpiente", 4, 7, None), (S, 2, 4, None), (M + "heart_of_the_sea", 1, 1, 0.5)],
    "delfin_nether": [(R + "pez_brasa", 0, 1, None), (S, 1, 1, None)],
    "ballena_azul": [(M + "heart_of_the_sea", 1, 1, 0.25), (R + "pez_brasa", 3, 8, None), (M + "cod", 2, 5, None), (S, 1, 2, None)],
    "dragon_infernal": [(S, 2, 4, None), (M + "magma_cream", 1, 3, None), (M + "blaze_rod", 0, 2, None)],
    "dragon_infernal_domesticable": [(S, 2, 4, None), (M + "magma_cream", 1, 3, None), (M + "blaze_rod", 0, 2, None)],
}

# apariciones en el Mar del Nether: categoría -> [(id, peso, mín, máx)]
SPAWNS = {
    "water_ambient": [("pez_brasa", 15, 3, 6), ("pez_alma", 8, 2, 4), ("anguila_rubi", 3, 1, 1), ("medusa_vacio", 6, 1, 3)],
    # grupos (las crías se agregan al aparecer, ver SeaFamily.java): delfines de 3 a 5 (+2 crías, más comunes),
    # 2 mantas (+1 cría), caballito solo (+4 crías), ballena sola (rara vez con cría)
    "water_creature": [("delfin_nether", 9, 3, 5), ("ballena_azul", 1, 1, 1), ("manta_carmesi", 3, 2, 2),
                       ("tortuga_obsidiana", 3, 1, 2), ("caballito_magma", 3, 1, 1), ("cangrejo_basalto", 5, 1, 3)],
    # tiburón: menos, y solo (a veces con una cría)
    "monster": [("tiburon_infernal", 3, 1, 1), ("serpiente_marina", 1, 1, 1)],
}

RECIPES = {
    # Tridente de Rubí: dientes de tiburón, prismarina y rubí (lo pidió el usuario)
    "ruby_trident": (["DRD", " P ", " P "], {"D": R + "dientes_tiburon", "R": R + "ruby", "P": M + "prismarine_shard"}, R + "ruby_trident"),
    "obsidian_turtle_helmet": (["SSS", "S S"], {"S": R + "obsidian_scale"}, R + "obsidian_turtle_helmet"),
    "serpent_helmet": (["EEE", "EHE"], {"E": R + "escama_serpiente", "H": R + "obsidian_turtle_helmet"}, R + "serpent_helmet"),
    "infernal_dragon_egg": (["MFM", "FEF", "MFM"], {"M": M + "magma_block", "F": M + "fire_charge", "E": R + "dragon_egg"},
                            R + "infernal_dragon_egg"),
}


def copy_models():
    geo = os.path.join(ASSETS, "geo", "entity")
    ani = os.path.join(ASSETS, "animations", "entity")
    tex = os.path.join(ASSETS, "textures", "entity")
    for n in CREATURES:
        shutil.copy(os.path.join(REF, n + ".geo.json"), os.path.join(geo, n + ".geo.json"))
        shutil.copy(os.path.join(REF, n + ".animation.json"), os.path.join(ani, n + ".animation.json"))
        shutil.copy(os.path.join(REF, n + ".png"), os.path.join(tex, n + ".png"))
        g = os.path.join(REF, n + "_glowmask.png")
        if os.path.exists(g):
            shutil.copy(g, os.path.join(tex, n + "_glowmask.png"))
    item = os.path.join(ASSETS, "textures", "item")
    for n in ("dientes_tiburon", "escama_serpiente"):
        shutil.copy(os.path.join(REF, n + ".png"), os.path.join(item, n + ".png"))
    shutil.copy(os.path.join(REF, "tridente_rubi.png"), os.path.join(item, "ruby_trident.png"))


def lang():
    for code in ("es_es", "es_cl", "es_mx", "es_ar", "en_us"):
        p = os.path.join(ASSETS, "lang", code + ".json")
        d = json.load(open(p, encoding="utf-8"))
        en = code == "en_us"
        for k, (a, b, _, _) in CREATURES.items():
            d["entity.%s.%s" % (MODID, k)] = b if en else a
            d["item.%s.%s_spawn_egg" % (MODID, k)] = ("%s Spawn Egg" % b) if en else ("Huevo de generación de %s" % a)
        for k, (a, b) in ITEMS.items():
            d["item.%s.%s" % (MODID, k)] = b if en else a
        for k, (a, b) in MESSAGES.items():
            d[k] = b if en else a
        save_json(p, d)


def item_models():
    im = os.path.join(ASSETS, "models", "item")
    for k in ITEMS:
        if k == "ruby_trident":
            continue
        save_json(os.path.join(im, k + ".json"), {"parent": "minecraft:item/generated", "textures": {"layer0": R + "item/" + k}})
    # Tridente de Rubí: en la mano es el modelo 3D rojo (como el tridente vanilla); en el inventario, el suelo y los
    # marcos se ve el dibujo 32x32 del usuario (RubyTridentItemRenderer elige cuál)
    ident = {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]}
    hand = {"thirdperson_righthand": {"rotation": [0, 60, 0], "translation": [11, 17, -2], "scale": [1, 1, 1]},
            "thirdperson_lefthand": {"rotation": [0, 60, 0], "translation": [3, 17, 12], "scale": [1, 1, 1]},
            "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [-3, 17, 1], "scale": [1, 1, 1]},
            "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [13, 17, 1], "scale": [1, 1, 1]},
            "gui": ident, "ground": ident, "fixed": ident, "head": ident}
    throw = dict(hand)
    throw.update({"thirdperson_righthand": {"rotation": [0, 90, 180], "translation": [8, -11, -0.5], "scale": [1, 1, 1]},
                  "thirdperson_lefthand": {"rotation": [0, 90, 180], "translation": [8, -11, 0.5], "scale": [1, 1, 1]}})
    save_json(os.path.join(im, "ruby_trident.json"), {
        "parent": "minecraft:builtin/entity", "gui_light": "front", "textures": {"particle": R + "item/ruby_trident"},
        "display": hand, "overrides": [{"predicate": {"minecraft:throwing": 1}, "model": R + "item/ruby_trident_throwing"}]})
    save_json(os.path.join(im, "ruby_trident_throwing.json"), {
        "parent": "minecraft:builtin/entity", "gui_light": "front", "textures": {"particle": R + "item/ruby_trident"},
        "display": throw})
    save_json(os.path.join(im, "ruby_trident_inventory.json"), {
        "parent": "minecraft:item/generated", "textures": {"layer0": R + "item/ruby_trident"}})
    for k in list(CREATURES) + ["dragon_infernal", "dragon_infernal_domesticable"]:
        save_json(os.path.join(im, k + "_spawn_egg.json"), {"parent": "minecraft:item/template_spawn_egg"})


def recipes():
    import datagen2
    for name, (pat, key, res) in RECIPES.items():
        datagen2.shaped(name, pat, key, res, 1, "equipment" if "helmet" in name or "trident" in name else "misc")
    for kind, suffix, time in (("smelting", "", 200), ("smoking", "_from_smoking", 100), ("campfire_cooking", "_from_campfire", 600)):
        save_json(os.path.join(DATA, "recipe", "cooked_pez_brasa" + suffix + ".json"), {
            "type": M + kind, "category": "food", "cookingtime": time, "experience": 0.35,
            "ingredient": {"item": R + "pez_brasa"}, "result": {"id": R + "cooked_pez_brasa"}})


def loot():
    for name, pools in LOOT.items():
        out = []
        for itm, lo, hi, chance in pools:
            p = {"rolls": 1, "entries": [{"type": "minecraft:item", "name": itm, "functions": [
                {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]}]}
            if chance:
                p["conditions"] = [{"condition": "minecraft:random_chance", "chance": chance}]
            out.append(p)
        save_json(os.path.join(DATA, "loot_table", "entities", name + ".json"), {"type": "minecraft:entity", "pools": out})


def tags():
    import datagen2
    # el agua del Nether es agua: los peces respiran y nadan, los delfines la siguen, se puede pescar y hidrata la tierra
    datagen2.add_tag("fluid/water", [R + "nether_water", R + "flowing_nether_water"])
    # los delfines comen Pez Brasa y te guían hasta el Reino Humano
    datagen2.add_tag("item/fishes", [R + "pez_brasa", R + "cooked_pez_brasa"])
    datagen2.add_tag("worldgen/structure/dolphin_located", [R + "capital"])
    datagen2.add_tag("item/head_armor", [R + "obsidian_turtle_helmet", R + "serpent_helmet"])
    datagen2.add_tag("item/enchantable/trident", [R + "ruby_trident"])
    datagen2.add_tag("item/enchantable/durability", [R + "ruby_trident"])
    # respiran bajo el agua (NeoForge no deja cambiarlo en el código: va por esta etiqueta)
    datagen2.add_tag("entity_type/can_breathe_under_water", [R + "tortuga_obsidiana", R + "caballito_magma", R + "cangrejo_basalto"])
    # el encantamiento Empalamiento hace más daño a las criaturas del mar
    datagen2.add_tag("entity_type/aquatic", [R + k for k in CREATURES])


def nest():
    wg = os.path.join(DATA, "worldgen")
    save_json(os.path.join(wg, "configured_feature", "nido_infernal.json"), {"type": R + "infernal_nest", "config": {}})
    save_json(os.path.join(wg, "placed_feature", "nido_infernal.json"), {
        "feature": R + "nido_infernal", "placement": [
            {"type": "minecraft:rarity_filter", "chance": 36}, {"type": "minecraft:in_square"},
            {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform", "min_inclusive": {"absolute": 40},
                                                           "max_inclusive": {"absolute": 100}}},
            {"type": "minecraft:biome"}]})
    save_json(os.path.join(DATA, "neoforge", "biome_modifier", "nido_infernal.json"), {
        "type": "neoforge:add_features", "biomes": "minecraft:crimson_forest", "features": R + "nido_infernal",
        "step": "surface_structures"})


REF_INFERNAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref", "infernal")


def tame_infernal_skin():
    """Skin del Dragón Infernal domesticable: la del usuario si la mandó (ref/infernal/dragon_infernal_domesticable.png);
    si no, por ahora la misma del salvaje."""
    ent = os.path.join(ASSETS, "textures", "entity")
    for suf in ("", "_glowmask"):
        own = os.path.join(REF_INFERNAL, "dragon_infernal_domesticable%s.png" % suf)
        src = own if os.path.exists(own) else os.path.join(ent, "dragon_infernal%s.png" % suf)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(ent, "dragon_infernal_domesticable%s.png" % suf))


def write_all():
    copy_models()
    infernal.write_all()
    tame_infernal_skin()
    sea_icons.write_all()
    lang()
    item_models()
    recipes()
    loot()
    tags()
    nest()


if __name__ == "__main__":
    write_all()
