#!/usr/bin/env python3
"""Gera samples de NF-e 4.00 (validos e invalidos) de forma deterministica.

Dados ficticios: CNPJs/CPFs inventados com DVs validos.
Regenerar: python scripts/generate_samples.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "cli"))

from nfe_cli.dv import dv_cnpj, dv_cpf, dv_modulo11_chave

VALIDOS = RAIZ / "samples" / "validos"
INVALIDOS = RAIZ / "samples" / "invalidos"
NS = "http://www.portalfiscal.inf.br/nfe"
VERSAO = "4.00"
UF_POR_CUF = {"35": "SP", "31": "MG", "43": "RS"}


def dec2(valor: float) -> str:
    return f"{valor:.2f}"


def montar_xml(
    *,
    cuf: str,
    cnpj_base12: str,
    serie: int,
    nnf: int,
    cnf: int,
    dhemi: str,
    cmun_fg: str,
    itens: list[tuple[str, str, str, str, str, str, str, str]],
    v_desc: float = 0.0,
    v_frete: float = 0.0,
    v_outro: float = 0.0,
    dup_venc: str | None = None,
    cpf_dest: str | None = None,
    incluir_dest: bool = True,
    incluir_total: bool = True,
    chave_dv_override: str | None = None,
    cnpj_dv_errado: bool = False,
    cpf_dv_errado: bool = False,
    vprod_item_extra: float = 0.0,
    vnf_extra: float = 0.0,
) -> str:
    cnpj = cnpj_base12 + dv_cnpj(cnpj_base12)
    if cnpj_dv_errado:
        dv_bom = dv_cnpj(cnpj_base12)[-1]
        cnpj = cnpj_base12 + ("0" if dv_bom != "0" else "1")
    chave_base = f"{cuf}2610{cnpj}55{serie:03d}{nnf:09d}1{cnf:08d}"
    dv = chave_dv_override or dv_modulo11_chave(chave_base)
    chave = chave_base + dv

    v_prod_total = sum(float(i[7]) for i in itens)
    v_nf = round(v_prod_total - v_desc + v_frete + v_outro + vnf_extra, 2)

    dets = []
    for idx, (cprod, xprod, ncm, cfop, ucom, qcom, vuncom, vprod) in enumerate(itens, start=1):
        vprod_real = dec2(float(vprod) + (vprod_item_extra if idx == len(itens) else 0.0))
        dets.append(f"""    <det nItem="{idx}">
      <prod>
        <cProd>{cprod}</cProd>
        <cEAN>SEM GTIN</cEAN>
        <xProd>{xprod}</xProd>
        <NCM>{ncm}</NCM>
        <CFOP>{cfop}</CFOP>
        <uCom>{ucom}</uCom>
        <qCom>{qcom}</qCom>
        <vUnCom>{vuncom}</vUnCom>
        <vProd>{vprod_real}</vProd>
        <cEANTrib>SEM GTIN</cEANTrib>
        <uTrib>{ucom}</uTrib>
        <qTrib>{qcom}</qTrib>
        <vUnTrib>{vuncom}</vUnTrib>
        <indTot>1</indTot>
      </prod>
      <imposto>
        <ICMS>
          <ICMS00>
            <orig>0</orig>
            <CST>00</CST>
            <modBC>3</modBC>
            <vBC>{dec2(float(vprod))}</vBC>
            <pICMS>18.00</pICMS>
            <vICMS>{dec2(float(vprod) * 0.18)}</vICMS>
          </ICMS00>
        </ICMS>
        <PIS><PISNT><CST>08</CST></PISNT></PIS>
        <COFINS><COFINSNT><CST>08</CST></COFINSNT></COFINS>
      </imposto>
    </det>""")

    if cpf_dest:
        dv_ok = dv_cpf(cpf_dest)
        dv_final = ("0" if dv_ok[0] != "0" else "1") + dv_ok[1] if cpf_dv_errado else dv_ok
        doc_dest = f"        <CPF>{cpf_dest}{dv_final}</CPF>\n"
    else:
        doc_dest = f"        <CNPJ>{cnpj}</CNPJ>\n"

    bloco_dest = f"""    <dest>
{doc_dest}      <xNome>DESTINATARIO FICTICIO LTDA</xNome>
      <enderDest>
        <xLgr>RUA DAS ACACIAS</xLgr>
        <nro>456</nro>
        <xBairro>JARDIM</xBairro>
        <cMun>{cmun_fg}</cMun>
        <xMun>MUNICIPIO FICTICIO</xMun>
        <UF>{UF_POR_CUF[cuf]}</UF>
        <CEP>01000000</CEP>
        <cPais>1058</cPais>
        <xPais>BRASIL</xPais>
      </enderDest>
      <indIEDest>9</indIEDest>
    </dest>""" if incluir_dest else ""

    bloco_total = f"""    <total>
      <ICMSTot>
        <vBC>{dec2(v_prod_total)}</vBC>
        <vICMS>{dec2(v_prod_total * 0.18)}</vICMS>
        <vICMSDeson>0.00</vICMSDeson>
        <vFCP>0.00</vFCP>
        <vBCST>0.00</vBCST>
        <vST>0.00</vST>
        <vFCPST>0.00</vFCPST>
        <vFCPSTRet>0.00</vFCPSTRet>
        <vProd>{dec2(v_prod_total)}</vProd>
        <vFrete>{dec2(v_frete)}</vFrete>
        <vSeg>0.00</vSeg>
        <vDesc>{dec2(v_desc)}</vDesc>
        <vII>0.00</vII>
        <vIPI>0.00</vIPI>
        <vIPIDevol>0.00</vIPIDevol>
        <vPIS>0.00</vPIS>
        <vCOFINS>0.00</vCOFINS>
        <vOutro>{dec2(v_outro)}</vOutro>
        <vNF>{dec2(v_nf)}</vNF>
      </ICMSTot>
    </total>""" if incluir_total else ""

    bloco_cobr = f"""    <cobr>
      <dup>
        <nDup>001</nDup>
        <dVenc>{dup_venc}</dVenc>
        <vDup>{dec2(v_nf)}</vDup>
      </dup>
    </cobr>""" if dup_venc else ""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<NFe xmlns="{NS}">
  <infNFe Id="NFe{chave}" versao="{VERSAO}">
    <ide>
      <cUF>{cuf}</cUF>
      <cNF>{cnf:08d}</cNF>
      <natOp>VENDA DE MERCADORIA</natOp>
      <mod>55</mod>
      <serie>{serie}</serie>
      <nNF>{nnf}</nNF>
      <dhEmi>{dhemi}</dhEmi>
      <tpNF>1</tpNF>
      <idDest>1</idDest>
      <cMunFG>{cmun_fg}</cMunFG>
      <tpImp>1</tpImp>
      <tpEmis>1</tpEmis>
      <cDV>{dv}</cDV>
      <tpAmb>2</tpAmb>
      <finNFe>1</finNFe>
      <indFinal>0</indFinal>
      <indPres>0</indPres>
      <procEmi>0</procEmi>
      <verProc>nfe-xml-to-report</verProc>
    </ide>
    <emit>
      <CNPJ>{cnpj}</CNPJ>
      <xNome>EMPRESA FICTICIA COMERCIO LTDA</xNome>
      <xFant>FICTICIA COMERCIO</xFant>
      <enderEmit>
        <xLgr>AVENIDA PAULISTA</xLgr>
        <nro>1000</nro>
        <xBairro>BELA VISTA</xBairro>
        <cMun>3550308</cMun>
        <xMun>SAO PAULO</xMun>
        <UF>SP</UF>
        <CEP>01310100</CEP>
        <cPais>1058</cPais>
        <xPais>BRASIL</xPais>
        <fone>1130000000</fone>
      </enderEmit>
      <IE>110042490114</IE>
      <CRT>3</CRT>
    </emit>
{bloco_dest}
{chr(10).join(dets)}
{bloco_total}
    <transp>
      <modFrete>0</modFrete>
    </transp>
{bloco_cobr}
    <pag>
      <detPag>
        <tPag>01</tPag>
        <vPag>{dec2(v_nf)}</vPag>
      </detPag>
    </pag>
  </infNFe>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
      <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
      <Reference URI="#NFe{chave}">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
          <Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
        </Transforms>
        <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
        <DigestValue>AAAAAAAAAAAAAAAAAAAAAAAAAAA=</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue>U0lHTkFUVVJFREFETw==</SignatureValue>
    <KeyInfo>
      <X509Data>
        <X509Certificate>Q0VSVElGSUNBREFETw==</X509Certificate>
      </X509Data>
    </KeyInfo>
  </Signature>
</NFe>
"""


