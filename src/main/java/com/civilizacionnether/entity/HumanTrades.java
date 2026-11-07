package com.civilizacionnether.entity;

import com.civilizacionnether.registry.ModItems;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.EnchantedBookItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentInstance;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;
import net.minecraft.world.level.ItemLike;

import java.util.Optional;

/**
 * Intercambios de cada clase. La moneda del reino es el rubí; el Aldeano Necromancer además
 * cambia esmeraldas por rubíes y por la Armadura del Frío Eterno, y almas por los huevos de generación del reino.
 */
public final class HumanTrades {
    private HumanTrades() {
    }

    private static MerchantOffer sell(ItemLike price, int count, ItemStack result, int uses) {
        return new MerchantOffer(new ItemCost(price, count), result, uses, 0, 0.05f);
    }

    private static MerchantOffer sell(ItemLike price, int count, ItemLike result, int n, int uses) {
        return sell(price, count, new ItemStack(result, n), uses);
    }

    private static MerchantOffer sell2(ItemLike a, int ca, ItemLike b, int cb, ItemStack result, int uses) {
        return new MerchantOffer(new ItemCost(a, ca), Optional.of(new ItemCost(b, cb)), result, uses, 0, 0.05f);
    }

    private static ItemStack book(NetherHumanoidEntity e, ResourceKey<Enchantment> key, int level) {
        try {
            Holder<Enchantment> h = e.level().registryAccess().registryOrThrow(Registries.ENCHANTMENT).getHolderOrThrow(key);
            return EnchantedBookItem.createForEnchantment(new EnchantmentInstance(h, level));
        } catch (Exception ex) {
            return new ItemStack(Items.BOOK);
        }
    }

