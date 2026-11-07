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
import org.joml.Vector3f;
import com.civilizacionnether.event.FrostArmorEvents;
import com.civilizacionnether.registry.ModFluids;
import com.mojang.blaze3d.shaders.FogShape;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.client.renderer.ItemBlockRenderTypes;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.level.material.FogType;
import net.neoforged.neoforge.client.event.ViewportEvent;
import net.neoforged.neoforge.client.extensions.common.IClientFluidTypeExtensions;
import net.neoforged.neoforge.client.extensions.common.RegisterClientExtensionsEvent;

public final class ClientEvents {
    /** R: ráfaga de fuego grande (cuando la barra de carga está llena). */
    public static final KeyMapping BREATH_KEY = new KeyMapping("key.civilizacion_nether.breath",
            InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_R, "key.categories.civilizacion_nether");
    /** X: cámara de dragón (tercera persona alejada) mientras lo montas. */
    /** G: agarrar al mob que tenga adelante y lanzarlo por los aires (los dos dragones). */
    public static final KeyMapping GRAB_KEY = new KeyMapping("key.civilizacion_nether.dragon_grab",
            InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_G, "key.categories.civilizacion_nether");
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
            event.registerEntityRenderer(ModEntities.DRAGON_INFERNAL.get(), InfernalDragonRenderer::new);
            event.registerEntityRenderer(ModEntities.DRAGON_INFERNAL_DOMESTICABLE.get(), InfernalDragonRenderer::new);
            event.registerEntityRenderer(net.minecraft.world.entity.EntityType.TRIDENT, RubyTridentRenderer::new);
            // aldeanos: los del Nether (y los de las 5 profesiones nuevas) con sus skins; los demás, igual que vanilla
            event.registerEntityRenderer(net.minecraft.world.entity.EntityType.VILLAGER, NetherVillagerRenderer::new);
            // fauna del Océano Púrpura: (nombre, escala, sombra, se inclina al nadar, brilla, transparente)
            event.registerEntityRenderer(ModEntities.PEZ_BRASA.get(), ctx -> new SeaCreatureRenderer<>(ctx, "pez_brasa", 1.0f, 0.25f, false, true, false));
            event.registerEntityRenderer(ModEntities.PEZ_ALMA.get(), ctx -> new SeaCreatureRenderer<>(ctx, "pez_alma", 1.0f, 0.25f, false, true, false));
            event.registerEntityRenderer(ModEntities.ANGUILA_RUBI.get(), ctx -> new SeaCreatureRenderer<>(ctx, "anguila_rubi", 1.0f, 0.25f, false, true, false));
            event.registerEntityRenderer(ModEntities.MEDUSA_VACIO.get(), ctx -> new SeaCreatureRenderer<>(ctx, "medusa_vacio", 1.0f, 0.35f, false, true, true));
            event.registerEntityRenderer(ModEntities.CANGREJO_BASALTO.get(), ctx -> new SeaCreatureRenderer<>(ctx, "cangrejo_basalto", 1.0f, 0.5f, false, true, false));
            event.registerEntityRenderer(ModEntities.CABALLITO_MAGMA.get(), ctx -> new SeaCreatureRenderer<>(ctx, "caballito_magma", 1.0f, 0.25f, false, true, false));
            event.registerEntityRenderer(ModEntities.MANTA_CARMESI.get(), ctx -> new SeaCreatureRenderer<>(ctx, "manta_carmesi", 1.0f, 1.2f, true, true, false));
            event.registerEntityRenderer(ModEntities.TORTUGA_OBSIDIANA.get(), ctx -> new SeaCreatureRenderer<>(ctx, "tortuga_obsidiana", 1.0f, 0.8f, true, true, false));
            event.registerEntityRenderer(ModEntities.TIBURON_INFERNAL.get(), ctx -> new SeaCreatureRenderer<>(ctx, "tiburon_infernal", 1.0f, 0.8f, true, true, false));
            event.registerEntityRenderer(ModEntities.SERPIENTE_MARINA.get(), ctx -> new SeaCreatureRenderer<>(ctx, "serpiente_marina", 1.0f, 1.6f, true, true, false));
            event.registerEntityRenderer(ModEntities.DELFIN_NETHER.get(), ctx -> new SeaCreatureRenderer<>(ctx, "delfin_nether", 1.0f, 0.5f, true, true, false));
            event.registerEntityRenderer(ModEntities.BALLENA_AZUL.get(), ctx -> new SeaCreatureRenderer<>(ctx, "ballena_azul", 2.0f, 2.5f, true, false, false));
        }

        @SubscribeEvent
        public static void keys(RegisterKeyMappingsEvent event) {
            event.register(BREATH_KEY);
            event.register(CAMERA_KEY);
            event.register(GRAB_KEY);
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
                // Ballesta de rubí: tensado y cargada (como la ballesta normal)
                ItemProperties.register(ModItems.RUBY_CROSSBOW.get(), ResourceLocation.withDefaultNamespace("pull"),
                        (stack, level, entity, seed) -> {
                            if (entity == null || entity.getUseItem() != stack || CrossbowItem.isCharged(stack)) {
                                return 0.0f;
                            }
                            return (stack.getUseDuration(entity) - entity.getUseItemRemainingTicks()) / 25.0f;
                        });
                ItemProperties.register(ModItems.RUBY_CROSSBOW.get(), ResourceLocation.withDefaultNamespace("pulling"),
                        (stack, level, entity, seed) -> entity != null && entity.isUsingItem() && entity.getUseItem() == stack
                                && !CrossbowItem.isCharged(stack) ? 1.0f : 0.0f);
                ItemProperties.register(ModItems.RUBY_CROSSBOW.get(), ResourceLocation.withDefaultNamespace("charged"),
                        (stack, level, entity, seed) -> CrossbowItem.isCharged(stack) ? 1.0f : 0.0f);
                // Tridente de Rubí: pose de lanzar (como el tridente normal)
                ItemProperties.register(ModItems.RUBY_TRIDENT.get(), ResourceLocation.withDefaultNamespace("throwing"),
                        (stack, level, entity, seed) -> entity != null && entity.isUsingItem() && entity.getUseItem() == stack ? 1.0f : 0.0f);
                // el agua del Nether es transparente como el agua
                ItemBlockRenderTypes.setRenderLayer(ModFluids.NETHER_WATER.get(), RenderType.translucent());
                ItemBlockRenderTypes.setRenderLayer(ModFluids.FLOWING_NETHER_WATER.get(), RenderType.translucent());
            });
        }

        /** Agua del Nether: texturas animadas, niebla morada bajo el agua (como en la foto del usuario). */
        /** El dibujo plano del Tridente de Rubí (para el inventario) se carga aparte del modelo 3D. */
        @SubscribeEvent
        public static void additionalModels(net.neoforged.neoforge.client.event.ModelEvent.RegisterAdditional event) {
            event.register(RubyTridentItemRenderer.INVENTORY_MODEL);
        }

        @SubscribeEvent
        public static void clientExtensions(RegisterClientExtensionsEvent event) {
            // Tridente de Rubí: modelo 3D rojo en la mano
            event.registerItem(new net.neoforged.neoforge.client.extensions.common.IClientItemExtensions() {
                private RubyTridentItemRenderer renderer;

                @Override
                public net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer getCustomRenderer() {
                    if (renderer == null) {
                        renderer = new RubyTridentItemRenderer();
                    }
                    return renderer;
                }
            }, ModItems.RUBY_TRIDENT.get());
            event.registerFluidType(new IClientFluidTypeExtensions() {
                private final ResourceLocation still = CivilizacionNether.id("block/nether_water_still");
                private final ResourceLocation flow = CivilizacionNether.id("block/nether_water_flow");
                private final ResourceLocation overlay = ResourceLocation.withDefaultNamespace("textures/misc/underwater.png");

                @Override
                public ResourceLocation getStillTexture() {
                    return still;
                }

                @Override
                public ResourceLocation getFlowingTexture() {
                    return flow;
                }

                @Override
                public ResourceLocation getOverlayTexture() {
                    return flow;
                }

                @Override
                public ResourceLocation getRenderOverlayTexture(Minecraft mc) {
                    return overlay;
                }

                @Override
                public int getTintColor() {
                    return 0xFFFFFFFF;
                }

                @Override
                public Vector3f modifyFogColor(Camera camera, float partialTick, ClientLevel level, int renderDistance,
                                               float darkenWorldAmount, Vector3f fluidFogColor) {
                    return new Vector3f(0.32f, 0.10f, 0.58f);
                }

                @Override
                public void modifyFogRender(Camera camera, FogRenderer.FogMode mode, float renderDistance, float partialTick,
                                            float nearDistance, float farDistance, FogShape shape) {
                    RenderSystem.setShaderFogStart(-4.0f);
                    RenderSystem.setShaderFogEnd(40.0f);
                }
            }, ModFluids.NETHER_WATER_TYPE.get());
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
            while (GRAB_KEY.consumeClick()) {
                if (mc.player != null && mc.player.getVehicle() instanceof NetherDragonEntity) {
                    PacketDistributor.sendToServer(new com.civilizacionnether.network.DragonGrabPayload());
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

        /** Armadura del Frío Eterno completa: se ve perfecto dentro de la lava. */
        @SubscribeEvent
        public static void lavaFog(ViewportEvent.RenderFog event) {
            Minecraft mc = Minecraft.getInstance();
            if (event.getType() == FogType.LAVA && mc.player != null && FrostArmorEvents.hasFullFrost(mc.player)) {
                event.setNearPlaneDistance(0.0f);
                event.setFarPlaneDistance(96.0f);
                event.setCanceled(true);
            }
        }

        /** Con el set del Frío Eterno no se ve el fuego en la cara (ni en la lava ni prendido). */
        @SubscribeEvent
        public static void noFireOverlay(net.neoforged.neoforge.client.event.RenderBlockScreenEffectEvent event) {
            if (event.getOverlayType() == net.neoforged.neoforge.client.event.RenderBlockScreenEffectEvent.OverlayType.FIRE
                    && FrostArmorEvents.hasFullFrost(event.getPlayer())) {
                event.setCanceled(true);
            }
        }

        /** Bajo la lava con el Frío Eterno el color de la niebla es más claro (se ve como bajo el agua, pero naranja). */
        @SubscribeEvent
        public static void lavaFogColor(ViewportEvent.ComputeFogColor event) {
            Minecraft mc = Minecraft.getInstance();
            if (mc.player != null && event.getCamera().getFluidInCamera() == FogType.LAVA && FrostArmorEvents.hasFullFrost(mc.player)) {
                event.setRed(0.55f);
                event.setGreen(0.25f);
                event.setBlue(0.08f);
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
