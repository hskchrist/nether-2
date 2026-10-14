"""Arco de rubí recurvo 32x32 (normal + 3 estados de tensado), dibujado por geometría y píxel a píxel."""
import math
from PIL import Image

N = 32
A, B = (27.0, 4.0), (4.0, 27.0)            # puntas (arriba-derecha / abajo-izquierda)
M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
L = math.hypot(B[0] - A[0], B[1] - A[1]) / 2
U = ((B[0] - A[0]) / (2 * L), (B[1] - A[1]) / (2 * L))  # dirección de la cuerda
NRM = (-0.7071, -0.7071)                   # hacia afuera del arco (arriba-izquierda)

WOOD = (74, 20, 26); WOOD_L = (128, 44, 46); WOOD_D = (38, 8, 12)
GOLD = (214, 160, 38); GOLD_L = (252, 216, 92); GOLD_D = (150, 100, 20)
LEA = (96, 52, 30); LEA_D = (62, 32, 18)
RUBY = (214, 22, 32); RUBY_L = (255, 110, 116); RUBY_D = (120, 8, 16); WHITE = (255, 255, 255)
STRING = (232, 222, 200); OUT = (24, 6, 8)
SHAFT = (176, 140, 96); SHAFT_D = (130, 98, 62); HEAD = (200, 200, 210); HEAD_D = (120, 120, 132)
FL1 = (236, 236, 232); FL2 = (200, 30, 36)


def d(t):
    a = abs(t)
    v = 8.6 * (1 - t * t)
    if a > 0.78:
        v -= 7.5 * (a - 0.78)  # recurvado en las puntas
    return v


def P(t):
    return (M[0] + U[0] * t * L + NRM[0] * d(t), M[1] + U[1] * t * L + NRM[1] * d(t))


def radius(t):
    a = abs(t)
    if a < 0.17:
        return 1.75
    return 1.45 - 0.75 * (a - 0.17) / 0.83


SAMPLES = [i / 600.0 * 2 - 1 for i in range(601)]
CURVE = [(t, P(t)) for t in SAMPLES]


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    s = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2)) if L2 else 0.0
    return math.hypot(px - (ax + s * dx), py - (ay + s * dy)), s


def make(pull):
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    tipA, tipB = P(-1), P(1)
    S = (M[0] - NRM[0] * (pull - 0.3), M[1] - NRM[1] * (pull - 0.3))  # centro de la cuerda (tirada hacia abajo-derecha)
    kind = {}
    for y in range(N):
        for x in range(N):
            c = (x + 0.5, y + 0.5)
            # --- arco
            best, bt = 1e9, 0
            for t, p in CURVE:
                dd = (c[0] - p[0]) ** 2 + (c[1] - p[1]) ** 2
                if dd < best:
                    best, bt = dd, t
            dist = math.sqrt(best)
            if dist <= radius(bt):
                p = P(bt)
                side = (c[0] - p[0]) * NRM[0] + (c[1] - p[1]) * NRM[1]  # >0 lado exterior
                edge = dist > radius(bt) - 0.75
                a = abs(bt)
                if a > 0.86:
                    col = GOLD_L if side > 0 else (GOLD_D if edge else GOLD)
                elif 0.17 <= a <= 0.23:
                    col = GOLD_L if side > 0 else GOLD
                elif a < 0.17:
                    col = LEA if (x + y) % 3 else LEA_D
                else:
                    col = WOOD_L if (side > 0 and edge) else (WOOD_D if (side < 0 and edge) else WOOD)
                kind[(x, y)] = ("bow", col)
                continue
            # --- cuerda
            if pull == 0:
                ds, _ = seg_dist(c, tipA, tipB)
                if ds <= 0.5:
                    kind[(x, y)] = ("str", STRING)
            else:
                d1, _ = seg_dist(c, tipA, S)
                d2, _ = seg_dist(c, S, tipB)
                if min(d1, d2) <= 0.5:
                    kind[(x, y)] = ("str", STRING)
    # --- gema de rubí en la empuñadura (lado exterior)
    g = (P(0)[0] + NRM[0] * 1.1, P(0)[1] + NRM[1] * 1.1)
    for y in range(N):
        for x in range(N):
            dd = math.hypot(x + 0.5 - g[0], y + 0.5 - g[1])
            if dd <= 1.6:
                lx = (x + 0.5 - g[0]) + (y + 0.5 - g[1])
                kind[(x, y)] = ("bow", RUBY_L if lx < -0.6 else (RUBY_D if lx > 0.9 else RUBY))
    # --- flecha montada (estados de tensado)
    if pull:
        tail = S
        head = (S[0] + NRM[0] * 19, S[1] + NRM[1] * 19)
        for y in range(N):
            for x in range(N):
                c = (x + 0.5, y + 0.5)
                ds, s = seg_dist(c, tail, head)
                along = s * 19
                if along > 16.2 and ds <= 1.35 - (along - 16.2) * 0.45:
                    kind[(x, y)] = ("arr", HEAD if (x + y) % 2 else HEAD_D)
                elif ds <= 0.55:
                    if along < 3.5:
                        kind[(x, y)] = ("arr", FL2 if int(along) % 2 else FL1)
                    else:
                        kind[(x, y)] = ("arr", SHAFT if (x + y) % 3 else SHAFT_D)
                elif along < 3.2 and ds <= 1.45:
                    kind[(x, y)] = ("arr", FL1 if (x + y) % 2 else FL2)
    for (x, y), (_, col) in kind.items():
        im.putpixel((x, y), col + (255,))
    # contorno oscuro (no en la cuerda)
    src = dict(kind)
    for y in range(N):
        for x in range(N):
            if (x, y) in src:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                k = src.get((x + dx, y + dy))
                if k and k[0] != "str":
                    im.putpixel((x, y), OUT + (255,))
                    break
    # brillo
    for (x, y) in [(int(g[0]) - 1, int(g[1]) - 1)]:
        if 0 <= x < N and 0 <= y < N:
            im.putpixel((x, y), WHITE + (255,))
    return im


def write(item_dir):
    import os
    names = [("ruby_bow", 0), ("ruby_bow_pulling_0", 2), ("ruby_bow_pulling_1", 4), ("ruby_bow_pulling_2", 6)]
    out = []
    for n, pull in names:
        im = make(pull)
        im.save(os.path.join(item_dir, n + ".png"))
        out.append(im)
    return out


if __name__ == "__main__":
    import sys
    from PIL import ImageDraw, ImageFont
    ims = [make(p) for p in (0, 2, 4, 6)]
    S = Image.new("RGBA", (4 * 300, 330), (40, 40, 46, 255))
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    d = ImageDraw.Draw(S)
    for i, (im, lab) in enumerate(zip(ims, ["Normal", "Tensando 1", "Tensando 2", "Tensado máximo"])):
        big = im.resize((256, 256), Image.NEAREST)
        S.paste(big, (i * 300 + 22, 20), big)
        sm = im.resize((64, 64), Image.NEAREST)
        w = d.textlength(lab, font=f)
        d.text((i * 300 + 150 - w / 2, 290), lab, fill=(240, 210, 90), font=f)
    S.save(sys.argv[1])
