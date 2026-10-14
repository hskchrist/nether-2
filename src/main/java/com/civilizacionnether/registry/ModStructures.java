package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.worldgen.CapitalPiece;
import com.civilizacionnether.worldgen.CapitalStructure;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Tipo de estructura y tipo de pieza de la capital gigante. */
public final class ModStructures {
    public static final DeferredRegister<StructureType<?>> STRUCTURE_TYPES =
            DeferredRegister.create(Registries.STRUCTURE_TYPE, CivilizacionNether.MODID);
    public static final DeferredRegister<StructurePieceType> PIECES =
            DeferredRegister.create(Registries.STRUCTURE_PIECE, CivilizacionNether.MODID);

    public static final DeferredHolder<StructureType<?>, StructureType<CapitalStructure>> CAPITAL =
            STRUCTURE_TYPES.register("capital", () -> () -> CapitalStructure.CODEC);
    public static final DeferredHolder<StructurePieceType, StructurePieceType> CAPITAL_PIECE =
            PIECES.register("capital", () -> (StructurePieceType) CapitalPiece::new);

    private ModStructures() {
    }
}
