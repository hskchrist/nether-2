"""Humanos nuevos del Reino del Nether.

- Profesiones con hombre y mujer (skins del usuario en tools/ref/humanos): bibliotecario, domador, granjero,
  minero y ciudadano. Usan el cuerpo del guerrero (formato de skin de 64x64; se guardan en 64x68 repitiendo
  la última fila, como el guerrero).
- Versiones mujer del guerrero, arquero, guerrero real y ballestero (pelo largo pintado sobre su skin).
- Aldeano Necromancer: modelo de aldeano del usuario (tools/ref/aldeano_necromancer_modelo.java.txt) con
  brazos cruzados, skin del usuario (tools/ref/humanos/aldeano_necromancer_skin.png) y animaciones.
- Animaciones de las profesiones (reposo, caminar, correr, golpe, trabajar en su mesa, sentarse, festejar).

Salida en assets/civilizacion_nether/: textures/entity/human/*.png (+ _glowmask), geo/entity/aldeano_necromancer.geo.json,
animations/entity/human.animation.json y aldeano_necromancer.animation.json.
"""
import os
import random
from PIL import Image
from common import ASSETS, save_json
from models import Geo, anim

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref", "humanos")
ENT = os.path.join(ASSETS, "textures", "entity")
HUMAN = os.path.join(ENT, "human")

# profesión -> (skins de hombre, skins de mujer)   (debe coincidir con HumanoidType.java)
PROFESSIONS = {"bibliotecario": (3, 3), "domador": (3, 3), "granjero": (4, 4), "minero": (6, 5), "ciudadano": (1, 1)}
# soldados: textura base -> versión mujer
SOLDIERS = {"warrior": "normal", "archer": "hood", "royal_warrior": "helmet", "crossbowman": "cap"}


def pad68(img):
    out = Image.new("RGBA", (64, 68))
    out.paste(img.crop((0, 0, 64, 64)), (0, 0))
    for y in range(64, 68):
        out.paste(img.crop((0, 63, 64, 64)), (0, y))
    return out


def glowmask(img):
    """Brillan solo los ojos: píxeles muy saturados y claros en la franja de los ojos de la cara (capa y sombrero)."""
    gm = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for (x0, x1) in ((8, 16), (40, 48)):
        for y in range(10, 14):
            for x in range(x0, x1):
                r, g, b, a = img.getpixel((x, y))
                if a and max(r, g, b) > 170 and max(r, g, b) - min(r, g, b) > 120:
                    gm.putpixel((x, y), (r, g, b, 255))
    return gm


def save_tex(img, name, folder=HUMAN):
    os.makedirs(folder, exist_ok=True)
    img.save(os.path.join(folder, name + ".png"))
    glowmask(img).save(os.path.join(folder, name + "_glowmask.png"))


def write_profession_skins():
    count = 0
    for prof, (nm, nf) in PROFESSIONS.items():
        for g, n in (("m", nm), ("f", nf)):
            for i in range(n):
                src = Image.open(os.path.join(REF, "%s_%s_%d.png" % (prof, g, i))).convert("RGBA")
                save_tex(pad68(src), "%s_%s_%d" % (prof, g, i))
                count += 1
    return count


# ---------------------------------------------------------------- pelo largo para las mujeres soldado
HAIR = [(46, 14, 16), (78, 24, 22), (112, 38, 30), (150, 60, 40)]


def hair_px(x, y, rnd):
    k = (x * 7 + y * 3 + rnd.randint(0, 2)) % 5
    return HAIR[0] if k == 0 else (HAIR[2] if k == 4 else HAIR[1])


def put(img, x, y, c):
    img.putpixel((x, y), tuple(c) + (255,))


