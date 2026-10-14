package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.HumanoidType;
import com.civilizacionnether.item.DragonArmorItem;
import com.civilizacionnether.item.DragonEggItem;
import com.civilizacionnether.item.DragonStaffItem;
import com.civilizacionnether.item.RubyArmorItem;
import com.civilizacionnether.item.NecroStaffItem;
import com.civilizacionnether.item.RubyTier;
import com.civilizacionnether.item.SoulScytheItem;
import net.minecraft.world.item.DiggerItem;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.level.block.Block;
import net.neoforged.neoforge.common.DeferredSpawnEggItem;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.ArrayList;
import java.util.List;

public final class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(CivilizacionNether.MODID);

    public static final DeferredItem<Item> RUBY = ITEMS.register("ruby", () -> new Item(new Item.Properties()));

    public static final DeferredItem<SwordItem> RUBY_SWORD = ITEMS.register("ruby_sword", () -> new SwordItem(RubyTier.INSTANCE,
            new Item.Properties().attributes(SwordItem.createAttributes(RubyTier.INSTANCE, 3, -2.4f))));

    /** Báculo del Rey Necromancer (lo suelta el Rey al morir; también se craftea). */
    public static final DeferredItem<NecroStaffItem> NECRO_STAFF = ITEMS.register("necro_staff",
            () -> new NecroStaffItem(new Item.Properties().durability(600).rarity(Rarity.EPIC)));

    public static final DeferredItem<BowItem> RUBY_BOW = ITEMS.register("ruby_bow",
            () -> new BowItem(new Item.Properties().durability(640)));

    public static final DeferredItem<RubyArmorItem> RUBY_HELMET = ITEMS.register("ruby_helmet", () -> new RubyArmorItem(
            ModArmorMaterials.RUBY, ArmorItem.Type.HELMET, new Item.Properties().durability(ArmorItem.Type.HELMET.getDurability(35))));
    public static final DeferredItem<RubyArmorItem> RUBY_CHESTPLATE = ITEMS.register("ruby_chestplate", () -> new RubyArmorItem(
            ModArmorMaterials.RUBY, ArmorItem.Type.CHESTPLATE, new Item.Properties().durability(ArmorItem.Type.CHESTPLATE.getDurability(35))));
    public static final DeferredItem<RubyArmorItem> RUBY_LEGGINGS = ITEMS.register("ruby_leggings", () -> new RubyArmorItem(
            ModArmorMaterials.RUBY, ArmorItem.Type.LEGGINGS, new Item.Properties().durability(ArmorItem.Type.LEGGINGS.getDurability(35))));
    public static final DeferredItem<RubyArmorItem> RUBY_BOOTS = ITEMS.register("ruby_boots", () -> new RubyArmorItem(
            ModArmorMaterials.RUBY, ArmorItem.Type.BOOTS, new Item.Properties().durability(ArmorItem.Type.BOOTS.getDurability(35))));

    public static final DeferredItem<DragonArmorItem> DRAGON_ARMOR = ITEMS.register("dragon_armor",
            () -> new DragonArmorItem(new Item.Properties().stacksTo(1).rarity(Rarity.RARE)));

    /** Huevo de Dragón del Nether (se craftea, está en el nido de la capital y lo ponen dos dragones adultos). */
    public static final DeferredItem<DragonEggItem> DRAGON_EGG = ITEMS.register("dragon_egg",
            () -> new DragonEggItem(new Item.Properties().stacksTo(16).rarity(Rarity.EPIC).fireResistant()));

    /** Alma: la sueltan todas las criaturas del mod al morir y la arena de almas rota con la Hoz de almas. */
    public static final DeferredItem<Item> SOUL = ITEMS.register("soul",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON).fireResistant()));

    /** Hoz de almas: rompe arena de almas para sacar de 1 a 3 almas según su Fortuna. */
    public static final DeferredItem<SoulScytheItem> SOUL_SCYTHE = ITEMS.register("soul_scythe",
            () -> new SoulScytheItem(RubyTier.INSTANCE, new Item.Properties().fireResistant().rarity(Rarity.RARE)
                    .attributes(DiggerItem.createAttributes(RubyTier.INSTANCE, 4.0f, -3.0f))));

    /** Báculo de dragón: llama a tu dragón (clic derecho) y activa su modo libre (mayús + clic derecho). */
    public static final DeferredItem<DragonStaffItem> DRAGON_STAFF = ITEMS.register("dragon_staff",
            () -> new DragonStaffItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant()));

    public static final DeferredItem<BlockItem> RUBY_BLOCK = block("ruby_block", ModBlocks.RUBY_BLOCK);
    public static final DeferredItem<BlockItem> RUBY_ORE = block("ruby_ore", ModBlocks.RUBY_ORE);
    public static final DeferredItem<BlockItem> RUBY_LAMP = block("ruby_lamp", ModBlocks.RUBY_LAMP);
    public static final DeferredItem<BlockItem> RUBY_BRICKS = block("ruby_bricks", ModBlocks.RUBY_BRICKS);

    /** Huevos de generación (uno por cada clase y cada dragón; solo en creativo). */
    public static final List<DeferredItem<DeferredSpawnEggItem>> SPAWN_EGGS = new ArrayList<>();

    static {
        for (HumanoidType type : HumanoidType.values()) {
            SPAWN_EGGS.add(ITEMS.register(type.id + "_spawn_egg", () -> new DeferredSpawnEggItem(
                    ModEntities.HUMANOIDS.get(type), type.eggBackground, type.eggSpots, new Item.Properties())));
        }
        SPAWN_EGGS.add(ITEMS.register("nether_dragon_spawn_egg", () -> new DeferredSpawnEggItem(
                ModEntities.NETHER_DRAGON, 0x161014, 0xE0281E, new Item.Properties())));
    }

    private static DeferredItem<BlockItem> block(String name, DeferredBlock<Block> block) {
        return ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));
    }

    private ModItems() {
    }
}
