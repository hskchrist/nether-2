package com.civilizacionnether.entity.sea;

import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/** Paseo de las criaturas grandes: elige un punto con agua más adelante (sin dar vueltas bruscas) y nada hacia él. */
public class BigSwimGoal extends Goal {
    private final PathfinderMob mob;
    private final double speed;
    private final int range;
    private final int interval;
    private Vec3 wanted;
    private int ticks;

    public BigSwimGoal(PathfinderMob mob, double speed, int range, int interval) {
        this.mob = mob;
        this.speed = speed;
        this.range = range;
        this.interval = interval;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (!mob.isInWater() || mob.getTarget() != null || mob.getRandom().nextInt(interval) != 0) {
            return false;
        }
        wanted = pick();
        return wanted != null;
    }

    private Vec3 pick() {
        for (int i = 0; i < 12; i++) {
            float yaw = mob.getYRot() + (mob.getRandom().nextFloat() - 0.5f) * (i < 6 ? 120.0f : 300.0f);
            double dist = range * (0.4 + mob.getRandom().nextDouble() * 0.6);
            double x = mob.getX() - Mth.sin(yaw * Mth.DEG_TO_RAD) * dist;
            double z = mob.getZ() + Mth.cos(yaw * Mth.DEG_TO_RAD) * dist;
            double y = mob.getY() + (mob.getRandom().nextDouble() - 0.5) * 8.0;
            BlockPos p = BlockPos.containing(x, y, z);
            if (SeaLife.isWater(mob.level(), p) && SeaLife.isWater(mob.level(), p.above((int) Math.ceil(mob.getBbHeight())))
                    && SeaLife.isWater(mob.level(), p.below())) {
                return Vec3.atCenterOf(p);
            }
        }
        return null;
    }

    @Override
    public void start() {
        ticks = 0;
        mob.getMoveControl().setWantedPosition(wanted.x, wanted.y, wanted.z, speed);
    }

    @Override
    public boolean canContinueToUse() {
        return wanted != null && mob.getTarget() == null && ticks < 300 && mob.isInWater()
                && mob.position().distanceToSqr(wanted) > 4.0;
    }

    @Override
    public void tick() {
        if (++ticks % 20 == 0) {
            mob.getMoveControl().setWantedPosition(wanted.x, wanted.y, wanted.z, speed);
        }
    }

    @Override
    public void stop() {
        wanted = null;
    }
}
