"""Datos y recursos de la actualización del Reino Humano del Nether:
nombres, modelos de ítems, crafteos, botín, etiquetas, sonidos (voces del usuario), bioma Mar del Nether,
árbol de hielo de Picos de Hielo y el reino nuevo.
"""
import json
import os
import shutil
import subprocess
from common import ASSETS, DATA, MCDATA, MODID, RES, save_json

HERE = os.path.dirname(os.path.abspath(__file__))
M = "minecraft:"
R = MODID + ":"

NEW_ITEMS = {
    "ruby_longsword": ("Espada larga de rubí", "Ruby Longsword"),
    "ruby_crossbow": ("Ballesta de rubí", "Ruby Crossbow"),
    "human_helmet": ("Casco humano del Nether", "Nether Human Helmet"),
    "human_chestplate": ("Pechera humana del Nether", "Nether Human Chestplate"),
    "human_leggings": ("Grebas humanas del Nether", "Nether Human Leggings"),
    "human_boots": ("Botas humanas del Nether", "Nether Human Boots"),
    "frost_helmet": ("Casco del Frío Eterno", "Eternal Frost Helmet"),
    "frost_chestplate": ("Pechera del Frío Eterno", "Eternal Frost Chestplate"),
    "frost_leggings": ("Pantalones del Frío Eterno", "Eternal Frost Leggings"),
    "frost_boots": ("Botas del Frío Eterno", "Eternal Frost Boots"),
    "eternal_frost_leaf": ("Hoja del Frío Eterno", "Eternal Frost Leaf"),
    "nether_water_bucket": ("Balde de agua del Nether", "Nether Water Bucket"),
}
NEW_BLOCKS = {
    "necromancer_table": ("Mesa del Aldeano Necromancer", "Necromancer Villager Table"),
    "librarian_lectern": ("Atril del Bibliotecario", "Librarian Lectern"),
    "tamer_nest": ("Nido del Domador", "Tamer Nest"),
    "farmer_basket": ("Cesto del Granjero", "Farmer Basket"),
    "miner_cart": ("Carrito del Minero", "Miner Cart"),
    "nether_bed": ("Cama del Nether", "Nether Bed"),
    "nether_water": ("Agua del Nether", "Nether Water"),
    "frost_leaves": ("Hojas del Árbol de Hielo", "Frost Tree Leaves"),
}
MESSAGES = {
    "msg.civilizacion_nether.need_beds": ("Para tener un hijo necesitan camas del Nether libres cerca.",
                                          "They need free Nether beds nearby to have a child."),
    "msg.civilizacion_nether.bed_spawn": ("Te acostaste en la cama del Nether: tu punto de reaparición quedó guardado.",
                                          "You lay down in the Nether bed: your respawn point is saved."),
    "biome.civilizacion_nether.mar_del_nether": ("Mar del Nether", "Nether Sea"),
    "subtitles.civilizacion_nether.human.hurt": ("Humano herido", "Human hurts"),
    "fluid_type.civilizacion_nether.nether_water": ("Agua del Nether", "Nether Water"),
}


def lang():
    for code in ("es_es", "es_cl", "es_mx", "es_ar", "en_us"):
        p = os.path.join(ASSETS, "lang", code + ".json")
        d = json.load(open(p, encoding="utf-8"))
        en = code == "en_us"
        for k, (a, b) in NEW_ITEMS.items():
            d["item.%s.%s" % (MODID, k)] = b if en else a
        for k, (a, b) in NEW_BLOCKS.items():
            d["block.%s.%s" % (MODID, k)] = b if en else a
        for k, (a, b) in MESSAGES.items():
            d[k] = b if en else a
        save_json(p, d)


