package com.civilizacionnether.event;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.NetherDragonEntity;
import com.civilizacionnether.entity.NetherHumanoidEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.NeutralMob;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;

/**
 * Los mobs hostiles ven a los humanos del Nether y a los aldeanos igual que al jugador: los buscan para matarlos.
 * Los humanos ya atacan a todos los hostiles, así que se pelean a muerte. (Los neutrales, como los piglins zombi y los
 * enderman, siguen igual: solo atacan si los provocan.)
 */
@EventBusSubscriber(modid = CivilizacionNether.MODID)
public final class HostileEvents {
    @SubscribeEvent
    public static void join(EntityJoinLevelEvent event) {
        if (event.getLevel().isClientSide() || !(event.getEntity() instanceof Mob mob) || !(mob instanceof Enemy)
                || mob instanceof NeutralMob || mob instanceof NetherHumanoidEntity || mob instanceof NetherDragonEntity) {
            return;
        }
        mob.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(mob, NetherHumanoidEntity.class, true,
                h -> h instanceof NetherHumanoidEntity n && !n.getHumanoidType().isSoul()));
        mob.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(mob, AbstractVillager.class, true));
    }

    private HostileEvents() {
    }
}
