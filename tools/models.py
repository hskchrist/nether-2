"""Genera los modelos .geo.json y las animaciones .animation.json (formato Bedrock / GeckoLib)."""
import os
from common import ASSETS, Packer, save_json


class Geo:
    def __init__(self, ident, tw, th):
        self.ident, self.tw, self.th = ident, tw, th
        self.bones = {}
        self.order = []
        self.cubes = []

    def bone(self, name, pivot, parent=None, rotation=None):
        self.bones[name] = {"name": name, "pivot": list(pivot), "cubes": []}
        if parent:
            self.bones[name]["parent"] = parent
        if rotation:
            self.bones[name]["rotation"] = list(rotation)
        self.order.append(name)

    def cube(self, bone, kind, origin, size, uv, inflate=0.0, tag=None, rotation=None, pivot=None):
        c = {"origin": list(origin), "size": list(size), "uv": list(uv)}
        if inflate:
            c["inflate"] = inflate
        if rotation:
            c["rotation"] = list(rotation)
            c["pivot"] = list(pivot if pivot is not None else origin)
        self.bones[bone]["cubes"].append(c)
        self.cubes.append(dict(bone=bone, kind=kind, origin=list(origin), size=list(size), uv=list(uv), tag=tag))

    def to_json(self):
        bones = []
        for n in self.order:
            b = dict(self.bones[n])
            if not b["cubes"]:
                del b["cubes"]
            bones.append(b)
        return {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": self.ident,
                    "texture_width": self.tw,
                    "texture_height": self.th,
                    "visible_bounds_width": 8,
                    "visible_bounds_height": 6,
                    "visible_bounds_offset": [0, 1.5, 0],
                },
                "bones": bones,
            }],
        }


