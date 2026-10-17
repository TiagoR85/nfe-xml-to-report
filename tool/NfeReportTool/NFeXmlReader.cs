using System.Globalization;
using System.Xml;
using System.Xml.Linq;
using NfeReportTool.Models;

namespace NfeReportTool;

public static class NFeXmlReader
{
    private static readonly XNamespace Ns = "http://www.portalfiscal.inf.br/nfe";

    private static readonly XmlReaderSettings Seguro = new()
    {
        DtdProcessing = DtdProcessing.Prohibit,
        XmlResolver = null,
    };

    public static NFeModel Ler(string caminho)
    {
        using var reader = XmlReader.Create(caminho, Seguro);
        var doc = XDocument.Load(reader);
        var inf = doc.Root?.Element(Ns + "infNFe")
            ?? throw new InvalidOperationException("infNFe nao encontrado");

        var chave = (inf.Attribute("Id")?.Value ?? "")["NFe".Length..];
        var ide = inf.Element(Ns + "ide")
            ?? throw new InvalidOperationException("ide nao encontrado");
        var emit = inf.Element(Ns + "emit")
            ?? throw new InvalidOperationException("emit nao encontrado");
        var dest = inf.Element(Ns + "dest")
            ?? throw new InvalidOperationException("dest nao encontrado");
        var total = inf.Element(Ns + "total")?.Element(Ns + "ICMSTot")
            ?? throw new InvalidOperationException("ICMSTot nao encontrado");

        var itens = inf.Elements(Ns + "det").Select(det =>
        {
            var prod = det.Element(Ns + "prod")
                ?? throw new InvalidOperationException("prod nao encontrado");
            return new ItemNFe(
                int.Parse(det.Attribute("nItem")?.Value ?? "0", CultureInfo.InvariantCulture),
                Texto(prod, "cProd"), Texto(prod, "xProd"), Texto(prod, "NCM"),
                Texto(prod, "CFOP"), Texto(prod, "uCom"),
                Dec(prod, "qCom"), Dec(prod, "vUnCom"), Dec(prod, "vProd"));
        }).ToList();

        var docDest = Texto(dest, "CNPJ") is { Length: > 0 } cnpj ? cnpj : Texto(dest, "CPF");

        return new NFeModel(
            Chave: chave,
            Serie: int.Parse(Texto(ide, "serie"), CultureInfo.InvariantCulture),
            Numero: int.Parse(Texto(ide, "nNF"), CultureInfo.InvariantCulture),
            DhEmissao: DateTimeOffset.Parse(Texto(ide, "dhEmi"), CultureInfo.InvariantCulture,
                DateTimeStyles.RoundtripKind),
            NatOp: Texto(ide, "natOp"),
            Emit: new Emitente(Texto(emit, "xNome"), Texto(emit, "CNPJ"),
                Texto(emit, "IE"), Endereco(emit, "enderEmit")),
            Dest: new Destinatario(Texto(dest, "xNome"), docDest ?? "", Endereco(dest, "enderDest")),
            Itens: itens,
            Totais: new Totais(Dec(total, "vProd"), Dec(total, "vDesc"), Dec(total, "vFrete"),
                Dec(total, "vOutro"), Dec(total, "vSeg"), Dec(total, "vNF")));
    }

    public static IReadOnlyList<NFeModel> LerLote(string dirIn) =>
        Directory.GetFiles(dirIn, "*.xml")
            .OrderBy(f => f, StringComparer.Ordinal)
            .Select(Ler)
            .ToList();

    private static string Texto(XElement pai, string nome) =>
        (pai.Element(Ns + nome)?.Value ?? "").Trim();

    private static decimal Dec(XElement pai, string nome) =>
        decimal.Parse(Texto(pai, nome), CultureInfo.InvariantCulture);

    private static string Endereco(XElement pai, string nome)
    {
        var end = pai.Element(Ns + nome);
        if (end is null) return "";
        var partes = new[] { "xLgr", "nro", "xBairro", "xMun", "UF" }
            .Select(c => Texto(end, c)).Where(s => s.Length > 0);
        return string.Join(", ", partes);
    }
}
