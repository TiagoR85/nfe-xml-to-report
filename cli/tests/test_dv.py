from nfe_cli.dv import dv_cnpj, dv_cpf, dv_modulo11_chave


def test_chave_dv_ciclo_2a9():
    base = "35503089999999000191550010000000011000000010"
    assert dv_modulo11_chave(base) in "0123456789"


def test_chave_dv_conhecido():
    base = "352610112223330001815500100000123000000001"
    assert dv_modulo11_chave(base) == dv_modulo11_chave(base)


def test_cnpj_dv_exemplo_classico():
    # 11.222.333/0001-81 e um CNPJ exemplo com DV valido
    assert dv_cnpj("112223330001") == "81"


def test_cpf_dv_exemplo_classico():
    # 529.982.247-25 e um CPF exemplo com DV valido
    assert dv_cpf("529982247") == "25"
