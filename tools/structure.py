"""Construye la capital del Reino del Nether como plantilla de estructura .nbt (formato de bloque de estructura)."""
import gzip
import os
import struct
from common import DATA, MODID

DATA_VERSION = 3955  # Minecraft 1.21.1


# ------------------------------------------------------------------ escritor NBT mínimo
class Byte(int): pass
class Int(int): pass
class Double(float): pass
class ListOf(list):
    def __init__(self, tag, items):
        super().__init__(items)
        self.tag = tag


def _payload(v):
    if isinstance(v, Byte):
        return 1, struct.pack(">b", v)
    if isinstance(v, Int):
        return 3, struct.pack(">i", v)
    if isinstance(v, Double):
        return 6, struct.pack(">d", v)
    if isinstance(v, str):
        b = v.encode("utf-8")
        return 8, struct.pack(">H", len(b)) + b
    if isinstance(v, ListOf):
        out = struct.pack(">bi", v.tag if len(v) else 0, len(v))
        for it in v:
            out += _payload(it)[1]
        return 9, out
    if isinstance(v, dict):
        out = b""
        for k, val in v.items():
            t, p = _payload(val)
            kb = k.encode("utf-8")
            out += struct.pack(">bH", t, len(kb)) + kb + p
        return 10, out + b"\x00"
    raise TypeError(type(v))


def write_nbt(path, root):
    t, p = _payload(root)
    data = struct.pack(">bH", 10, 0) + p
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wb") as f:
        f.write(data)


# ------------------------------------------------------------------ constructor
SX, SY, SZ = 49, 42, 49
C = 24  # centro
FLOOR = 4  # altura del suelo de la ciudad (local)


class World:
    def __init__(self):
        self.b = {}
        self.ents = []

    def set(self, x, y, z, name, **props):
        if 0 <= x < SX and 0 <= y < SY and 0 <= z < SZ:
            self.b[(x, y, z)] = (name, tuple(sorted(props.items())))

    def get(self, x, y, z):
        return self.b.get((x, y, z), (None,))[0]

    def fill(self, x0, y0, z0, x1, y1, z1, name, **p):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, name, **p)

    def walls(self, x0, y0, z0, x1, y1, z1, name, **p):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    if x in (x0, x1) or z in (z0, z1):
                        self.set(x, y, z, name, **p)

    def entity(self, x, y, z, eid, extra=None):
        nbt = {"id": eid, "PersistenceRequired": Byte(1)}
        if extra:
            nbt.update(extra)
        self.ents.append((x + 0.5, y, z + 0.5, nbt))


M = "minecraft:"
R = MODID + ":"
PBB = M + "polished_blackstone_bricks"
RNB = M + "red_nether_bricks"
NB = M + "nether_bricks"
BS = M + "blackstone"
GB = M + "gilded_blackstone"
GOLD = M + "gold_block"
SHROOM = M + "shroomlight"
GLASS = M + "red_stained_glass"
AIR = M + "air"
RUBY = R + "ruby_block"
LAMP = R + "ruby_lamp"
RBR = R + "ruby_bricks"


