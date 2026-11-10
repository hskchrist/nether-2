package com.civilizacionnether.entity;

import com.civilizacionnether.registry.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.FollowParentGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RunAroundLikeCrazyGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Caballo del Nether (modelo y skin del usuario). Se doma montándolo como un caballo normal, se ensilla, se cría con
 * zanahorias o manzanas de oro, y come hongos carmesí y distorsionados. No le hace daño el fuego ni la lava, y nada en
 * la lava. Aparece solo o con su potrillo. Los guerreros, ballesteros y arqueros del Nether lo montan y lo manejan
 * (y pelean o disparan desde arriba).
 */
public class NetherHorseEntity extends AbstractHorse implements GeoEntity {
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    /** Jinete que hay que subirle (huevos de jinete y el Reino): "guerrero", "ballestero" o "arquero". */
    private String rider = "";

    public NetherHorseEntity(EntityType<? extends AbstractHorse> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return AbstractHorse.createBaseHorseAttributes()
                .add(Attributes.MAX_HEALTH, 34.0)
                .add(Attributes.MOVEMENT_SPEED, 0.29)
                .add(Attributes.JUMP_STRENGTH, 0.85)
                .add(Attributes.ARMOR, 3.0)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new PanicGoal(this, 1.2) {
            @Override
            public boolean canUse() {
                return !isVehicle() && super.canUse(); // con jinete, manda el jinete
            }
        });
        this.goalSelector.addGoal(1, new RunAroundLikeCrazyGoal(this, 1.2));
        this.goalSelector.addGoal(2, new BreedGoal(this, 1.0, AbstractHorse.class));
        this.goalSelector.addGoal(4, new FollowParentGoal(this, 1.0));
        this.goalSelector.addGoal(5, new TemptGoal(this, 1.25, Ingredient.of(Items.GOLDEN_CARROT, Items.GOLDEN_APPLE,
                Items.CRIMSON_FUNGUS, Items.WARPED_FUNGUS), false));
        this.goalSelector.addGoal(6, new WaterAvoidingRandomStrollGoal(this, 0.7) {
            @Override
            public boolean canUse() {
                return !isVehicle() && super.canUse();
            }
        });
        this.goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 6.0f));
        this.goalSelector.addGoal(8, new RandomLookAroundGoal(this));
    }

    @Override
    protected void randomizeAttributes(RandomSource random) {
        getAttribute(Attributes.MAX_HEALTH).setBaseValue(30.0 + random.nextInt(9));
        getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(0.27 + random.nextDouble() * 0.05);
        getAttribute(Attributes.JUMP_STRENGTH).setBaseValue(0.75 + random.nextDouble() * 0.2);
    }

    /** Come lo de los caballos y también hongos del Nether. */
    @Override
    public boolean isFood(ItemStack stack) {
        return super.isFood(stack) || stack.is(Items.CRIMSON_FUNGUS) || stack.is(Items.WARPED_FUNGUS);
    }

    @Override
    protected boolean handleEating(Player player, ItemStack stack) {
        if (stack.is(Items.CRIMSON_FUNGUS) || stack.is(Items.WARPED_FUNGUS)) {
            boolean used = false;
            if (getHealth() < getMaxHealth()) {
                heal(4.0f);
                used = true;
            }
            if (!isTamed() && getTemper() < getMaxTemper()) {
                modifyTemper(5);
                used = true;
            }
            if (isBaby()) {
                ageUp(30);
                used = true;
            }
            if (used) {
                playSound(net.minecraft.sounds.SoundEvents.HORSE_EAT, 1.0f, 1.0f);
                gameEvent(net.minecraft.world.level.gameevent.GameEvent.EAT);
            }
            return used;
        }
        return super.handleEating(player, stack);
    }

    /** Quién lo maneja: el jugador si está ensillado, o el humano del Nether que lo monte. */
    @Nullable
    @Override
    public LivingEntity getControllingPassenger() {
        Entity first = getFirstPassenger();
        if (first instanceof NetherHumanoidEntity human) {
            return human;
        }
        return super.getControllingPassenger();
    }

    /** Nada en la lava (no le hace daño). */
    @Override
    public void travel(Vec3 input) {
        if (isInLava() && getControllingPassenger() == null && LavaSwim.travel(this, input)) {
            return;
        }
        super.travel(input);
    }

    @Nullable
    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {
        NetherHorseEntity foal = ModEntities.CABALLO_NETHER.get().create(level);
        if (foal != null && partner instanceof AbstractHorse other) {
            setOffspringAttributes(other, foal);
        }
        return foal;
    }

    @Override
    public boolean canMate(net.minecraft.world.entity.animal.Animal other) {
        return other instanceof NetherHorseEntity && other != this && canParent() && ((NetherHorseEntity) other).canParent();
    }

    // ------------------------------------------------------------------ aparecer (solo, con potrillo o con jinete)
    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        @Nullable SpawnGroupData data) {
        SpawnGroupData out = super.finalizeSpawn(level, difficulty, reason, data);
        if ((reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION) && !isBaby()
                && random.nextFloat() < 0.4f) {
            NetherHorseEntity foal = ModEntities.CABALLO_NETHER.get().create(level.getLevel());
            if (foal != null) {
                foal.moveTo(getX() + 1.5, getY(), getZ() + 1.0, random.nextFloat() * 360.0f, 0.0f);
                foal.setAge(-24000);
                level.addFreshEntity(foal);
            }
        }
        return out;
    }

    public void setRider(String kind) {
        this.rider = kind == null ? "" : kind;
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide && !rider.isEmpty() && tickCount > 1) {
            mountRider();
        }
    }

    /** Sube al jinete (lo crea, le pone su equipo y lo monta), y deja el caballo domado y ensillado. */
    private void mountRider() {
        String kind = rider;
        rider = "";
        if (isVehicle() || isBaby() || !(level() instanceof ServerLevel server)) {
            return;
        }
        EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath("civilizacion_nether", kind));
        Entity e = type.create(server);
        if (!(e instanceof NetherHumanoidEntity human)) {
            return;
        }
        human.moveTo(getX(), getY(), getZ(), getYRot(), 0.0f);
        human.finalizeSpawn(server, server.getCurrentDifficultyAt(blockPosition()), MobSpawnType.EVENT, null);
        if (isPersistenceRequired()) {
            human.setPersistenceRequired();
        }
        setTamed(true);
        if (!isSaddled()) {
            equipSaddle(new ItemStack(Items.SADDLE), null);
        }
        server.addFreshEntity(human);
        human.startRiding(this, true);
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (!rider.isEmpty()) {
            tag.putString("Jinete", rider);
        }
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        rider = tag.getString("Jinete");
    }

    public static boolean canSpawn(EntityType<NetherHorseEntity> type, ServerLevelAccessor level, MobSpawnType reason, BlockPos pos,
                                   RandomSource random) {
        BlockPos below = pos.below();
        return level.getBlockState(below).isValidSpawn(level, below, type) && !level.getBlockState(below).liquid()
                && level.getBlockState(pos).isAir();
    }

    // ------------------------------------------------------------------ animaciones
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.caballo_nether.idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.caballo_nether.walk");
    private static final RawAnimation RUN = RawAnimation.begin().thenLoop("animation.caballo_nether.run");
    private static final RawAnimation EAT = RawAnimation.begin().thenLoop("animation.caballo_nether.eat");
    private static final RawAnimation REAR = RawAnimation.begin().thenLoop("animation.caballo_nether.rear");

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 4, state -> {
            if (isStanding()) {
                return state.setAndContinue(REAR);
            }
            if (state.isMoving()) {
                boolean fast = getDeltaMovement().horizontalDistanceSqr() > 0.03 || (isVehicle() && getDeltaMovement().horizontalDistanceSqr() > 0.02);
                return state.setAndContinue(fast ? RUN : WALK);
            }
            if (isEating()) {
                return state.setAndContinue(EAT);
            }
            return state.setAndContinue(IDLE);
        }));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
