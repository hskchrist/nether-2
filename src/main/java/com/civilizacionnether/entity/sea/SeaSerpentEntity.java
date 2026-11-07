package com.civilizacionnether.entity.sea;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.WaterAnimal;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.EnumSet;

/**
 * Serpiente Marina del Nether: criatura rara del Océano Púrpura (20 de vida, como el esqueleto wither; no es jefe).
 * Muerde fuerte y cada tanto ruge: empuja y debilita a los que estén cerca. Nunca entra a pelear dentro del Reino.
 * Suelta Escamas de Serpiente (para el Casco de la Serpiente) y a veces un Corazón del Mar.
 */
public class SeaSerpentEntity extends WaterAnimal implements GeoEntity, Enemy {
    private static final String P = "animation.serpiente_marina.";
    private static final RawAnimation SWIM = RawAnimation.begin().thenLoop(P + "swim");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private int roarCooldown = 200;

    public SeaSerpentEntity(EntityType<? extends SeaSerpentEntity> type, Level level) {
        super(type, level);
        this.moveControl = new SteerSwimMoveControl(this, 40.0f, 6.0f, 0.035f);
        this.lookControl = new SmoothSwimmingLookControl(this, 10);
        this.xpReward = 10;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 20.0)
                .add(Attributes.ATTACK_DAMAGE, 14.0)
                .add(Attributes.ARMOR, 10.0)
                .add(Attributes.MOVEMENT_SPEED, 1.0)
                .add(Attributes.FOLLOW_RANGE, 40.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new SerpentAttackGoal());
        this.goalSelector.addGoal(4, new BigSwimGoal(this, 0.8, 24, 40));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false,
                e -> !SeaLife.insideKingdom(level(), e.blockPosition())));
    }

    @Override
    public boolean isInWater() {
        return super.isInWater() || SeaLife.inNetherWater(this);
    }

    @Override
    public void travel(Vec3 input) {
        if (isControlledByLocalInstance() && isInWater()) {
            moveRelative(getSpeed(), input);
            move(MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(0.9));
        } else {
            super.travel(input);
        }
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        LivingEntity target = getTarget();
        if (target != null && tickCount % 20 == 0 && target instanceof Player
                && SeaLife.insideKingdom(level(), target.blockPosition()) && getLastHurtByMob() != target) {
            setTarget(null);
        }
        if (roarCooldown > 0) {
            roarCooldown--;
        } else if (target != null && distanceToSqr(target) < 14 * 14) {
            roar();
        }
    }

    /** Rugido: empuja y debilita a todos los que estén a 12 bloques. */
    private void roar() {
        roarCooldown = 220 + random.nextInt(120);
        triggerAnim("action", "roar");
        playSound(SoundEvents.RAVAGER_ROAR, 3.0f, 0.55f);
        playSound(SoundEvents.ELDER_GUARDIAN_CURSE, 1.5f, 0.7f);
        if (level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.BUBBLE_COLUMN_UP, getX(), getY() + 2.0, getZ(), 80, 3.0, 1.5, 3.0, 0.3);
            server.sendParticles(ParticleTypes.SOUL, getX(), getY() + 2.0, getZ(), 20, 2.0, 1.0, 2.0, 0.05);
        }
        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(12.0),
                e -> e != this && e.isAlive() && !(e instanceof WaterAnimal))) {
            if (e instanceof Player p && (p.isCreative() || p.isSpectator())) {
                continue;
            }
            Vec3 push = e.position().subtract(position()).normalize().scale(1.2);
            e.push(push.x, 0.4, push.z);
            e.hurtMarked = true;
            e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 160, 0), this);
            e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 1), this);
        }
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return getTarget() == null;
    }

    @Override
    protected boolean shouldDespawnInPeaceful() {
        return true;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return SoundEvents.ELDER_GUARDIAN_AMBIENT;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.ELDER_GUARDIAN_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.ELDER_GUARDIAN_DEATH;
    }

    @Override
    protected float getSoundVolume() {
        return 3.0f;
    }

    @Override
    public float getVoicePitch() {
        return 0.6f + random.nextFloat() * 0.1f;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "move", 6, state -> state.setAndContinue(SWIM)));
        controllers.add(new AnimationController<>(this, "action", 3, state -> PlayState.STOP)
                .triggerableAnim("roar", RawAnimation.begin().thenPlay(P + "roar")));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    /** Persigue nadando directo hacia el objetivo y muerde al alcanzarlo (la cabeza está muy adelante y arriba). */
    private class SerpentAttackGoal extends Goal {
        private int biteCooldown;

        SerpentAttackGoal() {
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = getTarget();
            return t != null && t.isAlive();
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            LivingEntity t = getTarget();
            if (t == null) {
                return;
            }
            getLookControl().setLookAt(t, 30.0f, 30.0f);
            getMoveControl().setWantedPosition(t.getX(), t.getY(0.5) - 1.0, t.getZ(), 1.25);
            if (biteCooldown > 0) {
                biteCooldown--;
                return;
            }
            double reach = getBbWidth() * 0.5 + t.getBbWidth() * 0.5 + 3.0;
            if (distanceToSqr(t) < reach * reach) {
                biteCooldown = 30;
                playSound(SoundEvents.EVOKER_FANGS_ATTACK, 2.0f, 0.5f);
                doHurtTarget(t);
            }
        }
    }
}