# ====================================================================== HUMANOIDE
def build_humanoid():
    g = Geo("geometry.nether_humanoid", 128, 128)
    pk = Packer([(64, 0, 128, 128), (0, 64, 64, 128)])

    g.bone("body", [0, 12, 0])
    g.cube("body", "body", [-4, 12, -2], [8, 12, 4], [16, 16])
    g.cube("body", "jacket", [-4, 12, -2], [8, 12, 4], [16, 32], 0.25)

    g.bone("head", [0, 24, 0], "body")
    g.cube("head", "head", [-4, 24, -4], [8, 8, 8], [0, 0])
    g.cube("head", "hat", [-4, 24, -4], [8, 8, 8], [32, 0], 0.5)

    g.bone("right_arm", [-5, 22, 0], "body")
    g.cube("right_arm", "arm", [-8, 12, -2], [4, 12, 4], [40, 16], tag="r")
    g.cube("right_arm", "sleeve", [-8, 12, -2], [4, 12, 4], [40, 32], 0.25, tag="r")
    g.bone("left_arm", [5, 22, 0], "body")
    g.cube("left_arm", "arm", [4, 12, -2], [4, 12, 4], [32, 48], tag="l")
    g.cube("left_arm", "sleeve", [4, 12, -2], [4, 12, 4], [48, 48], 0.25, tag="l")

    g.bone("right_leg", [-1.9, 12, 0])
    g.cube("right_leg", "leg", [-3.9, 0, -2], [4, 12, 4], [0, 16])
    g.cube("right_leg", "pants", [-3.9, 0, -2], [4, 12, 4], [0, 32], 0.25)
    g.bone("left_leg", [1.9, 12, 0])
    g.cube("left_leg", "leg", [-0.1, 0, -2], [4, 12, 4], [16, 48])
    g.cube("left_leg", "pants", [-0.1, 0, -2], [4, 12, 4], [0, 48], 0.25)

    def ex(bone, kind, origin, size, tag=None):
        g.cube(bone, kind, origin, size, pk.alloc(*size), tag=tag)

    # piezas opcionales: se muestran u ocultan por tipo desde Java
    g.bone("crown", [0, 32, 0], "head")
    ex("crown", "crown", [-5, 32, -5], [10, 2, 10])
    for (x, z) in [(-5, -5), (3, -5), (-5, 3), (3, 3)]:
        ex("crown", "crown", [x, 34, z], [2, 3, 2])
    ex("crown", "crown", [-1, 34, -5], [2, 4, 2])
    ex("crown", "gem", [-1, 32, -6], [2, 2, 1])

    g.bone("hat_mago", [0, 32, 0], "head")
    ex("hat_mago", "hatm", [-7, 32, -7], [14, 1, 14])
    ex("hat_mago", "hatm", [-4, 33, -4], [8, 4, 8])
    ex("hat_mago", "hatm", [-3, 37, -3], [6, 4, 6])
    ex("hat_mago", "hatm", [-2, 41, -2], [4, 4, 4])
    ex("hat_mago", "hatm", [-1, 45, -1], [2, 3, 2])
    ex("hat_mago", "band", [-5, 33, -5], [10, 1, 10])

    g.bone("hat_summoner", [0, 32, 0], "head")
    ex("hat_summoner", "hatm", [-5, 32, -5], [10, 2, 10])
    ex("hat_summoner", "horn", [3, 33, -1], [2, 5, 2])
    ex("hat_summoner", "horn", [4, 38, -1], [2, 4, 2])
    ex("hat_summoner", "horn", [-5, 33, -1], [2, 5, 2])
    ex("hat_summoner", "horn", [-6, 38, -1], [2, 4, 2])

    g.bone("hood", [0, 32, 0], "head")
    ex("hood", "hood", [-5, 32, -5], [10, 2, 10])
    ex("hood", "hood", [-5, 24, 4], [10, 9, 1])
    ex("hood", "hood", [4, 24, -4], [1, 8, 8])
    ex("hood", "hood", [-5, 24, -4], [1, 8, 8])

    g.bone("cape", [0, 23, 2], "body")
    ex("cape", "cape", [-4, 3, 2], [8, 20, 1])
    g.bone("robe", [0, 12, 0], "body")
    ex("robe", "robe", [-5, 2, -3], [10, 10, 6])
    g.bone("quiver", [0, 18, 2], "body")
    ex("quiver", "quiver", [-2, 13, 2], [4, 10, 2])
    ex("quiver", "arrow", [-1, 23, 2], [1, 3, 1])
    ex("quiver", "arrow", [0, 23, 3], [1, 3, 1])

    g.bone("right_pauldron", [-5, 22, 0], "right_arm")
    ex("right_pauldron", "paul", [-9, 21, -3], [5, 3, 6])
    g.bone("left_pauldron", [5, 22, 0], "left_arm")
    ex("left_pauldron", "paul", [4, 21, -3], [5, 3, 6])

    g.bone("right_hand_item", [-6, 13, 0], "right_arm")
    g.bone("left_hand_item", [6, 13, 0], "left_arm")
    return g


P = "animation.nether_humanoid."


def anim(length, loop, bones):
    out = {"animation_length": length, "bones": {}}
    if loop:
        out["loop"] = True
    for b, chans in bones.items():
        out["bones"][b] = {}
        for ch, frames in chans.items():
            out["bones"][b][ch] = {("%.2f" % t): list(v) for t, v in frames.items()}
    return out


