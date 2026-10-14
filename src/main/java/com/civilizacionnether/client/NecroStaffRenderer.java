package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.item.NecroStaffItem;
import software.bernie.geckolib.model.DefaultedItemGeoModel;
import software.bernie.geckolib.renderer.GeoItemRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/** Báculo 3D en la mano: geo/item/necro_staff.geo.json; el orbe brilla con textures/item/necro_staff_glowmask.png. */
public class NecroStaffRenderer extends GeoItemRenderer<NecroStaffItem> {
    public NecroStaffRenderer() {
        super(new DefaultedItemGeoModel<>(CivilizacionNether.id("necro_staff")));
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }
}
