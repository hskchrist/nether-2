package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import com.google.common.collect.ImmutableSet;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.entity.npc.VillagerType;
import net.minecraft.world.entity.ai.village.poi.PoiType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Aldeanos del Nether: el tipo "nether" (los aldeanos que están en el Nether lo toman, como cuando cambian de bioma)
 * y las 5 profesiones con mesa propia del Nether. Sus intercambios son los mismos de la profesión vanilla equivalente.
 */
public final class ModVillagers {
    public static final DeferredRegister<VillagerType> TYPES = DeferredRegister.create(Registries.VILLAGER_TYPE, CivilizacionNether.MODID);
    public static final DeferredRegister<VillagerProfession> PROFESSIONS = DeferredRegister.create(Registries.VILLAGER_PROFESSION, CivilizacionNether.MODID);

    public static final DeferredHolder<VillagerType, VillagerType> NETHER = TYPES.register("nether", () -> new VillagerType("nether"));

    public static final DeferredHolder<VillagerProfession, VillagerProfession> CARTOGRAFO =
            profession("cartografo", ModPoiTypes.CARTOGRAPHER_DESK, SoundEvents.VILLAGER_WORK_CARTOGRAPHER);
    public static final DeferredHolder<VillagerProfession, VillagerProfession> FLECHERO =
            profession("flechero", ModPoiTypes.FLETCHER_BENCH, SoundEvents.VILLAGER_WORK_FLETCHER);
    public static final DeferredHolder<VillagerProfession, VillagerProfession> PELETERO =
            profession("peletero", ModPoiTypes.LEATHER_CAULDRON, SoundEvents.VILLAGER_WORK_LEATHERWORKER);
    public static final DeferredHolder<VillagerProfession, VillagerProfession> PASTOR =
            profession("pastor", ModPoiTypes.SHEPHERD_LOOM, SoundEvents.VILLAGER_WORK_SHEPHERD);
    public static final DeferredHolder<VillagerProfession, VillagerProfession> ALBANIL =
            profession("albanil", ModPoiTypes.MASON_CUTTER, SoundEvents.VILLAGER_WORK_MASON);

    private static DeferredHolder<VillagerProfession, VillagerProfession> profession(String name, DeferredHolder<PoiType, PoiType> poi,
                                                                                    SoundEvent sound) {
        return PROFESSIONS.register(name, () -> {
            ResourceKey<PoiType> key = poi.getKey();
            return new VillagerProfession(name, h -> h.is(key), h -> h.is(key), ImmutableSet.of(), ImmutableSet.of(), sound);
        });
    }

    private ModVillagers() {
    }
}
