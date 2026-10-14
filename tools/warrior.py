"""Guerrero del Nether: convierte el modelo de Blockbench del usuario (nether_zero_warrior.bbmodel) a GeckoLib,
le añade el punto de agarre de la espada de rubí y crea sus animaciones.

Salida:
  assets/.../geo/entity/warrior.geo.json
  assets/.../animations/entity/warrior.animation.json
  assets/.../textures/entity/warrior.png      (64 x 68: se repiten las últimas filas para las caras que el
                                                modelo original lee más allá del píxel 64)
"""
import base64
import io
import json
import os
from PIL import Image
from common import ASSETS, save_json
from models import Geo, anim, flip_y

HERE = os.path.dirname(os.path.abspath(__file__))
BBMODEL = os.path.join(HERE, "ref", "nether_zero_warrior.bbmodel")
TEX_H = 68

# elemento de Blockbench -> hueso de GeckoLib
BONE_OF = {"head": "head", "headwear": "head", "body": "body", "jacket": "body",
           "left_arm": "left_arm", "left_sleeve": "left_arm", "right_arm": "right_arm", "right_sleeve": "right_arm",
           "left_leg": "left_leg", "left_pants": "left_leg", "right_leg": "right_leg", "right_pants": "right_leg"}


def load_bbmodel():
    m = json.load(open(BBMODEL, encoding="utf-8"))
    src = m["textures"][0]["source"].split(",", 1)[1]
    tex = Image.open(io.BytesIO(base64.b64decode(src))).convert("RGBA")
    return m, tex


def build_geo():
    m, tex = load_bbmodel()
    g = Geo("geometry.nether_warrior", 64, TEX_H)
    # Coordenadas Bedrock: la X se invierte respecto de Blockbench (derecha del mob = -X)
    g.bone("body", [0, 13, 0])
    g.bone("head", [0, 26, 0], "body")
    g.bone("right_arm", [-6, 24, 0], "body")
    g.bone("right_hand_item", [-6, 13, -0.5], "right_arm")
    g.bone("left_arm", [6, 24, 0], "body")
    g.bone("left_hand_item", [6, 13, -0.5], "left_arm")
    g.bone("right_leg", [-2, 13, 0])
    g.bone("left_leg", [2, 13, 0])
    for e in m["elements"]:
        f, t = e["from"], e["to"]
        origin = [-t[0], f[1], f[2]]
        size = [t[i] - f[i] for i in range(3)]
        uv = e.get("uv_offset", [0, 0])
        g.cube(BONE_OF[e["name"]], e["name"], origin, size, uv, e.get("inflate", 0.0))
    # textura: 64x68, repitiendo la última fila (como hace Blockbench con "limited")
    out = Image.new("RGBA", (64, TEX_H))
    out.paste(tex, (0, 0))
    for y in range(64, TEX_H):
        out.paste(tex.crop((0, 63, 64, 64)), (0, y))
    return g, out


A = "animation.nether_warrior."


