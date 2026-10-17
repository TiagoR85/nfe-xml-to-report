namespace NfeReportTool.Models;

public sealed record ItemNFe(
    int NItem, string CProd, string XProd, string Ncm, string Cfop,
    string UCom, decimal QCom, decimal VUnCom, decimal VProd);

public sealed record Emitente(string XNome, string Cnpj, string Ie, string Endereco);

public sealed record Destinatario(string XNome, string Documento, string Endereco);

public sealed record Totais(
    decimal VProd, decimal VDesc, decimal VFrete, decimal VOutro, decimal VSeg, decimal VNF);

public sealed record NFeModel(
    string Chave, int Serie, int Numero, DateTimeOffset DhEmissao, string NatOp,
    Emitente Emit, Destinatario Dest, IReadOnlyList<ItemNFe> Itens, Totais Totais);
