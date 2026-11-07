package com.civilizacionnether.entity;

/**
 * Las clases de la civilización del Nether. Cada una tiene su modelo (geo/entity/&lt;model&gt;.geo.json),
 * sus animaciones (animations/entity/&lt;anim&gt;.animation.json) y sus texturas.
 * <ul>
 *   <li>Soldados (guerrero, arquero, guerrero real, ballestero): se contratan con rubíes, tienen hombre y mujer.</li>
 *   <li>Profesiones (bibliotecario, domador, granjero, minero, ciudadano): skins del usuario elegidas al azar,
 *       trabajan en su mesa, comercian y pelean contra los hostiles.</li>
 *   <li>Aldeano Necromancer: modelo de aldeano, comercia almas y esmeraldas; no pelea, huye de los no muertos.</li>
 *   <li>Rey Necromancer y Súbdito de Almas: como antes.</li>
 * </ul>
 */
public enum HumanoidType {
    GUERRERO(new Spec("guerrero", "warrior", "warrior").anim("warrior", "animation.nether_warrior.")
            .stats(36, 6, 6, 0.30).combat(Combat.MELEE, 18).size(1.13f, 0.7f, 2.4f).egg(0x2A2228, 0xD6A026)
            .soldier().skins(0, 0).item("ruby_sword")),
    ARQUERO(new Spec("arquero", "archer", "archer").anim("archer", "animation.nether_archer.")
            .stats(28, 4, 3, 0.31).combat(Combat.BOW, 34).size(1.13f, 0.7f, 2.4f).egg(0x46101A, 0xEC4040)
            .soldier().skins(0, 0).offhand("ruby_bow")),
    REY_NECROMANCER(new Spec("rey_necromancer", "necro_king", "necro_king").anim("necro_king", "animation.necro_king.")
            .stats(160, 10, 10, 0.27).combat(Combat.SPELL, 30).size(1.1f, 0.8f, 2.6f).egg(0x141012, 0xC81A20)),
    SUBDITO_ALMA(new Spec("subdito_alma", "warrior", "soul_minion").anim("warrior", "animation.nether_warrior.")
            .stats(20, 5, 2, 0.33).combat(Combat.MELEE, 16).size(1.0f, 0.6f, 2.1f).egg(0x0E1A34, 0x5AF5F5)),
    GUERRERO_REAL(new Spec("guerrero_real", "royal_warrior", "royal_warrior").anim("royal_warrior", "animation.nether_royal_warrior.")
            .stats(48, 9, 9, 0.29).combat(Combat.MELEE, 22).size(1.15f, 0.7f, 2.45f).egg(0x1C1C28, 0xE8BE38)
            .soldier().skins(0, 0).item("ruby_longsword")),
    BALLESTERO(new Spec("ballestero", "crossbowman", "crossbowman").anim("crossbowman", "animation.nether_crossbowman.")
            .stats(32, 6, 5, 0.30).combat(Combat.CROSSBOW, 44).size(1.13f, 0.7f, 2.4f).egg(0x3A2418, 0xB8B8C8)
            .soldier().skins(0, 0).item("ruby_crossbow")),
    BIBLIOTECARIO(new Spec("bibliotecario", "warrior", "human").anim("human", "animation.nether_human.")
            .stats(24, 3, 2, 0.30).combat(Combat.MELEE, 20).size(1.05f, 0.6f, 2.2f).egg(0xE8E0D0, 0xA0141E)
            .profession("librarian_lectern").skins(3, 3).item("minecraft:book")),
    DOMADOR(new Spec("domador", "warrior", "human").anim("human", "animation.nether_human.")
            .stats(30, 5, 4, 0.30).combat(Combat.MELEE, 18).size(1.08f, 0.62f, 2.25f).egg(0x2A2A30, 0xC8A050)
            .profession("tamer_nest").skins(3, 3).item("dragon_staff")),
    GRANJERO(new Spec("granjero", "warrior", "human").anim("human", "animation.nether_human.")
            .stats(24, 4, 2, 0.30).combat(Combat.MELEE, 20).size(1.05f, 0.6f, 2.2f).egg(0x4A7AB0, 0x8E2A2A)
            .profession("farmer_basket").skins(4, 4).item("minecraft:iron_hoe")),
    MINERO(new Spec("minero", "warrior", "human").anim("human", "animation.nether_human.")
            .stats(28, 5, 3, 0.30).combat(Combat.MELEE, 20).size(1.08f, 0.62f, 2.25f).egg(0x2A1414, 0xE02020)
            .profession("miner_cart").skins(6, 5).item("minecraft:iron_pickaxe")),
    CIUDADANO(new Spec("ciudadano", "warrior", "human").anim("human", "animation.nether_human.")
            .stats(22, 3, 2, 0.30).combat(Combat.MELEE, 20).size(1.05f, 0.6f, 2.2f).egg(0x8A5030, 0xE0A020)
            .profession(null).skins(1, 1)),
    ALDEANO_NECROMANCER(new Spec("aldeano_necromancer", "aldeano_necromancer", "human").anim("aldeano_necromancer", "animation.aldeano_necromancer.")
            .stats(22, 0, 1, 0.32).combat(Combat.NONE, 20).size(1.0f, 0.6f, 1.95f).egg(0x141016, 0xC0186A)
            .profession("necromancer_table").skins(0, 0).villagerModel());

