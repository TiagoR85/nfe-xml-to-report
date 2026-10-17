from pathlib import Path

from nfe_cli.main import main

RAIZ = Path(__file__).resolve().parents[2]
VALIDOS = RAIZ / "samples" / "validos"
INVALIDOS = RAIZ / "samples" / "invalidos"


def test_validate_validos_exit0(capsys):
    assert main(["validate", "--in", str(VALIDOS)]) == 0
    assert "OK: 3 NF-e validas" in capsys.readouterr().out


def test_validate_invalidos_exit2(capsys):
    assert main(["validate", "--in", str(INVALIDOS)]) == 2
    err = capsys.readouterr().err
    assert "chave-dv-errado.xml:CHAVE_DV:" in err
    assert "xsd-violado.xml:XSD:" in err


def test_dir_inexistente_exit1():
    assert main(["validate", "--in", "nao-existe"]) == 1


def test_dir_sem_xmls_exit1(tmp_path):
    vazio = tmp_path / "vazio"
    vazio.mkdir()
    assert main(["validate", "--in", str(vazio)]) == 1


def test_sem_args_exit1():
    assert main([]) == 1
