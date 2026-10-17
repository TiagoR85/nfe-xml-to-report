using ClosedXML.Excel;
using NfeReportTool;
using NfeReportTool.Models;

namespace NfeReportTool;

public static class ExcelRenderer
{
    public static void Gerar(IReadOnlyList<NFeModel> nfes, string caminhoSaida)
    {
        using var wb = new XLWorkbook();

        var resumo = wb.Worksheets.Add("Resumo");
        string[] colsResumo = ["chave", "numero", "serie", "dhEmi", "emitente",
            "cnpjEmitente", "destinatario", "vProd", "vNF"];
        for (var c = 0; c < colsResumo.Length; c++)
        {
            resumo.Cell(1, c + 1).Value = colsResumo[c];
            resumo.Cell(1, c + 1).Style.Font.Bold = true;
        }
        var linha = 2;
        foreach (var nfe in nfes)
        {
            resumo.Cell(linha, 1).Value = nfe.Chave;
            resumo.Cell(linha, 2).Value = nfe.Numero;
            resumo.Cell(linha, 3).Value = nfe.Serie;
            resumo.Cell(linha, 4).Value = nfe.DhEmissao.ToString("yyyy-MM-ddTHH:mm:sszzz");
            resumo.Cell(linha, 5).Value = nfe.Emit.XNome;
            resumo.Cell(linha, 6).Value = nfe.Emit.Cnpj;
            resumo.Cell(linha, 7).Value = nfe.Dest.XNome;
            resumo.Cell(linha, 8).Value = nfe.Totais.VProd;
            resumo.Cell(linha, 8).Style.NumberFormat.Format = "R$ #,##0.00";
            resumo.Cell(linha, 9).Value = nfe.Totais.VNF;
            resumo.Cell(linha, 9).Style.NumberFormat.Format = "R$ #,##0.00";
            linha++;
        }
        resumo.Columns().AdjustToContents();
        resumo.SheetView.FreezeRows(1);
        resumo.RangeUsed()!.SetAutoFilter();

        var itens = wb.Worksheets.Add("Itens");
        string[] colsItens = ["chave", "nItem", "cProd", "xProd", "ncm", "cfop",
            "uCom", "qCom", "vUnCom", "vProd"];
        for (var c = 0; c < colsItens.Length; c++)
        {
            itens.Cell(1, c + 1).Value = colsItens[c];
            itens.Cell(1, c + 1).Style.Font.Bold = true;
        }
        linha = 2;
        foreach (var nfe in nfes)
        {
            foreach (var item in nfe.Itens)
            {
                itens.Cell(linha, 1).Value = nfe.Chave;
                itens.Cell(linha, 2).Value = item.NItem;
                itens.Cell(linha, 3).Value = item.CProd;
                itens.Cell(linha, 4).Value = item.XProd;
                itens.Cell(linha, 5).Value = item.Ncm;
                itens.Cell(linha, 6).Value = item.Cfop;
                itens.Cell(linha, 7).Value = item.UCom;
                itens.Cell(linha, 8).Value = item.QCom;
                itens.Cell(linha, 9).Value = item.VUnCom;
                itens.Cell(linha, 10).Value = item.VProd;
                itens.Cell(linha, 10).Style.NumberFormat.Format = "R$ #,##0.00";
                linha++;
            }
        }
        itens.Columns().AdjustToContents();
        itens.SheetView.FreezeRows(1);
        itens.RangeUsed()!.SetAutoFilter();

        wb.SaveAs(caminhoSaida);
    }
}
