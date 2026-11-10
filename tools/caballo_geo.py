"""Convierte el modelo del caballo del usuario (tools/ref/caballo/nether_horse.obj, exportado de Blockbench) a un
.geo.json de GeckoLib SIN cambiar la forma ni la textura: cada cubo queda igual (tamaño, giro y UV de cada cara).
Sólo se agrupan los cubos en huesos para poder animarlos (patas, cola, cuello, cabeza, silla, riendas)."""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OBJ = os.path.join(HERE, "ref", "caballo", "nether_horse.obj")
TW = TH = 64

# hueso de cada pieza
BONE = {"Body": "body", "Saddle": "saddle", "BagL": "bags", "BagR": "bags", "Tail": "tail",
        "LegBL": "leg_back_left", "LegBR": "leg_back_right", "LegFL": "leg_front_left", "LegFR": "leg_front_right",
        "Neck": "neck", "Mane": "neck", "ReinsL": "reins", "ReinsR": "reins",
        "Head": "head", "Muzzle": "head", "EarL": "head", "EarR": "head", "MuleEarL": "mule_ears", "MuleEarR": "mule_ears",
        "Bridle": "bridle", "BitL": "bridle", "BitR": "bridle"}


def rot_matrix(rx, ry, rz):  # igual que preview2 / GeckoLib
    rx, ry, rz = -math.radians(rx), math.radians(ry), -math.radians(rz)
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Z @ Y @ X


def parse():
    objs, V, VT = [], [], []
    cur = None
    for line in open(OBJ):
        p = line.split()
        if not p:
            continue
        if p[0] == "o":
            cur = {"name": p[1], "f": []}
            objs.append(cur)
        elif p[0] == "v":
            V.append([float(x) for x in p[1:4]])
        elif p[0] == "vt":
            VT.append([float(x) for x in p[1:3]])
        elif p[0] == "f":
            cur["f"].append([tuple(int(i) for i in t.split("/")[:2]) for t in p[1:]])
    return objs, np.array(V), np.array(VT)


def to_geo(p):  # Blockbench (bloques) -> Bedrock (píxeles, X invertido)
    return np.array([-p[0] * 16, p[1] * 16, p[2] * 16])


def solve_rotation(R):
    best = None
    for rx in np.arange(-180, 180.01, 0.5):
        for ry in (0.0,):
            for rz in (0.0,):
                err = np.abs(rot_matrix(rx, ry, rz) - R).sum()
                if best is None or err < best[0]:
                    best = (err, rx, ry, rz)
    if best[0] > 1e-2:  # no es sólo un giro en X: búsqueda completa
        for rx in np.arange(-180, 180, 2.5):
            for ry in np.arange(-180, 180, 2.5):
                for rz in np.arange(-180, 180, 2.5):
                    err = np.abs(rot_matrix(rx, ry, rz) - R).sum()
                    if err < best[0]:
                        best = (err, rx, ry, rz)
        # afinar alrededor del mejor
        for step in (0.25, 0.02):
            e0, bx, by, bz = best
            for rx in np.arange(bx - 10 * step, bx + 10 * step, step):
                for ry in np.arange(by - 10 * step, by + 10 * step, step):
                    for rz in np.arange(bz - 10 * step, bz + 10 * step, step):
                        err = np.abs(rot_matrix(rx, ry, rz) - R).sum()
                        if err < best[0]:
                            best = (err, rx, ry, rz)
    return best


