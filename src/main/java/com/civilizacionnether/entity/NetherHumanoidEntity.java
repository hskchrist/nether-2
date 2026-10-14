package com.civilizacionnether.entity;

import com.civilizacionnether.entity.ai.FollowOwnerSimpleGoal;
import com.civilizacionnether.entity.ai.HumanoidCombatGoal;
import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.NeutralMob;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.SitWhenOrderedToGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.OwnerHurtTargetGoal;
import net.minecraft.world.entity.animal.AbstractGolem;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
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
 * Humanos del Nether: Guerrero, Arquero, Rey Necromancer y sus Súbditos de Almas.
 * <ul>
 *   <li>Aliados del jugador, aldeanos, golems y todos sus aliados; atacan a los mobs hostiles.</li>
 *   <li>Guerrero y Arquero se domestican con rubíes; el Rey con 3 manzanas doradas encantadas.</li>
 *   <li>Domesticados: clic derecho del dueño = quedarse quieto / volver a seguir.</li>
 *   <li>Guerrero y Arquero se reproducen con chuleta de cerdo asada.</li>
 * </ul>
 */
public class NetherHumanoidEntity extends TamableAnimal implements GeoEntity {
    public static final int KING_APPLES = 3;
    private static final int SOUL_LIFE = 600; // 30 segundos

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private final HumanoidType humanoidType;

    private int lifeTicks = -1;          // solo los súbditos invocados
    private int applesFed;               // rey: manzanas doradas encantadas recibidas
    private int summonCooldown = 100;    // rey: espera entre invocaciones
    private int meleeCombo;
    @Nullable
    private UUID summonerId;             // súbdito: el rey al que defiende
    @Nullable
    private BlockPos home;               // rey sin domesticar: su trono

    public NetherHumanoidEntity(EntityType<? extends TamableAnimal> entityType, Level level, HumanoidType type) {
        super(entityType, level);
        this.humanoidType = type;
        this.xpReward = type.isKing() ? 50 : (type.isSoul() ? 0 : 6);
        equipDefaults();
        addTypeGoals();
    }

    public HumanoidType getHumanoidType() {
        return humanoidType;
    }

