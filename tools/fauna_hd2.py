"""Tiburón Infernal y Serpiente Marina del Nether, armados desde la lámina del usuario
(tools/ref/fauna/texturas_tiburon_serpiente.png).

Método: la vista de lado del dibujo da la silueta exacta (largo y alto). El ancho sale de la vista de arriba (tiburón)
o de la vista de frente (cabeza de la serpiente). El cuerpo se rellena con cubos de sección ovalada y las aletas y
púas quedan como placas finas. Cada cara de cada cubo toma su trozo de arte por proyección: los costados de la vista de
lado, el lomo de la vista de arriba, el frente de la vista de frente y la cola de la vista de atrás. Nada se estira.
"""
import math
import os

import numpy as np
from PIL import Image
from scipy import ndimage

from models import Geo
from fauna_hd import HDAtlas, add_cube

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "ref", "fauna", "texturas_tiburon_serpiente.png")
NW, NH = 384, 256


def native(path=SHEET):
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(float)
    H, W = a.shape[:2]
    sx, sy = W / NW, H / NH
    out = np.zeros((NH, NW, 4), dtype=np.uint8)
    for j in range(NH):
        for i in range(NW):
            x0 = int(i * sx + sx * 0.25)
            x1 = max(x0 + 1, int((i + 1) * sx - sx * 0.25))
            y0 = int(j * sy + sy * 0.25)
            y1 = max(y0 + 1, int((j + 1) * sy - sy * 0.25))
            c = np.median(a[y0:y1, x0:x1].reshape(-1, 3), axis=0)
            out[j, i, :3] = c
            out[j, i, 3] = 255 if c.max() > 7 else 0
    return out


def crop(sheet, box, largest=True, extra=(), join=True):
    x0, y0, x1, y1 = box
    p = sheet[y0:y1, x0:x1].copy()
    m = p[..., 3] > 0
    # las partes negras del dibujo (el cuerpo del tiburón) no son fondo: se cierran los huecos
    m = ndimage.binary_closing(m, iterations=1) | m
    m = ndimage.binary_fill_holes(m)
    p[..., 3] = np.where(m, 255, 0)
    lab, n = ndimage.label(m)
    if largest and n > 1:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        order = list(np.argsort(sizes)[::-1])
        keep = lab == 1 + order[0]
        for k in order[1:]:
            # piezas sueltas grandes pegadas a la principal (aletas cortadas por el borde del dibujo)
            if (join and sizes[k] >= 0.08 * sizes[order[0]]) or (k + 1) in extra:
                keep |= lab == 1 + k
        keep = ndimage.binary_fill_holes(keep)
        p[~keep] = 0
    return p


def flipx(a):
    return np.ascontiguousarray(a[:, ::-1])


def flipy(a):
    return np.ascontiguousarray(a[::-1])


def T(a):
    return np.ascontiguousarray(np.transpose(a, (1, 0, 2)))


def resize(a, w, h):
    return np.array(Image.fromarray(a, "RGBA").resize((max(1, int(round(w))), max(1, int(round(h)))), Image.NEAREST))


def solid_fill(a):
    """Rellena lo transparente con el color opaco más cercano (para que ninguna cara lea negro)."""
    op = a[..., 3] > 0
    if op.all() or not op.any():
        return a
    idx = ndimage.distance_transform_edt(~op, return_distances=False, return_indices=True)
    b = a[idx[0], idx[1]].copy()
    b[..., 3] = 255
    return b


