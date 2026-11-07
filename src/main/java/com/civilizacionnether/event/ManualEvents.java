package com.civilizacionnether.event;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;

/** La primera vez que un jugador entra a un mundo recibe el Manual (una sola vez; si lo pierde, se craftea). */
@EventBusSubscriber(modid = CivilizacionNether.MODID)
public final class ManualEvents {
    /** Datos del jugador que se conservan aunque muera. */
    private static final String PERSISTED = "PlayerPersisted";
    private static final String KEY = "civilizacion_nether.got_manual";

    @SubscribeEvent
    public static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        CompoundTag data = player.getPersistentData();
        CompoundTag persisted = data.getCompound(PERSISTED);
        if (persisted.getBoolean(KEY)) {
            return;
        }
        persisted.putBoolean(KEY, true);
        data.put(PERSISTED, persisted);
        ItemStack manual = new ItemStack(ModItems.MANUAL.get());
        if (!player.getInventory().add(manual)) {
            player.drop(manual, false);
        }
    }

    private ManualEvents() {
    }
}
