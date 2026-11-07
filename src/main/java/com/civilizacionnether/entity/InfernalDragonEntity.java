package com.civilizacionnether.entity;

import com.civilizacionnether.entity.ai.DragonCombatGoal;
import com.civilizacionnether.entity.ai.DragonFlyGoal;
import com.civilizacionnether.entity.ai.DragonRecallGoal;
import com.civilizacionnether.entity.ai.DragonRestGoal;
import com.civilizacionnether.entity.ai.FollowOwnerSimpleGoal;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtTargetGoal;
import net.minecraft.world.entity.animal.AbstractGolem;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.Tags;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;

/**
 * Dragón Infernal (modelo del usuario). Todo lo del Dragón del Nether le sirve igual (crecer, silla, armadura, báculo,
 * montar, volar, vínculo, huevos); solo cambian los ataques:
 * <ul>
 *   <li>Bola de fuego explosiva (clic derecho del jinete o de lejos por su cuenta).</li>
 *   <li>Agarre: baja en picada, toma al mob con las patas, lo sube y lo suelta desde lo alto
 *       (por su cuenta, o el jinete con la barra llena + R; R otra vez lo suelta).</li>
 * </ul>
 * El salvaje vive en un nido del Bosque Carmesí con su huevo, y ataca a todos los mobs sin excepción.
 * Si le robas el huevo, la cría que nazca será tuya.
 */
