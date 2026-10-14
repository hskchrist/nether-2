"""Genera los JSON de datos y recursos: idiomas, modelos de ítem, estados de bloque, recetas, botín, spawns y mena."""
import os
from common import *

ITEMS_ES = {
    "ruby": ("Rubí", "Ruby"),
    "ruby_sword": ("Espada de rubí", "Ruby Sword"),
    "necro_staff": ("Báculo del Rey Necromancer", "Necromancer King's Staff"),
    "ruby_bow": ("Arco de rubí", "Ruby Bow"),
    "ruby_helmet": ("Casco de rubí", "Ruby Helmet"),
    "ruby_chestplate": ("Peto de rubí", "Ruby Chestplate"),
    "ruby_leggings": ("Grebas de rubí", "Ruby Leggings"),
    "ruby_boots": ("Botas de rubí", "Ruby Boots"),
    "dragon_armor": ("Armadura de dragón", "Dragon Armor"),
    "dragon_egg": ("Huevo de Dragón del Nether", "Nether Dragon Egg"),
    "soul": ("Alma", "Soul"),
    "soul_scythe": ("Hoz de almas", "Soul Scythe"),
    "soul_potion": ("Poción de Alma", "Soul Potion"),
    "dragon_staff": ("Báculo de dragón", "Dragon Staff"),
}
BLOCKS_ES = {
    "ruby_block": ("Bloque de rubí", "Block of Ruby"),
    "ruby_ore": ("Mena de rubí del Nether", "Nether Ruby Ore"),
    "ruby_lamp": ("Lámpara de rubí", "Ruby Lamp"),
    "ruby_bricks": ("Ladrillos de rubí", "Ruby Bricks"),
}
EGG_COLORS = {  # fondo, manchas (deben coincidir con ModItems.java solo como referencia visual)
}


