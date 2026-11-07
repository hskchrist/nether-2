package com.civilizacionnether.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** Ítem simple con una línea de ayuda debajo del nombre. */
public class TooltipItem extends Item {
    private final String tooltip;

    public TooltipItem(Properties properties, String tooltip) {
        super(properties);
        this.tooltip = tooltip;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> lines, TooltipFlag flag) {
        lines.add(Component.translatable(tooltip).withStyle(ChatFormatting.GRAY));
    }
}
