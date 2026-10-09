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


def test_detecta_errores_reales_de_la_v1():
    """Cada control de texto detecta el error que lo motivó y acepta un texto sano (control positivo y negativo)."""
    sano = "Artículo 1.—Uno.\nArtículo 2.—Dos.\nArtículo 3.—Tres.\n"
    assert validar.errores_texto(sano, "cr/prueba") == []
    assert validar.errores_texto("Artículo 1.\nArtículo 3.\nArtículo 2.\n", "cr/prueba")
    assert validar.errores_texto(sano + "La Gaceta Nº 212 — Viernes 29 de octubre del 2004 Pág 3\n", "cr/prueba")
    assert validar.errores_texto(sano + "LEY N.º 9635 \n 80 \n", "cr/prueba")
    assert validar.errores_texto(sano + "serv1c1os por (<C238 223 960)\n", "cr/prueba")


def test_reforma_que_transcribe_articulos_no_es_desorden():
    """Una reforma que transcribe artículos de otra ley (8422, art. 65) no se confunde con columnas intercaladas."""
    texto = "Artículo 1.—A.\nArtículo 2.—B.\nArtículo 1.—Texto reformado.\nArtículo 3.—C.\n"
    assert not any("orden" in e for e in validar.errores_texto(texto, "cr/prueba"))
