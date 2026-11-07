package com.civilizacionnether.registry;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.HumanoidType;
import com.civilizacionnether.item.DragonArmorItem;
import com.civilizacionnether.item.DragonEggItem;
import com.civilizacionnether.item.DragonStaffItem;
import com.civilizacionnether.item.NecroStaffItem;
import com.civilizacionnether.item.RubyArmorItem;
import com.civilizacionnether.item.ManualItem;
import com.civilizacionnether.item.RubyTier;
import com.civilizacionnether.item.RubyTridentItem;
import com.civilizacionnether.item.TooltipItem;
import com.civilizacionnether.item.WaterHelmetItem;
import com.civilizacionnether.item.SkinArmorItem;
import com.civilizacionnether.item.SoulScytheItem;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.DiggerItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.TridentItem;
import net.minecraft.world.level.block.Block;
import net.neoforged.neoforge.common.DeferredSpawnEggItem;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

public final class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(CivilizacionNether.MODID);

    public static final DeferredItem<Item> RUBY = ITEMS.register("ruby", () -> new Item(new Item.Properties()));

    public static final DeferredItem<SwordItem> RUBY_SWORD = ITEMS.register("ruby_sword", () -> new SwordItem(RubyTier.INSTANCE,
            new Item.Properties().attributes(SwordItem.createAttributes(RubyTier.INSTANCE, 3, -2.4f))));

    /** Espada larga de rubí (la del Guerrero Real): pega fuerte pero lenta. */
    public static final DeferredItem<SwordItem> RUBY_LONGSWORD = ITEMS.register("ruby_longsword", () -> new SwordItem(RubyTier.INSTANCE,
            new Item.Properties().rarity(Rarity.UNCOMMON).attributes(SwordItem.createAttributes(RubyTier.INSTANCE, 6, -3.0f))));

    /** Ballesta de rubí (la del Ballestero). */
    public static final DeferredItem<CrossbowItem> RUBY_CROSSBOW = ITEMS.register("ruby_crossbow",
            () -> new CrossbowItem(new Item.Properties().durability(700)));

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

    // ---- Armadura Humana del Nether (la que llevan los humanos): entre diamante y netherita
    private static DeferredItem<SkinArmorItem> skinArmor(String name, Holder<ArmorMaterial> mat, ArmorItem.Type type, int mult,
                                                        String texture, boolean glow, boolean fireproof) {
        return ITEMS.register(name, () -> {
            Item.Properties p = new Item.Properties().durability(type.getDurability(mult));
            if (fireproof) {
                p = p.fireResistant();
            }
            return new SkinArmorItem(mat, type, p, texture, glow);
        });
    }

    public static final DeferredItem<SkinArmorItem> HUMAN_HELMET = skinArmor("human_helmet", ModArmorMaterials.HUMAN, ArmorItem.Type.HELMET, 36, "human_armor", false, false);
    public static final DeferredItem<SkinArmorItem> HUMAN_CHESTPLATE = skinArmor("human_chestplate", ModArmorMaterials.HUMAN, ArmorItem.Type.CHESTPLATE, 36, "human_armor", false, false);
    public static final DeferredItem<SkinArmorItem> HUMAN_LEGGINGS = skinArmor("human_leggings", ModArmorMaterials.HUMAN, ArmorItem.Type.LEGGINGS, 36, "human_armor", false, false);
    public static final DeferredItem<SkinArmorItem> HUMAN_BOOTS = skinArmor("human_boots", ModArmorMaterials.HUMAN, ArmorItem.Type.BOOTS, 36, "human_armor", false, false);

    // ---- Armadura del Frío Eterno: con el set completo se nada, se corre y se ve dentro de la lava
    public static final DeferredItem<SkinArmorItem> FROST_HELMET = skinArmor("frost_helmet", ModArmorMaterials.FROST, ArmorItem.Type.HELMET, 30, "frost_armor", true, true);
    public static final DeferredItem<SkinArmorItem> FROST_CHESTPLATE = skinArmor("frost_chestplate", ModArmorMaterials.FROST, ArmorItem.Type.CHESTPLATE, 30, "frost_armor", true, true);
    public static final DeferredItem<SkinArmorItem> FROST_LEGGINGS = skinArmor("frost_leggings", ModArmorMaterials.FROST, ArmorItem.Type.LEGGINGS, 30, "frost_armor", true, true);
    public static final DeferredItem<SkinArmorItem> FROST_BOOTS = skinArmor("frost_boots", ModArmorMaterials.FROST, ArmorItem.Type.BOOTS, 30, "frost_armor", true, true);

    /** Hoja del Frío Eterno: sale de las hojas del árbol de hielo de Picos de Hielo. */
    public static final DeferredItem<Item> ETERNAL_FROST_LEAF = ITEMS.register("eternal_frost_leaf",
            () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON)));

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

    /** Balde de agua del Nether. */
    public static final DeferredItem<BucketItem> NETHER_WATER_BUCKET = ITEMS.register("nether_water_bucket",
            () -> new BucketItem(ModFluids.NETHER_WATER.get(), new Item.Properties().craftRemainder(Items.BUCKET).stacksTo(1)));

    public static final DeferredItem<BlockItem> RUBY_BLOCK = block("ruby_block", ModBlocks.RUBY_BLOCK);
    public static final DeferredItem<BlockItem> RUBY_ORE = block("ruby_ore", ModBlocks.RUBY_ORE);
    public static final DeferredItem<BlockItem> RUBY_LAMP = block("ruby_lamp", ModBlocks.RUBY_LAMP);
    public static final DeferredItem<BlockItem> RUBY_BRICKS = block("ruby_bricks", ModBlocks.RUBY_BRICKS);
    public static final DeferredItem<BlockItem> NECROMANCER_TABLE = block("necromancer_table", ModBlocks.NECROMANCER_TABLE);
    public static final DeferredItem<BlockItem> LIBRARIAN_LECTERN = block("librarian_lectern", ModBlocks.LIBRARIAN_LECTERN);
    public static final DeferredItem<BlockItem> TAMER_NEST = block("tamer_nest", ModBlocks.TAMER_NEST);
    public static final DeferredItem<BlockItem> FARMER_BASKET = block("farmer_basket", ModBlocks.FARMER_BASKET);
    public static final DeferredItem<BlockItem> MINER_CART = block("miner_cart", ModBlocks.MINER_CART);
    public static final DeferredItem<BlockItem> CARTOGRAPHER_DESK = block("cartographer_desk", ModBlocks.CARTOGRAPHER_DESK);
    public static final DeferredItem<BlockItem> FLETCHER_BENCH = block("fletcher_bench", ModBlocks.FLETCHER_BENCH);
    public static final DeferredItem<BlockItem> LEATHER_CAULDRON = block("leather_cauldron", ModBlocks.LEATHER_CAULDRON);
    public static final DeferredItem<BlockItem> SHEPHERD_LOOM = block("shepherd_loom", ModBlocks.SHEPHERD_LOOM);
    public static final DeferredItem<BlockItem> MASON_CUTTER = block("mason_cutter", ModBlocks.MASON_CUTTER);
    public static final DeferredItem<BlockItem> NETHER_BED = ITEMS.register("nether_bed",
            () -> new BlockItem(ModBlocks.NETHER_BED.get(), new Item.Properties().stacksTo(1)));
    public static final DeferredItem<BlockItem> FROST_LEAVES = block("frost_leaves", ModBlocks.FROST_LEAVES);

    // ---- Océano Púrpura y Dragón Infernal
    /** Pez Brasa crudo (comida de los delfines; se cría a los cangrejos, tortugas y caballitos con él). */
    public static final DeferredItem<Item> PEZ_BRASA = ITEMS.register("pez_brasa", () -> new Item(new Item.Properties()
            .food(new FoodProperties.Builder().nutrition(2).saturationModifier(0.1f).build())));
    /** Pez Brasa asado: buena comida y 30 segundos de resistencia al fuego. */
    public static final DeferredItem<TooltipItem> COOKED_PEZ_BRASA = ITEMS.register("cooked_pez_brasa", () -> new TooltipItem(new Item.Properties()
            .food(new FoodProperties.Builder().nutrition(6).saturationModifier(0.8f)
                    .effect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 600, 0), 1.0f).build()),
            "tooltip.civilizacion_nether.cooked_pez_brasa"));
    /** Silla del Dragón Infernal: se le pone al Dragón Infernal adulto para montarlo (se ve sobre su lomo). */
    public static final DeferredItem<TooltipItem> INFERNAL_SADDLE = ITEMS.register("infernal_saddle", () -> new TooltipItem(
            new Item.Properties().stacksTo(1).rarity(Rarity.RARE).fireResistant(), "tooltip.civilizacion_nether.infernal_saddle"));
    public static final DeferredItem<Item> DIENTES_TIBURON = ITEMS.register("dientes_tiburon", () -> new Item(new Item.Properties()));
    public static final DeferredItem<Item> ESCAMA_SERPIENTE = ITEMS.register("escama_serpiente",
            () -> new Item(new Item.Properties().rarity(Rarity.RARE).fireResistant()));
    /** Gel del Vacío (Medusa): en el soporte para pociones, poción rara + gel = respiración acuática. */
    public static final DeferredItem<Item> VOID_GEL = ITEMS.register("void_gel", () -> new Item(new Item.Properties()));
    /** Caparazón de Basalto (Cangrejo): poción rara + caparazón = poción del maestro tortuga. */
    public static final DeferredItem<Item> BASALT_SHELL = ITEMS.register("basalt_shell", () -> new Item(new Item.Properties()));
    public static final DeferredItem<Item> OBSIDIAN_SCALE = ITEMS.register("obsidian_scale", () -> new Item(new Item.Properties().fireResistant()));
    public static final DeferredItem<WaterHelmetItem> OBSIDIAN_TURTLE_HELMET = ITEMS.register("obsidian_turtle_helmet",
            () -> new WaterHelmetItem(ModArmorMaterials.OBSIDIAN_TURTLE,
                    new Item.Properties().durability(ArmorItem.Type.HELMET.getDurability(30)).fireResistant(), false));
    public static final DeferredItem<WaterHelmetItem> SERPENT_HELMET = ITEMS.register("serpent_helmet",
            () -> new WaterHelmetItem(ModArmorMaterials.SERPENT,
                    new Item.Properties().durability(ArmorItem.Type.HELMET.getDurability(40)).fireResistant().rarity(Rarity.EPIC), true));
    /** Tridente de Rubí: dientes de tiburón + prismarina + rubí. */
    public static final DeferredItem<RubyTridentItem> RUBY_TRIDENT = ITEMS.register("ruby_trident",
            () -> new RubyTridentItem(new Item.Properties().rarity(Rarity.EPIC).durability(500).fireResistant()
                    .attributes(RubyTridentItem.createRubyAttributes())
                    .component(DataComponents.TOOL, TridentItem.createToolProperties())));
    /** Huevo de Dragón Infernal: está en los nidos del Bosque Carmesí (y lo ponen dos Dragones Infernales). */
    public static final DeferredItem<DragonEggItem> INFERNAL_DRAGON_EGG = ITEMS.register("infernal_dragon_egg",
            () -> new DragonEggItem(new Item.Properties().stacksTo(16).rarity(Rarity.EPIC).fireResistant(), true));

    /** Manual de la Civilización del Nether (el libro del mod; llega al entrar por primera vez a un mundo). */
    public static final DeferredItem<ManualItem> MANUAL = ITEMS.register("manual",
            () -> new ManualItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)));

    /** Huevos de generación (uno por cada clase y el del dragón; en creativo y con el Aldeano Necromancer). */
    public static final List<DeferredItem<DeferredSpawnEggItem>> SPAWN_EGGS = new ArrayList<>();
    private static final Map<HumanoidType, DeferredItem<DeferredSpawnEggItem>> EGG_BY_TYPE = new EnumMap<>(HumanoidType.class);
    public static final DeferredItem<DeferredSpawnEggItem> DRAGON_SPAWN_EGG;

    static {
        for (HumanoidType type : HumanoidType.values()) {
            DeferredItem<DeferredSpawnEggItem> egg = ITEMS.register(type.id + "_spawn_egg", () -> new DeferredSpawnEggItem(
                    ModEntities.HUMANOIDS.get(type), type.eggBackground, type.eggSpots, new Item.Properties()));
            SPAWN_EGGS.add(egg);
            EGG_BY_TYPE.put(type, egg);
        }
        DRAGON_SPAWN_EGG = ITEMS.register("nether_dragon_spawn_egg", () -> new DeferredSpawnEggItem(
                ModEntities.NETHER_DRAGON, 0x161014, 0xE0281E, new Item.Properties()));
        SPAWN_EGGS.add(DRAGON_SPAWN_EGG);
        SPAWN_EGGS.add(spawnEgg("dragon_infernal", ModEntities.DRAGON_INFERNAL, 0x2A0A04, 0xFF7A1A));
        SPAWN_EGGS.add(spawnEgg("pez_brasa", ModEntities.PEZ_BRASA, 0x3A0A06, 0xFF8A1A));
        SPAWN_EGGS.add(spawnEgg("pez_alma", ModEntities.PEZ_ALMA, 0x10263A, 0x7AE6FF));
        SPAWN_EGGS.add(spawnEgg("anguila_rubi", ModEntities.ANGUILA_RUBI, 0x2A0610, 0xE0283C));
        SPAWN_EGGS.add(spawnEgg("medusa_vacio", ModEntities.MEDUSA_VACIO, 0x1C0838, 0xB070FF));
        SPAWN_EGGS.add(spawnEgg("cangrejo_basalto", ModEntities.CANGREJO_BASALTO, 0x2B2B31, 0xFF7A1A));
        SPAWN_EGGS.add(spawnEgg("caballito_magma", ModEntities.CABALLITO_MAGMA, 0x5A1408, 0xFFB347));
        SPAWN_EGGS.add(spawnEgg("manta_carmesi", ModEntities.MANTA_CARMESI, 0x5A0A1E, 0xFF4A6A));
        SPAWN_EGGS.add(spawnEgg("tortuga_obsidiana", ModEntities.TORTUGA_OBSIDIANA, 0x0C0614, 0x8A5CD0));
        SPAWN_EGGS.add(spawnEgg("tiburon_infernal", ModEntities.TIBURON_INFERNAL, 0x1A1418, 0xFF3A1A));
        SPAWN_EGGS.add(spawnEgg("serpiente_marina", ModEntities.SERPIENTE_MARINA, 0x2A0620, 0xFF6AB4));
        SPAWN_EGGS.add(spawnEgg("delfin_nether", ModEntities.DELFIN_NETHER, 0x3B1F5C, 0xE8C8FF));
        SPAWN_EGGS.add(spawnEgg("ballena_azul", ModEntities.BALLENA_AZUL, 0x1E2E5A, 0x9AB8FF));
    }

    private static <E extends Mob> DeferredItem<DeferredSpawnEggItem> spawnEgg(String id, DeferredHolder<EntityType<?>, EntityType<E>> type,
                                                                               int background, int spots) {
        return ITEMS.register(id + "_spawn_egg", () -> new DeferredSpawnEggItem(type, background, spots, new Item.Properties()));
    }

    public static Item spawnEgg(HumanoidType type) {
        return EGG_BY_TYPE.get(type).get();
    }

    private static <B extends Block> DeferredItem<BlockItem> block(String name, DeferredBlock<B> block) {
        return ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));
    }

    private ModItems() {
    }
}
