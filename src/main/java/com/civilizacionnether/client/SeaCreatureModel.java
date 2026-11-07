package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import software.bernie.geckolib.animatable.GeoAnimatable;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;

/**
 * Modelo de las criaturas del mar (geo/entity, textures/entity y animations/entity con el mismo nombre).
 * Las que nadan en 3D inclinan el cuerpo al subir y bajar.
 */
public class SeaCreatureModel<T extends LivingEntity & GeoAnimatable> extends DefaultedEntityGeoModel<T> {
    private final boolean pitch;

    public SeaCreatureModel(String name, boolean pitch) {
        super(CivilizacionNether.id(name));
        this.pitch = pitch;
    }

    @Override
    public void setCustomAnimations(T animatable, long instanceId, AnimationState<T> animationState) {
        super.setCustomAnimations(animatable, instanceId, animationState);
        if (!pitch) {
            return;
        }
        GeoBone root = getAnimationProcessor().getBone("root");
        if (root != null) {
            float xRot = Mth.lerp(animationState.getPartialTick(), animatable.xRotO, animatable.getXRot());
            root.setRotX(root.getRotX() - xRot * Mth.DEG_TO_RAD);
        }
    }
}
