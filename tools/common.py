"""Utilidades comunes del generador de recursos de Civilización del Nether."""
import json
import os
import random

MODID = "civilizacion_nether"
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "src", "main", "resources"))
ASSETS = os.path.join(RES, "assets", MODID)
DATA = os.path.join(RES, "data", MODID)
MCDATA = os.path.join(RES, "data", "minecraft")


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def save_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


GOLD = (214, 160, 38)
GOLD_D = (150, 104, 24)
GOLD_L = (250, 214, 92)
RED = (168, 22, 30)
RED_D = (96, 12, 18)
RED_L = (236, 64, 64)
RED_X = (255, 40, 40)
BLACK = (20, 8, 10)
CHAR = (42, 34, 40)
STEEL = (74, 62, 68)
SKIN = (116, 66, 48)
SKIN_D = (92, 50, 38)
WHITE = (240, 232, 224)


def jit(c, rnd, amt=7):
    return tuple(max(0, min(255, v + rnd.randint(-amt, amt))) for v in c[:3]) + (255,)


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


# id, nombre ES, nombre EN  (orden = HumanoidType.java; el dragón es uno solo)
HUMANOIDS = [
    ("guerrero", "Guerrero del Nether", "Nether Warrior"),
    ("arquero", "Arquero del Nether", "Nether Archer"),
    ("rey_necromancer", "Rey Necromancer", "Necromancer King"),
    ("subdito_alma", "Súbdito de Almas", "Soul Minion"),
]
DRAGONS = [
    ("nether_dragon", "Dragón del Nether", "Nether Dragon"),
]


class Packer:
    """Empaqueta cajas UV dentro de regiones rectangulares de una textura."""

    def __init__(self, regions):
        self.regions = [list(r) for r in regions]
        self.idx = 0
        r = self.regions[0]
        self.cx, self.cy, self.rowh = r[0], r[1], 0

    def alloc(self, w, h, d):
        bw, bh = int(2 * (w + d)), int(h + d)
        while True:
            x0, y0, x1, y1 = self.regions[self.idx]
            if self.cx + bw > x1:
                self.cx = x0
                self.cy += self.rowh
                self.rowh = 0
            if self.cy + bh <= y1 and self.cx + bw <= x1:
                u, v = self.cx, self.cy
                self.cx += bw
                self.rowh = max(self.rowh, bh)
                return [u, v]
            self.idx += 1
            if self.idx >= len(self.regions):
                raise RuntimeError("Sin espacio en la textura")
            r = self.regions[self.idx]
            self.cx, self.cy, self.rowh = r[0], r[1], 0

OPTIONAL_BONES = ["crown", "hat_mago", "hat_summoner", "hood", "cape", "robe", "quiver", "right_pauldron", "left_pauldron"]
PAUL = ["right_pauldron", "left_pauldron"]
VISIBLE = {
    "civil_comun": [],
    "aldeano_nether": ["hood"],
    "guerrero": PAUL,
    "arquero": ["hood", "quiver"],
    "mago": ["hat_mago", "robe", "cape"],
    "summoner": ["hat_summoner", "robe", "cape"],
    "sacerdote": ["hood", "robe", "cape"],
    "noble": ["crown", "robe", "cape"],
    "guardia_real": PAUL,
    "caballero_rubi": PAUL + ["cape"],
    "arquero_elite": ["hood", "quiver", "cape"],
    "mago_batalla": PAUL + ["robe", "cape"],
    "berserker": PAUL,
    "sacerdote_supremo": PAUL + ["crown", "robe", "cape"],
    "alma_nether": [],
}
