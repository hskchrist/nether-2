"""Convierte el modelo "Void Dragon" (Blockbench exportado a glTF; autor RedVoid_, licencia CC BY 4.0,
https://sketchfab.com/3d-models/void-dragon-not-animated-b25da6a39fcd4d29962cd2444fad608a) a GeckoLib.

El glTF de Blockbench guarda el modelo en el mismo espacio que Minecraft (en bloques). GeckoLib lee el
formato Bedrock, que tiene el eje X invertido y los giros X/Y con signo cambiado; aquí se hace esa conversión,
cubo por cubo, con UV por cara.
"""
import io
import json
import math
import os
import struct
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GLB = os.path.join(HERE, "ref", "void_dragon.glb")
CREDIT = "Void Dragon por RedVoid_ (CC BY 4.0) - sketchfab.com/RedVoid_"


def load(path=None):
    b = open(path or GLB, "rb").read()
    L = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + L])
    off = 20 + L
    blen = struct.unpack("<I", b[off:off + 4])[0]
    binc = b[off + 8: off + 8 + blen]
    return j, binc


def accessor(j, binc, idx):
    a = j["accessors"][idx]
    bv = j["bufferViews"][a["bufferView"]]
    comp = {5126: ("f", 4), 5123: ("H", 2), 5125: ("I", 4), 5121: ("B", 1)}[a["componentType"]]
    n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
    start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", comp[1] * n)
    out = []
    for k in range(a["count"]):
        p = start + k * stride
        out.append(struct.unpack("<" + comp[0] * n, binc[p:p + comp[1] * n]))
    return np.array(out)


def quat_mat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def local(n):
    """(T, R) del nodo."""
    if "matrix" in n:
        m = np.array(n["matrix"]).reshape(4, 4).T
        return m[:3, 3].copy(), m[:3, :3].copy()
    T = np.array(n.get("translation", [0, 0, 0]), dtype=float)
    R = quat_mat(n["rotation"]) if "rotation" in n else np.eye(3)
    return T, R


def euler_zyx(R):
    """R = Rz(a) Ry(b) Rx(c) -> (a, b, c) en grados."""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    if abs(math.cos(b)) > 1e-6:
        a = math.atan2(R[1, 0], R[0, 0])
        c = math.atan2(R[2, 1], R[2, 2])
    else:
        a = math.atan2(-R[0, 1], R[1, 1])
        c = 0.0
    return [math.degrees(v) for v in (a, b, c)]


def bedrock_rot(R):
    a, b, c = euler_zyx(R)
    r = [-c, -b, a]
    return None if all(abs(v) < 1e-4 for v in r) else [round(v, 4) for v in r]


def clean(name):
    base = name.rsplit("_", 1)
    return base[0] if len(base) == 2 and base[1].isdigit() else name


# vértices de cada cara de GeckoLib (espacio Minecraft) y el UV que recibe cada uno
def gl_quads(x0, y0, z0, x1, y1, z1):
    blb, brb, tlb, trb = (x0, y0, z0), (x0, y0, z1), (x0, y1, z0), (x0, y1, z1)
    tlf, trf, blf, brf = (x1, y1, z0), (x1, y1, z1), (x1, y0, z0), (x1, y0, z1)
    return {
        "west": [trb, tlb, blb, brb], "east": [tlf, trf, brf, blf], "north": [tlb, tlf, blf, blb],
        "south": [trf, trb, brb, brf], "up": [trb, trf, tlf, tlb], "down": [blb, blf, brf, brb]}


def pose_overrides(j, binc, k):
    """Pose estática k guardada en el glTF: {indice_nodo: {"rotation": q, "translation": t}}."""
    a = j["animations"][k]
    out = {}
    for ch in a["channels"]:
        smp = a["samplers"][ch["sampler"]]
        val = accessor(j, binc, smp["output"])[0]
        out.setdefault(ch["target"]["node"], {})[ch["target"]["path"]] = list(val)
    return out