    public static MerchantOffers create(NetherHumanoidEntity e) {
        MerchantOffers o = new MerchantOffers();
        Item ruby = ModItems.RUBY.get();
        Item soul = ModItems.SOUL.get();
        switch (e.getHumanoidType()) {
            case ALDEANO_NECROMANCER -> {
                o.add(sell(Items.EMERALD, 2, ruby, 1, 16));
                o.add(sell(Items.EMERALD, 8, ModItems.FROST_HELMET.get(), 1, 3));
                o.add(sell(Items.EMERALD, 12, ModItems.FROST_CHESTPLATE.get(), 1, 3));
                o.add(sell(Items.EMERALD, 10, ModItems.FROST_LEGGINGS.get(), 1, 3));
                o.add(sell(Items.EMERALD, 8, ModItems.FROST_BOOTS.get(), 1, 3));
                for (HumanoidType t : HumanoidType.values()) {
                    if (t == HumanoidType.REY_NECROMANCER) {
                        o.add(sell(soul, 20, ModItems.spawnEgg(t), 1, 2));
                    } else {
                        o.add(sell(soul, 8, ModItems.spawnEgg(t), 1, 6));
                    }
                }
                o.add(sell(soul, 25, ModItems.DRAGON_SPAWN_EGG.get(), 1, 2));
                o.add(sell(soul, 30, ModItems.SOUL_SCYTHE.get(), 1, 2));
            }
            case BIBLIOTECARIO -> {
                o.add(sell(ruby, 1, Items.BOOK, 2, 12));
                o.add(sell2(ruby, 5, Items.BOOK, 1, book(e, Enchantments.PROTECTION, 3), 4));
                o.add(sell2(ruby, 5, Items.BOOK, 1, book(e, Enchantments.EFFICIENCY, 3), 4));
                o.add(sell2(ruby, 8, Items.BOOK, 1, book(e, Enchantments.FORTUNE, 2), 3));
                o.add(sell2(ruby, 8, Items.BOOK, 1, book(e, Enchantments.SHARPNESS, 3), 3));
                o.add(sell(ruby, 3, Items.BOOKSHELF, 2, 8));
                o.add(sell(Items.PAPER, 16, ruby, 1, 12));
            }
            case DOMADOR -> {
                o.add(sell(ruby, 6, Items.SADDLE, 1, 4));
                o.add(sell(ruby, 24, ModItems.DRAGON_ARMOR.get(), 1, 2));
                o.add(sell2(ruby, 12, soul, 1, new ItemStack(ModItems.DRAGON_STAFF.get()), 2));
                o.add(sell(ruby, 40, ModItems.DRAGON_EGG.get(), 1, 1));
                o.add(sell(Items.BEEF, 8, ruby, 1, 12));
                o.add(sell(Items.COOKED_PORKCHOP, 10, ruby, 1, 12));
            }
            case GRANJERO -> {
                o.add(sell(ruby, 1, Items.NETHER_WART, 8, 16));
                o.add(sell(ruby, 1, Items.CRIMSON_FUNGUS, 4, 12));
                o.add(sell(ruby, 1, Items.WARPED_FUNGUS, 4, 12));
                o.add(sell(ruby, 1, Items.BREAD, 6, 16));
                o.add(sell(ruby, 1, Items.COOKED_BEEF, 3, 16));
                o.add(sell(ruby, 2, ModItems.NETHER_WATER_BUCKET.get(), 1, 6));
                o.add(sell(Items.WHEAT, 20, ruby, 1, 16));
            }
            case MINERO -> {
                o.add(sell(Items.COAL, 16, ruby, 1, 16));
                o.add(sell(ruby, 1, Items.QUARTZ, 4, 16));
                o.add(sell(ruby, 1, Items.TORCH, 8, 16));
                o.add(sell(ruby, 3, Items.IRON_PICKAXE, 1, 4));
                o.add(sell(ruby, 12, Items.DIAMOND_PICKAXE, 1, 2));
                o.add(sell(ruby, 6, Items.GOLD_INGOT, 4, 8));
                o.add(sell(Items.RAW_IRON, 8, ruby, 1, 12));
            }
            case CIUDADANO -> {
                o.add(sell(ruby, 1, Items.BREAD, 4, 16));
                o.add(sell(ruby, 2, ModItems.NETHER_BED.get(), 1, 4));
                o.add(sell(ruby, 1, Items.LANTERN, 2, 8));
                o.add(sell(Items.COOKED_BEEF, 6, ruby, 1, 12));
            }
            case GUERRERO -> {
                o.add(sell(ruby, 8, ModItems.RUBY_SWORD.get(), 1, 3));
                o.add(sell(ruby, 2, Items.SHIELD, 1, 4));
                o.add(sell(ruby, 1, Items.COOKED_BEEF, 4, 12));
            }
            case ARQUERO -> {
                o.add(sell(ruby, 1, Items.ARROW, 16, 16));
                o.add(sell(ruby, 8, ModItems.RUBY_BOW.get(), 1, 3));
                o.add(sell(Items.STRING, 12, ruby, 1, 12));
            }
            case GUERRERO_REAL -> {
                o.add(sell(ruby, 18, ModItems.RUBY_LONGSWORD.get(), 1, 2));
                o.add(sell2(ruby, 10, Items.DIAMOND, 2, new ItemStack(ModItems.HUMAN_HELMET.get()), 2));
                o.add(sell2(ruby, 16, Items.DIAMOND, 4, new ItemStack(ModItems.HUMAN_CHESTPLATE.get()), 2));
                o.add(sell2(ruby, 14, Items.DIAMOND, 3, new ItemStack(ModItems.HUMAN_LEGGINGS.get()), 2));
                o.add(sell2(ruby, 10, Items.DIAMOND, 2, new ItemStack(ModItems.HUMAN_BOOTS.get()), 2));
            }
            case BALLESTERO -> {
                o.add(sell(ruby, 10, ModItems.RUBY_CROSSBOW.get(), 1, 3));
                o.add(sell(ruby, 1, Items.ARROW, 16, 16));
                o.add(sell(Items.STRING, 12, ruby, 1, 12));
            }
            case REY_NECROMANCER -> {
                o.add(sell(Items.GOLD_INGOT, 4, ruby, 1, 16));
                o.add(sell(ruby, 48, ModItems.NECRO_STAFF.get(), 1, 1));
                o.add(sell(ruby, 3, Items.GOLDEN_APPLE, 1, 4));
            }
            default -> {
            }
        }
        return o;
    }
}