def cube(o, V, VT):
    idx = sorted({v - 1 for f in o["f"] for v, _ in f})
    P = np.array([to_geo(V[i]) for i in idx])
    center = P.mean(0)
    # ejes del cubo: direcciones de sus aristas (sirve también para cubos planos, como las riendas)
    axes = []
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            d = P[j] - P[i]
            L = np.linalg.norm(d)
            if L < 1e-6:
                continue
            d = d / L
            # una arista es perpendicular a una de las otras ya encontradas, o es la primera
            if any(abs(abs(np.dot(d, m)) - 1) < 1e-4 for m in axes):
                continue
            if all(abs(np.dot(d, m)) < 1e-4 for m in axes):
                axes.append(d)
            if len(axes) == 3:
                break
        if len(axes) == 3:
            break
    if len(axes) == 2:  # cubo plano: el tercer eje sale de los otros dos
        axes.append(np.cross(axes[0], axes[1]))
    # ordenar como X, Y, Z del mundo
    R = np.zeros((3, 3))
    used = set()
    for k in range(3):
        e = np.eye(3)[k]
        j = max((j for j in range(len(axes)) if j not in used), key=lambda j: abs(np.dot(axes[j], e)))
        used.add(j)
        ax = axes[j] * (1 if np.dot(axes[j], e) >= 0 else -1)
        R[:, k] = ax
    if np.linalg.det(R) < 0:
        R[:, 2] = -R[:, 2]
    local = (P - center) @ R
    size = (local.max(0) - local.min(0)).round(4)
    err, rx, ry, rz = solve_rotation(R)
    rot = [round(rx, 3), round(ry, 3), round(rz, 3)]
    Rm = rot_matrix(*rot)
    origin = (center - size / 2).round(4)
    x0, y0, z0 = origin
    x1, y1, z1 = origin + size
    piv = center
    mx0, mx1 = -x1, -x0

    def Pq(q):
        return Rm @ (np.array([-q[0], q[1], q[2]]) - piv) + piv

    blb, brb, tlb, trb = (mx0, y0, z0), (mx0, y0, z1), (mx0, y1, z0), (mx0, y1, z1)
    tlf, trf, blf, brf = (mx1, y1, z0), (mx1, y1, z1), (mx1, y0, z0), (mx1, y0, z1)
    quads = {"west": [trb, tlb, blb, brb], "east": [tlf, trf, brf, blf], "north": [tlb, tlf, blf, blb],
             "south": [trf, trb, brb, brf], "up": [trb, trf, tlf, tlb], "down": [blb, blf, brf, brb]}
    uv = {}
    problems = []
    for f in o["f"]:
        pts = [to_geo(V[v - 1]) for v, _ in f]
        tex = [(VT[t - 1][0] * TW, (1 - VT[t - 1][1]) * TH) for _, t in f]
        fc = np.mean(pts, axis=0)
        # qué cara es: la de la lista cuyo centro coincide
        name = min(quads, key=lambda k: np.linalg.norm(np.mean([Pq(q) for q in quads[k]], axis=0) - fc))
        q = [Pq(c) for c in quads[name]]

        def uv_at(p):
            i = min(range(4), key=lambda i: np.linalg.norm(pts[i] - p))
            if np.linalg.norm(pts[i] - p) > 1e-2:
                problems.append((o["name"], name, "esquina"))
            return tex[i]

        u1, v1 = uv_at(q[1])
        u0, v0 = uv_at(q[0])
        u2, v2 = uv_at(q[2])
        u3, v3 = uv_at(q[3])
        du, dv = u0 - u1, v2 - v1
        # comprobar que la cara no está girada (u sólo cambia en eu, v sólo en ev)
        if abs(v0 - v1) > 1e-3 or abs(u2 - u1) > 1e-3 or abs(u3 - u0) > 1e-3 or abs(v3 - v2) > 1e-3:
            problems.append((o["name"], name, "uv girado"))
        uv[name] = {"uv": [round(u1, 4), round(v1, 4)], "uv_size": [round(du, 4), round(dv, 4)]}
    c = {"origin": origin.tolist(), "size": size.tolist(), "uv": uv}
    if any(abs(a) > 1e-3 for a in rot):
        c["rotation"] = rot
        c["pivot"] = piv.round(4).tolist()
    return c, err, problems


