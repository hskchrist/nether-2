package com.civilizacionnether.event;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.InfernalDragonEntity;
import com.civilizacionnether.entity.NetherHumanoidEntity;
import com.civilizacionnether.network.RubyTridentPayload;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrownTrident;
import net.minecraft.world.item.alchemy.Potions;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.brewing.RegisterBrewingRecipesEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/** Pociones del mar, explosiones del Dragón Infernal domesticado y el Tridente de Rubí lanzado. */
@EventBusSubscriber(modid = CivilizacionNether.MODID)
public final class SeaEvents {

    /** Poción rara + Gel del Vacío = respiración acuática; + Caparazón de Basalto = maestro tortuga. */
    @SubscribeEvent
    public static void brewing(RegisterBrewingRecipesEvent event) {
        event.getBuilder().addMix(Potions.AWKWARD, ModItems.VOID_GEL.get(), Potions.WATER_BREATHING);
        event.getBuilder().addMix(Potions.AWKWARD, ModItems.BASALT_SHELL.get(), Potions.TURTLE_MASTER);
    }

    /** Las explosiones del Dragón Infernal domesticado no dañan a su jinete, a su dueño ni a los aliados. */
    @SubscribeEvent
    public static void protectAllies(LivingIncomingDamageEvent event) {
        if (!(event.getSource().getEntity() instanceof InfernalDragonEntity dragon) || !event.getSource().is(DamageTypeTags.IS_EXPLOSION)) {
            return;
        }
        LivingEntity victim = event.getEntity();
        if (victim == dragon || victim instanceof InfernalDragonEntity) {
            event.setCanceled(true);
            return;
        }
        if (dragon.isTame() && (dragon.hasPassenger(victim) || dragon.isOwnedBy(victim) || NetherHumanoidEntity.isAlly(victim))) {
            event.setCanceled(true);
        }
    }

    /** Cuando un jugador empieza a ver un tridente lanzado de rubí, se le avisa para dibujarlo con su color. */
    /** El Tridente de Rubí vuela en llamas; al clavarse se le apagan solas a los 3 segundos. Bajo el agua no arde. */
    @SubscribeEvent
    public static void burningTrident(net.neoforged.neoforge.event.tick.EntityTickEvent.Post event) {
        if (event.getEntity() instanceof ThrownTrident trident && !trident.level().isClientSide()
                && trident.getPickupItemStackOrigin().is(ModItems.RUBY_TRIDENT.get())) {
            if (trident.isInWaterOrRain()) {
                trident.clearFire();
            } else if (trident.getDeltaMovement().lengthSqr() > 0.01) {
                trident.setRemainingFireTicks(Math.max(trident.getRemainingFireTicks(), 60));
            }
        }
    }

    /** Lo que golpea el Tridente de Rubí lanzado se prende fuego (5 segundos), como con una flecha en llamas. */
    @SubscribeEvent
    public static void tridentBurns(net.neoforged.neoforge.event.entity.ProjectileImpactEvent event) {
        if (event.getProjectile() instanceof ThrownTrident trident && !trident.level().isClientSide()
                && trident.getPickupItemStackOrigin().is(ModItems.RUBY_TRIDENT.get())
                && event.getRayTraceResult() instanceof net.minecraft.world.phys.EntityHitResult hit
                && !hit.getEntity().fireImmune() && !hit.getEntity().isInWaterOrRain()) {
            hit.getEntity().igniteForSeconds(5.0f);
        }
    }

    @SubscribeEvent
    public static void startTracking(PlayerEvent.StartTracking event) {
        if (event.getTarget() instanceof ThrownTrident trident && event.getEntity() instanceof ServerPlayer player
                && trident.getPickupItemStackOrigin().is(ModItems.RUBY_TRIDENT.get())) {
            PacketDistributor.sendToPlayer(player, new RubyTridentPayload(trident.getId()));
        }
    }

    private SeaEvents() {
    }
}