def lang():
    es, en = {}, {}
    for tid, nes, nen in HUMANOIDS + DRAGONS:
        es["entity.%s.%s" % (MODID, tid)] = nes
        en["entity.%s.%s" % (MODID, tid)] = nen
        es["item.%s.%s_spawn_egg" % (MODID, tid)] = "Huevo de generación de %s" % nes
        en["item.%s.%s_spawn_egg" % (MODID, tid)] = "%s Spawn Egg" % nen
    es["entity.%s.dragon_egg" % MODID] = "Huevo de Dragón del Nether"
    en["entity.%s.dragon_egg" % MODID] = "Nether Dragon Egg"
    es["entity.%s.dragon_fireball" % MODID] = "Bola de fuego de dragón"
    en["entity.%s.dragon_fireball" % MODID] = "Dragon Fireball"
    for k, (a, b) in ITEMS_ES.items():
        es["item.%s.%s" % (MODID, k)] = a
        en["item.%s.%s" % (MODID, k)] = b
    for k, (a, b) in BLOCKS_ES.items():
        es["block.%s.%s" % (MODID, k)] = a
        en["block.%s.%s" % (MODID, k)] = b
    extra = {
        "itemGroup.civilizacion_nether": ("Civilización del Nether", "Nether Civilization"),
        "key.categories.civilizacion_nether": ("Civilización del Nether", "Nether Civilization"),
        "key.civilizacion_nether.breath": ("Ráfaga de fuego del dragón (barra cargada)", "Dragon fire burst (charged bar)"),
        "hud.civilizacion_nether.charge": ("Ráfaga: %s/%s · clic derecho para disparar", "Burst: %s/%s · right click to shoot"),
        "hud.civilizacion_nether.burst_ready": ("¡RÁFAGA LISTA! Pulsa %s", "BURST READY! Press %s"),
        "msg.civilizacion_nether.burst_not_ready": ("La ráfaga aún no está cargada (%s/%s). Dispara con clic derecho para cargarla.",
                                                   "The burst is not charged yet (%s/%s). Shoot with right click to charge it."),
        "msg.civilizacion_nether.tamed": ("¡%s ahora te sigue!", "%s now follows you!"),
        "msg.civilizacion_nether.king_offering": ("%s acepta tu ofrenda (%s/%s manzanas doradas encantadas)",
                                                 "%s accepts your offering (%s/%s enchanted golden apples)"),
        "msg.civilizacion_nether.tame_fail": ("%s no está convencido todavía…", "%s is not convinced yet…"),
        "msg.civilizacion_nether.sit": ("%s se queda quieto aquí.", "%s will stay here."),
        "msg.civilizacion_nether.follow": ("%s te sigue.", "%s follows you."),
        "msg.civilizacion_nether.need_saddle": ("Coloca una silla al dragón para montarlo.", "Put a saddle on the dragon to ride it."),
        "msg.civilizacion_nether.not_owner": ("Este dragón no es tuyo.", "This dragon is not yours."),
        "msg.civilizacion_nether.bond": ("Vínculo con %s: %s/100", "Bond with %s: %s/100"),
        "msg.civilizacion_nether.ride_hint": ("Mira arriba y avanza (W) para despegar. Clic derecho: bola de fuego. 3 disparos cargan la barra → R: ráfaga grande. X: cámara de dragón.",
                                             "Look up and move forward (W) to take off. Right click: fireball. 3 shots charge the bar → R: big burst. X: dragon camera."),
        "msg.civilizacion_nether.too_young": ("%s es muy pequeño para montarlo (%s%% de crecimiento). Sigue alimentándolo con carne o pescado.",
                                             "%s is too small to ride (%s%% grown). Keep feeding it meat or fish."),
        "msg.civilizacion_nether.dragon_growth": ("%s: %s (%s%% de crecimiento)", "%s: %s (%s%% grown)"),
        "msg.civilizacion_nether.dragon_stage_up": ("¡%s creció! Ahora es: %s", "%s grew! It is now: %s"),
        "msg.civilizacion_nether.dragon_adult": ("¡%s ya es adulto! Ponle una silla de montar y haz clic derecho para volar.",
                                                "%s is now an adult! Put a saddle on it and right click to fly."),
        "msg.civilizacion_nether.egg_placed": ("Huevo puesto. Eclosiona en unos 5 minutos (la mitad cerca de lava, magma o fuego).",
                                              "Egg placed. It hatches in about 5 minutes (half that near lava, magma or fire)."),
        "msg.civilizacion_nether.egg_adopted": ("Ahora este huevo es tuyo: empezó a incubarse.", "This egg is yours now: it started incubating."),
        "msg.civilizacion_nether.egg_time": ("Al huevo le faltan unos %s segundos para eclosionar.", "The egg will hatch in about %s seconds."),
        "msg.civilizacion_nether.egg_heat": ("Al huevo le faltan unos %s segundos para eclosionar (el calor lo acelera).",
                                            "The egg will hatch in about %s seconds (the heat speeds it up)."),
        "msg.civilizacion_nether.egg_hatched": ("¡Nació tu Dragón del Nether! Aliméntalo con carne o pescado para que crezca.",
                                               "Your Nether Dragon hatched! Feed it meat or fish so it grows."),
        "msg.civilizacion_nether.egg_laid": ("¡Tus dragones pusieron un huevo!", "Your dragons laid an egg!"),
        "stage.civilizacion_nether.0": ("Recién nacido", "Hatchling"),
        "stage.civilizacion_nether.1": ("Cría", "Whelp"),
        "stage.civilizacion_nether.2": ("Joven", "Juvenile"),
        "stage.civilizacion_nether.3": ("Subadulto", "Subadult"),
        "stage.civilizacion_nether.4": ("Adulto", "Adult"),
        "item.civilizacion_nether.enchanted_potion": ("%s encantada", "Enchanted %s"),
        "key.civilizacion_nether.dragon_camera": ("Cámara de dragón (al montarlo)", "Dragon camera (while riding)"),
        "msg.civilizacion_nether.staff_bound": ("Báculo vinculado a %s", "Staff bound to %s"),
        "msg.civilizacion_nether.staff_none": ("No hay ningún dragón tuyo cerca (o el vinculado no está cargado).",
                                              "None of your dragons is nearby (or the bound one is not loaded)."),
        "msg.civilizacion_nether.staff_recall": ("%s viene hacia ti (%s bloques)", "%s is coming to you (%s blocks)"),
        "msg.civilizacion_nether.staff_free": ("%s anda libre: camina, vuela y descansa por su cuenta.",
                                              "%s roams free: it walks, flies and rests on its own."),
        "msg.civilizacion_nether.staff_follow": ("%s vuelve a seguirte.", "%s follows you again."),
        "tooltip.civilizacion_nether.staff_bound": ("Vinculado a: %s", "Bound to: %s"),
        "tooltip.civilizacion_nether.staff_unbound": ("Sin vincular: llama a todos tus dragones cercanos (clic derecho a un dragón para vincularlo)",
                                                      "Unbound: calls all your nearby dragons (right click a dragon to bind it)"),
        "tooltip.civilizacion_nether.staff_use": ("Clic derecho: tu dragón viene volando o caminando", "Right click: your dragon flies or walks to you"),
        "tooltip.civilizacion_nether.staff_use2": ("Mayús + clic derecho: modo libre / seguirte", "Sneak + right click: free mode / follow you"),
        "tooltip.civilizacion_nether.soul_scythe": ("Rompe arena de almas: suelta de 1 a 3 almas", "Break soul sand: drops 1 to 3 souls"),
        "tooltip.civilizacion_nether.soul_scythe2": ("Sin encantar 1 · Fortuna I 1-2 · II 2-3 · III 3",
                                                    "Unenchanted 1 · Fortune I 1-2 · II 2-3 · III 3"),
        "tooltip.civilizacion_nether.dragon_egg": ("Ponlo en el suelo: eclosiona en ~5 min (más rápido con calor)",
                                                  "Place it on the ground: hatches in ~5 min (faster with heat)"),
        "tooltip.civilizacion_nether.dragon_egg2": ("La cría será tuya. Crece comiendo carne y pescado.",
                                                   "The hatchling will be yours. It grows by eating meat and fish."),
        "tooltip.civilizacion_nether.necro_staff": ("Clic derecho: rayo de almas", "Right click: soul bolt"),
        "tooltip.civilizacion_nether.necro_staff_summon": ("Mayús + clic derecho: invoca 2 Súbditos de Almas",
                                                          "Sneak + right click: summons 2 Soul Minions"),
        "tooltip.civilizacion_nether.dragon_armor": ("Úsala sobre un dragón domesticado", "Use it on a tamed dragon"),
    }
    for k, (a, b) in extra.items():
        es[k] = a
        en[k] = b
    save_json(os.path.join(ASSETS, "lang", "es_es.json"), es)
    for code in ("es_cl", "es_mx", "es_ar", "es_es"):
        save_json(os.path.join(ASSETS, "lang", code + ".json"), es)
    save_json(os.path.join(ASSETS, "lang", "en_us.json"), en)


