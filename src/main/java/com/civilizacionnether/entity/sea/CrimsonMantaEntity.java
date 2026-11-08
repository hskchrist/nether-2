package com.civilizacionnether.entity.sea;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WaterBoundPathNavigation;
import net.minecraft.world.entity.animal.WaterAnimal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Manta Carmesí: con una silla se monta y nada muy rápido hacia donde miras (W avanza, arriba/abajo con la mirada).
 * Mientras la montas puedes respirar bajo el agua.
 */
public class CrimsonMantaEntity extends WaterAnimal implements GeoEntity {
    private static final EntityDataAccessor<Boolean> SADDLED = SynchedEntityData.defineId(CrimsonMantaEntity.class, EntityDataSerializers.BOOLEAN);
    private static final String P = "animation.manta_carmesi.";
    private static final RawAnimation SWIM = RawAnimation.begin().thenLoop(P + "swim");
    private static final RawAnimation GLIDE = RawAnimation.begin().thenLoop(P + "glide");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public CrimsonMantaEntity(EntityType<? extends CrimsonMantaEntity> type, Level level) {
        super(type, level);
        this.moveControl = new SmoothSwimmingMoveControl(this, 85, 10, 0.02f, 0.1f, true);
        this.lookControl = new SmoothSwimmingLookControl(this, 10);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 30.0)
                .add(Attributes.MOVEMENT_SPEED, 1.3)
                .add(Attributes.FOLLOW_RANGE, 16.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(SADDLED, false);
    }

    public boolean isSaddled() {
        return entityData.get(SADDLED);
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new WaterBoundPathNavigation(this, level);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(4, new RandomSwimmingGoal(this, 1.0, 10) {
            @Override
            public boolean canUse() {
                return !isVehicle() && super.canUse();
            }
        });
    }

    @Override
    public boolean isInWater() {
        return super.isInWater() || SeaLife.inNetherWater(this) || isInLava();
    }

    // ------------------------------------------------------------------ montar
    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        boolean client = level().isClientSide;
        if (stack.is(Items.SADDLE) && !isSaddled()) {
            if (!client) {
                stack.consume(1, player);
                entityData.set(SADDLED, true);
                level().playSound(null, getX(), getY(), getZ(), SoundEvents.HORSE_SADDLE, SoundSource.NEUTRAL, 1.0f, 1.0f);
            }
            return InteractionResult.sidedSuccess(client);
        }
        if (!isSaddled()) {
            if (!client) {
                player.displayClientMessage(Component.translatable("msg.civilizacion_nether.manta_saddle"), true);
            }
            return InteractionResult.sidedSuccess(client);
        }
        if (!isVehicle() && !player.isSecondaryUseActive()) {
            if (!client) {
                player.setYRot(getYRot());
                player.setXRot(getXRot());
                player.startRiding(this);
            }
            return InteractionResult.sidedSuccess(client);
        }
        return super.mobInteract(player, hand);
    }

    @Nullable
    @Override
    public LivingEntity getControllingPassenger() {
        if (isSaddled() && getFirstPassenger() instanceof Player player) {
            return player;
        }
        return null;
    }

    @Override
    protected void tickRidden(Player player, Vec3 input) {
        super.tickRidden(player, input);
        setYRot(player.getYRot());
        yRotO = getYRot();
        setXRot(player.getXRot() * 0.6f);
        setRot(getYRot(), getXRot());
        yBodyRot = getYRot();
        yHeadRot = getYRot();
    }

    @Override
    protected Vec3 getRiddenInput(Player player, Vec3 input) {
        float forward = player.zza;
        if (forward < 0.0f) {
            forward *= 0.3f;
        }
        return new Vec3(player.xxa * 0.4f, 0.0, forward);
    }

    @Override
    protected float getRiddenSpeed(Player player) {
        return (float) getAttributeValue(Attributes.MOVEMENT_SPEED);
    }

    @Override
    public void travel(Vec3 input) {
        if (isControlledByLocalInstance() && isInWater()) {
            if (getControllingPassenger() instanceof Player rider) {
                double speed = getAttributeValue(Attributes.MOVEMENT_SPEED) * 0.045;
                Vec3 look = rider.getLookAngle();
                Vec3 motion = getDeltaMovement().scale(0.9);
                if (input.z != 0) {
                    motion = motion.add(look.scale(speed * input.z));
                }
                if (input.x != 0) {
                    Vec3 right = new Vec3(-look.z, 0, look.x).normalize();
                    motion = motion.add(right.scale(-input.x * speed * 0.6));
                }
                setDeltaMovement(motion);
                move(MoverType.SELF, getDeltaMovement());
                calculateEntityAnimation(true);
                return;
            }
            moveRelative(getSpeed(), input);
            move(MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(0.9));
            if (getTarget() == null) {
                setDeltaMovement(getDeltaMovement().add(0.0, -0.004, 0.0));
            }
        } else {
            super.travel(input);
        }
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide && tickCount % 20 == 0 && getFirstPassenger() instanceof LivingEntity rider) {
            rider.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 60, 0, true, false));
        }
    }

    @Override
    public boolean isPushable() {
        return !isVehicle();
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return !isSaddled() && !isVehicle();
    }

    @Override
    protected void dropCustomDeathLoot(ServerLevel level, DamageSource source, boolean recentlyHit) {
        super.dropCustomDeathLoot(level, source, recentlyHit);
        if (isSaddled()) {
            spawnAtLocation(Items.SADDLE);
        }
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Saddled", isSaddled());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        entityData.set(SADDLED, tag.getBoolean("Saddled"));
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.SQUID_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.SQUID_DEATH;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "move", 6, state ->
                state.setAndContinue(getDeltaMovement().lengthSqr() > 0.004 ? SWIM : GLIDE)));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
