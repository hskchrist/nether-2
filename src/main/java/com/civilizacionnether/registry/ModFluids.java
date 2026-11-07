package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.level.material.Fluid;
import net.neoforged.neoforge.common.SoundActions;
import net.neoforged.neoforge.fluids.BaseFlowingFluid;
import net.neoforged.neoforge.fluids.FluidType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/** Agua del Nether: se nada y se ahoga como en el agua normal, riega cultivos y no se evapora en el Nether. */
public final class ModFluids {
    public static final DeferredRegister<FluidType> FLUID_TYPES = DeferredRegister.create(NeoForgeRegistries.Keys.FLUID_TYPES, CivilizacionNether.MODID);
    public static final DeferredRegister<Fluid> FLUIDS = DeferredRegister.create(Registries.FLUID, CivilizacionNether.MODID);

    public static final DeferredHolder<FluidType, FluidType> NETHER_WATER_TYPE = FLUID_TYPES.register("nether_water", () -> new FluidType(
            FluidType.Properties.create()
                    .descriptionId("block.civilizacion_nether.nether_water")
                    .canSwim(true).canDrown(true).canPushEntity(true).canExtinguish(true).canConvertToSource(true)
                    .supportsBoating(true).canHydrate(true).fallDistanceModifier(0.0f).lightLevel(4)
                    .density(1000).viscosity(1000).motionScale(0.014)
                    .sound(SoundActions.BUCKET_FILL, SoundEvents.BUCKET_FILL)
                    .sound(SoundActions.BUCKET_EMPTY, SoundEvents.BUCKET_EMPTY)));

    public static final DeferredHolder<Fluid, BaseFlowingFluid.Source> NETHER_WATER = FLUIDS.register("nether_water",
            () -> new BaseFlowingFluid.Source(props()));
    public static final DeferredHolder<Fluid, BaseFlowingFluid.Flowing> FLOWING_NETHER_WATER = FLUIDS.register("flowing_nether_water",
            () -> new BaseFlowingFluid.Flowing(props()));

    private static BaseFlowingFluid.Properties props() {
        return new BaseFlowingFluid.Properties(NETHER_WATER_TYPE, NETHER_WATER, FLOWING_NETHER_WATER)
                .bucket(ModItems.NETHER_WATER_BUCKET).block(ModBlocks.NETHER_WATER)
                .slopeFindDistance(4).levelDecreasePerBlock(1).tickRate(5);
    }

    private ModFluids() {
    }
}
