package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.NetherHumanoidEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.model.data.EntityModelData;

/** Cada clase usa su propio modelo, textura y animaciones; la cabeza sigue la mirada. */
public class HumanoidModel extends GeoModel<NetherHumanoidEntity> {

    @Override
    public ResourceLocation getModelResource(NetherHumanoidEntity animatable) {
        return CivilizacionNether.id("geo/entity/" + animatable.getHumanoidType().model + ".geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(NetherHumanoidEntity animatable) {
        return CivilizacionNether.id("textures/entity/" + animatable.getHumanoidType().texture + ".png");
    }

    @Override
    public ResourceLocation getAnimationResource(NetherHumanoidEntity animatable) {
        return CivilizacionNether.id("animations/entity/" + animatable.getHumanoidType().model + ".animation.json");
    }

    @Override
    public void setCustomAnimations(NetherHumanoidEntity animatable, long instanceId, AnimationState<NetherHumanoidEntity> animationState) {
        super.setCustomAnimations(animatable, instanceId, animationState);
        GeoBone head = getAnimationProcessor().getBone("head");
        EntityModelData data = animationState.getData(DataTickets.ENTITY_MODEL_DATA);
        if (head != null && data != null) {
            head.setRotX(data.headPitch() * Mth.DEG_TO_RAD);
            head.setRotY(data.netHeadYaw() * Mth.DEG_TO_RAD);
        }
    }
}
