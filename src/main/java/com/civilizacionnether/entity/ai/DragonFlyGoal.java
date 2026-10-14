package com.civilizacionnether.entity.ai;

import com.civilizacionnether.entity.NetherDragonEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Vuelo libre: de vez en cuando el dragón (desde la fase "Joven") despega, da vueltas por el aire y vuelve a aterrizar.
 * Salvaje vuela por su zona; domesticado vuela alrededor de su dueño.
 */
public class DragonFlyGoal extends Goal {
    private final NetherDragonEntity dragon;
    private int ticksLeft;
    private int repick;

    public DragonFlyGoal(NetherDragonEntity dragon) {
        this.dragon = dragon;
        setFlags(EnumSet.of(Flag.MOVE, Flag.JUMP));
    }

    @Override
    public boolean canUse() {
        if (!dragon.canFlyNow() || dragon.isVehicle() || dragon.isOrderedToSit() || dragon.getTarget() != null
                || dragon.isResting() || dragon.isLeashed() || dragon.isPassenger() || !dragon.onGround()) {
            return false;
        }
        if (dragon.hasRecall()) {
            return false;
        }
        if (dragon.isTame() && !dragon.isFree()) {
            LivingEntity owner = dragon.getOwner();
            if (owner == null || dragon.distanceToSqr(owner) > 20 * 20) {
                return false;
            }
            return dragon.getRandom().nextInt(1200) == 0;
        }
        return dragon.getRandom().nextInt(400) == 0; // salvaje o en modo libre
    }

    @Override
    public boolean canContinueToUse() {
        if (ticksLeft <= 0 || dragon.isVehicle() || dragon.isOrderedToSit() || dragon.getTarget() != null || dragon.hasRecall()) {
            return false;
        }
        if (dragon.isTame() && !dragon.isFree()) {
            LivingEntity owner = dragon.getOwner();
            return owner != null && dragon.distanceToSqr(owner) < 28 * 28;
        }
        return true;
    }

    @Override
    public void start() {
        ticksLeft = 300 + dragon.getRandom().nextInt(500);
        dragon.setFlightGoalRunning(true);
        dragon.takeOff();
        repick = 20;
    }

    @Override
    public void stop() {
        dragon.setFlightGoalRunning(false);
        dragon.land();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        ticksLeft--;
        Vec3 target = dragon.getFlyTarget();
        boolean reached = target != null && dragon.position().distanceToSqr(target) < 9.0;
        if (--repick <= 0 || reached || dragon.horizontalCollision || target == null) {
            pickWaypoint();
        }
    }

    private void pickWaypoint() {
        repick = 100 + dragon.getRandom().nextInt(60);
        LivingEntity owner = dragon.isTame() && !dragon.isFree() ? dragon.getOwner() : null;
        Vec3 center = owner != null ? owner.position() : dragon.position();
        double maxY = dragon.level().dimensionType().hasCeiling() ? 118 : dragon.level().getMaxBuildHeight() - 8;
        for (int i = 0; i < 10; i++) {
            double x = center.x + (dragon.getRandom().nextDouble() - 0.5) * 40;
            double z = center.z + (dragon.getRandom().nextDouble() - 0.5) * 40;
            Vec3 probe = new Vec3(x, Math.min(maxY, dragon.getY() + 12), z);
            Vec3 ground = dragon.groundBelow(probe);
            double baseY = ground != null ? ground.y : dragon.getY();
            double y = Math.min(maxY, baseY + 6 + dragon.getRandom().nextInt(9));
            Vec3 point = new Vec3(x, y, z);
            if (dragon.clearPathTo(point)) {
                dragon.setFlyTarget(point);
                return;
            }
        }
        dragon.setFlyTarget(dragon.position().add(0, 3, 0));
    }
}
