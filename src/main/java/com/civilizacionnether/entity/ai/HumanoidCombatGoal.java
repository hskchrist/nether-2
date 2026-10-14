package com.civilizacionnether.entity.ai;

import com.civilizacionnether.entity.HumanoidType;
import com.civilizacionnether.entity.NetherHumanoidEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/**
 * Combate de la civilización: el Guerrero y los Súbditos pelean cuerpo a cuerpo, el Arquero dispara con su arco
 * de rubí manteniendo la distancia y el Rey Necromancer lanza rayos de almas e invoca súbditos.
 */
public class HumanoidCombatGoal extends Goal {
    private final NetherHumanoidEntity mob;
    private int cooldown;
    private int windup;
    private int repath;

    public HumanoidCombatGoal(NetherHumanoidEntity mob) {
        this.mob = mob;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean canUse() {
        LivingEntity target = mob.getTarget();
        return target != null && target.isAlive() && !mob.isOrderedToSit();
    }

    @Override
    public boolean canContinueToUse() {
        return canUse() && mob.canAttack(mob.getTarget());
    }

    @Override
    public void start() {
        mob.setAggressive(true);
        windup = 0;
        repath = 0;
    }

    @Override
    public void stop() {
        mob.setAggressive(false);
        mob.getNavigation().stop();
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public void tick() {
        LivingEntity target = mob.getTarget();
        if (target == null) {
            return;
        }
        HumanoidType type = mob.getHumanoidType();
        mob.getLookControl().setLookAt(target, 30.0f, 30.0f);
        double distSq = mob.distanceToSqr(target);
        boolean sees = mob.getSensing().hasLineOfSight(target);
        if (cooldown > 0) {
            cooldown--;
        }

        // carga de los ataques a distancia (sincronizada con la animación)
        if (windup > 0) {
            mob.getNavigation().stop();
            if (--windup == 0 && target.isAlive() && sees) {
                if (type.combat == HumanoidType.Combat.BOW) {
                    mob.shootArrow(target);
                } else {
                    mob.castBolt(target);
                }
            }
            return;
        }

        if (type.combat == HumanoidType.Combat.MELEE) {
            double reach = mob.getBbWidth() * 2.0 + target.getBbWidth();
            if (--repath <= 0) {
                repath = 6 + mob.getRandom().nextInt(4);
                mob.getNavigation().moveTo(target, 1.2);
            }
            if (distSq <= reach * reach && cooldown <= 0) {
                cooldown = type.attackCooldown;
                mob.performMelee(target);
            }
            return;
        }

        // Rey: invoca súbditos cuando entra en combate y luego cada 20 segundos
        if (mob.canSummon() && sees && distSq < 24.0 * 24.0) {
            mob.summonSouls(target);
            cooldown = Math.max(cooldown, 30);
            return;
        }

        // A distancia: acercarse hasta tener línea de visión a ~14 bloques; retroceder si está muy cerca
        double ideal = 14.0;
        if (!sees || distSq > ideal * ideal) {
            if (--repath <= 0) {
                repath = 8;
                mob.getNavigation().moveTo(target, 1.15);
            }
        } else if (distSq < 25.0) {
            if (--repath <= 0) {
                repath = 10;
                double dx = mob.getX() - target.getX();
                double dz = mob.getZ() - target.getZ();
                mob.getNavigation().moveTo(mob.getX() + dx, mob.getY(), mob.getZ() + dz, 1.15);
            }
        } else {
            mob.getNavigation().stop();
        }

        if (sees && distSq < 20.0 * 20.0 && cooldown <= 0) {
            cooldown = type.attackCooldown;
            if (type.combat == HumanoidType.Combat.BOW) {
                mob.playAction("attack_bow");
                windup = 16;
            } else {
                mob.playAction("cast");
                windup = 10;
            }
        }
    }
}