    public static AttributeSupplier.Builder createAttributes(HumanoidType type) {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, type.health)
                .add(Attributes.ATTACK_DAMAGE, type.damage)
                .add(Attributes.ARMOR, type.armor)
                .add(Attributes.MOVEMENT_SPEED, type.speed)
                .add(Attributes.FOLLOW_RANGE, type.isKing() ? 40.0 : 32.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, type.isKing() ? 0.8 : 0.1);
    }

    // ------------------------------------------------------------------ equipo
    private void equipDefaults() {
        ItemStack main = humanoidType == HumanoidType.GUERRERO ? new ItemStack(ModItems.RUBY_SWORD.get()) : ItemStack.EMPTY;
        // el arquero sostiene el arco en la mano izquierda
        ItemStack off = humanoidType == HumanoidType.ARQUERO ? new ItemStack(ModItems.RUBY_BOW.get()) : ItemStack.EMPTY;
        setItemSlot(EquipmentSlot.MAINHAND, main);
        setItemSlot(EquipmentSlot.OFFHAND, off);
        setDropChance(EquipmentSlot.MAINHAND, 0.0f);
        setDropChance(EquipmentSlot.OFFHAND, 0.0f);
    }

    // ------------------------------------------------------------------ IA
    @Override
    protected void registerGoals() {
        // Comunes (el tipo aún no existe aquí; lo específico va en addTypeGoals)
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new SitWhenOrderedToGoal(this));
        this.goalSelector.addGoal(2, new HumanoidCombatGoal(this));
        this.goalSelector.addGoal(4, new FollowOwnerSimpleGoal(this, 1.15, 10.0, 3.0));
        this.goalSelector.addGoal(6, new MoveTowardsRestrictionGoal(this, 0.9));
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 8.0f));
        this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));

        this.targetSelector.addGoal(1, new OwnerHurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new OwnerHurtTargetGoal(this));
        this.targetSelector.addGoal(3, new HurtByTargetGoal(this, Player.class, NetherHumanoidEntity.class,
                NetherDragonEntity.class, AbstractGolem.class, AbstractVillager.class, AbstractHorse.class).setAlertOthers());
        this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, Mob.class, 10, true, false,
                NetherHumanoidEntity::isHostileTarget));
    }

    private void addTypeGoals() {
        if (humanoidType.canBreed()) {
            this.goalSelector.addGoal(5, new BreedGoal(this, 1.0));
        }
        if (humanoidType.isKing()) {
            // el Rey se pasea poco y despacio (sin domesticar, alrededor de su trono)
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.6, 360));
        } else {
            this.goalSelector.addGoal(7, new WaterAvoidingRandomStrollGoal(this, 0.8));
        }
    }

    /** Mobs hostiles a los que atacan por iniciativa propia. Los neutrales solo si están enojados. */
    public static boolean isHostileTarget(LivingEntity e) {
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
                || e instanceof NetherHumanoidEntity || e instanceof NetherDragonEntity || e instanceof AbstractHorse
                || (e instanceof TamableAnimal t && t.isTame());
    }

    @Override
    public boolean canAttack(LivingEntity target) {
        if (isAlly(target)) {
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
        if (attacker instanceof NetherHumanoidEntity || attacker instanceof NetherDragonEntity
                || attacker instanceof AbstractGolem || attacker instanceof AbstractVillager) {
            return false;
        }
        if (isOrderedToSit() && attacker != null && !(attacker instanceof Player)) {
            setOrderedToSit(false);
            setInSittingPose(false);
        }
        return super.hurt(source, amount);
    }

    // ------------------------------------------------------------------ ataques
    public void playAction(String name) {
        triggerAnim("action", name);
    }

    public void performMelee(LivingEntity target) {
        swing(InteractionHand.MAIN_HAND);
        // el guerrero alterna tajo y barrido; el barrido golpea también a los hostiles de alrededor
        boolean sweep = humanoidType == HumanoidType.GUERRERO && (++meleeCombo % 3 == 0);
        playAction(sweep ? "attack_sweep" : "attack_slash");
        if (doHurtTarget(target) && sweep) {
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
        arrow.shoot(dx, dy + horizontal * 0.2, dz, 2.0f, 4.0f);
        arrow.setBaseDamage(humanoidType.damage * 0.6);
        arrow.pickup = AbstractArrow.Pickup.DISALLOWED;
        if (getRandom().nextInt(3) == 0) {
            arrow.setRemainingFireTicks(100); // flecha de rubí ardiente
        }
        level().addFreshEntity(arrow);
        playSound(SoundEvents.SKELETON_SHOOT, 1.0f, 1.0f / (getRandom().nextFloat() * 0.4f + 0.8f));
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
        // el Rey sin domesticar no se aleja de su trono
        if (humanoidType.isKing() && !isTame()) {
            if (home == null) {
                home = blockPosition();
            }
            if (!hasRestriction()) {
                restrictTo(home, 5);
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

        // Guerrero y Arquero: rubíes
        if (!humanoidType.isKing() && !isTame() && stack.is(ModItems.RUBY.get())) {
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

        // Reproducción (y curación si ya es tuyo): chuleta de cerdo asada
        if (isFood(stack)) {
            if (isTame() && getHealth() < getMaxHealth() && !isInLove()) {
                if (!client) {
                    stack.consume(1, player);
                    heal(6.0f);
                    level().broadcastEntityEvent(this, (byte) 7);
                }
                return InteractionResult.sidedSuccess(client);
            }
            InteractionResult breed = super.mobInteract(player, hand);
            if (breed.consumesAction()) {
                return breed;
            }
        }

        // Quedarse quieto / volver a seguir (clic derecho del dueño)
        if (isTame() && isOwnedBy(player)) {
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

    @Override
    public boolean isFood(ItemStack stack) {
        return humanoidType.canBreed() && stack.is(Items.COOKED_PORKCHOP);
    }

    @Override
    public boolean canMate(Animal other) {
        return other != this && other instanceof NetherHumanoidEntity mate
                && mate.humanoidType == this.humanoidType && isInLove() && mate.isInLove()
                && !isOrderedToSit() && !mate.isOrderedToSit();
    }

    @Nullable
    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob otherParent) {
        NetherHumanoidEntity baby = ModEntities.humanoid(humanoidType).create(level);
        if (baby != null && isTame() && getOwnerUUID() != null) {
            baby.setOwnerUUID(getOwnerUUID());
            baby.setTame(true, true);
        }
        return baby;
    }

    // ------------------------------------------------------------------ guardado
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("LifeTicks", lifeTicks);
        tag.putInt("ApplesFed", applesFed);
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
        return switch (humanoidType) {
            case SUBDITO_ALMA -> SoundEvents.VEX_AMBIENT;
            case REY_NECROMANCER -> SoundEvents.EVOKER_AMBIENT;
            default -> null;
        };
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return isSoul() ? SoundEvents.VEX_HURT : SoundEvents.PLAYER_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return isSoul() ? SoundEvents.VEX_DEATH : (humanoidType.isKing() ? SoundEvents.EVOKER_DEATH : SoundEvents.PLAYER_DEATH);
    }

    @Override
    public float getVoicePitch() {
        return isBaby() ? 1.5f : (humanoidType.isKing() ? 0.7f : 0.9f + getRandom().nextFloat() * 0.1f);
    }

    @Override
    public int getAmbientSoundInterval() {
        return 400;
    }

    // ------------------------------------------------------------------ GeckoLib
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        String p = humanoidType.animPrefix;
        RawAnimation idle = RawAnimation.begin().thenLoop(p + "idle");
        RawAnimation walk = RawAnimation.begin().thenLoop(p + "walk");
        RawAnimation run = RawAnimation.begin().thenLoop(p + (humanoidType.isKing() ? "walk" : "run"));
        RawAnimation sit = RawAnimation.begin().thenLoop(p + "sit");
        controllers.add(new AnimationController<>(this, "movement", 4, state -> {
            if (isInSittingPose()) {
                return state.setAndContinue(humanoidType.hasSitAnimation() ? sit : idle);
            }
            if (state.isMoving()) {
                return state.setAndContinue(isAggressive() ? run : walk);
            }
            return state.setAndContinue(idle);
        }));
        AnimationController<NetherHumanoidEntity> action = new AnimationController<>(this, "action", 2, state -> PlayState.STOP);
        String[] actions = switch (humanoidType) {
            case GUERRERO, SUBDITO_ALMA -> new String[]{"attack_slash", "attack_sweep", "tamed"};
            case ARQUERO -> new String[]{"attack_bow", "tamed"};
            case REY_NECROMANCER -> new String[]{"cast", "summon"};
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
