package com.civilizacionnether.entity.sea;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.living.FinalizeSpawnEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.EntityTickEvent;
import org.jetbrains.annotations.Nullable;

/**
 * Familias del mar del Nether:
 * <ul>
 *   <li>Crías y apareamiento para las criaturas que no son animales normales (delfín, tiburón, manta, ballena, peces,
 *   medusa y serpiente): se les da su comida, se buscan, y nace una cría chica que crece en 20 minutos y sigue a los
 *   grandes. El caballito, la tortuga y el cangrejo ya se aparean como animales normales (con Pez Brasa).</li>
 *   <li>Grupos al aparecer: caballito con 4 crías, 2 mantas con 1 cría, delfines de 3 a 5 con 2 crías, tiburón solo
 *   (a veces con una cría) y, rara vez, ballena con su cría.</li>
 *   <li>En la lava nadan igual que en el agua: buscan solos por dónde ir (los caminos normales sólo sirven en agua).</li>
 *   <li>Delfines (y ballenas en la lava) saltan fuera de la superficie.</li>
 * </ul>
 */
@EventBusSubscriber(modid = CivilizacionNether.MODID)
public final class SeaFamily {
    private static final ResourceLocation BABY = CivilizacionNether.id("cria");
    private static final String AGE = "CNAge";
    private static final String LOVE = "CNLove";
    private static final String COOLDOWN = "CNBreedCooldown";
    private static final int GROW_TIME = 24000;

    /** Comida que los pone en celo (null = no usa este sistema). */
    @Nullable
    public static Item food(Entity e) {
        if (e instanceof NetherDolphinEntity || e instanceof InfernalSharkEntity) {
            return ModItems.PEZ_BRASA.get();
        }
        if (e instanceof CrimsonMantaEntity || e instanceof BlueWhaleEntity) {
            return ModItems.VOID_GEL.get();
        }
        if (e instanceof NetherFishEntity) {
            return net.minecraft.world.item.Items.NETHER_WART;
        }
        if (e instanceof VoidJellyfishEntity) {
            return net.minecraft.world.item.Items.GLOWSTONE_DUST;
        }
        if (e instanceof SeaSerpentEntity) {
            return ModItems.COOKED_PEZ_BRASA.get();
        }
        return null;
    }

    public static boolean isBaby(Entity e) {
        if (e instanceof AgeableMob a) {
            return a.isBaby();
        }
        if (e instanceof Mob m) {
            AttributeInstance scale = m.getAttribute(Attributes.SCALE);
            return scale != null && scale.hasModifier(BABY);
        }
        return false;
    }

    /** La vuelve cría (chica). */
    public static void makeBaby(Mob m) {
        if (m instanceof AgeableMob a) {
            a.setAge(-GROW_TIME);
            return;
        }
        m.getPersistentData().putInt(AGE, -GROW_TIME);
        AttributeInstance scale = m.getAttribute(Attributes.SCALE);
        if (scale != null && !scale.hasModifier(BABY)) {
            scale.addPermanentModifier(new AttributeModifier(BABY, m instanceof BlueWhaleEntity ? -0.65 : -0.55,
                    AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
        }
    }

    private static void growUp(Mob m) {
        m.getPersistentData().remove(AGE);
        AttributeInstance scale = m.getAttribute(Attributes.SCALE);
        if (scale != null) {
            scale.removeModifier(BABY);
        }
    }

    // ------------------------------------------------------------------ darles de comer
    @SubscribeEvent
    public static void feed(PlayerInteractEvent.EntityInteract event) {
        Entity target = event.getTarget();
        Item food = food(target);
        Player player = event.getEntity();
        ItemStack stack = event.getItemStack();
        if (food == null || !stack.is(food) || !(target instanceof Mob mob) || isBaby(mob)) {
            return;
        }
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.sidedSuccess(event.getLevel().isClientSide));
        if (event.getLevel().isClientSide) {
            return;
        }
        CompoundTag data = mob.getPersistentData();
        if (data.getInt(LOVE) > 0 || data.getInt(COOLDOWN) > 0) {
            return;
        }
        stack.consume(1, player);
        data.putInt(LOVE, 600);
        mob.playSound(SoundEvents.GENERIC_EAT, 1.0f, 1.2f);
        if (mob.level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.HEART, mob.getX(), mob.getY() + mob.getBbHeight(), mob.getZ(), 6, 0.4, 0.3, 0.4, 0.0);
        }
    }

