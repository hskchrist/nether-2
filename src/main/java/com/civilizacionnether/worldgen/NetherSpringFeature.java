package com.civilizacionnether.worldgen;

import com.civilizacionnether.registry.ModBlocks;
import com.civilizacionnether.registry.ModFluids;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/**
 * Manantial de agua del Nether: un ojo de agua en una pared de roca que corre y cae como arroyo o cascada. No aparece
 * donde se construye el Reino.
 */
public class NetherSpringFeature extends Feature<NoneFeatureConfiguration> {
    public NetherSpringFeature(Codec<NoneFeatureConfiguration> codec) {
        super(codec);
    }

    private static boolean rock(BlockState s) {
        return s.is(Blocks.NETHERRACK) || s.is(ModBlocks.NETHER_SEA_GRASS_BLOCK.get()) || s.is(Blocks.BLACKSTONE) || s.is(Blocks.SOUL_SOIL);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        BlockPos p = ctx.origin();
        if (!rock(level.getBlockState(p)) || !rock(level.getBlockState(p.above())) || !rock(level.getBlockState(p.below()))) {
            return false;
        }
        int rockSides = 0;
        int open = 0;
        for (Direction d : Direction.Plane.HORIZONTAL) {
            BlockState s = level.getBlockState(p.relative(d));
            if (rock(s)) {
                rockSides++;
            } else if (s.isAir()) {
                open++;
            }
        }
        if (rockSides != 3 || open != 1 || KingdomArea.near(level, ctx.chunkGenerator(), p, 24)) {
            return false;
        }
        level.setBlock(p, ModBlocks.NETHER_WATER.get().defaultBlockState(), 2);
        level.scheduleTick(p, ModFluids.NETHER_WATER.get(), 0);
        return true;
    }
}
