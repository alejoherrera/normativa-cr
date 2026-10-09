"""Construye los registros de normativa-cr desde los PDF oficiales de La Gaceta.

Por qué existe: el dataset solo puede contener lo que dice la edición oficial. Este programa descarga cada
PDF de la Imprenta Nacional (o lo toma de la caché local), calcula su huella SHA-256, extrae el texto de las
páginas de la norma, y antes de escribir nada verifica contra ese texto: el título oficial, el número de
Gaceta y cada cita literal que respalda una relación. Si una verificación falla, aborta sin escribir.

Uso:
    python src/construir.py            # usa la caché .cache/gaceta y descarga lo que falte
"""

from __future__ import annotations

import datetime
import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

import fitz  # PyMuPDF

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / ".cache" / "gaceta"
SALIDA = RAIZ / "normas"
PAUSA_S = 4  # descarga respetuosa: una petición por documento, con pausa
DECLARACION = ("El contenido de este registro se descargó del Diario Oficial La Gaceta, edición oficial "
               "publicada por la Imprenta Nacional de Costa Rica, en el PDF indicado en url_pdf.")


def plano(texto: str) -> str:
    """Normaliza para comparar: sin espacios, sin marcas de OCR de guion, en minúsculas."""
    texto = unicodedata.normalize("NFKC", texto).replace("­", "")
    return re.sub(r"\s+", "", texto).lower()


UMBRAL_TITULO_OCR = 0.85


def _mejor_similitud(aguja: str, pajar: str) -> float:
    """Mayor parecido entre la aguja y cualquier ventana del mismo largo del pajar (0 a 1)."""
    from difflib import SequenceMatcher
    n = len(aguja)
    return max((SequenceMatcher(None, aguja, pajar[i:i + n]).ratio()
                for i in range(0, max(1, len(pajar) - n + 1))), default=0.0)


def pdf_local(url: str) -> Path:
    """Devuelve el PDF desde la caché; si falta, lo descarga una sola vez."""
    CACHE.mkdir(parents=True, exist_ok=True)
    destino = CACHE / url.rsplit("/", 1)[1]
    if not destino.exists() or destino.stat().st_size == 0:
        print(f"[..] descargando {url}")
        with urllib.request.urlopen(url, timeout=120) as r:
            destino.write_bytes(r.read())
        time.sleep(PAUSA_S)
    return destino


# Encabezado de la reproducción de un decreto legislativo dentro del alcance: «LEY N.º 9635» y el número
# de página del documento («94», «-96-»), en un bloque propio cerca del borde superior.
ENCABEZADO_LEGISLATIVO = re.compile(r"^\s*(-\s*\d+\s*-\s*)?(LEY N\.?\s*[º°0]\s*\d{3,5}\s*)?(-?\s*\d{1,3}\s*-?)?\s*$")


def es_encabezado(bloque, alto: float) -> bool:
    """Encabezados de página: no son texto de la norma.

    - Encabezado corrido de La Gaceta («La Gaceta Nº 212 — Viernes… Pág 3»): ocupa la franja superior,
      que termina antes del 4,5 % de la altura (medido en las ediciones de 2004, 2005 y 2022).
    - Encabezado del documento legislativo reproducido: bloque que solo dice «LEY N.º NNNN» y/o un número.
    """
    if bloque[3] < alto * 0.045:
        return True
    return bloque[1] < alto * 0.12 and bool(ENCABEZADO_LEGISLATIVO.match(bloque[4])) and bloque[4].strip() != ""


def leer_pagina(pagina) -> str:
    """Texto de una página en orden de lectura, sin encabezados de página.

    La Gaceta ordinaria se compone a dos columnas; la extracción simple de PyMuPDF mezcla columnas y llegó
    a intercalar otras leyes dentro de una norma (Ley 10224 con 10217 y 10223). Aquí se ordenan los bloques
    por columna y luego de arriba hacia abajo.

    La página es de dos columnas si hay texto contenido en cada mitad que ocupe una altura apreciable. No se
    cuentan bloques: en el Alcance 11 de 2005 una columna entera es un solo bloque, y la regla anterior
    («más de 3 bloques por lado») trató la página como de una columna e intercaló los artículos 27-38.
    """
    ancho, alto = pagina.rect.width, pagina.rect.height
    bloques = [b for b in pagina.get_text("blocks") if b[6] == 0 and not es_encabezado(b, alto)]
    izquierda = sum(b[3] - b[1] for b in bloques if b[2] <= ancho * 0.55)
    derecha = sum(b[3] - b[1] for b in bloques if b[0] >= ancho * 0.45)
    if izquierda > alto * 0.15 and derecha > alto * 0.15:
        def clave(b):
            return (0 if b[0] < ancho * 0.48 else 1, b[1], b[0])
    else:
        def clave(b):
            return (round(b[1]), b[0])
    return "\n".join(b[4] for b in sorted(bloques, key=clave))


