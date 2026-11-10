package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.NetherHorseEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/**
 * Caballo del Nether: el modelo y la skin del usuario tal cual (un 15 % más grande). La silla, la brida y las riendas
 * se ven sólo si está ensillado (las riendas, además, cuando alguien lo monta). Las bolsas y las orejas de mula del
 * modelo no se usan.
 */
public class NetherHorseRenderer extends GeoEntityRenderer<NetherHorseEntity> {
    public NetherHorseRenderer(EntityRendererProvider.Context context) {
        super(context, new Model());
        withScale(1.15f);
        this.shadowRadius = 0.85f;
    }

    static class Model extends GeoModel<NetherHorseEntity> {
        private static final ResourceLocation GEO = CivilizacionNether.id("geo/entity/caballo_nether.geo.json");
        private static final ResourceLocation TEX = CivilizacionNether.id("textures/entity/caballo_nether.png");
        private static final ResourceLocation ANIM = CivilizacionNether.id("animations/entity/caballo_nether.animation.json");

        @Override
        public ResourceLocation getModelResource(NetherHorseEntity animatable) {
            return GEO;
        }

        @Override
        public ResourceLocation getTextureResource(NetherHorseEntity animatable) {
            return TEX;
        }

        @Override
        public ResourceLocation getAnimationResource(NetherHorseEntity animatable) {
            return ANIM;
        }

        @Override
        public void setCustomAnimations(NetherHorseEntity horse, long instanceId, AnimationState<NetherHorseEntity> state) {
            super.setCustomAnimations(horse, instanceId, state);
            boolean saddled = horse.isSaddled();
            hide("saddle", !saddled);
            hide("bridle", !saddled);
            hide("reins", !(saddled && horse.isVehicle()));
            hide("bags", true);
            hide("mule_ears", true);
        }

        private void hide(String bone, boolean hidden) {
            GeoBone b = getAnimationProcessor().getBone(bone);
            if (b != null) {
                b.setHidden(hidden);
            }
        }
    }
}
