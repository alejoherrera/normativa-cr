# Instrucciones para modelos y agentes de IA

Este archivo es para cualquier modelo o agente (Claude, GPT, Gemini, Copilot, etc.) que trabaje en este
repositorio. Las reglas de `CONSTITUTION.md` prevalecen sobre todo lo demás.

## Lo que este proyecto es

Un conjunto de datos de normativa costarricense cuyo **contenido sale únicamente del Diario Oficial La Gaceta**
(PDF de la Imprenta Nacional). Cada dato tiene que poder rastrearse hasta un PDF oficial y una página.

## Reglas obligatorias

1. **Fuente del contenido: solo La Gaceta.** Texto, títulos, fechas, páginas y relaciones se toman del PDF
   oficial en `https://www.imprentanacional.go.cr/pub/AAAA/MM/DD/…`.
2. **El SCIJ/SINALEVI solo como índice.** Se puede consultar para saber en qué Gaceta se publicó una norma,
   con pocas consultas y a ritmo humano. **Nunca** copiar de ahí textos consolidados, notas («Nota de
   Sinalevi»), «Así reformado…», concordancias, descriptores ni identificadores internos. La Procuraduría ha
   manifestado que reclama derechos sobre ese contenido editorial. Si se usó como índice, decirlo en
   `localizacion`.
3. **No inventar.** Si no se puede verificar un dato en el PDF, no se pone. Nunca deduzcas un número de
   Gaceta, una fecha o una relación «porque suena bien».
4. **Toda relación lleva una cita literal** del texto oficial que la establece (`cita`). `construir.py` la
   comprueba; si no aparece literalmente, la relación no va.
5. **Descarga respetuosa.** Una petición por documento, con pausa (ya lo hace `construir.py`). Nada de
   barridos masivos. Si un sitio muestra CAPTCHA, desafío o bloqueo, **detente**: no intentes evadirlo.
6. **Cuidado con la maquetación.** La Gaceta ordinaria es a dos columnas y a veces intercala otras
   publicaciones. Después de construir, revisa el inicio y el final de cada texto nuevo y busca encabezados de
   otras normas dentro. Si hay un tramo ajeno, exclúyelo con `excluir` y explica el motivo.
7. **Escaneos.** Si el texto del PDF es una imagen con OCR defectuoso, no publiques el texto:
   `texto_incluido: false` con `motivo_sin_texto`.
8. **No edites `schema/norma.v1.json`** una vez publicado: los cambios de contrato van en `norma.v2.json`.
9. **Nada se entrega con la validación en rojo.** `python src/construir.py`, `python src/validar.py` y
   `python -m pytest -q tests` deben pasar.

## Cómo agregar una norma (pasos)

Sigue `CONTRIBUTING.md`, sección «Agregar una norma». En resumen:

1. Ubica la publicación (Gaceta, alcance y fecha) y la URL del PDF en la Imprenta Nacional.
2. Descarga y verifica que la norma esté en ese PDF; anota la página inicial y final.
3. Agrega la entrada en `catalogo.json` (marcadores de inicio y fin, título, relaciones con cita).
4. Corre `python src/construir.py`. Si aborta, corrige el catálogo; no fuerces el código.
5. Revisa a mano el texto generado (bordes y tramos ajenos).
6. Corre `python src/validar.py` y `python -m pytest -q tests`.
7. Abre un *pull request* con la plantilla completa.

## Lo que no debes hacer

- Modificar `construir.py` o `validar.py` para que una verificación «pase». Si falla, el dato está mal.
- Agregar textos consolidados o resúmenes propios dentro de los textos oficiales.
- Subir los PDF al repositorio (se enlazan, no se redistribuyen).
- Presentar el proyecto como fuente oficial.
