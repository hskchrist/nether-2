"""Armaduras nuevas: Armadura Humana del Nether (la del usuario, "armadura base") y Armadura del Frío Eterno.

Ambas usan un modelo de armadura con el formato de skin de 64x64 (como la ropa de los humanos del Nether),
así la textura de la armadura base del usuario se ve igual que en su skin.
"""
import os
import random
import shutil
from PIL import Image
from common import ASSETS, MODID, save_json
from models import Geo

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref")
ARMOR_TEX = os.path.join(ASSETS, "textures", "armor")
ITEM_TEX = os.path.join(ASSETS, "textures", "item")
ICONS_FROST = os.path.join(REF, "iconos_frio_eterno")   # 16x16 sacados de la lámina del usuario


def boot_faces(leg_uv, outer_first):
    """UV por cara de la bota (4x5x4) tomando las 5 filas de abajo de la pierna de la skin."""
    u, v = leg_uv
    d = 4
    y = v + d + 12 - 5
    right, front, left, back = (u, y), (u + d, y), (u + d + 4, y), (u + d + 4 + d, y)
    west, east = (right, left) if outer_first else (left, right)
    return {"north": {"uv": list(front), "uv_size": [4, 5]}, "south": {"uv": list(back), "uv_size": [4, 5]},
            "west": {"uv": list(west), "uv_size": [4, 5]}, "east": {"uv": list(east), "uv_size": [4, 5]},
            "up": {"uv": [u + d, v], "uv_size": [4, 4]}, "down": {"uv": [u + d + 4, v], "uv_size": [4, 4]}}


def skin_armor_geo(ident):
    g = Geo(ident, 64, 64)
    g.bone("armorHead", [0, 24, 0])
    g.cube("armorHead", "h", [-4, 24, -4], [8, 8, 8], [0, 0], 0.6)
    g.cube("armorHead", "h2", [-4, 24, -4], [8, 8, 8], [32, 0], 1.05)
    g.bone("armorBody", [0, 24, 0])
    g.cube("armorBody", "b", [-4, 12, -2], [8, 12, 4], [16, 16], 0.55)
    g.cube("armorBody", "b2", [-4, 12, -2], [8, 12, 4], [16, 32], 0.85)
    g.bone("armorRightArm", [-5, 22, 0])
    g.cube("armorRightArm", "ra", [-8, 12, -2], [4, 12, 4], [40, 16], 0.55)
    g.cube("armorRightArm", "ra2", [-8, 12, -2], [4, 12, 4], [40, 32], 0.85)
    g.bone("armorLeftArm", [5, 22, 0])
    g.cube("armorLeftArm", "la", [4, 12, -2], [4, 12, 4], [32, 48], 0.55)
    g.cube("armorLeftArm", "la2", [4, 12, -2], [4, 12, 4], [48, 48], 0.85)
    g.bone("armorRightLeg", [-1.9, 12, 0])
    g.cube("armorRightLeg", "rl", [-3.9, 0, -2], [4, 12, 4], [0, 16], 0.45)
    g.cube("armorRightLeg", "rl2", [-3.9, 0, -2], [4, 12, 4], [0, 32], 0.6)
    g.bone("armorLeftLeg", [1.9, 12, 0])
    g.cube("armorLeftLeg", "ll", [-0.1, 0, -2], [4, 12, 4], [16, 48], 0.45)
    g.cube("armorLeftLeg", "ll2", [-0.1, 0, -2], [4, 12, 4], [0, 48], 0.6)
    g.bone("armorRightBoot", [-1.9, 12, 0])
    g.cube("armorRightBoot", "rb", [-3.9, 0, -2], [4, 5, 4], [0, 0], 0.85)
    g.bones["armorRightBoot"]["cubes"][-1]["uv"] = boot_faces((0, 16), True)
    g.bone("armorLeftBoot", [1.9, 12, 0])
    g.cube("armorLeftBoot", "lb", [-0.1, 0, -2], [4, 5, 4], [0, 0], 0.85)
    g.bones["armorLeftBoot"]["cubes"][-1]["uv"] = boot_faces((16, 48), False)
    return g


# ---------------------------------------------------------------- textura de la armadura del Frío Eterno
ICE = [(186, 236, 255), (120, 200, 250), (70, 150, 236), (40, 96, 200), (26, 56, 140)]
CRIM = [(214, 32, 48), (150, 18, 34), (96, 10, 24)]
DARK = (22, 20, 34)


def ice_px(x, y, r):
    k = (x * 5 + y * 3 + r.randint(0, 3)) % 9
    if k == 0:
        return ICE[0]
    if k < 3:
        return ICE[1]
    if k < 6:
        return ICE[2]
    return ICE[3]


