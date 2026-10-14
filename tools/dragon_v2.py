"""Dragón del Nether v2: el Void Dragon aprobado con cuerpo más grande, la cabeza de "Dragon Head"
(Joshie Models BB, CC BY 4.0) y alas más gruesas (mismo diseño), con la unión de las alas proporcional.

Créditos de los modelos base (CC BY 4.0):
  - Void Dragon por RedVoid_  (sketchfab.com/RedVoid_)
  - Dragon Head por Joshie Models BB  (sketchfab.com/kats43434)
"""
import copy
import json
import math
import os
import numpy as np
from PIL import Image
import void_dragon as vd

HERE = os.path.dirname(os.path.abspath(__file__))
HEAD_GLB = os.path.join(HERE, "ref", "dragon_head.glb")
CREDITS = ["Void Dragon por RedVoid_ (CC BY 4.0)", "Dragon Head por Joshie Models BB (CC BY 4.0)"]

BODY_SCALE = (1.32, 1.30, 1.15)     # torso más grande (ancho, alto, largo)
BODY_LIFT = 3.5                      # el lomo sube al crecer el torso
WING_SHIFT = 6.0                     # la unión de las alas se abre con el torso
WING_THICK = 1.7                     # grosor de los huesos del ala (el largo y la membrana no cambian)
SHOULDER_SCALE = 1.6                 # pieza que une el ala al cuerpo
LEG_THICK = 1.2
HEAD_SCALE = 1.9


def children_map(bones):
    kids = {}
    for b in bones:
        kids.setdefault(b.get("parent"), []).append(b["name"])
    return kids


def descendants(kids, n):
    out = [n]
    for c in kids.get(n, []):
        out += descendants(kids, c)
    return out


def scale_cube(c, s):
    """Escala un cubo alrededor de su centro (sin rotar). s = (sx, sy, sz)."""
    o = np.array(c["origin"], dtype=float)
    z = np.array(c["size"], dtype=float)
    ctr = o + z / 2
    z2 = z * np.array(s)
    c["origin"] = [round(v, 4) for v in (ctr - z2 / 2)]
    c["size"] = [round(v, 4) for v in z2]


def thicken(c, k):
    """Engrosa los dos ejes menores de un cubo (no toca planos de membrana ni el largo)."""
    z = np.array(c["size"], dtype=float)
    if z.min() < 0.05:
        return
    order = np.argsort(z)
    s = [1.0, 1.0, 1.0]
    s[order[0]] = k
    s[order[1]] = k
    scale_cube(c, s)