def models():
    im = os.path.join(ASSETS, "models", "item")
    for k in ["ruby", "ruby_helmet", "ruby_chestplate", "ruby_leggings", "ruby_boots", "dragon_armor", "dragon_egg", "soul"]:
        save_json(os.path.join(im, k + ".json"), {"parent": "minecraft:item/generated",
                                                  "textures": {"layer0": "%s:item/%s" % (MODID, k)}})
    for k in ["ruby_sword", "soul_scythe", "dragon_staff"]:
        save_json(os.path.join(im, k + ".json"), {"parent": "minecraft:item/handheld",
                                                  "textures": {"layer0": "%s:item/%s" % (MODID, k)}})
    # báculo 3D (GeckoLib) en la mano; ícono 2D en el inventario, en el suelo y en marcos
    icon = {"parent": "minecraft:item/generated", "textures": {"layer0": "%s:item/necro_staff_icon" % MODID}}
    held3 = {"rotation": [75, 0, 0], "translation": [0, -1.24, -4.64], "scale": [0.6, 0.6, 0.6]}
    held1 = {"rotation": [-10, 0, 10], "translation": [1.2, -3.0, 0.5], "scale": [0.5, 0.5, 0.5]}
    save_json(os.path.join(im, "necro_staff.json"), {
        "loader": "neoforge:separate_transforms",
        "base": {"parent": "minecraft:builtin/entity", "gui_light": "front",
                 "textures": {"particle": "%s:item/necro_staff_icon" % MODID},
                 "display": {"thirdperson_righthand": held3, "thirdperson_lefthand": held3,
                             "firstperson_righthand": held1, "firstperson_lefthand": held1,
                             "head": {"rotation": [0, 0, 0], "translation": [0, 6, 0], "scale": [0.6, 0.6, 0.6]}}},
        "perspectives": {"gui": icon, "ground": icon, "fixed": icon}})
    bow = {"parent": "minecraft:item/bow", "textures": {"layer0": "%s:item/ruby_bow" % MODID}, "overrides": [
        {"predicate": {"pulling": 1}, "model": "%s:item/ruby_bow_pulling_0" % MODID},
        {"predicate": {"pulling": 1, "pull": 0.65}, "model": "%s:item/ruby_bow_pulling_1" % MODID},
        {"predicate": {"pulling": 1, "pull": 0.9}, "model": "%s:item/ruby_bow_pulling_2" % MODID}]}
    save_json(os.path.join(im, "ruby_bow.json"), bow)
    for i in range(3):
        save_json(os.path.join(im, "ruby_bow_pulling_%d.json" % i),
                  {"parent": "%s:item/ruby_bow" % MODID, "textures": {"layer0": "%s:item/ruby_bow_pulling_%d" % (MODID, i)}})
    for tid, _, _ in HUMANOIDS + DRAGONS:
        save_json(os.path.join(im, tid + "_spawn_egg.json"), {"parent": "minecraft:item/template_spawn_egg"})
    for b in BLOCKS_ES:
        save_json(os.path.join(ASSETS, "blockstates", b + ".json"), {"variants": {"": {"model": "%s:block/%s" % (MODID, b)}}})
        save_json(os.path.join(ASSETS, "models", "block", b + ".json"),
                  {"parent": "minecraft:block/cube_all", "textures": {"all": "%s:block/%s" % (MODID, b)}})
        save_json(os.path.join(im, b + ".json"), {"parent": "%s:block/%s" % (MODID, b)})


