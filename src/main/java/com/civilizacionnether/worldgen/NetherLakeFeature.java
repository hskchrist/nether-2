package com.civilizacionnether.worldgen;

import com.civilizacionnether.registry.ModBlocks;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

/**
 * Lago o laguna de agua del Nether en el suelo del Mar del Nether: una cuenca ovalada, más honda al medio. Sólo se
 * hace si todo el borde es suelo firme (así el agua no se derrama por un barranco).
 */
public class NetherLakeFeature extends Feature<NoneFeatureConfiguration> {
    public NetherLakeFeature(Codec<NoneFeatureConfiguration> codec) {
        super(codec);
    }

    private static boolean ground(BlockState s) {
        return s.isSolid() && !s.is(Blocks.BEDROCK);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource rnd = ctx.random();
        BlockPos o = ctx.origin();
        BlockPos c = o.below(); // el suelo (como mucho 8 bloques a cada lado: no se sale de la zona que se puede tocar)
        if (!ground(level.getBlockState(c)) || !level.getBlockState(c.above()).canBeReplaced()
                || KingdomArea.near(level, ctx.chunkGenerator(), c, 12)) {
            return false;
        }
        double rx = 3.5 + rnd.nextInt(4);
        double rz = 3.5 + rnd.nextInt(4);
        int depth = 2 + rnd.nextInt(3);
        int r = (int) Math.ceil(Math.max(rx, rz)) + 1;
        // revisar: dentro, suelo con aire encima; en el borde, suelo firme a la altura del agua
        for (int dx = -r; dx <= r; dx++) {
            for (int dz = -r; dz <= r; dz++) {
                double e = (dx * dx) / (rx * rx) + (dz * dz) / (rz * rz);
                BlockPos p = c.offset(dx, 0, dz);
                if (e <= 1.0) {
                    if (!ground(level.getBlockState(p)) || !level.getBlockState(p.below()).isSolid()) {
                        return false;
                    }
                } else if (e <= 1.6) {
                    if (!ground(level.getBlockState(p))) {
                        return false;
                    }
                }
            }
        }
        BlockState water = ModBlocks.NETHER_WATER.get().defaultBlockState();
        for (int dx = -r; dx <= r; dx++) {
            for (int dz = -r; dz <= r; dz++) {
                double e = (dx * dx) / (rx * rx) + (dz * dz) / (rz * rz);
                if (e > 1.0) {
                    continue;
                }
                int d = Math.max(1, (int) Math.round(depth * (1.0 - e)) + 1);
                BlockPos p = c.offset(dx, 0, dz);
                for (int k = 1; k <= 3; k++) {
                    BlockPos a = p.above(k);
                    if (!level.getBlockState(a).isAir() && level.getBlockState(a).canBeReplaced()) {
                        level.setBlock(a, Blocks.AIR.defaultBlockState(), 2); // hierba encima
                    }
                }
                for (int k = 0; k < d; k++) {
                    level.setBlock(p.below(k), water, 2);
                }
                level.setBlock(p.below(d), rnd.nextInt(4) == 0 ? Blocks.BLACKSTONE.defaultBlockState()
                        : Blocks.WARPED_NYLIUM.defaultBlockState(), 2);
            }
        }
        return true;
    }
}