public class InfernalDragonEntity extends NetherDragonEntity {
    private static final EntityDataAccessor<Boolean> CARRYING = SynchedEntityData.defineId(InfernalDragonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final String P = "animation.dragon_infernal.";
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop(P + "idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop(P + "walk");
    private static final RawAnimation RUN = RawAnimation.begin().thenLoop(P + "run");
    private static final RawAnimation REST = RawAnimation.begin().thenLoop(P + "rest");
    private static final RawAnimation FLY = RawAnimation.begin().thenLoop(P + "fly");
    private static final RawAnimation GLIDE = RawAnimation.begin().thenLoop(P + "glide");
    private static final RawAnimation HOVER = RawAnimation.begin().thenLoop(P + "hover");
    private static final RawAnimation CARRY = RawAnimation.begin().thenLoop(P + "carry");
    private static final int NONE = 0;
    private static final int SWOOP = 1;
    private static final int LIFT = 2;
    private static final int RIDER_CARRY = 3;

    @Nullable
    private BlockPos nest;
    @Nullable
    private LivingEntity grabTarget;
    @Nullable
    private LivingEntity carried;
    private int grabPhase = NONE;
    private int grabTicks;
    private int grabCooldown = 100;
    private double liftTopY;

    public InfernalDragonEntity(EntityType<? extends InfernalDragonEntity> entityType, Level level) {
        super(entityType, level);
        this.xpReward = 50;
    }

    public static AttributeSupplier.Builder createInfernalAttributes() {
        return NetherDragonEntity.createAttributes().add(Attributes.ARMOR, 14.0);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(CARRYING, false);
    }

    public boolean isCarrying() {
        return entityData.get(CARRYING);
    }

    @Override
    public boolean isWildHostile() {
        return !isTame();
    }

    @Override
    public boolean isInfernal() {
        return true;
    }

    /** Se monta con la Silla del Dragón Infernal (la silla normal no le sirve). */
    @Override
    protected boolean isSaddleItem(net.minecraft.world.item.ItemStack stack) {
        return stack.is(com.civilizacionnether.registry.ModItems.INFERNAL_SADDLE.get());
    }

    @Override
    protected net.minecraft.world.level.ItemLike saddleItem() {
        return com.civilizacionnether.registry.ModItems.INFERNAL_SADDLE.get();
    }

    @Override
    protected String needSaddleMessage() {
        return "msg.civilizacion_nether.need_infernal_saddle";
    }

    public void setNest(BlockPos pos) {
        this.nest = pos;
        restrictTo(pos, 28);
    }

    // ------------------------------------------------------------------ IA
    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new SitWhenOrderedToGoal(this));
        this.goalSelector.addGoal(1, new DragonRecallGoal(this));
        this.goalSelector.addGoal(2, new DragonCombatGoal(this));
        this.goalSelector.addGoal(3, new BreedGoal(this, 1.0));
        this.goalSelector.addGoal(4, new FollowOwnerSimpleGoal(this, 1.1, 16.0, 6.0) {
            @Override
            public boolean canUse() {
                return !isFree() && super.canUse();
            }
        });
        this.goalSelector.addGoal(5, new DragonFlyGoal(this));
        this.goalSelector.addGoal(6, new DragonRestGoal(this));
        this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.6, 160));
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 12.0f));
        this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));

        this.targetSelector.addGoal(1, new OwnerHurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new OwnerHurtTargetGoal(this));
        this.targetSelector.addGoal(3, new HurtByTargetGoal(this, NetherHumanoidEntity.class, NetherDragonEntity.class,
                AbstractGolem.class, AbstractVillager.class) {
            @Override
            public boolean canUse() {
                return isTame() && super.canUse();
            }
        });
        this.targetSelector.addGoal(3, new HurtByTargetGoal(this) {
            @Override
            public boolean canUse() {
                return !isTame() && super.canUse();
            }
        });
        this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, Mob.class, 10, true, false,
                e -> isTame() && NetherHumanoidEntity.isHostileTarget(e)));
        this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, LivingEntity.class, 10, true, false, this::isWildPrey));
    }

    /** Salvaje: todos los mobs y jugadores cerca de su nido son presa (menos otros Dragones Infernales y los huevos). */
    private boolean isWildPrey(LivingEntity e) {
        if (isTame() || !e.isAlive() || e instanceof InfernalDragonEntity || e instanceof DragonEggEntity) {
            return false;
        }
        if (!(e instanceof Mob) && !(e instanceof Player)) {
            return false;
        }
        return nest == null || e.distanceToSqr(Vec3.atCenterOf(nest)) < 40.0 * 40.0;
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (!isTame()) {
            if (target instanceof InfernalDragonEntity || target instanceof DragonEggEntity) {
                return false;
            }
            if (target instanceof Player && level().getDifficulty() == Difficulty.PEACEFUL) {
                return false;
            }
            return target.canBeSeenAsEnemy();
        }
        return super.canAttack(target);
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    // ------------------------------------------------------------------ ataques
    @Override
    public Vec3 mouthPosition() {
        Vec3 forward = Vec3.directionFromRotation(0, yBodyRot);
        float s = getScale();
        return position().add(forward.scale(3.4 * s)).add(0, (isFlying() ? 1.4 : 2.7) * s, 0);
    }

    /** Bola de fuego explosiva. */
    @Override
    protected void spawnFireball(Vec3 from, Vec3 direction, float damage) {
        DragonFireballEntity.shootExplosive(this, from, direction, damage * 0.7f, isTame() ? 2.0f : 2.6f, !isTame());
    }

    /** En vez del aliento de fuego, la IA usa el agarre. */
    @Override
    public boolean canBreathe() {
        return grabCooldown <= 0 && grabPhase == NONE && canFlyNow() && !isVehicle();
    }

    @Override
    public void startBreath() {
        if (level().isClientSide || !canBreathe()) {
            return;
        }
        LivingEntity target = getTarget();
        if (target == null || !canCarry(target)) {
            if (target != null) {
                shootFireball(target.getBoundingBox().getCenter().subtract(mouthPosition()));
            }
            grabCooldown = 60;
            return;
        }
        grabTarget = target;
        grabPhase = SWOOP;
        grabTicks = 140;
        if (!isFlying()) {
            takeOff();
        }
        playSound(SoundEvents.ENDER_DRAGON_GROWL, 1.0f + getScale(), 1.1f);
    }

    /** ¿Lo puede levantar? (nada más grande que él, ni jefes, ni otros dragones). */
    private boolean canCarry(LivingEntity e) {
        if (!e.isAlive() || e.isPassenger() || e.isVehicle() || e instanceof NetherDragonEntity || e instanceof DragonEggEntity) {
            return false;
        }
        if (e.getType().is(Tags.EntityTypes.BOSSES)) {
            return false;
        }
        float s = Math.max(0.5f, getScale());
        return e.getBbWidth() <= 2.0f * s && e.getBbHeight() <= 3.0f * s;
    }

    private void grab(LivingEntity e, int phase, int ticks) {
        carried = e;
        grabTarget = null;
        grabPhase = phase;
        grabTicks = ticks;
        entityData.set(CARRYING, true);
        triggerAnim("action", "grab");
        playSound(SoundEvents.ENDER_DRAGON_GROWL, 1.2f + getScale(), 1.0f);
        e.hurt(damageSources().mobAttack(this), 3.0f + 4.0f * getScale());
        if (e instanceof Mob mob) {
            mob.getNavigation().stop();
        }
    }

    /** Lo suelta desde donde esté (la caída hace el resto). */
    public void release() {
        LivingEntity c = carried;
        carried = null;
        grabTarget = null;
        grabPhase = NONE;
        grabCooldown = 200;
        entityData.set(CARRYING, false);
        if (c != null && c.isAlive()) {
            Vec3 throwDir = Vec3.directionFromRotation(0, getYRot()).scale(0.5);
            c.setDeltaMovement(getDeltaMovement().add(throwDir).add(0.0, -0.3, 0.0));
            c.hurtMarked = true;
            playSound(SoundEvents.ENDER_DRAGON_GROWL, 1.0f + getScale(), 1.3f);
        }
    }

    private void holdCarried(LivingEntity c) {
        Vec3 forward = Vec3.directionFromRotation(0, yBodyRot).scale(0.8 * getScale());
        Vec3 hold = position().add(forward).add(0.0, -c.getBbHeight() * 0.85, 0.0);
        c.teleportTo(hold.x, hold.y, hold.z);
        c.setDeltaMovement(Vec3.ZERO);
        c.resetFallDistance();
        c.hurtMarked = true;
    }

    private void tickGrab() {
        if (grabPhase == SWOOP) {
            LivingEntity t = grabTarget;
            if (t == null || !t.isAlive() || t.level() != level() || --grabTicks < 0 || !canCarry(t)) {
                grabPhase = NONE;
                grabTarget = null;
                grabCooldown = 100;
                return;
            }
            if (!isFlying()) {
                takeOff();
            }
            // picada: justo encima del objetivo
            setFlyTarget(t.position().add(0.0, t.getBbHeight() + 0.3, 0.0));
            if (position().distanceTo(t.position().add(0.0, t.getBbHeight(), 0.0)) < 2.2 + getBbWidth() * 0.4) {
                grab(t, LIFT, 120);
                liftTopY = getY() + 16.0 + random.nextInt(8);
            }
            return;
        }
        LivingEntity c = carried;
        if (c == null || !c.isAlive() || c.level() != level() || --grabTicks < 0) {
            release();
            return;
        }
        holdCarried(c);
        if (grabPhase == LIFT) {
            Vec3 forward = Vec3.directionFromRotation(0, getYRot()).scale(3.0);
            setFlyTarget(new Vec3(getX() + forward.x, liftTopY, getZ() + forward.z));
            if (getY() >= liftTopY - 1.0 || horizontalCollision && grabTicks < 80) {
                release();
            }
        } else if (grabPhase == RIDER_CARRY && !(getControllingPassenger() instanceof Player)) {
            release();
        }
    }

    /** R del jinete: con la barra llena agarra al mob que tenga adelante; si ya lleva uno, lo suelta. */
    @Override
    public void riderSpecial(Player rider) {
        if (!isAdult()) {
            return;
        }
        if (carried != null) {
            release();
            return;
        }
        if (getCharge() < MAX_CHARGE) {
            rider.displayClientMessage(Component.translatable("msg.civilizacion_nether.burst_not_ready", getCharge(), MAX_CHARGE), true);
            return;
        }
        Vec3 look = rider.getLookAngle();
        Vec3 center = mouthPosition().add(look.scale(5.0));
        LivingEntity best = null;
        double bestDist = Double.MAX_VALUE;
        for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, new AABB(center, center).inflate(7.0),
                e -> e != this && e != rider && !NetherHumanoidEntity.isAlly(e) && canCarry(e))) {
            double d = e.distanceToSqr(center);
            if (d < bestDist) {
                bestDist = d;
                best = e;
            }
        }
        if (best == null) {
            rider.displayClientMessage(Component.translatable("msg.civilizacion_nether.nothing_to_grab"), true);
            return;
        }
        setCharge(0);
        grab(best, RIDER_CARRY, 600);
        rider.displayClientMessage(Component.translatable("msg.civilizacion_nether.grab_hint"), true);
        addBond(1);
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) {
            if (random.nextInt(4) == 0) {
                Vec3 m = mouthPosition();
                level().addParticle(random.nextBoolean() ? ParticleTypes.FLAME : ParticleTypes.SMOKE, m.x, m.y, m.z, 0.0, 0.03, 0.0);
            }
            return;
        }
        if (grabCooldown > 0) {
            grabCooldown--;
        }
        if (grabPhase != NONE) {
            tickGrab();
        }
        // el salvaje no se aleja de su nido
        if (!isTame() && nest != null && tickCount % 100 == 0 && getTarget() == null
                && distanceToSqr(Vec3.atCenterOf(nest)) > 40.0 * 40.0) {
            if (isFlying()) {
                setFlyTarget(Vec3.atCenterOf(nest).add(0.0, 8.0, 0.0));
            } else {
                getNavigation().moveTo(nest.getX() + 0.5, nest.getY(), nest.getZ() + 0.5, 1.0);
            }
        }
    }

    @Override
    public void remove(RemovalReason reason) {
        if (carried != null) {
            release();
        }
        super.remove(reason);
    }

    // ------------------------------------------------------------------ guardado
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (nest != null) {
            tag.putLong("Nest", nest.asLong());
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("Nest")) {
            setNest(BlockPos.of(tag.getLong("Nest")));
        }
    }

    @Override
    public float getVoicePitch() {
        return super.getVoicePitch() * 0.85f;
    }

    // ------------------------------------------------------------------ GeckoLib
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 6, state -> {
            if (isResting() || isInSittingPose()) {
                return state.setAndContinue(REST);
            }
            Vec3 v = getDeltaMovement();
            double h = v.horizontalDistance();
            if (isFlying() || (!onGround() && !isInWater() && !isInLava() && v.y < -0.6)) {
                if (v.y < -0.12 && h > 0.15) {
                    return state.setAndContinue(GLIDE);
                }
                return state.setAndContinue(h < 0.08 ? HOVER : FLY);
            }
            if (state.isMoving()) {
                return state.setAndContinue(isAggressive() || h > 0.24 ? RUN : WALK);
            }
            return state.setAndContinue(IDLE);
        }));
        controllers.add(new AnimationController<>(this, "carry", 4, state -> isCarrying() ? state.setAndContinue(CARRY) : PlayState.STOP));
        controllers.add(new AnimationController<>(this, "action", 3, state -> PlayState.STOP)
                .triggerableAnim("bite", RawAnimation.begin().thenPlay(P + "bite"))
                .triggerableAnim("breath", RawAnimation.begin().thenPlay(P + "breath"))
                .triggerableAnim("roar", RawAnimation.begin().thenPlay(P + "roar"))
                .triggerableAnim("takeoff", RawAnimation.begin().thenPlay(P + "takeoff"))
                .triggerableAnim("grab", RawAnimation.begin().thenPlay(P + "grab")));
    }
}
