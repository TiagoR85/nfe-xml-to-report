# ADR-0002: O dotnet tool lê o diretório de XMLs

## Contexto
Fronteira Python↔C#: podia ser JSON intermédio (Python extrai, tool só renderiza) ou o tool ler os mesmos XMLs.

## Decisão
O tool recebe `--in DIR` e lê os XMLs diretamente (uma invocação por lote). Contrato = CLI + exit codes (0/1/3).

## Consequências
- Zero duplicação de parsing/serialização; menos uma camada para testar.
- O tool confia no validador Python (pré-requisito documentado); o reader C# mantém o mesmo hardening (XmlReader seguro).
- Nota: args parsing manual em `Comando` (sem System.CommandLine) para evitar pin de prerelease — desvio consciente da escolha primária do spec §7.
