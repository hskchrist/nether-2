"""Manual de la Civilización del Nether: el mismo libro de Claude (libro.html) dentro del juego como ítem.

Las páginas son capturas del libro (tools/ref/manual/page_XXX.png, una por cara) y el índice sale de su índice.
El jugador lo recibe la primera vez que entra a un mundo y se craftea con un libro y un rubí.
"""
import json
import os
import shutil

from PIL import Image

from common import ASSETS, DATA, MODID, save_json

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "ref", "manual")
R = MODID + ":"


def icon():
    """Ícono del Manual: el fantasma rojo dibujado por Darthdrip Vader (13x20, píxeles intactos) en un lienzo 32x32."""
    return Image.open(os.path.join(HERE, "ref", "manual_icon.png")).convert("RGBA")


def write_all():
    icon().save(os.path.join(ASSETS, "textures", "item", "manual.png"))
    save_json(os.path.join(ASSETS, "models", "item", "manual.json"),
              {"parent": "minecraft:item/generated", "textures": {"layer0": R + "item/manual"}})
    save_json(os.path.join(DATA, "recipe", "manual.json"), {
        "type": "minecraft:crafting_shapeless", "category": "misc",
        "ingredients": [{"item": "minecraft:book"}, {"item": R + "ruby"}], "result": {"id": R + "manual", "count": 1}})
    for code in ("es_es", "es_cl", "es_mx", "es_ar", "en_us"):
        p = os.path.join(ASSETS, "lang", code + ".json")
        d = json.load(open(p, encoding="utf-8"))
        en = code == "en_us"
        d["item.civilizacion_nether.manual"] = "Nether Civilization Manual" if en else "Manual de la Civilización del Nether"
        d["tooltip.civilizacion_nether.manual"] = "Right click to read it" if en else "Clic derecho para leerlo"
        d["gui.civilizacion_nether.manual.prev"] = "◀ Back" if en else "◀ Atrás"
        d["gui.civilizacion_nether.manual.next"] = "Next ▶" if en else "Pasar ▶"
        d["gui.civilizacion_nether.manual.index"] = "Contents" if en else "Índice"
        d["gui.civilizacion_nether.manual.close"] = "Close" if en else "Cerrar"
        save_json(p, d)
    # páginas e índice
    if os.path.isdir(REF):
        out = os.path.join(ASSETS, "textures", "gui", "manual")
        os.makedirs(out, exist_ok=True)
        for f in os.listdir(out):
            os.remove(os.path.join(out, f))
        for f in sorted(os.listdir(REF)):
            if f.endswith(".png"):
                shutil.copy(os.path.join(REF, f), os.path.join(out, f))
        shutil.copy(os.path.join(REF, "index.json"), os.path.join(ASSETS, "manual_index.json"))


if __name__ == "__main__":
    write_all()