def long_hair(img, style, seed=3):
    rnd = random.Random(seed)
    img = img.copy()
    if style in ("normal", "cap"):
        for x in range(8, 16):            # coronilla
            for y in range(0, 8):
                put(img, x, y, hair_px(x, y, rnd))
        for x in range(24, 32):           # nuca
            for y in range(8, 16):
                put(img, x, y, hair_px(x, y, rnd))
        for y in range(8, 16):            # costados (la parte delantera de abajo queda libre: mejilla)
            for x in range(0, 8):
                if x <= 4 or y <= 10:
                    put(img, x, y, hair_px(x, y, rnd))
            for x in range(16, 24):
                if x >= 19 or y <= 10:
                    put(img, x, y, hair_px(x, y, rnd))
        for x in range(8, 16):            # flequillo
            put(img, x, 8, hair_px(x, 8, rnd))
        for x in (9, 10, 13, 14):
            put(img, x, 9, HAIR[1] if x in (9, 14) else HAIR[2])
        for y in range(9, 16):            # mechones que enmarcan la cara
            put(img, 8, y, HAIR[1])
            put(img, 15, y, HAIR[1])
    if style == "hood":
        for y in range(10, 16):
            put(img, 8, y, HAIR[1])
            put(img, 15, y, HAIR[1])
        put(img, 9, 15, HAIR[2])
        put(img, 14, 15, HAIR[2])
    if style == "helmet":
        # visera abierta: se ve la cara con flequillo y mechones
        for y in range(10, 15):
            for x in range(41, 47):
                img.putpixel((x, y), (0, 0, 0, 0))
        for x in range(8, 16):
            put(img, x, 9, hair_px(x, 9, rnd))
        for y in range(10, 16):
            put(img, 8, y, HAIR[1])
            put(img, 15, y, HAIR[1])
    # melena larga por la espalda (capa exterior del torso: se ve sobre la armadura)
    for y in range(36, 44):
        w = 3 if y < 41 else 2
        for x in range(36 - w, 36 + w):
            put(img, x, y, hair_px(x, y, rnd) if y < 43 else HAIR[0])
    return img


def write_soldier_females():
    for base, style in SOLDIERS.items():
        src = Image.open(os.path.join(ENT, base + ".png")).convert("RGBA")
        f = long_hair(src, style)
        f.save(os.path.join(ENT, base + "_f.png"))
        red_glow(f).save(os.path.join(ENT, base + "_f_glowmask.png"))
        if not os.path.exists(os.path.join(ENT, base + "_glowmask.png")):
            red_glow(src).save(os.path.join(ENT, base + "_glowmask.png"))


def red_glow(img):
    """Como los soldados originales: brillan los ojos rojos y los rubíes."""
    gm = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if a and r > 200 and g < 70 and b < 70:
                gm.putpixel((x, y), (r, g, b, a))
    return gm


# ---------------------------------------------------------------- animaciones de las profesiones
H = "animation.nether_human."


