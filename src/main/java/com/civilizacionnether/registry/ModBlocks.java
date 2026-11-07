package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.block.NetherBedBlock;
import com.civilizacionnether.block.WorkstationBlock;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(CivilizacionNether.MODID);

    public static final DeferredBlock<Block> RUBY_BLOCK = BLOCKS.register("ruby_block", () -> new Block(
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(5.0f, 6.0f)
                    .requiresCorrectToolForDrops().sound(SoundType.METAL)));

    public static final DeferredBlock<Block> RUBY_ORE = BLOCKS.register("ruby_ore", () -> new DropExperienceBlock(
            UniformInt.of(3, 7),
            BlockBehaviour.Properties.of().mapColor(MapColor.NETHER).strength(3.0f, 3.0f)
                    .requiresCorrectToolForDrops().sound(SoundType.NETHER_GOLD_ORE)));

    public static final DeferredBlock<Block> RUBY_LAMP = BLOCKS.register("ruby_lamp", () -> new Block(
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(1.5f)
                    .lightLevel(state -> 15).sound(SoundType.GLASS)));

    public static final DeferredBlock<Block> RUBY_BRICKS = BLOCKS.register("ruby_bricks", () -> new Block(
            BlockBehaviour.Properties.of().mapColor(MapColor.NETHER).strength(2.0f, 6.0f)
                    .requiresCorrectToolForDrops().sound(SoundType.NETHER_BRICKS)));

    // ---------------------------------------------------------------- mesas de trabajo de las profesiones
    private static DeferredBlock<WorkstationBlock> station(String name, VoxelShape shape, SoundType sound, MapColor color) {
        return BLOCKS.register(name, () -> new WorkstationBlock(BlockBehaviour.Properties.of().mapColor(color)
                .strength(2.0f, 3.0f).sound(sound).noOcclusion(), shape));
    }

    /** Mesa del Aldeano Necromancer (modelo oficial del usuario). */
    public static final DeferredBlock<WorkstationBlock> NECROMANCER_TABLE = station("necromancer_table",
            Block.box(1.4, 0, 1.4, 14.6, 15.7, 14.6), SoundType.WOOD, MapColor.COLOR_RED);
    public static final DeferredBlock<WorkstationBlock> LIBRARIAN_LECTERN = station("librarian_lectern",
            Shapes.or(Block.box(2, 0, 2, 14, 2, 14), Block.box(6, 2, 6, 10, 11, 10), Block.box(2, 11, 3, 14, 14, 13)),
            SoundType.STONE, MapColor.COLOR_BLACK);
    public static final DeferredBlock<WorkstationBlock> TAMER_NEST = station("tamer_nest",
            Block.box(1, 0, 1, 15, 10, 15), SoundType.GRASS, MapColor.COLOR_RED);
    public static final DeferredBlock<WorkstationBlock> FARMER_BASKET = station("farmer_basket",
            Block.box(1, 0, 1, 15, 11, 15), SoundType.WOOD, MapColor.CRIMSON_STEM);
    public static final DeferredBlock<WorkstationBlock> MINER_CART = station("miner_cart",
            Block.box(1, 0, 1, 15, 11, 15), SoundType.METAL, MapColor.METAL);

    // mesas de los aldeanos del Nether (el aldeano sin oficio que la toma se vuelve de esa profesión)
    public static final DeferredBlock<WorkstationBlock> CARTOGRAPHER_DESK = station("cartographer_desk",
            Block.box(0, 0, 0, 16, 15, 16), SoundType.WOOD, MapColor.CRIMSON_STEM);
    public static final DeferredBlock<WorkstationBlock> FLETCHER_BENCH = station("fletcher_bench",
            Block.box(0, 0, 0, 16, 15, 16), SoundType.WOOD, MapColor.CRIMSON_STEM);
    public static final DeferredBlock<WorkstationBlock> LEATHER_CAULDRON = station("leather_cauldron",
            Shapes.block(), SoundType.STONE, MapColor.COLOR_BLACK);
    public static final DeferredBlock<WorkstationBlock> SHEPHERD_LOOM = station("shepherd_loom",
            Shapes.block(), SoundType.WOOD, MapColor.CRIMSON_STEM);
    public static final DeferredBlock<WorkstationBlock> MASON_CUTTER = station("mason_cutter",
            Block.box(0, 0, 0, 16, 9, 16), SoundType.STONE, MapColor.COLOR_BLACK);

    /** Cama del Nether: se puede dormir en el Nether sin que explote. */
    public static final DeferredBlock<NetherBedBlock> NETHER_BED = BLOCKS.register("nether_bed", () -> new NetherBedBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_PURPLE).sound(SoundType.WOOD).strength(0.2f)
                    .noOcclusion().pushReaction(PushReaction.DESTROY)));

    /** Agua del Nether: morada, no se evapora en el Nether y riega los cultivos. */
    public static final DeferredBlock<LiquidBlock> NETHER_WATER = BLOCKS.register("nether_water", () -> new LiquidBlock(
            ModFluids.NETHER_WATER.get(), BlockBehaviour.Properties.ofFullCopy(Blocks.WATER).mapColor(MapColor.COLOR_PURPLE)
                    .lightLevel(state -> 4)));

    /** Hojas del árbol de hielo de Picos de Hielo (con tijeras se obtienen; dan la Hoja del Frío Eterno). */
    public static final DeferredBlock<LeavesBlock> FROST_LEAVES = BLOCKS.register("frost_leaves", () -> new LeavesBlock(
            BlockBehaviour.Properties.ofFullCopy(Blocks.SPRUCE_LEAVES).mapColor(MapColor.ICE).lightLevel(state -> 3)));

    private ModBlocks() {
    }
}
