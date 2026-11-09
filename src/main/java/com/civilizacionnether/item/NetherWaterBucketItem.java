package com.civilizacionnether.item;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.LiquidBlockContainer;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.FlowingFluid;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

/**
 * Balde de agua del Nether: el agua morada es del Nether, así que en el Nether (y en cualquier lugar caliente) NO se
 * evapora al vaciar el balde, a diferencia del agua normal. Sirve para hacer ríos, lagos y piscinas allá.
 */
public class NetherWaterBucketItem extends BucketItem {
    private final Fluid fluid;

    public NetherWaterBucketItem(Fluid fluid, Properties properties) {
        super(fluid, properties);
        this.fluid = fluid;
    }

    // (sin @Override: según la versión de NeoForge el juego llama a uno u otro)
    public boolean emptyContents(@Nullable Player player, Level level, BlockPos pos, @Nullable BlockHitResult hit, @Nullable ItemStack container) {
        return place(player, level, pos, hit);
    }

    public boolean emptyContents(@Nullable Player player, Level level, BlockPos pos, @Nullable BlockHitResult hit) {
        return place(player, level, pos, hit);
    }

    private boolean place(@Nullable Player player, Level level, BlockPos pos, @Nullable BlockHitResult hit) {
        if (!(fluid instanceof FlowingFluid flowing)) {
            return false;
        }
        BlockState state = level.getBlockState(pos);
        boolean replaceable = state.canBeReplaced(fluid);
        boolean container = state.getBlock() instanceof LiquidBlockContainer c && c.canPlaceLiquid(player, level, pos, state, fluid);
        if (!state.isAir() && !replaceable && !container) {
            return hit != null && place(player, level, hit.getBlockPos().relative(hit.getDirection()), null);
        }
        if (container) {
            ((LiquidBlockContainer) state.getBlock()).placeLiquid(level, pos, state, flowing.getSource(false));
            playEmptySound(player, level, pos);
            return true;
        }
        if (!level.isClientSide && replaceable && !state.liquid()) {
            level.destroyBlock(pos, true);
        }
        if (!level.setBlock(pos, fluid.defaultFluidState().createLegacyBlock(), 11) && !state.getFluidState().isSource()) {
            return false;
        }
        playEmptySound(player, level, pos);
        return true;
    }
}
