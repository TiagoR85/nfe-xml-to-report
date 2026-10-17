namespace NfeReportTool;

public static class Comando
{
    private const string Uso = "uso: nfe-report generate --in DIR --out DIR [--format excel|pdf|all]";

    public static int Executar(string[] args)
    {
        if (args.Length == 0 || args[0] != "generate")
        {
            Console.Error.WriteLine(Uso);
            return 1;
        }

        string? dirIn = null, dirOut = null, formato = "all";
        for (var i = 1; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--in" when i + 1 < args.Length:
                    dirIn = args[++i];
                    break;
                case "--out" when i + 1 < args.Length:
                    dirOut = args[++i];
                    break;
                case "--format" when i + 1 < args.Length:
                    formato = args[++i];
                    if (formato is not ("excel" or "pdf" or "all"))
                    {
                        Console.Error.WriteLine(Uso);
                        return 1;
                    }
                    break;
                default:
                    Console.Error.WriteLine(Uso);
                    return 1;
            }
        }

        if (dirIn is null || dirOut is null || !Directory.Exists(dirIn))
        {
            Console.Error.WriteLine(Uso);
            return 1;
        }
        if (Directory.GetFiles(dirIn, "*.xml").Length == 0)
        {
            Console.Error.WriteLine($"erro: nenhum .xml em {dirIn}");
            return 1;
        }

        try
        {
            Directory.CreateDirectory(dirOut);
            var nfes = NFeXmlReader.LerLote(dirIn);
            if (formato is "excel" or "all")
                ExcelRenderer.Gerar(nfes, Path.Combine(dirOut, "relatorio-nfe.xlsx"));
            if (formato is "pdf" or "all")
                foreach (var nfe in nfes)
                    PdfRenderer.Gerar(nfe, Path.Combine(dirOut, $"{nfe.Chave}.pdf"));
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"erro: {ex.Message}");
            return 3;
        }
    }
}
