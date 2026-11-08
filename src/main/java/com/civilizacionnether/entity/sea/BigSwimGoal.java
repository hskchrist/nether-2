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

    /**
     * Elige un punto más adelante donde el cuerpo entero quepa en el agua (o la lava), por debajo de la superficie: busca
     * en la columna de ese punto el tramo de agua y nada por el medio, así no se queda flotando arriba ni trabado.
     */
    private Vec3 pick() {
        int body = (int) Math.ceil(mob.getBbHeight());
        for (int i = 0; i < 24; i++) {
            float yaw = mob.getYRot() + (mob.getRandom().nextFloat() - 0.5f) * (i < 8 ? 120.0f : 360.0f);
            double dist = range * (i < 16 ? 0.4 + mob.getRandom().nextDouble() * 0.6 : 0.15 + mob.getRandom().nextDouble() * 0.3);
            int x = Mth.floor(mob.getX() - Mth.sin(yaw * Mth.DEG_TO_RAD) * dist);
            int z = Mth.floor(mob.getZ() + Mth.cos(yaw * Mth.DEG_TO_RAD) * dist);
            // tramo de agua en esa columna, cerca de la altura actual
            int y0 = Mth.floor(mob.getY());
            int top = Integer.MIN_VALUE;
            int bottom = Integer.MAX_VALUE;
            for (int dy = -12; dy <= 12; dy++) {
                if (SeaLife.isWater(mob.level(), new BlockPos(x, y0 + dy, z))) {
                    top = Math.max(top, y0 + dy);
                    bottom = Math.min(bottom, y0 + dy);
                }
            }
            if (top == Integer.MIN_VALUE || top - bottom + 1 < body + 1) {
                continue;
            }
            int lo = bottom + 1;
            int hi = Math.max(lo, top - body - 1);
            int y = lo + mob.getRandom().nextInt(hi - lo + 1);
            BlockPos p = new BlockPos(x, y, z);
            if (SeaLife.isWater(mob.level(), p) && SeaLife.isWater(mob.level(), p.above(body))) {
                return Vec3.atCenterOf(p);
            }
        }
        return null;
    }

    @Override
    public void start() {
        ticks = 0;
        stuck = 0;
        last = null;
        mob.getMoveControl().setWantedPosition(wanted.x, wanted.y, wanted.z, speed);
    }

    @Override
    public boolean canContinueToUse() {
        return wanted != null && mob.getTarget() == null && ticks < 300 && mob.isInWater() && stuck < 3
                && mob.position().distanceToSqr(wanted) > 4.0;
    }

    private Vec3 last;
    private int stuck;

    @Override
    public void tick() {
        if (++ticks % 20 == 0) {
            mob.getMoveControl().setWantedPosition(wanted.x, wanted.y, wanted.z, speed);
            // si casi no avanzó en un segundo, está trabado: busca otro punto
            if (last != null && mob.position().distanceToSqr(last) < 0.25) {
                stuck++;
            } else {
                stuck = 0;
            }
            last = mob.position();
        }
    }

    @Override
    public void stop() {
        wanted = null;
    }
}
