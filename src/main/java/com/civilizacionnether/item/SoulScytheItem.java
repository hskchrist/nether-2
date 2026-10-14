package com.civilizacionnether.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.HoeItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/**
 * Hoz de almas: al romper arena de almas suelta almas (1 sin encantar; con Fortuna I 1-2, II 2-3, III 3).
 * También sirve como arma (golpe fuerte y lento) y como azada.
 */
public class SoulScytheItem extends HoeItem {
    public SoulScytheItem(Tier tier, Properties properties) {
        super(tier, properties);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.civilizacion_nether.soul_scythe").withStyle(ChatFormatting.RED));
        tooltip.add(Component.translatable("tooltip.civilizacion_nether.soul_scythe2").withStyle(ChatFormatting.GRAY));
    }
}
