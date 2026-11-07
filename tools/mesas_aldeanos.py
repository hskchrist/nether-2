"""Mesas de trabajo del Nether para los aldeanos que no tenían la suya (propuesta, todavía no van en el mod):
cartógrafo, flechero, peletero, pastor y albañil. Misma estética que las mesas del reino: piedra negra con oro,
madera carmesí y rubí.
"""
import math
import random

from blocks2 import (el, noise, crimson_planks, stone_gold, basalt, BLACKSTONE, BLACK_D, GOLDC, GOLD_D, CRIMSON, CRIMSON_D,
                     CRIMSON_L, RUBYC, IRON, IRON_D)

PAPER, PAPER_D = (222, 196, 140), (182, 152, 100)
WATER, WATER_L = (82, 36, 140), (132, 74, 196)
LEATHER, LEATHER_D = (124, 72, 40), (88, 50, 26)
WOOL, WOOL_L = (140, 22, 54), (184, 44, 80)


# ----------------------------------------------------------------- texturas 16x16
def map_top(x, y):
    """Mapa del Nether sobre la mesa: el Océano Púrpura, el Reino al centro, caminos rojos y la rosa de los vientos."""
    if x in (0, 15) or y in (0, 15):
        return GOLD_D if (x + y) % 2 else GOLDC
    d = math.hypot(x - 7.5, y - 8)
    if d < 1.6:
        return RUBYC                                              # el Reino
    if 4.5 < d < 6.5 and (x + y) % 3:
        return WATER if (x * y) % 4 else WATER_L                  # el mar
    if x == 7 or y == 8:
        return (170, 40, 40)                                      # caminos
    if (x, y) in ((12, 3), (12, 2), (11, 3), (13, 3), (12, 4)):
        return GOLDC                                              # rosa de los vientos
    return noise(PAPER if (x + y) % 5 else PAPER_D, x, y, 6, 21)


def scroll(x, y):
    return PAPER_D if y in (0, 15) or x % 4 == 0 else PAPER


def fletch_top(x, y):
    """Flechas con plumas rojas y puntas de rubí sobre madera carmesí."""
    if y in (3, 8, 13) and 2 <= x <= 13:
        if x <= 4:
            return (240, 236, 226) if x % 2 else RUBYC            # pluma
        if x >= 12:
            return (255, 90, 100) if x == 13 else RUBYC           # punta de rubí
        return (96, 60, 34)                                       # astil
    if y in (2, 4, 7, 9, 12, 14) and 2 <= x <= 4:
        return RUBYC
    return crimson_planks(x, y)


def fletch_side(x, y):
    if y in (0, 15) or x in (0, 15):
        return GOLDC if (x + y) % 3 else GOLD_D
    if 5 <= y <= 10 and 5 <= x <= 10:                             # diana
        d = max(abs(x - 7.5), abs(y - 7.5))
        return RUBYC if d < 1 else (240, 236, 226) if d < 2 else RUBYC
    return crimson_planks(x, y)


def cauldron_side(x, y):
    if y in (0, 1):
        return GOLDC if x % 3 else GOLD_D
    if y == 15 or x in (0, 15):
        return BLACK_D
    if y in (6, 7) and x % 4 == 1:
        return RUBYC
    return noise(BLACKSTONE, x, y, 8, 22)


def cauldron_water(x, y):
    r = random.Random(x * 17 + y * 29)
    return WATER_L if r.random() < 0.2 else WATER


def leather(x, y):
    if x in (0, 15):
        return LEATHER_D
    if y % 3 == 0 and x in (2, 13):
        return GOLDC                                              # costuras de oro
    return noise(LEATHER, x, y, 8, 23)


def loom_frame(x, y):
    return noise(CRIMSON_D if (x + y) % 4 else (60, 18, 30), x, y, 5, 24)


def loom_weave(x, y):
    """Tela de lana carmesí a medio tejer, con un motivo de llama dorada."""
    if y < 3:
        return (230, 220, 210) if x % 2 else None                 # hilos sueltos arriba
    flame = abs(x - 7.5) < (y - 3) * 0.45 and y < 12 and (abs(x - 7.5) > (y - 3) * 0.2)
    if flame:
        return GOLDC if (x + y) % 2 else (255, 140, 40)
    return WOOL if (x + y) % 2 else WOOL_L


def spool(x, y):
    return WOOL_L if y % 2 else WOOL


