"""Armas nuevas de 32x32: espada larga de rubí (Guerrero Real) y ballesta de rubí (Ballestero)."""
import math
import os
from PIL import Image

N = 32
OUT = (22, 6, 10)
GOLD = (222, 168, 40); GOLD_L = (255, 222, 100); GOLD_D = (150, 100, 20)
STEEL = (64, 62, 76); STEEL_D = (40, 38, 50); STEEL_L = (196, 196, 210); STEEL_M = (120, 118, 134)
RUBY = (226, 26, 36); RUBY_L = (255, 120, 120); RUBY_D = (128, 8, 16); WHITE = (255, 236, 236)
LEA = (110, 22, 30); LEA_D = (70, 12, 18)
WOOD = (74, 20, 26); WOOD_L = (128, 44, 46); WOOD_D = (40, 10, 14)
STRING = (232, 222, 200)
SHAFT = (176, 140, 96); HEAD = (200, 200, 214); FL = (236, 236, 232)


def outline(im):
    src = im.copy()
    for y in range(N):
        for x in range(N):
            if src.getpixel((x, y))[3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    X, Y = x + dx, y + dy
                    if 0 <= X < N and 0 <= Y < N and src.getpixel((X, Y))[3]:
                        im.putpixel((x, y), OUT + (255,))
                        break
    return im


# ------------------------------------------------------------------ espada larga
def longsword():
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    p0 = (2.6, 29.4)                                   # pomo (abajo a la izquierda)
    u = (1 / math.sqrt(2), -1 / math.sqrt(2))          # hacia la punta
    n = (1 / math.sqrt(2), 1 / math.sqrt(2))           # perpendicular
    for y in range(N):
        for x in range(N):
            dx, dy = x + 0.5 - p0[0], y + 0.5 - p0[1]
            t = dx * u[0] + dy * u[1]
            s = dx * n[0] + dy * n[1]
            a = abs(s)
            c = None
            if t < 0:
                continue
            if t < 2.4:                                   # pomo
                if a <= 1.7:
                    c = RUBY if (a < 0.8 and 0.6 < t < 1.9) else (GOLD_L if s < 0 else GOLD)
            elif t < 9.6:                                 # empuñadura a dos manos
                if a <= 0.95:
                    k = int((t - 2.4) / 1.25)
                    c = GOLD if abs(t - 6.0) < 0.55 else (LEA if k % 2 == 0 else LEA_D)
            elif t < 11.8:                                # guarda curva
                lim = 6.2
                curve = 0.32 * (a ** 2) / 6.2
                if a <= lim and (t - 9.6) >= curve - 0.6 and (t - 9.6) <= curve + 2.2:
                    if a < 1.0:
                        c = RUBY_L if s < 0 else RUBY
                    else:
                        c = GOLD_L if (t - 9.6 - curve) < 0.7 else (GOLD if a < 4.2 else GOLD_D)
            else:                                         # hoja
                L = 38.0
                if t > L:
                    continue
                w = 2.25 - 0.6 * (t - 11.8) / (L - 11.8)
                if t > L - 3.2:
                    w *= (L - t) / 3.2                     # punta
                if a <= w + 0.15:
                    if a > w - 0.7:
                        c = STEEL_L if s < 0 else STEEL_M  # filo
                    elif a > w - 1.3:
                        c = STEEL_D
                    elif a < 0.6 and 13 < t < L - 4:
                        c = WHITE if (int(t) % 5 == 0 and a < 0.35) else RUBY   # canal de rubí
                    else:
                        c = STEEL if s < 0 else STEEL_D
            if c:
                im.putpixel((x, y), c + (255,))
    return outline(im)


# ------------------------------------------------------------------ ballesta
def crossbow(state):
    """state: 'standby', 'pulling_0', 'pulling_1', 'pulling_2', 'arrow', 'firework'.
    La ballesta apunta hacia arriba a la derecha (como la de Minecraft)."""
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    put = lambda x, y, c: im.putpixel((int(x), int(y)), c + (255,)) if 0 <= x < N and 0 <= y < N else None
    u = (1 / math.sqrt(2), -1 / math.sqrt(2))          # hacia adelante (arriba-derecha)
    n = (1 / math.sqrt(2), 1 / math.sqrt(2))
    base = (6.0, 26.0)                                  # culata
    pull = {"standby": 0.0, "pulling_0": 0.35, "pulling_1": 0.7, "pulling_2": 1.0, "arrow": 1.0, "firework": 1.0}[state]
    for y in range(N):
        for x in range(N):
            dx, dy = x + 0.5 - base[0], y + 0.5 - base[1]
            t = dx * u[0] + dy * u[1]
            s = dx * n[0] + dy * n[1]
            a = abs(s)
            c = None
            # culata y cuerpo de madera roja
            if -1.5 <= t <= 25 and a <= (1.6 if t < 6 else 1.1):
                c = WOOD_L if s < -0.3 else (WOOD if a < 0.8 else WOOD_D)
                if abs(t - 7) < 0.6 or abs(t - 15) < 0.6:
                    c = GOLD
                if t < -0.5:
                    c = GOLD_D
            # arco (palas) de acero con rubí en el centro: en la parte delantera, perpendicular al cuerpo
            tb = 19.0 - 3.0 * (a / 9.5) ** 2
            if a <= 9.5 and abs(t - tb) <= 0.85:
                c = RUBY if a < 1.2 else (STEEL_L if t - tb > 0 else STEEL)
                if 8.6 < a <= 9.5:
                    c = GOLD
            # estribo dorado en la punta
            if 24.2 <= t <= 27.2 and 1.0 <= a <= 2.2 or (26.4 <= t <= 27.4 and a <= 2.2):
                c = GOLD if s < 0 else GOLD_D
            if c:
                put(x, y, c)
    # cuerda: de las puntas a un punto que se mueve hacia atrás al tensar
    tip_t = 19.0 - 3.0
    back_t = tip_t - 1.0 - pull * 8.0
    for side in (-1, 1):
        x0 = base[0] + u[0] * tip_t + n[0] * side * 9.2
        y0 = base[1] + u[1] * tip_t + n[1] * side * 9.2
        x1 = base[0] + u[0] * back_t
        y1 = base[1] + u[1] * back_t
        steps = 40
        for k in range(steps + 1):
            f = k / steps
            put(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, STRING)
    # proyectil cargado
    if state in ("arrow", "firework"):
        for k in range(16):
            t = back_t + k * 1.0
            x = base[0] + u[0] * t
            y = base[1] + u[1] * t - 0.0
            put(x, y, SHAFT if k < 12 else HEAD)
        tx = base[0] + u[0] * (back_t + 16)
        ty = base[1] + u[1] * (back_t + 16)
        if state == "firework":
            for (ox, oy, cc) in [(0, 0, RUBY), (1, 0, GOLD_L), (0, -1, GOLD_L), (1, -1, RUBY_L), (-1, 1, (90, 200, 255))]:
                put(tx + ox, ty + oy, cc)
        else:
            put(tx, ty, HEAD); put(tx + 1, ty - 1, STEEL_L)
        # plumas
        bx = base[0] + u[0] * back_t
        by = base[1] + u[1] * back_t
        put(bx - 1, by, FL); put(bx, by + 1, RUBY)
    return outline(im)


CROSSBOW_STATES = ["standby", "pulling_0", "pulling_1", "pulling_2", "arrow", "firework"]


def write(item_dir):
    longsword().save(os.path.join(item_dir, "ruby_longsword.png"))
    for st in CROSSBOW_STATES:
        crossbow(st).save(os.path.join(item_dir, "ruby_crossbow_%s.png" % st))
