package com.civilizacionnether.client;

import com.civilizacionnether.entity.InfernalDragonEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/** Dragón Infernal: el adulto mide ~10 bloques de largo y ~10 de envergadura. Las grietas de magma brillan. */
public class InfernalDragonRenderer extends GeoEntityRenderer<InfernalDragonEntity> {
    public static final float ADULT_SCALE = 0.65f;

    public InfernalDragonRenderer(EntityRendererProvider.Context context) {
        super(context, new InfernalDragonModel());
        withScale(ADULT_SCALE);
        this.shadowRadius = 1.8f;
        addRenderLayer(new SafeGlowLayer<>(this));
        addRenderLayer(new InfernalSaddleLayer(this));
    }

    @Override
    public void render(InfernalDragonEntity entity, float entityYaw, float partialTick, PoseStack poseStack,
                       MultiBufferSource bufferSource, int packedLight) {
        this.shadowRadius = 1.8f * entity.getScale();
        super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
    }

    @Override
    protected void applyRotations(InfernalDragonEntity entity, PoseStack poseStack, float ageInTicks, float rotationYaw, float partialTick,
                                  float nativeScale) {
        super.applyRotations(entity, poseStack, ageInTicks, rotationYaw, partialTick, nativeScale);
        float drop = InfernalDragonModel.legDrop(entity);
        if (drop > 0.0f) {
            poseStack.translate(0.0f, -drop / 16.0f, 0.0f);
        }
    }
}
