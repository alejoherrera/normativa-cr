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
        errs += [f"texto: contiene la marca de SINALEVI {m!r}" for m in MARCAS_SINALEVI if m in contenido]
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
    print(f"[OK] autocomprobación: {len(danos)} daños detectados")


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
    for a, r in zip(archivos, registros):
        for e in errores_registro(r, set(ids)):
            print(f"[ERROR] {a.name}: {e}")
            fallas += 1
    print(f"[{'OK' if not fallas else 'ERROR'}] {len(registros)} registros, {fallas} problemas")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
