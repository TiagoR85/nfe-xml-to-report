# nfe-xml-to-report

[![ci](https://github.com/TiagoR85/nfe-xml-to-report/actions/workflows/ci.yml/badge.svg)](https://github.com/TiagoR85/nfe-xml-to-report/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/TiagoR85/nfe-xml-to-report)](https://github.com/TiagoR85/nfe-xml-to-report/releases)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Pipeline didático de XML de NF-e 4.00: validação em Python (lxml) + relatórios Excel/PDF em C# (dotnet tool).

## About this repository

CLI Python (`nfecli`) valida um diretório de XMLs de NF-e 4.00 — XSD + 8 regras semânticas — e, quando o lote está limpo, invoca o dotnet tool `nfe-report` que gera **1 Excel consolidado** (ClosedXML) e **1 PDF tipo DANFE simplificado por NF-e** (QuestPDF). A fronteira entre os dois mundos é filesystem + exit codes.

> Dados fictícios: os samples usam CNPJs/CPFs inventados (com DVs válidos). Nenhum dado real de contribuinte.

## Quickstart

```powershell
# 1. tool local (a partir do fonte)
dotnet pack tool/NfeReportTool/NfeReportTool.csproj -c Release -o nupkg
dotnet tool install --global --add-source nupkg nfe-report

# 2. CLI
pip install -e cli
nfecli process --in samples/validos --out out
# → out/relatorio-nfe.xlsx + 3 PDFs

nfecli validate --in samples/invalidos
# → exit 2, erros no stderr (um por linha: arquivo:REGRA: mensagem)
```

## Regras semânticas (códigos estáveis)

| Código | Regra |
|--------|-------|
| CHAVE_DV | chave de 44 dígitos + DV módulo 11 |
| CNPJ_DV / CPF_DV | dígitos verificadores módulo 11 |
| ITENS_SOMA_VPROD | Σ itens = vProd (tol. 0.01) |
| TOTAL_VNF | vNF = vProd − vDesc + vFrete + vOutro + vSeg |
| OBRIGATORIOS | ide/emit/dest/det/total presentes |
| SERIE_NUMERO_UNICO | (série, nº) únicos no lote |
| DUP_VENCIMENTO | vencimento ≥ emissão |
| XSD / PARSE / FILE_TOO_BIG | estrutura, XML seguro, limite 2 MB |

## Arquitetura

```
nfecli (Python/lxml)                    nfe-report (dotnet tool)
  parse hardened  ──┐                     XmlReader seguro
  XSD + 8 regras   ├─ exit 0 ──────────▶  ClosedXML → relatorio-nfe.xlsx
  exit 1/2/3       │                      QuestPDF  → <chave>.pdf
                   └─ filesystem + exit codes
```

## Segurança

- Python: `XMLParser(resolve_entities=False, no_network=True, load_dtd=False, huge_tree=False)` — payload XXE rejeitado (teste dedicado).
- C#: `XmlReaderSettings { DtdProcessing = Prohibit, XmlResolver = null }`.
- lxml 6.1.3 inclui o fix de CVE-2026-41066; mantemos o hardening explícito por defesa em profundidade.

## Decisões de design

- [ADR-0001](docs/adr/ADR-0001-closedxml-questpdf.md) — ClosedXML + QuestPDF vs EPPlus + iText (licenças).
- [ADR-0002](docs/adr/ADR-0002-tool-lera-diretorio.md) — tool lê o diretório vs contrato JSON intermédio.
- [ADR-0003](docs/adr/ADR-0003-xsd-oficial-vendorado.md) — XSD vendorado para CI offline.

## Backlog

DANFE oficial completo (QR, logo) · eventos/cancelamento (procEventoNFe) · streaming de lotes grandes · NFC-e/CT-e · download SEFAZ (ver soap-grpc-bridge) · publicação NuGet/PyPI.
