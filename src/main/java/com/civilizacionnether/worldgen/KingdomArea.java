package com.civilizacionnether.worldgen;

import com.civilizacionnether.CivilizacionNether;
import net.minecraft.core.BlockPos;
import net.minecraft.core.QuartPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.StructureSet;
import net.minecraft.world.level.levelgen.structure.placement.RandomSpreadStructurePlacement;

/**
 * ¿Va a haber un Reino en este lugar? Calcula dónde cae el Reino (igual que el juego: misma grilla y semilla) sin leer
 * chunks lejanos, para que los árboles, lagos y manantiales no aparezcan donde se construye el Reino (si no, quedaban
 * copas de árboles flotando sobre el reino y agua cayendo adentro).
 */
public final class KingdomArea {
    private static final int HALF = CapitalPiece.SIZE / 2;

    public static boolean near(WorldGenLevel level, ChunkGenerator generator, BlockPos pos, int margin) {
        try {
            StructureSet set = level.registryAccess().registryOrThrow(Registries.STRUCTURE_SET).get(CivilizacionNether.id("capital"));
            if (set == null || !(set.placement() instanceof RandomSpreadStructurePlacement spread)) {
                return false;
            }
            long seed = level.getSeed();
            int spacing = spread.spacing();
            int cx = pos.getX() >> 4;
            int cz = pos.getZ() >> 4;
            int gx0 = Math.floorDiv(cx, spacing);
            int gz0 = Math.floorDiv(cz, spacing);
            var sampler = level.getLevel().getChunkSource().randomState().sampler();
            for (int dx = -1; dx <= 1; dx++) {
                for (int dz = -1; dz <= 1; dz++) {
                    ChunkPos c = spread.getPotentialStructureChunk(seed, (gx0 + dx) * spacing, (gz0 + dz) * spacing);
                    int mx = c.getMiddleBlockX();
                    int mz = c.getMiddleBlockZ();
                    if (Math.abs(pos.getX() - mx) > HALF + margin || Math.abs(pos.getZ() - mz) > HALF + margin) {
                        continue;
                    }
                    // el Reino sólo existe si en su centro está el Mar del Nether
                    var biome = generator.getBiomeSource().getNoiseBiome(QuartPos.fromBlock(mx),
                            QuartPos.fromBlock(CapitalStructure.BASE_Y + CapitalPiece.FLOOR), QuartPos.fromBlock(mz), sampler);
                    if (biome.is(PurpleSeaFeature.BIOME)) {
                        return true;
                    }
                }
            }
        } catch (RuntimeException e) {
            return false;
        }
        return false;
    }

    private KingdomArea() {
    }
}
