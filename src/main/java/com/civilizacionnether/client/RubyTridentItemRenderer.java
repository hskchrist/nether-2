package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.TridentModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.ModelResourceLocation;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

/**
 * Tridente de Rubí como ítem: en la mano se dibuja el modelo 3D del tridente con la textura roja (igual que el
 * tridente vanilla); en el inventario, tirado en el suelo y en los marcos se ve el dibujo 32x32 del usuario.
 */
public class RubyTridentItemRenderer extends BlockEntityWithoutLevelRenderer {
    public static final ModelResourceLocation INVENTORY_MODEL =
            ModelResourceLocation.standalone(CivilizacionNether.id("item/ruby_trident_inventory"));
    private static final ResourceLocation TEXTURE = CivilizacionNether.id("textures/entity/ruby_trident.png");
    private TridentModel model;

    public RubyTridentItemRenderer() {
        super(Minecraft.getInstance().getBlockEntityRenderDispatcher(), Minecraft.getInstance().getEntityModels());
    }

    @Override
    public void renderByItem(ItemStack stack, ItemDisplayContext context, PoseStack poseStack, MultiBufferSource buffer,
                             int light, int overlay) {
        Minecraft mc = Minecraft.getInstance();
        if (context == ItemDisplayContext.GUI || context == ItemDisplayContext.GROUND || context == ItemDisplayContext.FIXED) {
            BakedModel sprite = mc.getModelManager().getModel(INVENTORY_MODEL);
            poseStack.pushPose();
            // el ItemRenderer ya corrió el modelo -0.5; el dibujo plano lo vuelve a hacer con sus propias posiciones
            poseStack.translate(0.5f, 0.5f, 0.5f);
            mc.getItemRenderer().render(stack, context, false, poseStack, buffer, light, overlay, sprite);
            poseStack.popPose();
            return;
        }
        if (model == null) {
            model = new TridentModel(mc.getEntityModels().bakeLayer(ModelLayers.TRIDENT));
        }
        poseStack.pushPose();
        poseStack.scale(1.0f, -1.0f, -1.0f);
        VertexConsumer vc = ItemRenderer.getFoilBufferDirect(buffer, model.renderType(TEXTURE), false, stack.hasFoil());
        model.renderToBuffer(poseStack, vc, light, overlay);
        poseStack.popPose();
    }
}
