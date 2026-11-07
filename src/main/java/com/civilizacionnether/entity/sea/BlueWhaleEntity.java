package com.civilizacionnether.entity.sea;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.animal.WaterAnimal;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.EnumSet;

/**
 * Ballena Azul del Nether: enorme y pacífica (nunca ataca). Nada lento por el mar, cada uno o dos minutos sube a
 * respirar (sopla un chorro de agua), a veces salta fuera del agua y después se sumerge. Si la golpean, nada más rápido.
 * Suelta peces y a veces un Corazón del Mar.
 */
public class BlueWhaleEntity extends WaterAnimal implements GeoEntity {
    private static final String P = "animation.ballena_azul.";
    private static final RawAnimation SWIM = RawAnimation.begin().thenLoop(P + "swim");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    /** Tiempo hasta la próxima subida a respirar. */
    private int breathTimer;
    private int fleeTicks;

    public BlueWhaleEntity(EntityType<? extends BlueWhaleEntity> type, Level level) {
        super(type, level);
        this.moveControl = new SteerSwimMoveControl(this, 25.0f, 2.5f, 0.05f);
        this.lookControl = new SmoothSwimmingLookControl(this, 6);
        this.breathTimer = 400 + level.getRandom().nextInt(1200);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 200.0)
                .add(Attributes.ARMOR, 4.0)
                .add(Attributes.MOVEMENT_SPEED, 0.7)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new BreathGoal());
        this.goalSelector.addGoal(3, new BigSwimGoal(this, 1.0, 28, 30) {
            @Override
            public boolean canUse() {
                return breathTimer > 0 && super.canUse();
            }
        });
    }

    @Override
    public boolean isInWater() {
        return super.isInWater() || SeaLife.inNetherWater(this);
    }

    @Override
    public void travel(Vec3 input) {
        if (isControlledByLocalInstance() && isInWater()) {
            moveRelative(getSpeed() * (fleeTicks > 0 ? 1.8f : 1.0f), input);
            move(MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(0.92));
        } else {
            super.travel(input);
        }
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        if (breathTimer > 0) {
            breathTimer--;
        }
        if (fleeTicks > 0) {
            fleeTicks--;
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        boolean hit = super.hurt(source, amount);
        if (hit && !level().isClientSide) {
            fleeTicks = 200;
        }
        return hit;
    }

    /** Las ballenas respiran aire: fuera del agua aguantan bastante, pero no para siempre. */
    @Override
    protected void handleAirSupply(int airSupply) {
        if (isAlive() && !isInWaterOrBubble()) {
            setAirSupply(airSupply - 1);
            if (getAirSupply() == -20) {
                setAirSupply(0);
                hurt(damageSources().dryOut(), 2.0f);
            }
        } else {
            setAirSupply(1200);
        }
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return distance > 160.0 * 160.0;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("BreathTimer", breathTimer);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        breathTimer = tag.getInt("BreathTimer");
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
    public float getVoicePitch() {
        return 0.35f + random.nextFloat() * 0.1f;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 500;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "move", 10, state -> state.setAndContinue(SWIM)));
        controllers.add(new AnimationController<>(this, "action", 6, state -> PlayState.STOP)
                .triggerableAnim("blow", RawAnimation.begin().thenPlay(P + "blow"))
                .triggerableAnim("breach", RawAnimation.begin().thenPlay(P + "breach"))
                .triggerableAnim("dive", RawAnimation.begin().thenPlay(P + "dive")));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    /** Subir a respirar: nada hasta la superficie, sopla, a veces salta, y vuelve a sumergirse. */
    private class BreathGoal extends Goal {
        private int surfaceY;
        private int phase;
        private int ticks;

        BreathGoal() {
            setFlags(EnumSet.of(Flag.MOVE));
        }

        @Override
        public boolean canUse() {
            return breathTimer <= 0 && isInWater();
        }

        @Override
        public void start() {
            surfaceY = SeaLife.surfaceAbove(level(), blockPosition());
            phase = 0;
            ticks = 0;
        }

        @Override
        public boolean canContinueToUse() {
            return phase < 3 && ticks < 600;
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            ticks++;
            Vec3 ahead = Vec3.directionFromRotation(0.0f, getYRot()).scale(8.0);
            if (phase == 0) {
                // subir: el lomo justo bajo la superficie
                getMoveControl().setWantedPosition(getX() + ahead.x, surfaceY - getBbHeight() * 0.55, getZ() + ahead.z, 1.0);
                if (getY() + getBbHeight() * 0.6 >= surfaceY - 0.6 || ticks > 400) {
                    blow();
                    phase = 1;
                    ticks = 0;
                }
            } else if (phase == 1) {
                getMoveControl().setWantedPosition(getX() + ahead.x, surfaceY - getBbHeight() * 0.55, getZ() + ahead.z, 0.6);
                if (ticks == 30 && random.nextInt(3) == 0) {
                    breach(ahead.normalize());
                }
                if (ticks > 70) {
                    triggerAnim("action", "dive");
                    phase = 2;
                    ticks = 0;
                }
            } else {
                BlockPos deep = BlockPos.containing(getX() + ahead.x * 2, surfaceY - 10, getZ() + ahead.z * 2);
                getMoveControl().setWantedPosition(deep.getX() + 0.5, deep.getY(), deep.getZ() + 0.5, 1.0);
                if (ticks > 60) {
                    phase = 3;
                }
            }
        }

        @Override
        public void stop() {
            breathTimer = 1200 + random.nextInt(1200);
        }

        private void blow() {
            triggerAnim("action", "blow");
            playSound(SoundEvents.PLAYER_SPLASH_HIGH_SPEED, 2.0f, 0.5f);
            if (level() instanceof ServerLevel server) {
                Vec3 head = position().add(Vec3.directionFromRotation(0.0f, getYRot()).scale(3.0));
                for (int i = 0; i < 6; i++) {
                    server.sendParticles(ParticleTypes.SPLASH, head.x, surfaceY + 0.5 + i * 0.6, head.z, 30, 0.25, 0.3, 0.25, 0.2);
                }
                server.sendParticles(ParticleTypes.CLOUD, head.x, surfaceY + 3.5, head.z, 12, 0.4, 0.4, 0.4, 0.02);
                server.sendParticles(ParticleTypes.BUBBLE_COLUMN_UP, head.x, surfaceY - 0.5, head.z, 20, 0.5, 0.3, 0.5, 0.1);
            }
        }

        private void breach(Vec3 forward) {
            triggerAnim("action", "breach");
            setDeltaMovement(forward.x * 0.5, 1.05, forward.z * 0.5);
            hurtMarked = true;
            playSound(SoundEvents.GENERIC_SPLASH, 3.0f, 0.4f);
            if (level() instanceof ServerLevel server) {
                server.sendParticles(ParticleTypes.SPLASH, getX(), surfaceY + 0.2, getZ(), 120, 3.0, 0.3, 3.0, 0.4);
            }
            setXRot(Mth.clamp(getXRot() - 30.0f, -60.0f, 60.0f));
        }
    }
}