def human_animations():
    a = {}
    a[H + "idle"] = anim(3.0, True, {
        "body": {"position": {0: [0, 0, 0], 1.5: [0, 0.25, 0], 3.0: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 1.5: [2, 0, 0], 3.0: [0, 0, 0]}},
        "right_arm": {"rotation": {0: [-6, 0, 3], 1.5: [-8, 0, 4], 3.0: [-6, 0, 3]}},
        "left_arm": {"rotation": {0: [3, 0, -3], 1.5: [1, 0, -4], 3.0: [3, 0, -3]}},
    })
    a[H + "walk"] = anim(1.0, True, {
        "right_leg": {"rotation": {0: [-30, 0, 0], 0.5: [30, 0, 0], 1.0: [-30, 0, 0]}},
        "left_leg": {"rotation": {0: [30, 0, 0], 0.5: [-30, 0, 0], 1.0: [30, 0, 0]}},
        "left_arm": {"rotation": {0: [-28, 0, -3], 0.5: [28, 0, -3], 1.0: [-28, 0, -3]}},
        "right_arm": {"rotation": {0: [22, 0, 3], 0.5: [-22, 0, 3], 1.0: [22, 0, 3]}},
        "body": {"position": {0: [0, 0, 0], 0.25: [0, 0.6, 0], 0.5: [0, 0, 0], 0.75: [0, 0.6, 0], 1.0: [0, 0, 0]}},
    })
    a[H + "run"] = anim(0.6, True, {
        "right_leg": {"rotation": {0: [-50, 0, 0], 0.3: [45, 0, 0], 0.6: [-50, 0, 0]}},
        "left_leg": {"rotation": {0: [45, 0, 0], 0.3: [-50, 0, 0], 0.6: [45, 0, 0]}},
        "left_arm": {"rotation": {0: [-55, 0, -5], 0.3: [50, 0, -5], 0.6: [-55, 0, -5]}},
        "right_arm": {"rotation": {0: [50, 0, 5], 0.3: [-55, 0, 5], 0.6: [50, 0, 5]}},
        "body": {"rotation": {0: [10, 0, 0], 0.6: [10, 0, 0]},
                 "position": {0: [0, 0, 0], 0.15: [0, 1.0, 0], 0.3: [0, 0, 0], 0.45: [0, 1.0, 0], 0.6: [0, 0, 0]}},
    })
    a[H + "attack_slash"] = anim(0.6, False, {
        "right_arm": {"rotation": {0: [-6, 0, 3], 0.2: [-150, 0, 10], 0.32: [-25, 0, 0], 0.6: [-6, 0, 3]}},
        "body": {"rotation": {0: [0, 0, 0], 0.2: [-6, -12, 0], 0.32: [10, 14, 0], 0.6: [0, 0, 0]}},
    })
    # trabajar en su mesa: golpecitos y movimientos de manos sobre la mesa, cabeza mirando abajo
    a[H + "work"] = anim(2.0, True, {
        "head": {"rotation": {0: [22, 0, 0], 1.0: [26, 6, 0], 2.0: [22, 0, 0]}},
        "body": {"rotation": {0: [8, 0, 0], 2.0: [8, 0, 0]}},
        "right_arm": {"rotation": {0: [-55, 0, 8], 0.25: [-80, 0, 8], 0.5: [-55, 0, 8], 0.75: [-80, 0, 8], 1.0: [-55, 0, 8],
                                   1.5: [-62, 12, 8], 2.0: [-55, 0, 8]}},
        "left_arm": {"rotation": {0: [-48, 0, -10], 1.0: [-52, -10, -10], 2.0: [-48, 0, -10]}},
    })
    a[H + "sit"] = anim(2.0, True, {
        "body": {"position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "right_leg": {"rotation": {0: [-90, 10, 0], 2.0: [-90, 10, 0]}, "position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "left_leg": {"rotation": {0: [-90, -10, 0], 2.0: [-90, -10, 0]}, "position": {0: [0, -11, 0], 2.0: [0, -11, 0]}},
        "right_arm": {"rotation": {0: [-30, 0, 6], 2.0: [-30, 0, 6]}},
        "left_arm": {"rotation": {0: [-30, 0, -6], 2.0: [-30, 0, -6]}},
    })
    a[H + "tamed"] = anim(1.2, False, {
        "right_arm": {"rotation": {0: [-6, 0, 3], 0.3: [-170, 0, 12], 0.9: [-170, 0, 12], 1.2: [-6, 0, 3]}},
        "left_arm": {"rotation": {0: [3, 0, -3], 0.3: [-170, 0, -12], 0.9: [-170, 0, -12], 1.2: [3, 0, -3]}},
        "body": {"position": {0: [0, 0, 0], 0.3: [0, 2, 0], 0.6: [0, 0, 0], 1.2: [0, 0, 0]}},
    })
    a[H + "sleep"] = anim(4.0, True, {
        "head": {"rotation": {0: [0, 0, 0], 4.0: [0, 0, 0]}},
        "body": {"position": {0: [0, 0, 0], 2.0: [0, 0.2, 0], 4.0: [0, 0, 0]}},
    })
    return a


# ---------------------------------------------------------------- Aldeano Necromancer (modelo de aldeano)
V = "animation.aldeano_necromancer."
VP = {
    ".": None,
    "K": (14, 12, 16), "k": (26, 22, 28), "q": (40, 34, 42),             # tela negra
    "R": (214, 28, 40), "r": (140, 14, 26), "M": (176, 24, 92), "m": (110, 14, 60),  # rojo y magenta
    "G": (232, 176, 60), "g": (160, 110, 30),                            # oro
    "S": (176, 118, 84), "s": (140, 88, 62), "t": (108, 66, 46),          # piel
    "P": (200, 90, 255), "p": (120, 40, 190), "W": (250, 246, 255),       # ojos morados
    "B": (74, 46, 34), "b": (50, 30, 22),                                  # botas
}


def vfill(img, x0, y0, w, h, fn):
    for j in range(h):
        for i in range(w):
            c = fn(i, j, w, h)
            if c:
                img.putpixel((x0 + i, y0 + j), tuple(VP[c]) + (255,) if VP[c] else (0, 0, 0, 0))


def vrows(img, x0, y0, rows):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != " ":
                img.putpixel((x0 + i, y0 + j), (tuple(VP[ch]) + (255,)) if VP[ch] else (0, 0, 0, 0))


def box_faces(img, u, v, w, h, d, faces):
    """Pinta las 6 caras de una caja con UV de caja (formato Minecraft). faces: nombre -> función(i, j, fw, fh) -> letra."""
    rects = {"top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d), "right": (u, v + d, d, h),
             "front": (u + d, v + d, w, h), "left": (u + d + w, v + d, d, h), "back": (u + d + w + d, v + d, w, h)}
    for name, (x0, y0, fw, fh) in rects.items():
        fn = faces.get(name) or faces.get("all")
        if fn:
            vfill(img, x0, y0, fw, fh, fn)


def cloth(i, j, fw, fh):
    return "K" if (i * 3 + j * 5) % 7 else "k"


def necro_villager_texture():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    # cabeza 8x10x8 (piel), con la cara: ojos morados brillantes y cejas
    box_faces(img, 0, 0, 8, 10, 8, {"all": lambda i, j, fw, fh: "S" if (i + j) % 5 else "s"})
    vrows(img, 8, 8, ["SSSSSSSS",
                      "SSSSSSSS",
                      "SttSStts",
                      "SWPSSPWS",
                      "SsSSSSsS",
                      "SSSSSSSS",
                      "SSssssSS",
                      "SSstsSSS",
                      "SsSSSSsS",
                      "ssSSSSss"])
    # capucha (capa exterior) negra con borde rojo y magenta que enmarca la cara
    hood = {"top": lambda i, j, fw, fh: "R" if j == fh - 1 else cloth(i, j, fw, fh),
            "back": lambda i, j, fw, fh: ("r" if j == fh - 1 else cloth(i, j, fw, fh)),
            "right": lambda i, j, fw, fh: ("M" if i == fw - 1 else ("R" if i == fw - 2 else cloth(i, j, fw, fh))),
            "left": lambda i, j, fw, fh: ("M" if i == 0 else ("R" if i == 1 else cloth(i, j, fw, fh))),
            "bottom": lambda i, j, fw, fh: None}
    box_faces(img, 32, 0, 8, 10, 8, hood)
    vrows(img, 40, 8, ["KkKKKKkK",
                       "RRRRRRRR",
                       "MR....RM",
                       "MR....RM",
                       "M......M",
                       "R......R",
                       "M......M",
                       "R......R",
                       "M......M",
                       "r......r"])
    # nariz
    box_faces(img, 24, 0, 2, 4, 2, {"all": lambda i, j, fw, fh: "s" if j < 3 else "t"})
    # torso 8x12x6: túnica negra abierta con el pecho y cinturón dorado
    box_faces(img, 16, 20, 8, 12, 6, {"all": cloth})
    vrows(img, 22, 26, ["KRSSSSRK",
                        "KRSssSRK",
                        "KRSSSSRK",
                        "KMRsSRMK",
                        "KKRSSRKK",
                        "KKMRRMKK",
                        "GGGgGGGG",
                        "KKKGgKKK",
                        "KkKKKKkK",
                        "KKKKKKKK",
                        "kKKKKKKk",
                        "KKKKKKKK"])
    # túnica larga (capa exterior del torso) 8x18x6: franjas rojas abajo y bordes rojos al frente
    def robe(i, j, fw, fh):
        if j in (fh - 2,):
            return "R"
        if j == fh - 1:
            return "r"
        if j in (fh - 5,):
            return "M"
        return cloth(i, j, fw, fh)
    box_faces(img, 0, 38, 8, 18, 6, {"all": robe, "top": lambda *a: None, "bottom": lambda *a: None})
    vrows(img, 6, 44, ["R......R",
                       "R......R",
                       "M......M",
                       "R......R",
                       "R......R",
                       "MR....RM",
                       "RK....KR",
                       "RKKKKKKR",
                       "RKkKKkKR",
                       "MKKKKKKM",
                       "RKKKKKKR",
                       "RKKkKKKR",
                       "RKKKKKKR"])
    # brazos cruzados: mangas negras con puños rojos y manos de piel
    box_faces(img, 44, 22, 4, 8, 4, {"all": lambda i, j, fw, fh: "R" if j == fh - 2 else ("M" if j == fh - 1 else cloth(i, j, fw, fh)),
                                     "bottom": lambda i, j, fw, fh: "S"})
    box_faces(img, 40, 38, 8, 4, 4, {"all": lambda i, j, fw, fh: "S" if (i + j) % 4 else "s",
                                     "top": lambda i, j, fw, fh: "R" if j == 0 else cloth(i, j, fw, fh)})
    # piernas con botas
    box_faces(img, 0, 22, 4, 12, 4, {"all": lambda i, j, fw, fh: "B" if j >= fh - 3 else ("b" if (i + j) % 4 == 0 else "k")})
    return img


def necro_villager_geo():
    """Modelo de aldeano del usuario (Blockbench, Java): misma geometría, en coordenadas Bedrock (y hacia arriba)."""
    g = Geo("geometry.aldeano_necromancer", 64, 64)
    g.bone("body", [0, 24, 0])
    g.bone("head", [0, 24, 0], "body")
    g.cube("head", "head", [-4, 24, -4], [8, 10, 8], [0, 0])
    g.cube("head", "hat", [-4, 24, -4], [8, 10, 8], [32, 0], 0.5)
    g.bone("nose", [0, 26, 0], "head")
    g.cube("nose", "nose", [-1, 23, -6], [2, 4, 2], [24, 0])
    g.cube("body", "body", [-4, 12, -3], [8, 12, 6], [16, 20])
    g.cube("body", "jacket", [-4, 6, -3], [8, 18, 6], [0, 38], 0.5)
    g.bone("arms", [0, 21, -1], "body", [-43, 0, 0])
    g.cube("arms", "arm_r", [4, 15, -3], [4, 8, 4], [44, 22])
    g.cube("arms", "arm_l", [-8, 15, -3], [4, 8, 4], [44, 22])
    g.bones["arms"]["cubes"][-1]["mirror"] = True
    g.cube("arms", "arms_mid", [-4, 15, -3], [8, 4, 4], [40, 38])
    g.bone("right_leg", [-2, 12, 0])
    g.cube("right_leg", "leg", [-4, 0, -2], [4, 12, 4], [0, 22])
    g.bone("left_leg", [2, 12, 0])
    g.cube("left_leg", "leg", [0, 0, -2], [4, 12, 4], [0, 22])
    g.bones["left_leg"]["cubes"][-1]["mirror"] = True
    return g


def necro_villager_animations():
    a = {}
    a[V + "idle"] = anim(3.0, True, {
        "head": {"rotation": {0: [0, 0, 0], 1.5: [3, 0, 0], 3.0: [0, 0, 0]}},
        "arms": {"position": {0: [0, 0, 0], 1.5: [0, 0.3, 0], 3.0: [0, 0, 0]}},
    })
    a[V + "walk"] = anim(1.0, True, {
        "right_leg": {"rotation": {0: [-26, 0, 0], 0.5: [26, 0, 0], 1.0: [-26, 0, 0]}},
        "left_leg": {"rotation": {0: [26, 0, 0], 0.5: [-26, 0, 0], 1.0: [26, 0, 0]}},
        "body": {"position": {0: [0, 0, 0], 0.25: [0, 0.5, 0], 0.5: [0, 0, 0], 0.75: [0, 0.5, 0], 1.0: [0, 0, 0]}},
    })
    # huyendo de los no muertos: corre agachado y mirando atrás
    a[V + "run"] = anim(0.5, True, {
        "right_leg": {"rotation": {0: [-48, 0, 0], 0.25: [44, 0, 0], 0.5: [-48, 0, 0]}},
        "left_leg": {"rotation": {0: [44, 0, 0], 0.25: [-48, 0, 0], 0.5: [44, 0, 0]}},
        "body": {"rotation": {0: [10, 0, 0], 0.5: [10, 0, 0]},
                 "position": {0: [0, 0, 0], 0.12: [0, 1.0, 0], 0.25: [0, 0, 0], 0.37: [0, 1.0, 0], 0.5: [0, 0, 0]}},
        "head": {"rotation": {0: [-8, 14, 0], 0.25: [-8, -14, 0], 0.5: [-8, 14, 0]}},
    })
    a[V + "work"] = anim(2.0, True, {
        "head": {"rotation": {0: [20, 0, 0], 1.0: [24, 8, 0], 2.0: [20, 0, 0]}},
        "arms": {"rotation": {0: [0, 0, 0], 0.5: [-12, 0, 0], 1.0: [0, 0, 0], 1.5: [-12, 0, 0], 2.0: [0, 0, 0]}},
    })
    a[V + "trade"] = anim(1.2, False, {
        "head": {"rotation": {0: [0, 0, 0], 0.3: [12, 0, 0], 0.6: [-4, 0, 0], 0.9: [12, 0, 0], 1.2: [0, 0, 0]}},
    })
    a[V + "sleep"] = anim(4.0, True, {"head": {"rotation": {0: [0, 0, 0], 4.0: [0, 0, 0]}}})
    a[V + "sit"] = a[V + "idle"]
    return a


def write_all():
    n = write_profession_skins()
    write_soldier_females()
    save_json(os.path.join(ASSETS, "animations", "entity", "human.animation.json"),
              {"format_version": "1.8.0", "animations": human_animations()})
    g = necro_villager_geo()
    save_json(os.path.join(ASSETS, "geo", "entity", "aldeano_necromancer.geo.json"), g.to_json())
    save_json(os.path.join(ASSETS, "animations", "entity", "aldeano_necromancer.animation.json"),
              {"format_version": "1.8.0", "animations": necro_villager_animations()})
    skin = os.path.join(HERE, "ref", "humanos", "aldeano_necromancer_skin.png")
    if os.path.exists(skin):
        # skin OFICIAL del usuario (formato aldeano 64x64): se copia sin tocar un pixel; brillan los ojos rojos
        tex = Image.open(skin).convert("RGBA")
        eyes = [(x, y) for x in (9, 10, 13, 14) for y in (13, 14)]
    else:
        tex = necro_villager_texture()
        eyes = [(9, 11), (10, 11), (13, 11), (14, 11)]
    tex.save(os.path.join(HUMAN, "aldeano_necromancer.png"))
    gm = Image.new("RGBA", tex.size, (0, 0, 0, 0))
    for (x, y) in eyes:
        gm.putpixel((x, y), tex.getpixel((x, y)))
    gm.save(os.path.join(HUMAN, "aldeano_necromancer_glowmask.png"))
    return n


if __name__ == "__main__":
    print(write_all(), "skins de profesiones")