# ---------------------------------------------------------------- modelos de ítem de las armas nuevas
def item_models():
    import weapons
    weapons.write(os.path.join(ASSETS, "textures", "item"))
    im = os.path.join(ASSETS, "models", "item")
    save_json(os.path.join(im, "ruby_longsword.json"), {"parent": "minecraft:item/handheld",
                                                         "textures": {"layer0": R + "item/ruby_longsword"}})
    states = ["pulling_0", "pulling_1", "pulling_2", "arrow", "firework"]
    for st in states:
        save_json(os.path.join(im, "ruby_crossbow_%s.json" % st), {"parent": "minecraft:item/crossbow",
                                                                   "textures": {"layer0": R + "item/ruby_crossbow_%s" % st}})
    save_json(os.path.join(im, "ruby_crossbow.json"), {
        "parent": "minecraft:item/crossbow", "textures": {"layer0": R + "item/ruby_crossbow_standby"},
        "overrides": [
            {"predicate": {"pulling": 1}, "model": R + "item/ruby_crossbow_pulling_0"},
            {"predicate": {"pulling": 1, "pull": 0.58}, "model": R + "item/ruby_crossbow_pulling_1"},
            {"predicate": {"pulling": 1, "pull": 1.0}, "model": R + "item/ruby_crossbow_pulling_2"},
            {"predicate": {"charged": 1}, "model": R + "item/ruby_crossbow_arrow"},
        ]})


# ---------------------------------------------------------------- crafteos
def shaped(name, pattern, key, result, count=1, cat="misc"):
    keys = {}
    for k, v in key.items():
        keys[k] = {"tag": v[1:]} if v.startswith("#") else {"item": v}
    save_json(os.path.join(DATA, "recipe", name + ".json"), {
        "type": "minecraft:crafting_shaped", "category": cat, "pattern": pattern, "key": keys,
        "result": {"id": result, "count": count}})


def shapeless(name, items, result, count=1, cat="misc"):
    save_json(os.path.join(DATA, "recipe", name + ".json"), {
        "type": "minecraft:crafting_shapeless", "category": cat,
        "ingredients": [{"tag": i[1:]} if i.startswith("#") else {"item": i} for i in items],
        "result": {"id": result, "count": count}})


RECIPES = {
    # mesa del Aldeano Necromancer: madera en las esquinas (cualquier tabla) y almas en el resto (pedido del usuario)
    "necromancer_table": (["WAW", "AAA", "WAW"], {"W": "#minecraft:planks", "A": R + "soul"}, R + "necromancer_table", 1),
    "librarian_lectern": (["CKC", " P ", "PPP"], {"C": M + "crimson_planks", "K": M + "book", "P": M + "polished_blackstone"}, R + "librarian_lectern", 1),
    "tamer_nest": (["RAR", "B B", "BBB"], {"R": M + "crimson_roots", "A": R + "soul", "B": M + "basalt"}, R + "tamer_nest", 1),
    "farmer_basket": (["WFW", "P P", "PPP"], {"W": M + "nether_wart", "F": M + "crimson_fungus", "P": M + "crimson_planks"}, R + "farmer_basket", 1),
    "miner_cart": (["IRI", "IPI"], {"I": M + "iron_ingot", "R": R + "ruby", "P": M + "iron_pickaxe"}, R + "miner_cart", 1),
    "nether_bed": (["WAW", "CCC"], {"W": M + "purple_wool", "A": R + "soul", "C": M + "crimson_planks"}, R + "nether_bed", 1),
    # armas del Guerrero Real y del Ballestero
    "ruby_longsword": (["  B", "GR ", "SG "], {"B": R + "ruby_block", "R": R + "ruby", "G": M + "gold_ingot", "S": M + "blaze_rod"}, R + "ruby_longsword", 1),
    "ruby_crossbow": (["SRS", "TCT", " S "], {"S": M + "blaze_rod", "R": R + "ruby", "T": M + "string", "C": M + "tripwire_hook"}, R + "ruby_crossbow", 1),
    # Armadura Humana del Nether: rubí y diamante (entre diamante y netherita)
    "human_helmet": (["RDR", "D D"], {"R": R + "ruby", "D": M + "diamond"}, R + "human_helmet", 1),
    "human_chestplate": (["D D", "RDR", "DRD"], {"R": R + "ruby", "D": M + "diamond"}, R + "human_chestplate", 1),
    "human_leggings": (["RDR", "D D", "D D"], {"R": R + "ruby", "D": M + "diamond"}, R + "human_leggings", 1),
    "human_boots": (["R R", "D D"], {"R": R + "ruby", "D": M + "diamond"}, R + "human_boots", 1),
    # Armadura del Frío Eterno: la pechera es la de la lámina del usuario; las otras piezas siguen la misma idea
    "frost_chestplate": (["RRR", "IHI", "III"], {"R": R + "ruby", "I": M + "iron_ingot", "H": R + "eternal_frost_leaf"}, R + "frost_chestplate", 1),
    "frost_helmet": (["RHR", "I I"], {"R": R + "ruby", "I": M + "iron_ingot", "H": R + "eternal_frost_leaf"}, R + "frost_helmet", 1),
    "frost_leggings": (["RHR", "I I", "I I"], {"R": R + "ruby", "I": M + "iron_ingot", "H": R + "eternal_frost_leaf"}, R + "frost_leggings", 1),
    "frost_boots": (["H H", "I I"], {"I": M + "iron_ingot", "H": R + "eternal_frost_leaf"}, R + "frost_boots", 1),
}


