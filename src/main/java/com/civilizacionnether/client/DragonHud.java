package com.civilizacionnether.client;

import com.civilizacionnether.entity.NetherDragonEntity;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;

/**
 * Barra de carga de la ráfaga (debajo de la mira, solo montado en un dragón adulto):
 * cada bola de fuego (clic derecho) llena un segmento; con los 3 llenos, R lanza la ráfaga grande.
 */
public final class DragonHud {
    private static final int SEG_W = 18;
    private static final int SEG_H = 5;
    private static final int GAP = 3;

    public static void render(GuiGraphics g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.options.hideGui || mc.player == null || !(mc.player.getVehicle() instanceof NetherDragonEntity dragon)
                || !dragon.isAdult() || !dragon.isSaddled()) {
            return;
        }
        int charge = dragon.getCharge();
        int max = NetherDragonEntity.MAX_CHARGE;
        boolean full = charge >= max;
        int total = max * SEG_W + (max - 1) * GAP;
        int x0 = g.guiWidth() / 2 - total / 2;
        int y0 = g.guiHeight() / 2 + 14;
        float pulse = (Mth.sin((mc.player.tickCount + delta.getGameTimeDeltaPartialTick(false)) * 0.35f) + 1.0f) * 0.5f;
        int fullColor = 0xFF000000 | lerpColor(0x2FC8FF, 0xC8F4FF, pulse);
        for (int i = 0; i < max; i++) {
            int x = x0 + i * (SEG_W + GAP);
            g.fill(x - 1, y0 - 1, x + SEG_W + 1, y0 + SEG_H + 1, 0xC0000000);
            g.fill(x, y0, x + SEG_W, y0 + SEG_H, 0xFF3A1414);
            if (i < charge) {
                g.fill(x, y0, x + SEG_W, y0 + SEG_H, full ? fullColor : 0xFFFF6A1A);
                g.fill(x, y0, x + SEG_W, y0 + 1, full ? 0xFFFFFFFF : 0xFFFFC060);
            }
        }
        Component label = full
                ? Component.translatable("hud.civilizacion_nether.burst_ready", ClientEvents.BREATH_KEY.getTranslatedKeyMessage())
                : Component.translatable("hud.civilizacion_nether.charge", charge, max);
        g.drawCenteredString(mc.font, label, g.guiWidth() / 2, y0 + SEG_H + 4, full ? fullColor : 0xFFFFB070);
    }

    private static int lerpColor(int a, int b, float t) {
        int r = (int) Mth.lerp(t, (a >> 16) & 255, (b >> 16) & 255);
        int gg = (int) Mth.lerp(t, (a >> 8) & 255, (b >> 8) & 255);
        int bb = (int) Mth.lerp(t, a & 255, b & 255);
        return (r << 16) | (gg << 8) | bb;
    }

    private DragonHud() {
    }
}
