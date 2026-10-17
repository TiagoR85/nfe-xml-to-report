namespace NfeReportTool.Tests;

public sealed class ScaffoldTests
{
    [Fact]
    public void Comando_stub_devolve_zero() => Assert.Equal(0, Comando.Executar([]));
}
