"""Rey Necromante (inspirado en necromancer_swim.bbmodel del usuario), su báculo y sus súbditos."""
import math
import os
import random
from PIL import Image
from common import ASSETS, save_json, Packer
from models import Geo, anim, flip_y
from textures import Sheet

rnd = random.Random(42)
PAL = {
    ".": None,
    "P": (30, 26, 30), "p": (18, 15, 18), "q": (48, 40, 44),
    "N": (24, 20, 22), "n": (12, 10, 12), "v": (44, 36, 38),
    "C": (204, 26, 32), "c": (132, 12, 18),
    "G": (232, 196, 58), "g": (176, 132, 28), "Y": (255, 238, 130),
    "R": (222, 24, 32), "r": (128, 10, 16), "W": (210, 210, 216), "w": (150, 150, 162),
    "F": (128, 102, 74), "f": (110, 86, 64), "h": (136, 114, 80), "O": (84, 59, 52), "k": (32, 23, 23), "Z": (197, 197, 181), "V": (51, 204, 54), "M": (66, 46, 40),
    "S": (200, 178, 156), "s": (156, 130, 112), "E": (196, 84, 255), "e": (128, 36, 196), "o": (56, 34, 70), "m": (92, 52, 62), "X": (166, 166, 180),
    "K": (14, 10, 20), "B": (54, 36, 30), "b": (36, 24, 20),
}


def px(ch, noise=4):
    c = PAL[ch]
    if c is None:
        return (0, 0, 0, 0)
    return tuple(max(0, min(255, v + rnd.randint(-noise, noise))) for v in c) + (255,)


def rows(*r):
    def f(i, j, fw, fh):
        line = r[min(j, len(r) - 1)]
        return px(line[min(i, len(line) - 1)])
    return f


def fill(ch, alt=None, p=0.2):
    return lambda i, j, fw, fh: px(alt if (alt and rnd.random() < p) else ch)


CLEAR = lambda *a: (0, 0, 0, 0)


def robe_front(fw, fh, hem=2):
    def f(i, j, fw2, fh2):
        mid = fw // 2
        if j >= fh - hem:
            return px("Y" if j == fh - hem else ("G" if (i + j) % 3 else "g"))
        if i in (mid - 1, mid) if fw % 2 == 0 else i == mid:
            return px("C" if j % 3 != 2 else "c")
        k = rnd.random()
        return px("q" if k < 0.15 else ("p" if k < 0.4 else "P"))
    return f


def cape_back(i, j, fw, fh):
    # tela azul noche con emblema de calavera de almas y bordes rasgados
    if j == 0:
        return px("G")
    skull = ["..CCCC..",
             ".CCCCCC.",
             ".CKCCKC.",
             ".CCCCCC.",
             "..CKKC..",
             "..C..C.."]
    sx, sy = (fw - 8) // 2, 5
    if sy <= j < sy + 6 and sx <= i < sx + 8:
        ch = skull[j - sy][i - sx]
        if ch != ".":
            return px(ch, 2)
    if j >= fh - 3:
        tear = (i * 7 + 3) % 5
        if j == fh - 1 and tear < 2:
            return (0, 0, 0, 0)
        if j >= fh - 2:
            return px("C" if tear % 2 else "c")
    if i in (0, fw - 1):
        return px("c")
    k = rnd.random()
    return px("v" if k < 0.12 else ("n" if k < 0.35 else "N"))


