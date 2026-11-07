"""Bloques nuevos del Reino: mesas de trabajo, cama del Nether, agua del Nether y hojas del árbol de hielo.

- Mesa del Aldeano Necromancer: modelo OFICIAL del usuario (tools/ref/mesa_necromancer_oficial.bbmodel), sin tocar
  sus píxeles (las caras de 236x236 se centran en un lienzo transparente de 256x256 para el atlas de Minecraft).
- Mesas de trabajo del bibliotecario (atril), domador (nido), granjero (cesto) y minero (carrito): diseño propio.
- Cama del Nether (2 bloques, se puede dormir en el Nether), texturas sacadas de la lámina del usuario.
- Agua del Nether (quieta y en movimiento, animada) y su balde (lámina del usuario).
- Hojas de Pico de Hielo y la Hoja del Frío Eterno.
"""
import base64
import io
import json
import math
import os
import random
import numpy as np
from PIL import Image
from common import ASSETS, MODID, save_json, save_text

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref")
BLOCK_TEX = os.path.join(ASSETS, "textures", "block")
ITEM_TEX = os.path.join(ASSETS, "textures", "item")
MODELS = os.path.join(ASSETS, "models")
rnd = random.Random(11)


def T(name):
    return "%s:block/%s" % (MODID, name)


def save_png(img, folder, name):
    os.makedirs(folder, exist_ok=True)
    img.save(os.path.join(folder, name + ".png"))


def facing_blockstate(name, model=None, extra=""):
    model = model or "%s:block/%s" % (MODID, name)
    v = {}
    for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270)):
        e = {"model": model}
        if y:
            e["y"] = y
        v["facing=%s%s" % (f, extra)] = e
    return {"variants": v}


# ====================================================================== pintura de texturas 16x16
def tex(fn, w=16, h=16):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            c = fn(x, y)
            if c is not None:
                img.putpixel((x, y), tuple(int(max(0, min(255, v))) for v in c[:3]) + ((c[3],) if len(c) > 3 else (255,)))
    return img


def noise(c, x, y, amt=10, seed=0):
    r = random.Random(x * 73856093 ^ y * 19349663 ^ seed)
    k = r.randint(-amt, amt)
    return (c[0] + k, c[1] + k, c[2] + k)


BLACKSTONE = (42, 36, 44)
BLACK_D = (26, 22, 28)
GOLDC = (226, 172, 52)
GOLD_D = (160, 112, 28)
CRIMSON = (116, 40, 58)
CRIMSON_D = (78, 26, 40)
CRIMSON_L = (150, 58, 76)
RUBYC = (220, 30, 40)
IRON = (150, 150, 158)
IRON_D = (96, 96, 106)
WOOD = (120, 84, 46)
WOOD_D = (84, 56, 30)


