package com.civilizacionnether.entity.ai;

import com.civilizacionnether.entity.NetherDragonEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/** Cuando el dragón se queda quieto un rato en el suelo, se echa a descansar (animación "rest"). */
public class DragonRestGoal extends Goal {
    private final NetherDragonEntity dragon;
    private int ticksLeft;
    private int lastHurt;

    public DragonRestGoal(NetherDragonEntity dragon) {
        this.dragon = dragon;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
    }

    @Override
    public boolean canUse() {
        return dragon.onGround() && !dragon.isFlying() && !dragon.isVehicle() && dragon.getTarget() == null
                && !dragon.isInLove() && dragon.getIdleTicks() > 100 && dragon.getRandom().nextInt(120) == 0;
    }

    @Override
    public boolean canContinueToUse() {
        return ticksLeft > 0 && dragon.getTarget() == null && !dragon.isVehicle() && !dragon.isFlying()
                && dragon.getLastHurtByMobTimestamp() == lastHurt && dragon.isResting();
    }

    @Override
    public void start() {
        ticksLeft = 400 + dragon.getRandom().nextInt(1200);
        lastHurt = dragon.getLastHurtByMobTimestamp();
        dragon.getNavigation().stop();
        dragon.setResting(true);
    }

    @Override
    public void stop() {
        if (!dragon.isInSittingPose()) {
            dragon.setResting(false);
        }
    }

    @Override
    public void tick() {
        ticksLeft--;
    }
}
