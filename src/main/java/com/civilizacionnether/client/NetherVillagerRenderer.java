package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.NetherVillagers;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.VillagerModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.VillagerRenderer;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.entity.layers.VillagerProfessionLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.npc.Villager;
import org.jetbrains.annotations.Nullable;

/**
 * Aldeanos: los del Nether (y los de las 5 profesiones nuevas) se dibujan con su skin completa (hecha a partir del
 * Aldeano Necromancer) y con los ojos que brillan; el resto de los aldeanos se ve exactamente igual que en vanilla.
 */
public class NetherVillagerRenderer extends VillagerRenderer {

    public NetherVillagerRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
        for (int i = 0; i < layers.size(); i++) {
            RenderLayer<Villager, VillagerModel<Villager>> layer = layers.get(i);
            if (layer instanceof VillagerProfessionLayer<?, ?>) {
                layers.set(i, new VanillaOnlyLayer(this, layer));
            }
        }
        addLayer(new GlowingEyesLayer(this));
    }

    @Nullable
    private static String skin(Villager v) {
        return NetherVillagers.skinName(v.getVillagerData());
    }

    private static ResourceLocation tex(String name) {
        return CivilizacionNether.id("textures/entity/villager/nether/" + name + ".png");
    }

    @Override
    public ResourceLocation getTextureLocation(Villager v) {
        String s = skin(v);
        return s != null ? tex(s) : super.getTextureLocation(v);
    }

    @Override
    public void render(Villager v, float yaw, float partialTicks, PoseStack poseStack, MultiBufferSource buffer, int light) {
        if (skin(v) != null) {
            // las capuchas de algunas skins van en la capa del sombrero
            getModel().hatVisible(true);
        }
        super.render(v, yaw, partialTicks, poseStack, buffer, light);
    }

    /** La ropa vanilla de profesión sólo para los aldeanos que no son del Nether (los del Nether ya la traen en la skin). */
    private static final class VanillaOnlyLayer extends RenderLayer<Villager, VillagerModel<Villager>> {
        private final RenderLayer<Villager, VillagerModel<Villager>> inner;

        VanillaOnlyLayer(RenderLayerParent<Villager, VillagerModel<Villager>> parent, RenderLayer<Villager, VillagerModel<Villager>> inner) {
            super(parent);
            this.inner = inner;
        }

        @Override
        public void render(PoseStack poseStack, MultiBufferSource buffer, int light, Villager v, float limbSwing, float limbSwingAmount,
                           float partialTick, float ageInTicks, float netHeadYaw, float headPitch) {
            if (skin(v) == null) {
                inner.render(poseStack, buffer, light, v, limbSwing, limbSwingAmount, partialTick, ageInTicks, netHeadYaw, headPitch);
            }
        }
    }

    /** Ojos rojos o morados que brillan en la oscuridad (como el Aldeano Necromancer). */
    private static final class GlowingEyesLayer extends RenderLayer<Villager, VillagerModel<Villager>> {
        GlowingEyesLayer(RenderLayerParent<Villager, VillagerModel<Villager>> parent) {
            super(parent);
        }

        @Override
        public void render(PoseStack poseStack, MultiBufferSource buffer, int light, Villager v, float limbSwing, float limbSwingAmount,
                           float partialTick, float ageInTicks, float netHeadYaw, float headPitch) {
            String s = skin(v);
            if (s == null || v.isInvisible()) {
                return;
            }
            VertexConsumer vc = buffer.getBuffer(RenderType.eyes(tex(s + "_glow")));
            getParentModel().renderToBuffer(poseStack, vc, 15728640, OverlayTexture.NO_OVERLAY);
        }
    }
}
