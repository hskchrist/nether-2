package com.civilizacionnether.entity;

import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModItems;
import com.civilizacionnether.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.UUID;

/**
 * Huevo de Dragón del Nether puesto en el suelo.
 * <ul>
 *   <li>Se incuba 5 minutos (el doble de rápido con lava, magma o fuego a 2 bloques) y nace una cría del dueño.</li>
 *   <li>Golpearlo lo recoge como ítem. Clic derecho: muestra cuánto falta (o lo adopta si no tiene dueño).</li>
 *   <li>Se tambalea cada vez más a medida que se acerca la eclosión.</li>
 * </ul>
 */
public class DragonEggEntity extends Mob implements GeoEntity {
    public static final int HATCH_TIME = 6000;
    private static final String P = "animation.nether_dragon_egg.";
    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop(P + "idle");

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    @Nullable
    private UUID owner;
    private int incubation;
    private int hatchTimer = -1;
    private boolean heated;

    public DragonEggEntity(EntityType<? extends DragonEggEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 10.0)
                .add(Attributes.MOVEMENT_SPEED, 0.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
    }

    public void setOwner(@Nullable UUID owner) {
        this.owner = owner;
    }

    @Override
    protected void registerGoals() {
        // un huevo no hace nada por su cuenta
    }

    // ------------------------------------------------------------------ incubación
    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide || !(level() instanceof ServerLevel server)) {
            return;
        }
        if (hatchTimer >= 0) {
            if (hatchTimer % 5 == 0) {
                server.sendParticles(ModParticles.BLACK_FLAME.get(), getX(), getY() + 0.6, getZ(), 6, 0.25, 0.3, 0.25, 0.02);
            }
            if (--hatchTimer < 0) {
                hatch(server);
            }
            return;
        }
        if (owner == null) {
            return; // huevo salvaje (nido de la capital): espera a que alguien lo adopte
        }
        if (tickCount % 20 == 0) {
            heated = isNearHeat();
        }
        incubation += heated ? 2 : 1;
        float progress = (float) incubation / HATCH_TIME;
        if (heated && tickCount % 10 == 0) {
            server.sendParticles(ParticleTypes.SMALL_FLAME, getX(), getY() + 0.2, getZ(), 1, 0.3, 0.1, 0.3, 0.0);
        }
        int wobbleEvery = progress > 0.85f ? 60 : progress > 0.6f ? 140 : progress > 0.35f ? 300 : 0;
        if (wobbleEvery > 0 && tickCount % wobbleEvery == 0) {
            triggerAnim("main", "wobble");
            playSound(SoundEvents.TURTLE_EGG_CRACK, 0.6f, 0.7f);
        }
        if (incubation >= HATCH_TIME) {
            hatchTimer = 20;
            triggerAnim("main", "hatch");
            playSound(SoundEvents.TURTLE_EGG_CRACK, 1.0f, 0.5f);
        }
    }

    private boolean isNearHeat() {
        BlockPos base = blockPosition();
        for (BlockPos p : BlockPos.betweenClosed(base.offset(-2, -1, -2), base.offset(2, 1, 2))) {
            BlockState s = level().getBlockState(p);
            if (s.is(Blocks.LAVA) || s.is(Blocks.MAGMA_BLOCK) || s.is(BlockTags.FIRE) || s.is(BlockTags.CAMPFIRES)) {
                return true;
            }
        }
        return false;
    }

    private void hatch(ServerLevel server) {
        NetherDragonEntity baby = ModEntities.NETHER_DRAGON.get().create(server);
        if (baby != null) {
            baby.moveTo(getX(), getY(), getZ(), getYRot(), 0.0f);
            if (owner != null) {
                baby.setTame(true, true);
                baby.setOwnerUUID(owner);
                baby.addBond(20);
            }
            baby.setGrowth(0.0f);
            baby.setHealth(baby.getMaxHealth());
            baby.setPersistenceRequired();
            server.addFreshEntity(baby);
            Player p = owner != null ? server.getPlayerByUUID(owner) : null;
            if (p != null) {
                p.displayClientMessage(Component.translatable("msg.civilizacion_nether.egg_hatched"), false);
            }
        }
        server.sendParticles(ModParticles.RED_SOUL.get(), getX(), getY() + 0.5, getZ(), 12, 0.3, 0.4, 0.3, 0.03);
        server.sendParticles(ParticleTypes.LAVA, getX(), getY() + 0.5, getZ(), 6, 0.3, 0.3, 0.3, 0.0);
        playSound(SoundEvents.TURTLE_EGG_HATCH, 1.0f, 0.6f);
        playSound(SoundEvents.ENDER_DRAGON_AMBIENT, 0.5f, 2.0f);
        discard();
    }

    // ------------------------------------------------------------------ interacción
    /** Golpearlo lo recoge (el huevo vuelve al inventario). Solo /kill y el vacío lo destruyen. */
    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (level().isClientSide) {
            return false;
        }
        if (source.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return super.hurt(source, amount);
        }
        Entity attacker = source.getEntity();
        if (attacker instanceof Player player && hatchTimer < 0) {
            ItemStack stack = new ItemStack(ModItems.DRAGON_EGG.get());
            if (!player.getInventory().add(stack)) {
                spawnAtLocation(stack);
            }
            playSound(SoundEvents.ITEM_PICKUP, 0.6f, 0.8f);
            discard();
            return true;
        }
        return false;
    }

    @Override
    protected InteractionResult mobInteract(Player player, InteractionHand hand) {
        if (level().isClientSide) {
            return InteractionResult.SUCCESS;
        }
        if (owner == null) {
            owner = player.getUUID();
            player.displayClientMessage(Component.translatable("msg.civilizacion_nether.egg_adopted"), true);
        } else {
            int left = Math.max(0, HATCH_TIME - incubation) / (heated ? 40 : 20);
            player.displayClientMessage(Component.translatable(
                    heated ? "msg.civilizacion_nether.egg_heat" : "msg.civilizacion_nether.egg_time", left), true);
        }
        return InteractionResult.CONSUME;
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    protected void doPush(Entity entity) {
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public boolean causeFallDamage(float fallDistance, float multiplier, DamageSource source) {
        return false;
    }

    // ------------------------------------------------------------------ guardado
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (owner != null) {
            tag.putUUID("EggOwner", owner);
        }
        tag.putInt("Incubation", incubation);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        owner = tag.hasUUID("EggOwner") ? tag.getUUID("EggOwner") : null;
        incubation = tag.getInt("Incubation");
    }

    // ------------------------------------------------------------------ GeckoLib
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 3, state -> state.setAndContinue(IDLE))
                .triggerableAnim("wobble", RawAnimation.begin().thenPlay(P + "wobble"))
                .triggerableAnim("hatch", RawAnimation.begin().thenPlay(P + "hatch")));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
