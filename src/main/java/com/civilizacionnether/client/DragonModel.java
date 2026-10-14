package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.DragonStages;
import com.civilizacionnether.entity.NetherDragonEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.model.GeoModel;

/**
 * Modelo del Dragón del Nether. Además de la escala general (atributo de escala según la fase),
 * cada fase cambia las proporciones: las crías tienen cabeza grande, alitas, cuello, cola y patas cortos.
 * La silla aparece si la tiene (y entonces se ocultan las espinas del lomo).
 */
public class DragonModel extends GeoModel<NetherDragonEntity> {
    private static final ResourceLocation MODEL = CivilizacionNether.id("geo/entity/nether_dragon.geo.json");
    private static final ResourceLocation TEXTURE = CivilizacionNether.id("textures/entity/nether_dragon.png");
    private static final ResourceLocation ANIMATIONS = CivilizacionNether.id("animations/entity/nether_dragon.animation.json");
    private static final String[] WING_ROOTS = {"bone70", "bone71"};
    private static final String[] LEG_ROOTS = {"bone13", "bone18", "bone12", "bone20"};
    /** Altura (en píxeles del modelo) que baja el cuerpo cuando las patas son más cortas. */
    private static final float LEG_DROP = 58.0f;

    @Override
    public ResourceLocation getModelResource(NetherDragonEntity animatable) {
        return MODEL;
    }

    @Override
    public ResourceLocation getTextureResource(NetherDragonEntity animatable) {
        return TEXTURE;
    }

    @Override
    public ResourceLocation getAnimationResource(NetherDragonEntity animatable) {
        return ANIMATIONS;
    }

    @Override
    public void setCustomAnimations(NetherDragonEntity animatable, long instanceId, AnimationState<NetherDragonEntity> animationState) {
        super.setCustomAnimations(animatable, instanceId, animationState);
        float g = animatable.getGrowth();
        scale("head", DragonStages.lerp(DragonStages.HEAD, g));
        scale("neck", DragonStages.lerp(DragonStages.NECK, g));
        scale("bone24", DragonStages.lerp(DragonStages.TAIL, g));
        float wings = DragonStages.lerp(DragonStages.WINGS, g);
        for (String w : WING_ROOTS) {
            scale(w, wings);
        }
        float legs = DragonStages.lerp(DragonStages.LEGS, g);
        for (String l : LEG_ROOTS) {
            scale(l, legs);
        }
        GeoBone root = getAnimationProcessor().getBone("root");
        if (root != null && legs < 0.999f) {
            root.setPosY(root.getPosY() - LEG_DROP * (1.0f - legs));
        }
        hide("saddle", !animatable.isSaddled());
        hide("spikes_b2", animatable.isSaddled());
        hide("ray", true);
    }

    private void scale(String name, float s) {
        GeoBone bone = getAnimationProcessor().getBone(name);
        if (bone != null) {
            bone.setScaleX(s);
            bone.setScaleY(s);
            bone.setScaleZ(s);
        }
    }

    private void hide(String name, boolean hidden) {
        GeoBone bone = getAnimationProcessor().getBone(name);
        if (bone != null) {
            bone.setHidden(hidden);
        }
    }
}
