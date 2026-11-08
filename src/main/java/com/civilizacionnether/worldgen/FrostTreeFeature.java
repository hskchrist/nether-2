package com.civilizacionnether.worldgen;

import com.civilizacionnether.registry.ModBlocks;
import com.mojang.serialization.Codec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Árbol de Hielo del Mar del Nether: tronco oscuro con raíces, copa ancha y aplastada de Hojas de Hielo, y por debajo
 * de la copa cuelgan hilos de hojas que terminan en carámbanos (como sauces congelados).
 */
public class FrostTreeFeature extends Feature<NoneFeatureConfiguration> {
    public FrostTreeFeature(Codec<NoneFeatureConfiguration> codec) {
        super(codec);
    }

    private static boolean ground(BlockState s) {
        return s.is(ModBlocks.NETHER_SEA_GRASS_BLOCK.get()) || s.is(Blocks.NETHERRACK) || s.is(BlockTags.NYLIUM);
    }

    private static boolean free(WorldGenLevel level, BlockPos p) {
        BlockState s = level.getBlockState(p);
        return s.isAir() || s.canBeReplaced() || s.getBlock() instanceof LeavesBlock;
    }

    @Override
    public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> ctx) {
        WorldGenLevel level = ctx.level();
        RandomSource rnd = ctx.random();
        BlockPos base = ctx.origin();
        if (!ground(level.getBlockState(base.below()))) {
            return false;
        }
        int height = 5 + rnd.nextInt(4);
        int radius = 3 + rnd.nextInt(2) + (height > 7 ? 1 : 0);
        // tiene que caber: tronco libre y algo de aire sobre la copa
        for (int y = 0; y <= height + 2; y++) {
            if (!free(level, base.above(y))) {
                return false;
            }
        }
        BlockState log = ModBlocks.FROST_LOG.get().defaultBlockState();
        BlockState leaves = ModBlocks.FROST_LEAVES.get().defaultBlockState();
        BlockState icicle = ModBlocks.FROST_ICICLE.get().defaultBlockState();
        Set<BlockPos> logs = new HashSet<>();
        Set<BlockPos> leafSet = new HashSet<>();

        level.setBlock(base.below(), ModBlocks.NETHER_SEA_GRASS_BLOCK.get().defaultBlockState(), 2);
        for (int y = 0; y < height; y++) {
            BlockPos p = base.above(y);
            level.setBlock(p, log, 2);
            logs.add(p);
        }
        // raíces
        for (Direction d : Direction.Plane.HORIZONTAL) {
            if (rnd.nextInt(3) != 0) {
                BlockPos r = base.relative(d);
                if (free(level, r) && ground(level.getBlockState(r.below()))) {
                    level.setBlock(r, log.setValue(RotatedPillarBlock.AXIS, d.getAxis()), 2);
                    logs.add(r);
                }
            }
        }
        // un par de ramas que salen de la parte alta del tronco
        BlockPos top = base.above(height - 1);
        for (Direction d : Direction.Plane.HORIZONTAL) {
            if (rnd.nextInt(2) == 0) {
                BlockPos b = top.below(1 + rnd.nextInt(2)).relative(d);
                if (free(level, b)) {
                    level.setBlock(b, log.setValue(RotatedPillarBlock.AXIS, d.getAxis()), 2);
                    logs.add(b);
                }
            }
        }
        // copa ancha y aplastada
        for (int dy = -1; dy <= 2; dy++) {
            int r = dy <= 0 ? radius : (dy == 1 ? radius - 1 : radius - 2);
            for (int dx = -r; dx <= r; dx++) {
                for (int dz = -r; dz <= r; dz++) {
                    double d = Math.sqrt(dx * dx + dz * dz);
                    if (d > r + 0.3 || (d > r - 0.7 && rnd.nextInt(3) == 0)) {
                        continue;
                    }
                    BlockPos p = top.offset(dx, dy, dz);
                    if (!logs.contains(p) && free(level, p)) {
                        leafSet.add(p);
                    }
                }
            }
        }
        // hilos colgando bajo la copa, con carámbano al final
        Map<BlockPos, Boolean> hanging = new HashMap<>();
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dz = -radius; dz <= radius; dz++) {
                double d = Math.sqrt(dx * dx + dz * dz);
                if (d < 1.5 || d > radius + 0.3 || rnd.nextInt(d > radius - 1.5 ? 2 : 5) != 0) {
                    continue;
                }
                BlockPos start = top.offset(dx, -2, dz);
                if (!leafSet.contains(start.above())) {
                    continue;
                }
                int len = 1 + rnd.nextInt(d > radius - 1.5 ? 4 : 2);
                BlockPos p = start;
                for (int i = 0; i < len && free(level, p); i++) {
                    leafSet.add(p);
                    p = p.below();
                }
                if (free(level, p) && rnd.nextInt(10) < 7) {
                    hanging.put(p, true);
                }
            }
        }
        // distancia de cada hoja al tronco (las muy lejanas quedan fijas para que no se caigan solas)
        Map<BlockPos, Integer> dist = new HashMap<>();
        ArrayDeque<BlockPos> queue = new ArrayDeque<>();
        for (BlockPos l : logs) {
            dist.put(l, 0);
            queue.add(l);
        }
        while (!queue.isEmpty()) {
            BlockPos p = queue.poll();
            int dp = dist.get(p);
            if (dp >= 6) {
                continue;
            }
            for (Direction d : Direction.values()) {
                BlockPos n = p.relative(d);
                if (leafSet.contains(n) && !dist.containsKey(n)) {
                    dist.put(n, dp + 1);
                    queue.add(n);
                }
            }
        }
        for (BlockPos p : leafSet) {
            Integer d = dist.get(p);
            level.setBlock(p, d == null ? leaves.setValue(LeavesBlock.PERSISTENT, true).setValue(LeavesBlock.DISTANCE, 7)
                    : leaves.setValue(LeavesBlock.DISTANCE, Math.max(1, d)), 2);
        }
        for (BlockPos p : hanging.keySet()) {
            if (level.getBlockState(p.above()).getBlock() instanceof LeavesBlock && free(level, p)) {
                level.setBlock(p, icicle, 2);
            }
        }
        return true;
    }
}
