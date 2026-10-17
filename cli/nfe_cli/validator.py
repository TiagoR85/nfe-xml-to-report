from __future__ import annotations

from pathlib import Path

from lxml import etree

from nfe_cli.model import NFe
from nfe_cli.parser import ParseError, carregar_arvore, parse_nfe
from nfe_cli.rules import verificar_nfe

SCHEMAS_DIR_DEFAULT = Path(__file__).resolve().parents[2] / "schemas" / "nfe_v4.00"


def _validar_xsd(raiz: etree._Element, schemas_dir: Path) -> str | None:
    xsd_path = schemas_dir / "nfe_v4.00.xsd"
    try:
        schema = etree.XMLSchema(etree.parse(str(xsd_path)))
    except (etree.XMLSchemaParseError, OSError) as exc:
        return f"XSD indisponivel: {exc}"
    if schema.validate(etree.ElementTree(raiz)):
        return None
    return f"XSD: {schema.error_log[0].message}"


def validar_dir(dir_in: Path, schemas_dir: Path | None = None) -> list[tuple[str, str, str]]:
    """Valida todos os .xml do diretorio. Devolve (basename, codigo, mensagem) ordenado."""
    schemas = schemas_dir or SCHEMAS_DIR_DEFAULT
    erros: list[tuple[str, str, str]] = []
    pares: list[tuple[str, NFe]] = []

    for caminho in sorted(dir_in.glob("*.xml")):
        nome = caminho.name
        try:
            raiz = carregar_arvore(caminho)
        except ParseError as exc:
            erros.append((nome, exc.codigo, exc.mensagem))
            continue
        msg_xsd = _validar_xsd(raiz, schemas)
        if msg_xsd is not None:
            erros.append((nome, "XSD", msg_xsd))
            continue
        try:
            pares.append((nome, parse_nfe(caminho)))
        except ParseError as exc:
            erros.append((nome, exc.codigo, exc.mensagem))

    vistos: set[tuple[int, int]] = set()
    for nome, nfe in pares:
        for codigo, mensagem in verificar_nfe(nfe):
            erros.append((nome, codigo, mensagem))
        if nfe.serie is not None and nfe.numero is not None:
            par = (nfe.serie, nfe.numero)
            if par in vistos:
                erros.append((nome, "SERIE_NUMERO_UNICO",
                              f"serie {nfe.serie} numero {nfe.numero} repetido no lote"))
            vistos.add(par)

    erros.sort()
    return erros
