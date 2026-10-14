package com.civilizacionnether.client.particle;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.core.particles.SimpleParticleType;

/** Alma roja (la skin del alma): sube flotando, brilla en la oscuridad y se desvanece. */
public class RedSoulParticle extends TextureSheetParticle {
    protected RedSoulParticle(ClientLevel level, double x, double y, double z, double dx, double dy, double dz, SpriteSet sprites) {
        super(level, x, y, z, dx, dy, dz);
        this.xd = dx * 0.5 + (this.random.nextDouble() - 0.5) * 0.02;
        this.yd = dy * 0.5 + 0.03 + this.random.nextDouble() * 0.02;
        this.zd = dz * 0.5 + (this.random.nextDouble() - 0.5) * 0.02;
        this.quadSize *= 1.2f + this.random.nextFloat() * 0.6f;
        this.lifetime = 24 + this.random.nextInt(16);
        this.hasPhysics = false;
        this.friction = 0.92f;
        this.gravity = -0.01f;
        pickSprite(sprites);
    }

    @Override
    public void tick() {
        super.tick();
        float life = (float) this.age / this.lifetime;
        this.alpha = life < 0.7f ? 1.0f : 1.0f - (life - 0.7f) / 0.3f;
    }

    @Override
    public ParticleRenderType getRenderType() {
        return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
    }

    @Override
    protected int getLightColor(float partialTick) {
        return 0xF000F0; // brilla aunque esté oscuro
    }

    public static class Provider implements ParticleProvider<SimpleParticleType> {
        private final SpriteSet sprites;

        public Provider(SpriteSet sprites) {
            this.sprites = sprites;
        }

        @Override
        public Particle createParticle(SimpleParticleType type, ClientLevel level, double x, double y, double z,
                                       double dx, double dy, double dz) {
            return new RedSoulParticle(level, x, y, z, dx, dy, dz, this.sprites);
        }
    }
}