def animations():
    a = {}
    # Reposo: respira, espada lista en la mano derecha
    a[A + "idle"] = anim(2.4, True, {
        "body": {"position": {0: [0, 0, 0], 1.2: [0, 0.3, 0], 2.4: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 1.2: [2, 0, 0], 2.4: [0, 0, 0]}},
        "right_arm": {"rotation": {0: [-14, 0, 6], 1.2: [-17, 0, 7], 2.4: [-14, 0, 6]}},
        "left_arm": {"rotation": {0: [0, 0, -5], 1.2: [-2, 0, -7], 2.4: [0, 0, -5]}},
    })
    # Caminar: piernas y brazo izquierdo alternados; el brazo de la espada se mueve poco
    a[A + "walk"] = anim(1.0, True, {
        "right_leg": {"rotation": {0: [-32, 0, 0], 0.5: [32, 0, 0], 1.0: [-32, 0, 0]}},
        "left_leg": {"rotation": {0: [32, 0, 0], 0.5: [-32, 0, 0], 1.0: [32, 0, 0]}},
        "left_arm": {"rotation": {0: [-30, 0, -4], 0.5: [30, 0, -4], 1.0: [-30, 0, -4]}},
        "right_arm": {"rotation": {0: [-4, 0, 6], 0.5: [-24, 0, 6], 1.0: [-4, 0, 6]}},
        "body": {"position": {0: [0, 0, 0], 0.25: [0, 0.7, 0], 0.5: [0, 0, 0], 0.75: [0, 0.7, 0], 1.0: [0, 0, 0]},
                 "rotation": {0: [0, 4, 0], 0.5: [0, -4, 0], 1.0: [0, 4, 0]}},
        "head": {"rotation": {0: [0, -4, 0], 0.5: [0, 4, 0], 1.0: [0, -4, 0]}},
    })
    # Correr (persiguiendo un enemigo): inclinado hacia adelante, espada al frente
    a[A + "run"] = anim(0.6, True, {
        "right_leg": {"rotation": {0: [-50, 0, 0], 0.3: [45, 0, 0], 0.6: [-50, 0, 0]}},
        "left_leg": {"rotation": {0: [45, 0, 0], 0.3: [-50, 0, 0], 0.6: [45, 0, 0]}},
        "left_arm": {"rotation": {0: [-55, 0, -6], 0.3: [50, 0, -6], 0.6: [-55, 0, -6]}},
        "right_arm": {"rotation": {0: [-45, 0, 8], 0.3: [-60, 0, 8], 0.6: [-45, 0, 8]}},
        "body": {"rotation": {0: [12, 0, 0], 0.6: [12, 0, 0]},
                 "position": {0: [0, 0, 0], 0.15: [0, 1.2, 0], 0.3: [0, 0, 0], 0.45: [0, 1.2, 0], 0.6: [0, 0, 0]}},
        "head": {"rotation": {0: [-10, 0, 0], 0.6: [-10, 0, 0]}},
    })
    # Ataque 1: tajo vertical desde arriba
    a[A + "attack_slash"] = anim(0.75, False, {
        "right_arm": {"rotation": {0: [-14, 0, 6], 0.25: [-170, -10, 20], 0.38: [-30, 10, 0], 0.55: [-10, 0, 4], 0.75: [-14, 0, 6]}},
        "left_arm": {"rotation": {0: [0, 0, -5], 0.25: [-35, 0, -20], 0.38: [10, 0, -8], 0.75: [0, 0, -5]}},
        "body": {"rotation": {0: [0, 0, 0], 0.25: [-8, -18, 0], 0.38: [14, 22, 0], 0.55: [6, 8, 0], 0.75: [0, 0, 0]}},
        "right_leg": {"rotation": {0: [0, 0, 0], 0.25: [10, 0, 0], 0.38: [-18, 0, 0], 0.75: [0, 0, 0]}},
        "left_leg": {"rotation": {0: [0, 0, 0], 0.38: [16, 0, 0], 0.75: [0, 0, 0]}},
    })
    # Ataque 2: tajo horizontal (barrido)
    a[A + "attack_sweep"] = anim(0.8, False, {
        "right_arm": {"rotation": {0: [-14, 0, 6], 0.25: [-90, 70, 0], 0.42: [-90, -60, 0], 0.6: [-40, -20, 0], 0.8: [-14, 0, 6]}},
        "body": {"rotation": {0: [0, 0, 0], 0.25: [0, 35, 0], 0.42: [6, -35, 0], 0.6: [0, -10, 0], 0.8: [0, 0, 0]}},
        "left_arm": {"rotation": {0: [0, 0, -5], 0.25: [-20, 0, -30], 0.42: [-10, 0, -10], 0.8: [0, 0, -5]}},
    })
    # Sentado (cuando se lo ordenas)
    a[A + "sit"] = anim(2.0, True, {
        "body": {"position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "right_leg": {"rotation": {0: [-90, 10, 0], 2.0: [-90, 10, 0]}, "position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "left_leg": {"rotation": {0: [-90, -10, 0], 2.0: [-90, -10, 0]}, "position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "right_arm": {"rotation": {0: [-35, 0, 6], 2.0: [-35, 0, 6]}},
        "left_arm": {"rotation": {0: [-30, 0, -6], 2.0: [-30, 0, -6]}},
    })
    # Celebración al ser domesticado: alza la espada
    a[A + "tamed"] = anim(1.2, False, {
        "right_arm": {"rotation": {0: [-14, 0, 6], 0.3: [-175, 0, 10], 0.9: [-175, 0, 10], 1.2: [-14, 0, 6]}},
        "body": {"position": {0: [0, 0, 0], 0.3: [0, 2, 0], 0.6: [0, 0, 0], 1.2: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.3: [-20, 0, 0], 0.9: [-20, 0, 0], 1.2: [0, 0, 0]}},
    })
    return a


def write_all():
    g, tex = build_geo()
    save_json(os.path.join(ASSETS, "geo", "entity", "warrior.geo.json"), g.to_json())
    save_json(os.path.join(ASSETS, "animations", "entity", "warrior.animation.json"),
              {"format_version": "1.8.0", "animations": flip_y(animations())})
    os.makedirs(os.path.join(ASSETS, "textures", "entity"), exist_ok=True)
    tex.save(os.path.join(ASSETS, "textures", "entity", "warrior.png"))
    return g, tex


# ------------------------------------------------------------------ vista previa animada (GIF)
def sample(anim_def, t):
    """Pose de cada hueso en el tiempo t (interpolación lineal, como GeckoLib con 'linear')."""
    length = anim_def["animation_length"]
    if anim_def.get("loop"):
        t = t % length
    pose = {}
    for bone, chans in anim_def["bones"].items():
        pose[bone] = {}
        for ch, frames in chans.items():
            ks = sorted((float(k), v) for k, v in frames.items())
            if t <= ks[0][0]:
                val = ks[0][1]
            elif t >= ks[-1][0]:
                val = ks[-1][1]
            else:
                for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
                    if t0 <= t <= t1:
                        f = (t - t0) / (t1 - t0) if t1 > t0 else 0
                        val = [v0[i] + (v1[i] - v0[i]) * f for i in range(3)]
                        break
            pose[bone][ch] = val
    return pose
