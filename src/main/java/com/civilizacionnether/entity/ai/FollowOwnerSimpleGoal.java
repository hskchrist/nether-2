package com.civilizacionnether.entity.ai;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/** Sigue al dueño y se teletransporta cerca si queda muy lejos (también mueve la montura). */
public class FollowOwnerSimpleGoal extends Goal {
    private final TamableAnimal mob;
    private final double speed;
    private final double startDistance;
    private final double stopDistance;
    private LivingEntity owner;
    private int repath;

    public FollowOwnerSimpleGoal(TamableAnimal mob, double speed, double startDistance, double stopDistance) {
        this.mob = mob;
        this.speed = speed;
        this.startDistance = startDistance;
        this.stopDistance = stopDistance;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (!mob.isTame() || mob.isOrderedToSit() || mob.getTarget() != null || mob.isVehicle()) {
            return false;
        }
        LivingEntity o = mob.getOwner();
        if (o == null || o.isSpectator() || o.level() != mob.level()) {
            return false;
        }
        if (mob.distanceToSqr(o) < startDistance * startDistance) {
            return false;
        }
        owner = o;
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        return owner != null && !mob.isOrderedToSit() && mob.getTarget() == null
                && mob.distanceToSqr(owner) > stopDistance * stopDistance;
    }

    @Override
    public void start() {
        repath = 0;
    }

    @Override
    public void stop() {
        owner = null;
        mover().getNavigation().stop();
    }

    private Mob mover() {
        return mob.getVehicle() instanceof Mob vehicle ? vehicle : mob;
    }

    @Override
    public void tick() {
        mob.getLookControl().setLookAt(owner, 10.0f, mob.getMaxHeadXRot());
        if (--repath > 0) {
            return;
        }
        repath = 10;
        if (mob.distanceToSqr(owner) > 30.0 * 30.0) {
            teleportNearOwner();
        } else {
            mover().getNavigation().moveTo(owner, speed);
        }
    }

    private void teleportNearOwner() {
        BlockPos base = owner.blockPosition();
        for (int i = 0; i < 12; i++) {
            int dx = mob.getRandom().nextIntBetweenInclusive(-3, 3);
            int dz = mob.getRandom().nextIntBetweenInclusive(-3, 3);
            if (Math.abs(dx) < 2 && Math.abs(dz) < 2) {
                continue;
            }
            Mob m = mover();
            if (m.randomTeleport(base.getX() + dx + 0.5, base.getY(), base.getZ() + dz + 0.5, false)) {
                m.getNavigation().stop();
                return;
            }
        }
    }
}
