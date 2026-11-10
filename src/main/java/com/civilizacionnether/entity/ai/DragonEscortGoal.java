package com.civilizacionnether.entity.ai;

import com.civilizacionnether.entity.NetherDragonEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/**
 * Dragón que sigue a su dueño VOLANDO (modo "seguir" del Báculo, ni libre ni sentado):
 * <ul>
 *   <li>Si el dueño vuela (montando un dragón o con élitros), el dragón despega y lo escolta en el aire, a un costado.</li>
 *   <li>Si el dueño está lejos (más de 20 bloques) o a otra altura, llega volando y aterriza a su lado.</li>
 *   <li>Sólo se teletransporta si no puede llegar volando (es cría, o está demasiado lejos, o se quedó trabado).</li>
 * </ul>
 */
public class DragonEscortGoal extends Goal {
    private final NetherDragonEntity dragon;
    private LivingEntity owner;
    private int repick;
    private int stuck;
    private Vec3 last;

    public DragonEscortGoal(NetherDragonEntity dragon) {
        this.dragon = dragon;
        setFlags(EnumSet.of(Flag.MOVE, Flag.JUMP));
    }

    /** ¿El dueño va volando? */
    public static boolean ownerFlies(LivingEntity owner) {
        if (owner.getVehicle() instanceof NetherDragonEntity mount) {
            return mount.isFlying() || !mount.onGround();
        }
        return owner.isFallFlying();
    }

    private boolean followMode() {
        return dragon.isTame() && !dragon.isFree() && !dragon.isOrderedToSit() && !dragon.isVehicle() && !dragon.isPassenger()
                && !dragon.isLeashed() && dragon.getTarget() == null && !dragon.hasRecall();
    }

    @Override
    public boolean canUse() {
        if (!followMode() || !dragon.canFlyNow()) {
            return false;
        }
        LivingEntity o = dragon.getOwner();
        if (o == null || o.level() != dragon.level() || o.isSpectator() || o.getVehicle() == dragon) {
            return false;
        }
        double d = dragon.distanceTo(o);
        if (ownerFlies(o)) {
            owner = o;
            return d > 5.0;
        }
        if (d > 20.0 || (d > 8.0 && Math.abs(o.getY() - dragon.getY()) > 6.0)) {
            owner = o;
            return true;
        }
        return false;
    }

    @Override
    public boolean canContinueToUse() {
        if (owner == null || !owner.isAlive() || owner.level() != dragon.level() || !followMode()) {
            return false;
        }
        if (ownerFlies(owner)) {
            return true;
        }
        // el dueño está en el suelo: sigue hasta llegar a su lado
        return dragon.distanceTo(owner) > 6.0 + dragon.getBbWidth();
    }

    @Override
    public void start() {
        repick = 0;
        stuck = 0;
        last = null;
        dragon.setResting(false);
        dragon.setFlightGoalRunning(true);
        dragon.getNavigation().stop();
        dragon.takeOff();
    }

    @Override
    public void stop() {
        dragon.setFlightGoalRunning(false);
        if (dragon.isFlying() && owner != null && !ownerFlies(owner)) {
            dragon.land(); // llegó: aterriza al lado del dueño
        }
        owner = null;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        if (owner == null) {
            return;
        }
        double dist = dragon.distanceTo(owner);
        // imposible llegar volando: muy lejos
        if (dist > 160.0 || stuck >= 8) {
            teleportNear();
            return;
        }
        if (!dragon.isFlying()) {
            dragon.takeOff();
        }
        if (--repick > 0) {
            return;
        }
        repick = 4;
        // a un costado del dueño (cada dragón en su lugar para que no choquen)
        int slot = Math.floorMod(dragon.getId(), 6);
        double side = (slot % 2 == 0 ? 1 : -1) * (5.0 + dragon.getBbWidth() + (slot / 2) * 4.0);
        Vec3 look = Vec3.directionFromRotation(0, owner.getYRot());
        Vec3 right = new Vec3(-look.z, 0, look.x);
        Vec3 spot;
        if (ownerFlies(owner)) {
            spot = owner.position().add(right.scale(side)).add(look.scale(-3.0 - (slot / 2) * 3.0)).add(0, 1.0 + slot % 3, 0);
        } else {
            Vec3 to = owner.position().subtract(dragon.position()).multiply(1, 0, 1);
            Vec3 dir = to.lengthSqr() < 1.0e-3 ? look : to.normalize();
            spot = owner.position().subtract(dir.scale(4.0 + dragon.getBbWidth())).add(0, dist > 24.0 ? 8.0 : 3.0, 0);
        }
        dragon.setFlyTarget(spot);
        // ¿avanza? (si se traba contra el techo o una pared mucho rato, se teletransporta)
        if (last != null && dist > 24.0 && dragon.position().distanceToSqr(last) < 0.5) {
            stuck++;
        } else {
            stuck = 0;
        }
        last = dragon.position();
    }

    private void teleportNear() {
        stuck = 0;
        for (int i = 0; i < 12; i++) {
            double x = owner.getX() + dragon.getRandom().nextInt(9) - 4;
            double y = owner.getY() + (ownerFlies(owner) ? 2 : 0);
            double z = owner.getZ() + dragon.getRandom().nextInt(9) - 4;
            Vec3 old = dragon.position();
            dragon.moveTo(x, y, z, dragon.getYRot(), dragon.getXRot());
            if (dragon.level().noCollision(dragon)) {
                dragon.getNavigation().stop();
                return;
            }
            dragon.moveTo(old.x, old.y, old.z, dragon.getYRot(), dragon.getXRot());
        }
    }
}