def item(i, n=1):
    return {"id": i, "count": n}


def shaped(name, pattern, key, result, count=1, cat="misc"):
    save_json(os.path.join(DATA, "recipe", name + ".json"), {
        "type": "minecraft:crafting_shaped", "category": cat, "pattern": pattern,
        "key": {k: {"item": v} for k, v in key.items()}, "result": item(result, count)})


# Huevo: obsidiana llorosa en las esquinas, rubíes en cruz y un bloque de rubí al centro
DRAGON_EGG_RECIPE = (["ORO", "RBR", "ORO"], {"O": "minecraft:crying_obsidian", "R": MODID + ":ruby",
                                             "B": MODID + ":ruby_block"})


# Hoz de almas: hoja de rubí con un alma en la punta y mango de varas de blaze en diagonal
SCYTHE_RECIPE = (["RRA", " B ", "B  "], {"R": MODID + ":ruby", "A": MODID + ":soul", "B": "minecraft:blaze_rod"})


# Báculo de dragón: rubí y alma arriba, varas de blaze en diagonal y un anillo de oro
STAFF_DRAGON_RECIPE = ([" RA", " GR", "B  "], {"R": MODID + ":ruby", "A": MODID + ":soul", "G": "minecraft:gold_ingot",
                                               "B": "minecraft:blaze_rod"})


