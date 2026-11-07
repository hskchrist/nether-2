package com.civilizacionnether.network;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.NetherDragonEntity;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Cliente → servidor: el jinete pulsó G (agarrar al mob de adelante o lanzar el que lleva). */
public record DragonGrabPayload() implements CustomPacketPayload {
    public static final Type<DragonGrabPayload> TYPE = new Type<>(CivilizacionNether.id("dragon_grab"));
    public static final StreamCodec<ByteBuf, DragonGrabPayload> STREAM_CODEC = StreamCodec.unit(new DragonGrabPayload());

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void handle(DragonGrabPayload payload, IPayloadContext context) {
        context.enqueueWork(() -> {
            if (context.player().getVehicle() instanceof NetherDragonEntity dragon && dragon.isOwnedBy(context.player())) {
                dragon.riderGrab(context.player());
            }
        });
    }
}
