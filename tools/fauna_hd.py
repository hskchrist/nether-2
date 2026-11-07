"""Manta Carmesí y Tortuga Obsidiana con las texturas del usuario (tools/ref/fauna/texturas_manta_tortuga.png).

La lámina del usuario viene escalada (cada píxel del arte son ~6 píxeles); se reduce a su grilla real (284 x 142)
y cada pieza se reparte en un atlas nuevo. La forma del modelo sale de la silueta de cada pieza: el lomo de la manta
y el caparazón de la tortuga se arman con columnas de cubos que siguen el borde del dibujo, y cada cara toma
exactamente el trozo de arte que le corresponde (UV por cara). Así el modelo queda igual al dibujo, sin estirar nada.
"""
import math
import os

import numpy as np
from PIL import Image

from models import Geo

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "ref", "fauna", "texturas_manta_tortuga.png")
NW, NH = 284, 142                      # grilla real del arte


def native_sheet(path=SHEET):
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(float)
    H, W = a.shape[:2]
    sx, sy = W / NW, H / NH
    out = np.zeros((NH, NW, 4), dtype=np.uint8)
    for j in range(NH):
        for i in range(NW):
            x0 = int(i * sx + sx * 0.3)
            x1 = max(x0 + 1, int((i + 1) * sx - sx * 0.3))
            y0 = int(j * sy + sy * 0.3)
            y1 = max(y0 + 1, int((j + 1) * sy - sy * 0.3))
            c = np.median(a[y0:y1, x0:x1].reshape(-1, 3), axis=0)
            out[j, i, :3] = c
            out[j, i, 3] = 255 if c.max() > 10 else 0
    return out


def piece(sheet, box, largest=True):
    """Recorta una pieza del dibujo; con largest=True deja solo la mancha más grande (sin vecinas que se cuelen)."""
    x0, y0, x1, y1 = box
    p = sheet[y0:y1, x0:x1].copy()
    if largest:
        from scipy import ndimage
        m = p[..., 3] > 0
        lab, n = ndimage.label(m)
        if n > 1:
            sizes = ndimage.sum(m, lab, range(1, n + 1))
            keep = lab == 1 + int(np.argmax(sizes))
            keep = ndimage.binary_fill_holes(keep)
            p[..., 3] = np.where(keep, p[..., 3], 0)
            p[~keep] = 0
    return p


def fill_from(target_mask, src):
    """Copia src (estirado al tamaño de la máscara) y rellena los huecos con el píxel opaco más cercano."""
    h, w = target_mask.shape
    im = Image.fromarray(src).resize((w, h), Image.NEAREST)
    a = np.array(im)
    from scipy import ndimage
    opaque = a[..., 3] > 0
    if not opaque.all():
        idx = ndimage.distance_transform_edt(~opaque, return_distances=False, return_indices=True)
        a = a[idx[0], idx[1]]
    a[..., 3] = np.where(target_mask, 255, 0)
    return a


class HDAtlas:
    def __init__(self, w, h):
        self.img = np.zeros((h, w, 4), dtype=np.uint8)
        self.w, self.h = w, h
        self.x = self.y = self.row = 0

    def put(self, arr, pad=1):
        h, w = arr.shape[:2]
        if self.x + w > self.w:
            self.x, self.y, self.row = 0, self.y + self.row + pad, 0
        assert self.y + h <= self.h, "atlas lleno"
        self.img[self.y:self.y + h, self.x:self.x + w] = arr
        pos = (self.x, self.y)
        self.x += w + pad
        self.row = max(self.row, h)
        return pos

    def image(self):
        return Image.fromarray(self.img, "RGBA")


def add_cube(g, bone, origin, size, faces, rotation=None, pivot=None):
    c = {"origin": [round(v, 4) for v in origin], "size": [round(v, 4) for v in size],
         "uv": {k: {"uv": [round(a, 4) for a in v[0]], "uv_size": [round(a, 4) for a in v[1]]} for k, v in faces.items()}}
    if rotation:
        c["rotation"] = list(rotation)
        c["pivot"] = list(pivot)
    g.bones[bone]["cubes"].append(c)


