# Civilización del Nether

Mod para **Minecraft Java 1.21.1** con **NeoForge** (requiere **GeckoLib 4.7+**).

- Clases de la civilización, cada una con modelo, skin y animaciones propias:
  - **Guerrero del Nether** (espada de rubí). Se domestica con **rubíes**.
  - **Arquero del Nether** (arco de rubí en la mano izquierda). Se domestica con **rubíes**.
  - **Rey Necromancer**: aliado, aparece en el **trono de la capital** (y muy raro en otras partes del Nether).
    Ataca a distancia con rayos de almas e invoca **Súbditos de Almas** que lo defienden. Se domestica con
    **3 manzanas doradas encantadas**. Al morir suelta su **báculo**.
- Domesticados: **clic derecho** = se quedan quietos; otro clic derecho = vuelven a seguirte.
- Guerreros y arqueros se reproducen con **chuleta de cerdo asada**.
- Aliados del jugador, aldeanos, golems y todos sus aliados; atacan a los mobs hostiles.
- **Dragón del Nether** (domesticable y montable):
  - Nace de un **huevo** que pones en el suelo (5 min; la mitad con lava, magma o fuego cerca). La cría es tuya.
  - **Crece por fases** al darle carne o pescado: recién nacido → cría → joven → subadulto → adulto.
  - En estado natural **camina, vuela y descansa** cuando se queda quieto.
  - Adulto + **silla de montar**: se monta y vuela hacia donde miras.
  - Montado: **clic derecho** dispara bolas de fuego; cada disparo carga la **barra de ráfaga** (3).
    Con la barra llena, **R** lanza una **ráfaga de fuego grande**.
  - Dos adultos domesticados alimentados con carne asada **ponen un huevo**. También hay un huevo en el nido de la capital.
  - Su fuego es **negro**, con partículas de **almas rojas**.
  - **X** (montado): cámara de dragón en tercera persona alejada; otra vez X vuelve a primera persona.
  - **Báculo de dragón** (crafteo: rubí y alma arriba, oro y rubí al medio, vara de blaze abajo): clic derecho = tu dragón
    viene volando o caminando hacia ti; mayús + clic derecho = **modo libre** (anda, vuela y descansa por su cuenta).
    Clic derecho a un dragón con el báculo lo vincula a ese dragón.
- **Almas:** todas las criaturas del mod sueltan un **Alma** al morir.
  - **Hoz de almas** (crafteo: 2 rubíes + 1 alma arriba y 2 varas de blaze en diagonal): al romper **arena de almas**
    suelta almas: sin encantar 1, Fortuna I 1-2, Fortuna II 2-3, Fortuna III 3.
  - **Soporte para pociones** con el Alma arriba: botellas de agua → **Poción de Alma** (Fuerza, Resistencia,
    Resistencia al fuego y Regeneración); cualquier otra poción → la misma poción **encantada** (un nivel más y 50 % más larga).
- **La capital del Reino del Nether** (176 × 176 bloques) se genera en el Nether, dentro de su propia caverna gigante:
  castillo real con sala del trono y patio, plaza central con fuente, distrito comercial (tiendas y puestos),
  barrio residencial (60+ casas), talleres y almacenes, zona militar (cuarteles, armería, entrenamiento, torres),
  murallas con 4 puertas fortificadas y torres, y montañas con minas y campamento minero.
  Para encontrarla: `/locate structure civilizacion_nether:capital`.
- Rubí, mena, bloques, espada, arco, armadura 3D de rubí, el Báculo del Rey Necromancer (3D), el huevo de dragón, la armadura de dragón y la Hoz de almas. Todos con crafteo (el Alma se obtiene de las criaturas y de la arena de almas).

El manual completo está en `Manual_Civilizacion_del_Nether.docx`.

## Obtener el .jar

**Opción fácil (sin instalar nada):** sube esta carpeta a un repositorio de GitHub. La pestaña **Actions**
compila el mod sola; descarga el artefacto `civilizacion_nether-jar`.

**En tu PC:** instala Java 21 y Gradle 8.14, abre una terminal en esta carpeta y ejecuta `gradle build`.
El mod queda en `build/libs/civilizacion_nether-1.0.0.jar`.

## Regenerar recursos

`python tools/generate.py` (requiere Pillow y numpy). Sobrescribe modelos y texturas.

## Créditos

- Cuerpo, alas y animaciones base del dragón: modelo **"Void Dragon" por RedVoid_** (CC BY 4.0).
- Cabeza del dragón: modelo **"Dragon Head" por Joshie Models BB** (CC BY 4.0).

Ambos modelos se adaptaron (recoloreado, cuerpo más grande, alas más gruesas, montura y animaciones nuevas).
Licencia CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