def recipes():
    for name, (pat, key, res, n) in RECIPES.items():
        cat = "equipment" if any(w in name for w in ("helmet", "chest", "leggings", "boots", "sword", "crossbow")) else "misc"
        shaped(name, pat, key, res, n, cat)
    shapeless("eternal_frost_leaf", [R + "frost_leaves"], R + "eternal_frost_leaf", 1)
    shapeless("nether_water_bucket", [M + "water_bucket", R + "soul", M + "amethyst_shard"], R + "nether_water_bucket", 1)


# ---------------------------------------------------------------- botín
def pool(itm, lo, hi, chance=None):
    p = {"rolls": 1, "entries": [{"type": "minecraft:item", "name": itm, "functions": [
        {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]}]}
    if chance:
        p["conditions"] = [{"condition": "minecraft:random_chance", "chance": chance}]
    return p


def loot():
    lt = os.path.join(DATA, "loot_table")
    for b in ("necromancer_table", "librarian_lectern", "tamer_nest", "farmer_basket", "miner_cart"):
        save_json(os.path.join(lt, "blocks", b + ".json"), {
            "type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": R + b}],
                                                   "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    save_json(os.path.join(lt, "blocks", "nether_bed.json"), {
        "type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": R + "nether_bed", "conditions": [
            {"condition": "minecraft:block_state_property", "block": R + "nether_bed", "properties": {"part": "head"}}]}],
            "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    shears = {"condition": "minecraft:any_of", "terms": [
        {"condition": "minecraft:match_tool", "predicate": {"items": "minecraft:shears"}},
        {"condition": "minecraft:match_tool", "predicate": {"predicates": {"minecraft:enchantments": [
            {"enchantments": "minecraft:silk_touch", "levels": {"min": 1}}]}}}]}
    save_json(os.path.join(lt, "blocks", "frost_leaves.json"), {
        "type": "minecraft:block", "pools": [
            {"rolls": 1, "entries": [{"type": "minecraft:alternatives", "children": [
                {"type": "minecraft:item", "name": R + "frost_leaves", "conditions": [shears]},
                {"type": "minecraft:item", "name": M + "stick", "conditions": [
                    {"condition": "minecraft:random_chance", "chance": 0.05}]}]}]}]})
    S = R + "soul"
    ent = {
        "guerrero_real": [pool(R + "ruby", 1, 3), pool(M + "gold_ingot", 1, 2, 0.5), pool(S, 1, 1)],
        "ballestero": [pool(R + "ruby", 0, 1), pool(M + "arrow", 2, 6), pool(S, 1, 1)],
        "bibliotecario": [pool(M + "paper", 1, 4), pool(M + "book", 0, 1), pool(S, 1, 1)],
        "domador": [pool(M + "leather", 1, 3), pool(R + "ruby", 0, 1), pool(S, 1, 1)],
        "granjero": [pool(M + "nether_wart", 1, 4), pool(M + "bread", 0, 2), pool(S, 1, 1)],
        "minero": [pool(M + "coal", 1, 4), pool(R + "ruby", 0, 1), pool(S, 1, 1)],
        "ciudadano": [pool(M + "bread", 0, 2), pool(S, 1, 1)],
        "aldeano_necromancer": [pool(M + "emerald", 0, 2), pool(S, 1, 1)],
    }
    for name, pools in ent.items():
        save_json(os.path.join(lt, "entities", name + ".json"), {"type": "minecraft:entity", "pools": pools})


