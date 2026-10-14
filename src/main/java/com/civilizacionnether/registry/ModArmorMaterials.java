package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.crafting.Ingredient;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.EnumMap;
import java.util.List;

public final class ModArmorMaterials {
    public static final DeferredRegister<ArmorMaterial> ARMOR_MATERIALS =
            DeferredRegister.create(Registries.ARMOR_MATERIAL, CivilizacionNether.MODID);

    /** Armadura de rubí: entre diamante y netherita. Textura: textures/models/armor/ruby_layer_1/2.png */
    public static final DeferredHolder<ArmorMaterial, ArmorMaterial> RUBY = ARMOR_MATERIALS.register("ruby", () -> {
        EnumMap<ArmorItem.Type, Integer> defense = new EnumMap<>(ArmorItem.Type.class);
        defense.put(ArmorItem.Type.BOOTS, 3);
        defense.put(ArmorItem.Type.LEGGINGS, 6);
        defense.put(ArmorItem.Type.CHESTPLATE, 8);
        defense.put(ArmorItem.Type.HELMET, 3);
        defense.put(ArmorItem.Type.BODY, 11);
        return new ArmorMaterial(defense, 18, SoundEvents.ARMOR_EQUIP_DIAMOND,
                () -> Ingredient.of(ModItems.RUBY.get()),
                List.of(new ArmorMaterial.Layer(CivilizacionNether.id("ruby"))),
                2.5f, 0.05f);
    });

    private ModArmorMaterials() {
    }
}
