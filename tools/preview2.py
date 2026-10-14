"""Renderizador por software con z-buffer (numpy) para modelos .geo.json.

Más preciso que preview.py: cada cara se proyecta en ortográfica (un rectángulo pasa a ser un paralelogramo,
así que la textura se mapea de forma exacta), con prueba de profundidad por píxel, transparencia recortada,
rotación por cubo, escala por hueso e iluminación direccional suave.
"""
import json
import math
import numpy as np
from PIL import Image


def rot_matrix(rx, ry, rz):
    # Igual que GeckoLib (que invierte X e Y y además refleja el eje X del modelo): en el espacio Bedrock
    # equivale a Rz(-z) * Ry(+y) * Rx(-x).
    rx, ry, rz = -math.radians(rx), math.radians(ry), -math.radians(rz)
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Z @ Y @ X


_cache = {}


def _load(geo_path, tex_path):
    key = (geo_path, tex_path)
    if key not in _cache:
        geo = json.load(open(geo_path))["minecraft:geometry"][0]
        tex = np.array(Image.open(tex_path).convert("RGBA"))
        _cache[key] = (geo, tex)
    return _cache[key]


def clear_cache():
    _cache.clear()


def render(geo_path, tex_path, size=(600, 600), yaw=35, pitch=15, pose=None, hidden=(), scale=None, bg=(24, 10, 12, 255),
           emissive=None, center=None, ss=2, out_path=None, light=(0.45, 0.8, -0.4), ambient=0.55, ground=None, markers=()):
    """Devuelve una imagen PIL. pose = {hueso: {"rotation": [..], "position": [..], "scale": [..]}}.
    center = punto del modelo (x, y, z) que queda en el centro de la imagen (por defecto, el centro del modelo).
    ground = altura (y) donde dibujar una sombra elíptica, o None."""
    pose = pose or {}
    geo, tex = _load(geo_path, tex_path)
    th, tw = tex.shape[:2]
    bones = {b["name"]: b for b in geo["bones"]}

    def hidden_bone(name):
        n = name
        while n:
            if n in hidden:
                return True
            n = bones[n].get("parent")
        return False

    # matrices 4x4 por hueso (espacio local -> modelo)
    mats = {}

    def bone_mat(name):
        if name in mats:
            return mats[name]
        b = bones[name]
        r = list(b.get("rotation", [0, 0, 0]))
        pr = pose.get(name, {})
        if "rotation" in pr:
            r = [r[i] + pr["rotation"][i] for i in range(3)]
        piv = np.array(b["pivot"], dtype=float)
        sc = np.array(pr.get("scale", [1, 1, 1]), dtype=float)
        pos = pr.get("position", [0, 0, 0])
        M = np.eye(4)
        R = rot_matrix(*r) * sc[None, :]
        M[:3, :3] = R
        M[:3, 3] = piv - R @ piv + np.array([-pos[0], pos[1], pos[2]], dtype=float)
        par = b.get("parent")
        if par:
            M = bone_mat(par) @ M
        mats[name] = M
        return M

    # vista ortográfica
    V = rot_matrix(-pitch, 0, 0) @ rot_matrix(0, -yaw, 0)
    L = np.array(light, dtype=float)
    L = L / np.linalg.norm(L)

    faces = []  # (p0, eu, ev, normal, uvrect, emissive_ok)
    for b in geo["bones"]:
        if hidden_bone(b["name"]):
            continue
        M = bone_mat(b["name"])
        for c in b.get("cubes", []):
            ox, oy, oz = c["origin"]
            w, h, d = c["size"]
            inf = c.get("inflate", 0)
            x0, y0, z0 = ox - inf, oy - inf, oz - inf
            x1, y1, z1 = ox + w + inf, oy + h + inf, oz + d + inf
            if isinstance(c["uv"], dict):
                # UV por cara (como GeckoLib): esquinas en espacio Minecraft (X invertido) -> de vuelta a Bedrock
                mx0, mx1 = -x1, -x0
                Cm = np.eye(4)
                if "rotation" in c:
                    piv = np.array(c.get("pivot", [0, 0, 0]), dtype=float)
                    R = rot_matrix(*c["rotation"])
                    Cm[:3, :3] = R
                    Cm[:3, 3] = piv - R @ piv
                T = M @ Cm
                P = lambda q: (T @ np.array([-q[0], q[1], q[2], 1.0]))[:3]
                blb, brb, tlb, trb = (mx0, y0, z0), (mx0, y0, z1), (mx0, y1, z0), (mx0, y1, z1)
                tlf, trf, blf, brf = (mx1, y1, z0), (mx1, y1, z1), (mx1, y0, z0), (mx1, y0, z1)
                quads = {"west": [trb, tlb, blb, brb], "east": [tlf, trf, brf, blf], "north": [tlb, tlf, blf, blb],
                         "south": [trf, trb, brb, brf], "up": [trb, trf, tlf, tlb], "down": [blb, blf, brf, brb]}
                for fname, fuv in c["uv"].items():
                    v0, v1, v2, v3 = [P(q) for q in quads[fname]]
                    eu, ev = v0 - v1, v2 - v1
                    n = np.cross(ev, eu)
                    nn = np.linalg.norm(n)
                    n = n / nn if nn > 1e-9 else np.array([0, 1.0, 0])
                    (U0, V0), (du, dv) = fuv["uv"], fuv["uv_size"]
                    faces.append((v1, eu, ev, n, (U0, V0, du if abs(du) > 1e-3 else 1e-3, dv if abs(dv) > 1e-3 else 1e-3)))
                continue
            u, v = c["uv"]
            W, H, D = math.floor(w), math.floor(h), math.floor(d)
            Cm = np.eye(4)
            if "rotation" in c:
                piv = np.array(c.get("pivot", [0, 0, 0]), dtype=float)
                R = rot_matrix(*c["rotation"])
                Cm[:3, :3] = R
                Cm[:3, 3] = piv - R @ piv
            T = M @ Cm
            P = lambda x, y, z: (T @ np.array([x, y, z, 1.0]))[:3]
            # (esquina superior izquierda de la textura, dirección s, dirección t, rect uv)
            spec = [
                (P(x0, y1, z0), P(x1, y1, z0), P(x0, y0, z0), (u + D, v + D, W, H)),          # frente (-Z)
                (P(x1, y1, z1), P(x0, y1, z1), P(x1, y0, z1), (u + 2 * D + W, v + D, W, H)),  # espalda (+Z)
                (P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z0), (u + D + W, v + D, D, H)),      # izquierda (+X)
                (P(x0, y1, z1), P(x0, y1, z0), P(x0, y0, z1), (u, v + D, D, H)),              # derecha (-X)
                (P(x0, y1, z1), P(x1, y1, z1), P(x0, y1, z0), (u + D, v, W, D)),              # arriba
                (P(x0, y0, z0), P(x1, y0, z0), P(x0, y0, z1), (u + D + W, v, W, D)),          # abajo
            ]
            for a, bpt, cpt, rect in spec:
                # GeckoLib: si el tamaño redondeado es 0, la cara lee un solo texel
                rect = (rect[0], rect[1], max(rect[2], 1e-3), max(rect[3], 1e-3))
                eu, ev = bpt - a, cpt - a
                n = np.cross(ev, eu)
                nn = np.linalg.norm(n)
                n = n / nn if nn > 1e-9 else np.array([0, 1.0, 0])
                faces.append((a, eu, ev, n, rect))

    if not faces:
        raise RuntimeError("nada que dibujar")
    # proyectar
    pts = []
    for a, eu, ev, n, rect in faces:
        for p in (a, a + eu, a + ev, a + eu + ev):
            pts.append(V @ p)
    pts = np.array(pts)
    if center is None:
        cx, cy = (pts[:, 0].min() + pts[:, 0].max()) / 2, (pts[:, 1].min() + pts[:, 1].max()) / 2
    else:
        cc = V @ np.array(center, dtype=float)
        cx, cy = cc[0], cc[1]
    Wd, Hd = size[0] * ss, size[1] * ss
    if scale is None:
        sc = 0.86 * min(size[0] / (np.ptp(pts[:, 0]) + 1e-6), size[1] / (np.ptp(pts[:, 1]) + 1e-6))
    else:
        sc = scale
    sc *= ss
    color = np.zeros((Hd, Wd, 3), dtype=float)
    color[:] = np.array(bg[:3], dtype=float)
    zbuf = np.full((Hd, Wd), 1e9)

    def to_screen(p):
        q = V @ p
        return np.array([Wd / 2 + (q[0] - cx) * sc, Hd / 2 - (q[1] - cy) * sc, q[2]])

    # sombra en el suelo
    if ground is not None:
        g = to_screen(np.array([0, ground, 0.0]))
        rx = 0.35 * (np.ptp(pts[:, 0])) * sc
        yy, xx = np.mgrid[0:Hd, 0:Wd]
        e = ((xx - g[0]) / max(rx, 1)) ** 2 + ((yy - g[1]) / max(rx * 0.22, 1)) ** 2
        m = e < 1
        color[m] *= (0.55 + 0.45 * e[m])[:, None]

    texf = tex.astype(float)
    for a, eu, ev, n, (fu, fv, fw, fh) in faces:
        A = to_screen(a)
        U = to_screen(a + eu) - A
        Vv = to_screen(a + ev) - A
        det = U[0] * Vv[1] - U[1] * Vv[0]
        if abs(det) < 1e-6:
            continue
        corners = np.array([A, A + U, A + Vv, A + U + Vv])
        xmin = max(int(math.floor(corners[:, 0].min())), 0)
        xmax = min(int(math.ceil(corners[:, 0].max())), Wd - 1)
        ymin = max(int(math.floor(corners[:, 1].min())), 0)
        ymax = min(int(math.ceil(corners[:, 1].max())), Hd - 1)
        if xmin > xmax or ymin > ymax:
            continue
        yy, xx = np.mgrid[ymin:ymax + 1, xmin:xmax + 1]
        px_ = xx + 0.5 - A[0]
        py_ = yy + 0.5 - A[1]
        s = (px_ * Vv[1] - py_ * Vv[0]) / det
        t = (U[0] * py_ - U[1] * px_) / det
        inside = (s >= 0) & (s < 1) & (t >= 0) & (t < 1)
        if not inside.any():
            continue
        z = A[2] + s * U[2] + t * Vv[2]
        tu = np.clip(np.floor(fu + s * fw).astype(int), 0, tw - 1)
        tv = np.clip(np.floor(fv + t * fh).astype(int), 0, th - 1)
        texel = texf[tv, tu]
        ok = inside & (texel[..., 3] > 10) & (z < zbuf[ymin:ymax + 1, xmin:xmax + 1])
        if not ok.any():
            continue
        # iluminación: caras vistas por detrás usan la normal invertida
        nv = V @ n
        nrm = n if nv[2] <= 0 else -n
        diff = max(0.0, float(np.dot(nrm, L)))
        shade = ambient + (1 - ambient) * diff
        rgb = texel[..., :3] * shade
        if emissive is not None:
            em = np.zeros(ok.shape, dtype=bool)
            sub = texel[ok].astype(int)
            em_vals = np.array([emissive(tuple(p)) for p in sub]) if len(sub) < 4000 else None
            if em_vals is not None:
                em[ok] = em_vals
                rgb[em] = texel[..., :3][em]
        region = color[ymin:ymax + 1, xmin:xmax + 1]
        region[ok] = rgb[ok]
        zbuf[ymin:ymax + 1, xmin:xmax + 1][ok] = z[ok]
    img = Image.fromarray(np.clip(color, 0, 255).astype(np.uint8), "RGB")
    if ss > 1:
        img = img.resize(size, Image.LANCZOS)
    # puntos de referencia (hueso, punto local) -> coordenadas en la imagen final
    img.info["markers"] = []
    for bname, pt in markers:
        q = to_screen((bone_mat(bname) @ np.array(list(pt) + [1.0]))[:3])
        img.info["markers"].append((q[0] / ss, q[1] / ss, q[2]))
    if out_path:
        img.save(out_path)
    return img
