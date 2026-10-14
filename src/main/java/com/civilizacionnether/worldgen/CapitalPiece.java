package com.civilizacionnether.worldgen;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.registry.ModStructures;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.TemplateStructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;

/**
 * La pieza de la capital. Antes de colocar la plantilla (data/civilizacion_nether/structure/capital.nbt), en cada chunk:
 * excava la caverna (aire), pone la plataforma de piedra negra y los pilares de ladrillo del Nether sobre la lava.
 * Así la plantilla no necesita guardar aire y pesa mucho menos.
 */
public class CapitalPiece extends TemplateStructurePiece {
    public static final ResourceLocation TEMPLATE = CivilizacionNether.id("capital");
    public static final int SIZE = 176;
    public static final int HEIGHT = 72;
    public static final int FLOOR = 4;
    private static final int WALL0 = 8;
    private static final int WALL1 = 167;

    public CapitalPiece(StructureTemplateManager manager, BlockPos origin) {
        super(ModStructures.CAPITAL_PIECE.get(), 0, manager, TEMPLATE, TEMPLATE.toString(), new StructurePlaceSettings(), origin);
    }

    public CapitalPiece(StructurePieceSerializationContext context, CompoundTag tag) {
        super(ModStructures.CAPITAL_PIECE.get(), tag, context.structureTemplateManager(), id -> new StructurePlaceSettings());
    }

    @Override
    protected void handleDataMarker(String name, BlockPos pos, ServerLevelAccessor level, RandomSource random, BoundingBox box) {
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager structureManager, ChunkGenerator generator, RandomSource random,
                            BoundingBox box, ChunkPos chunkPos, BlockPos pivot) {
        BlockPos origin = this.templatePosition;
        int minX = Math.max(origin.getX(), box.minX());
        int maxX = Math.min(origin.getX() + SIZE - 1, box.maxX());
        int minZ = Math.max(origin.getZ(), box.minZ());
        int maxZ = Math.min(origin.getZ() + SIZE - 1, box.maxZ());
        int baseY = origin.getY();
        BlockState air = Blocks.AIR.defaultBlockState();
        BlockState bricks = Blocks.POLISHED_BLACKSTONE_BRICKS.defaultBlockState();
        BlockState netherrack = Blocks.NETHERRACK.defaultBlockState();
        BlockState blackstone = Blocks.BLACKSTONE.defaultBlockState();
        BlockState pillar = Blocks.NETHER_BRICKS.defaultBlockState();
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int x = minX; x <= maxX; x++) {
            for (int z = minZ; z <= maxZ; z++) {
                int lx = x - origin.getX();
                int lz = z - origin.getZ();
                boolean inside = lx >= WALL0 && lx <= WALL1 && lz >= WALL0 && lz <= WALL1;
                for (int y = baseY + FLOOR; y < baseY + HEIGHT; y++) {
                    level.setBlock(p.set(x, y, z), air, 2);
                }
                level.setBlock(p.set(x, baseY + FLOOR - 1, z), inside ? bricks : netherrack, 2);
                level.setBlock(p.set(x, baseY + FLOOR - 2, z), blackstone, 2);
                if (lx % 6 < 2 && lz % 6 < 2) {
                    for (int y = baseY; y < baseY + FLOOR - 2; y++) {
                        level.setBlock(p.set(x, y, z), pillar, 2);
                    }
                }
            }
        }
        super.postProcess(level, structureManager, generator, random, box, chunkPos, pivot);
    }
}