class ViewModel:
    """Construye el modelo a partir de la vista de lado (y vistas auxiliares)."""

    def __init__(self, ident, side, s, vu=1.0, atlas=(1024, 512)):
        self.g = Geo(ident, *atlas)
        self.at = HDAtlas(*atlas)
        self.side = side
        self.s, self.vu = s, vu                  # texeles por unidad, unidades por celda
        self.k = s * vu                          # texeles por celda
        H, W = side.shape[:2]
        self.nz, self.ny = int(math.ceil(W / self.k)), int(math.ceil(H / self.k))
        full = solid_fill(side)
        self.SW = self.at.put(full)              # costado (u crece hacia la cola)
        self.SE = self.at.put(flipx(full))       # el otro costado (espejado)
        self.W, self.H = W, H
        m = side[..., 3] > 0
        self.mask = np.zeros((self.ny, self.nz), bool)
        for iy in range(self.ny):
            for iz in range(self.nz):
                blk = m[int(iy * self.k):int(min(H, (iy + 1) * self.k)), int(iz * self.k):int(min(W, (iz + 1) * self.k))]
                self.mask[iy, iz] = blk.size > 0 and blk.mean() >= 0.45
        self.cells = {}                          # (iy, iz) -> (hw, kind)

    def body_bounds(self, win=9, z_end=None):
        top = np.full(self.nz, -1.0)
        bot = np.full(self.nz, -1.0)
        for iz in range(self.nz):
            ys = np.nonzero(self.mask[:, iz])[0]
            if len(ys):
                top[iz], bot[iz] = ys.min(), ys.max()
        valid = top >= 0
        t2 = np.where(valid, top, top[valid].max())
        b2 = np.where(valid, bot, bot[valid].min())
        # el lomo y el vientre suaves: las aletas (picos angostos) se quitan
        t2 = ndimage.grey_closing(t2, size=win)
        b2 = ndimage.grey_opening(b2, size=win)
        t2 = ndimage.uniform_filter1d(t2, 3)
        b2 = ndimage.uniform_filter1d(b2, 3)
        self.top_b, self.bot_b, self.valid = t2, b2, valid
        self.z_end = z_end if z_end is not None else self.nz
        return t2, b2

    def fill(self, width_fn, fin_hw=0.5, q=0.5, head_fn=None, head_end=0):
        """width_fn(iz) = ancho total del cuerpo (unidades). head_fn(iz, iy) = media anchura en la cabeza."""
        for iz in range(self.nz):
            yc = (self.top_b[iz] + self.bot_b[iz]) / 2
            hh = max(0.6, (self.bot_b[iz] - self.top_b[iz] + 1) / 2)
            for iy in range(self.ny):
                if not self.mask[iy, iz]:
                    continue
                inside = self.top_b[iz] - 0.5 <= iy <= self.bot_b[iz] + 0.5 and iz < self.z_end
                if head_fn is not None and iz < head_end:
                    hw = head_fn(iz, iy)
                    kind = "body" if hw > fin_hw else "fin"
                    hw = max(hw, fin_hw)
                elif inside:
                    r = (iy + 0.5 - (yc + 0.5)) / (hh + 0.35)
                    hw = width_fn(iz) / 2 * math.sqrt(max(0.06, 1 - r * r))
                    kind = "body"
                else:
                    hw, kind = fin_hw, "fin"
                hw = max(fin_hw, round(hw / q) * q)
                self.cells[(iy, iz)] = (hw, kind)

    def build(self, bone_of, y_base=0.0, z_front=0.0, dorsal=None, belly=None, front=None, back=None):
        """dorsal/belly: (pos, ancho en texeles, texeles por unidad de ancho) del mapa transpuesto y volteado.
        front/back: (pos, w, h, ancho total en unidades, y arriba en unidades, alto en unidades)."""
        used = set()
        k, vu = self.k, self.vu
        n = 0
        keys = sorted(self.cells, key=lambda c: (c[1], c[0]))
        for (iy, iz) in keys:
            if (iy, iz) in used:
                continue
            hw, kind = self.cells[(iy, iz)]
            bone = bone_of(iz)
            # crece hacia abajo
            y1 = iy
            while (y1 + 1, iz) in self.cells and (y1 + 1, iz) not in used and self.cells[(y1 + 1, iz)] == (hw, kind):
                y1 += 1
            # crece hacia la cola mientras la columna entera coincida y el hueso sea el mismo
            z1 = iz
            while True:
                nz_ = z1 + 1
                if bone_of(nz_) != bone:
                    break
                if all((yy, nz_) in self.cells and (yy, nz_) not in used and self.cells[(yy, nz_)] == (hw, kind) for yy in range(iy, y1 + 1)):
                    z1 = nz_
                else:
                    break
            for zz in range(iz, z1 + 1):
                for yy in range(iy, y1 + 1):
                    used.add((yy, zz))
            u0, u1 = iz * k, min(self.W, (z1 + 1) * k)
            v0, v1 = iy * k, min(self.H, (y1 + 1) * k)
            f = {}
            f["west"] = ([self.SW[0] + u0, self.SW[1] + v0], [u1 - u0, v1 - v0])
            f["east"] = ([self.SE[0] + (self.W - u1), self.SE[1] + v0], [u1 - u0, v1 - v0])
            zf, zb = iz * vu, (z1 + 1) * vu
            if dorsal:
                (dx, dy), dw, kd, L = dorsal
                cx = dw / 2
                f["up"] = ([dx + cx - hw * kd, dy + (L - u1)], [2 * hw * kd, u1 - u0])
            else:
                f["up"] = ([self.SW[0] + u0, self.SW[1] + v0], [u1 - u0, min(k, v1 - v0)])
            if belly:
                (bx, by), bw, kb, L = belly
                f["down"] = ([bx + bw / 2 - hw * kb, by + u0], [2 * hw * kb, u1 - u0])
            else:
                f["down"] = ([self.SW[0] + u0, self.SW[1] + v1 - min(k, v1 - v0)], [u1 - u0, min(k, v1 - v0)])
            ytop = y_base + (self.ny - iy) * vu
            ybot = y_base + (self.ny - 1 - y1) * vu
            for name, view in (("north", front), ("south", back)):
                if view:
                    (px, py), w, h, wu, ytop_u, hu = view
                    kx, ky = w / wu, h / hu
                    uu = px + w / 2 + (-hw if name == "north" else -hw) * kx
                    vv = py + (ytop_u - ytop) * ky
                    f[name] = ([uu, vv], [2 * hw * kx, (ytop - ybot) * ky])
                else:
                    uz = u0 if name == "north" else u1 - min(k, u1 - u0)
                    f[name] = ([self.SW[0] + uz, self.SW[1] + v0], [min(k, u1 - u0), v1 - v0])
            add_cube(self.g, bone, [-hw, ybot, z_front + zf], [2 * hw, ytop - ybot, zb - zf], f)
            n += 1
        return n


