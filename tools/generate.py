"""Regenera TODOS los recursos del mod (modelos, animaciones, texturas, datos y el reino).

Uso:  python tools/generate.py      (requiere Python 3, Pillow y numpy:  pip install pillow numpy)

Si editas un modelo o una textura a mano en Blockbench, NO vuelvas a ejecutar este script
o se sobrescribirán tus cambios.
"""
import models
import textures
import datagen
import datagen2
import armor
import armor_items
import armor2
import warrior
import archer
import necro
import royal
import humans
import dragon_v2
import souls
import blocks2
import kingdom
import sealife
import manual
import aldeanos
import infernal_saddle

if __name__ == "__main__":
    h, d = models.write_all()
    textures.write_all(h, d)
    warrior.write_all()      # Guerrero (modelo del usuario + animaciones)
    archer.write_all()       # Arquero (capucha, máscara, carcaj, arco en la mano izquierda)
    necro.write_all()        # Rey Necromancer, báculo 3D y Súbdito de Almas
    royal.write_all()        # Guerrero Real (espada larga) y Ballestero
    humans.write_all()       # profesiones (skins del usuario), mujeres soldado y Aldeano Necromancer
    souls.write_all()        # Alma (skin del usuario), Hoz de almas, partículas de fuego negro y almas rojas
    dragon_v2.write_all()    # Dragón del Nether (Void Dragon de RedVoid_ + cabeza de Joshie Models BB) y su huevo
    textures.glowmasks()
    datagen.write_all()
    datagen2.write_all()     # nombres, crafteos, botín, voces, bioma Océano Púrpura y árbol de hielo
    armor.write_all()
    armor_items.write_assets()
    armor2.write_all()       # Armadura Humana del Nether y del Frío Eterno
    blocks2.write_all()      # mesas de trabajo, cama y agua del Nether, hojas de hielo
    aldeanos.write_all()     # aldeanos del Nether: 5 mesas nuevas, skins con ojos que brillan, etiquetas y nombres
    manual.write_all()       # el manual (el libro dentro del juego)
    sealife.write_all()      # fauna del Océano Púrpura (12 criaturas) y Dragón Infernal con su nido
    infernal_saddle.write_all()  # silla visible del Dragón Infernal (hueso nuevo + su propia textura) y su crafteo
    info = kingdom.write_all()
    print("Recursos generados. Reino: %d bloques, %d habitantes." % info)
