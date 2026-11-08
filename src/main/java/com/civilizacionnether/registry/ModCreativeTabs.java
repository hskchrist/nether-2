package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, CivilizacionNether.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN = TABS.register("main", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.civilizacion_nether"))
            .icon(() -> new ItemStack(ModItems.RUBY.get()))
            .displayItems((params, output) -> {
                output.accept(ModItems.RUBY.get());
                output.accept(ModItems.RUBY_BLOCK.get());
                output.accept(ModItems.RUBY_ORE.get());
                output.accept(ModItems.RUBY_BRICKS.get());
                output.accept(ModItems.RUBY_LAMP.get());
                output.accept(ModItems.RUBY_SWORD.get());
                output.accept(ModItems.RUBY_BOW.get());
                output.accept(ModItems.NECRO_STAFF.get());
                output.accept(ModItems.RUBY_HELMET.get());
                output.accept(ModItems.RUBY_CHESTPLATE.get());
                output.accept(ModItems.RUBY_LEGGINGS.get());
                output.accept(ModItems.RUBY_BOOTS.get());
                output.accept(ModItems.SOUL.get());
                output.accept(ModItems.SOUL_SCYTHE.get());
                output.accept(ModItems.DRAGON_EGG.get());
                output.accept(ModItems.DRAGON_STAFF.get());
                output.accept(ModItems.DRAGON_ARMOR.get());
                output.accept(ModItems.RUBY_LONGSWORD.get());
                output.accept(ModItems.RUBY_CROSSBOW.get());
                output.accept(ModItems.HUMAN_HELMET.get());
                output.accept(ModItems.HUMAN_CHESTPLATE.get());
                output.accept(ModItems.HUMAN_LEGGINGS.get());
                output.accept(ModItems.HUMAN_BOOTS.get());
                output.accept(ModItems.FROST_HELMET.get());
                output.accept(ModItems.FROST_CHESTPLATE.get());
                output.accept(ModItems.FROST_LEGGINGS.get());
                output.accept(ModItems.FROST_BOOTS.get());
                output.accept(ModItems.ETERNAL_FROST_LEAF.get());
                output.accept(ModItems.FROST_LEAVES.get());
                output.accept(ModItems.FROST_LOG.get());
                output.accept(ModItems.FROST_ICICLE.get());
                output.accept(ModItems.NETHER_SEA_GRASS_BLOCK.get());
                output.accept(ModItems.NETHER_SEA_GRASS.get());
                output.accept(ModItems.NETHER_SEA_CRYSTAL.get());
                output.accept(ModItems.NECROMANCER_TABLE.get());
                output.accept(ModItems.LIBRARIAN_LECTERN.get());
                output.accept(ModItems.TAMER_NEST.get());
                output.accept(ModItems.FARMER_BASKET.get());
                output.accept(ModItems.MINER_CART.get());
                output.accept(ModItems.CARTOGRAPHER_DESK.get());
                output.accept(ModItems.FLETCHER_BENCH.get());
                output.accept(ModItems.LEATHER_CAULDRON.get());
                output.accept(ModItems.SHEPHERD_LOOM.get());
                output.accept(ModItems.MASON_CUTTER.get());
                output.accept(ModItems.NETHER_BED.get());
                output.accept(ModItems.NETHER_WATER_BUCKET.get());
                output.accept(ModItems.PEZ_BRASA.get());
                output.accept(ModItems.COOKED_PEZ_BRASA.get());
                output.accept(ModItems.DIENTES_TIBURON.get());
                output.accept(ModItems.ESCAMA_SERPIENTE.get());
                output.accept(ModItems.VOID_GEL.get());
                output.accept(ModItems.BASALT_SHELL.get());
                output.accept(ModItems.OBSIDIAN_SCALE.get());
                output.accept(ModItems.OBSIDIAN_TURTLE_HELMET.get());
                output.accept(ModItems.SERPENT_HELMET.get());
                output.accept(ModItems.RUBY_TRIDENT.get());
                output.accept(ModItems.INFERNAL_DRAGON_EGG.get());
                output.accept(ModItems.ALMAS_DRAGON_EGG.get());
                output.accept(ModItems.OBSIDIANA_DRAGON_EGG.get());
                output.accept(ModItems.INFERNAL_SADDLE.get());
                output.accept(ModItems.MANUAL.get());
                ModItems.SPAWN_EGGS.forEach(egg -> output.accept(egg.get()));
            })
            .build());

    private ModCreativeTabs() {
    }
}
