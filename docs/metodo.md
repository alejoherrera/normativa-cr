# Método y control de calidad

## 1. Selección

Versión 1: diez normas de contratación pública y empleo público, elegidas para que haya relaciones entre
ellas (leyes y sus reglamentos, y reformas).

## 2. Localización de cada publicación

La Gaceta no tiene un índice público por número de norma. La edición en que salió cada una se identificó
con referencias públicas: el considerando de otra norma publicada en La Gaceta, dictámenes publicados por la
Procuraduría, prensa, la edición del día en el sitio de la Imprenta Nacional y, en dos casos (Ley 10224 y
Decreto 43952-PLAN), la ficha pública del SCIJ/SINALEVI consultada **solo como índice**. Ninguno de esos datos
se usó sin confirmarlo en el PDF de La Gaceta. Cada registro lo dice en `procedencia.localizacion`.

## 3. Descarga

PDF desde `https://www.imprentanacional.go.cr/pub/AAAA/MM/DD/…`, una petición por documento y con pausa.
Se guarda una copia local (no publicada) y se registra su SHA-256, tamaño y fecha de descarga.

## 4. Extracción del texto

- Se extraen solo las páginas de la norma y se recorta entre un marcador de inicio y su código de
  publicación (por ejemplo `( L9986 - IN2021554294 )`).
- **Dos columnas:** La Gaceta ordinaria se compone a dos columnas. Una extracción ingenua mezcla las columnas;
  en la primera prueba intercaló otras leyes dentro de la Ley 10224. El texto se extrae por bloques ordenados
  por columna y de arriba hacia abajo.
- **Tramos ajenos:** cuando la maquetación intercala otra publicación dentro de las páginas de una norma, el
  tramo se quita y el registro lo documenta en `texto.exclusiones` (caso del Decreto 32333-MP-J).
- **Escaneos:** si la norma se publicó como imagen y el OCR es defectuoso (Ley 10159), no se publica el texto;
  se publican los metadatos y el enlace, con el motivo.
- El texto es el **original publicado**. No se consolidan reformas.

## 5. Verificaciones al construir (bloqueantes)

`src/construir.py` aborta y no escribe nada si falla cualquiera de estas comprobaciones, hechas contra el
texto del PDF oficial:

1. La portada muestra el número de alcance (o de Gaceta) y el año indicados.
2. El número de la norma aparece en sus páginas.
3. El título oficial aparece literalmente. En escaneos, se acepta una coincidencia aproximada de al menos
   0,85 en la primera página, y se informa.
4. Cada relación tiene una cita que aparece **literalmente** en el texto oficial.

## 6. Validación independiente

`src/validar.py` revisa los registros generados:

- esquema `schema/norma.v1.json`, identificadores únicos;
- procedencia completa y declaración expresa de que el contenido se descargó de La Gaceta;
- URL del PDF dentro del sitio de la Imprenta Nacional;
- coherencia de `objetivo_en_dataset` en las relaciones;
- huella SHA-256 de cada texto;
- **barrido de contenido del SCIJ/SINALEVI**: ningún texto contiene sus marcas editoriales («Nota de
  Sinalevi», «Así reformado…», «Ficha artículo», etc.);
- **control negativo**: antes de revisar el dataset, el validador se prueba con registros dañados a propósito
  (sin procedencia, URL ajena, relación incoherente, huella alterada) y falla si no los detecta.

## 7. Comprobaciones adicionales hechas para la versión 1

- **Bordes de cada texto:** se revisó a mano el inicio y el final de los diez textos y se buscaron
  encabezados de otras normas dentro de cada uno.
- **Equivalencia:** el texto del artículo 14 de la Ley 8422 extraído de la Ley 10224 (La Gaceta 100 de 2022)
  coincide al 100 % con el que muestra el SCIJ/SINALEVI como vigente (comprobación hecha a mano, sin copiar).

## 8. Limitaciones

- En páginas a dos columnas con maquetación irregular, el orden de lectura extraído puede diferir del visual
  en detalles. El PDF oficial prevalece.
- Las firmas al final de algunas leyes son imágenes y su OCR es ilegible.
- La versión 1 no consolida textos ni incluye concordancias.
