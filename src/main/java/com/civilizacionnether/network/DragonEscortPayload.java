package com.civilizacionnether.network;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.NetherDragonEntity;
import com.civilizacionnether.entity.ai.DragonEscortGoal;
import com.civilizacionnether.item.DragonStaffItem;
import com.civilizacionnether.registry.ModItems;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/**
 * Cliente → servidor: T con el Báculo de dragón en la mano. Tus dragones dejan de estar libres o sentados y te siguen;
 * si vas volando en un dragón, despegan y te escoltan volando (sólo se teletransportan si no pueden llegar volando).
 */
public record DragonEscortPayload() implements CustomPacketPayload {
    public static final Type<DragonEscortPayload> TYPE = new Type<>(CivilizacionNether.id("dragon_escort"));
    public static final StreamCodec<ByteBuf, DragonEscortPayload> STREAM_CODEC = StreamCodec.unit(new DragonEscortPayload());

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void handle(DragonEscortPayload payload, IPayloadContext context) {
        context.enqueueWork(() -> {
            Player player = context.player();
            if (!(player.level() instanceof ServerLevel server)) {
                return;
            }
            ItemStack staff = player.getMainHandItem().is(ModItems.DRAGON_STAFF.get()) ? player.getMainHandItem()
                    : player.getOffhandItem().is(ModItems.DRAGON_STAFF.get()) ? player.getOffhandItem() : ItemStack.EMPTY;
            if (staff.isEmpty()) {
                return;
            }
            boolean flying = DragonEscortGoal.ownerFlies(player);
            int n = 0;
            for (NetherDragonEntity d : DragonStaffItem.targets(server, player, staff)) {
                if (d == player.getVehicle()) {
                    continue;
                }
                d.setFree(false);
                d.setOrderedToSit(false);
                d.setResting(false);
                d.stopRecall();
                if (flying && d.canFlyNow()) {
                    d.takeOff();
                }
                n++;
            }
            player.displayClientMessage(Component.translatable(n == 0 ? "msg.civilizacion_nether.staff_none"
                    : flying ? "msg.civilizacion_nether.staff_escort_fly" : "msg.civilizacion_nether.staff_escort", n), true);
            if (n > 0) {
                server.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.ENDER_DRAGON_FLAP, SoundSource.PLAYERS, 0.8f, 1.3f);
            }
        });
    }
}
