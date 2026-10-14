"""Almas: ítem "Alma" (skin del usuario, ref/alma_skin.png), Hoz de almas, partículas de fuego negro y de alma roja,
y la textura de la bola de fuego negra del dragón."""
import math
import os
import random
from PIL import Image
from common import ASSETS, save_json, MODID

HERE = os.path.dirname(os.path.abspath(__file__))


def soul_icon():
    """La skin del alma (13x20 píxeles) reducida a 11x16 y centrada en 16x16."""
    s = Image.open(os.path.join(HERE, "ref", "alma_skin.png")).convert("RGBA")
    r = s.resize((11, 16), Image.NEAREST)
    out = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    out.paste(r, (2, 0))
    return out


def scythe_icon():
    """Hoz de almas: mango de piedra negra con vetas de alma y hoja curva de rubí."""
    rows = [
        "................",
        ".....rrRRRRRb...",
        "...rRRLLLLRRRb..",
        "..rRLLRRRRbRHHb.",
        ".rRLRr....bHSHb.",
        ".rLRr.....hSSb..",
        "rLRr.....hSSb...",
        "rRr.....hSSb....",
        "rr.....hSSb.....",
        "r.....hSSb......",
        "......hSb.......",
        ".....hSb........",
        "....hSb.........",
        "...hSb..........",
        "..ss............",
        "................",
    ]
    pal = {"r": (120, 10, 18), "R": (214, 30, 40), "L": (255, 120, 120), "b": (20, 14, 18), "H": (230, 190, 70),
           "S": (52, 40, 48), "h": (90, 76, 86), "s": (255, 70, 60)}
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                im.putpixel((x, y), pal[ch] + (255,))
    return im


def dragon_staff_icon():
    """Báculo de dragón: vara de obsidiana con anillos de oro y una cabeza de dragón negra con un rubí entre los cuernos."""
    rows = [
        "..........H...H.",
        "..........hH.Hh.",
        "...........kRk..",
        "..........kRLRk.",
        "..........kkRkk.",
        "...........ekk..",
        "..........Gk....",
        ".........sG.....",
        "........ss......",
        ".......sS.......",
        "......Gs........",
        ".....sG.........",
        "....sS..........",
        "...sS...........",
        "..sS............",
        ".rr.............",
    ]
    pal = {"H": (200, 200, 200), "h": (120, 120, 120), "k": (30, 24, 32), "e": (255, 50, 40), "R": (214, 30, 40),
           "L": (255, 140, 130), "G": (240, 190, 60), "s": (40, 30, 52), "S": (80, 60, 110), "r": (200, 30, 40)}
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                im.putpixel((x, y), pal[ch] + (255,))
    return im


def black_flame_frames(n=4):
    """Llamas negras de 8x8: núcleo negro, borde rojo oscuro y chispas rojas; cada cuadro más pequeño."""
    frames = []
    rnd = random.Random(7)
    for k in range(n):
        im = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        h = 7.5 - k * 1.3
        for y in range(8):
            for x in range(8):
                t = (7.5 - y) / max(h, 1)            # 0 abajo, 1 en la punta
                if t > 1 or t < 0:
                    continue
                w = 3.4 * math.sin(math.pi * min(1.0, 0.25 + t * 0.85)) * (1.0 - 0.15 * k)
                d = abs(x + 0.5 - 4)
                if d > w:
                    continue
                edge = d > w - 1.1
                if edge:
                    c = (150, 18, 30, 255) if rnd.random() < 0.6 else (90, 8, 20, 255)
                else:
                    c = (10, 4, 8, 255) if rnd.random() < 0.8 else (40, 6, 14, 255)
                im.putpixel((x, y), c)
        frames.append(im)
    return frames


def black_fireball():
    """Bola de fuego negra de 16x16 con borde rojo y un alma roja dentro."""
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    rnd = random.Random(3)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if d > 7.6:
                continue
            if d > 6.2:
                c = (200, 30, 36) if rnd.random() < 0.7 else (255, 90, 70)
            elif d > 4.8:
                c = (60, 6, 14) if rnd.random() < 0.7 else (110, 14, 22)
            else:
                c = (8, 2, 6) if rnd.random() < 0.85 else (36, 4, 10)
            im.putpixel((x, y), c + (255,))
    small = Image.open(os.path.join(HERE, "ref", "alma_skin.png")).convert("RGBA").resize((5, 7), Image.NEAREST)
    im.paste(small, (6, 5), small)
    return im


def write_all():
    item = os.path.join(ASSETS, "textures", "item")
    part = os.path.join(ASSETS, "textures", "particle")
    os.makedirs(part, exist_ok=True)
    soul_icon().save(os.path.join(item, "soul.png"))
    scythe_icon().save(os.path.join(item, "soul_scythe.png"))
    dragon_staff_icon().save(os.path.join(item, "dragon_staff.png"))
    soul_icon().save(os.path.join(part, "red_soul.png"))
    names = []
    for i, fr in enumerate(black_flame_frames()):
        fr.save(os.path.join(part, "black_flame_%d.png" % i))
        names.append("%s:black_flame_%d" % (MODID, i))
    save_json(os.path.join(ASSETS, "particles", "black_flame.json"), {"textures": names})
    save_json(os.path.join(ASSETS, "particles", "red_soul.json"), {"textures": ["%s:red_soul" % MODID]})
    black_fireball().save(os.path.join(ASSETS, "textures", "entity", "black_fireball.png"))


if __name__ == "__main__":
    write_all()
