package com.civilizacionnether.client;

import com.civilizacionnether.CivilizacionNether;
import com.civilizacionnether.entity.HumanoidType;
import com.civilizacionnether.entity.NetherDragonEntity;
import com.civilizacionnether.network.DragonBreathPayload;
import com.civilizacionnether.network.DragonShootPayload;
import com.civilizacionnether.registry.ModEntities;
import com.civilizacionnether.registry.ModItems;
import com.civilizacionnether.registry.ModParticles;
import com.civilizacionnether.client.particle.BlackFlameParticle;
import com.civilizacionnether.client.particle.RedSoulParticle;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.neoforge.client.event.CalculateDetachedCameraDistanceEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.minecraft.client.CameraType;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.InputEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.event.RegisterParticleProvidersEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import org.lwjgl.glfw.GLFW;

public final class ClientEvents {
    /** R: ráfaga de fuego grande (cuando la barra de carga está llena). */
    public static final KeyMapping BREATH_KEY = new KeyMapping("key.civilizacion_nether.breath",
            InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_R, "key.categories.civilizacion_nether");
    /** X: cámara de dragón (tercera persona alejada) mientras lo montas. */
    public static final KeyMapping CAMERA_KEY = new KeyMapping("key.civilizacion_nether.dragon_camera",
            InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_X, "key.categories.civilizacion_nether");
    /** Distancia de la cámara de dragón (la normal de Minecraft es 4). */
    private static final float DRAGON_CAMERA_DISTANCE = 12.0f;
    private static boolean dragonCamera;

    @EventBusSubscriber(modid = CivilizacionNether.MODID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
    public static final class ModBus {
        @SubscribeEvent
        public static void renderers(EntityRenderersEvent.RegisterRenderers event) {
            for (HumanoidType type : HumanoidType.values()) {
                event.registerEntityRenderer(ModEntities.HUMANOIDS.get(type).get(), ctx -> new HumanoidRenderer(ctx, type));
            }
            event.registerEntityRenderer(ModEntities.NETHER_DRAGON.get(), DragonRenderer::new);
            event.registerEntityRenderer(ModEntities.DRAGON_EGG.get(), DragonEggRenderer::new);
            event.registerEntityRenderer(ModEntities.DRAGON_FIREBALL.get(), DragonFireballRenderer::new);
        }

        @SubscribeEvent
        public static void keys(RegisterKeyMappingsEvent event) {
            event.register(BREATH_KEY);
            event.register(CAMERA_KEY);
        }

        @SubscribeEvent
        public static void particles(RegisterParticleProvidersEvent event) {
            event.registerSpriteSet(ModParticles.BLACK_FLAME.get(), BlackFlameParticle.Provider::new);
            event.registerSpriteSet(ModParticles.RED_SOUL.get(), RedSoulParticle.Provider::new);
        }

        @SubscribeEvent
        public static void guiLayers(RegisterGuiLayersEvent event) {
            event.registerAbove(VanillaGuiLayers.CROSSHAIR, CivilizacionNether.id("dragon_charge"), DragonHud::render);
        }

        @SubscribeEvent
        public static void setup(FMLClientSetupEvent event) {
            event.enqueueWork(() -> {
                // Animación de tensado del arco de rubí
                ItemProperties.register(ModItems.RUBY_BOW.get(), ResourceLocation.withDefaultNamespace("pull"),
                        (stack, level, entity, seed) -> {
                            if (entity == null || entity.getUseItem() != stack) {
                                return 0.0f;
                            }
                            return (stack.getUseDuration(entity) - entity.getUseItemRemainingTicks()) / 20.0f;
                        });
                ItemProperties.register(ModItems.RUBY_BOW.get(), ResourceLocation.withDefaultNamespace("pulling"),
                        (stack, level, entity, seed) -> entity != null && entity.isUsingItem() && entity.getUseItem() == stack ? 1.0f : 0.0f);
            });
        }

        private ModBus() {
        }
    }

    @EventBusSubscriber(modid = CivilizacionNether.MODID, value = Dist.CLIENT)
    public static final class GameBus {
        @SubscribeEvent
        public static void clientTick(ClientTickEvent.Post event) {
            Minecraft mc = Minecraft.getInstance();
            while (BREATH_KEY.consumeClick()) {
                if (mc.player != null && mc.player.getVehicle() instanceof NetherDragonEntity) {
                    PacketDistributor.sendToServer(new DragonBreathPayload());
                }
            }
        }

        /** X montado en el dragón: alterna la cámara de dragón; al bajarse vuelve a primera persona. */
        @SubscribeEvent
        public static void cameraKey(ClientTickEvent.Post event) {
            Minecraft mc = Minecraft.getInstance();
            boolean riding = mc.player != null && mc.player.getVehicle() instanceof NetherDragonEntity;
            while (CAMERA_KEY.consumeClick()) {
                if (riding) {
                    dragonCamera = !dragonCamera;
                    mc.options.setCameraType(dragonCamera ? CameraType.THIRD_PERSON_BACK : CameraType.FIRST_PERSON);
                }
            }
            if (!riding && dragonCamera) {
                dragonCamera = false;
                mc.options.setCameraType(CameraType.FIRST_PERSON);
            }
        }

        @SubscribeEvent
        public static void cameraDistance(CalculateDetachedCameraDistanceEvent event) {
            Minecraft mc = Minecraft.getInstance();
            if (dragonCamera && mc.player != null && mc.player.getVehicle() instanceof NetherDragonEntity dragon) {
                event.setDistance(Math.max(event.getDistance(), DRAGON_CAMERA_DISTANCE * Math.max(0.6f, dragon.getScale())));
            }
        }

        /** Montado en el dragón adulto, el clic derecho dispara una bola de fuego (en vez de usar el ítem de la mano). */
        @SubscribeEvent
        public static void rightClick(InputEvent.InteractionKeyMappingTriggered event) {
            Minecraft mc = Minecraft.getInstance();
            if (event.isUseItem() && mc.player != null && mc.screen == null
                    && mc.player.getVehicle() instanceof NetherDragonEntity dragon && dragon.isAdult() && dragon.isSaddled()) {
                event.setCanceled(true);
                event.setSwingHand(false);
                PacketDistributor.sendToServer(new DragonShootPayload());
            }
        }

        private GameBus() {
        }
    }

    private ClientEvents() {
    }
}
