package com.civilizacionnether.entity.ai;

import com.civilizacionnether.entity.NetherDragonEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Llamada con el Báculo de dragón: el dragón va hacia su dueño desde donde esté.
 * Si está lejos (más de 20 bloques), a otra altura o ya volando, llega volando y aterriza al lado; si está cerca, camina.
 */
public class DragonRecallGoal extends Goal {
    private final NetherDragonEntity dragon;
    private Player player;
    private int repath;

    public DragonRecallGoal(NetherDragonEntity dragon) {
        this.dragon = dragon;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
    }

    @Override
    public boolean canUse() {
        if (!dragon.hasRecall() || dragon.isVehicle()) {
            return false;
        }
        player = dragon.getRecallPlayer();
        return player != null && player.level() == dragon.level();
    }

    @Override
    public boolean canContinueToUse() {
        return player != null && player.isAlive() && dragon.hasRecall() && !dragon.isVehicle()
                && player.level() == dragon.level();
    }

    @Override
    public void start() {
        repath = 0;
        dragon.setFlightGoalRunning(true);
        dragon.getNavigation().stop();
    }

    @Override
    public void stop() {
        dragon.setFlightGoalRunning(false);
        dragon.stopRecall();
        dragon.getNavigation().stop();
        if (dragon.isFlying()) {
            dragon.land();
        }
        player = null;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        if (dragon.getRecallPlayer() == null) { // también descuenta el tiempo máximo de la llamada
            dragon.stopRecall();
            return;
        }
        dragon.getLookControl().setLookAt(player, 20.0f, 20.0f);
        Vec3 to = player.position().subtract(dragon.position());
        double horiz = to.horizontalDistance();
        double arrive = 4.0 + dragon.getBbWidth();
        boolean wantsFlight = dragon.canFlyNow() && (dragon.isFlying() || horiz > 20.0 || Math.abs(to.y) > 4.0);
        if (wantsFlight) {
            if (!dragon.isFlying()) {
                dragon.takeOff();
            }
            if (horiz < arrive) {
                dragon.land();       // ya llegó: aterriza a su lado
                dragon.stopRecall();
            } else {
                Vec3 dir = new Vec3(to.x, 0, to.z).normalize();
                double height = horiz > 24.0 ? 8.0 : 3.0;
                dragon.setFlyTarget(player.position().subtract(dir.scale(arrive * 0.6)).add(0, height, 0));
            }
            return;
        }
        if (horiz < arrive) {
            dragon.stopRecall();
            return;
        }
        if (--repath <= 0) {
            repath = 10;
            dragon.getNavigation().moveTo(player, 1.5);
        }
    }
}
