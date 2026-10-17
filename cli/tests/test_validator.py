from pathlib import Path

from nfe_cli.validator import validar_dir

RAIZ = Path(__file__).resolve().parents[2]
VALIDOS = RAIZ / "samples" / "validos"
INVALIDOS = RAIZ / "samples" / "invalidos"


def test_validar_dir_validos_vazio():
    assert validar_dir(VALIDOS) == []


def test_validar_dir_invalidos_lista_todos():
    erros = validar_dir(INVALIDOS)
    codigos = {c for _, c, _ in erros}
    assert {"CHAVE_DV", "CNPJ_DV", "CPF_DV", "ITENS_SOMA_VPROD", "TOTAL_VNF",
            "OBRIGATORIOS", "DUP_VENCIMENTO", "XSD"} <= codigos
    assert any(c == "PARSE" for _, c, _ in erros)


def test_validar_dir_formato_linha(tmp_path):
    destino = tmp_path / "lote"
    destino.mkdir()
    (destino / "k.xml").write_bytes((INVALIDOS / "chave-dv-errado.xml").read_bytes())
    erros = validar_dir(destino)
    assert erros[0][0] == "k.xml"
    assert erros[0][1] == "CHAVE_DV"