    // ------------------------------------------------------------------ cada tick
    @SubscribeEvent
    public static void tick(EntityTickEvent.Post event) {
        if (!(event.getEntity() instanceof Mob mob) || mob.level().isClientSide || !isSeaCreature(mob) || !mob.isAlive()) {
            return;
        }
        lavaSwim(mob);
        surfaceJumps(mob);
        if (food(mob) == null) {
            return;
        }
        CompoundTag data = mob.getPersistentData();
        // crecer
        if (data.contains(AGE)) {
            int age = data.getInt(AGE) + 1;
            if (age >= 0) {
                growUp(mob);
            } else {
                data.putInt(AGE, age);
                if (mob.tickCount % 20 == 0) {
                    followParent(mob);
                    if (mob instanceof InfernalSharkEntity) {
                        mob.setTarget(null); // las crías de tiburón no atacan
                    }
                }
            }
        }
        if (data.getInt(COOLDOWN) > 0) {
            data.putInt(COOLDOWN, data.getInt(COOLDOWN) - 1);
        }
        int love = data.getInt(LOVE);
        if (love > 0) {
            data.putInt(LOVE, love - 1);
            if (mob.tickCount % 10 == 0 && mob.level() instanceof ServerLevel server) {
                server.sendParticles(ParticleTypes.HEART, mob.getX(), mob.getY() + mob.getBbHeight(), mob.getZ(), 1, 0.3, 0.2, 0.3, 0.0);
            }
            if (mob.tickCount % 5 == 0) {
                findPartner(mob);
            }
        }
    }

    private static boolean isSeaCreature(Mob mob) {
        return mob.getClass().getPackageName().equals(SeaFamily.class.getPackageName());
    }

    private static void followParent(Mob baby) {
        Mob parent = null;
        double best = 24 * 24;
        for (Mob m : baby.level().getEntitiesOfClass(Mob.class, baby.getBoundingBox().inflate(24.0),
                m -> m != baby && m.getType() == baby.getType() && !isBaby(m))) {
            double d = m.distanceToSqr(baby);
            if (d < best) {
                best = d;
                parent = m;
            }
        }
        if (parent != null && best > 25.0) {
            baby.getMoveControl().setWantedPosition(parent.getX(), parent.getY(), parent.getZ(), 1.2);
        }
    }

    private static void findPartner(Mob mob) {
        for (Mob other : mob.level().getEntitiesOfClass(Mob.class, mob.getBoundingBox().inflate(12.0),
                m -> m != mob && m.getType() == mob.getType() && !isBaby(m) && m.getPersistentData().getInt(LOVE) > 0)) {
            double reach = mob.getBbWidth() + 2.0;
            if (mob.distanceToSqr(other) > reach * reach) {
                mob.getMoveControl().setWantedPosition(other.getX(), other.getY(), other.getZ(), 1.0);
                return;
            }
            // ¡nace una cría!
            mob.getPersistentData().putInt(LOVE, 0);
            other.getPersistentData().putInt(LOVE, 0);
            mob.getPersistentData().putInt(COOLDOWN, 6000);
            other.getPersistentData().putInt(COOLDOWN, 6000);
            if (mob.level() instanceof ServerLevel server) {
                Entity e = mob.getType().create(server);
                if (e instanceof Mob baby) {
                    Vec3 mid = mob.position().add(other.position()).scale(0.5);
                    baby.moveTo(mid.x, mid.y, mid.z, mob.getYRot(), 0.0f);
                    makeBaby(baby);
                    baby.setPersistenceRequired();
                    server.addFreshEntity(baby);
                    server.sendParticles(ParticleTypes.HEART, mid.x, mid.y + 1.0, mid.z, 8, 0.6, 0.4, 0.6, 0.0);
                    server.addFreshEntity(new ExperienceOrb(server, mid.x, mid.y, mid.z, 1 + mob.getRandom().nextInt(7)));
                }
            }
            return;
        }
    }

    /** En la lava: los caminos no sirven, así que eligen solos un punto de lava cercano y nadan hacia él. */
    private static void lavaSwim(Mob mob) {
        if (!mob.isInLava() || mob instanceof BlueWhaleEntity || mob instanceof SeaSerpentEntity) {
            return; // la ballena y la serpiente ya nadan sin caminos
        }
        if (mob.getTarget() != null && mob.tickCount % 10 == 0) {
            Entity t = mob.getTarget();
            mob.getMoveControl().setWantedPosition(t.getX(), t.getY(0.5), t.getZ(), 1.3);
            return;
        }
        // cada 2 segundos, si no avanza (el camino no sirve en la lava), elige solo a dónde nadar
        if (mob.tickCount % 40 != 0 || mob.getDeltaMovement().lengthSqr() > 0.0025) {
            return;
        }
        mob.getNavigation().stop();
        for (int i = 0; i < 8; i++) {
            BlockPos p = mob.blockPosition().offset(mob.getRandom().nextInt(17) - 8, mob.getRandom().nextInt(7) - 3,
                    mob.getRandom().nextInt(17) - 8);
            if (mob.level().getFluidState(p).is(FluidTags.LAVA)) {
                mob.getMoveControl().setWantedPosition(p.getX() + 0.5, p.getY() + 0.3, p.getZ() + 0.5, 1.0);
                return;
            }
        }
    }

