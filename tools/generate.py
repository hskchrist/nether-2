"""Regenera TODOS los recursos del mod (modelos, animaciones, texturas, datos y la capital).

Uso:  python tools/generate.py      (requiere Python 3, Pillow y numpy:  pip install pillow numpy)

Si editas un modelo o una textura a mano en Blockbench, NO vuelvas a ejecutar este script
o se sobrescribirán tus cambios.
"""
import models
import textures
import datagen
import capital
import armor
import armor_items
import warrior
import archer
import necro
import dragon_v2
import souls

if __name__ == "__main__":
    h, d = models.write_all()
    textures.write_all(h, d)
    warrior.write_all()      # Guerrero (modelo del usuario + animaciones)
    archer.write_all()       # Arquero (capucha, máscara, carcaj, arco en la mano izquierda)
    necro.write_all()        # Rey Necromancer, báculo 3D y Súbdito de Almas
    souls.write_all()        # Alma (skin del usuario), Hoz de almas, partículas de fuego negro y almas rojas
    dragon_v2.write_all()    # Dragón del Nether (Void Dragon de RedVoid_ + cabeza de Joshie Models BB) y su huevo
    textures.glowmasks()
    datagen.write_all()
    armor.write_all()
    armor_items.write_assets()
    w, info = capital.write_all()
    print("Recursos generados. Capital: %d bloques, %d tipos de bloque, %d habitantes, %d casas." % (info + (w.houses,)))
