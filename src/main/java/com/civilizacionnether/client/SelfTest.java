package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.gui.screens.AccessibilityOnboardingScreen;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.LevelSettings;
import net.minecraft.world.level.WorldDataConfiguration;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.ScreenEvent;

import java.util.ArrayList;
import java.util.List;

/**
 * Prueba automática (sólo para la compilación en GitHub; en el juego normal no hace nada): con
 * -Dcivilizacion_nether.selftest=true crea un mundo, hace aparecer todas las criaturas del mod (y aldeanos)
 * en el mundo normal, el Nether y el End, saca fotos y cierra el juego. Si algo se cae, queda el reporte.
 */
@EventBusSubscriber(modid = CivilizacionNether.MODID, value = Dist.CLIENT)
public final class SelfTest {
    private static final boolean ON = Boolean.getBoolean("civilizacion_nether.selftest");
    private static boolean started;
    private static int tick;
    private static int step;
    private static final List<String> TYPES = new ArrayList<>();

    @SubscribeEvent
    public static void screen(ScreenEvent.Init.Post event) {
        if (!ON || started) {
            return;
        }
        if (event.getScreen() instanceof TitleScreen || event.getScreen() instanceof AccessibilityOnboardingScreen) {
            started = true;
            Minecraft mc = Minecraft.getInstance();
            mc.execute(() -> {
                LevelSettings settings = new LevelSettings("prueba", GameType.CREATIVE, false, Difficulty.NORMAL, true,
                        new GameRules(), WorldDataConfiguration.DEFAULT);
                mc.createWorldOpenFlows().createFreshLevel("prueba", settings, new WorldOptions(12345L, true, false),
                        reg -> reg.lookupOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).value().createWorldDimensions(),
                        new TitleScreen());
            });
        }
    }

    private static void cmd(String c) {
        Minecraft mc = Minecraft.getInstance();
        MinecraftServer server = mc.getSingleplayerServer();
        if (server == null || mc.player == null) {
            return;
        }
        server.execute(() -> {
            var p = server.getPlayerList().getPlayer(mc.player.getUUID());
            if (p != null) {
                server.getCommands().performPrefixedCommand(p.createCommandSourceStack().withPermission(4).withSuppressedOutput(), c);
            }
        });
        CivilizacionNether.LOGGER.info("SELFTEST cmd: {}", c);
    }

    private static void shot(String name) {
        Minecraft mc = Minecraft.getInstance();
        Screenshot.grab(mc.gameDirectory, name + ".png", mc.getMainRenderTarget(), m -> CivilizacionNether.LOGGER.info("SELFTEST foto {}", name));
    }

    /** Arma una pileta de agua y un piso, y pone todas las criaturas en fila delante de la cámara. */
    private static void stage(String dim, String block) {
        String in = "execute in " + dim + " run ";
        // en el Nether la pileta es de lava (para ver que nadan en la lava); en el End, de agua del Nether
        String fluid = dim.endsWith("nether") ? "minecraft:lava" : dim.endsWith("end") ? "civilizacion_nether:nether_water" : "minecraft:water";
        cmd(in + "forceload add -32 -32 32 32");
        cmd(in + "fill -24 99 -4 24 112 30 minecraft:air");
        cmd(in + "fill -24 98 -4 24 98 30 " + block);
        cmd(in + "fill -25 88 13 25 98 31 minecraft:glass");
        cmd(in + "fill -24 89 14 24 98 30 " + fluid);
        cmd(in + "tp @s 0 106 -2 0 35");
        int i = 0;
        for (String t : TYPES) {
            boolean sea = t.matches(".*(pez|anguila|medusa|cangrejo|caballito|manta|tortuga|tiburon|serpiente|delfin|ballena).*");
            int x = -20 + (i % 11) * 4;
            int z = sea ? 18 + (i / 11) * 4 : 3 + (i / 11) * 3;
            String extra = sea ? "" : "";
            cmd(in + "summon " + t + " " + x + " " + (sea ? 93 : 99) + " " + z + extra);
            i++;
        }
        cmd(in + "summon minecraft:villager 6 99 9");
        cmd(in + "summon minecraft:villager 9 99 9 {VillagerData:{type:\"civilizacion_nether:nether\",profession:\"civilizacion_nether:albanil\",level:2}}");
        cmd(in + "summon minecraft:villager 12 99 9 {VillagerData:{type:\"civilizacion_nether:nether\",profession:\"minecraft:cleric\",level:2}}");
    }

    @SubscribeEvent
    public static void tick(ClientTickEvent.Post event) {
        if (!ON || !started) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.getSingleplayerServer() == null) {
            return;
        }
        tick++;
        if (TYPES.isEmpty()) {
            for (ResourceLocation id : BuiltInRegistries.ENTITY_TYPE.keySet()) {
                EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(id);
                if (CivilizacionNether.MODID.equals(id.getNamespace()) && type.getCategory() != MobCategory.MISC) {
                    TYPES.add(id.toString());
                }
            }
            TYPES.add("civilizacion_nether:dragon_egg");
            CivilizacionNether.LOGGER.info("SELFTEST criaturas: {}", TYPES);
            mc.options.hideGui = true;
            cmd("gamerule doDaylightCycle false");
            cmd("time set 6000");
            cmd("weather clear");
            cmd("gamemode spectator");
            cmd("gamerule mobGriefing false");
        }
        String[] dims = {"minecraft:overworld", "minecraft:the_nether", "minecraft:the_end"};
        String[] floors = {"minecraft:stone", "minecraft:netherrack", "minecraft:end_stone"};
        int phase = tick / 500;
        int t = tick % 500;
        if (phase == dims.length || phase == dims.length + 1) {
            seaBiome(mc, tick - dims.length * 500);
            return;
        }
        if (phase > dims.length + 1) {
            if (t == 1) {
                CivilizacionNether.LOGGER.info("SELFTEST terminado sin caerse");
                mc.stop();
            }
            return;
        }
        String d = dims[phase].substring(10);
        if (t > 60 && t % 40 == 0) {
            logStats(mc, dims[phase]);
        }
        if (t == 40) {
            stage(dims[phase], floors[phase]);
        } else if (t == 160 || t == 300 || t == 440) {
            shot(d + "_" + t);
        } else if (t == 230) {
            cmd("execute in " + dims[phase] + " run tp @s 0 100 8 0 15");
        } else if (t == 240) {
            shot(d + "_cerca");
        } else if (t == 250) {
            cmd("execute in " + dims[phase] + " run tp @s 0 98.5 10 0 10");
        } else if (t == 262) {
            shot(d + "_agua");
        } else if (t == 270) {
            cmd("execute in " + dims[phase] + " run tp @s 0 106 -2 0 35");
        } else if (t == 120) {
            babies(mc, dims[phase]);
        } else if (t == 130) {
            naturalSpawns(mc, dims[phase]);
        } else if (t == 490) {
            cmd("execute in " + dims[phase] + " run kill @e[type=!player]");
        }
    }

    /**
     * Simula la aparición natural en grupo (como el juego): a cada criatura del mod le pasa el evento y el dato del grupo
     * dos veces seguidas, igual que cuando aparece un cardumen o una manada. Así se ve si algo se cae al aparecer solo.
     */
    private static void naturalSpawns(Minecraft mc, String dim) {
        MinecraftServer server = mc.getSingleplayerServer();
        server.execute(() -> {
            var level = server.getLevel(net.minecraft.resources.ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(dim)));
            if (level == null) {
                return;
            }
            int i = 0;
            for (String t : TYPES) {
                EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.parse(t));
                net.minecraft.world.entity.SpawnGroupData data = null;
                for (int k = 0; k < 2; k++) {
                    var e = type.create(level);
                    if (!(e instanceof net.minecraft.world.entity.Mob mob)) {
                        break;
                    }
                    mob.moveTo(-20 + (i % 11) * 4, 93, 22 + k, 0, 0);
                    data = net.neoforged.neoforge.event.EventHooks.finalizeMobSpawn(mob, level,
                            level.getCurrentDifficultyAt(mob.blockPosition()), net.minecraft.world.entity.MobSpawnType.NATURAL, data);
                    level.addFreshEntity(mob);
                }
                i++;
            }
            CivilizacionNether.LOGGER.info("SELFTEST aparicion natural en grupo ok en {}", dim);
        });
    }

    /** Vuelve crías a algunas criaturas del mar para verlas en las fotos. */
    private static void babies(Minecraft mc, String dim) {
        MinecraftServer server = mc.getSingleplayerServer();
        server.execute(() -> {
            var level = server.getLevel(net.minecraft.resources.ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(dim)));
            if (level == null) {
                return;
            }
            for (var e : level.getAllEntities()) {
                if (e instanceof net.minecraft.world.entity.Mob m && com.civilizacionnether.entity.sea.SeaFamily.food(m) != null
                        && m.getId() % 2 == 0) {
                    com.civilizacionnether.entity.sea.SeaFamily.makeBaby(m);
                    CivilizacionNether.LOGGER.info("SELFTEST cria {}", BuiltInRegistries.ENTITY_TYPE.getKey(m.getType()));
                }
            }
        });
    }

    private static net.minecraft.core.BlockPos seaPos;

    /** Visita el Mar del Nether alrededor del Reino (en un Nether normal) y saca fotos. */
    private static void seaBiome(Minecraft mc, int t) {
        MinecraftServer server = mc.getSingleplayerServer();
        if (t == 20) {
            server.execute(() -> {
                var nether = server.getLevel(net.minecraft.world.level.Level.NETHER);
                var p = nether.findNearestMapStructure(net.minecraft.tags.TagKey.create(Registries.STRUCTURE, CivilizacionNether.id("capitales")),
                        net.minecraft.core.BlockPos.ZERO, 50, false);
                CivilizacionNether.LOGGER.info("SELFTEST reino en {}", p);
                seaPos = p;
            });
        }
        if (seaPos == null) {
            return;
        }
        int x = seaPos.getX();
        int z = seaPos.getZ();
        // fotos: afuera del reino (el bioma), y el reino desde arriba
        int[][] views = {{x + 130, 72, z + 10, 90, 20}, {x - 20, 70, z - 140, 200, 15}, {x + 90, 66, z + 120, 135, 15},
                         {x, 62, z - 110, 0, 12}};
        for (int i = 0; i < views.length; i++) {
            int[] v = views[i];
            if (t == 40 + i * 220) {
                cmd("execute in minecraft:the_nether run tp @s " + v[0] + " " + v[1] + " " + v[2] + " " + v[3] + " " + v[4]);
            } else if (t == 40 + i * 220 + 200) {
                shot(i == 3 ? "reino" : "mar_del_nether_" + i);
                logBlocks(mc);
            }
        }
        if (t > 60 && t % 100 == 0) {
            logStats(mc, "minecraft:the_nether");
        }
    }

    /** Anota dónde está y hacia dónde mira cada criatura (para ver si alguna gira sin parar o se queda trabada). */
    private static void logStats(Minecraft mc, String dim) {
        MinecraftServer server = mc.getSingleplayerServer();
        server.execute(() -> {
            var key = net.minecraft.resources.ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(dim));
            var level = server.getLevel(key);
            if (level == null) {
                return;
            }
            for (var e : level.getAllEntities()) {
                ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(e.getType());
                if (e instanceof net.minecraft.world.entity.LivingEntity le && (CivilizacionNether.MODID.equals(id.getNamespace())
                        || id.getPath().equals("villager"))) {
                    CivilizacionNether.LOGGER.info(String.format(java.util.Locale.ROOT,
                            "SELFTEST stat %s %s id=%d pos=%.1f,%.1f,%.1f yaw=%.1f body=%.1f pitch=%.1f water=%s ground=%s hp=%.0f",
                            dim, id.getPath(), e.getId(), e.getX(), e.getY(), e.getZ(), e.getYRot(), le.yBodyRot, e.getXRot(),
                            e.isInWater(), e.onGround(), le.getHealth()));
                }
            }
        });
    }

    /** Cuenta los bloques del bioma alrededor (para saber si el pasto, la hierba y los árboles aparecieron). */
    private static void logBlocks(Minecraft mc) {
        MinecraftServer server = mc.getSingleplayerServer();
        if (seaPos == null) {
            return;
        }
        server.execute(() -> {
            var nether = server.getLevel(net.minecraft.world.level.Level.NETHER);
            java.util.Map<String, Integer> count = new java.util.TreeMap<>();
            var c = mc.player.blockPosition();
            for (int x = -40; x <= 40; x++) {
                for (int z = -40; z <= 40; z++) {
                    for (int y = 8; y < 120; y++) {
                        var p = new net.minecraft.core.BlockPos(c.getX() + x, y, c.getZ() + z);
                        if (!nether.isLoaded(p)) {
                            continue;
                        }
                        var id = BuiltInRegistries.BLOCK.getKey(nether.getBlockState(p).getBlock());
                        if (CivilizacionNether.MODID.equals(id.getNamespace()) || id.getPath().equals("ancient_debris")
                                || id.getPath().equals("nether_gold_ore") || id.getPath().equals("nether_quartz_ore")) {
                            count.merge(id.getPath(), 1, Integer::sum);
                        }
                    }
                }
            }
            CivilizacionNether.LOGGER.info("SELFTEST bloques del bioma: {}", count);
        });
    }

    private SelfTest() {
    }
}
