package com.civilizacionnether.entity;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.block.NetherBedBlock;
import com.civilizacionnether.entity.ai.FollowOwnerSimpleGoal;
import com.civilizacionnether.entity.ai.HumanoidCombatGoal;
import com.civilizacionnether.entity.ai.SleepInNetherBedGoal;
import com.civilizacionnether.entity.ai.WorkAtStationGoal;
import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModItems;
import com.civilizacionnether.registry.ModPoiTypes;
import com.civilizacionnether.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.NeutralMob;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal;
import net.minecraft.world.entity.ai.goal.OpenDoorGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtTargetGoal;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.entity.ai.village.poi.PoiManager;
import net.minecraft.world.entity.animal.AbstractGolem;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.Merchant;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.UUID;

/**
 * Humanos del Nether: soldados, profesiones, el Aldeano Necromancer, el Rey Necromancer y sus Súbditos de Almas.
 * <ul>
 *   <li>Aliados del jugador, aldeanos, golems y todos sus aliados; atacan a los mobs hostiles
 *       (menos el Aldeano Necromancer, que huye de los no muertos).</li>
 *   <li>Clic derecho: comerciar. Mayús + clic derecho del dueño: quedarse quieto / volver a seguir.</li>
 *   <li>Soldados: se contratan con rubíes. El Rey: con 3 manzanas doradas encantadas.</li>
 *   <li>Hombres y mujeres: con carne de vaca asada, y si hay camas del Nether libres cerca, tienen un hijo.
 *       Los hijos crecen poco a poco y son adultos en 20 minutos.</li>
 *   <li>Duermen 10 minutos en la cama del Nether, trabajan en su mesa, abren puertas y nadan.</li>
 * </ul>
 */
