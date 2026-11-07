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

    /** Armadura Humana del Nether (la armadura base de los humanos): entre diamante y netherita. */
    public static final DeferredHolder<ArmorMaterial, ArmorMaterial> HUMAN = ARMOR_MATERIALS.register("human", () -> {
        EnumMap<ArmorItem.Type, Integer> defense = new EnumMap<>(ArmorItem.Type.class);
        defense.put(ArmorItem.Type.BOOTS, 3);
        defense.put(ArmorItem.Type.LEGGINGS, 6);
        defense.put(ArmorItem.Type.CHESTPLATE, 8);
        defense.put(ArmorItem.Type.HELMET, 3);
        defense.put(ArmorItem.Type.BODY, 11);
        return new ArmorMaterial(defense, 13, SoundEvents.ARMOR_EQUIP_NETHERITE,
                () -> Ingredient.of(ModItems.RUBY.get()),
                List.of(new ArmorMaterial.Layer(CivilizacionNether.id("human"))),
                2.8f, 0.08f);
    });

    /** Armadura del Frío Eterno: con el set completo se nada y se ve en la lava sin quemarse. */
    public static final DeferredHolder<ArmorMaterial, ArmorMaterial> FROST = ARMOR_MATERIALS.register("frost", () -> {
        EnumMap<ArmorItem.Type, Integer> defense = new EnumMap<>(ArmorItem.Type.class);
        defense.put(ArmorItem.Type.BOOTS, 3);
        defense.put(ArmorItem.Type.LEGGINGS, 6);
        defense.put(ArmorItem.Type.CHESTPLATE, 7);
        defense.put(ArmorItem.Type.HELMET, 3);
        defense.put(ArmorItem.Type.BODY, 10);
        return new ArmorMaterial(defense, 16, SoundEvents.ARMOR_EQUIP_DIAMOND,
                () -> Ingredient.of(ModItems.ETERNAL_FROST_LEAF.get()),
                List.of(new ArmorMaterial.Layer(CivilizacionNether.id("frost"))),
                2.0f, 0.0f);
    });

    /** Casco de Tortuga Obsidiana (respirar bajo el agua). */
    public static final DeferredHolder<ArmorMaterial, ArmorMaterial> OBSIDIAN_TURTLE = ARMOR_MATERIALS.register("obsidian_turtle", () -> {
        EnumMap<ArmorItem.Type, Integer> defense = new EnumMap<>(ArmorItem.Type.class);
        defense.put(ArmorItem.Type.BOOTS, 2);
        defense.put(ArmorItem.Type.LEGGINGS, 5);
        defense.put(ArmorItem.Type.CHESTPLATE, 6);
        defense.put(ArmorItem.Type.HELMET, 3);
        defense.put(ArmorItem.Type.BODY, 8);
        return new ArmorMaterial(defense, 12, SoundEvents.ARMOR_EQUIP_TURTLE,
                () -> Ingredient.of(ModItems.OBSIDIAN_SCALE.get()),
                List.of(new ArmorMaterial.Layer(CivilizacionNether.id("obsidian_turtle"))),
                1.0f, 0.05f);
    });

    /** Casco de la Serpiente (respirar, ver y nadar rápido bajo el agua). */
    public static final DeferredHolder<ArmorMaterial, ArmorMaterial> SERPENT = ARMOR_MATERIALS.register("serpent", () -> {
        EnumMap<ArmorItem.Type, Integer> defense = new EnumMap<>(ArmorItem.Type.class);
        defense.put(ArmorItem.Type.BOOTS, 3);
        defense.put(ArmorItem.Type.LEGGINGS, 6);
        defense.put(ArmorItem.Type.CHESTPLATE, 8);
        defense.put(ArmorItem.Type.HELMET, 4);
        defense.put(ArmorItem.Type.BODY, 11);
        return new ArmorMaterial(defense, 15, SoundEvents.ARMOR_EQUIP_TURTLE,
                () -> Ingredient.of(ModItems.ESCAMA_SERPIENTE.get()),
                List.of(new ArmorMaterial.Layer(CivilizacionNether.id("serpent"))),
                2.5f, 0.1f);
    });

    private ModArmorMaterials() {
    }
}
