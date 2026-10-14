package com.civilizacionnether.worldgen;

import com.civilizacionnether.registry.ModStructures;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

import java.util.Optional;

/**
 * Capital del Reino del Nether: una sola pieza gigante (176 x 176 bloques) centrada en el chunk elegido.
 * La pieza excava su propia caverna, así que se ve completa aunque el Nether sea macizo en ese lugar.
 */
public class CapitalStructure extends Structure {
    public static final MapCodec<CapitalStructure> CODEC = simpleCodec(CapitalStructure::new);
    /** Altura de la base de la plantilla: el suelo de la ciudad queda en y = 34, justo sobre el mar de lava. */
    public static final int BASE_Y = 30;

    public CapitalStructure(StructureSettings settings) {
        super(settings);
    }

    @Override
    protected Optional<GenerationStub> findGenerationPoint(GenerationContext context) {
        ChunkPos chunk = context.chunkPos();
        BlockPos origin = new BlockPos(chunk.getMiddleBlockX() - CapitalPiece.SIZE / 2, BASE_Y,
                chunk.getMiddleBlockZ() - CapitalPiece.SIZE / 2);
        BlockPos center = new BlockPos(chunk.getMiddleBlockX(), BASE_Y + CapitalPiece.FLOOR, chunk.getMiddleBlockZ());
        return Optional.of(new GenerationStub(center,
                builder -> builder.addPiece(new CapitalPiece(context.structureTemplateManager(), origin))));
    }

    @Override
    public StructureType<?> type() {
        return ModStructures.CAPITAL.get();
    }
}
