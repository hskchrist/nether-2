package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.item.SkinArmorItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoArmorRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/** Dibuja la armadura con forma de skin (humana o del Frío Eterno); la del Frío Eterno brilla. */
public class SkinArmorRenderer extends GeoArmorRenderer<SkinArmorItem> {
    private static final ResourceLocation MODEL = CivilizacionNether.id("geo/armor/skin_armor.geo.json");
    private static final ResourceLocation ANIMATIONS = CivilizacionNether.id("animations/armor/skin_armor.animation.json");

    public SkinArmorRenderer(boolean glowing) {
        super(new GeoModel<>() {
            @Override
            public ResourceLocation getModelResource(SkinArmorItem animatable) {
                return MODEL;
            }

            @Override
            public ResourceLocation getTextureResource(SkinArmorItem animatable) {
                return CivilizacionNether.id("textures/armor/" + animatable.getArmorTexture() + ".png");
            }

            @Override
            public ResourceLocation getAnimationResource(SkinArmorItem animatable) {
                return ANIMATIONS;
            }
        });
        if (glowing) {
            addRenderLayer(new SafeGlowLayer<>(this));
        }
    }
}
