package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.renderer.texture.AbstractTexture;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import org.lwjgl.glfw.GLFW;

import java.io.Reader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * El Manual: las mismas páginas del libro del mod, de a dos como un libro abierto.
 * Flechas del teclado, rueda del mouse o los botones para pasar; la página 2 es el índice y se le puede hacer clic.
 * Recuerda la última página leída mientras el juego esté abierto.
 */
public class ManualScreen extends Screen {
    private static final int TEX_W = 700;
    private static final int TEX_H = 965;
    private static final int INDEX_PAGE = 2;
    private static int pages = 130;
    private static List<Entry> index;
    private static int lastSpread;
    private static final Set<ResourceLocation> FILTERED = new HashSet<>();

    private record Entry(int page, String label, boolean chapter) {
    }

    private int spread;
    private int pw;
    private int ph;
    private int x0;
    private int y0;
    private double indexScroll;
    private Button prev;
    private Button next;

    public ManualScreen() {
        super(Component.translatable("item.civilizacion_nether.manual"));
        this.spread = lastSpread;
    }

    private static void loadIndex() {
        if (index != null) {
            return;
        }
        index = new ArrayList<>();
        Minecraft.getInstance().getResourceManager().getResource(CivilizacionNether.id("manual_index.json")).ifPresent(res -> {
            try (Reader reader = res.openAsReader()) {
                JsonObject root = JsonParser.parseReader(reader).getAsJsonObject();
                pages = root.get("pages").getAsInt();
                for (JsonElement e : root.getAsJsonArray("index")) {
                    JsonObject o = e.getAsJsonObject();
                    index.add(new Entry(o.get("page").getAsInt(), o.get("label").getAsString(), o.get("chapter").getAsBoolean()));
                }
            } catch (Exception ignored) {
                // sin índice el manual igual se lee página por página
            }
        });
    }

    private static int spreads() {
        return 1 + (pages - 1 + 1) / 2;
    }

    private static int spreadOf(int page) {
        return page <= 0 ? 0 : (page + 1) / 2;
    }

    private static ResourceLocation tex(int page) {
        return CivilizacionNether.id(String.format("textures/gui/manual/page_%03d.png", page));
    }

    @Override
    protected void init() {
        loadIndex();
        ph = Math.min(height - 40, (int) ((width - 20) / 2.0 * TEX_H / TEX_W));
        pw = ph * TEX_W / TEX_H;
        x0 = width / 2 - pw;
        y0 = 6;
        int by = y0 + ph + 6;
        prev = addRenderableWidget(Button.builder(Component.translatable("gui.civilizacion_nether.manual.prev"), b -> turn(-1))
                .bounds(width / 2 - pw, by, 80, 20).build());
        next = addRenderableWidget(Button.builder(Component.translatable("gui.civilizacion_nether.manual.next"), b -> turn(1))
                .bounds(width / 2 + pw - 80, by, 80, 20).build());
        addRenderableWidget(Button.builder(Component.translatable("gui.civilizacion_nether.manual.index"), b -> go(spreadOf(INDEX_PAGE)))
                .bounds(width / 2 - 84, by, 80, 20).build());
        addRenderableWidget(Button.builder(Component.translatable("gui.civilizacion_nether.manual.close"), b -> onClose())
                .bounds(width / 2 + 4, by, 80, 20).build());
        updateButtons();
    }

    private void updateButtons() {
        if (prev != null) {
            prev.active = spread > 0;
            next.active = spread < spreads() - 1;
        }
    }

