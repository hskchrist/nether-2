package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.DragonFireballEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;

/** Bola de fuego negro: un sprite que siempre mira a la cámara, gira y brilla (igual que la del Ender Dragon). */
public class DragonFireballRenderer extends EntityRenderer<DragonFireballEntity> {
    private static final ResourceLocation TEXTURE = CivilizacionNether.id("textures/entity/black_fireball.png");
    private static final RenderType RENDER_TYPE = RenderType.entityCutoutNoCull(TEXTURE);
    private static final int FULL_BRIGHT = 0xF000F0;

    public DragonFireballRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public void render(DragonFireballEntity entity, float entityYaw, float partialTick, PoseStack poseStack,
                       MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();
        poseStack.scale(1.6f, 1.6f, 1.6f);
        poseStack.mulPose(this.entityRenderDispatcher.cameraOrientation());
        poseStack.mulPose(Axis.ZP.rotationDegrees((entity.tickCount + partialTick) * 25.0f));
        PoseStack.Pose pose = poseStack.last();
        VertexConsumer consumer = buffer.getBuffer(RENDER_TYPE);
        vertex(consumer, pose, 0.0f, 0, 0, 1);
        vertex(consumer, pose, 1.0f, 0, 1, 1);
        vertex(consumer, pose, 1.0f, 1, 1, 0);
        vertex(consumer, pose, 0.0f, 1, 0, 0);
        poseStack.popPose();
        super.render(entity, entityYaw, partialTick, poseStack, buffer, packedLight);
    }

    private static void vertex(VertexConsumer consumer, PoseStack.Pose pose, float x, int y, int u, int v) {
        consumer.addVertex(pose, x - 0.5f, y - 0.5f, 0.0f)
                .setColor(-1)
                .setUv(u, v)
                .setOverlay(OverlayTexture.NO_OVERLAY)
                .setLight(FULL_BRIGHT)
                .setNormal(pose, 0.0f, 1.0f, 0.0f);
    }

    @Override
    public ResourceLocation getTextureLocation(DragonFireballEntity entity) {
        return TEXTURE;
    }
}