def frost_texture():
    """Se parte de la armadura base del usuario (misma forma de placas) y se convierte en hielo:
    el metal oscuro pasa a azul profundo, las placas claras a cristal de hielo brillante y el rojo queda carmesí."""
    src = Image.open(os.path.join(REF, "armadura_base_humana.png")).convert("RGBA")
    img = Image.new("RGBA", src.size, (0, 0, 0, 0))
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = src.getpixel((x, y))
            if not a:
                continue
            if r > 110 and r > g * 1.6 and r > b * 1.6:          # rojo: se queda carmesí
                c = CRIM[0] if r > 180 else CRIM[1]
            else:
                l = 0.3 * r + 0.59 * g + 0.11 * b
                k = random.Random(x * 7919 + y * 104729).random()
                if l < 16:
                    c = ICE[4]
                elif l < 32:
                    c = ICE[3] if k > 0.25 else ICE[2]
                elif l < 52:
                    c = ICE[2] if k > 0.2 else ICE[1]
                elif l < 80:
                    c = ICE[1]
                else:
                    c = ICE[0]
                if k < 0.07:
                    c = ICE[0]
            img.putpixel((x, y), c + (a,))
    # ojos de hielo en el casco
    for (x, y) in ((42, 11), (45, 11), (10, 11), (13, 11)):
        if img.getpixel((x, y))[3]:
            img.putpixel((x, y), ICE[0] + (255,))
    return img


def glow_of(img):
    gm = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for y in range(img.height):
        for x in range(img.width):
            c = img.getpixel((x, y))
            if c[3] and c[2] > 230 and c[0] > 160:
                gm.putpixel((x, y), c)
    return gm


# ---------------------------------------------------------------- íconos de la armadura humana
SIL = {
    "helmet": ["................", "................", "................", "....XXXXXXXX....", "...XRooooooRX...", "..XooooooooooX..",
               "..XooRXXXXRooX..", "..XoX......XoX..", "..XoX......XoX..", "..XXX......XXX..", "................",
               "................", "................", "................", "................", "................"],
    "chestplate": ["................", "..XXX......XXX..", ".XoooXX..XXoooX.", ".XooooRooRooooX.", ".XXXooooooooXXX.",
                   "...XooooooooX...", "...XoooGGoooX...", "...XoooGGoooX...", "...XooooooooX...", "...XRoooooooX...",
                   "...XooooooooX...", "...XooooooRoX...", "...XXXXXXXXXX...", "................", "................", "................"],
    "leggings": ["................", "...XXXXXXXXXX...", "...XRRRGGRRRX...", "...XooooooooX...", "...XoooXXoooX...",
                 "...XoooXXoooX...", "...XoooX.XooX...", "...XoooX.XooX...", "...XoooX.XooX...", "...XoooX.XooX...",
                 "...XRooX.XoRX...", "...XXXXX.XXXX...", "................", "................", "................", "................"],
    "boots": ["................", "................", "................", "................", "................", "................",
              "...XXXX..XXXX...", "...XooX..XooX...", "...XooX..XooX...", "..XoooX..XoooX..", ".XRoooX..XoooRX.",
              ".XXXXXX..XXXXXX.", "................", "................", "................", "................"],
}
PAL = {"X": (14, 10, 14), "o": (54, 44, 54), "R": (214, 30, 38), "G": (232, 40, 34)}


def human_icon(kind):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(SIL[kind]):
        for x, ch in enumerate(row):
            if ch in PAL:
                c = PAL[ch]
                if ch == "o" and (x + y) % 4 == 0:
                    c = (72, 60, 72)
                img.putpixel((x, y), c + (255,))
    return img


PIECES = ["helmet", "chestplate", "leggings", "boots"]
FROST_ICON_SRC = {"helmet": "casco", "chestplate": "pechera", "leggings": "grebas", "boots": "botas"}


def write_all():
    g = skin_armor_geo("geometry.skin_armor")
    save_json(os.path.join(ASSETS, "geo", "armor", "skin_armor.geo.json"), g.to_json())
    save_json(os.path.join(ASSETS, "animations", "armor", "skin_armor.animation.json"), {"format_version": "1.8.0", "animations": {}})
    os.makedirs(ARMOR_TEX, exist_ok=True)
    shutil.copy(os.path.join(REF, "armadura_base_humana.png"), os.path.join(ARMOR_TEX, "human_armor.png"))
    ft = frost_texture()
    ft.save(os.path.join(ARMOR_TEX, "frost_armor.png"))
    glow_of(ft).save(os.path.join(ARMOR_TEX, "frost_armor_glowmask.png"))
    im = os.path.join(ASSETS, "models", "item")
    for p in PIECES:
        human_icon(p).save(os.path.join(ITEM_TEX, "human_%s.png" % p))
        shutil.copy(os.path.join(ICONS_FROST, FROST_ICON_SRC[p] + ".png"), os.path.join(ITEM_TEX, "frost_%s.png" % p))
        for pre in ("human", "frost"):
            save_json(os.path.join(im, "%s_%s.json" % (pre, p)), {"parent": "minecraft:item/generated",
                                                               "textures": {"layer0": "%s:item/%s_%s" % (MODID, pre, p)}})
    shutil.copy(os.path.join(ICONS_FROST, "hoja.png"), os.path.join(ITEM_TEX, "eternal_frost_leaf.png"))
    save_json(os.path.join(im, "eternal_frost_leaf.json"), {"parent": "minecraft:item/generated",
                                                            "textures": {"layer0": "%s:item/eternal_frost_leaf" % MODID}})


if __name__ == "__main__":
    write_all()
