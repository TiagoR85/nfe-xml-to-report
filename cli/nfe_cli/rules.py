from __future__ import annotations

from decimal import Decimal

from nfe_cli.dv import dv_cnpj, dv_cpf, dv_modulo11_chave
from nfe_cli.model import NFe

TOLERANCIA = Decimal("0.01")


def chave_valida(chave: str) -> bool:
    if len(chave) != 44 or not chave.isdigit():
        return False
    return dv_modulo11_chave(chave[:43]) == chave[43]


def cnpj_valido(cnpj: str) -> bool:
    if len(cnpj) != 14 or not cnpj.isdigit() or len(set(cnpj)) == 1:
        return False
    return dv_cnpj(cnpj[:12]) == cnpj[12:]


def cpf_valido(cpf: str) -> bool:
    if len(cpf) != 11 or not cpf.isdigit() or len(set(cpf)) == 1:
        return False
    return dv_cpf(cpf[:9]) == cpf[9:]


def _fmt(valor: Decimal | None) -> str:
    return f"{valor:.2f}" if valor is not None else "?"


def verificar_nfe(nfe: NFe) -> list[tuple[str, str]]:
    erros: list[tuple[str, str]] = []

    if not chave_valida(nfe.chave):
        erros.append(("CHAVE_DV", "digito verificador da chave invalido"))

    obrigatorio_falta = False
    if nfe.serie is None or nfe.numero is None or nfe.dh_emi is None or nfe.nat_op is None:
        obrigatorio_falta = True
    if nfe.emitente is None or not nfe.emitente.x_nome:
        obrigatorio_falta = True
    if nfe.destinatario is None or not nfe.destinatario.x_nome:
        obrigatorio_falta = True
    if not nfe.itens:
        obrigatorio_falta = True
    if nfe.totais is None or nfe.totais.v_prod is None or nfe.totais.v_nf is None:
        obrigatorio_falta = True
    if obrigatorio_falta:
        erros.append(("OBRIGATORIOS", "elemento obrigatorio em falta"))

    if nfe.emitente is not None and nfe.emitente.cnpj and not cnpj_valido(nfe.emitente.cnpj):
        erros.append(("CNPJ_DV", "cnpj com digito verificador invalido"))
    if nfe.destinatario is not None:
        if nfe.destinatario.cnpj and not cnpj_valido(nfe.destinatario.cnpj):
            erros.append(("CNPJ_DV", "cnpj com digito verificador invalido"))
        if nfe.destinatario.cpf and not cpf_valido(nfe.destinatario.cpf):
            erros.append(("CPF_DV", "cpf com digito verificador invalido"))

    if nfe.totais is not None and nfe.totais.v_prod is not None:
        soma = sum((i.v_prod for i in nfe.itens), Decimal(0))
        if abs(soma - nfe.totais.v_prod) > TOLERANCIA:
            erros.append((
                "ITENS_SOMA_VPROD",
                f"soma dos itens ({_fmt(soma)}) difere de vProd ({_fmt(nfe.totais.v_prod)})",
            ))

    if nfe.totais is not None and nfe.totais.v_nf is not None and nfe.totais.v_prod is not None:
        t = nfe.totais
        esperado = (
            t.v_prod
            - (t.v_desc or Decimal(0))
            + (t.v_frete or Decimal(0))
            + (t.v_outro or Decimal(0))
            + (t.v_seg or Decimal(0))
        )
        if abs(esperado - t.v_nf) > TOLERANCIA:
            erros.append((
                "TOTAL_VNF",
                f"vNF ({_fmt(t.v_nf)}) nao confere com vProd-vDesc+vFrete+vOutro+vSeg ({_fmt(esperado)})",
            ))

    for dup in nfe.duplicatas:
        if dup.venc is not None and nfe.dh_emi is not None and dup.venc < nfe.dh_emi.date():
            erros.append((
                "DUP_VENCIMENTO",
                f"vencimento {dup.venc.isoformat()} anterior a emissao {nfe.dh_emi.date().isoformat()}",
            ))

    return erros


def verificar_lote(nfes: list[NFe]) -> list[tuple[str, str]]:
    erros: list[tuple[str, str]] = []
    vistos: set[tuple[int, int]] = set()
    for nfe in nfes:
        erros.extend(verificar_nfe(nfe))
        if nfe.serie is not None and nfe.numero is not None:
            par = (nfe.serie, nfe.numero)
            if par in vistos:
                erros.append((
                    "SERIE_NUMERO_UNICO",
                    f"serie {nfe.serie} numero {nfe.numero} repetido no lote",
                ))
            vistos.add(par)
    return erros
