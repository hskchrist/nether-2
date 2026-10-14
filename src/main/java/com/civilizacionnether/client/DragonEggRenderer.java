package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.DragonEggEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/** Huevo 3D con grietas de fuego de almas que brillan en la oscuridad. */
public class DragonEggRenderer extends GeoEntityRenderer<DragonEggEntity> {
    public DragonEggRenderer(EntityRendererProvider.Context context) {
        super(context, new DefaultedEntityGeoModel<>(CivilizacionNether.id("nether_dragon_egg")));
        withScale(1.4f);
        this.shadowRadius = 0.45f;
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }
}
