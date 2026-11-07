package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.block.NetherBedBlock;
import com.google.common.collect.ImmutableSet;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.ai.village.poi.PoiType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BedPart;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import org.jetbrains.annotations.Nullable;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/** Puntos de interés: camas del Nether (cabecera) y mesas de trabajo, para que los humanos las encuentren rápido. */
public final class ModPoiTypes {
    public static final DeferredRegister<PoiType> POI_TYPES = DeferredRegister.create(Registries.POINT_OF_INTEREST_TYPE, CivilizacionNether.MODID);
    private static final Map<String, DeferredHolder<PoiType, PoiType>> BY_STATION = new HashMap<>();

    public static final DeferredHolder<PoiType, PoiType> NETHER_BED = POI_TYPES.register("nether_bed", () -> new PoiType(
            ModBlocks.NETHER_BED.get().getStateDefinition().getPossibleStates().stream()
                    .filter(s -> s.getValue(NetherBedBlock.PART) == BedPart.HEAD).collect(Collectors.toUnmodifiableSet()), 1, 1));

    // sitios de trabajo de las 5 profesiones nuevas de los aldeanos del Nether (un aldeano por mesa, como en vanilla)
    public static final DeferredHolder<PoiType, PoiType> CARTOGRAPHER_DESK = job("cartographer_desk", ModBlocks.CARTOGRAPHER_DESK);
    public static final DeferredHolder<PoiType, PoiType> FLETCHER_BENCH = job("fletcher_bench", ModBlocks.FLETCHER_BENCH);
    public static final DeferredHolder<PoiType, PoiType> LEATHER_CAULDRON = job("leather_cauldron", ModBlocks.LEATHER_CAULDRON);
    public static final DeferredHolder<PoiType, PoiType> SHEPHERD_LOOM = job("shepherd_loom", ModBlocks.SHEPHERD_LOOM);
    public static final DeferredHolder<PoiType, PoiType> MASON_CUTTER = job("mason_cutter", ModBlocks.MASON_CUTTER);

    static {
        station("necromancer_table", ModBlocks.NECROMANCER_TABLE);
        station("librarian_lectern", ModBlocks.LIBRARIAN_LECTERN);
        station("tamer_nest", ModBlocks.TAMER_NEST);
        station("farmer_basket", ModBlocks.FARMER_BASKET);
        station("miner_cart", ModBlocks.MINER_CART);
    }

    private static void station(String name, DeferredBlock<? extends Block> block) {
        BY_STATION.put(name, POI_TYPES.register(name, () -> new PoiType(allStates(block.get()), 4, 1)));
    }

    private static DeferredHolder<PoiType, PoiType> job(String name, DeferredBlock<? extends Block> block) {
        return POI_TYPES.register(name, () -> new PoiType(allStates(block.get()), 1, 1));
    }

    private static Set<BlockState> allStates(Block block) {
        return ImmutableSet.copyOf(block.getStateDefinition().getPossibleStates());
    }

    @Nullable
    public static ResourceKey<PoiType> keyFor(@Nullable String station) {
        DeferredHolder<PoiType, PoiType> h = station == null ? null : BY_STATION.get(station);
        return h == null ? null : h.getKey();
    }

    private ModPoiTypes() {
    }
}