def recipes():
    R = MODID + ":ruby"
    shaped("ruby_block", ["RRR", "RRR", "RRR"], {"R": R}, MODID + ":ruby_block", cat="building")
    save_json(os.path.join(DATA, "recipe", "ruby_from_block.json"), {
        "type": "minecraft:crafting_shapeless", "category": "misc",
        "ingredients": [{"item": MODID + ":ruby_block"}], "result": item(R, 9)})
    shaped("ruby_bricks", ["RN", "NR"], {"R": R, "N": "minecraft:nether_bricks"}, MODID + ":ruby_bricks", 4, "building")
    shaped("ruby_lamp", [" G ", "RSR", " G "], {"R": R, "G": "minecraft:gold_ingot", "S": "minecraft:shroomlight"},
           MODID + ":ruby_lamp", 2, "building")
    shaped("ruby_sword", ["R", "R", "B"], {"R": R, "B": "minecraft:blaze_rod"}, MODID + ":ruby_sword", cat="equipment")
    import necro
    pattern, key = necro.STAFF_RECIPE
    shaped("necro_staff", pattern, key, MODID + ":necro_staff", cat="equipment")
    shaped("ruby_bow", [" RS", "B S", " RS"], {"R": R, "B": "minecraft:blaze_rod", "S": "minecraft:string"},
           MODID + ":ruby_bow", cat="equipment")
    shaped("dragon_armor", ["  R", "RBR", "RRR"], {"R": R, "B": MODID + ":ruby_block"}, MODID + ":dragon_armor", cat="equipment")
    shaped("dragon_egg", DRAGON_EGG_RECIPE[0], DRAGON_EGG_RECIPE[1], MODID + ":dragon_egg")
    shaped("soul_scythe", SCYTHE_RECIPE[0], SCYTHE_RECIPE[1], MODID + ":soul_scythe", cat="equipment")
    shaped("dragon_staff", STAFF_DRAGON_RECIPE[0], STAFF_DRAGON_RECIPE[1], MODID + ":dragon_staff", cat="equipment")
    for name, src in [("ruby_from_smelting", "minecraft:smelting"), ("ruby_from_blasting", "minecraft:blasting")]:
        save_json(os.path.join(DATA, "recipe", name + ".json"), {
            "type": src, "category": "misc", "ingredient": {"item": MODID + ":ruby_ore"},
            "result": {"id": R}, "experience": 1.0, "cookingtime": 200 if "smelt" in name else 100})


def loot():
    lt = os.path.join(DATA, "loot_table")
    for b in ["ruby_block", "ruby_lamp", "ruby_bricks"]:
        save_json(os.path.join(lt, "blocks", b + ".json"), {
            "type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "%s:%s" % (MODID, b)}],
                                                   "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    save_json(os.path.join(lt, "blocks", "ruby_ore.json"), {
        "type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:alternatives", "children": [
            {"type": "minecraft:item", "name": MODID + ":ruby_ore", "conditions": [{"condition": "minecraft:match_tool", "predicate": {
                "predicates": {"minecraft:enchantments": [{"enchantments": "minecraft:silk_touch", "levels": {"min": 1}}]}}}]},
            {"type": "minecraft:item", "name": MODID + ":ruby", "functions": [
                {"function": "minecraft:apply_bonus", "enchantment": "minecraft:fortune", "formula": "minecraft:ore_drops"},
                {"function": "minecraft:explosion_decay"}]}]}]}]})

    def entity(name, entries):
        save_json(os.path.join(lt, "entities", name + ".json"), {"type": "minecraft:entity", "pools": entries})

    def pool(itm, lo, hi, chance=None):
        p = {"rolls": 1, "entries": [{"type": "minecraft:item", "name": itm, "functions": [
            {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}}]}]}
        if chance:
            p["conditions"] = [{"condition": "minecraft:random_chance", "chance": chance}]
        return p
    R = MODID + ":ruby"
    S = MODID + ":soul"  # todas las criaturas del mod sueltan un alma al morir
    entity("guerrero", [pool(R, 0, 2), pool("minecraft:gold_nugget", 1, 4, 0.5), pool(S, 1, 1)])
    entity("arquero", [pool(R, 0, 1), pool("minecraft:arrow", 1, 4), pool("minecraft:gold_nugget", 1, 3, 0.5), pool(S, 1, 1)])
    # el Rey Necromancer siempre suelta su báculo
    entity("rey_necromancer", [pool(MODID + ":necro_staff", 1, 1), pool(R, 4, 8), pool("minecraft:gold_ingot", 2, 5), pool(S, 1, 1)])
    entity("subdito_alma", [pool(S, 1, 1)])
    entity("nether_dragon", [pool(R, 3, 7), pool("minecraft:leather", 2, 5), pool("minecraft:bone", 2, 6),
                             pool("minecraft:magma_cream", 1, 3, 0.5), pool(S, 1, 1)])
    entity("dragon_egg", [pool(MODID + ":dragon_egg", 1, 1)])


