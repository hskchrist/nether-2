package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.core.registries.Registries;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Partículas propias: el fuego negro del dragón y las almas rojas (skin del alma). */
public final class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES =
            DeferredRegister.create(Registries.PARTICLE_TYPE, CivilizacionNether.MODID);

    public static final DeferredHolder<ParticleType<?>, SimpleParticleType> BLACK_FLAME =
            PARTICLES.register("black_flame", () -> new SimpleParticleType(false));
    public static final DeferredHolder<ParticleType<?>, SimpleParticleType> RED_SOUL =
            PARTICLES.register("red_soul", () -> new SimpleParticleType(false));

    private ModParticles() {
    }
}