# ---------------------------------------------------------------- etiquetas
def add_tag(path, values):
    p = os.path.join(MCDATA, "tags", path + ".json")
    d = {"replace": False, "values": []}
    if os.path.exists(p):
        d = json.load(open(p))
    for v in values:
        if v not in d["values"]:
            d["values"].append(v)
    save_json(p, d)


def tags():
    add_tag("block/mineable/axe", [R + "necromancer_table", R + "farmer_basket", R + "nether_bed"])
    add_tag("block/mineable/pickaxe", [R + "librarian_lectern", R + "miner_cart"])
    add_tag("block/mineable/hoe", [R + "frost_leaves", R + "tamer_nest"])
    add_tag("block/leaves", [R + "frost_leaves"])
    add_tag("item/leaves", [R + "frost_leaves"])
    add_tag("item/swords", [R + "ruby_longsword", R + "ruby_sword"])
    add_tag("item/enchantable/crossbow", [R + "ruby_crossbow"])
    add_tag("item/enchantable/durability", [R + "ruby_crossbow"])
    for p in ("helmet", "chestplate", "leggings", "boots"):
        kind = {"helmet": "head_armor", "chestplate": "chest_armor", "leggings": "leg_armor", "boots": "foot_armor"}[p]
        add_tag("item/" + kind, [R + "human_" + p, R + "frost_" + p, R + "ruby_" + p])
    # el bioma nuevo es parte del Nether (para spawns, la mena de rubí y la música)
    save_json(os.path.join(MCDATA, "tags", "worldgen", "biome", "is_nether.json"), {"replace": False, "values": [R + "mar_del_nether"]})


# ---------------------------------------------------------------- sonidos: voces del usuario
AUDIO_SRC = os.path.join(HERE, "ref", "audio")
VOICES = {  # evento -> lista de (archivo ogg, tono)
    "human.man.hurt": [("hombre_golpe_1", 1.0)],
    "human.boy.hurt": [("nino_golpe_1", 1.0)],
    "human.girl.hurt": [("nina_golpe_1", 1.0)],
    "human.woman.hurt": [("mujer_golpe_1", 1.0)],
}


def sounds():
    out_dir = os.path.join(ASSETS, "sounds", "human")
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(AUDIO_SRC):
        if f.endswith(".ogg"):
            shutil.copy(os.path.join(AUDIO_SRC, f), os.path.join(out_dir, f))
    sj = {}
    for ev, files in VOICES.items():
        sj[ev] = {"subtitle": "subtitles.civilizacion_nether.human.hurt",
                  "sounds": [{"name": R + "human/" + f, "pitch": p} if p != 1.0 else R + "human/" + f for f, p in files]}
    save_json(os.path.join(ASSETS, "sounds.json"), sj)