# ====================================================================== Tiburón Infernal
def tiburon(sheet):
    side = crop(sheet, (5, 22, 181, 102))
    top = crop(sheet, (3, 99, 91, 154))
    frontv = crop(sheet, (88, 99, 146, 154))
    backv = crop(sheet, (150, 105, 191, 149))
    bellyp = crop(sheet, (47, 165, 142, 210))
    s = 3.6
    vm = ViewModel("geometry.tiburon_infernal", side, s, vu=1.0)
    L = side.shape[1]
    # vista de arriba estirada al mismo largo que la de lado (la cabeza a la izquierda en las dos)
    ts = resize(top, L, top.shape[0] * L / top.shape[1])
    tmask = ts[..., 3] > 0
    tdist = ndimage.distance_transform_edt(tmask)
    rows = np.arange(ts.shape[0])
    half = []
    for x in range(L):
        col = tmask[:, x]
        if col.any():
            ys = rows[col]
            half.append((ys.max() - ys.min() + 1) / 2)
        else:
            half.append(0)
    half = np.array(half, float)
    body_half = ndimage.grey_opening(half, size=int(L * 0.12))          # sin las aletas pectorales
    body_half = ndimage.uniform_filter1d(body_half, 5)
    kd = s                                                               # texeles de la vista de arriba por unidad de ancho
    tcenter = ts.shape[0] / 2
    vm.body_bounds(win=11, z_end=int(vm.nz * 0.80))

    def width(iz):
        x = min(L - 1, int((iz + 0.5) * vm.k))
        return max(1.0, 2 * body_half[x] / kd) * 1.05

    vm.fill(width, fin_hw=0.5)
    nzz = vm.nz

    def bone_of(iz):
        if iz < nzz * 0.30:
            return "head"
        if iz < nzz * 0.62:
            return "body"
        if iz < nzz * 0.80:
            return "tail1"
        return "tail2"

    g = vm.g
    g.bone("root", [0, 0, 0])
    z_front = -nzz / 2
    g.bone("body", [0, 10, z_front + nzz * 0.30], "root")
    g.bone("head", [0, 10, z_front + nzz * 0.30], "body")
    g.bone("tail1", [0, 10, z_front + nzz * 0.62], "body")
    g.bone("tail2", [0, 10, z_front + nzz * 0.80], "tail1")
    # mapas del lomo (vista de arriba) y del vientre
    tsf = solid_fill(ts)
    dmap = flipy(T(tsf))                     # filas = largo (cola arriba), columnas = ancho
    dpos = vm.at.put(dmap)
    belly_strip = solid_fill(bellyp[int(bellyp.shape[0] * 0.62):, :])   # la parte blanca del vientre
    bmap = resize(belly_strip, ts.shape[0], L)
    bpos = vm.at.put(bmap)
    fpos = vm.at.put(solid_fill(frontv))
    bkpos = vm.at.put(solid_fill(backv))
    H_units = vm.ny * vm.vu
    maxw = 2 * body_half.max() / kd * 1.05
    n = vm.build(bone_of, y_base=0, z_front=z_front,
                 dorsal=(dpos, ts.shape[0], kd, L), belly=(bpos, ts.shape[0], kd, L),
                 front=(fpos, frontv.shape[1], frontv.shape[0], frontv.shape[1] / frontv.shape[0] * H_units, H_units, H_units),
                 back=(bkpos, backv.shape[1], backv.shape[0], backv.shape[1] / backv.shape[0] * H_units, H_units, H_units))
    # aletas pectorales (de la vista de arriba): placas a los lados, un poco bajo la mitad del cuerpo
    for side_name, sgn in (("left", 1), ("right", -1)):
        bn = "fin_" + side_name
        zc = int(nzz * 0.40)
        yc = (vm.ny - (vm.top_b[zc] + vm.bot_b[zc]) / 2) * vm.vu - 1.5
        g.bone(bn, [sgn * width(zc) / 2, yc, z_front + zc], "body")
        for iz in range(int(nzz * 0.25), int(nzz * 0.62)):
            x = min(L - 1, int((iz + 0.5) * vm.k))
            col = tmask[:, x]
            if not col.any():
                continue
            ys = rows[col]
            ext = ((ys.max() - tcenter) if sgn > 0 else (tcenter - ys.min())) / kd
            bw = width(iz) / 2
            if ext <= bw + 0.6:
                continue
            x0, x1 = (bw - 0.3, ext) if sgn > 0 else (-ext, -bw + 0.3)
            u0 = iz * vm.k
            dx, dy = dpos
            cx = ts.shape[0] / 2
            up = ([dx + cx + x0 * kd, dy + (L - u0 - vm.k)], [(x1 - x0) * kd, vm.k])
            dn = ([dx + cx + x0 * kd, dy + (L - u0 - vm.k)], [(x1 - x0) * kd, vm.k])
            sideuv = ([vm.SW[0] + u0, vm.SW[1] + vm.k * 8], [vm.k, 2])
            add_cube(g, bn, [x0, yc - 0.4, z_front + iz], [x1 - x0, 0.8, 1],
                     {"up": up, "down": dn, "north": sideuv, "south": sideuv, "east": sideuv, "west": sideuv})
    from fauna import wave, anim
    swim = {"head": {"rotation": wave(-4, 1.2, steps=8, phase=0.6)},
            "body": {"rotation": wave(4, 1.2, steps=8)},
            "tail1": {"rotation": wave(12, 1.2, steps=8, phase=-0.9)},
            "tail2": {"rotation": wave(22, 1.2, steps=8, phase=-1.8)},
            "fin_left": {"rotation": wave(8, 1.2, steps=8, axis=2)},
            "fin_right": {"rotation": wave(-8, 1.2, steps=8, axis=2)}}
    bite = {"head": {"rotation": {"0.00": [0, 0, 0], "0.15": [-14, 0, 0], "0.30": [8, 0, 0], "0.50": [0, 0, 0]},
                     "position": {"0.00": [0, 0, 0], "0.15": [0, 0, -2], "0.50": [0, 0, 0]}},
            "tail2": {"rotation": {"0.00": [0, 0, 0], "0.20": [0, 30, 0], "0.50": [0, 0, 0]}}}
    anims = {"animation.tiburon_infernal.swim": anim(swim, 1.2), "animation.tiburon_infernal.bite": anim(bite, 0.5, loop=False)}
    tex = vm.at.image()
    return g, tex, glow_of(tex, lambda r, gg, b: r > 200 and gg < 60 and b < 70), anims


