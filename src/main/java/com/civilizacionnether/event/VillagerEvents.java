package com.civilizacionnether.event;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.block.NetherBedBlock;
import com.civilizacionnether.entity.NetherVillagers;
import com.civilizacionnether.registry.ModBlocks;
import com.civilizacionnether.registry.ModVillagers;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.entity.ai.village.poi.PoiType;
import net.minecraft.world.entity.ai.village.poi.PoiTypes;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.entity.npc.VillagerData;
import net.minecraft.world.entity.npc.VillagerProfession;
import net.minecraft.world.entity.npc.VillagerTrades;
import net.minecraft.world.entity.npc.VillagerType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BedPart;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.village.VillagerTradesEvent;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

/** Aldeanos del Nether: tipo Nether al estar en el Nether, intercambios de las profesiones nuevas y camas del Nether. */
@EventBusSubscriber(modid = CivilizacionNether.MODID)
public final class VillagerEvents {

    /** Los aldeanos que aparecen, nacen, se curan o llegan por un portal al Nether se vuelven aldeanos del Nether. */
    @SubscribeEvent
    public static void joinLevel(EntityJoinLevelEvent event) {
        if (event.getLevel().isClientSide() || !(event.getEntity() instanceof Villager villager)
                || event.getLevel().dimension() != Level.NETHER) {
            return;
        }
        VillagerType nether = ModVillagers.NETHER.get();
        VillagerData data = villager.getVillagerData();
        if (data.getType() != nether) {
            villager.setVillagerData(data.setType(nether));
        }
    }

    /** Las 5 profesiones nuevas intercambian lo mismo que su profesión vanilla (cartógrafo, flechero, peletero, pastor, albañil). */
    @SubscribeEvent
    public static void trades(VillagerTradesEvent event) {
        VillagerProfession from = NetherVillagers.tradesFrom(event.getType());
        if (from == null) {
            return;
        }
        Int2ObjectMap<VillagerTrades.ItemListing[]> vanilla = VillagerTrades.TRADES.get(from);
        if (vanilla == null) {
            return;
        }
        for (Int2ObjectMap.Entry<VillagerTrades.ItemListing[]> e : vanilla.int2ObjectEntrySet()) {
            List<VillagerTrades.ItemListing> level = event.getTrades().get(e.getIntKey());
            if (level != null) {
                level.addAll(Arrays.asList(e.getValue()));
            }
        }
    }

    @EventBusSubscriber(modid = CivilizacionNether.MODID, bus = EventBusSubscriber.Bus.MOD)
    public static final class ModBus {
        @SubscribeEvent
        public static void setup(FMLCommonSetupEvent event) {
            event.enqueueWork(ModBus::netherBedsAreHomes);
        }

        /**
         * La cabecera de la cama del Nether pasa a ser un "hogar" vanilla: así los aldeanos la reclaman, duermen en ella
         * y pueden tener hijos. Los humanos del mod la siguen encontrando (buscan los dos tipos).
         * Si alguna versión de NeoForge no deja cambiarlo, el mod sigue funcionando: sólo que los aldeanos no usan esas camas.
         */
        @SuppressWarnings("unchecked")
        private static void netherBedsAreHomes() {
            Holder<PoiType> home = BuiltInRegistries.POINT_OF_INTEREST_TYPE.getHolderOrThrow(PoiTypes.HOME);
            List<Map<BlockState, Holder<PoiType>>> maps = new ArrayList<>();
            try {
                Field f = PoiTypes.class.getDeclaredField("TYPE_BY_STATE");
                f.setAccessible(true);
                Object o = f.get(null);
                if (o instanceof Map<?, ?> m) {
                    maps.add((Map<BlockState, Holder<PoiType>>) m);
                }
            } catch (Throwable ignored) {
                // NeoForge puede guardar el mapa en otro lado
            }
            try {
                Method m = Class.forName("net.neoforged.neoforge.registries.GameData").getMethod("getBlockStatePointOfInterestTypeMap");
                Object o = m.invoke(null);
                if (o instanceof Map<?, ?> map && maps.stream().noneMatch(x -> x == map)) {
                    maps.add((Map<BlockState, Holder<PoiType>>) map);
                }
            } catch (Throwable ignored) {
                // no existe en esta versión
            }
            int done = 0;
            for (BlockState s : ModBlocks.NETHER_BED.get().getStateDefinition().getPossibleStates()) {
                if (s.getValue(NetherBedBlock.PART) != BedPart.HEAD) {
                    continue;
                }
                for (Map<BlockState, Holder<PoiType>> map : maps) {
                    try {
                        map.put(s, home);
                        done++;
                    } catch (Throwable ignored) {
                        // mapa de sólo lectura
                    }
                }
            }
            CivilizacionNether.LOGGER.info("Camas del Nether como hogar de aldeanos: {} estados en {} mapas", done, maps.size());
        }
    }

    private VillagerEvents() {
    }
}
