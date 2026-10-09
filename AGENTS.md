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
   `texto_incluido: false` con `motivo_sin_texto`. Que el PDF «tenga texto seleccionable» no prueba que no sea
   un escaneo: muchos traen una capa OCR invisible debajo de la imagen. Compruébalo (ver «Controles de calidad
   del texto»).
8. **No edites `schema/norma.v1.json`** una vez publicado: los cambios de contrato van en `norma.v2.json`.
9. **Nada se entrega con la validación en rojo.** `python src/construir.py`, `python src/validar.py` y
   `python -m pytest -q tests` deben pasar.

## Controles de calidad del texto (obligatorios)

Lección de la revisión del 2026-10-08 (`docs/revision_calidad_20261008.md`): la versión 1 pasaba la validación
en verde y tenía artículos intercalados entre columnas, encabezados de página dentro de las oraciones y una ley
completa tomada de un OCR con montos en colones ilegibles. **Que la validación pase no prueba que el texto esté
bien.** Antes de entregar una norma nueva o un cambio de extracción:

1. **Orden de los artículos.** Lista los encabezados «Artículo N» del texto generado y confirma que salen en
   orden. Si un número aparece antes que uno menor (26 → 34 → 27), hay columnas intercaladas: corrige la
   extracción, no el catálogo. Los artículos de otra ley que una reforma transcribe aparecen repetidos más
   adelante; eso es legítimo.
2. **Sin encabezados de página.** El texto no debe contener «La Gaceta Nº … Pág N», «Alcance Nº … a La
   Gaceta Nº …» ni los encabezados del documento legislativo reproducido («LEY N.º 9635» + número de página).
   `construir.py` los descarta; si aparece uno con otra forma, amplía el filtro y documenta la medición.
3. **¿Es un escaneo?** Revisa si las páginas de la norma son imágenes (`page.get_images()`) y busca marcas de
   OCR: letras y cifras mezcladas dentro de una palabra («serv1c1os»), el signo de colones mal leído
   («(<C238»), números romanos leídos como cifras («CAPÍTULO 11» por II), «1 O» por «10». Si el texto viene
   de OCR con errores, la norma va sin texto (regla 7). Si solo algunas páginas son escaneo (por ejemplo las
   firmas), exclúyelas con `excluir` y explica el motivo.
4. **Citas de documentos escaneados.** Una cita tomada de la capa OCR puede diferir del original («ARTICULO»
   por «ARTÍCULO»). Compárala con la imagen de la página renderizada y usa un tramo que el OCR reproduzca
   fielmente.
5. **Prueba de equivalencia al cambiar la extracción.** Si modificas `construir.py`, compara palabra por
   palabra los textos de antes y de después: solo debe desaparecer lo que querías quitar, y las normas que no
   tenían el problema deben quedar idénticas. Si se va algo más (un número de portada, una palabra), el
   filtro es demasiado amplio.
6. **No dejes parches viejos.** Una exclusión (`excluir`) que se agregó para tapar un error de extracción
   debe revisarse cuando se corrige la causa: en la v1, los «acuerdos intercalados» del Decreto 32333 eran el
   mismo error de columnas.
7. **Ningún `.txt` huérfano.** Si una norma pasa a `texto_incluido: false`, borra su `.txt`.
8. **Número de Gaceta de un alcance, comprobado en La Gaceta.** Muchas portadas de alcance solo dicen
   «Alcance Nº 38». No tomes el número de Gaceta de un dictamen, un sitio web o tu memoria: si la portada del
   alcance no lo trae, pon en `confirmacion_gaceta` la URL de la edición ordinaria del mismo día
   (`COMP_DD_MM_AAAA.pdf`), cuya portada muestra fecha y número. `construir.py` lo exige.
9. **Lo que el registro dice de sí mismo debe ser cierto.** No escribas «verificado en el PDF» en
   `localizacion` para un dato que no comprobaste ahí; di de dónde salió cada dato.

`src/construir.py` aplica el control 8. `src/validar.py` aplica automáticamente los controles 1, 2, 3 (marcas de OCR) y 7, y se prueba a sí mismo con
un ejemplo de cada error real antes de revisar el dataset. Los controles 3 (imágenes), 4, 5 y 6 requieren tu
revisión.

## Cómo agregar una norma (pasos)

Sigue `CONTRIBUTING.md`, sección «Agregar una norma». En resumen:

1. Ubica la publicación (Gaceta, alcance y fecha) y la URL del PDF en la Imprenta Nacional.
2. Descarga y verifica que la norma esté en ese PDF; anota la página inicial y final.
3. Agrega la entrada en `catalogo.json` (marcadores de inicio y fin, título, relaciones con cita).
4. Corre `python src/construir.py`. Si aborta, corrige el catálogo; no fuerces el código.
5. Revisa a mano el texto generado (bordes y tramos ajenos) y aplica los «Controles de calidad del texto».
6. Corre `python src/validar.py` y `python -m pytest -q tests`.
7. Abre un *pull request* con la plantilla completa.

## Lo que no debes hacer

- Modificar `construir.py` o `validar.py` para que una verificación «pase». Si falla, el dato está mal.
- Agregar textos consolidados o resúmenes propios dentro de los textos oficiales.
- Subir los PDF al repositorio (se enlazan, no se redistribuyen).
- Presentar el proyecto como fuente oficial.