# ====================================================================== Serpiente Marina
CUT = 85          # en la vista estirada, aquí termina la cabeza (vista desde arriba) y empieza el cuello


def compose_serpent(sheet, band):
    """Une la cabeza de perfil (de la vista curva, enderezada 30°) con el cuerpo estirado de la otra vista."""
    head = crop(sheet, (186, 26, 244, 100))
    im = Image.fromarray(head, "RGBA").rotate(-30, resample=Image.NEAREST, expand=True)
    im = im.crop(im.getbbox())
    hm = np.array(im)[..., 3] > 0
    # cuerpo más largo para el jefe: se repite un tramo de escamas del medio (mismo arte, sin estirar)
    body = np.concatenate([band[:, CUT:145], band[:, 100:145], band[:, 145:]], axis=1)
    bm = body[..., 3] > 0
    def col_extent(m, xs):
        ys = np.nonzero(m[:, xs].any(1))[0]
        return ys.min(), ys.max()
    b0, b1 = col_extent(bm, slice(0, 4))
    h0, h1 = col_extent(hm, slice(hm.shape[1] - 4, hm.shape[1]))
    sc = 1.7 * (b1 - b0 + 1) / hm.shape[0]
    im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.NEAREST)
    ha = np.array(im)
    hm = ha[..., 3] > 0
    h0, h1 = col_extent(hm, slice(int(hm.shape[1] * 0.75), hm.shape[1]))
    off = int(round((b0 + b1) / 2 - (h0 + h1) / 2))         # centro del cuello alineado con el centro del cuerpo
    top = min(0, off)
    H = max(body.shape[0], off + ha.shape[0]) - top
    overlap = 3
    W = ha.shape[1] + body.shape[1] - overlap
    out = np.zeros((H, W, 4), np.uint8)
    out[-top:-top + body.shape[0], ha.shape[1] - overlap:] = body
    y0 = off - top
    region = out[y0:y0 + ha.shape[0], :ha.shape[1]]
    region[hm] = ha[hm]
    return out