def build():
    objs, V, VT = parse()
    cubes = {}
    report = []
    for o in objs:
        c, err, prob = cube(o, V, VT)
        cubes.setdefault(BONE[o["name"]], []).append(c)
        report.append((o["name"], round(float(err), 4), c.get("rotation"), prob))
    # pivotes de los huesos (para animar)
    piv = {"body": [0, 16, 0], "saddle": [0, 16, 0], "bags": [0, 16, 0], "tail": [0, 20, 10],
           "leg_back_left": [3, 11, 9], "leg_back_right": [-3, 11, 9], "leg_front_left": [3, 11, -9], "leg_front_right": [-3, 11, -9],
           "neck": [0, 20, -8], "reins": [0, 20, -8], "head": [0, 28, -11], "mule_ears": [0, 28, -11], "bridle": [0, 28, -11]}
    parent = {"saddle": "body", "bags": "body", "tail": "body", "neck": "body", "reins": "neck", "head": "neck",
              "mule_ears": "head", "bridle": "head"}
    order = ["body", "saddle", "bags", "tail", "leg_back_left", "leg_back_right", "leg_front_left", "leg_front_right",
             "neck", "reins", "head", "mule_ears", "bridle", "rider"]
    bones = []
    for b in order:
        if b == "rider":  # punto donde se sienta el jinete (para ubicarlo)
            bones.append({"name": "rider", "parent": "body", "pivot": [0, 22, 0]})
            continue
        bone = {"name": b, "pivot": piv[b]}
        if b in parent:
            bone["parent"] = parent[b]
        if b in cubes:
            bone["cubes"] = cubes[b]
        bones.append(bone)
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry.caballo_nether", "texture_width": TW, "texture_height": TH,
                        "visible_bounds_width": 4, "visible_bounds_height": 4, "visible_bounds_offset": [0, 1.5, 0]},
        "bones": bones}]}
    return geo, report


if __name__ == "__main__":
    g, rep = build()
    for r in rep:
        print(r)
    json.dump(g, open("/tmp/claude-0/caballo_in/caballo_nether.geo.json", "w"), indent=1)


def bbmodel(geo, tex_path, out_path):
    """El mismo modelo como proyecto de Blockbench (.bbmodel) para abrirlo y verlo."""
    import base64
    import uuid
    g = geo["minecraft:geometry"][0]
    elements, outliner_by = [], {}
    groups = {}
    for b in g["bones"]:
        px, py, pz = b.get("pivot", [0, 0, 0])
        grp = {"name": b["name"], "origin": [-px, py, pz], "rotation": [0, 0, 0], "uuid": str(uuid.uuid4()),
               "export": True, "isOpen": True, "visibility": b["name"] not in ("bags", "mule_ears"), "children": []}
        groups[b["name"]] = grp
        for c in b.get("cubes", []):
            ox, oy, oz = c["origin"]
            sx, sy, sz = c["size"]
            el = {"name": b["name"], "box_uv": False, "rescale": False, "locked": False, "render_order": "default",
                  "from": [-(ox + sx), oy, oz], "to": [-ox, oy + sy, oz + sz], "autouv": 0, "color": 0,
                  "origin": [-c["pivot"][0], c["pivot"][1], c["pivot"][2]] if "pivot" in c else [-px, py, pz],
                  "faces": {}, "type": "cube", "uuid": str(uuid.uuid4())}
            if "rotation" in c:
                r = c["rotation"]
                el["rotation"] = [-r[0], -r[1], r[2]]
            for fname, fuv in c["uv"].items():
                (u, v), (du, dv) = fuv["uv"], fuv["uv_size"]
                el["faces"][fname] = {"uv": [u, v, u + du, v + dv], "texture": 0}
            elements.append(el)
            grp["children"].append(el["uuid"])
    outliner = []
    for b in g["bones"]:
        grp = groups[b["name"]]
        if b.get("parent"):
            groups[b["parent"]]["children"].append(grp)
        else:
            outliner.append(grp)
    data = base64.b64encode(open(tex_path, "rb").read()).decode()
    proj = {"meta": {"format_version": "4.10", "model_format": "bedrock", "box_uv": False},
            "name": "caballo_nether", "model_identifier": "caballo_nether", "visible_box": [4, 4, 1.5],
            "resolution": {"width": 64, "height": 64}, "elements": elements, "outliner": outliner,
            "textures": [{"path": "", "name": "caballo_nether.png", "folder": "", "namespace": "", "id": "0",
                          "width": 64, "height": 64, "uv_width": 64, "uv_height": 64, "particle": False,
                          "render_mode": "default", "visible": True, "internal": True, "saved": True,
                          "uuid": str(uuid.uuid4()), "source": "data:image/png;base64," + data}]}
    json.dump(proj, open(out_path, "w"))
