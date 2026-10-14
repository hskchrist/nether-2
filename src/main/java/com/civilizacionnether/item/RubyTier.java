package com.civilizacionnether.item;

import com.civilizacionnether.registry.ModItems;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.Block;

/** Nivel de herramienta del rubí: algo mejor que el diamante. */
public enum RubyTier implements Tier {
    INSTANCE;

    @Override
    public int getUses() {
        return 1900;
    }

    @Override
    public float getSpeed() {
        return 9.0f;
    }

    @Override
    public float getAttackDamageBonus() {
        return 3.5f;
    }

    @Override
    public TagKey<Block> getIncorrectBlocksForDrops() {
        return BlockTags.INCORRECT_FOR_DIAMOND_TOOL;
    }

    @Override
    public int getEnchantmentValue() {
        return 16;
    }

    @Override
    public Ingredient getRepairIngredient() {
        return Ingredient.of(ModItems.RUBY.get());
    }
}