def leer_paginas(doc, paginas) -> str:
    return "\n".join(leer_pagina(doc[i]) for i in range(paginas[0] - 1, paginas[1]))


def segmento(doc, paginas, inicio, fin) -> str:
    """Texto de las páginas de la norma, recortado entre sus marcadores (si los hay)."""
    texto = re.sub(r"[ \t]+", " ", leer_paginas(doc, paginas))
    if inicio:
        i = re.sub(r"\s+", " ", texto).find(inicio)
        if i < 0:
            raise SystemExit(f"[ERROR] marcador de inicio no encontrado: {inicio!r}")
        texto = _cortar_desde(texto, inicio)
    if fin:
        texto = _cortar_hasta(texto, fin)
    return texto.strip()


def _cortar_desde(texto: str, marcador: str) -> str:
    patron = r"\s+".join(map(re.escape, marcador.split()))
    m = re.search(patron, texto)
    return texto[m.start():]


def _cortar_hasta(texto: str, marcador: str) -> str:
    patron = r"\s*".join(map(re.escape, marcador.replace(" ", "")))
    m = re.search(patron, texto)
    if not m:
        raise SystemExit(f"[ERROR] marcador de fin no encontrado: {marcador!r}")
    return texto[:m.end()]


def aplicar_exclusiones(texto: str, excluir: list[dict]) -> tuple[str, list[dict]]:
    """Quita tramos de otras publicaciones intercalados por la maquetación, y deja constancia."""
    hechas = []
    for x in excluir:
        a = re.search(r"\s+".join(map(re.escape, x["desde"].split())), texto)
        b = re.search(r"\s+".join(map(re.escape, x["hasta_antes_de"].split())), texto)
        if not a or not b or b.start() <= a.start():
            raise SystemExit(f"[ERROR] exclusión no aplicable: {x['desde']!r}")
        hechas.append({**x, "caracteres": b.start() - a.start()})
        texto = texto[:a.start()] + texto[b.start():]
    return texto, hechas


MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre")


def muestra_fecha(portada_plana: str, fecha: str) -> bool:
    """La portada muestra día, mes y año de la fecha ISO (antes solo se comprobaba el año)."""
    anno, mes, dia = fecha.split("-")
    return bool(re.search(rf"(?i)\b{int(dia)} de {MESES[int(mes) - 1]} del? {anno}\b", portada_plana))


def verificar_gaceta_del_alcance(entrada: dict, portada_plana: str) -> None:
    """El número de Gaceta de un alcance se comprueba en La Gaceta, no se toma de terceros.

    Hasta el 2026-10-08 solo se verificaba el número de alcance: las portadas de los alcances 38 de 2019 y
    202 de 2018 no traen el número de Gaceta, y ese dato venía de dictámenes de la PGR. Si la portada del
    alcance no lo trae, se confirma en la portada de la edición ordinaria del mismo día
    (`confirmacion_gaceta` en el catálogo), que muestra la fecha y el número.
    """
    pub = entrada["publicacion"]
    if re.search(rf"(?i)GACETA\s+N[OoºÚ°.]*\s*{pub['gaceta']}\b", portada_plana):
        return
    url = entrada.get("confirmacion_gaceta")
    if not url:
        raise SystemExit(f"[ERROR] {entrada['id']}: la portada del alcance no muestra la Gaceta {pub['gaceta']} "
                         "y no hay edición ordinaria del día para confirmarla (confirmacion_gaceta)")
    portada_dia = re.sub(r"\s+", " ", fitz.open(pdf_local(url))[0].get_text())
    if not (re.search(rf"N[º°o.]\s*{pub['gaceta']}\b", portada_dia) and muestra_fecha(portada_dia, pub["fecha"])):
        raise SystemExit(f"[ERROR] {entrada['id']}: la edición del día no confirma la Gaceta {pub['gaceta']}")
    print(f"[..] {entrada['id']}: Gaceta {pub['gaceta']} confirmada en la edición ordinaria del mismo día")


