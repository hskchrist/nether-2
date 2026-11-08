"""Encantamiento "Escudo de Dragón": para cualquier armadura (casco, pechera, pantalones o botas, de cualquier material,
también las del mod). Protege de los disparos de los dragones: las bolas de fuego (y sus explosiones) del Dragón del
Nether, de los Dragones Infernal, de Almas y de Obsidiana, y del Dragón del End.

Nivel I a IV. Cada nivel en cada pieza resta 12 % del daño de esos disparos (con las 4 piezas en IV, hasta el 80 %, el
máximo que permite el juego sumando todas las protecciones). Es compatible con Protección y con todos los demás.
Sale en la mesa de encantamientos, con aldeanos bibliotecarios, y se craftea el libro (nivel I).
"""
import json
import os

from common import ASSETS, DATA, MCDATA, MODID, save_json

R = MODID + ":"
ID = "escudo_dragon"


def write_all():
    save_json(os.path.join(DATA, "tags", "entity_type", "disparos_dragon.json"), {"values": [
        R + "dragon_fireball", "minecraft:dragon_fireball"]})
    shot = {"condition": "minecraft:damage_source_properties",
            "predicate": {"direct_entity": {"type": "#" + R + "disparos_dragon"}}}
    save_json(os.path.join(DATA, "enchantment", ID + ".json"), {
        "description": {"translate": "enchantment.%s.%s" % (MODID, ID)},
        "supported_items": "#minecraft:enchantable/armor",
        "weight": 3, "max_level": 4,
        "min_cost": {"base": 8, "per_level_above_first": 9},
        "max_cost": {"base": 28, "per_level_above_first": 9},
        "anvil_cost": 2,
        "slots": ["armor"],
        "effects": {"minecraft:damage_protection": [{
            "effect": {"type": "minecraft:add", "value": {"type": "minecraft:linear", "base": 3, "per_level_above_first": 3}},
            "requirements": shot}]}})
    for tag in ("in_enchanting_table", "non_treasure", "tradeable", "on_random_loot", "on_traded_equipment"):
        save_json(os.path.join(MCDATA, "tags", "enchantment", tag + ".json"), {"replace": False, "values": [R + ID]})
    # el libro: rubíes, crema de magma y un libro
    save_json(os.path.join(DATA, "recipe", "libro_escudo_dragon.json"), {
        "type": "minecraft:crafting_shaped", "category": "misc",
        "pattern": ["RMR", "MBM", "RMR"],
        "key": {"R": {"item": R + "ruby"}, "M": {"item": "minecraft:magma_cream"}, "B": {"item": "minecraft:book"}},
        "result": {"id": "minecraft:enchanted_book", "count": 1,
                   "components": {"minecraft:stored_enchantments": {"levels": {R + ID: 1}}}}})
    for code in ("es_es", "es_cl", "es_mx", "es_ar", "en_us"):
        p = os.path.join(ASSETS, "lang", code + ".json")
        d = json.load(open(p, encoding="utf-8"))
        d["enchantment.%s.%s" % (MODID, ID)] = "Dragon Ward" if code == "en_us" else "Escudo de Dragón"
        d["enchantment.%s.%s.desc" % (MODID, ID)] = ("Protects from dragon shots" if code == "en_us"
                                                    else "Protege de los disparos de los dragones")
        save_json(p, d)


if __name__ == "__main__":
    write_all()
