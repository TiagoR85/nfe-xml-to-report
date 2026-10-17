# ADR-0003: XSD NF-e vendorado no repo

## Contexto
Validação XSD precisa do schema; CI e testes devem correr offline.

## Decisão
Vendorar o XSD oficial em `schemas/nfe_v4.00/` (pacote completo: `nfe_v4.00.xsd` + `leiauteNFe_v4.00.xsd` + `tiposBasico_v4.00.xsd` + `xmldsig-core-schema_v1.01.xsd` + `DFeTiposBasicos_v1.00.xsd`), obtido do pacote npm `@brasil-fiscal/nfe@2.0.1`.

## Consequências
- CI sem rede para o XSD; samples e schema versionados juntos (drift visível em diff).
- Validação equivalente ao schema da SEFAZ para o subconjunto usado nos samples (inclui assinatura XMLDSig estrutural).
- Atualização futura = substituir os ficheiros + regenerar samples + correr pytest.