class Plate:
    """Una pieza del arte vista desde arriba, convertida en columnas de cubos.

    up / down: posiciones en el atlas del arte de arriba (ya volteado) y de abajo, del mismo tamaño;
    side: posición del arte transpuesto (para los costados); s: píxeles de arte por unidad de modelo.
    El borde de arriba del dibujo es el frente (-Z) del modelo."""

    def __init__(self, mask, up, down, side, s, x_left, z_front):
        self.mask, self.up, self.down, self.side, self.s = mask, up, down, side, s
        self.h, self.w = mask.shape
        self.x_left, self.z_front = x_left, z_front

    def columns(self, step=1):
        """Devuelve (ix0, ix1, iz0, iz1) en unidades de modelo: corridas opacas por columna."""
        s = self.s
        nx = int(math.ceil(self.w / s))
        nz = int(math.ceil(self.h / s))
        grid = np.zeros((nz, nx), bool)
        for iz in range(nz):
            for ix in range(nx):
                blk = self.mask[int(iz * s):int(min(self.h, (iz + 1) * s)), int(ix * s):int(min(self.w, (ix + 1) * s))]
                grid[iz, ix] = blk.size > 0 and blk.mean() >= 0.5
        runs = []
        for ix in range(nx):
            iz = 0
            while iz < nz:
                if grid[iz, ix]:
                    a = iz
                    while iz < nz and grid[iz, ix]:
                        iz += 1
                    runs.append((ix, a, iz))
                else:
                    iz += 1
        return runs, grid

    def faces(self, ix, iz0, iz1, front=None, back=None):
        s = self.s
        u0, u1 = ix * s, min(self.w, (ix + 1) * s)
        v0, v1 = iz0 * s, min(self.h, iz1 * s)
        du = u1 - u0
        UX, UY = self.up
        DX, DY = self.down
        SX, SY = self.side
        f = {}
        # arriba: el arte de arriba está volteado (fila 0 = cola), así el dibujo queda derecho
        f["up"] = ([UX + u0, UY + (self.h - v1)], [du, v1 - v0])
        f["down"] = ([DX + u0, DY + v0], [du, v1 - v0])
        # costados: el arte transpuesto (u = largo, v = ancho)
        f["east"] = ([SX + v0, SY + u0], [v1 - v0, min(s, du)])
        f["west"] = ([SX + v0, SY + u0], [v1 - v0, min(s, du)])
        f["north"] = front or ([UX + u0, UY + (self.h - v0) - min(s, v1 - v0)], [du, min(s, v1 - v0)])
        f["south"] = back or ([UX + u0, UY + (self.h - v1)], [du, min(s, v1 - v0)])
        return f


def transpose(arr):
    return np.ascontiguousarray(np.transpose(arr, (1, 0, 2)))


