"""Dragón Infernal: modelo del usuario (dragon_infernal.gltf convertido), skin del Nether y todas sus animaciones.

Las animaciones tienen los mismos nombres que las del Dragón del Nether (idle, walk, run, rest, fly, glide, hover,
bite, breath, roar, takeoff) más "grab" (agarra a un mob con las patas) para que use la misma IA.
"""
import json
import math
import os
import shutil

from common import ASSETS
from fauna import wave, anim

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref", "infernal")
P = "animation.dragon_infernal."
NECKS = ["neck", "neck2", "neck3", "neck4", "neck5"]
TAILS = ["tail"] + ["tail%d" % i for i in range(2, 13)]
LIFT_GROUND = 46    # las patas delanteras estiradas tocan el suelo
LIFT_AIR = 25       # en el aire el cuerpo queda al medio de la caja de colisión
WING_FOLD = (60, 30, -60)   # alas plegadas a los costados (y, z, punta z)


def merge(*parts):
    out = {}
    for p in parts:
        for bone, chans in p.items():
            out.setdefault(bone, {}).update(chans)
    return out


def const(v):
    return {"0.0": list(v)}


def legs_ground(swing=0.0, L=1.0, lift_feet=0.0):
    """Patas para estar en el suelo: delanteras rectas y traseras dobladas (rodilla adelante, talón atrás)."""
    d = {}
    for side in ("", "1"):
        ph = 0.0 if side == "" else math.pi
        if swing:
            d["frontleg" + side] = {"rotation": wave(swing, L, steps=8, axis=0, phase=ph, extra=[-65, 0, 0])}
            d["rearleg" + side] = {"rotation": wave(swing, L, steps=8, axis=0, phase=ph + math.pi, extra=[-103, 0, 0])}
            d["frontlegtip" + side] = {"rotation": wave(swing * 0.6, L, steps=8, axis=0, phase=ph - 1.2, extra=[20, 0, 0])}
            d["rearlegtip" + side] = {"rotation": wave(swing * 0.6, L, steps=8, axis=0, phase=ph + math.pi - 1.2, extra=[61, 0, 0])}
        else:
            d["frontleg" + side] = {"rotation": const([-65, 0, 0])}
            d["rearleg" + side] = {"rotation": const([-103, 0, 0])}
            d["frontlegtip" + side] = {"rotation": const([20, 0, 0])}
            d["rearlegtip" + side] = {"rotation": const([61, 0, 0])}
        d["frontfoot" + side] = {"rotation": const([-45, 0, 0])}
        d["rearfoot" + side] = {"rotation": const([-88, 0, 0])}
    return d


def wings_folded(breathe=0.0, L=3.0):
    wy, wz, wt = WING_FOLD
    if breathe:
        return {"wing": {"rotation": wave(breathe, L, steps=8, axis=2, extra=[0, wy, wz])},
                "wing1": {"rotation": wave(-breathe, L, steps=8, axis=2, extra=[0, -wy, -wz])},
                "wingtip": {"rotation": const([0, 0, wt])}, "wingtip1": {"rotation": const([0, 0, -wt])}}
    return {"wing": {"rotation": const([0, wy, wz])}, "wing1": {"rotation": const([0, -wy, -wz])},
            "wingtip": {"rotation": const([0, 0, wt])}, "wingtip1": {"rotation": const([0, 0, -wt])}}


def neck_up(base=-8.0, amp=1.5, L=3.0):
    d = {}
    for k, n in enumerate(NECKS):
        d[n] = {"rotation": wave(amp, L, steps=8, axis=0, phase=-0.4 * k, extra=[base if k < 2 else 0.0, 0, 0])}
    d["head"] = {"rotation": wave(amp, L, steps=8, axis=0, phase=-2.0, extra=[-base * 1.4, 0, 0])}
    return d


def tail_sway(amp=4.0, L=3.0):
    return {t: {"rotation": wave(amp * (0.4 + k * 0.08), L, steps=8, axis=1, phase=-0.45 * k)} for k, t in enumerate(TAILS)}


