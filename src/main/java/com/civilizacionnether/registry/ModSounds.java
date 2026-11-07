package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Voces grabadas por el usuario para los humanos del Nether (al recibir golpes y al morir). */
public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(Registries.SOUND_EVENT, CivilizacionNether.MODID);

    public static final DeferredHolder<SoundEvent, SoundEvent> MAN_HURT = register("human.man.hurt");
    public static final DeferredHolder<SoundEvent, SoundEvent> WOMAN_HURT = register("human.woman.hurt");
    public static final DeferredHolder<SoundEvent, SoundEvent> BOY_HURT = register("human.boy.hurt");
    public static final DeferredHolder<SoundEvent, SoundEvent> GIRL_HURT = register("human.girl.hurt");

    private static DeferredHolder<SoundEvent, SoundEvent> register(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(CivilizacionNether.id(name)));
    }

    private ModSounds() {
    }
}
