package com.civilizacionnether.client;

import com.civilizacionnether.entity.NetherDragonEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/**
 * El modelo original mide ~25 bloques de largo (con la cola); el adulto se dibuja a la mitad (~12 bloques).
 * GeckoLib además aplica el atributo de escala de la fase de crecimiento.
 */
public class DragonRenderer extends GeoEntityRenderer<NetherDragonEntity> {
    public static final float ADULT_SCALE = 0.5f;

    public DragonRenderer(EntityRendererProvider.Context context) {
        super(context, new DragonModel());
        withScale(ADULT_SCALE);
        this.shadowRadius = 1.8f;
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }

    @Override
    public void render(NetherDragonEntity entity, float entityYaw, float partialTick, PoseStack poseStack,
                       MultiBufferSource bufferSource, int packedLight) {
        this.shadowRadius = 1.8f * entity.getScale();
        super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
    }
}
