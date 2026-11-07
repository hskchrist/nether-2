package com.civilizacionnether.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.TridentItem;
import net.minecraft.world.item.component.ItemAttributeModifiers;

import java.util.List;

/**
 * Tridente de Rubí: se hace con dientes de tiburón, prismarina y rubí. Funciona igual que el tridente (mismo daño,
 * se lanza, se clava, acepta Lealtad, Canalización, Propulsión y Empalamiento), pero lanzado va en llamas y quema a lo
 * que golpea, y en la mano suelta chispas de fuego (SeaEvents y client/RubyTridentEffects). Dura el doble.
 */
public class RubyTridentItem extends TridentItem {
    public RubyTridentItem(Properties properties) {
        super(properties);
    }

    public static ItemAttributeModifiers createRubyAttributes() {
        return ItemAttributeModifiers.builder()
                .add(Attributes.ATTACK_DAMAGE, new AttributeModifier(BASE_ATTACK_DAMAGE_ID, 8.0, AttributeModifier.Operation.ADD_VALUE),
                        EquipmentSlotGroup.MAINHAND)
                .add(Attributes.ATTACK_SPEED, new AttributeModifier(BASE_ATTACK_SPEED_ID, -2.9f, AttributeModifier.Operation.ADD_VALUE),
                        EquipmentSlotGroup.MAINHAND)
                .build();
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> lines, TooltipFlag flag) {
        lines.add(Component.translatable("tooltip.civilizacion_nether.ruby_trident").withStyle(ChatFormatting.RED));
    }
}
