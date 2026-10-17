from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from lxml import etree

from nfe_cli.model import Destinatario, Duplicata, Emitente, Item, NFe, Totais

NS = {"n": "http://www.portalfiscal.inf.br/nfe"}
MAX_BYTES = 2 * 1024 * 1024


class ParseError(Exception):
    def __init__(self, codigo: str, mensagem: str):
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem


def _parser_hardened() -> etree.XMLParser:
    return etree.XMLParser(
        resolve_entities=False, no_network=True, load_dtd=False, huge_tree=False
    )


def carregar_arvore(caminho: Path) -> etree._Element:
    if caminho.stat().st_size > MAX_BYTES:
        raise ParseError("FILE_TOO_BIG", f"ficheiro excede {MAX_BYTES} bytes")
    try:
        arvore = etree.parse(str(caminho), _parser_hardened())
    except (etree.XMLSyntaxError, ValueError) as exc:
        raise ParseError("PARSE", f"xml rejeitado: {exc}") from exc
    if arvore.docinfo.doctype:
        raise ParseError("PARSE", "doctype rejeitado")
    return arvore.getroot()


def _texto(raiz: etree._Element, xpath: str) -> str | None:
    nos = raiz.xpath(xpath, namespaces=NS)
    if not nos:
        return None
    valor = (nos[0].text or "").strip()
    return valor or None


def _decimal(raiz: etree._Element, xpath: str) -> Decimal | None:
    texto = _texto(raiz, xpath)
    if texto is None:
        return None
    try:
        return Decimal(texto)
    except InvalidOperation as exc:
        raise ParseError("PARSE", f"valor decimal invalido em {xpath}: {texto}") from exc


def _inteiro(valor: str | None) -> int | None:
    return int(valor) if valor is not None and valor.isdigit() else None


def _ender(raiz: etree._Element, xpath: str) -> str | None:
    partes = []
    for campo in ("xLgr", "nro", "xBairro", "xMun", "UF"):
        valor = _texto(raiz, f"{xpath}/{campo}")
        if valor:
            partes.append(valor)
    return ", ".join(partes) if partes else None


def parse_nfe(caminho: Path) -> NFe:
    raiz = carregar_arvore(caminho)
    inf = raiz.find("n:infNFe", NS)
    if inf is None:
        raise ParseError("PARSE", "elemento infNFe nao encontrado")

    chave = (inf.get("Id") or "").removeprefix("NFe")

    emit_el = raiz.find("n:infNFe/n:emit", NS)
    emit = None
    if emit_el is not None:
        emit = Emitente(
            x_nome=_texto(raiz, "n:infNFe/n:emit/n:xNome"),
            cnpj=_texto(raiz, "n:infNFe/n:emit/n:CNPJ"),
            ie=_texto(raiz, "n:infNFe/n:emit/n:IE"),
            endereco=_ender(raiz, "n:infNFe/n:emit/n:enderEmit"),
        )

    dest_el = raiz.find("n:infNFe/n:dest", NS)
    dest = None
    if dest_el is not None:
        dest = Destinatario(
            x_nome=_texto(raiz, "n:infNFe/n:dest/n:xNome"),
            cnpj=_texto(raiz, "n:infNFe/n:dest/n:CNPJ"),
            cpf=_texto(raiz, "n:infNFe/n:dest/n:CPF"),
            endereco=_ender(raiz, "n:infNFe/n:dest/n:enderDest"),
        )

    itens = []
    for det in raiz.findall("n:infNFe/n:det", NS):
        n_item = int(det.get("nItem") or 0)
        itens.append(Item(
            n_item=n_item,
            c_prod=_texto(det, "n:prod/n:cProd") or "",
            x_prod=_texto(det, "n:prod/n:xProd") or "",
            ncm=_texto(det, "n:prod/n:NCM") or "",
            cfop=_texto(det, "n:prod/n:CFOP") or "",
            u_com=_texto(det, "n:prod/n:uCom") or "",
            q_com=_decimal(det, "n:prod/n:qCom") or Decimal(0),
            v_un_com=_decimal(det, "n:prod/n:vUnCom") or Decimal(0),
            v_prod=_decimal(det, "n:prod/n:vProd") or Decimal(0),
        ))

    totais = None
    if raiz.find("n:infNFe/n:total/n:ICMSTot", NS) is not None:
        totais = Totais(
            v_prod=_decimal(raiz, "n:infNFe/n:total/n:ICMSTot/n:vProd"),
            v_desc=_decimal(raiz, "n:infNFe/n:total/n:ICMSTot/n:vDesc"),
            v_frete=_decimal(raiz, "n:infNFe/n:total/n:ICMSTot/n:vFrete"),
            v_outro=_decimal(raiz, "n:infNFe/n:total/n:ICMSTot/n:vOutro"),
            v_seg=_decimal(raiz, "n:infNFe/n:total/n:ICMSTot/n:vSeg"),
            v_nf=_decimal(raiz, "n:infNFe/n:total/n:ICMSTot/n:vNF"),
            v_bc=_decimal(raiz, "n:infNFe/n:total/n:ICMSTot/n:vBC"),
            v_icms=_decimal(raiz, "n:infNFe/n:total/n:ICMSTot/n:vICMS"),
        )

    duplicatas = []
    for dup in raiz.findall("n:infNFe/n:cobr/n:dup", NS):
        venc_texto = _texto(dup, "n:dVenc")
        venc = None
        if venc_texto:
            venc = date.fromisoformat(venc_texto[:10])
        duplicatas.append(Duplicata(
            numero=_texto(dup, "n:nDup"),
            venc=venc,
            v_dup=_decimal(dup, "n:vDup"),
        ))

    dh_texto = _texto(raiz, "n:infNFe/n:ide/n:dhEmi")
    dh_emi = datetime.fromisoformat(dh_texto) if dh_texto else None

    return NFe(
        chave=chave,
        serie=_inteiro(_texto(raiz, "n:infNFe/n:ide/n:serie")),
        numero=_inteiro(_texto(raiz, "n:infNFe/n:ide/n:nNF")),
        dh_emi=dh_emi,
        nat_op=_texto(raiz, "n:infNFe/n:ide/n:natOp"),
        emitente=emit,
        destinatario=dest,
        itens=tuple(itens),
        totais=totais,
        duplicatas=tuple(duplicatas),
    )
