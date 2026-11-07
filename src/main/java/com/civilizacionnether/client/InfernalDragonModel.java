package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.DragonStages;
import com.civilizacionnether.entity.InfernalDragonEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.model.GeoModel;

/**
 * Modelo del Dragón Infernal (el del usuario). Igual que el Dragón del Nether, cada fase cambia las proporciones:
 * las crías tienen cabeza grande y alas, cuello, cola y patas cortos.
 */
public class InfernalDragonModel extends GeoModel<InfernalDragonEntity> {
    private static final ResourceLocation MODEL = CivilizacionNether.id("geo/entity/dragon_infernal.geo.json");
    private static final ResourceLocation TEXTURE = CivilizacionNether.id("textures/entity/dragon_infernal.png");
    /** Skin del Dragón Infernal domesticable (la puede pintar distinta el usuario). */
    private static final ResourceLocation TAME_TEXTURE = CivilizacionNether.id("textures/entity/dragon_infernal_domesticable.png");
    private static final ResourceLocation ALMAS_TEXTURE = CivilizacionNether.id("textures/entity/dragon_almas.png");
    private static final ResourceLocation OBSIDIANA_TEXTURE = CivilizacionNether.id("textures/entity/dragon_obsidiana.png");
    private static final ResourceLocation ANIMATIONS = CivilizacionNether.id("animations/entity/dragon_infernal.animation.json");
    private static final String[] WINGS = {"wing", "wing1"};
    private static final String[] LEGS = {"frontleg", "frontleg1", "rearleg", "rearleg1"};
    /** Cuánto levantan el cuerpo las patas en el suelo (en píxeles del modelo). */
    private static final float LEG_LIFT = 46.0f;

    @Override
    public ResourceLocation getModelResource(InfernalDragonEntity animatable) {
        return MODEL;
    }

    @Override
    public ResourceLocation getTextureResource(InfernalDragonEntity animatable) {
        return switch (animatable.species()) {
            case ALMAS -> ALMAS_TEXTURE;
            case OBSIDIANA -> OBSIDIANA_TEXTURE;
            default -> animatable.isTameVariant() ? TAME_TEXTURE : TEXTURE;
        };
    }

    @Override
    public ResourceLocation getAnimationResource(InfernalDragonEntity animatable) {
        return ANIMATIONS;
    }

    @Override
    public void setCustomAnimations(InfernalDragonEntity animatable, long instanceId, AnimationState<InfernalDragonEntity> animationState) {
        super.setCustomAnimations(animatable, instanceId, animationState);
        float g = animatable.getGrowth();
        scale("head", DragonStages.lerp(DragonStages.HEAD, g));
        scale("neck", DragonStages.lerp(DragonStages.NECK, g));
        scale("tail", DragonStages.lerp(DragonStages.TAIL, g));
        float wings = DragonStages.lerp(DragonStages.WINGS, g);
        for (String w : WINGS) {
            scale(w, wings);
        }
        float legs = DragonStages.lerp(DragonStages.LEGS, g);
        for (String l : LEGS) {
            scale(l, legs);
        }
        // la silla se dibuja aparte, con su propia textura (InfernalSaddleLayer); la púa bajo el asiento se esconde
        GeoBone saddle = getAnimationProcessor().getBone("saddle");
        if (saddle != null) {
            saddle.setHidden(true);
        }
        GeoBone spike = getAnimationProcessor().getBone("spike_saddle");
        if (spike != null) {
            spike.setHidden(animatable.isSaddled());
        }
    }

    /** Cuánto se baja el cuerpo de las crías en tierra (patas más cortas), en píxeles del modelo (InfernalDragonRenderer). */
    public static float legDrop(InfernalDragonEntity d) {
        float legs = DragonStages.lerp(DragonStages.LEGS, d.getGrowth());
        return legs < 0.999f && !d.isFlying() && !d.isResting() ? LEG_LIFT * (1.0f - legs) : 0.0f;
    }

    private void scale(String name, float s) {
        GeoBone bone = getAnimationProcessor().getBone(name);
        if (bone != null) {
            bone.setScaleX(s);
            bone.setScaleY(s);
            bone.setScaleZ(s);
        }
    }
}
