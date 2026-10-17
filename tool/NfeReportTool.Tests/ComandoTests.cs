using NfeReportTool;

namespace NfeReportTool.Tests;

public sealed class ComandoTests : IDisposable
{
    private readonly string _out = Path.Combine(Path.GetTempPath(), $"nfe-cmd-{Guid.NewGuid():N}");

    public ComandoTests() => Directory.CreateDirectory(_out);

    public void Dispose() => Directory.Delete(_out, recursive: true);

    private static string Samples => Path.GetFullPath(Path.Combine(
        AppContext.BaseDirectory, "..", "..", "..", "..", "..", "samples", "validos"));

    [Fact]
    public void Sem_args_exit1() => Assert.Equal(1, Comando.Executar([]));

    [Fact]
    public void Dir_inexistente_exit1() =>
        Assert.Equal(1, Comando.Executar(["generate", "--in", "nao-existe", "--out", _out]));

    [Fact]
    public void Dir_sem_xmls_exit1()
    {
        var vazio = Path.Combine(_out, "vazio");
        Directory.CreateDirectory(vazio);
        Assert.Equal(1, Comando.Executar(["generate", "--in", vazio, "--out", _out]));
    }

    [Fact]
    public void Generate_validos_exit0_e_escreve_relatorios()
    {
        var saida = Path.Combine(_out, "ok");
        var exit = Comando.Executar(["generate", "--in", Samples, "--out", saida, "--format", "all"]);
        Assert.Equal(0, exit);
        Assert.True(File.Exists(Path.Combine(saida, "relatorio-nfe.xlsx")));
        Assert.Equal(3, Directory.GetFiles(saida, "*.pdf").Length);
    }

    [Fact]
    public void Generate_somente_excel_exit0_sem_pdf()
    {
        var saida = Path.Combine(_out, "so-excel");
        var exit = Comando.Executar(["generate", "--in", Samples, "--out", saida, "--format", "excel"]);
        Assert.Equal(0, exit);
        Assert.True(File.Exists(Path.Combine(saida, "relatorio-nfe.xlsx")));
        Assert.Empty(Directory.GetFiles(saida, "*.pdf"));
    }
}