def serpiente(sheet):
    band = crop(sheet, (198, 105, 380, 185), join=False)
    side = compose_serpent(sheet, band)
    frontv = crop(sheet, (202, 148, 273, 216))
    backv = crop(sheet, (290, 148, 359, 213))
    s, vu = 1.0, 2.0
    vm = ViewModel("geometry.serpiente_marina", side, s, vu=vu, atlas=(1024, 512))
    vm.body_bounds(win=9)
    nzz = vm.nz
    head_cells = (side.shape[1] - (band.shape[1] - CUT + 45) + 3) / vm.k
    head_end = int(round(head_cells))
    # ancho de la cabeza desde la vista de frente (por fila)
    fm = frontv[..., 3] > 0
    fh_rows = []
    for r in range(fm.shape[0]):
        xs = np.nonzero(fm[r])[0]
        fh_rows.append((xs.max() - xs.min() + 1) / 2 if len(xs) else 0)
    fh_rows = np.array(fh_rows, float)
    # la vista de frente mide lo mismo de alto que la cabeza de lado
    hy0 = int(vm.top_b[:head_end].min()) if head_end else 0
    hy1 = int(max(np.nonzero(vm.mask[:, :head_end].any(1))[0]))
    head_h = (hy1 - hy0 + 1) * vu
    kf = fm.shape[0] / head_h

    def head_fn(iz, iy):
        r = int((iy - hy0 + 0.5) * vu * kf)
        r = min(max(r, 0), fm.shape[0] - 1)
        hw = fh_rows[r] / kf
        taper = min(1.0, 0.45 + 0.55 * (iz + 1) / max(1, head_end * 0.6))   # el hocico más angosto
        return hw * taper * 0.8

    def width(iz):
        h = (vm.bot_b[iz] - vm.top_b[iz] + 1) * vu
        return max(2.0, h * 0.78)

    vm.fill(width, fin_hw=1.0, q=1.0, head_fn=head_fn, head_end=head_end)
    nseg = 8
    seg_len = (nzz - head_end) / nseg

    def bone_of(iz):
        if iz < head_end:
            return "head"
        return "seg%d" % min(nseg, 1 + int((iz - head_end) / seg_len))

    g = vm.g
    g.bone("root", [0, 0, 0])
    z_front = -nzz * vu / 2
    ymid = (vm.ny - (vm.top_b[head_end] + vm.bot_b[head_end]) / 2) * vu
    g.bone("neck", [0, ymid, z_front + head_end * vu], "root")
    g.bone("head", [0, ymid, z_front + head_end * vu], "neck")
    prev = "neck"
    for k in range(1, nseg + 1):
        z = z_front + (head_end + (k - 1) * seg_len) * vu
        izc = min(nzz - 1, int(head_end + (k - 0.5) * seg_len))
        yk = (vm.ny - (vm.top_b[izc] + vm.bot_b[izc]) / 2) * vu
        g.bone("seg%d" % k, [0, yk, z], prev)
        prev = "seg%d" % k
    # lomo y vientre: franjas tomadas de la parte de arriba y de abajo del cuerpo en la vista de lado
    L = side.shape[1]
    full = solid_fill(side)
    dors = np.zeros((32, L, 4), np.uint8)
    bel = np.zeros((32, L, 4), np.uint8)
    for x in range(L):
        iz = min(nzz - 1, int(x / vm.k))
        t = int(vm.top_b[iz] * vm.k)
        b = int((vm.bot_b[iz] + 1) * vm.k) - 1
        tt = min(full.shape[0] - 1, t + 2)
        colt = full[tt:tt + 6, x] if tt + 6 <= full.shape[0] else full[-6:, x]
        colb = full[max(0, b - 5):b + 1, x]
        for r in range(32):
            dors[r, x] = colt[(r * 7 + x) % len(colt)]
            bel[r, x] = colb[(r * 3 + x) % len(colb)]
    dmap = flipy(T(dors))
    dpos = vm.at.put(dmap)
    bpos = vm.at.put(T(bel))
    fpos = vm.at.put(solid_fill(frontv))
    bkpos = vm.at.put(solid_fill(backv))
    maxw = 2 * max(fh_rows) / kf * 0.8
    H_head_top = (vm.ny - hy0) * vu
    n = vm.build(bone_of, y_base=0, z_front=z_front, dorsal=(dpos, 32, 32 / 24.0, L), belly=(bpos, 32, 32 / 24.0, L),
                 front=(fpos, frontv.shape[1], frontv.shape[0], frontv.shape[1] / kf, H_head_top, head_h),
                 back=(bkpos, backv.shape[1], backv.shape[0], backv.shape[1] / kf, H_head_top, head_h))
    from fauna import wave, anim
    swim = {"head": {"rotation": wave(6, 2.4, steps=12, phase=0.8)}, "neck": {"rotation": wave(5, 2.4, steps=12, phase=0.4)}}
    for k in range(1, nseg + 1):
        swim["seg%d" % k] = {"rotation": wave(7 + k * 1.2, 2.4, steps=12, phase=-k * 0.75)}
    roar = {"head": {"rotation": {"0.00": [0, 0, 0], "0.40": [-28, 0, 0], "1.20": [-28, 0, 0], "1.60": [0, 0, 0]}},
            "neck": {"rotation": {"0.00": [0, 0, 0], "0.40": [-12, 0, 0], "1.20": [-12, 0, 0], "1.60": [0, 0, 0]}}}
    anims = {"animation.serpiente_marina.swim": anim(swim, 2.4), "animation.serpiente_marina.roar": anim(roar, 1.6, loop=False)}
    tex = vm.at.image()
    return g, tex, glow_of(tex, lambda r, gg, b: r > 220 and gg < 70 and b > 60), anims


def glow_of(img, test):
    a = np.array(img)
    r, gg, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    sel = (a[..., 3] > 0) & np.vectorize(lambda x, y, z: bool(test(x, y, z)))(r, gg, b)
    out = np.zeros_like(a)
    out[sel] = a[sel]
    return Image.fromarray(out, "RGBA")
