package com.civilizacionnether.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.core.particles.SimpleParticleType;

/** Llama negra del aliento del dragón: se encoge mientras avanza y se apaga. */
public class BlackFlameParticle extends TextureSheetParticle {
    private final SpriteSet sprites;

    protected BlackFlameParticle(ClientLevel level, double x, double y, double z, double dx, double dy, double dz, SpriteSet sprites) {
        super(level, x, y, z, dx, dy, dz);
        this.sprites = sprites;
        this.xd = dx + (this.random.nextDouble() - 0.5) * 0.02;
        this.yd = dy + (this.random.nextDouble() - 0.5) * 0.02;
        this.zd = dz + (this.random.nextDouble() - 0.5) * 0.02;
        this.quadSize *= 1.4f + this.random.nextFloat() * 0.8f;
        this.lifetime = 12 + this.random.nextInt(10);
        this.hasPhysics = false;
        this.friction = 0.94f;
        setSpriteFromAge(sprites);
    }

    @Override
    public void tick() {
        super.tick();
        if (!this.removed) {
            setSpriteFromAge(this.sprites);
        }
    }

    @Override
    public ParticleRenderType getRenderType() {
        return ParticleRenderType.PARTICLE_SHEET_OPAQUE;
    }

    public static class Provider implements ParticleProvider<SimpleParticleType> {
        private final SpriteSet sprites;

        public Provider(SpriteSet sprites) {
            this.sprites = sprites;
        }

        @Override
        public Particle createParticle(SimpleParticleType type, ClientLevel level, double x, double y, double z,
                                       double dx, double dy, double dz) {
            return new BlackFlameParticle(level, x, y, z, dx, dy, dz, this.sprites);
        }
    }
}