ITENS_SP = [
    ("PROD-001", "PRODUTO ALPHA", "84713012", "5102", "UN", "2.0000", "150.00", "300.00"),
    ("PROD-002", "PRODUTO BETA", "84713012", "5102", "UN", "1.0000", "250.00", "250.00"),
]
ITENS_MG = [("PROD-101", "PRODUTO GAMMA", "39269090", "5102", "PC", "5.0000", "20.00", "100.00")]
ITENS_RS = [
    ("PROD-201", "PRODUTO DELTA", "64041100", "5102", "UN", "1.0000", "100.00", "100.00"),
    ("PROD-202", "PRODUTO EPSILON", "64041100", "5102", "UN", "2.0000", "50.00", "100.00"),
    ("PROD-203", "PRODUTO ZETA", "64041100", "5102", "UN", "1.0000", "75.00", "75.00"),
]


def gerar() -> None:
    VALIDOS.mkdir(parents=True, exist_ok=True)
    INVALIDOS.mkdir(parents=True, exist_ok=True)

    (VALIDOS / "nfe-sp-001.xml").write_text(montar_xml(
        cuf="35", cnpj_base12="112223330001", serie=1, nnf=123, cnf=1,
        dhemi="2026-10-01T10:00:00-03:00", cmun_fg="3550308", itens=ITENS_SP,
        dup_venc="2026-10-11"), encoding="utf-8")

    (VALIDOS / "nfe-mg-001.xml").write_text(montar_xml(
        cuf="31", cnpj_base12="445566770001", serie=1, nnf=45, cnf=2,
        dhemi="2026-10-02T14:30:00-03:00", cmun_fg="3106200", itens=ITENS_MG),
        encoding="utf-8")

    (VALIDOS / "nfe-rs-001.xml").write_text(montar_xml(
        cuf="43", cnpj_base12="998877660001", serie=2, nnf=7, cnf=3,
        dhemi="2026-10-03T09:00:00-03:00", cmun_fg="4314902", itens=ITENS_RS,
        v_desc=10.0, v_frete=20.0, v_outro=5.0, dup_venc="2026-10-20"),
        encoding="utf-8")

    base = {
        "cuf": "35", "cnpj_base12": "112223330001", "serie": 1, "nnf": 123, "cnf": 1,
        "dhemi": "2026-10-01T10:00:00-03:00", "cmun_fg": "3550308", "itens": ITENS_SP,
        "dup_venc": "2026-10-11",
    }
    dv_bom = dv_modulo11_chave("352610112223330001815500100000123000000001")
    (INVALIDOS / "chave-dv-errado.xml").write_text(
        montar_xml(**base, chave_dv_override="0" if dv_bom != "0" else "1"), encoding="utf-8")
    (INVALIDOS / "cnpj-dv-errado.xml").write_text(
        montar_xml(**base, cnpj_dv_errado=True), encoding="utf-8")
    (INVALIDOS / "cpf-dv-errado.xml").write_text(
        montar_xml(**{**base, "dup_venc": None}, cpf_dest="123456789", cpf_dv_errado=True),
        encoding="utf-8")
    (INVALIDOS / "soma-itens-errada.xml").write_text(
        montar_xml(**base, vprod_item_extra=10.0), encoding="utf-8")
    (INVALIDOS / "vnf-incoerente.xml").write_text(
        montar_xml(**base, vnf_extra=5.0), encoding="utf-8")
    (INVALIDOS / "sem-dest.xml").write_text(
        montar_xml(**base, incluir_dest=False), encoding="utf-8")
    venc_vencida = (datetime(2026, 10, 1) - timedelta(days=1)).date().isoformat()
    (INVALIDOS / "dup-vencida.xml").write_text(
        montar_xml(**{**base, "dup_venc": venc_vencida}), encoding="utf-8")
    (INVALIDOS / "xsd-violado.xml").write_text(
        montar_xml(**base, incluir_total=False), encoding="utf-8")
    (INVALIDOS / "xxe.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE NFe [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\n'
        f'<NFe xmlns="{NS}" versao="{VERSAO}">\n'
        '  <infNFe Id="NFe352610112223330001815500100000123000000001" versao="4.00">\n'
        '    <ide><cUF>&xxe;</cUF></ide>\n'
        "  </infNFe>\n"
        "</NFe>\n", encoding="utf-8")

    print(f"Gerados 3 validos em {VALIDOS} e 9 invalidos em {INVALIDOS}")


if __name__ == "__main__":
    gerar()
