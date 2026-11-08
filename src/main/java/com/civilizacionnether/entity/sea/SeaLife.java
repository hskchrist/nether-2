package com.civilizacionnether.entity.sea;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.registry.ModFluids;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.AABB;

/** Ayudas comunes de la fauna del Mar del Nether: agua del Nether, zona del Reino y reglas de aparición. */
public final class SeaLife {
    public static final ResourceKey<Structure> CAPITAL = ResourceKey.create(Registries.STRUCTURE, CivilizacionNether.id("capital"));

    /** ¿Está dentro del agua del Nether? (además del agua normal). */
    public static boolean inNetherWater(Entity entity) {
        return entity.isInFluidType(ModFluids.NETHER_WATER_TYPE.get());
    }

    /** ¿Se puede nadar ahí? Agua normal, agua del Nether o lava (la fauna del Nether nada en las tres). */
    public static boolean isWater(LevelReader level, BlockPos pos) {
        var f = level.getFluidState(pos);
        return f.is(FluidTags.WATER) || f.is(FluidTags.LAVA);
    }

    /** Sólo agua (para dónde aparecen). */
    public static boolean isRealWater(LevelReader level, BlockPos pos) {
        return level.getFluidState(pos).is(FluidTags.WATER);
    }

    /** ¿Está dentro del Reino Humano (de borde a borde, con el muelle)? */
    public static boolean insideKingdom(Level level, BlockPos pos) {
        if (!(level instanceof ServerLevel server)) {
            return false;
        }
        Structure capital = server.registryAccess().registryOrThrow(Registries.STRUCTURE).get(CAPITAL);
        return capital != null && server.structureManager().getStructureAt(pos, capital).isValid();
    }

    /** Altura de la superficie del agua sobre un punto (el primer bloque sin agua hacia arriba). */
    public static int surfaceAbove(LevelReader level, BlockPos from) {
        BlockPos.MutableBlockPos m = from.mutable();
        int limit = from.getY() + 48;
        while (m.getY() < limit && isWater(level, m)) {
            m.move(Direction.UP);
        }
        return m.getY();
    }

    // ------------------------------------------------------------------ reglas de aparición
    /** Peces, medusas, delfines, mantas y caballitos: en el agua (con agua encima). */
    public static <T extends Entity> boolean canSpawnInWater(EntityType<T> type, ServerLevelAccessor level, MobSpawnType reason,
                                                             BlockPos pos, RandomSource random) {
        return isRealWater(level, pos) && isRealWater(level, pos.above());
    }

    /** Ballena: agua honda (al menos 4 bloques de agua). */
    public static <T extends Entity> boolean canSpawnDeep(EntityType<T> type, ServerLevelAccessor level, MobSpawnType reason,
                                                          BlockPos pos, RandomSource random) {
        for (int dy = 0; dy < 4; dy++) {
            if (!isRealWater(level, pos.above(dy))) {
                return false;
            }
        }
        return isRealWater(level, pos.below());
    }

    /** Cangrejo y tortuga: en el fondo del mar. */
    public static <T extends Entity> boolean canSpawnOnFloor(EntityType<T> type, ServerLevelAccessor level, MobSpawnType reason,
                                                             BlockPos pos, RandomSource random) {
        BlockPos below = pos.below();
        return isRealWater(level, pos) && level.getBlockState(below).isFaceSturdy(level, below, Direction.UP);
    }

    /** Tiburón: en el agua y nunca dentro del Reino. */
    public static <T extends Entity> boolean canSpawnShark(EntityType<T> type, ServerLevelAccessor level, MobSpawnType reason,
                                                           BlockPos pos, RandomSource random) {
        if (!canSpawnInWater(type, level, reason, pos, random)) {
            return false;
        }
        return reason != MobSpawnType.NATURAL || !insideKingdom(level.getLevel(), pos);
    }

    /** Serpiente Marina: muy rara, en agua honda, lejos del Reino y nunca dos cerca. */
    public static <T extends Entity> boolean canSpawnSerpent(EntityType<T> type, ServerLevelAccessor level, MobSpawnType reason,
                                                             BlockPos pos, RandomSource random) {
        if (!canSpawnDeep(type, level, reason, pos, random)) {
            return false;
        }
        if (reason != MobSpawnType.NATURAL) {
            return true;
        }
        if (random.nextInt(6) != 0 || insideKingdom(level.getLevel(), pos)) {
            return false;
        }
        return level.getEntitiesOfClass(SeaSerpentEntity.class, new AABB(pos).inflate(160.0)).isEmpty();
    }

    private SeaLife() {
    }
}