def recolor_head(img):
    """Pasa la cabeza (marrón/dorado) a la paleta del dragón: escamas negras y detalles rojos brillantes."""
    a = np.array(img.convert("RGBA")).astype(float)
    rgb = a[..., :3]
    lum = 0.3 * rgb[..., 0] + 0.59 * rgb[..., 1] + 0.11 * rgb[..., 2]
    warm = (rgb[..., 0] - rgb[..., 2]) > 40          # dorados / naranjas -> rojo de brasa
    green = (rgb[..., 1] > rgb[..., 0] + 10) & (rgb[..., 1] > 90)
    out = np.zeros_like(rgb)
    base = np.clip(lum * 0.42, 6, 70)
    out[..., 0] = base * 1.05
    out[..., 1] = base * 0.92
    out[..., 2] = base * 1.0
    hot = warm & (lum > 95)
    out[hot] = np.stack([np.clip(lum[hot] * 1.6, 150, 255), lum[hot] * 0.12, lum[hot] * 0.12], -1)
    mid = warm & ~hot
    out[mid] = np.stack([lum[mid] * 0.9, lum[mid] * 0.18, lum[mid] * 0.2], -1)
    out[green] = np.stack([np.full(green.sum(), 255.0), np.full(green.sum(), 60.0), np.full(green.sum(), 40.0)], -1)
    a[..., :3] = np.clip(out, 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def build(recolor=True):
    geo, tex, glow = vd.build_all()
    g = geo["minecraft:geometry"][0]
    bones = g["bones"]
    B = {b["name"]: b for b in bones}
    kids = children_map(bones)

    # ---------------- 1) torso más grande
    for n in ("body", "body2", "body3"):
        for c in B[n].get("cubes", []):
            scale_cube(c, BODY_SCALE)
    for n in ("spikes_b", "spikes_b2", "spikes_b3"):
        b = B[n]
        b["pivot"][1] += BODY_LIFT
        for c in b.get("cubes", []):
            c["origin"][1] += BODY_LIFT
            if "pivot" in c:
                c["pivot"][1] += BODY_LIFT
    for c in B["saddle"]["cubes"]:
        c["origin"][1] += BODY_LIFT
        # la manta y la cincha se ensanchan con el cuerpo
        if c["size"][0] > 15:
            w = c["size"][0] * BODY_SCALE[0]
            c["origin"][0] = -w / 2
            c["size"][0] = w
        elif abs(c["origin"][0]) > 9:                 # estribos y alforjas: hacia afuera
            c["origin"][0] += (1 if c["origin"][0] > 0 else -1) * 3.4
    B["saddle"]["pivot"][1] += BODY_LIFT

    # ---------------- 2) alas: unión proporcional y huesos más gruesos (mismo diseño)
    for root, sgn in (("bone70", -1), ("bone71", 1)):
        B[root]["pivot"][0] += sgn * WING_SHIFT
        B[root]["pivot"][1] += BODY_LIFT
        shift = np.array([sgn * WING_SHIFT, BODY_LIFT, 0.0])
        for n in descendants(kids, root):
            b = B[n]
            if n != root:
                pass
            for c in b.get("cubes", []):
                if n == root:
                    thicken(c, SHOULDER_SCALE)
                else:
                    thicken(c, WING_THICK)
        # el ala izquierda vive en su propio marco (girado 180°): sus hijos no se mueven, solo el pivote raíz
    # las piezas del ala derecha están en coordenadas del modelo: hay que desplazarlas junto con el pivote
    for n in descendants(kids, "bone70"):
        b = B[n]
        if n != "bone70":
            b["pivot"][0] -= WING_SHIFT
            b["pivot"][1] += BODY_LIFT
        for c in b.get("cubes", []):
            c["origin"][0] -= WING_SHIFT
            c["origin"][1] += BODY_LIFT
            if "pivot" in c:
                c["pivot"][0] -= WING_SHIFT
                c["pivot"][1] += BODY_LIFT
    for n in descendants(kids, "bone71"):
        b = B[n]
        if n != "bone71":
            b["pivot"][0] += WING_SHIFT
            b["pivot"][1] += BODY_LIFT
        for c in b.get("cubes", []):
            c["origin"][0] += WING_SHIFT
            c["origin"][1] += BODY_LIFT
            if "pivot" in c:
                c["pivot"][0] += WING_SHIFT
                c["pivot"][1] += BODY_LIFT

    # ---------------- 3) patas algo más gruesas
    for root in ("bone13", "bone18", "bone12", "bone20"):
        for n in descendants(kids, root):
            for c in B[n].get("cubes", []):
                z = c["size"]
                if min(z) > 0.05 and max(z) > 6:
                    thicken(c, LEG_THICK)

    # ---------------- 4) cabeza nueva
    old = [n for n in descendants(kids, "head") if n != "head"]
    B["head"]["cubes"] = []
    keep = [b for b in bones if b["name"] not in old or b["name"] == "ray"]
    B["ray"]["cubes"] = []
    hgeo, htexs, _ = vd.convert(path=HEAD_GLB)
    hg = hgeo["minecraft:geometry"][0]
    htex = htexs[0]
    used = (0, 528, 494, 1024)                          # zona usada de la textura de la cabeza
    crop = htex.crop(used)
    if recolor:
        crop = recolor_head(crop)
    TW, TH = tex.size
    new_tex = Image.new("RGBA", (TW, TH + crop.size[1]), (0, 0, 0, 0))
    new_tex.paste(tex, (0, 0))
    new_tex.paste(crop, (0, TH))
    new_glow = Image.new("RGBA", new_tex.size, (0, 0, 0, 0))
    new_glow.paste(glow, (0, 0))
    ca = np.array(crop)
    gm = (ca[..., 0] > 140) & (ca[..., 1] < 90) & (ca[..., 3] > 0)
    gl = np.zeros_like(ca)
    gl[gm] = ca[gm]
    new_glow.paste(Image.fromarray(gl, "RGBA"), (0, TH))
    dv = TH - used[1]
    HB = {b["name"]: b for b in hg["bones"]}
    pts = []
    for b in hg["bones"]:
        for c in b.get("cubes", []):
            pts.append(c["origin"])
            pts.append(list(np.add(c["origin"], c["size"])))
    pts = np.array(pts)
    mn, mx = pts.min(0), pts.max(0)
    c_new = np.array([(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mx[2]])      # centro de la nuca
    c_tgt = np.array([0.0, 58.0, -92.0])
    k = HEAD_SCALE

    def tp(p):
        return [round(v, 4) for v in (k * (np.array(p, dtype=float) - c_new) + c_tgt)]

    def conv_cube(c):
        c = copy.deepcopy(c)
        c["origin"] = tp(c["origin"])
        c["size"] = [round(v * k, 4) for v in c["size"]]
        if "pivot" in c:
            c["pivot"] = tp(c["pivot"])
        for fc in c["uv"].values():
            fc["uv"] = [fc["uv"][0], fc["uv"][1] + dv]
        return c
    B["head"]["cubes"] = [conv_cube(c) for c in HB["a_head5"].get("cubes", [])]
    jaw = {"name": "jaw", "parent": "head", "pivot": tp(HB["jaw5"]["pivot"]),
           "cubes": [conv_cube(c) for c in HB["jaw5"].get("cubes", [])]}
    if "rotation" in HB["jaw5"]:
        jaw["rotation"] = HB["jaw5"]["rotation"]
    attach_head(B, jaw)
    out_bones = []
    for b in keep:
        out_bones.append(b)
        if b["name"] == "head":
            out_bones.append(jaw)
    g["bones"] = out_bones
    g["description"]["texture_height"] = new_tex.size[1]
    g["description"]["identifier"] = "geometry.nether_dragon"
    return geo, new_tex, new_glow


NECK_TIP = (0.0, 58.0, -97.0)   # punto en el cuello (más allá de su cara frontal) que entra en la nuca
SKULL_BACK = (0.0, 61.0, -106.0)  # parte trasera del cráneo nuevo (sin contar los cuernos)


def _rest_mat(B, n):
    from preview2 import rot_matrix
    b = B[n]
    R = rot_matrix(*b.get("rotation", [0, 0, 0]))
    p = np.array(b["pivot"], dtype=float)
    m = np.eye(4)
    m[:3, :3] = R
    m[:3, 3] = p - R @ p
    return _rest_mat(B, b["parent"]) @ m if b.get("parent") else m


def attach_head(B, jaw):
    """Desplaza la cabeza (y la mandíbula) para que el cráneo se apoye sobre el final del cuello."""
    target = _rest_mat(B, "neck3") @ np.r_[NECK_TIP, 1.0]
    local = np.linalg.inv(_rest_mat(B, "head")) @ target
    d = local[:3] - np.array(SKULL_BACK)
    for c in B["head"]["cubes"] + jaw["cubes"]:
        c["origin"] = [round(float(v), 4) for v in np.add(c["origin"], d)]
        if "pivot" in c:
            c["pivot"] = [round(float(v), 4) for v in np.add(c["pivot"], d)]
    jaw["pivot"] = [round(float(v), 4) for v in np.add(jaw["pivot"], d)]
    return d


def write_all():
    from common import ASSETS, save_json
    geo, tex, glow = build()
    save_json(os.path.join(ASSETS, "geo", "entity", "nether_dragon.geo.json"), geo)
    save_json(os.path.join(ASSETS, "animations", "entity", "nether_dragon.animation.json"),
              {"format_version": "1.8.0", "animations": vd.animations()})
    tex.save(os.path.join(ASSETS, "textures", "entity", "nether_dragon.png"))
    glow.save(os.path.join(ASSETS, "textures", "entity", "nether_dragon_glowmask.png"))
    # huevo (entidad 3D que se pone en el suelo + ícono del ítem)
    import dragon as eggs
    eg, etex = eggs.build_egg()
    save_json(os.path.join(ASSETS, "geo", "entity", "nether_dragon_egg.geo.json"), eg.to_json())
    save_json(os.path.join(ASSETS, "animations", "entity", "nether_dragon_egg.animation.json"),
              {"format_version": "1.8.0", "animations": eggs.egg_animations()})
    etex.save(os.path.join(ASSETS, "textures", "entity", "nether_dragon_egg.png"))
    eggs.glowmask(etex).save(os.path.join(ASSETS, "textures", "entity", "nether_dragon_egg_glowmask.png"))
    eggs.egg_icon().save(os.path.join(ASSETS, "textures", "item", "dragon_egg.png"))
    return geo, tex


# ====================================================================== EXPORTAR A BLOCKBENCH (.bbmodel)
def to_bbmodel(geo, tex, anims, name="dragon_del_nether"):
    """Proyecto de Blockbench (formato Bedrock, UV por cara) con textura incrustada y las animaciones."""
    import base64
    import io
    import uuid as U
    g = geo["minecraft:geometry"][0]
    buf = io.BytesIO()
    tex.save(buf, "PNG")
    elements, groups = [], {}
    outliner_children = {}
    order = []
    for b in g["bones"]:
        gid = str(U.uuid4())
        rot = b.get("rotation", [0, 0, 0])
        groups[b["name"]] = {"name": b["name"], "origin": [-b["pivot"][0], b["pivot"][1], b["pivot"][2]],
                             "rotation": [-rot[0], -rot[1], rot[2]], "uuid": gid, "export": True, "isOpen": False,
                             "visibility": True, "autouv": 0, "children": []}
        order.append(b["name"])
        for c in b.get("cubes", []):
            eid = str(U.uuid4())
            o, s = c["origin"], c["size"]
            frm = [-(o[0] + s[0]), o[1], o[2]]
            to = [-o[0], o[1] + s[1], o[2] + s[2]]
            el = {"name": "cube", "box_uv": False, "rescale": False, "locked": False, "render_order": "default",
                  "allow_mirror_modeling": True, "from": frm, "to": to, "autouv": 0, "color": 0,
                  "origin": [-c["pivot"][0], c["pivot"][1], c["pivot"][2]] if "pivot" in c else [-o[0], o[1], o[2]],
                  "faces": {}, "type": "cube", "uuid": eid}
            if "rotation" in c:
                r = c["rotation"]
                el["rotation"] = [-r[0], -r[1], r[2]]
            if c.get("inflate"):
                el["inflate"] = c["inflate"]
            if isinstance(c["uv"], dict):
                for fn in ("north", "east", "south", "west", "up", "down"):
                    if fn in c["uv"]:
                        u, v = c["uv"][fn]["uv"]
                        du, dv = c["uv"][fn]["uv_size"]
                        el["faces"][fn] = {"uv": [u, v, u + du, v + dv], "texture": 0}
                    else:
                        el["faces"][fn] = {"uv": [0, 0, 0, 0], "texture": None}
            else:   # UV de caja convertida a UV por cara
                u, v = c["uv"]
                w, h, d = [math.floor(x) for x in s]
                lay = {"north": (u + d, v + d, w, h), "east": (u, v + d, d, h), "south": (u + 2 * d + w, v + d, w, h),
                       "west": (u + d + w, v + d, d, h), "up": (u + d, v, w, d), "down": (u + d + w, v + d, w, -d)}
                for fn, (a1, b1, ww, hh) in lay.items():
                    el["faces"][fn] = {"uv": [a1, b1, a1 + ww, b1 + hh], "texture": 0}
            elements.append(el)
            groups[b["name"]]["children"].append(eid)
    roots = []
    for nme in order:
        b = next(x for x in g["bones"] if x["name"] == nme)
        if b.get("parent") and b["parent"] in groups:
            groups[b["parent"]]["children"].append(groups[nme])
        else:
            roots.append(groups[nme])
    animations = []
    for aname, a in anims.items():
        animators = {}
        for bn, chans in a["bones"].items():
            if bn not in groups:
                continue
            kfs = []
            for ch, frames in chans.items():
                for t, val in frames.items():
                    x, y, z = val
                    if ch == "rotation":
                        dp = {"x": -x, "y": -y, "z": z}
                    elif ch == "position":
                        dp = {"x": -x, "y": y, "z": z}
                    else:
                        dp = {"x": x, "y": y, "z": z}
                    kfs.append({"channel": ch, "data_points": [{k2: str(v2) for k2, v2 in dp.items()}],
                                "uuid": str(U.uuid4()), "time": float(t), "color": -1, "interpolation": "linear"})
            animators[groups[bn]["uuid"]] = {"name": bn, "type": "bone", "keyframes": kfs}
        animations.append({"uuid": str(U.uuid4()), "name": aname, "loop": "loop" if a.get("loop") else "once",
                           "override": False, "length": a["animation_length"], "snapping": 24, "selected": False,
                           "anim_time_update": "", "blend_weight": "", "start_delay": "", "loop_delay": "",
                           "animators": animators})
    return {
        "meta": {"format_version": "4.5", "model_format": "bedrock", "box_uv": False},
        "name": name, "model_identifier": "nether_dragon", "visible_box": [12, 8, 2],
        "variable_placeholders": "", "variable_placeholder_buttons": [], "timeline_setups": [],
        "unhandled_root_fields": {},
        "resolution": {"width": tex.size[0], "height": tex.size[1]},
        "elements": elements, "outliner": roots,
        "textures": [{"path": "", "name": name + ".png", "folder": "", "namespace": "", "id": "0", "particle": False,
                      "render_mode": "default", "render_sides": "auto", "frame_time": 1, "frame_order_type": "loop",
                      "frame_order": "", "frame_interpolate": False, "visible": True, "mode": "bitmap", "saved": False,
                      "uuid": str(U.uuid4()), "relative_path": "",
                      "source": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}],
        "animations": animations,
    }
