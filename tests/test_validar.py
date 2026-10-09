"""Pruebas del validador: el dataset publicado pasa y los daños se detectan."""
import copy
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
import validar  # noqa: E402


def _registros():
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((RAIZ / "normas").glob("*.json"))]


def test_dataset_sin_errores():
    regs = _registros()
    ids = {r["id"] for r in regs}
    assert all(not validar.errores_registro(r, ids) for r in regs)


def test_detecta_marca_de_sinalevi(tmp_path):
    reg = copy.deepcopy(next(r for r in _registros() if r["texto"]["incluido"]))
    falso = tmp_path / "normas"
    falso.mkdir()
    contenido = "texto\n(Así reformado por la ley X)\n"
    (falso / "x.txt").write_text(contenido, encoding="utf-8")
    import hashlib
    reg["texto"].update(archivo="normas/x.txt", sha256=hashlib.sha256(contenido.encode()).hexdigest())
    errs = validar.errores_registro(reg, {reg["id"]}, raiz=tmp_path)
    assert any("SINALEVI" in e for e in errs)


def test_toda_procedencia_declara_la_gaceta():
    assert all("La Gaceta" in r["procedencia"]["declaracion"] for r in _registros())
