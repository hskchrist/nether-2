package com.civilizacionnether.entity;

import com.civilizacionnether.entity.ai.DragonCombatGoal;
import com.civilizacionnether.entity.ai.DragonFlyGoal;
import com.civilizacionnether.entity.ai.DragonRestGoal;
import com.civilizacionnether.entity.ai.FollowOwnerSimpleGoal;
import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModItems;
import com.civilizacionnether.registry.ModParticles;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
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
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.HashMap;
import java.util.Map;

/**
 * Dragón del Nether (modelo "Void Dragon" de RedVoid_ con la cabeza "Dragon Head" de Joshie Models BB, CC BY 4.0).
 * <ul>
 *   <li>Nace de un huevo (ítem) puesto en el suelo; la cría es de quien puso el huevo.</li>
 *   <li>Crece al alimentarlo con carne o pescado: recién nacido → cría → joven → subadulto → adulto ({@link DragonStages}).</li>
 *   <li>En estado natural camina, vuela y descansa cuando se queda quieto.</li>
 *   <li>Adulto + silla de montar: se monta y vuela hacia donde mira el jinete.
 *       Clic derecho: bola de fuego (cada disparo carga 1/3 de la barra). Barra llena + R: ráfaga de fuego grande.</li>
 *   <li>Por su cuenta ataca con mordiscos, aliento de fuego de almas y bolas de fuego.</li>
 *   <li>Dos dragones adultos domesticados alimentados con carne asada ponen un huevo.</li>
 * </ul>
 */