def verificar(entrada: dict, texto_paginas: str, portada: str) -> None:
    """QA-2/QA-3: título, número de Gaceta y citas, contra el texto oficial. Aborta si algo falla."""
    base = plano(texto_paginas)
    pub = entrada["publicacion"]
    portada_plana = re.sub(r"\s+", " ", portada)
    # Las portadas de alcance traen el número de alcance (algunas, no el de Gaceta); las ediciones
    # ordinarias traen el número de Gaceta.
    if pub["alcance"]:
        patron = rf"ALCANCE\s+N[OoºÚ°.]*\s*{pub['alcance']}\b|Alcance\s+N[º°o.]*\s*{pub['alcance']}\b"
    else:
        patron = rf"N[º°o.]\s*{pub['gaceta']}\b"
    if not re.search(patron, portada_plana):
        raise SystemExit(f"[ERROR] {entrada['id']}: la portada no coincide con la publicación indicada")
    if not muestra_fecha(portada_plana, pub["fecha"]):
        raise SystemExit(f"[ERROR] {entrada['id']}: la portada no muestra la fecha {pub['fecha']}")
    if pub["alcance"]:
        verificar_gaceta_del_alcance(entrada, portada_plana)
    if entrada["titulo_tipo"] == "oficial" and plano(entrada["titulo"]) not in base:
        # En los escaneos (texto no incluido) el OCR deforma letras: se acepta una coincidencia
        # aproximada alta del título dentro de la primera página de la norma.
        similitud = _mejor_similitud(plano(entrada["titulo"]), plano(texto_paginas[:3000]))
        if entrada["texto_incluido"] or similitud < UMBRAL_TITULO_OCR:
            raise SystemExit(f"[ERROR] {entrada['id']}: título oficial no encontrado (similitud {similitud:.2f})")
        print(f"[..] {entrada['id']}: título verificado por aproximación OCR ({similitud:.2f})")
    if plano(entrada["numero"].split("-")[0]) not in base:
        raise SystemExit(f"[ERROR] {entrada['id']}: número no encontrado en el PDF")
    for rel in entrada["relaciones"]:
        if plano(rel["cita"]) not in base:
            raise SystemExit(f"[ERROR] {entrada['id']}: cita no literal: {rel['cita'][:80]!r}")


def construir() -> None:
    catalogo = json.loads((RAIZ / "catalogo.json").read_text(encoding="utf-8"))
    ids = {e["id"] for e in catalogo}
    SALIDA.mkdir(exist_ok=True)
    hoy = datetime.date.today().isoformat()
    for e in catalogo:
        url = e["publicacion"]["url_pdf"]
        ruta = pdf_local(url)
        datos = ruta.read_bytes()
        doc = fitz.open(ruta)
        p0, p1 = e["paginas"]
        crudo = leer_paginas(doc, (p0, p1))
        verificar(e, crudo, doc[0].get_text())
        slug = e["id"].replace("/", "_")
        texto = {"incluido": e["texto_incluido"]}
        if e["texto_incluido"]:
            t = segmento(doc, e["paginas"], e.get("marcador_inicio"), e.get("marcador_fin"))
            t, exclusiones = aplicar_exclusiones(t, e.get("excluir", []))
            if exclusiones:
                texto["exclusiones"] = exclusiones
            archivo = SALIDA / f"{slug}.txt"
            archivo.write_text(t + "\n", encoding="utf-8")
            texto.update({"archivo": f"normas/{slug}.txt", "tipo": "original", "caracteres": len(t),
                          "sha256": hashlib.sha256((t + "\n").encode("utf-8")).hexdigest()})
        else:
            texto["motivo_no_incluido"] = e["motivo_sin_texto"]
        registro = {
            "esquema": "norma.v1",
            "id": e["id"], "tipo": e["tipo"], "numero": e["numero"],
            "titulo": e["titulo"], "titulo_tipo": e["titulo_tipo"], "emisor": e["emisor"],
            "publicacion": {"diario": "La Gaceta, Diario Oficial de Costa Rica",
                            "gaceta": e["publicacion"]["gaceta"], "alcance": e["publicacion"]["alcance"],
                            "fecha": e["publicacion"]["fecha"]},
            "procedencia": {
                "declaracion": DECLARACION,
                "fuente": "Imprenta Nacional de Costa Rica — La Gaceta (edición oficial)",
                "url_pdf": url, "fecha_descarga": hoy,
                "sha256_pdf": hashlib.sha256(datos).hexdigest(), "bytes_pdf": len(datos),
                "paginas": e["paginas"], "localizacion": e["localizacion"]},
            "texto": texto,
            "relaciones": [{**r, "objetivo_en_dataset": r["objetivo"] in ids} for r in e["relaciones"]],
        }
        (SALIDA / f"{slug}.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
        print(f"[OK] {e['id']}: {len(e['relaciones'])} relaciones, texto {'sí' if e['texto_incluido'] else 'no'}")


if __name__ == "__main__":
    construir()