# ---------------------------------------------------------------- bioma Mar del Nether y árbol de hielo
def sea(category):
    """Fauna marina del Mar del Nether (ver sealife.py)."""
    import sealife
    return [{"type": R + k, "weight": w, "minCount": lo, "maxCount": hi} for k, w, lo, hi in sealife.SPAWNS[category]]


def worldgen():
    wg = os.path.join(DATA, "worldgen")
    # mar púrpura: cambia la lava del bioma por agua del Nether
    save_json(os.path.join(wg, "configured_feature", "mar_purpura.json"), {"type": R + "purple_sea", "config": {}})
    save_json(os.path.join(wg, "placed_feature", "mar_purpura.json"), {"feature": R + "mar_purpura", "placement": []})
    save_json(os.path.join(wg, "configured_feature", "piedra_brillante_purpura.json"), {"type": "minecraft:glowstone_blob", "config": {}})
    save_json(os.path.join(wg, "placed_feature", "piedra_brillante_purpura.json"), {
        "feature": R + "piedra_brillante_purpura", "placement": [
            {"type": "minecraft:count", "count": {"type": "minecraft:biased_to_bottom", "min_inclusive": 0, "max_inclusive": 9}},
            {"type": "minecraft:in_square"},
            {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform", "min_inclusive": {"above_bottom": 4},
                                                           "max_inclusive": {"below_top": 4}}},
            {"type": "minecraft:biome"}]})
    save_json(os.path.join(wg, "configured_feature", "cuarzo_purpura.json"), {
        "type": "minecraft:ore", "config": {"size": 14, "discard_chance_on_air_exposure": 0.0, "targets": [
            {"target": {"predicate_type": "minecraft:block_match", "block": "minecraft:netherrack"},
             "state": {"Name": "minecraft:nether_quartz_ore"}}]}})
    save_json(os.path.join(wg, "placed_feature", "cuarzo_purpura.json"), {
        "feature": R + "cuarzo_purpura", "placement": [
            {"type": "minecraft:count", "count": 16}, {"type": "minecraft:in_square"},
            {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform", "min_inclusive": {"above_bottom": 10},
                                                           "max_inclusive": {"below_top": 10}}},
            {"type": "minecraft:biome"}]})
    feats = [[] for _ in range(11)]
    # el árbol va en el mismo paso que el pasto (antes del Reino, que despeja su terreno: no crecen árboles adentro)
    # lagos y lagunas de agua del Nether, y manantiales que bajan como arroyos y cascadas (los ríos del Nether)
    feats[1] = [R + "mar_purpura", R + "lago_mar_nether", R + "arbol_de_hielo"]
    feats[8] = [R + "manantial_mar_nether", R + "manantial_mar_nether_escondido"]
    feats[6] = [R + "rubi_mar_nether"]  # más rubí en este bioma
    # menas normales del Nether (como en los otros biomas): oro, cuarzo, magma, grava, piedra negra y
    # escombros ancestrales (la netherita), en el mismo orden que usa el juego
    feats[7] = [R + "piedra_brillante_purpura", R + "cuarzo_purpura", "minecraft:ore_magma", "minecraft:spring_closed",
                "minecraft:ore_gravel_nether", "minecraft:ore_blackstone", "minecraft:ore_gold_nether",
                "minecraft:ore_quartz_nether", "minecraft:ore_ancient_debris_large", "minecraft:ore_debris_small"]
    save_json(os.path.join(wg, "biome", "mar_del_nether.json"), {
        "has_precipitation": False, "temperature": 2.0, "downfall": 0.0,
        "effects": {
            "fog_color": 0x5A1A38, "sky_color": 0x6E1A3C, "water_color": 0x7A2BD6, "water_fog_color": 0x3B0F66,
            "particle": {"options": {"type": "minecraft:portal"}, "probability": 0.006},
            "ambient_sound": "minecraft:ambient.crimson_forest.loop",
            "mood_sound": {"sound": "minecraft:ambient.crimson_forest.mood", "tick_delay": 6000, "block_search_extent": 8, "offset": 2.0},
            "additions_sound": {"sound": "minecraft:ambient.crimson_forest.additions", "tick_chance": 0.0111},
            "music": {"sound": "minecraft:music.nether.crimson_forest", "min_delay": 12000, "max_delay": 24000, "replace_current_music": False},
        },
        "spawners": {
            "monster": [{"type": "minecraft:ghast", "weight": 30, "minCount": 1, "maxCount": 2},
                        {"type": "minecraft:magma_cube", "weight": 5, "minCount": 2, "maxCount": 4},
                        {"type": "minecraft:zombified_piglin", "weight": 40, "minCount": 2, "maxCount": 4}] + sea("monster"),
            "creature": [], "ambient": [], "axolotls": [], "underground_water_creature": [], "water_creature": sea("water_creature"),
            "water_ambient": sea("water_ambient"), "misc": []},
        "spawn_costs": {},
        "carvers": {"air": "minecraft:nether_cave"},
        "features": feats})
    # el Nether con el Mar del Nether (los 5 biomas normales con sus parámetros de siempre + el nuevo)
    nb = [("minecraft:nether_wastes", 0.0, 0.0, 0.0), ("minecraft:soul_sand_valley", 0.0, -0.5, 0.0),
          ("minecraft:crimson_forest", 0.4, 0.0, 0.0), ("minecraft:warped_forest", 0.0, 0.5, 0.375),
          ("minecraft:basalt_deltas", -0.5, 0.0, 0.175), (R + "mar_del_nether", -0.3, 0.3, 0.0),
          # puntos extra: el Mar del Nether es un bioma grande
          (R + "mar_del_nether", -0.5, 0.5, 0.0), (R + "mar_del_nether", -0.2, 0.15, 0.0)]
    save_json(os.path.join(MCDATA, "dimension", "the_nether.json"), {
        "type": "minecraft:the_nether",
        "generator": {"type": "minecraft:noise", "settings": "minecraft:nether", "biome_source": {
            "type": "minecraft:multi_noise", "biomes": [
                {"biome": b, "parameters": {"temperature": t, "humidity": h, "continentalness": 0.0, "erosion": 0.0,
                                            "depth": 0.0, "weirdness": 0.0, "offset": o}} for b, t, h, o in nb]}}})
    # Árbol de Hielo: crece en el Mar del Nether (sus hojas dan la Hoja del Frío Eterno), ya no en Picos de Hielo
    save_json(os.path.join(wg, "configured_feature", "arbol_de_hielo.json"), {"type": R + "frost_tree", "config": {}})
    save_json(os.path.join(wg, "placed_feature", "arbol_de_hielo.json"), {
        "feature": R + "arbol_de_hielo", "placement": [
            {"type": "minecraft:count_on_every_layer", "count": 2}, {"type": "minecraft:biome"}]})
    # el reino aparece en el Mar del Nether
    save_json(os.path.join(DATA, "tags", "worldgen", "biome", "has_reino.json"), {"values": [R + "mar_del_nether"]})
    save_json(os.path.join(wg, "structure", "capital.json"), {
        "type": R + "capital", "biomes": "#" + R + "has_reino", "step": "surface_structures",
        # dentro del reino (de borde a borde, con el muelle) no aparece ningún mob hostil; los humanos y el dragón
        # son de la categoría "creature" y siguen apareciendo normal
        "spawn_overrides": {"monster": {"bounding_box": "full", "spawns": []}}, "terrain_adaptation": "none"})
    save_json(os.path.join(wg, "structure_set", "capital.json"), {
        "structures": [{"structure": R + "capital", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 24, "separation": 12, "salt": 74839201}})


def write_all():
    lang()
    item_models()
    recipes()
    loot()
    tags()
    sounds()
    worldgen()


if __name__ == "__main__":
    write_all()
