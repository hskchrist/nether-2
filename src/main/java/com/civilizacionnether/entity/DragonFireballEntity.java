package com.civilizacionnether.entity;

import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModParticles;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
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
    /** Bola de fuego explosiva del Dragón Infernal (otra textura y explota al chocar). */
    private static final EntityDataAccessor<Boolean> EXPLOSIVE = SynchedEntityData.defineId(DragonFireballEntity.class, EntityDataSerializers.BOOLEAN);
    private float damage = 8.0f;
    private float power;
    private boolean griefing;
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

    /** Bola explosiva: si el dragón es salvaje rompe bloques y prende fuego (según la regla mobGriefing); domesticado, no. */
    public static void shootExplosive(LivingEntity shooter, Vec3 from, Vec3 direction, float damage, float power, boolean griefing) {
        DragonFireballEntity ball = ModEntities.DRAGON_FIREBALL.get().create(shooter.level());
        if (ball == null) {
            return;
        }
        ball.setOwner(shooter);
        ball.damage = damage;
        ball.power = power;
        ball.griefing = griefing;
        ball.entityData.set(EXPLOSIVE, true);
        ball.moveTo(from.x, from.y, from.z, shooter.getYRot(), shooter.getXRot());
        Vec3 dir = direction.normalize();
        ball.shoot(dir.x, dir.y, dir.z, 1.8f, 0.6f);
        shooter.level().addFreshEntity(ball);
    }

    public boolean isExplosive() {
        return entityData.get(EXPLOSIVE);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        builder.define(EXPLOSIVE, false);
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
        if (level().isClientSide && isExplosive()) {
            for (int i = 0; i < 3; i++) {
                level().addParticle(ParticleTypes.FLAME,
                        getX() - v.x * i * 0.3 + (random.nextDouble() - 0.5) * 0.4,
                        getY() + 0.2 - v.y * i * 0.3 + (random.nextDouble() - 0.5) * 0.4,
                        getZ() - v.z * i * 0.3 + (random.nextDouble() - 0.5) * 0.4, 0, 0, 0);
            }
            if (random.nextInt(3) == 0) {
                level().addParticle(ParticleTypes.LAVA, getX(), getY() + 0.2, getZ(), 0, 0, 0);
            }
            level().addParticle(ParticleTypes.LARGE_SMOKE, getX(), getY() + 0.2, getZ(), 0, 0, 0);
        } else if (level().isClientSide) {
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
        if (owner instanceof NetherDragonEntity dragon && dragon.isWildHostile()) {
            // el Dragón Infernal salvaje le pega a todos menos a los de su especie y a los huevos
            return !(target instanceof DragonEggEntity) && !(target instanceof NetherDragonEntity other && other.isWildHostile());
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
        if (!level().isClientSide && level() instanceof ServerLevel server && isExplosive()) {
            server.explode(this, getX(), getY(), getZ(), power, griefing,
                    griefing ? Level.ExplosionInteraction.MOB : Level.ExplosionInteraction.NONE);
            discard();
            return;
        }
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
        tag.putBoolean("Explosive", isExplosive());
        tag.putFloat("Power", power);
        tag.putBoolean("Griefing", griefing);
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        damage = tag.getFloat("Damage");
        life = tag.getInt("Life");
        entityData.set(EXPLOSIVE, tag.getBoolean("Explosive"));
        power = tag.getFloat("Power");
        griefing = tag.getBoolean("Griefing");
    }
}
