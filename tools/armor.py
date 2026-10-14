"""Armadura de rubí v2 (modelo 3D GeckoLib) basada en la skin de referencia del usuario.

Genera:
  assets/.../geo/armor/ruby_armor.geo.json      (huesos estándar de armadura GeckoLib)
  assets/.../textures/armor/ruby_armor.png      (128 x 64)
y vistas previas en /tmp/claude-0/armor_preview/.
"""
import os
import random
from PIL import Image
from common import ASSETS, Packer, save_json
from models import Geo
from textures import Sheet

PAL = {
    ".": None,
    "K": (30, 10, 8), "B": (58, 20, 16), "b": (80, 32, 22), "L": (104, 48, 32),
    "G": (236, 214, 74), "g": (216, 172, 40), "O": (212, 136, 18), "o": (160, 84, 10),
    "R": (204, 20, 26), "r": (130, 10, 16), "W": (220, 220, 214),
    "S": (52, 54, 62), "s": (78, 80, 92), "T": (176, 150, 118), "h": (140, 104, 76),
}
rnd = random.Random(7)
SKIN_REF = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref", "skin_referencia.png")).convert("RGBA")


def px(ch, noise=4):
    c = PAL[ch]
    if c is None:
        return (0, 0, 0, 0)
    return tuple(max(0, min(255, v + rnd.randint(-noise, noise))) for v in c) + (255,)


def rows(*r):
    """Devuelve función de cara a partir de filas ASCII (se repite/recorta si el tamaño no calza)."""
    def f(i, j, fw, fh):
        line = r[min(j, len(r) - 1)]
        return px(line[min(i, len(line) - 1)])
    return f


def fill(ch):
    return lambda i, j, fw, fh: px(ch)


def leather(i, j, fw, fh):
    if j == fh - 1:
        return px("K")
    k = rnd.random()
    return px("b" if k < 0.18 else ("L" if k < 0.24 else "B"))


CLEAR = lambda *a: (0, 0, 0, 0)


def build():
    g = Geo("geometry.ruby_armor", 128, 64)
    pk = Packer([(64, 0, 128, 64), (16, 32, 64, 48), (32, 0, 64, 16), (48, 48, 64, 64)])
    paint = []  # (uv, size, faces)

    def cube(bone, origin, size, uv, faces, inflate=0.0):
        g.cube(bone, "armor", origin, size, uv, inflate)
        paint.append((uv, size, faces))

    def extra(bone, origin, size, faces, inflate=0.0):
        cube(bone, origin, size, pk.alloc(*size), faces, inflate)

    # ---------------------------------------------------------------- CASCO (copia exacta de la capa exterior de la cabeza de la skin)
    g.bone("armorHead", [0, 24, 0])

    def from_skin(x, y):
        return lambda i, j, fw, fh: SKIN_REF.getpixel((x + i, y + j))
    cube("armorHead", [-4, 24, -4], [8, 8, 8], [0, 0], {
        "front": from_skin(40, 8), "right": from_skin(32, 8), "left": from_skin(48, 8),
        "back": from_skin(56, 8), "top": from_skin(40, 0), "bottom": from_skin(48, 0)}, 1.0)

    # ---------------------------------------------------------------- PETO
    g.bone("armorBody", [0, 24, 0])
    side = rows("oOOo", "BBBB", "BbBB", "BBBB", "BBbB", "BBBB", "bBBB", "BBBB", "BBBB", "oOOo", "oOOo", "KKKK")
    cube("armorBody", [-4, 12, -2], [8, 12, 4], [16, 16], {
        "front": rows("oOOOOOOo",
                      "BOOooOOB",
                      "OgGGGGgO",
                      "ROgGGgOR",
                      "BROggORB",
                      "BBRRRRBB",
                      "BBBRrBBB",
                      "BBBRrBBB",
                      "BBORRoBB",
                      "oOggggOo",
                      "oOOooOOo",
                      "KBKssKBK"),
        "back": rows("BBBBBBBB",
                     "BbBBBBbB",
                     "OoBBBBBB",
                     "oOOOBBBB",
                     "BBBBBbBB",
                     "BBbBBBBB",
                     "BBBBBBBB",
                     "BBBBbBBB",
                     "BBBBBBBB",
                     "BBBgOOBB",
                     "BBBooOBB",
                     "KBKKKKBK"),
        "right": side, "left": side,
        "top": rows("OOOOOOOO", "BBBBBBBB", "BBBBBBBB", "OOOOOOOO"),
        "bottom": CLEAR}, 1.0)
    extra("armorBody", [-1, 16, -3.5], [2, 3, 1], {"front": rows("WR", "RR", "Rr"), "all": fill("r"), "top": fill("R")})

    paul = {"top": lambda i, j, fw, fh: px("G" if (i + j) % 3 else "g"),
            "all": rows("GGGGGG", "GgGGgG", "gggggg", "OOOOOO", "oooooo"),
            "bottom": fill("o")}
    sleeve_top = ["BBBB", "bBBb", "BBBB", "KKKK"]

    g.bone("armorRightArm", [-5, 22, 0])
    r_front = rows(*sleeve_top, "....", "....", "SsSS", "BRWB", "BrRB", "SsSS", "GGgG", "....")
    r_other = rows(*sleeve_top, "....", "....", "SsSS", "BbBB", "BBBB", "SsSS", "GGgG", "....")
    cube("armorRightArm", [-8, 12, -2], [4, 12, 4], [40, 16],
         {"front": r_front, "right": r_other, "left": r_other, "back": r_other, "top": fill("B"), "bottom": CLEAR}, 1.0)
    extra("armorRightArm", [-10, 21, -3.5], [6, 5, 7], paul)

    g.bone("armorLeftArm", [5, 22, 0])
    l_all = rows(*sleeve_top, "....", "SsSS", "sSSs", "BBBB", "bBBb", "KBBK", "....", "....")
    cube("armorLeftArm", [4, 12, -2], [4, 12, 4], [32, 48], {"all": l_all, "top": fill("B"), "bottom": CLEAR}, 1.0)
    extra("armorLeftArm", [4, 21, -3.5], [6, 5, 7], paul)

    # ---------------------------------------------------------------- GREBAS (pantalón de cuero con parches)
    leg_front = rows("KKKK", "BBBB", "BBbB", "BSsB", "BBBB", "bBBB", "BBSB", "BBBB", "BBBB", "bBBb", "BBBB", "KKKK")
    leg_back = rows("KKKK", "BTBB", "BBbB", "BBBB", "BsSB", "BBBB", "bBBB", "BBBB", "BBBB", "bBBb", "BBBB", "KKKK")
    leg_side = rows("KKKK", "BBBB", "BbBB", "BBBB", "BBsB", "BBBB", "BBBB", "bBBB", "BBBB", "bBBb", "BBBB", "KKKK")
    for name, pivot, origin, uv in [("armorRightLeg", [-1.9, 12, 0], [-3.9, 0, -2], [0, 16]),
                                    ("armorLeftLeg", [1.9, 12, 0], [-0.1, 0, -2], [16, 48])]:
        g.bone(name, pivot)
        cube(name, origin, [4, 12, 4], uv,
             {"front": leg_front, "back": leg_back, "right": leg_side, "left": leg_side, "top": CLEAR, "bottom": CLEAR}, 0.5)

    # ---------------------------------------------------------------- BOTAS (con gemas en las rodillas)
    boot_front = rows("....", "....", "....", "....", "....", "bBBb", "BBBB", "BWRB", "BRrB", "BbbB", "BBBB", "KKKK")
    boot_other = rows("....", "....", "....", "....", "....", "bBBb", "BBBB", "BBBB", "BbBB", "BBBB", "BBBB", "KKKK")
    for name, pivot, origin, uv, gx in [("armorRightBoot", [-1.9, 12, 0], [-3.9, 0, -2], [0, 32], -2.9),
                                        ("armorLeftBoot", [1.9, 12, 0], [-0.1, 0, -2], [0, 48], 0.9)]:
        g.bone(name, pivot)
        cube(name, origin, [4, 12, 4], uv,
             {"front": boot_front, "back": boot_other, "right": boot_other, "left": boot_other,
              "top": CLEAR, "bottom": fill("K")}, 1.0)
        extra(name, [gx, 3, -3.6], [2, 2, 1], {"front": rows("WR", "Rr"), "all": fill("r"), "top": fill("R")})

    sheet = Sheet(128, 64)
    for (u, v), (w, h, d), faces in paint:
        sheet.box(u, v, w, h, d, faces)
    return g, sheet.img


