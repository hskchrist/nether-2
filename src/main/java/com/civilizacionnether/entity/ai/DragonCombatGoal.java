package com.civilizacionnether.entity.ai;

import com.civilizacionnether.entity.NetherDragonEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Pelea del dragón cuando no lo monta nadie: mordisco de cerca, aliento de fuego de almas a media distancia
 * y bolas de fuego de lejos. Si está volando, pelea desde el aire.
 */
public class DragonCombatGoal extends Goal {
    private final NetherDragonEntity dragon;
    private int biteCooldown;
    private int repath;

    public DragonCombatGoal(NetherDragonEntity dragon) {
        this.dragon = dragon;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        LivingEntity target = dragon.getTarget();
        return target != null && target.isAlive() && !dragon.isOrderedToSit() && !dragon.isVehicle();
    }

    @Override
    public void start() {
        dragon.setAggressive(true);
        dragon.setResting(false);
        repath = 0;
    }

    @Override
    public void stop() {
        dragon.setAggressive(false);
        dragon.getNavigation().stop();
        if (dragon.isFlying()) {
            dragon.land();
        }
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        LivingEntity target = dragon.getTarget();
        if (target == null) {
            return;
        }
        dragon.getLookControl().setLookAt(target, 20.0f, 20.0f);
        double distSq = dragon.distanceToSqr(target);
        double reach = dragon.getBbWidth() * 0.9 + target.getBbWidth() + 1.5;
        boolean sees = dragon.getSensing().hasLineOfSight(target);
        if (biteCooldown > 0) {
            biteCooldown--;
        }
        if (!dragon.isFlying() && dragon.canFlyNow() && target.getY() - dragon.getY() > 5.0) {
            dragon.takeOff(); // el objetivo está en lo alto (por ejemplo un ghast): sube a pelear
            repath = 0;
        }
        if (--repath <= 0) {
            repath = 10;
            if (dragon.isFlying()) {
                // da vueltas por encima del objetivo
                Vec3 away = dragon.position().subtract(target.position()).multiply(1, 0, 1);
                Vec3 side = away.lengthSqr() < 1.0e-3 ? new Vec3(1, 0, 0) : away.normalize();
                dragon.setFlyTarget(target.position().add(side.scale(6.0)).add(0, 4.0 + dragon.getBbHeight(), 0));
            } else {
                dragon.getNavigation().moveTo(target, 1.15);
            }
        }
        if (distSq <= reach * reach) {
            if (biteCooldown <= 0) {
                biteCooldown = 24;
                dragon.bite(target);
            }
        } else if (sees && distSq < 14 * 14 && dragon.canBreathe() && dragon.getRandom().nextInt(25) == 0) {
            dragon.startBreath();
        } else if (sees && distSq > 8 * 8 && distSq < 40 * 40 && dragon.getRandom().nextInt(30) == 0) {
            dragon.shootFireball(target.getBoundingBox().getCenter().subtract(dragon.mouthPosition()));
        }
    }
}
