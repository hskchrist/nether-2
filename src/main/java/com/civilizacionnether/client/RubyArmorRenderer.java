package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.item.RubyArmorItem;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoArmorRenderer;

/** Dibuja la armadura de rubí 3D sobre el jugador (huesos armorHead, armorBody, armorRightArm, etc.). */
public class RubyArmorRenderer extends GeoArmorRenderer<RubyArmorItem> {
    private static final ResourceLocation MODEL = CivilizacionNether.id("geo/armor/ruby_armor.geo.json");
    private static final ResourceLocation TEXTURE = CivilizacionNether.id("textures/armor/ruby_armor.png");
    private static final ResourceLocation ANIMATIONS = CivilizacionNether.id("animations/armor/ruby_armor.animation.json");

    public RubyArmorRenderer() {
        super(new GeoModel<>() {
            @Override
            public ResourceLocation getModelResource(RubyArmorItem animatable) {
                return MODEL;
            }

            @Override
            public ResourceLocation getTextureResource(RubyArmorItem animatable) {
                return TEXTURE;
            }

            @Override
            public ResourceLocation getAnimationResource(RubyArmorItem animatable) {
                return ANIMATIONS;
            }
        });
    }
}