def convert(pose=None, path=None, root_prefix="root_"):
    j, binc = load(path)
    nodes = [dict(n) for n in j["nodes"]]
    if pose is not None:
        for idx, ov in pose_overrides(j, binc, pose).items():
            nodes[idx].pop("matrix", None) if ("rotation" in ov) else None
            if "matrix" in j["nodes"][idx] and "rotation" in ov:
                m = np.array(j["nodes"][idx]["matrix"]).reshape(4, 4).T
                nodes[idx]["translation"] = list(m[:3, 3])
            nodes[idx].update(ov)
    img = j["images"]
    tex_imgs = []
    for im in img:
        bv = j["bufferViews"][im["bufferView"]]
        data = binc[bv.get("byteOffset", 0): bv.get("byteOffset", 0) + bv["byteLength"]]
        tex_imgs.append(Image.open(io.BytesIO(data)).convert("RGBA"))
    TW, TH = tex_imgs[0].size
    root = next((i for i, n in enumerate(nodes) if n.get("name", "").startswith(root_prefix)), None)
    if root is None:
        root = next(i for i, n in enumerate(nodes) if n.get("name", "").startswith("_"))
    bones, order, names = {}, [], set()
    node_bone = {}
    stats = {"cubes": 0, "uv_mismatch": 0}

    def uniq(nm):
        k, base = 1, nm
        while nm in names:
            k += 1
            nm = "%s_%d" % (base, k)
        names.add(nm)
        return nm

    def walk(idx, parent_name, origin):
        n = nodes[idx]
        T, R = local(n)
        nm = n.get("name", "")
        if nm.startswith("cube_"):
            # cubo: la malla está en el nodo hijo
            for c in n.get("children", []):
                cn = nodes[c]
                if "mesh" not in cn:
                    continue
                T2, R2 = local(cn)
                for prim in j["meshes"][cn["mesh"]]["primitives"]:
                    P = accessor(j, binc, prim["attributes"]["POSITION"])
                    UV = accessor(j, binc, prim["attributes"]["TEXCOORD_0"])
                    NR = accessor(j, binc, prim["attributes"]["NORMAL"])
                    P = (R2 @ P.T).T + T2
                    NR = (R2 @ NR.T).T
                    add_cube(parent_name, origin, T, R, P, UV, NR)
            return
        bname = uniq(clean(nm))
        node_bone[idx] = bname
        piv = origin + T
        bones[bname] = {"name": bname, "pivot": [round(-piv[0] * 16, 4), round(piv[1] * 16, 4), round(piv[2] * 16, 4)]}
        if parent_name:
            bones[bname]["parent"] = parent_name
        r = bedrock_rot(R)
        if r:
            bones[bname]["rotation"] = r
        bones[bname]["cubes"] = []
        order.append(bname)
        for c in n.get("children", []):
            walk(c, bname, piv)

    def add_cube(bone, origin, T, R, P, UV, NR):
        stats["cubes"] += 1
        mn, mx = P.min(axis=0), P.max(axis=0)
        x0, y0, z0 = mn
        x1, y1, z1 = mx
        cube = {"origin": [round(-(origin[0] + T[0] + x1) * 16, 4), round((origin[1] + T[1] + y0) * 16, 4),
                           round((origin[2] + T[2] + z0) * 16, 4)],
                "size": [round((x1 - x0) * 16, 4), round((y1 - y0) * 16, 4), round((z1 - z0) * 16, 4)]}
        r = bedrock_rot(R)
        if r:
            cube["rotation"] = r
            pv = origin + T
            cube["pivot"] = [round(-pv[0] * 16, 4), round(pv[1] * 16, 4), round(pv[2] * 16, 4)]
        quads = gl_quads(x0, y0, z0, x1, y1, z1)
        faces = {}
        for face, corners in quads.items():
            uvs = []
            for cpos in corners:
                d = np.abs(P - np.array(cpos)).sum(axis=1)
                # entre los vértices en esa esquina, el que pertenece a la cara correcta
                cand = np.where(d < 1e-4)[0]
                ndir = np.array({"west": [-1, 0, 0], "east": [1, 0, 0], "north": [0, 0, -1], "south": [0, 0, 1],
                                 "up": [0, 1, 0], "down": [0, -1, 0]}[face], dtype=float)
                pick = None
                best = -2
                for ci in cand:
                    dot = float(np.dot(NR[ci], ndir))
                    if dot > best:
                        best, pick = dot, ci
                if pick is None or best < 0.5:
                    uvs = None
                    break
                uvs.append(UV[pick] * [TW, TH])
            if uvs is None:
                continue
            U1, V0 = uvs[0]
            U0, _ = uvs[1]
            _, V1 = uvs[2]
            chk = uvs[3]
            if abs(chk[0] - U1) > 0.01 or abs(chk[1] - V1) > 0.01:
                stats["uv_mismatch"] += 1
            if abs(U1 - U0) < 1e-6 and abs(V1 - V0) < 1e-6:
                continue
            faces[face] = {"uv": [round(U0, 4), round(V0, 4)], "uv_size": [round(U1 - U0, 4), round(V1 - V0, 4)]}
        cube["uv"] = faces
        bones[bone]["cubes"].append(cube)

    bones["root"] = {"name": "root", "pivot": [0, 0, 0], "cubes": []}
    order.append("root")
    node_bone[root] = "root"
    for c in nodes[root].get("children", []):
        walk(c, "root", np.zeros(3))
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry.void_dragon", "texture_width": TW, "texture_height": TH,
                        "visible_bounds_width": 12, "visible_bounds_height": 8, "visible_bounds_offset": [0, 2, 0]},
        "bones": [dict(bones[b]) for b in order]}]}
    for b in geo["minecraft:geometry"][0]["bones"]:
        if not b["cubes"]:
            del b["cubes"]
    geo["node_bone"] = node_bone
    return geo, tex_imgs, stats


