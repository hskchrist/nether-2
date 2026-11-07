package com.civilizacionnether.entity.sea;

import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.MoveControl;

/**
 * Nado dirigido para las criaturas grandes (ballena y serpiente): va directo al punto pedido, girando de a poco
 * y subiendo o bajando el morro, sin necesitar un camino (los caminos fallan con cuerpos tan grandes).
 */
public class SteerSwimMoveControl extends MoveControl {
    private final float maxPitch;
    private final float maxTurn;
    private final float waterSpeed;

    public SteerSwimMoveControl(Mob mob, float maxPitch, float maxTurn, float waterSpeed) {
        super(mob);
        this.maxPitch = maxPitch;
        this.maxTurn = maxTurn;
        this.waterSpeed = waterSpeed;
    }

    @Override
    public void tick() {
        if (operation != Operation.MOVE_TO) {
            mob.setSpeed(0.0f);
            mob.setZza(0.0f);
            mob.setYya(0.0f);
            mob.setXRot(rotlerp(mob.getXRot(), 0.0f, 2.0f));
            return;
        }
        double dx = wantedX - mob.getX();
        double dy = wantedY - mob.getY();
        double dz = wantedZ - mob.getZ();
        double dist2 = dx * dx + dy * dy + dz * dz;
        if (dist2 < 2.0) {
            operation = Operation.WAIT;
            mob.setZza(0.0f);
            mob.setYya(0.0f);
            return;
        }
        float yaw = (float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90.0f;
        mob.setYRot(rotlerp(mob.getYRot(), yaw, maxTurn));
        mob.yBodyRot = mob.getYRot();
        mob.yHeadRot = mob.getYRot();
        float speed = (float) (speedModifier * mob.getAttributeValue(Attributes.MOVEMENT_SPEED));
        if (mob.isInWater()) {
            mob.setSpeed(speed * waterSpeed);
            double horizontal = Math.sqrt(dx * dx + dz * dz);
            float pitch = -(float) (Mth.atan2(dy, horizontal) * Mth.RAD_TO_DEG);
            pitch = Mth.clamp(Mth.wrapDegrees(pitch), -maxPitch, maxPitch);
            mob.setXRot(rotlerp(mob.getXRot(), pitch, 3.0f));
            float cos = Mth.cos(mob.getXRot() * Mth.DEG_TO_RAD);
            float sin = Mth.sin(mob.getXRot() * Mth.DEG_TO_RAD);
            mob.zza = cos * speed;
            mob.yya = -sin * speed;
        } else {
            mob.setSpeed(speed * 0.05f);
            mob.zza = 0.0f;
            mob.yya = 0.0f;
        }
    }
}
