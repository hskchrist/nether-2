package com.civilizacionnether.network;

import com.civilizacionnether.CivilizacionNether;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.neoforged.neoforge.network.handling.IPayloadContext;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/**
 * Servidor → cliente: este tridente lanzado es un Tridente de Rubí (así se dibuja rojo y dorado en el aire).
 * Se manda cuando el jugador empieza a ver el tridente.
 */
public record RubyTridentPayload(int entityId) implements CustomPacketPayload {
    public static final Type<RubyTridentPayload> TYPE = new Type<>(CivilizacionNether.id("ruby_trident"));
    public static final StreamCodec<ByteBuf, RubyTridentPayload> STREAM_CODEC =
            ByteBufCodecs.VAR_INT.map(RubyTridentPayload::new, RubyTridentPayload::entityId);
    /** Ids (del lado del cliente) de los tridentes lanzados que son de rubí. */
    public static final Set<Integer> RUBY_TRIDENTS = Collections.synchronizedSet(new HashSet<>());

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void handle(RubyTridentPayload payload, IPayloadContext context) {
        context.enqueueWork(() -> {
            if (RUBY_TRIDENTS.size() > 512) {
                RUBY_TRIDENTS.clear();
            }
            RUBY_TRIDENTS.add(payload.entityId());
        });
    }
}