    /** Delfines: a veces saltan fuera de la superficie (en el agua y en la lava), como los de verdad. */
    private static void surfaceJumps(Mob mob) {
        if (!(mob instanceof NetherDolphinEntity) || !mob.isInWater() || mob.getRandom().nextInt(180) != 0) {
            return;
        }
        BlockPos head = BlockPos.containing(mob.getX(), mob.getY() + mob.getBbHeight() + 0.6, mob.getZ());
        if (!mob.level().getFluidState(head).isEmpty() || !mob.level().getBlockState(head).isAir()) {
            return; // no está en la superficie
        }
        Vec3 dir = mob.getDeltaMovement().horizontalDistanceSqr() > 1.0E-4
                ? mob.getDeltaMovement().multiply(1, 0, 1).normalize() : Vec3.directionFromRotation(0, mob.getYRot());
        mob.setDeltaMovement(dir.x * 0.6, 0.75, dir.z * 0.6);
        mob.hurtMarked = true;
        mob.playSound(mob.isInLava() ? SoundEvents.LAVA_POP : SoundEvents.DOLPHIN_JUMP, 1.0f, 1.0f);
        if (mob.level() instanceof ServerLevel server) {
            server.sendParticles(mob.isInLava() ? ParticleTypes.LAVA : ParticleTypes.SPLASH, mob.getX(), mob.getY() + 0.5, mob.getZ(),
                    mob.isInLava() ? 8 : 30, 0.4, 0.2, 0.4, 0.1);
        }
    }

    // ------------------------------------------------------------------ grupos al aparecer

    @SubscribeEvent
    public static void groups(FinalizeSpawnEvent event) {
        MobSpawnType reason = event.getSpawnType();
        if (reason != MobSpawnType.NATURAL && reason != MobSpawnType.CHUNK_GENERATION) {
            return;
        }
        Mob mob = event.getEntity();
        if (!isSeaCreature(mob)) {
            return;
        }
        // ¿es el primero del grupo? (no se toca el dato del grupo: los peces usan el suyo para el cardumen)
        // si ya hay crías de su especie justo al lado, otro del grupo ya las trajo
        ServerLevelAccessor lvl = event.getLevel();
        boolean first = lvl.getEntitiesOfClass(Mob.class, new net.minecraft.world.phys.AABB(event.getX() - 10, event.getY() - 6,
                event.getZ() - 10, event.getX() + 10, event.getY() + 6, event.getZ() + 10),
                m -> m != mob && m.getType() == mob.getType() && isBaby(m)).isEmpty();
        var rnd = mob.getRandom();
        int babies = 0;
        if (mob instanceof MagmaSeahorseEntity) {
            babies = 4;
        } else if (mob instanceof CrimsonMantaEntity) {
            // al generarse el mundo no se ven los otros del grupo: se reparte al azar (en promedio 1 cría)
            babies = reason == MobSpawnType.CHUNK_GENERATION ? (rnd.nextBoolean() ? 1 : 0) : (first ? 1 : 0);
        } else if (mob instanceof NetherDolphinEntity) {
            babies = reason == MobSpawnType.CHUNK_GENERATION ? (rnd.nextFloat() < 0.45f ? 1 : 0) : (first ? 2 : 0);
        } else if (mob instanceof InfernalSharkEntity && rnd.nextFloat() < 0.3f) {
            babies = 1;
        } else if (mob instanceof BlueWhaleEntity && rnd.nextFloat() < 0.15f) {
            babies = 1;
        }
        ServerLevelAccessor level = event.getLevel();
        for (int i = 0; i < babies; i++) {
            Entity e = mob.getType().create(level.getLevel());
            if (e instanceof Mob baby) {
                float a = rnd.nextFloat() * Mth.TWO_PI;
                double r = mob.getBbWidth() * 0.6 + 0.8;
                baby.moveTo(event.getX() + Mth.cos(a) * r, event.getY(), event.getZ() + Mth.sin(a) * r, rnd.nextFloat() * 360.0f, 0.0f);
                if (!level.noCollision(baby)) {
                    baby.moveTo(event.getX(), event.getY(), event.getZ(), rnd.nextFloat() * 360.0f, 0.0f);
                }
                makeBaby(baby);
                level.addFreshEntity(baby);
            }
        }
    }

    private SeaFamily() {
    }
}
