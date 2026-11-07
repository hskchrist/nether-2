package com.civilizacionnether.worldgen;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.registry.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import com.mojang.serialization.Codec;

/**
 * Océano Púrpura del Nether: en cada columna del chunk que esté en el bioma, el mar de lava (bajo el nivel 32) se
 * convierte en agua del Nether; el fondo se cubre de nylium carmesí y distorsionado, con raíces y luces de hongo.
 */
public class PurpleSeaFeature extends Feature<NoneFeatureConfiguration> {
    public static final ResourceKey<Biome> BIOME = ResourceKey.create(Registries.BIOME, CivilizacionNether.id("oceano_purpura"));
    private static final int SEA_TOP = 31;

    public PurpleSeaFeature(Codec<NoneFeatureConfiguration> codec) {
        super(codec);
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource rnd = ctx.random();
        BlockPos origin = ctx.origin();
        int cx = origin.getX() & ~15;
        int cz = origin.getZ() & ~15;
        BlockState water = ModBlocks.NETHER_WATER.get().defaultBlockState();
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        boolean any = false;
        for (int x = cx; x < cx + 16; x++) {
            for (int z = cz; z < cz + 16; z++) {
                m.set(x, SEA_TOP, z);
                if (!level.getBiome(m).is(BIOME)) {
                    continue;
                }
                int y = SEA_TOP;
                while (y > level.getMinBuildHeight() + 1) {
                    m.set(x, y, z);
                    BlockState s = level.getBlockState(m);
                    if (!s.is(Blocks.LAVA)) {
                        break;
                    }
                    level.setBlock(m, water, 2);
                    any = true;
                    y--;
                }
                // fondo del mar
                if (y < SEA_TOP) {
                    m.set(x, y, z);
                    BlockState floor = level.getBlockState(m);
                    if (floor.is(Blocks.NETHERRACK) || floor.is(Blocks.SOUL_SAND) || floor.is(Blocks.SOUL_SOIL)) {
                        float k = rnd.nextFloat();
                        level.setBlock(m, k < 0.45f ? Blocks.CRIMSON_NYLIUM.defaultBlockState()
                                : (k < 0.75f ? Blocks.WARPED_NYLIUM.defaultBlockState() : Blocks.BLACKSTONE.defaultBlockState()), 2);
                        if (rnd.nextInt(40) == 0) {
                            level.setBlock(m, Blocks.SHROOMLIGHT.defaultBlockState(), 2);
                        }
                    }
                }
            }
        }
        return any;
    }
}
