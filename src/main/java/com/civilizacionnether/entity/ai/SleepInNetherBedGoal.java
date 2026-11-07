package com.civilizacionnether.entity.ai;

import com.civilizacionnether.block.NetherBedBlock;
import com.civilizacionnether.entity.NetherHumanoidEntity;
import com.civilizacionnether.registry.ModPoiTypes;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.village.poi.PoiManager;
import net.minecraft.world.entity.ai.village.poi.PoiTypes;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BedPart;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;
import java.util.Optional;

/**
 * En la hora de dormir (10 minutos) los humanos sin dueño caminan a la cama del Nether libre más cercana y se acuestan.
 * Se despiertan solos al terminar la noche, si los atacan o si les quitan la cama (NetherHumanoidEntity.tick).
 */
public class SleepInNetherBedGoal extends Goal {
    private final NetherHumanoidEntity mob;
    @Nullable
    private BlockPos bed;
    private int timeout;
    private int cooldown;

    public SleepInNetherBedGoal(NetherHumanoidEntity mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        if (cooldown > 0) {
            cooldown--;
            return false;
        }
        if (mob.isTame() || mob.isSleeping() || mob.getTarget() != null || !mob.isRestTime() || mob.isPassenger()
                || !(mob.level() instanceof ServerLevel server)) {
            return false;
        }
        cooldown = 40 + mob.getRandom().nextInt(40);
        bed = findFreeBed(server, mob.blockPosition(), 32);
        return bed != null;
    }

    @Override
    public void start() {
        timeout = 600;
        moveToBed();
    }

    private void moveToBed() {
        if (bed != null) {
            mob.getNavigation().moveTo(bed.getX() + 0.5, bed.getY(), bed.getZ() + 0.5, 0.8);
        }
    }

    @Override
    public boolean canContinueToUse() {
        return bed != null && !mob.isSleeping() && mob.isRestTime() && mob.getTarget() == null && timeout > 0
                && isFreeBedHead(mob.level().getBlockState(bed));
    }

    @Override
    public void tick() {
        timeout--;
        if (bed == null) {
            return;
        }
        double d = mob.distanceToSqr(bed.getX() + 0.5, bed.getY() + 0.5, bed.getZ() + 0.5);
        if (d < 3.2) {
            mob.getNavigation().stop();
            mob.startSleeping(bed);
        } else if (mob.getNavigation().isDone()) {
            moveToBed();
        }
    }

    @Override
    public void stop() {
        bed = null;
    }

    public static boolean isFreeBedHead(BlockState s) {
        return s.getBlock() instanceof NetherBedBlock && s.getValue(NetherBedBlock.PART) == BedPart.HEAD
                && !s.getValue(NetherBedBlock.OCCUPIED);
    }

    @Nullable
    public static BlockPos findFreeBed(ServerLevel level, BlockPos from, int radius) {
        Optional<BlockPos> poi = level.getPoiManager().findClosest(h -> h.is(ModPoiTypes.NETHER_BED.getKey()) || h.is(PoiTypes.HOME),
                p -> isFreeBedHead(level.getBlockState(p)), from, radius, PoiManager.Occupancy.ANY);
        if (poi.isPresent()) {
            return poi.get();
        }
        // respaldo: búsqueda directa de bloques cerca
        BlockPos best = null;
        double bestD = Double.MAX_VALUE;
        int r = Math.min(radius, 12);
        for (BlockPos p : BlockPos.betweenClosed(from.offset(-r, -3, -r), from.offset(r, 3, r))) {
            if (isFreeBedHead(level.getBlockState(p))) {
                double d = p.distSqr(from);
                if (d < bestD) {
                    bestD = d;
                    best = p.immutable();
                }
            }
        }
        return best;
    }

    public static long countBedsNear(ServerLevel level, BlockPos from, int r) {
        long n = 0;
        for (BlockPos p : BlockPos.betweenClosed(from.offset(-r, -3, -r), from.offset(r, 3, r))) {
            BlockState s = level.getBlockState(p);
            if (s.getBlock() instanceof NetherBedBlock && s.getValue(NetherBedBlock.PART) == BedPart.HEAD) {
                n++;
            }
        }
        return n;
    }
}