# ====================================================================== Manta Carmesí
def manta(sheet):
    at = HDAtlas(512, 256)
    dorsal = piece(sheet, (3, 3, 140, 76))
    mask = dorsal[..., 3] > 0
    belly = fill_from(mask, piece(sheet, (22, 102, 121, 139)))
    up = at.put(dorsal[::-1].copy())
    down = at.put(belly)
    side = at.put(transpose(dorsal))
    headp = piece(sheet, (3, 77, 69, 101))
    head_pos = at.put(headp)
    tail = piece(sheet, (125, 55, 142, 106))
    tmask = tail[..., 3] > 0
    t_up = at.put(tail[::-1].copy())
    t_down = at.put(tail)
    t_side = at.put(transpose(tail))
    lobe = piece(sheet, (3, 58, 25, 74))
    s = 2.4
    g = Geo("geometry.manta_carmesi", at.w, at.h)
    W_units = dorsal.shape[1] / s
    x_left = -W_units / 2
    z_front = -14.0
    pl = Plate(mask, up, down, side, s, x_left, z_front)
    runs, grid = pl.columns()
    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 5, 0], "root")
    edges = [7, 14, 21]
    for side_name, sx in (("left", 1), ("right", -1)):
        parent = "body"
        for k, e in enumerate(edges, 1):
            n = "wing%d_%s" % (k, side_name)
            g.bone(n, [sx * e, 5, -2], parent)
            parent = n
    nx = grid.shape[1]
    hx0, hx1 = headp.shape[1] * 18 / 66, headp.shape[1] * 48 / 66     # el centro de la cabeza (con los ojos)
    for (ix, iz0, iz1) in runs:
        xc = x_left + ix + 0.5
        ax = abs(xc)
        t = max(0.6, 3.6 - ax * 0.13) if ax > 5 else 3.6 + (1.0 if ax < 3 else 0.4)
        y0 = 5 - t * 0.45
        bone = "body"
        for k, e in enumerate(edges, 1):
            if ax > e:
                bone = "wing%d_%s" % (k, "left" if xc > 0 else "right")
        front = None
        # cara frontal del centro: la cara de la manta con los ojos
        if ax < 6.5 and iz0 == min(r[1] for r in runs if r[0] == ix):
            u = head_pos[0] + hx0 + (xc + 6.5) / 13 * (hx1 - hx0) - 0.5
            front = ([u, head_pos[1] + 6], [(hx1 - hx0) / 13, 18])
        f = pl.faces(ix, iz0, iz1, front=front)
        add_cube(g, bone, [xc - 0.5, y0, z_front + iz0], [1, t, iz1 - iz0], f)
    # cola (vista desde arriba en el dibujo; la horquilla es la punta)
    z_tail = z_front + grid.shape[0] - 3
    g.bone("tail", [0, 5, z_tail], "body")
    g.bone("tail_tip", [0, 5, z_tail + 12], "tail")
    st = 2.2
    tp = Plate(tmask, t_up, t_down, t_side, st, -tail.shape[1] / st / 2, z_tail)
    truns, tgrid = tp.columns()
    for (ix, iz0, iz1) in truns:
        xc = tp.x_left + ix + 0.5
        for a, b in ((iz0, min(iz1, 12)), (max(iz0, 12), iz1)):
            if b <= a:
                continue
            add_cube(g, "tail" if a < 12 else "tail_tip", [xc - 0.5, 4.6, z_tail + a], [1, 0.8, b - a], tp.faces(ix, a, b))
    g.bone("saddle_spot", [0, 9, -2], "body")
    from fauna import wave, anim
    swim, glide = {}, {}
    for side_name, sx in (("left", 1), ("right", -1)):
        for k in range(1, 4):
            swim["wing%d_%s" % (k, side_name)] = {"rotation": wave(sx * (14 + 5 * k), 1.6, steps=8, axis=2, phase=-0.55 * (k - 1))}
            glide["wing%d_%s" % (k, side_name)] = {"rotation": wave(sx * (3 + 2 * k), 3.0, steps=6, axis=2, phase=-0.45 * (k - 1))}
    swim["tail"] = {"rotation": wave(6, 1.6, steps=8, axis=0, phase=-1.5)}
    swim["tail_tip"] = {"rotation": wave(10, 1.6, steps=8, axis=1, phase=-2.3)}
    swim["body"] = {"position": wave(0.8, 1.6, steps=8, axis=1, phase=1.6)}
    glide["tail"] = {"rotation": wave(4, 3.0, steps=6, axis=1)}
    glide["tail_tip"] = {"rotation": wave(6, 3.0, steps=6, axis=1, phase=-1)}
    anims = {"animation.manta_carmesi.swim": anim(swim, 1.6), "animation.manta_carmesi.glide": anim(glide, 3.0)}
    tex = at.image()
    glow = glow_mask(tex, lambda r, gg, b: r > 235 and gg > 150 and b > 140)   # el borde claro brilla apenas
    return g, tex, glow, anims


