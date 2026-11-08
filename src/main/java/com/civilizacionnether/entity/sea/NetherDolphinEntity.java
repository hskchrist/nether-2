package com.civilizacionnether.entity.sea;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.Dolphin;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Delfín del Nether: igual que el delfín normal (anda en grupos de 3, te da Gracia del Delfín al nadar a su lado,
 * salta fuera del agua) y además:
 * <ul>
 *   <li>Si le das un Pez Brasa te guía nadando hasta el Reino Humano.</li>
 *   <li>Ataca a los Tiburones Infernales (y ellos a él).</li>
 * </ul>
 */
public class NetherDolphinEntity extends Dolphin implements GeoEntity {
    private static final String P = "animation.delfin_nether.";
    private static final RawAnimation SWIM = RawAnimation.begin().thenLoop(P + "swim");
    private static final RawAnimation JUMP = RawAnimation.begin().thenPlayAndHold(P + "jump");
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    public NetherDolphinEntity(EntityType<? extends NetherDolphinEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createNetherAttributes() {
        return Dolphin.createAttributes()
                .add(Attributes.MAX_HEALTH, 16.0)
                .add(Attributes.ATTACK_DAMAGE, 5.0);
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, InfernalSharkEntity.class, 10, true, false, null));
    }

    @Override
    public boolean isInWater() {
        return super.isInWater() || SeaLife.inNetherWater(this) || isInLava();
    }

    @Override
    public boolean doHurtTarget(Entity target) {
        triggerAnim("action", "ram");
        return super.doHurtTarget(target);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "move", 4, state -> state.setAndContinue(isInWater() ? SWIM : JUMP)));
        controllers.add(new AnimationController<>(this, "action", 2, state -> PlayState.STOP)
                .triggerableAnim("ram", RawAnimation.begin().thenPlay(P + "ram")));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
