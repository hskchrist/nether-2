package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.DropExperienceBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
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

    private ModBlocks() {
    }
}
