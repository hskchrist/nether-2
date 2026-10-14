"""Íconos 16x16 de la armadura de rubí v2 e imágenes de sus crafteos."""
import os
from PIL import Image, ImageDraw, ImageFont
from common import ASSETS

C = {
    ".": None, "x": (22, 8, 6),
    "H": (0x56, 0x21, 0x15), "h": (0x3e, 0x15, 0x0c), "d": (0x33, 0x11, 0x09),
    "K": (30, 10, 8), "B": (58, 20, 16), "b": (80, 32, 22),
    "G": (236, 214, 74), "g": (216, 172, 40), "O": (212, 136, 18), "o": (160, 84, 10),
    "R": (204, 20, 26), "r": (130, 10, 16), "W": (230, 230, 224),
    "S": (52, 54, 62), "s": (88, 90, 102), "T": (176, 150, 118),
    # solo para ilustrar los ingredientes
    "l": (150, 84, 44), "L": (186, 110, 60), "m": (110, 58, 30),
    "y": (250, 230, 110), "Y": (220, 180, 40), "z": (170, 120, 20),
}

ICONS = {
    "ruby_helmet": [
        "................",
        ".....xxxxxx.....",
        "...xxhhdhhhxx...",
        "..xhhhhdhhhhhx..",
        ".xHhhhhhhhhhhHx.",
        ".xHhhhhWRhhhhHx.",
        ".xHhhhhRrhhhhHx.",
        ".xHhhdxxxxdhhHx.",
        ".xHhhx....xhhHx.",
        ".xHhx......xhHx.",
        ".xHhx......xhHx.",
        ".xHhx......xhHx.",
        ".xHHx......xHHx.",
        ".xxxx......xxxx.",
        "................",
        "................",
    ],
    "ruby_chestplate": [
        "................",
        ".xxxxx....xxxxx.",
        "xGGGGgx..xgGGGGx",
        "xgggggOxxOgggggx",
        "xoooOOGGGGOOooox",
        ".xxxBOgGGgOBxxx.",
        "...xROgGGgORx...",
        "...xBROggORBx...",
        "...xBBRRRRBBx...",
        "...xBBBWRBBBx...",
        "...xBBBRrBBBx...",
        "...xBBORRoBBx...",
        "...xoOggggOox...",
        "...xoOOooOOox...",
        "...xKBKssKBKx...",
        "...xxxxxxxxxx...",
    ],
    "ruby_leggings": [
        "................",
        "...xxxxxxxxxx...",
        "...xKKKTTKKKx...",
        "...xBBBBBBBBx...",
        "...xBSsBBbBBx...",
        "...xBBBBBBSsx...",
        "...xbBBxxBBBx...",
        "...xBBBx.xBBx...",
        "...xBSsx.xbBx...",
        "...xBBBx.xBBx...",
        "...xBbBx.xSsx...",
        "...xBBBx.xBBx...",
        "...xBBBx.xBBx...",
        "...xKKKx.xKKx...",
        "...xxxxx.xxxx...",
        "................",
    ],
    "ruby_boots": [
        "................",
        "................",
        "................",
        "...xxxxx.xxxxx..",
        "...xbBBx.xbBBx..",
        "...xBBBx.xBBBx..",
        "...xWRBx.xWRBx..",
        "...xRrBx.xRrBx..",
        "...xBBBx.xBBBx..",
        "...xBbBx.xBbBx..",
        "...xBBBxxxBBBxx.",
        "..xBBBBBxxBBBBBx",
        "..xBBBBBxxBBBBBx",
        "..xKKKKKxxKKKKKx",
        "..xxxxxxxxxxxxxx",
        "................",
    ],
    # ingredientes (solo para las imágenes de crafteo; el juego usa los suyos)
    "leather": [
        "................",
        "................",
        "...xxx....xxx...",
        "..xLLLxxxxLLLx..",
        "..xLllLLLLllLx..",
        "...xLlllllllx...",
        "...xLllmmlllx...",
        "...xLllmmlllx...",
        "...xLlllllllx...",
        "..xLllllllllLx..",
        "..xLLlllllllLx..",
        "...xxLLlllLxx...",
        ".....xxxxxx.....",
        "................",
        "................",
        "................",
    ],
    "gold_ingot": [
        "................",
        "................",
        "................",
        "................",
        "................",
        ".....xxxxxxxx...",
        "....xyyyyyyYzx..",
        "...xyyyyyyyYzx..",
        "..xyyYYYYYYzzx..",
        "..xYYYYYYYYzx...",
        "..xzzzzzzzzx....",
        "...xxxxxxxxx....",
        "................",
        "................",
        "................",
        "................",
    ],
}


def icon(name):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(ICONS[name]):
        for x, ch in enumerate(row):
            if C.get(ch):
                im.putpixel((x, y), C[ch] + (255,))
    return im


