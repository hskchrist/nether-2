package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.worldgen.PurpleSeaFeature;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModFeatures {
    public static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(Registries.FEATURE, CivilizacionNether.MODID);

    /** Océano Púrpura: cambia el mar de lava del bioma por agua del Nether y decora el fondo. */
    public static final DeferredHolder<Feature<?>, PurpleSeaFeature> PURPLE_SEA = FEATURES.register("purple_sea",
            () -> new PurpleSeaFeature(NoneFeatureConfiguration.CODEC));

    /** Nido del Dragón Infernal en el Bosque Carmesí. */
    public static final DeferredHolder<Feature<?>, com.civilizacionnether.worldgen.InfernalNestFeature> INFERNAL_NEST = FEATURES.register("infernal_nest",
            () -> new com.civilizacionnether.worldgen.InfernalNestFeature(NoneFeatureConfiguration.CODEC));

    private ModFeatures() {
    }
}