def humanoid_animations():
    a = {}
    a[P + "idle"] = anim(3.0, True, {
        "body": {"position": {0: [0, 0, 0], 1.5: [0, 0.35, 0], 3.0: [0, 0, 0]}},
        "right_arm": {"rotation": {0: [0, 0, 3], 1.5: [0, 0, 5], 3.0: [0, 0, 3]}},
        "left_arm": {"rotation": {0: [0, 0, -3], 1.5: [0, 0, -5], 3.0: [0, 0, -3]}},
    })
    a[P + "idle_guard"] = anim(4.0, True, {
        "body": {"rotation": {0: [-2, 0, 0], 2.0: [-4, 0, 0], 4.0: [-2, 0, 0]}},
        "right_arm": {"rotation": {0: [-14, 0, 6], 2.0: [-18, 0, 6], 4.0: [-14, 0, 6]}},
        "left_arm": {"rotation": {0: [-14, 0, -6], 2.0: [-18, 0, -6], 4.0: [-14, 0, -6]}},
    })
    a[P + "idle_berserk"] = anim(1.5, True, {
        "body": {"rotation": {0: [6, 0, 0], 0.75: [10, 0, 0], 1.5: [6, 0, 0]},
                 "position": {0: [0, 0, 0], 0.75: [0, 0.5, 0], 1.5: [0, 0, 0]}},
        "right_arm": {"rotation": {0: [-22, 0, 12], 0.75: [-28, 0, 14], 1.5: [-22, 0, 12]}},
        "left_arm": {"rotation": {0: [-22, 0, -12], 0.75: [-28, 0, -14], 1.5: [-22, 0, -12]}},
    })
    a[P + "sit"] = anim(2.0, True, {
        "body": {"position": {0: [0, -10, 0], 2.0: [0, -10, 0]}},
        "right_leg": {"rotation": {0: [-90, 10, 0], 2.0: [-90, 10, 0]}, "position": {0: [0, -10, 0], 2.0: [0, -10, 0]}},
        "left_leg": {"rotation": {0: [-90, -10, 0], 2.0: [-90, -10, 0]}, "position": {0: [0, -10, 0], 2.0: [0, -10, 0]}},
        "right_arm": {"rotation": {0: [-30, 0, 0], 2.0: [-30, 0, 0]}},
        "left_arm": {"rotation": {0: [-30, 0, 0], 2.0: [-30, 0, 0]}},
    })
    a[P + "ride"] = anim(2.0, True, {
        "right_leg": {"rotation": {0: [-80, 20, 0], 2.0: [-80, 20, 0]}},
        "left_leg": {"rotation": {0: [-80, -20, 0], 2.0: [-80, -20, 0]}},
        "right_arm": {"rotation": {0: [-25, 0, 0], 2.0: [-25, 0, 0]}},
    })
    a[P + "walk"] = anim(1.0, True, {
        "right_leg": {"rotation": {0: [35, 0, 0], 0.5: [-35, 0, 0], 1.0: [35, 0, 0]}},
        "left_leg": {"rotation": {0: [-35, 0, 0], 0.5: [35, 0, 0], 1.0: [-35, 0, 0]}},
        "right_arm": {"rotation": {0: [-28, 0, 3], 0.5: [28, 0, 3], 1.0: [-28, 0, 3]}},
        "left_arm": {"rotation": {0: [28, 0, -3], 0.5: [-28, 0, -3], 1.0: [28, 0, -3]}},
        "body": {"position": {0: [0, 0, 0], 0.25: [0, 0.6, 0], 0.5: [0, 0, 0], 0.75: [0, 0.6, 0], 1.0: [0, 0, 0]}},
    })
    a[P + "run"] = anim(0.6, True, {
        "right_leg": {"rotation": {0: [55, 0, 0], 0.3: [-55, 0, 0], 0.6: [55, 0, 0]}},
        "left_leg": {"rotation": {0: [-55, 0, 0], 0.3: [55, 0, 0], 0.6: [-55, 0, 0]}},
        "right_arm": {"rotation": {0: [-65, 0, 4], 0.3: [65, 0, 4], 0.6: [-65, 0, 4]}},
        "left_arm": {"rotation": {0: [65, 0, -4], 0.3: [-65, 0, -4], 0.6: [65, 0, -4]}},
        "body": {"rotation": {0: [12, 0, 0], 0.6: [12, 0, 0]},
                 "position": {0: [0, 0, 0], 0.15: [0, 1.0, 0], 0.3: [0, 0, 0], 0.45: [0, 1.0, 0], 0.6: [0, 0, 0]}},
    })
    a[P + "attack_melee"] = anim(0.8, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.2: [-160, 0, 10], 0.35: [-40, 0, 0], 0.8: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [0, 0, 0], 0.2: [-30, 0, -10], 0.35: [-10, 0, -5], 0.8: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.2: [-6, -15, 0], 0.35: [10, 20, 0], 0.8: [0, 0, 0]}},
    })
    a[P + "attack_berserk"] = anim(0.9, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.15: [-170, 0, 20], 0.3: [-20, 0, 0], 0.9: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [0, 0, 0], 0.35: [-170, 0, -20], 0.5: [-20, 0, 0], 0.9: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.15: [-8, -30, 0], 0.3: [14, 30, 0], 0.5: [14, -30, 0], 0.9: [0, 0, 0]}},
    })
    a[P + "attack_bow"] = anim(1.0, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.15: [-90, 0, 0], 0.9: [-90, 0, 0], 1.0: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [0, 0, 0], 0.15: [-85, -40, 0], 0.7: [-95, -60, 0], 0.8: [-85, -40, 0], 1.0: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.15: [0, -15, 0], 0.9: [0, -15, 0], 1.0: [0, 0, 0]}},
    })
    a[P + "attack_spell"] = anim(0.9, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.25: [-130, 0, 0], 0.45: [-80, 0, 0], 0.9: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [0, 0, 0], 0.25: [-60, 0, -30], 0.9: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.25: [-10, 0, 0], 0.45: [8, 0, 0], 0.9: [0, 0, 0]}},
    })
    a[P + "summon"] = anim(2.0, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.3: [-170, 0, 25], 1.5: [-170, 0, 25], 1.7: [-20, 0, 0], 2.0: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [0, 0, 0], 0.3: [-170, 0, -25], 1.5: [-170, 0, -25], 1.7: [-20, 0, 0], 2.0: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.3: [-10, 0, 0], 1.5: [-10, 0, 0], 1.7: [15, 0, 0], 2.0: [0, 0, 0]}},
    })
    a[P + "bless"] = anim(1.6, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.3: [-25, 0, 80], 1.2: [-25, 0, 80], 1.6: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [0, 0, 0], 0.3: [-25, 0, -80], 1.2: [-25, 0, -80], 1.6: [0, 0, 0]}},
        "body": {"position": {0: [0, 0, 0], 0.6: [0, 0.8, 0], 1.2: [0, 0.8, 0], 1.6: [0, 0, 0]}},
    })
    a[P + "work_farm"] = anim(2.4, False, {
        "body": {"rotation": {0: [0, 0, 0], 0.4: [40, 0, 0], 0.8: [25, 0, 0], 1.2: [40, 0, 0], 1.6: [25, 0, 0], 2.0: [40, 0, 0], 2.4: [0, 0, 0]}},
        "right_arm": {"rotation": {0: [0, 0, 0], 0.4: [-30, 0, 0], 0.8: [-80, 0, 0], 1.2: [-30, 0, 0], 1.6: [-80, 0, 0], 2.0: [-30, 0, 0], 2.4: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [0, 0, 0], 0.4: [-60, 0, 0], 0.8: [-20, 0, 0], 1.2: [-60, 0, 0], 1.6: [-20, 0, 0], 2.0: [-60, 0, 0], 2.4: [0, 0, 0]}},
    })
    a[P + "forge"] = anim(1.6, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.2: [-140, 0, 0], 0.4: [-50, 0, 0], 0.6: [-140, 0, 0], 0.8: [-50, 0, 0], 1.0: [-140, 0, 0], 1.2: [-50, 0, 0], 1.6: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.4: [12, 0, 0], 1.2: [12, 0, 0], 1.6: [0, 0, 0]}},
    })
    a[P + "pray"] = anim(3.0, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.5: [-65, 30, 0], 2.5: [-65, 30, 0], 3.0: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [0, 0, 0], 0.5: [-65, -30, 0], 2.5: [-65, -30, 0], 3.0: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.5: [10, 0, 0], 2.5: [10, 0, 0], 3.0: [0, 0, 0]}},
    })
    a[P + "command"] = anim(2.0, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.3: [-95, 15, 0], 0.9: [-95, -15, 0], 1.5: [-95, 15, 0], 2.0: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.3: [0, -10, 0], 1.5: [0, -10, 0], 2.0: [0, 0, 0]}},
    })
    a[P + "ritual"] = anim(2.4, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.4: [-100, 0, 20], 1.0: [-100, 0, 45], 1.6: [-100, 0, 20], 2.0: [-100, 0, 45], 2.4: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [0, 0, 0], 0.4: [-100, 0, -20], 1.0: [-100, 0, -45], 1.6: [-100, 0, -20], 2.0: [-100, 0, -45], 2.4: [0, 0, 0]}},
        "body": {"position": {0: [0, 0, 0], 1.2: [0, 1.0, 0], 2.4: [0, 0, 0]}},
    })
    a[P + "trade"] = anim(1.2, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.3: [-70, -15, 0], 0.8: [-70, -15, 0], 1.2: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.3: [8, 0, 0], 0.8: [8, 0, 0], 1.2: [0, 0, 0]}},
    })
    a[P + "tamed"] = anim(1.0, False, {
        "right_arm": {"rotation": {0: [0, 0, 0], 0.3: [-170, 0, 10], 0.7: [-170, 0, 10], 1.0: [0, 0, 0]}},
        "body": {"position": {0: [0, 0, 0], 0.3: [0, 2, 0], 0.6: [0, 0, 0], 1.0: [0, 0, 0]}},
    })
    return a