def pose_deltas(k):
    """Pose k del glTF convertida a valores de animación Bedrock (rotación y posición sumadas al reposo)."""
    j, binc = load()
    geo, _, _ = convert()
    nb = geo["node_bone"]
    out = {}
    for idx, ov in pose_overrides(j, binc, k).items():
        if idx not in nb:
            continue
        T0, R0 = local(j["nodes"][idx])
        ch = {}
        if "rotation" in ov:
            r0 = bedrock_rot(R0) or [0, 0, 0]
            r1 = bedrock_rot(quat_mat(ov["rotation"])) or [0, 0, 0]
            d = [r1[i] - r0[i] for i in range(3)]
            d = [((v + 180) % 360) - 180 for v in d]
            if any(abs(v) > 1e-3 for v in d):
                ch["rotation"] = [round(v, 3) for v in d]
        if "translation" in ov:
            dt = np.array(ov["translation"]) - T0
            if np.abs(dt).max() > 1e-5:
                ch["position"] = [round(-dt[0] * 16, 3), round(dt[1] * 16, 3), round(dt[2] * 16, 3)]
        if ch:
            out[nb[idx]] = ch
    return out


if __name__ == "__main__":
    geo, texs, st = convert()
    print(st, [t.size for t in texs])
    os.makedirs("/tmp/claude-0/vd", exist_ok=True)
    json.dump(geo, open("/tmp/claude-0/vd/vd.geo.json", "w"), indent=1)
    for k, t in enumerate(texs):
        t.save("/tmp/claude-0/vd/tex%d.png" % k)
    print([b["name"] for b in geo["minecraft:geometry"][0]["bones"]])


# ====================================================================== ANIMACIONES PROPIAS
from models import anim  # noqa: E402

