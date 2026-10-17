from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class Item:
    n_item: int
    c_prod: str
    x_prod: str
    ncm: str
    cfop: str
    u_com: str
    q_com: Decimal
    v_un_com: Decimal
    v_prod: Decimal


@dataclass(frozen=True)
class Emitente:
    x_nome: str | None
    cnpj: str | None
    ie: str | None
    endereco: str | None


@dataclass(frozen=True)
class Destinatario:
    x_nome: str | None
    cnpj: str | None
    cpf: str | None
    endereco: str | None


@dataclass(frozen=True)
class Totais:
    v_prod: Decimal | None
    v_desc: Decimal | None
    v_frete: Decimal | None
    v_outro: Decimal | None
    v_seg: Decimal | None
    v_nf: Decimal | None
    v_bc: Decimal | None
    v_icms: Decimal | None


@dataclass(frozen=True)
class Duplicata:
    numero: str | None
    venc: date | None
    v_dup: Decimal | None


@dataclass(frozen=True)
class NFe:
    chave: str
    serie: int | None
    numero: int | None
    dh_emi: datetime | None
    nat_op: str | None
    emitente: Emitente | None
    destinatario: Destinatario | None
    itens: tuple[Item, ...]
    totais: Totais | None
    duplicatas: tuple[Duplicata, ...]
