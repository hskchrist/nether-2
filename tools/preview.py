"""Renderizador por software de modelos .geo.json (para revisar y para el manual)."""
import json
import math
from PIL import Image, ImageDraw


def rot_matrix(rx, ry, rz):
    # Convención Bedrock: los tres ejes van invertidos respecto a la mano derecha.
    rx, ry, rz = [-math.radians(a) for a in (rx, ry, rz)]
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Y = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Z = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    return mul(Z, mul(Y, X))


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def apply(m, v):
    return [sum(m[i][k] * v[k] for k in range(3)) for i in range(3)]


def render(geo_path, tex_path, out_path, size=(600, 600), yaw=35, pitch=15, pose=None, hidden=(), scale=None, bg=(24, 10, 12, 255), emissive=None):
    pose = pose or {}
    geo = json.load(open(geo_path))["minecraft:geometry"][0]
    bones = {b["name"]: b for b in geo["bones"]}
    tex = Image.open(tex_path).convert("RGBA")

    def bone_tf(name):
        """Devuelve función que transforma un punto local del hueso al espacio del modelo."""
        chain = []
        n = name
        while n:
            chain.append(bones[n])
            n = bones[n].get("parent")
        def f(p):
            for b in chain:
                r = list(b.get("rotation", [0, 0, 0]))
                pr = pose.get(b["name"], {})
                if "rotation" in pr:
                    r = [r[i] + pr["rotation"][i] for i in range(3)]
                piv = b["pivot"]
                m = rot_matrix(*r)
                q = apply(m, [p[i] - piv[i] for i in range(3)])
                p = [q[i] + piv[i] for i in range(3)]
                if "position" in pr:
                    p = [p[0] - pr["position"][0], p[1] + pr["position"][1], p[2] + pr["position"][2]]
            return p
        return f

    def hidden_bone(name):
        n = name
        while n:
            if n in hidden:
                return True
            n = bones[n].get("parent")
        return False

    view = mul(rot_matrix(-pitch, 0, 0), rot_matrix(0, yaw, 0))
    quads = []
    for b in geo["bones"]:
        if hidden_bone(b["name"]):
            continue
        f = bone_tf(b["name"])
        for c in b.get("cubes", []):
            ox, oy, oz = c["origin"]
            w, h, d = c["size"]
            inf = c.get("inflate", 0)
            x0, y0, z0 = ox - inf, oy - inf, oz - inf
            x1, y1, z1 = ox + w + inf, oy + h + inf, oz + d + inf
            u, v = c["uv"]
            W, H, Dd = math.ceil(w), math.ceil(h), math.ceil(d)
            # caras: (uv rect, función (s,t)->punto 3D con s,t en [0,1]); norte = -Z = frente
            faces = [
                ((u + Dd, v + Dd, W, H), lambda s, t: (x0 + s * (x1 - x0), y1 - t * (y1 - y0), z0)),          # frente (-Z)
                ((u + 2 * Dd + W, v + Dd, W, H), lambda s, t: (x1 - s * (x1 - x0), y1 - t * (y1 - y0), z1)),  # espalda (+Z)
                ((u + Dd + W, v + Dd, Dd, H), lambda s, t: (x1, y1 - t * (y1 - y0), z0 + s * (z1 - z0))),     # lado izquierdo (+X)
                ((u, v + Dd, Dd, H), lambda s, t: (x0, y1 - t * (y1 - y0), z1 - s * (z1 - z0))),              # lado derecho (-X)
                ((u + Dd, v, W, Dd), lambda s, t: (x0 + s * (x1 - x0), y1, z1 - t * (z1 - z0))),              # arriba
                ((u + Dd + W, v, W, Dd), lambda s, t: (x0 + s * (x1 - x0), y0, z0 + t * (z1 - z0))),          # abajo
            ]
            for fi, ((fu, fv, fw, fh), fn) in enumerate(faces):
                shade = [0.82, 0.7, 0.62, 0.62, 1.0, 0.45][fi]
                if fw <= 0 or fh <= 0:
                    continue
                for j in range(fh):
                    for i in range(fw):
                        px = tex.getpixel((min(tex.width - 1, fu + i), min(tex.height - 1, fv + j)))
                        if px[3] < 10:
                            continue
                        pts = [fn(i / fw, j / fh), fn((i + 1) / fw, j / fh), fn((i + 1) / fw, (j + 1) / fh), fn(i / fw, (j + 1) / fh)]
                        pts = [apply(view, f(p)) for p in pts]
                        depth = sum(p[2] for p in pts) / 4
                        sh_ = 1.0 if (emissive and emissive(px)) else shade
                        quads.append((depth, pts, tuple(int(cc * sh_) for cc in px[:3]) + (255,)))
    if not quads:
        raise RuntimeError("nada que dibujar")
    xs = [p[0] for q in quads for p in q[1]]
    ys = [p[1] for q in quads for p in q[1]]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    sc = scale or 0.86 * min(size[0] / (maxx - minx), size[1] / (maxy - miny))
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    img = Image.new("RGBA", size, bg)
    dr = ImageDraw.Draw(img)
    quads.sort(key=lambda q: q[0], reverse=True)
    for depth, pts, col in quads:
        poly = [(size[0] / 2 + (p[0] - cx) * sc, size[1] / 2 - (p[1] - cy) * sc) for p in pts]
        dr.polygon(poly, fill=col[:3] + (255,))
    img.save(out_path)
    return img
