package com.civilizacionnether.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** Armadura opcional para dragones domesticados (+12 de armadura, se ve sobre el dragón). */
public class DragonArmorItem extends Item {
    public DragonArmorItem(Properties properties) {
        super(properties);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.civilizacion_nether.dragon_armor").withStyle(ChatFormatting.GOLD));
    }
}