    private void go(int s) {
        s = Math.max(0, Math.min(spreads() - 1, s));
        if (s != spread) {
            spread = s;
            lastSpread = s;
            indexScroll = 0;
            Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1.0f));
            updateButtons();
        }
    }

    private void turn(int d) {
        go(spread + d);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        if (spread == 0) {
            drawPage(g, 0, width / 2 - pw / 2);
        } else {
            int left = spread * 2 - 1;
            int right = left + 1;
            drawPage(g, left, x0);
            if (right < pages) {
                drawPage(g, right, x0 + pw);
            }
            if (left == INDEX_PAGE) {
                drawIndex(g, x0, mouseX, mouseY);
            } else if (right == INDEX_PAGE) {
                drawIndex(g, x0 + pw, mouseX, mouseY);
            }
        }
    }

    private void drawPage(GuiGraphics g, int page, int x) {
        ResourceLocation rl = tex(page);
        if (FILTERED.add(rl)) {
            AbstractTexture t = Minecraft.getInstance().getTextureManager().getTexture(rl);
            t.setFilter(true, false);   // letras suaves al achicar la página
        }
        g.blit(rl, x, y0, pw, ph, 0.0f, 0.0f, TEX_W, TEX_H, TEX_W, TEX_H);
    }

    // ------------------------------------------------------------------ índice (página 2)
    private int listTop() {
        return y0 + (int) (ph * 0.10);
    }

    private int listBottom() {
        return y0 + (int) (ph * 0.93);
    }

    private static final int LINE = 11;

    private void drawIndex(GuiGraphics g, int x, int mouseX, int mouseY) {
        int top = listTop();
        int bottom = listBottom();
        int left = x + (int) (pw * 0.06);
        int rightEdge = x + pw - (int) (pw * 0.06);
        g.enableScissor(x, top, x + pw, bottom);
        int y = top - (int) indexScroll;
        for (Entry e : index) {
            if (y + LINE >= top && y <= bottom) {
                boolean hover = mouseX >= left && mouseX <= rightEdge && mouseY >= y && mouseY < y + LINE && mouseY >= top && mouseY < bottom;
                int color = e.chapter() ? 0xFFE0B040 : (hover ? 0xFFFFFFFF : 0xFFCFC6BE);
                if (hover) {
                    g.fill(left - 2, y - 1, rightEdge + 2, y + LINE - 1, 0x40FF4060);
                }
                int indent = e.chapter() ? 0 : 8;
                String num = String.valueOf(e.page());
                String label = font.plainSubstrByWidth(e.label(), rightEdge - left - indent - font.width(num) - 8);
                g.drawString(font, label, left + indent, y + 1, color, false);
                g.drawString(font, num, rightEdge - font.width(num), y + 1, 0xFFB08040, false);
            }
            y += LINE;
        }
        g.disableScissor();
    }

    private boolean overIndex(double mx, double my) {
        int left = spread * 2 - 1;
        int x;
        if (left == INDEX_PAGE) {
            x = x0;
        } else if (left + 1 == INDEX_PAGE) {
            x = x0 + pw;
        } else {
            return false;
        }
        return spread > 0 && mx >= x && mx < x + pw && my >= listTop() && my < listBottom();
    }

    private int indexPageX() {
        return (spread * 2 - 1 == INDEX_PAGE) ? x0 : x0 + pw;
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (button == 0 && overIndex(mouseX, mouseY)) {
            int row = (int) ((mouseY - listTop() + indexScroll) / LINE);
            if (row >= 0 && row < index.size()) {
                go(spreadOf(index.get(row).page()));
                return true;
            }
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double scrollX, double scrollY) {
        if (overIndex(mouseX, mouseY)) {
            int max = Math.max(0, index.size() * LINE - (listBottom() - listTop()));
            indexScroll = Math.max(0, Math.min(max, indexScroll - scrollY * LINE * 2));
            return true;
        }
        turn(scrollY < 0 ? 1 : -1);
        return true;
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode == GLFW.GLFW_KEY_RIGHT || keyCode == GLFW.GLFW_KEY_PAGE_DOWN || keyCode == GLFW.GLFW_KEY_D) {
            turn(1);
            return true;
        }
        if (keyCode == GLFW.GLFW_KEY_LEFT || keyCode == GLFW.GLFW_KEY_PAGE_UP || keyCode == GLFW.GLFW_KEY_A) {
            turn(-1);
            return true;
        }
        if (keyCode == GLFW.GLFW_KEY_HOME) {
            go(0);
            return true;
        }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }

    @Override
    public void onClose() {
        lastSpread = spread;
        super.onClose();
    }
}