public class NetherHumanoidEntity extends TamableAnimal implements GeoEntity, Merchant {
    public static final int KING_APPLES = 3;
    private static final int SOUL_LIFE = 600; // 30 segundos
    private static final EntityDataAccessor<Boolean> FEMALE = SynchedEntityData.defineId(NetherHumanoidEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> VARIANT = SynchedEntityData.defineId(NetherHumanoidEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> GROWTH = SynchedEntityData.defineId(NetherHumanoidEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Boolean> WORKING = SynchedEntityData.defineId(NetherHumanoidEntity.class, EntityDataSerializers.BOOLEAN);

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private final HumanoidType humanoidType;

    private int lifeTicks = -1;          // solo los súbditos invocados
    private int applesFed;               // rey: manzanas doradas encantadas recibidas
    private int summonCooldown = 100;    // rey: espera entre invocaciones
    private int meleeCombo;
    private boolean genderSet;
    @Nullable
    private UUID summonerId;             // súbdito: el rey al que defiende
    @Nullable
    private BlockPos home;               // sin dueño: su casa en el reino (el rey, su trono)
    @Nullable
    private Player tradingPlayer;
    @Nullable
    private MerchantOffers offers;
    private int restockTimer;

    public NetherHumanoidEntity(EntityType<? extends TamableAnimal> entityType, Level level, HumanoidType type) {
        super(entityType, level);
        this.humanoidType = type;
        this.xpReward = type.isKing() ? 50 : (type.isSoul() ? 0 : 6);
        equipDefaults();
        addTypeGoals();
        // la lava y el fuego no les hacen daño: pueden cruzarla nadando
        setPathfindingMalus(net.minecraft.world.level.pathfinder.PathType.LAVA, 8.0f);
        setPathfindingMalus(net.minecraft.world.level.pathfinder.PathType.DANGER_FIRE, 0.0f);
        setPathfindingMalus(net.minecraft.world.level.pathfinder.PathType.DAMAGE_FIRE, 0.0f);
        setPathfindingMalus(net.minecraft.world.level.pathfinder.PathType.WATER, 0.0f);
    }

    /** En la lava nadan como en el agua (no se hunden). */
    @Override
    public void travel(net.minecraft.world.phys.Vec3 input) {
        if (!LavaSwim.travel(this, input)) {
            super.travel(input);
        }
    }

    public HumanoidType getHumanoidType() {
        return humanoidType;
    }

    public static AttributeSupplier.Builder createAttributes(HumanoidType type) {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, type.health)
                .add(Attributes.ATTACK_DAMAGE, Math.max(1.0, type.damage))
                .add(Attributes.ARMOR, type.armor)
                .add(Attributes.MOVEMENT_SPEED, type.speed)
                .add(Attributes.FOLLOW_RANGE, type.isKing() ? 40.0 : 32.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, type.isKing() ? 0.8 : 0.1);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(FEMALE, false);
        builder.define(VARIANT, 0);
        builder.define(GROWTH, 1.0f);
        builder.define(WORKING, false);
    }

    // ------------------------------------------------------------------ género, skin y crecimiento
    public boolean isFemale() {
        return entityData.get(FEMALE);
    }

    public void setFemale(boolean female) {
        entityData.set(FEMALE, female);
    }

    public int getVariant() {
        return entityData.get(VARIANT);
    }

    public void setVariant(int v) {
        entityData.set(VARIANT, Math.max(0, v));
    }

    public boolean isWorking() {
        return entityData.get(WORKING);
    }

    public void setWorking(boolean w) {
        entityData.set(WORKING, w);
    }

    public void assignRandomLook() {
        if (humanoidType.isGendered()) {
            boolean female = getRandom().nextBoolean();
            setFemale(female);
            setVariant(getRandom().nextInt(humanoidType.skinCount(female)));
        }
        genderSet = true;
    }

    /** Los hijos crecen de a poco: de 45 % a 100 % del tamaño en 20 minutos. */
    @Override
    public float getAgeScale() {
        return isBaby() ? 0.45f + 0.55f * Mth.clamp(entityData.get(GROWTH), 0.0f, 1.0f) : 1.0f;
    }

    @Override
    public void setAge(int age) {
        super.setAge(age);
        if (!level().isClientSide) {
            float g = age < 0 ? Mth.clamp(1.0f + age / 24000.0f, 0.0f, 1.0f) : 1.0f;
            g = Math.round(g * 50.0f) / 50.0f;
            if (g != entityData.get(GROWTH)) {
                entityData.set(GROWTH, g);
                refreshDimensions();
            }
        }
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (GROWTH.equals(key)) {
            refreshDimensions();
        }
    }

    @Nullable
    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType reason,
                                        @Nullable SpawnGroupData data) {
        SpawnGroupData out = super.finalizeSpawn(level, difficulty, reason, data);
        if (!genderSet) {
            assignRandomLook();
        }
        return out;
    }

    // ------------------------------------------------------------------ equipo
    private void equipDefaults() {
        setItemSlot(EquipmentSlot.MAINHAND, stackOf(humanoidType.mainItem));
        setItemSlot(EquipmentSlot.OFFHAND, stackOf(humanoidType.offItem));
        setDropChance(EquipmentSlot.MAINHAND, 0.0f);
        setDropChance(EquipmentSlot.OFFHAND, 0.0f);
    }

    private static ItemStack stackOf(@Nullable String id) {
        if (id == null) {
            return ItemStack.EMPTY;
        }
        ResourceLocation rl = id.contains(":") ? ResourceLocation.parse(id) : CivilizacionNether.id(id);
        Item item = BuiltInRegistries.ITEM.get(rl);
        return item == Items.AIR ? ItemStack.EMPTY : new ItemStack(item);
    }

    // ------------------------------------------------------------------ IA
    @Override
    protected void registerGoals() {
        // Comunes (el tipo aún no existe aquí; lo específico va en addTypeGoals)
        if (getNavigation() instanceof GroundPathNavigation nav) {
            nav.setCanOpenDoors(true);
            nav.setCanPassDoors(true);
        }
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new SitWhenOrderedToGoal(this));
        this.goalSelector.addGoal(1, new OpenDoorGoal(this, true));
        this.goalSelector.addGoal(1, new TradeWithPlayerGoal());
        this.goalSelector.addGoal(2, new HumanoidCombatGoal(this));
        this.goalSelector.addGoal(4, new FollowOwnerSimpleGoal(this, 1.15, 10.0, 3.0));
        this.goalSelector.addGoal(6, new MoveTowardsRestrictionGoal(this, 0.9));
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 8.0f));
        this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));

        this.targetSelector.addGoal(1, new OwnerHurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new OwnerHurtTargetGoal(this));
    }

    private void addTypeGoals() {
        if (humanoidType.combat != HumanoidType.Combat.NONE) {
            this.targetSelector.addGoal(3, new HurtByTargetGoal(this, Player.class, NetherHumanoidEntity.class,
                    NetherDragonEntity.class, AbstractGolem.class, AbstractVillager.class, AbstractHorse.class).setAlertOthers());
            this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, Mob.class, 10, true, false,
                    NetherHumanoidEntity::isHostileTarget));
        }
        if (humanoidType.fleesUndead()) {
            this.goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Monster.class, 12.0f, 0.75, 1.15,
                    e -> e.getType().is(EntityTypeTags.UNDEAD)));
        }
        if (humanoidType.canBreed()) {
            this.goalSelector.addGoal(5, new BreedGoal(this, 1.0));
        }
        if (humanoidType.isGendered()) {
            this.goalSelector.addGoal(3, new SleepInNetherBedGoal(this));
        }
        if (humanoidType.workstation != null) {
            this.goalSelector.addGoal(5, new WorkAtStationGoal(this));
        }
        if (humanoidType.isKing()) {
            // el Rey se pasea poco y despacio (sin domesticar, alrededor de su trono)
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.6, 360));
        } else {
            this.goalSelector.addGoal(7, new WaterAvoidingRandomStrollGoal(this, 0.75));
        }
    }

    /** Hora de dormir: la segunda mitad del día de Minecraft (10 minutos), también en el Nether. */
    public boolean isRestTime() {
        long t = level().getDayTime() % 24000L;
        return t >= 12000L;
    }

    /** Mobs hostiles a los que atacan por iniciativa propia. Los neutrales solo si están enojados. */
    public static boolean isHostileTarget(LivingEntity e) {
        if (e instanceof NetherDragonEntity dragon) {
            return dragon.isWildHostile() && dragon.isAlive(); // el Dragón Infernal salvaje es enemigo de todos
        }
        if (!(e instanceof Enemy) || !e.isAlive()) {
            return false;
        }
        if (e instanceof NeutralMob neutral) {
            return neutral.isAngry();
        }
        return true;
    }

    /** Aliados: el jugador, aldeanos, golems, caballos, la civilización y los dragones. */
    public static boolean isAlly(LivingEntity e) {
        return e instanceof Player || e instanceof AbstractVillager || e instanceof AbstractGolem
                || e instanceof NetherHumanoidEntity || (e instanceof NetherDragonEntity d && !d.isWildHostile()) || e instanceof AbstractHorse
                || (e instanceof TamableAnimal t && t.isTame());
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (isAlly(target) || humanoidType.combat == HumanoidType.Combat.NONE) {
            return false;
        }
        return super.canAttack(target);
    }

    @Override
    public boolean wantsToAttack(LivingEntity target, LivingEntity owner) {
        return !isAlly(target);
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        // Sin fuego amigo: los aliados no se dañan entre sí (flechas, rayos, alientos).
        Entity attacker = source.getEntity();
        if (attacker instanceof NetherHumanoidEntity || (attacker instanceof NetherDragonEntity d && !d.isWildHostile())
                || attacker instanceof AbstractGolem || attacker instanceof AbstractVillager) {
            return false;
        }
        if (isOrderedToSit() && attacker != null && !(attacker instanceof Player)) {
            setOrderedToSit(false);
            setInSittingPose(false);
        }
        return super.hurt(source, amount);
    }

    /** Mientras duerme no camina ni piensa (como el jugador acostado). */
    @Override
    protected boolean isImmobile() {
        return super.isImmobile() || isSleeping();
    }

    // ------------------------------------------------------------------ ataques
    public void playAction(String name) {
        triggerAnim("action", name);
    }

    public void performMelee(LivingEntity target) {
        swing(InteractionHand.MAIN_HAND);
        int combo = ++meleeCombo;
        boolean area;
        switch (humanoidType) {
            case GUERRERO, SUBDITO_ALMA -> {
                area = combo % 3 == 0;
                playAction(area ? "attack_sweep" : "attack_slash");
            }
            case GUERRERO_REAL -> {
                // tajo desde arriba, estocada y torbellino (el torbellino golpea a todos alrededor)
                int k = combo % 3;
                area = k == 0;
                playAction(k == 1 ? "attack_overhead" : (k == 2 ? "attack_thrust" : "attack_spin"));
            }
            default -> {
                area = false;
                playAction("attack_slash");
            }
        }
        if (doHurtTarget(target) && area) {
            for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, target.getBoundingBox().inflate(1.5),
                    e -> e != target && e != this && isHostileTarget(e))) {
                e.hurt(damageSources().mobAttack(this), (float) humanoidType.damage * 0.6f);
                e.knockback(0.4, getX() - e.getX(), getZ() - e.getZ());
            }
            if (level() instanceof ServerLevel server) {
                server.sendParticles(ParticleTypes.SWEEP_ATTACK, target.getX(), target.getY(0.5), target.getZ(), 1, 0, 0, 0, 0);
            }
        }
    }

    public void shootArrow(LivingEntity target) {
        boolean bolt = humanoidType.combat == HumanoidType.Combat.CROSSBOW;
        Arrow arrow = EntityType.ARROW.create(level());
        if (arrow == null) {
            return;
        }
        arrow.setOwner(this);
        arrow.setPos(getX(), getEyeY() - 0.2, getZ());
        double dx = target.getX() - getX();
        double dy = target.getY(0.3333) - arrow.getY();
        double dz = target.getZ() - getZ();
        double horizontal = Math.sqrt(dx * dx + dz * dz);
        arrow.shoot(dx, dy + horizontal * (bolt ? 0.12 : 0.2), dz, bolt ? 3.0f : 2.0f, bolt ? 2.0f : 4.0f);
        arrow.setBaseDamage(humanoidType.damage * (bolt ? 0.5 : 0.6));
        arrow.pickup = AbstractArrow.Pickup.DISALLOWED;
        if (bolt || getRandom().nextInt(3) == 0) {
            arrow.setRemainingFireTicks(100); // flecha de rubí ardiente
        }
        level().addFreshEntity(arrow);
        playSound(bolt ? SoundEvents.CROSSBOW_SHOOT : SoundEvents.SKELETON_SHOOT, 1.0f, 1.0f / (getRandom().nextFloat() * 0.4f + 0.8f));
    }

    /** Rayo de almas del Rey: instantáneo, con partículas de fuego de almas y rubí, sin dañar bloques. */
    public void castBolt(LivingEntity target) {
        if (!(level() instanceof ServerLevel server)) {
            return;
        }
        Vec3 from = new Vec3(getX(), getEyeY() + 0.4, getZ());
        Vec3 to = target.getBoundingBox().getCenter();
        soulBolt(server, from, to);
        target.hurt(damageSources().indirectMagic(this, this), (float) humanoidType.damage);
        target.setRemainingFireTicks(60);
        playSound(SoundEvents.EVOKER_CAST_SPELL, 1.0f, 0.8f);
        playSound(SoundEvents.BLAZE_SHOOT, 0.6f, 0.6f);
    }

    public static void soulBolt(ServerLevel server, Vec3 from, Vec3 to) {
        Vec3 dir = to.subtract(from);
        int steps = (int) Math.max(4, dir.length() * 3);
        for (int i = 1; i <= steps; i++) {
            Vec3 p = from.add(dir.scale(i / (double) steps));
            server.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, p.x, p.y, p.z, 1, 0.03, 0.03, 0.03, 0.0);
            if (i % 3 == 0) {
                server.sendParticles(ParticleTypes.CRIMSON_SPORE, p.x, p.y, p.z, 2, 0.05, 0.05, 0.05, 0.0);
            }
        }
        server.sendParticles(ParticleTypes.SOUL, to.x, to.y, to.z, 8, 0.3, 0.3, 0.3, 0.03);
    }

    public boolean canSummon() {
        return humanoidType.isKing() && summonCooldown <= 0;
    }

    /** Rey: invoca Súbditos de Almas que lo defienden durante 30 segundos. */
    public void summonSouls(@Nullable LivingEntity target) {
        if (!(level() instanceof ServerLevel server)) {
            return;
        }
        summonCooldown = 400;
        playAction("summon");
        long alive = server.getEntitiesOfClass(NetherHumanoidEntity.class, getBoundingBox().inflate(24),
                e -> e.isSoul() && getUUID().equals(e.summonerId)).size();
        int count = (int) Math.min(3, 5 - alive);
        for (int i = 0; i < count; i++) {
            NetherHumanoidEntity soul = spawnSoul(server, this, getX(), getY(), getZ());
            if (soul == null) {
                continue;
            }
            soul.summonerId = getUUID();
            if (isTame() && getOwnerUUID() != null) {
                soul.setOwnerUUID(getOwnerUUID());
                soul.setTame(true, false);
            }
            if (target != null) {
                soul.setTarget(target);
            }
        }
        playSound(SoundEvents.EVOKER_PREPARE_SUMMON, 1.2f, 0.8f);
    }

    /** Crea un Súbdito de Almas cerca de (x, y, z). También lo usa el báculo del jugador. */
    @Nullable
    public static NetherHumanoidEntity spawnSoul(ServerLevel server, LivingEntity caller, double x, double y, double z) {
        NetherHumanoidEntity soul = ModEntities.humanoid(HumanoidType.SUBDITO_ALMA).create(server);
        if (soul == null) {
            return null;
        }
        double ox = (caller.getRandom().nextDouble() - 0.5) * 4;
        double oz = (caller.getRandom().nextDouble() - 0.5) * 4;
        soul.moveTo(x + ox, y, z + oz, caller.getYRot(), 0);
        soul.lifeTicks = SOUL_LIFE;
        soul.genderSet = true;
        server.addFreshEntity(soul);
        server.sendParticles(ParticleTypes.SOUL, soul.getX(), soul.getY() + 1, soul.getZ(), 20, 0.4, 0.8, 0.4, 0.02);
        server.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, soul.getX(), soul.getY() + 0.2, soul.getZ(), 15, 0.5, 0.1, 0.5, 0.01);
        return soul;
    }

    public boolean isSoul() {
        return humanoidType.isSoul();
    }

    private void vanish() {
        if (level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.SOUL, getX(), getY() + 1, getZ(), 15, 0.3, 0.6, 0.3, 0.02);
        }
        discard();
    }

    // ------------------------------------------------------------------ ciclo de vida
    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) {
            if (isSoul() && getRandom().nextInt(3) == 0) {
                level().addParticle(ParticleTypes.SOUL_FIRE_FLAME, getRandomX(0.5), getRandomY(), getRandomZ(0.5), 0, 0.02, 0);
            }
            if (humanoidType.isKing() && getRandom().nextInt(6) == 0) {
                level().addParticle(ParticleTypes.SOUL, getRandomX(0.6), getY() + 0.1, getRandomZ(0.6), 0, 0.03, 0);
            }
            return;
        }
        if (!genderSet) {
            assignRandomLook();
        }
        if (summonCooldown > 0) {
            summonCooldown--;
        }
        if (lifeTicks > 0 && --lifeTicks == 0) {
            vanish();
            return;
        }
        if (isSoul() && summonerId != null && tickCount % 10 == 0) {
            defendSummoner((ServerLevel) level());
        }
        // se despierta al terminar la noche o si le quitan la cama
        if (isSleeping() && tickCount % 20 == 0) {
            boolean bedOk = getSleepingPos().map(p -> level().getBlockState(p).getBlock() instanceof NetherBedBlock).orElse(false);
            if (!isRestTime() || !bedOk || getTarget() != null) {
                stopSleeping();
            }
        }
        // comercio: deja de comerciar si el jugador se va o cierra la ventana
        if (tradingPlayer != null && (!tradingPlayer.isAlive() || tradingPlayer.distanceToSqr(this) > 64.0
                || !(tradingPlayer.containerMenu instanceof MerchantMenu))) {
            setTradingPlayer(null);
        }
        if (offers != null && ++restockTimer >= 6000) {
            restockTimer = 0;
            offers.forEach(MerchantOffer::resetUses);
        }
        // sin dueño: vive en su zona del reino (el Rey, junto a su trono)
        if (!isTame() && !isSoul()) {
            if (home == null) {
                home = blockPosition();
            }
            if (!hasRestriction()) {
                restrictTo(home, humanoidType.isKing() ? 5 : 40);
            }
        }
    }

    private void defendSummoner(ServerLevel server) {
        Entity s = server.getEntity(summonerId);
        if (!(s instanceof LivingEntity summoner) || !summoner.isAlive()) {
            vanish();
            return;
        }
        LivingEntity threat = summoner.getLastHurtByMob();
        if ((threat == null || !threat.isAlive()) && summoner instanceof Mob m) {
            threat = m.getTarget();
        }
        if (threat != null && threat.isAlive() && threat != this && canAttack(threat)) {
            setTarget(threat);
        } else if (getTarget() == null && distanceToSqr(summoner) > 36) {
            getNavigation().moveTo(summoner, 1.2);
        }
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (humanoidType.isKing() && level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.SOUL, getX(), getY() + 1.2, getZ(), 60, 0.6, 1.0, 0.6, 0.05);
        }
    }

    /** Permite moverse en la oscuridad del Nether (los animales normales necesitan luz o pasto). */
    @Override
    public float getWalkTargetValue(BlockPos pos, LevelReader level) {
        return 0.0f;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    // ------------------------------------------------------------------ interacción
    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (isSoul()) {
            return InteractionResult.PASS;
        }
        boolean client = level().isClientSide;

        // Familia (y curación si ya es tuyo): carne de vaca asada
        if (isFood(stack)) {
            if (isTame() && getHealth() < getMaxHealth() && !isInLove() && !isBaby()) {
                if (!client) {
                    stack.consume(1, player);
                    heal(6.0f);
                    level().broadcastEntityEvent(this, (byte) 7);
                }
                return InteractionResult.sidedSuccess(client);
            }
            InteractionResult breed = super.mobInteract(player, hand);
            if (breed.consumesAction()) {
                if (!client && isInLove() && !hasFreeBed()) {
                    player.displayClientMessage(Component.translatable("msg.civilizacion_nether.need_beds"), true);
                }
                return breed;
            }
        }

        // Rey: 3 manzanas doradas encantadas
        if (humanoidType.isKing() && !isTame() && stack.is(Items.ENCHANTED_GOLDEN_APPLE)) {
            if (!client) {
                stack.consume(1, player);
                applesFed++;
                playSound(SoundEvents.GENERIC_EAT, 1.0f, 0.8f);
                if (applesFed >= KING_APPLES) {
                    becomeTamedBy(player);
                } else {
                    ((ServerLevel) level()).sendParticles(ParticleTypes.HAPPY_VILLAGER, getX(), getY() + 2.0, getZ(), 12, 0.5, 0.5, 0.5, 0.0);
                    player.displayClientMessage(Component.translatable("msg.civilizacion_nether.king_offering",
                            getDisplayName(), applesFed, KING_APPLES), true);
                }
            }
            return InteractionResult.sidedSuccess(client);
        }

        // Soldados: rubíes
        if (humanoidType.soldier && !isTame() && stack.is(ModItems.RUBY.get())) {
            if (!client) {
                stack.consume(1, player);
                if (getRandom().nextInt(3) == 0) {
                    becomeTamedBy(player);
                } else {
                    level().broadcastEntityEvent(this, (byte) 6);
                    player.displayClientMessage(Component.translatable("msg.civilizacion_nether.tame_fail", getDisplayName()), true);
                }
            }
            return InteractionResult.sidedSuccess(client);
        }

        // Curar al Rey domesticado con manzanas doradas
        if (humanoidType.isKing() && isTame() && stack.is(Items.GOLDEN_APPLE) && getHealth() < getMaxHealth()) {
            if (!client) {
                stack.consume(1, player);
                heal(20.0f);
                level().broadcastEntityEvent(this, (byte) 7);
            }
            return InteractionResult.sidedSuccess(client);
        }

        // Quedarse quieto / volver a seguir (Mayús + clic derecho del dueño)
        if (isTame() && isOwnedBy(player) && (player.isSecondaryUseActive() || !humanoidType.canTrade())) {
            if (!client) {
                boolean stay = !isOrderedToSit();
                setOrderedToSit(stay);
                setInSittingPose(stay);
                setJumping(false);
                getNavigation().stop();
                setTarget(null);
                player.displayClientMessage(Component.translatable(
                        stay ? "msg.civilizacion_nether.sit" : "msg.civilizacion_nether.follow", getDisplayName()), true);
            }
            return InteractionResult.sidedSuccess(client);
        }

        // Comerciar (clic derecho)
        if (humanoidType.canTrade() && !isBaby() && !isSleeping() && isAlive()) {
            if (!client) {
                if (getTradingPlayer() != null && getTradingPlayer() != player) {
                    return InteractionResult.CONSUME;
                }
                MerchantOffers list = getOffers();
                if (!list.isEmpty()) {
                    setTradingPlayer(player);
                    openTradingScreen(player, getDisplayName(), 1);
                    if (humanoidType.villagerModel) {
                        playAction("trade");
                    }
                }
            }
            return InteractionResult.sidedSuccess(client);
        }
        return super.mobInteract(player, hand);
    }

    private void becomeTamedBy(Player player) {
        tame(player);
        getNavigation().stop();
        setTarget(null);
        setOrderedToSit(false);
        setInSittingPose(false);
        clearRestriction();
        home = null;
        level().broadcastEntityEvent(this, (byte) 7);
        if (humanoidType.isKing()) {
            playSound(SoundEvents.TOTEM_USE, 0.8f, 0.9f);
            ((ServerLevel) level()).sendParticles(ParticleTypes.SOUL_FIRE_FLAME, getX(), getY() + 1.2, getZ(), 40, 0.6, 1.0, 0.6, 0.03);
        } else {
            playAction("tamed");
        }
        player.displayClientMessage(Component.translatable("msg.civilizacion_nether.tamed", getDisplayName()), true);
    }

    // ------------------------------------------------------------------ familia
    @Override
    public boolean isFood(ItemStack stack) {
        return humanoidType.canBreed() && stack.is(Items.COOKED_BEEF);
    }

    /** Camas del Nether de sobra cerca: más camas que humanos alrededor. */
    public boolean hasFreeBed() {
        if (!(level() instanceof ServerLevel server)) {
            return false;
        }
        long beds = server.getPoiManager().getInRange(h -> h.is(ModPoiTypes.NETHER_BED.getKey())
                        || h.is(net.minecraft.world.entity.ai.village.poi.PoiTypes.HOME), blockPosition(), 24, PoiManager.Occupancy.ANY)
                .filter(r -> server.getBlockState(r.getPos()).getBlock() instanceof com.civilizacionnether.block.NetherBedBlock).count();
        if (beds == 0) {
            beds = SleepInNetherBedGoal.countBedsNear(server, blockPosition(), 12);
        }
        long people = server.getEntitiesOfClass(NetherHumanoidEntity.class, getBoundingBox().inflate(24),
                h -> h.getHumanoidType().isGendered()).size();
        return beds > people;
    }

    @Override
    public boolean canMate(Animal other) {
        if (other == this || !(other instanceof NetherHumanoidEntity mate)) {
            return false;
        }
        if (!humanoidType.canBreed() || !mate.humanoidType.canBreed() || isFemale() == mate.isFemale()) {
            return false;
        }
        return isInLove() && mate.isInLove() && !isOrderedToSit() && !mate.isOrderedToSit() && hasFreeBed();
    }

    @Nullable
    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob otherParent) {
        HumanoidType childType = humanoidType;
        if (otherParent instanceof NetherHumanoidEntity mate && getRandom().nextBoolean()) {
            childType = mate.humanoidType;
        }
        NetherHumanoidEntity baby = ModEntities.humanoid(childType).create(level);
        if (baby != null) {
            boolean female = getRandom().nextBoolean();
            baby.setFemale(female);
            baby.setVariant(getRandom().nextInt(childType.skinCount(female)));
            baby.genderSet = true;
            if (isTame() && getOwnerUUID() != null) {
                baby.setOwnerUUID(getOwnerUUID());
                baby.setTame(true, true);
            }
        }
        return baby;
    }

    // ------------------------------------------------------------------ comercio
    @Override
    public void setTradingPlayer(@Nullable Player player) {
        this.tradingPlayer = player;
    }

    @Nullable
    @Override
    public Player getTradingPlayer() {
        return tradingPlayer;
    }

    @Override
    public MerchantOffers getOffers() {
        if (offers == null) {
            offers = HumanTrades.create(this);
        }
        return offers;
    }

    @Override
    public void overrideOffers(MerchantOffers offers) {
    }

    @Override
    public void notifyTrade(MerchantOffer offer) {
        offer.increaseUses();
        this.ambientSoundTime = -getAmbientSoundInterval();
        playSound(getNotifyTradeSound(), 1.0f, getVoicePitch());
    }

    @Override
    public void notifyTradeUpdated(ItemStack stack) {
    }

    @Override
    public int getVillagerXp() {
        return 0;
    }

    @Override
    public void overrideXp(int xp) {
    }

    @Override
    public boolean showProgressBar() {
        return false;
    }

    @Override
    public SoundEvent getNotifyTradeSound() {
        return humanoidType.villagerModel ? SoundEvents.VILLAGER_YES : SoundEvents.EXPERIENCE_ORB_PICKUP;
    }

    @Override
    public boolean isClientSide() {
        return level().isClientSide;
    }

    /** Mientras comercia se queda quieto mirando al jugador. */
    private class TradeWithPlayerGoal extends Goal {
        TradeWithPlayerGoal() {
            setFlags(java.util.EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
        }

        @Override
        public boolean canUse() {
            return tradingPlayer != null && isAlive();
        }

        @Override
        public void start() {
            getNavigation().stop();
        }

        @Override
        public void tick() {
            if (tradingPlayer != null) {
                getLookControl().setLookAt(tradingPlayer, 30.0f, 30.0f);
            }
        }
    }

    // ------------------------------------------------------------------ guardado
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("LifeTicks", lifeTicks);
        tag.putInt("ApplesFed", applesFed);
        tag.putBoolean("Female", isFemale());
        tag.putInt("Variant", getVariant());
        tag.putBoolean("GenderSet", genderSet);
        if (summonerId != null) {
            tag.putUUID("Summoner", summonerId);
        }
        if (home != null) {
            tag.putInt("HomeX", home.getX());
            tag.putInt("HomeY", home.getY());
            tag.putInt("HomeZ", home.getZ());
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("LifeTicks")) {
            lifeTicks = tag.getInt("LifeTicks");
        }
        applesFed = tag.getInt("ApplesFed");
        if (tag.contains("Female")) {
            setFemale(tag.getBoolean("Female"));
            setVariant(tag.getInt("Variant"));
            genderSet = tag.getBoolean("GenderSet") || tag.contains("Variant");
        }
        if (tag.hasUUID("Summoner")) {
            summonerId = tag.getUUID("Summoner");
        }
        if (tag.contains("HomeX")) {
            home = new BlockPos(tag.getInt("HomeX"), tag.getInt("HomeY"), tag.getInt("HomeZ"));
        }
    }

    // ------------------------------------------------------------------ sonidos
    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        if (isSleeping()) {
            return null;
        }
        if (humanoidType.villagerModel) {
            return SoundEvents.VILLAGER_AMBIENT;
        }
        return switch (humanoidType) {
            case SUBDITO_ALMA -> SoundEvents.VEX_AMBIENT;
            case REY_NECROMANCER -> SoundEvents.EVOKER_AMBIENT;
            default -> null;
        };
    }

    /** Voz grabada por el usuario: hombre, mujer, niño o niña. */
    private SoundEvent voice() {
        if (isFemale()) {
            return isBaby() ? ModSounds.GIRL_HURT.get() : ModSounds.WOMAN_HURT.get();
        }
        return isBaby() ? ModSounds.BOY_HURT.get() : ModSounds.MAN_HURT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        if (isSoul()) {
            return SoundEvents.VEX_HURT;
        }
        if (humanoidType.villagerModel) {
            return SoundEvents.VILLAGER_HURT;
        }
        if (humanoidType.isKing()) {
            return SoundEvents.EVOKER_HURT;
        }
        return voice();
    }

    @Override
    protected SoundEvent getDeathSound() {
        if (isSoul()) {
            return SoundEvents.VEX_DEATH;
        }
        if (humanoidType.villagerModel) {
            return SoundEvents.VILLAGER_DEATH;
        }
        if (humanoidType.isKing()) {
            return SoundEvents.EVOKER_DEATH;
        }
        return voice();
    }

    /** Además de la voz: choque metálico de la armadura, golpe de cuero o eco mágico según la clase. */
    @Override
    protected void playHurtSound(DamageSource source) {
        super.playHurtSound(source);
        switch (humanoidType) {
            case GUERRERO, GUERRERO_REAL -> playSound(SoundEvents.ANVIL_LAND, 0.12f, 1.9f + getRandom().nextFloat() * 0.2f);
            case ARQUERO, BALLESTERO -> playSound(SoundEvents.ARMOR_EQUIP_LEATHER.value(), 0.7f, 1.2f);
            case REY_NECROMANCER -> playSound(SoundEvents.ILLUSIONER_HURT, 0.6f, 0.6f);
            default -> {
            }
        }
    }

    @Override
    public float getVoicePitch() {
        if (humanoidType.isKing()) {
            return 0.7f;
        }
        return 0.95f + getRandom().nextFloat() * 0.1f;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 400;
    }

    // ------------------------------------------------------------------ GeckoLib
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        String p = humanoidType.animPrefix;
        boolean human = humanoidType.professional && !humanoidType.villagerModel;
        boolean villager = humanoidType.villagerModel;
        RawAnimation idle = RawAnimation.begin().thenLoop(p + "idle");
        RawAnimation walk = RawAnimation.begin().thenLoop(p + "walk");
        RawAnimation run = RawAnimation.begin().thenLoop(p + (humanoidType.isKing() ? "walk" : "run"));
        RawAnimation sit = RawAnimation.begin().thenLoop(p + "sit");
        RawAnimation work = RawAnimation.begin().thenLoop(p + "work");
        RawAnimation sleep = RawAnimation.begin().thenLoop(p + ((human || villager) ? "sleep" : "idle"));
        controllers.add(new AnimationController<>(this, "movement", 4, state -> {
            if (isSleeping()) {
                return state.setAndContinue(sleep);
            }
            if (isInSittingPose()) {
                return state.setAndContinue(humanoidType.hasSitAnimation() ? sit : idle);
            }
            if (isWorking() && (human || villager)) {
                return state.setAndContinue(work);
            }
            if (state.isMoving()) {
                boolean fast = isAggressive() || getDeltaMovement().horizontalDistanceSqr() > 0.012;
                return state.setAndContinue(fast ? run : walk);
            }
            return state.setAndContinue(idle);
        }));
        AnimationController<NetherHumanoidEntity> action = new AnimationController<>(this, "action", 2, state -> PlayState.STOP);
        String[] actions = switch (humanoidType) {
            case GUERRERO, SUBDITO_ALMA -> new String[]{"attack_slash", "attack_sweep", "tamed"};
            case ARQUERO -> new String[]{"attack_bow", "tamed"};
            case REY_NECROMANCER -> new String[]{"cast", "summon"};
            case GUERRERO_REAL -> new String[]{"attack_overhead", "attack_spin", "attack_thrust", "tamed"};
            case BALLESTERO -> new String[]{"attack_crossbow", "tamed"};
            case ALDEANO_NECROMANCER -> new String[]{"trade"};
            default -> new String[]{"attack_slash", "tamed"};
        };
        for (String name : actions) {
            action.triggerableAnim(name, RawAnimation.begin().thenPlay(p + name));
        }
        controllers.add(action);
        if (humanoidType.isKing()) {
            // el orbe de rubí del báculo gira y late sin parar
            RawAnimation orb = RawAnimation.begin().thenLoop(p + "staff_orb");
            controllers.add(new AnimationController<>(this, "staff", 0, state -> state.setAndContinue(orb)));
        }
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
