package com.civilizacionnether.event;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.DragonEggEntity;
import com.civilizacionnether.entity.HumanoidType;
import com.civilizacionnether.entity.InfernalDragonEntity;
import com.civilizacionnether.entity.sea.BasaltCrabEntity;
import com.civilizacionnether.entity.sea.BlueWhaleEntity;
import com.civilizacionnether.entity.sea.CrimsonMantaEntity;
import com.civilizacionnether.entity.sea.InfernalSharkEntity;
import com.civilizacionnether.entity.sea.MagmaSeahorseEntity;
import com.civilizacionnether.entity.sea.NetherDolphinEntity;
import com.civilizacionnether.entity.sea.NetherFishEntity;
import com.civilizacionnether.entity.sea.ObsidianTurtleEntity;
import com.civilizacionnether.entity.sea.SeaLife;
import com.civilizacionnether.entity.sea.SeaSerpentEntity;
import com.civilizacionnether.entity.sea.VoidJellyfishEntity;
import com.civilizacionnether.network.RubyTridentPayload;
import com.civilizacionnether.entity.NetherDragonEntity;
import com.civilizacionnether.entity.NetherHumanoidEntity;
import com.civilizacionnether.network.DragonBreathPayload;
import com.civilizacionnether.network.DragonShootPayload;
import com.civilizacionnether.registry.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import com.civilizacionnether.registry.ModFluids;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.NeoForgeMod;
import net.neoforged.neoforge.fluids.FluidInteractionRegistry;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.RegisterSpawnPlacementsEvent;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;

@EventBusSubscriber(modid = CivilizacionNether.MODID, bus = EventBusSubscriber.Bus.MOD)
public final class CommonEvents {

    @SubscribeEvent
    public static void attributes(EntityAttributeCreationEvent event) {
        for (HumanoidType type : HumanoidType.values()) {
            event.put(ModEntities.HUMANOIDS.get(type).get(), NetherHumanoidEntity.createAttributes(type).build());
        }
        event.put(ModEntities.NETHER_DRAGON.get(), NetherDragonEntity.createAttributes().build());
        event.put(ModEntities.DRAGON_EGG.get(), DragonEggEntity.createAttributes().build());
        event.put(ModEntities.DRAGON_INFERNAL.get(), InfernalDragonEntity.createInfernalAttributes().build());
        event.put(ModEntities.DRAGON_INFERNAL_DOMESTICABLE.get(), InfernalDragonEntity.createInfernalAttributes().build());
        event.put(ModEntities.DRAGON_ALMAS.get(), InfernalDragonEntity.createInfernalAttributes().build());
        event.put(ModEntities.DRAGON_ALMAS_DOMESTICABLE.get(), InfernalDragonEntity.createInfernalAttributes().build());
        event.put(ModEntities.DRAGON_OBSIDIANA.get(), InfernalDragonEntity.createInfernalAttributes().build());
        event.put(ModEntities.DRAGON_OBSIDIANA_DOMESTICABLE.get(), InfernalDragonEntity.createInfernalAttributes().build());
        event.put(ModEntities.PEZ_BRASA.get(), NetherFishEntity.createAttributes(3.0).build());
        event.put(ModEntities.PEZ_ALMA.get(), NetherFishEntity.createAttributes(4.0).build());
        event.put(ModEntities.ANGUILA_RUBI.get(), NetherFishEntity.createAttributes(6.0).build());
        event.put(ModEntities.MEDUSA_VACIO.get(), VoidJellyfishEntity.createAttributes().build());
        event.put(ModEntities.CANGREJO_BASALTO.get(), BasaltCrabEntity.createAttributes().build());
        event.put(ModEntities.CABALLITO_MAGMA.get(), MagmaSeahorseEntity.createAttributes().build());
        event.put(ModEntities.MANTA_CARMESI.get(), CrimsonMantaEntity.createAttributes().build());
        event.put(ModEntities.TORTUGA_OBSIDIANA.get(), ObsidianTurtleEntity.createAttributes().build());
        event.put(ModEntities.TIBURON_INFERNAL.get(), InfernalSharkEntity.createAttributes().build());
        event.put(ModEntities.SERPIENTE_MARINA.get(), SeaSerpentEntity.createAttributes().build());
        event.put(ModEntities.DELFIN_NETHER.get(), NetherDolphinEntity.createNetherAttributes().build());
        event.put(ModEntities.BALLENA_AZUL.get(), BlueWhaleEntity.createAttributes().build());
    }

