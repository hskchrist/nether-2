package com.civilizacionnether.item;

import com.civilizacionnether.client.SkinArmorRenderer;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.core.Holder;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.ItemStack;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.animatable.client.GeoRenderProvider;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.function.Consumer;

/**
 * Armadura con forma de "ropa" de skin (64x64): la Armadura Humana del Nether y la del Frío Eterno.
 * El modelo es geo/armor/skin_armor.geo.json; la textura, textures/armor/&lt;texture&gt;.png.
 */
public class SkinArmorItem extends ArmorItem implements GeoItem {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private final String texture;
    private final boolean glowing;

    public SkinArmorItem(Holder<ArmorMaterial> material, Type type, Properties properties, String texture, boolean glowing) {
        super(material, type, properties);
        this.texture = texture;
        this.glowing = glowing;
    }

    public String getArmorTexture() {
        return texture;
    }

    @Override
    public void createGeoRenderer(Consumer<GeoRenderProvider> consumer) {
        consumer.accept(new GeoRenderProvider() {
            private SkinArmorRenderer renderer;

            @Override
            public <T extends LivingEntity> HumanoidModel<?> getGeoArmorRenderer(@Nullable T livingEntity, ItemStack itemStack,
                                                                              @Nullable EquipmentSlot equipmentSlot,
                                                                              @Nullable HumanoidModel<T> original) {
                if (this.renderer == null) {
                    this.renderer = new SkinArmorRenderer(glowing);
                }
                return this.renderer;
            }
        });
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
