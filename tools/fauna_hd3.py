"""Pez Brasa, Pez Alma, Anguila de Rubí, Medusa del Vacío, Cangrejo de Basalto y Caballito de Magma en HD,
armados desde la lámina del usuario (tools/ref/fauna/texturas_peces_medusa_cangrejo_caballito.png).

Igual que el tiburón y la serpiente: la vista de lado de cada dibujo da la silueta exacta y cada cara de cada cubo
toma su trozo de arte por proyección (los costados de la vista de lado, el lomo de su borde de arriba). El cangrejo
está dibujado desde arriba, así que se proyecta desde arriba; la medusa es redonda: su campana se arma por anillos
con la vista de arriba en la tapa y sus tentáculos son láminas cruzadas.
"""
import math
import os

import numpy as np
from PIL import Image
from scipy import ndimage

from models import Geo
from fauna_hd import HDAtlas, add_cube as _add_cube


def add_cube(g, bone, origin, size, faces, rotation=None, pivot=None):
    faces = {k: ([float(a) for a in v[0]], [float(a) for a in v[1]]) for k, v in faces.items()}
    _add_cube(g, bone, [float(v) for v in origin], [float(v) for v in size], faces,
              [float(v) for v in rotation] if rotation else None, [float(v) for v in pivot] if pivot else None)
from fauna_hd2 import ViewModel, solid_fill, flipx, flipy, T, resize, glow_of
from fauna import wave, anim

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "ref", "fauna", "texturas_peces_medusa_cangrejo_caballito.png")
CELL = 6          # píxeles de la lámina por texel (el arte tiene "píxeles" de ~12-13: cada uno queda en 2 texels)


def native(path=SHEET, cell=CELL):
    a = np.array(Image.open(path).convert("RGB")).astype(float)
    H, W = a.shape[:2]
    nw, nh = W // cell, H // cell
    out = np.zeros((nh, nw, 4), np.uint8)
    for j in range(nh):
        for i in range(nw):
            blk = a[j * cell + 1:(j + 1) * cell - 1, i * cell + 1:(i + 1) * cell - 1].reshape(-1, 3)
            c = np.median(blk, axis=0)
            out[j, i, :3] = c
            out[j, i, 3] = 255 if c.max() > 34 else 0
    return out


