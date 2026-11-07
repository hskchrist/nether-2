package com.civilizacionnether.event;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Armadura del Frío Eterno (set completo): no te quemas en la lava, nadas y te mueves rápido dentro de ella.
 * (La visión perfecta bajo la lava está en ClientEvents, en la niebla.)
 */
@EventBusSubscriber(modid = CivilizacionNether.MODID)
public final class FrostArmorEvents {

    public static boolean hasFullFrost(LivingEntity e) {
        return e.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.FROST_HELMET.get())
                && e.getItemBySlot(EquipmentSlot.CHEST).is(ModItems.FROST_CHESTPLATE.get())
                && e.getItemBySlot(EquipmentSlot.LEGS).is(ModItems.FROST_LEGGINGS.get())
                && e.getItemBySlot(EquipmentSlot.FEET).is(ModItems.FROST_BOOTS.get());
    }

    @SubscribeEvent
    public static void tick(PlayerTickEvent.Post event) {
        Player p = event.getEntity();
        if (!hasFullFrost(p)) {
            return;
        }
        if (p.isInLava() || p.isOnFire()) {
            p.clearFire();
            if (!p.level().isClientSide && (p.getEffect(MobEffects.FIRE_RESISTANCE) == null
                    || p.getEffect(MobEffects.FIRE_RESISTANCE).getDuration() < 40)) {
                p.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 100, 0, true, false, true));
            }
        }
        if (p.isInLava()) {
            // nadar en la lava como en el agua: más rápido y con control para subir y bajar
            Vec3 v = p.getDeltaMovement();
            double hx = v.x * 1.35;
            double hz = v.z * 1.35;
            double h = Math.sqrt(hx * hx + hz * hz);
            double max = p.isSprinting() ? 0.42 : 0.3;
            if (h > max) {
                hx = hx / h * max;
                hz = hz / h * max;
            }
            double vy = v.y;
            if (p.isShiftKeyDown()) {
                vy -= 0.03;
            }
            p.setDeltaMovement(hx, vy, hz);
            p.resetFallDistance();
        }
    }

    private FrostArmorEvents() {
    }
}
