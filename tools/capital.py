"""Capital gigante del Reino del Nether (176 x 176 bloques) como plantilla de estructura .nbt.

La plantilla NO guarda aire: el mod (CapitalStructure.java) excava la caverna, pone la plataforma de piedra negra
y los pilares sobre el mar de lava, y luego coloca estos bloques encima.

Distritos:
  centro-norte  castillo real (muralla interior, torreón, torres, sala del trono, patio y jardines)
  centro        plaza central con fuente y avenidas hacia las 4 puertas
  noroeste      montañas, minas, vetas de minerales y campamento minero
  noreste       zona militar: cuarteles, armería, patio de entrenamiento, campo de tiro y torres
  oeste         talleres (herrería, alquimia, carpintería, fundición) y almacenes
  este          distrito comercial: puestos con toldos y tiendas
  sur           barrio residencial con muchas casas y huertos de verruga
  borde         murallas exteriores con 4 puertas fortificadas, torres y puestos de guardia
"""
import math
import os
import random

from common import DATA, MODID
from structure import Byte, Int, Double, ListOf, write_nbt, DATA_VERSION

SX, SY, SZ = 176, 72, 176
C = 88              # centro
FLOOR = 4           # y local del suelo de la ciudad (la plataforma está en FLOOR - 1, la pone el mod)
WALL0, WALL1 = 8, 167   # murallas exteriores (3 de grosor hacia dentro)

M = "minecraft:"
R = MODID + ":"
PBB = M + "polished_blackstone_bricks"
CPBB = M + "cracked_polished_blackstone_bricks"
PB = M + "polished_blackstone"
CPB = M + "chiseled_polished_blackstone"
BS = M + "blackstone"
GB = M + "gilded_blackstone"
RNB = M + "red_nether_bricks"
NB = M + "nether_bricks"
CNB = M + "chiseled_nether_bricks"
QB = M + "quartz_bricks"
QP = M + "quartz_pillar"
BASALT = M + "polished_basalt"
RAWBASALT = M + "basalt"
NR = M + "netherrack"
GOLD = M + "gold_block"
SHROOM = M + "shroomlight"
GLASS = M + "red_stained_glass"
BGLASS = M + "black_stained_glass"
OBS = M + "obsidian"
CRY = M + "crying_obsidian"
MAGMA = M + "magma_block"
SOULSAND = M + "soul_sand"
SOULSOIL = M + "soul_soil"
NWB = M + "nether_wart_block"
WWB = M + "warped_wart_block"
CPL = M + "crimson_planks"
WPL = M + "warped_planks"
CST = M + "stripped_crimson_stem"
WST = M + "stripped_warped_stem"
RUBY = R + "ruby_block"
LAMP = R + "ruby_lamp"
RBR = R + "ruby_bricks"
RORE = R + "ruby_ore"
CHEST_LOOT = ["minecraft:chests/bastion_other", "minecraft:chests/nether_bridge", "minecraft:chests/village/village_weaponsmith",
              "minecraft:chests/village/village_toolsmith", "minecraft:chests/village/village_armorer"]


class World:
    def __init__(self):
        self.b = {}
        self.nbt = {}
        self.ents = []

    def set(self, x, y, z, name, **props):
        if 0 <= x < SX and 0 <= y < SY and 0 <= z < SZ:
            self.b[(x, y, z)] = (name, tuple(sorted((k, str(v)) for k, v in props.items())))
            self.nbt.pop((x, y, z), None)

    def clear(self, x, y, z):
        self.b.pop((x, y, z), None)
        self.nbt.pop((x, y, z), None)

    def clear_box(self, x0, y0, z0, x1, y1, z1):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.clear(x, y, z)

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

    def chest(self, x, y, z, facing, loot, block="chest"):
        if block == "chest":
            self.set(x, y, z, M + "chest", facing=facing, type="single", waterlogged="false")
        else:
            self.set(x, y, z, M + "barrel", facing="up", open="false")
        self.nbt[(x, y, z)] = {"LootTable": loot}

    def entity(self, x, y, z, eid, extra=None):
        nbt = {"id": eid, "PersistenceRequired": Byte(1)}
        if extra:
            nbt.update(extra)
        self.ents.append((x + 0.5, y, z + 0.5, nbt))


OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
STEP = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}


def stairs(w, x, y, z, block, facing, half="bottom"):
    w.set(x, y, z, block, facing=facing, half=half, shape="straight", waterlogged="false")


def slab(w, x, y, z, block, kind="bottom"):
    w.set(x, y, z, block, type=kind, waterlogged="false")


def door(w, x, y, z, facing, block="crimson_door"):
    w.set(x, y, z, M + block, facing=facing, half="lower", hinge="left", open="false", powered="false")
    w.set(x, y + 1, z, M + block, facing=facing, half="upper", hinge="left", open="false", powered="false")


def bed(w, x, y, z, facing, color="red"):
    """La cabecera queda hacia 'facing'."""
    dx, dz = STEP[facing]
    w.set(x, y, z, M + color + "_bed", facing=facing, part="foot", occupied="false")
    w.set(x + dx, y, z + dz, M + color + "_bed", facing=facing, part="head", occupied="false")


def lantern(w, x, y, z, hanging=True, soul=False):
    w.set(x, y, z, M + ("soul_lantern" if soul else "lantern"), hanging=str(hanging).lower(), waterlogged="false")


def lamp_post(w, x, z, h=3, top=LAMP, base=PB):
    w.fill(x, FLOOR, z, x, FLOOR + h - 1, z, base)
    w.set(x, FLOOR + h, z, top)


def crimson_tree(w, x, z, rnd, h=None, warped=False):
    h = h or rnd.randint(5, 8)
    stem = M + ("warped_stem" if warped else "crimson_stem")
    cap = WWB if warped else NWB
    w.fill(x, FLOOR, z, x, FLOOR + h - 1, z, stem, axis="y")
    r = 2 if h < 7 else 3
    for dy in range(0, 3):
        rr = r - dy
        for dx in range(-rr, rr + 1):
            for dz in range(-rr, rr + 1):
                if abs(dx) + abs(dz) <= rr + 1:
                    w.set(x + dx, FLOOR + h - 1 + dy, z + dz, SHROOM if rnd.random() < 0.08 else cap)
    w.set(x, FLOOR + h - 1, z, stem, axis="y")


def gable_roof(w, x0, z0, wd, dp, ytop, stair, fill, ridge_slab, along_x=None):
    """Tejado a dos aguas sobre el rectángulo [x0, x0+wd) x [z0, z0+dp), con alero de 1 bloque."""
    if along_x is None:
        along_x = wd >= dp
    if along_x:
        a, b, k = z0 - 1, z0 + dp, 0
        while a <= b:
            y = ytop + k
            for x in range(x0 - 1, x0 + wd + 1):
                if a == b:
                    slab(w, x, y, a, ridge_slab)
                else:
                    stairs(w, x, y, a, stair, "south")
                    stairs(w, x, y, b, stair, "north")
            for z in range(a + 1, b):
                w.set(x0, y, z, fill)
                w.set(x0 + wd - 1, y, z, fill)
            a, b, k = a + 1, b - 1, k + 1
    else:
        a, b, k = x0 - 1, x0 + wd, 0
        while a <= b:
            y = ytop + k
            for z in range(z0 - 1, z0 + dp + 1):
                if a == b:
                    slab(w, a, y, z, ridge_slab)
                else:
                    stairs(w, a, y, z, stair, "east")
                    stairs(w, b, y, z, stair, "west")
            for x in range(a + 1, b):
                w.set(x, y, z0, fill)
                w.set(x, y, z0 + dp - 1, fill)
            a, b, k = a + 1, b - 1, k + 1


def pyramid_roof(w, x0, z0, size, ytop, stair, cap):
    """Tejado de pirámide sobre un cuadrado size x size (con alero de 1 bloque)."""
    ax, bx, az, bz, k = x0 - 1, x0 + size, z0 - 1, z0 + size, 0
    while ax < bx and az < bz:
        y = ytop + k
        for i in range(ax, bx + 1):
            stairs(w, i, y, az, stair, "south")
            stairs(w, i, y, bz, stair, "north")
        for i in range(az, bz + 1):
            stairs(w, ax, y, i, stair, "east")
            stairs(w, bx, y, i, stair, "west")
        ax, bx, az, bz, k = ax + 1, bx - 1, az + 1, bz - 1, k + 1
    cx, cz = (x0 * 2 + size - 1) // 2, (z0 * 2 + size - 1) // 2
    w.set(cx, ytop + k, cz, cap)
    w.set(cx, ytop + k + 1, cz, LAMP)


