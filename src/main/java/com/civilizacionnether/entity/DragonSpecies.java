package com.civilizacionnether.entity;

import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.Item;

/**
 * Especies de dragón. Los tres "infernales" (Infernal, de Almas y de Obsidiana) usan el mismo modelo y los mismos
 * ataques; cambian la skin, el color del fuego y el bioma. Cada uno tiene versión salvaje y domesticable.
 */
public enum DragonSpecies {
    NETHER("nether"),
    INFERNAL("infernal"),
    ALMAS("almas"),
    OBSIDIANA("obsidiana");

    public final String id;

    DragonSpecies(String id) {
        this.id = id;
    }

    public static DragonSpecies byId(int ordinal) {
        DragonSpecies[] v = values();
        return ordinal >= 0 && ordinal < v.length ? v[ordinal] : NETHER;
    }

    /** ¿Es de la familia del Dragón Infernal (modelo del usuario, fuego explosivo, agarre)? */
    public boolean infernalFamily() {
        return this != NETHER;
    }

    /** Llama de su fuego (boca, bolas de fuego, huevos). */
    public ParticleOptions flame() {
        return switch (this) {
            case ALMAS -> ParticleTypes.SOUL_FIRE_FLAME;
            case OBSIDIANA -> ParticleTypes.REVERSE_PORTAL;
            default -> ParticleTypes.FLAME;
        };
    }

    /** Chispas grandes al explotar o al volar la bola de fuego. */
    public ParticleOptions spark() {
        return switch (this) {
            case ALMAS -> ParticleTypes.SOUL;
            case OBSIDIANA -> ParticleTypes.WITCH;
            default -> ParticleTypes.LAVA;
        };
    }

    public EntityType<? extends InfernalDragonEntity> wildType() {
        return switch (this) {
            case ALMAS -> ModEntities.DRAGON_ALMAS.get();
            case OBSIDIANA -> ModEntities.DRAGON_OBSIDIANA.get();
            default -> ModEntities.DRAGON_INFERNAL.get();
        };
    }

    public EntityType<? extends InfernalDragonEntity> tameType() {
        return switch (this) {
            case ALMAS -> ModEntities.DRAGON_ALMAS_DOMESTICABLE.get();
            case OBSIDIANA -> ModEntities.DRAGON_OBSIDIANA_DOMESTICABLE.get();
            default -> ModEntities.DRAGON_INFERNAL_DOMESTICABLE.get();
        };
    }

    public Item eggItem() {
        return switch (this) {
            case INFERNAL -> ModItems.INFERNAL_DRAGON_EGG.get();
            case ALMAS -> ModItems.ALMAS_DRAGON_EGG.get();
            case OBSIDIANA -> ModItems.OBSIDIANA_DRAGON_EGG.get();
            default -> ModItems.DRAGON_EGG.get();
        };
    }

    /** Especie según el tipo de entidad. */
    public static DragonSpecies of(EntityType<?> type) {
        if (type == ModEntities.DRAGON_ALMAS.get() || type == ModEntities.DRAGON_ALMAS_DOMESTICABLE.get()) {
            return ALMAS;
        }
        if (type == ModEntities.DRAGON_OBSIDIANA.get() || type == ModEntities.DRAGON_OBSIDIANA_DOMESTICABLE.get()) {
            return OBSIDIANA;
        }
        if (type == ModEntities.DRAGON_INFERNAL.get() || type == ModEntities.DRAGON_INFERNAL_DOMESTICABLE.get()) {
            return INFERNAL;
        }
        return NETHER;
    }

    public static boolean isTameType(EntityType<?> type) {
        return type == ModEntities.DRAGON_INFERNAL_DOMESTICABLE.get() || type == ModEntities.DRAGON_ALMAS_DOMESTICABLE.get()
                || type == ModEntities.DRAGON_OBSIDIANA_DOMESTICABLE.get();
    }
}
