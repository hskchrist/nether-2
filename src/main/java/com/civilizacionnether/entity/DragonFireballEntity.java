package com.civilizacionnether.entity;

import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModParticles;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Bola de fuego negro del Dragón del Nether: vuela recta, deja estela de llamas negras y almas rojas, quema y daña al impactar.
 * No rompe bloques ni prende fuego al terreno, y nunca daña a jugadores ni aliados.
 */
public class DragonFireballEntity extends Projectile {
    private float damage = 8.0f;
    private int life;

    public DragonFireballEntity(EntityType<? extends DragonFireballEntity> type, Level level) {
        super(type, level);
        setNoGravity(true);
    }

    public static void shoot(LivingEntity shooter, Vec3 from, Vec3 direction, float damage) {
        DragonFireballEntity ball = ModEntities.DRAGON_FIREBALL.get().create(shooter.level());
        if (ball == null) {
            return;
        }
        ball.setOwner(shooter);
        ball.damage = damage;
        ball.moveTo(from.x, from.y, from.z, shooter.getYRot(), shooter.getXRot());
        Vec3 dir = direction.normalize();
        ball.shoot(dir.x, dir.y, dir.z, 2.2f, 0.5f);
        shooter.level().addFreshEntity(ball);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
    }

    @Override
    public void tick() {
        super.tick();
        HitResult hit = ProjectileUtil.getHitResultOnMoveVector(this, this::canHitEntity);
        if (hit.getType() != HitResult.Type.MISS) {
            onHit(hit);
            if (isRemoved()) {
                return;
            }
        }
        Vec3 v = getDeltaMovement();
        setPos(getX() + v.x, getY() + v.y, getZ() + v.z);
        ProjectileUtil.rotateTowardsMovement(this, 0.2f);
        if (level().isClientSide) {
            for (int i = 0; i < 3; i++) {
                level().addParticle(ModParticles.BLACK_FLAME.get(),
                        getX() - v.x * i * 0.3 + (random.nextDouble() - 0.5) * 0.4,
                        getY() + 0.2 - v.y * i * 0.3 + (random.nextDouble() - 0.5) * 0.4,
                        getZ() - v.z * i * 0.3 + (random.nextDouble() - 0.5) * 0.4, 0, 0, 0);
            }
            if (random.nextInt(3) == 0) {
                level().addParticle(ModParticles.RED_SOUL.get(), getX(), getY() + 0.2, getZ(), 0, 0, 0);
            }
            level().addParticle(ParticleTypes.SMOKE, getX(), getY() + 0.2, getZ(), 0, 0, 0);
        } else if (++life > 80 || isInWater()) {
            if (isInWater()) {
                playSound(SoundEvents.FIRE_EXTINGUISH, 0.6f, 1.2f);
            }
            discard();
        }
    }

    @Override
    protected boolean canHitEntity(Entity target) {
        if (!super.canHitEntity(target)) {
            return false;
        }
        Entity owner = getOwner();
        if (owner != null && (target == owner || owner.hasPassenger(target) || target.isPassengerOfSameVehicle(owner))) {
            return false;
        }
        return !(target instanceof LivingEntity living && NetherHumanoidEntity.isAlly(living));
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        if (level().isClientSide) {
            return;
        }
        Entity target = result.getEntity();
        Entity owner = getOwner();
        target.hurt(damageSources().mobProjectile(this, owner instanceof LivingEntity living ? living : null), damage);
        target.setRemainingFireTicks(100);
    }

    @Override
    protected void onHit(HitResult result) {
        super.onHit(result);
        if (!level().isClientSide && level() instanceof ServerLevel server) {
            server.sendParticles(ModParticles.BLACK_FLAME.get(), getX(), getY(), getZ(), 24, 0.4, 0.4, 0.4, 0.06);
            server.sendParticles(ModParticles.RED_SOUL.get(), getX(), getY(), getZ(), 6, 0.3, 0.3, 0.3, 0.02);
            playSound(SoundEvents.FIRECHARGE_USE, 0.8f, 0.7f);
            discard();
        }
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putFloat("Damage", damage);
        tag.putInt("Life", life);
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        damage = tag.getFloat("Damage");
        life = tag.getInt("Life");
    }
}
