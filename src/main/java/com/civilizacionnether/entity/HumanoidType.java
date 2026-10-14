package com.civilizacionnether.entity;

/**
 * Las clases de la civilización del Nether. Cada una tiene su propio modelo, textura y animaciones
 * (geo/entity/&lt;model&gt;.geo.json, textures/entity/&lt;texture&gt;.png, animations/entity/&lt;model&gt;.animation.json).
 */
public enum HumanoidType {
    //           id                 modelo         textura         prefijo de animaciones        vida daño armad. veloc. combate        cooldown escala ancho alto  huevo fondo/manchas
    GUERRERO("guerrero", "warrior", "warrior", "animation.nether_warrior.", 36, 6, 6, 0.30, Combat.MELEE, 18, 1.13f, 0.7f, 2.4f, 0x2A2228, 0xD6A026),
    ARQUERO("arquero", "archer", "archer", "animation.nether_archer.", 28, 4, 3, 0.31, Combat.BOW, 34, 1.13f, 0.7f, 2.4f, 0x46101A, 0xEC4040),
    REY_NECROMANCER("rey_necromancer", "necro_king", "necro_king", "animation.necro_king.", 160, 10, 10, 0.27, Combat.SPELL, 30, 1.1f, 0.8f, 2.6f, 0x141012, 0xC81A20),
    SUBDITO_ALMA("subdito_alma", "warrior", "soul_minion", "animation.nether_warrior.", 20, 5, 2, 0.33, Combat.MELEE, 16, 1.0f, 0.6f, 2.1f, 0x0E1A34, 0x5AF5F5);

    public enum Combat { MELEE, BOW, SPELL }

    public final String id;
    public final String model;
    public final String texture;
    public final String animPrefix;
    public final double health;
    public final double damage;
    public final double armor;
    public final double speed;
    public final Combat combat;
    public final int attackCooldown;
    public final float renderScale;
    public final float width;
    public final float height;
    public final int eggBackground;
    public final int eggSpots;

    HumanoidType(String id, String model, String texture, String animPrefix, double health, double damage, double armor,
                 double speed, Combat combat, int attackCooldown, float renderScale, float width, float height,
                 int eggBackground, int eggSpots) {
        this.id = id;
        this.model = model;
        this.texture = texture;
        this.animPrefix = animPrefix;
        this.health = health;
        this.damage = damage;
        this.armor = armor;
        this.speed = speed;
        this.combat = combat;
        this.attackCooldown = attackCooldown;
        this.renderScale = renderScale;
        this.width = width;
        this.height = height;
        this.eggBackground = eggBackground;
        this.eggSpots = eggSpots;
    }

    public boolean isKing() {
        return this == REY_NECROMANCER;
    }

    public boolean isSoul() {
        return this == SUBDITO_ALMA;
    }

    /** Solo guerreros y arqueros forman familias (chuleta de cerdo asada). */
    public boolean canBreed() {
        return this == GUERRERO || this == ARQUERO;
    }

    public boolean hasSitAnimation() {
        return this == GUERRERO || this == ARQUERO;
    }
}
