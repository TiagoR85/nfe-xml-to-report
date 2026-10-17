using NfeReportTool.Models;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace NfeReportTool;

public static class PdfRenderer
{
    public static void Gerar(NFeModel nfe, string caminhoSaida)
    {
        QuestPDF.Settings.License = LicenseType.Community;
        Document.Create(container =>
        {
            container.Page(page =>
            {
                page.Size(PageSizes.A4);
                page.Margin(20);
                page.DefaultTextStyle(t => t.FontFamily("Lato").FontSize(9));

                page.Header().Column(col =>
                {
                    col.Item().Text("DANFE simplificado — Documento Auxiliar da NF-e").FontSize(12).Bold();
                    col.Item().Text("Documento de estudo — sem validade fiscal").FontColor(Colors.Grey.Darken1);
                    col.Item().PaddingTop(6).Text(t =>
                    {
                        t.Span("Chave: ").Bold();
                        t.Span(EmGruposDe4(nfe.Chave));
                    });
                });

                page.Content().PaddingTop(10).Column(col =>
                {
                    col.Item().Text($"Emitente: {nfe.Emit.XNome} — CNPJ {nfe.Emit.Cnpj} — IE {nfe.Emit.Ie}").Bold();
                    col.Item().Text($"Endereco: {nfe.Emit.Endereco}");
                    col.Item().PaddingTop(4).Text($"Destinatario: {nfe.Dest.XNome} — {nfe.Dest.Documento}");
                    col.Item().Text($"Endereco: {nfe.Dest.Endereco}");
                    col.Item().PaddingTop(4).Text(
                        $"NF-e nº {nfe.Numero} Serie {nfe.Serie} — emissao {nfe.DhEmissao:yyyy-MM-dd} — {nfe.NatOp}");

                    col.Item().PaddingTop(8).Table(t =>
                    {
                        t.ColumnsDefinition(c =>
                        {
                            c.RelativeColumn(1);
                            c.RelativeColumn(4);
                            c.RelativeColumn(2);
                            c.RelativeColumn(2);
                            c.RelativeColumn(2);
                        });
                        t.Header(h =>
                        {
                            foreach (var titulo in new[] { "Item", "Produto", "NCM", "Qtd", "Valor" })
                                h.Cell().Background(Colors.Grey.Lighten3).Padding(3).Text(titulo).Bold();
                        });
                        foreach (var item in nfe.Itens)
                        {
                            t.Cell().Padding(3).Text(item.NItem.ToString());
                            t.Cell().Padding(3).Text(item.XProd);
                            t.Cell().Padding(3).Text(item.Ncm);
                            t.Cell().Padding(3).Text(item.QCom.ToString("0.####"));
                            t.Cell().Padding(3).Text(item.VProd.ToString("0.00"));
                        }
                    });

                    col.Item().PaddingTop(8).Text(t =>
                    {
                        t.Span("vProd: ").Bold();
                        t.Span(nfe.Totais.VProd.ToString("0.00"));
                        t.Span("   vNF: ").Bold();
                        t.Span(nfe.Totais.VNF.ToString("0.00"));
                    });
                });

                page.Footer().AlignCenter().Text("nfe-xml-to-report · gerado para fins de estudo");
            });
        }).GeneratePdf(caminhoSaida);
    }

    private static string EmGruposDe4(string chave) =>
        string.Join(" ", Enumerable.Range(0, chave.Length / 4)
            .Select(i => chave.Substring(i * 4, 4)));
}
