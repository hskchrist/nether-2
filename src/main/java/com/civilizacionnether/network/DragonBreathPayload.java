package com.civilizacionnether.network;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.NetherDragonEntity;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Cliente → servidor: el jinete pulsó R (ráfaga de fuego grande si la barra está cargada). */
public record DragonBreathPayload() implements CustomPacketPayload {
    public static final Type<DragonBreathPayload> TYPE = new Type<>(CivilizacionNether.id("dragon_breath"));
    public static final StreamCodec<ByteBuf, DragonBreathPayload> STREAM_CODEC = StreamCodec.unit(new DragonBreathPayload());

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void handle(DragonBreathPayload payload, IPayloadContext context) {
        context.enqueueWork(() -> {
            if (context.player().getVehicle() instanceof NetherDragonEntity dragon && dragon.isOwnedBy(context.player())) {
                dragon.riderSpecial(context.player());
            }
        });
    }
}
