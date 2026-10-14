package com.civilizacionnether.event;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.DragonEggEntity;
import com.civilizacionnether.entity.HumanoidType;
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
import net.minecraft.world.level.levelgen.Heightmap;
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

    @SubscribeEvent
    public static void payloads(RegisterPayloadHandlersEvent event) {
        PayloadRegistrar registrar = event.registrar("2");
        registrar.playToServer(DragonBreathPayload.TYPE, DragonBreathPayload.STREAM_CODEC, DragonBreathPayload::handle);
        registrar.playToServer(DragonShootPayload.TYPE, DragonShootPayload.STREAM_CODEC, DragonShootPayload::handle);
    }

    private CommonEvents() {
    }
}
