package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.DragonEggEntity;
import com.civilizacionnether.entity.DragonFireballEntity;
import com.civilizacionnether.entity.HumanoidType;
import com.civilizacionnether.entity.NetherDragonEntity;
import com.civilizacionnether.entity.NetherHumanoidEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.EnumMap;
import java.util.Map;

public final class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES =
            DeferredRegister.create(Registries.ENTITY_TYPE, CivilizacionNether.MODID);

    /** Un EntityType por cada tipo humano: misma clase, distinta configuración. */
    public static final Map<HumanoidType, DeferredHolder<EntityType<?>, EntityType<NetherHumanoidEntity>>> HUMANOIDS =
            new EnumMap<>(HumanoidType.class);

    /** Dragón del Nether: el tamaño es el del adulto; las fases de crecimiento lo achican con el atributo de escala. */
    public static final DeferredHolder<EntityType<?>, EntityType<NetherDragonEntity>> NETHER_DRAGON = ENTITIES.register("nether_dragon",
            () -> EntityType.Builder.<NetherDragonEntity>of(NetherDragonEntity::new, MobCategory.CREATURE)
                    .sized(3.2f, 2.8f)
                    .eyeHeight(2.5f)
                    .passengerAttachments(new Vec3(0.0, 2.3, -0.1))
                    .fireImmune()
                    .clientTrackingRange(16)
                    .build("nether_dragon"));

    /** Huevo puesto en el suelo (se incuba y nace una cría). */
    public static final DeferredHolder<EntityType<?>, EntityType<DragonEggEntity>> DRAGON_EGG = ENTITIES.register("dragon_egg",
            () -> EntityType.Builder.<DragonEggEntity>of(DragonEggEntity::new, MobCategory.MISC)
                    .sized(0.8f, 1.2f)
                    .eyeHeight(0.9f)
                    .fireImmune()
                    .clientTrackingRange(10)
                    .build("dragon_egg"));

    /** Bola de fuego que dispara el dragón (clic derecho del jinete). */
    public static final DeferredHolder<EntityType<?>, EntityType<DragonFireballEntity>> DRAGON_FIREBALL = ENTITIES.register("dragon_fireball",
            () -> EntityType.Builder.<DragonFireballEntity>of(DragonFireballEntity::new, MobCategory.MISC)
                    .sized(0.6f, 0.6f)
                    .clientTrackingRange(8)
                    .updateInterval(2)
                    .build("dragon_fireball"));

    static {
        for (HumanoidType type : HumanoidType.values()) {
            // Guerrero y Arquero: mismo tamaño que el Wither Skeleton (0,7 x 2,4 bloques); el Rey algo más alto
            HUMANOIDS.put(type, ENTITIES.register(type.id, () -> EntityType.Builder
                    .<NetherHumanoidEntity>of((entityType, level) -> new NetherHumanoidEntity(entityType, level, type), MobCategory.CREATURE)
                    .sized(type.width, type.height)
                    .eyeHeight(type.height * 0.875f)
                    .fireImmune()
                    .clientTrackingRange(10)
                    .build(type.id)));
        }
    }

    public static EntityType<NetherHumanoidEntity> humanoid(HumanoidType type) {
        return HUMANOIDS.get(type).get();
    }

    private ModEntities() {
    }
}