    public enum Combat { MELEE, BOW, CROSSBOW, SPELL, NONE }

    /** Datos de cada clase (se arma con métodos encadenados para que la lista de arriba sea fácil de leer). */
    static final class Spec {
        final String id;
        final String model;
        final String texture;
        String anim;
        String animPrefix;
        double health, damage, armor, speed;
        Combat combat = Combat.MELEE;
        int cooldown = 20;
        float renderScale = 1.0f, width = 0.6f, height = 1.95f;
        int eggBg, eggSpots;
        boolean soldier;
        boolean professional;
        String workstation;
        int maleSkins, femaleSkins;
        boolean villager;
        String mainItem, offItem;

        Spec(String id, String model, String texture) {
            this.id = id;
            this.model = model;
            this.texture = texture;
        }

        Spec anim(String a, String prefix) { this.anim = a; this.animPrefix = prefix; return this; }
        Spec stats(double h, double d, double a, double s) { health = h; damage = d; armor = a; speed = s; return this; }
        Spec combat(Combat c, int cd) { combat = c; cooldown = cd; return this; }
        Spec size(float scale, float w, float h) { renderScale = scale; width = w; height = h; return this; }
        Spec egg(int bg, int spots) { eggBg = bg; eggSpots = spots; return this; }
        Spec soldier() { soldier = true; return this; }
        Spec profession(String station) { professional = true; workstation = station; return this; }
        Spec skins(int m, int f) { maleSkins = m; femaleSkins = f; return this; }
        Spec villagerModel() { villager = true; return this; }
        Spec item(String i) { mainItem = i; return this; }
        Spec offhand(String i) { offItem = i; return this; }
    }

    public final String id;
    public final String model;
    public final String texture;
    public final String anim;
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
    /** Soldados: se contratan con rubíes. */
    public final boolean soldier;
    /** Profesiones: viven en el reino, trabajan en su mesa. */
    public final boolean professional;
    /** Bloque de trabajo (id del mod) o null. */
    public final String workstation;
    /** Cantidad de skins de hombre / mujer (0 y 0 = la textura única del modelo, con versión mujer "_f"). */
    public final int maleSkins;
    public final int femaleSkins;
    public final boolean villagerModel;
    public final String mainItem;
    public final String offItem;

    HumanoidType(Spec s) {
        this.id = s.id;
        this.model = s.model;
        this.texture = s.texture;
        this.anim = s.anim;
        this.animPrefix = s.animPrefix;
        this.health = s.health;
        this.damage = s.damage;
        this.armor = s.armor;
        this.speed = s.speed;
        this.combat = s.combat;
        this.attackCooldown = s.cooldown;
        this.renderScale = s.renderScale;
        this.width = s.width;
        this.height = s.height;
        this.eggBackground = s.eggBg;
        this.eggSpots = s.eggSpots;
        this.soldier = s.soldier;
        this.professional = s.professional;
        this.workstation = s.workstation;
        this.maleSkins = s.maleSkins;
        this.femaleSkins = s.femaleSkins;
        this.villagerModel = s.villager;
        this.mainItem = s.mainItem;
        this.offItem = s.offItem;
    }

    public boolean isKing() {
        return this == REY_NECROMANCER;
    }

    public boolean isSoul() {
        return this == SUBDITO_ALMA;
    }

    /** Humanos con hombre y mujer: forman familias, duermen y comercian. El Rey y los súbditos no. */
    public boolean isGendered() {
        return !isKing() && !isSoul();
    }

    public boolean canBreed() {
        return isGendered();
    }

    public boolean canTrade() {
        return !isSoul();
    }

    public boolean fleesUndead() {
        return this == ALDEANO_NECROMANCER;
    }

    public boolean hasSitAnimation() {
        return soldier || professional;
    }

    /** Textura según género y variante. */
    public String textureFor(boolean female, int variant) {
        if (villagerModel) {
            return "textures/entity/human/aldeano_necromancer.png";
        }
        if (maleSkins > 0) {
            int n = female ? femaleSkins : maleSkins;
            int v = Math.floorMod(variant, Math.max(1, n));
            return "textures/entity/human/" + id + "_" + (female ? "f" : "m") + "_" + v + ".png";
        }
        if (isGendered() && female) {
            return "textures/entity/" + texture + "_f.png";
        }
        return "textures/entity/" + texture + ".png";
    }

    public int skinCount(boolean female) {
        return Math.max(1, female ? femaleSkins : maleSkins);
    }
}
