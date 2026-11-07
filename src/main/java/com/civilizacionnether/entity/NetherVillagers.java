package com.civilizacionnether.entity;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.registry.ModVillagers;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.npc.VillagerData;
import net.minecraft.world.entity.npc.VillagerProfession;
import org.jetbrains.annotations.Nullable;

import java.util.HashMap;
import java.util.Map;

/** Qué skin lleva cada aldeano del Nether y de qué profesión vanilla copian sus intercambios las 5 profesiones nuevas. */
public final class NetherVillagers {
    private static final Map<VillagerProfession, String> VANILLA_SKINS = new HashMap<>();

    static {
        VANILLA_SKINS.put(VillagerProfession.BUTCHER, "carnicero");
        VANILLA_SKINS.put(VillagerProfession.FISHERMAN, "pescador");
        VANILLA_SKINS.put(VillagerProfession.CLERIC, "clerigo");
        VANILLA_SKINS.put(VillagerProfession.CARTOGRAPHER, "cartografo");
        VANILLA_SKINS.put(VillagerProfession.ARMORER, "armero");
        VANILLA_SKINS.put(VillagerProfession.TOOLSMITH, "herrero_herramientas");
        VANILLA_SKINS.put(VillagerProfession.WEAPONSMITH, "herrero_armas");
        VANILLA_SKINS.put(VillagerProfession.FLETCHER, "flechero");
        VANILLA_SKINS.put(VillagerProfession.LEATHERWORKER, "peletero");
        VANILLA_SKINS.put(VillagerProfession.SHEPHERD, "pastor");
        VANILLA_SKINS.put(VillagerProfession.MASON, "albanil");
    }

    /**
     * Nombre de la skin (textures/entity/villager/nether/NOMBRE.png) o null si el aldeano se dibuja como vanilla.
     * Las 5 profesiones del mod siempre llevan su skin; los aldeanos de tipo Nether llevan la de su profesión
     * (sin oficio, tonto, bibliotecario o granjero: la skin base del Aldeano del Nether).
     */
    @Nullable
    public static String skinName(VillagerData data) {
        VillagerProfession p = data.getProfession();
        ResourceLocation key = BuiltInRegistries.VILLAGER_PROFESSION.getKey(p);
        if (key != null && CivilizacionNether.MODID.equals(key.getNamespace())) {
            return key.getPath();
        }
        if (data.getType() != ModVillagers.NETHER.get()) {
            return null;
        }
        return VANILLA_SKINS.getOrDefault(p, "aldeano_nether");
    }

    /** Profesión vanilla cuyos intercambios copia una profesión del mod (null si no es del mod). */
    @Nullable
    public static VillagerProfession tradesFrom(VillagerProfession p) {
        if (p == ModVillagers.CARTOGRAFO.get()) {
            return VillagerProfession.CARTOGRAPHER;
        }
        if (p == ModVillagers.FLECHERO.get()) {
            return VillagerProfession.FLETCHER;
        }
        if (p == ModVillagers.PELETERO.get()) {
            return VillagerProfession.LEATHERWORKER;
        }
        if (p == ModVillagers.PASTOR.get()) {
            return VillagerProfession.SHEPHERD;
        }
        if (p == ModVillagers.ALBANIL.get()) {
            return VillagerProfession.MASON;
        }
        return null;
    }

    private NetherVillagers() {
    }
}