def build():
    g = Geo("geometry.necro_king", 128, 128)
    pk = Packer([(64, 0, 128, 128), (0, 64, 64, 128)])
    paint = []

    def cube(bone, origin, size, uv, faces, inflate=0.0):
        g.cube(bone, "c", origin, size, uv, inflate)
        paint.append((uv, size, faces))

    def extra(bone, origin, size, faces, inflate=0.0):
        cube(bone, origin, size, pk.alloc(*size), faces, inflate)

    # --- cuerpo y túnica
    g.bone("body", [0, 16, 0])
    cube("body", [-4, 16, -2], [8, 12, 4], [16, 16], {
        "front": rows("NvCYYCvN",
                      "PqGGGGqP",
                      "PpGRrGpP",
                      "PqGGGGqP",
                      "PPpCCpPP",
                      "PpPCCPpP",
                      "PPpCCpPP",
                      "PqPCCPqP",
                      "GGGgGGgG",
                      "gYGRRGYg",
                      "PpPCCPpP",
                      "PPpCCpPP"),
        "back": rows("NvNNNNvN", "PPpPPpPP", "PpPPPPpP", "PPPqPPPP", "PpPPPPpP", "PPPPpPPP",
                     "PpPPPPPP", "PPPpPPpP", "GGGgGGgG", "gYGgGGYg", "PPpPPpPP", "PpPPPPpP"),
        "right": rows("NNNN", "PPPP", "PpPP", "PPPP", "PPpP", "PPPP", "pPPP", "PPPP", "GGGG", "gYYg", "PPPP", "PpPP"),
        "left": rows("NNNN", "PPPP", "PPpP", "PPPP", "PpPP", "PPPP", "PPPp", "PPPP", "GGGG", "gYYg", "PPPP", "PPpP"),
        "top": fill("N", "v"), "bottom": fill("P")})
    # falda de la túnica hasta los tobillos
    g.bone("skirt", [0, 16, 0], "body")
    extra("skirt", [-4.5, 2, -2.5], [9, 14, 5], {"front": robe_front(9, 14), "back": robe_front(9, 14),
                                                 "right": robe_front(5, 14), "left": robe_front(5, 14),
                                                 "top": CLEAR, "bottom": fill("p")})
    # capa
    g.bone("cape", [0, 28, 2.2], "body", [6, 0, 0])
    extra("cape", [-6, 3, 2.2], [12, 25, 1], {"back": cape_back, "front": fill("r", "c", 0.3),
                                              "right": fill("N"), "left": fill("N"), "top": fill("G"), "bottom": fill("c")})

    # --- cabeza, capucha y corona
    g.bone("head", [0, 28, 0], "body")
    hair = lambda i, j, fw, fh: px("k")
    side_face = lambda i, j, fw, fh: px("k") if j < 2 else px("F" if (i + j) % 4 else "f")
    cube("head", [-4, 28, -4], [8, 8, 8], [0, 0], {
        "front": rows("kkkkkkkk",
                      "kkkhfkkk",
                      "kZVhfVZk",
                      "FFhFfOfF",
                      "FFfOOOFF",
                      "FfhOMOfF",
                      "FFfffFfF",
                      "FfFFFFfF"),
        "right": side_face, "left": side_face, "back": hair, "top": hair, "bottom": fill("F")})
    hood_side = lambda i, j, fw, fh: px("c") if (j == fh - 1 and i % 2 == 0) else px("v" if rnd.random() < 0.15 else "N")
    cube("head", [-4, 28, -4], [8, 8, 8], [32, 0], {
        "front": rows("NNvNNvNN",
                      "NC....CN",
                      "N......N",
                      "N......N",
                      "N......N",
                      "N......N",
                      "NC....CN",
                      "NNC..CNN"),
        "right": hood_side, "left": hood_side, "back": hood_side, "top": fill("N", "v"), "bottom": CLEAR}, 0.5)
    g.bone("crown", [0, 36.5, 0], "head")
    band = lambda i, j, fw, fh: px("Y" if j == 0 else ("G" if (i + j) % 3 else "g"))
    extra("crown", [-4.5, 36.5, -4.5], [9, 2, 9], {"all": band, "top": CLEAR, "bottom": CLEAR,
                                                   "front": rows("GGgCGgCGG"[:9], "gGRGRGRGg"[:9])})
    for (x, z, h) in [(-4.5, -4.5, 4), (3.5, -4.5, 4), (-4.5, 3.5, 3), (3.5, 3.5, 3)]:
        extra("crown", [x, 38.5, z], [1, h, 1], {"all": rows("Y", "G", "G", "g"), "top": fill("Y")})
    extra("crown", [-1, 38.5, -4.5], [2, 3, 1], {"front": rows("GG", "CR", "gg"), "all": fill("G"), "top": fill("Y")})
    extra("crown", [-1, 41.5, -4.5], [2, 2, 1], {"all": rows("YG", "GG"), "top": fill("Y")})
    for x in (-4.5, 3.5):
        extra("crown", [x, 38.5, -1], [1, 2, 2], {"all": rows("GG", "gC"), "top": fill("Y")})

    # --- brazos con hombreras
    sleeve = rows("NNNN", "NvNN", "NNNN", "NNvN", "NNNN", "NvNN", "NNNN", "CCCC", "NNNN", "GGgG", "SSSS", "SsSS")
    g.bone("right_arm", [-6, 26, 0], "body")
    cube("right_arm", [-8, 15, -2], [4, 12, 4], [40, 16], {"all": sleeve, "top": fill("N"), "bottom": fill("S")})
    g.bone("right_hand_item", [-6, 16, -0.5], "right_arm")
    add_staff(g, pk, paint, "right_arm", -6, 16, -0.5, [36, 0, 0])
    g.bone("left_arm", [6, 26, 0], "body")
    cube("left_arm", [4, 15, -2], [4, 12, 4], [32, 48], {"all": sleeve, "top": fill("N"), "bottom": fill("S")})
    g.bone("left_hand_item", [6, 16, -0.5], "left_arm")
    paul = {"top": lambda i, j, fw, fh: px("C" if (i % 2 == 1 and j % 2 == 1) else "N"),
            "all": rows("NvNNvN", "NNNNNN", "CCCCCC", "GgGgGg"), "bottom": fill("n")}
    extra("right_arm", [-10, 25, -3], [6, 4, 6], paul)
    extra("left_arm", [4, 25, -3], [6, 4, 6], paul)

    # --- piernas (casi ocultas por la túnica) con botas
    leg = rows("PPPP", "PpPP", "PPPP", "PPpP", "PPPP", "PPPP", "pPPP", "PPPP", "PPPP", "BBBB", "GgGg", "bbbb",
               "BBBB", "BbBB", "BBBB", "bbbb")
    g.bone("right_leg", [-2, 16, 0])
    cube("right_leg", [-4, 0, -2], [4, 16, 4], [0, 16], {"all": leg, "top": fill("P"), "bottom": fill("b")})
    g.bone("left_leg", [2, 16, 0])
    cube("left_leg", [0, 0, -2], [4, 16, 4], [16, 48], {"all": leg, "top": fill("P"), "bottom": fill("b")})

    sheet = Sheet(128, 128)
    for (u, v), (w, h, d), faces in paint:
        sheet.box(u, v, w, h, d, faces)
    return g, sheet.img