def build():
    w = World()
    # 1) limpiar el interior (aire) dentro del recinto amurallado
    w.fill(1, FLOOR, 1, SX - 2, SY - 1, SZ - 2, AIR)
    # 2) cimientos: pilares sobre el mar de lava y plataforma
    for x in range(0, SX, 6):
        for z in range(0, SZ, 6):
            w.fill(x, 0, z, min(x + 1, SX - 1), FLOOR - 1, min(z + 1, SZ - 1), NB)
    w.fill(0, FLOOR - 1, 0, SX - 1, FLOOR - 1, SZ - 1, PBB)
    w.fill(1, FLOOR - 2, 1, SX - 2, FLOOR - 2, SZ - 2, BS)
    # suelo con dibujo: ladrillos rojos en cruz y luces
    for x in range(1, SX - 1):
        for z in range(1, SZ - 1):
            if abs(x - C) <= 2 or abs(z - C) <= 2:
                w.set(x, FLOOR - 1, z, RNB)
            if x % 8 == 4 and z % 8 == 4:
                w.set(x, FLOOR - 1, z, SHROOM)
    # 3) murallas exteriores con almenas y franja roja
    w.walls(0, FLOOR, 0, SX - 1, FLOOR + 8, SZ - 1, PBB)
    w.walls(0, FLOOR + 5, 0, SX - 1, FLOOR + 5, SZ - 1, RNB)
    for i in range(0, SX, 2):
        for (x, z) in [(i, 0), (i, SZ - 1), (0, i), (SX - 1, i)]:
            w.set(x, FLOOR + 9, z, PBB)
    # adarve interior
    w.walls(1, FLOOR + 7, 1, SX - 2, FLOOR + 7, SZ - 2, M + "polished_blackstone_brick_slab", type="bottom", waterlogged="false")
    # puerta principal (sur) y puertas laterales
    w.fill(C - 3, FLOOR, SZ - 1, C + 3, FLOOR + 6, SZ - 1, AIR)
    w.fill(C - 4, FLOOR + 7, SZ - 1, C + 4, FLOOR + 8, SZ - 1, RNB)
    for dx in (-4, 4):
        w.fill(C + dx, FLOOR, SZ - 1, C + dx, FLOOR + 8, SZ - 1, GB)
        w.set(C + dx, FLOOR + 9, SZ - 1, LAMP)
    for x in (0, SX - 1):
        w.fill(x, FLOOR, C - 1, x, FLOOR + 3, C + 1, AIR)
    # estandartes en la puerta
    for dx in (-6, 6):
        w.set(C + dx, FLOOR + 6, SZ, M + "red_wall_banner", facing="south")
    # 4) torres en las esquinas
    for (tx, tz) in [(0, 0), (SX - 7, 0), (0, SZ - 7), (SX - 7, SZ - 7)]:
        w.walls(tx, FLOOR, tz, tx + 6, FLOOR + 15, tz + 6, PBB)
        w.fill(tx + 1, FLOOR, tz + 1, tx + 5, FLOOR + 14, tz + 5, AIR)
        w.walls(tx, FLOOR + 12, tz, tx + 6, FLOOR + 12, tz + 6, RNB)
        w.fill(tx + 1, FLOOR + 15, tz + 1, tx + 5, FLOOR + 15, tz + 5, PBB)
        w.fill(tx + 2, FLOOR + 16, tz + 2, tx + 4, FLOOR + 17, tz + 4, RNB)
        w.set(tx + 3, FLOOR + 18, tz + 3, GOLD)
        w.set(tx + 3, FLOOR + 19, tz + 3, LAMP)
        for (ax, az) in [(tx, tz), (tx + 6, tz), (tx, tz + 6), (tx + 6, tz + 6)]:
            w.set(ax, FLOOR + 16, az, PBB)
            w.set(ax, FLOOR + 17, az, LAMP)
        for y in (FLOOR + 4, FLOOR + 9):
            w.set(tx + 3, y, tz, GLASS)
            w.set(tx + 3, y, tz + 6, GLASS)
            w.set(tx, y, tz + 3, GLASS)
            w.set(tx + 6, y, tz + 3, GLASS)
        # escalera interior simple (bloques en espiral)
        spiral = [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (4, 5), (3, 5), (2, 5), (1, 5), (1, 4)]
        for i, (sx, sz) in enumerate(spiral):
            w.set(tx + sx, FLOOR + i, tz + sz, BS)
        w.fill(tx + 1, FLOOR + 14, tz + 1, tx + 5, FLOOR + 14, tz + 5, BS)
        w.set(tx + 1, FLOOR + 14, tz + 3, AIR)
        w.set(tx + 3, FLOOR, tz + 3, LAMP)
        # acceso desde el patio
        dx = 6 if tx == 0 else 0
        dz = 6 if tz == 0 else 0
        w.fill(tx + dx, FLOOR, tz + 3, tx + dx, FLOOR + 2, tz + 3, AIR)
        w.fill(tx + 3, FLOOR, tz + dz, tx + 3, FLOOR + 2, tz + dz, AIR)
    # 5) castillo central (torreón)
    k0, k1 = C - 7, C + 7
    w.walls(k0, FLOOR, k0, k1, FLOOR + 17, k1, PBB)
    w.fill(k0 + 1, FLOOR, k0 + 1, k1 - 1, FLOOR + 16, k1 - 1, AIR)
    for (x, z) in [(k0, k0), (k1, k0), (k0, k1), (k1, k1)]:
        w.fill(x, FLOOR, z, x, FLOOR + 20, z, RNB)
        w.set(x, FLOOR + 21, z, LAMP)
    w.walls(k0, FLOOR + 8, k0, k1, FLOOR + 8, k1, RNB)
    w.walls(k0, FLOOR + 17, k0, k1, FLOOR + 17, k1, RNB)
    w.fill(k0 + 1, FLOOR + 17, k0 + 1, k1 - 1, FLOOR + 17, k1 - 1, PBB)
    for i in range(k0, k1 + 1, 2):
        for (x, z) in [(i, k0), (i, k1), (k0, i), (k1, i)]:
            w.set(x, FLOOR + 18, z, PBB)
    # ventanas
    for y0 in (FLOOR + 3, FLOOR + 11):
        for i in range(k0 + 3, k1 - 2, 4):
            for (x, z) in [(i, k0), (i, k1), (k0, i), (k1, i)]:
                w.fill(x, y0, z, x, y0 + 2, z, GLASS)
    # entrada
    w.fill(C - 2, FLOOR, k1, C + 2, FLOOR + 4, k1, AIR)
    w.fill(C - 3, FLOOR + 5, k1, C + 3, FLOOR + 5, k1, GOLD)
    for dx in (-3, 3):
        w.set(C + dx, FLOOR + 3, k1 + 1, M + "red_wall_banner", facing="south")
    # sala del trono
    w.fill(C - 1, FLOOR - 1, k1 - 1, C + 1, FLOOR - 1, k0 + 2, RNB)
    w.fill(C, FLOOR, k1 - 1, C, FLOOR, k0 + 4, M + "red_carpet")
    w.fill(C - 2, FLOOR, k0 + 1, C + 2, FLOOR, k0 + 3, GOLD)
    w.set(C, FLOOR + 1, k0 + 2, RUBY)
    w.fill(C - 1, FLOOR + 1, k0 + 1, C + 1, FLOOR + 3, k0 + 1, RUBY)
    w.set(C, FLOOR + 4, k0 + 1, LAMP)
    for (x, z) in [(k0 + 2, k0 + 2), (k1 - 2, k0 + 2), (k0 + 2, k1 - 2), (k1 - 2, k1 - 2)]:
        w.fill(x, FLOOR, z, x, FLOOR + 7, z, RBR)
        w.set(x, FLOOR + 8, z, LAMP)
    w.fill(k0 + 1, FLOOR + 8, k0 + 1, k1 - 1, FLOOR + 8, k1 - 1, PBB)  # segundo piso
    w.fill(C - 1, FLOOR + 8, C - 1, C + 1, FLOOR + 8, C + 1, LAMP)
    # torre superior y aguja
    t0, t1 = C - 3, C + 3
    w.walls(t0, FLOOR + 18, t0, t1, FLOOR + 28, t1, PBB)
    w.fill(t0 + 1, FLOOR + 18, t0 + 1, t1 - 1, FLOOR + 27, t1 - 1, AIR)
    w.walls(t0, FLOOR + 25, t0, t1, FLOOR + 25, t1, RNB)
    for (x, z) in [(t0, t0), (t1, t0), (t0, t1), (t1, t1)]:
        w.fill(x, FLOOR + 18, z, x, FLOOR + 30, z, RNB)
        w.set(x, FLOOR + 31, z, LAMP)
    for y in (FLOOR + 21, FLOOR + 22):
        for (x, z) in [(C, t0), (C, t1), (t0, C), (t1, C)]:
            w.set(x, y, z, GLASS)
    w.fill(t0 + 1, FLOOR + 29, t0 + 1, t1 - 1, FLOOR + 29, t1 - 1, RNB)
    w.fill(C - 1, FLOOR + 30, C - 1, C + 1, FLOOR + 32, C + 1, PBB)
    w.fill(C, FLOOR + 33, C, C, FLOOR + 35, C, GOLD)
    w.set(C, FLOOR + 36, C, RUBY)
    w.set(C, FLOOR + 37, C, LAMP)
    # 6) Templo del Rubí (este)
    ex0, ez0 = 33, 9
    w.fill(ex0, FLOOR, ez0, ex0 + 10, FLOOR, ez0 + 9, M + "polished_blackstone")
    for x in range(ex0, ex0 + 11, 3):
        for z in (ez0, ez0 + 9):
            w.fill(x, FLOOR + 1, z, x, FLOOR + 7, z, RBR)
    w.fill(ex0, FLOOR + 8, ez0, ex0 + 10, FLOOR + 8, ez0 + 9, RNB)
    w.fill(ex0 + 1, FLOOR + 9, ez0 + 1, ex0 + 9, FLOOR + 9, ez0 + 8, RNB)
    w.fill(ex0 + 3, FLOOR + 10, ez0 + 3, ex0 + 7, FLOOR + 10, ez0 + 6, GOLD)
    w.set(ex0 + 5, FLOOR + 11, ez0 + 4, LAMP)
    w.fill(ex0 + 4, FLOOR + 1, ez0 + 4, ex0 + 6, FLOOR + 1, ez0 + 5, GOLD)
    w.set(ex0 + 5, FLOOR + 2, ez0 + 4, RUBY)
    w.set(ex0 + 5, FLOOR + 3, ez0 + 4, LAMP)
    for x in (ex0 + 2, ex0 + 8):
        w.set(x, FLOOR + 1, ez0 + 5, M + "soul_lantern", hanging="false", waterlogged="false")
    # 7) Cuartel Real y forja (oeste)
    bx0, bz0 = 6, 9
    w.walls(bx0, FLOOR, bz0, bx0 + 10, FLOOR + 6, bz0 + 9, PBB)
    w.fill(bx0 + 1, FLOOR, bz0 + 1, bx0 + 9, FLOOR + 5, bz0 + 8, AIR)
    w.fill(bx0, FLOOR + 7, bz0, bx0 + 10, FLOOR + 7, bz0 + 9, RNB)
    w.fill(bx0 + 4, FLOOR, bz0 + 9, bx0 + 6, FLOOR + 3, bz0 + 9, AIR)
    for i in range(bx0 + 2, bx0 + 9, 3):
        w.fill(i, FLOOR + 2, bz0, i, FLOOR + 3, bz0, GLASS)
    w.set(bx0 + 2, FLOOR, bz0 + 2, M + "anvil", facing="north")
    w.set(bx0 + 3, FLOOR, bz0 + 1, M + "smithing_table")
    w.set(bx0 + 5, FLOOR, bz0 + 1, M + "blast_furnace", facing="south", lit="true")
    w.set(bx0 + 7, FLOOR, bz0 + 1, M + "lava_cauldron")
    w.set(bx0 + 8, FLOOR, bz0 + 2, M + "grindstone", face="floor", facing="north")
    w.fill(bx0 + 8, FLOOR, bz0 + 5, bx0 + 9, FLOOR, bz0 + 7, M + "red_wool")
    w.set(bx0 + 5, FLOOR + 5, bz0 + 5, LAMP)
    # 8) Distrito residencial (suroeste)
    for (hx, hz) in [(6, 31), (13, 31), (6, 39), (13, 39)]:
        w.walls(hx, FLOOR, hz, hx + 5, FLOOR + 4, hz + 5, M + "crimson_planks")
        w.fill(hx + 1, FLOOR, hz + 1, hx + 4, FLOOR + 3, hz + 4, AIR)
        for (x, z) in [(hx, hz), (hx + 5, hz), (hx, hz + 5), (hx + 5, hz + 5)]:
            w.fill(x, FLOOR, z, x, FLOOR + 4, z, BS)
        w.fill(hx, FLOOR + 5, hz, hx + 5, FLOOR + 5, hz + 5, RNB)
        w.fill(hx + 1, FLOOR + 6, hz + 1, hx + 4, FLOOR + 6, hz + 4, M + "red_nether_brick_slab", type="bottom", waterlogged="false")
        w.fill(hx + 2, FLOOR, hz, hx + 2, FLOOR + 2, hz, AIR)
        w.set(hx + 4, FLOOR + 2, hz + 5, GLASS)
        w.set(hx + 3, FLOOR + 3, hz + 3, SHROOM)
        w.set(hx + 4, FLOOR, hz + 4, M + "red_bed", facing="north", part="foot", occupied="false")
        w.set(hx + 4, FLOOR, hz + 3, M + "red_bed", facing="north", part="head", occupied="false")
    # 9) Mercado del Nether (sureste)
    for (mx, mz) in [(32, 31), (39, 31), (32, 38), (39, 38)]:
        for (x, z) in [(mx, mz), (mx + 4, mz), (mx, mz + 4), (mx + 4, mz + 4)]:
            w.fill(x, FLOOR, z, x, FLOOR + 3, z, M + "crimson_fence")
        w.fill(mx, FLOOR + 4, mz, mx + 4, FLOOR + 4, mz + 4, M + "red_wool")
        w.fill(mx + 1, FLOOR + 4, mz + 1, mx + 3, FLOOR + 4, mz + 3, M + "black_wool")
        w.fill(mx + 1, FLOOR, mz + 1, mx + 3, FLOOR, mz + 1, M + "barrel", facing="up", open="false")
        w.set(mx + 2, FLOOR + 1, mz + 1, GOLD if (mx + mz) % 2 else RUBY)
    # 10) Cultivos de verruga (norte, detrás del castillo)
    for x in range(C - 6, C + 7):
        for z in range(3, 8):
            if x % 3 == 0:
                w.set(x, FLOOR - 1, z, SHROOM)
            else:
                w.set(x, FLOOR - 1, z, M + "soul_sand")
                w.set(x, FLOOR, z, M + "nether_wart", age="3")
    # faroles en la avenida
    for z in range(10, SZ - 3, 6):
        for x in (C - 4, C + 4):
            if not (C - 8 <= z <= C + 8):
                w.fill(x, FLOOR, z, x, FLOOR + 2, z, PBB)
                w.set(x, FLOOR + 3, z, LAMP)
    # 11) habitantes
    E = R
    G_, A_ = E + "guerrero", E + "arquero"
    # el Rey Necromancer en su trono de rubí, mirando hacia la entrada
    w.entity(C, FLOOR + 2, k0 + 2, E + "rey_necromancer")
    w.entity(C - 3, FLOOR, k0 + 4, G_)
    w.entity(C + 3, FLOOR, k0 + 4, A_)
    # guardias de la puerta y de la sala del trono
    w.entity(C - 2, FLOOR, SZ - 3, G_)
    w.entity(C + 2, FLOOR, SZ - 3, G_)
    w.entity(C - 2, FLOOR, k1 + 2, G_)
    w.entity(C + 2, FLOOR, k1 + 2, G_)
    # templo, cuartel, mercado y calles
    w.entity(ex0 + 5, FLOOR + 1, ez0 + 6, G_)
    w.entity(ex0 + 3, FLOOR + 1, ez0 + 7, A_)
    w.entity(bx0 + 3, FLOOR, bz0 + 4, G_)
    w.entity(bx0 + 6, FLOOR, bz0 + 4, G_)
    w.entity(bx0 + 4, FLOOR, bz0 + 6, A_)
    w.entity(bx0 + 7, FLOOR, bz0 + 6, A_)
    w.entity(34, FLOOR, 30, G_)
    w.entity(41, FLOOR, 37, A_)
    w.entity(10, FLOOR, 37, G_)
    w.entity(17, FLOOR, 37, A_)
    w.entity(C - 3, FLOOR, 9, G_)
    w.entity(C + 6, FLOOR, SZ - 6, G_)
    # arqueros en las torres de la muralla
    w.entity(3, FLOOR + 15, 3, A_)
    w.entity(SX - 4, FLOOR + 15, SZ - 4, A_)
    # nido con un huevo de Dragón del Nether (golpéalo para recogerlo y luego ponlo donde quieras)
    nx, nz = C + 12, C + 3
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dx or dz:
                w.set(nx + dx, FLOOR - 1, nz + dz, M + "soul_soil")
                w.set(nx + dx, FLOOR, nz + dz, M + "blackstone_slab", type="bottom", waterlogged="false")
    w.set(nx, FLOOR - 1, nz, M + "magma_block")
    w.entity(nx, FLOOR, nz, E + "dragon_egg")
    return w


def save(w, path):
    palette, pidx, blocks = [], {}, []
    for (x, y, z), (name, props) in sorted(w.b.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        key = (name, props)
        if key not in pidx:
            pidx[key] = len(palette)
            entry = {"Name": name}
            if props:
                entry["Properties"] = {k: str(v) for k, v in props}
            palette.append(entry)
        blocks.append({"pos": ListOf(3, [Int(x), Int(y), Int(z)]), "state": Int(pidx[key])})
    ents = []
    for (x, y, z, nbt) in w.ents:
        ents.append({"pos": ListOf(6, [Double(x), Double(y), Double(z)]),
                     "blockPos": ListOf(3, [Int(int(x)), Int(int(y)), Int(int(z))]), "nbt": nbt})
    root = {"DataVersion": Int(DATA_VERSION), "size": ListOf(3, [Int(SX), Int(SY), Int(SZ)]),
            "palette": ListOf(10, palette), "blocks": ListOf(10, blocks), "entities": ListOf(10, ents)}
    write_nbt(path, root)
    return len(blocks), len(palette), len(ents)


def write_all():
    w = build()
    return w, save(w, os.path.join(DATA, "structure", "capital.nbt"))