# ====================================================================== EDIFICIOS
HOUSE_STYLES = [
    # pared, marco, escalera del tejado, bloque del tejado, losa de cumbrera, suelo
    (CPL, CST, M + "red_nether_brick_stairs", RNB, M + "red_nether_brick_slab", CPL),
    (WPL, WST, M + "nether_brick_stairs", NB, M + "nether_brick_slab", WPL),
    (PBB, CST, M + "red_nether_brick_stairs", RNB, M + "red_nether_brick_slab", CPL),
    (QB, PB, M + "polished_blackstone_brick_stairs", PBB, M + "polished_blackstone_brick_slab", CPL),
    (NB, CST, M + "crimson_stairs", CPL, M + "crimson_slab", CPL),
    (RBR, PB, M + "blackstone_stairs", BS, M + "blackstone_slab", WPL),
]


def house(w, x0, z0, wd, dp, facing, rnd, floors=1, style=None, chimney=True):
    """Casa con marco, ventanas, puerta, muebles y tejado a dos aguas. facing = lado de la puerta."""
    wall, frame, rstair, rfill, rslab, flo = style or rnd.choice(HOUSE_STYLES)
    hgt = 4 * floors
    x1, z1 = x0 + wd - 1, z0 + dp - 1
    # zócalo y suelo
    w.fill(x0, FLOOR - 1, z0, x1, FLOOR - 1, z1, PB)
    w.fill(x0 + 1, FLOOR - 1, z0 + 1, x1 - 1, FLOOR - 1, z1 - 1, flo)
    for y in range(FLOOR, FLOOR + hgt):
        for x in range(x0, x1 + 1):
            for z in (z0, z1):
                w.set(x, y, z, wall)
        for z in range(z0, z1 + 1):
            for x in (x0, x1):
                w.set(x, y, z, wall)
    for (x, z) in [(x0, z0), (x1, z0), (x0, z1), (x1, z1)]:
        w.fill(x, FLOOR, z, x, FLOOR + hgt - 1, z, frame, axis="y")
    for f in range(floors):
        yb = FLOOR + 4 * f + 3
        for x in range(x0, x1 + 1):
            w.set(x, yb, z0, frame, axis="x")
            w.set(x, yb, z1, frame, axis="x")
        for z in range(z0, z1 + 1):
            w.set(x0, yb, z, frame, axis="z")
            w.set(x1, yb, z, frame, axis="z")
        # ventanas
        for x in range(x0 + 2, x1 - 1, 2):
            for z in (z0, z1):
                w.set(x, FLOOR + 4 * f + 1, z, GLASS)
        for z in range(z0 + 2, z1 - 1, 2):
            for x in (x0, x1):
                w.set(x, FLOOR + 4 * f + 1, z, GLASS)
        if f > 0:  # piso intermedio
            w.fill(x0 + 1, FLOOR + 4 * f - 1, z0 + 1, x1 - 1, FLOOR + 4 * f - 1, z1 - 1, flo)
    # puerta
    if facing in ("north", "south"):
        dx = (x0 + x1) // 2
        dz = z0 if facing == "north" else z1
        w.set(dx - 1, FLOOR + 1, dz, wall)
        w.set(dx + 1, FLOOR + 1, dz, wall)
    else:
        dz = (z0 + z1) // 2
        dx = x0 if facing == "west" else x1
        w.set(dx, FLOOR + 1, dz - 1, wall)
        w.set(dx, FLOOR + 1, dz + 1, wall)
    door(w, dx, FLOOR, dz, facing)
    sx, sz = STEP[facing]
    w.set(dx, FLOOR + 2, dz, SHROOM)
    stairs(w, dx + sx, FLOOR - 1, dz + sz, M + "polished_blackstone_stairs", OPP[facing])
    # muebles
    ix0, iz0, ix1, iz1 = x0 + 1, z0 + 1, x1 - 1, z1 - 1
    inner = [(x, z) for x in range(ix0, ix1 + 1) for z in range(iz0, iz1 + 1)
             if abs(x - (dx - sx)) + abs(z - (dz - sz)) > 1]
    rnd.shuffle(inner)
    corner = (ix1 if dx < (x0 + x1) / 2 + 0.1 else ix0, iz1 if facing == "north" else iz0)
    bx, bz = corner
    if facing in ("north", "south"):
        bed(w, bx, FLOOR, bz, "north" if bz == iz1 else "south", rnd.choice(["red", "black", "orange", "purple"]))
        bed_cells = {(bx, bz), (bx, bz + (-1 if bz == iz1 else 1))}
    else:
        bed(w, bx, FLOOR, bz, "west" if bx == ix1 else "east", rnd.choice(["red", "black", "orange", "purple"]))
        bed_cells = {(bx, bz), (bx + (-1 if bx == ix1 else 1), bz)}
    furniture = [(M + "crafting_table", {}), (M + "barrel", {"facing": "up", "open": "false"}),
                 (M + "furnace", {"facing": OPP[facing], "lit": "false"}), (M + "potted_crimson_fungus", {}),
                 (M + "cauldron", {}), (M + "lectern", {"facing": OPP[facing], "has_book": "false", "powered": "false"})]
    rnd.shuffle(furniture)
    placed = 0
    for (x, z) in inner:
        if placed >= 3:
            break
        if (x, z) in bed_cells or not (x in (ix0, ix1) or z in (iz0, iz1)):
            continue
        name, props = furniture[placed]
        w.set(x, FLOOR, z, name, **props)
        placed += 1
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    w.set(cx, FLOOR, cz, M + rnd.choice(["red_carpet", "black_carpet", "orange_carpet"]))
    for f in range(floors):
        lantern(w, cx, FLOOR + 4 * f + 2, cz, hanging=True)
    if floors > 1:  # escalera de mano al segundo piso
        lx, lz = (ix0, iz0) if (ix0, iz0) not in bed_cells else (ix1, iz0)
        for y in range(FLOOR, FLOOR + 4):
            w.set(lx, y, lz, M + "ladder", facing="south" if lz == iz0 else "north", waterlogged="false")
        w.clear(lx, FLOOR + 3, lz)
        w.set(lx, FLOOR + 3, lz, M + "ladder", facing="south" if lz == iz0 else "north", waterlogged="false")
        bed(w, ix1 if lx == ix0 else ix0, FLOOR + 4, iz1, "north", rnd.choice(["red", "black"]))
        w.set(ix0 + 1, FLOOR + 4, iz1, M + "barrel", facing="up", open="false")
    gable_roof(w, x0, z0, wd, dp, FLOOR + hgt, rstair, rfill, rslab)
    if chimney and rnd.random() < 0.6:
        chx, chz = x1 - 1, z0 + 1
        top = FLOOR + hgt + max(wd, dp) // 2 + 1
        w.fill(chx, FLOOR + hgt, chz, chx, top, chz, BS)
        w.set(chx, top + 1, chz, M + "campfire", lit="true", facing="north", signal_fire="false", waterlogged="false")


