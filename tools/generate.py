"""Regenera TODOS los recursos del mod (modelos, animaciones, texturas, datos y el reino).

Uso:  python tools/generate.py      (requiere Python 3, Pillow y numpy:  pip install pillow numpy)

Si editas un modelo o una textura a mano en Blockbench, NO vuelvas a ejecutar este script
o se sobrescribirán tus cambios.
"""
import os
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
import dragon_species
import mar_del_nether
import encantamientos
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
    mar_del_nether.write_all()   # bioma Mar del Nether: pasto, hierba, cristales, carámbanos y tronco del Árbol de Hielo
    encantamientos.write_all()   # Escudo de Dragón (contra los disparos de los dragones)
    dragon_species.write_all()   # Dragón de Almas y de Obsidiana (skins del usuario), huevos, nidos y biomas
    infernal_saddle.write_all()  # silla visible del Dragón Infernal (hueso nuevo + su propia textura) y su crafteo
    info = kingdom.write_all()
    # GeckoLib cierra el juego si una máscara de brillo está vacía: esas se borran (sin máscara = sin brillo)
    import glob
    import numpy as np
    from PIL import Image
    for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets",
                                    "civilizacion_nether", "textures", "**", "*_glowmask.png"), recursive=True):
        if not (np.array(Image.open(f).convert("RGBA"))[..., 3] > 0).any():
            os.remove(f)
    print("Recursos generados. Reino: %d bloques, %d habitantes." % info)
