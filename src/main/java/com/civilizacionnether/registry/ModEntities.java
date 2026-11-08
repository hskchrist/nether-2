package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.DragonEggEntity;
import com.civilizacionnether.entity.DragonFireballEntity;
import com.civilizacionnether.entity.HumanoidType;
import com.civilizacionnether.entity.InfernalDragonEntity;
import com.civilizacionnether.entity.NetherDragonEntity;
import com.civilizacionnether.entity.sea.BasaltCrabEntity;
import com.civilizacionnether.entity.sea.BlueWhaleEntity;
import com.civilizacionnether.entity.sea.CrimsonMantaEntity;
import com.civilizacionnether.entity.sea.InfernalSharkEntity;
import com.civilizacionnether.entity.sea.MagmaSeahorseEntity;
import com.civilizacionnether.entity.sea.NetherDolphinEntity;
import com.civilizacionnether.entity.sea.NetherFishEntity;
import com.civilizacionnether.entity.sea.ObsidianTurtleEntity;
import com.civilizacionnether.entity.sea.SeaSerpentEntity;
import com.civilizacionnether.entity.sea.VoidJellyfishEntity;
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

    /** Dragón Infernal: otro dragón (modelo del usuario); el salvaje vive en un nido del Bosque Carmesí. */
    public static final DeferredHolder<EntityType<?>, EntityType<InfernalDragonEntity>> DRAGON_INFERNAL = ENTITIES.register("dragon_infernal",
            () -> EntityType.Builder.<InfernalDragonEntity>of(InfernalDragonEntity::new, MobCategory.CREATURE)
                    .sized(3.4f, 3.0f)
                    .eyeHeight(2.7f)
                    .passengerAttachments(new Vec3(0.0, 2.55, -0.4))
                    .fireImmune()
                    .clientTrackingRange(16)
                    .build("dragon_infernal"));
    /** Dragón Infernal domesticable: sale de los huevos infernales con dueño y se doma con rubíes; los salvajes son sus rivales. */
    public static final DeferredHolder<EntityType<?>, EntityType<InfernalDragonEntity>> DRAGON_INFERNAL_DOMESTICABLE = ENTITIES.register("dragon_infernal_domesticable",
            () -> EntityType.Builder.<InfernalDragonEntity>of(InfernalDragonEntity::new, MobCategory.CREATURE)
                    .sized(3.4f, 3.0f)
                    .eyeHeight(2.7f)
                    .passengerAttachments(new Vec3(0.0, 2.55, -0.4))
                    .fireImmune()
                    .clientTrackingRange(16)
                    .build("dragon_infernal_domesticable"));
    /** Dragón de Almas salvaje (fuego azul; nido en el Valle de Arena de Almas). */
    public static final DeferredHolder<EntityType<?>, EntityType<InfernalDragonEntity>> DRAGON_ALMAS = ENTITIES.register("dragon_almas",
            () -> EntityType.Builder.<InfernalDragonEntity>of(InfernalDragonEntity::new, MobCategory.CREATURE)
                    .sized(3.4f, 3.0f)
                    .eyeHeight(2.7f)
                    .passengerAttachments(new Vec3(0.0, 2.55, -0.4))
                    .fireImmune()
                    .clientTrackingRange(16)
                    .build("dragon_almas"));
    /** Dragón de Almas domesticable. */
    public static final DeferredHolder<EntityType<?>, EntityType<InfernalDragonEntity>> DRAGON_ALMAS_DOMESTICABLE = ENTITIES.register("dragon_almas_domesticable",
            () -> EntityType.Builder.<InfernalDragonEntity>of(InfernalDragonEntity::new, MobCategory.CREATURE)
                    .sized(3.4f, 3.0f)
                    .eyeHeight(2.7f)
                    .passengerAttachments(new Vec3(0.0, 2.55, -0.4))
                    .fireImmune()
                    .clientTrackingRange(16)
                    .build("dragon_almas_domesticable"));
    /** Dragón de Obsidiana salvaje (fuego morado; nido en los Deltas de Basalto). */
    public static final DeferredHolder<EntityType<?>, EntityType<InfernalDragonEntity>> DRAGON_OBSIDIANA = ENTITIES.register("dragon_obsidiana",
            () -> EntityType.Builder.<InfernalDragonEntity>of(InfernalDragonEntity::new, MobCategory.CREATURE)
                    .sized(3.4f, 3.0f)
                    .eyeHeight(2.7f)
                    .passengerAttachments(new Vec3(0.0, 2.55, -0.4))
                    .fireImmune()
                    .clientTrackingRange(16)
                    .build("dragon_obsidiana"));
    /** Dragón de Obsidiana domesticable. */
    public static final DeferredHolder<EntityType<?>, EntityType<InfernalDragonEntity>> DRAGON_OBSIDIANA_DOMESTICABLE = ENTITIES.register("dragon_obsidiana_domesticable",
            () -> EntityType.Builder.<InfernalDragonEntity>of(InfernalDragonEntity::new, MobCategory.CREATURE)
                    .sized(3.4f, 3.0f)
                    .eyeHeight(2.7f)
                    .passengerAttachments(new Vec3(0.0, 2.55, -0.4))
                    .fireImmune()
                    .clientTrackingRange(16)
                    .build("dragon_obsidiana_domesticable"));

    // ------------------------------------------------------------------ fauna del Mar del Nether
    public static final DeferredHolder<EntityType<?>, EntityType<NetherFishEntity>> PEZ_BRASA = fish("pez_brasa", 0.5f, 0.35f);
    public static final DeferredHolder<EntityType<?>, EntityType<NetherFishEntity>> PEZ_ALMA = fish("pez_alma", 0.5f, 0.45f);
    public static final DeferredHolder<EntityType<?>, EntityType<NetherFishEntity>> ANGUILA_RUBI = fish("anguila_rubi", 0.45f, 0.35f);

    public static final DeferredHolder<EntityType<?>, EntityType<VoidJellyfishEntity>> MEDUSA_VACIO = ENTITIES.register("medusa_vacio",
            () -> EntityType.Builder.<VoidJellyfishEntity>of(VoidJellyfishEntity::new, MobCategory.WATER_AMBIENT)
                    .sized(0.6f, 1.0f).eyeHeight(0.7f).fireImmune().clientTrackingRange(8).build("medusa_vacio"));
    public static final DeferredHolder<EntityType<?>, EntityType<BasaltCrabEntity>> CANGREJO_BASALTO = ENTITIES.register("cangrejo_basalto",
            () -> EntityType.Builder.<BasaltCrabEntity>of(BasaltCrabEntity::new, MobCategory.WATER_CREATURE)
                    .sized(0.9f, 0.45f).eyeHeight(0.35f).fireImmune().clientTrackingRange(8).build("cangrejo_basalto"));
    public static final DeferredHolder<EntityType<?>, EntityType<MagmaSeahorseEntity>> CABALLITO_MAGMA = ENTITIES.register("caballito_magma",
            () -> EntityType.Builder.<MagmaSeahorseEntity>of(MagmaSeahorseEntity::new, MobCategory.WATER_CREATURE)
                    .sized(0.4f, 1.0f).eyeHeight(0.85f).fireImmune().clientTrackingRange(8).build("caballito_magma"));
    public static final DeferredHolder<EntityType<?>, EntityType<CrimsonMantaEntity>> MANTA_CARMESI = ENTITIES.register("manta_carmesi",
            () -> EntityType.Builder.<CrimsonMantaEntity>of(CrimsonMantaEntity::new, MobCategory.WATER_CREATURE)
                    .sized(2.6f, 0.5f).eyeHeight(0.3f).passengerAttachments(new Vec3(0.0, 0.42, 0.1))
                    .fireImmune().clientTrackingRange(10).build("manta_carmesi"));
    public static final DeferredHolder<EntityType<?>, EntityType<ObsidianTurtleEntity>> TORTUGA_OBSIDIANA = ENTITIES.register("tortuga_obsidiana",
            () -> EntityType.Builder.<ObsidianTurtleEntity>of(ObsidianTurtleEntity::new, MobCategory.WATER_CREATURE)
                    .sized(1.6f, 0.7f).eyeHeight(0.5f).fireImmune().clientTrackingRange(10).build("tortuga_obsidiana"));
    public static final DeferredHolder<EntityType<?>, EntityType<InfernalSharkEntity>> TIBURON_INFERNAL = ENTITIES.register("tiburon_infernal",
            () -> EntityType.Builder.<InfernalSharkEntity>of(InfernalSharkEntity::new, MobCategory.MONSTER)
                    .sized(1.6f, 1.3f).eyeHeight(0.8f).fireImmune().clientTrackingRange(10).build("tiburon_infernal"));
    public static final DeferredHolder<EntityType<?>, EntityType<SeaSerpentEntity>> SERPIENTE_MARINA = ENTITIES.register("serpiente_marina",
            () -> EntityType.Builder.<SeaSerpentEntity>of(SeaSerpentEntity::new, MobCategory.MONSTER)
                    .sized(3.0f, 3.0f).eyeHeight(2.6f).fireImmune().clientTrackingRange(16).build("serpiente_marina"));
    public static final DeferredHolder<EntityType<?>, EntityType<NetherDolphinEntity>> DELFIN_NETHER = ENTITIES.register("delfin_nether",
            () -> EntityType.Builder.<NetherDolphinEntity>of(NetherDolphinEntity::new, MobCategory.WATER_CREATURE)
                    .sized(0.9f, 0.6f).eyeHeight(0.3f).fireImmune().clientTrackingRange(10).build("delfin_nether"));
    public static final DeferredHolder<EntityType<?>, EntityType<BlueWhaleEntity>> BALLENA_AZUL = ENTITIES.register("ballena_azul",
            () -> EntityType.Builder.<BlueWhaleEntity>of(BlueWhaleEntity::new, MobCategory.WATER_CREATURE)
                    .sized(4.0f, 2.6f).eyeHeight(1.6f).fireImmune().clientTrackingRange(16).build("ballena_azul"));

    private static DeferredHolder<EntityType<?>, EntityType<NetherFishEntity>> fish(String id, float w, float h) {
        return ENTITIES.register(id, () -> EntityType.Builder.<NetherFishEntity>of(NetherFishEntity::new, MobCategory.WATER_AMBIENT)
                .sized(w, h).eyeHeight(h * 0.65f).fireImmune().clientTrackingRange(4).build(id));
    }

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
