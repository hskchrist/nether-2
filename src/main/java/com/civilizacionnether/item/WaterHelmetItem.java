package com.civilizacionnether.item;

import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.network.chat.Component;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * Cascos del mar: el de Tortuga Obsidiana deja respirar bajo el agua; el de la Serpiente además deja ver
 * bajo el agua (visión nocturna) y nadar más rápido (gracia del delfín).
 */
public class WaterHelmetItem extends ArmorItem {
    private final boolean serpent;

    public WaterHelmetItem(Holder<ArmorMaterial> material, Properties properties, boolean serpent) {
        super(material, Type.HELMET, properties);
        this.serpent = serpent;
    }

    @Override
    public void inventoryTick(ItemStack stack, Level level, Entity entity, int slot, boolean selected) {
        super.inventoryTick(stack, level, entity, slot, selected);
        if (level.isClientSide || !(entity instanceof Player player) || player.getItemBySlot(EquipmentSlot.HEAD) != stack) {
            return;
        }
        if (player.tickCount % 20 != 0) {
            return;
        }
        player.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 220, 0, false, false, true));
        if (serpent && player.isInWater()) {
            player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 420, 0, false, false, true));
            player.addEffect(new MobEffectInstance(MobEffects.DOLPHINS_GRACE, 60, 0, false, false, true));
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> lines, TooltipFlag flag) {
        lines.add(Component.translatable(serpent ? "tooltip.civilizacion_nether.serpent_helmet"
                : "tooltip.civilizacion_nether.obsidian_turtle_helmet").withStyle(ChatFormatting.AQUA));
    }
}
