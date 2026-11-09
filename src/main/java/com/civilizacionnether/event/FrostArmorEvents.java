package com.civilizacionnether.event;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Armadura del Frío Eterno (set completo): no te quemas en la lava, caminas, corres y nadas rápido dentro de ella.
 * (La visión clara y sin fuego en la cara bajo la lava está en ClientEvents.)
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
        // moverse bajo la lava: lo calcula el juego del jugador (en el servidor no hay teclas)
        if ((p.isInLava() || inNetherWater(p)) && p.level().isClientSide() && p.isLocalPlayer() && !p.getAbilities().flying) {
            lavaMove(p);
        }
        if (p.isInLava()) {
            p.resetFallDistance();
        }
    }

    /**
     * Bajo la lava se camina, se corre y se nada casi como en el agua: con W hacia adelante (más rápido corriendo),
     * espacio para subir, Shift para bajar, y corriendo con la vista bajo la lava se nada hacia donde miras.
     */
    private static boolean inNetherWater(Player p) {
        return p.isInFluidType(com.civilizacionnether.registry.ModFluids.NETHER_WATER_TYPE.get());
    }

    private static void lavaMove(Player p) {
        Vec3 v = p.getDeltaMovement();
        float fwd = p.zza;
        float str = p.xxa;
        float yaw = p.getYRot() * Mth.DEG_TO_RAD;
        double sin = Mth.sin(yaw);
        double cos = Mth.cos(yaw);
        double wx = str * cos - fwd * sin;
        double wz = fwd * cos + str * sin;
        double len = Math.sqrt(wx * wx + wz * wz);
        if (len > 1.0) {
            wx /= len;
            wz /= len;
        }
        boolean eyesIn = p.isEyeInFluid(FluidTags.LAVA) || p.isEyeInFluidType(com.civilizacionnether.registry.ModFluids.NETHER_WATER_TYPE.get());
        boolean swimming = p.isSprinting() && fwd > 0 && eyesIn;
        // rápido: caminando como corriendo en tierra, y corriendo casi el doble
        double speed = p.isSprinting() ? 0.50 : 0.28;
        double vy;
        if (swimming) {
            // nadar: hacia donde miras, como en el agua
            Vec3 look = p.getLookAngle();
            double flat = Math.sqrt(Math.max(0.0, 1.0 - look.y * look.y));
            wx *= flat;
            wz *= flat;
            vy = look.y * speed;
        } else if (p.isShiftKeyDown()) {
            vy = -0.15;
        } else if (v.y > 0.0) {
            vy = Math.min(0.28, v.y * 2.0 + 0.02);   // espacio: subir rápido
        } else {
            vy = Math.max(-0.08, v.y);                // se hunde despacio
        }
        double nx = Mth.lerp(0.5, v.x, wx * speed);
        double nz = Mth.lerp(0.5, v.z, wz * speed);
        p.setDeltaMovement(nx, Mth.lerp(0.5, v.y, vy), nz);
    }

    private FrostArmorEvents() {
    }
}
