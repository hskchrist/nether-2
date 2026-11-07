"""Reino Humano del Nether (192 x 192 bloques), igual a la imagen del usuario, en medio del Océano Púrpura.

Plano (como el "Plano General" de la imagen): ciudad redonda sobre una isla de piedra negra, con muralla y 12 torres,
un foso de lava con puentes, plaza central con fuente de lava y avenidas hacia las puertas. El castillo con el
Salón del Rey ocupa el norte.

Salas (las de la imagen): Plaza Central, Viviendas, Mercado Infernal, Templo de Fuego, Biblioteca, Sala de Herrería,
Sala de Control, Dormitorios Comunes, Sala de Comida, Granjas del Nether, Sala de Pesca Magmática, Sala de Defensa,
Laboratorio Arcano, Sala de Guardianes, Puentes, Jardines del Nether, Torres de Vigilancia y el Salón del Rey.

La plantilla no guarda aire: el mod (CapitalPiece.java) excava, pone la isla y el agua del Nether alrededor.
"""
import math
import os
import random

from common import DATA, MODID
from structure import Byte, Int, Double, Float, ListOf, write_nbt, DATA_VERSION

String = str
from capital import stairs, slab, lantern, crimson_tree, OPP, STEP

SX, SY, SZ = 192, 80, 192
C = 96
FLOOR = 4
R_WALL0, R_WALL1 = 81, 84      # muralla
R_MOAT0, R_MOAT1 = 60, 63      # foso de lava
AVE = 3                        # media anchura de las avenidas

M = "minecraft:"
R = MODID + ":"
PBB = M + "polished_blackstone_bricks"
CPBB = M + "cracked_polished_blackstone_bricks"
PB = M + "polished_blackstone"
CPB = M + "chiseled_polished_blackstone"
BS = M + "blackstone"
GB = M + "gilded_blackstone"
BASALT = M + "polished_basalt"
RNB = M + "red_nether_bricks"
NB = M + "nether_bricks"
MAGMA = M + "magma_block"
OBS = M + "obsidian"
CRY = M + "crying_obsidian"
GOLD = M + "gold_block"
RTERRA = M + "red_terracotta"
NWB = M + "nether_wart_block"
NYL = M + "crimson_nylium"
WNYL = M + "warped_nylium"
GLASS = M + "red_stained_glass"
SHROOM = M + "shroomlight"
QUARTZ = M + "quartz_block"
LAMP = R + "ruby_lamp"
RUBY = R + "ruby_block"
CPL = M + "crimson_planks"
LOOT = ["minecraft:chests/bastion_other", "minecraft:chests/nether_bridge", "minecraft:chests/village/village_weaponsmith",
        "minecraft:chests/village/village_armorer", "minecraft:chests/village/village_toolsmith"]
# Estandarte del reino: el tridente blanco (Ψ) sobre rojo, como en la imagen
PSI = [("white", "minecraft:stripe_left"), ("white", "minecraft:stripe_right"), ("white", "minecraft:stripe_center"),
       ("red", "minecraft:half_horizontal_bottom"), ("white", "minecraft:stripe_middle"), ("white", "minecraft:stripe_center")]


class World:
    def __init__(self):
        self.b = {}
        self.nbt = {}
        self.ents = []
        self.residents = 0
        self.villagers = 0

    def set(self, x, y, z, name, **props):
        if 0 <= x < SX and 0 <= y < SY and 0 <= z < SZ:
            self.b[(x, y, z)] = (name, tuple(sorted((k, str(v)) for k, v in props.items())))
            self.nbt.pop((x, y, z), None)

    def clear(self, x, y, z):
        self.b.pop((x, y, z), None)
        self.nbt.pop((x, y, z), None)

    def get(self, x, y, z):
        return self.b.get((x, y, z), (None,))[0]

    def fill(self, x0, y0, z0, x1, y1, z1, name, **p):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, name, **p)

    def clear_box(self, x0, y0, z0, x1, y1, z1):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.clear(x, y, z)

    def chest(self, x, y, z, facing, loot, barrel=False):
        if barrel:
            self.set(x, y, z, M + "barrel", facing="up", open="false")
        else:
            self.set(x, y, z, M + "chest", facing=facing, type="single", waterlogged="false")
        self.nbt[(x, y, z)] = {"LootTable": String(loot)}

    def banner(self, x, y, z, facing):
        """Estandarte de pared rojo con el emblema del reino (mira hacia 'facing')."""
        self.set(x, y, z, M + "red_wall_banner", facing=facing)
        self.nbt[(x, y, z)] = {"patterns": ListOf(10, [{"color": String(c), "pattern": String(p)} for c, p in PSI])}

    def banner_post(self, x, y, z, rotation=0):
        self.set(x, y, z, M + "red_banner", rotation=rotation)
        self.nbt[(x, y, z)] = {"patterns": ListOf(10, [{"color": String(c), "pattern": String(p)} for c, p in PSI])}

    def entity(self, x, y, z, eid, extra=None):
        nbt = {"id": String(eid), "PersistenceRequired": Byte(1)}
        if extra:
            nbt.update(extra)
        self.ents.append((x + 0.5, float(y), z + 0.5, nbt))

    def human(self, x, y, z, kind, rnd, female=None, skins=1):
        """Habitante del reino con su género y su skin ya elegidos."""
        if female is None:
            female = rnd.random() < 0.5
        self.entity(x, y, z, R + kind, {"Female": Byte(1 if female else 0), "Variant": Int(rnd.randrange(skins)),
                                         "GenderSet": Byte(1)})
        self.residents += 1

    def villager(self, x, y, z, profession):
        """Aldeano del Nether (aldeano vanilla de tipo Nether) que ya tiene su oficio: con 1 de experiencia no lo pierde
        y busca sola su mesa de trabajo de la sala (la que corresponde a su profesión)."""
        self.entity(x, y, z, M + "villager", {"VillagerData": {"type": String(R + "nether"), "profession": String(profession),
                                                               "level": Int(1)}, "Xp": Int(1)})
        self.villagers += 1

    def armor_stand(self, x, y, z, rot, armor, hand=None):
        items = [{"id": String(a), "count": Int(1)} if a else {} for a in armor]
        hands = [{"id": String(hand), "count": Int(1)} if hand else {}, {}]
        self.ents.append((x + 0.5, float(y), z + 0.5, {"id": String(M + "armor_stand"), "ShowArms": Byte(1), "NoBasePlate": Byte(0),
                                                        "ArmorItems": ListOf(10, items), "HandItems": ListOf(10, hands),
                                                        "Rotation": ListOf(5, [Float(rot), Float(0.0)])}))


SKINS = {"bibliotecario": (3, 3), "domador": (3, 3), "granjero": (4, 4), "minero": (6, 5), "ciudadano": (1, 1)}


def dist(x, z):
    return math.hypot(x + 0.5 - C, z + 0.5 - C)


def wall_material(rnd, base=PBB):
    k = rnd.random()
    if k < 0.08:
        return CPBB
    if k < 0.14:
        return BS
    return base


def door(w, x, y, z, facing, block="crimson_door"):
    w.set(x, y, z, M + block, facing=facing, half="lower", hinge="left", open="false", powered="false")
    w.set(x, y + 1, z, M + block, facing=facing, half="upper", hinge="left", open="false", powered="false")


def nether_bed(w, x, y, z, facing):
    """Cama del Nether del mod (la cabecera hacia 'facing')."""
    dx, dz = STEP[facing]
    w.set(x, y, z, R + "nether_bed", facing=facing, part="foot", occupied="false")
    w.set(x + dx, y, z + dz, R + "nether_bed", facing=facing, part="head", occupied="false")


def station(w, x, y, z, name, facing):
    w.set(x, y, z, R + name, facing=facing)


def free(w, x, z):
    return w.get(x, FLOOR, z) is None and w.get(x, FLOOR + 1, z) is None and w.get(x, FLOOR - 1, z) is not None


def job(w, prof, spots, station_name=None, facing="south", count=1):
    """Pone la mesa (si es del mod) en el primer lugar libre de 'spots' y a 'count' aldeanos del Nether al lado."""
    placed = None
    for (x, z) in spots:
        if station_name is None or free(w, x, z):
            if station_name:
                station(w, x, FLOOR, z, station_name, facing)
            placed = (x, z)
            break
    if placed is None:
        return
    x, z = placed
    n = 0
    for dx, dz in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1), (0, 2), (2, 0), (-2, 0), (0, -2)):
        if n >= count:
            break
        if free(w, x + dx, z + dz):
            w.villager(x + dx, FLOOR, z + dz, prof)
            n += 1


