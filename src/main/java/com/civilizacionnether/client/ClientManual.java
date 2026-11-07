package com.civilizacionnether.client;

import net.minecraft.client.Minecraft;

/** Solo del cliente: abre la pantalla del manual. */
public final class ClientManual {
    public static void open() {
        Minecraft.getInstance().setScreen(new ManualScreen());
    }

    private ClientManual() {
    }
}
