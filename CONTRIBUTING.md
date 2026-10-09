# Cómo contribuir

¡Gracias por ayudar! Antes de empezar, lee `CONSTITUTION.md`. Si usas un modelo de IA, dale también
`AGENTS.md`.

## Preparar el entorno

```bash
git clone https://github.com/alejoherrera/normativa-cr.git
cd normativa-cr
pip install pymupdf jsonschema pytest
python src/construir.py      # descarga los PDF de La Gaceta a .cache/ (no se publica) y verifica
python src/validar.py        # debe terminar en [OK]
```

## Agregar una norma

### 1. Ubicar la publicación

Necesitas el número de Gaceta, el número de alcance (si salió en un alcance) y la fecha. La Gaceta no tiene
índice por número de norma, así que puedes usar referencias públicas: el considerando de otra norma, un
dictamen, una noticia o la ficha pública del SCIJ/SINALEVI **solo como índice**. Anota cómo lo ubicaste.

Para ver qué publicó La Gaceta un día dado, abre
`https://www.imprentanacional.go.cr/gaceta/?date=DD/MM/AAAA`. Las URL de los PDF siguen el patrón:

- edición del día: `https://www.imprentanacional.go.cr/pub/AAAA/MM/DD/COMP_DD_MM_AAAA.pdf`
- alcance: `https://www.imprentanacional.go.cr/pub/AAAA/MM/DD/ALCA{n}_DD_MM_AAAA.pdf`

### 2. Verificar en el PDF

Descarga el PDF y confirma que la norma está ahí. Anota la página donde empieza y donde termina. El final suele
ser el código de publicación, por ejemplo `( L9986 - IN2021554294 )` o `( D45782 - IN202601068928 )`.

### 3. Agregar la entrada en `catalogo.json`

```json
{
  "id": "cr/ley/2022/10224",
  "tipo": "ley",
  "numero": "10224",
  "titulo": "Título exacto como aparece en La Gaceta",
  "titulo_tipo": "oficial",
  "emisor": "Asamblea Legislativa",
  "publicacion": {"gaceta": 100, "alcance": null, "fecha": "2022-05-31",
                  "url_pdf": "https://www.imprentanacional.go.cr/pub/2022/05/31/COMP_31_05_2022.pdf"},
  "paginas": [9, 10],
  "marcador_inicio": "texto literal con que empieza la norma",
  "marcador_fin": "( L10224 - IN2022648666 )",
  "texto_incluido": true,
  "localizacion": "Cómo ubicaste la publicación; verificado en el PDF.",
  "relaciones": [
    {"tipo": "modifica", "objetivo": "cr/ley/2004/8422",
     "cita": "Frase literal del texto oficial que establece la relación"}
  ]
}
```

- `id`: `cr/{ley|decreto}/{año de publicación}/{número}`.
- `titulo_tipo`: `oficial` si el título aparece literalmente en La Gaceta; `descriptivo` si la norma no tiene
  título formal y lo redactas tú.
- `relaciones.tipo`: `modifica`, `adiciona`, `deroga` o `reglamenta`. La `cita` debe aparecer **literalmente**
  en las páginas de la norma.
- Si la maquetación intercala otra publicación dentro de la norma, agrega
  `"excluir": [{"desde": "...", "hasta_antes_de": "...", "motivo": "..."}]`.
- Si el PDF es un escaneo con OCR defectuoso: `"texto_incluido": false` y `"motivo_sin_texto": "..."`.

### 4. Construir, revisar y validar

```bash
python src/construir.py
python src/validar.py
python -m pytest -q tests
```

`construir.py` se detiene si la portada, el número, el título o alguna cita no coinciden con el PDF. No
modifiques el código para que pase: corrige el dato.

Después de construir, **abre el `.txt` generado** y revisa el inicio, el final y que no se haya colado otra
norma. Aplica además los «Controles de calidad del texto» de `AGENTS.md`: artículos en orden, sin
encabezados de página, y si las páginas son imágenes escaneadas, sin texto de OCR defectuoso. Que la
validación pase no basta: la versión 1 pasaba en verde con esos tres errores.

### 5. Abrir un *pull request*

Completa la plantilla. GitHub corre la validación automáticamente; un *pull request* en rojo no se acepta.

## Cambiar el esquema

`schema/norma.v1.json` no se edita. Si hace falta un campo nuevo, propón un `norma.v2.json` en un *issue*
primero.

## Reportar un error

Abre un *issue* indicando el registro, el dato que crees incorrecto y la página del PDF oficial que lo
demuestra.
