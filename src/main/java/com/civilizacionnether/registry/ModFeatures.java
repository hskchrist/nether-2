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

    /** Mar del Nether: cambia el mar de lava del bioma por agua del Nether y decora el fondo. */
    public static final DeferredHolder<Feature<?>, PurpleSeaFeature> PURPLE_SEA = FEATURES.register("purple_sea",
            () -> new PurpleSeaFeature(NoneFeatureConfiguration.CODEC));

    /** Árbol de Hielo del Mar del Nether (copa ancha con hojas y carámbanos colgando). */
    public static final DeferredHolder<Feature<?>, com.civilizacionnether.worldgen.FrostTreeFeature> FROST_TREE = FEATURES.register("frost_tree",
            () -> new com.civilizacionnether.worldgen.FrostTreeFeature(NoneFeatureConfiguration.CODEC));

    /** Lagos y lagunas de agua del Nether en el Mar del Nether. */
    public static final DeferredHolder<Feature<?>, com.civilizacionnether.worldgen.NetherLakeFeature> NETHER_LAKE = FEATURES.register("nether_lake",
            () -> new com.civilizacionnether.worldgen.NetherLakeFeature(NoneFeatureConfiguration.CODEC));

    /** Manantiales de agua del Nether (arroyos y cascadas), lejos del Reino. */
    public static final DeferredHolder<Feature<?>, com.civilizacionnether.worldgen.NetherSpringFeature> NETHER_SPRING = FEATURES.register("nether_spring",
            () -> new com.civilizacionnether.worldgen.NetherSpringFeature(NoneFeatureConfiguration.CODEC));

    /** Nido del Dragón Infernal en el Bosque Carmesí. */
    public static final DeferredHolder<Feature<?>, com.civilizacionnether.worldgen.InfernalNestFeature> INFERNAL_NEST = FEATURES.register("infernal_nest",
            () -> new com.civilizacionnether.worldgen.InfernalNestFeature(NoneFeatureConfiguration.CODEC, com.civilizacionnether.entity.DragonSpecies.INFERNAL));
    /** Nido del Dragón de Almas en el Valle de Arena de Almas. */
    public static final DeferredHolder<Feature<?>, com.civilizacionnether.worldgen.InfernalNestFeature> ALMAS_NEST = FEATURES.register("almas_nest",
            () -> new com.civilizacionnether.worldgen.InfernalNestFeature(NoneFeatureConfiguration.CODEC, com.civilizacionnether.entity.DragonSpecies.ALMAS));
    /** Nido del Dragón de Obsidiana en los Deltas de Basalto. */
    public static final DeferredHolder<Feature<?>, com.civilizacionnether.worldgen.InfernalNestFeature> OBSIDIANA_NEST = FEATURES.register("obsidiana_nest",
            () -> new com.civilizacionnether.worldgen.InfernalNestFeature(NoneFeatureConfiguration.CODEC, com.civilizacionnether.entity.DragonSpecies.OBSIDIANA));

    private ModFeatures() {
    }
}
