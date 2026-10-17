from pathlib import Path

from nfe_cli.parser import parse_nfe
from nfe_cli.rules import cnpj_valido, cpf_valido, verificar_lote, verificar_nfe

RAIZ = Path(__file__).resolve().parents[2]
VALIDOS = RAIZ / "samples" / "validos"
INVALIDOS = RAIZ / "samples" / "invalidos"


def codigos(pares):
    return [c for c, _ in pares]


def test_sp_sem_erros():
    assert verificar_nfe(parse_nfe(VALIDOS / "nfe-sp-001.xml")) == []


def test_mg_sem_erros():
    assert verificar_nfe(parse_nfe(VALIDOS / "nfe-mg-001.xml")) == []


def test_rs_sem_erros():
    assert verificar_nfe(parse_nfe(VALIDOS / "nfe-rs-001.xml")) == []


def test_chave_dv_errado():
    erros = verificar_nfe(parse_nfe(INVALIDOS / "chave-dv-errado.xml"))
    assert "CHAVE_DV" in codigos(erros)


def test_cnpj_dv_errado():
    erros = verificar_nfe(parse_nfe(INVALIDOS / "cnpj-dv-errado.xml"))
    assert "CNPJ_DV" in codigos(erros)


def test_cpf_dv_errado():
    erros = verificar_nfe(parse_nfe(INVALIDOS / "cpf-dv-errado.xml"))
    assert "CPF_DV" in codigos(erros)


def test_soma_itens_errada():
    erros = verificar_nfe(parse_nfe(INVALIDOS / "soma-itens-errada.xml"))
    assert "ITENS_SOMA_VPROD" in codigos(erros)


def test_vnf_incoerente():
    erros = verificar_nfe(parse_nfe(INVALIDOS / "vnf-incoerente.xml"))
    assert "TOTAL_VNF" in codigos(erros)


def test_sem_dest_obrigatorios():
    erros = verificar_nfe(parse_nfe(INVALIDOS / "sem-dest.xml"))
    assert "OBRIGATORIOS" in codigos(erros)


def test_dup_vencida():
    erros = verificar_nfe(parse_nfe(INVALIDOS / "dup-vencida.xml"))
    assert "DUP_VENCIMENTO" in codigos(erros)


def test_serie_numero_unico_lote_temporario(tmp_path):
    origem = VALIDOS / "nfe-sp-001.xml"
    (tmp_path / "a.xml").write_bytes(origem.read_bytes())
    (tmp_path / "b.xml").write_bytes(origem.read_bytes())
    nfes = [parse_nfe(tmp_path / "a.xml"), parse_nfe(tmp_path / "b.xml")]
    erros = verificar_lote(nfes)
    assert "SERIE_NUMERO_UNICO" in codigos(erros)


def test_lote_sem_duplicatas_de_serie():
    nfes = [parse_nfe(p) for p in sorted(VALIDOS.glob("*.xml"))]
    assert "SERIE_NUMERO_UNICO" not in codigos(verificar_lote(nfes))


def test_cpf_valido_repetido_falso():
    assert not cpf_valido("11111111111")


def test_cnpj_valido_repetido_falso():
    assert not cnpj_valido("11111111111111")