# ====================================================================== DRAGÓN
def build_dragon():
    g = Geo("geometry.nether_dragon", 512, 512)
    pk = Packer([(0, 0, 512, 512)])
    Y0 = 30  # parte baja del vientre

    def ex(bone, kind, origin, size, tag=None, inflate=0.0):
        g.cube(bone, kind, origin, size, pk.alloc(*size), inflate, tag)

    g.bone("body", [0, Y0 + 11, 0])
    ex("body", "body", [-12, Y0, -22], [24, 22, 48])
    ex("body", "body", [-10, Y0 + 3, -32], [20, 18, 10])
    ex("body", "belly", [-11, Y0 - 1, -24], [22, 2, 46])
    for i in range(10):
        ex("body", "spike", [-2, Y0 + 22, -30 + i * 5.5], [4, 5 if i % 2 else 4, 4])

    g.bone("saddle", [0, Y0 + 22, -10], "body")
    ex("saddle", "saddle", [-11, Y0 + 21, -18], [22, 3, 16])
    ex("saddle", "saddle", [-13, Y0 + 6, -12], [1, 16, 4])
    ex("saddle", "saddle", [12, Y0 + 6, -12], [1, 16, 4])
    g.bone("armor", [0, Y0 + 11, 0], "body")
    ex("armor", "armor", [-13, Y0 + 3, -24], [26, 20, 40])

    segs = [("neck1", -30, 12, 13, -35), ("neck2", -42, 12, 12, -20),
            ("neck3", -54, 10, 11, -10), ("neck4", -64, 9, 10, 15)]
    parent = "body"
    for name, z, ln, w, rot in segs:
        g.bone(name, [0, Y0 + 14, z], parent, [rot, 0, 0])
        ex(name, "neck", [-w / 2, Y0 + 14 - w / 2, z - ln], [w, w, ln])
        ex(name, "spike", [-1.5, Y0 + 14 + w / 2, z - ln + 4], [3, 4, 3])
        parent = name

    g.bone("head", [0, Y0 + 14, -73], "neck4", [38, 0, 0])
    ex("head", "head", [-7, Y0 + 8, -91], [14, 13, 18], tag="main")
    ex("head", "head", [-5, Y0 + 9, -104], [10, 8, 13], tag="snout")
    ex("head", "horn", [3, Y0 + 20, -86], [3, 3, 9])
    ex("head", "horn", [3, Y0 + 22, -77], [2, 2, 9])
    ex("head", "horn", [-6, Y0 + 20, -86], [3, 3, 9])
    ex("head", "horn", [-5, Y0 + 22, -77], [2, 2, 9])
    g.bone("jaw", [0, Y0 + 9, -78], "head")
    ex("jaw", "jaw", [-5, Y0 + 4, -103], [10, 5, 25])
    g.bone("mouth", [0, Y0 + 9, -104], "head")

    parent = "body"
    z = 26
    for i, w in enumerate([14, 12, 11, 10, 8, 7, 5, 4]):
        name = "tail%d" % (i + 1)
        g.bone(name, [0, Y0 + 12, z], parent)
        ex(name, "tail", [-w / 2, Y0 + 12 - w / 2, z], [w, w, 16])
        if i < 7:
            ex(name, "spike", [-1.5, Y0 + 12 + w / 2, z + 6], [3, 4, 3])
        parent = name
        z += 16

    def leg(prefix, sx, hz, big):
        t_w = 11 if big else 9
        x0 = 8 if sx > 0 else -8 - t_w
        g.bone("leg_%s" % prefix, [12 * sx, Y0 + 8, hz], "body")
        ex("leg_%s" % prefix, "leg", [x0, 14, hz - 5.5], [t_w, 20, 11])
        g.bone("leg_%s2" % prefix, [12 * sx, 15, hz], "leg_%s" % prefix)
        lx = 9 if sx > 0 else -17
        ex("leg_%s2" % prefix, "leg", [lx, 4, hz - 4], [8, 12, 8])
        fx = 7.5 if sx > 0 else -19.5
        ex("leg_%s2" % prefix, "foot", [fx, 0, hz - 11], [12, 4, 15], tag="claw")

    leg("fl", 1, -14, False)
    leg("fr", -1, -14, False)
    leg("hl", 1, 14, True)
    leg("hr", -1, 14, True)

    def wing(side, sx):
        b1, b2 = "wing_%s" % side, "wing_%s2" % side
        g.bone(b1, [12 * sx, Y0 + 20, -8], "body")
        ox = 12 if sx > 0 else -92
        ex(b1, "wing", [ox, Y0 + 18, -11], [80, 6, 6])
        ex(b1, "mem", [ox, Y0 + 19, -5], [80, 1, 58])
        g.bone(b2, [92 * sx, Y0 + 21, -8], b1)
        ox2 = 92 if sx > 0 else -182
        ex(b2, "wing", [ox2, Y0 + 19, -10], [90, 4, 4])
        ex(b2, "mem", [ox2, Y0 + 20, -6], [90, 1, 46])
        ex(b2, "claw", [90 if sx > 0 else -93, Y0 + 24, -11], [3, 6, 3])

    wing("l", 1)
    wing("r", -1)
    return g


