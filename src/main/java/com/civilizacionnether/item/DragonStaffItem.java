package com.civilizacionnether.item;

import com.civilizacionnether.entity.NetherDragonEntity;
import com.civilizacionnether.registry.ModParticles;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.Level;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Báculo de dragón.
 * <ul>
 *   <li>Clic derecho: tu dragón viene hacia ti desde donde esté (volando si está lejos, caminando si está cerca).</li>
 *   <li>Mayús + clic derecho: activa o desactiva el modo libre (anda, vuela y descansa por su cuenta).</li>
 *   <li>Clic derecho sobre un dragón tuyo: vincula el báculo a ese dragón. Sin vincular, actúa sobre todos tus
 *       dragones a menos de 160 bloques.</li>
 * </ul>
 */
public class DragonStaffItem extends Item {
    private static final String KEY = "BoundDragon";
    private static final String NAME = "BoundDragonName";

    public DragonStaffItem(Properties properties) {
        super(properties);
    }

    public static void bind(ItemStack stack, NetherDragonEntity dragon) {
        CompoundTag tag = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        tag.putUUID(KEY, dragon.getUUID());
        tag.putString(NAME, dragon.getDisplayName().getString());
        stack.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
    }

    private static List<NetherDragonEntity> targets(ServerLevel level, Player player, ItemStack stack) {
        List<NetherDragonEntity> out = new ArrayList<>();
        CompoundTag tag = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        if (tag.hasUUID(KEY)) {
            UUID id = tag.getUUID(KEY);
            Entity e = level.getEntity(id);
            if (e instanceof NetherDragonEntity d && d.isOwnedBy(player)) {
                out.add(d);
            }
            return out;
        }
        out.addAll(level.getEntitiesOfClass(NetherDragonEntity.class, player.getBoundingBox().inflate(160.0),
                d -> d.isAlive() && d.isOwnedBy(player) && !d.isVehicle()));
        return out;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(level instanceof ServerLevel server)) {
            return InteractionResultHolder.success(stack);
        }
        if (player.getVehicle() instanceof NetherDragonEntity) {
            return InteractionResultHolder.pass(stack);
        }
        List<NetherDragonEntity> dragons = targets(server, player, stack);
        if (dragons.isEmpty()) {
            player.displayClientMessage(Component.translatable("msg.civilizacion_nether.staff_none"), true);
            return InteractionResultHolder.fail(stack);
        }
        if (player.isSecondaryUseActive()) {
            boolean free = !dragons.get(0).isFree();
            for (NetherDragonEntity d : dragons) {
                d.setFree(free);
                d.stopRecall();
            }
            player.displayClientMessage(Component.translatable(free ? "msg.civilizacion_nether.staff_free"
                    : "msg.civilizacion_nether.staff_follow", dragons.get(0).getDisplayName()), true);
        } else {
            for (NetherDragonEntity d : dragons) {
                d.recall(player);
            }
            player.displayClientMessage(Component.translatable("msg.civilizacion_nether.staff_recall",
                    dragons.get(0).getDisplayName(), (int) dragons.get(0).distanceTo(player)), true);
        }
        server.sendParticles(ModParticles.RED_SOUL.get(), player.getX(), player.getY() + 1.5, player.getZ(), 10, 0.4, 0.4, 0.4, 0.02);
        level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.ENDER_DRAGON_AMBIENT,
                SoundSource.PLAYERS, 0.6f, 1.5f);
        player.getCooldowns().addCooldown(this, 20);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        CompoundTag tag = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        if (tag.contains(NAME)) {
            tooltip.add(Component.translatable("tooltip.civilizacion_nether.staff_bound", tag.getString(NAME)).withStyle(ChatFormatting.GOLD));
        } else {
            tooltip.add(Component.translatable("tooltip.civilizacion_nether.staff_unbound").withStyle(ChatFormatting.GRAY));
        }
        tooltip.add(Component.translatable("tooltip.civilizacion_nether.staff_use").withStyle(ChatFormatting.RED));
        tooltip.add(Component.translatable("tooltip.civilizacion_nether.staff_use2").withStyle(ChatFormatting.RED));
    }
}