A = "animation.nether_dragon."
WR = ("bone70", "bone52", "bone68", "bone69")          # ala derecha: hombro, brazo, antebrazo, mano
WL = ("bone71", "bone72", "bone73", "bone74")          # ala izquierda (en el modelo está girada 180° en Z)
FR = ("bone53", "bone58", "bone63")                   # dedos del ala derecha
FL = ("bone75", "bone80", "bone85")
TAIL = ["bone%d" % k for k in range(24, 36)]
LEG_FL = ("bone13", "bone17", "bone48")               # delantera izquierda (hombro, codo, mano)
LEG_FR = ("bone18", "bone19", "bone44")
LEG_BL = ("bone12", "bone14", "bone15", "bone16")      # trasera izquierda
LEG_BR = ("bone20", "bone21", "bone22", "bone23")

FOLD = [[0, 0, 12], [0, -20, 0], [0, -155, 0], [0, 155, 0]]   # alas plegadas sobre el lomo
# alas abiertas para volar (sacadas de la pose de vuelo del modelo)
OPEN = [[-45, 10, 80], [0, 50, -40], [-25, -95, 0], [0, -27.5, 0]]
FINGERS_OPEN = [22.5, 65, 107.5]
OPEN_GROUND = [[0, 0, 35], [0, -20, 0], [-30, -60, 0], [0, -20, 0]]   # alas desplegadas de pie (rugido)
FINGERS_GROUND = [15, 57.5, 100]


def wings(frames):
    """frames: {t: (4 rotaciones del ala derecha, 3 ángulos de dedos o None)} -> ambas alas."""
    out = {}
    for t, (vals, fing) in frames.items():
        for side, names, fnames in (("R", WR, FR), ("L", WL, FL)):
            for nm, v in zip(names, vals):
                # el ala izquierda es el reflejo: X y Z cambian de signo (así vienen las poses del modelo)
                out.setdefault(nm, {"rotation": {}})["rotation"][t] = [v[0], v[1], v[2]] if side == "R" else [-v[0], v[1], -v[2]]
            if fing is not None:
                for nm, a in zip(fnames, fing):
                    out.setdefault(nm, {"rotation": {}})["rotation"][t] = [0, a, 0]
    return out


def add(v, d):
    return [v[i] + d[i] for i in range(3)]


def tail_wave(L, amp, phase=0.35, yaw=True, base=None, steps=4):
    out = {}
    for k, b in enumerate(TAIL):
        fr = {}
        for s in range(steps + 1):
            t = L * s / steps
            a = amp * (0.4 + 0.6 * k / len(TAIL)) * math.sin(2 * math.pi * (s / steps) - k * phase)
            v = [0, a, 0] if yaw else [a, 0, 0]
            if base:
                v = add(v, base[k] if isinstance(base, list) else base)
            fr[round(t, 3)] = v
        out[b] = {"rotation": fr}
    return out


def merge(*ds):
    out = {}
    for d in ds:
        for b, ch in d.items():
            out.setdefault(b, {}).update(ch)
    return out


