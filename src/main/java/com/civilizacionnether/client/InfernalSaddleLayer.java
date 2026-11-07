package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.InfernalDragonEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

/**
 * Silla del Dragón Infernal: cuando está ensillado se vuelve a dibujar el modelo con la textura de la silla
 * (transparente salvo la silla), mostrando sólo entonces el hueso "saddle". La textura del dragón no se toca.
 */
public class InfernalSaddleLayer extends GeoRenderLayer<InfernalDragonEntity> {
    private static final ResourceLocation TEXTURE = CivilizacionNether.id("textures/entity/dragon_infernal_saddle.png");

    public InfernalSaddleLayer(GeoRenderer<InfernalDragonEntity> renderer) {
        super(renderer);
    }

    @Override
    public void render(PoseStack poseStack, InfernalDragonEntity animatable, BakedGeoModel bakedModel, @Nullable RenderType renderType,
                       MultiBufferSource bufferSource, @Nullable VertexConsumer buffer, float partialTick, int packedLight, int packedOverlay) {
        if (!animatable.isSaddled() || animatable.isInvisible()) {
            return;
        }
        GeoBone saddle = getGeoModel().getAnimationProcessor().getBone("saddle");
        if (saddle == null) {
            return;
        }
        RenderType type = RenderType.entityCutoutNoCull(TEXTURE);
        saddle.setHidden(false);
        getRenderer().reRender(bakedModel, poseStack, bufferSource, animatable, type, bufferSource.getBuffer(type), partialTick,
                packedLight, packedOverlay, -1);
        saddle.setHidden(true);
    }
}