def lamp_post(w, x, z, h=3, top=LAMP):
    w.fill(x, FLOOR, z, x, FLOOR + h - 1, z, PB)
    w.set(x, FLOOR + h, z, top)


def campfire(w, x, y, z, soul=False):
    w.set(x, y, z, M + ("soul_campfire" if soul else "campfire"), facing="north", lit="true", signal_fire="false", waterlogged="false")


# ====================================================================== salas: caparazón común
def hall(w, x0, z0, x1, z1, h, door_side, rnd, roof="flat", floor=PB, wall=PBB, windows=True, door_w=2):
    """Edificio rectangular de piedra negra con pilares de basalto, ventanas rojas, puerta y techo.
    Devuelve (interior x0, z0, x1, z1, y del techo)."""
    top = FLOOR + h - 1
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.set(x, FLOOR - 1, z, floor)
            edge = x in (x0, x1) or z in (z0, z1)
            corner = x in (x0, x1) and z in (z0, z1)
            for y in range(FLOOR, top + 1):
                if corner:
                    w.set(x, y, z, BASALT, axis="y")
                elif edge:
                    if y == FLOOR:
                        w.set(x, y, z, BS)
                    elif y == top:
                        w.set(x, y, z, CPB)
                    else:
                        w.set(x, y, z, wall_material(rnd, wall))
            w.set(x, top + 1, z, PBB if edge else PB)
    # pilares de basalto cada 5 y ventanas entre ellos
    for x in range(x0 + 5, x1, 5):
        for z in (z0, z1):
            w.fill(x, FLOOR, z, x, top, z, BASALT, axis="y")
    for z in range(z0 + 5, z1, 5):
        for x in (x0, x1):
            w.fill(x, FLOOR, z, x, top, z, BASALT, axis="y")
    if windows and h >= 5:
        for x in range(x0 + 2, x1 - 1, 5):
            for z in (z0, z1):
                w.fill(x, FLOOR + 2, z, x + 1, min(top - 1, FLOOR + 4), z, GLASS)
        for z in range(z0 + 2, z1 - 1, 5):
            for x in (x0, x1):
                w.fill(x, FLOOR + 2, z, x, min(top - 1, FLOOR + 4), z + 1, GLASS)
    # puerta
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    if door_side in ("north", "south"):
        z = z0 if door_side == "north" else z1
        for i in range(door_w):
            w.clear_box(cx - door_w // 2 + i, FLOOR, z, cx - door_w // 2 + i, FLOOR + 2, z)
        for i in range(door_w):
            door(w, cx - door_w // 2 + i, FLOOR, z, door_side if door_side == "south" else "north")
        w.banner(cx - door_w // 2 - 1, FLOOR + 3, z + (1 if door_side == "south" else -1), door_side)
        w.banner(cx + door_w - door_w // 2, FLOOR + 3, z + (1 if door_side == "south" else -1), door_side)
        lantern(w, cx - door_w // 2 - 1, FLOOR + 1, z + (1 if door_side == "south" else -1), hanging=False)
    else:
        x = x0 if door_side == "west" else x1
        for i in range(door_w):
            w.clear_box(x, FLOOR, cz - door_w // 2 + i, x, FLOOR + 2, cz - door_w // 2 + i)
        for i in range(door_w):
            door(w, x, FLOOR, cz - door_w // 2 + i, door_side)
        w.banner(x + (1 if door_side == "east" else -1), FLOOR + 3, cz - door_w // 2 - 1, door_side)
        w.banner(x + (1 if door_side == "east" else -1), FLOOR + 3, cz + door_w - door_w // 2, door_side)
    # luz: lámparas colgantes y focos en el techo
    for x in range(x0 + 2, x1 - 1, 4):
        for z in range(z0 + 2, z1 - 1, 4):
            w.set(x, top + 1, z, SHROOM)
            if h >= 6:
                w.set(x, top, z, M + "chain", axis="y")
                lantern(w, x, top - 1, z, hanging=True)
    # techo
    if roof == "battlement":
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if (x in (x0, x1) or z in (z0, z1)) and (x + z) % 2 == 0:
                    w.set(x, top + 2, z, PBB)
    elif roof == "pyramid":
        y = top + 2
        a0, a1, b0, b1 = x0, x1, z0, z1
        while a0 <= a1 and b0 <= b1:
            for x in range(a0, a1 + 1):
                for z in range(b0, b1 + 1):
                    if x in (a0, a1) or z in (b0, b1):
                        if x == a0 and b0 < z < b1:
                            stairs(w, x, y, z, M + "blackstone_stairs", "east")
                        elif x == a1 and b0 < z < b1:
                            stairs(w, x, y, z, M + "blackstone_stairs", "west")
                        elif z == b0:
                            stairs(w, x, y, z, M + "blackstone_stairs", "south")
                        elif z == b1:
                            stairs(w, x, y, z, M + "blackstone_stairs", "north")
            a0, a1, b0, b1 = a0 + 1, a1 - 1, b0 + 1, b1 - 1
            y += 1
        w.set((x0 + x1) // 2, y, (z0 + z1) // 2, GOLD)
    return (x0 + 1, z0 + 1, x1 - 1, z1 - 1, top)


def door_toward_center(x0, z0, x1, z1):
    cx, cz = (x0 + x1) / 2 - C, (z0 + z1) / 2 - C
    if abs(cx) > abs(cz):
        return "west" if cx > 0 else "east"
    return "north" if cz > 0 else "south"


# ====================================================================== plaza, avenidas, foso, muralla
def plaza(w, rnd):
    for x in range(C - 15, C + 16):
        for z in range(C - 15, C + 16):
            r = dist(x, z)
            if r <= 14.5:
                ring = int(r) % 4
                w.set(x, FLOOR - 1, z, [PB, PBB, BS, GB if (x + z) % 7 == 0 else PBB][ring])
    # fuente de lava con fuego de almas en el centro
    for x in range(C - 4, C + 5):
        for z in range(C - 4, C + 5):
            r = dist(x, z)
            if r <= 4.5:
                w.set(x, FLOOR - 1, z, M + "lava", level=0) if r <= 3.5 else w.set(x, FLOOR, z, PBB)
                if r <= 3.5:
                    w.set(x, FLOOR - 2, z, BS)
    w.fill(C, FLOOR - 1, C, C, FLOOR + 2, C, BASALT, axis="y")
    w.set(C, FLOOR + 3, C, M + "soul_soil")
    w.set(C, FLOOR + 4, C, M + "soul_fire")
    for (dx, dz) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        w.set(C + dx, FLOOR + 2, C + dz, MAGMA)
    # estatuas y estandartes en diagonal, faroles alrededor
    for (dx, dz) in ((-9, -9), (9, -9), (-9, 9), (9, 9)):
        x, z = C + dx, C + dz
        w.fill(x, FLOOR, z, x, FLOOR + 1, z, CPB)
        w.fill(x, FLOOR + 2, z, x, FLOOR + 4, z, BASALT, axis="y")
        w.set(x, FLOOR + 5, z, GOLD)
        w.set(x, FLOOR + 6, z, LAMP)
    for a in range(0, 360, 30):
        x = int(round(C + 12 * math.cos(math.radians(a + 15))))
        z = int(round(C + 12 * math.sin(math.radians(a + 15))))
        lamp_post(w, x, z, 3)
        w.banner_post(x, FLOOR + 4, z, (a // 22) % 16) if False else None
    # bancos
    for a in range(0, 360, 45):
        x = int(round(C + 7 * math.cos(math.radians(a))))
        z = int(round(C + 7 * math.sin(math.radians(a))))
        stairs(w, x, FLOOR, z, M + "crimson_stairs", "north")


def avenues(w, rnd):
    def road(x0, z0, x1, z1):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for z in range(min(z0, z1), max(z0, z1) + 1):
                r = dist(x, z)
                if r < 14.6 or r > R_WALL1 + 1:
                    continue
                along_x = abs(x1 - x0) > abs(z1 - z0)
                off = abs(z - C) if along_x else abs(x - C)
                w.set(x, FLOOR - 1, z, RNB if off <= 1 else (PBB if off == AVE else PB))
    road(C + 14, C - AVE, R_WALL1 + 1 + C, C + AVE)     # este
    road(C - R_WALL1 - 1, C - AVE, C - 14, C + AVE)     # oeste
    road(C - AVE, C + 14, C + AVE, C + R_WALL1 + 1)     # sur
    road(C - AVE, 58, C + AVE, C - 14)                  # norte (al castillo)
    # faroles a los lados
    for d in range(20, 80, 10):
        if R_MOAT0 - 2 <= d <= R_MOAT1 + 2:
            continue
        for (x, z) in ((C + d, C - AVE - 1), (C - d, C + AVE + 1), (C - AVE - 1, C + d)):
            lamp_post(w, x, z, 3)
        if C - d > 60:
            lamp_post(w, C + AVE + 1, C - d, 3)


def moat(w, rnd):
    """Foso de lava con puentes de piedra negra (Puente del Nether) donde cruzan las avenidas."""
    for x in range(SX):
        for z in range(SZ):
            r = dist(x, z)
            if R_MOAT0 <= r <= R_MOAT1:
                if z < 60 and 66 <= x <= 126:   # el castillo
                    continue
                on_avenue = abs(x - C) <= AVE + 1 or abs(z - C) <= AVE + 1
                if on_avenue:
                    continue
                w.set(x, FLOOR - 1, z, M + "lava", level=0)
                w.set(x, FLOOR - 2, z, M + "lava", level=0)
                w.set(x, FLOOR - 3, z, BS)
            elif R_MOAT0 - 1 <= r < R_MOAT0 or R_MOAT1 < r <= R_MOAT1 + 1:
                if not (z < 60 and 66 <= x <= 126) and not (abs(x - C) <= AVE + 1 or abs(z - C) <= AVE + 1):
                    w.set(x, FLOOR, z, M + "polished_blackstone_wall", up="true", north="none", south="none", east="none", west="none",
                          waterlogged="false")
    # puentes: barandas, torrecitas en los extremos y faroles
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1)):
        for d in range(R_MOAT0 - 2, R_MOAT1 + 3):
            for side in (-AVE - 1, AVE + 1):
                x = C + dx * d + (side if dz else 0)
                z = C + dz * d + (side if dx else 0)
                w.set(x, FLOOR, z, M + "polished_blackstone_brick_wall", up="true", north="none", south="none", east="none",
                      west="none", waterlogged="false")
        for d in (R_MOAT0 - 3, R_MOAT1 + 3):
            for side in (-AVE - 2, AVE + 2):
                x = C + dx * d + (side if dz else 0)
                z = C + dz * d + (side if dx else 0)
                w.fill(x, FLOOR, z, x, FLOOR + 5, z, PBB)
                w.set(x, FLOOR + 6, z, MAGMA)
                w.set(x, FLOOR + 7, z, LAMP)
                face = "east" if dz and side < 0 else ("west" if dz else ("south" if side > 0 else "north"))
                bx = x + (STEP[face][0])
                bz = z + (STEP[face][1])
                w.banner(bx, FLOOR + 4, bz, face)


def tower(w, cx, cz, half, h, rnd, roof=True, archers=None, rnd_kind="arquero"):
    x0, x1, z0, z1 = cx - half, cx + half, cz - half, cz + half
    top = FLOOR + h
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1)
            for y in range(FLOOR, top + 1):
                if edge:
                    w.set(x, y, z, BASALT if (x in (x0, x1) and z in (z0, z1)) else wall_material(rnd))
            w.set(x, top + 1, z, PBB)
            w.set(x, FLOOR - 1, z, PB)
            if edge and (x + z) % 2 == 0:
                w.set(x, top + 2, z, PBB)
    # ventanas y franja de magma
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if x in (x0, x1) or z in (z0, z1):
                if (x == cx or z == cz) and not (x in (x0, x1) and z in (z0, z1)):
                    for y in range(FLOOR + 4, top - 2, 6):
                        w.set(x, y, z, GLASS)
                        w.set(x, y + 1, z, GLASS)
                w.set(x, top - 1, z, MAGMA if (x + z) % 3 == 0 else w.get(x, top - 1, z) or PBB)
    # escalera interior
    for y in range(FLOOR, top + 1):
        w.set(cx, y, z0 + 1, M + "ladder", facing="south", waterlogged="false")
    w.clear(cx, top + 1, z0 + 1)
    w.set(cx, top + 1, z0 + 1, M + "polished_blackstone_slab", type="bottom", waterlogged="false") if False else None
    # estandartes en las 4 caras
    for face, (bx, bz) in (("north", (cx, z0 - 1)), ("south", (cx, z1 + 1)), ("west", (x0 - 1, cz)), ("east", (x1 + 1, cz))):
        w.banner(bx, top - 3, bz, face)
    if roof:
        y = top + 3
        a = half
        while a >= 0:
            for x in range(cx - a, cx + a + 1):
                for z in range(cz - a, cz + a + 1):
                    if abs(x - cx) == a or abs(z - cz) == a:
                        w.set(x, y, z, RNB if a % 2 else NB)
            a -= 1
            y += 1
        w.set(cx, y, cz, LAMP)
    if archers is not None:
        archers.append((cx + 1, top + 2, cz + 1, rnd_kind))
    return top


def outer_wall(w, rnd, guards):
    gates = {"east": (1, 0), "south": (0, 1), "west": (-1, 0)}
    hgt = 14
    for x in range(SX):
        for z in range(SZ):
            r = dist(x, z)
            if not (R_WALL0 <= r <= R_WALL1 + 0.5):
                continue
            # aberturas de las puertas
            if (abs(z - C) <= AVE and x > C) or (abs(z - C) <= AVE and x < C) or (abs(x - C) <= AVE and z > C):
                for y in range(FLOOR + 8, FLOOR + hgt + 1):
                    w.set(x, y, z, wall_material(rnd))
                w.set(x, FLOOR - 1, z, PBB)
                continue
            for y in range(FLOOR, FLOOR + hgt + 1):
                if y == FLOOR + 6:
                    w.set(x, y, z, BASALT, axis="y")
                elif y == FLOOR + hgt - 1 and (x + z) % 4 == 0:
                    w.set(x, y, z, MAGMA)
                else:
                    w.set(x, y, z, wall_material(rnd))
            if r > R_WALL1 - 0.6 and (int(math.degrees(math.atan2(z - C, x - C)) * 2) % 2 == 0):
                w.set(x, FLOOR + hgt + 1, z, PBB)
            w.set(x, FLOOR - 1, z, PBB)
    # estandartes en la cara interior de la muralla
    for a in range(0, 360, 10):
        if a in (0, 90, 180, 270) or 235 < a < 305:
            continue
        rr = R_WALL0 - 1
        x = int(round(C + rr * math.cos(math.radians(a))))
        z = int(round(C + rr * math.sin(math.radians(a))))
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        face = ("west" if ca > 0 else "east") if abs(ca) > abs(sa) else ("north" if sa > 0 else "south")
        w.banner(x, FLOOR + 9, z, face)
    # 12 torres
    towers = []
    for k in range(12):
        a = math.radians(k * 30 + 15)
        cx = int(round(C + (R_WALL0 + 1.5) * math.cos(a)))
        cz = int(round(C + (R_WALL0 + 1.5) * math.sin(a)))
        if 66 <= cx <= 126 and cz < 40:
            continue   # detrás del castillo
        tower(w, cx, cz, 4, 22, rnd, archers=guards, rnd_kind="ballestero" if k % 2 else "arquero")
        towers.append((cx, cz))
    # puertas con torreones (la del sur es la gran puerta del reino, con el arco morado de la imagen)
    for name, (dx, dz) in gates.items():
        big = name == "south"
        d = R_WALL0 - 1
        for side in (-AVE - 3, AVE + 3):
            cx = C + dx * (d + 2) + (side if dz else 0)
            cz = C + dz * (d + 2) + (side if dx else 0)
            tower(w, cx, cz, 3 if not big else 4, 18 if not big else 26, rnd, archers=guards if big else None, rnd_kind="ballestero")
        # marco morado de obsidiana llorona sobre el arco
        for t in range(-AVE - 1, AVE + 2):
            for y in range(FLOOR, FLOOR + 9):
                x = C + dx * R_WALL0 + (t if dz else 0)
                z = C + dz * R_WALL0 + (t if dx else 0)
                if abs(t) == AVE + 1 or y == FLOOR + 8:
                    w.set(x, y, z, CRY if big else OBS)
                elif big and y >= FLOOR + 5:
                    w.set(x, y, z, M + "purple_stained_glass_pane", north="true", south="true", east="true", west="true", waterlogged="false")
        for side in (-2, 2):
            x = C + dx * (R_WALL0 - 1) + (side if dz else 0)
            z = C + dz * (R_WALL0 - 1) + (side if dx else 0)
            guards.append((x, FLOOR, z, "guerrero_real" if big else "guerrero"))
    # muelle del sur: de la gran puerta hasta el borde del océano púrpura
    for z in range(C + R_WALL1 + 1, SZ - 1):
        for x in range(C - AVE, C + AVE + 1):
            w.set(x, FLOOR - 1, z, PBB if abs(x - C) == AVE else PB)
        for x in (C - AVE - 1, C + AVE + 1):
            w.set(x, FLOOR, z, M + "polished_blackstone_brick_wall", up="true", north="none", south="none", east="none", west="none",
                  waterlogged="false")
            if z % 8 == 0:
                w.fill(x, FLOOR - 4, z, x, FLOOR - 2, z, BASALT, axis="y")
                w.set(x, FLOOR + 1, z, LAMP)
    return towers


# ====================================================================== castillo y Salón del Rey
def castle(w, rnd, guards):
    x0, x1, z0, z1 = 68, 124, 18, 58
    H = 20
    top = FLOOR + H
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.set(x, FLOOR - 1, z, PB)
            edge = x in (x0, x1) or z in (z0, z1)
            if edge:
                for y in range(FLOOR, top + 1):
                    w.set(x, y, z, wall_material(rnd))
                if (x + z) % 2 == 0:
                    w.set(x, top + 1, z, PBB)
            w.set(x, top, z, PBB if edge else PB)
    # pilastras de basalto con oro, ventanales rojos altos y estandartes en la fachada
    for x in range(x0 + 4, x1, 6):
        for z in (z0, z1):
            w.fill(x, FLOOR, z, x, top, z, BASALT, axis="y")
            w.set(x, top - 1, z, GOLD)
            w.set(x, FLOOR, z, GOLD)
    for z in range(z0 + 4, z1, 6):
        for x in (x0, x1):
            w.fill(x, FLOOR, z, x, top, z, BASALT, axis="y")
    for x in range(x0 + 6, x1 - 2, 6):
        for z in (z0, z1):
            if abs(x - C) > 6:
                w.fill(x + 1, FLOOR + 4, z, x + 2, FLOOR + 12, z, GLASS)
                w.set(x + 1, FLOOR + 13, z, GOLD)
                w.set(x + 2, FLOOR + 13, z, GOLD)
    for x in range(x0 + 7, x1 - 2, 12):
        if abs(x - C) > 8:
            w.banner(x, FLOOR + 15, z1 + 1, "south")
            w.banner(x, FLOOR + 9, z1 + 1, "south")
    # gran entrada con marco de obsidiana llorona y oro
    for x in range(C - 3, C + 4):
        for y in range(FLOOR, FLOOR + 9):
            w.clear(x, y, z1)
    for x in range(C - 4, C + 5):
        w.set(x, FLOOR + 9, z1, GOLD)
    for y in range(FLOOR, FLOOR + 10):
        w.set(C - 4, y, z1, CRY)
        w.set(C + 4, y, z1, CRY)
    for x in range(C - 3, C + 4):
        for y in range(FLOOR + 6, FLOOR + 9):
            w.set(x, y, z1, M + "purple_stained_glass_pane", north="false", south="false", east="true", west="true", waterlogged="false")
    # torres: 4 esquinas y 2 a los lados de la entrada
    for (cx, cz) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        tower(w, cx, cz, 4, 30, rnd)
    for cx in (C - 9, C + 9):
        tower(w, cx, z1 + 1, 3, 26, rnd, archers=guards, rnd_kind="ballestero")
    throne = salon_del_rey(w, rnd, x0 + 1, z0 + 1, x1 - 1, z1 - 1, top, guards)
    return throne


def salon_del_rey(w, rnd, x0, z0, x1, z1, top, guards):
    """Salón del Rey (la sala extra del usuario): piso de damero negro y blanco con borde de oro, alfombra roja con
    ribete dorado, pilares negros y dorados, candelabros colgando de cadenas, braseros de fuego, armaduras de guardia,
    estandartes rojos del reino y el trono de oro al fondo sobre un estrado."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            border = x in (x0, x1, x0 + 1, x1 - 1) or z in (z0, z1, z0 + 1, z1 - 1)
            w.set(x, FLOOR - 1, z, GOLD if border and (x + z) % 3 == 0 else (QUARTZ if (x + z) % 2 else PB))
    # alfombra roja con ribete dorado
    for z in range(z0 + 7, z1 + 1):
        for x in range(C - 2, C + 3):
            w.set(x, FLOOR, z, M + ("yellow_carpet" if abs(x - C) == 2 else "red_carpet"))
    # estrado de 3 escalones y trono de oro
    for step in range(3):
        for x in range(C - 6 + step, C + 7 - step):
            for z in range(z0, z0 + 7 - step):
                w.set(x, FLOOR + step, z, PBB if step < 2 else GB)
        for x in range(C - 6 + step, C + 7 - step):
            stairs(w, x, FLOOR + step, z0 + 7 - step, M + "polished_blackstone_brick_stairs", "north")
    ty = FLOOR + 3
    tz = z0 + 2
    stairs(w, C, ty, tz, M + "polished_blackstone_stairs", "north")
    w.set(C, ty, tz, M + "red_wool")
    for y in range(ty, ty + 4):
        w.set(C, y, tz - 1, GOLD if y != ty + 2 else RUBY)
        w.set(C - 1, y, tz - 1, GOLD)
        w.set(C + 1, y, tz - 1, GOLD)
    w.set(C, ty + 4, tz - 1, GOLD)
    w.set(C - 1, ty + 4, tz - 1, M + "red_wool")
    w.set(C + 1, ty + 4, tz - 1, M + "red_wool")
    w.set(C - 1, ty, tz, GOLD)
    w.set(C + 1, ty, tz, GOLD)
    w.fill(C - 3, ty, z0, C + 3, ty, z0, M + "red_wool")
    w.banner(C, ty + 6, z0 - 0, "south") if False else None
    for x in (C - 3, C + 3):
        w.banner(x, ty + 5, z0, "south")
    # pilares negros y dorados en dos filas, con estandartes y braseros
    for z in range(z0 + 9, z1 - 2, 6):
        for x in (C - 9, C + 9):
            w.set(x, FLOOR, z, GOLD)
            w.fill(x, FLOOR + 1, z, x, top - 2, z, PBB)
            w.set(x, top - 1, z, GOLD)
            w.banner(x + (1 if x > C else -1) * -1, FLOOR + 6, z, "east" if x < C else "west")
            # braseros (fogatas sobre pedestal)
            bx = x + (3 if x < C else -3)
            w.set(bx, FLOOR, z, CPB)
            campfire(w, bx, FLOOR + 1, z)
    # braseros grandes a los lados del estrado
    for x in (C - 9, C + 9):
        w.fill(x - 1, FLOOR, z0 + 3, x + 1, FLOOR + 1, z0 + 5, PBB)
        campfire(w, x, FLOOR + 2, z0 + 4)
        w.set(x - 1, FLOOR + 2, z0 + 4, MAGMA)
        w.set(x + 1, FLOOR + 2, z0 + 4, MAGMA)
    # candelabros: cadenas desde el techo con una corona de faroles
    for z in range(z0 + 10, z1 - 3, 10):
        for x in (C - 5, C, C + 5):
            w.fill(x, top - 5, z, x, top - 1, z, M + "chain", axis="y")
            w.set(x, top - 6, z, GOLD)
            for (dx, dz) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                lantern(w, x + dx, top - 7, z + dz, hanging=False) if False else None
                w.set(x + dx, top - 6, z + dz, M + "chain", axis="x" if dx else "z")
                lantern(w, x + dx, top - 7, z + dz, hanging=True)
    # armaduras de la guardia real a los lados del trono y de la alfombra
    netherite = [M + "netherite_boots", M + "netherite_leggings", M + "netherite_chestplate", M + "netherite_helmet"]
    for (x, z) in ((C - 4, z0 + 2), (C + 4, z0 + 2)):
        w.armor_stand(x, FLOOR + 3, z, 0.0, netherite, M + "netherite_sword")
    for z in range(z0 + 12, z1 - 2, 8):
        for x in (C - 4, C + 4):
            w.armor_stand(x, FLOOR, z, 90.0 if x < C else -90.0,
                          [R + "ruby_boots", R + "ruby_leggings", R + "ruby_chestplate", R + "ruby_helmet"], R + "ruby_sword")
    # macetas con arbustos carmesí junto a las paredes
    for z in range(z0 + 8, z1, 6):
        for x in (x0 + 1, x1 - 1):
            w.set(x, FLOOR, z, M + "potted_crimson_roots")
    # habitantes: el Rey en su trono y la guardia real
    guards.append((C, FLOOR + 3, z0 + 4, "rey_necromancer"))
    for (x, z) in ((C - 6, z0 + 9), (C + 6, z0 + 9), (C - 3, z1 - 2), (C + 3, z1 - 2)):
        guards.append((x, FLOOR, z, "guerrero_real"))
    return (C, FLOOR + 3, z0 + 4)


# ====================================================================== salas del interior
def templo_de_fuego(w, rnd, x0, z0, x1, z1, people):
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 13, door_toward_center(x0, z0, x1, z1), rnd, roof="pyramid")
    # columnas de lava encerradas en vidrio (como en la imagen)
    for (x, z) in ((ix0 + 2, iz0 + 2), (ix1 - 2, iz0 + 2), (ix0 + 2, iz1 - 2), (ix1 - 2, iz1 - 2)):
        for y in range(FLOOR, top):
            for (dx, dz) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                w.set(x + dx, y, z + dz, M + "orange_stained_glass")
            w.set(x, y, z, M + "lava", level=0)
        w.set(x, top, z, OBS)
        w.set(x, FLOOR - 1, z, OBS)
    # altar al fondo con fuego de almas y oro
    cx = (ix0 + ix1) // 2
    w.fill(cx - 2, FLOOR, iz0, cx + 2, FLOOR, iz0 + 1, PBB)
    w.fill(cx - 1, FLOOR + 1, iz0, cx + 1, FLOOR + 1, iz0, GOLD)
    w.set(cx, FLOOR + 1, iz0 + 1, M + "soul_soil")
    w.set(cx, FLOOR + 2, iz0 + 1, M + "soul_fire")
    w.fill(cx - 1, FLOOR + 2, iz0, cx + 1, FLOOR + 4, iz0, MAGMA)
    w.set(cx, FLOOR + 5, iz0, GOLD)
    for x in range(ix0 + 4, ix1 - 3):
        if x != cx:
            for z in range(iz0 + 4, iz1 - 2, 2):
                if abs(x - cx) > 1:
                    stairs(w, x, FLOOR, z, M + "blackstone_stairs", "north")
    # piso con franjas de magma
    for z in range(iz0, iz1 + 1):
        w.set(cx, FLOOR - 1, z, MAGMA)
    people += [(cx - 2, FLOOR, iz1 - 2, "ciudadano"), (cx + 2, FLOOR, iz1 - 3, "ciudadano")]


def biblioteca(w, rnd, x0, z0, x1, z1, people):
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 9, door_toward_center(x0, z0, x1, z1), rnd)
    for x in range(ix0, ix1 + 1):
        for z in range(iz0, iz1 + 1):
            if x in (ix0, ix1) or z in (iz0, iz1):
                if w.get(x, FLOOR, z) is None:
                    w.fill(x, FLOOR, z, x, FLOOR + 2, z, M + "bookshelf")
    # salida libre junto a la puerta
    side = door_toward_center(x0, z0, x1, z1)
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    if side in ("north", "south"):
        z = iz0 if side == "north" else iz1
        w.clear_box(cx - 2, FLOOR, z, cx + 1, FLOOR + 2, z)
    else:
        x = ix0 if side == "west" else ix1
        w.clear_box(x, FLOOR, cz - 2, x, FLOOR + 2, cz + 1)
    # atriles del bibliotecario, mesa de encantamientos y alfombra roja
    for i, x in enumerate(range(ix0 + 3, ix1 - 2, 4)):
        station(w, x, FLOOR, iz0 + 3, "librarian_lectern", "south")
        people.append((x, FLOOR, iz0 + 5, "bibliotecario"))
    w.set(cx, FLOOR, cz + 1, M + "enchanting_table")
    for x in range(ix0 + 2, ix1 - 1):
        w.set(x, FLOOR, cz + 3, M + "red_carpet")
    for x in (ix0 + 2, ix1 - 2):
        w.set(x, FLOOR, iz1 - 2, CPL) if False else None
        w.set(x, FLOOR, cz + 1, M + "crimson_fence", north="false", south="false", east="false", west="false", waterlogged="false")
        slab(w, x, FLOOR + 1, cz + 1, M + "crimson_slab")
        lantern(w, x, FLOOR + 2, cz + 1, hanging=False)


def mercado(w, rnd, x0, z0, x1, z1, people):
    """Mercado Infernal: puestos con toldos rojos y blancos; aquí trabaja el Aldeano Necromancer."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.set(x, FLOOR - 1, z, PBB if (x + z) % 2 else PB)
    for (sx, sz) in [(x, z) for x in range(x0 + 1, x1 - 3, 6) for z in (z0 + 1, z1 - 4)]:
        # puesto: postes, mostrador y toldo a rayas
        for (dx, dz) in ((0, 0), (4, 0), (0, 3), (4, 3)):
            w.fill(sx + dx, FLOOR, sz + dz, sx + dx, FLOOR + 3, sz + dz, M + "crimson_fence", north="false", south="false",
                   east="false", west="false", waterlogged="false")
        for x in range(sx - 1, sx + 6):
            for z in range(sz - 1, sz + 5):
                w.set(x, FLOOR + 4, z, M + ("red_wool" if (x - sx) % 2 == 0 else "white_wool"))
        for x in range(sx + 1, sx + 4):
            w.set(x, FLOOR, sz + 1, M + "barrel", facing="up", open="false")
        w.chest(sx + 1, FLOOR + 1, sz + 1, "north", LOOT[0], barrel=True) if rnd.random() < 0.3 else None
        lantern(w, sx + 2, FLOOR + 3, sz + 2, hanging=True)
        w.set(sx + 3, FLOOR + 1, sz + 1, M + "flower_pot") if False else None
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    for i, x in enumerate((cx - 4, cx + 4)):
        station(w, x, FLOOR, cz, "necromancer_table", "south")
        people.append((x, FLOOR, cz + 2, "aldeano_necromancer"))
    for (x, z) in ((cx, cz - 1), (cx, cz + 1)):
        lamp_post(w, x, z, 3)
    people += [(cx - 2, FLOOR, cz + 3, "ciudadano"), (cx + 2, FLOOR, cz - 3, "ciudadano")]
    job(w, R + "peletero", [(cx, cz + 3), (cx + 1, cz + 3), (cx, cz - 3), (cx - 1, cz + 4)], "leather_cauldron", "north")


def comedor(w, rnd, x0, z0, x1, z1, people):
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 7, door_toward_center(x0, z0, x1, z1), rnd)
    # mesas largas con sillas
    for z in range(iz0 + 2, iz1 - 1, 4):
        for x in range(ix0 + 2, ix1 - 1):
            w.set(x, FLOOR, z, M + "stripped_crimson_stem", axis="x")
            stairs(w, x, FLOOR, z - 1, M + "crimson_stairs", "south")
            stairs(w, x, FLOOR, z + 1, M + "crimson_stairs", "north")
            if x % 3 == 0:
                w.set(x, FLOOR + 1, z, M + "red_candle", candles=3, lit="true", waterlogged="false")
    w.set(ix0, FLOOR, iz0, M + "smoker", facing="east", lit="false")
    campfire(w, ix0, FLOOR, iz0 + 1)
    w.chest(ix1, FLOOR, iz0, "west", "minecraft:chests/village/village_butcher", barrel=True)
    people += [(ix0 + 3, FLOOR, iz1 - 1, "ciudadano"), (ix1 - 3, FLOOR, iz1 - 1, "granjero")]
    job(w, M + "butcher", [(ix0, iz0)])


def herreria(w, rnd, x0, z0, x1, z1, people):
    """Sala de Herrería: forja con lava, yunques, cadenas y los carritos de los mineros."""
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 9, door_toward_center(x0, z0, x1, z1), rnd)
    cx, cz = (ix0 + ix1) // 2, (iz0 + iz1) // 2
    # forja: pileta de lava con marco de piedra negra y chimenea
    w.fill(cx - 2, FLOOR, iz0, cx + 2, FLOOR, iz0 + 2, PBB)
    w.set(cx, FLOOR, iz0 + 1, M + "lava", level=0)
    w.set(cx - 1, FLOOR, iz0 + 1, M + "lava", level=0)
    w.set(cx + 1, FLOOR, iz0 + 1, M + "lava", level=0)
    w.fill(cx - 2, FLOOR + 1, iz0, cx + 2, top, iz0, BS)
    w.set(cx - 1, FLOOR + 1, iz0 + 2, M + "blast_furnace", facing="south", lit="true")
    w.set(cx + 1, FLOOR + 1, iz0 + 2, M + "furnace", facing="south", lit="true")
    for (x, z) in ((cx - 4, cz), (cx + 4, cz)):
        w.set(x, FLOOR, z, M + "anvil", facing="east")
        w.fill(x, top - 3, z, x, top, z, M + "chain", axis="y")
    w.set(cx, FLOOR, cz + 2, M + "smithing_table")
    w.set(cx - 2, FLOOR, cz + 2, M + "grindstone", face="floor", facing="north")
    for i, x in enumerate((ix0 + 2, ix1 - 2, cx)):
        z = iz1 - 1
        station(w, x, FLOOR, z, "miner_cart", "north")
        people.append((x, FLOOR, z - 2, "minero"))
    for z in range(iz0 + 1, iz1, 3):
        w.chest(ix0, FLOOR, z, "east", LOOT[4], barrel=True)
    people.append((cx + 3, FLOOR, cz + 2, "guerrero"))
    job(w, M + "armorer", [(cx - 1, iz0 + 3)])
    job(w, M + "toolsmith", [(cx, cz + 2)])
    job(w, M + "weaponsmith", [(cx - 2, cz + 2)])


def pesca(w, rnd, x0, z0, x1, z1, people):
    """Sala de Pesca Magmática: una poza de lava hundida en el piso, con baranda."""
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 7, door_toward_center(x0, z0, x1, z1), rnd)
    cx, cz = (ix0 + ix1) // 2, (iz0 + iz1) // 2
    for x in range(cx - 4, cx + 5):
        for z in range(cz - 3, cz + 4):
            if abs(x - cx) == 4 or abs(z - cz) == 3:
                w.set(x, FLOOR, z, M + "nether_brick_fence", north="false", south="false", east="false", west="false", waterlogged="false")
            else:
                w.set(x, FLOOR - 1, z, M + "lava", level=0)
                w.set(x, FLOOR - 2, z, M + "lava", level=0)
                w.set(x, FLOOR - 3, z, BS)
    for x in (cx - 4, cx + 4):
        w.clear(x, FLOOR, cz)
    for z in range(iz0, iz1 + 1, 3):
        w.chest(ix1, FLOOR, z, "west", "minecraft:chests/village/village_fisher", barrel=True)
    for x in range(ix0 + 1, ix1, 3):
        w.fill(x, top - 2, iz0 + 1, x, top, iz0 + 1, M + "chain", axis="y")
    people += [(cx, FLOOR, cz + 4, "ciudadano"), (cx - 2, FLOOR, cz - 4, "ciudadano")]
    job(w, M + "fisherman", [(ix1 - 1, iz0 + 1)], count=2)


def laboratorio(w, rnd, x0, z0, x1, z1, people):
    """Laboratorio Arcano: soportes para pociones, calderos, amatista y luz morada."""
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 8, door_toward_center(x0, z0, x1, z1), rnd, wall=PBB)
    cx, cz = (ix0 + ix1) // 2, (iz0 + iz1) // 2
    for x in range(ix0, ix1 + 1):
        w.set(x, top + 1, iz0, M + "amethyst_block")
        w.set(x, top + 1, iz1, M + "amethyst_block")
    for x in range(ix0 + 2, ix1 - 1, 3):
        w.set(x, FLOOR, iz0, PBB)
        w.set(x, FLOOR + 1, iz0, M + "brewing_stand", has_bottle_0="false", has_bottle_1="false", has_bottle_2="false")
        w.set(x + 1, FLOOR, iz0, CPB)
        w.set(x + 1, FLOOR + 1, iz0, M + "soul_lantern", hanging="false", waterlogged="false")
    w.set(cx, FLOOR, cz, M + "enchanting_table")
    for (dx, dz) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        w.set(cx + dx, FLOOR, cz + dz, CRY)
        w.set(cx + dx, FLOOR + 1, cz + dz, M + "amethyst_cluster", facing="up", waterlogged="false")
        w.set(cx + dx, FLOOR + 2, cz + dz, M + "soul_lantern", hanging="false", waterlogged="false")
    for z in range(iz0 + 2, iz1, 2):
        w.fill(ix1, FLOOR, z, ix1, FLOOR + 2, z, M + "bookshelf")
    for x in range(ix0 + 1, ix1):
        if x % 4 == 0:
            w.set(x, FLOOR + 2, iz1 + 1, M + "purple_stained_glass") if False else None
    people.append((cx + 3, FLOOR, cz + 1, "bibliotecario"))
    job(w, M + "cleric", [(ix0 + 2, iz0 + 1)], count=2)


def sala_control(w, rnd, x0, z0, x1, z1, people):
    """Sala de Control: el gran mapa del reino en la pared y la mesa de los consejeros."""
    side = door_toward_center(x0, z0, x1, z1)
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 8, side, rnd, windows=False)
    # mapa en la pared opuesta a la puerta
    pal = [NYL, WNYL, M + "red_concrete", NWB, M + "warped_wart_block", GOLD, M + "purple_concrete"]
    if side in ("east", "west"):
        x = ix0 if side == "east" else ix1
        for z in range(iz0 + 1, iz1):
            for y in range(FLOOR + 1, FLOOR + 6):
                w.set(x, y, z, pal[(z * 3 + y * 5) % len(pal)])
    else:
        z = iz0 if side == "south" else iz1
        for x in range(ix0 + 1, ix1):
            for y in range(FLOOR + 1, FLOOR + 6):
                w.set(x, y, z, pal[(x * 3 + y * 5) % len(pal)])
    cx, cz = (ix0 + ix1) // 2, (iz0 + iz1) // 2
    w.fill(cx - 2, FLOOR, cz - 1, cx + 2, FLOOR, cz + 1, PBB)
    for x in range(cx - 2, cx + 3):
        stairs(w, x, FLOOR, cz - 2, M + "blackstone_stairs", "south")
        stairs(w, x, FLOOR, cz + 2, M + "blackstone_stairs", "north")
    w.set(cx, FLOOR + 1, cz, LAMP)
    people += [(cx - 3, FLOOR, cz, "guerrero_real"), (cx + 3, FLOOR, cz, "ciudadano")]
    job(w, R + "cartografo", [(cx, cz + 4), (cx, cz - 4), (cx + 5, cz), (cx - 5, cz)], "cartographer_desk", "north")


def defensa(w, rnd, x0, z0, x1, z1, people):
    """Sala de Defensa (armería): armaduras en fila y cofres de armas."""
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 8, door_toward_center(x0, z0, x1, z1), rnd, roof="battlement")
    sets = [[R + "ruby_boots", R + "ruby_leggings", R + "ruby_chestplate", R + "ruby_helmet"],
            [R + "human_boots", R + "human_leggings", R + "human_chestplate", R + "human_helmet"],
            [M + "netherite_boots", M + "netherite_leggings", M + "netherite_chestplate", M + "netherite_helmet"]]
    hands = [R + "ruby_sword", R + "ruby_longsword", R + "ruby_crossbow"]
    i = 0
    for x in range(ix0 + 2, ix1 - 1, 3):
        for z in (iz0 + 1, iz1 - 1):
            w.armor_stand(x, FLOOR, z, 0.0 if z == iz0 + 1 else 180.0, sets[i % 3], hands[i % 3])
            i += 1
    for x in range(ix0 + 1, ix1, 4):
        w.chest(x, FLOOR, (iz0 + iz1) // 2, "north", LOOT[2])
    barracks(w, ix0, iz0, ix1, iz1)
    people += [(ix0 + 4, FLOOR, (iz0 + iz1) // 2 + 1, "guerrero"), (ix1 - 4, FLOOR, (iz0 + iz1) // 2 - 1, "arquero")]
    dcx, dcz = (ix0 + ix1) // 2, (iz0 + iz1) // 2
    job(w, R + "flechero", [(dcx, dcz + 2), (dcx + 1, dcz + 2), (dcx, dcz - 2), (dcx + 2, dcz)], "fletcher_bench", "north")


def barracks(w, ix0, iz0, ix1, iz1):
    """Literas de los soldados a lo largo de las paredes laterales (la puerta queda en otra pared)."""
    cz = (iz0 + iz1) // 2
    for z in range(iz0 + 3, iz1 - 2):
        if z == cz:
            continue
        for x, face in ((ix0 + 1, "west"), (ix1 - 1, "east")):
            hx = x + STEP[face][0]
            if w.get(x, FLOOR, z) is None and w.get(hx, FLOOR, z) is None:
                nether_bed(w, x, FLOOR, z, face)


def guardianes(w, rnd, x0, z0, x1, z1, people):
    """Sala de Guardianes: estatuas de gólem guardián (piedra negra pulida con ojos de oro) y vigilancia."""
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 10, door_toward_center(x0, z0, x1, z1), rnd)
    def golem(x, z):
        w.fill(x - 1, FLOOR, z, x + 1, FLOOR, z, CPB)              # pedestal
        w.fill(x - 1, FLOOR + 1, z, x - 1, FLOOR + 2, z, PB)        # piernas
        w.fill(x + 1, FLOOR + 1, z, x + 1, FLOOR + 2, z, PB)
        w.fill(x - 1, FLOOR + 3, z, x + 1, FLOOR + 4, z, M + "polished_blackstone_bricks")
        w.set(x - 2, FLOOR + 3, z, PB)                              # brazos
        w.set(x + 2, FLOOR + 3, z, PB)
        w.set(x - 2, FLOOR + 2, z, PB)
        w.set(x + 2, FLOOR + 2, z, PB)
        w.set(x, FLOOR + 5, z, CPB)                                 # cabeza
        w.set(x, FLOOR + 5, z + 1, GB) if False else None
        w.set(x, FLOOR + 6, z, GOLD)
        w.set(x, FLOOR + 4, z + 1, RUBY)
    for x in range(ix0 + 3, ix1 - 1, 5):
        golem(x, iz0 + 1)
        golem(x, iz1 - 1)
    cx, cz = (ix0 + ix1) // 2, (iz0 + iz1) // 2
    campfire(w, cx, FLOOR, cz)
    barracks(w, ix0, iz0, ix1, iz1)
    people += [(cx - 2, FLOOR, cz, "guerrero_real"), (cx + 2, FLOOR, cz, "ballestero")]


# ====================================================================== anillo exterior: casas, dormitorios, granjas, jardines, torres
def vivienda(w, rnd, x0, z0, x1, z1, people):
    side = door_toward_center(x0, z0, x1, z1)
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 5, side, rnd, roof="pyramid", windows=True)
    # dos camas del Nether contra la pared del fondo, cofre, mesa de crafteo y horno
    far = OPP[side]
    if far in ("north", "south"):
        z = iz0 if far == "north" else iz1
        dz = 1 if far == "north" else -1
        for bx in (ix0, (ix0 + ix1) // 2, ix1):
            nether_bed(w, bx, FLOOR, z + dz, far)
        w.chest(ix0, FLOOR, z + 3 * dz, OPP[far], LOOT[rnd.randrange(len(LOOT))])
    else:
        x = ix0 if far == "west" else ix1
        dx = 1 if far == "west" else -1
        for bz in (iz0, (iz0 + iz1) // 2, iz1):
            nether_bed(w, x + dx, FLOOR, bz, far)
        w.chest(x + 3 * dx, FLOOR, iz0, OPP[far], LOOT[rnd.randrange(len(LOOT))])
    w.set(ix1, FLOOR, iz1, M + "crafting_table") if w.get(ix1, FLOOR, iz1) is None else None
    lantern(w, (ix0 + ix1) // 2, FLOOR + 3, (iz0 + iz1) // 2, hanging=True)
    k = rnd.random()
    people.append(((ix0 + ix1) // 2, FLOOR, (iz0 + iz1) // 2, "ciudadano" if k < 0.6 else ("granjero" if k < 0.8 else "minero")))


def dormitorio(w, rnd, x0, z0, x1, z1, people):
    """Dormitorios Comunes: filas de camas del Nether."""
    side = door_toward_center(x0, z0, x1, z1)
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 6, side, rnd)
    if side in ("east", "west"):
        for z in range(iz0, iz1 + 1):
            if abs(z - (iz0 + iz1) // 2) <= 1:
                continue
            nether_bed(w, ix0 + 1, FLOOR, z, "west")
            nether_bed(w, ix1 - 1, FLOOR, z, "east")
    else:
        for x in range(ix0, ix1 + 1):
            if abs(x - (ix0 + ix1) // 2) <= 1:
                continue
            nether_bed(w, x, FLOOR, iz0 + 1, "north")
            nether_bed(w, x, FLOOR, iz1 - 1, "south")
    people += [((ix0 + ix1) // 2, FLOOR, (iz0 + iz1) // 2, "ciudadano"), ((ix0 + ix1) // 2, FLOOR, (iz0 + iz1) // 2 + 1, "ciudadano")]
    dcx, dcz = (ix0 + ix1) // 2, (iz0 + iz1) // 2
    job(w, R + "pastor", [(dcx, dcz - 1), (dcx + 1, dcz - 1), (dcx - 1, dcz - 1), (dcx + 1, dcz + 1)], "shepherd_loom", "south")


def taller(w, rnd, x0, z0, x1, z1, people):
    """Taller de Cantería: los cortapiedras de los albañiles, bloques de piedra negra apilados y polvo de basalto."""
    side = door_toward_center(x0, z0, x1, z1)
    ix0, iz0, ix1, iz1, top = hall(w, x0, z0, x1, z1, 6, side, rnd)
    cx, cz = (ix0 + ix1) // 2, (iz0 + iz1) // 2
    far = OPP[side]
    # pilas de bloques en las esquinas del fondo
    corners = {"north": [(ix0, iz0), (ix1, iz0)], "south": [(ix0, iz1), (ix1, iz1)],
               "west": [(ix0, iz0), (ix0, iz1)], "east": [(ix1, iz0), (ix1, iz1)]}[far]
    for (x, z) in corners:
        w.set(x, FLOOR, z, PBB)
        w.set(x, FLOOR + 1, z, BASALT, axis="y")
        w.set(x + (1 if x == ix0 else -1), FLOOR, z, BS)
        w.set(x, FLOOR, z + (1 if z == iz0 else -1), CPB)
    # piso con polvo de piedra (grava negra = basalto) alrededor de las mesas
    for x in range(cx - 2, cx + 3):
        for z in range(cz - 1, cz + 2):
            w.set(x, FLOOR - 1, z, M + "smooth_basalt" if (x + z) % 2 else PB)
    lantern(w, cx, FLOOR + 3, cz, hanging=True)
    w.chest(cx, FLOOR, {"north": iz0, "south": iz1, "west": cz, "east": cz}[far] if far in ("north", "south") else cz, OPP[far],
            "minecraft:chests/village/village_mason") if far in ("north", "south") else None
    job(w, R + "albanil", [(cx - 2, cz), (cx - 2, cz + 1)], "mason_cutter", "south")
    job(w, R + "albanil", [(cx + 2, cz), (cx + 2, cz + 1)], "mason_cutter", "south")
    people.append((cx, FLOOR, cz + 2 if cz + 2 <= iz1 else cz, "ciudadano"))


def granja(w, rnd, x0, z0, x1, z1, people):
    """Granjas del Nether: verruga en arena de almas regada con agua del Nether, hongos y el cesto del granjero."""
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1)
            if edge:
                w.set(x, FLOOR - 1, z, PBB)
                w.set(x, FLOOR, z, M + "nether_brick_fence", north="false", south="false", east="false", west="false", waterlogged="false")
            elif x == cx:
                w.set(x, FLOOR - 1, z, R + "nether_water")
            elif (x + z) % 5 == 0:
                w.set(x, FLOOR - 1, z, NYL)
                w.set(x, FLOOR, z, M + ("crimson_fungus" if rnd.random() < 0.6 else "warped_fungus"))
            else:
                w.set(x, FLOOR - 1, z, M + "soul_sand")
                w.set(x, FLOOR, z, M + "nether_wart", age=3)
    side = door_toward_center(x0, z0, x1, z1)
    gx, gz = {"north": (cx + 2, z0), "south": (cx + 2, z1), "east": (x1, cz + 2), "west": (x0, cz + 2)}[side]
    w.clear(gx, FLOOR, gz)
    w.set(gx, FLOOR, gz, M + "crimson_fence_gate", facing="north" if side in ("north", "south") else "east", in_wall="false",
          open="false", powered="false")
    sx, sz = {"north": (cx - 2, z0 - 1), "south": (cx - 2, z1 + 1), "east": (x1 + 1, cz - 2), "west": (x0 - 1, cz - 2)}[side]
    station(w, sx, FLOOR, sz, "farmer_basket", side)
    lamp_post(w, cx + 1, cz + 1, 3) if False else None
    people.append((sx, FLOOR, sz + (1 if side == "south" else -1) if side in ("north", "south") else sz, "granjero"))


def jardin(w, rnd, x0, z0, x1, z1, people):
    """Jardines del Nether: nylium, hongos gigantes carmesí y distorsionados, raíces y faroles."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            w.set(x, FLOOR - 1, z, NYL if (x * 7 + z * 3) % 5 else WNYL)
            k = rnd.random()
            if k < 0.25:
                w.set(x, FLOOR, z, M + "crimson_roots")
            elif k < 0.32:
                w.set(x, FLOOR, z, M + "nether_sprouts")
    cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
    for z in range(z0, z1 + 1):
        w.set(cx, FLOOR - 1, z, PBB)
        w.clear(cx, FLOOR, z)
    crimson_tree(w, x0 + 2, z0 + 2, rnd, 6)
    crimson_tree(w, x1 - 2, z1 - 2, rnd, 6, warped=True)
    lamp_post(w, cx, cz, 3)
    people.append((cx, FLOOR, cz + 1, "ciudadano"))


def torre_vigilancia(w, rnd, cx, cz, people, guards):
    """Torre de Vigilancia: torre alta con la percha de los domadores de dragón arriba."""
    top = tower(w, cx, cz, 3, 30, rnd, roof=False)
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 3, cz + 4):
            w.set(x, top + 1, z, PBB)
    for (dx, dz) in ((-2, -2), (2, 2)):
        station(w, cx + dx, top + 2, cz + dz, "tamer_nest", "south")
    people += [(cx - 1, top + 2, cz + 1, "domador"), (cx + 1, top + 2, cz - 1, "domador")]
    guards.append((cx, top + 2, cz, "arquero"))


def outer_ring(w, rnd, people, guards):
    kinds = []
    layout = {}
    plan = ["vivienda"] * 40
    special = {20: "granja", 50: "jardin", 80: "dormitorio", 125: "granja", 160: "torre", 200: "dormitorio",
               235: "jardin", 315: "granja", 340: "torre", 140: "dormitorio", 25: "torre", 105: "taller"}
    taken = []
    a = 6.0
    while a < 360:
        ang = a % 360
        if min(abs(ang - g) for g in (0, 90, 180, 270, 360)) < 9 or 234 < ang < 306:
            a += 3
            continue
        kind = "vivienda"
        for sa, sk in special.items():
            if abs(ang - sa) < 6 and sa not in [t[0] for t in taken if isinstance(t, tuple)]:
                kind = sk
                taken.append((sa, sk))
                break
        half = 4 if kind in ("vivienda", "torre") else 5
        rr = 72.5
        cx = int(round(C + rr * math.cos(math.radians(ang))))
        cz = int(round(C + rr * math.sin(math.radians(ang))))
        x0, z0, x1, z1 = cx - half + (1 if half == 4 else 0), cz - half + (1 if half == 4 else 0), cx + half - 1 if half == 4 else cx + half, cz + half - 1 if half == 4 else cz + half
        if kind == "vivienda":
            x0, z0, x1, z1 = cx - 3, cz - 3, cx + 3, cz + 3
        corners_ok = all(R_MOAT1 + 1.5 < dist(x, z) < R_WALL0 - 0.8 for x in (x0, x1) for z in (z0, z1))
        if not corners_ok:
            a += 2
            continue
        {"vivienda": vivienda, "granja": granja, "jardin": jardin, "dormitorio": dormitorio, "taller": taller}.get(kind, lambda *aa: None)(
            w, rnd, x0, z0, x1, z1, people)
        if kind == "torre":
            torre_vigilancia(w, rnd, cx, cz, people, guards)
        kinds.append(kind)
        a += 10.5 if kind == "vivienda" else 14.0
    return kinds


# ====================================================================== armar el reino
def build():
    rnd = random.Random(2024)
    w = World()
    people, guards = [], []
    plaza(w, rnd)
    avenues(w, rnd)
    moat(w, rnd)
    towers = outer_wall(w, rnd, guards)
    throne = castle(w, rnd, guards)
    # salas del interior (entre la plaza y el foso)
    templo_de_fuego(w, rnd, 104, 60, 122, 78, people)
    biblioteca(w, rnd, 126, 70, 146, 88, people)
    mercado(w, rnd, 104, 104, 128, 124, people)
    comedor(w, rnd, 132, 102, 150, 118, people)
    herreria(w, rnd, 66, 104, 88, 122, people)
    pesca(w, rnd, 44, 100, 62, 116, people)
    laboratorio(w, rnd, 68, 62, 88, 78, people)
    sala_control(w, rnd, 44, 74, 62, 90, people)
    defensa(w, rnd, 104, 130, 122, 148, people)
    guardianes(w, rnd, 70, 130, 88, 148, people)
    kinds = outer_ring(w, rnd, people, guards)
    # guardias por las avenidas y la plaza
    for (x, z) in ((C + 16, C - 2), (C - 16, C + 2), (C + 2, C + 16), (C - 2, C - 16), (C + 45, C - 2), (C - 45, C + 2),
                   (C + 2, C + 45)):
        guards.append((x, FLOOR, z, "guerrero" if (x + z) % 2 else "arquero"))
    for (x, z) in ((C - 6, C + 6), (C + 6, C - 6), (C + 6, C + 6), (C - 6, C - 6)):
        people.append((x, FLOOR, z, "ciudadano"))
    for (x, y, z, kind) in people + guards:
        skins = SKINS.get(kind, (1, 1))
        female = rnd.random() < 0.5
        if kind == "rey_necromancer":
            w.entity(x, y, z, R + kind)
            w.residents += 1
            continue
        w.human(x, y, z, kind, rnd, female=female, skins=skins[1] if female else skins[0])
    w.kinds = kinds
    w.throne = throne
    return w


# ====================================================================== guardar .nbt
def save(w, path):
    palette, pidx, blocks = [], {}, []
    for (x, y, z), (name, props) in sorted(w.b.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        key = (name, props)
        if key not in pidx:
            pidx[key] = len(palette)
            entry = {"Name": String(name)}
            if props:
                entry["Properties"] = {k: String(v) for k, v in props}
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
    return len(blocks), len(ents)


def write_all():
    w = build()
    return save(w, os.path.join(DATA, "structure", "capital.nbt"))


if __name__ == "__main__":
    w = build()
    print(len(w.b), "bloques", len(w.ents), "entidades", w.residents, "habitantes", w.kinds.count("vivienda"), "casas")