    @SubscribeEvent
    public static void spawnPlacements(RegisterSpawnPlacementsEvent event) {
        for (HumanoidType type : HumanoidType.values()) {
            event.register(ModEntities.HUMANOIDS.get(type).get(), SpawnPlacementTypes.ON_GROUND,
                    Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, CommonEvents::canSpawnHumanoid,
                    RegisterSpawnPlacementsEvent.Operation.REPLACE);
        }
        event.register(ModEntities.NETHER_DRAGON.get(), SpawnPlacementTypes.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, CommonEvents::canSpawnDragon,
                RegisterSpawnPlacementsEvent.Operation.REPLACE);
        // dragones Infernal, de Almas y de Obsidiana (salvajes y domesticables)
        for (var t : java.util.List.of(ModEntities.DRAGON_INFERNAL, ModEntities.DRAGON_INFERNAL_DOMESTICABLE, ModEntities.DRAGON_ALMAS,
                ModEntities.DRAGON_ALMAS_DOMESTICABLE, ModEntities.DRAGON_OBSIDIANA, ModEntities.DRAGON_OBSIDIANA_DOMESTICABLE)) {
            event.register(t.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                    CommonEvents::canSpawnInfernal, RegisterSpawnPlacementsEvent.Operation.REPLACE);
        }
        // fauna del Mar del Nether
        RegisterSpawnPlacementsEvent.Operation op = RegisterSpawnPlacementsEvent.Operation.REPLACE;
        Heightmap.Types hm = Heightmap.Types.MOTION_BLOCKING_NO_LEAVES;
        event.register(ModEntities.PEZ_BRASA.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnInWater, op);
        event.register(ModEntities.PEZ_ALMA.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnInWater, op);
        event.register(ModEntities.ANGUILA_RUBI.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnOnFloor, op);
        event.register(ModEntities.MEDUSA_VACIO.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnInWater, op);
        event.register(ModEntities.CANGREJO_BASALTO.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnOnFloor, op);
        event.register(ModEntities.CABALLITO_MAGMA.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnInWater, op);
        event.register(ModEntities.MANTA_CARMESI.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnInWater, op);
        event.register(ModEntities.TORTUGA_OBSIDIANA.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnOnFloor, op);
        event.register(ModEntities.TIBURON_INFERNAL.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnShark, op);
        event.register(ModEntities.SERPIENTE_MARINA.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnSerpent, op);
        event.register(ModEntities.DELFIN_NETHER.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnInWater, op);
        event.register(ModEntities.BALLENA_AZUL.get(), SpawnPlacementTypes.IN_WATER, hm, SeaLife::canSpawnDeep, op);
    }

    private static boolean canSpawnHumanoid(EntityType<NetherHumanoidEntity> type, ServerLevelAccessor level,
                                            MobSpawnType reason, BlockPos pos, RandomSource random) {
        if (reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION) {
            if (type == ModEntities.humanoid(HumanoidType.SUBDITO_ALMA)) {
                return false; // los súbditos solo aparecen invocados
            }
            if (type == ModEntities.humanoid(HumanoidType.REY_NECROMANCER) && random.nextInt(20) != 0) {
                return false; // fuera de la capital el Rey es muy raro
            }
        }
        BlockPos below = pos.below();
        return level.getBlockState(below).isValidSpawn(level, below, type) && !level.getBlockState(below).liquid();
    }

    private static boolean canSpawnDragon(EntityType<NetherDragonEntity> type, ServerLevelAccessor level,
                                          MobSpawnType reason, BlockPos pos, RandomSource random) {
        if (reason == MobSpawnType.NATURAL && random.nextInt(4) != 0) {
            return false; // los dragones son escasos
        }
        BlockPos below = pos.below();
        return level.getBlockState(below).isValidSpawn(level, below, type) && !level.getBlockState(below).liquid();
    }

    private static boolean canSpawnInfernal(EntityType<InfernalDragonEntity> type, ServerLevelAccessor level,
                                            MobSpawnType reason, BlockPos pos, RandomSource random) {
        if (reason == MobSpawnType.NATURAL && random.nextInt(3) != 0) {
            return false;
        }
        BlockPos below = pos.below();
        return level.getBlockState(below).isValidSpawn(level, below, type) && !level.getBlockState(below).liquid()
                && level.noCollision(type.getSpawnAABB(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5));
    }

    /** La lava con agua del Nether forma obsidiana (fuente) o piedra negra (corriente). */
    @SubscribeEvent
    public static void setup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> FluidInteractionRegistry.addInteraction(NeoForgeMod.LAVA_TYPE.value(),
                new FluidInteractionRegistry.InteractionInformation(ModFluids.NETHER_WATER_TYPE.get(),
                        fluid -> fluid.isSource() ? Blocks.OBSIDIAN.defaultBlockState() : Blocks.BLACKSTONE.defaultBlockState())));
    }

    @SubscribeEvent
    public static void payloads(RegisterPayloadHandlersEvent event) {
        PayloadRegistrar registrar = event.registrar("3");
        registrar.playToServer(DragonBreathPayload.TYPE, DragonBreathPayload.STREAM_CODEC, DragonBreathPayload::handle);
        registrar.playToServer(com.civilizacionnether.network.DragonGrabPayload.TYPE,
                com.civilizacionnether.network.DragonGrabPayload.STREAM_CODEC, com.civilizacionnether.network.DragonGrabPayload::handle);
        registrar.playToServer(DragonShootPayload.TYPE, DragonShootPayload.STREAM_CODEC, DragonShootPayload::handle);
        registrar.playToClient(RubyTridentPayload.TYPE, RubyTridentPayload.STREAM_CODEC, RubyTridentPayload::handle);
    }

    private CommonEvents() {
    }
}
