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
                ModItems.SPAWN_EGGS.forEach(egg -> output.accept(egg.get()));
            })
            .build());

    private ModCreativeTabs() {
    }
}
