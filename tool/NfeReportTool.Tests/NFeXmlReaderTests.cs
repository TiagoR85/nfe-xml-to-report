using NfeReportTool;

namespace NfeReportTool.Tests;

public sealed class NFeXmlReaderTests
{
    private static string Samples => Path.GetFullPath(Path.Combine(
        AppContext.BaseDirectory, "..", "..", "..", "..", "..", "samples", "validos"));

    [Fact]
    public void Le_sp_campos_principais()
    {
        var nfe = NFeXmlReader.Ler(Path.Combine(Samples, "nfe-sp-001.xml"));
        Assert.StartsWith("35261011222333000181", nfe.Chave);
        Assert.Equal(44, nfe.Chave.Length);
        Assert.Equal(1, nfe.Serie);
        Assert.Equal(123, nfe.Numero);
        Assert.Equal("VENDA DE MERCADORIA", nfe.NatOp);
        Assert.Equal("EMPRESA FICTICIA COMERCIO LTDA", nfe.Emit.XNome);
        Assert.Equal(2, nfe.Itens.Count);
        Assert.Equal(550.00m, nfe.Totais.VProd);
        Assert.Equal(550.00m, nfe.Totais.VNF);
    }

    [Fact]
    public void Le_rs_totais_com_desc_frete_outro()
    {
        var nfe = NFeXmlReader.Ler(Path.Combine(Samples, "nfe-rs-001.xml"));
        Assert.Equal(275.00m, nfe.Totais.VProd);
        Assert.Equal(10.00m, nfe.Totais.VDesc);
        Assert.Equal(20.00m, nfe.Totais.VFrete);
        Assert.Equal(5.00m, nfe.Totais.VOutro);
        Assert.Equal(290.00m, nfe.Totais.VNF);
    }

    [Fact]
    public void Ler_lote_devolve_tres()
    {
        var lote = NFeXmlReader.LerLote(Samples);
        Assert.Equal(3, lote.Count);
    }

    [Fact]
    public void Xml_com_dtd_e_rejeitado()
    {
        var dir = Path.Combine(Path.GetTempPath(), $"nfe-dtd-{Guid.NewGuid():N}");
        Directory.CreateDirectory(dir);
        var f = Path.Combine(dir, "mal.xml");
        File.WriteAllText(f,
            "<!DOCTYPE NFe [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>" +
            "<NFe xmlns=\"http://www.portalfiscal.inf.br/nfe\"><infNFe Id=\"NFe1\">" +
            "<ide><cUF>&xxe;</cUF></ide></infNFe></NFe>");
        Assert.ThrowsAny<Exception>(() => NFeXmlReader.Ler(f));
        Directory.Delete(dir, true);
    }
}