# ====================================================================== Tortuga Obsidiana
def tortuga(sheet):
    at = HDAtlas(512, 256)
    shell = piece(sheet, (166, 3, 238, 73))
    # la pieza del caparazón viene pegada a las aletas en el dibujo: se separa por la silueta central
    from scipy import ndimage
    m = shell[..., 3] > 0
    lab, n = ndimage.label(m)
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    keep = 1 + int(np.argmax(sizes))
    m = lab == keep
    m = ndimage.binary_fill_holes(m)
    shell[..., 3] = np.where(m, 255, 0)
    plast = fill_from(m, piece(sheet, (172, 103, 232, 139)))
    rim = piece(sheet, (262, 3, 281, 90))
    rim_h = transpose(rim)                         # la franja del borde, acostada
    up = at.put(shell[::-1].copy())
    down = at.put(plast)
    side_pos = at.put(transpose(shell))
    rim_pos = at.put(rim_h)
    headp = piece(sheet, (185, 77, 219, 102))
    head_pos = at.put(headp)
    neck = piece(sheet, (179, 81, 182, 95))
    neck_pos = at.put(neck)
    disc = piece(sheet, (262, 92, 281, 111))
    disc_pos = at.put(disc)
    fl_top = piece(sheet, (145, 14, 170, 38))
    fl_bot = piece(sheet, (148, 75, 177, 105))
    bl_top = piece(sheet, (146, 41, 168, 73))
    bl_bot = piece(sheet, (144, 108, 170, 139))
    s = 2.5
    g = Geo("geometry.tortuga_obsidiana", at.w, at.h)
    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 5, 0], "root")
    Wu, Hu = shell.shape[1] / s, shell.shape[0] / s
    x_left, z_front = -Wu / 2, -Hu / 2
    # cúpula: 4 capas, cada una más chica (la silueta erosionada) y más alta
    layers = [(0, 3.0, 2.0), (2, 5.0, 2.0), (5, 7.0, 1.5), (9, 8.5, 1.2)]
    for k, (ero, y0, th) in enumerate(layers):
        mk = ndimage.binary_erosion(m, iterations=ero) if ero else m
        if mk.sum() == 0:
            continue
        pl = Plate(mk, up, down, side_pos, s, x_left, z_front)
        runs, grid = pl.columns()
        for (ix, iz0, iz1) in runs:
            f = pl.faces(ix, iz0, iz1)
            if k == 0:
                # el borde del caparazón usa la franja del dibujo
                L = iz1 - iz0
                f["east"] = ([rim_pos[0] + (ix * 7) % max(1, rim_h.shape[1] - 30), rim_pos[1]], [min(30, rim_h.shape[1]), rim_h.shape[0]])
                f["west"] = f["east"]
                f["north"] = ([rim_pos[0] + (ix * 5) % 60, rim_pos[1]], [s * 2, rim_h.shape[0]])
                f["south"] = f["north"]
            else:
                f["down"] = f["up"]
            add_cube(g, "body", [x_left + ix, y0, z_front + iz0], [1, th, iz1 - iz0], f)
    # vientre (un poco más chico que el borde)
    # cabeza: la cara del dibujo al frente; arriba y a los lados, el disco oscuro
    g.bone("head", [0, 5, z_front + 1], "body")
    hw, hh, hd = 7.0, 5.0, 6.0
    hz = z_front - hd + 1
    add_cube(g, "head", [-2, 3.5, z_front - 2], [4, 3, 3],
             {"north": ([neck_pos[0], neck_pos[1]], [3, 14]), "south": ([neck_pos[0], neck_pos[1]], [3, 14]),
              "east": ([neck_pos[0], neck_pos[1]], [3, 14]), "west": ([neck_pos[0], neck_pos[1]], [3, 14]),
              "up": ([neck_pos[0], neck_pos[1]], [3, 14]), "down": ([neck_pos[0], neck_pos[1]], [3, 14])})
    dsk = ([disc_pos[0] + 2, disc_pos[1] + 2], [15, 15])
    add_cube(g, "head", [-hw / 2, 2.5, hz - 2], [hw, hh, hd],
             {"north": ([head_pos[0], head_pos[1]], [headp.shape[1], headp.shape[0]]), "south": dsk, "east": dsk, "west": dsk,
              "up": ([head_pos[0] + 4, head_pos[1]], [headp.shape[1] - 8, 8]), "down": dsk})
    # aletas: placas que siguen la silueta del dibujo (arriba y abajo con su propio arte)
    def flipper(top, bot, bone, pivot, x_out, z0, s2, mirror):
        tm = top[..., 3] > 0
        bt = fill_from(tm, bot)
        tp = top[:, ::-1].copy() if mirror else top
        bt = bt[:, ::-1].copy() if mirror else bt
        tmm = tp[..., 3] > 0
        u = at.put(tp[::-1].copy())
        d = at.put(bt)
        sd = at.put(transpose(tp))
        g.bone(bone, pivot, "body")
        pl = Plate(tmm, u, d, sd, s2, 0, z0)
        runs, grid = pl.columns()
        nx = grid.shape[1]
        for (ix, iz0, iz1) in runs:
            # la aleta sale hacia afuera desde el caparazón
            x = (pivot[0] + (nx - 1 - ix)) if not mirror else (pivot[0] - ix - 1)
            add_cube(g, bone, [x if not mirror else x, 3.6, z0 + iz0], [1, 1.0, iz1 - iz0], pl.faces(ix, iz0, iz1))
    # en el dibujo las aletas izquierdas apuntan a la izquierda: se espejan para el otro lado
    fx = Wu / 2 - 2
    flipper(fl_top, fl_bot, "front_right", [-fx, 4, z_front + 5], 0, z_front + 3, 2.3, True)
    flipper(fl_top, fl_bot, "front_left", [fx, 4, z_front + 5], 0, z_front + 3, 2.3, False)
    flipper(bl_top, bl_bot, "back_right", [-fx + 1, 4, Hu / 2 - 8], 0, Hu / 2 - 9, 2.6, True)
    flipper(bl_top, bl_bot, "back_left", [fx - 1, 4, Hu / 2 - 8], 0, Hu / 2 - 9, 2.6, False)
    g.bone("tail", [0, 4, Hu / 2 - 1], "body")
    add_cube(g, "tail", [-1, 3.2, Hu / 2 - 1], [2, 1.6, 3], {k: dsk for k in ("north", "south", "east", "west", "up", "down")})
    from fauna import wave, anim
    swim = {"body": {"position": wave(0.6, 2.0, steps=8, axis=1)}, "head": {"rotation": wave(4, 2.0, steps=8, axis=0, phase=1)}}
    walk = {"body": {"rotation": wave(3, 1.2, steps=8, axis=2)}, "head": {"rotation": wave(6, 1.2, steps=8, axis=1)}}
    for side_name, sx in (("left", 1), ("right", -1)):
        swim["front_" + side_name] = {"rotation": wave(sx * 30, 2.0, steps=8, axis=2)}
        swim["back_" + side_name] = {"rotation": wave(sx * 18, 2.0, steps=8, axis=2, phase=-1.0)}
        walk["front_" + side_name] = {"rotation": wave(28, 1.2, steps=8, axis=1, phase=0 if sx > 0 else math.pi)}
        walk["back_" + side_name] = {"rotation": wave(22, 1.2, steps=8, axis=1, phase=math.pi if sx > 0 else 0)}
    hide = {"head": {"position": {"0.00": [0, 0, 0], "0.40": [0, -1, 4], "2.00": [0, -1, 4], "2.40": [0, 0, 0]}}}
    anims = {"animation.tortuga_obsidiana.swim": anim(swim, 2.0), "animation.tortuga_obsidiana.walk": anim(walk, 1.2),
             "animation.tortuga_obsidiana.hide": anim(hide, 2.4, loop=False)}
    tex = at.image()
    glow = glow_mask(tex, lambda r, gg, b: b > 170 and r > 110 and gg < 120)    # las vetas moradas brillan
    return g, tex, glow, anims


def glow_mask(img, test):
    a = np.array(img)
    out = np.zeros_like(a)
    sel = (a[..., 3] > 0) & np.vectorize(lambda r, g, b: bool(test(int(r), int(g), int(b))))(a[..., 0], a[..., 1], a[..., 2])
    out[sel] = a[sel]
    return Image.fromarray(out, "RGBA")
