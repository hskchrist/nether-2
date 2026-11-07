package com.civilizacionnether.entity.ai;

import com.civilizacionnether.entity.NetherHumanoidEntity;
import com.civilizacionnether.registry.ModPoiTypes;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.village.poi.PoiManager;
import net.minecraft.world.entity.ai.village.poi.PoiType;
import net.minecraft.world.level.block.Block;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;
import java.util.Optional;

/**
 * De día, cada profesión va a su mesa de trabajo (atril, nido, cesto, carrito o la mesa del necromancer),
 * se para frente a ella y trabaja un rato con su animación.
 */
public class WorkAtStationGoal extends Goal {
    private final NetherHumanoidEntity mob;
    @Nullable
    private BlockPos station;
    private int workTicks;
    private int timeout;

    public WorkAtStationGoal(NetherHumanoidEntity mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Nullable
    private Block stationBlock() {
        String id = mob.getHumanoidType().workstation;
        return id == null ? null : BuiltInRegistries.BLOCK.get(com.civilizacionnether.CivilizacionNether.id(id));
    }

    @Override
    public boolean canUse() {
        if (mob.isTame() || mob.isBaby() || mob.isSleeping() || mob.getTarget() != null || mob.isRestTime()
                || mob.getTradingPlayer() != null || mob.getRandom().nextInt(200) != 0
                || !(mob.level() instanceof ServerLevel server)) {
            return false;
        }
        station = find(server);
        return station != null;
    }

    @Nullable
    private BlockPos find(ServerLevel server) {
        Block block = stationBlock();
        if (block == null) {
            return null;
        }
        ResourceKey<PoiType> key = ModPoiTypes.keyFor(mob.getHumanoidType().workstation);
        if (key != null) {
            Optional<BlockPos> p = server.getPoiManager().findClosest((Holder<PoiType> h) -> h.is(key), mob.blockPosition(), 24,
                    PoiManager.Occupancy.ANY);
            if (p.isPresent()) {
                return p.get();
            }
        }
        BlockPos from = mob.blockPosition();
        BlockPos best = null;
        double bestD = Double.MAX_VALUE;
        for (BlockPos p : BlockPos.betweenClosed(from.offset(-10, -3, -10), from.offset(10, 3, 10))) {
            if (server.getBlockState(p).is(block)) {
                double d = p.distSqr(from);
                if (d < bestD) {
                    bestD = d;
                    best = p.immutable();
                }
            }
        }
        return best;
    }

    @Override
    public void start() {
        workTicks = 160 + mob.getRandom().nextInt(200);
        timeout = 400;
        if (station != null) {
            mob.getNavigation().moveTo(station.getX() + 0.5, station.getY(), station.getZ() + 0.5, 0.75);
        }
    }

    @Override
    public boolean canContinueToUse() {
        return station != null && workTicks > 0 && timeout > 0 && mob.getTarget() == null && !mob.isSleeping()
                && mob.getTradingPlayer() == null && mob.level().getBlockState(station).is(stationBlockOr());
    }

    private Block stationBlockOr() {
        Block b = stationBlock();
        return b == null ? net.minecraft.world.level.block.Blocks.AIR : b;
    }

    @Override
    public void tick() {
        if (station == null) {
            return;
        }
        double d = mob.distanceToSqr(station.getX() + 0.5, station.getY() + 0.5, station.getZ() + 0.5);
        mob.getLookControl().setLookAt(station.getX() + 0.5, station.getY() + 0.7, station.getZ() + 0.5);
        if (d < 4.5) {
            mob.getNavigation().stop();
            mob.setWorking(true);
            workTicks--;
        } else {
            timeout--;
            mob.setWorking(false);
            if (mob.getNavigation().isDone()) {
                mob.getNavigation().moveTo(station.getX() + 0.5, station.getY(), station.getZ() + 0.5, 0.75);
            }
        }
    }

    @Override
    public void stop() {
        mob.setWorking(false);
        station = null;
    }
}
