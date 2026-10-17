import shutil
from pathlib import Path

import pytest
from nfe_cli.main import main

RAIZ = Path(__file__).resolve().parents[2]
VALIDOS = RAIZ / "samples" / "validos"
INVALIDOS = RAIZ / "samples" / "invalidos"

pytestmark = pytest.mark.e2e

tool_disponivel = shutil.which("nfe-report") is not None


@pytest.mark.skipif(not tool_disponivel, reason="nfe-report nao instalado")
def test_process_validos_exit0_gera_relatorios(tmp_path):
    out = tmp_path / "out"
    assert main(["process", "--in", str(VALIDOS), "--out", str(out)]) == 0
    assert (out / "relatorio-nfe.xlsx").is_file()
    assert len(list(out.glob("*.pdf"))) == 3


@pytest.mark.skipif(not tool_disponivel, reason="nfe-report nao instalado")
def test_process_invalidos_exit2_sem_saida(tmp_path, capsys):
    out = tmp_path / "out"
    assert main(["process", "--in", str(INVALIDOS), "--out", str(out)]) == 2
    assert not out.exists()
    assert "CHAVE_DV" in capsys.readouterr().err


def test_process_tool_faltando_exit3(tmp_path):
    out = tmp_path / "out"
    fantasma = tmp_path / "nao-existe.exe"
    assert main(["process", "--in", str(VALIDOS), "--out", str(out),
                 "--tool-path", str(fantasma)]) == 3