def saw(x, y):
    """Sierra circular de rubí con dientes (cara de frente)."""
    d = math.hypot(x - 7.5, y - 7.5)
    if d > 7.6:
        return None
    if d > 6.4:
        return (255, 120, 130) if (int(math.degrees(math.atan2(y - 7.5, x - 7.5))) // 30) % 2 else None
    if d < 1.5:
        return GOLDC
    return RUBYC if d > 3 else (160, 16, 28)


def stone_dust(x, y):
    r = random.Random(x * 41 + y * 13)
    if r.random() < 0.12:
        return (150, 146, 156)
    return noise(BLACKSTONE, x, y, 7, 25)


TEX = {
    "cartographer_desk_map": map_top, "cartographer_desk_wood": crimson_planks, "cartographer_desk_base": stone_gold,
    "cartographer_desk_scroll": scroll,
    "fletcher_bench_top": fletch_top, "fletcher_bench_side": fletch_side, "fletcher_bench_base": stone_gold,
    "leather_cauldron_side": cauldron_side, "leather_cauldron_water": cauldron_water, "leather_cauldron_leather": leather,
    "shepherd_loom_frame": loom_frame, "shepherd_loom_weave": loom_weave, "shepherd_loom_spool": spool,
    "shepherd_loom_base": stone_gold,
    "mason_cutter_base": stone_dust, "mason_cutter_trim": stone_gold, "mason_cutter_saw": saw, "mason_cutter_chips": basalt,
}


# ----------------------------------------------------------------- modelos
def models():
    m = {}
    m["cartographer_desk"] = [
        el([0, 0, 0], [16, 3, 16], "base", name="base"),
        el([1, 3, 1], [4, 12, 4], "wood", name="pata1"), el([12, 3, 1], [15, 12, 4], "wood", name="pata2"),
        el([1, 3, 12], [4, 12, 15], "wood", name="pata3"), el([12, 3, 12], [15, 12, 15], "wood", name="pata4"),
        el([0, 12, 0], [16, 15, 16], {"up": "map", "down": "wood", "north": "wood", "south": "wood", "east": "wood", "west": "wood"},
           name="tablero"),
        el([2, 15, 11], [10, 17, 13], "scroll", rot={"angle": 22.5, "axis": "y", "origin": [6, 16, 12]}, name="pergamino"),
    ]
    m["fletcher_bench"] = [
        el([0, 0, 0], [16, 2, 16], "base", name="base"),
        el([1, 2, 1], [15, 14, 15], {"up": "top", "down": "side", "north": "side", "south": "side", "east": "side", "west": "side"},
           name="mesa"),
        el([3, 14, 6], [13, 15, 7], "top", rot={"angle": -22.5, "axis": "y", "origin": [8, 14, 7]}, name="flecha"),
    ]
    m["leather_cauldron"] = [
        el([0, 0, 0], [16, 3, 16], "side", name="base"),
        el([0, 3, 0], [16, 16, 2], "side", name="pared_n"), el([0, 3, 14], [16, 16, 16], "side", name="pared_s"),
        el([0, 3, 2], [2, 16, 14], "side", name="pared_o"), el([14, 3, 2], [16, 16, 14], "side", name="pared_e"),
        el([2, 3, 2], [14, 13, 14], {"up": "water"}, name="agua"),
        el([12, 6, 1], [16, 17, 2], "leather", rot={"angle": 22.5, "axis": "z", "origin": [14, 16, 1.5]}, name="cuero"),
    ]
    m["shepherd_loom"] = [
        el([0, 0, 0], [16, 3, 16], "base", name="base"),
        el([1, 3, 6], [3, 16, 10], "frame", name="poste1"), el([13, 3, 6], [15, 16, 10], "frame", name="poste2"),
        el([1, 14, 6], [15, 16, 10], "frame", name="travesano"),
        el([3, 5, 7.5], [13, 14, 8.5], {"north": "weave", "south": "weave"}, name="tela"),
        el([3, 3, 3], [6, 6, 6], "spool", name="ovillo1"), el([10, 3, 11], [13, 6, 14], "spool", name="ovillo2"),
    ]
    m["mason_cutter"] = [
        el([0, 0, 0], [16, 9, 16], {"up": "trim", "down": "base", "north": "base", "south": "base", "east": "base", "west": "base"},
           name="base"),
        el([1, 9, 1], [15, 10, 15], "chips", name="viruta"),
        el([0, 9, 7.5], [16, 16, 8.5], {"north": "saw", "south": "saw"}, name="sierra"),
    ]
    texsets = {
        "cartographer_desk": {"map": "cartographer_desk_map", "wood": "cartographer_desk_wood", "base": "cartographer_desk_base",
                              "scroll": "cartographer_desk_scroll"},
        "fletcher_bench": {"top": "fletcher_bench_top", "side": "fletcher_bench_side", "base": "fletcher_bench_base"},
        "leather_cauldron": {"side": "leather_cauldron_side", "water": "leather_cauldron_water", "leather": "leather_cauldron_leather"},
        "shepherd_loom": {"frame": "shepherd_loom_frame", "weave": "shepherd_loom_weave", "spool": "shepherd_loom_spool",
                          "base": "shepherd_loom_base"},
        "mason_cutter": {"base": "mason_cutter_base", "trim": "mason_cutter_trim", "saw": "mason_cutter_saw", "chips": "mason_cutter_chips"},
    }
    return m, texsets


NAMES = {"cartographer_desk": "Mesa del Cartógrafo", "fletcher_bench": "Banco del Flechero", "leather_cauldron": "Caldero del Peletero",
         "shepherd_loom": "Telar del Pastor", "mason_cutter": "Cortapiedras del Albañil"}
