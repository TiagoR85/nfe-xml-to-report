from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from nfe_cli.parser import ParseError, parse_nfe

RAIZ = Path(__file__).resolve().parents[2]
VALIDOS = RAIZ / "samples" / "validos"
INVALIDOS = RAIZ / "samples" / "invalidos"


def test_parse_sp_campos_principais():
    nfe = parse_nfe(VALIDOS / "nfe-sp-001.xml")
    assert nfe.chave.startswith("35261011222333000181")
    assert len(nfe.chave) == 44
    assert nfe.serie == 1
    assert nfe.numero == 123
    assert nfe.dh_emi == datetime.fromisoformat("2026-10-01T10:00:00-03:00")
    assert nfe.nat_op == "VENDA DE MERCADORIA"
    assert nfe.emitente is not None
    assert nfe.emitente.x_nome == "EMPRESA FICTICIA COMERCIO LTDA"
    assert nfe.emitente.cnpj == "11222333000181"
    assert len(nfe.itens) == 2
    assert nfe.itens[0].c_prod == "PROD-001"
    assert nfe.itens[0].v_prod == Decimal("300.00")
    assert nfe.totais is not None
    assert nfe.totais.v_prod == Decimal("550.00")
    assert nfe.totais.v_nf == Decimal("550.00")
    assert nfe.duplicatas[0].venc == date(2026, 10, 11)


def test_parse_mg_um_item_sem_dup():
    nfe = parse_nfe(VALIDOS / "nfe-mg-001.xml")
    assert len(nfe.itens) == 1
    assert nfe.duplicatas == ()
    assert nfe.destinatario is not None


def test_parse_rs_totais_com_desc_frete_outro():
    nfe = parse_nfe(VALIDOS / "nfe-rs-001.xml")
    t = nfe.totais
    assert t is not None
    assert t.v_prod == Decimal("275.00")
    assert t.v_desc == Decimal("10.00")
    assert t.v_frete == Decimal("20.00")
    assert t.v_outro == Decimal("5.00")
    assert t.v_nf == Decimal("290.00")


def test_parse_dest_com_cpf():
    nfe = parse_nfe(INVALIDOS / "cpf-dv-errado.xml")
    assert nfe.destinatario is not None
    assert nfe.destinatario.cpf is not None
    assert nfe.destinatario.cnpj is None


def test_parse_sem_dest_leniente():
    nfe = parse_nfe(INVALIDOS / "sem-dest.xml")
    assert nfe.destinatario is None


def test_xxe_rejeitado():
    with pytest.raises(ParseError) as exc:
        parse_nfe(INVALIDOS / "xxe.xml")
    assert exc.value.codigo == "PARSE"


def test_malformado_rejeitado(tmp_path):
    f = tmp_path / "quebrado.xml"
    f.write_text("<NFe><infNFe>", encoding="utf-8")
    with pytest.raises(ParseError) as exc:
        parse_nfe(f)
    assert exc.value.codigo == "PARSE"


def test_arquivo_grande_rejeitado(tmp_path):
    f = tmp_path / "grande.xml"
    f.write_bytes(b"<NFe>" + b"a" * (2 * 1024 * 1024 + 1) + b"</NFe>")
    with pytest.raises(ParseError) as exc:
        parse_nfe(f)
    assert exc.value.codigo == "FILE_TOO_BIG"
