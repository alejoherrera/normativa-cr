# normativa-cr

**Datos abiertos de normativa costarricense, descargados del Diario Oficial La Gaceta.**

Todo el contenido de este conjunto de datos —textos, páginas, fechas y relaciones entre normas— **se
descargó de La Gaceta**, la edición oficial publicada por la Imprenta Nacional de Costa Rica. Cada registro
enlaza el PDF oficial del que proviene, con su huella SHA-256, la fecha de descarga y las páginas exactas.
Los PDF no se redistribuyen: se enlazan.

> **Aviso.** Este proyecto no es fuente oficial, no sustituye a La Gaceta ni al SCIJ/SINALEVI y no emite
> certificaciones. Los textos son los **originales publicados**, no textos consolidados con sus reformas.
> Ante cualquier diferencia, prevalece el PDF oficial de La Gaceta.

## Contenido (versión 1: 10 normas)

| Norma | Publicación en La Gaceta | Texto |
|---|---|---|
| Ley 9986, Ley General de Contratación Pública | Alcance 109 a La Gaceta 103, 31-05-2021 | Sí |
| Decreto 43808-H, Reglamento a la Ley General de Contratación Pública | Alcance 258 a La Gaceta 229, 30-11-2022 | Sí |
| Decreto 45782-H-MIDEPLAN-MICITT, reforma al Reglamento 43808-H | Alcance 62 a La Gaceta 95, 26-05-2026 | Sí |
| Ley 9635, Fortalecimiento de las Finanzas Públicas | Alcance 202 a La Gaceta 225, 04-12-2018 | Sí |
| Decreto 41564-MIDEPLAN-H, Reglamento del Título III de la Ley 9635 | Alcance 38 a La Gaceta 34, 18-02-2019 | Sí |
| Ley 8422, contra la Corrupción y el Enriquecimiento Ilícito en la Función Pública | La Gaceta 212, 29-10-2004 | Sí |
| Decreto 32333-MP-J, Reglamento a la Ley 8422 | Alcance 11 a La Gaceta 82, 29-04-2005 | Sí |
| Ley 10159, Ley Marco de Empleo Público | Alcance 50 a La Gaceta 46, 09-03-2022 | No (escaneo con OCR defectuoso) |
| Decreto 43952-PLAN, Reglamento a la Ley Marco de Empleo Público | Alcance 39 a La Gaceta 45, 10-03-2023 | Sí |
| Ley 10224, reforma del artículo 14 de la Ley 8422 | La Gaceta 100, 31-05-2022 | Sí |

Relaciones registradas: reglamentaciones (43808-H → 9986, 41564 → 9635, 32333 → 8422, 43952 → 10159) y
reformas o adiciones (45782 → 43808-H, 9635 → 8422 y 2166, 10159 → 2166, 10224 → 8422). Cada una con la
cita literal del texto oficial que la establece.

## Estructura

```
normas/<id>.json   registro de cada norma (esquema schema/norma.v1.json)
normas/<id>.txt    texto original extraído del PDF oficial (si se incluye)
catalogo.json      qué normas se construyen, en qué PDF y páginas
schema/            JSON Schema versionado
src/construir.py   descarga de La Gaceta, extracción y verificación
src/validar.py     control de calidad (debe pasar antes de publicar)
docs/metodo.md     método, criterios y control de calidad
```

Identificadores propios y persistentes: `cr/{tipo}/{año de publicación}/{número}`, por ejemplo
`cr/ley/2021/9986`.

## Reproducir

```bash
pip install pymupdf jsonschema
python src/construir.py   # descarga los PDF de La Gaceta (con pausa entre descargas) y verifica
python src/validar.py     # QA: debe terminar en [OK]
```

## Cómo se localizó cada publicación

La Gaceta no ofrece un índice por número de norma. Para saber en qué edición salió cada una se usaron
referencias públicas —en dos casos, la ficha pública del SCIJ/SINALEVI, **solo como índice**— y luego **se
verificó en el PDF de La Gaceta**. Cada registro lo declara en `procedencia.localizacion`. No se copió del
SCIJ/SINALEVI ningún texto consolidado, nota, concordancia, descriptor ni identificador interno.

## Control de calidad

Ver [docs/metodo.md](docs/metodo.md). En resumen: cada PDF se descarga de la Imprenta Nacional y se registra
su huella; se verifica en el PDF la portada (alcance o Gaceta y año), el número y el título de cada norma; cada
relación se respalda con una cita literal comprobada mecánicamente; los textos se extraen respetando las dos
columnas de La Gaceta; se excluyen y documentan los tramos de otras publicaciones intercalados por la
maquetación; y un validador independiente —que se prueba a sí mismo con registros dañados— revisa esquema,
procedencia, huellas y la ausencia de contenido editorial del SCIJ/SINALEVI.

## Licencias

- Textos normativos: libre reproducción conforme a la edición oficial (art. 75, Ley 6683 de Derechos de Autor).
- Datos y anotaciones del proyecto: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es).
- Código: MIT (ver `LICENSE`).

Fuente del texto: Imprenta Nacional de Costa Rica, Diario Oficial La Gaceta.
