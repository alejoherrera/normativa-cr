# Revisión de calidad de la versión 1 (2026-10-08)

La validación (`src/validar.py`) pasaba en verde, pero revisa la forma de los registros (esquema,
procedencia, huellas), no la calidad del texto extraído. Una revisión del contenido encontró estos errores.

## Hallazgos

| # | Norma | Error | Causa |
|---|---|---|---|
| 1 | Decreto 32333-MP-J | Artículos fuera de orden: 26 → 34–38 → 27–33, y 46 → 49–53 → 47–48 | En las páginas 4 y 5 cada columna es un único bloque largo de texto; la detección de dos columnas exigía más de 3 bloques por columna, la página se trató como de una columna y se ordenó por altura, intercalando columnas |
| 2 | Ley 8422, Decreto 32333, Ley 10224 | Encabezado de página de La Gaceta («La Gaceta Nº 212 — Viernes 29 de octubre del 2004 Pág 3») dentro del texto, a veces en medio de una oración | La extracción no descartaba el encabezado corrido de cada página |
| 3 | Ley 9986 | Texto con errores de reconocimiento óptico: montos en colones como «(<C238 223 960)», capítulos «11» y «111» por II y III, «ARTÍCULO 1 O», «serv1c1os», «princ1p1os» | Las 97 páginas del PDF oficial son imágenes escaneadas; el texto es la capa OCR del PDF. Igual que la Ley 10159, debió publicarse sin texto (Constitución §5) |
| 4 | Ley 9635 | 94 encabezados del documento legislativo («LEY N.º 9635» + número de página) dentro del texto; páginas finales de firmas escaneadas con OCR ilegible («n Acl'.lña Cabrera», «MARÍA D L ROCÍO G LAR MONTOYA») | Encabezados de la reproducción del decreto legislativo; las dos últimas páginas son imagen |
| 5 | Ley 10159 (relación → 2166) | La cita decía «ARTICULO 49-» sin tilde; el original escaneado dice «ARTÍCULO 49-» | La cita se tomó de la capa OCR |
| 6 | Decreto 41564 y Ley 9635 | El número de Gaceta (34 y 225) no figura en el PDF del alcance; venía de dictámenes de la PGR, y el registro decía «verificado en el PDF». Los números eran correctos | `construir.py` solo verificaba el número de alcance y el año, no el número de Gaceta ni el día y mes |

Revisado y correcto: la secuencia de artículos de la Ley 8422 (el «22–25» tras el 65 es el texto de los
artículos que reforma de la Ley 7494); el artículo 312 del Decreto 43808-H (encabezado sin guion); la
relación «adiciona» de la 9635 a la 2166 (artículo 3 del título III: «Se adicionan los siguientes
capítulos…»).

## Correcciones

1. Detección de columnas por geometría (bloques contenidos en cada mitad de la página), no por cantidad.
2. Se descartan los encabezados corridos de La Gaceta en el margen superior y los encabezados del documento
   legislativo («LEY N.º NNNN» + número de página, y «-NN-»).
3. Ley 9986: `texto_incluido = false`, con motivo.
4. Ley 9635: se excluye el tramo final de firmas escaneadas, con motivo.
5. Cita de la 10159 acotada a un tramo que la capa OCR reproduce fielmente, comprobado contra la imagen.
6. Número de Gaceta de los alcances: se exige en la portada del alcance o, si no está, en la portada de la
   edición ordinaria del mismo día (`confirmacion_gaceta` en el catálogo), que se descarga de la Imprenta
   Nacional. La fecha se comprueba completa (día, mes y año). Control negativo: Gaceta 35 en vez de 34, sin
   edición del día, y fecha 28 en vez de 29 detienen la construcción; los datos reales pasan.
7. El validador agrega controles de contenido para que estos errores no vuelvan a pasar en verde: orden de
   artículos, encabezados de página y marcas típicas de OCR.