D = "animation.nether_dragon."


def dragon_animations():
    a = {}
    a[D + "idle"] = anim(4.0, True, {
        "body": {"position": {0: [0, 0, 0], 2.0: [0, 0.6, 0], 4.0: [0, 0, 0]}},
        "neck1": {"rotation": {0: [-35, 0, 0], 2.0: [-33, 3, 0], 4.0: [-35, 0, 0]}},
        "head": {"rotation": {0: [38, 0, 0], 2.0: [34, -4, 0], 4.0: [38, 0, 0]}},
        "tail1": {"rotation": {0: [0, 0, 0], 2.0: [0, 6, 0], 4.0: [0, 0, 0]}},
        "tail3": {"rotation": {0: [0, 0, 0], 2.0: [0, 8, 0], 4.0: [0, 0, 0]}},
        "tail5": {"rotation": {0: [0, 0, 0], 2.0: [0, 10, 0], 4.0: [0, 0, 0]}},
        "wing_l": {"rotation": {0: [0, 0, 12], 2.0: [0, 0, 16], 4.0: [0, 0, 12]}},
        "wing_r": {"rotation": {0: [0, 0, -12], 2.0: [0, 0, -16], 4.0: [0, 0, -12]}},
        "wing_l2": {"rotation": {0: [0, 0, 6], 4.0: [0, 0, 6]}},
        "wing_r2": {"rotation": {0: [0, 0, -6], 4.0: [0, 0, -6]}},
    })
    a[D + "walk"] = anim(1.2, True, {
        "leg_fl": {"rotation": {0: [25, 0, 0], 0.6: [-25, 0, 0], 1.2: [25, 0, 0]}},
        "leg_hr": {"rotation": {0: [25, 0, 0], 0.6: [-25, 0, 0], 1.2: [25, 0, 0]}},
        "leg_fr": {"rotation": {0: [-25, 0, 0], 0.6: [25, 0, 0], 1.2: [-25, 0, 0]}},
        "leg_hl": {"rotation": {0: [-25, 0, 0], 0.6: [25, 0, 0], 1.2: [-25, 0, 0]}},
        "body": {"position": {0: [0, 0, 0], 0.3: [0, 1.2, 0], 0.6: [0, 0, 0], 0.9: [0, 1.2, 0], 1.2: [0, 0, 0]}},
        "tail1": {"rotation": {0: [0, -8, 0], 0.6: [0, 8, 0], 1.2: [0, -8, 0]}},
        "tail4": {"rotation": {0: [0, 10, 0], 0.6: [0, -10, 0], 1.2: [0, 10, 0]}},
        "tail7": {"rotation": {0: [0, -12, 0], 0.6: [0, 12, 0], 1.2: [0, -12, 0]}},
        "neck1": {"rotation": {0: [-35, -4, 0], 0.6: [-35, 4, 0], 1.2: [-35, -4, 0]}},
        "wing_l": {"rotation": {0: [0, 0, 14], 0.6: [0, 0, 22], 1.2: [0, 0, 14]}},
        "wing_r": {"rotation": {0: [0, 0, -14], 0.6: [0, 0, -22], 1.2: [0, 0, -14]}},
    })
    a[D + "fly"] = anim(1.0, True, {
        "wing_l": {"rotation": {0: [0, 0, 50], 0.5: [0, 0, -38], 1.0: [0, 0, 50]}},
        "wing_r": {"rotation": {0: [0, 0, -50], 0.5: [0, 0, 38], 1.0: [0, 0, -50]}},
        "wing_l2": {"rotation": {0: [0, 0, 20], 0.25: [0, 0, -6], 0.5: [0, 0, -40], 0.75: [0, 0, -6], 1.0: [0, 0, 20]}},
        "wing_r2": {"rotation": {0: [0, 0, -20], 0.25: [0, 0, 6], 0.5: [0, 0, 40], 0.75: [0, 0, 6], 1.0: [0, 0, -20]}},
        "body": {"position": {0: [0, 1.5, 0], 0.5: [0, -1.5, 0], 1.0: [0, 1.5, 0]}},
        "leg_fl": {"rotation": {0: [-35, 0, 0], 1.0: [-35, 0, 0]}},
        "leg_fr": {"rotation": {0: [-35, 0, 0], 1.0: [-35, 0, 0]}},
        "leg_hl": {"rotation": {0: [35, 0, 0], 1.0: [35, 0, 0]}},
        "leg_hr": {"rotation": {0: [35, 0, 0], 1.0: [35, 0, 0]}},
        "tail1": {"rotation": {0: [4, 0, 0], 0.5: [-4, 0, 0], 1.0: [4, 0, 0]}},
        "tail4": {"rotation": {0: [-6, 0, 0], 0.5: [6, 0, 0], 1.0: [-6, 0, 0]}},
        "tail7": {"rotation": {0: [8, 0, 0], 0.5: [-8, 0, 0], 1.0: [8, 0, 0]}},
        "neck1": {"rotation": {0: [-30, 0, 0], 0.5: [-38, 0, 0], 1.0: [-30, 0, 0]}},
    })
    a[D + "glide"] = anim(3.0, True, {
        "wing_l": {"rotation": {0: [0, 0, -5], 1.5: [0, 0, 0], 3.0: [0, 0, -5]}},
        "wing_r": {"rotation": {0: [0, 0, 5], 1.5: [0, 0, 0], 3.0: [0, 0, 5]}},
        "leg_fl": {"rotation": {0: [-35, 0, 0], 3.0: [-35, 0, 0]}},
        "leg_fr": {"rotation": {0: [-35, 0, 0], 3.0: [-35, 0, 0]}},
        "leg_hl": {"rotation": {0: [35, 0, 0], 3.0: [35, 0, 0]}},
        "leg_hr": {"rotation": {0: [35, 0, 0], 3.0: [35, 0, 0]}},
        "tail4": {"rotation": {0: [0, -5, 0], 1.5: [0, 5, 0], 3.0: [0, -5, 0]}},
    })
    a[D + "sit"] = anim(4.0, True, {
        "body": {"position": {0: [0, -12, 0], 4.0: [0, -12, 0]}},
        "leg_hl": {"rotation": {0: [-70, 0, 0], 4.0: [-70, 0, 0]}},
        "leg_hr": {"rotation": {0: [-70, 0, 0], 4.0: [-70, 0, 0]}},
        "leg_fl": {"rotation": {0: [10, 0, 0], 4.0: [10, 0, 0]}},
        "leg_fr": {"rotation": {0: [10, 0, 0], 4.0: [10, 0, 0]}},
        "neck1": {"rotation": {0: [-38, 0, 0], 2.0: [-34, 2, 0], 4.0: [-38, 0, 0]}},
        "wing_l": {"rotation": {0: [0, 0, 8], 4.0: [0, 0, 8]}},
        "wing_r": {"rotation": {0: [0, 0, -8], 4.0: [0, 0, -8]}},
    })
    a[D + "bite"] = anim(0.7, False, {
        "neck1": {"rotation": {0: [-35, 0, 0], 0.2: [-50, 0, 0], 0.35: [-15, 0, 0], 0.7: [-35, 0, 0]}},
        "head": {"rotation": {0: [38, 0, 0], 0.2: [30, 0, 0], 0.35: [52, 0, 0], 0.7: [38, 0, 0]}},
        "jaw": {"rotation": {0: [0, 0, 0], 0.2: [35, 0, 0], 0.35: [0, 0, 0], 0.7: [0, 0, 0]}},
    })
    a[D + "breath"] = anim(1.6, False, {
        "neck1": {"rotation": {0: [-35, 0, 0], 0.3: [-55, 0, 0], 1.4: [-55, 0, 0], 1.6: [-35, 0, 0]}},
        "head": {"rotation": {0: [38, 0, 0], 0.3: [20, 0, 0], 1.4: [20, 0, 0], 1.6: [38, 0, 0]}},
        "jaw": {"rotation": {0: [0, 0, 0], 0.3: [40, 0, 0], 1.4: [40, 0, 0], 1.6: [0, 0, 0]}},
        "body": {"rotation": {0: [0, 0, 0], 0.3: [-6, 0, 0], 1.4: [-6, 0, 0], 1.6: [0, 0, 0]}},
    })
    a[D + "roar"] = anim(1.4, False, {
        "neck1": {"rotation": {0: [-35, 0, 0], 0.3: [-60, 0, 0], 1.1: [-60, 0, 0], 1.4: [-35, 0, 0]}},
        "jaw": {"rotation": {0: [0, 0, 0], 0.3: [45, 0, 0], 1.1: [45, 0, 0], 1.4: [0, 0, 0]}},
        "wing_l": {"rotation": {0: [0, 0, 12], 0.3: [0, 0, -60], 1.1: [0, 0, -60], 1.4: [0, 0, 12]}},
        "wing_r": {"rotation": {0: [0, 0, -12], 0.3: [0, 0, 60], 1.1: [0, 0, 60], 1.4: [0, 0, -12]}},
    })
    return a


def write_all():
    # el dragón lo crea dragon_v2.py (modelo Void Dragon + cabeza nueva)
    return None, None


def flip_y(anims):
    """Invierte el giro Y de todas las animaciones (corrección para las que se diseñaron con la vista previa
    antigua, que mostraba el eje Y al revés que GeckoLib). Así en el juego se ven igual que en las fotos aprobadas."""
    for an in anims.values():
        for chans in an["bones"].values():
            rot = chans.get("rotation")
            if rot:
                for k, v in rot.items():
                    rot[k] = [v[0], -v[1], v[2]]
    return anims