# ------------------------------------------------------------------ maniquí para las fotos (parecido al personaje)
SKIN = (196, 140, 112)


def mannequin(geo):
    """Maniquí con la capa base de la skin de referencia (para ver la armadura como en el juego)."""
    off = 128
    parts = [("m_head", [0, 24, 0], [-4, 24, -4], [8, 8, 8], [0, 0]),
             ("m_body", [0, 24, 0], [-4, 12, -2], [8, 12, 4], [16, 16]),
             ("m_rarm", [-5, 22, 0], [-8, 12, -2], [4, 12, 4], [40, 16]),
             ("m_larm", [5, 22, 0], [4, 12, -2], [4, 12, 4], [32, 48]),
             ("m_rleg", [-1.9, 12, 0], [-3.9, 0, -2], [4, 12, 4], [0, 16]),
             ("m_lleg", [1.9, 12, 0], [-0.1, 0, -2], [4, 12, 4], [16, 48])]
    for name, pivot, origin, size, uv in parts:
        geo.bone(name, pivot)
        geo.cube(name, "m", origin, size, [uv[0] + off, uv[1]])
    return SKIN_REF


def write_all(out_preview=None):
    import json
    import preview
    g, tex = build()
    geo_path = os.path.join(ASSETS, "geo", "armor", "ruby_armor.geo.json")
    tex_path = os.path.join(ASSETS, "textures", "armor", "ruby_armor.png")
    save_json(geo_path, g.to_json())
    os.makedirs(os.path.dirname(tex_path), exist_ok=True)
    tex.save(tex_path)
    if out_preview is None:
        return None, None, geo_path, tex_path

    # modelo de vista previa = armadura + maniquí, textura combinada 192 x 64
    os.makedirs(out_preview, exist_ok=True)
    pg = Geo("geometry.preview", 192, 64)
    pg.bones = {k: json.loads(json.dumps(v)) for k, v in g.bones.items()}
    pg.order = list(g.order)
    mimg = mannequin(pg)
    comb = Image.new("RGBA", (192, 64), (0, 0, 0, 0))
    comb.paste(tex, (0, 0))
    comb.paste(mimg, (128, 0))
    comb_path = os.path.join(out_preview, "comb.png")
    comb.save(comb_path)
    pgeo = os.path.join(out_preview, "preview.geo.json")
    save_json(pgeo, pg.to_json())
    return pgeo, comb_path, geo_path, tex_path
