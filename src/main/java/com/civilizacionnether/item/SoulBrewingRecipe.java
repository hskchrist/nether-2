package com.civilizacionnether.item;

import com.civilizacionnether.registry.ModItems;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionContents;
import net.minecraft.world.item.component.CustomData;
import net.neoforged.neoforge.common.brewing.IBrewingRecipe;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Soporte para pociones: Alma (arriba) + pociones (abajo) = pociones encantadas (brillan).
 * <ul>
 *   <li>Botella de agua, poción rara, vulgar o espesa → <b>Poción de Alma</b>: Fuerza, Resistencia,
 *       Resistencia al fuego y Regeneración.</li>
 *   <li>Cualquier poción con efectos → la misma poción <b>encantada</b>: cada efecto sube un nivel y dura 50 % más.</li>
 * </ul>
 * Funciona con pociones normales, arrojadizas y persistentes. Una poción encantada no se puede volver a encantar.
 */
public class SoulBrewingRecipe implements IBrewingRecipe {
    private static final String MARK = "SoulEnchanted";
    private static final int SOUL_POTION_COLOR = 0xF2B21E;

    public static boolean isSoulEnchanted(ItemStack stack) {
        return stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().getBoolean(MARK);
    }

    @Override
    public boolean isInput(ItemStack input) {
        return (input.is(Items.POTION) || input.is(Items.SPLASH_POTION) || input.is(Items.LINGERING_POTION))
                && !isSoulEnchanted(input);
    }

    @Override
    public boolean isIngredient(ItemStack ingredient) {
        return ingredient.is(ModItems.SOUL.get());
    }

    @Override
    public ItemStack getOutput(ItemStack input, ItemStack ingredient) {
        if (!isInput(input) || !isIngredient(ingredient)) {
            return ItemStack.EMPTY;
        }
        PotionContents contents = input.getOrDefault(DataComponents.POTION_CONTENTS, PotionContents.EMPTY);
        List<MobEffectInstance> effects = new ArrayList<>();
        for (MobEffectInstance e : contents.getAllEffects()) {
            int duration = e.getEffect().value().isInstantenous() ? 1 : (int) (e.getDuration() * 1.5f);
            effects.add(new MobEffectInstance(e.getEffect(), duration, Math.min(e.getAmplifier() + 1, 4)));
        }
        Component name;
        int color;
        if (effects.isEmpty()) {
            effects.add(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 3600, 0));
            effects.add(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 3600, 0));
            effects.add(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 3600, 0));
            effects.add(new MobEffectInstance(MobEffects.REGENERATION, 900, 0));
            name = Component.translatable("item.civilizacion_nether.soul_potion");
            color = SOUL_POTION_COLOR;
        } else {
            name = Component.translatable("item.civilizacion_nether.enchanted_potion", input.getHoverName());
            color = contents.getColor();
        }
        ItemStack out = new ItemStack(input.getItem());
        out.set(DataComponents.POTION_CONTENTS, new PotionContents(Optional.empty(), Optional.of(color), effects));
        out.set(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true);
        out.set(DataComponents.ITEM_NAME, name);
        CompoundTag tag = new CompoundTag();
        tag.putBoolean(MARK, true);
        out.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
        return out;
    }
}
