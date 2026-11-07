package com.civilizacionnether.entity.sea;

import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.navigation.AmphibiousPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
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
 * Tortuga Obsidiana: tranquila, nada y camina por el fondo y la orilla; al recibir un golpe se esconde en el caparazón.
 * Se cría con Pez Brasa. Suelta Escamas Obsidiana (con 5 se hace el Casco de Tortuga Obsidiana).
 */
public class ObsidianTurtleEntity extends Animal implements GeoEntity {
    private static final String P = "animation.tortuga_obsidiana.";
    private static final RawAnimation SWIM = RawAnimation.begin().thenLoop(P + "swim");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop(P + "walk");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public ObsidianTurtleEntity(EntityType<? extends ObsidianTurtleEntity> type, Level level) {
        super(type, level);
        this.moveControl = new SmoothSwimmingMoveControl(this, 85, 10, 0.06f, 0.6f, false);
        this.lookControl = new SmoothSwimmingLookControl(this, 20);
        setPathfindingMalus(PathType.WATER, 0.0f);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 30.0)
                .add(Attributes.ARMOR, 10.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.5)
                .add(Attributes.MOVEMENT_SPEED, 0.25);
    }

    @Override
    protected PathNavigation createNavigation(Level level) {
        return new AmphibiousPathNavigation(this, level);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new BreedGoal(this, 1.0));
        this.goalSelector.addGoal(2, new TemptGoal(this, 1.1, Ingredient.of(ModItems.PEZ_BRASA.get()), false));
        this.goalSelector.addGoal(4, new RandomSwimmingGoal(this, 1.0, 60));
        this.goalSelector.addGoal(5, new RandomStrollGoal(this, 1.0, 100));
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
    public float getWalkTargetValue(net.minecraft.core.BlockPos pos, LevelReader level) {
        return 0.0f;
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
    public boolean hurt(DamageSource source, float amount) {
        boolean hit = super.hurt(source, amount);
        if (hit && !level().isClientSide && isAlive()) {
            triggerAnim("action", "hide");
        }
        return hit;
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return stack.is(ModItems.PEZ_BRASA.get());
    }

    @Nullable
    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob otherParent) {
        return ModEntities.TORTUGA_OBSIDIANA.get().create(level);
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return isInWater() ? SoundEvents.TURTLE_AMBIENT_LAND : null;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.TURTLE_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.TURTLE_DEATH;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "move", 4, state -> {
            if (isInWater()) {
                return state.setAndContinue(SWIM);
            }
            return state.isMoving() ? state.setAndContinue(WALK) : PlayState.STOP;
        }));
        controllers.add(new AnimationController<>(this, "action", 2, state -> PlayState.STOP)
                .triggerableAnim("hide", RawAnimation.begin().thenPlay(P + "hide")));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
