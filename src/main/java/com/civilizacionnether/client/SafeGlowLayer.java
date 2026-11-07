package com.civilizacionnether.client;

import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.Resource;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoAnimatable;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

import java.io.InputStream;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Brillo en la oscuridad (texturas _glowmask) que no cierra el juego: GeckoLib se cae si la máscara existe pero está
 * vacía, así que sólo se dibuja cuando la máscara existe y tiene al menos un píxel.
 */
public class SafeGlowLayer<T extends GeoAnimatable> extends AutoGlowingGeoLayer<T> {
    private static final Map<ResourceLocation, Boolean> USABLE = new ConcurrentHashMap<>();

    public SafeGlowLayer(GeoRenderer<T> renderer) {
        super(renderer);
    }

    @Nullable
    @Override
    protected RenderType getRenderType(T animatable) {
        ResourceLocation tex = getTextureResource(animatable);
        if (tex == null || !USABLE.computeIfAbsent(tex, SafeGlowLayer::hasGlow)) {
            return null;
        }
        return super.getRenderType(animatable);
    }

    private static boolean hasGlow(ResourceLocation texture) {
        String path = texture.getPath();
        if (!path.endsWith(".png")) {
            return false;
        }
        ResourceLocation mask = ResourceLocation.fromNamespaceAndPath(texture.getNamespace(),
                path.substring(0, path.length() - 4) + "_glowmask.png");
        Optional<Resource> res = Minecraft.getInstance().getResourceManager().getResource(mask);
        if (res.isEmpty()) {
            return false;
        }
        try (InputStream in = res.get().open(); NativeImage img = NativeImage.read(in)) {
            for (int y = 0; y < img.getHeight(); y++) {
                for (int x = 0; x < img.getWidth(); x++) {
                    if ((img.getPixelRGBA(x, y) >>> 24) != 0) {
                        return true;
                    }
                }
            }
        } catch (Exception ignored) {
            // máscara rota: sin brillo
        }
        return false;
    }

    /** Al recargar los recursos (F3+T) se vuelve a revisar. */
    public static void clearCache() {
        USABLE.clear();
    }
}
