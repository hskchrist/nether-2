package com.civilizacionnether.worldgen;

import com.civilizacionnether.entity.DragonEggEntity;
import com.civilizacionnether.entity.InfernalDragonEntity;
import com.civilizacionnether.registry.ModEntities;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.core.Direction;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/**
 * Nido del Dragón Infernal (Bosque Carmesí): un anillo de piedra negra, basalto y tallos carmesí con huesos,
 * magma al centro con un Huevo de Dragón Infernal encima, y el dragón salvaje que lo cuida.
 */
public class InfernalNestFeature extends Feature<NoneFeatureConfiguration> {
    public InfernalNestFeature(Codec<NoneFeatureConfiguration> codec) {
        super(codec);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource rnd = ctx.random();
        BlockPos.MutableBlockPos m = ctx.origin().mutable();
        BlockPos floor = null;
        for (int i = 0; i < 56 && m.getY() > level.getMinBuildHeight() + 6; i++) {
            m.move(Direction.DOWN);
            BlockPos below = m.below();
            if (level.isEmptyBlock(m) && level.getBlockState(below).isSolidRender(level, below)) {
                floor = m.immutable();
                break;
            }
        }
        if (floor == null || !roomFor(level, floor)) {
            return false;
        }
        int r = 5;
        for (int dx = -r - 1; dx <= r + 1; dx++) {
            for (int dz = -r - 1; dz <= r + 1; dz++) {
                double d = Math.sqrt(dx * dx + dz * dz);
                if (d > r + 0.6) {
                    continue;
                }
                BlockPos base = floor.offset(dx, -1, dz);
                // base del nido (rellena huecos debajo)
                level.setBlock(base, d < 1.6 ? Blocks.MAGMA_BLOCK.defaultBlockState()
                        : rnd.nextInt(4) == 0 ? Blocks.BASALT.defaultBlockState() : Blocks.BLACKSTONE.defaultBlockState(), 2);
                for (int dy = 2; dy <= 3; dy++) {
                    BlockPos under = floor.offset(dx, -dy, dz);
                    if (level.isEmptyBlock(under)) {
                        level.setBlock(under, Blocks.BLACKSTONE.defaultBlockState(), 2);
                    }
                }
                // borde: piedras, tallos carmesí y huesos
                if (d > r - 1.0) {
                    int h = 1 + rnd.nextInt(2);
                    for (int dy = 0; dy < h; dy++) {
                        level.setBlock(floor.offset(dx, dy, dz), rim(rnd, dx, dz), 2);
                    }
                } else if (d > 1.6 && rnd.nextInt(7) == 0) {
                    level.setBlock(floor.offset(dx, 0, dz), rnd.nextBoolean() ? Blocks.CRIMSON_ROOTS.defaultBlockState()
                            : Blocks.SOUL_SAND.defaultBlockState(), 2);
                }
            }
        }
        DragonEggEntity egg = ModEntities.DRAGON_EGG.get().create(level.getLevel());
        if (egg != null) {
            egg.moveTo(floor.getX() + 0.5, floor.getY(), floor.getZ() + 0.5, rnd.nextFloat() * 360.0f, 0.0f);
            egg.setInfernal(true);
            egg.setPersistenceRequired();
            level.addFreshEntity(egg);
        }
        InfernalDragonEntity dragon = ModEntities.DRAGON_INFERNAL.get().create(level.getLevel());
        if (dragon != null) {
            dragon.moveTo(floor.getX() + 0.5, floor.getY(), floor.getZ() + 3.5, rnd.nextFloat() * 360.0f, 0.0f);
            dragon.setNest(floor);
            dragon.setPersistenceRequired();
            dragon.setResting(true);
            level.addFreshEntity(dragon);
        }
        return true;
    }

    private static BlockState rim(RandomSource rnd, int dx, int dz) {
        int k = rnd.nextInt(6);
        if (k == 0) {
            return Blocks.BONE_BLOCK.defaultBlockState().setValue(RotatedPillarBlock.AXIS, Math.abs(dx) > Math.abs(dz) ? Direction.Axis.Z : Direction.Axis.X);
        }
        if (k == 1) {
            return Blocks.CRIMSON_STEM.defaultBlockState().setValue(RotatedPillarBlock.AXIS, Math.abs(dx) > Math.abs(dz) ? Direction.Axis.Z : Direction.Axis.X);
        }
        if (k == 2) {
            return Blocks.BASALT.defaultBlockState();
        }
        return Blocks.BLACKSTONE.defaultBlockState();
    }

    /** Lugar abierto: 7 bloques de aire sobre el centro y suelo firme. */
    private static boolean roomFor(WorldGenLevel level, BlockPos floor) {
        for (int dy = 0; dy < 7; dy++) {
            if (!level.isEmptyBlock(floor.above(dy)) && !level.getBlockState(floor.above(dy)).canBeReplaced()) {
                return false;
            }
        }
        return true;
    }
}