def tags():
    blocks = [MODID + ":" + b for b in BLOCKS_ES]
    save_json(os.path.join(MCDATA, "tags", "block", "mineable", "pickaxe.json"), {"replace": False, "values": blocks})
    save_json(os.path.join(MCDATA, "tags", "block", "needs_iron_tool.json"),
              {"replace": False, "values": [MODID + ":ruby_ore", MODID + ":ruby_block"]})
    save_json(os.path.join(MCDATA, "tags", "item", "beacon_payment_items.json"), {"replace": False, "values": [MODID + ":ruby"]})
    # la Hoz de almas es una azada: así acepta Fortuna, Eficiencia, Irrompibilidad y Reparación
    save_json(os.path.join(MCDATA, "tags", "item", "hoes.json"), {"replace": False, "values": [MODID + ":soul_scythe"]})
    save_json(os.path.join(MCDATA, "tags", "block", "beacon_base_blocks.json"), {"replace": False, "values": [MODID + ":ruby_block"]})


SPAWNS = [  # (id, peso, min, max); el Rey además pasa un filtro de 1/20 (CommonEvents) y su lugar es el trono de la capital
    ("guerrero", 10, 2, 3), ("arquero", 8, 1, 3), ("rey_necromancer", 1, 1, 1),
    ("nether_dragon", 3, 1, 1),
]


def worldgen():
    bm = os.path.join(DATA, "neoforge", "biome_modifier")
    save_json(os.path.join(bm, "spawns.json"), {
        "type": "neoforge:add_spawns", "biomes": "#minecraft:is_nether",
        "spawners": [{"type": "%s:%s" % (MODID, t), "weight": w, "minCount": a, "maxCount": b} for t, w, a, b in SPAWNS]})
    save_json(os.path.join(bm, "ruby_ore.json"), {
        "type": "neoforge:add_features", "biomes": "#minecraft:is_nether",
        "features": MODID + ":ruby_ore", "step": "underground_decoration"})
    save_json(os.path.join(DATA, "worldgen", "configured_feature", "ruby_ore.json"), {
        "type": "minecraft:ore", "config": {"size": 5, "discard_chance_on_air_exposure": 0.0, "targets": [
            {"target": {"predicate_type": "minecraft:block_match", "block": "minecraft:netherrack"},
             "state": {"Name": MODID + ":ruby_ore"}}]}})
    save_json(os.path.join(DATA, "worldgen", "placed_feature", "ruby_ore.json"), {
        "feature": MODID + ":ruby_ore", "placement": [
            {"type": "minecraft:count", "count": 12}, {"type": "minecraft:in_square"},
            {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform",
                                                           "min_inclusive": {"above_bottom": 10}, "max_inclusive": {"below_top": 10}}},
            {"type": "minecraft:biome"}]})
    # capital del reino: estructura propia (CapitalStructure.java) que excava su caverna y coloca capital.nbt
    save_json(os.path.join(DATA, "worldgen", "structure", "capital.json"), {
        "type": MODID + ":capital", "biomes": "#minecraft:is_nether", "step": "surface_structures",
        "spawn_overrides": {}, "terrain_adaptation": "none"})
    save_json(os.path.join(DATA, "worldgen", "structure_set", "capital.json"), {
        "structures": [{"structure": MODID + ":capital", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 40, "separation": 20, "salt": 74839201}})
    save_json(os.path.join(DATA, "tags", "worldgen", "structure", "capitales.json"), {"values": [MODID + ":capital"]})


def write_all():
    lang()
    models()
    recipes()
    loot()
    tags()
    worldgen()
