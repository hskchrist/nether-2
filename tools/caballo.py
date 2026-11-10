"""Caballo del Nether (modelo y skin del usuario: tools/ref/caballo/nether_horse.obj y caballo_nether.png) y sus jinetes.

- Modelo: caballo_geo.py lo convierte del .obj sin cambiar nada (sólo agrupa los cubos en huesos para animarlos).
- Animaciones: quieto, caminar (paso cruzado), galope, comer y pararse en dos patas.
- Nombres, botín, huevos de generación (el caballo y 3 de jinetes: guerrero, ballestero y arquero) y dónde aparece.
"""
import json
import math
import os
import shutil

from common import ASSETS, DATA, MODID, save_json

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref", "caballo")
R = MODID + ":"
A = "animation.caballo_nether."


def geo():
    # la conversión del .obj ya está hecha (tarda): ref/caballo/caballo_nether_convertido.geo.json
    # (para rehacerla: python3 caballo_geo.py y copiar el resultado)
    g = json.load(open(os.path.join(REF, "caballo_nether_convertido.geo.json")))
    bones = g["minecraft:geometry"][0]["bones"]
    for b in bones:
        # las patas cuelgan del cuerpo (así al pararse en dos patas se levantan con él)
        if b["name"].startswith("leg_"):
            b["parent"] = "body"
        if b["name"] == "body":
            b["pivot"] = [0, 13, 8]
    return g


def wave(period, amp, phase=0.0, steps=8, offset=0.0):
    """Keyframes de una onda (seno) en un ciclo."""
    out = {}
    for i in range(steps + 1):
        t = period * i / steps
        out["%.4g" % t] = round(offset + amp * math.sin(2 * math.pi * i / steps + phase), 3)
    return out


def rot_x(kf):
    return {"rotation": {t: [v, 0, 0] for t, v in kf.items()}}


def animations():
    anims = {}
    # quieto: cola y cabeza se mueven suave
    anims[A + "idle"] = {"loop": True, "animation_length": 4.0, "bones": {
        "tail": {"rotation": {t: [v, 0, v * 0.5] for t, v in wave(4.0, 4.0, steps=8, offset=0).items()}},
        "neck": rot_x(wave(4.0, 2.0, steps=8)),
    }}
    # caminar: paso cruzado (delantera izquierda con trasera derecha)
    P = 1.0
    anims[A + "walk"] = {"loop": True, "animation_length": P, "bones": {
        "leg_front_left": rot_x(wave(P, 22.0)), "leg_back_right": rot_x(wave(P, 22.0)),
        "leg_front_right": rot_x(wave(P, 22.0, math.pi)), "leg_back_left": rot_x(wave(P, 22.0, math.pi)),
        "neck": rot_x(wave(P, 3.0, 0, steps=8)),
        "tail": rot_x(wave(P, 6.0, math.pi / 2, offset=8.0)),
    }}
    # galope: patas en pares, cuerpo que sube y baja, cuello que acompaña
    P = 0.5
    anims[A + "run"] = {"loop": True, "animation_length": P, "bones": {
        "leg_front_left": rot_x(wave(P, 45.0)), "leg_front_right": rot_x(wave(P, 45.0, 0.6)),
        "leg_back_left": rot_x(wave(P, 40.0, math.pi)), "leg_back_right": rot_x(wave(P, 40.0, math.pi + 0.6)),
        "body": {"rotation": {t: [v, 0, 0] for t, v in wave(P, 4.0, math.pi / 2).items()},
                 "position": {t: [0, v, 0] for t, v in wave(P, 0.8, 0).items()}},
        "neck": rot_x(wave(P, 7.0, math.pi / 2, offset=-6.0)),
        "tail": rot_x(wave(P, 10.0, 0, offset=25.0)),
    }}
    # comer: baja la cabeza al suelo y mastica
    anims[A + "eat"] = {"loop": True, "animation_length": 2.0, "bones": {
        "neck": {"rotation": {"0": [52, 0, 0], "1": [56, 0, 0], "2": [52, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.5": [6, 0, 0], "1": [0, 0, 0], "1.5": [6, 0, 0], "2": [0, 0, 0]}},
        "tail": rot_x(wave(2.0, 5.0)),
    }}
    # pararse en dos patas (relincha)
    anims[A + "rear"] = {"loop": True, "animation_length": 1.0, "bones": {
        "body": {"rotation": {"0": [-40, 0, 0], "0.5": [-44, 0, 0], "1": [-40, 0, 0]}},
        "leg_back_left": {"rotation": {"0": [40, 0, 0], "1": [40, 0, 0]}},
        "leg_back_right": {"rotation": {"0": [40, 0, 0], "1": [40, 0, 0]}},
        "leg_front_left": rot_x(wave(1.0, 30.0, offset=-20.0)),
        "leg_front_right": rot_x(wave(1.0, 30.0, math.pi, offset=-20.0)),
        "neck": {"rotation": {"0": [10, 0, 0], "1": [10, 0, 0]}},
        "tail": {"rotation": {"0": [35, 0, 0], "1": [35, 0, 0]}},
    }}
    return {"format_version": "1.8.0", "animations": anims}


EGGS = {
    "caballo_nether": ("Huevo de generación de Caballo del Nether", "Nether Horse Spawn Egg"),
    "guerrero_a_caballo": ("Huevo de generación de Guerrero a caballo", "Mounted Warrior Spawn Egg"),
    "ballestero_a_caballo": ("Huevo de generación de Ballestero a caballo", "Mounted Crossbowman Spawn Egg"),
    "arquero_a_caballo": ("Huevo de generación de Arquero a caballo", "Mounted Archer Spawn Egg"),
}


def write_all():
    save_json(os.path.join(ASSETS, "geo", "entity", "caballo_nether.geo.json"), geo())
    save_json(os.path.join(ASSETS, "animations", "entity", "caballo_nether.animation.json"), animations())
    shutil.copy(os.path.join(REF, "caballo_nether.png"), os.path.join(ASSETS, "textures", "entity", "caballo_nether.png"))
    for k in EGGS:
        save_json(os.path.join(ASSETS, "models", "item", k + "_spawn_egg.json"), {"parent": "minecraft:item/template_spawn_egg"})
    for code in ("es_es", "es_cl", "es_mx", "es_ar", "en_us"):
        p = os.path.join(ASSETS, "lang", code + ".json")
        d = json.load(open(p, encoding="utf-8"))
        en = code == "en_us"
        d["entity.%s.caballo_nether" % MODID] = "Nether Horse" if en else "Caballo del Nether"
        for k, (es, eng) in EGGS.items():
            d["item.%s.%s_spawn_egg" % (MODID, k)] = eng if en else es
        save_json(p, d)
    # botín: cuero y, a veces, un hongo carmesí
    save_json(os.path.join(DATA, "loot_table", "entities", "caballo_nether.json"), {"type": "minecraft:entity", "pools": [
        {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:leather", "functions": [
            {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 0, "max": 2}}]}]},
        {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.3}],
         "entries": [{"type": "minecraft:item", "name": "minecraft:crimson_fungus"}]}]})
    # dónde aparece (solo, o con su potrillo)
    save_json(os.path.join(DATA, "neoforge", "biome_modifier", "caballos_nether.json"), {
        "type": "neoforge:add_spawns",
        "biomes": [R + "mar_del_nether", "minecraft:crimson_forest", "minecraft:nether_wastes"],
        "spawners": [{"type": R + "caballo_nether", "weight": 5, "minCount": 1, "maxCount": 1}]})


if __name__ == "__main__":
    write_all()
