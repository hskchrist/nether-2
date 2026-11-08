package com.civilizacionnether.worldgen;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.registry.ModBlocks;
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
 * La pieza del Reino Humano del Nether (192 x 192). Antes de colocar la plantilla (data/civilizacion_nether/structure/capital.nbt),
 * en cada chunk: excava el aire, levanta la isla redonda de piedra negra (radio 84 + borde de 2) y deja alrededor el
 * Mar del Nether de agua del Nether. Así la plantilla no necesita guardar aire y pesa mucho menos.
 */
public class CapitalPiece extends TemplateStructurePiece {
    public static final ResourceLocation TEMPLATE = CivilizacionNether.id("capital");
    public static final int SIZE = 192;
    public static final int HEIGHT = 80;
    public static final int FLOOR = 4;
    private static final double CENTER = 96.0;
    private static final double ISLAND = 84.5;
    private static final double RIM = 86.5;

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
        BlockState blackstone = Blocks.BLACKSTONE.defaultBlockState();
        BlockState basalt = Blocks.BASALT.defaultBlockState();
        BlockState water = ModBlocks.NETHER_WATER.get().defaultBlockState();
        BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
        for (int x = minX; x <= maxX; x++) {
            for (int z = minZ; z <= maxZ; z++) {
                double dx = x - origin.getX() + 0.5 - CENTER;
                double dz = z - origin.getZ() + 0.5 - CENTER;
                double r = Math.sqrt(dx * dx + dz * dz);
                if (r <= RIM) {
                    // la isla: aire arriba, piso de ladrillo (o borde de piedra negra) y un cimiento macizo hasta abajo
                    for (int y = baseY + FLOOR; y < baseY + HEIGHT; y++) {
                        level.setBlock(p.set(x, y, z), air, 2);
                    }
                    level.setBlock(p.set(x, baseY + FLOOR - 1, z), r <= ISLAND ? bricks : blackstone, 2);
                    for (int y = baseY - 10; y < baseY + FLOOR - 1; y++) {
                        level.setBlock(p.set(x, y, z), (x * 7 + y * 3 + z * 5) % 11 == 0 ? basalt : blackstone, 2);
                    }
                } else {
                    // el Mar del Nether alrededor del reino (la superficie queda a la altura del mar del Nether)
                    for (int y = baseY + 2; y < baseY + HEIGHT; y++) {
                        level.setBlock(p.set(x, y, z), air, 2);
                    }
                    for (int y = baseY - 6; y <= baseY + 1; y++) {
                        level.setBlock(p.set(x, y, z), water, 2);
                    }
                    level.setBlock(p.set(x, baseY - 7, z), blackstone, 2);
                }
            }
        }
        super.postProcess(level, structureManager, generator, random, box, chunkPos, pivot);
    }
}