def animations():
    a = {}
    # ---------------- en tierra (alas plegadas)
    a[A + "idle"] = anim(4.0, True, merge(
        wings({0: (FOLD, None), 2.0: ([add(FOLD[0], [0, 0, 3])] + FOLD[1:], None), 4.0: (FOLD, None)}),
        tail_wave(4.0, 5),
        {"body": {"position": {0: [0, 0, 0], 2.0: [0, 0.8, 0], 4.0: [0, 0, 0]}},
         "neck": {"rotation": {0: [0, 0, 0], 1.0: [-3, 6, 0], 2.0: [0, 0, 0], 3.0: [-2, -6, 0], 4.0: [0, 0, 0]}},
         "head": {"rotation": {0: [0, 0, 0], 1.0: [4, -6, 0], 2.0: [0, 0, 0], 3.0: [3, 6, 0], 4.0: [0, 0, 0]}},
         "jaw": {"rotation": {0: [0, 0, 0], 3.2: [0, 0, 0], 3.5: [12, 0, 0], 3.8: [0, 0, 0], 4.0: [0, 0, 0]}}}))

    def gait(L, amp):
        h = L / 2
        g = {}
        for names, sign in ((LEG_FL, 1), (LEG_FR, -1), (LEG_BL, -1), (LEG_BR, 1)):
            g[names[0]] = {"rotation": {0: [amp * sign, 0, 0], h: [-amp * sign, 0, 0], L: [amp * sign, 0, 0]}}
            knee = names[1]
            lift = (L / 4) if sign > 0 else (3 * L / 4)
            g[knee] = {"rotation": {0: [0, 0, 0], round(lift, 3): [-amp * 0.9, 0, 0], h: [0, 0, 0], L: [0, 0, 0]} if sign > 0 else
                       {0: [0, 0, 0], h: [0, 0, 0], round(lift, 3): [-amp * 0.9, 0, 0], L: [0, 0, 0]}}
        g["body"] = {"position": {0: [0, 0, 0], L / 4: [0, 1.2, 0], h: [0, 0, 0], 3 * L / 4: [0, 1.2, 0], L: [0, 0, 0]},
                     "rotation": {0: [0, 2, 1], h: [0, -2, -1], L: [0, 2, 1]}}
        g["neck"] = {"rotation": {0: [3, 0, 0], L / 4: [-3, 0, 0], h: [3, 0, 0], 3 * L / 4: [-3, 0, 0], L: [3, 0, 0]}}
        return g
    a[A + "walk"] = anim(1.6, True, merge(wings({0: (FOLD, None), 1.6: (FOLD, None)}), tail_wave(1.6, 7), gait(1.6, 18)))
    run_w = wings({0: (FOLD, None), 0.4: ([add(FOLD[0], [0, 0, 18])] + FOLD[1:], None), 0.8: (FOLD, None)})
    a[A + "run"] = anim(0.8, True, merge(run_w, tail_wave(0.8, 9), gait(0.8, 28)))
    # descansando: se echa, cabeza al suelo y cola enroscada
    rest = {"root": {"position": {0: [0, -24, 0], 3.0: [0, -23.4, 0], 6.0: [0, -24, 0]}}}
    for names in (LEG_FL, LEG_FR):
        rest[names[0]] = {"rotation": {0: [20, 0, 0], 6.0: [20, 0, 0]}}
        rest[names[1]] = {"rotation": {0: [-60, 0, 0], 6.0: [-60, 0, 0]}}
    for names in (LEG_BL, LEG_BR):
        rest[names[0]] = {"rotation": {0: [-52, 0, 0], 6.0: [-52, 0, 0]}}
        rest[names[1]] = {"rotation": {0: [-20, 0, 0], 6.0: [-20, 0, 0]}}
    rest["neck"] = {"rotation": {0: [30, -25, 0], 6.0: [30, -25, 0]}}
    rest["neck2"] = {"rotation": {0: [10, -20, 0], 6.0: [10, -20, 0]}}
    rest["head"] = {"rotation": {0: [-10, -10, 0], 3.0: [-8, -10, 0], 6.0: [-10, -10, 0]}}
    curl = [[0, -12, 0]] * len(TAIL)
    a[A + "rest"] = anim(6.0, True, merge(wings({0: (FOLD, None), 6.0: (FOLD, None)}), tail_wave(6.0, 3, base=curl), rest))
    # ---------------- en el aire
    flap = lambda dz: [add(OPEN[0], [0, 0, dz])] + OPEN[1:]
    fly_w = wings({0: (flap(-30), FINGERS_OPEN), 0.3: (flap(0), FINGERS_OPEN), 0.6: (flap(32), FINGERS_OPEN),
                   0.9: (flap(0), FINGERS_OPEN), 1.2: (flap(-30), FINGERS_OPEN)})
    fly_body = {"root": {"position": {0: [0, -2, 0], 0.6: [0, 2, 0], 1.2: [0, -2, 0]}},
                "neck": {"rotation": {0: [12, 0, 0], 1.2: [12, 0, 0]}},
                "head": {"rotation": {0: [-10, 0, 0], 1.2: [-10, 0, 0]}}}
    for names in (LEG_FL, LEG_FR):
        fly_body[names[0]] = {"rotation": {0: [45, 0, 0], 1.2: [45, 0, 0]}}
        fly_body[names[1]] = {"rotation": {0: [40, 0, 0], 1.2: [40, 0, 0]}}
    for names in (LEG_BL, LEG_BR):
        fly_body[names[0]] = {"rotation": {0: [62.5, 0, -10 if names is LEG_BL else 10], 1.2: [62.5, 0, -10 if names is LEG_BL else 10]}}
    a[A + "fly"] = anim(1.2, True, merge(fly_w, tail_wave(1.2, 6, yaw=False), fly_body))
    glide_w = wings({0: (flap(-6), FINGERS_OPEN), 1.5: (flap(-2), FINGERS_OPEN), 3.0: (flap(-6), FINGERS_OPEN)})
    glide_body = {k: v for k, v in fly_body.items() if k != "root"}
    glide_body["root"] = {"rotation": {0: [0, 0, -4], 1.5: [0, 0, 4], 3.0: [0, 0, -4]}}
    a[A + "glide"] = anim(3.0, True, merge(glide_w, tail_wave(3.0, 4, yaw=False), glide_body))
    hover_w = wings({0: (flap(-36), FINGERS_OPEN), 0.4: (flap(30), FINGERS_OPEN), 0.8: (flap(-36), FINGERS_OPEN)})
    hover_body = dict(glide_body)
    hover_body["root"] = {"rotation": {0: [-30, 0, 0], 0.8: [-30, 0, 0]},
                          "position": {0: [0, 1.5, 0], 0.4: [0, -1.5, 0], 0.8: [0, 1.5, 0]}}
    hover_body["neck"] = {"rotation": {0: [25, 0, 0], 0.8: [25, 0, 0]}}
    a[A + "hover"] = anim(0.8, True, merge(hover_w, tail_wave(0.8, 6, yaw=False), hover_body))
    a[A + "takeoff"] = anim(1.0, False, merge(
        wings({0: (FOLD, [0, 0, 0]), 0.3: (OPEN_GROUND, FINGERS_GROUND), 0.6: (flap(30), FINGERS_OPEN), 1.0: (flap(-20), FINGERS_OPEN)}),
        {"root": {"position": {0: [0, 0, 0], 0.3: [0, -6, 0], 0.6: [0, 10, 0], 1.0: [0, 6, 0]},
                  "rotation": {0: [0, 0, 0], 0.3: [6, 0, 0], 0.6: [-20, 0, 0], 1.0: [-6, 0, 0]}}}))
    # ---------------- acciones (encima del movimiento)
    a[A + "breath"] = anim(1.6, False, {
        "neck": {"rotation": {0: [0, 0, 0], 0.25: [-12, 0, 0], 0.45: [14, 0, 0], 1.3: [14, 0, 0], 1.6: [0, 0, 0]}},
        "neck2": {"rotation": {0: [0, 0, 0], 0.45: [8, 0, 0], 1.3: [8, 0, 0], 1.6: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.25: [-14, 0, 0], 0.45: [-6, 0, 0], 0.9: [-8, 4, 0], 1.3: [-6, -4, 0], 1.6: [0, 0, 0]}},
        "jaw": {"rotation": {0: [0, 0, 0], 0.25: [15, 0, 0], 0.45: [55, 0, 0], 1.3: [55, 0, 0], 1.6: [0, 0, 0]}},
    })
    a[A + "bite"] = anim(0.6, False, {
        "neck": {"rotation": {0: [0, 0, 0], 0.15: [-10, 0, 0], 0.3: [20, 0, 0], 0.6: [0, 0, 0]}},
        "head": {"rotation": {0: [0, 0, 0], 0.15: [-12, 0, 0], 0.3: [6, 0, 0], 0.6: [0, 0, 0]}},
        "jaw": {"rotation": {0: [0, 0, 0], 0.15: [50, 0, 0], 0.3: [0, 0, 0], 0.6: [0, 0, 0]}},
    })
    a[A + "roar"] = anim(2.2, False, merge(
        wings({0: (FOLD, [0, 0, 0]), 0.5: (OPEN_GROUND, FINGERS_GROUND), 1.7: (OPEN_GROUND, FINGERS_GROUND), 2.2: (FOLD, [0, 0, 0])}),
        {"body": {"rotation": {0: [0, 0, 0], 0.5: [-25, 0, 0], 1.7: [-25, 0, 0], 2.2: [0, 0, 0]}},
         "neck": {"rotation": {0: [0, 0, 0], 0.5: [17.5, 0, 0], 1.7: [17.5, 0, 0], 2.2: [0, 0, 0]}},
         "neck3": {"rotation": {0: [0, 0, 0], 0.5: [17.5, 0, 0], 1.7: [17.5, 0, 0], 2.2: [0, 0, 0]}},
         "head": {"rotation": {0: [0, 0, 0], 0.6: [-10, 6, 0], 1.2: [-10, -6, 0], 1.7: [-5, 0, 0], 2.2: [0, 0, 0]}},
         "jaw": {"rotation": {0: [0, 0, 0], 0.5: [60, 0, 0], 1.7: [60, 0, 0], 2.2: [0, 0, 0]}}}))
    return a


