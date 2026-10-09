# Constitución — normativa-cr

Reglas no negociables del proyecto. Toda especificación, cambio o contribución las respeta.

## 1. Propósito

Publicar un conjunto de datos **abierto, estructurado y verificable** de normativa costarricense, construido
**exclusivamente desde la edición oficial: el Diario Oficial La Gaceta (Imprenta Nacional)**.

No es fuente oficial, no sustituye a La Gaceta ni al SCIJ/SINALEVI y no emite certificaciones.

## 2. Fuentes

- **Contenido** (texto, páginas, relaciones, fechas): solo de los PDF oficiales de La Gaceta y sus alcances,
  descargados del sitio de la Imprenta Nacional.
- **Localización** (en qué Gaceta salió una norma): puede consultarse cualquier índice público, incluido el
  SCIJ/SINALEVI, **solo para ubicar la publicación**, a ritmo humano y en pocas consultas. El dato siempre se
  confirma en el PDF de La Gaceta, y el registro declara cómo se localizó.
- **Prohibido** copiar del SCIJ/SINALEVI sus textos consolidados, notas, concordancias, descriptores,
  observaciones o identificadores internos: la Procuraduría ha manifestado que reclama derechos sobre ese
  contenido editorial.

## 3. Procedencia obligatoria

Cada registro dice que su contenido **se descargó de La Gaceta**, con: número de Gaceta y de alcance, fecha,
URL del PDF en la Imprenta Nacional, fecha de descarga, SHA-256 del archivo y páginas. Un registro sin
procedencia completa no pasa la validación. Los PDF **no se redistribuyen**: se enlazan.

## 4. Verificabilidad

- Toda relación entre normas (reforma, adición, reglamentación) se respalda con la **cita literal** del texto
  oficial que la establece, comprobada mecánicamente contra el PDF.
- Todo título, número y fecha se comprueba contra el PDF.
- Las anotaciones propias (títulos descriptivos, calidad del texto) se marcan como tales.

## 5. Calidad del texto

Si el PDF es un escaneo con OCR defectuoso, el registro **no publica el texto extraído**: publica los
metadatos y el enlace, y lo declara (`texto.incluido = false` con su motivo).

## 6. Formatos y versiones

- Un JSON por norma, validado contra `schema/norma.v1.json`. Un esquema publicado **no se edita**: los
  cambios van en `norma.v2.json`.
- Identificadores propios persistentes: `cr/{tipo}/{año de publicación}/{número}`.

## 7. Licencias

- Textos normativos: libre reproducción conforme a la edición oficial (art. 75, Ley 6683).
- Datos y anotaciones del proyecto: CC BY 4.0. Código: MIT.

## 8. Operación

- Descarga respetuosa: una petición por documento, con pausa. Si un sitio presenta un control de acceso, se
  detiene la automatización.
- Ningún cambio se publica con la validación (`python src/validar.py`) en rojo.

## 9. Enmiendas

Las enmiendas a esta Constitución se hacen por commit explícito que la modifique y explique el motivo.
