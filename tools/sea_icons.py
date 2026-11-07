"""Íconos (16x16, estilo Minecraft) de los objetos nuevos del Océano Púrpura y del Dragón Infernal,
las capas de armadura de los cascos, la textura del Tridente de Rubí lanzado, la bola de fuego explosiva
y el huevo del Dragón Infernal.
"""
import math
import os

import numpy as np
from PIL import Image

from common import ASSETS

HERE = os.path.dirname(os.path.abspath(__file__))


def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def outline(img, color):
    """Borde oscuro de 1 píxel alrededor de lo dibujado (como los ítems de Minecraft)."""
    a = np.array(img)
    m = a[..., 3] > 0
    out = a.copy()
    h, w = m.shape
    for y in range(h):
        for x in range(w):
            if m[y, x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and m[yy, xx]:
                    out[y, x] = color
                    break
    return Image.fromarray(out)


def shade_grid(rows, pal):
    h, w = len(rows), len(rows[0])
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for y, r in enumerate(rows):
        assert len(r) == w, (y, r)
        for x, ch in enumerate(r):
            if ch != ".":
                px[x, y] = pal[ch]
    return img


# ---------------------------------------------------------------- peces
def fish(cooked=False):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    if cooked:
        top, mid, belly, fin = hexc("6b2e14"), hexc("a5521f"), hexc("d98c3c"), hexc("5a2410")
    else:
        top, mid, belly, fin = hexc("9e1f16"), hexc("e8561a"), hexc("ffc23a"), hexc("c23214")
    for y in range(16):
        for x in range(16):
            dx, dy = (x - 6.0) / 5.2, (y - 8.0) / 3.4
            if dx * dx + dy * dy <= 1.0:
                t = (y - 4.6) / 6.8
                c = top if t < 0.33 else mid if t < 0.7 else belly
                px[x, y] = c
            # cola
            ay = abs(y - 8)
            if 11 <= x <= 14 and ay <= (x - 10) * 1.1 and not (x >= 13 and ay <= (x - 13) * 1.5 + 0.4):
                px[x, y] = fin
    # aleta de arriba y de abajo
    for (x, y) in ((6, 4), (7, 4), (8, 4), (7, 3), (6, 12), (7, 12)):
        px[x, y] = fin
    # brasas (pintas que brillan)
    if not cooked:
        for (x, y) in ((5, 6), (8, 7), (9, 9), (4, 9), (10, 6)):
            px[x, y] = hexc("ffe48a")
    else:
        for (x, y) in ((5, 7), (8, 8), (10, 7)):
            px[x, y] = hexc("3b1608")   # marcas de la parrilla
        for (x, y) in ((6, 9), (9, 9)):
            px[x, y] = hexc("3b1608")
    # ojo
    px[3, 7] = hexc("1a0804") if not cooked else hexc("f2e2c0")
    img = outline(img, hexc("2a0a06"))
    return img


# ---------------------------------------------------------------- gel del vacío
def void_gel():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for y in range(16):
        for x in range(16):
            d = math.hypot((x - 7.5) / 5.2, (y - 9.0) / 4.4)
            drip = x in (5, 10) and 12 <= y <= 13
            if d <= 1.0 or drip:
                t = min(1.0, d)
                c = (int(90 + 80 * (1 - t)), int(30 + 40 * (1 - t)), int(150 + 90 * (1 - t)), 230)
                px[x, y] = c
    for (x, y) in ((7, 8), (8, 9), (7, 10), (9, 8)):
        px[x, y] = hexc("1c0838")          # el núcleo oscuro del vacío
    for (x, y) in ((5, 6), (6, 6), (5, 7)):
        px[x, y] = hexc("e6c8ff")          # brillo
    px[11, 7] = hexc("c9a2ff")
    return outline(img, hexc("2a0d4a"))


# ---------------------------------------------------------------- caparazón de basalto
def basalt_shell():
    rows = [
        "................",
        "................",
        "................",
        "......2222......",
        "....22333322....",
        "...2334444332...",
        "..233444o44332..",
        "..23444o444432..",
        ".2344o44444o432.",
        ".23444o444o4432.",
        ".2333344443333 .".replace(" ", "2"),
        "..222233332222..",
        "....22222222....",
        "................",
        "................",
        "................",
    ]
    pal = {"2": hexc("2b2b31"), "3": hexc("4a4a52"), "4": hexc("6b6b74"), "o": hexc("ff7a1a")}
    return outline(shade_grid(rows, pal), hexc("141418"))


# ---------------------------------------------------------------- escama obsidiana
def obsidian_scale():
    rows = [
        "................",
        "................",
        "......1111......",
        ".....133331.....",
        "....13344331....",
        "...1334554331...",
        "...1345665431...",
        "...1345665431...",
        "...1334554331...",
        "....13344331....",
        "....13344331....",
        ".....133331.....",
        "......1331......",
        ".......11.......",
        "................",
        "................",
    ]
    pal = {"1": hexc("0c0614"), "3": hexc("1e1030"), "4": hexc("3b1f5c"), "5": hexc("6b3fa0"), "6": hexc("b48cff")}
    return shade_grid(rows, pal)


# ---------------------------------------------------------------- cascos
HELMET = [
    "................",
    "................",
    ".....111111.....",
    "...1144444311...",
    "..134455544331..",
    "..134444444331..",
    ".13344333344331.",
    ".13311111111331.",
    ".1331......1331.",
    ".1331......1331.",
    ".131........131.",
    ".11..........11.",
    "................",
    "................",
    "................",
    "................",
]


def turtle_helmet():
    pal = {"1": hexc("0c0614"), "3": hexc("24133a"), "4": hexc("3d2260"), "5": hexc("8a5cd0")}
    img = shade_grid(HELMET, pal)
    px = img.load()
    for (x, y) in ((5, 4), (9, 3), (11, 5), (4, 6)):
        px[x, y] = hexc("b48cff")   # brillos de obsidiana
    return img


def serpent_helmet():
    pal = {"1": hexc("1a0614"), "3": hexc("5a1440"), "4": hexc("a0286e"), "5": hexc("ff6ab4")}
    img = shade_grid(HELMET, pal)
    px = img.load()
    # cresta de aleta en la parte de arriba
    for (x, y) in ((7, 0), (8, 0), (6, 1), (7, 1), (8, 1), (9, 1)):
        px[x, y] = hexc("ffb347")
    for (x, y) in ((7, 2), (8, 2)):
        px[x, y] = hexc("ff8a1a")
    # escamas
    for (x, y) in ((4, 5), (6, 5), (8, 5), (10, 5), (5, 4), (9, 4)):
        px[x, y] = hexc("6e1a50")
    return img


def armor_layer(kind):
    """Capa 1 de armadura (64x32, solo la cabeza): escamas sobre la cabeza y la frente, la cara queda libre."""
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    px = img.load()
    if kind == "obsidian_turtle":
        dark, mid, light, hi = hexc("0c0614"), hexc("24133a"), hexc("3d2260"), hexc("8a5cd0")
    else:
        dark, mid, light, hi = hexc("1a0614"), hexc("5a1440"), hexc("a0286e"), hexc("ff6ab4")

    def scale_color(x, y):
        k = ((x // 2) + (y // 2) * 3) % 5
        c = [mid, light, mid, dark, light][k]
        if (x + y * 2) % 7 == 0:
            c = hi
        return c
    # cubo de la cabeza: arriba (8..16, 0..8), abajo (16..24, 0..8), lados y frente/atrás (0..32, 8..16)
    for y in range(0, 8):
        for x in range(8, 16):
            px[x, y] = scale_color(x, y)
    for y in range(8, 16):
        for x in range(0, 32):
            face = x // 8
            fx = x % 8
            ry = y - 8
            if face == 1:   # frente: banda de la frente y los costados de la cara
                if ry <= 2 or fx <= 0 or fx >= 7:
                    px[x, y] = scale_color(x, y)
            elif ry <= 6:
                px[x, y] = scale_color(x, y)
    if kind == "serpent":
        # cresta de aleta (en la capa de sombrero, arriba y atrás)
        for y in range(0, 8):
            for x in range(43, 45):
                px[x, y] = hexc("ffb347")
        for y in range(8, 12):
            for x in range(56, 64):
                if x in (59, 60):
                    px[x, y] = hexc("ff8a1a")
    return img


# ---------------------------------------------------------------- Tridente de Rubí lanzado (modelo del tridente: 32x32)
def trident_entity():
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = img.load()
    ruby = [hexc("7a0c14"), hexc("c41a2a"), hexc("ff4d5e"), hexc("ffb0b8")]
    gold = [hexc("8a5a10"), hexc("d4a21e"), hexc("ffe27a")]
    shaft = [hexc("2a0d12"), hexc("4a1620")]
    for y in range(32):
        for x in range(32):
            px[x, y] = ruby[1]
    # punta del medio (0,0)-(4,5) y puntas de los costados (4,3)-(8,8)
    for (x0, y0, x1, y1) in ((0, 0, 4, 5), (4, 3, 8, 8)):
        for y in range(y0, y1):
            for x in range(x0, x1):
                px[x, y] = ruby[3] if y == y0 else ruby[2] if (x - x0) % 2 == 0 else ruby[1]
    # base dorada (4,0)-(12,3)
    for y in range(0, 3):
        for x in range(4, 12):
            px[x, y] = gold[2] if y == 0 else gold[1] if x % 2 else gold[0]
    # asta (0,6)-(4,32): oscura con anillos de oro y rubí
    for y in range(6, 32):
        for x in range(0, 4):
            c = shaft[(x + y) % 2]
            if y % 7 == 0:
                c = gold[1]
            if y % 7 == 3 and x % 2 == 0:
                c = ruby[2]
            px[x, y] = c
    return img


# ---------------------------------------------------------------- recolores (copias nuevas, los originales no se tocan)
def fire_recolor(src, glow=False):
    a = np.array(Image.open(src).convert("RGBA")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = (0.5 * r + 0.35 * g + 0.15 * b) / 255.0
    red = (r > g * 1.6) & (r > 90)
    out = a.copy()
    # grietas / fuego: de naranja a amarillo
    t = np.clip(lum * 1.6, 0, 1)
    out[..., 0] = np.where(red, 255, out[..., 0])
    out[..., 1] = np.where(red, 90 + 150 * t, out[..., 1])
    out[..., 2] = np.where(red, 20 + 60 * t ** 2, out[..., 2])
    # cáscara: carbón tostado
    if not glow:
        shell = ~red & (a[..., 3] > 0)
        out[..., 0] = np.where(shell, np.clip(r * 1.45 + 10, 0, 255), out[..., 0])
        out[..., 1] = np.where(shell, np.clip(g * 0.95 + 4, 0, 255), out[..., 1])
        out[..., 2] = np.where(shell, np.clip(b * 0.6, 0, 255), out[..., 2])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


ICONS = {
    "pez_brasa": lambda: fish(False),
    "cooked_pez_brasa": lambda: fish(True),
    "void_gel": void_gel,
    "basalt_shell": basalt_shell,
    "obsidian_scale": obsidian_scale,
    "obsidian_turtle_helmet": turtle_helmet,
    "serpent_helmet": serpent_helmet,
}


def write_all():
    item = os.path.join(ASSETS, "textures", "item")
    ent = os.path.join(ASSETS, "textures", "entity")
    arm = os.path.join(ASSETS, "textures", "models", "armor")
    for name, fn in ICONS.items():
        fn().save(os.path.join(item, name + ".png"))
    for k in ("obsidian_turtle", "serpent"):
        armor_layer(k).save(os.path.join(arm, k + "_layer_1.png"))
        Image.new("RGBA", (64, 32), (0, 0, 0, 0)).save(os.path.join(arm, k + "_layer_2.png"))
    # tridente lanzado y en la mano: el modelo del tridente (del .glb del usuario) con sus colores pasados a rojo
    lanzado = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref", "sea", "tridente_rubi_lanzado.png")
    (Image.open(lanzado).convert("RGBA") if os.path.exists(lanzado) else trident_entity()).save(os.path.join(ent, "ruby_trident.png"))
    fire_recolor(os.path.join(ent, "black_fireball.png")).save(os.path.join(ent, "infernal_fireball.png"))
    fire_recolor(os.path.join(ent, "nether_dragon_egg.png")).save(os.path.join(ent, "infernal_dragon_egg.png"))
    fire_recolor(os.path.join(ent, "nether_dragon_egg_glowmask.png"), glow=True).save(
        os.path.join(ent, "infernal_dragon_egg_glowmask.png"))
    fire_recolor(os.path.join(item, "dragon_egg.png")).save(os.path.join(item, "infernal_dragon_egg.png"))