def build():
    with open(os.path.join(REF, "anims_base.json")) as f:
        anims = json.load(f)["animations"]      # fly, glide, roar, bite, breath (ya mostradas al usuario)
    for k in ("fly", "glide"):
        anims[P + k]["bones"]["root"] = {"position": const([0, LIFT_AIR, 0])}
    ground = {"root": {"position": const([0, LIFT_GROUND, 0])}}
    # quieto: respira, mueve la cola y mira
    L = 3.0
    anims[P + "idle"] = anim(merge(ground, legs_ground(), wings_folded(2.0, L), neck_up(-10, 1.5, L), tail_sway(3.0, L),
                                   {"body": {"position": wave(0.4, L, steps=8, axis=1)}}), L)
    # caminar y correr
    L = 1.6
    walk = merge(legs_ground(22, L), wings_folded(1.0, L), neck_up(-8, 2.0, L / 2), tail_sway(5.0, L),
                 {"root": {"position": wave(1.2, L / 2, steps=4, axis=1, extra=[0, LIFT_GROUND, 0])}})
    anims[P + "walk"] = anim(walk, L)
    L = 0.9
    run = merge(legs_ground(36, L), wings_folded(4.0, L), neck_up(-4, 3.0, L / 2), tail_sway(7.0, L),
                {"root": {"position": wave(2.2, L / 2, steps=4, axis=1, extra=[0, LIFT_GROUND, 0])}})
    anims[P + "run"] = anim(run, L)
    # descansar: echado en el suelo, patas recogidas, cuello y cabeza abajo, cola enroscada
    L = 4.0
    rest = {"root": {"position": const([0, 5, 0])}}
    for side in ("", "1"):
        rest["frontleg" + side] = {"rotation": const([25, 0, 0])}
        rest["frontlegtip" + side] = {"rotation": const([-160, 0, 0])}
        rest["frontfoot" + side] = {"rotation": const([40, 0, 0])}
        rest["rearleg" + side] = {"rotation": const([30, 0, 0])}
        rest["rearlegtip" + side] = {"rotation": const([120, 0, 0])}
        rest["rearfoot" + side] = {"rotation": const([40, 0, 0])}
    for k, n in enumerate(NECKS):
        rest[n] = {"rotation": wave(0.8, L, steps=8, axis=0, phase=-0.4 * k, extra=[4, 8 if k > 1 else 0, 0])}
    rest["head"] = {"rotation": const([6, 6, 0])}
    for k, t in enumerate(TAILS):
        rest[t] = {"rotation": wave(1.0, L, steps=8, axis=1, phase=-0.4 * k, extra=[0, -9, 0])}
    anims[P + "rest"] = anim(merge(rest, wings_folded(1.0, L)), L)
    # en el aire sin avanzar: aleteo rápido, cuerpo erguido y patas colgando
    L = 1.1
    hover = json.loads(json.dumps(anims[P + "fly"]["bones"]))
    for b in ("wing", "wing1", "wingtip", "wingtip1"):
        for t, v in hover[b]["rotation"].items():
            hover[b]["rotation"][t] = [x * 1.25 for x in v]
    hover = {b: {ch: {"%.2f" % (float(t) * L / 1.6): v for t, v in fr.items()} for ch, fr in chans.items()} for b, chans in hover.items()}
    hover["root"] = {"position": wave(2.0, L, steps=8, axis=1, phase=math.pi, extra=[0, LIFT_AIR + 6, 0]),
                     "rotation": const([-14, 0, 0])}
    for side in ("", "1"):
        hover["frontleg" + side] = {"rotation": wave(5, L, steps=8, axis=0, extra=[-35, 0, 0])}
        hover["rearleg" + side] = {"rotation": wave(5, L, steps=8, axis=0, phase=0.8, extra=[-40, 0, 0])}
    anims[P + "hover"] = anim(hover, L)
    # despegue: se agacha, salta y da dos aletazos fuertes mientras recoge las patas
    up = {"root": {"position": {"0.0": [0, LIFT_GROUND, 0], "0.25": [0, LIFT_GROUND - 10, 0], "0.5": [0, LIFT_GROUND + 6, 0],
                                "1.2": [0, LIFT_AIR, 0]}},
          "wing": {"rotation": {"0.0": [0, 60, 30], "0.3": [0, 0, 55], "0.55": [0, 0, -35], "0.8": [0, 0, 45], "1.05": [0, 0, -30], "1.2": [0, 0, 0]}},
          "wing1": {"rotation": {"0.0": [0, -60, -30], "0.3": [0, 0, -55], "0.55": [0, 0, 35], "0.8": [0, 0, -45], "1.05": [0, 0, 30], "1.2": [0, 0, 0]}},
          "wingtip": {"rotation": {"0.0": [0, 0, -60], "0.35": [0, 0, 30], "0.6": [0, 0, -25], "0.85": [0, 0, 30], "1.2": [0, 0, 0]}},
          "wingtip1": {"rotation": {"0.0": [0, 0, 60], "0.35": [0, 0, -30], "0.6": [0, 0, 25], "0.85": [0, 0, -30], "1.2": [0, 0, 0]}},
          "neck": {"rotation": {"0.0": [-10, 0, 0], "0.5": [-16, 0, 0], "1.2": [0, 0, 0]}}}
    for side in ("", "1"):
        up["frontleg" + side] = {"rotation": {"0.0": [-65, 0, 0], "0.5": [-65, 0, 0], "1.2": [0, 0, 0]}}
        up["frontlegtip" + side] = {"rotation": {"0.0": [20, 0, 0], "0.5": [20, 0, 0], "1.2": [0, 0, 0]}}
        up["frontfoot" + side] = {"rotation": {"0.0": [-45, 0, 0], "0.5": [-45, 0, 0], "1.2": [0, 0, 0]}}
        up["rearleg" + side] = {"rotation": {"0.0": [-103, 0, 0], "0.3": [-120, 0, 0], "0.55": [-60, 0, 0], "1.2": [0, 0, 0]}}
        up["rearlegtip" + side] = {"rotation": {"0.0": [61, 0, 0], "0.3": [90, 0, 0], "0.55": [20, 0, 0], "1.2": [0, 0, 0]}}
        up["rearfoot" + side] = {"rotation": {"0.0": [-88, 0, 0], "0.55": [-30, 0, 0], "1.2": [0, 0, 0]}}
    anims[P + "takeoff"] = anim(up, 1.2, loop=False)
    # agarrar: patas delanteras hacia adelante y abajo, garras cerradas, y un rugido corto
    grab = {"neck": {"rotation": {"0.0": [0, 0, 0], "0.3": [-10, 0, 0], "1.0": [0, 0, 0]}},
            "jaw": {"rotation": {"0.0": [0, 0, 0], "0.25": [30, 0, 0], "0.7": [0, 0, 0]}}}
    for side in ("", "1"):
        grab["frontleg" + side] = {"rotation": {"0.0": [0, 0, 0], "0.3": [-100, 0, 0], "0.6": [-80, 0, 0], "1.0": [-70, 0, 0]}}
        grab["frontfoot" + side] = {"rotation": {"0.0": [0, 0, 0], "0.3": [-30, 0, 0], "0.6": [40, 0, 0], "1.0": [40, 0, 0]}}
        grab["rearleg" + side] = {"rotation": {"0.0": [0, 0, 0], "0.3": [-60, 0, 0], "1.0": [-50, 0, 0]}}
    anims[P + "grab"] = anim(grab, 1.0, loop=False)
    # llevar algo agarrado (en bucle, sobre el vuelo): patas delanteras abrazando lo que lleva
    carry = {}
    for side in ("", "1"):
        carry["frontleg" + side] = {"rotation": const([-70, 0, 0])}
        carry["frontfoot" + side] = {"rotation": const([40, 0, 0])}
        carry["rearleg" + side] = {"rotation": const([-50, 0, 0])}
    anims[P + "carry"] = anim(carry, 1.0)
    return anims


def write_all():
    geo_dir = os.path.join(ASSETS, "geo", "entity")
    shutil.copy(os.path.join(REF, "dragon_infernal.geo.json"), os.path.join(geo_dir, "dragon_infernal.geo.json"))
    tex_dir = os.path.join(ASSETS, "textures", "entity")
    shutil.copy(os.path.join(REF, "dragon_infernal.png"), os.path.join(tex_dir, "dragon_infernal.png"))
    shutil.copy(os.path.join(REF, "dragon_infernal_glowmask.png"), os.path.join(tex_dir, "dragon_infernal_glowmask.png"))
    out = os.path.join(ASSETS, "animations", "entity", "dragon_infernal.animation.json")
    with open(out, "w") as f:
        json.dump({"format_version": "1.8.0", "animations": build()}, f, indent=1)


if __name__ == "__main__":
    write_all()
