package com.civilizacionnether.client;

import com.civilizacionnether.entity.HumanoidType;
import com.civilizacionnether.entity.NetherHumanoidEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;
import software.bernie.geckolib.renderer.layer.BlockAndItemGeoLayer;

/**
 * Se escala cada clase para quedar a la altura del Wither Skeleton (el Rey un poco más alto).
 * Ojos, almas y el orbe de rubí brillan en la oscuridad (texturas _glowmask).
 */
public class HumanoidRenderer extends GeoEntityRenderer<NetherHumanoidEntity> {
    public HumanoidRenderer(EntityRendererProvider.Context context, HumanoidType type) {
        super(context, new HumanoidModel());
        withScale(type.renderScale);
        this.shadowRadius = type.width * 0.7f;
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
        addRenderLayer(new HeldItemLayer(this));
    }

    @Override
    public void render(NetherHumanoidEntity entity, float entityYaw, float partialTick, PoseStack poseStack,
                       MultiBufferSource bufferSource, int packedLight) {
        if (entity.isBaby()) {
            poseStack.pushPose();
            poseStack.scale(0.5f, 0.5f, 0.5f);
            super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
            poseStack.popPose();
        } else {
            super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
        }
    }

    private static class HeldItemLayer extends BlockAndItemGeoLayer<NetherHumanoidEntity> {
        HeldItemLayer(GeoRenderer<NetherHumanoidEntity> renderer) {
            super(renderer);
        }

        @Nullable
        @Override
        protected ItemStack getStackForBone(GeoBone bone, NetherHumanoidEntity animatable) {
            return switch (bone.getName()) {
                case "right_hand_item" -> animatable.getMainHandItem();
                case "left_hand_item" -> animatable.getOffhandItem();
                default -> null;
            };
        }

        @Override
        protected ItemDisplayContext getTransformTypeForStack(GeoBone bone, ItemStack stack, NetherHumanoidEntity animatable) {
            return bone.getName().equals("left_hand_item")
                    ? ItemDisplayContext.THIRD_PERSON_LEFT_HAND : ItemDisplayContext.THIRD_PERSON_RIGHT_HAND;
        }

        @Override
        protected void renderStackForBone(PoseStack poseStack, GeoBone bone, ItemStack stack, NetherHumanoidEntity animatable,
                                          MultiBufferSource bufferSource, float partialTick, int packedLight, int packedOverlay) {
            // Igual que Minecraft (ItemInHandLayer): el arco queda con la curva hacia el blanco y la cuerda hacia el arquero
            poseStack.mulPose(Axis.XP.rotationDegrees(-90f));
            poseStack.mulPose(Axis.YP.rotationDegrees(180f));
            super.renderStackForBone(poseStack, bone, stack, animatable, bufferSource, partialTick, packedLight, packedOverlay);
        }
    }
}
