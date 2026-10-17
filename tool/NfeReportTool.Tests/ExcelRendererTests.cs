using ClosedXML.Excel;
using NfeReportTool;

namespace NfeReportTool.Tests;

public sealed class ExcelRendererTests : IDisposable
{
    private readonly string _out = Path.Combine(Path.GetTempPath(), $"nfe-xlsx-{Guid.NewGuid():N}");

    public ExcelRendererTests() => Directory.CreateDirectory(_out);

    public void Dispose() => Directory.Delete(_out, recursive: true);

    private static string Samples => Path.GetFullPath(Path.Combine(
        AppContext.BaseDirectory, "..", "..", "..", "..", "..", "samples", "validos"));

    [Fact]
    public void Gera_workbook_com_resumo_e_itens()
    {
        var nfes = NFeXmlReader.LerLote(Samples);
        var caminho = Path.Combine(_out, "relatorio-nfe.xlsx");
        ExcelRenderer.Gerar(nfes, caminho);

        Assert.True(File.Exists(caminho));
        using var wb = new XLWorkbook(caminho);
        Assert.Equal(new[] { "Resumo", "Itens" }, wb.Worksheets.Select(w => w.Name).ToArray());

        var resumo = wb.Worksheet("Resumo");
        Assert.Equal("chave", resumo.Cell(1, 1).GetString());
        // LerLote ordena alfabeticamente: mg, rs, sp
        Assert.Equal(nfes[0].Chave, resumo.Cell(2, 1).GetString());
        Assert.Equal(nfes[0].Totais.VProd, resumo.Cell(2, 8).GetValue<decimal>());
        var linhaSp = Array.FindIndex(nfes.ToArray(), n => n.Numero == 123) + 2;
        Assert.Equal(550.00m, resumo.Cell(linhaSp, 8).GetValue<decimal>());

        var itens = wb.Worksheet("Itens");
        Assert.Equal("xProd", itens.Cell(1, 4).GetString());
        Assert.Equal("PRODUTO GAMMA", itens.Cell(2, 4).GetString());
    }
}
