package com.civilizacionnether.entity;

import net.minecraft.util.Mth;

/**
 * Fases de crecimiento del Dragón del Nether (crecimiento 0..1, sube al alimentarlo con carne y pescado).
 * Entre fases todo se interpola, así que crece poco a poco con cada comida.
 * <pre>
 *  fase            crecimiento  tamaño  cabeza  alas  cola  cuello  patas
 *  Recién nacido   0 %          0.24    1.70    0.45  0.60  0.70    0.80
 *  Cría            15 %         0.38    1.45    0.62  0.72  0.80    0.85
 *  Joven           40 %         0.58    1.22    0.80  0.85  0.90    0.92   (ya lanza aliento y puede volar)
 *  Subadulto       70 %         0.80    1.08    0.93  0.95  1.00    0.97
 *  Adulto          100 %        1.00    1.00    1.00  1.00  1.00    1.00   (se puede montar)
 * </pre>
 */
public final class DragonStages {
    public static final float[] GROW = {0.00f, 0.15f, 0.40f, 0.70f, 1.00f};
    public static final float[] SIZE = {0.24f, 0.38f, 0.58f, 0.80f, 1.00f};
    public static final float[] HEAD = {1.70f, 1.45f, 1.22f, 1.08f, 1.00f};
    public static final float[] WINGS = {0.45f, 0.62f, 0.80f, 0.93f, 1.00f};
    public static final float[] TAIL = {0.60f, 0.72f, 0.85f, 0.95f, 1.00f};
    public static final float[] NECK = {0.70f, 0.80f, 0.90f, 1.00f, 1.00f};
    public static final float[] LEGS = {0.80f, 0.85f, 0.92f, 0.97f, 1.00f};

    /** Desde "Joven" puede volar y lanzar aliento de almas. */
    public static final float CAN_FLY = 0.40f;

    /** Vida y mordida del recién nacido y del adulto (se interpolan con el tamaño). */
    public static final double HEALTH_BABY = 20.0;
    public static final double HEALTH_ADULT = 200.0;
    public static final double BITE_BABY = 3.0;
    public static final double BITE_ADULT = 16.0;

    /** Índice de la fase actual (0 = recién nacido ... 4 = adulto). */
    public static int stage(float growth) {
        int s = 0;
        for (int i = 0; i < GROW.length; i++) {
            if (growth >= GROW[i] - 1.0e-4f) {
                s = i;
            }
        }
        return s;
    }

    /** Valor interpolado de una tabla según el crecimiento. */
    public static float lerp(float[] table, float growth) {
        float g = Mth.clamp(growth, 0.0f, 1.0f);
        for (int i = 0; i < GROW.length - 1; i++) {
            if (g <= GROW[i + 1]) {
                float t = (g - GROW[i]) / (GROW[i + 1] - GROW[i]);
                return Mth.lerp(t, table[i], table[i + 1]);
            }
        }
        return table[table.length - 1];
    }

    private DragonStages() {
    }
}
