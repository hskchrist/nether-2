package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import software.bernie.geckolib.animatable.GeoAnimatable;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;

/**
 * Modelo de las criaturas del mar (geo/entity, textures/entity y animations/entity con el mismo nombre).
 * Las que nadan en 3D inclinan el cuerpo al subir y bajar (en SeaCreatureRenderer: antes se sumaba al hueso "root"
 * cada cuadro y la criatura terminaba dando vueltas).
 */
public class SeaCreatureModel<T extends LivingEntity & GeoAnimatable> extends DefaultedEntityGeoModel<T> {
    private final boolean pitch;

    public SeaCreatureModel(String name, boolean pitch) {
        super(CivilizacionNether.id(name));
        this.pitch = pitch;
    }

    /** ¿Inclina el cuerpo al subir y bajar? (lo hace SeaCreatureRenderer sobre todo el modelo). */
    public boolean pitches() {
        return pitch;
    }
}