RECIPES = {
    # id: (patrón, clave)
    "ruby_helmet": (["LRL", "R R"], {"L": "minecraft:leather", "R": "civilizacion_nether:ruby"}),
    "ruby_chestplate": (["G G", "RRR", "LRL"], {"G": "minecraft:gold_ingot", "R": "civilizacion_nether:ruby", "L": "minecraft:leather"}),
    "ruby_leggings": (["LGL", "R R", "L L"], {"L": "minecraft:leather", "G": "minecraft:gold_ingot", "R": "civilizacion_nether:ruby"}),
    "ruby_boots": (["R R", "L L"], {"R": "civilizacion_nether:ruby", "L": "minecraft:leather"}),
}
NAMES = {"ruby_helmet": "Casco de rubí", "ruby_chestplate": "Peto de rubí",
         "ruby_leggings": "Grebas de rubí", "ruby_boots": "Botas de rubí"}
ING = {"minecraft:leather": "leather", "minecraft:gold_ingot": "gold_ingot", "civilizacion_nether:ruby": "ruby"}
ING_ES = {"minecraft:leather": "cuero", "minecraft:gold_ingot": "lingote de oro", "civilizacion_nether:ruby": "rubí"}


def write_assets():
    from common import save_json, DATA
    tex = os.path.join(ASSETS, "textures", "item")
    for n in RECIPES:
        icon(n).save(os.path.join(tex, n + ".png"))
        pattern, key = RECIPES[n]
        save_json(os.path.join(DATA, "recipe", n + ".json"), {
            "type": "minecraft:crafting_shaped", "category": "equipment", "pattern": pattern,
            "key": {k: {"item": v} for k, v in key.items()},
            "result": {"id": "civilizacion_nether:" + n, "count": 1}})


def crafting_images(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    ruby = Image.open(os.path.join(ASSETS, "textures", "item", "ruby.png")).convert("RGBA")
    cache = {"ruby": ruby}
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    SL, SC = 64, 3  # tamaño de casilla, escala del ícono (16*3 = 48)
    panels = []
    for n, (pattern, key) in RECIPES.items():
        W, H = 520, 330
        im = Image.new("RGB", (W, H), (198, 198, 198))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, W - 1, H - 1], outline=(85, 85, 85), width=3)
        d.text((16, 10), NAMES[n], fill=(64, 64, 64), font=f)
        ox, oy = 30, 60
        for r in range(3):
            for c in range(3):
                x, y = ox + c * SL, oy + r * SL
                d.rectangle([x, y, x + SL - 4, y + SL - 4], fill=(139, 139, 139), outline=(55, 55, 55), width=2)
                if r < len(pattern) and c < len(pattern[r]) and pattern[r][c] != " ":
                    item = key[pattern[r][c]]
                    nm = ING[item]
                    if nm not in cache:
                        cache[nm] = icon(nm)
                    ic = cache[nm].resize((16 * SC, 16 * SC), Image.NEAREST)
                    im.paste(ic, (x + 6, y + 6), ic)
        # flecha
        ax, ay = ox + 3 * SL + 20, oy + SL + 10
        d.polygon([(ax, ay + 12), (ax + 40, ay + 12), (ax + 40, ay), (ax + 64, ay + 22), (ax + 40, ay + 44), (ax + 40, ay + 32), (ax, ay + 32)],
                  fill=(120, 120, 120))
        rx, ry = ax + 90, oy + SL - 10
        d.rectangle([rx, ry, rx + 84, ry + 84], fill=(139, 139, 139), outline=(55, 55, 55), width=2)
        ic = icon(n).resize((64, 64), Image.NEAREST)
        im.paste(ic, (rx + 10, ry + 10), ic)
        # leyenda
        cnt = {}
        for row in pattern:
            for ch in row:
                if ch != " ":
                    cnt[key[ch]] = cnt.get(key[ch], 0) + 1
        legend = "  ·  ".join("%d %s" % (v, ING_ES[k]) for k, v in cnt.items())
        d.text((30, H - 50), legend, fill=(50, 50, 50), font=fs)
        panels.append(im)
    sheet = Image.new("RGB", (1060, 690), (40, 40, 46))
    for i, p in enumerate(panels):
        sheet.paste(p, (10 + (i % 2) * 530, 10 + (i // 2) * 340))
    sheet.save(os.path.join(out_dir, "crafteos_armadura.png"))
    # íconos grandes
    row = Image.new("RGB", (4 * 180 + 20, 230), (40, 40, 46))
    d = ImageDraw.Draw(row)
    for i, n in enumerate(RECIPES):
        ic = icon(n).resize((128, 128), Image.NEAREST)
        row.paste(ic, (20 + i * 180 + 16, 30), ic)
        w = d.textlength(NAMES[n], font=fs)
        d.text((20 + i * 180 + 80 - w / 2, 180), NAMES[n], fill=(240, 210, 90), font=fs)
    row.save(os.path.join(out_dir, "iconos_armadura.png"))
