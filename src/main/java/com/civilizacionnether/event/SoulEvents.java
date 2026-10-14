package com.civilizacionnether.event;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.item.SoulBrewingRecipe;
import com.civilizacionnether.registry.ModItems;
import com.civilizacionnether.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.brewing.RegisterBrewingRecipesEvent;
import net.neoforged.neoforge.event.level.BlockEvent;

/** Almas: la Hoz de almas saca almas de la arena de almas y el alma encanta pociones en el soporte para pociones. */
@EventBusSubscriber(modid = CivilizacionNether.MODID)
public final class SoulEvents {

    /** Arena de almas rota con la Hoz: 1 alma; Fortuna I 1-2, II 2-3, III 3. */
    @SubscribeEvent
    public static void breakSoulSand(BlockEvent.BreakEvent event) {
        Player player = event.getPlayer();
        if (!(event.getLevel() instanceof ServerLevel level) || player == null || player.isCreative()
                || !event.getState().is(Blocks.SOUL_SAND)) {
            return;
        }
        ItemStack tool = player.getMainHandItem();
        if (!tool.is(ModItems.SOUL_SCYTHE.get())) {
            return;
        }
        Holder<Enchantment> fortune = level.registryAccess().registryOrThrow(Registries.ENCHANTMENT)
                .getHolderOrThrow(Enchantments.FORTUNE);
        int lvl = EnchantmentHelper.getItemEnchantmentLevel(fortune, tool);
        int min = lvl >= 3 ? 3 : lvl == 2 ? 2 : 1;
        int max = lvl >= 2 ? 3 : lvl == 1 ? 2 : 1;
        int count = min + level.getRandom().nextInt(max - min + 1);
        BlockPos pos = event.getPos();
        Block.popResource(level, pos, new ItemStack(ModItems.SOUL.get(), count));
        level.sendParticles(ModParticles.RED_SOUL.get(), pos.getX() + 0.5, pos.getY() + 0.8, pos.getZ() + 0.5,
                3 + count * 2, 0.3, 0.2, 0.3, 0.02);
        level.playSound(null, pos, SoundEvents.SOUL_SAND_BREAK, SoundSource.BLOCKS, 1.0f, 0.6f);
    }

    @SubscribeEvent
    public static void brewing(RegisterBrewingRecipesEvent event) {
        event.getBuilder().addRecipe(new SoulBrewingRecipe());
    }

    private SoulEvents() {
    }
}
