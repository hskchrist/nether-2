package com.civilizacionnether.entity.sea;

import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WaterBoundPathNavigation;
import net.minecraft.world.entity.animal.WaterAnimal;
import net.minecraft.world.entity.monster.Enemy;
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
 * Tiburón Infernal: hostil. Ataca a los jugadores que nadan lejos del Reino y a los Delfines del Nether
 * (y los delfines lo atacan a él). Nunca aparece ni persigue dentro del Reino. Suelta Dientes de Tiburón.
 */
public class InfernalSharkEntity extends WaterAnimal implements GeoEntity, Enemy {
    private static final String P = "animation.tiburon_infernal.";
    private static final RawAnimation SWIM = RawAnimation.begin().thenLoop(P + "swim");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public InfernalSharkEntity(EntityType<? extends InfernalSharkEntity> type, Level level) {
        super(type, level);
        this.moveControl = new SmoothSwimmingMoveControl(this, 85, 10, 0.02f, 0.1f, true);
        this.lookControl = new SmoothSwimmingLookControl(this, 10);
        this.xpReward = 10;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 40.0)
                .add(Attributes.ATTACK_DAMAGE, 7.0)
                .add(Attributes.MOVEMENT_SPEED, 0.9)
                .add(Attributes.FOLLOW_RANGE, 32.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.3);
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new WaterBoundPathNavigation(this, level);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.4, true));
        this.goalSelector.addGoal(4, new RandomSwimmingGoal(this, 1.0, 20));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, 10, true, false, this::isPrey));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, NetherDolphinEntity.class, 10, true, false, null));
    }

    /** Solo persigue a quien nada en el mar abierto, nunca dentro del Reino. */
    private boolean isPrey(LivingEntity e) {
        return e.isInWater() && !SeaLife.insideKingdom(level(), e.blockPosition());
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        LivingEntity target = getTarget();
        if (tickCount % 20 == 0 && target instanceof Player && !isPrey(target) && getLastHurtByMob() != target) {
            setTarget(null);
        }
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
            if (getTarget() == null) {
                setDeltaMovement(getDeltaMovement().add(0.0, -0.005, 0.0));
            }
        } else {
            super.travel(input);
        }
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        triggerAnim("action", "bite");
        playSound(SoundEvents.EVOKER_FANGS_ATTACK, 1.0f, 0.8f);
        return super.doHurtTarget(target);
    }

    @Override
    protected boolean shouldDespawnInPeaceful() {
        return true;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.GUARDIAN_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.GUARDIAN_DEATH;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "move", 4, state -> state.setAndContinue(SWIM)));
        controllers.add(new AnimationController<>(this, "action", 2, state -> PlayState.STOP)
                .triggerableAnim("bite", RawAnimation.begin().thenPlay(P + "bite")));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
