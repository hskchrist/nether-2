package com.civilizacionnether.network;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.NetherDragonEntity;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Cliente → servidor: el jinete hizo clic derecho (bola de fuego; cada disparo carga la barra). */
public record DragonShootPayload() implements CustomPacketPayload {
    public static final Type<DragonShootPayload> TYPE = new Type<>(CivilizacionNether.id("dragon_shoot"));
    public static final StreamCodec<ByteBuf, DragonShootPayload> STREAM_CODEC = StreamCodec.unit(new DragonShootPayload());

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void handle(DragonShootPayload payload, IPayloadContext context) {
        context.enqueueWork(() -> {
            if (context.player().getVehicle() instanceof NetherDragonEntity dragon && dragon.isOwnedBy(context.player())) {
                dragon.riderShoot(context.player());
            }
        });
    }
}
