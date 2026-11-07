package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.network.RubyTridentPayload;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ThrownTridentRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.projectile.ThrownTrident;

/** Tridente lanzado: si es un Tridente de Rubí se dibuja con su textura roja y dorada. */
public class RubyTridentRenderer extends ThrownTridentRenderer {
    private static final ResourceLocation RUBY = CivilizacionNether.id("textures/entity/ruby_trident.png");

    public RubyTridentRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public ResourceLocation getTextureLocation(ThrownTrident entity) {
        return RubyTridentPayload.RUBY_TRIDENTS.contains(entity.getId()) ? RUBY : super.getTextureLocation(entity);
    }
}