public class NetherDragonEntity extends TamableAnimal implements GeoEntity {
    private static final EntityDataAccessor<Boolean> SADDLED = SynchedEntityData.defineId(NetherDragonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> ARMORED = SynchedEntityData.defineId(NetherDragonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> BOND = SynchedEntityData.defineId(NetherDragonEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> GROWTH = SynchedEntityData.defineId(NetherDragonEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Boolean> FLYING = SynchedEntityData.defineId(NetherDragonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> RESTING = SynchedEntityData.defineId(NetherDragonEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> CHARGE = SynchedEntityData.defineId(NetherDragonEntity.class, EntityDataSerializers.INT);

    /** Disparos necesarios para cargar la ráfaga grande. */
    public static final int MAX_CHARGE = 3;
    private static final int SHOT_COOLDOWN = 12;

    private static final String P = "animation.nether_dragon.";
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop(P + "idle");
    private static final RawAnimation WALK = RawAnimation.begin().thenLoop(P + "walk");
    private static final RawAnimation RUN = RawAnimation.begin().thenLoop(P + "run");
    private static final RawAnimation REST = RawAnimation.begin().thenLoop(P + "rest");
    private static final RawAnimation FLY = RawAnimation.begin().thenLoop(P + "fly");
    private static final RawAnimation GLIDE = RawAnimation.begin().thenLoop(P + "glide");
    private static final RawAnimation HOVER = RawAnimation.begin().thenLoop(P + "hover");

    /** Comida: carne y pescado. Lo cocido hace crecer más. */
    private static final Map<Item, Float> FOOD = new HashMap<>();

    static {
        for (Item raw : new Item[]{Items.BEEF, Items.PORKCHOP, Items.MUTTON, Items.CHICKEN, Items.RABBIT,
                Items.COD, Items.SALMON, Items.TROPICAL_FISH}) {
            FOOD.put(raw, 0.025f);
        }
        for (Item cooked : new Item[]{Items.COOKED_BEEF, Items.COOKED_PORKCHOP, Items.COOKED_MUTTON, Items.COOKED_CHICKEN,
                Items.COOKED_RABBIT, Items.COOKED_COD, Items.COOKED_SALMON}) {
            FOOD.put(cooked, 0.04f);
        }
    }

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private int breathTicks;
    private boolean megaBreath;
    private int breathCooldown;
    private int shotCooldown;
    private int rideBondTimer;
    private int idleTicks;
    // vuelo sin jinete
    @Nullable
    private Vec3 flyTarget;
    private boolean landing;
    private boolean flightGoalRunning;
    /** Modo libre (báculo): domesticado pero anda, vuela y descansa por su cuenta sin seguir al dueño. */
    private boolean free;
    /** Llamado con el báculo: vuela o camina hacia este jugador. */
    @Nullable
    private java.util.UUID recallPlayer;
    private int recallTicks;

    public NetherDragonEntity(EntityType<? extends NetherDragonEntity> entityType, Level level) {
        super(entityType, level);
        this.xpReward = 40;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, DragonStages.HEALTH_ADULT)
                .add(Attributes.ATTACK_DAMAGE, DragonStages.BITE_ADULT)
                .add(Attributes.ARMOR, 12.0)
                .add(Attributes.MOVEMENT_SPEED, 0.28)
                .add(Attributes.FLYING_SPEED, 0.62)
                .add(Attributes.FOLLOW_RANGE, 48.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.9)
                .add(Attributes.STEP_HEIGHT, 1.5);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(SADDLED, false);
        builder.define(ARMORED, false);
        builder.define(BOND, 0);
        builder.define(GROWTH, 1.0f);
        builder.define(FLYING, false);
        builder.define(RESTING, false);
        builder.define(CHARGE, 0);
    }

    // ------------------------------------------------------------------ estado
    public boolean isSaddled() {
        return entityData.get(SADDLED);
    }

    public boolean isArmored() {
        return entityData.get(ARMORED);
    }

    public int getBond() {
        return entityData.get(BOND);
    }

    public void addBond(int amount) {
        entityData.set(BOND, Mth.clamp(getBond() + amount, 0, 100));
    }

    public float getGrowth() {
        return entityData.get(GROWTH);
    }

    public boolean isAdult() {
        return getGrowth() >= 0.999f;
    }

    public int getStage() {
        return DragonStages.stage(getGrowth());
    }

    public boolean canFlyNow() {
        return getGrowth() >= DragonStages.CAN_FLY;
    }

    public boolean isFlying() {
        return entityData.get(FLYING);
    }

    public boolean isResting() {
        return entityData.get(RESTING);
    }

    public void setResting(boolean resting) {
        entityData.set(RESTING, resting);
    }

    public int getCharge() {
        return entityData.get(CHARGE);
    }

    private void setCharge(int charge) {
        entityData.set(CHARGE, Mth.clamp(charge, 0, MAX_CHARGE));
    }

    public int getIdleTicks() {
        return idleTicks;
    }

    /** El crecimiento (0..1) cambia tamaño (atributo de escala → caja de colisión y modelo), vida y mordida. */
    public void setGrowth(float growth) {
        entityData.set(GROWTH, Mth.clamp(growth, 0.0f, 1.0f));
        if (!level().isClientSide) {
            applyGrowthAttributes();
        }
    }

    private void applyGrowthAttributes() {
        float size = DragonStages.lerp(DragonStages.SIZE, getGrowth());
        double t = (size - DragonStages.SIZE[0]) / (1.0 - DragonStages.SIZE[0]);
        AttributeInstance scale = getAttribute(Attributes.SCALE);
        if (scale != null) {
            scale.setBaseValue(size);
        }
        AttributeInstance health = getAttribute(Attributes.MAX_HEALTH);
        if (health != null) {
            health.setBaseValue(Mth.lerp(t, DragonStages.HEALTH_BABY, DragonStages.HEALTH_ADULT));
        }
        AttributeInstance bite = getAttribute(Attributes.ATTACK_DAMAGE);
        if (bite != null) {
            bite.setBaseValue(Mth.lerp(t, DragonStages.BITE_BABY, DragonStages.BITE_ADULT));
        }
        if (getHealth() > getMaxHealth()) {
            setHealth(getMaxHealth());
        }
        refreshDimensions();
    }

    /** Suma crecimiento; si cambia de fase, ruge y avisa al dueño. */
    private void grow(float amount, @Nullable Player player) {
        int before = getStage();
        float oldMax = getMaxHealth();
        setGrowth(getGrowth() + amount);
        heal(getMaxHealth() - oldMax + 4.0f);
        int after = getStage();
        if (player == null) {
            return;
        }
        if (after != before) {
            triggerAnim("action", "roar");
            playSound(SoundEvents.ENDER_DRAGON_GROWL, 0.6f + 0.25f * after, 1.7f - 0.15f * after);
            if (level() instanceof ServerLevel server) {
                server.sendParticles(ModParticles.RED_SOUL.get(), getX(), getY() + getBbHeight() * 0.6, getZ(),
                        30, getBbWidth() * 0.4, getBbHeight() * 0.4, getBbWidth() * 0.4, 0.02);
            }
            player.displayClientMessage(isAdult()
                    ? Component.translatable("msg.civilizacion_nether.dragon_adult", getDisplayName())
                    : Component.translatable("msg.civilizacion_nether.dragon_stage_up", getDisplayName(),
                    Component.translatable("stage.civilizacion_nether." + after)), false);
        } else {
            player.displayClientMessage(Component.translatable("msg.civilizacion_nether.dragon_growth", getDisplayName(),
                    Component.translatable("stage.civilizacion_nether." + after), Math.round(getGrowth() * 100)), true);
        }
    }

    /** Usamos nuestras propias fases de crecimiento, no las crías de Minecraft (que se ven a la mitad). */
    @Override
    public boolean isBaby() {
        return false;
    }

    // ------------------------------------------------------------------ IA
    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new SitWhenOrderedToGoal(this));
        this.goalSelector.addGoal(2, new DragonCombatGoal(this));
        this.goalSelector.addGoal(3, new BreedGoal(this, 1.0));
        this.goalSelector.addGoal(1, new com.civilizacionnether.entity.ai.DragonRecallGoal(this));
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
                AbstractGolem.class, AbstractVillager.class));
        this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, Mob.class, 10, true, false,
                e -> isTame() && NetherHumanoidEntity.isHostileTarget(e)));
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (target instanceof NetherHumanoidEntity || target instanceof NetherDragonEntity
                || target instanceof AbstractVillager || target instanceof AbstractGolem) {
            return false;
        }
        if (isTame() && target instanceof Player) {
            return false; // un dragón domesticado nunca ataca jugadores
        }
        return super.canAttack(target);
    }

    @Override
    public boolean wantsToAttack(LivingEntity target, LivingEntity owner) {
        return !NetherHumanoidEntity.isAlly(target);
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        Entity attacker = source.getEntity();
        if (attacker instanceof NetherHumanoidEntity || attacker instanceof NetherDragonEntity) {
            return false;
        }
        if (attacker != null && hasPassenger(attacker)) {
            return false;
        }
        if (isOrderedToSit() && attacker != null && !(attacker instanceof Player)) {
            setOrderedToSit(false);
        }
        if (!level().isClientSide && isResting()) {
            setResting(false);
        }
        return super.hurt(source, amount);
    }

    @Override
    public int getArmorValue() {
        return super.getArmorValue() + (isArmored() ? 12 : 0);
    }

    @Override
    public boolean causeFallDamage(float fallDistance, float multiplier, DamageSource source) {
        return false;
    }

    /** Permite aparecer y moverse en la oscuridad del Nether (los animales normales necesitan luz o pasto). */
    @Override
    public float getWalkTargetValue(net.minecraft.core.BlockPos pos, net.minecraft.world.level.LevelReader level) {
        return 0.0f;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public void awardKillScore(Entity killed, int score, DamageSource source) {
        super.awardKillScore(killed, score, source);
        if (isTame()) {
            addBond(2);
        }
    }

    // ------------------------------------------------------------------ boca, puntería y ataques
    /** Punto aproximado de la boca (el modelo se escala con la fase). */
    public Vec3 mouthPosition() {
        Vec3 forward = Vec3.directionFromRotation(0, yBodyRot);
        float s = getScale();
        return position().add(forward.scale(3.4 * s)).add(0, 2.3 * s, 0);
    }

    /** Dirección desde la boca hacia el punto que mira el jinete (así la bola va justo a la mira). */
    private Vec3 riderAim(Player rider) {
        Vec3 eye = rider.getEyePosition();
        Vec3 far = eye.add(rider.getLookAngle().scale(64.0));
        HitResult hit = level().clip(new ClipContext(eye, far, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, rider));
        Vec3 point = hit.getType() == HitResult.Type.MISS ? far : hit.getLocation();
        Vec3 dir = point.subtract(mouthPosition());
        return dir.lengthSqr() < 1.0e-4 ? rider.getLookAngle() : dir.normalize();
    }

    private Vec3 aimDirection() {
        if (getControllingPassenger() instanceof Player rider) {
            return riderAim(rider);
        }
        LivingEntity target = getTarget();
        if (target != null) {
            return target.getBoundingBox().getCenter().subtract(mouthPosition()).normalize();
        }
        return Vec3.directionFromRotation(getXRot(), getYRot());
    }

    public boolean canBreathe() {
        return breathCooldown <= 0 && breathTicks <= 0 && canFlyNow();
    }

    /** Aliento de fuego de almas (lo usa solo, sin jinete). */
    public void startBreath() {
        if (!canBreathe() || level().isClientSide) {
            return;
        }
        megaBreath = false;
        breathTicks = 30;
        breathCooldown = 90 - getBond() / 3;
        triggerAnim("action", "breath");
        playSound(SoundEvents.ENDER_DRAGON_SHOOT, 1.2f + getScale(), 0.8f + getRandom().nextFloat() * 0.2f);
    }

    public void bite(LivingEntity target) {
        triggerAnim("action", "bite");
        doHurtTarget(target);
        playSound(SoundEvents.RAVAGER_ATTACK, 1.5f, 0.7f + (1.0f - getGrowth()) * 0.6f);
    }

    /** Bola de fuego hacia una dirección (jinete o IA). Devuelve true si disparó. */
    public boolean shootFireball(Vec3 direction) {
        if (shotCooldown > 0 || !canFlyNow() || level().isClientSide) {
            return false;
        }
        shotCooldown = SHOT_COOLDOWN;
        float damage = 6.0f + 4.0f * getScale() + getBond() / 20.0f;
        DragonFireballEntity.shoot(this, mouthPosition(), direction, damage);
        triggerAnim("action", "bite");
        playSound(SoundEvents.BLAZE_SHOOT, 1.5f, 0.6f + getRandom().nextFloat() * 0.2f);
        return true;
    }

    /** Clic derecho del jinete: dispara y carga la barra. */
    public void riderShoot(Player rider) {
        if (!isAdult() || !shootFireball(riderAim(rider))) {
            return;
        }
        int before = getCharge();
        setCharge(before + 1);
        if (before < MAX_CHARGE && getCharge() == MAX_CHARGE) {
            playSound(SoundEvents.ENDER_DRAGON_GROWL, 0.8f, 1.4f);
        }
    }

    /** Tecla R del jinete: con la barra llena lanza la ráfaga de fuego grande. */
    public void riderSpecial(Player rider) {
        if (!isAdult() || breathTicks > 0) {
            return;
        }
        if (getCharge() < MAX_CHARGE) {
            rider.displayClientMessage(Component.translatable("msg.civilizacion_nether.burst_not_ready", getCharge(), MAX_CHARGE), true);
            return;
        }
        setCharge(0);
        megaBreath = true;
        breathTicks = 60;
        triggerAnim("action", "breath");
        playSound(SoundEvents.ENDER_DRAGON_GROWL, 3.0f, 0.7f);
        playSound(SoundEvents.ENDER_DRAGON_SHOOT, 3.0f, 0.6f);
        addBond(1);
    }

    private void tickBreath(ServerLevel server) {
        Vec3 mouth = mouthPosition();
        Vec3 dir = aimDirection();
        float s = Math.max(0.5f, getScale());
        double range = (megaBreath ? 24.0 : 13.0) * s;
        int steps = megaBreath ? 22 : 12;
        for (int i = 1; i <= steps; i++) {
            double along = range * i / steps;
            Vec3 p = mouth.add(dir.scale(along));
            double spread = (megaBreath ? 0.12 : 0.07) * along;
            server.sendParticles(ModParticles.BLACK_FLAME.get(), p.x, p.y, p.z, megaBreath ? 8 : 4, spread, spread, spread, 0.03);
            if (i % 2 == 0) {
                server.sendParticles(ModParticles.RED_SOUL.get(), p.x, p.y, p.z,
                        megaBreath ? 5 : 2, spread, spread, spread, 0.01);
            }
            if (megaBreath && i % 5 == 0) {
                server.sendParticles(ParticleTypes.LARGE_SMOKE, p.x, p.y, p.z, 2, spread, spread, spread, 0.01);
                server.sendParticles(ModParticles.RED_SOUL.get(), p.x, p.y, p.z, 2, spread, spread, spread, 0.02);
            }
        }
        if (megaBreath && breathTicks % 10 == 0) {
            playSound(SoundEvents.BLAZE_SHOOT, 2.0f, 0.5f);
            if (breathTicks == 30) {
                triggerAnim("action", "breath");
            }
        }
        if (breathTicks % (megaBreath ? 4 : 5) != 0) {
            return;
        }
        float damage = megaBreath ? 9.0f + getBond() / 10.0f : 7.0f * s * (1.0f + getBond() / 200.0f);
        Vec3 end = mouth.add(dir.scale(range));
        AABB area = new AABB(mouth, end).inflate(megaBreath ? 4.0 : 2.5);
        for (LivingEntity e : server.getEntitiesOfClass(LivingEntity.class, area, e -> e != this && e.isAlive() && !hasPassenger(e))) {
            if (NetherHumanoidEntity.isAlly(e) && (isTame() || !(e instanceof Player))) {
                continue;
            }
            Vec3 to = e.getBoundingBox().getCenter().subtract(mouth);
            double along = to.dot(dir);
            if (along < 0 || along > range) {
                continue;
            }
            double off = to.subtract(dir.scale(along)).length();
            if (off > (megaBreath ? 1.8 + along * 0.3 : 1.2 + along * 0.18)) {
                continue;
            }
            e.hurt(damageSources().mobAttack(this), damage);
            e.setRemainingFireTicks(megaBreath ? 160 : 100);
            if (megaBreath) {
                e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 100, 0));
                e.push(dir.x * 0.4, 0.15, dir.z * 0.4);
            }
        }
    }

    // ------------------------------------------------------------------ vuelo
    private void setFlying(boolean flying) {
        if (flying != isFlying()) {
            entityData.set(FLYING, flying);
        }
        setNoGravity(flying);
    }

    /** Despega (lo usan la IA y la pelea). */
    public void takeOff() {
        if (isFlying() || !canFlyNow()) {
            return;
        }
        setResting(false);
        setFlying(true);
        landing = false;
        getNavigation().stop();
        setDeltaMovement(getDeltaMovement().add(0.0, 0.55, 0.0));
        flyTarget = position().add(0.0, 6.0, 0.0);
        triggerAnim("action", "takeoff");
        playSound(SoundEvents.ENDER_DRAGON_FLAP, 1.5f, 0.8f + (1.0f - getGrowth()) * 0.6f);
    }

    /** Baja a tierra (al llegar al suelo deja de volar). */
    public void land() {
        if (isFlying()) {
            landing = true;
            flyTarget = null;
        }
    }

    public void setFlyTarget(Vec3 target) {
        flyTarget = target;
        landing = false;
    }

    @Nullable
    public Vec3 getFlyTarget() {
        return flyTarget;
    }

    // ------------------------------------------------------------------ báculo: modo libre y llamada
    public boolean isFree() {
        return free;
    }

    public void setFree(boolean free) {
        this.free = free;
        if (free) {
            setOrderedToSit(false);
            setInSittingPose(false);
            setResting(false);
        }
    }

    /** El dueño lo llama con el báculo: deja lo que hace y va hacia él (volando si está lejos o a otra altura). */
    public void recall(Player player) {
        setFree(false);
        setOrderedToSit(false);
        setInSittingPose(false);
        setResting(false);
        setTarget(null);
        recallPlayer = player.getUUID();
        recallTicks = 1200;
        triggerAnim("action", "roar");
        playSound(SoundEvents.ENDER_DRAGON_GROWL, 0.8f + getScale(), 1.1f);
    }

    @Nullable
    public Player getRecallPlayer() {
        if (recallPlayer == null || --recallTicks < 0) {
            recallPlayer = null;
            return null;
        }
        return level().getPlayerByUUID(recallPlayer);
    }

    public void stopRecall() {
        recallPlayer = null;
        recallTicks = 0;
    }

    public boolean hasRecall() {
        return recallPlayer != null;
    }

    public void setFlightGoalRunning(boolean running) {
        flightGoalRunning = running;
    }

    /** Suelo bajo un punto (o null si no hay nada en 48 bloques). */
    @Nullable
    public Vec3 groundBelow(Vec3 from) {
        BlockHitResult hit = level().clip(new ClipContext(from, from.add(0, -48, 0), ClipContext.Block.COLLIDER,
                ClipContext.Fluid.ANY, this));
        return hit.getType() == HitResult.Type.MISS ? null : hit.getLocation();
    }

    /** ¿Hay camino libre (sin bloques) hasta ese punto? */
    public boolean clearPathTo(Vec3 to) {
        Vec3 from = position().add(0, getBbHeight() * 0.5, 0);
        return level().clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this))
                .getType() == HitResult.Type.MISS;
    }

    private void flyTravel() {
        if (landing) {
            Vec3 ground = groundBelow(position().add(0, 0.5, 0));
            flyTarget = ground != null ? ground : position().add(0, -4, 0);
        }
        Vec3 target = flyTarget != null ? flyTarget : position();
        Vec3 to = target.subtract(position());
        double dist = to.length();
        double max = getAttributeValue(Attributes.FLYING_SPEED) * (landing ? 0.5 : hasRecall() ? 1.05 : 0.75) * Math.max(0.6, getScale());
        Vec3 desired = dist < 0.4 ? Vec3.ZERO : to.scale(Math.min(max, dist * 0.12) / dist);
        Vec3 motion = getDeltaMovement().scale(0.88).add(desired.scale(0.12));
        setDeltaMovement(motion);
        move(MoverType.SELF, motion);
        double h = motion.horizontalDistance();
        if (h > 0.03) {
            float yaw = (float) (Mth.atan2(motion.z, motion.x) * Mth.RAD_TO_DEG) - 90.0f;
            setYRot(Mth.approachDegrees(getYRot(), yaw, 8.0f));
            yBodyRot = getYRot();
            yHeadRot = getYRot();
        }
        resetFallDistance();
    }

    // ------------------------------------------------------------------ tick
    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) {
            return;
        }
        if (breathCooldown > 0) {
            breathCooldown--;
        }
        if (shotCooldown > 0) {
            shotCooldown--;
        }
        if (breathTicks > 0) {
            breathTicks--;
            if (level() instanceof ServerLevel server) {
                tickBreath(server);
            }
            if (breathTicks == 0) {
                megaBreath = false;
            }
        }
        boolean ridden = getControllingPassenger() instanceof Player;
        if (ridden) {
            // el jinete controla el vuelo: estamos volando si no tocamos el suelo
            boolean airborne = !onGround() && !isInWater() && !isInLava();
            if (airborne && !isFlying()) {
                triggerAnim("action", "takeoff");
            }
            setFlying(airborne);
            landing = false;
            setResting(false);
            if (++rideBondTimer >= 400) {
                rideBondTimer = 0;
                addBond(1);
            }
        } else if (isFlying()) {
            if (landing && (onGround() || isInWater() || isInLava())) {
                setFlying(false);
                landing = false;
                flyTarget = null;
            } else if (!landing && !flightGoalRunning && getTarget() == null) {
                land();
            }
        } else if (isNoGravity()) {
            setNoGravity(false);
        }
        if (isFlying() && tickCount % 22 == 0) {
            playSound(SoundEvents.ENDER_DRAGON_FLAP, 0.4f + 0.6f * getScale(), 0.9f + (1.0f - getGrowth()) * 0.5f);
        }
        // contador de quietud (para descansar)
        if (onGround() && !isVehicle() && getDeltaMovement().horizontalDistanceSqr() < 1.0e-4 && getTarget() == null) {
            idleTicks++;
        } else {
            idleTicks = 0;
        }
        if (isInSittingPose() && !isResting()) {
            setResting(true);
        }
        if (tickCount % 200 == 0 && getHealth() < getMaxHealth()) {
            heal(1.0f);
        }
    }

    // ------------------------------------------------------------------ montar y volar
    @Nullable
    @Override
    public LivingEntity getControllingPassenger() {
        if (isSaddled() && isAdult() && getFirstPassenger() instanceof Player player && isOwnedBy(player)) {
            return player;
        }
        return super.getControllingPassenger();
    }

    @Override
    protected void tickRidden(Player player, Vec3 input) {
        super.tickRidden(player, input);
        setYRot(player.getYRot());
        yRotO = getYRot();
        setXRot(player.getXRot() * 0.5f);
        setRot(getYRot(), getXRot());
        yBodyRot = getYRot();
        yHeadRot = getYRot();
    }

    @Override
    protected Vec3 getRiddenInput(Player player, Vec3 input) {
        float strafe = player.xxa * 0.5f;
        float forward = player.zza;
        if (forward <= 0.0f) {
            forward *= 0.3f;
        }
        return new Vec3(strafe, 0.0, forward);
    }

    @Override
    protected float getRiddenSpeed(Player player) {
        return (float) getAttributeValue(Attributes.MOVEMENT_SPEED) * 1.15f;
    }

    @Override
    public void travel(Vec3 input) {
        if (isAlive() && isVehicle() && getControllingPassenger() instanceof Player rider) {
            boolean airborne = !onGround() && !isInLava() && !isInWater();
            // Despegue: avanzar mirando hacia arriba
            if (!airborne && input.z > 0 && rider.getXRot() < -20.0f) {
                setNoGravity(true);
                setDeltaMovement(getDeltaMovement().add(0.0, 0.7, 0.0));
                move(MoverType.SELF, getDeltaMovement());
                return;
            }
            if (airborne) {
                setNoGravity(true);
                double speed = getAttributeValue(Attributes.FLYING_SPEED) * (1.0 + getBond() / 200.0);
                Vec3 look = rider.getLookAngle();
                Vec3 motion = getDeltaMovement().scale(0.91);
                if (input.z > 0) {
                    motion = motion.add(look.scale(speed * 0.12));
                } else {
                    motion = motion.add(0.0, -0.035, 0.0); // sin avanzar: planea hacia abajo
                }
                if (input.x != 0) {
                    Vec3 right = new Vec3(-look.z, 0, look.x).normalize();
                    motion = motion.add(right.scale(-input.x * speed * 0.05));
                }
                double max = speed * 1.6;
                if (motion.length() > max) {
                    motion = motion.normalize().scale(max);
                }
                setDeltaMovement(motion);
                move(MoverType.SELF, getDeltaMovement());
                calculateEntityAnimation(true);
                resetFallDistance();
                return;
            }
            setNoGravity(false);
            super.travel(input);
            return;
        }
        if (isFlying() && !level().isClientSide) {
            flyTravel();
            return;
        }
        super.travel(input);
    }

    @Override
    protected void removePassenger(Entity passenger) {
        super.removePassenger(passenger);
        if (passenger instanceof LivingEntity living && !onGround()) {
            living.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 200, 0));
        }
    }

    @Override
    public boolean isPushable() {
        return !isVehicle();
    }

    // ------------------------------------------------------------------ interacción
    public static boolean isDragonFood(ItemStack stack) {
        return FOOD.containsKey(stack.getItem());
    }

    @Override
    public boolean isFood(ItemStack stack) {
        return isDragonFood(stack);
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        boolean client = level().isClientSide;
        if (!client && isResting() && !isOrderedToSit()) {
            setResting(false);
        }

        // Domesticar un dragón salvaje con rubí
        if (!isTame()) {
            if (stack.is(ModItems.RUBY.get())) {
                if (!client) {
                    stack.consume(1, player);
                    if (getRandom().nextFloat() < 0.25f) {
                        tame(player);
                        setTarget(null);
                        getNavigation().stop();
                        setOrderedToSit(false);
                        addBond(10);
                        level().broadcastEntityEvent(this, (byte) 7);
                        triggerAnim("action", "roar");
                        playSound(SoundEvents.ENDER_DRAGON_GROWL, 1.5f, 1.2f);
                        player.displayClientMessage(Component.translatable("msg.civilizacion_nether.tamed", getDisplayName()), true);
                    } else {
                        level().broadcastEntityEvent(this, (byte) 6);
                        player.displayClientMessage(Component.translatable("msg.civilizacion_nether.tame_fail", getDisplayName()), true);
                    }
                }
                return InteractionResult.sidedSuccess(client);
            }
            return super.mobInteract(player, hand);
        }

        if (!isOwnedBy(player)) {
            if (!client) {
                player.displayClientMessage(Component.translatable("msg.civilizacion_nether.not_owner"), true);
            }
            return InteractionResult.sidedSuccess(client);
        }

        // Carne o pescado: hace crecer a la cría; al adulto lo cura o (asado y con la vida llena) lo prepara para poner un huevo
        Float food = FOOD.get(stack.getItem());
        if (food != null) {
            if (!isAdult()) {
                if (!client) {
                    stack.consume(1, player);
                    playSound(SoundEvents.HORSE_EAT, 1.0f, 1.6f - getGrowth() * 0.6f);
                    level().broadcastEntityEvent(this, (byte) 7);
                    grow(food, player);
                }
                return InteractionResult.sidedSuccess(client);
            }
            if (getHealth() < getMaxHealth()) {
                if (!client) {
                    stack.consume(1, player);
                    playSound(SoundEvents.HORSE_EAT, 1.0f, 0.8f);
                    heal(food * 300.0f);
                    level().broadcastEntityEvent(this, (byte) 7);
                }
                return InteractionResult.sidedSuccess(client);
            }
            if (food > 0.03f && getAge() == 0 && canFallInLove()) {
                if (!client) {
                    stack.consume(1, player);
                    setInLove(player);
                }
                return InteractionResult.sidedSuccess(client);
            }
        }

        // Rubí: sube el vínculo
        if (stack.is(ModItems.RUBY.get())) {
            if (!client) {
                stack.consume(1, player);
                addBond(5);
                heal(4.0f);
                level().broadcastEntityEvent(this, (byte) 7);
                player.displayClientMessage(Component.translatable("msg.civilizacion_nether.bond", getDisplayName(), getBond()), true);
            }
            return InteractionResult.sidedSuccess(client);
        }

        // Silla (solo adulto)
        if (stack.is(Items.SADDLE) && !isSaddled()) {
            if (!client) {
                if (!isAdult()) {
                    player.displayClientMessage(Component.translatable("msg.civilizacion_nether.too_young", getDisplayName(),
                            Math.round(getGrowth() * 100)), true);
                } else {
                    stack.consume(1, player);
                    entityData.set(SADDLED, true);
                    level().playSound(null, getX(), getY(), getZ(), SoundEvents.HORSE_SADDLE, SoundSource.NEUTRAL, 1.0f, 0.8f);
                }
            }
            return InteractionResult.sidedSuccess(client);
        }

        // Armadura (opcional, solo adulto)
        if (stack.is(ModItems.DRAGON_ARMOR.get()) && !isArmored() && isAdult()) {
            if (!client) {
                stack.consume(1, player);
                entityData.set(ARMORED, true);
                level().playSound(null, getX(), getY(), getZ(), SoundEvents.ARMOR_EQUIP_NETHERITE.value(), SoundSource.NEUTRAL, 1.0f, 0.8f);
            }
            return InteractionResult.sidedSuccess(client);
        }

        // Báculo de dragón: vincularlo a este dragón
        if (stack.is(ModItems.DRAGON_STAFF.get())) {
            if (!client) {
                com.civilizacionnether.item.DragonStaffItem.bind(stack, this);
                player.displayClientMessage(Component.translatable("msg.civilizacion_nether.staff_bound", getDisplayName()), true);
                playSound(SoundEvents.ENDER_DRAGON_AMBIENT, 0.6f, 1.4f);
            }
            return InteractionResult.sidedSuccess(client);
        }

        // Mayús + clic: quedarse quieto (descansa) / seguir
        if (player.isSecondaryUseActive()) {
            if (!client) {
                free = false;
                stopRecall();
                boolean sit = !isOrderedToSit();
                setOrderedToSit(sit);
                setInSittingPose(sit);
                setResting(sit);
                land();
                getNavigation().stop();
                setTarget(null);
                player.displayClientMessage(Component.translatable(
                        sit ? "msg.civilizacion_nether.sit" : "msg.civilizacion_nether.follow", getDisplayName()), true);
            }
            return InteractionResult.sidedSuccess(client);
        }

        // Montar
        if (!isAdult()) {
            if (!client) {
                player.displayClientMessage(Component.translatable("msg.civilizacion_nether.dragon_growth", getDisplayName(),
                        Component.translatable("stage.civilizacion_nether." + getStage()), Math.round(getGrowth() * 100)), true);
            }
            return InteractionResult.sidedSuccess(client);
        }
        if (!isSaddled()) {
            if (!client) {
                player.displayClientMessage(Component.translatable("msg.civilizacion_nether.need_saddle"), true);
            }
            return InteractionResult.sidedSuccess(client);
        }
        if (!client) {
            setOrderedToSit(false);
            setInSittingPose(false);
            setResting(false);
            player.setYRot(getYRot());
            player.setXRot(getXRot());
            player.startRiding(this);
            player.displayClientMessage(Component.translatable("msg.civilizacion_nether.ride_hint"), true);
        }
        return InteractionResult.sidedSuccess(client);
    }

    @Override
    public boolean canMate(Animal other) {
        return other != this && other instanceof NetherDragonEntity mate && isAdult() && mate.isAdult()
                && isTame() && mate.isTame() && isInLove() && mate.isInLove();
    }

    /** Dos dragones adultos no tienen crías directamente: ponen un huevo. */
    @Override
    public void spawnChildFromBreeding(ServerLevel level, Animal mate) {
        DragonEggEntity egg = ModEntities.DRAGON_EGG.get().create(level);
        if (egg != null) {
            egg.moveTo(getX(), getY(), getZ(), getRandom().nextFloat() * 360.0f, 0.0f);
            egg.setOwner(getOwnerUUID());
            level.addFreshEntity(egg);
            if (getOwner() instanceof Player owner) {
                owner.displayClientMessage(Component.translatable("msg.civilizacion_nether.egg_laid"), false);
            }
        }
        setAge(6000);
        mate.setAge(6000);
        resetLove();
        mate.resetLove();
        level.broadcastEntityEvent(this, (byte) 18);
    }

    @Nullable
    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob otherParent) {
        return null;
    }

    // ------------------------------------------------------------------ guardado
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Saddled", isSaddled());
        tag.putBoolean("Armored", isArmored());
        tag.putInt("Bond", getBond());
        tag.putFloat("Growth", getGrowth());
        tag.putBoolean("Flying", isFlying());
        tag.putInt("Charge", getCharge());
        tag.putBoolean("FreeMode", free);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        entityData.set(SADDLED, tag.getBoolean("Saddled"));
        entityData.set(ARMORED, tag.getBoolean("Armored"));
        entityData.set(BOND, tag.getInt("Bond"));
        setGrowth(tag.contains("Growth") ? tag.getFloat("Growth") : 1.0f);
        setCharge(tag.getInt("Charge"));
        free = tag.getBoolean("FreeMode");
        if (tag.getBoolean("Flying")) {
            setFlying(true);
            land();
        }
    }

    @Override
    protected void dropCustomDeathLoot(ServerLevel level, DamageSource source, boolean recentlyHit) {
        super.dropCustomDeathLoot(level, source, recentlyHit);
        if (isSaddled()) {
            spawnAtLocation(Items.SADDLE);
        }
        if (isArmored()) {
            spawnAtLocation(ModItems.DRAGON_ARMOR.get());
        }
    }

    // ------------------------------------------------------------------ sonidos
    @Override
    protected SoundEvent getAmbientSound() {
        return isResting() ? null : SoundEvents.ENDER_DRAGON_AMBIENT;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.ENDER_DRAGON_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.ENDER_DRAGON_GROWL;
    }

    @Override
    protected float getSoundVolume() {
        return 0.4f + 0.8f * getScale();
    }

    @Override
    public float getVoicePitch() {
        return 1.0f + (1.0f - getGrowth()) * 0.8f + (getRandom().nextFloat() - 0.5f) * 0.2f;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 600;
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
        controllers.add(new AnimationController<>(this, "action", 3, state -> PlayState.STOP)
                .triggerableAnim("bite", RawAnimation.begin().thenPlay(P + "bite"))
                .triggerableAnim("breath", RawAnimation.begin().thenPlay(P + "breath"))
                .triggerableAnim("roar", RawAnimation.begin().thenPlay(P + "roar"))
                .triggerableAnim("takeoff", RawAnimation.begin().thenPlay(P + "takeoff")));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
