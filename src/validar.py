"""Validación (QA) del dataset normativa-cr. Código de salida distinto de 0 si algo falla.

Por qué existe: la Constitución exige que nada se publique sin verificar. Este programa revisa los registros
ya generados, sin descargar nada: esquema, identificadores, procedencia completa, coherencia de relaciones,
huellas de los textos, y un barrido que confirma que no se copió contenido editorial del SCIJ/SINALEVI.
Antes de revisar el dataset, se prueba a sí mismo con registros dañados a propósito (control negativo).

Uso:
    python src/validar.py
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RAIZ = Path(__file__).resolve().parent.parent
ESQUEMA = json.loads((RAIZ / "schema" / "norma.v1.json").read_text(encoding="utf-8"))
VALIDADOR = Draft202012Validator(ESQUEMA, format_checker=FormatChecker())
# Marcas propias de la edición de SINALEVI que no deben aparecer en los textos (QA-6).
MARCAS_SINALEVI = ("Nota de Sinalevi", "Ficha articulo", "Ficha Artículo", "(Así reformado", "(Así adicionado",
                   "Versión de la Norma", "pgrweb.go.cr", "sinalevi.go.cr")

# Controles de contenido (revisión del 2026-10-08, docs/revision_calidad_20261008.md): la v1 pasaba esta
# validación con artículos intercalados entre columnas, encabezados de página dentro del texto y una ley
# entera tomada de un OCR defectuoso. Cada patrón corresponde a un error que efectivamente se publicó.
DEFECTOS_DE_TEXTO = {
    "encabezado de página de La Gaceta": re.compile(
        r"(?m)La Gaceta N[º°]\s*\d+\s*—.*Pág\s*\d+|^\s*Pág\s*\d+\s*$|^\s*Alcance N[º°]\s*\d+ a La Gaceta N[º°]\s*\d+\s*$"),
    "encabezado del documento legislativo": re.compile(r"(?m)^\s*LEY N\.?\s*[º°0]\s*\d{3,5}\s*$"),
    "marca de OCR defectuoso": re.compile(r"\(<C\d|[a-záéíóúñ]1[a-záéíóúñ]+1|\bART[ÍI]CULO\s+\d+\s+O-"),
}
ENCABEZADO_ARTICULO = re.compile(r"(?m)^\s*(?:ART[ÍI]CULO|Art[íi]culo)\s+(\d+)")
# Normas cuya numeración de artículos reinicia legítimamente (el control de orden no aplica).
NUMERACION_REINICIADA = {"cr/ley/2018/9635": "cada título de la ley reinicia la numeración de sus artículos"}


def errores_texto(contenido: str, id_norma: str) -> list[str]:
    """Defectos de extracción en el texto de una norma (lista vacía = sin defectos detectados)."""
    errs = [f"texto: contiene la marca de SINALEVI {m!r}" for m in MARCAS_SINALEVI if m in contenido]
    for nombre, patron in DEFECTOS_DE_TEXTO.items():
        m = patron.search(contenido)
        if m:
            errs.append(f"texto: {nombre}: {m.group(0).strip()[:60]!r}")
    if id_norma not in NUMERACION_REINICIADA:
        # Orden de primera aparición: los artículos de otra ley que una reforma transcribe aparecen después
        # de su primera aparición propia y no cuentan; un intercalado de columnas sí rompe este orden.
        primeras = list(dict.fromkeys(int(n) for n in ENCABEZADO_ARTICULO.findall(contenido)))
        fuera = [(a, b) for a, b in zip(primeras, primeras[1:]) if b < a]
        if fuera:
            errs.append(f"texto: artículos fuera de orden (p. ej. {fuera[0][0]} antes de {fuera[0][1]})")
    return errs


def errores_registro(reg: dict, ids: set[str], raiz: Path = RAIZ) -> list[str]:
    """Todos los problemas de un registro (lista vacía = válido)."""
    errs = [f"esquema: {e.message}" for e in VALIDADOR.iter_errors(reg)]
    if errs:
        return errs
    if "La Gaceta" not in reg["procedencia"]["declaracion"]:
        errs.append("procedencia: la declaración no dice que el contenido se descargó de La Gaceta")
    for rel in reg["relaciones"]:
        if rel["objetivo_en_dataset"] != (rel["objetivo"] in ids):
            errs.append(f"relación: objetivo_en_dataset incoherente para {rel['objetivo']}")
    t = reg["texto"]
    if t["incluido"]:
        ruta = raiz / t["archivo"]
        if not ruta.exists():
            return errs + [f"texto: falta {t['archivo']}"]
        contenido = ruta.read_text(encoding="utf-8")
        if hashlib.sha256(contenido.encode("utf-8")).hexdigest() != t["sha256"]:
            errs.append("texto: la huella SHA-256 no coincide con el archivo")
        errs += errores_texto(contenido, reg["id"])
    elif not t.get("motivo_no_incluido"):
        errs.append("texto: no incluido y sin motivo")
    return errs


def autocomprobacion(muestra: dict, ids: set[str]) -> None:
    """Control negativo: el validador debe detectar daños introducidos a propósito."""
    danos = {
        "sin procedencia": lambda r: r.pop("procedencia"),
        "url ajena a la Imprenta": lambda r: r["procedencia"].update(url_pdf="https://ejemplo.com/x.pdf"),
        "relación incoherente": lambda r: r["relaciones"].append(
            {"tipo": "modifica", "objetivo": "cr/ley/1900/1", "objetivo_en_dataset": True, "cita": "x" * 25}),
        "huella alterada": lambda r: r["texto"].update(sha256="0" * 64),
    }
    for nombre, danar in danos.items():
        r = copy.deepcopy(muestra)
        danar(r)
        if not errores_registro(r, ids):
            raise SystemExit(f"[ERROR] autocomprobación: el validador no detectó «{nombre}»")
    # Daños de texto: cada uno reproduce un error real de la v1.
    base = "Artículo 1.—Uno.\nArtículo 2.—Dos.\nArtículo 3.—Tres.\n"
    danos_texto = {
        "artículos intercalados": "Artículo 1.—Uno.\nArtículo 3.—Tres.\nArtículo 2.—Dos.\n",
        "encabezado de La Gaceta": base + "La Gaceta Nº 212 — Viernes 29 de octubre del 2004 Pág 3\n",
        "encabezado legislativo": base + "LEY N.º 9635 \n 80 \n",
        "OCR defectuoso": base + "contrataciones de serv1c1os por (<C238 223 960)\n",
    }
    if errores_texto(base, "cr/prueba"):
        raise SystemExit("[ERROR] autocomprobación: el control de texto rechaza un texto sano")
    for nombre, texto in danos_texto.items():
        if not errores_texto(texto, "cr/prueba"):
            raise SystemExit(f"[ERROR] autocomprobación: el validador no detectó «{nombre}»")
    print(f"[OK] autocomprobación: {len(danos) + len(danos_texto)} daños detectados y un texto sano aceptado")


def main() -> int:
    archivos = sorted((RAIZ / "normas").glob("*.json"))
    registros = [json.loads(a.read_text(encoding="utf-8")) for a in archivos]
    ids = [r.get("id") for r in registros]
    if not registros:
        print("[ERROR] no hay registros")
        return 1
    if len(ids) != len(set(ids)):
        print("[ERROR] identificadores duplicados")
        return 1
    # Todo registro publicado debe salir del catálogo (y viceversa): impide subir registros hechos a mano.
    catalogo = {e["id"] for e in json.loads((RAIZ / "catalogo.json").read_text(encoding="utf-8"))}
    if catalogo != set(ids):
        print(f"[ERROR] catálogo y registros no coinciden: solo en catálogo {sorted(catalogo - set(ids))}, "
              f"solo en registros {sorted(set(ids) - catalogo)}")
        return 1
    autocomprobacion(next(r for r in registros if r["texto"]["incluido"] and r["relaciones"]), set(ids))
    fallas = 0
    # Un .txt sin registro que lo declare es texto publicado sin control (pasó con la 9986 al excluir su texto).
    declarados = {r["texto"]["archivo"] for r in registros if r["texto"]["incluido"]}
    for t in sorted((RAIZ / "normas").glob("*.txt")):
        if f"normas/{t.name}" not in declarados:
            print(f"[ERROR] {t.name}: texto sin registro que lo declare")
            fallas += 1
    for a, r in zip(archivos, registros):
        for e in errores_registro(r, set(ids)):
            print(f"[ERROR] {a.name}: {e}")
            fallas += 1
    print(f"[{'OK' if not fallas else 'ERROR'}] {len(registros)} registros, {fallas} problemas")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
