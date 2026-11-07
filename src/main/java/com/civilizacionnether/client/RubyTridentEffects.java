package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.network.RubyTridentPayload;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrownTrident;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;

/**
 * Fuego del Tridente de Rubí: chispas y llamitas saliendo de la mano de quien lo lleva (más al apuntar para lanzarlo)
 * y una estela de fuego cuando vuela.
 */
@EventBusSubscriber(modid = CivilizacionNether.MODID, value = Dist.CLIENT)
public final class RubyTridentEffects {

    @SubscribeEvent
    public static void tick(ClientTickEvent.Post event) {
        Minecraft mc = Minecraft.getInstance();
        ClientLevel level = mc.level;
        if (level == null || mc.isPaused() || mc.player == null) {
            return;
        }
        RandomSource r = level.getRandom();
        Vec3 cam = mc.player.position();
        for (Entity e : level.entitiesForRendering()) {
            if (e.distanceToSqr(cam) > 48 * 48) {
                continue;
            }
            if (e instanceof ThrownTrident t && RubyTridentPayload.RUBY_TRIDENTS.contains(t.getId())) {
                trail(level, t, r);
            } else if (e instanceof LivingEntity le && !le.isInvisible()) {
                for (InteractionHand hand : InteractionHand.values()) {
                    if (le.getItemInHand(hand).is(ModItems.RUBY_TRIDENT.get())) {
                        held(mc, level, le, hand, r);
                    }
                }
            }
        }
    }

    private static void trail(ClientLevel level, ThrownTrident t, RandomSource r) {
        Vec3 v = t.getDeltaMovement();
        boolean flying = v.lengthSqr() > 0.01;
        if (t.isInWaterOrRain()) {
            return;
        }
        int n = flying ? 3 : (r.nextInt(4) == 0 ? 1 : 0);
        for (int i = 0; i < n; i++) {
            double k = r.nextDouble();
            level.addParticle(ParticleTypes.FLAME, t.getX() - v.x * k, t.getY() - v.y * k + 0.1, t.getZ() - v.z * k,
                    (r.nextDouble() - 0.5) * 0.03, 0.01, (r.nextDouble() - 0.5) * 0.03);
        }
        if (flying && r.nextInt(3) == 0) {
            level.addParticle(ParticleTypes.SMOKE, t.getX(), t.getY() + 0.1, t.getZ(), 0.0, 0.01, 0.0);
        }
    }

    private static void held(Minecraft mc, ClientLevel level, LivingEntity le, InteractionHand hand, RandomSource r) {
        boolean charging = le.isUsingItem() && le.getUsedItemHand() == hand;
        if (!charging && r.nextInt(3) != 0) {
            return;
        }
        HumanoidArm arm = hand == InteractionHand.MAIN_HAND ? le.getMainArm() : le.getMainArm().getOpposite();
        double side = arm == HumanoidArm.RIGHT ? 1.0 : -1.0;
        Vec3 pos;
        boolean firstPerson = le == mc.player && mc.options.getCameraType() == CameraType.FIRST_PERSON;
        if (firstPerson) {
            // primera persona: abajo a la derecha de la vista, donde se ve el tridente
            Vec3 look = le.getViewVector(1.0f);
            Vec3 right = new Vec3(-look.z, 0.0, look.x).normalize().scale(side);
            pos = le.getEyePosition().add(look.scale(0.7)).add(right.scale(0.32)).add(0.0, -0.18 + r.nextDouble() * 0.25, 0.0);
        } else {
            float yaw = le.yBodyRot * Mth.DEG_TO_RAD;
            Vec3 forward = new Vec3(-Mth.sin(yaw), 0.0, Mth.cos(yaw));
            Vec3 right = new Vec3(-Mth.cos(yaw), 0.0, -Mth.sin(yaw)).scale(side);
            double s = le.getScale();
            // a lo largo del tridente: de la mano hacia las puntas
            double up = charging ? 1.6 + r.nextDouble() * 0.6 : 0.8 + r.nextDouble() * 0.9;
            pos = le.position().add(right.scale(0.38 * s)).add(forward.scale((charging ? -0.1 : 0.25) * s)).add(0.0, up * s, 0.0);
        }
        double dx = (r.nextDouble() - 0.5) * 0.12;
        double dz = (r.nextDouble() - 0.5) * 0.12;
        level.addParticle(r.nextInt(3) == 0 ? ParticleTypes.FLAME : ParticleTypes.SMALL_FLAME,
                pos.x + dx, pos.y, pos.z + dz, 0.0, 0.015 + r.nextDouble() * 0.02, 0.0);
        if (charging && r.nextInt(2) == 0) {
            level.addParticle(ParticleTypes.LAVA, pos.x, pos.y, pos.z, 0.0, 0.0, 0.0);
        }
    }

    private RubyTridentEffects() {
    }
}
