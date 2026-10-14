package com.civilizacionnether;

import com.civilizacionnether.registry.ModArmorMaterials;
import com.civilizacionnether.registry.ModBlocks;
import com.civilizacionnether.registry.ModCreativeTabs;
import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModItems;
import com.civilizacionnether.registry.ModParticles;
import com.civilizacionnether.registry.ModStructures;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Civilización del Nether: humanos del Nether aliados del jugador, dragones domesticables
 * y la capital del Reino del Nether.
 */
@Mod(CivilizacionNether.MODID)
public class CivilizacionNether {
    public static final String MODID = "civilizacion_nether";
    public static final Logger LOGGER = LoggerFactory.getLogger(MODID);

    public CivilizacionNether(IEventBus modBus, ModContainer container) {
        ModBlocks.BLOCKS.register(modBus);
        ModArmorMaterials.ARMOR_MATERIALS.register(modBus);
        ModEntities.ENTITIES.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModParticles.PARTICLES.register(modBus);
        ModStructures.STRUCTURE_TYPES.register(modBus);
        ModStructures.PIECES.register(modBus);
        ModCreativeTabs.TABS.register(modBus);
        LOGGER.info("Civilización del Nether cargada");
    }

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MODID, path);
    }
}