def stall(w, x0, z0, rnd, facing="south"):
    """Puesto de mercado 5x4: postes, toldo a rayas, mostrador y mercancía."""
    colors = rnd.choice([("red", "black"), ("red", "yellow"), ("orange", "black"), ("purple", "black"), ("red", "white"),
                         ("magenta", "black"), ("yellow", "brown")])
    x1, z1 = x0 + 4, z0 + 3
    for (x, z) in [(x0, z0), (x1, z0), (x0, z1), (x1, z1)]:
        w.fill(x, FLOOR, z, x, FLOOR + 2, z, M + "crimson_fence", north="false", south="false", east="false",
               west="false", waterlogged="false")
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.set(x, FLOOR + 3, z, M + colors[(x - x0) % 2] + "_wool")
    for x in range(x0 - 1, x1 + 2):  # alero inclinado
        slab(w, x, FLOOR + 3, z1 + 1 if facing == "south" else z0 - 1, M + "crimson_slab", "top")
    zc = z1 if facing == "south" else z0
    goods = [GOLD, RUBY, SHROOM, NWB, M + "bone_block", M + "quartz_block", M + "melon", M + "pumpkin", M + "hay_block",
             M + "honeycomb_block", M + "gold_ore", MAGMA]
    for x in range(x0 + 1, x1):
        slab(w, x, FLOOR, zc, M + "polished_blackstone_slab", "top")
        if rnd.random() < 0.7:
            w.set(x, FLOOR + 1, zc, rnd.choice(goods))
    w.set(x0 + 1, FLOOR, z0 + 1 if facing == "south" else z1 - 1, M + "barrel", facing="up", open="false")
    w.set(x1 - 1, FLOOR, z0 + 1 if facing == "south" else z1 - 1, M + "composter", level="0")
    lantern(w, (x0 + x1) // 2, FLOOR + 2, (z0 + z1) // 2, hanging=True)


def shop(w, x0, z0, rnd, facing="south"):
    """Tienda de 9x7 y 2 pisos: mostrador abierto al frente, estanterías, cofres, cartel colgante (estandarte)."""
    style = rnd.choice(HOUSE_STYLES)
    wall, frame, rstair, rfill, rslab, flo = style
    wd, dp = 9, 7
    x1, z1 = x0 + wd - 1, z0 + dp - 1
    house(w, x0, z0, wd, dp, facing, rnd, floors=2, style=style, chimney=False)
    # frente abierto con mostrador
    zf = z1 if facing == "south" else z0
    for x in range(x0 + 1, x1):
        w.clear(x, FLOOR, zf)
        w.clear(x, FLOOR + 1, zf)
        w.clear(x, FLOOR + 2, zf)
    zi = zf - 1 if facing == "south" else zf + 1
    for x in range(x0 + 1, x1):
        slab(w, x, FLOOR, zi, M + "polished_blackstone_slab", "top")
        w.clear(x, FLOOR + 1, zi)
    for x in range(x0 + 2, x1 - 1, 2):
        w.set(x, FLOOR + 1, zi, rnd.choice([GOLD, RUBY, M + "bookshelf", M + "brewing_stand", SHROOM, M + "anvil"]))
    zb = z0 + 1 if facing == "south" else z1 - 1
    for x in range(x0 + 1, x1):
        w.set(x, FLOOR, zb, M + "bookshelf")
        w.set(x, FLOOR + 1, zb, M + "bookshelf")
    w.chest(x0 + 1, FLOOR, (zb + zi) // 2, "east", rnd.choice(CHEST_LOOT))
    w.chest(x1 - 1, FLOOR, (zb + zi) // 2, "west", rnd.choice(CHEST_LOOT), block="barrel")
    for x in (x0 - 1, x1 + 1):
        w.set(x, FLOOR + 3, zf, M + rnd.choice(["red", "black", "orange", "yellow"]) + "_wall_banner", facing=facing)
    for x in range(x0, x1 + 1):  # toldo del frente
        slab(w, x, FLOOR + 3, zf + (1 if facing == "south" else -1), M + "crimson_slab", "top")


def warehouse(w, x0, z0, wd, dp, rnd, facing="south"):
    """Almacén grande: muros de piedra negra, portón doble, pilas de barriles y cofres con botín."""
    x1, z1 = x0 + wd - 1, z0 + dp - 1
    h = 7
    w.fill(x0, FLOOR - 1, z0, x1, FLOOR - 1, z1, PB)
    for y in range(FLOOR, FLOOR + h):
        for x in range(x0, x1 + 1):
            w.set(x, y, z0, PBB if y < FLOOR + h - 1 else RNB)
            w.set(x, y, z1, PBB if y < FLOOR + h - 1 else RNB)
        for z in range(z0, z1 + 1):
            w.set(x0, y, z, PBB if y < FLOOR + h - 1 else RNB)
            w.set(x1, y, z, PBB if y < FLOOR + h - 1 else RNB)
    for x in range(x0, x1 + 1, 4):
        for z in (z0, z1):
            w.fill(x, FLOOR, z, x, FLOOR + h - 1, z, BASALT, axis="y")
    for x in range(x0 + 2, x1 - 1, 4):
        for z in (z0, z1):
            w.set(x, FLOOR + 4, z, GLASS)
    zf = z1 if facing == "south" else z0
    cx = (x0 + x1) // 2
    for x in range(cx - 1, cx + 2):  # portón
        for y in range(FLOOR, FLOOR + 4):
            w.clear(x, y, zf)
    w.fill(cx - 2, FLOOR + 4, zf, cx + 2, FLOOR + 4, zf, CPL)
    # pilas de barriles y cofres
    for x in range(x0 + 2, x1 - 1, 3):
        for z in range(z0 + 2, z1 - 1, 3):
            if abs(x - cx) <= 1:
                continue
            hh = rnd.randint(1, 3)
            for y in range(hh):
                w.set(x, FLOOR + y, z, M + "barrel", facing="up", open="false")
            if rnd.random() < 0.5:
                w.chest(x + 1, FLOOR, z, "west", rnd.choice(CHEST_LOOT))
            elif rnd.random() < 0.5:
                w.set(x + 1, FLOOR, z, M + "hay_block", axis="y")
    for x in range(x0 + 3, x1 - 2, 5):
        lantern(w, x, FLOOR + h - 2, (z0 + z1) // 2, hanging=True)
    w.fill(x0 + 1, FLOOR + h - 1, z0 + 1, x1 - 1, FLOOR + h - 1, z1 - 1, CPL)
    gable_roof(w, x0, z0, wd, dp, FLOOR + h, M + "nether_brick_stairs", NB, M + "nether_brick_slab")


def workshop(w, x0, z0, kind, rnd, facing="south"):
    """Taller 11x8 con frente abierto: herrería, alquimia, carpintería o fundición."""
    wd, dp = 11, 8
    x1, z1 = x0 + wd - 1, z0 + dp - 1
    w.fill(x0, FLOOR - 1, z0, x1, FLOOR - 1, z1, PB)
    for y in range(FLOOR, FLOOR + 5):
        for z in range(z0, z1 + 1):
            w.set(x0, y, z, PBB)
            w.set(x1, y, z, PBB)
        for x in range(x0, x1 + 1):
            w.set(x, y, z0 if facing == "south" else z1, PBB)
    zf = z1 if facing == "south" else z0
    for x in (x0, x0 + 5, x1):
        w.fill(x, FLOOR, zf, x, FLOOR + 4, zf, CST, axis="y")
    w.fill(x0, FLOOR + 5, z0, x1, FLOOR + 5, z1, CPL)
    zb = z0 + 1 if facing == "south" else z1 - 1
    zm = (z0 + z1) // 2
    if kind == "herreria":
        w.set(x0 + 2, FLOOR, zm, M + "anvil", facing="east")
        w.set(x0 + 4, FLOOR, zm, M + "anvil", facing="east")
        w.set(x0 + 2, FLOOR, zb, M + "smithing_table")
        w.set(x0 + 3, FLOOR, zb, M + "grindstone", face="floor", facing="south")
        w.fill(x1 - 3, FLOOR, zb, x1 - 1, FLOOR, zb, M + "blast_furnace", facing=OPP["north" if facing == "south" else "south"], lit="true")
        w.set(x1 - 2, FLOOR + 1, zb, M + "lava_cauldron")
        w.fill(x1 - 3, FLOOR - 1, zm, x1 - 2, FLOOR - 1, zm + 1, M + "lava")  # pozo de lava de la forja
        for (x, z) in [(x1 - 4, zm), (x1 - 4, zm + 1), (x1 - 1, zm), (x1 - 1, zm + 1)]:
            w.set(x, FLOOR - 1, z, OBS)
        w.chest(x0 + 6, FLOOR, zb, "south", "minecraft:chests/village/village_weaponsmith")
    elif kind == "alquimia":
        for x in range(x0 + 2, x1 - 1, 2):
            slab(w, x, FLOOR, zb, M + "polished_blackstone_slab", "top")
            w.set(x, FLOOR + 1, zb, M + "brewing_stand", has_bottle_0="false", has_bottle_1="false", has_bottle_2="false")
        w.set(x0 + 2, FLOOR, zm, M + "cauldron")
        w.set(x0 + 3, FLOOR, zm, M + "enchanting_table")
        w.fill(x1 - 1, FLOOR, z0 + 1, x1 - 1, FLOOR + 2, z1 - 1, M + "bookshelf")
        w.set(x0 + 5, FLOOR, zm, SOULSAND)
        w.set(x0 + 5, FLOOR + 1, zm, M + "nether_wart", age="3")
        w.chest(x0 + 1, FLOOR, zb, "east", "minecraft:chests/bastion_other")
    elif kind == "carpinteria":
        w.set(x0 + 2, FLOOR, zb, M + "stonecutter", facing="south")
        w.set(x0 + 3, FLOOR, zb, M + "loom", facing="south")
        w.set(x0 + 4, FLOOR, zb, M + "cartography_table")
        w.set(x0 + 5, FLOOR, zb, M + "fletching_table")
        for x in range(x0 + 2, x1 - 1, 2):
            w.fill(x, FLOOR, zm, x, FLOOR + 1, zm, CST, axis="x")
        w.chest(x1 - 1, FLOOR, zb, "west", "minecraft:chests/village/village_toolsmith", block="barrel")
    else:  # fundición
        w.fill(x0 + 2, FLOOR, zb, x1 - 2, FLOOR, zb, M + "furnace", facing="south", lit="true")
        w.fill(x0 + 2, FLOOR + 1, zb, x1 - 2, FLOOR + 1, zb, M + "blast_furnace", facing="south", lit="true")
        w.fill(x0 + 3, FLOOR, zm, x0 + 5, FLOOR, zm + 1, M + "gold_block")
        w.fill(x1 - 4, FLOOR, zm, x1 - 3, FLOOR + 1, zm, M + "raw_gold_block")
        w.set(x1 - 2, FLOOR, zm, M + "raw_iron_block")
    lantern(w, (x0 + x1) // 2, FLOOR + 4, zm, hanging=True)
    lantern(w, x0 + 2, FLOOR + 4, zm, hanging=True, soul=True)
    # chimenea grande
    w.fill(x1 - 1, FLOOR + 6, zb, x1 - 1, FLOOR + 12, zb, BS)
    w.set(x1 - 1, FLOOR + 13, zb, M + "campfire", lit="true", facing="north", signal_fire="false", waterlogged="false")
    roof = rnd.choice([(M + "red_nether_brick_stairs", RNB, M + "red_nether_brick_slab"),
                       (M + "nether_brick_stairs", NB, M + "nether_brick_slab"),
                       (M + "polished_blackstone_brick_stairs", PBB, M + "polished_blackstone_brick_slab")])
    gable_roof(w, x0, z0, wd, dp, FLOOR + 6, roof[0], roof[1], roof[2], along_x=True)


def tower(w, x0, z0, size, h, rnd, roof=True, door_side=None):
    """Torre cuadrada con ventanas, escalera de mano interior, plataforma y techo de pirámide."""
    x1, z1 = x0 + size - 1, z0 + size - 1
    for y in range(FLOOR, FLOOR + h):
        for x in range(x0, x1 + 1):
            for z in (z0, z1):
                w.set(x, y, z, PBB if rnd.random() > 0.08 else CPBB)
        for z in range(z0, z1 + 1):
            for x in (x0, x1):
                w.set(x, y, z, PBB if rnd.random() > 0.08 else CPBB)
    for (x, z) in [(x0, z0), (x1, z0), (x0, z1), (x1, z1)]:
        w.fill(x, FLOOR, z, x, FLOOR + h, z, RNB)
    for y in range(FLOOR + 3, FLOOR + h - 2, 5):
        for (x, z) in [((x0 + x1) // 2, z0), ((x0 + x1) // 2, z1), (x0, (z0 + z1) // 2), (x1, (z0 + z1) // 2)]:
            w.set(x, y, z, GLASS)
            w.set(x, y + 1, z, GLASS)
    w.fill(x0, FLOOR + h, z0, x1, FLOOR + h, z1, PB)
    w.walls(x0, FLOOR + h - 1, z0, x1, FLOOR + h - 1, z1, RNB)
    for i in range(x0, x1 + 1, 2):  # almenas
        for (x, z) in [(i, z0), (i, z1)]:
            w.set(x, FLOOR + h + 1, z, PBB)
    for i in range(z0, z1 + 1, 2):
        for (x, z) in [(x0, i), (x1, i)]:
            w.set(x, FLOOR + h + 1, z, PBB)
    # escalera de mano interior
    lx, lz = x0 + 1, z0 + 1
    for y in range(FLOOR, FLOOR + h + 1):
        w.set(lx, y, lz, M + "ladder", facing="south", waterlogged="false")
    if door_side:
        dx, dz = {"north": ((x0 + x1) // 2, z0), "south": ((x0 + x1) // 2, z1),
                  "west": (x0, (z0 + z1) // 2), "east": (x1, (z0 + z1) // 2)}[door_side]
        door(w, dx, FLOOR, dz, door_side, "warped_door")
    lantern(w, (x0 + x1) // 2, FLOOR + h - 2, (z0 + z1) // 2, hanging=True)
    if roof:
        # techo sobre pilares en las esquinas
        for (x, z) in [(x0, z0), (x1, z0), (x0, z1), (x1, z1)]:
            w.fill(x, FLOOR + h + 1, z, x, FLOOR + h + 3, z, RNB)
        pyramid_roof(w, x0, z0, size, FLOOR + h + 4, M + "red_nether_brick_stairs", RNB)
        lantern(w, (x0 + x1) // 2, FLOOR + h + 3, (z0 + z1) // 2, hanging=True)
    return (x0 + x1) // 2, FLOOR + h + 1, (z0 + z1) // 2


# ====================================================================== MURALLAS
def outer_walls(w, rnd):
    h = 14
    a, b = WALL0, WALL1
    for t in range(3):  # 3 de grosor
        lo, hi = a + t, b - t
        for i in range(lo, hi + 1):
            for (x, z) in [(i, lo), (i, hi), (lo, i), (hi, i)]:
                for y in range(FLOOR, FLOOR + h):
                    if t == 0 and y == FLOOR + 9:
                        w.set(x, y, z, RNB)
                    elif t == 0 and y < FLOOR + 2:
                        w.set(x, y, z, BS)
                    else:
                        w.set(x, y, z, PBB if rnd.random() > 0.07 else CPBB)
    # adarve y almenas
    for i in range(a, b + 1):
        for t in range(3):
            for (x, z) in [(i, a + t), (i, b - t), (a + t, i), (b - t, i)]:
                w.set(x, FLOOR + h, z, PB)
        for (x, z) in [(i, a), (i, b), (a, i), (b, i)]:
            if i % 2 == 0:
                w.set(x, FLOOR + h + 1, z, PBB)
                if i % 8 == 0:
                    w.set(x, FLOOR + h + 2, z, LAMP)
    # contrafuertes por fuera
    for i in range(a + 6, b - 5, 8):
        for (x, z, dx, dz) in [(i, a - 1, 0, -1), (i, b + 1, 0, 1), (a - 1, i, -1, 0), (b + 1, i, 1, 0)]:
            for k in range(3):
                hh = h - 3 - k * 4
                w.fill(x + dx * k, FLOOR, z + dz * k, x + dx * k, FLOOR + max(1, hh), z + dz * k, PBB)
    # torres cada 32 bloques (incluye esquinas)
    posts = []
    for i in list(range(a, b - 5, 32)) + [b - 8]:
        for (tx, tz) in [(i - 1, a - 1), (i - 1, b - 8), (a - 1, i - 1), (b - 8, i - 1)]:
            if abs(tx + 4 - C) < 14 or abs(tz + 4 - C) < 14:
                continue  # el centro de cada lado es la puerta
            top = tower(w, tx, tz, 9, 22, rnd)
            posts.append(top)
    # puertas fortificadas
    for side in ("north", "south", "west", "east"):
        gatehouse(w, side, rnd)
    return posts


def gatehouse(w, side, rnd):
    """Puerta de 7 de ancho con dos torres, rastrillo de cadenas, estandartes y camino exterior."""
    a, b = WALL0, WALL1
    if side in ("north", "south"):
        z = a if side == "north" else b - 2
        zt = a - 3 if side == "north" else b - 6
        for x in range(C - 3, C + 4):
            for y in range(FLOOR, FLOOR + 9):
                for t in range(3):
                    w.clear(x, y, z + t)
        for x in range(C - 4, C + 5):
            for t in range(3):
                w.set(x, FLOOR + 9, z + t, RNB)
                w.set(x, FLOOR - 1, z + t, RNB)
        for x in range(C - 3, C + 4):  # rastrillo levantado
            w.set(x, FLOOR + 8, z + 1, M + "chain", axis="y", waterlogged="false")
            w.set(x, FLOOR + 7, z + 1, M + "chain", axis="y", waterlogged="false")
        tower(w, C - 12, zt, 8, 24, rnd)
        tower(w, C + 5, zt, 8, 24, rnd)
        outward = -1 if side == "north" else 1
        zf = a - 1 if side == "north" else b + 1
        for dx in (-5, 5):
            w.set(C + dx, FLOOR + 6, zf, M + "red_wall_banner", facing=side)
            w.set(C + dx, FLOOR + 4, zf, M + "black_wall_banner", facing=side)
        w.fill(C - 4, FLOOR + 10, z + (0 if side == "north" else 2), C + 4, FLOOR + 10, z + (0 if side == "north" else 2), GOLD)
        # camino exterior
        zz = zf
        while 0 <= zz < SZ:
            for x in range(C - 3, C + 4):
                w.set(x, FLOOR - 1, zz, RNB if abs(x - C) < 3 else PBB)
            zz += outward
        for dx in (-4, 4):
            for zl in (zf + outward * 2, zf + outward * 6):
                if 0 <= zl < SZ:
                    lamp_post(w, C + dx, zl, 3)
    else:
        x = a if side == "west" else b - 2
        xt = a - 3 if side == "west" else b - 6
        for z in range(C - 3, C + 4):
            for y in range(FLOOR, FLOOR + 9):
                for t in range(3):
                    w.clear(x + t, y, z)
        for z in range(C - 4, C + 5):
            for t in range(3):
                w.set(x + t, FLOOR + 9, z, RNB)
                w.set(x + t, FLOOR - 1, z, RNB)
        for z in range(C - 3, C + 4):
            w.set(x + 1, FLOOR + 8, z, M + "chain", axis="y", waterlogged="false")
            w.set(x + 1, FLOOR + 7, z, M + "chain", axis="y", waterlogged="false")
        tower(w, xt, C - 12, 8, 24, rnd)
        tower(w, xt, C + 5, 8, 24, rnd)
        outward = -1 if side == "west" else 1
        xf = a - 1 if side == "west" else b + 1
        for dz in (-5, 5):
            w.set(xf, FLOOR + 6, C + dz, M + "red_wall_banner", facing=side)
            w.set(xf, FLOOR + 4, C + dz, M + "black_wall_banner", facing=side)
        w.fill(x + (0 if side == "west" else 2), FLOOR + 10, C - 4, x + (0 if side == "west" else 2), FLOOR + 10, C + 4, GOLD)
        xx = xf
        while 0 <= xx < SX:
            for z in range(C - 3, C + 4):
                w.set(xx, FLOOR - 1, z, RNB if abs(z - C) < 3 else PBB)
            xx += outward
        for dz in (-4, 4):
            for xl in (xf + outward * 2, xf + outward * 6):
                if 0 <= xl < SX:
                    lamp_post(w, xl, C + dz, 3)


def outskirts(w, rnd):
    """Entre la muralla y el borde de la caverna: columnas de basalto, montículos y fuegos de almas."""
    for x in range(SX):
        for z in range(SZ):
            if WALL0 - 1 <= x <= WALL1 + 1 and WALL0 - 1 <= z <= WALL1 + 1:
                continue
            if abs(x - C) <= 4 or abs(z - C) <= 4:
                continue
            r = rnd.random()
            if r < 0.035:
                hh = rnd.randint(2, 9)
                w.fill(x, FLOOR, z, x, FLOOR + hh, z, RAWBASALT, axis="y")
            elif r < 0.06:
                w.set(x, FLOOR - 1, z, SOULSOIL)
                if rnd.random() < 0.3:
                    w.set(x, FLOOR, z, M + "soul_fire")
            elif r < 0.2:
                w.set(x, FLOOR - 1, z, rnd.choice([NR, BS, M + "crimson_nylium"]))


# ====================================================================== CASTILLO Y PLAZA
def castle(w, rnd):
    """Castillo real (x 60-116, z 12-58): muralla interior, patio con jardines, torreón y torres con agujas."""
    x0, x1, z0, z1 = 60, 116, 12, 58
    # muralla interior
    for y in range(FLOOR, FLOOR + 10):
        for x in range(x0, x1 + 1):
            for z in (z0, z0 + 1, z1 - 1, z1):
                w.set(x, y, z, PBB if y != FLOOR + 6 else RNB)
        for z in range(z0, z1 + 1):
            for x in (x0, x0 + 1, x1 - 1, x1):
                w.set(x, y, z, PBB if y != FLOOR + 6 else RNB)
    for i in range(x0, x1 + 1, 2):
        w.set(i, FLOOR + 10, z0, GB)
        w.set(i, FLOOR + 10, z1, GB)
    for i in range(z0, z1 + 1, 2):
        w.set(x0, FLOOR + 10, i, GB)
        w.set(x1, FLOOR + 10, i, GB)
    # patio: suelo de cuarzo y piedra negra
    for x in range(x0 + 2, x1 - 1):
        for z in range(z0 + 2, z1 - 1):
            w.set(x, FLOOR - 1, z, QB if (x + z) % 2 == 0 else PB)
    # puerta trasera (norte, hacia la puerta norte de la ciudad)
    for x in range(C - 3, C + 4):
        for y in range(FLOOR, FLOOR + 7):
            w.clear(x, y, z0)
            w.clear(x, y, z0 + 1)
    w.fill(C - 4, FLOOR + 7, z0, C + 4, FLOOR + 7, z0, GOLD)
    # puerta del castillo (al sur, hacia la plaza)
    for x in range(C - 3, C + 4):
        for y in range(FLOOR, FLOOR + 7):
            w.clear(x, y, z1)
            w.clear(x, y, z1 - 1)
    w.fill(C - 4, FLOOR + 7, z1, C + 4, FLOOR + 7, z1, GOLD)
    for dx in (-5, 5):
        w.fill(C + dx, FLOOR, z1 + 1, C + dx, FLOOR + 9, z1 + 1, RNB)
        w.set(C + dx, FLOOR + 10, z1 + 1, LAMP)
        w.set(C + dx, FLOOR + 6, z1 + 2, M + "red_wall_banner", facing="south")
    # torres de las esquinas de la muralla interior, con aguja
    for (tx, tz) in [(x0 - 2, z0 - 2), (x1 - 6, z0 - 2), (x0 - 2, z1 - 6), (x1 - 6, z1 - 6)]:
        tower(w, tx, tz, 9, 26, rnd)
    # torreón (keep): x 72-104, z 18-42
    k0x, k1x, k0z, k1z = 72, 104, 18, 42
    hk = 22
    for y in range(FLOOR, FLOOR + hk):
        for x in range(k0x, k1x + 1):
            for z in (k0z, k1z):
                w.set(x, y, z, PBB if rnd.random() > 0.05 else CPBB)
        for z in range(k0z, k1z + 1):
            for x in (k0x, k1x):
                w.set(x, y, z, PBB if rnd.random() > 0.05 else CPBB)
    for y in (FLOOR + 10, FLOOR + hk - 1):
        w.walls(k0x, y, k0z, k1x, y, k1z, RNB)
    for x in range(k0x, k1x + 1, 4):  # pilastras doradas
        for z in (k0z, k1z):
            w.fill(x, FLOOR, z, x, FLOOR + hk, z, QP, axis="y")
    for z in range(k0z, k1z + 1, 4):
        for x in (k0x, k1x):
            w.fill(x, FLOOR, z, x, FLOOR + hk, z, QP, axis="y")
    # ventanales
    for y0 in (FLOOR + 3, FLOOR + 13):
        for x in range(k0x + 2, k1x - 1, 4):
            for z in (k0z, k1z):
                w.fill(x, y0, z, x + 1, y0 + 4, z, GLASS)
        for z in range(k0z + 2, k1z - 1, 4):
            for x in (k0x, k1x):
                w.fill(x, y0, z, x, y0 + 4, z + 1, GLASS)
    w.fill(k0x + 1, FLOOR + 11, k0z + 1, k1x - 1, FLOOR + 11, k1z - 1, PB)  # segundo piso
    w.fill(k0x, FLOOR + hk, k0z, k1x, FLOOR + hk, k1z, PB)  # azotea
    for i in range(k0x, k1x + 1, 2):
        w.set(i, FLOOR + hk + 1, k0z, PBB)
        w.set(i, FLOOR + hk + 1, k1z, PBB)
    for i in range(k0z, k1z + 1, 2):
        w.set(k0x, FLOOR + hk + 1, i, PBB)
        w.set(k1x, FLOOR + hk + 1, i, PBB)
    # entrada del torreón
    for x in range(C - 2, C + 3):
        for y in range(FLOOR, FLOOR + 6):
            w.clear(x, y, k1z)
    w.fill(C - 3, FLOOR + 6, k1z, C + 3, FLOOR + 6, k1z, GOLD)
    # sala del trono: alfombra, columnas, trono elevado
    w.fill(C - 2, FLOOR - 1, k0z + 2, C + 2, FLOOR - 1, k1z, RNB)
    w.fill(C - 1, FLOOR - 1, k0z + 5, C + 1, FLOOR - 1, k1z, M + "red_concrete")
    w.fill(C - 1, FLOOR, k0z + 6, C + 1, FLOOR, k1z - 1, M + "red_carpet")
    for z in range(k0z + 5, k1z - 1, 4):
        for x in (C - 6, C + 6):
            w.fill(x, FLOOR, z, x, FLOOR + 10, z, QP, axis="y")
            w.set(x, FLOOR + 6, z + (1 if z < k1z - 2 else -1), M + "red_wall_banner", facing="south")
            lantern(w, x, FLOOR + 10, z + 1, hanging=True, soul=True)
    w.fill(C - 4, FLOOR, k0z + 1, C + 4, FLOOR, k0z + 4, GOLD)          # tarima
    w.fill(C - 3, FLOOR + 1, k0z + 1, C + 3, FLOOR + 1, k0z + 3, M + "red_carpet")
    w.set(C, FLOOR + 1, k0z + 2, RUBY)                                   # trono
    w.fill(C - 1, FLOOR + 2, k0z + 1, C + 1, FLOOR + 4, k0z + 1, RUBY)
    w.set(C, FLOOR + 5, k0z + 1, LAMP)
    for dx in (-1, 1):
        stairs(w, C + dx, FLOOR + 2, k0z + 2, M + "polished_blackstone_brick_stairs", "west" if dx < 0 else "east")
    for dx in (-4, 4):
        w.fill(C + dx, FLOOR + 1, k0z + 1, C + dx, FLOOR + 6, k0z + 1, RBR)
        w.set(C + dx, FLOOR + 7, k0z + 1, LAMP)
    for x in range(k0x + 3, k1x - 2, 6):  # lámparas del techo
        lantern(w, x, FLOOR + 9, (k0z + k1z) // 2, hanging=True)
    # cuartos del segundo piso: biblioteca y dormitorio real
    w.fill(k0x + 2, FLOOR + 12, k0z + 1, k0x + 12, FLOOR + 14, k0z + 1, M + "bookshelf")
    w.set(k0x + 6, FLOOR + 12, k0z + 6, M + "enchanting_table")
    bed(w, k1x - 4, FLOOR + 12, k0z + 2, "north", "red")
    bed(w, k1x - 5, FLOOR + 12, k0z + 2, "north", "red")
    w.chest(k1x - 2, FLOOR + 12, k0z + 1, "south", "minecraft:chests/bastion_treasure")
    w.fill(C - 1, FLOOR + 11, k0z + 8, C + 1, FLOOR + 11, k0z + 10, LAMP)
    for y in range(FLOOR, FLOOR + 12):  # escalera de mano a los pisos
        w.set(k0x + 1, y, k1z - 1, M + "ladder", facing="north", waterlogged="false")
    w.clear(k0x + 1, FLOOR + 11, k1z - 1)
    w.set(k0x + 1, FLOOR + 11, k1z - 1, M + "ladder", facing="north", waterlogged="false")
    for y in range(FLOOR + 12, FLOOR + hk + 1):
        w.set(k0x + 1, y, k1z - 1, M + "ladder", facing="north", waterlogged="false")
    # torres del torreón en sus esquinas
    for (tx, tz) in [(k0x - 3, k0z - 3), (k1x - 3, k0z - 3), (k0x - 3, k1z - 3), (k1x - 3, k1z - 3)]:
        tower(w, tx, tz, 7, 32, rnd)
    # gran torre central (donjon) con aguja
    d0x, d0z, ds = C - 5, 25, 11
    for y in range(FLOOR + hk, FLOOR + hk + 22):
        for x in range(d0x, d0x + ds):
            for z in (d0z, d0z + ds - 1):
                w.set(x, y, z, PBB)
        for z in range(d0z, d0z + ds):
            for x in (d0x, d0x + ds - 1):
                w.set(x, y, z, PBB)
    for (x, z) in [(d0x, d0z), (d0x + ds - 1, d0z), (d0x, d0z + ds - 1), (d0x + ds - 1, d0z + ds - 1)]:
        w.fill(x, FLOOR + hk, z, x, FLOOR + hk + 24, z, RNB)
        w.set(x, FLOOR + hk + 25, z, LAMP)
    for y in range(FLOOR + hk + 4, FLOOR + hk + 20, 6):
        for (x, z) in [(C, d0z), (C, d0z + ds - 1), (d0x, d0z + ds // 2), (d0x + ds - 1, d0z + ds // 2)]:
            w.fill(x, y, z, x, y + 2, z, GLASS)
    pyramid_roof(w, d0x, d0z, ds, FLOOR + hk + 22, M + "red_nether_brick_stairs", RNB)
    top = FLOOR + hk + 22 + ds // 2 + 2
    w.fill(C, top, d0z + ds // 2, C, min(SY - 3, top + 6), d0z + ds // 2, GOLD)
    w.set(C, min(SY - 2, top + 7), d0z + ds // 2, RUBY)
    # jardines del patio: árboles carmesí y distorsionados, fuente pequeña, huerto real
    for (x, z, warped) in [(66, 48, False), (70, 52, True), (110, 48, False), (106, 52, True), (66, 18, True), (110, 18, False)]:
        crimson_tree(w, x, z, rnd, warped=warped)
    for x in range(64, 70):
        for z in range(24, 40, 2):
            w.set(x, FLOOR - 1, z, SOULSAND)
            w.set(x, FLOOR, z, M + "nether_wart", age=str(rnd.randint(2, 3)))
    # pozo con lava rodeado de obsidiana
    w.fill(108, FLOOR - 1, 28, 112, FLOOR - 1, 32, OBS)
    w.fill(109, FLOOR - 1, 29, 111, FLOOR - 1, 31, M + "lava")
    for (x, z) in [(108, 28), (112, 28), (108, 32), (112, 32)]:
        w.fill(x, FLOOR, z, x, FLOOR + 2, z, PB)
    w.fill(108, FLOOR + 3, 28, 112, FLOOR + 3, 32, M + "polished_blackstone_slab", type="bottom", waterlogged="false")
    # nido del dragón en el patio
    nx, nz = 76, 50
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if dx or dz:
                w.set(nx + dx, FLOOR - 1, nz + dz, SOULSOIL)
                slab(w, nx + dx, FLOOR, nz + dz, M + "blackstone_slab")
    w.set(nx, FLOOR - 1, nz, MAGMA)
    w.entity(nx, FLOOR, nz, R + "dragon_egg")
    return (C, FLOOR + 2, k0z + 2), (k0z, k1z)


def plaza(w, rnd):
    """Plaza central (x 66-110, z 62-88): fuente de lava y fuego de almas, estatuas, bancos y árboles."""
    px0, px1, pz0, pz1 = 66, 110, 62, 88
    cz = (pz0 + pz1) // 2
    for x in range(px0, px1 + 1):
        for z in range(pz0, pz1 + 1):
            d = max(abs(x - C), abs(z - cz))
            w.set(x, FLOOR - 1, z, RNB if d % 6 == 0 else (PB if (x + z) % 2 else PBB))
    # fuente
    w.fill(C - 5, FLOOR - 1, cz - 5, C + 5, FLOOR, cz + 5, PB)
    w.fill(C - 4, FLOOR - 1, cz - 4, C + 4, FLOOR - 1, cz + 4, OBS)
    w.fill(C - 4, FLOOR, cz - 4, C + 4, FLOOR, cz + 4, M + "lava")
    w.fill(C - 1, FLOOR - 1, cz - 1, C + 1, FLOOR + 3, cz + 1, CPB)
    w.fill(C - 1, FLOOR + 4, cz - 1, C + 1, FLOOR + 4, cz + 1, GOLD)
    w.set(C, FLOOR + 5, cz, SOULSOIL)
    w.set(C, FLOOR + 6, cz, M + "soul_fire")
    for (dx, dz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        w.set(C + dx, FLOOR + 5, cz + dz, LAMP)
    # estatuas de guerreros en las 4 esquinas
    for (sx, sz) in [(px0 + 4, pz0 + 4), (px1 - 4, pz0 + 4), (px0 + 4, pz1 - 4), (px1 - 4, pz1 - 4)]:
        w.fill(sx - 1, FLOOR, sz - 1, sx + 1, FLOOR, sz + 1, PBB)
        w.fill(sx, FLOOR + 1, sz, sx, FLOOR + 2, sz, BS)          # piernas
        w.fill(sx, FLOOR + 3, sz, sx, FLOOR + 4, sz, GB)          # torso
        w.set(sx - 1, FLOOR + 4, sz, BS)
        w.set(sx + 1, FLOOR + 4, sz, BS)
        w.set(sx, FLOOR + 5, sz, M + "wither_skeleton_skull", rotation="0")
        w.fill(sx + 1, FLOOR + 5, sz, sx + 1, FLOOR + 7, sz, RUBY)   # espada de rubí
    # bancos, faroles y árboles alrededor
    for x in range(px0 + 8, px1 - 7, 6):
        for (z, f) in [(pz0 + 2, "south"), (pz1 - 2, "north")]:
            stairs(w, x, FLOOR, z, M + "crimson_stairs", OPP[f])
            stairs(w, x + 1, FLOOR, z, M + "crimson_stairs", OPP[f])
            lamp_post(w, x + 3, z, 3)
    for (x, z) in [(px0 + 2, cz - 6), (px0 + 2, cz + 6), (px1 - 2, cz - 6), (px1 - 2, cz + 6)]:
        crimson_tree(w, x, z, rnd, warped=(x > C))


def avenues(w):
    """Avenidas: sur (plaza → puerta sur), este-oeste (puerta oeste → puerta este) y calles de cada barrio."""
    def road(x0, z0, x1, z1, core=RNB, edge=PBB):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for z in range(min(z0, z1), max(z0, z1) + 1):
                if w.get(x, FLOOR - 1, z) is None:
                    w.set(x, FLOOR - 1, z, core)
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for z in (min(z0, z1), max(z0, z1)):
                w.set(x, FLOOR - 1, z, edge)
    road(C - 3, 88, C + 3, WALL1 - 1)            # avenida sur
    road(WALL0 + 3, C - 3, 66, C + 3)            # avenida oeste
    road(110, C - 3, WALL1 - 3, C + 3)           # avenida este
    road(C - 3, WALL0 + 3, C + 3, 12)            # salida norte (detrás del castillo)
    for z in range(96, WALL1 - 3, 8):            # faroles de la avenida sur
        lamp_post(w, C - 5, z, 4)
        lamp_post(w, C + 5, z, 4)
    for x in list(range(WALL0 + 8, 64, 8)) + list(range(114, WALL1 - 4, 8)):
        lamp_post(w, x, C - 5, 4)
        lamp_post(w, x, C + 5, 4)
    return road


# ====================================================================== DISTRITOS
def residential(w, rnd, road):
    """Barrio residencial (sur): calles con muchas casas de 1 y 2 pisos, huertos de verruga y pozos."""
    houses = 0
    # calles transversales
    for zr in (106, 128, 150):
        road(WALL0 + 3, zr, WALL1 - 3, zr + 2, NB, PBB)
    for xr in (34, 60, 116, 142):
        road(xr, 106, xr + 2, WALL1 - 3, NB, PBB)
    blocks_x = [(17, 33), (37, 59), (63, C - 5), (C + 5, 115), (119, 141), (145, 157)]
    # junto a la avenida este-oeste (z 93-104) solo hay casas en el centro: a los lados están almacenes y mercado
    blocks_z = [(93, 104), (109, 127), (131, 149), (153, 158)]
    for (bx0, bx1) in blocks_x:
        for (bz0, bz1) in blocks_z:
            if bz0 == 93 and not (63 <= bx0 <= C + 5):
                continue
            x = bx0 + 1
            while x + 6 <= bx1:
                wd = rnd.randint(5, 8)
                if x + wd - 1 > bx1:
                    break
                dp = rnd.randint(6, 8)
                floors = 2 if rnd.random() < 0.4 else 1
                depth = bz1 - bz0 + 1
                if depth < dp + 1 and depth - 1 >= 5:
                    dp = depth - 1
                if bz1 - bz0 + 1 >= 2 * dp + 2:
                    house(w, x, bz0 + 1, wd, dp, "north", rnd, floors)
                    house(w, x, bz1 - dp, wd, dp, "south", rnd, 2 if rnd.random() < 0.35 else 1)
                    houses += 2
                elif bz1 - bz0 + 1 >= dp + 1:
                    side = "north" if rnd.random() < 0.5 else "south"
                    zz = bz0 + 1 if side == "north" else bz1 - dp
                    if rnd.random() < 0.15:
                        farm(w, x, bz0 + 1, wd, bz1 - bz0 - 1, rnd)
                    else:
                        house(w, x, zz, wd, dp, side, rnd, floors)
                        houses += 1
                x += wd + rnd.randint(1, 2)
    return houses


def farm(w, x0, z0, wd, dp, rnd):
    w.walls(x0, FLOOR - 1, z0, x0 + wd - 1, FLOOR - 1, z0 + dp - 1, CPL)
    for x in range(x0 + 1, x0 + wd - 1):
        for z in range(z0 + 1, z0 + dp - 1):
            w.set(x, FLOOR - 1, z, SOULSAND)
            w.set(x, FLOOR, z, M + "nether_wart", age=str(rnd.randint(1, 3)))
    w.set(x0 + wd // 2, FLOOR - 1, z0 + dp // 2, SHROOM)
    w.clear(x0 + wd // 2, FLOOR, z0 + dp // 2)


def commercial(w, rnd):
    """Distrito comercial (este, x 114-158, z 62-104): tiendas de 2 pisos, puestos a ambos lados de la avenida
    y una fila más de puestos en la plaza del mercado."""
    for x in (114, 125, 136, 147):
        shop(w, x, 68, rnd, "south")
    for x in range(114, 152, 7):
        stall(w, x, C - 9, rnd, "south")
        stall(w, x, C + 6, rnd, "north")
        stall(w, x + 3, C + 12, rnd, "north")
    for x in range(116, 156, 10):
        lamp_post(w, x, C + 11, 3)


def workshops(w, rnd):
    """Distrito de talleres y almacenes (oeste, x 12-62, z 62-88)."""
    kinds = ["herreria", "alquimia", "carpinteria", "fundicion"]
    x = 14
    for i, k in enumerate(kinds):
        workshop(w, x, 70, k, rnd, "south")
        x += 13
    warehouse(w, 17, C + 6, 18, 10, rnd, "north")
    warehouse(w, 39, C + 6, 22, 10, rnd, "north")
    # patio de carga entre almacenes
    for (x, z) in [(36, C + 8), (37, C + 12), (62, C + 9)]:
        for y in range(rnd.randint(1, 3)):
            w.set(x, FLOOR + y, z, M + "barrel", facing="up", open="false")
    w.set(62, FLOOR, C + 12, M + "hay_block", axis="y")


def military(w, rnd):
    """Zona militar (noreste, x 120-164, z 12-58): cuarteles, armería, patio de entrenamiento, campo de tiro y torres."""
    # cuartel 1 (largo, con literas)
    bx0, bz0, bw, bd = 122, 17, 26, 10
    house(w, bx0, bz0, bw, bd, "south", rnd, floors=1, style=(PBB, RNB, M + "nether_brick_stairs", NB, M + "nether_brick_slab", PB), chimney=False)
    for x in range(bx0 + 2, bx0 + bw - 2, 3):
        w.set(x, FLOOR, bz0 + 1, M + "red_bed", facing="north", part="head", occupied="false")
        w.set(x, FLOOR, bz0 + 2, M + "red_bed", facing="north", part="foot", occupied="false")
        w.chest(x + 1, FLOOR, bz0 + 1, "south", "minecraft:chests/village/village_weaponsmith", block="barrel")
    # cuartel 2
    house(w, 122, 31, 20, 9, "north", rnd, floors=2, style=(PBB, RNB, M + "red_nether_brick_stairs", RNB, M + "red_nether_brick_slab", PB), chimney=True)
    # armería
    ax0, az0 = 146, 31
    house(w, ax0, az0, 14, 10, "west", rnd, floors=1, style=(RBR, PB, M + "polished_blackstone_brick_stairs", PBB, M + "polished_blackstone_brick_slab", PB), chimney=False)
    for x in range(ax0 + 2, ax0 + 12, 2):
        w.set(x, FLOOR, az0 + 1, M + "anvil", facing="east")
        w.chest(x + 1, FLOOR, az0 + 8, "north", rnd.choice(["minecraft:chests/village/village_armorer", "minecraft:chests/village/village_weaponsmith"]))
    w.set(ax0 + 3, FLOOR, az0 + 5, M + "smithing_table")
    w.set(ax0 + 4, FLOOR, az0 + 5, M + "grindstone", face="floor", facing="north")
    # patio de entrenamiento: arena, muñecos (dianas) y fardos
    tx0, tz0 = 122, 45
    w.walls(tx0, FLOOR, tz0, tx0 + 22, FLOOR, tz0 + 12, M + "crimson_fence", north="false", south="false", east="false",
            west="false", waterlogged="false")
    for x in range(tx0 + 1, tx0 + 22):
        for z in range(tz0 + 1, tz0 + 12):
            w.set(x, FLOOR - 1, z, SOULSOIL if (x + z) % 3 else BS)
    for x in range(tx0 + 3, tx0 + 21, 4):
        w.set(x, FLOOR, tz0 + 4, M + "hay_block", axis="y")
        w.set(x, FLOOR + 1, tz0 + 4, M + "target", power="0")
        w.set(x, FLOOR + 2, tz0 + 4, M + "carved_pumpkin", facing="south")
    for x in range(tx0 + 3, tx0 + 21, 6):
        w.set(x, FLOOR, tz0 + 9, M + "hay_block", axis="x")
    # campo de tiro con dianas en la pared norte
    for x in range(148, 162, 3):
        w.set(x, FLOOR + 1, 18, M + "target", power="0")
        w.set(x, FLOOR, 18, M + "hay_block", axis="y")
    # torres de vigilancia de la zona militar
    tower(w, 150, 46, 7, 18, rnd, door_side="west")
    # estandartes
    for x in range(124, 146, 6):
        w.set(x, FLOOR + 3, 27, M + "red_wall_banner", facing="south")


def mountains(w, rnd):
    """Montañas y minas (noroeste, x 11-58, z 11-58): picos de basalto y piedra negra, vetas de minerales,
    túneles de mina con rieles y soportes, y un campamento minero."""
    x0, x1, z0, z1 = 11, 57, 11, 57
    peaks = [(24, 22, 44, 9), (44, 17, 32, 8), (17, 44, 30, 8), (38, 38, 20, 7), (30, 50, 14, 6)]
    heights = {}
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            h = 0.0
            for (px, pz, ph, pr) in peaks:
                d = math.hypot(x - px, z - pz)
                h = max(h, ph * math.exp(-(d / (pr * 1.5)) ** 1.6))
            h += 1.5 * math.sin(x * 0.7) * math.cos(z * 0.6) + rnd.random() * 1.2
            # bajar hacia el campamento (sureste de la zona)
            if x > 40 and z > 44:
                h *= 0.2
            heights[(x, z)] = int(max(0, h))
    tunnels = set()
    # túnel 1: del campamento hacia el oeste (z 50-52), túnel 2: hacia el norte (x 46-48)
    for x in range(14, 50):
        for z in range(49, 52):
            tunnels.add((x, z))
    for z in range(14, 52):
        for x in range(45, 48):
            tunnels.add((x, z))
    for x in range(22, 47):  # galería transversal
        for z in range(27, 30):
            tunnels.add((x, z))
    for (x, z), h in heights.items():
        for y in range(FLOOR, FLOOR + h):
            dy = y - FLOOR
            if (x, z) in tunnels and dy < 4:
                continue
            top = dy >= h - 2
            r = rnd.random()
            if top:
                block = RAWBASALT if r < 0.45 else (BS if r < 0.8 else NR)
                props = {"axis": "y"} if block == RAWBASALT else {}
            elif r < 0.035:
                block, props = M + "nether_gold_ore", {}
            elif r < 0.07:
                block, props = M + "nether_quartz_ore", {}
            elif r < 0.085:
                block, props = RORE, {}
            elif r < 0.088:
                block, props = M + "ancient_debris", {}
            else:
                block, props = (NR if r < 0.6 else BS), {}
            w.set(x, y, z, block, **props)
    # soportes, rieles y faroles de los túneles
    def support(x, z, along_x):
        if along_x:
            for zz in (z - 1, z + 1):
                w.fill(x, FLOOR, zz, x, FLOOR + 2, zz, CST, axis="y")
            w.fill(x, FLOOR + 3, z - 1, x, FLOOR + 3, z + 1, CST, axis="z")
            lantern(w, x, FLOOR + 2, z, hanging=True)
        else:
            for xx in (x - 1, x + 1):
                w.fill(xx, FLOOR, z, xx, FLOOR + 2, z, CST, axis="y")
            w.fill(x - 1, FLOOR + 3, z, x + 1, FLOOR + 3, z, CST, axis="x")
            lantern(w, x, FLOOR + 2, z, hanging=True)
    for x in range(16, 50):
        if heights.get((x, 50), 0) > 4:
            w.set(x, FLOOR, 50, M + "rail", shape="east_west", waterlogged="false")
            if x % 5 == 0:
                support(x, 50, True)
    for z in range(15, 50):
        if heights.get((46, z), 0) > 4:
            w.set(46, FLOOR, z, M + "rail", shape="north_south", waterlogged="false")
            if z % 5 == 0:
                support(46, z, False)
    for x in range(23, 46):
        if heights.get((x, 28), 0) > 4 and x % 6 == 0:
            support(x, 28, True)
    # vetas brillantes y cofres de minero al fondo de los túneles
    w.chest(15, FLOOR, 50, "east", "minecraft:chests/abandoned_mineshaft")
    w.chest(46, FLOOR, 15, "south", "minecraft:chests/abandoned_mineshaft")
    w.chest(23, FLOOR, 28, "east", "minecraft:chests/abandoned_mineshaft")
    # campamento minero (sureste de la zona): cabañas, montones de mineral, grúa y fundición
    house(w, 49, 52, 7, 6, "west", rnd, 1, style=HOUSE_STYLES[4])
    house(w, 50, 43, 6, 6, "west", rnd, 1, style=HOUSE_STYLES[1])
    for (x, z, b) in [(42, 46, M + "raw_gold_block"), (43, 46, M + "raw_gold_block"), (42, 47, M + "quartz_block"),
                      (44, 47, M + "raw_iron_block"), (43, 47, RORE)]:
        w.set(x, FLOOR, z, b)
    w.set(42, FLOOR + 1, 46, M + "raw_gold_block")
    # grúa sobre un montón de mineral
    w.fill(45, FLOOR, 56, 45, FLOOR + 7, 56, CST, axis="y")
    w.fill(41, FLOOR + 8, 56, 45, FLOOR + 8, 56, CST, axis="x")
    for y in range(FLOOR + 4, FLOOR + 8):
        w.set(41, y, 56, M + "chain", axis="y", waterlogged="false")
    w.set(41, FLOOR + 3, 56, M + "barrel", facing="up", open="false")
    w.fill(42, FLOOR, 58, 43, FLOOR, 58, M + "blast_furnace", facing="north", lit="true")
    # torre de vigilancia en el pico más alto y un puente colgante entre dos picos
    pk = (24, 22)
    ph = heights[pk]
    w.fill(pk[0] - 1, FLOOR + ph, pk[1] - 1, pk[0] + 1, FLOOR + ph + 5, pk[1] + 1, PBB)
    w.fill(pk[0] - 2, FLOOR + ph + 6, pk[1] - 2, pk[0] + 2, FLOOR + ph + 6, pk[1] + 2, PB)
    w.set(pk[0], FLOOR + ph + 7, pk[1], LAMP)
    for (x, z) in [(pk[0] - 2, pk[1] - 2), (pk[0] + 2, pk[1] - 2), (pk[0] - 2, pk[1] + 2), (pk[0] + 2, pk[1] + 2)]:
        w.set(x, FLOOR + ph + 7, z, PBB)
    p2 = (44, 18)
    h2 = heights[p2]
    yb = FLOOR + min(ph, h2) + 2
    for x in range(pk[0] + 2, p2[0] - 1):
        z = round(pk[1] + (p2[1] - pk[1]) * (x - pk[0]) / (p2[0] - pk[0]))
        slab(w, x, yb, z, M + "crimson_slab")
    return heights


def residents(w, throne, rnd, towers):
    E = R
    G_, A_ = E + "guerrero", E + "arquero"
    w.entity(throne[0], throne[1], throne[2], E + "rey_necromancer")
    for (x, z) in [(C - 3, 26), (C + 3, 26), (C - 3, 34), (C + 3, 34), (C - 4, 41), (C + 4, 41)]:
        w.entity(x, FLOOR, z, G_)
    for (x, z) in [(C - 4, 60), (C + 4, 60)]:  # puerta del castillo
        w.entity(x, FLOOR, z, G_)
    for (gx, gz) in [(C - 5, WALL1 - 4), (C + 5, WALL1 - 4), (C - 5, WALL0 + 4), (C + 5, WALL0 + 4),
                     (WALL0 + 4, C - 5), (WALL0 + 4, C + 5), (WALL1 - 4, C - 5), (WALL1 - 4, C + 5)]:
        w.entity(gx, FLOOR, gz, G_)
    for (x, y, z) in towers[::2]:
        w.entity(x, y, z, A_)
    for (x, z) in [(130, 51), (136, 51), (142, 51), (126, 41), (150, 23), (154, 23)]:  # zona militar
        w.entity(x, FLOOR, z, G_ if x % 2 == 0 else A_)
    for (x, z) in [(80, 70), (96, 80), (C, 100), (C, 130), (C, 152), (40, C), (130, C), (150, C), (30, 80), (48, 129),
                   (122, 151), (52, 50)]:  # calles
        w.entity(x, FLOOR, z, G_ if rnd.random() < 0.6 else A_)


def build():
    rnd = random.Random(1408)
    w = World()
    outskirts(w, rnd)
    road = avenues(w)
    throne, _ = castle(w, rnd)
    plaza(w, rnd)
    towers = outer_walls(w, rnd)
    mountains(w, rnd)
    military(w, rnd)
    workshops(w, rnd)
    commercial(w, rnd)
    houses = residential(w, rnd, road)
    residents(w, throne, rnd, towers)
    w.houses = houses
    return w


def save(w, path):
    palette, pidx, blocks = [], {}, []
    for (x, y, z), (name, props) in sorted(w.b.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        key = (name, props)
        if key not in pidx:
            pidx[key] = len(palette)
            entry = {"Name": name}
            if props:
                entry["Properties"] = {k: v for k, v in props}
            palette.append(entry)
        entry = {"pos": ListOf(3, [Int(x), Int(y), Int(z)]), "state": Int(pidx[key])}
        if (x, y, z) in w.nbt:
            entry["nbt"] = w.nbt[(x, y, z)]
        blocks.append(entry)
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


if __name__ == "__main__":
    w, info = write_all()
    print("capital: %d bloques, %d tipos, %d habitantes, %d casas" % (info + (w.houses,)))