def stone_gold(x, y):
    if y in (0, 15) or x in (0, 15):
        return GOLDC if (x + y) % 3 else GOLD_D
    return noise(BLACKSTONE, x, y, 7, 1) if (x // 4 + y // 4) % 2 else noise(BLACK_D, x, y, 6, 2)


def column(x, y):
    if y in (2, 3, 12, 13):
        return GOLDC if x % 3 else GOLD_D
    if y == 7 and x in (7, 8):
        return RUBYC
    return noise(BLACKSTONE, x, y, 8, 3)


def crimson_planks(x, y):
    if y % 4 == 3:
        return CRIMSON_D
    c = CRIMSON_L if (x + (y // 4) * 5) % 9 == 0 else CRIMSON
    return noise(c, x, y, 6, 4)


def open_book(x, y):
    # libro abierto visto desde arriba: tapas rojas, páginas blancas con renglones, cinta dorada al medio
    if x in (0, 15) or y in (0, 15):
        return (130, 16, 26)
    if x in (7, 8):
        return (90, 10, 18) if y % 3 else GOLDC
    if y in (1, 14) or x in (1, 14):
        return (176, 24, 36)
    page = (236, 228, 214) if x < 7 else (226, 218, 204)
    if y % 2 == 1 and 3 <= y <= 12 and x not in (2, 6, 9, 13):
        return (70, 54, 50) if (x + y) % 5 else (150, 30, 40)
    return page


def straw(x, y):
    r = random.Random(x * 31 + y * 17)
    base = [(148, 40, 46), (176, 60, 52), (120, 30, 38), (196, 96, 64)][r.randint(0, 3)]
    if (x + y * 2) % 5 == 0:
        base = (90, 22, 30)
    return base


def basalt(x, y):
    return noise((62, 58, 66) if x % 4 else (44, 40, 48), x, y, 8, 5)


def dragon_egg_tex(x, y):
    r = random.Random(x * 13 + y * 7)
    c = (30, 20, 26) if r.random() < 0.7 else (48, 34, 40)
    if (x in (7, 8) and y % 3 != 1) or (y == 6 and 5 <= x <= 9) or (x == 10 and 8 <= y <= 11):
        c = (230, 40, 34)
    return c


def bone_tex(x, y):
    return (236, 228, 210) if (x + y) % 4 else (200, 190, 170)


def crate(x, y):
    if x in (0, 15) or y in (0, 15) or x == y or x == 15 - y:
        return noise(CRIMSON_D, x, y, 5, 6)
    return crimson_planks(x, y)


def harvest(x, y):
    r = random.Random(x * 101 + y * 37)
    k = r.random()
    if k < 0.45:
        return (170, 24, 34) if (x + y) % 2 else (120, 14, 22)        # verruga del Nether
    if k < 0.7:
        return (232, 104, 40) if (x * y) % 3 else (180, 60, 28)        # hongo carmesí
    if k < 0.85:
        return (60, 168, 150) if r.random() < 0.5 else (36, 120, 108)  # hongo distorsionado
    return (96, 20, 28)


def iron_side(x, y):
    if y in (0, 15):
        return IRON_D
    if y in (4, 11):
        return (70, 70, 80)
    if x in (1, 14) and y in (2, 6, 9, 13):
        return (190, 190, 200)
    return noise(IRON, x, y, 8, 7)


def ore_pile(x, y):
    r = random.Random(x * 57 + y * 91)
    k = r.random()
    if k < 0.3:
        return (222, 34, 44) if (x + y) % 2 else (150, 16, 26)      # rubí
    if k < 0.5:
        return (240, 196, 60)                                        # oro
    if k < 0.75:
        return (40, 36, 40)                                          # carbón
    return noise((112, 48, 46), x, y, 12, 8)                         # netherrack


def wheel(x, y):
    return (40, 38, 44) if (x + y) % 3 else (90, 90, 96)


def wood(x, y):
    return noise(WOOD if x % 3 else WOOD_D, x, y, 6, 9)


def iron(x, y):
    return noise(IRON, x, y, 10, 10)


WS_TEX = {
    "librarian_lectern_base": stone_gold, "librarian_lectern_column": column, "librarian_lectern_book": open_book,
    "librarian_lectern_wood": crimson_planks,
    "tamer_nest_straw": straw, "tamer_nest_base": basalt, "tamer_nest_egg": dragon_egg_tex, "tamer_nest_bone": bone_tex,
    "farmer_basket_side": crate, "farmer_basket_harvest": harvest, "farmer_basket_wood": wood, "farmer_basket_iron": iron,
    "miner_cart_side": iron_side, "miner_cart_load": ore_pile, "miner_cart_wheel": wheel, "miner_cart_wood": wood,
    "miner_cart_iron": iron,
}


def el(f, t, faces, rot=None, name=None):
    """Elemento de modelo Java. faces: textura para todas o dict cara->textura."""
    e = {"from": list(f), "to": list(t), "faces": {}}
    if name:
        e["name"] = name
    if isinstance(faces, str):
        faces = {k: faces for k in ("north", "south", "east", "west", "up", "down")}
    x1, y1, z1 = f
    x2, y2, z2 = t
    auto = {"north": [16 - x2, 16 - y2, 16 - x1, 16 - y1], "south": [x1, 16 - y2, x2, 16 - y1], "west": [z1, 16 - y2, z2, 16 - y1],
            "east": [16 - z2, 16 - y2, 16 - z1, 16 - y1], "up": [x1, z1, x2, z2], "down": [x1, 16 - z2, x2, 16 - z1]}
    for k, v in faces.items():
        uv = auto[k]
        e["faces"][k] = {"uv": [round(max(0, min(16, a)), 3) for a in uv], "texture": "#" + v}
    if rot:
        e["rotation"] = rot
    return e


def workstation_models():
    out = {}
    # --- atril del bibliotecario
    out["librarian_lectern"] = [
        el([2, 0, 2], [14, 2, 14], "base", name="base"),
        el([6, 2, 6], [10, 11, 10], "column", name="columna"),
        el([2, 11, 3], [14, 13, 13], {"up": "book", "down": "wood", "north": "wood", "south": "wood", "east": "wood", "west": "wood"},
           rot={"angle": -22.5, "axis": "x", "origin": [8, 12, 8]}, name="atril"),
    ]
    # --- nido del domador
    out["tamer_nest"] = [
        el([1, 0, 1], [15, 2, 15], "base", name="base"),
        el([3, 2, 3], [13, 3, 13], "straw", name="fondo"),
        el([1, 2, 1], [15, 5, 3], "straw", name="borde_n"),
        el([1, 2, 13], [15, 5, 15], "straw", name="borde_s"),
        el([1, 2, 3], [3, 5, 13], "straw", name="borde_o"),
        el([13, 2, 3], [15, 5, 13], "straw", name="borde_e"),
        el([6, 3, 6], [10, 9, 10], "egg", name="huevo"),
        el([7, 9, 7], [9, 10, 9], "egg", name="huevo_punta"),
        el([3, 3, 9], [9, 4, 10], "bone", rot={"angle": 22.5, "axis": "y", "origin": [6, 3, 9]}, name="hueso"),
    ]
    # --- cesto del granjero (con una azada apoyada)
    out["farmer_basket"] = [
        el([1, 0, 1], [15, 9, 15], {"north": "side", "south": "side", "east": "side", "west": "side", "down": "wood", "up": "harvest"}, name="cesto"),
        el([2, 9, 2], [14, 11, 14], {"up": "harvest", "north": "harvest", "south": "harvest", "east": "harvest", "west": "harvest"}, name="cosecha"),
        el([11, 6, 3], [12, 16, 4], "wood", rot={"angle": 22.5, "axis": "z", "origin": [11.5, 6, 3.5]}, name="mango"),
        el([8, 15, 3], [12, 16, 4], "iron", rot={"angle": 22.5, "axis": "z", "origin": [11.5, 6, 3.5]}, name="azada"),
    ]
    # --- carrito del minero (con un pico clavado en la carga)
    out["miner_cart"] = [
        el([1, 2, 2], [15, 9, 14], {"north": "side", "south": "side", "east": "side", "west": "side", "down": "side", "up": "load"}, name="carro"),
        el([2, 9, 3], [14, 11, 13], "load", name="carga"),
        el([2, 0, 1], [5, 3, 2], "wheel", name="rueda1"),
        el([11, 0, 1], [14, 3, 2], "wheel", name="rueda2"),
        el([2, 0, 14], [5, 3, 15], "wheel", name="rueda3"),
        el([11, 0, 14], [14, 3, 15], "wheel", name="rueda4"),
        el([9, 9, 7.5], [10, 16, 8.5], "wood", rot={"angle": -22.5, "axis": "z", "origin": [9.5, 10, 8]}, name="mango"),
        el([6, 15, 7.5], [13, 16, 8.5], "iron", rot={"angle": -22.5, "axis": "z", "origin": [9.5, 10, 8]}, name="pico"),
    ]
    textures = {
        "librarian_lectern": {"base": "librarian_lectern_base", "column": "librarian_lectern_column", "book": "librarian_lectern_book",
                              "wood": "librarian_lectern_wood"},
        "tamer_nest": {"base": "tamer_nest_base", "straw": "tamer_nest_straw", "egg": "tamer_nest_egg", "bone": "tamer_nest_bone"},
        "farmer_basket": {"side": "farmer_basket_side", "harvest": "farmer_basket_harvest", "wood": "farmer_basket_wood",
                          "iron": "farmer_basket_iron"},
        "miner_cart": {"side": "miner_cart_side", "load": "miner_cart_load", "wheel": "miner_cart_wheel", "wood": "miner_cart_wood",
                       "iron": "miner_cart_iron"},
    }
    return out, textures


# ====================================================================== mesa del Aldeano Necromancer (modelo oficial)
def necromancer_table():
    bb = json.load(open(os.path.join(REF, "mesa_necromancer_oficial.bbmodel"), encoding="utf-8"))
    names = []
    for t in bb["textures"]:
        raw = base64.b64decode(t["source"].split(",", 1)[1])
        img = Image.open(io.BytesIO(raw)).convert("RGBA")
        w, h = img.size
        canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        canvas.paste(img, ((256 - w) // 2, (256 - h) // 2))   # los píxeles del usuario quedan intactos
        nm = "necromancer_table_" + t["name"].replace("mesa_", "").replace(".png", "")
        save_png(canvas, BLOCK_TEX, nm)
        names.append((nm, w, h))
    off = (256 - names[0][1]) / 2.0

    def conv(u):  # uv 0-16 sobre 236 px -> uv 0-16 sobre 256 px
        return round((u / 16.0 * names[0][1] + off) / 256.0 * 16.0, 4)
    elements = []
    for e in bb["elements"]:
        faces = {}
        for fn, fv in e["faces"].items():
            if fv.get("texture") is None:
                continue
            faces[fn] = {"uv": [conv(v) for v in fv["uv"]], "texture": "#t%d" % fv["texture"]}
        elements.append({"name": e["name"], "from": e["from"], "to": e["to"], "faces": faces})
    texmap = {"t%d" % i: T(n) for i, (n, _, _) in enumerate(names)}
    texmap["particle"] = T(names[1][0])
    model = {"parent": "minecraft:block/block", "render_type": "minecraft:cutout", "textures": texmap, "elements": elements}
    return model


# ====================================================================== cama del Nether
def lamina():
    return np.array(Image.open(os.path.join(REF, "agua_cama", "lamina_cama_agua.png")).convert("RGB")).astype(int)


def sample_grid(a, x0, y0, x1, y1, nx, ny):
    out = np.zeros((ny, nx, 4), np.uint8)
    cw, ch = (x1 - x0) / nx, (y1 - y0) / ny
    for j in range(ny):
        for i in range(nx):
            cx, cy = int(x0 + (i + 0.5) * cw), int(y0 + (j + 0.5) * ch)
            blk = a[cy - 1:cy + 2, cx - 1:cx + 2].reshape(-1, 3)
            c = np.median(blk, 0)
            out[j, i, :3] = c
            out[j, i, 3] = 0 if c.max() < 30 else 255
    return out


def bed_textures():
    a = lamina()
    top = sample_grid(a, 636, 428, 736, 580, 16, 32)       # panel de arriba: almohada + frazada + borde de madera
    top[..., 3] = 255
    head_top = Image.fromarray(top[:16], "RGBA")
    foot_top = Image.fromarray(top[16:], "RGBA")
    side = sample_grid(a, 948, 450, 1078, 557, 32, 9)        # vista de lado (para el ícono y los costados)
    blanket = [tuple(int(v) for v in top[j, i, :3]) for j in range(8, 28) for i in range(16)]
    pillow_w = tuple(int(v) for v in top[2, 8, :3])

    def side_fn(head):
        def f(x, y):
            # costado del colchón (filas 7..12 de la cara), madera abajo
            if y < 7:
                return None
            if y >= 13:
                return WOOD if (x + y) % 3 else WOOD_D
            if head and x >= 10 and y < 10:
                return pillow_w if y > 7 else (200, 196, 210)
            c = blanket[(x * 5 + y * 11) % len(blanket)]
            return c if y < 12 else tuple(int(v * 0.6) for v in c)
        return f
    imgs = {
        "nether_bed_head_top": head_top, "nether_bed_foot_top": foot_top,
        "nether_bed_head_side": tex(side_fn(True)), "nether_bed_foot_side": tex(side_fn(False)),
        "nether_bed_end_head": tex(lambda x, y: None if y < 7 else ((200, 196, 210) if y < 12 and 2 <= x <= 13 else (WOOD if y >= 13 else (60, 30, 80)))),
        "nether_bed_end_foot": tex(lambda x, y: None if y < 7 else (WOOD if y >= 13 else blanket[(x * 3 + y * 7) % len(blanket)])),
        "nether_bed_bottom": tex(wood),
    }
    # ícono: vista de costado sacada de la lámina, centrada en 16x16
    icon = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    s = Image.fromarray(side, "RGBA").resize((16, 7), Image.NEAREST)
    icon.paste(s, (0, 6))
    return imgs, icon


def bed_models():
    tx = {"particle": T("nether_bed_head_top")}
    head = {"parent": "minecraft:block/block", "textures": dict(tx, top=T("nether_bed_head_top"), side=T("nether_bed_head_side"),
                                                              end=T("nether_bed_end_head"), bottom=T("nether_bed_bottom")),
            "elements": [
                # colchón (cabecera hacia el norte)
                {"from": [0, 3, 0], "to": [16, 9, 16], "faces": {
                    "up": {"uv": [0, 0, 16, 16], "texture": "#top"},
                    "north": {"uv": [0, 7, 16, 13], "texture": "#end"},
                    "east": {"uv": [0, 7, 16, 13], "texture": "#side"},
                    "west": {"uv": [16, 7, 0, 13], "texture": "#side"},
                    "down": {"uv": [0, 0, 16, 16], "texture": "#bottom"}}},
                {"from": [0, 0, 0], "to": [3, 3, 3], "faces": {k: {"uv": [0, 13, 3, 16], "texture": "#side"} for k in ("north", "east", "south", "west", "down")}},
                {"from": [13, 0, 0], "to": [16, 3, 3], "faces": {k: {"uv": [0, 13, 3, 16], "texture": "#side"} for k in ("north", "east", "south", "west", "down")}},
            ]}
    foot = {"parent": "minecraft:block/block", "textures": dict(tx, top=T("nether_bed_foot_top"), side=T("nether_bed_foot_side"),
                                                              end=T("nether_bed_end_foot"), bottom=T("nether_bed_bottom")),
            "elements": [
                {"from": [0, 3, 0], "to": [16, 9, 16], "faces": {
                    "up": {"uv": [0, 0, 16, 16], "texture": "#top"},
                    "south": {"uv": [0, 7, 16, 13], "texture": "#end"},
                    "east": {"uv": [0, 7, 16, 13], "texture": "#side"},
                    "west": {"uv": [16, 7, 0, 13], "texture": "#side"},
                    "down": {"uv": [0, 0, 16, 16], "texture": "#bottom"}}},
                {"from": [0, 0, 13], "to": [3, 3, 16], "faces": {k: {"uv": [0, 13, 3, 16], "texture": "#side"} for k in ("north", "east", "south", "west", "down")}},
                {"from": [13, 0, 13], "to": [16, 3, 16], "faces": {k: {"uv": [0, 13, 3, 16], "texture": "#side"} for k in ("north", "east", "south", "west", "down")}},
            ]}
    return head, foot


# ====================================================================== agua del Nether
def water_textures():
    src = np.array(Image.open(os.path.join(REF, "agua_cama", "agua.png")).convert("RGBA")).astype(int)
    h, w = src.shape[:2]
    base = np.zeros((16, 16, 4), np.uint8)
    for j in range(16):
        for i in range(16):
            cx, cy = int((i + 0.5) * w / 16), int((j + 0.5) * h / 16)
            base[j, i, :3] = np.median(src[cy - 2:cy + 3, cx - 2:cx + 3, :3].reshape(-1, 3), 0)
            base[j, i, 3] = 225
    # animación: las vetas brillantes laten como ondas (32 cuadros)
    lum = base[..., :3].max(2).astype(float)
    bright = (lum - lum.min()) / max(1, lum.max() - lum.min())
    frames = []
    for f in range(32):
        fr = base.copy().astype(float)
        for j in range(16):
            for i in range(16):
                wave = 0.5 + 0.5 * math.sin((f / 32.0) * 2 * math.pi + (i + j) * 0.55)
                k = 0.78 + 0.42 * wave * bright[j, i]
                fr[j, i, :3] = np.clip(fr[j, i, :3] * k, 0, 255)
        frames.append(fr.astype(np.uint8))
    still = Image.new("RGBA", (16, 16 * 32))
    for f, fr in enumerate(frames):
        still.paste(Image.fromarray(fr, "RGBA"), (0, f * 16))
    flow = Image.new("RGBA", (16, 16 * 32))
    for f in range(32):
        fr = np.roll(frames[f], shift=f // 2, axis=0)   # en movimiento: la textura corre hacia abajo
        flow.paste(Image.fromarray(fr, "RGBA"), (0, f * 16))
    return still, flow, Image.fromarray(base, "RGBA")


def bucket_icon():
    src = np.array(Image.open(os.path.join(REF, "agua_cama", "balde.png")).convert("RGBA")).astype(int)
    a = src[..., 3] > 40
    ys, xs = np.where(a.any(1))[0], np.where(a.any(0))[0]
    x0, x1, y0, y1 = xs[0], xs[-1] + 1, ys[0], ys[-1] + 1
    s = max(x1 - x0, y1 - y0) * 16 / 15.0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = np.zeros((16, 16, 4), np.uint8)
    for j in range(16):
        for i in range(16):
            px, py = int(cx - s / 2 + (i + 0.5) * s / 16), int(cy - s / 2 + (j + 0.5) * s / 16)
            if 0 <= px < src.shape[1] and 0 <= py < src.shape[0]:
                blk = src[max(0, py - 1):py + 2, max(0, px - 1):px + 2].reshape(-1, 4)
                op = blk[blk[:, 3] > 128]
                if len(op) >= 5:
                    out[j, i, :3] = np.median(op[:, :3], 0)
                    out[j, i, 3] = 255
    return Image.fromarray(out, "RGBA")


# ====================================================================== hojas de hielo
def frost_leaves():
    def f(x, y):
        r = random.Random(x * 131 + y * 71)
        k = r.random()
        if k < 0.18:
            return None
        if k < 0.3:
            return (230, 250, 255)
        c = [(112, 196, 240), (80, 160, 224), (58, 120, 200), (150, 220, 250)][r.randint(0, 3)]
        return c
    return tex(f)


# ====================================================================== vista previa de modelos de bloque
def render_model(elements, textures, yaw=35, pitch=28, size=300, bg=(30, 24, 26)):
    """Render ortográfico simple de un modelo Java (con rotación de elementos) para mostrar los diseños."""
    cy_, sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    M = np.array([[1, 0, 0], [0, cp, sp], [0, -sp, cp]]) @ np.array([[cy_, 0, -sy_], [0, 1, 0], [sy_, 0, cy_]])
    ss = 2
    W = size * ss
    col = np.zeros((W, W, 3))
    col[:] = bg
    zb = np.full((W, W), 1e9)
    sc = size * 0.036 * ss

    def scr(p):
        q = M @ (np.array(p, float) - 8)
        return np.array([W / 2 - q[0] * sc, W / 2 - q[1] * sc, q[2]])
    shade = {"up": 1.0, "down": 0.5, "north": 0.85, "south": 0.85, "east": 0.7, "west": 0.7}
    NORM = {"north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0), "east": (1, 0, 0), "up": (0, 1, 0), "down": (0, -1, 0)}
    for e in elements:
        x1, y1, z1 = e["from"]
        x2, y2, z2 = e["to"]
        R = np.eye(3)
        org = np.zeros(3)
        if "rotation" in e:
            r = e["rotation"]
            a = math.radians(r["angle"])
            c, s = math.cos(a), math.sin(a)
            R = {"x": np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), "y": np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
                 "z": np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[r["axis"]]
            org = np.array(r["origin"], float)
        geo = {"north": ((x2, y2, z1), (x1 - x2, 0, 0), (0, y1 - y2, 0)), "south": ((x1, y2, z2), (x2 - x1, 0, 0), (0, y1 - y2, 0)),
               "west": ((x1, y2, z1), (0, 0, z2 - z1), (0, y1 - y2, 0)), "east": ((x2, y2, z2), (0, 0, z1 - z2), (0, y1 - y2, 0)),
               "up": ((x1, y2, z1), (x2 - x1, 0, 0), (0, 0, z2 - z1)), "down": ((x1, y1, z2), (x2 - x1, 0, 0), (0, 0, z1 - z2))}
        for fn, fv in e["faces"].items():
            n = R @ np.array(NORM[fn], float)
            if (M @ n)[2] >= 0:
                continue
            o, eu, ev = [np.array(v, float) for v in geo[fn]]
            o = R @ (o - org) + org
            eu, ev = R @ eu, R @ ev
            img = textures[fv["texture"].lstrip("#")]
            tw, th = img.shape[1], img.shape[0]
            u1, v1, u2, v2 = fv["uv"]
            A = scr(o)
            U = scr(o + eu) - A
            Vv = scr(o + ev) - A
            det = U[0] * Vv[1] - U[1] * Vv[0]
            if abs(det) < 1e-6:
                continue
            cs = np.array([A, A + U, A + Vv, A + U + Vv])
            xa, xb = max(0, int(cs[:, 0].min())), min(W - 1, int(cs[:, 0].max()) + 1)
            ya, yb = max(0, int(cs[:, 1].min())), min(W - 1, int(cs[:, 1].max()) + 1)
            if xa > xb or ya > yb:
                continue
            yy, xx = np.mgrid[ya:yb + 1, xa:xb + 1]
            px, py = xx + .5 - A[0], yy + .5 - A[1]
            s_ = (px * Vv[1] - py * Vv[0]) / det
            t_ = (U[0] * py - U[1] * px) / det
            ins = (s_ >= 0) & (s_ < 1) & (t_ >= 0) & (t_ < 1)
            z = A[2] + s_ * U[2] + t_ * Vv[2]
            tu = np.clip(((u1 + s_ * (u2 - u1)) / 16 * tw).astype(int), 0, tw - 1)
            tv = np.clip(((v1 + t_ * (v2 - v1)) / 16 * th).astype(int), 0, th - 1)
            tx = img[tv, tu].astype(float)
            ok = ins & (tx[..., 3] > 25) & (z < zb[ya:yb + 1, xa:xb + 1])
            col[ya:yb + 1, xa:xb + 1][ok] = tx[..., :3][ok] * shade[fn]
            zb[ya:yb + 1, xa:xb + 1][ok] = z[ok]
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).resize((size, size), Image.LANCZOS)


# ====================================================================== escribir todo
WORKSTATIONS = ["necromancer_table", "librarian_lectern", "tamer_nest", "farmer_basket", "miner_cart"]


def write_all():
    bm = os.path.join(MODELS, "block")
    im = os.path.join(MODELS, "item")
    # mesa del necromancer
    save_json(os.path.join(bm, "necromancer_table.json"), necromancer_table())
    # mesas de trabajo diseñadas
    for k, fn in WS_TEX.items():
        save_png(tex(fn), BLOCK_TEX, k)
    models, texsets = workstation_models()
    for name, elements in models.items():
        tx = {k: T(v) for k, v in texsets[name].items()}
        tx["particle"] = tx[list(tx)[0]]
        save_json(os.path.join(bm, name + ".json"), {"parent": "minecraft:block/block", "render_type": "minecraft:cutout",
                                                     "textures": tx, "elements": elements})
    for name in WORKSTATIONS:
        save_json(os.path.join(ASSETS, "blockstates", name + ".json"), facing_blockstate(name))
        save_json(os.path.join(im, name + ".json"), {"parent": "%s:block/%s" % (MODID, name)})
    # cama del Nether
    imgs, icon = bed_textures()
    for k, v in imgs.items():
        save_png(v, BLOCK_TEX, k)
    save_png(icon, ITEM_TEX, "nether_bed")
    head, foot = bed_models()
    save_json(os.path.join(bm, "nether_bed_head.json"), head)
    save_json(os.path.join(bm, "nether_bed_foot.json"), foot)
    v = {}
    for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270)):
        for part in ("head", "foot"):
            for occ in ("false", "true"):
                e = {"model": "%s:block/nether_bed_%s" % (MODID, part)}
                if y:
                    e["y"] = y
                v["facing=%s,occupied=%s,part=%s" % (f, occ, part)] = e
    save_json(os.path.join(ASSETS, "blockstates", "nether_bed.json"), {"variants": v})
    save_json(os.path.join(im, "nether_bed.json"), {"parent": "minecraft:item/generated", "textures": {"layer0": "%s:item/nether_bed" % MODID}})
    # agua del Nether
    still, flow, base = water_textures()
    save_png(still, BLOCK_TEX, "nether_water_still")
    save_png(flow, BLOCK_TEX, "nether_water_flow")
    for nm in ("nether_water_still", "nether_water_flow"):
        save_text(os.path.join(BLOCK_TEX, nm + ".png.mcmeta"), json.dumps({"animation": {"frametime": 2, "interpolate": True}}))
    save_json(os.path.join(ASSETS, "blockstates", "nether_water.json"), {"variants": {"": {"model": "%s:block/nether_water" % MODID}}})
    save_json(os.path.join(bm, "nether_water.json"), {"textures": {"particle": T("nether_water_still")}})
    save_png(bucket_icon(), ITEM_TEX, "nether_water_bucket")
    save_json(os.path.join(im, "nether_water_bucket.json"), {"parent": "minecraft:item/generated",
                                                             "textures": {"layer0": "%s:item/nether_water_bucket" % MODID}})
    # hojas de hielo
    save_png(frost_leaves(), BLOCK_TEX, "frost_leaves")
    save_json(os.path.join(ASSETS, "blockstates", "frost_leaves.json"), {"variants": {"": {"model": "%s:block/frost_leaves" % MODID}}})
    save_json(os.path.join(bm, "frost_leaves.json"), {"parent": "minecraft:block/leaves", "render_type": "minecraft:cutout_mipped",
                                                      "textures": {"all": T("frost_leaves")}})
    save_json(os.path.join(im, "frost_leaves.json"), {"parent": "%s:block/frost_leaves" % MODID})
    return base


def preview(path):
    """Lámina con las 4 mesas nuevas, la mesa del necromancer y la cama."""
    from PIL import ImageDraw, ImageFont
    def load_tex(model):
        out = {}
        for k, v in model["textures"].items():
            p = os.path.join(BLOCK_TEX, v.split("block/")[1] + ".png")
            out[k] = np.array(Image.open(p).convert("RGBA"))
        return out
    bm = os.path.join(MODELS, "block")
    items = []
    for name, label in (("necromancer_table", "Aldeano Necromancer"), ("librarian_lectern", "Bibliotecario: Atril"),
                        ("tamer_nest", "Domador: Nido"), ("farmer_basket", "Granjero: Cesto"), ("miner_cart", "Minero: Carrito")):
        m = json.load(open(os.path.join(bm, name + ".json")))
        items.append((label, render_model(m["elements"], load_tex(m))))
    head = json.load(open(os.path.join(bm, "nether_bed_head.json")))
    foot = json.load(open(os.path.join(bm, "nether_bed_foot.json")))
    # la cama son dos bloques: el pie va al sur de la cabecera
    th, tf = load_tex(head), load_tex(foot)
    tall = {("h_" + k): v for k, v in th.items()}
    tall.update({("f_" + k): v for k, v in tf.items()})
    els = []
    for e in head["elements"]:
        e2 = json.loads(json.dumps(e))
        e2["from"] = [e["from"][0], e["from"][1], e["from"][2] - 8]
        e2["to"] = [e["to"][0], e["to"][1], e["to"][2] - 8]
        for f in e2["faces"].values():
            f["texture"] = "#h_" + f["texture"].lstrip("#")
        els.append(e2)
    for e in foot["elements"]:
        e2 = json.loads(json.dumps(e))
        e2["from"] = [e["from"][0], e["from"][1], e["from"][2] + 8]
        e2["to"] = [e["to"][0], e["to"][1], e["to"][2] + 8]
        for f in e2["faces"].values():
            f["texture"] = "#f_" + f["texture"].lstrip("#")
        els.append(e2)
    items.append(("Cama del Nether", render_model(els, tall, yaw=-40, pitch=32)))
    S = Image.new("RGB", (3 * 310 + 10, 2 * 340 + 10), (18, 12, 14))
    d = ImageDraw.Draw(S)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    for i, (label, img) in enumerate(items):
        x, y = 10 + (i % 3) * 310, 10 + (i // 3) * 340
        S.paste(img, (x, y + 30))
        d.text((x + 6, y + 4), label, font=f, fill=(240, 220, 200))
    S.save(path)


if __name__ == "__main__":
    write_all()
    preview("/tmp/blocks_preview.png")
