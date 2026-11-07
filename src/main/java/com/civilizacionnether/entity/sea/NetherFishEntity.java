package com.civilizacionnether.entity.sea;

import com.civilizacionnether.registry.ModEntities;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.AbstractSchoolingFish;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Peces del Océano Púrpura (misma clase, distinto tipo):
 * <ul>
 *   <li>Pez Brasa: nada en cardúmenes de hasta 6; se come (asado da resistencia al fuego) y es la comida de los delfines.</li>
 *   <li>Pez Alma: cardúmenes de 4, deja una estela de almas; a veces suelta un alma.</li>
 *   <li>Anguila de Rubí: rara y solitaria; a veces suelta un rubí.</li>
 * </ul>
 */
public class NetherFishEntity extends AbstractSchoolingFish implements GeoEntity {
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private final RawAnimation swim;
    private final RawAnimation flop;

    public NetherFishEntity(EntityType<? extends NetherFishEntity> type, Level level) {
        super(type, level);
        String id = BuiltInRegistries.ENTITY_TYPE.getKey(type).getPath();
        this.swim = RawAnimation.begin().thenLoop("animation." + id + ".swim");
        this.flop = RawAnimation.begin().thenLoop("animation." + id + ".flop");
    }

    public static AttributeSupplier.Builder createAttributes(double health) {
        return Mob.createMobAttributes().add(Attributes.MAX_HEALTH, health);
    }

    private boolean isSoulFish() {
        return getType() == ModEntities.PEZ_ALMA.get();
    }

    private boolean isEel() {
        return getType() == ModEntities.ANGUILA_RUBI.get();
    }

    @Override
    public int getMaxSchoolSize() {
        return isEel() ? 1 : isSoulFish() ? 4 : 6;
    }

    /** El agua del Nether también es agua para ellos (respiran y nadan). */
    @Override
    public boolean isInWater() {
        return super.isInWater() || SeaLife.inNetherWater(this);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (level().isClientSide && isSoulFish() && isInWater() && random.nextInt(6) == 0) {
            level().addParticle(ParticleTypes.SOUL, getRandomX(0.4), getY() + 0.2, getRandomZ(0.4), 0.0, 0.02, 0.0);
        }
    }

    /** No se recogen con balde (el agua del Nether no entra en el balde de agua normal). */
    @Override
    protected InteractionResult mobInteract(Player player, InteractionHand hand) {
        return InteractionResult.PASS;
    }

    @Override
    public ItemStack getBucketItemStack() {
        return new ItemStack(Items.WATER_BUCKET);
    }

    @Override
    protected SoundEvent getFlopSound() {
        return SoundEvents.COD_FLOP;
    }

    @Override
    protected SoundEvent getAmbientSound() {
        return SoundEvents.COD_AMBIENT;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.COD_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.COD_DEATH;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "move", 4, state -> state.setAndContinue(isInWater() ? swim : flop)));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
