package com.civilizacionnether.entity.sea;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.WaterAnimal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Medusa del Vacío: flota a la deriva dando impulsos hacia arriba (como un calamar).
 * Si la tocas te pica: un poco de daño y lentitud. Suelta Gel del Vacío (poción de respiración acuática).
 */
public class VoidJellyfishEntity extends WaterAnimal implements GeoEntity {
    private static final String P = "animation.medusa_vacio.";
    private static final RawAnimation SWIM = RawAnimation.begin().thenLoop(P + "swim");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private int pulse;

    public VoidJellyfishEntity(EntityType<? extends VoidJellyfishEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes().add(Attributes.MAX_HEALTH, 8.0);
    }

    @Override
    public boolean isInWater() {
        return super.isInWater() || SeaLife.inNetherWater(this);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide) {
            if (random.nextInt(10) == 0) {
                level().addParticle(ParticleTypes.PORTAL, getRandomX(0.5), getRandomY(), getRandomZ(0.5), 0.0, 0.0, 0.0);
            }
            return;
        }
        if (isInWater() && --pulse <= 0) {
            // impulso: mayormente hacia arriba, con una dirección al azar
            pulse = 40 + random.nextInt(50);
            float yaw = random.nextFloat() * Mth.TWO_PI;
            double up = SeaLife.isWater(level(), blockPosition().above(2)) ? 0.12 : -0.04;
            setDeltaMovement(getDeltaMovement().add(Mth.cos(yaw) * 0.05, up, Mth.sin(yaw) * 0.05));
        }
        if (tickCount % 10 == 0) {
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(0.15),
                    e -> e != this && e.isAlive() && !(e instanceof WaterAnimal))) {
                if (e instanceof Player p && (p.isCreative() || p.isSpectator())) {
                    continue;
                }
                if (e.hurt(damageSources().mobAttack(this), 2.0f)) {
                    e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 1), this);
                    playSound(SoundEvents.SLIME_ATTACK, 0.6f, 1.6f);
                }
            }
        }
    }

    @Override
    public void travel(Vec3 input) {
        if (isControlledByLocalInstance() && isInWater()) {
            move(MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().multiply(0.94, 0.94, 0.94).add(0.0, -0.002, 0.0));
        } else {
            super.travel(input);
        }
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.SLIME_HURT_SMALL;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.SLIME_DEATH_SMALL;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "move", 4, state -> isInWater() ? state.setAndContinue(SWIM) : PlayState.STOP));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
