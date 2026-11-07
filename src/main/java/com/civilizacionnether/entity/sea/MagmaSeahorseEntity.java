package com.civilizacionnether.entity.sea;

import com.civilizacionnether.entity.ai.FollowOwnerSimpleGoal;
import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.navigation.AmphibiousPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.pathfinder.PathType;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Caballito de Magma: mascota del mar. Se domestica dándole Pez Brasa (1 de cada 3 veces) y desde entonces te sigue
 * nadando. Mayús + clic: se queda quieto. Con Pez Brasa se cura y se cría.
 */
public class MagmaSeahorseEntity extends TamableAnimal implements GeoEntity {
    private static final String P = "animation.caballito_magma.";
    private static final RawAnimation SWIM = RawAnimation.begin().thenLoop(P + "swim");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public MagmaSeahorseEntity(EntityType<? extends MagmaSeahorseEntity> type, Level level) {
        super(type, level);
        this.moveControl = new SmoothSwimmingMoveControl(this, 85, 10, 0.1f, 0.5f, false);
        this.lookControl = new SmoothSwimmingLookControl(this, 20);
        setPathfindingMalus(PathType.WATER, 0.0f);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 10.0)
                .add(Attributes.MOVEMENT_SPEED, 1.0)
                .add(Attributes.FOLLOW_RANGE, 16.0);
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new AmphibiousPathNavigation(this, level);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new SitWhenOrderedToGoal(this));
        this.goalSelector.addGoal(2, new FollowOwnerSimpleGoal(this, 1.2, 8.0, 3.0));
        this.goalSelector.addGoal(3, new BreedGoal(this, 1.0));
        this.goalSelector.addGoal(4, new TemptGoal(this, 1.1, Ingredient.of(ModItems.PEZ_BRASA.get()), false));
        this.goalSelector.addGoal(5, new RandomSwimmingGoal(this, 1.0, 40));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 6.0f));
    }

    @Override
    public boolean isInWater() {
        return super.isInWater() || SeaLife.inNetherWater(this);
    }

    @Override
    public boolean isPushedByFluid() {
        return false;
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
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide && random.nextInt(20) == 0) {
            level().addParticle(isInWater() ? ParticleTypes.BUBBLE : ParticleTypes.SMALL_FLAME,
                    getRandomX(0.3), getRandomY(), getRandomZ(0.3), 0.0, 0.02, 0.0);
        }
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return stack.is(ModItems.PEZ_BRASA.get());
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        boolean client = level().isClientSide;
        if (!isTame() && isFood(stack)) {
            if (!client) {
                stack.consume(1, player);
                if (random.nextInt(3) == 0) {
                    tame(player);
                    getNavigation().stop();
                    setOrderedToSit(false);
                    level().broadcastEntityEvent(this, (byte) 7);
                    triggerAnim("action", "happy");
                    player.displayClientMessage(Component.translatable("msg.civilizacion_nether.seahorse_tamed"), true);
                } else {
                    level().broadcastEntityEvent(this, (byte) 6);
                }
            }
            return InteractionResult.sidedSuccess(client);
        }
        if (isTame() && isOwnedBy(player)) {
            if (isFood(stack) && getHealth() < getMaxHealth()) {
                if (!client) {
                    stack.consume(1, player);
                    heal(4.0f);
                    triggerAnim("action", "happy");
                }
                return InteractionResult.sidedSuccess(client);
            }
            if (player.isSecondaryUseActive() && !isFood(stack)) {
                if (!client) {
                    boolean sit = !isOrderedToSit();
                    setOrderedToSit(sit);
                    setInSittingPose(sit);
                    getNavigation().stop();
                    player.displayClientMessage(Component.translatable(
                            sit ? "msg.civilizacion_nether.sit" : "msg.civilizacion_nether.follow", getDisplayName()), true);
                }
                return InteractionResult.sidedSuccess(client);
            }
        }
        return super.mobInteract(player, hand);
    }

    @Nullable
    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob otherParent) {
        MagmaSeahorseEntity baby = ModEntities.CABALLITO_MAGMA.get().create(level);
        if (baby != null && getOwnerUUID() != null) {
            baby.setOwnerUUID(getOwnerUUID());
            baby.setTame(true, true);
        }
        return baby;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return !isTame();
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isInWater() ? SoundEvents.AXOLOTL_IDLE_WATER : SoundEvents.AXOLOTL_IDLE_AIR;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.AXOLOTL_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.AXOLOTL_DEATH;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "move", 4, state -> state.setAndContinue(SWIM)));
        controllers.add(new AnimationController<>(this, "action", 2, state -> PlayState.STOP)
                .triggerableAnim("happy", RawAnimation.begin().thenPlay(P + "happy")));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
