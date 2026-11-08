package com.civilizacionnether.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.util.Mth;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoAnimatable;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/** Dibuja las criaturas del Mar del Nether: brillo de su textura _glowmask, crías a la mitad y la medusa transparente. */
public class SeaCreatureRenderer<T extends LivingEntity & GeoAnimatable> extends GeoEntityRenderer<T> {
    private final boolean translucent;
    private final float shadow;

    public SeaCreatureRenderer(EntityRendererProvider.Context context, String name, float scale, float shadow,
                               boolean pitch, boolean glow, boolean translucent) {
        super(context, new SeaCreatureModel<>(name, pitch));
        withScale(scale);
        this.shadow = shadow;
        this.shadowRadius = shadow;
        this.translucent = translucent;
        if (glow) {
            addRenderLayer(new SafeGlowLayer<>(this));
        }
    }

    @Override
    public void render(T entity, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource bufferSource, int packedLight) {
        boolean baby = entity.isBaby();
        this.shadowRadius = baby ? shadow * 0.5f : shadow;
        if (baby) {
            poseStack.pushPose();
            poseStack.scale(0.5f, 0.5f, 0.5f);
        }
        super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
        if (baby) {
            poseStack.popPose();
        }
    }

    /** Inclina todo el cuerpo según hacia dónde nada (arriba/abajo), girando desde el centro de la criatura. */
    @Override
    protected void applyRotations(T entity, PoseStack poseStack, float ageInTicks, float rotationYaw, float partialTick, float nativeScale) {
        super.applyRotations(entity, poseStack, ageInTicks, rotationYaw, partialTick, nativeScale);
        if (getGeoModel() instanceof SeaCreatureModel<?> m && m.pitches() && entity.isAlive() && entity.isInWater()) {
            float xRot = Mth.wrapDegrees(Mth.rotLerp(partialTick, entity.xRotO, entity.getXRot()));
            xRot = Mth.clamp(xRot, -80.0f, 80.0f);
            float h = entity.getBbHeight() * 0.5f;
            poseStack.translate(0.0f, h, 0.0f);
            poseStack.mulPose(Axis.XP.rotationDegrees(-xRot));
            poseStack.translate(0.0f, -h, 0.0f);
        }
    }

    @Override
    public RenderType getRenderType(T animatable, ResourceLocation texture, @Nullable MultiBufferSource bufferSource, float partialTick) {
        if (translucent) {
            return RenderType.entityTranslucent(texture);
        }
        return super.getRenderType(animatable, texture, bufferSource, partialTick);
    }
}
