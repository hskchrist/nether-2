package com.civilizacionnether.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BedPart;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

/**
 * Cama del Nether: dos bloques como la cama normal, pero NO explota en el Nether.
 * El jugador se acuesta y queda guardado su punto de reaparición (puede quedarse acostado lo que quiera).
 * Los humanos del reino duermen en ella 10 minutos cada noche.
 */
public class NetherBedBlock extends HorizontalDirectionalBlock {
    public static final MapCodec<NetherBedBlock> CODEC = simpleCodec(NetherBedBlock::new);
    public static final EnumProperty<BedPart> PART = BlockStateProperties.BED_PART;
    public static final BooleanProperty OCCUPIED = BlockStateProperties.OCCUPIED;
    private static final VoxelShape SHAPE = Block.box(0, 0, 0, 16, 9, 16);

    public NetherBedBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH).setValue(PART, BedPart.FOOT).setValue(OCCUPIED, false));
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, PART, OCCUPIED);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    private static Direction neighbourDirection(BedPart part, Direction facing) {
        return part == BedPart.FOOT ? facing : facing.getOpposite();
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext ctx) {
        Direction dir = ctx.getHorizontalDirection();
        BlockPos head = ctx.getClickedPos().relative(dir);
        Level level = ctx.getLevel();
        return level.getBlockState(head).canBeReplaced(ctx) && level.getWorldBorder().isWithinBounds(head)
                ? defaultBlockState().setValue(FACING, dir) : null;
    }

    @Override
    public void setPlacedBy(Level level, BlockPos pos, BlockState state, @Nullable LivingEntity placer, ItemStack stack) {
        super.setPlacedBy(level, pos, state, placer, stack);
        if (!level.isClientSide) {
            BlockPos head = pos.relative(state.getValue(FACING));
            level.setBlock(head, state.setValue(PART, BedPart.HEAD), 3);
            level.blockUpdated(pos, Blocks.AIR);
            state.updateNeighbourShapes(level, pos, 3);
        }
    }

    @Override
    protected BlockState updateShape(BlockState state, Direction dir, BlockState neighbor, LevelAccessor level,
                                     BlockPos pos, BlockPos neighborPos) {
        if (dir == neighbourDirection(state.getValue(PART), state.getValue(FACING))) {
            return neighbor.is(this) && neighbor.getValue(PART) != state.getValue(PART)
                    ? state.setValue(OCCUPIED, neighbor.getValue(OCCUPIED)) : Blocks.AIR.defaultBlockState();
        }
        return super.updateShape(state, dir, neighbor, level, pos, neighborPos);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.CONSUME;
        }
        if (state.getValue(PART) != BedPart.HEAD) {
            pos = pos.relative(state.getValue(FACING));
            state = level.getBlockState(pos);
            if (!state.is(this)) {
                return InteractionResult.CONSUME;
            }
        }
        if (state.getValue(OCCUPIED)) {
            player.displayClientMessage(Component.translatable("block.minecraft.bed.occupied"), true);
            return InteractionResult.SUCCESS;
        }
        if (player instanceof ServerPlayer sp) {
            sp.setRespawnPosition(level.dimension(), pos, sp.getYRot(), true, false);
            sp.startSleeping(pos);
            sp.displayClientMessage(Component.translatable("msg.civilizacion_nether.bed_spawn"), true);
        }
        return InteractionResult.SUCCESS;
    }

    // ---- Neoforge: es una cama (para dormir, la orientación del durmiente y la ocupación)
    // (sin @Override: según la versión de NeoForge el último parámetro es LivingEntity o Entity; las dos versiones sirven)
    public boolean isBed(BlockState state, BlockGetter level, BlockPos pos, @Nullable LivingEntity sleeper) {
        return true;
    }

    public boolean isBed(BlockState state, BlockGetter level, BlockPos pos, @Nullable net.minecraft.world.entity.Entity sleeper) {
        return true;
    }

    public void setBedOccupied(BlockState state, Level level, BlockPos pos, LivingEntity sleeper, boolean occupied) {
        if (state.is(this)) {
            level.setBlock(pos, state.setValue(OCCUPIED, occupied), 3);
        }
    }

    /** Reaparecer: se puede aparecer sobre la cama aunque estés en el Nether. */
    @Override
    public boolean isPossibleToRespawnInThis(BlockState state) {
        return true;
    }
}
