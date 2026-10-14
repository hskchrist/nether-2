package com.civilizacionnether.item;

import com.civilizacionnether.entity.DragonEggEntity;
import com.civilizacionnether.registry.ModEntities;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

import java.util.List;

/** Huevo de Dragón del Nether: clic derecho sobre el suelo para ponerlo; la cría que nazca será tuya. */
public class DragonEggItem extends Item {
    public DragonEggItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        BlockPos pos = context.getClickedPos().relative(context.getClickedFace());
        if (!level.getBlockState(pos).getCollisionShape(level, pos).isEmpty()) {
            return InteractionResult.FAIL;
        }
        if (!(level instanceof ServerLevel server)) {
            return InteractionResult.SUCCESS;
        }
        DragonEggEntity egg = ModEntities.DRAGON_EGG.get().create(server);
        if (egg == null) {
            return InteractionResult.FAIL;
        }
        Player player = context.getPlayer();
        egg.moveTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5,
                player != null ? player.getYRot() + 180.0f : 0.0f, 0.0f);
        egg.setPersistenceRequired();
        if (player != null) {
            egg.setOwner(player.getUUID());
            player.displayClientMessage(Component.translatable("msg.civilizacion_nether.egg_placed"), true);
        }
        server.addFreshEntity(egg);
        level.playSound(null, pos, SoundEvents.TURTLE_LAY_EGG, SoundSource.BLOCKS, 1.0f, 0.7f);
        ItemStack stack = context.getItemInHand();
        if (player == null || !player.getAbilities().instabuild) {
            stack.shrink(1);
        }
        return InteractionResult.CONSUME;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.civilizacion_nether.dragon_egg").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("tooltip.civilizacion_nether.dragon_egg2").withStyle(ChatFormatting.GRAY));
    }
}