A = "animation.necro_king."


def animations():
    a = {}
    a[A + "idle"] = anim(3.0, True, {
        "body": {"position": {0: [0, 0, 0], 1.5: [0, 0.35, 0], 3.0: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 1.5: [3, -4, 0], 3.0: [0, 0, 0]}},
        "right_arm": {"rotation": {0: [-36, 0, 6], 1.5: [-39, 0, 7], 3.0: [-36, 0, 6]}},
        "left_arm": {"rotation": {0: [-12, 0, -8], 1.5: [-16, 0, -10], 3.0: [-12, 0, -8]}},
        "cape": {"rotation": {0: [6, 0, 0], 1.5: [9, 0, 1], 3.0: [6, 0, 0]}},
        "skirt": {"rotation": {0: [0, 0, 0], 1.5: [1, 0, 0], 3.0: [0, 0, 0]}},
    })
    a[A + "walk"] = anim(1.4, True, {
        "right_leg": {"rotation": {0: [-22, 0, 0], 0.7: [22, 0, 0], 1.4: [-22, 0, 0]}},
        "left_leg": {"rotation": {0: [22, 0, 0], 0.7: [-22, 0, 0], 1.4: [22, 0, 0]}},
        "skirt": {"rotation": {0: [4, 0, 2], 0.7: [-4, 0, -2], 1.4: [4, 0, 2]}},
        "right_arm": {"rotation": {0: [-32, 0, 6], 0.7: [-40, 0, 6], 1.4: [-32, 0, 6]}},
        "left_arm": {"rotation": {0: [-18, 0, -8], 0.7: [8, 0, -8], 1.4: [-18, 0, -8]}},
        "cape": {"rotation": {0: [10, 0, 0], 0.35: [16, 0, 2], 0.7: [10, 0, 0], 1.05: [16, 0, -2], 1.4: [10, 0, 0]}},
        "body": {"position": {0: [0, 0, 0], 0.35: [0, 0.5, 0], 0.7: [0, 0, 0], 1.05: [0, 0.5, 0], 1.4: [0, 0, 0]},
                 "rotation": {0: [0, 3, 0], 0.7: [0, -3, 0], 1.4: [0, 3, 0]}},
    })
    # Ataque a distancia: alza el báculo y lanza el rayo de almas hacia adelante
    a[A + "cast"] = anim(1.0, False, {
        "right_arm": {"rotation": {0: [-36, 0, 6], 0.35: [-150, 0, 10], 0.5: [-80, 0, 0], 0.75: [-80, 0, 0], 1.0: [-36, 0, 6]}},
        "left_arm": {"rotation": {0: [-12, 0, -8], 0.35: [-40, 0, -30], 0.5: [-90, 0, -5], 0.75: [-90, 0, -5], 1.0: [-12, 0, -8]}},
        "body": {"rotation": {0: [0, 0, 0], 0.35: [-8, 0, 0], 0.5: [10, 0, 0], 0.75: [6, 0, 0], 1.0: [0, 0, 0]}},
        "cape": {"rotation": {0: [6, 0, 0], 0.35: [4, 0, 0], 0.5: [30, 0, 0], 0.75: [22, 0, 0], 1.0: [6, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.5: [-6, 0, 0], 1.0: [0, 0, 0]}},
    })
    # Invocación: alza los brazos, la capa se agita y golpea el suelo con el báculo
    a[A + "summon"] = anim(2.0, False, {
        "right_arm": {"rotation": {0: [-36, 0, 6], 0.4: [-165, 0, 25], 1.4: [-165, 0, 25], 1.6: [-40, 0, 6], 2.0: [-36, 0, 6]}},
        "left_arm": {"rotation": {0: [-12, 0, -8], 0.4: [-165, 0, -25], 1.4: [-165, 0, -25], 1.6: [-30, 0, -8], 2.0: [-12, 0, -8]}},
        "head": {"rotation": {0: [0, 0, 0], 0.4: [-18, 0, 0], 1.4: [-18, 0, 0], 1.6: [8, 0, 0], 2.0: [0, 0, 0]}},
        "body": {"position": {0: [0, 0, 0], 0.4: [0, 1.5, 0], 1.4: [0, 1.5, 0], 1.6: [0, -0.5, 0], 2.0: [0, 0, 0]},
                 "rotation": {0: [0, 0, 0], 0.4: [-6, 0, 0], 1.4: [-6, 0, 0], 1.6: [10, 0, 0], 2.0: [0, 0, 0]}},
        "cape": {"rotation": {0: [6, 0, 0], 0.4: [35, 0, 4], 0.9: [45, 0, -4], 1.4: [35, 0, 4], 1.6: [12, 0, 0], 2.0: [6, 0, 0]}},
        "skirt": {"rotation": {0: [0, 0, 0], 0.4: [6, 0, 0], 1.4: [6, 0, 0], 2.0: [0, 0, 0]}},
    })
    a[A + "staff_orb"] = anim(2.4, True, staff_anim_bones())
    return a


def build_staff_item():
    """Modelo GeckoLib del báculo como ítem (el mismo diseño que lleva el rey). Centro del agarre en (0, 8, 0)."""
    g = Geo("geometry.necro_staff", 64, 64)
    pk = Packer([(0, 0, 64, 64)])
    paint = []
    add_staff(g, pk, paint, None, 0, 8, 0)
    sheet = Sheet(64, 64)
    for (u, v), (w, h, d), faces in paint:
        sheet.box(u, v, w, h, d, faces)
    return g, sheet.img


# ------------------------------------------------------------------ báculo (ítem 32x32, ya no se usa: el ítem es 3D)
def staff_icon():
    N = 32
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    put = lambda x, y, c: im.putpixel((x, y), tuple(c) + (255,)) if 0 <= x < N and 0 <= y < N else None
    # asta diagonal (de abajo-izquierda a arriba-derecha)
    for k in range(0, 21):
        x, y = 4 + k, 27 - k
        put(x, y, PAL["n"]); put(x + 1, y, PAL["N"]); put(x, y - 1, PAL["v"])
        if k % 5 == 2:
            put(x, y, PAL["G"]); put(x + 1, y, PAL["Y"]); put(x, y - 1, PAL["g"]); put(x + 1, y - 1, PAL["G"])
        elif k % 5 == 4 and 4 < k < 18:
            put(x + 1, y, PAL["C"])
    # pomo de oro
    for (x, y) in [(2, 29), (3, 29), (2, 28), (3, 28), (4, 28), (3, 27)]:
        put(x, y, PAL["G"])
    put(2, 30, PAL["g"]); put(3, 30, PAL["g"]); put(2, 28, PAL["Y"])
    # garra dorada que sostiene el cristal
    claw = [(22, 9), (23, 8), (24, 9), (21, 8), (20, 7), (20, 6), (26, 10), (27, 10), (28, 9), (28, 8),
            (21, 5), (27, 11), (19, 8), (25, 12)]
    for (x, y) in claw:
        put(x, y, PAL["G"])
    for (x, y) in [(20, 5), (28, 7), (24, 13)]:
        put(x, y, PAL["Y"])
    # rubí bajo el cristal
    for (x, y) in [(23, 9), (24, 10), (23, 10)]:
        put(x, y, PAL["R"])
    put(24, 9, PAL["r"])
    # orbe de rubí (esfera con brillo)
    cx, cy = 24.5, 5.0
    for y in range(0, 11):
        for x in range(19, 31):
            dd = ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5
            if dd <= 4.1:
                shade = (x + 0.5 - cx) * 0.55 + (y + 0.5 - cy) * 0.45
                col = ORB_COLORS["L"] if shade < -1.3 else (ORB_COLORS["R"] if shade < 1.2 else ORB_COLORS["r"])
                put(x, y, col)
    put(23, 3, ORB_COLORS["W"]); put(22, 4, ORB_COLORS["W"]); put(23, 4, ORB_COLORS["L"])
    # contorno
    src = im.copy()
    for y in range(N):
        for x in range(N):
            if src.getpixel((x, y))[3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    X, Y = x + dx, y + dy
                    if 0 <= X < N and 0 <= Y < N and src.getpixel((X, Y))[3]:
                        im.putpixel((x, y), (10, 8, 18, 255))
                        break
    return im


STAFF_RECIPE = (["RGL", " BG", "B R"], {"R": "civilizacion_nether:ruby", "G": "minecraft:gold_ingot",
                                         "L": "minecraft:soul_lantern", "B": "minecraft:blaze_rod"})


# ------------------------------------------------------------------ súbdito espectral (cuerpo del guerrero, textura de almas)
def minion_texture():
    import warrior
    _, wtex = warrior.load_bbmodel()
    out = Image.new("RGBA", (64, 68), (0, 0, 0, 0))
    out.paste(wtex, (0, 0))
    for y in range(64, 68):
        out.paste(wtex.crop((0, 63, 64, 64)), (0, y))
    for y in range(68):
        for x in range(64):
            r, g_, b, a = out.getpixel((x, y))
            if a == 0:
                continue
            lum = (0.3 * r + 0.59 * g_ + 0.11 * b) / 255.0
            if r > 200 and g_ < 80 and b < 80:          # rubíes -> almas cian brillantes
                col = (90, 245, 245)
            elif r > 170 and g_ > 120 and b < 110:      # oro -> oro pálido
                col = (220, 200, 120)
            else:                                       # resto -> azul noche / morado espectral
                t = min(1.0, lum * 1.8)
                col = (int(14 + 70 * t), int(26 + 90 * t), int(52 + 140 * t))
            out.putpixel((x, y), col + (255,))
    return out


def write_all():
    g, tex = build()
    save_json(os.path.join(ASSETS, "geo", "entity", "necro_king.geo.json"), g.to_json())
    an = flip_y(animations())
    save_json(os.path.join(ASSETS, "animations", "entity", "necro_king.animation.json"),
              {"format_version": "1.8.0", "animations": an})
    tex.save(os.path.join(ASSETS, "textures", "entity", "necro_king.png"))
    glowmask(tex).save(os.path.join(ASSETS, "textures", "entity", "necro_king_glowmask.png"))
    sg, stex = build_staff_item()
    save_json(os.path.join(ASSETS, "geo", "item", "necro_staff.geo.json"), sg.to_json())
    save_json(os.path.join(ASSETS, "animations", "item", "necro_staff.animation.json"),
              {"format_version": "1.8.0", "animations": {"animation.necro_staff.orb": an[A + "staff_orb"]}})
    os.makedirs(os.path.join(ASSETS, "textures", "item"), exist_ok=True)
    stex.save(os.path.join(ASSETS, "textures", "item", "necro_staff.png"))
    glowmask(stex).save(os.path.join(ASSETS, "textures", "item", "necro_staff_glowmask.png"))
    staff_icon().save(os.path.join(ASSETS, "textures", "item", "necro_staff_icon.png"))
    minion_texture().save(os.path.join(ASSETS, "textures", "entity", "soul_minion.png"))
    return g, tex


# ================================================================== BÁCULO 3D (orbe de rubí animado y brillante)
ORB_COLORS = {"R": (232, 30, 40), "L": (255, 120, 126), "r": (150, 10, 20), "W": (255, 236, 236)}


def orb_face(i, j, fw, fh):
    if (i, j) in ((0, 0), (1, 0), (0, 1)):
        return ORB_COLORS["W"] + (255,) if (i, j) == (0, 0) else ORB_COLORS["L"] + (255,)
    t = i + j
    c = ORB_COLORS["L"] if t <= 2 else (ORB_COLORS["R"] if t <= 4 else ORB_COLORS["r"])
    return c + (255,)


def add_staff(g, pk, paint, parent, gx, gy, gz, rot=None):
    """Báculo 3D. (gx, gy, gz) = punto de agarre. Huesos: staff, staff_orb, staff_shards."""
    def cube(bone, origin, size, faces):
        uv = pk.alloc(*size)
        g.cube(bone, "staff", origin, size, uv)
        paint.append((uv, size, faces))
    g.bone("staff", [gx, gy, gz], parent, rot)
    # asta de obsidiana con espiral de runas cian
    shaft = lambda i, j, fw, fh: px("C") if ((j + i * 2) % 7 == 0) else px("n" if (i + j) % 3 else "N")
    cube("staff", [gx - 0.5, gy - 8, gz - 0.5], [1, 26, 1], {"all": shaft, "top": fill("N"), "bottom": fill("G")})
    gold = {"all": lambda i, j, fw, fh: px("Y" if j == 0 else ("G" if (i + j) % 2 else "g")), "top": fill("Y"), "bottom": fill("g")}
    for y in (gy - 4, gy + 4, gy + 12):
        cube("staff", [gx - 1, y, gz - 1], [2, 1, 2], gold)
    # empuñadura de cuero con gema
    cube("staff", [gx - 1, gy - 2, gz - 1], [2, 4, 2], {"all": lambda i, j, fw, fh: px("B" if (i + j) % 2 else "b"),
                                                       "top": fill("g"), "bottom": fill("g")})
    cube("staff", [gx - 1, gy - 10, gz - 1], [2, 2, 2], gold)                 # pomo
    cube("staff", [gx - 0.5, gy - 11, gz - 0.5], [1, 1, 1], gold)
    # adornos en forma de alas bajo la cabeza
    cube("staff", [gx - 3, gy + 15, gz - 0.5], [6, 1, 1], {"all": rows("gYYYYg"), "top": fill("Y"), "bottom": fill("g")})
    cube("staff", [gx - 2, gy + 16, gz - 0.5], [4, 1, 1], {"all": rows("gYYg"), "top": fill("Y")})
    collar = {"all": rows("YGGY", "gRRg"), "top": fill("G"), "bottom": fill("g")}
    cube("staff", [gx - 2, gy + 18, gz - 2], [4, 2, 4], collar)              # collar con rubíes
    for (dx, dz) in [(-2.5, -2.5), (1.5, -2.5), (-2.5, 1.5), (1.5, 1.5)]:     # garras
        cube("staff", [gx + dx, gy + 20, gz + dz], [1, 5, 1], {"all": rows("G", "G", "g", "G", "Y"), "top": fill("Y"), "bottom": fill("g")})
    for (dx, dz) in [(-2.1, -2.1), (1.1, -2.1), (-2.1, 1.1), (1.1, 1.1)]:
        cube("staff", [gx + dx, gy + 25, gz + dz], [1, 1, 1], {"all": fill("Y")})
    # orbe de rubí flotante (gira, sube/baja y late)
    g.bone("staff_orb", [gx, gy + 23, gz], "staff")
    uv = pk.alloc(4, 4, 4)
    g.cube("staff_orb", "orb", [gx - 2, gy + 21, gz - 2], [4, 4, 4], uv)
    paint.append((uv, [4, 4, 4], {"all": orb_face}))
    # fragmentos de rubí que orbitan
    g.bone("staff_shards", [gx, gy + 23, gz], "staff")
    for dx, dz in [(3.8, 0), (-3.8, 0), (0, 3.8), (0, -3.8)]:
        uv = pk.alloc(1, 1, 1)
        g.cube("staff_shards", "orb", [gx + dx - 0.5, gy + 22.5, gz + dz - 0.5], [1, 1, 1], uv)
        paint.append((uv, [1, 1, 1], {"all": lambda i, j, fw, fh: ORB_COLORS["L"] + (255,)}))


def staff_anim_bones():
    return {
        "staff_orb": {"rotation": {0: [0, 0, 0], 1.2: [0, 180, 0], 2.4: [0, 360, 0]},
                      "position": {0: [0, 0, 0], 0.6: [0, 0.5, 0], 1.2: [0, 0, 0], 1.8: [0, 0.5, 0], 2.4: [0, 0, 0]},
                      "scale": {0: [1, 1, 1], 0.6: [1.12, 1.12, 1.12], 1.2: [1, 1, 1], 1.8: [1.12, 1.12, 1.12], 2.4: [1, 1, 1]}},
        "staff_shards": {"rotation": {0: [0, 0, 0], 1.2: [0, -180, 0], 2.4: [0, -360, 0]}},
    }


GLOW_COLORS = [ORB_COLORS["R"], ORB_COLORS["L"], ORB_COLORS["r"], ORB_COLORS["W"], (51, 204, 54)]


def is_glow_pixel(c):
    """Solo brillan el orbe de rubí, sus fragmentos y los ojos verdes."""
    r, g_, b, a = c
    if a == 0:
        return False
    return any(abs(r - q[0]) + abs(g_ - q[1]) + abs(b - q[2]) <= 12 for q in GLOW_COLORS)


def glowmask(img):
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for y in range(img.height):
        for x in range(img.width):
            c = img.getpixel((x, y))
            if is_glow_pixel(c):
                out.putpixel((x, y), c)
    return out
