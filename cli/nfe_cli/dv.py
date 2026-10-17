"""Validacao de digitos verificadores: chave NF-e (mod 11), CNPJ, CPF."""


def dv_modulo11_chave(base43: str) -> str:
    soma, peso = 0, 2
    for c in reversed(base43):
        soma += int(c) * peso
        peso = 2 if peso == 9 else peso + 1
    resto = soma % 11
    return "0" if resto < 2 else str(11 - resto)


def dv_cnpj(base12: str) -> str:
    def parcial(base: str, peso: int) -> str:
        soma = 0
        for c in base:
            soma += int(c) * peso
            peso -= 1
            if peso == 1:
                peso = 9
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    d1 = parcial(base12, 5)
    return d1 + parcial(base12 + d1, 6)


def dv_cpf(base9: str) -> str:
    def parcial(base: str, peso: int) -> str:
        soma = sum(int(c) * p for c, p in zip(base, range(peso, 1, -1)))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    d1 = parcial(base9, 10)
    return d1 + parcial(base9 + d1, 11)
