package com.civilizacionnether.item;

import com.civilizacionnether.client.NecroStaffRenderer;
import com.civilizacionnether.entity.NetherHumanoidEntity;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.ChatFormatting;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.client.GeoRenderProvider;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;

/**
 * Báculo del Rey Necromancer (modelo 3D con orbe de rubí que gira y brilla).
 * <ul>
 *   <li>Clic derecho: rayo de almas que daña y quema al primer objetivo en la mira.</li>
 *   <li>Mayús + clic derecho: invoca 2 Súbditos de Almas que te defienden durante 30 segundos.</li>
 * </ul>
 */
public class NecroStaffItem extends Item implements GeoItem {
    public static final double RANGE = 26.0;
    private static final RawAnimation ORB = RawAnimation.begin().thenLoop("animation.necro_staff.orb");
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public NecroStaffItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.isSecondaryUseActive()) {
            if (level instanceof ServerLevel server) {
                for (int i = 0; i < 2; i++) {
                    NetherHumanoidEntity soul = NetherHumanoidEntity.spawnSoul(server, player, player.getX(), player.getY(), player.getZ());
                    if (soul != null) {
                        soul.tame(player);
                    }
                }
                level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.EVOKER_PREPARE_SUMMON, SoundSource.PLAYERS, 1.0f, 0.9f);
                stack.hurtAndBreak(5, player, LivingEntity.getSlotForHand(hand));
            }
            player.getCooldowns().addCooldown(this, 600);
        } else {
            if (level instanceof ServerLevel server) {
                castBolt(server, player);
                stack.hurtAndBreak(1, player, LivingEntity.getSlotForHand(hand));
            }
            player.getCooldowns().addCooldown(this, 15);
        }
        player.swing(hand);
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    private static void castBolt(ServerLevel level, Player player) {
        Vec3 start = player.getEyePosition();
        Vec3 end = start.add(player.getLookAngle().scale(RANGE));
        HitResult blockHit = level.clip(new ClipContext(start, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
        if (blockHit.getType() != HitResult.Type.MISS) {
            end = blockHit.getLocation();
        }
        LivingEntity best = null;
        double bestDist = Double.MAX_VALUE;
        AABB area = new AABB(start, end).inflate(1.5);
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, area,
                e -> e != player && e.isAlive() && !e.isAlliedTo(player)
                        && !(e instanceof NetherHumanoidEntity h && h.isTame() && h.isOwnedBy(player)))) {
            Optional<Vec3> hit = e.getBoundingBox().inflate(0.3).clip(start, end);
            if (hit.isPresent()) {
                double d = start.distanceToSqr(hit.get());
                if (d < bestDist) {
                    bestDist = d;
                    best = e;
                }
            }
        }
        if (best != null) {
            end = best.getBoundingBox().getCenter();
            best.hurt(level.damageSources().indirectMagic(player, player), 9.0f);
            best.setRemainingFireTicks(60);
        }
        NetherHumanoidEntity.soulBolt(level, start.add(0, -0.2, 0), end);
        level.playSound(null, player.getX(), player.getY(), player.getZ(), SoundEvents.EVOKER_CAST_SPELL, SoundSource.PLAYERS, 0.9f, 1.1f);
    }

    @Override
    public boolean isValidRepairItem(ItemStack stack, ItemStack repair) {
        return repair.is(ModItems.RUBY.get());
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.civilizacion_nether.necro_staff").withStyle(ChatFormatting.RED));
        tooltip.add(Component.translatable("tooltip.civilizacion_nether.necro_staff_summon").withStyle(ChatFormatting.AQUA));
    }

    // ------------------------------------------------------------------ GeckoLib
    @Override
    public void createGeoRenderer(Consumer<GeoRenderProvider> consumer) {
        consumer.accept(new GeoRenderProvider() {
            private NecroStaffRenderer renderer;

            @Override
            public BlockEntityWithoutLevelRenderer getGeoItemRenderer() {
                if (this.renderer == null) {
                    this.renderer = new NecroStaffRenderer();
                }
                return this.renderer;
            }
        });
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "orb", 0, state -> state.setAndContinue(ORB)));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