def cut(sheet, box, largest=True, fill=True, keep_small=0.0):
    """Recorta una pieza (caja en píxeles de la lámina) y se queda con la mancha más grande."""
    x0, y0, x1, y1 = [int(round(v / CELL)) for v in box]
    p = sheet[y0:y1, x0:x1].copy()
    m = p[..., 3] > 0
    if fill:
        m = ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=1) | m)
    if largest:
        lab, n = ndimage.label(m)
        if n > 1:
            sizes = ndimage.sum(m, lab, range(1, n + 1))
            big = np.argmax(sizes)
            keep = lab == big + 1
            for k in range(n):
                if k != big and sizes[k] >= keep_small * sizes[big] and keep_small > 0:
                    keep |= lab == k + 1
            m = keep
    p[..., 3] = np.where(m, 255, 0)
    p[~m, :3] = 0
    ys, xs = np.nonzero(m)
    return p[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def edge_strips(side, vm, rows=24):
    """Mapas del lomo y del vientre: los colores del borde de arriba y de abajo de la vista de lado, por columna."""
    L = side.shape[1]
    full = solid_fill(side)
    dors = np.zeros((rows, L, 4), np.uint8)
    bel = np.zeros((rows, L, 4), np.uint8)
    m = side[..., 3] > 0
    for x in range(L):
        ys = np.nonzero(m[:, x])[0]
        if len(ys) == 0:
            ys = np.array([0, full.shape[0] - 1])
        t, b = ys.min(), ys.max()
        col = full[t:b + 1, x]
        lum = col[:, :3].astype(int).sum(1)
        bright = col[lum > 150]
        if len(bright) == 0:
            bright = col
        colt = bright[:min(len(bright), 4)]          # sin el contorno oscuro (si no, el lomo sale lleno de pintas negras)
        colb = bright[max(0, len(bright) - 4):]
        for r in range(rows):
            dors[r, x] = colt[(r * 3 + x) % len(colt)]
            bel[r, x] = colb[(r * 5 + x) % len(colb)]
    return flipy(T(dors)), T(bel)


class BoneVM(ViewModel):
    """ViewModel con huesos por celda (columna y fila): sirve para criaturas paradas como el caballito."""

    def build2(self, bone_of, y_base=0.0, z_front=0.0, dorsal=None, belly=None):
        used = set()
        k, vu = self.k, self.vu
        for (iy, iz) in sorted(self.cells, key=lambda c: (c[1], c[0])):
            if (iy, iz) in used:
                continue
            hw, kind = self.cells[(iy, iz)]
            bone = bone_of(iz, iy)
            y1 = iy
            while ((y1 + 1, iz) in self.cells and (y1 + 1, iz) not in used and self.cells[(y1 + 1, iz)] == (hw, kind)
                   and bone_of(iz, y1 + 1) == bone):
                y1 += 1
            z1 = iz
            while all((yy, z1 + 1) in self.cells and (yy, z1 + 1) not in used and self.cells[(yy, z1 + 1)] == (hw, kind)
                      and bone_of(z1 + 1, yy) == bone for yy in range(iy, y1 + 1)):
                z1 += 1
            for zz in range(iz, z1 + 1):
                for yy in range(iy, y1 + 1):
                    used.add((yy, zz))
            u0, u1 = iz * k, min(self.W, (z1 + 1) * k)
            v0, v1 = iy * k, min(self.H, (y1 + 1) * k)
            f = {"west": ([self.SW[0] + u0, self.SW[1] + v0], [u1 - u0, v1 - v0]),
                 "east": ([self.SE[0] + (self.W - u1), self.SE[1] + v0], [u1 - u0, v1 - v0])}
            (dx, dy), dw, kd, L = dorsal
            f["up"] = ([dx + dw / 2 - hw * kd, dy + (L - u1)], [2 * hw * kd, u1 - u0])
            (bx, by), bw, kb, _ = belly
            f["down"] = ([bx + bw / 2 - hw * kb, by + u0], [2 * hw * kb, u1 - u0])
            f["north"] = ([self.SW[0] + u0, self.SW[1] + v0], [min(k, u1 - u0), v1 - v0])
            f["south"] = ([self.SW[0] + u1 - min(k, u1 - u0), self.SW[1] + v0], [min(k, u1 - u0), v1 - v0])
            ytop = y_base + (self.ny - iy) * vu
            ybot = y_base + (self.ny - 1 - y1) * vu
            add_cube(self.g, bone, [-hw, ybot, z_front + iz * vu], [2 * hw, ytop - ybot, (z1 + 1 - iz) * vu], f)


def remask(vm, thr):
    """Celdas opacas con menos cobertura (así la cola fina no se corta del cuerpo)."""
    m = vm.side[..., 3] > 0
    k = vm.k
    for iy in range(vm.ny):
        for iz in range(vm.nz):
            blk = m[int(iy * k):int(min(vm.H, (iy + 1) * k)), int(iz * k):int(min(vm.W, (iz + 1) * k))]
            vm.mask[iy, iz] = blk.size > 0 and blk.mean() >= thr


def side_creature(ident, side, s, width_frac, bones, fin_hw=0.25, atlas=(256, 256), win=5, z_end=1.0, vu=1.0):
    """Pez o anguila de perfil. bones = [(nombre, desde fracción del largo, padre)]."""
    vm = ViewModel(ident, side, s, vu=vu, atlas=atlas)
    remask(vm, 0.32)
    vm.body_bounds(win=win, z_end=int(round(vm.nz * z_end)))

    def width(iz):
        h = (vm.bot_b[iz] - vm.top_b[iz] + 1) * vu
        return max(0.8, h * width_frac(iz / max(1, vm.nz - 1)))

    vm.fill(width, fin_hw=fin_hw, q=0.25)
    dmap, bmap = edge_strips(side, vm)
    dpos, bpos = vm.at.put(dmap), vm.at.put(bmap)
    g = vm.g
    g.bone("root", [0, 0, 0])
    z_front = -vm.nz * vu / 2
    starts = []
    for name, frac, parent in bones:
        iz = int(round(frac * vm.nz))
        izc = min(vm.nz - 1, iz)
        yc = (vm.ny - (vm.top_b[izc] + vm.bot_b[izc] + 1) / 2) * vu
        g.bone(name, [0, round(yc, 2), round(z_front + iz * vu, 2)], parent)
        starts.append((iz, name))

    def bone_of(iz):
        cur = starts[0][1]
        for st, nm in starts:
            if iz >= st:
                cur = nm
        return cur

    kd = 24 / max(width(i) for i in range(vm.nz))
    vm.build(bone_of, y_base=0, z_front=z_front, dorsal=(dpos, 24, kd, side.shape[1]), belly=(bpos, 24, kd, side.shape[1]))
    return vm


def fit_atlas(vm, w, h):
    """Recorta el atlas al tamaño usado (potencia de 2) y lo deja en el geo."""
    img = vm.at.image()
    a = np.array(img)
    ys, xs = np.nonzero(a[..., 3])
    tw = 1 << int(math.ceil(math.log2(max(16, xs.max() + 2))))
    th = 1 << int(math.ceil(math.log2(max(16, ys.max() + 2))))
    vm.g.tw, vm.g.th = tw, th
    return img.crop((0, 0, tw, th))


# ====================================================================== peces
def pez_brasa(sheet):
    side = cut(sheet, (17, 58, 478, 290))
    vm = side_creature("geometry.pez_brasa", side, 6.0, lambda t: 0.55 - 0.25 * max(0, t - 0.5), 
                       [("body", 0.0, "root"), ("tail", 0.70, "body")], z_end=0.78)
    tex = fit_atlas(vm, 256, 256)
    swim = {"body": {"rotation": wave(5, 0.8, steps=8)}, "tail": {"rotation": wave(24, 0.8, steps=8, phase=-1.2)}}
    hw = 2.5
    flop = {"root": {"rotation": wave(14, 0.4, steps=4, axis=0, extra=[0, 0, 90]), "position": {"0.0": [0, hw, 0]}},
            "tail": {"rotation": wave(30, 0.4, steps=4, phase=-1.0)}}
    anims = {"animation.pez_brasa.swim": anim(swim, 0.8), "animation.pez_brasa.flop": anim(flop, 0.4)}
    return vm.g, tex, glow_of(tex, lambda r, g, b: r > 230 and g > 140), anims


def pez_alma(sheet):
    side = cut(sheet, (524, 60, 950, 296))
    vm = side_creature("geometry.pez_alma", side, 5.5, lambda t: 0.5 - 0.25 * max(0, t - 0.5),
                       [("body", 0.0, "root"), ("tail", 0.68, "body")], z_end=0.74)
    tex = fit_atlas(vm, 256, 256)
    swim = {"body": {"rotation": wave(5, 1.2, steps=8)}, "tail": {"rotation": wave(22, 1.2, steps=8, phase=-1.2)},
            "root": {"position": wave(0.6, 1.2, steps=8, axis=1)}}
    flop = {"root": {"rotation": wave(14, 0.5, steps=4, axis=0, extra=[0, 0, 90]), "position": {"0.0": [0, 2.5, 0]}},
            "tail": {"rotation": wave(30, 0.5, steps=4, phase=-1.0)}}
    anims = {"animation.pez_alma.swim": anim(swim, 1.2), "animation.pez_alma.flop": anim(flop, 0.5)}
    return vm.g, tex, glow_of(tex, lambda r, g, b: b > 200 and g > 170), anims


def anguila_rubi(sheet):
    a = cut(sheet, (1002, 78, 1518, 206))
    c = cut(sheet, (1002, 342, 1404, 467))
    # la cabeza y el cuerpo (con el ojo) + el tramo final que se angosta, a la misma altura
    c = resize(c, c.shape[1] * a.shape[0] / c.shape[0], a.shape[0])
    side = np.concatenate([a[:, :-2], c], axis=1)
    segs = [("head", 0.0, "root"), ("seg1", 0.18, "head"), ("seg2", 0.34, "seg1"), ("seg3", 0.50, "seg2"),
            ("seg4", 0.66, "seg3"), ("tail", 0.82, "seg4")]
    vm = side_creature("geometry.anguila_rubi", side, 5.0, lambda t: 0.75, segs, win=3)
    tex = fit_atlas(vm, 512, 256)
    swim, flop = {}, {}
    for k, (n, _, _) in enumerate(segs):
        swim[n] = {"rotation": wave(8 + k * 2.5, 1.6, steps=8, phase=-k * 0.9)}
        flop[n] = {"rotation": wave(16 + k * 4, 0.6, steps=4, phase=-k * 1.2)}
    flop["root"] = {"rotation": {"0.0": [0, 0, 90]}, "position": {"0.0": [0, 2, 0]}}
    anims = {"animation.anguila_rubi.swim": anim(swim, 1.6), "animation.anguila_rubi.flop": anim(flop, 0.6)}
    return vm.g, tex, glow_of(tex, lambda r, g, b: r > 220 and g < 80 and b < 90), anims


# ====================================================================== caballito
def caballito_magma(sheet):
    side = cut(sheet, (1147, 578, 1393, 997))
    s = 3.6
    vm = BoneVM("geometry.caballito_magma", side, s, vu=1.0, atlas=(256, 256))
    vm.body_bounds(win=3)
    ny, nz = vm.ny, vm.nz
    m = vm.mask

    # el ancho sale del alto de la fila (el caballito es angosto): cabeza y panza más anchas, cola fina
    def width(iz):
        return 3.2

    vm.fill(width, fin_hw=0.25, q=0.25)
    # todas las celdas opacas son cuerpo; el ancho baja hacia abajo (la cola) y la aleta del lomo es fina
    for (iy, iz), (hw, kind) in list(vm.cells.items()):
        t = iy / max(1, ny - 1)
        row = np.nonzero(m[iy])[0]
        run = len(row)
        hw2 = 1.6 if t < 0.55 else max(0.5, 1.6 - (t - 0.55) * 3.0)
        if run <= 2:
            hw2 = min(hw2, 0.6)
        vm.cells[(iy, iz)] = (round(hw2 / 0.25) * 0.25, "body")
    # la aleta del lomo: celdas de la derecha del cuerpo en la mitad de arriba
    rows = [np.nonzero(m[iy])[0] for iy in range(ny)]
    for iy in range(ny):
        if len(rows[iy]) and 0.3 < iy / ny < 0.6:
            for iz in rows[iy]:
                if iz >= rows[iy].max() - 2 and (iy, iz) in vm.cells:
                    vm.cells[(iy, iz)] = (0.25, "fin")
    dmap, bmap = edge_strips(side, vm)
    dpos, bpos = vm.at.put(dmap), vm.at.put(bmap)
    g = vm.g
    g.bone("root", [0, 0, 0])
    z_front = -nz / 2
    head_end = int(ny * 0.30)
    tails = [int(ny * f) for f in (0.62, 0.74, 0.84, 0.92)]
    g.bone("body", [0, ny - head_end, 0], "root")
    g.bone("head", [0, ny - head_end, 0], "body")
    g.bone("fin_left", [0, ny * 0.5, z_front + nz * 0.7], "body")
    prev = "body"
    for k, ty in enumerate(tails):
        nm = "tail%d" % (k + 1)
        g.bone(nm, [0, ny - ty, z_front + nz * 0.45], prev)
        prev = nm

    def bone_of(iz, iy):
        if vm.cells.get((iy, iz), (0, ""))[1] == "fin":
            return "fin_left"
        if iy < head_end:
            return "head"
        name = "body"
        for k, ty in enumerate(tails):
            if iy >= ty:
                name = "tail%d" % (k + 1)
        return name

    vm.build2(bone_of, y_base=0, z_front=z_front, dorsal=(dpos, 24, 24 / 3.2, side.shape[1]), belly=(bpos, 24, 24 / 3.2, side.shape[1]))
    tex = fit_atlas(vm, 256, 256)
    swim = {"root": {"position": wave(0.8, 2.4, steps=8, axis=1)},
            "head": {"rotation": wave(4, 2.4, steps=8, axis=0, phase=0.5)},
            "fin_left": {"rotation": wave(25, 0.3, steps=4, axis=1)}}
    for k in range(4):
        swim["tail%d" % (k + 1)] = {"rotation": wave(6 + k * 3, 2.4, steps=8, axis=0, phase=-0.7 * k)}
    happy = {"root": {"rotation": {"0.0": [0, 0, 0], "0.15": [0, 0, 12], "0.3": [0, 0, -12], "0.45": [0, 0, 8], "0.6": [0, 0, 0]},
                      "position": {"0.0": [0, 0, 0], "0.3": [0, 2, 0], "0.6": [0, 0, 0]}}}
    anims = {"animation.caballito_magma.swim": anim(swim, 2.4), "animation.caballito_magma.happy": anim(happy, 0.6, loop=False)}
    return g, tex, glow_of(tex, lambda r, gg, b: r > 235 and gg > 130), anims


# ====================================================================== medusa
def medusa_vacio(sheet):
    side = cut(sheet, (22, 565, 329, 1000), largest=False, fill=False)
    topv = cut(sheet, (333, 667, 504, 806))
    th0, tw0 = topv.shape[:2]
    topv = topv[int(th0 * 0.12):int(th0 * 0.88), int(tw0 * 0.12):int(tw0 * 0.88)]
    s = 4.5
    H, W = side.shape[:2]
    m = side[..., 3] > 0
    widths = np.array([m[r].sum() for r in range(H)])
    spans = []
    for r in range(H):
        xs = np.nonzero(m[r])[0]
        spans.append((xs.min(), xs.max()) if len(xs) else (0, 0))
    wmax = widths.max()
    bell_end = next(r for r in range(int(H * 0.2), H) if widths[r] < 0.62 * wmax)   # aquí empiezan los tentáculos
    g = Geo("geometry.medusa_vacio", 256, 256)
    at = HDAtlas(256, 256)
    bell_img = solid_fill(side[:bell_end])
    bpos = at.put(bell_img)
    tpos = at.put(solid_fill(topv))
    tent = side[bell_end - 2:].copy()                 # los tentáculos conservan su transparencia
    tnt = at.put(tent)
    g.bone("root", [0, 0, 0])
    tent_h = (H - bell_end + 2) / s
    bell_y0 = tent_h - 0.6
    g.bone("bell", [0, round(bell_y0 + bell_end / s * 0.5, 2), 0], "root")
    g.bone("tentacles", [0, round(bell_y0, 2), 0], "bell")
    nrows = int(math.ceil(bell_end / s))
    th, tw = topv.shape[:2]
    for i in range(nrows):
        r0, r1 = int(i * s), min(bell_end, int((i + 1) * s))
        x0 = min(spans[r][0] for r in range(r0, r1))
        x1 = max(spans[r][1] for r in range(r0, r1)) + 1
        hw = (x1 - x0) / 2 / s
        ytop = bell_y0 + (bell_end - r0) / s
        ybot = bell_y0 + (bell_end - r1) / s
        sideuv = ([bpos[0] + x0, bpos[1] + r0], [x1 - x0, r1 - r0])
        f = {"north": sideuv, "south": sideuv, "east": sideuv, "west": sideuv,
             "up": ([tpos[0], tpos[1]], [tw, th]), "down": ([tpos[0], tpos[1]], [tw, th])}
        add_cube(g, "bell", [-hw, ybot, -hw], [2 * hw, ytop - ybot, 2 * hw], f)
    # tentáculos: 4 láminas cruzadas (a 0°, 45°, 90° y 135°) con el dibujo de los tentáculos
    tH, tW = tent.shape[:2]
    hw = tW / 2 / s * 0.86
    uv = ([tnt[0], tnt[1]], [tW, tH])
    empty = ([tnt[0], tnt[1]], [0, 0])
    for ang in (0, 45, 90, 135):
        faces = {"north": uv, "south": uv, "east": empty, "west": empty, "up": empty, "down": empty}
        add_cube(g, "tentacles", [-hw, bell_y0 - tH / s + 2 / s, 0], [2 * hw, tH / s, 0], faces,
                 rotation=[0, ang if ang <= 90 else ang - 180, 0], pivot=[0, 0, 0])
    tex = at.image()
    a = np.array(tex); ys, xs = np.nonzero(a[..., 3])
    tw2 = 1 << int(math.ceil(math.log2(xs.max() + 2))); th2 = 1 << int(math.ceil(math.log2(ys.max() + 2)))
    g.tw, g.th = tw2, th2
    tex = tex.crop((0, 0, tw2, th2))
    swim = {"bell": {"scale": {"0.0": [1, 1, 1], "0.5": [1.1, 0.88, 1.1], "1.0": [0.96, 1.06, 0.96], "2.0": [1, 1, 1]}},
            "root": {"position": {"0.0": [0, 0, 0], "0.6": [0, 1.2, 0], "2.0": [0, 0, 0]}},
            "tentacles": {"rotation": wave(5, 2.0, steps=8, axis=0, extra=[0, 0, 0]),
                          "scale": {"0.0": [1, 1, 1], "0.6": [0.9, 1.08, 0.9], "2.0": [1, 1, 1]}}}
    sting = {"bell": {"scale": {"0.0": [1, 1, 1], "0.15": [1.2, 0.8, 1.2], "0.4": [1, 1, 1]}},
             "tentacles": {"rotation": {"0.0": [0, 0, 0], "0.15": [0, 45, 0], "0.4": [0, 0, 0]}}}
    anims = {"animation.medusa_vacio.swim": anim(swim, 2.0), "animation.medusa_vacio.sting": anim(sting, 0.4, loop=False)}
    return g, tex, glow_of(tex, lambda r, gg, b: b > 200 and (r > 170 or gg > 150)), anims


# ====================================================================== cangrejo (mismo cuerpo de antes, con el arte del usuario)
CRAB = {  # pieza: caja en píxeles de la lámina
    "carapace": (672, 574, 960, 752), "abdomen": (722, 771, 915, 877), "tail": (760, 888, 883, 992),
    "claw_left": (547, 578, 644, 708), "claw_right": (989, 578, 1110, 709),
    "arm_left": (561, 645, 693, 823), "arm_right": (948, 645, 1084, 823),
    "eye_left": (681, 683, 735, 733), "eye_right": (904, 684, 955, 733),
    "leg_left0": (649, 733, 705, 822), "leg_right0": (928, 733, 984, 822),
    "leg_left1": (556, 833, 723, 979), "leg_right1": (917, 834, 1081, 979),
    "leg_left2": (690, 879, 748, 997), "leg_right2": (894, 879, 951, 997),
}
D = 8   # texels por unidad


def cangrejo_basalto(sheet):
    pieces = {k: solid_fill(cut(sheet, b)) for k, b in CRAB.items()}
    g = Geo("geometry.cangrejo_basalto", 512, 256)
    at = HDAtlas(512, 256)
    cache = {}

    def face(key, w, h, box=(0, 0, 1, 1), rot=False, flip=False):
        """Un trozo (box en fracciones) de la pieza, al tamaño de la cara (w x h unidades)."""
        ck = (key, w, h, box, rot, flip)
        if ck in cache:
            return cache[ck]
        a = pieces[key]
        H, W = a.shape[:2]
        x0, y0, x1, y1 = box
        a = a[int(y0 * H):max(int(y0 * H) + 1, int(y1 * H)), int(x0 * W):max(int(x0 * W) + 1, int(x1 * W))]
        if rot:
            a = T(a)
        if flip:
            a = flipy(a)
        a = resize(a, max(1, w * D), max(1, h * D))
        pos = at.put(a)
        cache[ck] = ([pos[0], pos[1]], [a.shape[1], a.shape[0]])
        return cache[ck]

    def cube(bone, origin, size, up, side, front=None, back=None, down=None, rotation=None, pivot=None):
        sx, sy, sz = size
        f = {"up": face(*up(sx, sz)), "down": face(*(down or up)(sx, sz)),
             "north": face(*(front or side)(sx, sy)), "south": face(*(back or side)(sx, sy)),
             "east": face(*side(sz, sy)), "west": face(*side(sz, sy))}
        add_cube(g, bone, origin, size, f, rotation, pivot)

    g.bone("root", [0, 0, 0])
    g.bone("body", [0, 3, 0], "root")
    # caparazón: arriba el dibujo del caparazón, adelante la boca, abajo el abdomen y atrás la cola
    cube("body", [-5, 2, -3.5], [10, 3, 7],
         up=lambda w, h: ("carapace", w, h, (0, 0, 1, 0.82)),
         side=lambda w, h: ("carapace", w, h, (0, 0.55, 1, 0.82)),
         front=lambda w, h: ("carapace", w, h, (0.1, 0.78, 0.9, 1.0)),
         back=lambda w, h: ("tail", w, h, (0, 0, 1, 0.6)),
         down=lambda w, h: ("abdomen", w, h, (0, 0, 1, 1), False, True))
    cube("body", [-3.5, 5, -2.5], [7, 1, 5],
         up=lambda w, h: ("carapace", w, h, (0.15, 0.1, 0.85, 0.7)),
         side=lambda w, h: ("carapace", w, h, (0.15, 0.3, 0.85, 0.5)))
    for sd, sg in (("left", 1), ("right", -1)):
        g.bone("eye_" + sd, [sg * 1.8, 5, -3], "body")
        cube("eye_" + sd, [sg * 1.8 - 0.5, 5, -3.5], [1, 2, 1],
             up=lambda w, h, sd=sd: ("eye_" + sd, w, h, (0.2, 0.0, 0.8, 0.4)),
             side=lambda w, h, sd=sd: ("eye_" + sd, w, h))
        g.bone("arm_" + sd, [sg * 3.5, 3, -3.5], "body", rotation=[0, -sg * 20, 0])
        cube("arm_" + sd, [sg * 3.5 - 1, 2.5, -7], [2, 1.5, 3.5],
             up=lambda w, h, sd=sd: ("arm_" + sd, w, h, (0, 0, 1, 0.5), False, True),
             side=lambda w, h, sd=sd: ("arm_" + sd, w, h, (0, 0.2, 1, 0.5)))
        g.bone("claw_" + sd, [sg * 3.5, 3, -7], "arm_" + sd)
        cube("claw_" + sd, [sg * 3.5 - 1.75, 2, -10.5], [3.5, 2.5, 3.5],
             up=lambda w, h, sd=sd: ("claw_" + sd, w, h, (0, 0, 1, 0.8), False, True),
             side=lambda w, h, sd=sd: ("claw_" + sd, w, h, (0, 0.3, 1, 0.8)),
             front=lambda w, h, sd=sd: ("claw_" + sd, w, h, (0, 0, 1, 0.45)))
        g.bone("pincer_" + sd, [sg * 3.5, 2, -8], "claw_" + sd)
        cube("pincer_" + sd, [sg * 3.5 - 1.25, 1, -10.5], [2.5, 1, 2.5],
             up=lambda w, h, sd=sd: ("claw_" + sd, w, h, (0.1, 0.0, 0.9, 0.5), False, True),
             side=lambda w, h, sd=sd: ("claw_" + sd, w, h, (0.1, 0.5, 0.9, 0.8)))
        for k, z in enumerate((-2.0, 0.0, 2.0)):
            nm = "leg_%s%d" % (sd, k)
            g.bone(nm, [sg * 5, 3, z], "body", rotation=[0, 0, sg * 35])
            x0 = 5 if sg > 0 else -10
            cube(nm, [x0, 2.5, z - 0.6], [5, 1.2, 1.2],
                 up=lambda w, h, nm=nm: (nm, w, h, (0, 0, 1, 1), True),
                 side=lambda w, h, nm=nm: (nm, w, h, (0, 0, 1, 1), True))
    tex = at.image()
    a = np.array(tex); ys, xs = np.nonzero(a[..., 3])
    tw = 1 << int(math.ceil(math.log2(xs.max() + 2))); th = 1 << int(math.ceil(math.log2(ys.max() + 2)))
    g.tw, g.th = tw, th
    tex = tex.crop((0, 0, tw, th))
    walk, idle = {}, {}
    for sd, sg in (("left", 1), ("right", -1)):
        for k in range(3):
            ph = (k + (0 if sd == "left" else 1)) * math.pi / 2
            fr = wave(14, 0.4, steps=4, axis=2, phase=ph)
            walk["leg_%s%d" % (sd, k)] = {"rotation": {t: [0, v[2] * 0.8, v[2]] for t, v in fr.items()}}
        idle["claw_" + sd] = {"rotation": wave(6, 3.0, steps=8, axis=0, phase=0 if sd == "left" else 1.5)}
        idle["pincer_" + sd] = {"rotation": wave(10, 1.5, steps=4, axis=0)}
        idle["eye_" + sd] = {"rotation": wave(8, 3.0, steps=8, axis=0, phase=1.0)}
    idle["body"] = {"position": wave(0.25, 3.0, steps=8, axis=1)}
    walk["body"] = {"position": wave(0.3, 0.2, steps=4, axis=1)}
    pinch = {}
    for sd, sg in (("left", 1), ("right", -1)):
        pinch["arm_" + sd] = {"rotation": {"0.0": [0, 0, 0], "0.15": [0, sg * 25, 0], "0.3": [0, -sg * 10, 0], "0.45": [0, 0, 0]}}
        pinch["pincer_" + sd] = {"rotation": {"0.0": [0, 0, 0], "0.12": [30, 0, 0], "0.25": [0, 0, 0]}}
    anims = {"animation.cangrejo_basalto.idle": anim(idle, 3.0), "animation.cangrejo_basalto.walk": anim(walk, 0.4),
             "animation.cangrejo_basalto.pinch": anim(pinch, 0.45, loop=False)}
    return g, tex, glow_of(tex, lambda r, gg, b: r > 200 and 70 < gg < 170 and b < 80), anims