# ====================================================================== MONTURA Y TEXTURA
def build_all():
    """Geo final (con montura), textura (con la zona de la montura añadida debajo) y máscara de brillo."""
    import dragon
    from textures import Sheet
    geo, texs, st = convert()
    geo.pop("node_bone", None)
    g = geo["minecraft:geometry"][0]
    TW, TH = texs[0].size
    EXTRA = 128
    tex = Image.new("RGBA", (TW, TH + EXTRA), (0, 0, 0, 0))
    tex.paste(texs[0], (0, 0))
    glow_src = np.array(texs[2].convert("RGB")).astype(int)
    base = np.array(texs[0])
    mask = glow_src.max(axis=2) > 40
    glow = np.zeros((TH + EXTRA, TW, 4), dtype=np.uint8)
    glow[:TH][mask] = base[mask]
    g["description"]["texture_height"] = TH + EXTRA
    # montura con UV de caja en la zona nueva
    from common import Packer
    pk = Packer([(0, TH, 256, TH + EXTRA)])
    sheet = Sheet(TW, TH + EXTRA)
    sheet.img = tex
    saddle = {"name": "saddle", "parent": "body2", "pivot": [0, 70, 4], "cubes": []}
    D = dragon

    def cube(origin, size, faces):
        uv = pk.alloc(*[max(1, math.floor(v)) for v in size])
        saddle["cubes"].append({"origin": origin, "size": size, "uv": uv})
        D.paint_box(sheet, uv[0], uv[1], size, faces)
        return uv

    def pair(origin, size, faces):
        uv = cube(origin, size, faces)
        saddle["cubes"].append({"origin": [-(origin[0] + size[0]), origin[1], origin[2]], "size": size, "uv": uv})
    C = D.CLEAR
    cube([-10.5, 60, -6], [21, 10.5, 18], {"all": D.blanket_side, "top": D.blanket_top, "bottom": C, "front": C, "back": C})
    cube([-5.5, 70.5, -4], [11, 1.6, 13], {"all": D.leather, "top": D.seat_top})
    cube([-4.5, 72.1, -2.5], [9, 1.4, 9], {"all": D.fill("r", "R", 0.4), "top": D.cushion})
    cube([-1.5, 72.1, -5.6], [3, 4, 2.2], {"all": D.leather, "front": D.pommel_front})
    cube([-1.8, 76.1, -5.9], [3.6, 1, 2.8], {"all": D.gold})
    cube([-5, 72.1, 7.4], [10, 4, 2.2], {"all": D.leather, "top": D.gold, "back": D.cantle_back})
    cube([-10.8, 46, 2], [21.6, 25, 2.2], {"all": D.strap, "top": C, "front": C, "back": C})
    pair([10.6, 57.5, -1], [0.6, 10, 1.2], {"all": D.fill("K", "k", 0.3)})
    pair([10.3, 56, -2], [1.4, 1.6, 3.2], {"all": D.gold, "top": C})
    pair([10.5, 61, 3], [3, 6, 7], {"all": D.saddlebag, "top": D.fill("k")})
    cube([-0.5, 72.1, 8.6], [1, 14, 1], {"all": D.fill("g", "G", 0.3)})
    cube([-0.75, 86.1, 8.35], [1.5, 1.5, 1.5], {"all": D.fill("U", "u", 0.3)})
    cube([-0.05, 78, 9.6], [0.1, 8, 9], {"all": D.banner})
    g["bones"].append(saddle)
    tex = sheet.img
    return geo, tex, Image.fromarray(glow, "RGBA")


