package com.civilizacionnether.entity;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.phys.Vec3;

/**
 * Nado en la lava para los mobs del Nether que caminan (humanos, aldeanos y dragones): en vez de hundirse lento como
 * los mobs normales, nadan en la lava como en el agua (la lava no les hace daño).
 */
public final class LavaSwim {
    /** @return true si se movió nadando en la lava (entonces no hay que llamar al travel normal). */
    public static boolean travel(LivingEntity e, Vec3 input) {
        if (!e.isInLava() || !e.isControlledByLocalInstance() || e.isSpectator() || !e.fireImmune()) {
            return false;
        }
        e.moveRelative(0.1f, input);
        e.move(MoverType.SELF, e.getDeltaMovement());
        Vec3 v = e.getDeltaMovement().scale(0.8);
        // flota un poco: no se hunde (FloatGoal lo hace subir si quiere)
        e.setDeltaMovement(v.x, v.y - 0.005, v.z);
        e.calculateEntityAnimation(false);
        return true;
    }

    private LavaSwim() {
    }
}
