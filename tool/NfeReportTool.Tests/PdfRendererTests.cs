using NfeReportTool;
using UglyToad.PdfPig;

namespace NfeReportTool.Tests;

public sealed class PdfRendererTests : IDisposable
{
    private readonly string _out = Path.Combine(Path.GetTempPath(), $"nfe-pdf-{Guid.NewGuid():N}");

    public PdfRendererTests() => Directory.CreateDirectory(_out);

    public void Dispose() => Directory.Delete(_out, recursive: true);

    private static string Samples => Path.GetFullPath(Path.Combine(
        AppContext.BaseDirectory, "..", "..", "..", "..", "..", "samples", "validos"));

    [Fact]
    public void Pdf_contem_chave_emitente_e_rodape()
    {
        var nfe = NFeXmlReader.Ler(Path.Combine(Samples, "nfe-sp-001.xml"));
        var caminho = Path.Combine(_out, "doc.pdf");
        PdfRenderer.Gerar(nfe, caminho);

        Assert.True(File.Exists(caminho));
        using var doc = PdfDocument.Open(caminho);
        Assert.True(doc.NumberOfPages >= 1);
        var texto = string.Concat(doc.GetPages().SelectMany(p => p.GetWords()).Select(w => w.Text));
        Assert.Contains("EMPRESA", texto);
        Assert.Contains("Documento", texto);
        Assert.Contains(nfe.Chave[..4], texto);
    }
}