def write_all():
    from common import ASSETS, save_json
    geo, tex, glow = build_all()
    save_json(os.path.join(ASSETS, "geo", "entity", "nether_dragon.geo.json"), geo)
    save_json(os.path.join(ASSETS, "animations", "entity", "nether_dragon.animation.json"),
              {"format_version": "1.8.0", "animations": animations()})
    tex.save(os.path.join(ASSETS, "textures", "entity", "nether_dragon.png"))
    glow.save(os.path.join(ASSETS, "textures", "entity", "nether_dragon_glowmask.png"))
    return geo, tex


# ====================================================================== FASES DE CRECIMIENTO
# escala del cuerpo (sobre la escala del adulto en el juego), cabeza, alas, cola, cuello y patas
STAGES = [
    dict(name="Recién nacido", grow=0.00, scale=0.24, head=1.70, wings=0.45, tail=0.60, neck=0.70, legs=0.80),
    dict(name="Cría", grow=0.15, scale=0.38, head=1.45, wings=0.62, tail=0.72, neck=0.80, legs=0.85),
    dict(name="Joven", grow=0.40, scale=0.58, head=1.22, wings=0.80, tail=0.85, neck=0.90, legs=0.92),
    dict(name="Subadulto", grow=0.70, scale=0.80, head=1.08, wings=0.93, tail=0.95, neck=1.0, legs=0.97),
    dict(name="Adulto", grow=1.00, scale=1.00, head=1.00, wings=1.00, tail=1.00, neck=1.00, legs=1.00),
]
ADULT_SCALE = 0.42      # el modelo original mide ~24 bloques; en el juego el adulto queda en ~10 bloques de largo
LEG_ROOTS = ["bone13", "bone18", "bone12", "bone20"]


def stage_for(growth):
    st = STAGES[0]
    for x in STAGES:
        if growth >= x["grow"]:
            st = x
    return st


def stage_pose(st, pose=None):
    p = {k: {c: list(v2) for c, v2 in v.items()} for k, v in (pose or {}).items()}
    for b, v in [("head", st["head"]), ("bone70", st["wings"]), ("bone71", st["wings"]), ("bone24", st["tail"]),
                 ("neck", st["neck"])] + [(b, st["legs"]) for b in LEG_ROOTS]:
        p.setdefault(b, {})["scale"] = [v, v, v]
    drop = 58 * (1 - st["legs"])
    r = p.setdefault("root", {})
    pos = r.get("position", [0, 0, 0])
    r["position"] = [pos[0], pos[1] - drop, pos[2]]
    return p, st["scale"]
