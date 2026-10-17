# ADR-0001: ClosedXML + QuestPDF para relatórios

## Contexto
A spec-mãe do portfólio sugeria EPPlus + iText. EPPlus mudou para licença comercial (>=v5) e iText 7 é AGPL — ambos conflitam com o objetivo MIT/didático.

## Decisão
Usar **ClosedXML 0.105.1** (MIT) e **QuestPDF 2026.9.1** (Community: grátis para indivíduos e organizações < $1M/ano).

## Consequências
- Licenças compatíveis com MIT e com uso didático público.
- QuestPDF exige `Settings.License = LicenseType.Community`; desde 2026.9.x as fontes do sistema não são incluídas por omissão — usamos a família `Lato` que vem no archive default do QuestPDF.
- Se o portfólio crescer para uso comercial > $1M, reavaliar (ex.: PdfSharpCore + outra lib).
